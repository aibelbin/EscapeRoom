from __future__ import annotations

import cv2
import numpy as np

from dribble_station.geometry import Corridor
from dribble_station.round import RoundState

LINE = (40, 220, 220)
FINISH = (40, 200, 40)
BALL = (40, 220, 40)
HUD = (245, 245, 245)
RED = (0, 0, 200)
GREEN = (0, 180, 0)


def message_frame(text: str, size: tuple[int, int] = (720, 1280)) -> np.ndarray:
    height, width = size
    frame = np.full((height, width, 3), 18, dtype=np.uint8)
    _put_center(frame, text, (width // 2, height // 2), HUD, 1.1)
    return frame


def draw_play(
    frame: np.ndarray,
    corridor: Corridor,
    state: RoundState,
) -> np.ndarray:
    out = frame.copy()
    height, width = out.shape[:2]
    if state.phase == "out":
        out[:] = RED
        _put_center(out, "OUT", (width // 2, height // 2), (255, 255, 255), 2.4)
        _put_center(out, "R retry    Q quit", (width // 2, height // 2 + 80), HUD, 0.8)
        return out
    if state.phase == "clear":
        out[:] = GREEN
        _put_center(out, "DRIBBLE STATION CLEAR", (width // 2, height // 2), (255, 255, 255), 1.4)
        _put_center(out, "R retry    Q quit", (width // 2, height // 2 + 70), (230, 255, 230), 0.7)
        return out

    poly = np.array(corridor.polygon, dtype=np.int32)
    cv2.polylines(out, [poly], True, LINE, 2, cv2.LINE_AA)
    far = (int(corridor.left_far[0]), int(corridor.left_far[1])), (
        int(corridor.right_far[0]),
        int(corridor.right_far[1]),
    )
    cv2.line(out, far[0], far[1], FINISH, 4, cv2.LINE_AA)
    if state.ball is not None:
        center = (int(state.ball[0]), int(state.ball[1]))
        cv2.circle(out, center, 12, BALL, 2, cv2.LINE_AA)
    cv2.putText(out, state.prompt, (24, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.0, HUD, 2, cv2.LINE_AA)
    return out


def draw_setup(frame: np.ndarray, points: dict, prompt: str) -> np.ndarray:
    out = frame.copy()
    if "left_near" in points and "left_far" in points:
        cv2.line(out, _i(points["left_near"]), _i(points["left_far"]), LINE, 2, cv2.LINE_AA)
    if "right_near" in points and "right_far" in points:
        cv2.line(out, _i(points["right_near"]), _i(points["right_far"]), LINE, 2, cv2.LINE_AA)
    for name, pt in points.items():
        if name == "ball":
            continue
        cv2.circle(out, _i(pt), 6, LINE, -1, cv2.LINE_AA)
    if "ball" in points:
        cv2.circle(out, _i(points["ball"]), 10, BALL, 2, cv2.LINE_AA)
    cv2.putText(out, prompt, (24, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.9, HUD, 2, cv2.LINE_AA)
    cv2.putText(
        out,
        "Enter save   Esc cancel",
        (24, 74),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        HUD,
        1,
        cv2.LINE_AA,
    )
    return out


def _i(pt) -> tuple[int, int]:
    return (int(pt[0]), int(pt[1]))


def _put_center(
    frame: np.ndarray,
    text: str,
    center: tuple[int, int],
    color: tuple[int, int, int],
    scale: float,
) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), _ = cv2.getTextSize(text, font, scale, 2)
    origin = (center[0] - tw // 2, center[1] + th // 2)
    cv2.putText(frame, text, origin, font, scale, color, 2, cv2.LINE_AA)
