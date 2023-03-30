"""
This module contains functions to summarize a job description \
by calling the OpenAI GPT API. The main function is \
`summary_job_description`, which takes a job description text \
as input and returns a summarized version of it.
"""
import streamlit as st
from optimizer.gpt.api import call_openai_api, MODEL


SYSTEM_ROLE = "You are my Career Coach. You will help me revise my resume for a target job."


@st.cache_data(show_spinner=False)
def summary_job_description(txt_jd):
    """
    Call GPT API to summary the job


    Returns:
    A str representing the reply from GPT API
    """
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": "Can you tell me what is the job about?"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=0.8)
    return reply


def job_description():
    """
    Asks the user to copy and paste a job description, calls \
    the `summary_job_description` function to summarize it, \
    and displays the summary to the user.

    Returns:
    None
    """

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
        st.markdown("### Can you tell me what is the job about?")
        st.write(job_analysed)
