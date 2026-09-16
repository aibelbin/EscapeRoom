import mediapipe as mp

from pose_station.detector import _require_macos_safe_mediapipe


def test_mediapipe_pose_solution_is_available():
    assert hasattr(mp.solutions, "pose")
    assert hasattr(mp.solutions.pose, "Pose")


def test_macos_safe_mediapipe_allows_pinned_version():
    _require_macos_safe_mediapipe()
