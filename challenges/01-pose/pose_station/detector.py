from __future__ import annotations

import mediapipe as mp
import numpy as np

from pose_station.landmarks import from_pose_landmarks


class PoseDetector:
    def __init__(self):
        self._pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect(self, rgb_frame: np.ndarray) -> dict[str, tuple[float, float, float]] | None:
        result = self._pose.process(np.ascontiguousarray(rgb_frame))
        if not result.pose_landmarks:
            return None
        return from_pose_landmarks(result.pose_landmarks.landmark)

    def close(self) -> None:
        self._pose.close()
