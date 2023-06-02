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


def edit_statement() -> None:
    """
    This function generates a personal statement for the user and allows \
    them to choose between different versions of the generated statement.

    Returns:
    None
    """
    st.markdown("<h2 style='text-align: center;'>Personal statement</h2>",
                unsafe_allow_html=True)
    st.session_state['statement'] = st.text_area(
        'Personal statement', st.session_state['statement'], height=300)
    col_statement_words, col_statement_temp, col_statement = st.columns([
                                                                        1, 1, 1])
    with col_statement_words:
        statement_words = st.slider("Words", 10, 300, value=120)
    with col_statement_temp:
        statement_temp = st.slider("Temperature", 0.0, 1.0, 0.8)
    with col_statement:
        if st.button('Generate statement'):
            replies = generate_statements(
                statement_words,
                statement_temp
            )
            new_statements = parse_statements(replies)
            st.session_state['new_statements'] = new_statements
            st.session_state['btn_generate_statement'] = True

    if st.session_state['btn_generate_statement']:
        options = []
        option = f"Version 0: {count_words(st.session_state['statement'])} \
        words"
        options.append(option)
        st.write('### ' + option)
        st.write(st.session_state['statement'])
        for i in range(len(st.session_state['new_statements'])):
            new_statement = st.session_state['new_statements'][i]
            option = f"Version {i+1}: {count_words(new_statement)} words"
            options.append(option)
            st.write('### ' + option)
            st.write(new_statement)
        if 'statement_choice' in st.session_state:
            statement_choice_index = options.index(
                st.session_state['statement_choice'])
        else:
            statement_choice_index = 0

        st.session_state['statement_choice'] = st.selectbox(
            'Choose final statement', options, index=statement_choice_index)


initialise()
edit_statement()
