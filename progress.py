"""Progress persistence and deterministic overall-completion calculation."""

from database.db import (
    get_progress_for_student,
    save_progress,
    save_progress_batch,
)


def calculate_overall_progress(progress_data: list[dict] | None) -> float:
    """Return rounded completed-skills percentage, using the prompt's formula."""
    if progress_data is None or progress_data == []:
        return 0.0
    if not isinstance(progress_data, list):
        raise TypeError("Progress data must be a list of skill records.")
    if not all(isinstance(item, dict) for item in progress_data):
        raise TypeError("Each progress record must be a dictionary.")
    completed = sum(
        1
        for item in progress_data
        if item.get("completed") is True or item.get("status") == "completed"
    )
    return float(round(100 * completed / len(progress_data)))


def summarize_required_skills(
    required_skills: list[dict], progress_data: list[dict]
) -> list[dict]:
    """Derive each required skill's complete/incomplete state without editing it."""
    progress_by_skill = {item["skill_id"]: item for item in progress_data}
    summary = []
    for skill in required_skills:
        saved = progress_by_skill.get(skill["id"])
        completed = bool(saved and saved.get("status") == "completed")
        summary.append(
            {
                "skill_id": skill["id"],
                "skill": skill["name"],
                "status": "completed" if completed else "not_started",
                "completed": completed,
            }
        )
    return summary


def update_skill_progress(
    student_id: int, skill_id: int, progress_percent: int
) -> None:
    """Save a skill's percentage and derive its status from that value."""
    if isinstance(progress_percent, bool) or not isinstance(progress_percent, int):
        raise ValueError("Progress must be a whole number from 0 to 100.")
    if not 0 <= progress_percent <= 100:
        raise ValueError("Progress must be between 0 and 100.")
    status = (
        "completed"
        if progress_percent == 100
        else "not_started"
        if progress_percent == 0
        else "in_progress"
    )
    save_progress(student_id, skill_id, status, progress_percent)


def update_progress_for_skills(student_id: int, progress_values: dict[int, int]) -> None:
    """Validate and atomically persist several skill percentages."""
    for progress_percent in progress_values.values():
        if (
            isinstance(progress_percent, bool)
            or not isinstance(progress_percent, int)
            or not 0 <= progress_percent <= 100
        ):
            raise ValueError("Progress must be a whole number from 0 to 100.")
    save_progress_batch(student_id, progress_values)


def get_student_progress(student_id: int, roadmap_id: int | None = None) -> list[dict]:
    """Load all persisted progress for a student, optionally scoped to a roadmap."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    return [dict(row) for row in get_progress_for_student(student_id, roadmap_id)]
