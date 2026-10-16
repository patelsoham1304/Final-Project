"""Rule-based next-skill recommendation."""


def get_next_recommended_skill(skill_gap: list[dict] | None) -> dict | None:
    """Return the first skill in an already ordered gap, or None when complete."""
    if skill_gap is None or skill_gap == []:
        return None
    if not isinstance(skill_gap, list):
        raise TypeError("skill_gap must be a list of dicts")
    if not all(isinstance(skill, dict) for skill in skill_gap):
        raise TypeError("Each skill gap entry must be a dictionary.")
    return skill_gap[0]
