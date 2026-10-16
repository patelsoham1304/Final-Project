"""Persist student self-assessments as completed or unstarted skills."""

from database.db import get_skills, get_student_skills, save_student_skills


def get_assessments(student_id: int) -> list[dict]:
    """Return a student's completed-skill assessment."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    return [dict(row) for row in get_student_skills(student_id)]


def get_available_skills() -> list[dict]:
    """Return the skills from the database for the assessment screen."""
    return [dict(row) for row in get_skills()]


def save_assessment(student_id: int, skill_ids: list[int]) -> None:
    """Validate and persist the student's current known skills."""
    if not isinstance(skill_ids, list):
        raise ValueError("Skills must be supplied as a list of skill IDs.")
    save_student_skills(student_id, skill_ids)


def save_career_assessment(
    student_id: int,
    career_skill_ids: list[int],
    selected_skill_ids: list[int],
) -> None:
    """Save target-career skills while retaining known skills shared with other paths."""
    if not isinstance(career_skill_ids, list) or not isinstance(selected_skill_ids, list):
        raise ValueError("Career skills and selected skills must be lists.")
    if any(
        isinstance(skill_id, bool) or not isinstance(skill_id, int) or skill_id <= 0
        for skill_id in career_skill_ids + selected_skill_ids
    ):
        raise ValueError("Skill IDs must be positive integers.")
    career_skill_set = set(career_skill_ids)
    if not career_skill_set.issuperset(selected_skill_ids):
        raise ValueError("Only skills listed for the selected career can be assessed.")
    previously_known = {
        item["skill_id"] for item in get_assessments(student_id)
    }
    transferable = previously_known - career_skill_set
    save_assessment(
        student_id,
        list(transferable | set(selected_skill_ids)),
    )
