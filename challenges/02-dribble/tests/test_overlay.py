import numpy as np

from dribble_station.geometry import Corridor
from dribble_station.overlay import draw_play
from dribble_station.round import RoundState
from dribble_station.setup import SetupSession


def test_out_screen_is_red():
    frame = np.zeros((180, 320, 3), dtype=np.uint8)
    corridor = Corridor((10, 10), (10, 170), (300, 10), (300, 170))
    state = RoundState("out", "OUT", False, None, None)
    out = draw_play(frame, corridor, state)
    b, g, r = (int(v) for v in out[90, 160])
    assert r > 100 and r > g and r > b


def test_setup_five_clicks_ready():
    session = SetupSession()
    session.click(1, 2, (0, 0, 255))
    session.click(1, 80, (0, 0, 255))
    session.click(90, 2, (0, 0, 255))
    session.click(90, 80, (0, 0, 255))
    assert not session.ready
    session.click(40, 40, (0, 140, 255))
    assert session.ready
    assert session.ball_bgr == (0, 140, 255)
    lo, hi = session.hsv_range()
    assert lo[0] <= hi[0]
