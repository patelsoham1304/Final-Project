from pathlib import Path


def test_streamlit_entrypoint_imports_all_screens():
    import app

    assert callable(app.ui.career_path_ui.render)


def test_streamlit_app_renders_resume_first_screen():
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()

    assert not app_test.exception
    assert any("Resume Upload" in item.value for item in app_test.header)
    assert len(app_test.file_uploader) == 1
    assert any(
        item.label == "Continue to student profile" for item in app_test.button
    )
    assert any(item.label == "Ask tutor" for item in app_test.button)
    assert [item.key for item in app_test.text_input] == ["ai_tutor_api_key"]
    assert not app_test.number_input
    assert not any("Analyze resume" in item.value for item in app_test.caption)
    assert "Resume Builder" not in app_test.sidebar.radio[0].options


def test_upload_continue_button_moves_to_student_profile():
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()
    app_test.button[0].click().run()

    assert not app_test.exception
    assert app_test.session_state["workflow_step"] == "Select Career"
    assert any("Career" in item.value for item in app_test.header)


def test_update_progress_screen_is_removed_from_navigation():
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()

    assert not app_test.exception
    assert "Create Student" not in app_test.sidebar.radio[0].options
    assert len(app_test.sidebar.radio[0].options) == 5
    assert not app_test.slider


def test_ai_tutor_panel_is_present_on_every_workflow_screen(monkeypatch):
    from database.db import (
        create_roadmap,
        create_student,
        get_career_by_name,
    )
    from database.seed import seed_db
    from streamlit.testing.v1 import AppTest

    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    seed_db()
    student_id = create_student("Tutor Flow Student")
    career_id = get_career_by_name("Data Analyst")["id"]
    create_roadmap(student_id, career_id)

    steps = [
        "Resume Career Path",
        "Select Career",
        "Skill Gap & Roadmap",
        "Study Planner",
        "Dashboard",
    ]
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()

    for step in steps:
        app_test.session_state["student_id"] = student_id
        app_test.session_state["workflow_step"] = step
        app_test.run()

        assert not app_test.exception, step
        assert any(item.value == "AI Learning Tutor" for item in app_test.subheader), step
        assert any(item.label == "Ask tutor" for item in app_test.button), step
        assert any(item.key == "ai_tutor_api_key" for item in app_test.text_input), step


def test_dashboard_hides_only_the_skills_completed_metric():
    from database.db import (
        create_roadmap,
        create_student,
        get_career_by_name,
        get_skills_for_career,
    )
    from database.seed import seed_db
    from modules.skill_assessment import save_assessment
    from streamlit.testing.v1 import AppTest

    seed_db()
    student_id = create_student("Dashboard Metric Student")
    career_id = get_career_by_name("Data Analyst")["id"]
    create_roadmap(student_id, career_id)
    skills = get_skills_for_career(career_id)
    save_assessment(student_id, [skills[0]["id"]])

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()
    app_test.session_state["student_id"] = student_id
    app_test.session_state["workflow_step"] = "Dashboard"
    app_test.run()

    assert not app_test.exception
    metric_labels = [item.label for item in app_test.metric]
    assert "Skills completed" not in metric_labels
    assert "Skills remaining" in metric_labels
    assert "Next recommended skill" in metric_labels
    assert next(
        item.value for item in app_test.metric if item.label == "Initial skill coverage"
    ) == "14%"
    assert next(
        item.value for item in app_test.metric if item.label == "Skills remaining"
    ) == "6"
    assert any(item.value == "Already known skills" for item in app_test.subheader)
    assert any(item.value == "Remaining skills" for item in app_test.subheader)


def test_roadmap_displays_every_ordered_skill_and_marks_assessed_skills():
    from database.db import (
        create_roadmap,
        create_student,
        get_career_by_name,
        get_skills_for_career,
    )
    from database.seed import seed_db
    from modules.skill_assessment import save_assessment
    from streamlit.testing.v1 import AppTest

    seed_db()
    student_id = create_student("Full Roadmap Student")
    career_id = get_career_by_name("Data Analyst")["id"]
    create_roadmap(student_id, career_id)
    skills = get_skills_for_career(career_id)
    save_assessment(student_id, [skills[0]["id"]])

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()
    app_test.session_state["student_id"] = student_id
    app_test.session_state["workflow_step"] = "Skill Gap & Roadmap"
    app_test.run()

    assert not app_test.exception
    assert any(item.value == "Complete career roadmap" for item in app_test.subheader)
    expander_labels = [item.label for item in app_test.expander]
    assert len(expander_labels) == len(skills)
    assert expander_labels[0] == f"1. Already know: {skills[0]['name']}"
    assert expander_labels[1] == f"2. Learn {skills[1]['name']}"
    assert "Update Progress" not in app_test.sidebar.radio[0].options


def test_study_planner_allocates_only_skills_not_marked_as_known():
    from database.db import (
        create_roadmap,
        create_student,
        get_career_by_name,
        get_skills_for_career,
    )
    from database.seed import seed_db
    from modules.skill_assessment import save_assessment
    from streamlit.testing.v1 import AppTest

    seed_db()
    student_id = create_student("Planner Assessment Student")
    career_id = get_career_by_name("Data Analyst")["id"]
    create_roadmap(student_id, career_id)
    skills = get_skills_for_career(career_id)
    save_assessment(student_id, [skills[0]["id"]])

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()
    app_test.session_state["student_id"] = student_id
    app_test.session_state["workflow_step"] = "Study Planner"
    app_test.run()

    assert not app_test.exception
    assert any(item.value == "Equal split across 6 ordered skills:" for item in app_test.markdown)
    assert not any(
        skills[0]["name"] in str(item.value) for item in app_test.dataframe
    )


def test_tutor_chat_uses_active_roadmap_and_persists_only_in_session(monkeypatch):
    import ui.ai_tutor_ui
    from database.db import (
        create_roadmap,
        create_student,
        get_career_by_name,
        get_skills_for_career,
    )
    from database.seed import seed_db
    from modules.skill_assessment import save_assessment
    from streamlit.testing.v1 import AppTest

    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "gemma4:31b")
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    seed_db()
    student_id = create_student("Tutor Chat Student")
    career_id = get_career_by_name("Data Analyst")["id"]
    create_roadmap(student_id, career_id)
    first_skill = get_skills_for_career(career_id)[0]
    save_assessment(student_id, [first_skill["id"]])
    captured = {}

    def fake_reply(prompt, context, history, config):
        captured["prompt"] = prompt
        captured["context"] = context
        captured["history"] = list(history)
        captured["config"] = config
        return "Continue with the next incomplete skill."

    monkeypatch.setattr(ui.ai_tutor_ui, "request_tutor_reply", fake_reply)
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app_test = AppTest.from_file(str(app_path), default_timeout=20).run()
    app_test.session_state["student_id"] = student_id
    app_test.session_state["workflow_step"] = "Skill Gap & Roadmap"
    app_test.run()
    next(
        item for item in app_test.text_input if item.key == "ai_tutor_api_key"
    ).set_value("test-user-key").run()
    app_test.text_area[0].set_value("What should I learn next?").run()
    next(button for button in app_test.button if button.label == "Ask tutor").click().run()

    assert not app_test.exception
    assert captured["prompt"] == "What should I learn next?"
    assert "Data Analyst" in captured["context"]
    assert f"{first_skill['name']}: already known" in captured["context"]
    assert "%" not in captured["context"]
    assert captured["history"] == []
    assert captured["config"].api_key == "test-user-key"
    assert captured["config"].base_url == "https://ollama.com"
    assert app_test.session_state[f"ai_tutor_messages_{student_id}"] == [
        {"role": "user", "content": "What should I learn next?"},
        {
            "role": "assistant",
            "content": "Continue with the next incomplete skill.",
        },
    ]
