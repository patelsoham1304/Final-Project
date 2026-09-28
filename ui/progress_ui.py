import streamlit as st

def render():
    st.header("Update Progress")
    
    if "student_id" not in st.session_state:
        st.warning("Please complete previous steps.")
        return
        
    with st.form("progress_form"):
        st.write("Mark skills as completed:")
        skill_a = st.checkbox("Missing Skill A")
        skill_b = st.checkbox("Missing Skill B")
        
        submitted = st.form_submit_button("Save & Go to Dashboard")
        
        if submitted:
            st.session_state.workflow_step = "Dashboard"
            st.rerun()
