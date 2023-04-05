"""
This module provides utility functions for initializing Streamlit \
session state and text fields.
"""

import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from optimizer.utils.format import custom_layout


def init_state(name, value=False):
    """
    Initialise session_state with provide field name and value
    """

    if name not in st.session_state:
        st.session_state[name] = value


def initialise():
    """
    Initialises controllers states and text fields

    Returns:
    None
    """
    # initialise controllers states
    button_states = ['btn_summary', 'btn_analyse', 'btn_estimate',
                     'btn_generate_statement', 'btn_sort_skills',
                     'btn_generate_skills', 'new_statements',
                     'new_skills']
    for button in button_states:
        init_state(button)

    # initialise text fields
    text_fields = ['txt_jd', 'txt_resume', 'txt_skills',
                   'statement', 'dl_link', 'letter']

    for text in text_fields:
        init_state(text, '')

    # initialise list fields
    list_fields = ['experiences', 'motivations', 'skills', 'choosen_skills']

    for field in list_fields:
        init_state(field, [])

    custom_layout()


def reset():
    """
    Resets the current session while keeping the text input of resume. It \
    then executes ''initialise()'' and ''switch_page(''Job description'')''.
    """
    if st.button("Warning: Reset", help="You will lose all your progress!"):
        st.session_state = {'txt_resume': st.session_state['txt_resume']}
        initialise()
        switch_page('Job description')
