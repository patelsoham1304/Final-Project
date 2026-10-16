from pathlib import Path


def test_streamlit_entrypoint_imports_all_screens():
    import app

    assert callable(app.ui.career_path_ui.render)


def test_streamlit_app_renders_resume_first_screen():
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()

    assert not app_test.exception
    assert any("Resume-to-Career Path" in item.value for item in app_test.header)
