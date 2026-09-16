from __future__ import annotations

from dribble_station.geometry import Corridor
from dribble_station.tracker import hsv_range_from_bgr

SETUP_ORDER = ("left_near", "left_far", "right_near", "right_far", "ball")
SETUP_PROMPTS = {
    "left_near": "Click LEFT line, NEAR end",
    "left_far": "Click LEFT line, FAR end",
    "right_near": "Click RIGHT line, NEAR end",
    "right_far": "Click RIGHT line, FAR end",
    "ball": "Click the BALL",
}


class SetupSession:
    def __init__(self):
        self.points: dict[str, tuple[float, float]] = {}
        self.ball_bgr: tuple[int, int, int] | None = None
        self.index = 0

    @property
    def prompt(self) -> str:
        if self.ready:
            return "Enter to save calibration"
        return SETUP_PROMPTS[SETUP_ORDER[self.index]]

    @property
    def ready(self) -> bool:
        return self.index >= len(SETUP_ORDER)

    def click(self, x: int, y: int, bgr: tuple[int, int, int]) -> None:
        if self.ready:
            return
        name = SETUP_ORDER[self.index]
        self.points[name] = (float(x), float(y))
        if name == "ball":
            self.ball_bgr = bgr
        self.index += 1

    def corridor(self) -> Corridor:
        return Corridor(
            left_near=self.points["left_near"],
            left_far=self.points["left_far"],
            right_near=self.points["right_near"],
            right_far=self.points["right_far"],
        )

    def hsv_range(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        if self.ball_bgr is None:
            raise ValueError("ball color not sampled")
        return hsv_range_from_bgr(self.ball_bgr)
