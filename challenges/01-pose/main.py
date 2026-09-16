from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

from pose_station.detector import PoseDetector
from pose_station.overlay import draw, message_frame
from pose_station.poses import load_poses
from pose_station.progress import write_progress
from pose_station.round import RoundEngine

ROOT = Path(__file__).resolve().parent
WINDOW = "Pose Station"
STATION_ID = "pose"
MAX_DT = 0.1
RETRY_SECONDS = 2.0


def open_camera() -> cv2.VideoCapture | None:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return cap
    cap.release()
    return None


def _show_retry(engine: RoundEngine) -> str | None:
    frame = message_frame("Camera not found. Retrying...")
    cv2.imshow(WINDOW, frame)
    return _handle_keys(engine)


def run() -> int:
    poses = load_poses(ROOT / "poses.json")
    engine = RoundEngine(poses)
    progress_path = ROOT / "progress.json"
    wrote = False
    pose_model = PoseDetector()

    cap: cv2.VideoCapture | None = None
    last_retry = 0.0
    prev = time.monotonic()

    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    try:
        while True:
            now = time.monotonic()
            dt = min(MAX_DT, max(0.0, now - prev))
            prev = now

            try:
                if cap is None:
                    if now - last_retry >= RETRY_SECONDS:
                        cap = open_camera()
                        last_retry = now
                    if cap is None:
                        if _show_retry(engine) == "quit":
                            return 0
                        continue

                ok, frame = cap.read()
                if not ok:
                    cap.release()
                    cap = None
                    last_retry = now
                    if _show_retry(engine) == "quit":
                        return 0
                    continue

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                landmarks = pose_model.detect(rgb)

                state = engine.update(dt, landmarks)
                if state.station_complete and not wrote:
                    write_progress(
                        progress_path,
                        station_id=STATION_ID,
                        cleared=state.pose_total,
                        total=state.pose_total,
                        completed_at=datetime.now().isoformat(timespec="seconds"),
                    )
                    wrote = True

                canvas = draw(frame, state, engine.current_pose, player=landmarks)
                cv2.imshow(WINDOW, canvas)
                key = _handle_keys(engine)
                if key == "quit":
                    return 0
                if key == "restart":
                    wrote = False
            except Exception as exc:
                print(f"frame error: {exc}", file=sys.stderr)
                if _handle_keys(engine) == "quit":
                    return 0
    finally:
        pose_model.close()
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()


def _handle_keys(engine: RoundEngine) -> str | None:
    key = cv2.waitKey(1) & 0xFF
    if key in (ord("q"), ord("Q"), 27):
        return "quit"
    if key in (ord("r"), ord("R")):
        engine.restart()
        return "restart"
    return None


if __name__ == "__main__":
    raise SystemExit(run())
