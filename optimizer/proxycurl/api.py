"""
This module provides functions to retrieve job information from LinkedIn \
using the proxycurl API.
"""
from dotenv import dotenv_values
import requests
import streamlit as st
from optimizer.utils.web import retry


@st.cache_data(show_spinner=False)
@retry(requests.exceptions.Timeout, tries=5, delay=1, backoff=2, max_delay=120)
def call_proxycurl_api(job_id: str) -> requests.Response:
    """Retrieve job information from LinkedIn using proxycurl API

    Args:
        job_id (str): LinkedIn job ID

    Returns:
        requests.Response: HTTP response object
    """
    config = dotenv_values(".env")
    proxycurl_api_key = config['PROXYCURL_API_KEY']
    api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/job'
    header_dic = {'Authorization': 'Bearer ' + proxycurl_api_key}
    params = {
        'url': f'https://www.linkedin.com/jobs/view/{job_id}/',
    }
    response = requests.get(api_endpoint,
                            params=params,
                            headers=header_dic,
                            timeout=(300, 600))

    return response
