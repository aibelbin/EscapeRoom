from pose_station.landmarks import from_pose_landmarks


class _Point:
    def __init__(self, x, y, visibility=None, presence=None):
        self.x = x
        self.y = y
        self.visibility = visibility
        self.presence = presence


def test_from_pose_landmarks_maps_named_joints():
    points = [_Point(0, 0, 0) for _ in range(33)]
    points[11] = _Point(0.4, 0.25, 0.9)
    points[12] = _Point(0.6, 0.25, 0.8)
    mapped = from_pose_landmarks(points)
    assert mapped["left_shoulder"] == (0.4, 0.25, 0.9)
    assert mapped["right_shoulder"] == (0.6, 0.25, 0.8)
    assert "left_wrist" in mapped


def test_from_pose_landmarks_uses_presence_when_visibility_missing():
    points = [_Point(0, 0, visibility=None, presence=0) for _ in range(33)]
    points[11] = _Point(0.4, 0.25, visibility=None, presence=0.95)
    mapped = from_pose_landmarks(points)
    assert mapped["left_shoulder"] == (0.4, 0.25, 0.95)


def test_zero_visibility_is_treated_as_tracked():
    points = [_Point(0, 0, visibility=0.0) for _ in range(33)]
    points[11] = _Point(0.4, 0.25, visibility=0.0)
    mapped = from_pose_landmarks(points)
    assert mapped["left_shoulder"][2] == 1.0
