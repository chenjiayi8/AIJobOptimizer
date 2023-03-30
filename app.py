"""
This Streamlit app allows the user to choose between different pages, \
and displays the content based on their selection. \
The "Introduction" page provides an overview of the module, \
while the "Test API" page runs tests on the module's application \
programming interface (API). The user selects their desired page \
from the sidebar dropdown menu.
"""

import streamlit as st
from optimizer.core.introduction import intro
from optimizer.tests.tests import testAPI


page_names_to_funcs = {
    "Introduction": intro,
    "Test API": testAPI,
}

demo_name = st.sidebar.selectbox("Choose a page", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
