"""
This module contains functions to parse resume data in JSON format, \
and extract information like personal statement, skills and experiences \
for further use.
"""

import datetime
import json
import re
import uuid
import streamlit as st
from optimizer.gpt.api import MODEL, call_openai_api
from optimizer.utils.extract import extract_code, extract_by_quotation_mark


SECRETARY_ROLE = """You are my secretary. I need you to identify and \
extract all the information of a resume. You have to do it very carefully."""


def search_field(obj: dict, candidates: list) -> str | list | dict:
    """
    Search for the first matching field in the given object, selected from a list of candidates.

    Parameters:
        obj (dict): The object to search for the field in.
        candidates (sequence): A sequence of candidate field names to search for.

    Returns:
        The value of the first matching field found in the object, or None if no such field exists.
    """
    candidate = (v for i, v in enumerate(candidates) if v in obj)
    key = next(candidate, None)
    if key is not None:
        return obj[key]
    else:
        return None


def get_statement(resume: dict) -> str | None:
    """
    A function that takes a resume as a dictionary and returns the personal statement if it exists.

    Args:
        resume (dict): The dictionary representing the resume to be searched.

    Returns:
        str | None: Returns the personal statement if it exists, otherwise returns None.
    """
    candidates = ['profile', 'personal_statement',
                  'personal_profile', 'statement']
    statement = search_field(resume, candidates)
    if statement is not None:
        return statement
    return ""


def get_skills(resume: dict) -> list | None:
    """
    Searches the input `resume` dictionary for a list of skills. \
    The function searches for skills under different keys such as 'skills', \
    'Core Competencies', 'core_competencies', 'Competencies', and \
    'competencies'. If a skills list is found, it is returned. \
    If no skills are found, this function returns None.

    Parameters:
    -----------
    resume: dict
        The dictionary from which to extract skills.

    Returns:
    --------
    list | None:
        A list of skills if any are found. If no skills are found, None is returned.
    """
    candidates = ['skills', 'Core Competencies',
                  'core_competencies', 'Competencies', 'competencies']
    skills = search_field(resume, candidates)
    if skills is not None:
        return skills
    return ""


def get_experiences(resume: dict) -> dict | None:
    """
    Search for experience-related fields in a resume and return them if found.

    Args:
        resume (dict): A dictionary containing fields in a resume.

    Returns:
        dict | None: A dictionary with experience-related fields if found, otherwise None.
    """

    candidates = ['experience', 'experiences',
                  'work_experiences', 'professional_experience']
    experiences = search_field(resume, candidates)
    if experiences is not None:
        return experiences
    return ""


def get_date_range(exp: dict) -> str:
    """
    Get a date range string in the format "MMM YYYY - MMM YYYY"
    from a dictionary of start and end dates.

    Parameters:
    exp (dict): A dictionary with keys 'start' and 'end' that each
                hold a dictionary with keys 'year' and 'month'.

    Returns:
    str_range (str): A string in the format "MMM YYYY - MMM YYYY".
    """
    date_start = datetime.datetime(year=int(exp['start']['year']),
                                   month=int(exp['start']['month']), day=1)
    month_start = date_start.strftime('%b')
    date_end = datetime.datetime(year=int(exp['end']['year']),
                                 month=int(exp['end']['month']), day=1)
    month_end = date_end.strftime('%b')
    str_range = f"{month_start} {exp['start']['year']} - \
                  {month_end} {exp['end']['year']}"
    return str_range


@st.cache_data
def query_project_title(project_info: str) -> str:
    """
    This function sends a list of messages to an OpenAI API for processing \
    and returns the extracted project name from the API response.

    Args:
    project_info (str): The information about the project that needs to \
    be queried.

    Returns:
    str: The extracted project name surrounded with code tags.
    """
    messages = [
        {"role": "system", "content": SECRETARY_ROLE},
        {"role": "user", "content": "The following is the resume"},
        {"role": "user", "content": st.session_state['txt_resume']},
        {"role": "user", "content": f"Can you find the project name with \
        this infomration: {project_info}?"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=0.1)
    result_str = extract_code(reply)
    if result_str is None:
        result_str = extract_by_quotation_mark(reply)
    return result_str


@st.cache_data
def query_project_description(project_name: str) -> str:
    """
    Returns the project description of a given `project_name`.

    Args:
    project_name (str): The name of the project to extract the description from.

    Returns:
    str: The extracted project description, surrounded by code tags.
    """
    messages = [
        {"role": "system", "content": SECRETARY_ROLE},
        {"role": "user", "content": "The following is the resume"},
        {"role": "user", "content": st.session_state['txt_resume']},
        {"role": "user", "content": f"Can you extract the project \
        description of Project:  {project_name}, between project name and \
        key contributions?"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=0.1)
    result_str = extract_code(reply)
    return result_str


@st.cache_data
def query_project_contributions(project_name: str) -> list | None:
    """
    Takes in a project_name and generates a list of key contributions
    of the project using OpenAI's GPT3 model.

    Parameters:
    -----------
    project_name : str
        The name of the project whose contributions need to be extracted.

    Returns:
    --------
    contributions : list of str
        The list of key contributions of the project. Each string in the
        list has been stripped of non-alphanumeric characters and whitespaces.
    """
    messages = [
        {"role": "system", "content": SECRETARY_ROLE},
        {"role": "user", "content": "The following is my resume"},
        {"role": "user", "content": st.session_state['txt_resume']},
        {"role": "user", "content": f"Can you extract the key \
        contributions of Project:  {project_name}?"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=0.1)
    result_str = extract_code(reply)

    # assemble contributions list, which contains strings that have \
    # been stripped of non-alphanumeric characters and whitespace.
    if result_str is not None:
        contributions = result_str.strip().split('\n')
        contributions = [re.sub(r'[^A-Za-z0-9 ]+', '', c)
                         for c in contributions]
    else:
        contributions = []
    return contributions
