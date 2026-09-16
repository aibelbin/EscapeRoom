# Pose Station (Challenge 01) Design

Date: 2026-09-16
Status: approved

## Problem

The escape room is a physical party: one laptop per obstacle, no shared Wi-Fi we can trust. Challenge 01 is a webcam pose round. Players copy weird on-screen poses, hold them, and clear the station. Success is a full-screen green light plus a local progress file the later dashboard can ingest.

## Scope

In:

- Monorepo folder layout for future obstacles
- `challenges/01-pose` Python OpenCV + MediaPipe app
- Three preset weird poses, hold-to-pass
- Local `progress.json` written once all three are cleared
- Shared progress schema so a future dashboard can fill a bar from copied files

Out:

- Live network, FastAPI hub, POSTs, or any runtime interconnection
- Dashboard UI
- Multi-person scoring
- Auto-launch of the next obstacle

## Architecture

Each obstacle is an independent folder. Nothing talks to anything else while the room is running.

```
EscapeRoom/
  shared/progress.schema.json
  challenges/01-pose/          # this laptop only
  challenges/02-.../           # later
  dashboard/                   # later, reads copied progress files
```

`01-pose` is a fullscreen OpenCV window. MediaPipe estimates body landmarks. A matcher scores joint angles against the current target. A round engine tracks hold time and pose index. On full clear, the window goes green and `progress.json` is written beside the app.

## Game flow

1. Camera on, mirrored preview. Target stick figure and label `POSE 1 / 3`. Empty hold bar.
2. Player skeleton drawn on the live feed. Target tint: red (far), yellow (close), green (in pose).
3. Hold bar fills only while score stays at or above the match threshold for 2.0 seconds.
4. Pose cleared: brief flash, next pose loads.
5. After pose 3: full-screen green, text `POSE STATION CLEAR`, write `progress.json` once. Stay on success. `R` restarts a new run. `Q` or `Esc` quits at any time.

If nobody is in frame, show `Stand in frame`. Breaking a pose dumps the hold bar; same pose, no fail state, no penalty. Camera missing: on-screen error and retry, no crash loop.

## Pose matching

Use MediaPipe Pose landmarks. Do not require a floor mark.

Compare these joint angles (degrees at the middle point):

- left elbow (shoulder-elbow-wrist)
- right elbow
- left shoulder (elbow-shoulder-hip)
- right shoulder
- left hip (shoulder-hip-knee)
- right hip
- left knee (hip-knee-ankle)
- right knee

A pose in `poses.json` lists a target angle and tolerance per named joint. Score is the fraction of configured joints whose absolute error is within tolerance. In-pose when score >= 0.80.

Different heights and a slightly off-center body still match because angles are scale- and translation-invariant. Visibility below 0.5 on a required landmark means that joint does not count as matched this frame.

## Data

### Shared progress schema (`shared/progress.schema.json`)

Every station writes the same shape so the dashboard can fill a bar later (USB or copy, not live):

```json
{
  "id": "pose",
  "complete": true,
  "poses_cleared": 3,
  "poses_total": 3,
  "completed_at": "2026-09-16T13:38:00"
}
```

`id` is the station slug. `complete` is true only when `poses_cleared == poses_total`. `completed_at` is local ISO-8601 without timezone conversion requirements.

### Poses file (`challenges/01-pose/poses.json`)

Three poses, editable without code changes:

1. Arms in a Y
2. Stork (one leg raised)
3. Disco point (one arm up, one hand on hip)

Each pose has `id`, `label`, `hold_seconds` (2.0), `angles` (name -> `{target, tolerance}`), and `skeleton` (normalized 0-1 joint xy for drawing the ghost).

## Components

| Unit | Responsibility | Depends on |
|------|----------------|------------|
| `angles` | Angle at a joint from three 2D points | none |
| `matcher` | Score landmarks vs a pose's angle targets | `angles` |
| `poses` | Load `poses.json` | none |
| `progress` | Read/write `progress.json` to schema | none |
| `round` | Hold timer, pose index, restart, complete flag | `matcher`, `poses` |
| `overlay` | Draw camera, skeletons, hold bar, prompts, green success | `round` |
| `main` | Camera, MediaPipe, keys, retry if device missing | all of the above |

## Error handling

- No camera: message `Camera not found. Retrying...`, retry open every 2 seconds.
- MediaPipe returns no pose: `Stand in frame`, hold progress = 0.
- Low-visibility joints: those angles fail for the frame (score drops; bar may dump).
- `progress.json` already complete: still playable. `R` starts a fresh run. A new full clear overwrites the file.
- Draw/loop exceptions: log to stderr, keep trying the next frame unless quit.

## Testing

Automated (no webcam required):

- Angle math
- Matcher: in-pose, out-of-pose, missing landmarks, 0.80 threshold
- Pose file loads three poses
- Progress writer emits schema-valid JSON; complete only at 3/3
- Round engine: hold 2s to advance, dump on break, green/complete after third, `R` resets

Manual on this Mac: run `main.py`, complete three holds, confirm green screen and `progress.json`.

## Constraints

- All local. No network calls.
- Python 3.10+. Dependencies: `opencv-python`, `mediapipe`, `numpy`, `pytest` for tests.
- Window is fullscreen OpenCV, not a browser.
- One person in frame is enough.
- Do not crash-quit the station on a missing person or a broken hold.
