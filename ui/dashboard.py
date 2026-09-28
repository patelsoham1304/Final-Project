import streamlit as st

# TEMP UI MOCK: Will be replaced by modules.progress.calculate_overall_progress
def calculate_overall_progress(student_id: str) -> dict:
    return {
        "overall_percentage": 65,
        "completed_skills": ["Python", "JavaScript", "Missing Skill A"]
    }

def render():
    st.header("Dashboard")
    
    if "student_id" not in st.session_state:
        st.warning("Please create a profile first.")
        return
        
    student_id = st.session_state.student_id
    
    try:
        progress = calculate_overall_progress(student_id)
        st.metric("Overall Progress", f"{progress.get('overall_percentage')}%")
        
        st.subheader("Completed Skills")
        for skill in progress.get('completed_skills', []):
            st.write(f"- {skill}")
            
        if st.button("Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
