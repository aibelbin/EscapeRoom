# Selfie Puzzle

Third laptop in the room. Someone stands in front of the webcam, hits **Start**, and drags squares of their own face onto an empty board.

3×3 jigsaw. Camera optional. Green screen + local `progress.json`. No Wi-Fi.

Python 3.12 is enough. No venv, no pip.

---

## Night of

```bash
cd challenges/03-selfie-puzzle
python3.12 main.py
```

That opens [http://127.0.0.1:8765/](http://127.0.0.1:8765/). Chrome or Safari. Allow the camera when the browser asks.

Tape the laptop so the guest’s head fills the polaroid. Leave it on that page until the room is done.

`Ctrl+C` in the terminal stops the server.

---

## How it plays

1. Live preview in the polaroid. If the camera fails, a backup photo shows instead.
2. **Start** snaps a square crop and cuts it into 9 squares in a tray.
3. Drag pieces onto the empty 3×3 board. Drop on an occupied cell to swap. Drop off the board to return a piece to the tray.
4. Screen goes green: **SELFIE STATION CLEAR**. `progress.json` is written in this folder.
5. **Again** takes a new photo for the next guest.

---

## Controls

| Input | What it does |
| --- | --- |
| Drag a piece onto a cell | Place it (swap if the cell is taken) |
| Drop off the board | Return it to the tray |
| **Again** | New photo, new scramble |

---

## Test the fallback

Use this when you want the backup photo on purpose, without fighting the webcam:

[http://127.0.0.1:8765/?fallback=1](http://127.0.0.1:8765/?fallback=1)

You should see the goofy stock face, a gold status line that says `Using fallback photo`, then the tray of squares after **Start**.

It also falls back on its own if:

- the browser blocks the camera
- `getUserMedia` errors or hangs (~2.5s)
- the video never actually starts

---

## After a clear

This folder gets `progress.json`:

```json
{
  "id": "selfie",
  "complete": true,
  "poses_cleared": 1,
  "poses_total": 1,
  "completed_at": "2026-09-16T23:46:21"
}
```

Copy that file later if you want it on the end-of-room dashboard. It is gitignored.

---

## Tests

```bash
cd challenges/03-selfie-puzzle
node --test tests/puzzle.test.js
python3.12 -m pytest tests/test_progress.py -v
```
