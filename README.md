# Escape Room

A physical party. Guests walk a sequence of obstacles. Each obstacle is a laptop (or an Arduino) that does not talk to the others.

Clear a station and the screen goes green. That laptop writes `progress.json` next to the app. Copy the files later if you want a scoreboard. There is no Wi-Fi, no hub, no live dashboard.

Python 3.12 on the Macs. Pose needs that pin because of MediaPipe.

| # | Folder | What the guest does | Tonight |
|---|--------|---------------------|---------|
| 1 | [`challenges/01-pose`](challenges/01-pose) | Copy three weird poses and hold them | Ready |
| 2 | [`challenges/02-dribble`](challenges/02-dribble) | Dribble a ball down a cone lane | Ready |
| 3 | [`challenges/03-selfie-puzzle`](challenges/03-selfie-puzzle) | Drag selfie squares onto a jigsaw board | Ready |
| 4 | [`challenges/04-laser-maze`](challenges/04-laser-maze) | Break (or don't break) laser tripwires | Arduino sketch only |

`shared/progress.schema.json` is the file shape every ready station writes. `dashboard/` is still empty.

---

## Night of

Tape each webcam, run the station, leave it up.

```bash
# Pose  —  fullscreen OpenCV
cd challenges/01-pose && source .venv/bin/activate && python main.py

# Dribble  —  fullscreen OpenCV, camera NOT mirrored
cd challenges/02-dribble && source .venv/bin/activate && python main.py

# Selfie  —  opens http://127.0.0.1:8765/ in the browser
cd challenges/03-selfie-puzzle && python3.12 main.py
```

First-time setup is in each folder's README. Pose and dribble need a venv; selfie is stdlib only.

Guests play. Stations do not know about each other. After a clear, `progress.json` is sitting in that folder (gitignored). Optional last step: copy those files onto one machine.

---

## 1. Pose

Mirrored webcam. Stick figure on the right. Hold each pose 2 seconds until the bar fills.

**Arms in a Y → Stork stand → Disco point.** Then `POSE STATION CLEAR`.

Skeleton tint is red / yellow / green as they get closer. Break the pose and the bar dumps; same pose, no fail. Empty frame says `Stand in frame`. No camera retries every 2 seconds.

Poses live in `poses.json`. Matching is MediaPipe joint angles, 80% in tolerance. Keep `mediapipe==0.10.14` — newer builds abort on macOS.

`R` restart · `Q` / `Esc` quit

---

## 2. Dribble

Top-down webcam on a cone corridor. Bright ball that is not the floor color. Left on screen must be left on the floor.

Start in the near third, stay between the lines, cross the far edge. Out after the run starts: red + one buzzer (`afplay` on macOS). Lost the blob: `Find the ball`, no fail. Clear: `DRIBBLE STATION CLEAR`.

First launch, click calibration: left near → left far → right near → right far → ball → Enter. Saved as `calibration.json`. `E` to redo. Esc cancels an edit if that file already exists.

`R` retry · `Q` quit

---

## 3. Selfie puzzle

Local page, Chrome or Safari. Polaroid preview, **Start**, then nine selfie squares in a tray under an empty 3×3 board. Drag a piece onto a cell. Occupied cell swaps. Off the board returns to the tray. Clear: `SELFIE STATION CLEAR`. **Again** for the next guest.

No camera, blocked camera, or a hung `getUserMedia` (~2.5s) → fallback photo. Force it with [`?fallback=1`](http://127.0.0.1:8765/?fallback=1).

`Ctrl+C` stops the server.

---

## 4. Laser maze

Not a laptop station yet. [`laser_module.ino`](challenges/04-laser-maze/laser_module/laser_module.ino) is one tripwire:

- LDR on digital pin 2
- 9600 baud, ~50 Hz
- Serial `1` = beam broken, `0` = intact
- Invert the `HIGH`/`LOW` check if your module is backwards

Flash it, open Serial Monitor, confirm the beam. No green screen and no `progress.json` until the maze app exists.

---

## Progress

Same JSON on every clear:

```json
{
  "id": "pose",
  "complete": true,
  "poses_cleared": 3,
  "poses_total": 3,
  "completed_at": "2026-09-16T13:38:00"
}
```

| Station | `id` | cleared / total |
|---------|------|-----------------|
| Pose | `pose` | 3 / 3 |
| Dribble | `dribble` | 1 / 1 |
| Selfie | `selfie` | 1 / 1 |

`complete` is true only when the two counts match. Timestamp is local ISO-8601, seconds, no timezone math. A new clear overwrites the file. Stations stay playable if a complete file is already there.

Also gitignored: dribble's `calibration.json`.

The dashboard, when it exists, will read these files from a USB copy — not over the network.

---

## Tests

No webcam required.

```bash
cd challenges/01-pose && source .venv/bin/activate && python -m pytest -v
cd challenges/02-dribble && source .venv/bin/activate && python -m pytest -v
cd challenges/03-selfie-puzzle && node --test tests/puzzle.test.js
cd challenges/03-selfie-puzzle && python3.12 -m pytest tests/test_progress.py -v
```
