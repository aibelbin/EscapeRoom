from dribble_station.geometry import (
    Corridor,
    crossed_finish,
    in_start_zone,
    point_in_polygon,
    progress_t,
)

# A rectangular corridor: x 100-300, y 50 (near) to 450 (far)
LEFT_NEAR = (100.0, 50.0)
LEFT_FAR = (100.0, 450.0)
RIGHT_NEAR = (300.0, 50.0)
RIGHT_FAR = (300.0, 450.0)
CORRIDOR = Corridor(LEFT_NEAR, LEFT_FAR, RIGHT_NEAR, RIGHT_FAR)


def test_point_inside_corridor():
    assert point_in_polygon((200.0, 250.0), CORRIDOR.polygon)


def test_point_outside_corridor():
    assert not point_in_polygon((20.0, 250.0), CORRIDOR.polygon)


def test_progress_near_is_zero_far_is_one():
    assert progress_t((200.0, 50.0), CORRIDOR) == 0.0
    assert abs(progress_t((200.0, 450.0), CORRIDOR) - 1.0) < 1e-6


def test_start_zone_is_near_third():
    assert in_start_zone(0.0)
    assert in_start_zone(1.0 / 3.0)
    assert not in_start_zone(0.5)


def test_crossed_finish_detects_crossing():
    assert crossed_finish(0.9, 1.05)
    assert not crossed_finish(0.5, 0.6)
    assert not crossed_finish(1.1, 1.2)
