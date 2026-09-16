import json
from pathlib import Path

from pose_station.poses import load_poses


def test_load_poses_reads_required_fields(tmp_path: Path):
    payload = [
        {
            "id": "y",
            "label": "Arms in a Y",
            "hold_seconds": 2.0,
            "angles": {"left_elbow": {"target": 170.0, "tolerance": 35.0}},
            "skeleton": {"left_wrist": [0.2, 0.1]},
        }
    ]
    path = tmp_path / "poses.json"
    path.write_text(json.dumps(payload))
    poses = load_poses(path)
    assert len(poses) == 1
    assert poses[0]["id"] == "y"
    assert poses[0]["label"] == "Arms in a Y"
    assert poses[0]["hold_seconds"] == 2.0
    assert "left_elbow" in poses[0]["angles"]
    assert poses[0]["skeleton"]["left_wrist"] == [0.2, 0.1]


def test_packaged_poses_has_three_named_poses():
    path = Path(__file__).resolve().parents[1] / "poses.json"
    poses = load_poses(path)
    assert [p["id"] for p in poses] == ["y", "stork", "disco"]
    for pose in poses:
        assert pose["label"]
        assert pose["hold_seconds"] == 2.0
        assert pose["angles"]
        assert pose["skeleton"]
