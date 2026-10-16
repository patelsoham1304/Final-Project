"""Deterministic skill-gap calculation."""


def _normalize_skill_name(skill_name: str, kind: str) -> str:
    if not isinstance(skill_name, str) or not skill_name.strip():
        raise ValueError(f"{kind} skill names must be non-empty strings.")
    return skill_name.strip().casefold()


def calculate_skill_gap(
    required_skills: dict[str, int] | None,
    current_skills: dict[str, int] | None,
    skill_order: list[str] | None = None,
) -> list[dict]:
    """Return missing skill levels, optionally following career dependency order."""
    if required_skills is None:
        required_skills = {}
    if current_skills is None:
        current_skills = {}
    if not isinstance(required_skills, dict) or not isinstance(current_skills, dict):
        raise TypeError("Required and current skills must be dictionaries.")
    if skill_order is not None and not isinstance(skill_order, list):
        raise TypeError("Skill order must be supplied as a list.")

    normalized_current = {}
    for skill_name, level in current_skills.items():
        key = _normalize_skill_name(skill_name, "Current")
        if isinstance(level, bool) or not isinstance(level, int) or level < 0 or level > 5:
            raise ValueError(f"Invalid current skill level for {skill_name}: {level}")
        normalized_current[key] = level

    gaps = []
    for skill_name, required_level in required_skills.items():
        key = _normalize_skill_name(skill_name, "Required")
        if (
            isinstance(required_level, bool)
            or not isinstance(required_level, int)
            or required_level < 0
            or required_level > 5
        ):
            raise ValueError(
                f"Invalid required skill level for {skill_name}: {required_level}"
            )
        current_level = normalized_current.get(key, 0)
        difference = required_level - current_level
        if difference > 0:
            gaps.append(
                {
                    "skill": skill_name.strip(),
                    "required": required_level,
                    "current": current_level,
                    "gap": difference,
                }
            )

    if skill_order is not None:
        ordered_names = [
            _normalize_skill_name(name, "Ordered")
            for name in skill_order
        ]
        order_map = {name: position for position, name in enumerate(ordered_names)}
        gaps.sort(key=lambda gap: order_map.get(gap["skill"].casefold(), len(order_map)))
    else:
        gaps.sort(key=lambda gap: gap["gap"], reverse=True)
    return gaps
