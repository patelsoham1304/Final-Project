import pytest

from modules.progress import calculate_overall_progress, summarize_required_skills

def test_progress_normal():
    data = [{"completed": True}, {"completed": False}, {"completed": True}]
    assert calculate_overall_progress(data) == 67.0

def test_progress_empty():
    assert calculate_overall_progress([]) == 0.0
    assert calculate_overall_progress(None) == 0.0

def test_progress_all_completed():
    data = [{"completed": True}, {"completed": True}]
    assert calculate_overall_progress(data) == 100.0

def test_progress_none_completed():
    data = [{"completed": False}, {"completed": False}]
    assert calculate_overall_progress(data) == 0.0

def test_progress_missing_key():
    data = [{"other": 1}, {"completed": True}]
    assert calculate_overall_progress(data) == 50.0

@pytest.mark.parametrize(
    ("completed_count", "expected"),
    [(0, 0.0), (1, 25.0), (2, 50.0), (3, 75.0), (4, 100.0)],
)
def test_prompt_overall_progress_formula(completed_count, expected):
    data = [
        {"status": "completed" if index < completed_count else "in_progress"}
        for index in range(4)
    ]
    assert calculate_overall_progress(data) == expected

def test_progress_rejects_non_list_input():
    with pytest.raises(TypeError, match="list of skill records"):
        calculate_overall_progress({"completed": True})


def test_required_skill_progress_is_derived_from_completed_skill_records():
    required = [
        {"id": 1, "name": "Python"},
        {"id": 2, "name": "SQL"},
        {"id": 3, "name": "Git"},
    ]
    saved_progress = [
        {"skill_id": 1, "status": "completed"},
        {"skill_id": 2, "status": "in_progress"},
    ]

    summary = summarize_required_skills(required, saved_progress)

    assert [item["status"] for item in summary] == [
        "completed",
        "not_started",
        "not_started",
    ]
    assert sum(item["completed"] for item in summary) == 1
    assert calculate_overall_progress(summary) == 33.0


def test_required_skill_progress_ignores_skills_outside_selected_career():
    required = [{"id": 1, "name": "Python"}]
    saved_progress = [{"skill_id": 99, "status": "completed"}]

    summary = summarize_required_skills(required, saved_progress)

    assert summary == [
        {
            "skill_id": 1,
            "skill": "Python",
            "status": "not_started",
            "completed": False,
        }
    ]
