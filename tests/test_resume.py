import pytest

from database.db import create_student, get_careers, get_resume_profile
from database.seed import seed_db
from modules.resume import build_resume_markdown, get_resume, save_resume


@pytest.fixture
def resume_context():
    seed_db()
    student_id = create_student("Asha Student", "asha@example.com")
    careers_by_name = {career["name"]: career for career in get_careers()}
    return student_id, careers_by_name


def test_saves_and_reads_persistent_resume(resume_context):
    student_id, careers = resume_context
    details = {
        "headline": "Aspiring frontend developer",
        "summary": "BCA student interested in accessible web applications.",
        "education": "BCA, Example College, 2023-2026",
        "projects": "Study Planner — built a Streamlit learning app.",
        "certifications": "Web fundamentals",
        "portfolio_url": "https://example.com/portfolio",
        "linkedin_url": "https://www.linkedin.com/in/asha",
    }
    save_resume(student_id, careers["Frontend Developer"]["id"], details)
    saved = get_resume(student_id)
    assert saved["headline"] == details["headline"]
    assert saved["career_id"] == careers["Frontend Developer"]["id"]
    assert get_resume_profile(student_id)["projects"] == details["projects"]


def test_updating_resume_replaces_old_content(resume_context):
    student_id, careers = resume_context
    first = {"summary": "First draft"}
    second = {"summary": "Updated draft"}
    save_resume(student_id, careers["Data Analyst"]["id"], first)
    save_resume(student_id, careers["Data Scientist"]["id"], second)
    saved = get_resume(student_id)
    assert saved["summary"] == "Updated draft"
    assert saved["career_id"] == careers["Data Scientist"]["id"]


@pytest.mark.parametrize("invalid_url", ["example.com", "javascript:alert(1)", "https:///bad"])
def test_rejects_invalid_resume_links(resume_context, invalid_url):
    student_id, careers = resume_context
    with pytest.raises(ValueError, match="valid http or https URL"):
        save_resume(
            student_id,
            careers["Data Analyst"]["id"],
            {"portfolio_url": invalid_url},
        )


def test_markdown_export_includes_student_target_and_completed_skills():
    markdown = build_resume_markdown(
        "Asha Student",
        "asha@example.com",
        "Frontend Developer",
        {
            "headline": "Aspiring frontend developer",
            "summary": "Builds accessible interfaces.",
            "education": "BCA, Example College",
            "projects": "Portfolio site — responsive design.",
            "certifications": "Web fundamentals",
            "portfolio_url": "https://example.com",
            "linkedin_url": "",
        },
        ["HTML", "CSS"],
    )
    assert "# Asha Student" in markdown
    assert "Target role:** Frontend Developer" in markdown
    assert "HTML, CSS" in markdown
    assert "Portfolio site" in markdown


def test_markdown_export_rejects_missing_name_or_target():
    details = {}
    with pytest.raises(ValueError, match="student name"):
        build_resume_markdown("", None, "Data Analyst", details, [])
    with pytest.raises(ValueError, match="target career"):
        build_resume_markdown("Asha", None, "", details, [])
