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


def parse_experience(exp_in: dict) -> dict:
    '''
    Given a dictionary `exp_in` containing information about a work experience,
    this function parses the dictionary and returns a new dictionary `exp_out`
    containing the following fields:

     - 'title': the job title
     - 'company': the name of the company or organization
     - 'date_range': the date range of the experience (if available),
     - 'projects': a list of projects associated with the experience, \
        where each project is represented as a dictionary with fields:
                - 'uuid': a unique identifier for the project
                - 'title': the title of the project
                - 'description': a description of the project
                - 'contributions': a list of contributions made to the project

    For each project in the input dictionary 'exp_in', the function \
    searches for the project title, description, and contributions. If \
    the values are missing, the function attempts to query for them using \
    various strategies.

    Arguments:
    exp_in -- a dictionary containing information about a work experience

    Returns:
    A dictionary containing the parsed information about the work experience
    '''
    exp_out = {}
    exp_out['title'] = search_field(exp_in, ['title', 'position', 'job_title'])
    exp_out['company'] = search_field(exp_in, ['company', 'organisation'])
    if 'start' in exp_in:
        exp_out['date_range'] = get_date_range(exp_in)
    else:
        exp_out['date_range'] = search_field(
            exp_in, ['dates', 'date', 'date_range'])
    if exp_out['date_range'] is None:
        start_date = search_field(exp_in, ['start_date'])
        end_date = search_field(exp_in, ['end_date'])
        exp_out['date_range'] = start_date + ' - ' + end_date

    exp_out['projects'] = search_field(exp_in, ['projects'])
    if exp_out['projects'] is None:
        project = {}
        project['uuid'] = str(uuid.uuid4())
        # locate project title; in some cases, GPT employs description instead
        project['title'] = search_field(exp_in, ['project', 'description'])
        project['description'] = search_field(
            exp_in, ['project_description', 'project description', 'description'])
        # Check if the value of key 'description' in 'project' is None or \
        # equal to the value of key 'title' in 'project', and if true, \
        # call the function 'query_project_description'
        if project['description'] is None or \
                project['description'] == project['title']:
            project['title'] = query_project_title(project['title'])
            project['description'] = query_project_description(
                project['title'])

        project['description'] = project['description'].replace(
            project['title'], '').strip()
        project['description'] = project['description'].replace(
            'Project:', '').strip()
        project['title'] = project['title'].replace('Project:', '').strip()
        project['title'] = project['title'].replace(
            'The project name is ', '').strip()
        temp_title = extract_by_quotation_mark(project['title'])
        if temp_title is not None:
            project['title'] = temp_title
        project['contributions'] = search_field(
            exp_in, ['contributions', 'key_contributions'])
        if project['contributions'] is None:
            project['contributions'] = query_project_contributions(
                project['title'])

        exp_out['projects'] = [project]
    else:
        for i in range(len(exp_out['projects'])):
            project_old = exp_out['projects'][i]
            project = {}
            project['uuid'] = str(uuid.uuid4())
            project['title'] = search_field(project_old, ['title', 'project'])
            project['description'] = search_field(project_old, ['description'])
            if project['description'] is None:
                project['description'] = query_project_description(
                    project['title'])

            project['contributions'] = search_field(
                project_old, ['key_contributions', 'contributions'])
            if project['contributions'] is None:
                project['contributions'] = query_project_contributions(
                    project_old['title'])
            exp_out['projects'][i] = project

    return exp_out


def parse_expereinces() -> None:
    """
    Parses the experiences stored in the `st.session_state` dictionary,
    generates a unique UUID for each experience, and returns a list of
    experiences as dictionaries.

    Each experience is parsed using the `parse_experience()` function,
    which should return a dictionary with keys 'title', 'company', \
    'description', and 'date_range'.

    The UUID is generated using the `uuid.uuid4()` function and added to
    each experience dictionary with key 'uuid'.

    The parsed experiences are stored back in the `st.session_state` dictionary.

    Returns:
        A list of experiences as dictionaries, with a unique UUID generated
        for each experience.
    """
    experiences = []
    for exp in st.session_state['experiences']:
        experience = parse_experience(exp)
        experience['uuid'] = str(uuid.uuid4())
        experiences.append(experience)
    with st.expander("Debug: preconditioned experiences"):
        st.write("experiences: ", experiences)
    st.session_state['experiences'] = experiences
