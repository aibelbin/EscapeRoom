import numpy as np

from dribble_station.tracker import find_ball, hsv_range_from_bgr


def test_find_ball_on_synthetic_orange_circle():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    center = (160, 120)
    import cv2

    cv2.circle(frame, center, 18, (0, 140, 255), -1)
    sample = tuple(int(v) for v in frame[center[1], center[0]])
    lower, upper = hsv_range_from_bgr(sample)
    found = find_ball(frame, lower, upper)
    assert found is not None
    assert abs(found[0] - center[0]) < 8
    assert abs(found[1] - center[1]) < 8


def test_find_ball_returns_none_on_empty_frame():
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    lower, upper = hsv_range_from_bgr((0, 140, 255))
    assert find_ball(frame, lower, upper) is None
