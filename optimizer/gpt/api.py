"""
This module includes a decorator function that retries a function a specified number of times \
if a specified exception occurs and a function that sends a request to the OpenAI API to generate \
a completion for the specified model, messages, temperature and n.
"""


import streamlit as st
from dotenv import dotenv_values
import requests

from optimizer.gpt.token import num_tokens_from_messages
from optimizer.utils.web import retry

MODELS = {"gpt-3.5-turbo": 4096,
          "gpt-3.5-turbo-16k": 16384,
          "gpt-4": 8192,
          "gpt-4-32k": 32768}

SYSTEM_ROLE = "You are my Career Coach. You will help me revise my resume for a target job."


def get_model_names():
    """
    Returns a list of the names of the available models.

    Returns:
        list: A list of the names of the available models.
    """
    return list(MODELS.keys())


def get_model_name_by_index(index):
    """
    Returns the name of the model at the specified index.

    Args:
        index (int): The index of the model.

    Returns:
        str: The name of the model at the specified index.
    """
    model_names = get_model_names()
    return model_names[index]


def get_default_mode():
    """
    Returns the name of the default model.

    Returns:
        str: The name of the default model.
    """
    return get_model_name_by_index(0)


def get_model_index_by_name(model_name):
    """
    Returns the index of the specified model.

    Args:
        model_name (str): The name of the model.

    Returns:
        int: The index of the specified model.
    """
    model_names = get_model_names()
    return model_names.index(model_name)


@retry(requests.exceptions.Timeout, tries=5, delay=1, backoff=2, max_delay=120)
def call_openai_api(messages, temperature=0.1, number_completion=1):
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
    model = st.session_state['MODEL']
    num_tokens = num_tokens_from_messages(messages, model)
    if num_tokens > MODELS[model]*0.9:
        st.write("### :red[Your input is too long!]")
        return None
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
                             json=data, timeout=(300, 600))
    response.raise_for_status()
    response_obj = response.json()
    for field in ['prompt_tokens',
                  'completion_tokens', 'total_tokens']:
        if field in response_obj['usage']:
            st.session_state[field] += response_obj['usage'][field]
    choices = response.json()['choices']
    replies = []
    for choice in choices:
        if choice['finish_reason'] == 'length':
            st.write("### :red[Your input is too long!]")
            return None
        replies.append(choice['message']['content'])

    if len(replies) == 0:
        return None
    if len(replies) == 1:
        return replies[0]
    return replies
