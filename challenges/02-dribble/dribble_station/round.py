from __future__ import annotations

from dataclasses import dataclass

from dribble_station.geometry import (
    Corridor,
    crossed_finish,
    in_start_zone,
    point_in_polygon,
    progress_t,
)

Point = tuple[float, float]


@dataclass(frozen=True)
class RoundState:
    phase: str
    prompt: str
    should_buzz: bool
    ball: Point | None
    t: float | None


class RoundEngine:
    def __init__(self, corridor: Corridor):
        self.corridor = corridor
        self.restart()

    def restart(self) -> None:
        self._phase = "idle"
        self._prev_t = 0.0
        self._prev_inside = False

    def update(self, ball: Point | None) -> RoundState:
        buzz = False
        t: float | None = None

        if self._phase in ("out", "clear"):
            prompt = "OUT" if self._phase == "out" else "DRIBBLE STATION CLEAR"
            return RoundState(self._phase, prompt, False, ball, None)

        if ball is None:
            prompt = "Find the ball" if self._phase == "running" else "Start at the near end"
            return RoundState(self._phase, prompt, False, None, None)

        inside = point_in_polygon(ball, self.corridor.polygon)
        t = progress_t(ball, self.corridor)

        if self._phase == "idle":
            if inside and in_start_zone(t):
                self._phase = "running"
            self._prev_t = t
            self._prev_inside = inside
            prompt = "Stay between the lines" if self._phase == "running" else "Start at the near end"
            return RoundState(self._phase, prompt, False, ball, t)

        if crossed_finish(self._prev_t, t) and self._prev_inside:
            self._phase = "clear"
        elif not inside:
            self._phase = "out"
            buzz = True

        self._prev_t = t
        self._prev_inside = inside
        prompt = {
            "running": "Stay between the lines",
            "out": "OUT",
            "clear": "DRIBBLE STATION CLEAR",
        }[self._phase]
        return RoundState(self._phase, prompt, buzz, ball, t)
