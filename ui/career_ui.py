import streamlit as st

def render():
    st.header("Select Career & Skills")
    
    if "student_id" not in st.session_state:
        st.warning("Please create a student profile first.")
        if st.button("Back to Profile"):
            st.session_state.workflow_step = "Create Student"
            st.rerun()
        return
        
    with st.form("career_form"):
        target_career = st.selectbox(
            "Target Career",
            ["Frontend Developer", "Backend Developer", "Data Scientist", "UI/UX Designer"]
        )
        
        current_skills = st.multiselect(
            "Select Current Skills",
            ["Python", "JavaScript", "React", "SQL", "HTML/CSS", "Figma", "Machine Learning"]
        )
        
        submitted = st.form_submit_button("Next: View Skill Gap & Roadmap")
        
        if submitted:
            st.session_state.target_career = target_career
            st.session_state.current_skills = current_skills
            st.session_state.workflow_step = "Skill Gap & Roadmap"
            st.rerun()
