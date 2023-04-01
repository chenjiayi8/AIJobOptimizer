
import streamlit as st
from collections import OrderedDict
from optimizer.utils.format import custom_layout

st.set_page_config(
    page_title="Experiences",
    page_icon=":male-office-worker:",
)


def edit_description(project):
    project['description'] = st.text_area(
        'Description',  project['description'], height=200)


def edit_contribtions(project):
    st.markdown("#### Key contributions:")
    for contribution in project['contributions']:
        st.markdown('- ' + contribution)


def edit_project(project):
    project['title'] = st.text_input("Project:", project['title'])
    edit_description(project)
    edit_contribtions(project)


def edit_experience(exp):
    st.markdown(
        f"<div style='display: flex; justify-content: space-between;'><div> <b>{exp['title']}</b> at {exp['company']}</div>    <div>({exp['date_range']})</div></div>", unsafe_allow_html=True)

    if len(exp['projects']) == 1:
        edit_project(exp['projects'][0])
    else:
        options = OrderedDict()
        for index, project in enumerate(exp['projects']):
            options[project['title']] = index
        project_title = st.sidebar.selectbox(
            "Project", options.keys())
        edit_project(exp['projects'][options[project_title]])


def edit_experiences() -> None:
    """
    Edit experiences function

    This function retrieves the list of experiences from the session state and allows the user to choose an experience to edit
    through a selectbox in the sidebar.

    Args:
        None

    Returns:
        None
    """
    experiences = st.session_state['experiences']
    if len(experiences) == 0:
        st.write("# No experiences to edit")
        return
    options = OrderedDict()
    for index, exp in enumerate(experiences):
        options[exp['title']] = index
    exp_title = st.sidebar.selectbox('Choose an experience', options.keys())
    edit_experience(experiences[options[exp_title]])


edit_experiences()
custom_layout()
