
import json
import streamlit as st
from collections import OrderedDict
from optimizer.core.initialisation import init_state, initialise
from optimizer.gpt.api import MODEL, SYSTEM_ROLE, call_openai_api
from optimizer.utils.extract import extract_code

st.set_page_config(
    page_title="Experiences",
    page_icon=":male-office-worker:",
)

initialise()


def generate_descriptions(words, temperature):
    """
    This function generates descriptions based on the job requirements and \
    other inputs provided by the user. It takes in the following parameters:

    words (int): Number of words for the rephrased project description
    temperature (float): Controls the creativity of the generated descriptions

    The function first converts the experiences list to a json string. It \
    then creates a list of messages between the user and the AI assistant. \
    This list includes the job description, the user's skills and \
    experiences, and a request to rephrase the project description. The \
    messages are then passed to an OpenAI API using the specified model and \
    temperature parameters, and the generated replies are returned.

    The output should be surrounded by code tags using the "<code> Your \
    message here </code>" syntax.
    """
    txt_jd = st.session_state['txt_jd']
    skills = st.session_state['skills']
    experiences_str = json.dumps(st.session_state['experiences'])
    description = st.session_state['description']
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "assistant",
            "content":  "Can you tell me about your skills and experiences?"},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills},
        {"role": "user", "content": "I will give you my experiences as \
        following:"},
        {"role": "user", "content": experiences_str},
        {"role": "user", "content": f"Can you rephrase the following project \
        description in {words} words, to align with the job description?"},
        {"role": "user", "content": description},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},

    ]
    replies = call_openai_api(MODEL, messages, temperature=temperature, n=3)
    return replies


def parse_descriptions(replies):
    """
    Extracts code descriptions from a list of reply messages.

    Args:
    - replies: a list of strings representing reply messages.

    Returns:
    - A list of strings containing the extracted code descriptions from \
    the reply messages.
    """
    descriptions = []
    for reply in replies:
        description = extract_code(reply)
        descriptions.append(description)
    return descriptions


def edit_description(project):
    name = project['uuid']
    project['description'] = st.text_area(
        'Description',  project['description'], height=200)

    col_description_words, \
        col_description_temp, \
        col_description = st.columns([1, 1, 1])
    with col_description_words:
        description_words = st.slider(
            "Words", 50, 100, value=60, key='description_words_'+name)

    with col_description_temp:
        description_temp = st.slider(
            "Temperature", 0.0, 1.0, 0.8, key='description_temp_'+name)

    with col_description:
        if st.button('Generate description', key='gene_description_'+name):
            replies = generate_descriptions(
                description_words,
                description_temp
            )
            new_descriptions = parse_descriptions(replies)
            st.session_state['generate_description_'+name] = True
            st.session_state['new_descriptions_' + name] = new_descriptions

    if st.session_state['generate_description_'+name]:
        options = []
        option = 'Version ' + str(0)
        options.append(option)
        st.write('### ' + option)
        st.write(project['description'])
        for j in range(len(st.session_state['new_descriptions_' + name])):
            option = 'Version ' + str(j+1)
            options.append(option)
            st.write('### ' + option)
            st.write(st.session_state['new_descriptions_' + name][j])
        description_choice = st.selectbox(
            'Choose final description', options, key='description'+name)
        st.session_state['description_choice_'+name] = description_choice


def edit_contribtions(project):
    st.markdown("#### Key contributions:")
    for contribution in project['contributions']:
        st.markdown('- ' + contribution)


def init_project(project):
    """
    Initializes the project with the given UUID by creating four states for it:
    - generate_description_<UUID>
    - generate_contributions_<UUID>
    - new_descriptions_<UUID>
    - new_contributions_<UUID>

    Parameters:
    project (dict): A dictionary containing the UUID of the project.
    """
    name = project['uuid']
    init_state('generate_description_'+name)
    init_state('generate_contributions_'+name)
    init_state('new_descriptions_' + name)
    init_state('new_contributions_' + name)


def edit_project(project):
    """
    Initializes a project and allows the user to edit its title, \
    description, and list of contributions.

    Args:
        project (dict): A dictionary with keys for 'title', 'description', \
        and 'contributions'.

    Returns:
        None. The function updates the project dictionary in place.
    """
    init_project(project)
    project['title'] = st.text_input("Project:", project['title'])
    edit_description(project)
    edit_contribtions(project)


def edit_experience(exp):
    """Display and edit work experience details for a given experience object.

    Parameters
    ----------
    exp : dict
        A dictionary containing the details of the work experience, with the
        following keys: 'title' (str), 'company' (str), 'date_range' (str),
        and 'projects' (list of dicts). The 'projects' key maps to a list of
        dictionaries, where each dictionary represents a project associated
        with the experience, and has the following keys: 'title' (str),
        'description' (str), and 'key contributions' (list of str).

    Outputs
    -------
    None
        The function displays the details of the experience (including each
        project associated with it) using Streamlit components, and allows
        the user to edit the details of each project.
    """
    st.markdown(
        f"<div style='display: flex; justify-content: space-between;'><div> \
        <b>{exp['title']}</b> at {exp['company']}</div>    <div>( \
        {exp ['date_range']})</div></div>", unsafe_allow_html=True)

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

    This function retrieves the list of experiences from the session state \
    and allows the user to choose an experience to edit
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
