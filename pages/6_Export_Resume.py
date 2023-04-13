"""
This module contains a function to export a resume to a docx file format
based on user-defined choices. The module imports libraries:
OrderedDict, copy, re, streamlit, and functions from the optimizer
package.
"""
from collections import OrderedDict
import copy
import re
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from optimizer.core.initialisation import initialise, reset
from optimizer.gpt.api import MODEL, SYSTEM_ROLE, call_openai_api
from optimizer.utils.extract import extract_code, extract_html_list
from optimizer.io.docx_file import to_docx, validate_template
from optimizer.utils.download import download_button

st.set_page_config(
    page_title="Export resume to docx",
    page_icon=":page_facing_up:",
)

template_fields = ['{statement}', '{competencies}', '{experiences}']

initialise()


@st.cache_data()
def query_company_and_role(txt_jd) -> str:
    """
    Function to query the company and role from a given job description \
    using OpenAI's API.

    Returns:
        - reply (str): A string containing the identified company and role \
        in the following syntax: {company}_{role}

    Caching:
        The function is cached using Streamlit's caching mechanism to reduce \
        API calls.
        The cached data is deleted when the inputs to the function change.
        The spinner is disabled to prevent unnecessary UI clutter.
    """
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": "Can you identify the role and the \
        company from the job description?"},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code>{company}_{role}</code>"},
    ]
    reply = call_openai_api(MODEL, messages, temperature=0.2)
    return reply


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
    Selects skills to export.

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


def get_company_role():
    """
    A function that uses the `query_company_and_role()` function to retrieve \
    the company and role information from the user input stored in the \
    session state under the key 'txt_jd'. It then extracts the code from \
    the retrieved information using the `extract_code()` function and returns \
    it as a string.

    Returns:
    - str: The extracted code from the retrieved company and role information.
    """
    reply = query_company_and_role(st.session_state['txt_jd'])
    company_role = extract_code(reply)
    return company_role


def write_docx(choices: list, options: dict):
    """
    Generates a Word document containing job seeker's CV given the configured \
    template.

    Args:
        choices (list): List containing the experience and projects that \
        are to be included in the CV.
        options (dict): Dictionary containing the experience and projects \
        along with their unique ids.

    Returns:
        str: Name of the output file if successfully generated, None otherwise.
    """

    st.session_state['company_role'] = get_company_role()
    statement = choose_statement()
    skills = choose_skills()
    skills_str = ' | '.join(skills)
    experiences = OrderedDict()  # experiences are ordered
    for choice in choices:
        proj_uuid = options[choice]['proj_uuid']
        exp_uuid = options[choice]['exp_uuid']
        if exp_uuid not in experiences:
            exp = find_experience(st.session_state['experiences'], exp_uuid)
            exp['choosen_projects'] = [proj_uuid]
            experiences[exp_uuid] = exp
        else:
            experiences[exp_uuid]['choosen_projects'].append(proj_uuid)

    for key, exp in experiences.items():
        for project in exp['projects']:
            if project['uuid'] not in exp['choosen_projects']:
                exp['projects'].remove(project)
        experiences[key] = exp

    for key, exp in experiences.items():
        for project in exp['projects']:
            project['description'] = choose_description(project)
            project['contributions'] = choose_contributions(project)

    if 'company_role' in st.session_state:
        company_role = st.session_state['company_role']
        company_role = re.sub(r'[^\w_. -]', '_', company_role)
        company_role = company_role.strip().replace(' ', '_')
        output_file_name = f"CV_{company_role}.docx"
    else:
        output_file_name = 'CV_exported.docx'

    st.session_state['experiences_choosen'] = experiences
    output_path = to_docx(st.session_state['template']['bytes_data'],
                          statement, skills_str, experiences)

    return (output_path, output_file_name)


def create_docx_template(uploaded_file: UploadedFile) -> None:
    """
    This function takes in a `uploaded_file` object which is a binary file \
    in docx format. It reads the bytes data from this file and creates a \
    `doc` object of `Document` class from it using a `BytesIO` class. It \
    then validates the template using `validate_template` function and if \
    it's valid, returns the `doc` object, otherwise returns None.

    Args:
    - uploaded_file: An object representing the uploaded docx file

    Returns:
    - doc: A `Document` object if the template is valid, otherwise None
    """

    bytes_data = uploaded_file.getvalue()
    missed_fields = validate_template(bytes_data, template_fields)
    if len(missed_fields) == 0:
        st.session_state['template'] = {}
        st.session_state['template']['name'] = uploaded_file.name
        st.session_state['template']['bytes_data'] = bytes_data
    else:
        for field in missed_fields:
            st.error(f"{field} is missing in your template")


def export_docx() -> None:
    """
    This function renders a Markdown heading with the title "Export resume".
    It creates a dictionary of project titles and corresponding project and \
    experience UUIDs, based on the experiences and projects stored in the \
    current session state.

    It then displays a multiselect drop-down widget populated with the \
    project options from the dictionary.
    When the user clicks the "Export to docx" button, the selected options \
    and their corresponding UUIDs are passed to the write_docx() function \
    to generate a docx file.

    """
    if len(st.session_state['experiences']) == 0:
        st.write("# Nothing to export")
        return
    st.markdown("<h2 style='text-align: center;'>Export resume</h2>",
                unsafe_allow_html=True)
    options = {}
    for i in range(len(st.session_state['experiences'])):
        exp = st.session_state['experiences'][i]
        for j in range(len(exp['projects'])):
            project_title = f"{exp['projects'][j]['title']}"
            options[project_title] = {}
            options[project_title]['proj_uuid'] = exp['projects'][j]['uuid']
            options[project_title]['exp_uuid'] = exp['uuid']
    choices = st.multiselect('Select relevant projects',
                             options.keys(), default=options)

    with st.form("my-form", clear_on_submit=True):
        uploaded_file = st.file_uploader(
            "Upload your temperature", type='docx')
        submitted = st.form_submit_button("UPLOAD!")
    if submitted and uploaded_file is not None:
        create_docx_template(uploaded_file)

    if 'template' in st.session_state:
        doc_bytes, doc_name = write_docx(choices, options)
        st.session_state['dl_link'] = download_button(
            doc_bytes, doc_name, 'Download')
        st.write(
            f"Current template: __{st.session_state['template']['name']}__")
        col_resume, col_download = st.columns([2, 1])

        with col_resume:
            st.write(f"Your resume: __{doc_name}__")
        with col_download:
            st.write(st.session_state['dl_link'], unsafe_allow_html=True)

    st.markdown("***")


export_docx()
reset()
with st.expander("Debug: Raw output"):
    st.write("session_state: ", st.session_state)
