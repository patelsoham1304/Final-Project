import pytest
from modules.recommendation import get_next_recommended_skill

def test_normal_case():
    gap = [
        {"skill": "Python", "required": 4, "current": 2, "gap": 2},
        {"skill": "SQL", "required": 3, "current": 2, "gap": 1}
    ]
    res = get_next_recommended_skill(gap)
    assert res == {"skill": "Python", "required": 4, "current": 2, "gap": 2}

def test_empty_case():
    assert get_next_recommended_skill([]) is None
    assert get_next_recommended_skill(None) is None

def test_single_item():
    gap = [{"skill": "AWS", "required": 2, "current": 0, "gap": 2}]
    res = get_next_recommended_skill(gap)
    assert res == {"skill": "AWS", "required": 2, "current": 0, "gap": 2}

def test_type_error():
    with pytest.raises(TypeError):
        get_next_recommended_skill("invalid") # type: ignore

def test_none_input():
    assert get_next_recommended_skill(None) is None
