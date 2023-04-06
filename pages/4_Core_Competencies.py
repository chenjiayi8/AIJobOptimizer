"""
This module provides the functions for generating and sorting skills for a job description.

Functions:
    sort_skills: sort skills based on relevance to job description
    generate_skills: generate skills based on job description and user experiences
    edit_skills: edit skills using sorting or generating functions
"""
import copy
import json
import streamlit as st
from optimizer.core.initialisation import initialise
from optimizer.utils.extract import extract_code
from optimizer.gpt.api import MODEL, SYSTEM_ROLE, call_openai_api

st.set_page_config(
    page_title="Core Competencies",
    page_icon=":toolbox:",
)

initialise()


def parse_skills(reply):
    """
    Extracts a list of skills from a string of comma-separated skills.

        Args:
        - reply (str): A string containing comma-separated skills.

        Returns:
        - skills (list): A list of strings, each representing a parsed skill.
    """
    def capitalize(skill):
        return skill[0].capitalize() + skill[1:]
    skills_str = extract_code(reply)
    skills = skills_str.split(',')
    skills = [capitalize(skill.strip()) for skill in skills]
    return skills


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
    skills_str = ','.join(skills)
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills_str},
        {"role": "user", "content": "Please rank my skills in order of \
        relevance, based on the job description, starting with the most \
        in-demand skill to the least required."},
        {"role": "user", "content": "Please remove the duplicated skills"},
        {"role": "user", "content": "Please list the skills separated by \
        commas: skill1, skill2, skill3"},
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
        reply (str): Extracted skills separated by commas and enclosed in \
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
        and extract {number} skills which are demanded by the job desription? \
        Each skill is less than {words} words."},
        {"role": "user", "content": "Can you please list the skills like \
        skill1, skill2, and skill3 separately using commas instead of 'and' \
        to join the last two skills, and provide your response in a single \
        paragraph?"},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code>skill1, skill2, skill3</code>"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=temperature)
    return reply


def distribute_new_skills():
    """
    This function distributes new skills by adding them to the user's master \
    skills list (`skills`), sorted skills list (`sorted_skills`), and chosen \
    skills list (`choosen_skills`), for as long as they don't already exist \
    in those lists. It then removes the new skills from the `new_skills` \
    list, updates the `max_skills_number` value based on the length of the \
    `choosen_skills` list.

    Parameters:
    None

    Returns:
    None

    """
    skills = copy.deepcopy(st.session_state['new_skills'])
    for skill in skills:
        if skill not in st.session_state['skills']:
            st.session_state['skills'].append(skill)
        if skill not in st.session_state['sorted_skills']:
            st.session_state['sorted_skills'].append(skill)
        if skill not in st.session_state['choosen_skills']:
            st.session_state['choosen_skills'].append(skill)

    st.session_state['new_skills'] = []
    st.session_state['max_skills_number'] = len(
        st.session_state['choosen_skills'])


def on_skills_sorted():
    """
    This function retrieves the sorted list of skills from the session state \
    and saves a truncated version of it in the session state. The maximum \
    number of skills to save is determined by the value stored in the \
    'max_skills_number' variable of the session state.

    Parameters:
    None

    Returns:
    None

    Session State:
    - 'sorted_skills' (list): The sorted list of skills.
    - 'max_skills_number' (int): The maximum number of skills to save.
    - 'choosen_skills' (list): The truncated list of skills that is saved in the session state.
    """
    skills = st.session_state['sorted_skills']
    max_number = st.session_state['max_skills_number']
    st.session_state['choosen_skills'] = \
        skills[:max_number] if len(skills) > max_number else skills


def on_skills_number_changed():
    """
    Updates the list of chosen skills based on the maximum number of skills \
    allowed.

    If the maximum number of skills allowed is greater than the number of \
    chosen skills, the skill pool is used (i.e., all sorted skills). \
    Otherwise, the list of chosen skills is used. The updated list of chosen \
    skills is stored in session state.

    Args:
        None

    Returns:
        None
    """
    max_number = st.session_state['max_skills_number']
    if max_number > len(st.session_state['choosen_skills']):
        skills = st.session_state['sorted_skills']  # skill pool
    else:
        skills = st.session_state['choosen_skills']
    st.session_state['choosen_skills'] = \
        skills[:max_number] if len(skills) > max_number else skills


def trigger_skills_number_changed():
    """
    Updates the maximum number of skills to be displayed and sets the
    session state 'skills_number_changed' to True.

    Parameters:
    None

    Returns:
    None
    """
    st.session_state['max_skills_number'] = \
        st.session_state.max_skills_number_slider
    st.session_state['skills_number_changed'] = True


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

    for skill in st.session_state['choosen_skills']:
        if skill not in st.session_state['skills']:
            st.session_state['skills'].append(skill)

    # limit the number of choosen skills
    if st.session_state['skills_number_changed']:
        on_skills_number_changed()
        st.session_state['skills_number_changed'] = False
        st.experimental_rerun()

    st.session_state['choosen_skills'] = st.multiselect(
        "Core Competencies:",
        options=st.session_state['skills'],
        default=st.session_state['choosen_skills'],
        key='choosen_skills_multiselect'
    )
    if len(st.session_state['skills']) > 0:
        col_skills_sort, col_max_skills = st.columns([1, 1])
        with col_skills_sort:
            if st.button('Sort skills', help="Sort your skills based on their \
                        relevance to the job description", key="sort_skills"):
                st.session_state['btn_sort_skills'] = True
                with st.spinner("Sorting"):
                    reply = sort_skills(
                        st.session_state['txt_jd'],
                        st.session_state['skills']
                    )
                    st.session_state['sorted_skills'] = parse_skills(reply)
                    on_skills_sorted()
                    st.experimental_rerun()

        with col_max_skills:
            st.session_state['max_skills_number'] = st.slider(
                "Total number of skills", 0, len(st.session_state['skills']),
                value=st.session_state['max_skills_number'],
                key="max_skills_number_slider",
                on_change=trigger_skills_number_changed)

    col_skills_generate_number, \
        col_skills_generate_words, \
        col_skills_generate_temp = st.columns([1, 1, 1])
    with col_skills_generate_number:
        create_skills_number = st.slider(
            "Number of skills", 3, 10, value=5, key="create_skills_number")

    with col_skills_generate_words:
        skills_words = st.slider(
            "Words of skill", 3, 10, value=5, key="skills_words")

    with col_skills_generate_temp:
        skills_temp = st.slider("Temperature", 0.0, 1.0,
                                value=0.2, key="skills_temp")

    col_skills_sort, \
        col_skills_null, \
        col_skills_generate = st.columns([1, 1, 1])

    with col_skills_null:
        st.write("")

    with col_skills_generate:
        if st.button('Generate skills', help="Generate skills from the job \
                    description and your experiences", key="generate_skills"):
            reply = generate_skills(
                create_skills_number, skills_words, skills_temp)
            st.session_state['new_skills'] = parse_skills(reply)
            st.session_state['btn_generate_skills'] = True
            st.session_state['btn_sort_skills'] = False

    if st.session_state['btn_generate_skills'] and \
            len(st.session_state['new_skills']) > 0:
        st.session_state['new_skills'] = st.multiselect(
            "Experience based Core Competencies",
            st.session_state['new_skills'],
            st.session_state['new_skills']
        )
        if st.button("Add selected skills",
                     help="Click to add selected new skills",
                     key="add_new_skills"):
            distribute_new_skills()
            st.experimental_rerun()

    if len(st.session_state['choosen_skills']) > 0:
        st.write('#### Final Core Competencies:')
        st.write(f"{' | '.join(st.session_state['choosen_skills'])}")


edit_skills()
