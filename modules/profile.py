def _mock_get_student(student_id: int) -> dict:
    # TEMP MOCK — remove once database layer ready
    return {"id": student_id, "name": "Alice", "current_skills": {"Python": 2, "SQL": 3}}

def get_student_profile(student_id: int) -> dict:
    """Get the profile of a student."""
    return _mock_get_student(student_id)
