import pytest
from modules.gamification import get_student_gamification_data
from modules.roadmap_exporter import generate_roadmap_html, generate_roadmap_pdf_or_docx
from database.seed import seed_db
from database.db import create_student, create_roadmap, get_career_by_name

def test_gamification_metrics():
    seed_db()
    sid = create_student("GamifyTestUser", "gamify@example.com")
    career = get_career_by_name("Data Analyst")
    create_roadmap(sid, career["id"])
    
    data = get_student_gamification_data(sid)
    assert "streak" in data
    assert "xp" in data
    assert "level" in data
    assert "badges" in data
    assert isinstance(data["badges"], list)
    assert len(data["badges"]) >= 3

def test_roadmap_html_and_docx_export():
    html = generate_roadmap_html(
        student_name="Test Student",
        career_name="Data Analyst",
        overall_progress=40.0,
        known_skills=["Python", "SQL"],
        remaining_steps=[{"step": 1, "skill": "Pandas"}, {"step": 2, "skill": "Excel"}],
        student_email="student@test.com",
    )
    assert "PathFinder AI" in html
    assert "Data Analyst" in html
    assert "40%" in html
    assert "Pandas" in html

    docx_bytes = generate_roadmap_pdf_or_docx(
        student_name="Test Student",
        career_name="Data Analyst",
        overall_progress=40.0,
        known_skills=["Python", "SQL"],
        remaining_steps=[{"step": 1, "skill": "Pandas"}],
    )
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 500
