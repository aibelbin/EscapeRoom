from pose_station.angles import angle_deg


def test_right_angle_at_origin():
    assert abs(angle_deg((1, 0), (0, 0), (0, 1)) - 90.0) < 1e-6


def test_straight_line_is_180():
    assert abs(angle_deg((0, 0), (1, 0), (2, 0)) - 180.0) < 1e-6


def test_zero_length_side_returns_zero():
    assert angle_deg((0, 0), (0, 0), (1, 0)) == 0.0
