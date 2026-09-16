# Selfie Puzzle

Third escape-room obstacle. A local web page snaps whoever is in front of the webcam and turns that photo into a 3x3 sliding puzzle. Solve your own face. If the camera fails, a fallback photo is used. Green screen + `progress.json`. No Wi-Fi.

## Run

```bash
cd challenges/03-selfie-puzzle
python3.12 main.py
```

Opens `http://127.0.0.1:8765/`. Use Chrome or Safari. Allow the camera. Press Start.

To skip the camera and use the backup photo: `http://127.0.0.1:8765/?fallback=1`

- Click a tile next to the hole to slide it
- Arrow keys also work
- Again takes a new photo

- Click a tile next to the hole to slide it
- Arrow keys also work
- Again takes a new photo

Ctrl+C stops the server.

## Tests

```bash
cd challenges/03-selfie-puzzle
node --test tests/puzzle.test.js
python3.12 -m pytest tests/test_progress.py -v
```
