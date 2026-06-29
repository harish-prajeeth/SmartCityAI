# src/tracking/tracker.py

import math


class CentroidTracker:
    def __init__(self, max_distance=50):
        self.next_object_id = 1
        self.objects = {}  # object_id -> {"centroid": (x, y), "bbox": ..., "class_name": ..., "confidence": ...}
        self.max_distance = max_distance

    def _get_centroid(self, bbox):
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def update(self, detections):
        updated_objects = {}
        assigned_ids = set()

        # Convert detections to centroids
        det_centroids = []
        for det in detections:
            centroid = self._get_centroid(det["bbox"])
            det_centroids.append((det, centroid))

        # Match with existing objects
        for obj_id, obj_data in self.objects.items():
            old_centroid = obj_data["centroid"]
            best_match = None
            best_distance = float("inf")

            for det, centroid in det_centroids:
                if det.get("_assigned", False):
                    continue

                distance = math.dist(old_centroid, centroid)
                if distance < best_distance and distance < self.max_distance:
                    best_distance = distance
                    best_match = (det, centroid)

            if best_match:
                det, centroid = best_match
                det["_assigned"] = True
                updated_objects[obj_id] = {
                    "centroid": centroid,
                    "bbox": det["bbox"],
                    "class_name": det["class_name"],
                    "confidence": det.get("confidence", 0.0)
                }
                assigned_ids.add(obj_id)

        # Add new objects for unmatched detections
        for det, centroid in det_centroids:
            if det.get("_assigned", False):
                continue

            updated_objects[self.next_object_id] = {
                "centroid": centroid,
                "bbox": det["bbox"],
                "class_name": det["class_name"],
                "confidence": det.get("confidence", 0.0)
            }
            self.next_object_id += 1

        self.objects = updated_objects
        return self.objects
