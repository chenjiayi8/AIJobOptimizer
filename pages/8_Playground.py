"""
This module defines a playground to query gpt with question freely or \
based on selected background information
"""

import json
import streamlit as st
from optimizer.core.initialisation import initialise
from optimizer.gpt.api import MODEL, SYSTEM_ROLE, call_openai_api

st.set_page_config(
    page_title="Playground",
    page_icon=":skateboard:",
)

initialise()

COACH_ROLE = SYSTEM_ROLE
HR_ROLE = "You are a hiring manager. You are shortlisting candidates for a \
job"
ROLES = [
    {"name": "Career coach", "role": COACH_ROLE},
    {"name": "Hiring manger", "role": HR_ROLE},
]


def init_questions() -> None:
    """
    Defines system role and initializes the questions based on existing \
    background information.

    Parameters:
    None

    Returns:
    None

    The function first checks if there are any existing messages in the \
    session state. If there are none, it displays a message to the user and \
    creates a form to choose the role of the chatbot or input the role if it \
    is not already provided. Once the user confirms the role, the function \
    calls the init_background() function to initialize the background \
    information. If a role is selected from the list, the corresponding role \
    message is passed to the init_background() function.
    """

    if len(st.session_state['messages']) == 0:
        st.write("You can ask questions freely or based on selected \
                background information")
        with st.form("system_role", clear_on_submit=True):
            role = st.text_area(
                "Define system role", "",
                placeholder="""1. Write a message to define the role of chatgpt \n2. or leave it empty \n3. or choose a predefined role""")
            col_list = st.columns(len(ROLES)+1)
            with col_list[0]:
                if st.form_submit_button("Confirm"):
                    init_background(role)
                    st.experimental_rerun()
            for index, role in enumerate(ROLES):
                with col_list[index+1]:
                    label = role['name']
                    role_msg = role['role']
                    if st.form_submit_button(label):
                        init_background(role_msg)
                        st.experimental_rerun()


def get_system_msg(system_role: str) -> dict:
    """
    Takes a system_role parameter. It returns a list of a single dictionary \
    containing 4 key-value pairs: "select" with the value True, "type" with \
    the value "input", "role" with the value "system", and "content" with the \
    value of the system_role parameter. This dictionary represents a system \
    message that will be added to the message_history list. The purpose of \
    this message is to inform the user that the system role has been set to \
    the value of system_role.

    Parameters:
    system_role: str

    Returns:
    system_msg: Dict

    """
    system_msg = [
        {"select": True, "type": "input", "role": "system",
         "content": system_role},
    ]
    return system_msg


def get_job_description_msg() -> dict:
    """
    Returns a list containing a single dictionary object. The dictionary \
    object has four key-value pairs: "select" with a value of True, "type" \
    with a value of "info", "role" with a value of "user", and "content" with \
    a value that consists of the job description stored in the \
    st.session_state['txt_jd'] variable formatted into a string preceded by \
    the text "The job description is follows:". This function can be used to \
    create a message to inform the user about the job description in a \
    Streamlit app.


    Parameters:
    None

    Returns:
    jd_msg: dict


    """
    jd_msg = [
        {"select": True, "type": "info", "role": "user",
         "content":
         f"The job description is follows: \n{st.session_state['txt_jd']}"},
    ]
    return jd_msg


def choose_skills() -> list:
    """
    Selects skills as background information.

    If choosen_skills are present in the session_state, it will return them. \
    Otherwise, it will return the skills originally stored in the \
    session_state.

    Parameters:
    None

    Returns:
    A list of skills to select.
    """
    if 'choosen_skills' in st.session_state:
        if len(st.session_state['choosen_skills']) > 0:
            return st.session_state['choosen_skills']
    return st.session_state['skills']


def get_skills_msg() -> dict:
    """
    Returns a list containing a single dictionary object. The dictionary \
    object contains keys "select", "type", "role", and "content" with their \
    corresponding values. The purpose of this function is to generate a \
    message that informs the user of the current selected skills.
    """
    skills = choose_skills()
    skills_str = ', '.join(skills)
    skills_msg = [
        {"select": True, "type": "info", "role": "user",
            "content": f"I will give you my skills as follows: \n {skills_str}"
         },
    ]
    return skills_msg


def choose_experiences() -> dict:
    """
    Selects experiences as background information.

    If experiences_choosen are present in the session_state, it will return \
    them. Otherwise, it will return the experiences originally stored in the \
    session_state.

    Parameters:
    None

    Returns:
    A dict of the experiences to select.
    """
    if 'experiences_choosen' in st.session_state:
        return st.session_state['experiences_choosen']
    return st.session_state['experiences']


def get_experiences_msg():
    """
    Returns a list containing a single dictionary object. The dictionary \
    object contains keys "select", "type", "role", and "content" with their \
    corresponding values. The purpose of this function is to generate a \
    message that informs the user of the current selected experiences.
    """
    experiences = choose_experiences()
    experiences_str = json.dumps(experiences)
    experiences_msg = [
        {"select": True, "type": "info", "role": "user",
         "content":
         f"I will give you my experiences as follows: \n{experiences_str}"},
    ]
    return experiences_msg


def reset_messages() -> None:
    """
    Clears the value of st.session_state['messages'] and then it executes a \
    rerun of the Streamlit script by calling st.experimental_rerun(). This \
    function is likely used to clear any previous messages in the application \
    and allow it to display new ones.
    """
    st.session_state['messages'] = []
    st.experimental_rerun()


def init_background(system_role):
    """
    Takes in a parameter called system_role. The purpose of the function is \
    to initialize the st.session_state['messages'] list with messages related \
    to the job description and required skills and experiences. If the \
    system_role parameter has a length greater than 0, the function also gets \
    system messages related to that role and appends them to the messages list.

    Parameters:
    system_role: string

    Returns:
    None

    """
    st.session_state['messages'] = []
    if len(system_role) > 0:
        st.session_state['messages'] += get_system_msg(system_role)
    st.session_state['messages'] += get_job_description_msg()
    st.session_state['messages'] += get_skills_msg()
    st.session_state['messages'] += get_experiences_msg()


def handle_text_change(index: int) -> None:
    """
    Modify the value of the 'content' key in a dictionary at the given index \
    of the 'messages' list in the session_state object.

    Parameters:
        index (int): The index of the dictionary to modify in 'messages' list.

    Returns:
        None. The function modifies the 'content' key of a dictionary in-place.
    """

    msg = st.session_state['messages'][index]
    new_content = st.session_state[f"msg_{index}"]
    msg['content'] = new_content


def handle_check_change(index):
    """
    Toggle the bool value of the 'select' key in a dictionary at the given \
    index of the 'messages' list in the session_state object.

    Parameters:
        index (int): The index of the dictionary to modify in 'messages' list.

    Returns:
        None. The function modifies the 'select' key of a dictionary in-place.
    """
    msg = st.session_state['messages'][index]
    msg['select'] = not msg['select']


def parse_messages() -> None:
    """
    Iterates over the dictionaries inside the 'messages' list in the \
    st.session_state object. For each dictionary, it displays the message \
    type or role in the left column, the message content in a text area in \
    the middle column (with different formatting for the last message), and \
    a checkbox on the right column.
    """
    if len(st.session_state['messages']) > 0:
        for index, msg in enumerate(st.session_state['messages']):
            col_left, col_middle, col_right = st.columns([1, 7.5, 1])
            with col_left:
                if msg['type'] == 'info':
                    st.markdown("__Info__")
                else:
                    st.markdown(f"__{msg['role']}__")
            with col_middle:
                if index == len(st.session_state['messages']) - 1 and msg['type'] != 'info':
                    st.text_area(msg['role'], msg['content'],
                                 key=f"msg_{index}",
                                 height=100+round(len(msg['content'])*0.5),
                                 on_change=handle_text_change,
                                 args=(index,),
                                 label_visibility="hidden")
                else:
                    st.text_area(msg['role'], msg['content'],
                                 key=f"msg_{index}",
                                 on_change=handle_text_change,
                                 args=(index,),
                                 label_visibility="hidden")
            with col_right:
                st.write("# ")
                st.checkbox(
                    "Select", msg['select'], key=f"check_{index}",
                    on_change=handle_check_change,
                    args=(index, ),
                    label_visibility="hidden")


def precondition_msg(msg):
    """
    Iterate over the valid fields, and creates a new dictionary with only the \
    valid fields from the input msg dictionary, and returns it as output.
    """
    valid_fields = ['role', 'content']
    out = {}
    for field in valid_fields:
        out[field] = msg[field]
    return out


def query_gpt(temperature: float) -> None:
    """
    Takes a single argument temperature. The function initializes an empty \
    list called messages. It then iterates over a list called messages \
    stored in the session state of Streamlit. For each msg in messages, if \
    the value of msg['select'] evaluates to True, it passes msg to a \
    function called precondition_msg and appends the result to the messages \
    list. The function then calls another function called call_openai_api \
    with arguments 'MODEL', the messages list, and temperature. The returned \
    value is assigned to a variable called reply. The function then creates a \
    new dictionary called msg with keys 'select', 'type', 'role' and \
    'content' and the corresponding values True, 'reply', 'assistant' and \
    reply respectively. This new dictionary msg is then appended to the \
    messages list stored in the session state.

    Parameters:
    temperature (float): The sampling temperature to use when generating \
    responses.

    Returns:
    None

    """
    messages = []
    for msg in st.session_state['messages']:
        if msg['select']:
            messages.append(precondition_msg(msg))
    reply = call_openai_api(MODEL, messages, temperature=temperature)
    msg = {'select': True, 'type': 'reply', 'role':
           'assistant', 'content': reply}
    st.session_state['messages'].append(msg)


def append_input() -> None:
    """
    Updates the messages stored in the Streamlit's session state with a new \
    user message. Firstly, it checks whether there are already messages in \
    the session state. If there are, it creates a new form called \
    "new_message" with a text area where the user can type their message. \
    It also adds a slider called "Temperature" with a default range of 0.1 \
    and 1.0 to adjust how "creative" the AI's response is going to be.
    """
    if len(st.session_state['messages']) > 0:
        with st.form("new_message", clear_on_submit=True):
            new_msg = st.text_area("__Enter your message:__", "",
                                   placeholder="Send a message...")
            col_submit, \
                col_empty1, \
                col_temp, \
                col_empty2, \
                col_reset = st.columns([1, 0.5, 2, 0.5, 1])
            with col_submit:
                submitted = st.form_submit_button("Send")
            with col_empty1:
                st.write("")
            with col_temp:
                st.session_state['temperature_message'] = \
                    st.slider("Temperature", 0.1, 1.0,
                              st.session_state['temperature_message'])
                st.write("")
            with col_empty2:
                st.write("")
            with col_reset:
                if st.form_submit_button("Reset", help="Remove all messages"):
                    reset_messages()

        if submitted and len(new_msg) > 0:
            st.session_state['messages'] += [
                {"select": True, "type": "input",
                    "role": "user", "content": new_msg},
            ]
            query_gpt(st.session_state['temperature_message'])

            st.experimental_rerun()


def custom_questions():
    """
    Adds a section to the Streamlit app with customizable input questions.

    The function generates a playground section on the app with a header \
    that reads 'Playground'.  It then calls the 'init_questions', \
    'parse_messages' and 'append_input' functions to set up customizable \
    input questions and record user responses.

    Returns:
    None
    """
    st.markdown("<h2 style='text-align: center;'>Playground</h2>",
                unsafe_allow_html=True)
    init_questions()
    parse_messages()
    append_input()


custom_questions()
with st.expander("Debug: messages"):
    st.write("Messages", st.session_state['messages'])
