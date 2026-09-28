def get_next_recommended_skill(skill_gap: list[dict] | None) -> dict | None:
    """
    Get the next recommended skill to learn based on the skill gap.
    Returns the highest-priority skill dict, or None if the gap is empty.
    """
    if skill_gap is None:
        return None
    if not isinstance(skill_gap, list):
        raise TypeError("skill_gap must be a list of dicts")
    if not skill_gap:
        return None
        
    return skill_gap[0]
