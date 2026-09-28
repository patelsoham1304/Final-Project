# NOTES_DB_ASSUMPTIONS

## Assumed DB Functions

1. `get_student(student_id: int) -> dict`
   Returns profile info and current skills.
   Shape: `{"id": int, "name": str, "current_skills": dict[str, int]}`

2. `get_skills_for_career(career_name: str) -> dict[str, int]`
   Returns the required skills and their required levels for a given career.
   Shape: `{"skill_name": int}`

3. `get_all_careers() -> list[str]`
   Returns a list of all available careers.

4. `update_student_progress(student_id: int, progress_data: dict) -> bool`
   Saves calculated progress data to the database.

5. `get_skill_assessments(student_id: int) -> list[dict]`
   Returns past assessments.
