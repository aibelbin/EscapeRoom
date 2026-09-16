import cv2
import numpy as np

from pose_station.round import RoundState

TINT_BGR = {
    "red": (40, 40, 200),
    "yellow": (40, 200, 220),
    "green": (40, 200, 40),
}
SUCCESS_BGR = (0, 180, 0)
HUD = (245, 245, 245)
PANEL = (24, 24, 24)

BONES = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
]


def message_frame(text: str, size: tuple[int, int] = (720, 1280)) -> np.ndarray:
    height, width = size
    frame = np.full((height, width, 3), 18, dtype=np.uint8)
    _put_center(frame, text, (width // 2, height // 2), HUD, scale=1.1)
    return frame


def draw(
    frame: np.ndarray,
    state: RoundState,
    pose: dict,
    player: dict | None = None,
) -> np.ndarray:
    out = frame.copy()
    height, width = out.shape[:2]
    if state.station_complete:
        out[:] = SUCCESS_BGR
        _put_center(out, "POSE STATION CLEAR", (width // 2, height // 2), (255, 255, 255), scale=1.6)
        _put_center(
            out,
            "R restart    Q quit",
            (width // 2, min(height - 40, height // 2 + 70)),
            (230, 255, 230),
            scale=0.7,
        )
        return out

    tint = TINT_BGR.get(state.tint, TINT_BGR["red"])
    _draw_named_skeleton(out, player, tint, 0, 0, width, height, thickness=3)
    _draw_target_panel(out, pose.get("skeleton") or {}, tint)
    _draw_hud(out, state, pose, tint)
    if state.just_advanced and not state.station_complete:
        flash = np.full_like(out, (40, 220, 40))
        cv2.addWeighted(flash, 0.35, out, 0.65, 0, out)
    return out


def _draw_target_panel(frame: np.ndarray, skeleton: dict, tint: tuple[int, int, int]) -> None:
    height, width = frame.shape[:2]
    panel_w = max(120, int(width * 0.28))
    x0 = width - panel_w - 16
    y0 = 70
    x1 = width - 16
    y1 = height - 50
    overlay = frame.copy()
    cv2.rectangle(overlay, (x0, y0), (x1, y1), PANEL, -1)
    cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, frame)
    cv2.rectangle(frame, (x0, y0), (x1, y1), tint, 2)
    pad = 24
    _draw_named_skeleton(
        frame,
        {name: (xy[0], xy[1], 1.0) for name, xy in skeleton.items()},
        tint,
        x0 + pad,
        y0 + pad,
        (x1 - x0) - pad * 2,
        (y1 - y0) - pad * 2,
        thickness=3,
    )


def _draw_named_skeleton(
    frame: np.ndarray,
    landmarks: dict | None,
    color: tuple[int, int, int],
    x: int,
    y: int,
    w: int,
    h: int,
    thickness: int,
) -> None:
    if not landmarks or w <= 0 or h <= 0:
        return
    points: dict[str, tuple[int, int]] = {}
    for name, data in landmarks.items():
        px, py = data[0], data[1]
        vis = data[2] if len(data) > 2 else 1.0
        if vis < 0.5:
            continue
        points[name] = (int(x + px * w), int(y + py * h))
    for a, b in BONES:
        if a in points and b in points:
            cv2.line(frame, points[a], points[b], color, thickness, cv2.LINE_AA)
    for point in points.values():
        cv2.circle(frame, point, thickness + 2, color, -1, cv2.LINE_AA)


def _draw_hud(
    frame: np.ndarray,
    state: RoundState,
    pose: dict,
    tint: tuple[int, int, int],
) -> None:
    height, width = frame.shape[:2]
    label = pose.get("label", "")
    cv2.putText(
        frame,
        state.prompt,
        (24, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        HUD,
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        label,
        (24, 74),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        tint,
        2,
        cv2.LINE_AA,
    )
    bar_x, bar_y = 24, height - 8
    bar_h = 12
    bar_w = width - 48
    cv2.rectangle(frame, (bar_x, bar_y - bar_h), (bar_x + bar_w, bar_y), (40, 40, 40), -1)
    filled = int(bar_w * max(0.0, min(1.0, state.hold_ratio)))
    if filled > 0:
        cv2.rectangle(
            frame,
            (bar_x, bar_y - bar_h),
            (bar_x + filled, bar_y),
            tint,
            -1,
        )


def _put_center(
    frame: np.ndarray,
    text: str,
    center: tuple[int, int],
    color: tuple[int, int, int],
    scale: float = 1.0,
) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), _ = cv2.getTextSize(text, font, scale, 2)
    origin = (center[0] - tw // 2, center[1] + th // 2)
    cv2.putText(frame, text, origin, font, scale, color, 2, cv2.LINE_AA)
