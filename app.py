import streamlit as st
import ui.profile_ui
import ui.career_ui
import ui.roadmap_ui
import ui.progress_ui
import ui.planner_ui
import ui.dashboard

def main():
    st.set_page_config(page_title="Education Path Generator", layout="wide")
    
    if "workflow_step" not in st.session_state:
        st.session_state.workflow_step = "Create Student"
        
    st.sidebar.title("Navigation")
    steps = [
        "Create Student", 
        "Select Career", 
        "Skill Gap & Roadmap", 
        "Update Progress", 
        "Dashboard"
    ]
    
    # Allow manual navigation for testing, though normally controlled by buttons
    st.session_state.workflow_step = st.sidebar.radio(
        "Go to", 
        steps, 
        index=steps.index(st.session_state.workflow_step) if st.session_state.workflow_step in steps else 0
    )
    
    if st.session_state.workflow_step == "Create Student":
        ui.profile_ui.render()
    elif st.session_state.workflow_step == "Select Career":
        ui.career_ui.render()
    elif st.session_state.workflow_step == "Skill Gap & Roadmap":
        ui.roadmap_ui.render()
    elif st.session_state.workflow_step == "Update Progress":
        ui.progress_ui.render()
    elif st.session_state.workflow_step == "Dashboard":
        ui.dashboard.render()

if __name__ == "__main__":
    main()
