# src/analytics/counting.py

class VehicleCounter:
    def __init__(self, counting_line_y):
        self.counting_line_y = counting_line_y
        self.counted_ids = set()

        self.total_count = 0
        self.class_counts = {
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0
        }

    def update(self, tracked_objects):
        """
        tracked_objects:
        {
            object_id: {
                "centroid": (x, y),
                "bbox": [...],
                "class_name": "car"
            }
        }
        """
        for object_id, data in tracked_objects.items():
            cx, cy = data["centroid"]
            class_name = data["class_name"]

            if cy >= self.counting_line_y and object_id not in self.counted_ids:
                self.counted_ids.add(object_id)
                self.total_count += 1

                if class_name in self.class_counts:
                    self.class_counts[class_name] += 1

    def get_counts(self):
        return {
            "total": self.total_count,
            "car": self.class_counts["car"],
            "motorcycle": self.class_counts["motorcycle"],
            "bus": self.class_counts["bus"],
            "truck": self.class_counts["truck"]
        }
