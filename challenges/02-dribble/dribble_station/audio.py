from __future__ import annotations

import math
import sys
import wave
from pathlib import Path
import struct
import subprocess

DEFAULT_BUZZER = Path(__file__).resolve().parents[1] / "assets" / "buzzer.wav"


def ensure_buzzer(path: Path = DEFAULT_BUZZER) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.stat().st_size > 100:
        return path
    _write_buzzer(path)
    return path


def _write_buzzer(path: Path, seconds: float = 0.55, rate: int = 22050) -> None:
    n = int(seconds * rate)
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            t = i / rate
            a = math.copysign(1.0, math.sin(2 * math.pi * 420 * t))
            b = math.copysign(1.0, math.sin(2 * math.pi * 640 * t))
            burst = t < 0.12 or 0.18 < t < 0.32 or 0.38 < t < 0.52
            env = 1.0 if burst else 0.04
            sample = int(max(-1.0, min(1.0, (0.45 * a + 0.35 * b) * env)) * 31000)
            frames += struct.pack("<h", sample)
        wav.writeframes(frames)


def play_buzzer(path: Path | None = None) -> None:
    wav = ensure_buzzer(path or DEFAULT_BUZZER)
    try:
        subprocess.Popen(
            ["afplay", str(wav)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        print(f"buzzer failed: {exc}", file=sys.stderr)
