# src/analytics/parking.py

import math


class ParkingDetector:
    def __init__(self, threshold_seconds=20, movement_threshold=10, fps=30):
        self.threshold_seconds = threshold_seconds
        self.movement_threshold = movement_threshold
        self.fps = fps

        self.last_positions = {}
        self.stationary_start_time = {}
        self.flagged_ids = set()
        self.virtual_time = 0.0  # Simulated video time in seconds

    def update(self, tracked_objects):
        parking_violations = []

        # Advance virtual video time by 1 frame duration (1/fps)
        self.virtual_time += 1.0 / self.fps
        current_time = self.virtual_time

        for object_id, data in tracked_objects.items():
            cx, cy = data["centroid"]

            if object_id in self.last_positions:
                prev_x, prev_y = self.last_positions[object_id]
                movement = math.dist((prev_x, prev_y), (cx, cy))

                if movement < self.movement_threshold:
                    if object_id not in self.stationary_start_time:
                        self.stationary_start_time[object_id] = current_time
                    else:
                        parked_duration = current_time - self.stationary_start_time[object_id]

                        if parked_duration >= self.threshold_seconds and object_id not in self.flagged_ids:
                            parking_violations.append({
                                "vehicle_id": object_id,
                                "violation_type": "Illegal Parking",
                                "details": f"Vehicle {object_id} parked for {int(parked_duration)} sec",
                                "duration": parked_duration
                            })
                            self.flagged_ids.add(object_id)
                else:
                    self.stationary_start_time.pop(object_id, None)

            self.last_positions[object_id] = (cx, cy)

        return parking_violations
