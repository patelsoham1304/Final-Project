def calculate_overall_progress(progress_data: list[dict] | None) -> float:
    """
    Calculate overall progress as a percentage 0.0 to 100.0.
    Expects a list of dicts with a 'completed' boolean key.
    """
    if not progress_data:
        return 0.0
        
    total = len(progress_data)
    completed = sum(1 for item in progress_data if item.get("completed", False))
    
    return round((completed / total) * 100, 2)
