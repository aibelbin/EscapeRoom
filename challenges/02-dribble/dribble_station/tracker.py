from __future__ import annotations

import cv2
import numpy as np

BGR = tuple[int, int, int]
HSV = tuple[int, int, int]


def hsv_range_from_bgr(
    bgr: BGR,
    h_pad: int = 12,
    s_pad: int = 50,
    v_pad: int = 50,
) -> tuple[HSV, HSV]:
    pixel = np.uint8([[bgr]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0, 0]
    h, s, v = (int(x) for x in hsv)
    lower = (max(0, h - h_pad), max(0, s - s_pad), max(0, v - v_pad))
    upper = (min(179, h + h_pad), min(255, s + s_pad), min(255, v + v_pad))
    return lower, upper


def find_ball(
    frame: np.ndarray,
    lower: HSV,
    upper: HSV,
    min_area: float = 80.0,
) -> tuple[float, float] | None:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    biggest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(biggest) < min_area:
        return None
    m = cv2.moments(biggest)
    if m["m00"] == 0:
        return None
    return (m["m10"] / m["m00"], m["m01"] / m["m00"])
