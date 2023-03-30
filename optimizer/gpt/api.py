"""
This module includes a decorator function that retries a function a specified number of times \
if a specified exception occurs and a function that sends a request to the OpenAI API to generate \
a completion for the specified model, messages, temperature and n.
"""

import time
from functools import wraps
import streamlit as st
from dotenv import dotenv_values
import requests


def retry(exception, tries=5, delay=1, backoff=2, max_delay=120):
    """
    Decorator function that retries the wrapped function a specified number of times \
      if a specified exception occurs.

    Args:
        exception (Exception): The exception to catch.
        tries (int, optional): The maximum number of times to retry the function. Defaults to 5.
        delay (int, optional): The initial delay in seconds between retries. Defaults to 1.
        backoff (int, optional): The factor by which to increase the delay each retry. \
            Defaults to 2.
        max_delay (int, optional): The maximum delay in seconds between retries. Defaults to 120.

    Returns:
        function: The wrapped function with retry logic.
    """

    def deco_retry(func):
        @wraps(func)
        def f_retry(*args, **kwargs):
            m_delay = delay
            num_tries = tries
            while tries > 1:
                try:
                    return func(*args, **kwargs)
                except exception as error:
                    with st.empty():
                        st.write(f"{error}, Retrying in {m_delay} seconds...")
                        time.sleep(m_delay)
                        st.write("")
                    num_tries -= 1
                    m_delay = min(m_delay * backoff, max_delay)
            # last attempt
            return func(*args, **kwargs)
        return f_retry
    return deco_retry


@retry(requests.exceptions.Timeout, tries=5, delay=1, backoff=2, max_delay=120)
def call_openai_api(model, messages, temperature=0.1, number_completion=1):
    """
    Function that sends a request to the OpenAI API to \
        generate a completion for the specified model, messages, temperature and n.

    Args:
        model (str): The ID of the model to use.
        messages (list): A list of past conversation messages.
        temperature (float, optional): \
            Controls the "creativity" of the generated completion. \
            A higher value means more creative,\
            a lower value means more predictable. Defaults to 0.1.
        n (int, optional): The number of completions to generate. Defaults to 1.

    Returns:
        list or str or None: A list of generated completions, \
            a single generated completion or None if no completion could be generated.
    """

    config = dotenv_values(".env")
    openai_api_key = config['OPENAI_API_KEY']
    url = r"https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {openai_api_key}",
               }
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "n": number_completion,
    }
    response = requests.post(url, headers=headers,
                             json=data, timeout=(60, 120))
    response.raise_for_status()
    choices = response.json()['choices']
    replies = [choice['message']['content'] for choice in choices]
    if len(replies) == 0:
        return None
    if len(replies) == 1:
        return replies[0]
    return replies
