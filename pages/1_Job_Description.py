"""
This page contains functions to upload a job description and summarize it \
by calling the OpenAI GPT API.
"""
import streamlit as st
from optimizer.core.initialisation import initialise
from optimizer.gpt.query import get_company_role, summary_job_description

st.set_page_config(
    page_title="Job Description",
    page_icon=":microscope:",
)

initialise()


def job_description():
    """
    Asks the user to copy and paste a job description, calls \
    the `summary_job_description` function to summarize it, \
    and displays the summary to the user.

    Returns:
    None
    """
    st.markdown("<h2 style='text-align: center;'>Job Description</h2>",
                unsafe_allow_html=True)
    st.session_state['txt_jd'] = st.text_area(
        'Job Description',
        st.session_state['txt_jd'],
        placeholder="Copy and Paste the job description",
        height=300
    )
    if st.button('Summary'):
        st.session_state['btn_summary'] = True

    if st.session_state['btn_summary']:
        with st.spinner("Summarying the job ..."):
            job_analysed = summary_job_description(st.session_state['txt_jd'])
            st.session_state['company_role'] = get_company_role()
        st.markdown(f"__Position:__ {st.session_state['company_role'] }")
        st.markdown(f"__Summary:__ {job_analysed}")


job_description()
