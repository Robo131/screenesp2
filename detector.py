"""
Two-stage detection:
 1. YOLOv8 finds "person" bounding boxes in the full frame (fast).
 2. For each box, MediaPipe Pose runs on the cropped region to get a
    33-point skeleton, which is more reliable than running pose on
    the whole frame at once.
"""

from dataclasses import dataclass, field
import numpy as np
import cv2
from ultralytics import YOLO
import mediapipe as mp

import config


@dataclass
class Detection:
    box: tuple[int, int, int, int]          # x1, y1, x2, y2 in full-frame coords
    confidence: float
    keypoints: list[tuple[float, float, float]] = field(default_factory=list)
    # keypoints are (x, y, visibility) in full-frame coords, or empty if pose failed


class PersonDetector:
    def __init__(self):
        self.yolo = YOLO(config.YOLO_MODEL)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,   # each crop is treated independently
            model_complexity=config.POSE_MODEL_COMPLEXITY,
            min_detection_confidence=config.POSE_MIN_DETECTION_CONF,
            min_tracking_confidence=config.POSE_MIN_TRACKING_CONF,
        )

    def detect(self, frame: np.ndarray) -> list[Detection]:
        h, w = frame.shape[:2]
        scale = config.DOWNSCALE_FOR_DETECTION
        small = cv2.resize(frame, (int(w * scale), int(h * scale))) if scale != 1.0 else frame

        results = self.yolo(
            small,
            classes=[config.PERSON_CLASS_ID],
            conf=config.CONFIDENCE_THRESHOLD,
            device=config.DEVICE,
            verbose=False,
        )

        detections: list[Detection] = []
        if not results:
            return detections

        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])

            # scale box back up to full-frame coordinates
            x1, y1, x2, y2 = [int(v / scale) for v in (x1, y1, x2, y2)]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 <= x1 or y2 <= y1:
                continue

            keypoints = self._extract_pose(frame, x1, y1, x2, y2)
            detections.append(Detection(box=(x1, y1, x2, y2), confidence=conf, keypoints=keypoints))

        return detections

    def _extract_pose(self, frame, x1, y1, x2, y2) -> list[tuple[float, float, float]]:
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return []

        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        result = self.pose.process(crop_rgb)
        if not result.pose_landmarks:
            return []

        crop_h, crop_w = crop.shape[:2]
        points = []
        for lm in result.pose_landmarks.landmark:
            # convert from crop-relative normalized coords to full-frame pixel coords
            px = x1 + lm.x * crop_w
            py = y1 + lm.y * crop_h
            points.append((px, py, lm.visibility))
        return points

    def close(self):
        self.pose.close()


POSE_CONNECTIONS = list(mp.solutions.pose.POSE_CONNECTIONS)
