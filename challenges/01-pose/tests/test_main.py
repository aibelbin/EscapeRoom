import main


def test_main_module_exports_run_and_open_camera():
    assert callable(main.open_camera)
    assert callable(main.run)
    assert main.STATION_ID == "pose"
