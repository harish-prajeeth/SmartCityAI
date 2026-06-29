# src/database/db.py

import sqlite3
from pathlib import Path
from datetime import datetime

# Resolve paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = str(PROJECT_ROOT / "database" / "smartcity.db")
SCHEMA_PATH = str(PROJECT_ROOT / "database" / "schema.sql")


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._ensure_database()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_database(self):
        db_file = Path(self.db_path)
        db_file.parent.mkdir(exist_ok=True)
        
        conn = self._connect()
        cursor = conn.cursor()

        # Check if traffic_log table already exists before executing schema to avoid wiping out data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='traffic_log'")
        table_exists = cursor.fetchone()

        if not table_exists:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema = f.read()
            cursor.executescript(schema)
            conn.commit()
            
        conn.close()

    def insert_traffic_log(self, timestamp, frame_no, vehicle_count, car_count, bike_count, bus_count, truck_count, avg_speed, congestion_level):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO traffic_log (
                timestamp, frame_no, vehicle_count, car_count, bike_count, bus_count, truck_count, avg_speed, congestion_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, frame_no, vehicle_count, car_count, bike_count, bus_count, truck_count, avg_speed, congestion_level))
        conn.commit()
        conn.close()

    def insert_violation(self, timestamp, frame_no, vehicle_id, violation_type, confidence, details, evidence_image_path):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO violations (timestamp, frame_no, vehicle_id, violation_type, confidence, details, evidence_image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, frame_no, vehicle_id, violation_type, confidence, details, evidence_image_path))
        conn.commit()
        conn.close()

    def insert_alert(self, timestamp, severity, alert_type, message, related_vehicle_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (timestamp, severity, alert_type, message, related_vehicle_id)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, severity, alert_type, message, related_vehicle_id))
        conn.commit()
        conn.close()

    def insert_parking_event(self, timestamp, vehicle_id, parked_duration, status):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parking_events (timestamp, vehicle_id, parked_duration, status)
            VALUES (?, ?, ?, ?)
        """, (timestamp, vehicle_id, parked_duration, status))
        conn.commit()
        conn.close()

    def fetch_traffic_logs(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM traffic_log ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def fetch_violations(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM violations ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def fetch_alerts(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def fetch_summary(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM traffic_log")
        total_traffic_entries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM violations")
        total_violations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alerts")
        total_alerts = cursor.fetchone()[0]

        cursor.execute("""
            SELECT vehicle_count, avg_speed, congestion_level
            FROM traffic_log
            WHERE vehicle_count > 0
            ORDER BY id DESC LIMIT 1
        """)
        latest = cursor.fetchone()
        
        # If no active vehicle logs exist, fall back to the absolute latest entry
        if not latest:
            cursor.execute("""
                SELECT vehicle_count, avg_speed, congestion_level
                FROM traffic_log
                ORDER BY id DESC LIMIT 1
            """)
            latest = cursor.fetchone()

        conn.close()

        summary = {
            "total_traffic_entries": total_traffic_entries,
            "total_violations": total_violations,
            "total_alerts": total_alerts,
            "latest_vehicle_count": latest[0] if latest else 0,
            "latest_avg_speed": latest[1] if latest else 0.0,
            "latest_congestion_level": latest[2] if latest else "N/A"
        }
        return summary
