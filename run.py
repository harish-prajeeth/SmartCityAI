# run.py

import os
from src.main import run_pipeline

if __name__ == "__main__":
    # Define batch video processing tasks
    videos = [
        ("datasets/sample_videos/traffic1.mp4", "outputs/processed_videos/output_traffic1.mp4"),
        ("datasets/sample_videos/traffic2.mp4", "outputs/processed_videos/output_traffic2.mp4"),
        ("datasets/sample_videos/traffic3.mp4", "outputs/processed_videos/output_traffic3.mp4")
    ]
    
    print("==================================================")
    print("   SMARTCITYAI BATCH VIDEO PIPELINE PROCESSING    ")
    print("==================================================")
    
    for idx, (in_path, out_path) in enumerate(videos):
        print(f"\n[RUN {idx+1}/3] Processing: {in_path}")
        if os.path.exists(in_path):
            run_pipeline(video_path=in_path, output_path=out_path, show_preview=False)
            print(f"-> Saved output to: {out_path}")
        else:
            print(f"-> Error: Input file not found: {in_path}")
            
    print("\n==================================================")
    print("            BATCH PROCESSING COMPLETED            ")
    print("==================================================")
