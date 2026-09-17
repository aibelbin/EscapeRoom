from __future__ import annotations

import json
from pathlib import Path


class LeaderboardError(ValueError):
    pass


def load(path: Path) -> dict:
    if not path.is_file():
        return {"entries": []}
    data = json.loads(path.read_text())
    entries = data.get("entries")
    if not isinstance(entries, list):
        return {"entries": []}
    return {"entries": entries}


def ranked(entries: list[dict]) -> list[dict]:
    return sorted(entries, key=lambda row: (int(row["time_ms"]), str(row["finished_at"])))


def add_finish(path: Path, *, name: str, time_ms: int, finished_at: str) -> dict:
    cleaned = name.strip()
    if not cleaned:
        raise LeaderboardError("Need a name")
    if int(time_ms) <= 0:
        raise LeaderboardError("Start the clock first")
    data = load(path)
    data["entries"].append(
        {
            "name": cleaned,
            "time_ms": int(time_ms),
            "finished_at": finished_at,
        }
    )
    path.write_text(json.dumps(data, indent=2) + "\n")
    return {"entries": ranked(data["entries"])}
