NAME_TO_INDEX = {
    "nose": 0,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
}


def _score(point) -> float:
    value = getattr(point, "visibility", None)
    if value is None:
        value = getattr(point, "presence", None)
    if value is None:
        return 1.0
    return float(value)


def from_pose_landmarks(landmarks) -> dict[str, tuple[float, float, float]]:
    mapped: dict[str, tuple[float, float, float]] = {}
    count = len(landmarks)
    for name, index in NAME_TO_INDEX.items():
        if index >= count:
            continue
        point = landmarks[index]
        if point.x is None or point.y is None:
            continue
        mapped[name] = (float(point.x), float(point.y), _score(point))
    return mapped
