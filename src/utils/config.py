# src/utils/config.py

VIDEO_PATH = "datasets/sample_videos/traffic1.mp4"
OUTPUT_VIDEO_PATH = "outputs/processed_videos/output_traffic1.mp4"
DB_PATH = "database/smartcity.db"

# Detection settings
CONFIDENCE_THRESHOLD = 0.35

# Allowed vehicle classes from COCO
# YOLO COCO names:
# car=2, motorcycle=3, bus=5, truck=7
VEHICLE_CLASS_IDS = [2, 3, 5, 7]

# Counting line (y coordinate)
COUNTING_LINE_Y = 350

# Speed estimation calibration
SPEED_REFERENCE_DISTANCE_PIXELS = 180  # distance in pixels on video
SPEED_REFERENCE_REAL_METERS = 10.0     # corresponding real-world distance in meters
FPS_DEFAULT = 30

# Congestion thresholds
LOW_TRAFFIC_THRESHOLD = 10
MEDIUM_TRAFFIC_THRESHOLD = 20
HIGH_TRAFFIC_THRESHOLD = 35

# Wrong-way allowed direction
# "left_to_right" means x should increase
WRONG_WAY_ALLOWED_DIRECTION = "left_to_right"

# Parking violation settings
PARKING_ZONE_COORDS = [400, 305]       # center coordinate of parking zone
PARKING_TIME_THRESHOLD = 20           # seconds for demo

# Frame resize
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Region of Interest (ROI) Polygon (vertices defining valid road area)
# Format: List of [x, y] coordinates
ROI_POLYGON = [
    [50, 50],
    [1230, 50],
    [1230, 670],
    [50, 670]
]
