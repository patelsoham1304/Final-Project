from modules.skill_gap import calculate_skill_gap

def generate_roadmap(required_skills: dict[str, int] | None, current_skills: dict[str, int] | None) -> list[dict]:
    """
    Generate an ordered learning roadmap based on skill gaps.
    """
    gaps = calculate_skill_gap(required_skills, current_skills)
    roadmap = []
    
    for i, gap_info in enumerate(gaps, start=1):
        roadmap.append({
            "step": i,
            "skill": gap_info["skill"],
            "from_level": gap_info["current"],
            "to_level": gap_info["required"]
        })
        
    return roadmap
