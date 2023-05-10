"""
This page defines a playground to query gpt with question freely or \
based on selected background information
"""

import copy
import uuid
from st_dropfill_textarea import st_dropfill_textarea
import streamlit as st
import streamlit.components.v1 as components
from optimizer.core.initialisation import init_state
from optimizer.gpt.api import MODELS, SYSTEM_ROLE
from optimizer.gpt.query import get_experiences_msg, get_job_description_msg, \
    get_skills_msg, get_system_msg, query_gpt
from optimizer.utils.copy import copy_button

st.set_page_config(
    page_title="ChatGPT",
    page_icon=":skateboard:",
)

init_state("MODEL", MODELS[0])
init_state("messages_initalised", False)

COACH_ROLE = SYSTEM_ROLE
HR_ROLE = "You are a hiring manager. You are shortlisting candidates for a \
job"
TRANSLATOR_NL_EN = "You are a translator, who is an expert to translate Dutch \
    to English. You will translate all my messages to English."
TRANSLATOR_EN_CN = "You are a translator, who is an expert to translate \
English to Chinese. You will translate all my messages to Chinese."
TRANSLATOR_NL_CN = "You are a translator, who is an expert to translate Dutch \
to Chinese. You will translate all my messages to Chinese."
ROLES = [
    {"name": "Career coach", "role": COACH_ROLE},
    {"name": "Hiring manger", "role": HR_ROLE},
    {"name": "NL to CN", "role": TRANSLATOR_NL_CN},
    {"name": "NL to EN", "role": TRANSLATOR_NL_EN},
    {"name": "EN to CN", "role": TRANSLATOR_EN_CN},
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
    placeholder = ("1. Write a message to define the role of chatgpt \n"
                   "2. or leave it empty \n"
                   "3. or choose a predefined role")
    if not st.session_state['messages_initalised']:
        st.write("You can ask questions freely or based on selected \
                background information")
        with st.form("system_role", clear_on_submit=True):
            role = st.text_area("Define system role", "",
                                placeholder=placeholder
                                )
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


def reset_messages() -> None:
    """
    Clears the value of st.session_state['messages'] and then it executes a \
    rerun of the Streamlit script by calling st.experimental_rerun(). This \
    function is likely used to clear any previous messages in the application \
    and allow it to display new ones.
    """
    st.session_state['messages'] = []
    st.session_state['messages_initalised'] = False
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
    st.session_state['messages_initalised'] = True
    st.session_state['messages'] = []
    if len(system_role) > 0:
        st.session_state['messages'] += get_system_msg(system_role)
    jd_msg = get_job_description_msg()
    skills_msg = get_skills_msg()
    experiences_msg = get_experiences_msg()
    info_msgs = [jd_msg, skills_msg, experiences_msg]
    for msg in info_msgs:
        if msg is not None:
            st.session_state['messages'] += msg


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


def regenerate_response(index):
    """
    Regenerate the response of a message at the given index of the 'messages' \
    list in the session_state object.

    Parameters:
        index (int): The index of the dictionary to modify in 'messages' list.

    Returns:
        None. The function modifies the 'content' key of a dictionary in-place.
    """
    old_messages = copy.deepcopy(st.session_state['messages'])
    st.session_state['messages'].clear()
    for ind, msg in enumerate(old_messages):
        if ind <= index:
            st.session_state['messages'].append(msg)
        if ind > index and not msg['select']:
            st.session_state['messages'].append(msg)
    query_gpt(st.session_state['temperature_message'])


def parse_messages() -> None:
    """
    Iterates over the dictionaries inside the 'messages' list in the \
    st.session_state object. For each dictionary, it displays the message \
    type or role in the left column, the message content in a text area in \
    the middle column (with different formatting for the last message), and \
    a checkbox on the right column.
    """
    if st.session_state['messages_initalised']:
        for index, msg in enumerate(st.session_state['messages']):
            col_left, col_middle, col_right = st.columns([8, 1, 1])

            if msg['type'] == 'info':
                label = "Info: "

            else:
                label = msg['role'].capitalize() + ': '
            with col_left:
                if index == len(st.session_state['messages']) - 1 and msg['type'] != 'info':
                    height = 100+round(len(msg['content'])*0.3)
                else:
                    height = 200

                msg['content'] = st_dropfill_textarea(
                    label,
                    msg['content'],
                    key=msg['id'],
                    height=height,
                    layout="row",
                    labelWidth=70,
                )

            with col_middle:
                st.write("# ")
                st.checkbox(
                    "Select", msg['select'], key=f"check_{index}",
                    on_change=handle_check_change,
                    args=(index, ),
                    label_visibility="hidden")
            with col_right:
                if msg['select'] and msg['type'] == 'input':
                    if st.button(":new:", key=f"regen_{index}",
                                 help="Regenerate response"):
                        regenerate_response(index)
                        st.experimental_rerun()


def style_messages():
    """
    sets CSS styling for messages displayed in a Streamlit app.
    """
    # style message container with a border and padding
    st.write(
        """<style>
        [data-testid="stHorizontalBlock"] {
            align-items: center;
            vertical-align: middle;
            border: solid;
            border-width: thin;
            border-radius: 10px;
            border-color: rgb(49, 51, 63,0.2);
            padding: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # hide the textarea label
    st.markdown('''
        <style>
        div.stTextArea label{
            display: none
        }
        </style>
    ''', unsafe_allow_html=True)


def append_input() -> None:
    """
    Updates the messages stored in the Streamlit's session state with a new \
    user message. Firstly, it checks whether there are already messages in \
    the session state. If there are, it creates a new form called \
    "new_message" with a text area where the user can type their message. \
    It also adds a slider called "Temperature" with a default range of 0.1 \
    and 1.0 to adjust how "creative" the AI's response is going to be.
    """
    if st.session_state['messages_initalised']:
        with st.form("new_message", clear_on_submit=True):
            new_msg = st.text_area("__Enter your message:__", "",
                                   placeholder="Send a message...")
            col_submit, \
                col_empty1, \
                col_temp, \
                col_copy, \
                col_reset = st.columns([1, 0.5, 2, 1, 1])
            with col_submit:
                submitted = st.form_submit_button("Send")
            with col_empty1:
                st.write("")
            with col_temp:
                st.session_state['temperature_message'] = \
                    st.slider("Temperature", 0.1, 1.0,
                              st.session_state['temperature_message'])
                st.write("")
            with col_copy:
                my_copy_button = get_copy_button()
                components.html(my_copy_button, width=100, height=100)
            with col_reset:
                if st.form_submit_button("Reset", help="Remove all messages"):
                    reset_messages()

        if submitted and len(new_msg) > 0:
            st.session_state['messages'] += [
                {"id": str(uuid.uuid4()), "select": True, "type": "input",
                    "role": "user", "content": new_msg},
            ]
            query_gpt(st.session_state['temperature_message'])
            st.experimental_rerun()


def get_messages() -> str:
    """
    Retrieves messages from the st.session_state['messages'] list based on \
    their type being either "reply" or "input". These messages are then \
    joined into a string with "\\n\\n" separators and returned by the function.
    """
    messages = []
    for msg in st.session_state['messages']:
        if msg['type'] in ['reply', 'input']:
            messages.append(msg['content'])
    message_str = '\n\n'.join(messages)
    return message_str


def get_copy_button():
    """
    This function creates an expander widget in Streamlit, which allows the \
    user to copy messages to clipboard. The widget expands to display the \
    messages returned by get_messages() function which are in string format. \
    The messages are formatted in code-like font and hence can be easily \
    copied as they are.
    """
    messages_str = get_messages()
    my_copy_button = copy_button(
        messages_str+'\n\n', label='Copy',
        tips="Copy messages to the clipboard")
    return my_copy_button


def insert_messages():
    """
    Inserts the messages stored in the Streamlit's session state with a new \
    user/assistant message. Firstly, it checks whether there are already \
    messages in the session state. If there are, it creates a new form called \
    "insert_message" with a text area where the user can type their message \
    and a select box to choose whose belongs to the message. This function \
    tries to utilise in-context learning of the GPT model.
    """
    if st.session_state['messages_initalised']:
        with st.form("insert_message", clear_on_submit=True):
            message_types = {'user': 'input', 'assistant': 'reply'}
            new_msg = st.text_area("__Enter your message:__", "",
                                   placeholder="Append a message...")
            col_role, \
                col_insert, col_empty = st.columns([1, 1, 2])
            with col_role:
                role = st.selectbox("Role", message_types.keys(), index=0)
            with col_insert:
                insertted = st.form_submit_button("Insert")
            with col_empty:
                st.write("")

        if insertted and len(new_msg) > 0:
            st.session_state['messages'] += [
                {"select": True, "type": message_types[role],
                    "role": role, "content": new_msg},
            ]
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
    new_model = st.selectbox(
        "ChatGPT Model: ", MODELS, MODELS.index(st.session_state['MODEL']),
        help="Select a model to use for the chatbot, which is also used by \
        previous pages")
    if new_model != st.session_state['MODEL']:
        st.session_state['MODEL'] = new_model
        st.cache_data.clear()
        st.experimental_rerun()
    init_questions()
    style_messages()
    parse_messages()
    append_input()
    get_copy_button()


custom_questions()
with st.expander("Debug: messages"):
    st.write("Messages", st.session_state['messages'])

with st.expander("Advanced"):
    insert_messages()
