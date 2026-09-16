import json
from pathlib import Path


def write_progress(
    path: Path,
    *,
    station_id: str,
    cleared: int,
    total: int,
    completed_at: str,
) -> dict:
    payload = {
        "id": station_id,
        "complete": cleared == total and total > 0,
        "poses_cleared": cleared,
        "poses_total": total,
        "completed_at": completed_at,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload
