# src/utils/drawing.py

import cv2


def draw_counting_line(frame, y):
    cv2.line(frame, (0, y), (frame.shape[1], y), (0, 255, 255), 2)
    cv2.putText(frame, "Counting Line", (20, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


def draw_tracked_objects(frame, tracked_objects, speed_estimator):
    for object_id, data in tracked_objects.items():
        x1, y1, x2, y2 = data["bbox"]
        class_name = data["class_name"]
        speed = speed_estimator.get_speed(object_id)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"ID {object_id} | {class_name} | {speed:.1f} km/h"
        cv2.putText(frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)


def draw_dashboard_text(frame, counts, avg_speed, congestion_level):
    cv2.putText(frame, f"Total Count: {counts['total']}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"Cars: {counts['car']}  Bikes: {counts['motorcycle']}  Buses: {counts['bus']}  Trucks: {counts['truck']}",
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Avg Speed: {avg_speed:.2f} km/h", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Congestion: {congestion_level}", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
