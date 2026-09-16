from __future__ import annotations

from dataclasses import dataclass

Point = tuple[float, float]


@dataclass(frozen=True)
class Corridor:
    left_near: Point
    left_far: Point
    right_near: Point
    right_far: Point

    @property
    def polygon(self) -> list[Point]:
        return [self.left_near, self.left_far, self.right_far, self.right_near]

    @property
    def near_mid(self) -> Point:
        return _mid(self.left_near, self.right_near)

    @property
    def far_mid(self) -> Point:
        return _mid(self.left_far, self.right_far)


def _mid(a: Point, b: Point) -> Point:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        intersects = (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
        if intersects:
            inside = not inside
        j = i
    return inside


def progress_t(point: Point, corridor: Corridor) -> float:
    nx, ny = corridor.near_mid
    fx, fy = corridor.far_mid
    vx, vy = fx - nx, fy - ny
    length2 = vx * vx + vy * vy
    if length2 == 0:
        return 0.0
    px, py = point[0] - nx, point[1] - ny
    t = (px * vx + py * vy) / length2
    return t


def in_start_zone(t: float) -> bool:
    return t <= (1.0 / 3.0)


def crossed_finish(prev_t: float, t: float) -> bool:
    return prev_t < 1.0 <= t
