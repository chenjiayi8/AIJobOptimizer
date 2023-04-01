"""
This module contains functions to analyse the resume \
by calling the OpenAI GPT API.
"""

import streamlit as st
from optimizer.gpt.api import call_openai_api, MODEL, SYSTEM_ROLE
from optimizer.utils.format import custom_layout
from optimizer.utils.parser import parse_resume

st.set_page_config(
    page_title="Resume",
    page_icon=":notebook:",
)


@st.cache_data(show_spinner=False)
def estimate_match_rate(txt_jd: str, txt_resume: str) -> str:
    """
    Estimate the match rate between a job description and a resume using OpenAI's GPT-3 API.

    Parameters
    ----------
    txt_jd : str
        The text of the job description.
    txt_resume : str
        The text of the resume.

    Returns
    -------
    str
        The estimated match rate between the job description and the resume, as a string.

    """
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "user", "content":  "The job description is following:"},
        {"role": "user", "content":  txt_jd},
        {"role": "user", "content":  "My resume is following:"},
        {"role": "user", "content":  txt_resume},
        {"role": "user", "content": "Can you help me estimate the match \
        rate between my experiences and this job description?"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=0.5)
    return reply


def upload_resume():
    """
    Takes the resume text from user and parse the text to assign \
    components of resume; provide function to estimate the match rate \
    with the job description

    Returns:
    None
    """
    st.markdown("<h2 style='text-align: center;'>Resume</h2>",
                unsafe_allow_html=True)
    st.session_state['txt_resume'] = st.text_area(
        'Your resume',
        st.session_state['txt_resume'],
        placeholder="Copy and Paste your full resume (max 3 pages)",
        height=300
    )

    if st.button('Analyse'):
        st.session_state['btn_analyse'] = True

    if st.session_state['btn_analyse']:
        with st.spinner('Analysing your resume ...'):
            parse_resume(st.session_state['txt_resume'])

        with st.spinner("Estimating the match rate ..."):
            reply = estimate_match_rate(
                st.session_state['txt_jd'], st.session_state['txt_resume'])
            st.markdown(
                "### Can you help me estimate the match rate between \
                my experiences and this job description?")
            st.write(reply)


upload_resume()
custom_layout()
