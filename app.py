"""
This Streamlit app allows the user to choose between different pages, \
and displays the content based on their selection. \
The "Introduction" page provides an overview of the module, \
while the "Test API" page runs tests on the module's application \
programming interface (API). The user selects their desired page \
from the sidebar dropdown menu.
"""

import sys
import traceback
import streamlit as st
from optimizer.core.initialisation import initialise
from optimizer.core.introduction import intro
from optimizer.core.job import job_description
from optimizer.core.resume import upload_resume
from optimizer.tests.test_apis import test_api


def main():
    """
    Runs the main process of the application. The function initializes \
    and generates a dictionary containing the desired page names and \
    their respective functions. This dictionary is then used to create a \
    dropdown menu in the sidebar, allowing the user to select the desired \
    page to display. The selected function is then called to display \
    the chosen page.

    Returns:
    None
    """

    initialise()
    page_names_to_funcs = {
        "Introduction": intro,
        "Test API": test_api,
        "Job description": job_description,
        "Upload Resume": upload_resume,
    }

    demo_name = st.sidebar.selectbox(
        "Choose a page", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name]()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as error:
        trace_back_obj = sys.exc_info()
        st.write(traceback.format_exc())
