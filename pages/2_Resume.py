"""
This page contains functions to upload a resume and analyse it by calling \
the OpenAI GPT API.
"""

import json
import streamlit as st
from st_dropfill_textarea import st_dropfill_textarea
from optimizer.core.initialisation import initialise
from optimizer.gpt.query import estimate_match_rate
from optimizer.utils.parser import parse_resume
from optimizer.io.docx_file import docx_to_text

st.set_page_config(
    page_title="Resume",
    page_icon=":notebook:",
)

initialise()


def show_debug_info() -> None:
    """
    Displays information about the user's resume, statement, skills, and experiences.

    Displays each piece of information in an expander to make it collapsible.
    """
    if 'resume' not in st.session_state:
        return
    with st.expander("Debug: Raw input"):
        st.write("resume: ", st.session_state['resume'])
    with st.expander("Debug: statement"):
        st.write("statement: ", st.session_state['statement'])
    with st.expander("Debug: skills"):
        st.write("Skills: ", st.session_state['skills'])
    with st.expander("Debug: experiences"):
        st.write("Experiences: ", st.session_state['experiences'])


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
    with st.form("my-form", clear_on_submit=True):
        uploaded_file = st.file_uploader(
            "Upload your resume", type='docx')
        submitted = st.form_submit_button("UPLOAD!")
    if submitted and uploaded_file is not None:
        st.session_state['txt_resume'] = docx_to_text(uploaded_file.getvalue())
    placeholder = ("* Drag and drop your resume (docx, text, html or json)\n"
                   "* Or Copy and Paste your full resume\n"
                   "* Max 3 pages\n")
    new_txt_resume = st_dropfill_textarea(
        "Your resume",
        st.session_state['txt_resume'],
        placeholder=placeholder,
        height=300,
        key="textarea_resume",
    )
    if new_txt_resume != st.session_state['txt_resume']:
        st.session_state['txt_resume'] = new_txt_resume
        # st.experimental_rerun()

    col_analyse, col_download, col_estimate = st.columns([1, 1, 1])

    with col_analyse:
        if st.button('Analyse', help='Analyse your resume and pre-fill the form'):
            with st.spinner('Analysing your resume ...'):
                parse_resume(st.session_state['txt_resume'])
                st.session_state['btn_analyse'] = True

    with col_download:
        if st.session_state['btn_analyse']:
            help_message = """
            Download your resume in JSON format to avoid waiting for the \
            analysis next time.
            """
            st.download_button(
                label="Download",
                data=json.dumps(st.session_state['resume'], indent=4),
                file_name="resume.json",
                mime="application/json",
                help=help_message
            )
        else:
            st.write("")

    with col_estimate:
        if st.button("Estimate", help="Estimate your match rate with the job"):
            st.session_state['btn_estimate'] = True

    help_message = """
            Download your resume in JSON format to avoid waiting for the \
            analysis next time.
    """
    if st.session_state['btn_analyse']:
        show_debug_info()
    if st.session_state['btn_estimate']:
        with st.spinner("Estimating the match rate ..."):
            reply = estimate_match_rate(
                st.session_state['txt_jd'], st.session_state['txt_resume'])
            st.markdown(
                "### Can you help me estimate the match rate between \
                my experiences and this job description?")
            st.write(reply)


upload_resume()
