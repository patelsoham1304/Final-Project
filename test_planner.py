import pytest

from modules.planner import plan_study_time


def test_evenly_splits_weekly_hours_in_given_order():
    plan = plan_study_time(10, ["SQL", "Statistics", "Pandas"])
    assert [step["skill"] for step in plan] == ["SQL", "Statistics", "Pandas"]
    assert sum(step["hours"] for step in plan) == 10
    assert [step["hours"] for step in plan] == [3.33, 3.33, 3.34]


def test_empty_path_returns_no_allocations():
    assert plan_study_time(10, []) == []


def test_zero_hours_returns_no_allocations():
    assert plan_study_time(0, ["SQL"]) == []


def test_rejects_negative_or_excessive_hours():
    with pytest.raises(ValueError, match="between 0 and 168"):
        plan_study_time(-1, ["SQL"])
    with pytest.raises(ValueError, match="between 0 and 168"):
        plan_study_time(169, ["SQL"])


def test_rejects_invalid_skill_list():
    with pytest.raises(ValueError, match="non-empty"):
        plan_study_time(5, [""])
