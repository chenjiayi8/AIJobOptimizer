"""
This page initializes and creates a motivation letter using Streamlit \
framework.
"""

import uuid
import re
import streamlit as st
from st_dropfill_textarea import st_dropfill_textarea
from optimizer.core.initialisation import initialise, get_layout
from optimizer.core.resume import count_words
from optimizer.gpt.query import create_motivation, generate_motivations, \
    revise_motivation, revise_motivations
from optimizer.io.docx_file import write_letter
from optimizer.utils.download import download_button

st.set_page_config(
    page_title="Motivation letter",
    page_icon=":page_facing_up:",
    layout=get_layout(),
)

initialise()


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
    placeholder = """
    Use a template:
    1.Upload a template
    1.1. Drag and drop your motivation letter (docx, txt)
    1.2. Copy and paste your motivation letter
    2. Use the template
    2.1. Button Split: split the letter into different paragraphs
    2.2. Button Revise: revise the entire letter at once

    or

    Without a templrate:
    Button Generate: generate a motivation letter based on your expeirences
    """

    new_letter = st_dropfill_textarea(
        "Your motivation letter",
        st.session_state['letter'],
        height=300,
        placeholder=placeholder
    )
    if new_letter != st.session_state['letter']:
        st.session_state['letter'] = new_letter
        st.experimental_rerun()
    col_split, \
        col_words, \
        col_temp, \
        col_analyse, \
        col_generate = st.columns([
            0.75, 1, 1, 1, 1])
    with col_words:
        words = st.slider('Words', 200, 800, 500)

    with col_temp:
        temp = st.slider("Temperature", 0.1, 1.0, 0.8)

    with col_split:
        if st.button("Split", help="Split your motivation letter into \
                    individual paragraphs"):
            parse_letter()
            st.experimental_rerun()

    with col_analyse:
        if st.button(
                "Revise", help="Revise the entire motivation letter at once"):
            st.session_state['letter'] = revise_motivations(words, temp)
            parse_letter()
            st.experimental_rerun()

    with col_generate:
        if st.button(
            "Generate",
                help="Generate a motivation letter based on your expeirences"):
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

    col_words, col_temp, col_reset = st.columns([1, 1, 1])

    with col_words:
        motivation_words = st.slider("Words", 5, 300, 100)

    with col_temp:
        motivation_temp = st.slider("Temperature", 0.1, 1.0, 0.8)

    with col_reset:
        if st.button("Reset letter"):
            st.session_state['letter'] = ''
            st.session_state['motivations'] = []
            st.experimental_rerun()

    config = {}
    config['words'] = motivation_words
    config['temp'] = motivation_temp
    for index, motivation in enumerate(st.session_state['motivations']):
        col_content, col_revise = st.columns([6, 1])
        with col_content:
            motivation['content'] = st.text_area(
                f"motivation {index}",
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
                    st.experimental_rerun()
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
    if len(letter) > 10:
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
