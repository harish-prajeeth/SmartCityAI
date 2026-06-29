# datasets/sample_videos/generate_synthetic_video.py

import cv2
import numpy as np
import os
from pathlib import Path

def create_video(filename, road_color, double_line_color):
    project_root = Path(__file__).resolve().parent.parent.parent
    output_dir = project_root / "datasets" / "sample_videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    video_path = str(output_dir / filename)
    
    # 750 frames at 30 FPS = 25 seconds
    fps = 30
    width = 1280
    height = 720
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    
    for f in range(750):
        # Create road base
        frame = np.ones((height, width, 3), dtype=np.uint8)
        frame[:, :, 0] = road_color[0]
        frame[:, :, 1] = road_color[1]
        frame[:, :, 2] = road_color[2]
        
        # Draw grass shoulders
        cv2.rectangle(frame, (0, 0), (width, 80), (34, 139, 34), -1)
        cv2.rectangle(frame, (0, 640), (width, height), (34, 139, 34), -1)
        
        # Dashed lane white lines
        for x in range(0, width, 100):
            cv2.line(frame, (x, 360), (x + 50, 360), (220, 220, 220), 4)
            
        # Draw double lines split
        cv2.line(frame, (0, 355), (width, 355), double_line_color, 2)
        cv2.line(frame, (0, 365), (width, 365), double_line_color, 2)
        
        # Border boundaries
        cv2.line(frame, (0, 80), (width, 80), (180, 180, 180), 4)
        cv2.line(frame, (0, 640), (width, 640), (180, 180, 180), 4)
        
        # Draw simulated vehicles (vary positions slightly based on file)
        if "traffic2" in filename:
            # Video 2 Scenario: Moves right to left standard lane
            # Car (Red)
            x1 = 1100 - 6 * f
            y1 = 200 + 1 * f
            if x1 > -80:
                cv2.rectangle(frame, (max(0, x1), y1), (max(0, x1 + 80), y1 + 50), (50, 50, 220), -1)
            # Truck (Green)
            x4 = 1000 - 5 * f
            y4 = 100 + 2 * f
            if x4 > -100:
                cv2.rectangle(frame, (max(0, x4), y4), (max(0, x4 + 100), y4 + 70), (50, 180, 50), -1)
        elif "traffic3" in filename:
            # Video 3 Scenario: Heavy traffic congestion
            # Car 1
            x1 = 50 + 4 * f
            y1 = 200 + 1 * f
            cv2.rectangle(frame, (x1, y1), (x1 + 80, y1 + 50), (50, 50, 220), -1)
            # Bus (Cyan)
            x3 = 100 + 3 * f
            y3 = 250 + 1 * f
            cv2.rectangle(frame, (x3, y3), (x3 + 120, y3 + 80), (220, 220, 50), -1)
        else:
            # Video 1 standard flow
            x1 = 50 + 5 * f
            y1 = 200 + 2 * f
            cv2.rectangle(frame, (x1, y1), (x1 + 80, y1 + 50), (50, 50, 220), -1)
            
        writer.write(frame)
        
    writer.release()
    print(f"Generated synthetic video: {video_path}")


def generate_all():
    # Video 1: Gray road with yellow lines
    create_video("traffic1.mp4", [40, 40, 40], [0, 255, 255])
    # Video 2: Slightly lighter asphalt with white center lines
    create_video("traffic2.mp4", [60, 60, 60], [255, 255, 255])
    # Video 3: Light gray road with orange center lines
    create_video("traffic3.mp4", [80, 80, 80], [0, 165, 255])


if __name__ == "__main__":
    generate_all()
