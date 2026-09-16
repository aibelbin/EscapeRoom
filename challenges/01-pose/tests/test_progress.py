import json
from pathlib import Path

from pose_station.progress import write_progress


def test_write_progress_complete_when_all_cleared(tmp_path: Path):
    path = tmp_path / "progress.json"
    payload = write_progress(
        path,
        station_id="pose",
        cleared=3,
        total=3,
        completed_at="2026-09-16T13:38:00",
    )
    assert payload == {
        "id": "pose",
        "complete": True,
        "poses_cleared": 3,
        "poses_total": 3,
        "completed_at": "2026-09-16T13:38:00",
    }
    saved = json.loads(path.read_text())
    assert saved == payload


def test_write_progress_incomplete_when_short(tmp_path: Path):
    path = tmp_path / "progress.json"
    payload = write_progress(
        path,
        station_id="pose",
        cleared=2,
        total=3,
        completed_at="2026-09-16T13:38:00",
    )
    assert payload["complete"] is False
    assert json.loads(path.read_text())["complete"] is False
