import main
from dribble_station.audio import ensure_buzzer


def test_main_exports_run():
    assert callable(main.run)
    assert main.STATION_ID == "dribble"


def test_buzzer_wav_is_created(tmp_path):
    path = tmp_path / "buzzer.wav"
    written = ensure_buzzer(path)
    assert written.is_file()
    assert written.stat().st_size > 100
