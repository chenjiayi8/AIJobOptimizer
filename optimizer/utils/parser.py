"""
This module contains functions to parse resume data in JSON format, \
and extract information like personal statement, skills and experiences \
for further use.
"""

import copy
import datetime
import json
import re
import uuid
import streamlit as st
from optimizer.gpt.api import MODEL, call_openai_api
from optimizer.utils.extract import extract_code, extract_by_quotation_mark


SECRETARY_ROLE = """You are my secretary. I need you to identify and \
extract all the information of a resume. You have to do it very carefully."""


def search_field(obj: dict, candidates: list) -> any:
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
    return []


def get_experiences(resume: dict) -> list | None:
    """
    Search for experience-related fields in a resume and return them if found.

    Args:
        resume (dict): A dictionary containing fields in a resume.

    Returns:
        list | None: A list with experience-related fields if found, otherwise None.
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
def query_project_description(project: dict) -> str:
    """
    Returns the project description of a given `project_name`.

    Args:
    project_name (str): The name of the project to extract the description from.

    Returns:
    str: The extracted project description, surrounded by code tags.
    """
    # project_str = json.dumps(project, indent=2)
    messages = [
        {"role": "system", "content": SECRETARY_ROLE},
        {"role": "user", "content": "The following is the resume"},
        {"role": "user", "content": st.session_state['txt_resume']},
        {"role": "user", "content": "The following is one project of \
        the resume:"},
        {"role": "user", "content": f"Project name/title: {project['title']}"},
        {"role": "user", "content": "Can you find the project description \
        from the resume, located between the project name and key \
        contributions?"},
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


def parse_project(exp_or_project_in: dict) -> dict:
    """
    Parses a project from a given dictionary.

    Parameters:
    exp_or_project_in (dict): A dictionary containing the project information.

    Returns:
    dict: A dictionary containing the parsed project with the following keys:
          'uuid': A randomly generated unique identifier.
          'title': The project's title.
          'description': The project's description.
          'contributions': The project's contributions.
    """
    project = {}
    project['uuid'] = str(uuid.uuid4())
    # locate project title; in some cases, GPT employs description instead
    project['title'] = search_field(
        exp_or_project_in, ['project', 'description', 'title'])
    project['description'] = search_field(
        exp_or_project_in, ['project_description', 'project description', 'description'])

    # Check if the value of key 'description' in 'project' is None or \
    # equal to the value of key 'title' in 'project', and if true, \
    # call the function 'query_project_description'
    if project['description'] is None or \
            project['description'] == project['title']:
        project['title'] = query_project_title(project['title'])
        project['description'] = query_project_description(project)
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
        exp_or_project_in, ['contributions', 'key_contributions'])
    if project['contributions'] is None:
        project['contributions'] = query_project_contributions(
            project['title'])
    return project


@st.cache_data
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
    exp_out['company'] = search_field(
        exp_in, ['company', 'organisation', 'employer'])
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
        project = parse_project(copy.deepcopy(exp_in))
        exp_out['projects'] = [project]
    else:
        for i in range(len(exp_out['projects'])):
            project_old = copy.deepcopy(exp_out['projects'][i])
            exp_out['projects'][i] = parse_project(project_old)

    return exp_out


def parse_expereinces() -> None:
    """
    Parses the experiences and generates a unique UUID for each experience, \
    and returns a list of experiences as dictionaries.

    Each experience is parsed using the `parse_experience()` function,
    which should return a dictionary with keys 'title', 'company', \
    'description', and 'date_range'.

    The UUID is generated using the `uuid.uuid4()` function and added to
    each experience dictionary with key 'uuid'.

    The parsed experiences are stored in the `st.session_state` dictionary.

    Returns:
        None
    """
    experiences = []
    for exp in st.session_state['experiences']:
        if 'uuid' not in exp:
            experience = parse_experience(exp)
            experience['uuid'] = str(uuid.uuid4())
        else:
            experience = copy.deepcopy(exp)

        experiences.append(experience)
    st.session_state['experiences'] = experiences
    with st.expander("Debug: preconditioned experiences"):
        st.write("experiences: ", experiences)


@st.cache_data
def parse_json(txt_resume: str) -> None:
    """
    Parse json str and assign components of resume

    Returns:
    None
    """
    st.session_state['resume'] = json.loads(txt_resume)
    st.session_state['statement'] = st.session_state['resume']['statement']
    skills = []
    for value in st.session_state['resume']['skills'].values():
        skills += value

    st.session_state['skills'] = skills
    st.session_state['sorted_skills'] = skills
    st.session_state['choosen_skills'] = skills
    st.session_state['max_skills_number'] = len(skills)
    st.session_state['experiences'] = st.session_state['resume']['experiences']


def parse_api_json(reply_json_str: str) -> None:
    """
    Parses and stores the API response JSON string in the session state.

    Args:
        reply_json_str (str): The JSON string returned by the API response.

    Returns:
        None
    """
    st.session_state['resume'] = json.loads(reply_json_str)
    st.session_state['statement'] = get_statement(st.session_state['resume'])
    skills = get_skills(st.session_state['resume'])
    st.session_state['skills'] = skills
    st.session_state['sorted_skills'] = skills
    st.session_state['choosen_skills'] = skills
    st.session_state['max_skills_number'] = len(skills)
    st.session_state['experiences'] = get_experiences(
        st.session_state['resume'])


@st.cache_data(show_spinner=False)
def analyse_resume(txt_resume: str, temperature: float) -> str:
    """Extracts information from a resume using GPT-3.

    Args:
        txt_resume (str): The text of the resume to analyse.
        temperature (float): The sampling temperature to use when generating responses.

    Returns:
        A dictionary-like object that contains the extracted information from the resume.

    Raises:
        ValueError: If the `txt_resume` argument is an empty string or None.
        OpenAIAPIError: If the OpenAI API returns an error status code or message.
    """
    if txt_resume is None or len(txt_resume) == 0:
        raise ValueError("Invalid resume")
    temp_msgs = [
        {"role": "system", "content": "You are my secretary. I need you to \
        identify and extract all the information of a resume. You have to \
        do it very carefully."},
        {"role": "user", "content": "The following is the resume"},
        {"role": "user", "content": txt_resume},
        {"role": "user", "content": "Can you give me the information as JSON-like?"},
    ]
    reply = call_openai_api(MODEL, temp_msgs, temperature=temperature)
    reply_json_str = extract_code(reply)
    return reply_json_str


def show_debug_info() -> None:
    """
    Displays information about the user's resume, statement, skills, and experiences.

    Displays each piece of information in an expander to make it collapsible.
    """

    with st.expander("Debug: Raw input"):
        st.write("resume: ", st.session_state['resume'])
    with st.expander("Debug: statement"):
        st.write("statement: ", st.session_state['statement'])
    with st.expander("Debug: skills"):
        st.write("Skills: ", st.session_state['skills'])
    with st.expander("Debug: experiences"):
        st.write("Experiences: ", st.session_state['experiences'])


def parse_resume(txt_resume: str) -> None:
    """
    Caches the result of parsing the provided resume text using JSON \
    parsing or API analysis and JSON parsing.

    Args:
        txt_resume (str): The text of the resume to be parsed.

    Returns:
        None
    """
    try:
        parse_json(txt_resume)
    except ValueError:
        reply_json = analyse_resume(txt_resume, temperature=0.1)
        parse_api_json(reply_json)
    except Exception as error:
        print(f"Error: {str(error)}")
    finally:
        parse_expereinces()
        show_debug_info()
