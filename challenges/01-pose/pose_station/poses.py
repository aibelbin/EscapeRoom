import json
from pathlib import Path


def load_poses(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError("poses.json must be a list of poses")
    return data
