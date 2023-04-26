"""
This page contains a function to export a resume to a docx file format
based on user-defined choices.
"""
from collections import OrderedDict
import re
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from optimizer.core.initialisation import initialise, reset
from optimizer.core.resume import choose_contributions, \
    choose_project_description, choose_skills, choose_statement, \
    find_experience
from optimizer.gpt.query import get_company_role
from optimizer.io.docx_file import to_docx, validate_template
from optimizer.utils.download import download_button

st.set_page_config(
    page_title="Export resume to docx",
    page_icon=":page_facing_up:",
)

template_fields = ['{statement}', '{competencies}', '{experiences}']

initialise()


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
            project['description'] = choose_project_description(project)
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
        for missed_field in missed_fields:
            st.error(f"{missed_field} is missing in your template")


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

    if len(st.session_state['project_choices']) == 0:
        st.session_state['project_choices'] = \
            st.multiselect('Select relevant projects',
                           options.keys(), default=options)
    else:
        st.session_state['project_choices'] = \
            st.multiselect('Select relevant projects',
                           options.keys(),
                           default=st.session_state['project_choices'])

    with st.form("my-form", clear_on_submit=True):
        uploaded_file = st.file_uploader(
            "Upload your temperature", type='docx')
        submitted = st.form_submit_button("UPLOAD!")
    if submitted and uploaded_file is not None:
        create_docx_template(uploaded_file)

    if 'template' in st.session_state and \
            'project_choices' in st.session_state:
        template_name = st.session_state['template']['name']
        doc_bytes, doc_name = write_docx(
            st.session_state['project_choices'], options)
        st.session_state['dl_link'] = download_button(
            doc_bytes, doc_name, 'Download')
        st.write(
            f"Current template: __{template_name}__")
        col_resume, col_download = st.columns([2, 1])

        with col_resume:
            st.write(f"Your resume: __{doc_name}__")
        with col_download:
            st.write(st.session_state['dl_link'], unsafe_allow_html=True)

    st.markdown("***")


export_docx()
reset()
with st.expander("Debug: Raw output"):
    st.write("Usage: ")
    for field in st.session_state:
        if 'token' in field:
            st.write(field, ": ", st.session_state[field])
    st.write("session_state: ", st.session_state)
