from pose_station.matcher import IN_POSE_THRESHOLD, is_in_pose, score_pose

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


def test_straight_elbows_match_standing_arms():
    pose = {
        "left_elbow": {"target": 180.0, "tolerance": 20.0},
        "right_elbow": {"target": 180.0, "tolerance": 20.0},
    }
    score = score_pose(STANDING, pose)
    assert score == 1.0
    assert is_in_pose(score)


def test_bent_elbow_targets_do_not_match_standing():
    pose = {
        "left_elbow": {"target": 90.0, "tolerance": 15.0},
        "right_elbow": {"target": 90.0, "tolerance": 15.0},
    }
    score = score_pose(STANDING, pose)
    assert score == 0.0
    assert not is_in_pose(score)


def test_low_visibility_joint_is_skipped():
    landmarks = dict(STANDING)
    landmarks["left_wrist"] = (0.40, 0.55, 0.1)
    pose = {
        "left_elbow": {"target": 180.0, "tolerance": 20.0},
        "right_elbow": {"target": 180.0, "tolerance": 20.0},
        "left_knee": {"target": 180.0, "tolerance": 20.0},
    }
    assert score_pose(landmarks, pose) == 1.0


def test_threshold_is_sixty_five_percent():
    assert IN_POSE_THRESHOLD == 0.65
    assert is_in_pose(0.65)
    assert not is_in_pose(0.64)


def test_too_few_visible_joints_scores_zero():
    landmarks = {
        "left_shoulder": (0.40, 0.25, 0.05),
        "left_elbow": (0.40, 0.40, 0.05),
        "left_wrist": (0.40, 0.55, 0.05),
    }
    pose = {
        "left_elbow": {"target": 180.0, "tolerance": 20.0},
        "right_elbow": {"target": 180.0, "tolerance": 20.0},
    }
    assert score_pose(landmarks, pose) == 0.0
