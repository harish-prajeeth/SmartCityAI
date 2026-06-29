# src/detection/vehicle_detector.py

import os
from ultralytics import YOLO
from src.utils.config import CONFIDENCE_THRESHOLD, VEHICLE_CLASS_IDS


class VehicleDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.mock = os.environ.get("SMARTCITYAI_MOCK", "0") == "1"
        self.frame_index = 0

        if not self.mock:
            try:
                self.model = YOLO(model_path)
            except Exception as e:
                print(f"Failed to load YOLO model ({model_path}): {e}.")
                print("Falling back to simulated (mock) vehicle detector for testing...")
                self.mock = True

    def detect(self, frame):
        """
        Returns list of detections:
        [
            {
                "bbox": [x1, y1, x2, y2],
                "confidence": float,
                "class_id": int,
                "class_name": str
            },
            ...
        ]
        """
        if self.mock:
            self.frame_index += 1
            detections = []
            f = self.frame_index

            # Simulate 4 vehicles to trigger all features:
            
            # Vehicle 1: Car (Normal top-to-bottom, left-to-right movement)
            # Will cross counting line (y=350) around frame 75
            x1 = 50 + 5 * f
            y1 = 200 + 2 * f
            if x1 < 1200 and y1 < 650:
                detections.append({
                    "bbox": [x1, y1, x1 + 80, y1 + 50],
                    "confidence": 0.90,
                    "class_id": 2,
                    "class_name": "car"
                })

            # Vehicle 2: Motorcycle (Stationary for > 20s to trigger Illegal Parking)
            # Stays at x=400, y=305 from frame 50 to 750 (700 frames / 30 fps = 23.3 seconds)
            if f < 50:
                x2 = 100 + 6 * f
                y2 = 280 + int(0.5 * f)
            elif f < 750:
                x2 = 400
                y2 = 305
            else:
                x2 = 400 + 6 * (f - 750)
                y2 = 305 + int(0.5 * (f - 750))

            if x2 < 1200 and y2 < 650:
                detections.append({
                    "bbox": [x2, y2, x2 + 40, y2 + 30],
                    "confidence": 0.85,
                    "class_id": 3,
                    "class_name": "motorcycle"
                })

            # Vehicle 3: Bus (Right-to-left movement, dx = -15 -> triggers Wrong Way violation)
            # Starts at x=1100, y=250, moves diagonally down-left
            x3 = 1100 - 15 * f
            y3 = 250 + 1 * f
            if x3 > 50 and y3 < 650:
                detections.append({
                    "bbox": [x3, y3, x3 + 120, y3 + 80],
                    "confidence": 0.95,
                    "class_id": 5,
                    "class_name": "bus"
                })

            # Vehicle 4: Truck (Normal movement, left-to-right)
            x4 = 150 + 4 * f
            y4 = 100 + 3 * f
            if x4 < 1200 and y4 < 650:
                detections.append({
                    "bbox": [x4, y4, x4 + 100, y4 + 70],
                    "confidence": 0.92,
                    "class_id": 7,
                    "class_name": "truck"
                })

            return detections

        # Real YOLOv8 detector path
        results = self.model(frame, verbose=False)
        detections = []

        for result in results:
            boxes = result.boxes
            names = result.names

            if boxes is None:
                continue

            for box in boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])

                if conf < CONFIDENCE_THRESHOLD:
                    continue

                if cls_id not in VEHICLE_CLASS_IDS:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": conf,
                    "class_id": cls_id,
                    "class_name": names[cls_id]
                })

        return detections
