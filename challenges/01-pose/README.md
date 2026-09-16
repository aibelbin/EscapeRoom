# Pose Station

First escape-room obstacle. Stand in front of this laptop, copy the five poses, hold each one until the bar fills. The screen goes green and `progress.json` is written locally. No Wi-Fi.

## Setup (once)

Use Python 3.12 (MediaPipe does not follow the newest Python immediately):

```bash
cd challenges/01-pose
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The pose model is bundled inside the MediaPipe install. No extra download.

## Run on the station laptop

```bash
cd challenges/01-pose
source .venv/bin/activate
python main.py
```

- Fullscreen webcam, mirrored
- Match the stick figure on the right
- Hold until the bottom bar fills (about 1.5 seconds)
- Watch the match percent; it turns green when you are close enough
- `R` restarts, `Q` or `Esc` quits

After all five poses, the window stays green. Copy `progress.json` later if you want it on the end-of-room dashboard.

## Tests

```bash
cd challenges/01-pose
source .venv/bin/activate
python -m pytest -v
```
