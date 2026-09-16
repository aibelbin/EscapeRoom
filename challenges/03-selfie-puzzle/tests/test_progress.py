import json
from pathlib import Path

from progress import write_progress


def test_write_progress_selfie(tmp_path: Path):
    path = tmp_path / "progress.json"
    payload = write_progress(
        path,
        station_id="selfie",
        cleared=1,
        total=1,
        completed_at="2026-09-16T23:00:00",
    )
    assert payload["id"] == "selfie"
    assert payload["complete"] is True
    assert json.loads(path.read_text()) == payload
