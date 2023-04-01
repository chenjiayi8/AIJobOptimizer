"""
This module provides the functions for generating and sorting skills for a job description.

Functions:
    sort_skills: sort skills based on relevance to job description
    generate_skills: generate skills based on job description and user experiences
    edit_skills: edit skills using sorting or generating functions
"""

import json
import streamlit as st
from optimizer.utils.extract import extract_code
from optimizer.gpt.api import MODEL, SYSTEM_ROLE, call_openai_api

st.set_page_config(
    page_title="Core Competencies",
    page_icon=":toolbox:",
)


@st.cache_data(show_spinner=False)
def sort_skills(txt_jd: str, skills: str) -> str:
    """
    This function takes in two parameters the job description and the user's \
    skills. It then sends a series of messages to the OpenAI API to rank and \
    sort the user's skills based on their relevance to the job description.

    Parameters:
    - txt_jd (str): The job description.
    - skills (str): A string containing the user's skills.

    Returns:
    - reply (str): A string containing the sorted user's skills based on \
    their relevance to the job description.
    """
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills},
        {"role": "user", "content": "Please rank my skills in order of \
        relevance, based on the job description, starting with the most \
        in-demand skill to the least required."},
        {"role": "user", "content": "Remove the duplicated, chain the result \
        with ' | '"},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=0.2)
    return reply


def generate_skills(number: int, words: int, temperature: float = 0.2) -> str:
    """
    This function generates skills from the job description and user \
    experiences.

    Args:
        number (int): Number of skills to be extracted from the job \
        description.
        words (int): Maximum number of words allowed for each extracted skill.
        temperature (float): Controls the randomness and creativity of output.

    Returns:
        reply (str): Extracted skills separated by '|' and enclosed in \
        '<code></code>'.
    """
    txt_jd = st.session_state['txt_jd']
    experiences_str = json.dumps(st.session_state['experiences'])
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": "I will give you my experiences as \
        following:"},
        {"role": "user", "content": experiences_str},
        {"role": "user", "content": f"From my experiences, can you identify \
        and extract {number} skills which is demanded by the job desription? \
        Each skill is less than {words} words. Chained the skills with ' | '"},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=temperature)
    return reply


def edit_skills():
    """
    Method to render a skill-related section on a Streamlit app page. \
    Allows users to edit core competencies as a text area, set the number of \
    skills to generate, define the number of words in each skill, and set \
    the temperature value for skill generation. The user can sort and/or \
    generate skills based on these inputs, and the final output is displayed \
    on the page.

    Returns:
    None.

    """
    st.markdown("<h2 style='text-align: center;'>Skills</h2>",
                unsafe_allow_html=True)
    st.session_state['skills'] = st.text_area(
        'Core Competencies', st.session_state['skills'], height=200)
    col_skills_generate_number, \
        col_skills_generate_words, \
        col_skills_generate_temp = st.columns([1, 1, 1])
    with col_skills_generate_number:
        skills_number = st.slider(
            "Number of skills", 3, 10, value=5, key="skills_number")

    with col_skills_generate_words:
        skills_words = st.slider(
            "Words of skill", 3, 10, value=5, key="skills_words")

    with col_skills_generate_temp:
        skills_temp = st.slider("Temperature", 0.0, 1.0,
                                value=0.2, key="skills_temp")

    col_skills_sort, \
        col_skills_null, \
        col_skills_generate = st.columns([1, 1, 1])

    with col_skills_sort:
        if st.button('Sort skills', help="Sort your skills based on their \
                    relevance to the job description"):
            st.session_state['btn_sort_skills'] = True
            with st.spinner("Sorting"):
                reply = sort_skills(
                    st.session_state['txt_jd'], st.session_state['skills'])
                sorted_skills = extract_code(reply)
                st.session_state['sorted_skills'] = sorted_skills

    with col_skills_null:
        st.write("")

    with col_skills_generate:
        if st.button('Generate skills', help="Generate skills from the job \
                    description and your experiences"):
            reply = generate_skills(skills_number, skills_words, skills_temp)
            new_skills = extract_code(reply)
            st.session_state['new_skills'] = ' | ' + new_skills.strip()
            st.session_state['btn_generate_skills'] = True
            st.session_state['btn_sort_skills'] = False

    if st.session_state['btn_generate_skills'] and \
            not st.session_state['btn_sort_skills']:
        st.write('#### Experience based Core Competencies')
        st.write(st.session_state['new_skills'])

    if not st.session_state['btn_generate_skills'] and \
            st.session_state['btn_sort_skills']:
        st.write('#### Job description based Core Competencies')
        st.write(st.session_state['sorted_skills'])

    if st.session_state['btn_generate_skills'] and \
            st.session_state['btn_sort_skills']:
        st.write('#### Final Core Competencies')
        st.write(st.session_state['sorted_skills'])


edit_skills()
