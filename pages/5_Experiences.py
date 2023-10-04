"""
This page provides the functions for editing experience and corresponding \
projects for a job description.
"""
from collections import OrderedDict
import streamlit as st
import streamlit.components.v1 as components
from optimizer.core.initialisation import init_state, initialise, get_layout
from optimizer.core.resume import count_words
from optimizer.gpt.query import generate_contributions, generate_descriptions
from optimizer.utils.extract import extract_code

st.set_page_config(
    page_title="Experiences",
    page_icon=":male-office-worker:",
    layout=get_layout(),
)

initialise()


def parse_descriptions(replies: list) -> list:
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
    if all([description is None for description in descriptions]):
        return replies
    return descriptions


def edit_description(project: dict) -> None:
    """
    Edit the description of a project using Streamlit widgets.

    Parameters
    ----------
    project : dict
        A dictionary representing the project to edit. It should contain a
        'uuid' key with a unique identifier, and a 'description' key with the
        current description value.

    Returns
    -------
    None

    Notes
    -----
    This function uses Streamlit to create an interactive interface with the
    following elements:

    - A text area to input the new description (with a default height of \
        200px).
    - Two sliders to control the length and the creativity of the generated
      descriptions.
    - A button to trigger the generation of new descriptions based on the
      input parameters.
    - A list of generated descriptions, each with a title ('Version 0' for
      the original description, 'Version 1' for the first generated
      description, and so on), and a selectbox to choose the final description.
    - The description choice is stored in \
      `st.session_state['description_choice_'+name]`.

    """
    name = project["uuid"]
    project["description"] = st.text_area(
        "Description", project["description"], height=200
    )

    col_description_words, col_description_temp, col_description = st.columns(
        [1, 1, 1]
    )
    with col_description_words:
        description_words = st.slider(
            "Words", 10, 100, value=60, key="description_words_" + name
        )

    with col_description_temp:
        description_temp = st.slider(
            "Temperature", 0.0, 1.0, 0.8, key="description_temp_" + name
        )

    with col_description:
        if st.button("Generate description", key="gene_description_" + name):
            replies = generate_descriptions(
                project, description_words, description_temp
            )
            new_descriptions = parse_descriptions(replies)
            st.session_state["generate_description_" + name] = True
            st.session_state["new_descriptions_" + name] = new_descriptions

    if st.session_state["generate_description_" + name]:
        options = []
        option = f"Version 0: {count_words(project['description'])} words"
        options.append(option)
        st.write("### " + option)
        st.write(project["description"])
        for j in range(len(st.session_state["new_descriptions_" + name])):
            new_descriptions = st.session_state["new_descriptions_" + name][j]
            option = f"Version {j+1}: {count_words(new_descriptions)} words"
            options.append(option)
            st.write("### " + option)
            st.write(new_descriptions)

        if "description_choice_" + name in st.session_state:
            description_choice_index = options.index(
                st.session_state["description_choice_" + name]
            )
        else:
            description_choice_index = 0

        description_choice = st.selectbox(
            "Choose final description",
            options,
            key="description" + name,
            index=description_choice_index,
        )
        st.session_state["description_choice_" + name] = description_choice


def parse_contributions(replies):
    """
    Parses a list of replies to extract contributions
    that contain code snippets.

    Args:
        replies (list): A list of strings representing replies.

    Returns:
        A list of strings representing contributions,
        where each contribution contains at least one code snippet.
    """
    contributions = []
    for reply in replies:
        contribution = extract_code(reply)
        contributions.append(contribution)
    return contributions


def edit_contribtions(project):
    """
    Function that takes in a project dictionary and outputs the
    list of key contributions in a markdown format.

    Args:
    project: a dictionary representing a project. It should have a \
    'contributions' key which is a list of strings representing the key \
    contributions of the project.

    Returns:
    None
    """
    name = project["uuid"]
    st.markdown("#### Key contributions:")
    for contribution in project["contributions"]:
        st.markdown("- " + contribution)
    (
        col_contributions_words,
        col_contributions_number,
        col_contributions_temp,
        col_contributions,
    ) = st.columns([1.5, 1.5, 1.5, 2])
    with col_contributions_words:
        contributions_words = st.slider(
            "Words of contributions",
            10,
            50,
            value=30,
            key="contributions_words_" + name,
        )
    with col_contributions_number:
        contributions_number = st.slider(
            "Number of contributions",
            2,
            8,
            value=4,
            key="contributions_number_" + name,
        )
    with col_contributions_temp:
        contributions_temperature = st.slider(
            "Temperature",
            0.1,
            1.0,
            value=0.8,
            key="contributions_temp_" + name,
        )
    with col_contributions:
        if st.button(
            "Generate contributions", key="gene_contributions_" + name
        ):
            responses = generate_contributions(
                project,
                contributions_words,
                contributions_number,
                contributions_temperature,
            )
            new_contributions = parse_contributions(responses)
            st.session_state["generate_contributions_" + name] = True
            st.session_state["new_contributions_" + name] = new_contributions
    if st.session_state["generate_contributions_" + name]:
        options = []
        words = 0
        for contribution in project["contributions"]:
            words += count_words(contribution)
        option = f"Version 0: {words} words"
        options.append(option)
        st.write("### " + option)
        for contribution in project["contributions"]:
            st.markdown("- " + contribution)
        for j in range(len(st.session_state["new_contributions_" + name])):
            new_contributions = st.session_state["new_contributions_" + name][
                j
            ]
            option = f"Version {j+1}: {count_words(new_contributions)} words"
            options.append(option)
            st.write("### " + option)
            components.html(new_contributions, scrolling=True)

        if "contributions_choice_" + name in st.session_state:
            contributions_choice_index = options.index(
                st.session_state["contributions_choice_" + name]
            )
        else:
            contributions_choice_index = 0

        contributions_choice = st.selectbox(
            "Choose final contributions",
            options,
            key="contributions" + name,
            index=contributions_choice_index,
        )
        st.session_state["contributions_choice_" + name] = contributions_choice


def init_project(project: dict) -> None:
    """
    Initializes the project with the given UUID by creating four states for it:
    - generate_description_<UUID>
    - generate_contributions_<UUID>
    - new_descriptions_<UUID>
    - new_contributions_<UUID>

    Parameters:
    project (dict): A dictionary containing the UUID of the project.
    """
    name = project["uuid"]
    init_state("generate_description_" + name)
    init_state("generate_contributions_" + name)
    init_state("new_descriptions_" + name)
    init_state("new_contributions_" + name)


def edit_project(project: dict) -> None:
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
    project["title"] = st.text_input("Project:", project["title"])
    edit_description(project)
    edit_contribtions(project)


def edit_experience(exp: dict) -> None:
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
        {exp ['date_range']})</div></div>",
        unsafe_allow_html=True,
    )

    if len(exp["projects"]) == 1:
        edit_project(exp["projects"][0])
    else:
        options = OrderedDict()
        for index, project in enumerate(exp["projects"]):
            options[project["title"]] = index
        project_title = st.sidebar.selectbox("Project", options.keys())
        edit_project(exp["projects"][options[project_title]])


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
    experiences = st.session_state["experiences"]
    if len(experiences) == 0:
        st.write("# No experiences to edit")
        return
    options = OrderedDict()
    for index, exp in enumerate(experiences):
        options[exp["title"]] = index
    exp_title = st.sidebar.selectbox("Choose an experience", options.keys())
    edit_experience(experiences[options[exp_title]])


edit_experiences()
