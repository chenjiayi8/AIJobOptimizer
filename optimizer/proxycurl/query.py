"""
This module consists of a set of functions to query proxycurl API to extract \
the job description from a LinkedIn job posting.

"""
from optimizer.proxycurl.api import call_proxycurl_api
from optimizer.utils.extract import exctract_linkedin_job_id
from optimizer.utils.parser import parse_linkedin_job_description


def scrap_job_description(url):
    """
    Scrapes the job description from a LinkedIn job posting.

    Args:
    url (str): The URL of the job posting.

    Returns:
    str: The job description.
    """
    job_id = exctract_linkedin_job_id(url)
    if job_id is None:
        return None
    page = call_proxycurl_api(job_id)
    scrapped_text = parse_linkedin_job_description(page)
    return scrapped_text
