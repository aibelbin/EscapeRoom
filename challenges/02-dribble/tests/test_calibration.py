import json
from pathlib import Path

from dribble_station.calibration import load_calibration, save_calibration
from dribble_station.geometry import Corridor
from dribble_station.progress import write_progress


def test_calibration_roundtrip(tmp_path: Path):
    path = tmp_path / "calibration.json"
    corridor = Corridor((1, 2), (3, 4), (5, 6), (7, 8))
    save_calibration(path, corridor, (10, 20, 30), (40, 50, 60))
    loaded = load_calibration(path)
    assert loaded.corridor == corridor
    assert loaded.hsv_lower == (10, 20, 30)
    assert loaded.hsv_upper == (40, 50, 60)


def test_write_progress_dribble(tmp_path: Path):
    path = tmp_path / "progress.json"
    payload = write_progress(
        path,
        station_id="dribble",
        cleared=1,
        total=1,
        completed_at="2026-09-16T20:00:00",
    )
    assert payload["id"] == "dribble"
    assert payload["complete"] is True
    assert json.loads(path.read_text()) == payload
