"""
This module provides utility functions for initializing Streamlit \
session state and text fields.
"""

import streamlit as st


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
    button_states = ['btn_summary', 'btn_analyse', 'btn_generate_statement',
                     'btn_sort_skills', 'btn_generate_skills', 'new_statements',
                     'new_skills']
    for button in button_states:
        init_state(button)

    # initialise text fields
    text_fields = ['txt_jd', 'txt_resume']

    for text in text_fields:
        init_state(text, '')
