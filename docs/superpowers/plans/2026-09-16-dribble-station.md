# Dribble Station Implementation Plan

> **For agentic workers:** Execute inline in one pass. No per-task human review. No commits unless asked. One review at the end.

**Goal:** Local OpenCV dribble station: saved corridor + ball color, finish-line win, out-of-bounds red + buzzer, retry with R.

**Architecture:** Pure geometry and round engine (tested without a camera). OpenCV only at tracker/overlay/main. Calibration JSON on disk.

**Tech Stack:** Python 3.10+, opencv-python, numpy, pytest, macOS `afplay` for the buzzer.

## Global Constraints

- All local. Do not edit `challenges/01-pose`.
- Same progress schema as pose, `id` is `dribble`, 1/1 on clear.
- Camera not mirrored. Fail = red `OUT` + buzzer once. `R` retries.
- Calibration persisted; `E` re-edits.

## File map

- `challenges/02-dribble/dribble_station/{geometry,tracker,round,calibration,progress,overlay,audio}.py`
- `challenges/02-dribble/main.py`
- `challenges/02-dribble/tests/...`
- `challenges/02-dribble/assets/buzzer.wav` (generated)
- `challenges/02-dribble/{requirements.txt,README.md,pytest.ini}`

## Tasks

1. Geometry TDD: polygon, `t` along midline, start zone, finish cross.
2. Tracker TDD: HSV from a BGR sample, largest blob on a fake image.
3. Round engine TDD: idle / arm / out / clear / lost ball / restart.
4. Calibration + progress load/save TDD.
5. Overlay, buzzer, main loop, README. Update root README table.
6. pytest + detector-free checks. Final review once.
