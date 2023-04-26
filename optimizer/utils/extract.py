"""
This module provides functions for extracting specific types of strings from \
input strings, using regular expressions.
"""

import re


def extract_by_quotation_mark(content):
    """
    Extracts the substring enclosed in the first pair of quotes (either single or double)
    found in the input string `content`, using regular expressions.

    Args:
        content (str): the input string.

    Returns:
        str or None: the substring enclosed in the first pair of quotes found in `content`,
        or None if `content` does not contain any quotes.

    """
    pattern1 = r'(?<=").+?(?=")'
    pattern2 = r"(?<=').+(?=')"
    if '"' in content:
        match = re.findall(pattern1, content,  flags=re.DOTALL)
    elif "'" in content:
        match = re.findall(pattern2, content,  flags=re.DOTALL)
    else:
        return None
    if len(match) > 0:
        return match[0]
    else:
        return None


def extract_code(content):
    """
    Extracts code snippets from a string that may contain one or more snippets
    written in Python, HTML, or enclosed in triple backticks or <code> tags.
    This function uses a list of regular expressions to match the patterns of
    these snippets, and returns the first match found in the content string.

    Args:
        content (str): A string that may include one or more code snippets.

    Returns:
        str: The first code snippet found in the content, without the
        surrounding code blocks or tags. If no code snippet is found, or if
        an error occurs during the matching process, None is returned.
    """

    pattern1 = r'(?<=```python).+?(?=```)'
    pattern2 = r'(?<=```html).+?(?=```)'
    pattern3 = r'(?<=```).+(?=```)'
    pattern4 = r'(?<=<code>).+?(?=</code>)'
    pattern5 = r"<code>(.*?)</code>"
    pattern6 = r"(?<=:).*"
    pattern7 = r'(?<=").+?(?=")'
    pattern8 = r"(?<=').+(?=')"
    patterns = [pattern1, pattern2, pattern3, pattern4,
                pattern5, pattern6, pattern7, pattern8]
    for pattern in patterns:
        match = re.findall(pattern, content,  flags=re.DOTALL)
        if len(match) > 0:
            # print(pattern)
            result = match[0]
            result = result.replace('<code>', '')
            result = result.replace('</code>', '')
            return result
    print("extract_code: ", "find no pattern", content)
    return None


def extract_html_list(content):
    """
    Extracts a list of strings from an HTML content string.

    Args:
    - content (str): A string of HTML content

    Returns:
    - A list of strings that matched a <li> tag pattern that appear in the HTML content,
    or None if no matches found.

    """
    pattern1 = r"<li>(.*?)</li>"
    patterns = [pattern1]
    for pattern in patterns:
        match = re.findall(pattern, content,  flags=re.DOTALL)
        if len(match) > 0:
            return match
    print("extract_html_list: ", "find no pattern", content)
    return None


def exctract_linkedin_job_id(url):
    """
    Extracts the LinkedIn job ID from a job posting URL.

    Args:
    - url (str): A string containing a LinkedIn job posting URL.

    Returns:
    - A string containing the LinkedIn job ID, or None if no match is found.
    """
    # regular expression to match jobs/view/1234567890
    pattern1 = r"(?<=jobs/view/)\d+"
    # regular expression to match currentJobId=1234567890&distance
    pattern2 = r"(?<=currentJobId=)\d+(?=&)"
    patterns = [pattern1, pattern2]
    for pattern in patterns:
        match = re.findall(pattern, url, flags=re.DOTALL)
        if len(match) > 0:
            return match[0]

    return None
