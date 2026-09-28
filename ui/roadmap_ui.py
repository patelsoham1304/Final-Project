import streamlit as st

# TEMP UI MOCK: Will be replaced by modules.skill_gap.calculate_skill_gap
def calculate_skill_gap(student_id: str, current_skills: list, target_career: str) -> dict:
    return {
        "missing_skills": ["Missing Skill A", "Missing Skill B"],
        "match_percentage": 45
    }

# TEMP UI MOCK: Will be replaced by modules.roadmap.generate_roadmap
def generate_roadmap(student_id: str, target_career: str, current_skills: list) -> dict:
    return {
        "steps": [
            {"title": "Learn Skill A", "description": "Resource 1"},
            {"title": "Build Project B", "description": "Resource 2"}
        ]
    }

# TEMP UI MOCK: Will be replaced by modules.roadmap.get_next_recommended_skill
def get_next_recommended_skill(student_id: str, target_career: str) -> dict:
    return {"skill": "Missing Skill A", "reason": "High priority for role"}

def render():
    st.header("Skill Gap & Roadmap")
    
    if "student_id" not in st.session_state or "target_career" not in st.session_state:
        st.warning("Please complete previous steps.")
        return
        
    student_id = st.session_state.student_id
    current_skills = st.session_state.current_skills
    target_career = st.session_state.target_career
    
    try:
        gap = calculate_skill_gap(student_id, current_skills, target_career)
        st.subheader("Skill Gap Analysis")
        st.write(f"Match: {gap.get('match_percentage', 0)}%")
        st.write("Missing Skills:", ", ".join(gap.get('missing_skills', [])))
        
        rec = get_next_recommended_skill(student_id, target_career)
        st.info(f"Recommended next skill: **{rec.get('skill')}** - {rec.get('reason')}")
        
        roadmap = generate_roadmap(student_id, target_career, current_skills)
        st.subheader("Your Roadmap")
        for i, step in enumerate(roadmap.get('steps', [])):
            st.write(f"{i+1}. {step['title']} ({step['description']})")
            
        if st.button("Next: Update Progress"):
            st.session_state.workflow_step = "Update Progress"
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading roadmap: {str(e)}")
