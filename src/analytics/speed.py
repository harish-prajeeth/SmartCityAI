# src/analytics/speed.py

import math
from src.utils.config import SPEED_REFERENCE_DISTANCE_PIXELS, SPEED_REFERENCE_REAL_METERS


class SpeedEstimator:
    def __init__(self, pixel_to_meter=None, fps=30):
        self.fps = fps
        if pixel_to_meter is not None:
            self.pixel_to_meter = pixel_to_meter
        else:
            # Calibrate using config constants
            self.pixel_to_meter = SPEED_REFERENCE_REAL_METERS / SPEED_REFERENCE_DISTANCE_PIXELS
            
        self.previous_positions = {}
        self.speeds = {}

    def update(self, tracked_objects):
        for object_id, data in tracked_objects.items():
            cx, cy = data["centroid"]

            if object_id in self.previous_positions:
                prev_x, prev_y = self.previous_positions[object_id]

                pixel_distance = math.dist((prev_x, prev_y), (cx, cy))
                meter_distance = pixel_distance * self.pixel_to_meter
                time_seconds = 1 / self.fps

                speed_mps = meter_distance / time_seconds
                speed_kmph = speed_mps * 3.6

                self.speeds[object_id] = round(speed_kmph, 2)

            self.previous_positions[object_id] = (cx, cy)

    def get_speed(self, object_id):
        return self.speeds.get(object_id, 0.0)

    def get_average_speed(self):
        if not self.speeds:
            return 0.0
        return round(sum(self.speeds.values()) / len(self.speeds), 2)
