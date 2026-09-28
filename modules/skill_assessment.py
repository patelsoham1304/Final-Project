def _mock_get_skill_assessments(student_id: int) -> list[dict]:
    # TEMP MOCK — remove once database layer ready
    return [{"skill": "Python", "score": 2}]

def get_assessments(student_id: int) -> list[dict]:
    """Get skill assessments for a student."""
    return _mock_get_skill_assessments(student_id)
