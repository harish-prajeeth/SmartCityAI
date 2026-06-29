# src/main.py

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path

from src.utils.config import (
    VIDEO_PATH,
    OUTPUT_VIDEO_PATH,
    COUNTING_LINE_Y,
    FPS_DEFAULT,
    WRONG_WAY_ALLOWED_DIRECTION,
    PARKING_TIME_THRESHOLD,
    ROI_POLYGON
)

from src.utils.video_utils import open_video, resize_frame, create_video_writer
from src.utils.drawing import draw_counting_line, draw_tracked_objects, draw_dashboard_text

from src.detection.vehicle_detector import VehicleDetector
from src.tracking.tracker import CentroidTracker
from src.analytics.counting import VehicleCounter
from src.analytics.speed import SpeedEstimator
from src.analytics.congestion import CongestionAnalyzer
from src.analytics.wrong_way import WrongWayDetector
from src.analytics.parking import ParkingDetector
from src.database.db import DatabaseManager
from src.alerts.alert_manager import AlertManager


def save_violation_evidence(frame, vehicle_id, box, class_name, violation_type, confidence):
    # Copy frame to draw evidence details
    evidence_frame = frame.copy()
    x1, y1, x2, y2 = box
    cv2.rectangle(evidence_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Red border for violation
    label = f"VIOLATION: {violation_type} | ID {vehicle_id} | {class_name} | CONF: {confidence:.2f}"
    cv2.putText(evidence_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Save the screenshot safely
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"vehicle_{vehicle_id}_{violation_type.lower().replace(' ', '_')}_{timestamp_str}.jpg"
    
    project_root = Path(__file__).resolve().parent.parent
    screenshots_dir = project_root / "outputs" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = screenshots_dir / filename
    cv2.imwrite(str(filepath), evidence_frame)
    return f"outputs/screenshots/{filename}"


def run_pipeline(video_path=VIDEO_PATH, output_path=OUTPUT_VIDEO_PATH, show_preview=True):
    # Initialize modules
    detector = VehicleDetector("yolov8n.pt")
    tracker = CentroidTracker(max_distance=60)
    counter = VehicleCounter(COUNTING_LINE_Y)
    speed_estimator = SpeedEstimator(fps=FPS_DEFAULT)
    congestion_analyzer = CongestionAnalyzer()
    wrong_way_detector = WrongWayDetector(expected_direction=WRONG_WAY_ALLOWED_DIRECTION)
    parking_detector = ParkingDetector(threshold_seconds=PARKING_TIME_THRESHOLD)
    db = DatabaseManager()
    alert_manager = AlertManager(db)

    # Ensure output directories exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cap = open_video(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = FPS_DEFAULT

    width = 1280
    height = 720
    writer = create_video_writer(output_path, fps, width, height)

    frame_index = 0
    log_interval = int(fps * 2)  # log every 2 seconds

    print("Processing video...")
    
    preview_active = show_preview
    roi_contour = np.array(ROI_POLYGON, dtype=np.int32)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = resize_frame(frame)

        # 1. Detection
        detections = detector.detect(frame)

        # Filter detections by Region of Interest (ROI)
        filtered_detections = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            if cv2.pointPolygonTest(roi_contour, (cx, cy), False) >= 0:
                filtered_detections.append(det)

        # 2. Tracking
        tracked_objects = tracker.update(filtered_detections)

        # 3. Counting
        counter.update(tracked_objects)
        counts = counter.get_counts()

        # 4. Speed estimation
        speed_estimator.update(tracked_objects)
        avg_speed = speed_estimator.get_average_speed()

        # 5. Congestion analysis
        active_vehicle_count = len(tracked_objects)
        congestion_level = congestion_analyzer.analyze(active_vehicle_count)

        # 6. Wrong-way detection
        wrong_way_violations = wrong_way_detector.update(tracked_objects)
        for violation in wrong_way_violations:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vehicle_id = violation["vehicle_id"]
            
            # Retrieve metadata from tracked object
            vehicle_data = tracked_objects.get(vehicle_id, {})
            box = vehicle_data.get("bbox", [0, 0, 100, 100])
            class_name = vehicle_data.get("class_name", "unknown")
            confidence = vehicle_data.get("confidence", 0.90)
            
            # Capture evidence snapshot
            evidence_path = save_violation_evidence(frame, vehicle_id, box, class_name, "Wrong Way", confidence)
            
            db.insert_violation(
                timestamp=timestamp,
                frame_no=frame_index,
                vehicle_id=str(vehicle_id),
                violation_type=violation["violation_type"],
                confidence=confidence,
                details=violation["details"],
                evidence_image_path=evidence_path
            )
            alert_manager.process_violation_alert(violation["violation_type"], vehicle_id)

        # 7. Parking detection
        parking_violations = parking_detector.update(tracked_objects)
        for violation in parking_violations:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vehicle_id = violation["vehicle_id"]
            
            # Retrieve metadata from tracked object
            vehicle_data = tracked_objects.get(vehicle_id, {})
            box = vehicle_data.get("bbox", [0, 0, 100, 100])
            class_name = vehicle_data.get("class_name", "unknown")
            confidence = vehicle_data.get("confidence", 0.85)
            
            # Capture evidence snapshot
            evidence_path = save_violation_evidence(frame, vehicle_id, box, class_name, "Illegal Parking", confidence)
            
            db.insert_violation(
                timestamp=timestamp,
                frame_no=frame_index,
                vehicle_id=str(vehicle_id),
                violation_type=violation["violation_type"],
                confidence=confidence,
                details=violation["details"],
                evidence_image_path=evidence_path
            )
            db.insert_parking_event(timestamp, str(vehicle_id), violation["duration"], "VIOLATION")
            alert_manager.process_violation_alert(violation["violation_type"], vehicle_id)

        # 8. Congestion alerts
        alert_manager.process_congestion(congestion_level)

        # 9. Save periodic traffic log
        if frame_index % log_interval == 0:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.insert_traffic_log(
                timestamp=timestamp,
                frame_no=frame_index,
                vehicle_count=counts["total"],
                car_count=counts["car"],
                bike_count=counts["motorcycle"],
                bus_count=counts["bus"],
                truck_count=counts["truck"],
                avg_speed=avg_speed,
                congestion_level=congestion_level
            )

        # 10. Draw output overlays
        # Draw ROI Polygon border
        cv2.polylines(frame, [roi_contour], isClosed=True, color=(255, 0, 0), thickness=2)
        cv2.putText(frame, "ROI Boundary", (ROI_POLYGON[0][0] + 10, ROI_POLYGON[0][1] + 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        draw_counting_line(frame, COUNTING_LINE_Y)
        draw_tracked_objects(frame, tracked_objects, speed_estimator)
        draw_dashboard_text(frame, counts, avg_speed, congestion_level)

        # Highlight violations on active frame preview
        for violation in wrong_way_violations:
            cv2.putText(frame, f"ALERT: Wrong Way Vehicle {violation['vehicle_id']}",
                        (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        for violation in parking_violations:
            cv2.putText(frame, f"ALERT: Illegal Parking Vehicle {violation['vehicle_id']}",
                        (20, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        writer.write(frame)

        if preview_active:
            try:
                cv2.imshow("SmartCityAI", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            except Exception:
                print("GUI preview not supported or window closed. Continuing processing in headless mode...")
                preview_active = False

        frame_index += 1

    cap.release()
    writer.release()
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
    print("Processing completed.")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    run_pipeline()
