"""
This page provides functions for generating and editing personal statement \
by calling OpenAI GPT API.
"""
import streamlit as st
from optimizer.core.initialisation import initialise, get_layout
from optimizer.core.resume import count_words, parse_statements
from optimizer.gpt.query import generate_statements

st.set_page_config(
    page_title="Personal Statement",
    page_icon=":open_book:",
    layout=get_layout(),
)


def format_statement_choice(index: int) -> str:
    """
    This function formats the statement choice for display.
        Args:
            index (int): The index of the statement choice.
        Returns:
            str: The formatted statement choice.
    """
    if index == 0:
        count = count_words(st.session_state['statement'])
    else:
        count = count_words(st.session_state['new_statements'][index - 1])
    return 'Version ' + str(index) + ': ' + str(count) + ' words'


def edit_statement() -> None:
    """
    This function generates a personal statement for the user and allows \
    them to choose between different versions of the generated statement.

    Returns:
    None
    """
    st.markdown("<h2 style='text-align: center;'>Personal statement</h2>",
                unsafe_allow_html=True)
    statement = st.text_area(
        'Personal statement', st.session_state['statement'], height=300)
    if statement != st.session_state['statement']:
        st.session_state['statement'] = statement
        st.experimental_rerun()
    col_statement_words, col_statement_temp, col_statement = st.columns([
                                                                        1, 1, 1])
    with col_statement_words:
        statement_words = st.slider("Words", 10, 300, value=120)
    with col_statement_temp:
        statement_temp = st.slider("Temperature", 0.0, 1.0, 0.8)
    with col_statement:
        if st.button('Generate statement'):
            st.session_state['btn_generate_statement'] = False
            # default choice
            st.session_state['statement_choice'] = 0
            replies = generate_statements(
                statement_words,
                statement_temp
            )
            new_statements = parse_statements(replies)
            st.session_state['new_statements'] = new_statements
            st.session_state['btn_generate_statement'] = True

    if st.session_state['btn_generate_statement']:
        options = []
        option = 0
        options.append(option)
        st.write('### ' + format_statement_choice(option))
        st.write(st.session_state['statement'])
        for i in range(len(st.session_state['new_statements'])):
            new_statement = st.session_state['new_statements'][i]
            options.append(i+1)
            st.write('### ' + format_statement_choice(i+1))
            st.write(new_statement)

        choice_index = options.index(
            st.session_state['statement_choice'])

        statement_choice = st.selectbox(
            'Choose final statement',
            options,
            format_func=format_statement_choice,
            index=choice_index)
        if statement_choice != st.session_state['statement_choice']:
            st.session_state['statement_choice'] = statement_choice
            st.experimental_rerun()


initialise()
edit_statement()
