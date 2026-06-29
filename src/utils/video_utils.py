# src/utils/video_utils.py

import cv2
from src.utils.config import FRAME_WIDTH, FRAME_HEIGHT


def open_video(video_path):
    return cv2.VideoCapture(video_path)


def resize_frame(frame):
    return cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))


def create_video_writer(output_path, fps, width, height):
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    return cv2.VideoWriter(output_path, fourcc, fps, (width, height))
