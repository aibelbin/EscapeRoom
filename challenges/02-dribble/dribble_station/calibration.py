from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from dribble_station.geometry import Corridor, Point


@dataclass(frozen=True)
class Calibration:
    corridor: Corridor
    hsv_lower: tuple[int, int, int]
    hsv_upper: tuple[int, int, int]


def save_calibration(
    path: Path,
    corridor: Corridor,
    hsv_lower: tuple[int, int, int],
    hsv_upper: tuple[int, int, int],
) -> None:
    payload = {
        "left_near": list(corridor.left_near),
        "left_far": list(corridor.left_far),
        "right_near": list(corridor.right_near),
        "right_far": list(corridor.right_far),
        "hsv_lower": list(hsv_lower),
        "hsv_upper": list(hsv_upper),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n")


def load_calibration(path: Path) -> Calibration:
    data = json.loads(path.read_text())
    corridor = Corridor(
        left_near=_point(data["left_near"]),
        left_far=_point(data["left_far"]),
        right_near=_point(data["right_near"]),
        right_far=_point(data["right_far"]),
    )
    return Calibration(
        corridor=corridor,
        hsv_lower=_hsv(data["hsv_lower"]),
        hsv_upper=_hsv(data["hsv_upper"]),
    )


def _point(value) -> Point:
    return (float(value[0]), float(value[1]))


def _hsv(value) -> tuple[int, int, int]:
    return (int(value[0]), int(value[1]), int(value[2]))
