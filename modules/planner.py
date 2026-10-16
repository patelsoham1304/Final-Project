"""Simple, explainable weekly study-time allocation."""

import math


def plan_study_time(weekly_hours: float, ordered_skills: list[str]) -> list[dict]:
    """Split weekly hours evenly among ordered skills, keeping the total exact."""
    if isinstance(weekly_hours, bool) or not isinstance(weekly_hours, (int, float)):
        raise ValueError("Weekly study time must be a number.")
    if not math.isfinite(weekly_hours) or not 0 <= weekly_hours <= 168:
        raise ValueError("Weekly study time must be between 0 and 168 hours.")
    if not isinstance(ordered_skills, list):
        raise ValueError("Skills must be supplied as an ordered list.")
    if not ordered_skills or weekly_hours == 0:
        return []
    if any(not isinstance(skill, str) or not skill.strip() for skill in ordered_skills):
        raise ValueError("Each skill name must be non-empty.")

    total_hundredths = round(weekly_hours * 100)
    base, remainder = divmod(total_hundredths, len(ordered_skills))
    allocations = []
    for index, skill in enumerate(ordered_skills):
        hundredths = base + (remainder if index == len(ordered_skills) - 1 else 0)
        allocations.append(
            {"skill": skill.strip(), "hours": round(hundredths / 100, 2)}
        )
    return allocations


def plan_student_path(
    student_id: int,
    required: dict[str, int],
    current: dict[str, int],
    progress_data: list[dict] | None = None,
) -> dict:
    """Return a deterministic roadmap and the student's overall completion."""
    from modules.progress import calculate_overall_progress
    from modules.roadmap import generate_roadmap

    roadmap = generate_roadmap(required, current)
    progress = calculate_overall_progress(progress_data)
    return {"student_id": student_id, "roadmap": roadmap, "progress": progress}
