DROP TABLE IF EXISTS traffic_log;
DROP TABLE IF EXISTS violations;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS parking_events;

CREATE TABLE IF NOT EXISTS traffic_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    frame_no INTEGER,
    vehicle_count INTEGER,
    car_count INTEGER,
    bike_count INTEGER,
    bus_count INTEGER,
    truck_count INTEGER,
    avg_speed REAL,
    congestion_level TEXT
);

CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    frame_no INTEGER,
    vehicle_id TEXT,
    violation_type TEXT,
    confidence REAL,
    details TEXT,
    evidence_image_path TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    severity TEXT,
    alert_type TEXT,
    message TEXT,
    related_vehicle_id TEXT
);

CREATE TABLE IF NOT EXISTS parking_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    vehicle_id TEXT,
    parked_duration REAL,
    status TEXT
);
