# src/analytics/congestion.py

from src.utils.config import (
    LOW_TRAFFIC_THRESHOLD,
    MEDIUM_TRAFFIC_THRESHOLD,
    HIGH_TRAFFIC_THRESHOLD
)


class CongestionAnalyzer:
    def analyze(self, vehicle_count):
        if vehicle_count < LOW_TRAFFIC_THRESHOLD:
            return "LOW"
        elif vehicle_count < MEDIUM_TRAFFIC_THRESHOLD:
            return "MEDIUM"
        elif vehicle_count < HIGH_TRAFFIC_THRESHOLD:
            return "HIGH"
        else:
            return "CRITICAL"
