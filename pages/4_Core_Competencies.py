"""
This page provides the functions for generating and sorting skills for a job description.

"""
import copy
import streamlit as st
from optimizer.core.initialisation import initialise, get_layout
from optimizer.gpt.query import generate_skills, sort_skills
from optimizer.utils.extract import extract_code


st.set_page_config(
    page_title="Core Competencies",
    page_icon=":toolbox:",
    layout=get_layout(),
)

initialise()


def parse_skills(reply):
    """
    Extracts a list of skills from a string of comma-separated skills.

        Args:
        - reply (str): A string containing comma-separated skills.

        Returns:
        - skills (list): A list of strings, each representing a parsed skill.
    """
    def capitalize(skill):
        return skill[0].capitalize() + skill[1:]
    skills_str = extract_code(reply)
    skills = skills_str.split(',')
    skills = [capitalize(skill.strip()) for skill in skills]
    return skills


def distribute_new_skills():
    """
    This function distributes new skills by adding them to the user's master \
    skills list (`skills`), sorted skills list (`sorted_skills`), and chosen \
    skills list (`choosen_skills`), for as long as they don't already exist \
    in those lists. It then removes the new skills from the `new_skills` \
    list, updates the `max_skills_number` value based on the length of the \
    `choosen_skills` list.

    Parameters:
    None

    Returns:
    None

    """
    skills = copy.deepcopy(st.session_state['new_skills_select'])
    for skill in skills:
        if skill not in st.session_state['skills']:
            st.session_state['skills'].append(skill)
        if skill not in st.session_state['sorted_skills']:
            st.session_state['sorted_skills'].append(skill)
        if skill not in st.session_state['choosen_skills']:
            st.session_state['choosen_skills'].append(skill)

    st.session_state['new_skills'] = []
    st.session_state['new_skills_select'] = []
    st.session_state['max_skills_number'] = len(
        st.session_state['choosen_skills'])


def on_skills_sorted():
    """
    This function retrieves the sorted list of skills from the session state \
    and saves a truncated version of it in the session state. The maximum \
    number of skills to save is determined by the value stored in the \
    'max_skills_number' variable of the session state.

    Parameters:
    None

    Returns:
    None

    Session State:
    - 'sorted_skills' (list): The sorted list of skills.
    - 'max_skills_number' (int): The maximum number of skills to save.
    - 'choosen_skills' (list): The truncated list of skills that is saved in the session state.
    """
    skills = st.session_state['sorted_skills']
    max_number = st.session_state['max_skills_number']
    st.session_state['choosen_skills'] = \
        skills[:max_number] if len(skills) > max_number else skills


def on_skills_number_changed():
    """
    Updates the list of chosen skills based on the maximum number of skills \
    allowed.

    If the maximum number of skills allowed is greater than the number of \
    chosen skills, the skill pool is used (i.e., all sorted skills). \
    Otherwise, the list of chosen skills is used. The updated list of chosen \
    skills is stored in session state.

    Args:
        None

    Returns:
        None
    """
    max_number = st.session_state['max_skills_number']
    if max_number > len(st.session_state['choosen_skills']):
        skills = st.session_state['sorted_skills']  # skill pool
    else:
        skills = st.session_state['choosen_skills']
    st.session_state['choosen_skills'] = \
        skills[:max_number] if len(skills) > max_number else skills


def trigger_skills_number_changed():
    """
    Updates the maximum number of skills to be displayed and sets the
    session state 'skills_number_changed' to True.

    Parameters:
    None

    Returns:
    None
    """
    st.session_state['max_skills_number'] = \
        st.session_state.max_skills_number_slider
    st.session_state['skills_number_changed'] = True


def on_skills_selected_changed(choosen_skills):
    """
    This function updates the session state 'choosen_skills' with the \
    selected skills.

    Parameters:
    choosen_skills (list): The list of selected skills.

    Returns:
    None
    """
    st.session_state['choosen_skills'] = choosen_skills


def on_new_skills_selected(new_skills_selected):
    """
    This function updates the session state 'new_skills_select' with the \
    selected skills.

    Parameters:
    new_skills_selected (list): The list of selected skills.

    Returns:
    None
    """
    st.session_state['new_skills_select'] = new_skills_selected


def edit_skills():
    """
    Method to render a skill-related section on a Streamlit app page. \
    Allows users to edit core competencies as a text area, set the number of \
    skills to generate, define the number of words in each skill, and set \
    the temperature value for skill generation. The user can sort and/or \
    generate skills based on these inputs, and the final output is displayed \
    on the page.

    Returns:
    None.

    """
    st.markdown("<h2 style='text-align: center;'>Skills</h2>",
                unsafe_allow_html=True)

    for skill in st.session_state['choosen_skills']:
        if skill not in st.session_state['skills']:
            st.session_state['skills'].append(skill)

    # limit the number of choosen skills
    if st.session_state['skills_number_changed']:
        on_skills_number_changed()
        st.session_state['skills_number_changed'] = False
        st.experimental_rerun()

    st.session_state['choosen_skills'] = st.multiselect(
        "Core Competencies:",
        options=st.session_state['skills'],
        default=st.session_state['choosen_skills'],
        key='choosen_skills_multiselect',
        on_change=on_skills_selected_changed,
        args=(st.session_state['choosen_skills'],)
    )
    if len(st.session_state['skills']) > 0:
        col_skills_generate_number, \
            col_skills_generate_temp, \
            col_skills_generate = st.columns([1, 1, 1])
        with col_skills_generate_number:
            create_skills_number = st.slider(
                "Number of keywords", 3, 10, value=5,
                key="create_skills_number")

        with col_skills_generate_temp:
            skills_temp = st.slider("Temperature", 0.0, 1.0,
                                    value=0.8, key="skills_temp")
        with col_skills_generate:
            if st.button(
                'Identify keywords',
                help="Identify ATS keywords skills \
                        from the job description and your experiences",
                    key="generate_skills"):
                reply = generate_skills(
                    create_skills_number, skills_temp)
                st.session_state['new_skills'] = parse_skills(reply)
                st.session_state['new_skills_select'] = \
                    st.session_state['new_skills']
                st.session_state['btn_generate_skills'] = True
                st.session_state['btn_sort_skills'] = False

    if st.session_state['btn_generate_skills'] and \
            len(st.session_state['new_skills']) > 0:
        st.session_state['new_skills_select'] = st.multiselect(
            "ATS keywords",
            st.session_state['new_skills'],
            default=st.session_state['new_skills_select'],
            key='new_skills_multiselect',
            on_change=on_new_skills_selected,
            args=(st.session_state['new_skills_select'],),
        )
        if st.button("Add selected keywords",
                     help="Click to add selected new skills",
                     key="add_new_skills"):
            distribute_new_skills()
            st.experimental_rerun()

    if len(st.session_state['skills']) > 0:
        col_max_skills, col_skills_sort = st.columns([2, 1])

        with col_max_skills:
            st.session_state['max_skills_number'] = st.slider(
                "Total number of skills", 0, len(st.session_state['skills']),
                value=st.session_state['max_skills_number'],
                key="max_skills_number_slider",
                on_change=trigger_skills_number_changed
            )

        with col_skills_sort:
            if st.button('Sort skills', help="Sort your skills based on their \
                            relevance to the job description", key="sort_skills"):
                st.session_state['btn_sort_skills'] = True
                with st.spinner("Sorting"):
                    reply = sort_skills(
                        st.session_state['txt_jd'],
                        st.session_state['skills'],
                        skills_temp,
                    )
                    st.session_state['sorted_skills'] = parse_skills(reply)
                    on_skills_sorted()
                    st.experimental_rerun()

    if len(st.session_state['choosen_skills']) > 0:
        st.write('#### Final Core Competencies:')
        st.write(f"{' | '.join(st.session_state['choosen_skills'])}")


edit_skills()
