"""
This module contains functions for parsing and selecting statements, skills, \
descriptions, experiences, and contributions to be exported for a project.

"""


from collections import OrderedDict
import copy
import streamlit as st

from optimizer.utils.extract import extract_version_number, extract_code, extract_html_list


def choose_job_description() -> str:
    """
    Selects a job description to export.
    """
    return st.session_state['txt_jd']


def parse_statements(replies: list) -> list:
    """
    Given a list of replies, extracts the code from each reply and \
    appends it as a statement to a list of statements.

    Arguments:
    replies -- a list of strings representing replies

    Returns:
    A list of strings representing statements extracted from replies.

    """
    statements = []
    for reply in replies:
        statement = extract_code(reply)
        statements.append(statement)
    return statements


def choose_statement() -> str:
    """
    Selects a statement to export.

    If a statement_choice is present in the session_state, this function \
    will return the corresponding statement from the new_statements list \
    stored in the session_state. Otherwise, it will return the statement
    originally stored in the session_state.

    Parameters:
    None

    Returns:
    string: The statement to export.
    """
    if 'statement_choice' not in st.session_state:
        return st.session_state['statement']
    index = st.session_state['statement_choice'] - 1
    if index == -1:
        return st.session_state['statement']
    return st.session_state['new_statements'][index]


def choose_skills():
    """
    Selects skills.

    If choosen_skills are present in the session_state, it will return them. \
    Otherwise, it will return the skills originally stored in the \
    session_state.

    Parameters:
    None

    Returns:
    string: The skills to export.
    """
    if 'choosen_skills' in st.session_state:
        if len(st.session_state['choosen_skills']) > 0:
            return st.session_state['choosen_skills']
    return st.session_state['skills']


def choose_project_description(project):
    """
    Selects a description to export.

    If a description_choice is present in the session_state, this function \
    will return the corresponding description from the new_descriptions list \
    stored in the session_state. Otherwise, it will return the description
    originally stored in the session_state.

    Parameters:
    None

    Returns:
    string: The description to export.
    """
    choice_key = 'description_choice_'+project['uuid']
    choice_field = 'new_descriptions_'+project['uuid']
    # use default description
    if not all(key in st.session_state for key in (choice_key,
                                                   choice_field)):
        return project['description']
    index = int(extract_version_number(st.session_state[choice_key]))-1
    if index == -1:
        return project['description']
    return st.session_state[choice_field][index].strip()


def choose_experiences() -> dict | list | None:
    """
    Selects experiences as background information.

    If experiences_chosen are present in the session_state, it will return \
    them. Otherwise, it will return the experiences originally stored in the \
    session_state. Finally if the list of experiences is empty, return None

    Parameters:
    None

    Returns:
    None or A dict or list of the experiences to select.
    """

    if 'experiences_chosen' in st.session_state:
        experiences = st.session_state['experiences_chosen']
    else:
        experiences = st.session_state['experiences']
    if isinstance(experiences, list) and len(experiences) == 0:
        return None
    return experiences


def choose_contributions(project):
    """
    Selects contributions to export.

    If a contributions_choice is present in the session_state, this function \
    will return the corresponding contributions from the new_contributions \
    list stored in the session_state. Otherwise, it will return the \
    contributions originally stored in the session_state.

    Parameters:
    None

    Returns:
    string: The contributions to export.
    """
    choice_key = 'contributions_choice_'+project['uuid']
    choice_field = 'new_contributions_'+project['uuid']
    # use default contributions
    if not all(key in st.session_state for key in (choice_key,
                                                   choice_field)):
        return project['contributions']
    index = int(extract_version_number(st.session_state[choice_key]))-1
    if index == -1:
        return project['contributions']
    contributions = st.session_state[choice_field][index].strip(
    )
    if isinstance(contributions, list):
        return contributions
    contributions_new = extract_html_list(contributions)
    return contributions_new


def find_experience(experiences, exp_uuid):
    """
    Returns the experience dictionary from the given list of experiences \
    that has the specified UUID.

    Parameters:
    experiences (list): A list of experience dictionaries.
    exp_uuid (str): UUID of the experience to be searched.

    Returns:
    dict: a deep copy of the experience dictionary that has the specified UUID.

    """
    for exp in experiences:
        if exp['uuid'] == exp_uuid:
            return copy.deepcopy(exp)


def get_parsed_resume():
    """
    Returns a dictionary containing the parsed resume.

    Parameters:
    None

    Returns:
    dict: a dictionary containing the parsed resume.

    """
    parsed_resume = OrderedDict()
    fields = ['statement', 'skills', 'experiences']
    for field in fields:
        parsed_resume[field] = st.session_state[field]
    return parsed_resume


def count_words(paragraph: str) -> int:
    """
    Counts the number of words in a string.

    Args:
        paragraph (str): The string to be counted.

    Returns:
        int: The number of words in the string.
    """
    paragraph = paragraph.replace('/', ' ')
    return len(paragraph.split(' '))


def get_chosen_experiences(choices: list, options: dict) -> list:
    """
    Returns a list of experiences that have been selected by the user.

    Parameters:
    choices (list): A list of choices made by the user.
    options (dict): A dictionary containing the experiences of the user.

    Returns:
    list: a list of experiences that have been selected by the user.

    """
    experiences = OrderedDict()  # experiences are ordered
    for choice in choices:
        proj_uuid = options[choice]['proj_uuid']
        exp_uuid = options[choice]['exp_uuid']
        if exp_uuid not in experiences:
            exp = find_experience(st.session_state['experiences'], exp_uuid)
            exp['chosen_projects'] = [proj_uuid]
            experiences[exp_uuid] = exp
        else:
            experiences[exp_uuid]['chosen_projects'].append(proj_uuid)

    for key, exp in experiences.items():
        for project in exp['projects']:
            if project['uuid'] not in exp['chosen_projects']:
                exp['projects'].remove(project)
        experiences[key] = exp

    for key, exp in experiences.items():
        for project in exp['projects']:
            project['description'] = choose_project_description(project)
            project['contributions'] = choose_contributions(project)

    return list(experiences.values())
