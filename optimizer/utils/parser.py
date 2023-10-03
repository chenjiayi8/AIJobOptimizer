"""
This module contains functions to parse resume data in JSON format, \
and extract information like personal statement, skills and experiences \
for further use.
"""
from typing import Any
import copy
import datetime
import json
import uuid
from bs4 import BeautifulSoup
import requests
import streamlit as st
from optimizer.gpt.query import (
    analyse_resume,
    query_project_contributions,
    query_project_description,
    query_project_title,
)
from optimizer.utils.extract import extract_by_quotation_mark


def snake_case(arg: str, delimiter: str, upper_case: bool) -> str:
    """
    Convert a string to snake case based on the specified delimiter and case \
    style.

    Parameters:
    arg (str): The string to convert.
    delimiter (str): The delimiter to split the string into parts.
    upper_case (bool): Determines whether the resulting string should be in \
    uppercase or lowercase.

    Returns:
    str: The converted snake case string.

    """
    parts = arg.split(delimiter)
    if upper_case:
        parts = [part.upper() for part in parts]
    else:
        parts = [part.lower() for part in parts]
    return delimiter.join(parts)


def camel_case(arg: str, upper_case: bool) -> str:
    """Convert the given string to camel case format.

    Args:
        arg (str): The string which needs to be converted to camel \
        case.
        upper_case (bool): Whether to convert the first letter to \
        upper case.

    Returns:
        str: The camel case formatted string.
        """
    parts = arg.split("_")
    if len(parts) == 1:
        parts = arg.split(" ")
    if upper_case:
        return "".join(x.title() for x in parts)
    return parts[0].lower() + "".join(x.title() for x in parts[1:])


def search_field(obj: dict, candidates: list) -> Any:
    """
    Search for the first matching field in the given object, selected from a list of candidates.

    Parameters:
        obj (dict): The object to search for the field in.
        candidates (sequence): A sequence of candidate field names to search for.

    Returns:
        The value of the first matching field found in the object, or None if no such field exists.
    """
    new_list = []
    for candidate in candidates:
        # add the candidate itself to the list
        new_list.append(candidate)
        # example: Core_Competencies
        new_list.append(snake_case(candidate, "_", True))
        # example: core_competencies
        new_list.append(snake_case(candidate, "_", False))
        # example: Core Competencies
        new_list.append(snake_case(candidate, " ", True))
        # example: core competencies
        new_list.append(snake_case(candidate, " ", False))
        # example: CoreCompetencies
        new_list.append(camel_case(candidate, True))
        # example: coreCompetencies
        new_list.append(camel_case(candidate, False))
        # example: Duration
        new_list.append(candidate.capitalize())

    # remove duplicates
    new_list = list(set(new_list))
    candidate = (v for i, v in enumerate(new_list) if v in obj)
    key = next(candidate, None)
    if key is not None:
        return obj[key]
    return None


def get_statement(resume: dict) -> str | None:
    """
    A function that takes a resume as a dictionary and returns the personal statement if it exists.

    Args:
        resume (dict): The dictionary representing the resume to be searched.

    Returns:
        str | None: Returns the personal statement if it exists, otherwise returns None.
    """
    candidates = [
        "profile",
        "personal_statement",
        "personal_profile",
        "statement",
    ]
    statement = search_field(resume, candidates)
    if statement is not None:
        return statement
    return ""


def get_skills(resume: dict) -> list:
    """
    Searches the input `resume` dictionary for a list of skills. \
    The function searches for skills under different keys such as 'skills', \
    'Core Competencies', 'core_competencies', 'Competencies', and \
    'competencies'. If a skills list is found, it is returned. \
    If no skills are found, this function returns None.

    Parameters:
    -----------
    resume: dict
        The dictionary from which to extract skills.

    Returns:
    --------
    list | None:
        A list of skills if any are found. If no skills are found, None is returned.
    """
    candidates = [
        "skills",
        "Core Competencies",
        "core_competencies",
        "Competencies",
        "competencies",
    ]
    skills = search_field(resume, candidates)
    if skills is not None:
        if isinstance(skills, dict):
            skills = list(skills.values())
        if isinstance(skills, str):
            skills = parse_skills_string(skills)
        if len(skills) > 0:
            return [skill.strip() for skill in skills]
    return []


def reset_skills():
    """
    Reset the skills list based on the skills stored in the session state.

    If the 'skills' key in the session state is a list, then the function \
    will append each skill to the 'skills' list.
    If the 'skills' key in the session state is a dictionary, then the \
    function will append each value to the 'skills' list.

    The function will update the following session state keys:
    - 'skills': the updated skills list
    - 'sorted_skills': the sorted skills list
    - 'choosen_skills': the choosen skills list
    - 'max_skills_number': the length of the updated skills list
    """
    skills = get_skills(st.session_state["resume"])
    st.session_state["skills"] = skills
    st.session_state["sorted_skills"] = skills
    st.session_state["choosen_skills"] = skills
    st.session_state["max_skills_number"] = len(skills)


def get_experiences(resume: dict) -> list | None:
    """
    Search for experience-related fields in a resume and return them if found.

    Args:
        resume (dict): A dictionary containing fields in a resume.

    Returns:
        list | None: A list with experience-related fields if found, otherwise None.
    """

    candidates = [
        "experience",
        "experiences",
        "work_experiences",
        "work_experience",
        "professional_experience",
        "professional_experiences",
    ]
    experiences = search_field(resume, candidates)
    return experiences


def get_date_range(exp: dict) -> str:
    """
    Get a date range string in the format "MMM YYYY - MMM YYYY"
    from a dictionary of start and end dates.

    Parameters:
    exp (dict): A dictionary with keys 'start' and 'end' that each
                hold a dictionary with keys 'year' and 'month'.

    Returns:
    str_range (str): A string in the format "MMM YYYY - MMM YYYY".
    """
    date_start = datetime.datetime(
        year=int(exp["start"]["year"]), month=int(exp["start"]["month"]), day=1
    )
    month_start = date_start.strftime("%b")
    if "end" in exp:
        date_end = datetime.datetime(
            year=int(exp["end"]["year"]), month=int(exp["end"]["month"]), day=1
        )
        month_end = date_end.strftime("%b")
        str_range = f"{month_start} {exp['start']['year']} - \
                    {month_end} {exp['end']['year']}"
    else:
        str_range = f"{month_start} {exp['start']['year']} - Present"
    return str_range


def parse_project(exp_or_project_in: dict) -> dict:
    """
    Parses a project from a given dictionary.

    Parameters:
    exp_or_project_in (dict): A dictionary containing the project information.

    Returns:
    dict: A dictionary containing the parsed project with the following keys:
          'uuid': A randomly generated unique identifier.
          'title': The project's title.
          'description': The project's description.
          'contributions': The project's contributions.
    """
    project = {}
    project["uuid"] = str(uuid.uuid4())
    # locate project title; in some cases, GPT employs description instead
    project["title"] = search_field(
        exp_or_project_in, ["title", "project", "description"]
    )
    project["description"] = search_field(
        exp_or_project_in,
        ["project_description", "project description", "description"],
    )

    # Check if the value of key 'description' in 'project' is None or \
    # equal to the value of key 'title' in 'project', and if true, \
    # call the function 'query_project_description'
    if (
        project["description"] is None
        or project["description"] == project["title"]
    ):
        project["title"] = query_project_title(project["title"])
        project["description"] = query_project_description(project)
    project["description"] = (
        project["description"].replace(project["title"], "").strip()
    )
    project["description"] = (
        project["description"].replace("Project:", "").strip()
    )
    project["title"] = project["title"].replace("Project:", "").strip()
    project["title"] = (
        project["title"].replace("The project name is ", "").strip()
    )
    temp_title = extract_by_quotation_mark(project["title"])
    if temp_title is not None:
        project["title"] = temp_title
    project["contributions"] = search_field(
        exp_or_project_in, ["contributions", "key_contributions"]
    )
    if project["contributions"] is None:
        project["contributions"] = query_project_contributions(
            project["title"]
        )
    return project


@st.cache_data
def parse_experience(exp_in: dict) -> dict:
    """
    Given a dictionary `exp_in` containing information about a work experience,
    this function parses the dictionary and returns a new dictionary `exp_out`
    containing the following fields:

     - 'title': the job title
     - 'company': the name of the company or organization
     - 'date_range': the date range of the experience (if available),
     - 'projects': a list of projects associated with the experience, \
        where each project is represented as a dictionary with fields:
                - 'uuid': a unique identifier for the project
                - 'title': the title of the project
                - 'description': a description of the project
                - 'contributions': a list of contributions made to the project

    For each project in the input dictionary 'exp_in', the function \
    searches for the project title, description, and contributions. If \
    the values are missing, the function attempts to query for them using \
    various strategies.

    Arguments:
    exp_in -- a dictionary containing information about a work experience

    Returns:
    A dictionary containing the parsed information about the work experience
    """
    exp_out = {}
    exp_out["title"] = search_field(exp_in, ["title", "position", "job_title"])
    exp_out["company"] = search_field(
        exp_in, ["company", "organisation", "employer"]
    )
    if "start" in exp_in:
        exp_out["date_range"] = get_date_range(exp_in)
    else:
        exp_out["date_range"] = search_field(
            exp_in, ["dates", "date", "date_range", "duration"]
        )
    if exp_out["date_range"] is None:
        start_date = search_field(exp_in, ["start_date"])
        end_date = search_field(exp_in, ["end_date"])
        exp_out["date_range"] = start_date + " - " + end_date

    exp_out["projects"] = search_field(exp_in, ["projects"])
    if exp_out["projects"] is None:
        project = parse_project(copy.deepcopy(exp_in))
        exp_out["projects"] = [project]
    else:
        for i in range(len(exp_out["projects"])):
            project_old = copy.deepcopy(exp_out["projects"][i])
            exp_out["projects"][i] = parse_project(project_old)

    return exp_out


def parse_expereinces() -> None:
    """
    Parses the experiences and generates a unique UUID for each experience, \
    and returns a list of experiences as dictionaries.

    Each experience is parsed using the `parse_experience()` function,
    which should return a dictionary with keys 'title', 'company', \
    'description', and 'date_range'.

    The UUID is generated using the `uuid.uuid4()` function and added to
    each experience dictionary with key 'uuid'.

    The parsed experiences are stored in the `st.session_state` dictionary.

    Returns:
        None
    """
    experiences = []
    for exp in st.session_state["experiences"]:
        if "uuid" not in exp:
            experience = parse_experience(exp)
            experience["uuid"] = str(uuid.uuid4())
        else:
            experience = copy.deepcopy(exp)

        experiences.append(experience)
    st.session_state["experiences"] = experiences


# @st.cache_data
def parse_json(txt_resume: str) -> None:
    """
    Parse json str and assign components of resume

    Returns:
    None
    """
    st.session_state["resume"] = json.loads(txt_resume)
    st.session_state["statement"] = st.session_state["resume"]["statement"]
    reset_skills()
    st.session_state["experiences"] = st.session_state["resume"]["experiences"]


def parse_api_json(reply_json_str: str) -> None:
    """
    Parses and stores the API response JSON string in the session state.

    Args:
        reply_json_str (str): The JSON string returned by the API response.

    Returns:
        None
    """
    try:
        st.session_state["resume"] = json.loads(reply_json_str)
    except ValueError as error:
        st.write(f"{error}")
        st.error(f"Error to parse the reply from GPT:\n{reply_json_str}")

    st.session_state["statement"] = get_statement(st.session_state["resume"])
    skills = get_skills(st.session_state["resume"])
    st.session_state["skills"] = skills
    st.session_state["sorted_skills"] = skills
    st.session_state["choosen_skills"] = skills
    st.session_state["max_skills_number"] = len(skills)
    st.session_state["experiences"] = get_experiences(
        st.session_state["resume"]
    )


def parse_resume(txt_resume: str) -> None:
    """
    Caches the result of parsing the provided resume text using JSON \
    parsing or API analysis and JSON parsing.

    Args:
        txt_resume (str): The text of the resume to be parsed.

    Returns:
        None
    """
    try:
        parse_json(txt_resume)
    except ValueError:
        reply_json = analyse_resume(txt_resume, temperature=0.1)
        parse_api_json(reply_json)
    except Exception as error:
        print(f"Error: {str(error)}")
    finally:
        parse_expereinces()


def parse_linkedin_job_description(
    page: requests.models.Response,
) -> str | None:
    """
    Parses the job description from a LinkedIn job posting page.

    Args:
        page (requests.models.Response): The response object returned by \
            the `requests.get()` function.

    Returns:
        str: The job description in json str or None if there is an error.
    """
    soup = BeautifulSoup(page.content, "html.parser")
    if "Not enough credits" in soup.text:
        st.error("Not enough credits to parse the job description.")
        return None
    try:
        jd_obj = page.json()
    except json.decoder.JSONDecodeError:
        st.error("Error to parse the job description.")
        return None
    if "company" in jd_obj and "title" in jd_obj:
        company = jd_obj["company"]["name"]
        title = jd_obj["title"]
        st.session_state["company_role"] = company + "_" + title
    scrapped_text = json.dumps(jd_obj, indent=2)
    scrapped_text = scrapped_text.replace("\\n", "\n")
    return scrapped_text


def parse_skills_string(skill_str: str) -> list:
    """
    Parses a string containing a list of skills and returns a list of skills.

    Args:
        skill_str (str): A string containing a list of skills.

    Returns:
        list: A list of skills.
    """
    splitters = [";", ",", "|"]
    results = [skill_str.split(splitter) for splitter in splitters]
    counts = [len(result) for result in results]
    if max(counts) > 0:
        return results[counts.index(max(counts))]
    return []
