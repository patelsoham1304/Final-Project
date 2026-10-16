import pytest
from modules.roadmap import generate_roadmap

def test_generate_roadmap_normal():
    req = {"Python": 4, "SQL": 3}
    curr = {"Python": 2, "SQL": 3}
    roadmap = generate_roadmap(req, curr)
    assert len(roadmap) == 1
    assert roadmap[0] == {"step": 1, "skill": "Python", "from_level": 2, "to_level": 4}

def test_generate_roadmap_empty():
    assert generate_roadmap({}, {}) == []
    assert generate_roadmap(None, None) == []

def test_generate_roadmap_ordering():
    req = {"A": 5, "B": 3}
    curr = {"A": 4, "B": 0}
    # B gap is 3, A gap is 1. B should be step 1, A step 2
    roadmap = generate_roadmap(req, curr)
    assert len(roadmap) == 2
    assert roadmap[0]["step"] == 1
    assert roadmap[0]["skill"] == "B"
    assert roadmap[1]["step"] == 2
    assert roadmap[1]["skill"] == "A"
    
def test_generate_roadmap_no_gap():
    req = {"A": 2}
    curr = {"A": 2}
    assert generate_roadmap(req, curr) == []

def test_generate_roadmap_invalid_level():
    with pytest.raises(ValueError):
        generate_roadmap({"A": -1}, {})

def test_roadmap_uses_dependency_order_instead_of_gap_size():
    roadmap = generate_roadmap(
        {"Python": 5, "SQL": 1, "Excel": 3},
        {"Python": 0, "SQL": 0, "Excel": 0},
        ["SQL", "Excel", "Python"],
    )
    assert [step["skill"] for step in roadmap] == ["SQL", "Excel", "Python"]
