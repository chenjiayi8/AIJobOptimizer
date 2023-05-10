"""
This module consists of a set of functions to query GPT API to extract \
information from a resume.

"""
import json
import re
import uuid
import streamlit as st
from optimizer.core.resume import choose_experiences, choose_job_description, choose_skills
from optimizer.gpt.api import SYSTEM_ROLE, call_openai_api
from optimizer.utils.extract import extract_by_quotation_mark, extract_code


SECRETARY_ROLE = """You are my secretary. I need you to identify and \
extract all the information of a resume. You have to do it very carefully."""


@st.cache_data()
def query_company_and_role(txt_jd) -> str:
    """
    Function to query the company and role from a given job description \
    using OpenAI's API.

    Returns:
        - reply (str): A string containing the identified company and role \
        in the following syntax: {company}_{role}

    Caching:
        The function is cached using Streamlit's caching mechanism to reduce \
        API calls.
        The cached data is deleted when the inputs to the function change.
        The spinner is disabled to prevent unnecessary UI clutter.
    """
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": "Can you identify the role and the \
        company from the job description?"},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code>{company}_{role}</code>"},
    ]
    reply = call_openai_api(messages, temperature=0.2)
    return reply


def get_company_role():
    """
    A function that uses the `query_company_and_role()` function to retrieve \
    the company and role information from the user input stored in the \
    session state under the key 'txt_jd'. It then extracts the code from \
    the retrieved information using the `extract_code()` function and returns \
    it as a string.

    Returns:
    - str: The extracted code from the retrieved company and role information.
    """
    reply = query_company_and_role(st.session_state['txt_jd'])
    company_role = extract_code(reply)
    return company_role


@st.cache_data
def query_project_title(project_info: str) -> str:
    """
    This function sends a list of messages to an OpenAI API for processing \
    and returns the extracted project name from the API response.

    Args:
    project_info (str): The information about the project that needs to \
    be queried.

    Returns:
    str: The extracted project name surrounded with code tags.
    """
    messages = [
        {"role": "system", "content": SECRETARY_ROLE},
        {"role": "user", "content": "The following is the resume"},
        {"role": "user", "content": st.session_state['txt_resume']},
        {"role": "user", "content": f"Can you find the project name with \
        this infomration: {project_info}?"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(messages, temperature=0.1)
    result_str = extract_code(reply)
    if result_str is None:
        result_str = extract_by_quotation_mark(reply)
    return result_str


@st.cache_data
def query_project_description(project: dict) -> str:
    """
    Returns the project description of a given `project_name`.

    Args:
    project_name (str): The name of the project to extract the description from.

    Returns:
    str: The extracted project description, surrounded by code tags.
    """
    messages = [
        {"role": "system", "content": SECRETARY_ROLE},
        {"role": "user", "content": "The following is the resume"},
        {"role": "user", "content": st.session_state['txt_resume']},
        {"role": "user", "content": "The following is one project of \
        the resume:"},
        {"role": "user", "content": f"Project name/title: {project['title']}"},
        {"role": "user", "content": "Can you find the project description \
        from the resume, located between the project name and key \
        contributions?"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(messages, temperature=0.1)
    result_str = extract_code(reply)
    return result_str


@st.cache_data
def query_project_contributions(project_name: str) -> list | None:
    """
    Takes in a project_name and generates a list of key contributions
    of the project using OpenAI's GPT model.

    Parameters:
    -----------
    project_name : str
        The name of the project whose contributions need to be extracted.

    Returns:
    --------
    contributions : list of str
        The list of key contributions of the project. Each string in the
        list has been stripped of non-alphanumeric characters and whitespaces.
    """
    messages = [
        {"role": "system", "content": SECRETARY_ROLE},
        {"role": "user", "content": "The following is my resume"},
        {"role": "user", "content": st.session_state['txt_resume']},
        {"role": "user", "content": f"Can you extract the key \
        contributions of Project:  {project_name}?"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(messages, temperature=0.1)
    result_str = extract_code(reply)

    # assemble contributions list, which contains strings that have \
    # been stripped of non-alphanumeric characters and whitespace.
    if result_str is not None:
        contributions = result_str.strip().split('\n')
        contributions = [re.sub(r'[^A-Za-z0-9 ]+', '', c)
                         for c in contributions]
    else:
        contributions = []
    return contributions


@st.cache_data(show_spinner=False)
def analyse_resume(txt_resume: str, temperature: float) -> str:
    """Extracts information from a resume using GPT.

    Args:
        txt_resume (str): The text of the resume to analyse.
        temperature (float): The sampling temperature to use when generating responses.

    Returns:
        A dictionary-like object that contains the extracted information from the resume.

    Raises:
        ValueError: If the `txt_resume` argument is an empty string or None.
        OpenAIAPIError: If the OpenAI API returns an error status code or message.
    """
    if txt_resume is None or len(txt_resume) == 0:
        raise ValueError("Invalid resume")
    temp_msgs = [
        {"role": "system", "content": "You are my secretary. I need you to \
        identify and extract all the information of a resume. You have to \
        do it very carefully."},
        {"role": "user", "content": "The following is the resume"},
        {"role": "user", "content": txt_resume},
        {"role": "user", "content": "Can you provide me with a valid JSON \
        string that contains all the complete information?"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(temp_msgs, temperature=temperature)
    reply_json_str = extract_code(reply)
    return reply_json_str


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
    reply = call_openai_api(messages, temperature=temperature)
    msg = {'id': str(uuid.uuid4()), 'select': True, 'type': 'reply', 'role':
           'assistant', 'content': reply}
    st.session_state['messages'].append(msg)


@st.cache_data(show_spinner=False)
def summary_job_description(txt_jd):
    """
    Call GPT API to summary the job


    Returns:
    A str representing the reply from GPT API
    """
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": "Please summary the job description."},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},

    ]
    reply = call_openai_api(messages, temperature=0.8)
    return extract_code(reply)


@st.cache_data(show_spinner=False)
def estimate_match_rate(txt_jd: str, txt_resume: str) -> str:
    """
    Estimate the match rate between a job description and a resume using OpenAI's GPT API.

    Parameters
    ----------
    txt_jd : str
        The text of the job description.
    txt_resume : str
        The text of the resume.

    Returns
    -------
    str
        The estimated match rate between the job description and the resume, as a string.

    """
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "user", "content":  "The job description is following:"},
        {"role": "user", "content":  txt_jd},
        {"role": "user", "content":  "My resume is following:"},
        {"role": "user", "content":  txt_resume},
        {"role": "user", "content": "Can you help me estimate the match \
        rate between my experiences and this job description?"},
    ]
    reply = call_openai_api(messages, temperature=0.5)
    return reply


def generate_statements(words: int = 120, temperature: float = 0.8) -> list:
    """
    Generates statements by calling OpenAI API using the provided session state parameters.

    Parameters:
        words (int): The number of words for the generated statement. \
        Default is 120.
        temperature (float): Controls the "creativity" of the generated \
        response, with higher temperatures generating more creative \
        responses. Default is 0.8.

    Returns:
        replies (list): A list of replies generated by the OpenAI API.
    """
    txt_jd = st.session_state['txt_jd']
    skills = st.session_state['skills']
    skills_str = ','.join(skills)
    statement = st.session_state['statement']
    experiences_str = json.dumps(st.session_state['experiences'])

    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "assistant",
            "content":  "Can you tell me about your skills and experiences?"},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills_str},
        {"role": "user", "content": "I will give you my experiences as \
        following:"},
        {"role": "user", "content": experiences_str},
        {"role": "user", "content": "I will give you my personal statement \
        as following:"},
        {"role": "user", "content": statement},
        {"role": "user", "content": f"Can you write a new personal \
        statement for me in {words} words, connecting my skills and \
        experiences with the job description?"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    replies = call_openai_api(messages, temperature=temperature,
                              number_completion=3)
    return replies


@st.cache_data(show_spinner=False)
def sort_skills(txt_jd: str, skills: str, temperature: float) -> str:
    """
    This function takes in two parameters the job description and the user's \
    skills. It then sends a series of messages to the OpenAI API to rank and \
    sort the user's skills based on their relevance to the job description.

    Parameters:
    - txt_jd (str): The job description.
    - skills (str): A string containing the user's skills.
    - temperature (float): Controls the randomness and creativity of output.

    Returns:
    - reply (str): A string containing the sorted user's skills based on \
    their relevance to the job description.
    """
    skills_str = ','.join(skills)
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills_str},
        {"role": "user", "content": "Please rank my skills in order of \
        relevance, based on the job description, starting with the most \
        in-demand skill to the least required."},
        {"role": "user", "content": "Please remove the duplicated skills"},
        {"role": "user", "content": "Please list the skills separated by \
        commas: skill1, skill2, skill3"},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    reply = call_openai_api(messages, temperature=temperature)
    return reply


def generate_skills(number: int, temperature: float = 0.2) -> str:
    """
    This function generates skills from the job description and user \
    experiences.

    Args:
        number (int): Number of skills to be extracted from the job \
        description.
        words (int): Maximum number of words allowed for each extracted skill.
        temperature (float): Controls the randomness and creativity of output.

    Returns:
        reply (str): Extracted skills separated by commas and enclosed in \
        '<code></code>'.
    """
    txt_jd = st.session_state['txt_jd']
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content": f"From the job description, can you \
        identify {number} specific keywords used by an ATS system?"},
        {"role": "user", "content": "Can you please list the keywords like \
        keyword1, keyword2, and keyword3 separately using commas instead of \
        'and' to join the last two keywords, and provide your response in a \
        single paragraph?"},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code>keyword1, keyword2, keyword3</code>"},
    ]
    reply = call_openai_api(messages, temperature=temperature)
    return reply


def generate_descriptions(project: dict, words: int, temperature: float) -> list:
    """
    This function generates descriptions based on the job requirements and \
    other inputs provided by the user. It takes in the following parameters:

    words (int): Number of words for the rephrased project description
    temperature (float): Controls the creativity of the generated descriptions

    The function first converts the experiences list to a json string. It \
    then creates a list of messages between the user and the AI assistant. \
    This list includes the job description, the user's skills and \
    experiences, and a request to rephrase the project description. The \
    messages are then passed to an OpenAI API using the specified model and \
    temperature parameters, and the generated replies are returned.

    The output should be surrounded by code tags using the "<code> Your \
    message here </code>" syntax.

    Returns:
    a list of strings representing replies from OpenAI API
    """
    txt_jd = st.session_state['txt_jd']
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user", "content":  f"Now I want to rewrite the project key \
        description for project: {project['title']}."},
        {"role": "user", "content":  f"The project description is: \
        {project['description']}."},
        {"role": "user", "content": f"Can you rephrase the project \
        description in {words} words, to align with the job description?"},
        {"role": "user", "content": "Please always surround the output with \
        code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    replies = call_openai_api(messages, temperature=temperature,
                              number_completion=3)
    return replies


def generate_contributions(project, words, number, temperature):
    """
    Given a project and job description, generates new key contributions \
    aligned with the job description using OpenAI's GPT API.

    Args:
    project (dict): The project for which new key contributions need to \
    be generated.
    words (int): The maximum number of words in each key contribution.
    number (int): The number of new key contributions to generate.
    temperature (float): Controls the creativity of the generated text. \
    A higher temperature value leads to more creative responses, but they \
    may not be as coherent.

    Returns:
    replies (list): A list of key contributions generated by the GPT \
    model, aligned with the job description.
    """
    txt_jd = st.session_state['txt_jd']
    contributions_str = '\n'.join(project['contributions'])
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "user",
            "content":  f"Now I want to rewrite my key contributions for \
            project: {project['title']}."},
        {"role": "user", "content":  f"The project description is: \
        {project['description']}."},
        {"role": "user", "content":  "These are my key contributions \
        for the project:"},
        {"role": "user", "content":  contributions_str},
        {"role": "user", "content": f"Can you analyse them and write \
        {number} new key contributions in {words} words, to align with the \
        job description?"},
        {"role": "user", "content": "Formatting the output as html in \
        unordered list; identifiying the keywords relevant with the job \
        description."},
        {"role": "user", "content": "Please always surround the keywords \
        with bold tags by using the following syntax:"},
        {"role": "user", "content": "<b> keywords </b>"},
        {"role": "user", "content": "Please always surround the output \
        with code tags by using the following syntax:"},
        {"role": "user", "content": "<code> Your message here </code>"},
    ]
    replies = call_openai_api(messages, temperature=temperature,
                              number_completion=3)
    return replies


def create_motivation(index: int, config: dict) -> str:
    """Generates a paragraph for a motivation letter using OpenAI's GPT \
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
    skills_str = ','.join(skills)
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
        {"role": "user", "content": skills_str},
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
    reply = call_openai_api(messages, temperature=temperature)
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
    skills = choose_skills()
    skills_str = ','.join(skills)
    experiences_str = json.dumps(choose_experiences())
    words = config['words']
    temperature = config['temp']
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "assistant", "content":  "Can you tell me about your skills \
        and experiences?"},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills_str},
        {"role": "user", "content": "I will give you my experiences as \
        following:"},
        {"role": "user", "content": experiences_str},
        {"role": "user", "content": "I will give you one paragraph of my \
        motivation letter as following:"},
        {"role": "user", "content": content},
        {"role": "user", "content": f"Please revise this paragraph \
        of my motivation letter in {words} words, ensuring that it \
        effectively highlights my relevant experiences and skills in the \
        context of the position I am applying for. Feel free to make any \
        necessary changes in terms of structure or tone to make it more \
        compelling."},

    ]
    reply = call_openai_api(messages, temperature=temperature)
    return reply


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
    skills = choose_skills()
    skills_str = ','.join(skills)
    experiences_str = json.dumps(choose_experiences())
    letter = st.session_state['letter']
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  txt_jd},
        {"role": "assistant",
            "content":  "Can you tell me about your skills and experiences?"},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills_str},
        {"role": "user", "content": "I will give you my experiences as \
        following:"},
        {"role": "user", "content": experiences_str},
        {"role": "user", "content": "I will give you my motivation letter as \
        following:"},
        {"role": "user", "content": letter},
        {"role": "user", "content": f"Compose a motivation letter in {words} \
        words that highlights my unique experiences and skills, demonstrating \
        how they make me an ideal candidate for the desired position. Be sure \
        to discuss any relevant educational background, work experiences, \
        accomplishments, and personal traits that contribute to my passion \
        for this field."},

    ]
    reply = call_openai_api(messages, temperature=temperature)
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
    job_description = choose_job_description()
    skills = choose_skills()
    skills_str = ','.join(skills)
    experiences_str = json.dumps(choose_experiences())
    messages = [
        {"role": "system", "content": SYSTEM_ROLE},
        {"role": "assistant", "content":  "The job description is following:"},
        {"role": "assistant", "content":  job_description},
        {"role": "assistant",
            "content":  "Can you tell me about your skills and experiences?"},
        {"role": "user", "content": "I will give you my skills as following:"},
        {"role": "user", "content": skills_str},
        {"role": "user", "content": "I will give you my experiences as \
        following:"},
        {"role": "user", "content": experiences_str},
        {"role": "user", "content": f"Please write a motivation letter \
        for me in {words} words, connecting my skills and \
        experiences with the job description."},
    ]
    reply = call_openai_api(messages, temperature=temperature)
    return reply


def get_system_msg(system_role: str) -> list:
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
        {"id": str(uuid.uuid4()), "select": True, "type": "system",
         "role": "system", "content": system_role},
    ]
    return system_msg


def get_job_description_msg() -> dict | None:
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
    None or jd_msg: dict


    """
    if len(st.session_state['txt_jd']) == 0:
        return None
    jd_msg = [
        {"id": str(uuid.uuid4()), "select": True, "type": "info",
         "role": "user", "content":
         f"The job description is follows: \n{st.session_state['txt_jd']}"},
    ]
    return jd_msg


def get_skills_msg() -> dict | None:
    """
    Returns a list containing a single dictionary object. The dictionary \
    object contains keys "select", "type", "role", and "content" with their \
    corresponding values. The purpose of this function is to generate a \
    message that informs the user of the current selected skills. If the list \
    is empty, return None
    """
    skills = choose_skills()
    if len(skills) == 0:
        return None
    skills_str = ', '.join(skills)
    skills_msg = [
        {"id": str(uuid.uuid4()), "select": True, "type": "info", "role": "user",
            "content": f"I will give you my skills as follows: \n {skills_str}"
         },
    ]
    return skills_msg


def get_experiences_msg() -> dict | None:
    """
    Returns a list containing a single dictionary object. The dictionary \
    object contains keys "select", "type", "role", and "content" with their \
    corresponding values. The purpose of this function is to generate a \
    message that informs the user of the current selected experiences.
    """
    experiences = choose_experiences()
    if experiences is None:
        return None
    experiences_str = json.dumps(experiences)
    experiences_msg = [
        {"id": str(uuid.uuid4()), "select": True, "type": "info", "role": "user",
         "content":
         f"I will give you my experiences as follows: \n{experiences_str}"},
    ]
    return experiences_msg
