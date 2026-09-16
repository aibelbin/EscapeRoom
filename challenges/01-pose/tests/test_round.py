from pose_station.round import RoundEngine

STANDING = {
    "left_shoulder": (0.40, 0.25, 1.0),
    "right_shoulder": (0.60, 0.25, 1.0),
    "left_elbow": (0.40, 0.40, 1.0),
    "right_elbow": (0.60, 0.40, 1.0),
    "left_wrist": (0.40, 0.55, 1.0),
    "right_wrist": (0.60, 0.55, 1.0),
    "left_hip": (0.45, 0.55, 1.0),
    "right_hip": (0.55, 0.55, 1.0),
    "left_knee": (0.45, 0.75, 1.0),
    "right_knee": (0.55, 0.75, 1.0),
    "left_ankle": (0.45, 0.95, 1.0),
    "right_ankle": (0.55, 0.95, 1.0),
}

STRAIGHT_ARMS = {
    "id": "straight",
    "label": "Straight arms",
    "hold_seconds": 0.5,
    "angles": {
        "left_elbow": {"target": 180.0, "tolerance": 20.0},
        "right_elbow": {"target": 180.0, "tolerance": 20.0},
    },
    "skeleton": {},
}

BENT_ARMS = {
    "id": "bent",
    "label": "Bent arms",
    "hold_seconds": 0.5,
    "angles": {
        "left_elbow": {"target": 90.0, "tolerance": 15.0},
        "right_elbow": {"target": 90.0, "tolerance": 15.0},
    },
    "skeleton": {},
}


def test_no_person_prompts_stand_in_frame():
    engine = RoundEngine([STRAIGHT_ARMS])
    state = engine.update(0.1, None)
    assert state.person_present is False
    assert state.hold_ratio == 0.0
    assert state.prompt == "Stand in frame"
    assert state.pose_index == 0


def test_hold_completes_and_advances_pose():
    engine = RoundEngine([STRAIGHT_ARMS, BENT_ARMS])
    state = engine.update(0.5, STANDING)
    assert state.just_advanced is True
    assert state.pose_index == 1
    assert state.hold_ratio == 0.0
    assert state.station_complete is False


def test_breaking_pose_dumps_hold_bar():
    engine = RoundEngine([STRAIGHT_ARMS])
    engine.update(0.25, STANDING)
    bent = dict(STANDING)
    bent["left_wrist"] = (0.55, 0.40, 1.0)
    bent["right_wrist"] = (0.45, 0.40, 1.0)
    state = engine.update(0.1, bent)
    assert state.person_present is True
    assert state.hold_ratio == 0.0
    assert state.pose_index == 0
    assert state.station_complete is False


def test_third_hold_completes_station():
    poses = [
        {**STRAIGHT_ARMS, "id": "a"},
        {**STRAIGHT_ARMS, "id": "b"},
        {**STRAIGHT_ARMS, "id": "c"},
    ]
    engine = RoundEngine(poses)
    engine.update(0.5, STANDING)
    engine.update(0.5, STANDING)
    state = engine.update(0.5, STANDING)
    assert state.station_complete is True
    assert state.prompt == "POSE STATION CLEAR"
    assert state.tint == "green"
    assert state.pose_index == 2


def test_restart_clears_complete():
    engine = RoundEngine([STRAIGHT_ARMS])
    engine.update(0.5, STANDING)
    assert engine.update(0.0, STANDING).station_complete is True
    engine.restart()
    state = engine.update(0.0, None)
    assert state.station_complete is False
    assert state.pose_index == 0


def test_tint_red_when_far_yellow_when_half_matched():
    engine = RoundEngine([BENT_ARMS])
    far = engine.update(0.0, STANDING)
    assert far.tint == "red"

    half_pose = {
        "id": "half",
        "label": "Half",
        "hold_seconds": 0.5,
        "angles": {
            "left_elbow": {"target": 180.0, "tolerance": 20.0},
            "right_elbow": {"target": 90.0, "tolerance": 15.0},
        },
        "skeleton": {},
    }
    close = RoundEngine([half_pose]).update(0.0, STANDING)
    assert close.in_pose is False
    assert close.score == 0.5
    assert close.tint == "yellow"
