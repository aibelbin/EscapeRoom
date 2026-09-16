import mediapipe as mp


def test_mediapipe_pose_solution_is_available():
    assert hasattr(mp.solutions, "pose")
    assert hasattr(mp.solutions.pose, "Pose")
