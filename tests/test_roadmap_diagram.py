from pathlib import Path
import sqlite3

import pytest

from database.db import create_roadmap, create_student, get_career_by_name
from database.seed import seed_db
from ui.roadmap_diagram import (
    _roadmap_html,
    build_roadmap_diagram_data,
    build_resume_roadmap_diagram_data,
    roadmap_diagram_height,
)


def test_diagram_data_shows_full_order_and_assessed_known_skills():
    skills = [
        {"id": 10, "name": "SQL", "description": "Query relational data."},
        {"id": 13, "name": "Excel", "description": "Use spreadsheets."},
        {"id": 14, "name": "Statistics", "description": "Reason about data."},
        {"id": 11, "name": "Python", "description": "Write scripts."},
        {"id": 15, "name": "Pandas", "description": "Process tables."},
        {"id": 16, "name": "Data Visualization", "description": "Show results."},
        {"id": 12, "name": "Data Analysis Project", "description": "Apply the skills."},
    ]
    progress = {
        10: {"progress_percent": 100, "status": "completed"},
        11: {"progress_percent": 45, "status": "in_progress"},
    }
    data = build_roadmap_diagram_data(
        "Data Analyst",
        skills,
        progress,
        {
            10: [{"url": "https://example.com/sql"}],
            11: [{"url": "javascript:alert(1)"}],
        },
    )

    root, *rest = data["nodes"]
    groups = [node for node in rest if node["type"] == "branch"]
    skill_nodes = [node for node in rest if node["type"] == "skill"]
    assert root["label"] == "Data Analyst"
    assert [node["label"] for node in groups] == [
        "Data Foundations", "Analysis Tools", "Insights & Practice"
    ]
    assert [node["label"] for node in skill_nodes] == [
        "SQL", "Excel", "Statistics", "Python", "Pandas",
        "Data Visualization", "Data Analysis Project"
    ]
    assert [node["status"] for node in skill_nodes] == [
        "known", "to_learn", "to_learn", "to_learn", "to_learn", "to_learn",
        "to_learn",
    ]
    assert skill_nodes[0]["url"] == "https://example.com/sql"
    assert "url" not in skill_nodes[3]
    assert "progressPercent" not in skill_nodes[3]
    assert skill_nodes[3]["parentId"] == groups[1]["id"]
    assert data["skillCount"] == len(skill_nodes) == 7
    assert data["totalSkillCount"] == 7
    assert data["knownSkillCount"] == 1


def test_known_skills_remain_in_the_full_career_roadmap():
    skills = [
        {"id": 1, "name": "Python", "description": "Write scripts."},
        {"id": 2, "name": "Git", "description": "Track code changes."},
    ]

    data = build_roadmap_diagram_data(
        "Backend Developer",
        skills,
        {1: {"progress_percent": 100, "status": "completed"}},
        {},
    )

    skill_nodes = [node for node in data["nodes"] if node["type"] == "skill"]
    assert [node["label"] for node in skill_nodes] == ["Python", "Git"]
    assert [node["status"] for node in skill_nodes] == ["known", "to_learn"]
    assert data["skillCount"] == 2
    assert data["totalSkillCount"] == 2
    assert data["knownSkillCount"] == 1


def test_known_skill_detection_accepts_sqlite_assessment_records():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    progress_row = connection.execute(
        "SELECT 100 AS progress_percent, 'completed' AS status"
    ).fetchone()
    skills = [{"id": 1, "name": "Python", "description": "Write scripts."}]

    data = build_roadmap_diagram_data(
        "Backend Developer", skills, {1: progress_row}, {}
    )

    assert data["skillCount"] == 1
    assert [node["status"] for node in data["nodes"] if node["type"] == "skill"] == ["known"]
    assert data["knownSkillCount"] == 1


def test_fully_known_career_still_shows_all_roadmap_nodes():
    skills = [
        {"id": 1, "name": "Python", "description": "Write scripts."},
        {"id": 2, "name": "Git", "description": "Track code changes."},
    ]
    progress = {
        1: {"progress_percent": 100, "status": "completed"},
        2: {"progress_percent": 100, "status": "completed"},
    }

    data = build_roadmap_diagram_data("Backend Developer", skills, progress, {})

    assert sum(node["type"] == "root" for node in data["nodes"]) == 1
    assert sum(node["type"] == "branch" for node in data["nodes"]) >= 1
    assert sum(node["type"] == "skill" for node in data["nodes"]) == 2
    assert [node["status"] for node in data["nodes"] if node["type"] == "skill"] == [
        "known", "known"
    ]
    assert data["skillCount"] == 2
    assert data["knownSkillCount"] == data["totalSkillCount"] == 2


def test_resume_roadmap_diagram_uses_role_order_and_marks_demonstrated_skills():
    data = build_resume_roadmap_diagram_data(
        "Backend Developer",
        ["Python", "Git", "SQL", "HTTP and REST APIs"],
        [
            {"name": "Python", "level": 4},
            {"name": "SQL", "level": 2},
        ],
        [
            {
                "step": 1,
                "skill": "Git",
                "estimated_hours": 24,
                "start_week": 1,
                "end_week": 5,
            },
            {
                "step": 2,
                "skill": "SQL",
                "estimated_hours": 10,
                "start_week": 5,
                "end_week": 7,
            },
            {
                "step": 3,
                "skill": "HTTP and REST APIs",
                "estimated_hours": 30,
                "start_week": 7,
                "end_week": 13,
            },
        ],
    )

    skill_nodes = [node for node in data["nodes"] if node["type"] == "skill"]
    assert [node["label"] for node in skill_nodes] == [
        "Python", "Git", "SQL", "HTTP and REST APIs"
    ]
    assert [node["status"] for node in skill_nodes] == [
        "known", "to_learn", "to_learn", "to_learn"
    ]
    assert "10 hours" in skill_nodes[2]["description"]
    assert data["knownSkillCount"] == 1
    assert data["totalSkillCount"] == 4


def test_diagram_requires_career_and_ordered_skills():
    for career, skills in [("", [{"id": 1}]), ("Career", [])]:
        with pytest.raises(ValueError):
            build_roadmap_diagram_data(career, skills, {}, {})


def test_diagram_height_scales_for_the_full_skill_sequence():
    assert roadmap_diagram_height(0) == 620
    assert roadmap_diagram_height(8, 3) == 735
    assert roadmap_diagram_height(12, 4) > roadmap_diagram_height(8, 3)
    with pytest.raises(ValueError):
        roadmap_diagram_height(-1)


def test_all_supported_careers_keep_their_skill_order_inside_visual_groups():
    from database.seed import CAREER_CATALOG

    for career_name, career in CAREER_CATALOG.items():
        skills = [
            {"id": index, "name": name, "description": f"Learn {name}."}
            for index, name in enumerate(career["skills"], start=1)
        ]
        data = build_roadmap_diagram_data(career_name, skills, {}, {})
        groups = [node for node in data["nodes"] if node["type"] == "branch"]
        rendered_order = [
            child["label"]
            for group in groups
            for child in sorted(
                (node for node in data["nodes"] if node["parentId"] == group["id"]),
                key=lambda node: node["sequence"],
            )
        ]
        assert rendered_order == career["skills"]


def test_embedded_roadmap_is_self_contained_and_has_no_api_dependency():
    data = build_roadmap_diagram_data(
        "Backend Developer",
        [{"id": 1, "name": "Python", "description": "Learn Python."}],
        {},
        {},
    )

    html = _roadmap_html(data)

    assert "function buildLayout(data)" in html
    assert "function renderRoadmap(layout)" in html
    assert "function attachInteractions()" in html
    assert "progressPercent" not in html
    assert "meterValue" not in html
    assert "Python" not in html  # Data is encoded separately from executable markup.
    assert "https://" not in html


def test_skill_gap_page_renders_the_integrated_visual_roadmap():
    from streamlit.testing.v1 import AppTest

    seed_db()
    student_id = create_student("Roadmap Diagram Student")
    career_id = get_career_by_name("Backend Developer")["id"]
    create_roadmap(student_id, career_id)
    app_path = Path(__file__).resolve().parents[1] / "app.py"

    app_test = AppTest.from_file(str(app_path), default_timeout=20)
    app_test.session_state["student_id"] = student_id
    app_test.session_state["workflow_step"] = "Skill Gap & Roadmap"
    app_test.run()

    assert not app_test.exception
    assert any("Visual learning path" in item.value for item in app_test.subheader)
