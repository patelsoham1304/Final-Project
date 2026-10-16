"""Dependency-ordered roadmap generation."""

from modules.skill_gap import calculate_skill_gap


def generate_roadmap(
    required_skills: dict[str, int] | None,
    current_skills: dict[str, int] | None,
    skill_order: list[str] | None = None,
) -> list[dict]:
    """Turn an ordered skill gap into numbered learning steps."""
    gaps = calculate_skill_gap(required_skills, current_skills, skill_order)
    return [
        {
            "step": step,
            "skill": gap["skill"],
            "from_level": gap["current"],
            "to_level": gap["required"],
        }
        for step, gap in enumerate(gaps, start=1)
    ]
