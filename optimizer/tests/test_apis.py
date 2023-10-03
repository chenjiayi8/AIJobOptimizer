"""
This module defines tests for interacting with apis.
"""

import streamlit as st
from optimizer.gpt.api import call_openai_api


@st.cache_data(show_spinner=False)
def send_test_message():
    """
    Sends a test message to a OpenAI API model.

    Returns:
    A list or str or None representing the response from the API.
    """
    model = "gpt-3.5-turbo"
    test_messages = [
        {"role": "user", "content": "Tell me who you are."},
    ]
    return call_openai_api(model, test_messages)


def test_api():
    """
    This function sends a test message to the API and returns the reply.
    It also prints the conversation between the user and the GPT model \
    using streamlit.

    Returns:
    None
    """
    st.write("User: Tell me who you are.")
    with st.spinner("sending test message to API"):
        reply = send_test_message()
        st.write("GPT: " + reply)
