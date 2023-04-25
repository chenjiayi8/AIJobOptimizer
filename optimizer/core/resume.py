"""
This module contains functions for parsing and selecting statements, skills, \
descriptions, experiences, and contributions to be exported for a project.

"""


import copy
import streamlit as st

from optimizer.utils.extract import extract_code, extract_html_list


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
    choice = st.session_state['statement_choice']
    index = int(choice.split(' ')[1]) - 1
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


def choose_description(project):
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
    index = int(st.session_state[choice_key].split(' ')[1])-1
    if index == -1:
        return project['description']
    return st.session_state[choice_field][index].strip()


def choose_experiences() -> dict | list | None:
    """
    Selects experiences as background information.

    If experiences_choosen are present in the session_state, it will return \
    them. Otherwise, it will return the experiences originally stored in the \
    session_state. Finally if the list of experiences is empty, return None

    Parameters:
    None

    Returns:
    None or A dict or list of the experiences to select.
    """

    if 'experiences_choosen' in st.session_state:
        experiences = st.session_state['experiences_choosen']
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
    index = int(st.session_state[choice_key].split(' ')[1])-1
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
