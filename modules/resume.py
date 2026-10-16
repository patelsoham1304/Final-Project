"""Resume-profile validation and Markdown export."""

from urllib.parse import urlparse

from database.db import get_resume_profile, save_resume_profile


RESUME_FIELDS = (
    "headline",
    "summary",
    "education",
    "projects",
    "certifications",
    "portfolio_url",
    "linkedin_url",
)


def _validate_url(value: str, label: str) -> None:
    if not value:
        return
    if any(character.isspace() for character in value) or any(
        character in value for character in "<>\\"
    ):
        raise ValueError(f"{label} must be a valid http or https URL.")
    parsed = urlparse(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(f"{label} must be a valid http or https URL.")


def get_resume(student_id: int):
    """Load a student's saved resume content."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    return get_resume_profile(student_id)


def save_resume(
    student_id: int,
    career_id: int,
    resume_data: dict[str, str],
) -> None:
    """Validate and persist resume content for a chosen career."""
    if not isinstance(resume_data, dict):
        raise ValueError("Resume details must be supplied as a dictionary.")
    cleaned = {}
    for field in RESUME_FIELDS:
        value = resume_data.get(field, "")
        if not isinstance(value, str):
            raise ValueError(f"{field.replace('_', ' ').title()} must be text.")
        if len(value) > 10000:
            raise ValueError(
                f"{field.replace('_', ' ').title()} is too long (maximum 10,000 characters)."
            )
        cleaned[field] = value.strip()

    _validate_url(cleaned["portfolio_url"], "Portfolio URL")
    _validate_url(cleaned["linkedin_url"], "LinkedIn URL")
    save_resume_profile(
        student_id,
        career_id,
        cleaned["headline"],
        cleaned["summary"],
        cleaned["education"],
        cleaned["projects"],
        cleaned["certifications"],
        cleaned["portfolio_url"],
        cleaned["linkedin_url"],
    )


def build_resume_markdown(
    name: str,
    email: str | None,
    career_name: str,
    resume_data: dict,
    completed_skills: list[str],
) -> str:
    """Format saved profile data and verified completed skills as a resume."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("A student name is required to build the resume.")
    if not isinstance(career_name, str) or not career_name.strip():
        raise ValueError("Choose a target career before building the resume.")
    if not isinstance(resume_data, dict):
        raise ValueError("Resume details must be supplied as a dictionary.")
    if not isinstance(completed_skills, list) or not all(
        isinstance(skill, str) for skill in completed_skills
    ):
        raise ValueError("Completed skills must be a list of skill names.")

    headline = resume_data.get("headline", "").strip()
    summary = resume_data.get("summary", "").strip()
    lines = [f"# {name.strip()}"]
    contact = [email.strip()] if isinstance(email, str) and email.strip() else []
    portfolio = resume_data.get("portfolio_url", "").strip()
    linkedin = resume_data.get("linkedin_url", "").strip()
    if portfolio:
        contact.append(f"[Portfolio](<{portfolio}>)")
    if linkedin:
        contact.append(f"[LinkedIn](<{linkedin}>)")
    if contact:
        lines.extend(["", " · ".join(contact)])

    lines.extend(["", f"## {headline or career_name.strip()}"])
    lines.extend(["", f"**Target role:** {career_name.strip()}"])
    if summary:
        lines.extend(["", "## Professional Summary", "", summary])
    if completed_skills:
        lines.extend(["", "## Skills", "", ", ".join(completed_skills)])
    for title, key in (
        ("Education", "education"),
        ("Projects", "projects"),
        ("Certifications", "certifications"),
    ):
        content = resume_data.get(key, "").strip()
        if content:
            lines.extend(["", f"## {title}", "", content])
    return "\n".join(lines).strip() + "\n"
