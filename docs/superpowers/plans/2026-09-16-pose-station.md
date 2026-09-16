# Pose Station Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a local OpenCV + MediaPipe pose station that clears after three held poses, shows a green screen, and writes `progress.json`.

**Architecture:** Pure functions for angles, matching, pose loading, progress I/O, and a round state machine. OpenCV/MediaPipe stay at the edge (`overlay`, `main`) so tests need no camera.

**Tech Stack:** Python 3.10+, opencv-python, mediapipe, numpy, pytest

## Global Constraints

- All local. No network calls, hub, or dashboard UI.
- Python 3.10+. Packages: `opencv-python`, `mediapipe`, `numpy`, `pytest`.
- Fullscreen OpenCV window. One person in frame is enough.
- In-pose threshold is 0.80. Default hold is 2.0 seconds. Three poses.
- `Q` / `Esc` quit. `R` restarts after (or during) a run.
- Missing person or broken hold never ends the round as a failure.
- Do not create git commits unless the user asks.
- No per-task human review. One review after everything works.

## File map

- Create: `shared/progress.schema.json`
- Create: `challenges/01-pose/requirements.txt`
- Create: `challenges/01-pose/poses.json`
- Create: `challenges/01-pose/pose_station/__init__.py`
- Create: `challenges/01-pose/pose_station/angles.py`
- Create: `challenges/01-pose/pose_station/matcher.py`
- Create: `challenges/01-pose/pose_station/poses.py`
- Create: `challenges/01-pose/pose_station/progress.py`
- Create: `challenges/01-pose/pose_station/round.py`
- Create: `challenges/01-pose/pose_station/overlay.py`
- Create: `challenges/01-pose/main.py`
- Create: `challenges/01-pose/tests/test_angles.py`
- Create: `challenges/01-pose/tests/test_matcher.py`
- Create: `challenges/01-pose/tests/test_poses.py`
- Create: `challenges/01-pose/tests/test_progress.py`
- Create: `challenges/01-pose/tests/test_round.py`
- Create: `challenges/01-pose/README.md`

---

### Task 1: Angle helper

**Files:**
- Create: `challenges/01-pose/tests/test_angles.py`
- Create: `challenges/01-pose/pose_station/__init__.py`
- Create: `challenges/01-pose/pose_station/angles.py`
- Create: `challenges/01-pose/requirements.txt`

**Interfaces:**
- Consumes: nothing
- Produces: `angle_deg(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float`

- [ ] **Step 1: Write the failing test**

```python
from pose_station.angles import angle_deg


def test_right_angle_at_origin():
    assert abs(angle_deg((1, 0), (0, 0), (0, 1)) - 90.0) < 1e-6


def test_straight_line_is_180():
    assert abs(angle_deg((0, 0), (1, 0), (2, 0)) - 180.0) < 1e-6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd challenges/01-pose && python -m pytest tests/test_angles.py -v`
Expected: FAIL with import error or missing function

- [ ] **Step 3: Write minimal implementation**

```python
import math


def angle_deg(a, b, c) -> float:
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    na = math.hypot(*ba)
    nc = math.hypot(*bc)
    if na == 0 or nc == 0:
        return 0.0
    cosine = max(-1.0, min(1.0, (ba[0] * bc[0] + ba[1] * bc[1]) / (na * nc)))
    return math.degrees(math.acos(cosine))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd challenges/01-pose && python -m pytest tests/test_angles.py -v`
Expected: PASS

---

### Task 2: Matcher

**Files:**
- Create: `challenges/01-pose/tests/test_matcher.py`
- Create: `challenges/01-pose/pose_station/matcher.py`

**Interfaces:**
- Consumes: `angle_deg`
- Produces: `IN_POSE_THRESHOLD = 0.80`, `score_pose(landmarks: dict[str, tuple[float, float, float]], pose_angles: dict) -> float`, `is_in_pose(score: float) -> bool`

Landmark dict values are `(x, y, visibility)`. Pose angles: `{name: {"target": float, "tolerance": float}}`. Names: `left_elbow`, `right_elbow`, `left_shoulder`, `right_shoulder`, `left_hip`, `right_hip`, `left_knee`, `right_knee`.

- [ ] **Step 1: Write the failing test**

Use a standing-straight landmark set. A pose that wants ~180 elbows should score high. A pose that wants 90 elbows should score low. Visibility 0.1 on a required wrist should fail that joint.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd challenges/01-pose && python -m pytest tests/test_matcher.py -v`
Expected: FAIL import

- [ ] **Step 3: Write matcher using MediaPipe-style joint triples**

- [ ] **Step 4: Run tests PASS**

---

### Task 3: Pose loader and progress writer

**Files:**
- Create: `challenges/01-pose/poses.json` (exactly 3 poses: y, stork, disco)
- Create: `shared/progress.schema.json`
- Create: `challenges/01-pose/pose_station/poses.py`
- Create: `challenges/01-pose/pose_station/progress.py`
- Create: `challenges/01-pose/tests/test_poses.py`
- Create: `challenges/01-pose/tests/test_progress.py`

**Interfaces:**
- Produces: `load_poses(path: Path) -> list[dict]`
- Produces: `write_progress(path: Path, *, station_id: str, cleared: int, total: int, completed_at: str) -> dict`

- [ ] Tests: loads 3 poses; each has id, label, hold_seconds, angles, skeleton
- [ ] Tests: `write_progress` sets `complete` true only when cleared == total; writes JSON

---

### Task 4: Round engine

**Files:**
- Create: `challenges/01-pose/pose_station/round.py`
- Create: `challenges/01-pose/tests/test_round.py`

**Interfaces:**
- Produces: `class RoundEngine` with `update(dt: float, landmarks) -> RoundState`
- `RoundState`: `pose_index`, `pose_total`, `hold_ratio`, `score`, `in_pose`, `person_present`, `station_complete`, `prompt`, `tint` (`red`|`yellow`|`green`), `just_advanced`
- `restart()` resets to pose 0, not complete
- Hold bar dumps when not in pose or no person
- After last pose hold completes: `station_complete` True, prompt `POSE STATION CLEAR`

- [ ] Tests for advance, dump, complete, restart. Use fake landmarks and tiny hold_seconds in a test pose list.

---

### Task 5: Overlay + main loop

**Files:**
- Create: `challenges/01-pose/pose_station/overlay.py`
- Create: `challenges/01-pose/main.py`
- Create: `challenges/01-pose/README.md`

**Interfaces:**
- `draw(frame, state, current_pose) -> frame` (BGR)
- `main.py`: mirror webcam, MediaPipe Pose, map landmarks, `RoundEngine.update`, draw, keys, write progress once on complete, retry camera every 2s, fullscreen

Tint colors: red `(40, 40, 200)`, yellow `(40, 200, 220)`, green `(40, 200, 40)` in BGR. Success screen fills `(0, 180, 0)`.

---

### Task 6: Verify

- [ ] `python -m pytest challenges/01-pose/tests -v` all pass
- [ ] Import `main` / overlay without running camera in tests
- [ ] README has run instructions: venv, pip, `python main.py`
