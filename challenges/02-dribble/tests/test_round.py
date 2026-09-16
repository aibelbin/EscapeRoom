from dribble_station.geometry import Corridor
from dribble_station.round import RoundEngine

CORRIDOR = Corridor(
    left_near=(100.0, 50.0),
    left_far=(100.0, 450.0),
    right_near=(300.0, 50.0),
    right_far=(300.0, 450.0),
)


def test_idle_until_ball_in_start_zone():
    engine = RoundEngine(CORRIDOR)
    state = engine.update((200.0, 300.0))
    assert state.phase == "idle"
    state = engine.update((200.0, 80.0))
    assert state.phase == "running"


def test_out_of_bounds_after_start():
    engine = RoundEngine(CORRIDOR)
    engine.update((200.0, 80.0))
    state = engine.update((20.0, 200.0))
    assert state.phase == "out"
    assert state.should_buzz is True
    again = engine.update((20.0, 200.0))
    assert again.should_buzz is False


def test_finish_clears_station():
    engine = RoundEngine(CORRIDOR)
    engine.update((200.0, 80.0))
    engine.update((200.0, 400.0))
    state = engine.update((200.0, 460.0))
    assert state.phase == "clear"


def test_missing_ball_does_not_fail():
    engine = RoundEngine(CORRIDOR)
    engine.update((200.0, 80.0))
    state = engine.update(None)
    assert state.phase == "running"
    assert state.prompt == "Find the ball"


def test_restart_after_out():
    engine = RoundEngine(CORRIDOR)
    engine.update((200.0, 80.0))
    engine.update((20.0, 200.0))
    engine.restart()
    state = engine.update((200.0, 80.0))
    assert state.phase == "running"
