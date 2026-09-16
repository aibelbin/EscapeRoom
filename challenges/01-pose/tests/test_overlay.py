import numpy as np

from pose_station.overlay import draw
from pose_station.round import RoundState


def _state(**overrides) -> RoundState:
    base = dict(
        pose_index=0,
        pose_total=3,
        hold_ratio=0.4,
        score=0.5,
        in_pose=False,
        person_present=True,
        station_complete=False,
        prompt="POSE 1 / 3",
        tint="yellow",
        just_advanced=False,
    )
    base.update(overrides)
    return RoundState(**base)


def test_success_screen_is_green():
    frame = np.zeros((180, 320, 3), dtype=np.uint8)
    pose = {"label": "Arms in a Y", "skeleton": {}}
    out = draw(
        frame,
        _state(
            station_complete=True,
            prompt="POSE STATION CLEAR",
            tint="green",
            hold_ratio=1.0,
        ),
        pose,
    )
    b, g, r = (int(v) for v in out[90, 160])
    assert g > 100 and g > b and g > r


def test_hold_bar_draws_on_live_frame():
    frame = np.zeros((180, 320, 3), dtype=np.uint8)
    pose = {
        "label": "Arms in a Y",
        "skeleton": {
            "left_shoulder": [0.4, 0.3],
            "right_shoulder": [0.6, 0.3],
        },
    }
    out = draw(frame, _state(hold_ratio=1.0, tint="green"), pose)
    # hold bar sits near the bottom; a filled bar should not stay all black
    bar_row = out[168]
    assert bar_row.max() > 0
