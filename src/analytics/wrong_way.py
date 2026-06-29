# src/analytics/wrong_way.py

class WrongWayDetector:
    def __init__(self, expected_direction="left_to_right"):
        self.expected_direction = expected_direction
        self.previous_positions = {}
        self.flagged_ids = set()

    def update(self, tracked_objects):
        violations = []

        for object_id, data in tracked_objects.items():
            cx, cy = data["centroid"]

            if object_id in self.previous_positions:
                prev_x, prev_y = self.previous_positions[object_id]
                delta_x = cx - prev_x

                # if expected left->right but moving strongly right->left
                if self.expected_direction == "left_to_right":
                    if delta_x < -10 and object_id not in self.flagged_ids:
                        violations.append({
                            "vehicle_id": object_id,
                            "violation_type": "Wrong Way",
                            "details": f"Vehicle {object_id} moving in opposite direction"
                        })
                        self.flagged_ids.add(object_id)

                # if expected right->left but moving left->right
                elif self.expected_direction == "right_to_left":
                    if delta_x > 10 and object_id not in self.flagged_ids:
                        violations.append({
                            "vehicle_id": object_id,
                            "violation_type": "Wrong Way",
                            "details": f"Vehicle {object_id} moving in opposite direction"
                        })
                        self.flagged_ids.add(object_id)

            self.previous_positions[object_id] = (cx, cy)

        return violations
