# src/database/db.py

from pymongo import MongoClient
import pymongo
from datetime import datetime


class DatabaseManager:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="smartcity"):
        self.uri = uri
        self.db_name = db_name
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def insert_traffic_log(self, timestamp, frame_no, vehicle_count, car_count, bike_count, bus_count, truck_count, avg_speed, congestion_level):
        self.db.traffic_log.insert_one({
            "timestamp": timestamp,
            "frame_no": frame_no,
            "vehicle_count": vehicle_count,
            "car_count": car_count,
            "bike_count": bike_count,
            "bus_count": bus_count,
            "truck_count": truck_count,
            "avg_speed": avg_speed,
            "congestion_level": congestion_level
        })

    def insert_violation(self, timestamp, frame_no, vehicle_id, violation_type, confidence, details, evidence_image_path):
        self.db.violations.insert_one({
            "timestamp": timestamp,
            "frame_no": frame_no,
            "vehicle_id": vehicle_id,
            "violation_type": violation_type,
            "confidence": confidence,
            "details": details,
            "evidence_image_path": evidence_image_path
        })

    def insert_alert(self, timestamp, severity, alert_type, message, related_vehicle_id):
        self.db.alerts.insert_one({
            "timestamp": timestamp,
            "severity": severity,
            "alert_type": alert_type,
            "message": message,
            "related_vehicle_id": related_vehicle_id
        })

    def insert_parking_event(self, timestamp, vehicle_id, parked_duration, status):
        self.db.parking_events.insert_one({
            "timestamp": timestamp,
            "vehicle_id": vehicle_id,
            "parked_duration": parked_duration,
            "status": status
        })

    def fetch_traffic_logs(self):
        logs = list(self.db.traffic_log.find().sort("timestamp", pymongo.ASCENDING))
        rows = []
        for idx, log in enumerate(logs, start=1):
            rows.append((
                idx,
                log.get("timestamp"),
                log.get("frame_no"),
                log.get("vehicle_count"),
                log.get("car_count"),
                log.get("bike_count"),
                log.get("bus_count"),
                log.get("truck_count"),
                log.get("avg_speed"),
                log.get("congestion_level")
            ))
        return rows[::-1]

    def fetch_violations(self):
        vios = list(self.db.violations.find().sort("timestamp", pymongo.ASCENDING))
        rows = []
        for idx, v in enumerate(vios, start=1):
            rows.append((
                idx,
                v.get("timestamp"),
                v.get("frame_no"),
                v.get("vehicle_id"),
                v.get("violation_type"),
                v.get("confidence"),
                v.get("details"),
                v.get("evidence_image_path")
            ))
        return rows[::-1]

    def fetch_alerts(self):
        alrts = list(self.db.alerts.find().sort("timestamp", pymongo.ASCENDING))
        rows = []
        for idx, a in enumerate(alrts, start=1):
            rows.append((
                idx,
                a.get("timestamp"),
                a.get("severity"),
                a.get("alert_type"),
                a.get("message"),
                a.get("related_vehicle_id")
            ))
        return rows[::-1]

    def fetch_summary(self):
        total_traffic = self.db.traffic_log.count_documents({})
        total_violations = self.db.violations.count_documents({})
        total_alerts = self.db.alerts.count_documents({})
        
        # Get latest active traffic log
        latest_active = list(self.db.traffic_log.find({"vehicle_count": {"$gt": 0}}).sort("_id", pymongo.DESCENDING).limit(1))
        
        if latest_active:
            latest = latest_active[0]
        else:
            latest_list = list(self.db.traffic_log.find().sort("_id", pymongo.DESCENDING).limit(1))
            latest = latest_list[0] if latest_list else None
            
        summary = {
            "total_traffic_entries": total_traffic,
            "total_violations": total_violations,
            "total_alerts": total_alerts,
            "latest_vehicle_count": latest.get("vehicle_count", 0) if latest else 0,
            "latest_avg_speed": latest.get("avg_speed", 0.0) if latest else 0.0,
            "latest_congestion_level": latest.get("congestion_level", "N/A") if latest else "N/A"
        }
        return summary
