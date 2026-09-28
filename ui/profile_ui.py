import streamlit as st

def render():
    st.header("Student Profile")
    
    with st.form("profile_form"):
        student_id = st.text_input("Student ID (e.g., S123)")
        name = st.text_input("Full Name")
        
        submitted = st.form_submit_button("Next: Select Career")
        
        if submitted:
            if student_id and name:
                st.session_state.student_id = student_id
                st.session_state.student_name = name
                st.session_state.workflow_step = "Select Career"
                st.rerun()
            else:
                st.error("Please fill in all fields")
