from database.db import (
    create_student,
    get_career_by_name,
    get_skills_for_career,
    get_student_skills,
)
from database.seed import seed_db
from modules.skill_assessment import save_career_assessment


def test_assessment_retains_transferable_known_skills_between_careers():
    seed_db()
    student_id = create_student("Assessment Student")
    data_analyst = get_career_by_name("Data Analyst")
    frontend = get_career_by_name("Frontend Developer")
    data_analyst_skills = get_skills_for_career(data_analyst["id"])
    frontend_skills = get_skills_for_career(frontend["id"])
    sql_id = next(skill["id"] for skill in data_analyst_skills if skill["name"] == "SQL")
    html_id = next(skill["id"] for skill in frontend_skills if skill["name"] == "HTML")

    save_career_assessment(
        student_id,
        [skill["id"] for skill in data_analyst_skills],
        [sql_id],
    )
    save_career_assessment(
        student_id,
        [skill["id"] for skill in frontend_skills],
        [html_id],
    )

    known_ids = {skill["skill_id"] for skill in get_student_skills(student_id)}
    assert known_ids == {sql_id, html_id}
