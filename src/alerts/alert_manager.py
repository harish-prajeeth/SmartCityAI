# src/alerts/alert_manager.py

from datetime import datetime


class AlertManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_alert(self, severity, alert_type, message, related_vehicle_id=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.insert_alert(
            timestamp=timestamp, 
            severity=severity, 
            alert_type=alert_type, 
            message=message, 
            related_vehicle_id=str(related_vehicle_id) if related_vehicle_id else None
        )

    def process_congestion(self, congestion_level):
        if congestion_level == "CRITICAL":
            self.create_alert("HIGH", "Congestion", "Traffic congestion level is CRITICAL")
        elif congestion_level == "HIGH":
            self.create_alert("MEDIUM", "Congestion", "Traffic congestion level is HIGH")

    def process_violation_alert(self, violation_type, vehicle_id):
        # Violations are critical events -> severity set to HIGH
        self.create_alert(
            severity="HIGH", 
            alert_type=violation_type, 
            message=f"{violation_type} detected for vehicle {vehicle_id}", 
            related_vehicle_id=vehicle_id
        )
