"""Web utilities."""
import time
from functools import wraps
import urllib.parse
import streamlit as st


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


def is_valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
