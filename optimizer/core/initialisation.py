"""
This module provides utility functions for initializing Streamlit \
session state and text fields.
"""

from typing import Any
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from optimizer.gpt.api import get_default_mode
from optimizer.utils.format import custom_layout


def init_state(name, value: Any = False):
    """
    Initialise session_state with provide field name and value
    """

    if name not in st.session_state:
        st.session_state[name] = value


def initialise(formatted=True):
    """
    Initialises controllers states and text fields

    Returns:
    None
    """
    # initialise controllers states
    state_fields = [
        "btn_summary",
        "btn_analyse",
        "btn_estimate",
        "btn_generate_statement",
        "btn_sort_skills",
        "btn_generate_skills",
        "skills_number_changed",
        "messages_initalised",
    ]
    for field in state_fields:
        init_state(field, False)

    # initialise text fields
    text_fields = [
        "txt_jd",
        "txt_resume",
        "txt_skills",
        "statement",
        "dl_link",
        "letter",
        "company_role",
        "job_analysed",
    ]

    for field in text_fields:
        init_state(field, "")

    # initialise list fields
    list_fields = [
        "new_statements",
        "new_skills",
        "experiences",
        "motivations",
        "skills",
        "sorted_skills",
        "choosen_skills",
        "background",
        "messages",
        "project_choices",
    ]

    for field in list_fields:
        init_state(field, [])

    # initialise int fields
    int_fields = [
        "max_skills_number",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
    ]
    for field in int_fields:
        init_state(field, 0)

    # initialise float fields
    float_fields = ["temperature_message"]
    for field in float_fields:
        init_state(field, 0.5)

    # initialise GPT MODEL
    init_state("MODEL", get_default_mode())

    # initialise layout options
    init_state("layouts", ["centered", "wide"])
    init_state("layout", st.session_state["layouts"][0])

    if formatted:
        custom_layout()


def get_layout():
    """
    Returns the current layout of the Streamlit app.

    Returns:
    str: The current layout of the Streamlit app.
    """
    return (
        st.session_state["layout"]
        if "layout" in st.session_state
        else "centered"
    )


def reset():
    """
    Resets the current session while keeping the text input of resume. It \
    then executes ''initialise()'' and ''switch_page(''Job description'')''.
    """
    keep_list = ["txt_resume", "layouts", "layout", "MODEL"]
    if st.button("Warning: Reset", help="You will lose all your progress!"):
        for key in st.session_state:
            if key not in keep_list:
                del st.session_state[key]
        initialise()
        switch_page("Job description")
