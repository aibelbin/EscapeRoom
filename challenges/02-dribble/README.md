# Dribble Station

Second escape-room obstacle. Webcam looks at a cone lane. Dribble the ball from the near end to the far finish line. Leave the two side lines after the run starts and the screen goes red with a buzzer. `R` retries. Finish in-bounds for green + `progress.json`. No Wi-Fi.

Use a ball that does not match the floor. A bright color is easiest.

## Setup (once)

Python 3.12:

```bash
cd challenges/02-dribble
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
cd challenges/02-dribble
source .venv/bin/activate
python main.py
```

First launch (or if `calibration.json` is missing):

1. Click left line near, then far
2. Click right line near, then far
3. Click the ball
4. Press Enter

That file is reused every time. Press `E` to edit the lines and ball color again.

- `R` retry after OUT or after a clear
- `Q` quit
- Esc cancels an edit if calibration already exists

Tape the webcam so it sees the whole corridor. Do not mirror the image: left on screen should be left on the floor.

## Tests

```bash
cd challenges/02-dribble
source .venv/bin/activate
python -m pytest -v
```
