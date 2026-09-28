def _mock_get_skills_for_career(career_name: str) -> dict:
    # TEMP MOCK — remove once database layer ready
    return {"Python": 4, "SQL": 3, "AWS": 2}

def get_career_requirements(career_name: str) -> dict:
    """Get the skill requirements for a career."""
    return _mock_get_skills_for_career(career_name)
