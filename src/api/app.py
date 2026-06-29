# src/api/app.py

from fastapi import FastAPI
from src.database.db import DatabaseManager

app = FastAPI(title="SmartCityAI API")
db = DatabaseManager()


@app.get("/")
def root():
    return {"message": "SmartCityAI API is running"}


@app.get("/traffic")
def get_traffic():
    rows = db.fetch_traffic_logs()
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "timestamp": row[1],
            "frame_no": row[2],
            "vehicle_count": row[3],
            "car_count": row[4],
            "bike_count": row[5],
            "bus_count": row[6],
            "truck_count": row[7],
            "avg_speed": row[8],
            "congestion_level": row[9]
        })
    return data


@app.get("/violations")
def get_violations():
    rows = db.fetch_violations()
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "timestamp": row[1],
            "frame_no": row[2],
            "vehicle_id": row[3],
            "violation_type": row[4],
            "confidence": row[5],
            "details": row[6],
            "evidence_image_path": row[7]
        })
    return data


@app.get("/alerts")
def get_alerts():
    rows = db.fetch_alerts()
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "timestamp": row[1],
            "severity": row[2],
            "alert_type": row[3],
            "message": row[4],
            "related_vehicle_id": row[5]
        })
    return data


@app.get("/summary")
def get_summary():
    return db.fetch_summary()
