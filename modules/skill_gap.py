def calculate_skill_gap(required_skills: dict[str, int] | None, current_skills: dict[str, int] | None) -> list[dict]:
    """
    Calculate the skill gap between required and current skills.
    Returns a list of dicts sorted by gap descending.
    """
    if required_skills is None:
        required_skills = {}
    if current_skills is None:
        current_skills = {}
        
    normalized_current = {}
    for skill, level in current_skills.items():
        if level < 0:
            raise ValueError(f"Invalid current skill level for {skill}: {level}")
        normalized_current[skill.strip().lower()] = level

    gaps = []
    for skill, req_level in required_skills.items():
        if req_level < 0:
            raise ValueError(f"Invalid required skill level for {skill}: {req_level}")
        
        norm_skill = skill.strip().lower()
        curr_level = normalized_current.get(norm_skill, 0)
        
        gap = req_level - curr_level
        if gap > 0:
            gaps.append({
                "skill": skill.strip(), # keep original case for display, but cleaned
                "required": req_level,
                "current": curr_level,
                "gap": gap
            })
            
    return sorted(gaps, key=lambda x: x["gap"], reverse=True)
