import pytest
from modules.skill_gap import calculate_skill_gap

def test_normal_case():
    req = {"Python": 4, "SQL": 3, "AWS": 2}
    curr = {"Python": 2, "SQL": 3}
    gap = calculate_skill_gap(req, curr)
    assert len(gap) == 2
    assert gap[0] == {"skill": "Python", "required": 4, "current": 2, "gap": 2}
    assert gap[1] == {"skill": "AWS", "required": 2, "current": 0, "gap": 2}

def test_empty_input():
    assert calculate_skill_gap({}, {}) == []
    assert calculate_skill_gap(None, None) == []

def test_edge_case():
    # current >= required
    req = {"Python": 2}
    curr = {"Python": 4}
    assert calculate_skill_gap(req, curr) == []

def test_error_case():
    req = {"Python": -1}
    with pytest.raises(ValueError, match="Invalid required skill level for Python: -1"):
        calculate_skill_gap(req, {})
        
    req2 = {"Python": 2}
    curr2 = {"Python": -1}
    with pytest.raises(ValueError, match="Invalid current skill level for Python: -1"):
        calculate_skill_gap(req2, curr2)

def test_ordering():
    req = {"A": 5, "B": 3, "C": 4}
    curr = {"A": 4, "B": 0, "C": 2}
    gap = calculate_skill_gap(req, curr)
    # B gap 3, C gap 2, A gap 1
    assert gap[0]["skill"] == "B"
    assert gap[1]["skill"] == "C"
    assert gap[2]["skill"] == "A"

def test_normalization():
    req = {" Python ": 4}
    curr = {"python": 2}
    gap = calculate_skill_gap(req, curr)
    assert gap[0]["gap"] == 2
    assert gap[0]["skill"] == "Python"

def test_dependency_order_overrides_gap_size():
    required = {"Python": 5, "SQL": 1, "Excel": 3}
    current = {"Python": 0, "SQL": 0, "Excel": 0}
    gaps = calculate_skill_gap(
        required, current, ["SQL", "Excel", "Python"]
    )
    assert [item["skill"] for item in gaps] == ["SQL", "Excel", "Python"]

def test_rejects_levels_outside_supported_range():
    with pytest.raises(ValueError, match="Invalid required skill level"):
        calculate_skill_gap({"Python": 6}, {})
    with pytest.raises(ValueError, match="Invalid current skill level"):
        calculate_skill_gap({"Python": 1}, {"Python": -1})
