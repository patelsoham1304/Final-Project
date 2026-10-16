import json
from unittest.mock import Mock, patch

import pytest

from modules.career_path import (
    AIAnalysisError,
    CareerPathError,
    _call_openai_for_resume,
    _validated_ai_profile,
    analyze_resume,
    build_learning_roadmap,
    estimate_skill_hours_with_ai,
    rank_career_matches,
)


CAREERS = [
    {
        "name": "Python Developer",
        "description": "Build Python applications.",
        "skills": ["Python", "SQL"],
    },
    {
        "name": "Web Developer",
        "description": "Build websites.",
        "skills": ["HTML", "CSS"],
    },
]


def test_local_resume_analysis_ranks_by_supported_skill_proficiency():
    result = analyze_resume(
        "Built Python applications for a project. 2 years of professional experience.",
        CAREERS,
    )

    assert result["analysis_mode"] == "local"
    assert result["experience_years"] == 2
    assert result["role_matches"][0]["name"] == "Python Developer"
    assert result["role_matches"][0]["fit_percent"] == 50
    assert result["role_matches"][0]["demonstrated_skills"] == ["Python"]


def test_role_hint_changes_tie_order_not_evidence_fit():
    skills = [{"name": "Python", "level": 1, "evidence": "Python", "confidence": "low"}]
    roles = [
        {"name": "Python Developer", "skills": ["Python"]},
        {"name": "Python Engineer", "skills": ["Python"]},
    ]

    hinted = rank_career_matches(roles, skills, target_role="Python Engineer")
    unhinted = rank_career_matches(roles, skills)

    assert hinted[0]["name"] == "Python Engineer"
    assert hinted[0]["fit_percent"] == unhinted[0]["fit_percent"] == 33


def test_analysis_requires_resume_and_valid_career_data():
    with pytest.raises(CareerPathError, match="Resume text is required"):
        analyze_resume(" ", CAREERS)
    with pytest.raises(CareerPathError, match="Career profiles"):
        analyze_resume("Python", [{"name": "Missing skills"}])


def test_ai_result_requires_resume_evidence_and_uses_explicit_experience_only():
    result = _validated_ai_profile(
        {
            "skills": [
                {
                    "name": "Python",
                    "level": 4,
                    "evidence": "Built Python applications",
                    "confidence": "high",
                },
                {
                    "name": "SQL",
                    "level": 5,
                    "evidence": "Expert SQL databases",
                    "confidence": "high",
                },
            ],
        },
        "Built Python applications. 4 years of experience.",
        ["Python", "SQL"],
    )

    assert [item["name"] for item in result["skills"]] == ["Python"]
    assert result["experience_years"] == 4


def test_openai_call_uses_strict_schema_and_redacts_identifiers():
    resume = "Name: Student\nEmail: student@example.com\nBuilt Python applications."
    payload = {
        "output": [
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(
                            {
                                "skills": [
                                    {
                                        "name": "Python",
                                        "level": 3,
                                        "evidence": "Built Python applications",
                                        "confidence": "medium",
                                    }
                                ],
                            }
                        ),
                    }
                ]
            }
        ]
    }
    response = Mock()
    response.json.return_value = payload
    with patch("modules.career_path.requests.post", return_value=response) as post:
        result = _call_openai_for_resume(resume, CAREERS, ["Python", "SQL"], "test-key")

    prompt = post.call_args.kwargs["json"]["input"][1]["content"]
    schema = post.call_args.kwargs["json"]["text"]["format"]["schema"]
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert "student@example.com" not in prompt
    assert "roles" not in schema["properties"]
    assert "summary" not in schema["properties"]
    assert result["skills"][0]["name"] == "Python"


def test_ai_provider_failure_is_explicit():
    with patch(
        "modules.career_path.requests.post",
        side_effect=__import__("requests").RequestException("offline"),
    ):
        with pytest.raises(AIAnalysisError, match="could not be reached"):
            _call_openai_for_resume("Python", CAREERS, ["Python"], "test-key")


def test_ai_learning_hour_estimates_are_bounded_and_cover_each_gap():
    response = Mock()
    response.json.return_value = {
        "output": [
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(
                            {"estimates": [{"skill": "SQL", "hours": 42}]}
                        ),
                    }
                ]
            }
        ]
    }
    with patch("modules.career_path.requests.post", return_value=response):
        assert estimate_skill_hours_with_ai(
            "Python Developer",
            ["SQL"],
            {"Python": 3},
            2,
            "test-key",
        ) == {"SQL": 42}


def test_ai_learning_hour_estimates_reject_incomplete_response():
    response = Mock()
    response.json.return_value = {
        "output": [
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps({"estimates": []}),
                    }
                ]
            }
        ]
    }
    with patch("modules.career_path.requests.post", return_value=response):
        with pytest.raises(AIAnalysisError, match="did not cover every missing skill"):
            estimate_skill_hours_with_ai(
                "Python Developer",
                ["SQL"],
                {},
                None,
                "test-key",
            )


def test_roadmap_skips_demonstrated_skills_and_reports_bounded_duration():
    match = {
        "name": "Python Developer",
        "required_skills": ["Python", "SQL"],
    }
    roadmap = build_learning_roadmap(
        match,
        [{"name": "Python", "level": 3}],
        weekly_hours=5,
    )

    assert [step["skill"] for step in roadmap["steps"]] == ["SQL"]
    assert roadmap["total_learning_hours"] > 0
    assert roadmap["duration_range_weeks"][0] <= roadmap["estimated_weeks"]
    assert roadmap["duration_range_weeks"][1] >= roadmap["estimated_weeks"]


def test_roadmap_rejects_invalid_weekly_hours():
    with pytest.raises(CareerPathError, match="between 1 and 80"):
        build_learning_roadmap(
            {"name": "Role", "required_skills": ["Python"]},
            [],
            weekly_hours=0,
        )
