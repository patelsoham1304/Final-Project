from modules.roadmap import generate_roadmap
from modules.progress import calculate_overall_progress

def _mock_update_progress(student_id: int, progress: float):
    # TEMP MOCK — remove once database layer ready
    pass

def plan_student_path(student_id: int, required: dict, current: dict, progress_data: list) -> dict:
    """Plan a learning path and update progress."""
    roadmap = generate_roadmap(required, current)
    progress = calculate_overall_progress(progress_data)
    _mock_update_progress(student_id, progress)
    return {"roadmap": roadmap, "progress": progress}
