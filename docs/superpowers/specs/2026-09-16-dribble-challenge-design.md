# Dribble Station (Challenge 02) Design

Date: 2026-09-16
Status: approved

## Problem

Second physical-room laptop. A webcam looks at a cone lane. The player dribbles a ball from the near end to a far finish line, staying between two side lines. Leaving the corridor after the run starts is elimination: red screen + one buzzer. They can retry. Clearing writes local `progress.json`. Pose station is unchanged.

## Scope

In:

- `challenges/02-dribble` OpenCV app
- Click-once calibration of two side lines and ball color, saved to `calibration.json`
- Edit mode to redo calibration
- HSV blob tracking of the ball
- Finish-line win, out-of-bounds fail with red + buzzer
- Local `progress.json` using the shared schema (`id: "dribble"`)

Out:

- Network, dashboard UI, cone counting, pose-station edits
- Assuming a specific ball color (sampled at setup)

## Architecture

Independent folder, no runtime coupling to pose.

```
challenges/02-dribble/
  calibration.json    # created on this laptop
  progress.json       # on clear
  assets/buzzer.wav
```

Camera is not mirrored. Corridor is a polygon from four clicks: left near, left far, right near, right far. Finish is the far edge. Start zone is the near third along the corridor axis.

## Game flow

1. Missing calibration → setup. Otherwise play.
2. Idle until the ball is inside the near third. Then the run is armed.
3. Ball center outside the polygon while armed → `OUT`, red fill, buzzer once. `R` retries.
4. Ball stays inside and crosses the far edge → green `DRIBBLE STATION CLEAR`, write progress once.
5. Ball lost → `Find the ball`. Do not fail or win on a missing blob.
6. `E` edit lines (and re-click the ball). Enter saves. Esc cancels if a previous file exists.
7. `Q` quits (during setup Esc cancels edit; with no file yet, Esc also quits).

## Tracking

BGR click → HSV sample. Range about H±12, S±50, V±50 (hue wraps). Each frame: largest contour above a minimum area. Center of that contour is the ball.

Progress `t` is the projection of the ball onto the midline from near midpoint to far midpoint. Start zone: inside and `t <= 1/3`. Finish: armed, inside, previous `t < 1.0` and current `t >= 1.0`.

## Data

`calibration.json`:

```json
{
  "left_near": [x, y],
  "left_far": [x, y],
  "right_near": [x, y],
  "right_far": [x, y],
  "hsv_lower": [h, s, v],
  "hsv_upper": [h, s, v]
}
```

`progress.json`: `{ "id": "dribble", "complete": true, "poses_cleared": 1, "poses_total": 1, "completed_at": "..." }`

## Error handling

No camera: retry message every 2s. Failed frame read: same. Buzzer missing or `afplay` fails: still show red, log, no crash. Loop exceptions: log to stderr, continue. `Q` always available in play/fail/clear.

## Testing

Geometry and round engine with fake points (no webcam). Tracker on a synthetic colored circle. Manual: calibrate, step out (red + buzz), `R`, finish (green + progress file).

## Constraints

- All local. Python 3.10+. `opencv-python`, `numpy`, `pytest`. Buzzer via `afplay` on macOS (this party laptop).
- Do not change `challenges/01-pose`.
- No git commits unless asked. One review after the station works.
