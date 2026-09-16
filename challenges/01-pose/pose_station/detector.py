from __future__ import annotations

import mediapipe as mp
import numpy as np

from pose_station.landmarks import from_pose_landmarks


def _require_macos_safe_mediapipe() -> None:
    # MediaPipe 1.0+ loads libmediapipe.dylib and creates PoseLandmarker on a
    # worker thread via ctypes. On macOS that path initializes Metal
    # (DrishtiMetalHelper) off the main thread and abort()s the process.
    major = int(mp.__version__.split(".", 1)[0])
    if major >= 1:
        raise RuntimeError(
            "MediaPipe "
            f"{mp.__version__} crashes on macOS while creating the pose model "
            "(Metal abort in DrishtiMetalHelper). Install the pinned version:\n"
            "  pip install 'mediapipe==0.10.14'"
        )


class PoseDetector:
    def __init__(self):
        _require_macos_safe_mediapipe()
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
