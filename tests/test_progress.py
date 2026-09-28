import pytest
from modules.progress import calculate_overall_progress

def test_progress_normal():
    data = [{"completed": True}, {"completed": False}, {"completed": True}]
    assert calculate_overall_progress(data) == 66.67

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
