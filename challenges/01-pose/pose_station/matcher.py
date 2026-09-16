from pose_station.angles import angle_deg

IN_POSE_THRESHOLD = 0.80
VISIBILITY_MIN = 0.5

JOINT_TRIPLES: dict[str, tuple[str, str, str]] = {
    "left_elbow": ("left_shoulder", "left_elbow", "left_wrist"),
    "right_elbow": ("right_shoulder", "right_elbow", "right_wrist"),
    "left_shoulder": ("left_elbow", "left_shoulder", "left_hip"),
    "right_shoulder": ("right_elbow", "right_shoulder", "right_hip"),
    "left_hip": ("left_shoulder", "left_hip", "left_knee"),
    "right_hip": ("right_shoulder", "right_hip", "right_knee"),
    "left_knee": ("left_hip", "left_knee", "left_ankle"),
    "right_knee": ("right_hip", "right_knee", "right_ankle"),
}

Landmark = tuple[float, float, float]


def _point(landmarks: dict[str, Landmark], name: str) -> tuple[float, float] | None:
    data = landmarks.get(name)
    if data is None or data[2] < VISIBILITY_MIN:
        return None
    return (data[0], data[1])


def score_pose(
    landmarks: dict[str, Landmark],
    pose_angles: dict[str, dict[str, float]],
) -> float:
    if not pose_angles:
        return 0.0
    matched = 0
    for name, spec in pose_angles.items():
        triple = JOINT_TRIPLES.get(name)
        if triple is None:
            continue
        a = _point(landmarks, triple[0])
        b = _point(landmarks, triple[1])
        c = _point(landmarks, triple[2])
        if a is None or b is None or c is None:
            continue
        error = abs(angle_deg(a, b, c) - spec["target"])
        if error <= spec["tolerance"]:
            matched += 1
    return matched / len(pose_angles)


def is_in_pose(score: float) -> bool:
    return score >= IN_POSE_THRESHOLD
