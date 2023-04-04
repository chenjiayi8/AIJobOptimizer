"""
This module initializes and creates a motivation letter using Streamlit \
framework.
"""

import json
import uuid
import re
import streamlit as st

from optimizer.core.initialisation import initialise
from optimizer.gpt.api import MODEL, SYSTEM_ROLE, call_openai_api
from optimizer.export.to_docx import write_letter
from optimizer.utils.download import download_button

st.set_page_config(
    page_title="Motivation letter",
    page_icon=":page_facing_up:",
)

initialise()


def create_motivation(index: int, config: dict) -> str:
    """Generates a paragraph for a motivation letter using OpenAI's GPT-3 \
    and model.

    Parameters:
    index (int): The index of the current motivation letter.
    config (dict): A dictionary containing the words and temperature to be \
    used in generating the paragraph.

    Returns:
    str: The generated paragraph.
    """
    words = config['words']
    temperature = config['temp']
    txt_jd = st.session_state['txt_jd']
    skills = st.session_state['skills']
    experiences_str = json.dumps(st.session_state['experiences'])
    previous_letter = ''
    for i in range(index):
        previous_letter += st.session_state['motivations'][i]['content'] + '\n'

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
        {"role": "user", "content": "I will give you my previous part of my \
        motivation letter as following:"},
        {"role": "user", "content": previous_letter},
        {"role": "user", "content": f"Please continue to write one paragraph \
        in {words} words, connecting my skills and experiences with \
        the job description."},
    ]
    reply = call_openai_api(MODEL, messages, temperature=temperature)
    return reply


def revise_motivation(content, config):
    """
    Generates a motivation letter by calling OpenAI API using the \
    provided session state parameters.

    Parameters:
        words (int): The number of words for the generated statement.
        temperature (float): Controls the "creativity" of the generated \
        response, with higher temperatures generating more creative \
        responses.

    Returns:
        reply

    """
    txt_jd = st.session_state['txt_jd']
    skills = st.session_state['skills']
    experiences_str = json.dumps(st.session_state['experiences'])
    # paragraph = st.session_state['motivations'][index]
    words = config['words']
    temperature = config['temp']
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "assistant", "content":  "Can you tell me about your skills \
        and experiences?"},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills},
        {"role": "user", "content": "I will give you my experiences as \
        following:"},
        {"role": "user", "content": experiences_str},
        {"role": "user", "content": "I will give you one paragraph of my \
        motivation letter as following:"},
        {"role": "user", "content": content},
        {"role": "user", "content": f"Please revise this paragraph \
        for me in {words} words, connecting my skills and \
        experiences with the job description."},

    ]
    reply = call_openai_api(MODEL, messages, temperature=temperature)
    return reply


def parse_letter():
    """
    Split the letter stored in the Session State into separate lines, \
    create a dictionary object for each line, assigning it a unique uuid, \
    and append it to a list of motivations stored in the Session State.
    """
    parts = st.session_state['letter'].split('\n')
    st.session_state['motivations'] = []
    for part in parts:
        if len(part) == 0:
            continue
        motivation = {}
        motivation['uuid'] = str(uuid.uuid4())
        motivation['content'] = part
        st.session_state['motivations'].append(motivation)


def revise_motivations(words: int, temperature: float) -> str:
    """
    Generates a motivation letter by calling OpenAI API using the \
    provided session state parameters.

    Parameters:
        words (int): The number of words for the generated statement.
        temperature (float): Controls the "creativity" of the generated \
        response, with higher temperatures generating more creative \
        responses.

    Returns:
        reply

    """
    txt_jd = st.session_state['txt_jd']
    skills = st.session_state['skills']
    experiences_str = json.dumps(st.session_state['experiences'])
    letter = st.session_state['letter']
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
        {"role": "user", "content": "I will give you my motivation letter as \
        following:"},
        {"role": "user", "content": letter},
        {"role": "user", "content": f"Please revise my motivation letter \
        for me in {words} words, connecting my skills and \
        experiences with the job description."},

    ]
    reply = call_openai_api(MODEL, messages, temperature=temperature)
    return reply


def generate_motivations(words: int, temperature: float) -> str:
    """
    Generates a motivation letter by calling OpenAI API using the \
    provided session state parameters.

    Parameters:
        words (int): The number of words for the generated statement.
        temperature (float): Controls the "creativity" of the generated \
        response, with higher temperatures generating more creative \
        responses.

    Returns:
        reply (str): A string of reply generated by the OpenAI API.
    """
    txt_jd = st.session_state['txt_jd']
    skills = st.session_state['skills']
    experiences_str = json.dumps(st.session_state['experiences'])
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
        {"role": "user", "content": f"Please write a motivation letter \
        for me in {words} words, connecting my skills and \
        experiences with the job description."},
    ]
    reply = call_openai_api(MODEL, messages, temperature=temperature)
    return reply


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


def create_letter():
    """
    Creates the Streamlit app interface for generating a motivation letter.

    The function creates a text area where the user can input or paste a \
    motivation letter as a template. Then, it creates four columns with \
    different components:
    - The first column contains an "Revise" button that could implement some \
    text analysis features.
    - The second column contains a slider for selecting the number of words \
    in the generated letter.
    - The third column contains a slider for selecting the temperature of \
    the generation process.
    - The fourth column contains a "Generate" button that triggers the \
    generation of a new motivation letter based on the template and the \
    selected number of words and temperature.

    The resulting generated letter is stored in the Streamlit session_state, \
    and it's displayed in the same text area as the template.

    Returns:
    None
    """
    st.session_state['letter'] = st.text_area(
        "Your motivation letter",
        st.session_state['letter'],
        height=300,
        placeholder="Copy and paste your motivation letter as a template"
    )
    col_analyse, col_words, col_temp, col_generate = st.columns([1, 1, 1, 1])
    with col_words:
        words = st.slider('Words', 300, 600, 500)

    with col_temp:
        temp = st.slider("Temperature", 0.1, 1.0, 0.8)

    with col_analyse:
        if st.button("Revise"):
            st.session_state['letter'] = revise_motivations(words, temp)
            parse_letter()
            st.experimental_rerun()

    with col_generate:
        if st.button("Generate"):
            st.session_state['letter'] = generate_motivations(words, temp)
            parse_letter()
            st.experimental_rerun()


def insert_motivation(index):
    """
    Inserts a new motivation dictionary in the given index of the \
    'motivations' list in the session state. The motivation dictionary has \
    two keys: 'uuid', with a string representation of a new Universally \
    Unique Identifier (UUID), and 'content', an empty string.

    Parameters
    ----------
    index : int
        The position in the 'motivations' list where the new motivation \
        dictionary should be inserted.

    Returns
    -------
    None
    """
    motivation = {}
    motivation['uuid'] = str(uuid.uuid4())
    motivation['content'] = ""
    st.session_state['motivations'].insert(index, motivation)


def delete_motivation(index: int) -> None:
    """
    Deletes a motivation from the session state's 'motivations' list at \
    the given index.

    Parameters:
    index (int): The index of the motivation to be deleted in the \
    'motivations' list.
    """
    del st.session_state['motivations'][index]


def edit_motivations() -> None:
    """
    Allows the user to edit a list of motivations in a Streamlit app. If \
    the list is empty, it creates a new letter. For each motivation, it \
    displays a text area where the user can input or edit the motivation's \
    content. It also shows several options for the user to interact with the \
    content, such as revising the motivation with an external API, inserting \
    or deleting motivations, generating a new motivation based on the \
    previous letter, and setting configuration parameters for the GPT model \
    to be used in revision or generation.
    """
    if len(st.session_state['motivations']) == 0:
        create_letter()
        return
    col_append, col_words, col_temp = st.columns([1, 1, 1])
    with col_append:
        if st.button("Add motivation"):
            motivation = {}
            motivation['uuid'] = str(uuid.uuid4())
            motivation['content'] = ""
            st.session_state['motivations'].append(motivation)

    with col_words:
        motivation_words = st.slider("Words", 5, 300, 100)

    with col_temp:
        motivation_temp = st.slider("Temperature", 0.1, 1.0, 0.8)

    config = {}
    config['words'] = motivation_words
    config['temp'] = motivation_temp
    for index, motivation in enumerate(st.session_state['motivations']):
        col_content, col_revise = st.columns([6, 1])
        with col_content:
            motivation['content'] = st.text_area(
                "",
                motivation['content'],
                height=200,
                key='content_'+motivation['uuid']
            )

        with col_revise:
            if len(motivation['content']) != 0:
                st.write(f"Words: {count_words(motivation['content'])}")
                if st.button(
                    "Revise",
                    key='revise_moti_'+motivation['uuid'],
                    help="Revise this paragraph with GPT API"
                ):
                    motivation['content'] = revise_motivation(
                        motivation['content'], config)
                if st.button(
                    "Insert",
                    key="insert_moti_"+motivation['uuid'],
                    help="Insert an empty paragraph before this one"
                ):
                    insert_motivation(index)
                    st.experimental_rerun()
                if st.button(
                    "Delete",
                    key="delete_moti_"+motivation['uuid'],
                    help="Remove this paragraph"
                ):
                    delete_motivation(index)
                    st.experimental_rerun()
            else:
                if st.button(
                    "Generate",
                    key='generate_moti_'+motivation['uuid'],
                    help="Generate a paragraph based on previous letter"
                ):
                    motivation['content'] = create_motivation(index, config)
                    st.experimental_rerun()
                if st.button(
                    "Delete",
                    key="delete_moti_"+motivation['uuid'],
                    help="Remove this paragraph"
                ):
                    delete_motivation(index)
                    st.experimental_rerun()


def export_motivations() -> None:
    """
    A function that exports motivations into an MS Word document,
    and provides a preview and download button for the user

    Args:
        None

    Returns:
        None
    """
    if 'company_role' in st.session_state:
        company_role = st.session_state['company_role']
        company_role = re.sub(r'[^\w_. -]', '_', company_role)
        company_role = company_role.replace(' ', '_')
        output_file_name = f"CL_{company_role}.docx"
    else:
        output_file_name = 'CL_exported.docx'

    paragraphs = [m['content'] for m in st.session_state['motivations']]
    letter = '\n\n'.join(paragraphs)
    bytes_data = write_letter(letter)
    dl_link = download_button(
        bytes_data, output_file_name, 'Download motivation letter')
    st.markdown(
        f"<h2 style='text-align: center;'>Preview: motivation letter \
        ({count_words(letter)} words)</h2>", unsafe_allow_html=True)

    st.write(letter)

    st.write(dl_link, unsafe_allow_html=True)


edit_motivations()
export_motivations()