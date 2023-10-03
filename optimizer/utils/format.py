"""
This module defines a function `custom_layout()` which applies custom CSS \
styles to the Streamlit app. The function takes no arguments and returns None.

The custom styles defined by this function include horizontal lines, select \
boxes, and text alignment for the Streamlit app. These styles are defined \
using CSS and applied using the `st.markdown()` and `st.write()` functions \
from the Streamlit library.

The `unsafe_allow_html=True` parameter is used to allow Streamlit to parse \
and render the CSS code as HTML, which is necessary to apply the custom styles.

"""
import streamlit as st


def custom_layout() -> None:
    """
    Applies custom CSS layout to the Streamlit app.

    This function defines custom CSS styles for horizontal lines, select boxes, and text alignment.
    """
    st.markdown(
        """
        <style>
        [data-testid="stMarkdownContainer"] hr{
            background-color: rgb(107 114 128);
            border: 0 none;
            color: rgb(107 114 128);
            height: 2px;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.write(
        """<style>
        [data-testid="stHorizontalBlock"] {
            align-items: center;
            vertical-align: middle;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .stSelectbox [data-testid='stMarkdownContainer'] {
            width: 100%;
        }
        .stSelectbox [data-testid='stMarkdownContainer'] p {
            text-align: center;
            font-size: 2em;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
