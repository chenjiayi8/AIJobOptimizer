"""
The "Introduction" page provides an overview of the module
"""

import streamlit as st
from optimizer.core.initialisation import initialise

st.set_page_config(
    page_title="AIJobOptimizer",
    page_icon="👋",
)


def intro():
    """
    This function generates the introduction section of the AIJobOptimizer web application.

    It creates a header, a success message sidebar and a markdown text \
    block, which describes the purpose of the app and encourages the \
    user to select a page from the sidebar menu to start using the features.

    Returns:
    None
    """

    st.write("# Welcome to AIJobOptimizer! 👋")

    st.markdown(
        """
        AIJobOptimizer: Revolutionize your job application process \
        with AI-driven resume and motivation letter enhancements, \
        designed to capture employers' attention and increase your \
        success in the job market.

        **👈 Select a page from the sidebar on the left**!
    """
    )


initialise()
intro()
