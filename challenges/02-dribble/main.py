from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import cv2

from dribble_station.audio import ensure_buzzer, play_buzzer
from dribble_station.calibration import load_calibration, save_calibration
from dribble_station.overlay import draw_play, draw_setup, message_frame
from dribble_station.progress import write_progress
from dribble_station.round import RoundEngine
from dribble_station.setup import SetupSession
from dribble_station.tracker import find_ball

ROOT = Path(__file__).resolve().parent
WINDOW = "Dribble Station"
STATION_ID = "dribble"
RETRY_SECONDS = 2.0
CAL_PATH = ROOT / "calibration.json"
PROGRESS_PATH = ROOT / "progress.json"


def open_camera() -> cv2.VideoCapture | None:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return cap
    cap.release()
    return None


class App:
    def __init__(self):
        self.frame = None
        self.setup: SetupSession | None = None
        self.engine: RoundEngine | None = None
        self.hsv_lower = None
        self.hsv_upper = None
        self.wrote = False
        self._had_calibration = CAL_PATH.is_file()
        if self._had_calibration:
            self._apply_calibration()
        else:
            self.setup = SetupSession()

    def _apply_calibration(self) -> None:
        loaded = load_calibration(CAL_PATH)
        self.engine = RoundEngine(loaded.corridor)
        self.hsv_lower = loaded.hsv_lower
        self.hsv_upper = loaded.hsv_upper
        self.wrote = False

    def on_mouse(self, event, x, y, _flags, _userdata) -> None:
        if event != cv2.EVENT_LBUTTONDOWN or self.setup is None or self.frame is None:
            return
        h, w = self.frame.shape[:2]
        if not (0 <= x < w and 0 <= y < h):
            return
        bgr = tuple(int(v) for v in self.frame[y, x])
        self.setup.click(x, y, bgr)

    def save_setup(self) -> None:
        if self.setup is None or not self.setup.ready:
            return
        lower, upper = self.setup.hsv_range()
        save_calibration(CAL_PATH, self.setup.corridor(), lower, upper)
        self.setup = None
        self._had_calibration = True
        self._apply_calibration()


def run() -> int:
    import time

    ensure_buzzer()
    app = App()
    cap: cv2.VideoCapture | None = None
    last_retry = 0.0

    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(WINDOW, app.on_mouse)

    try:
        while True:
            now = time.monotonic()
            try:
                if cap is None:
                    if now - last_retry >= RETRY_SECONDS:
                        cap = open_camera()
                        last_retry = now
                    if cap is None:
                        cv2.imshow(WINDOW, message_frame("Camera not found. Retrying..."))
                        if _quit_pressed():
                            return 0
                        continue

                ok, frame = cap.read()
                if not ok:
                    cap.release()
                    cap = None
                    last_retry = now
                    cv2.imshow(WINDOW, message_frame("Camera not found. Retrying..."))
                    if _quit_pressed():
                        return 0
                    continue

                app.frame = frame
                canvas = _draw(app, frame)
                cv2.imshow(WINDOW, canvas)
                action = _handle_keys(app)
                if action == "quit":
                    return 0
            except Exception as exc:
                print(f"frame error: {exc}", file=sys.stderr)
                if _quit_pressed():
                    return 0
    finally:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()


def _draw(app: App, frame):
    if app.setup is not None:
        return draw_setup(frame, app.setup.points, app.setup.prompt)
    ball = find_ball(frame, app.hsv_lower, app.hsv_upper)
    state = app.engine.update(ball)
    if state.should_buzz:
        play_buzzer()
    if state.phase == "clear" and not app.wrote:
        write_progress(
            PROGRESS_PATH,
            station_id=STATION_ID,
            cleared=1,
            total=1,
            completed_at=datetime.now().isoformat(timespec="seconds"),
        )
        app.wrote = True
    return draw_play(frame, app.engine.corridor, state)


def _handle_keys(app: App) -> str | None:
    key = cv2.waitKey(1) & 0xFF
    if key in (ord("q"), ord("Q")):
        return "quit"
    if key == 27:
        if app.setup is not None and app._had_calibration:
            app.setup = None
            return None
        return "quit"
    if key in (13, 10) and app.setup is not None:
        app.save_setup()
        return None
    if key in (ord("e"), ord("E")) and app.setup is None:
        app.setup = SetupSession()
        return None
    if key in (ord("r"), ord("R")) and app.engine is not None and app.setup is None:
        app.engine.restart()
        app.wrote = False
        return "restart"
    return None


def _quit_pressed() -> bool:
    key = cv2.waitKey(1) & 0xFF
    return key in (ord("q"), ord("Q"), 27)


if __name__ == "__main__":
    raise SystemExit(run())
