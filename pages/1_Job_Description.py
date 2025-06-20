"""
This page contains functions to upload a job description and summarize it \
by calling the OpenAI GPT API.
"""
import streamlit as st
from optimizer.core.initialisation import initialise, get_layout
from optimizer.gpt.query import get_company_role, summary_job_description
from optimizer.proxycurl.query import scrap_job_description
from optimizer.utils.web import is_valid_url


st.set_page_config(
    page_title="Job Description", page_icon=":microscope:", layout=get_layout()
)

initialise()


def job_description():
    """
    Asks the user to copy and paste a job description, calls \
    the `summary_job_description` function to summarize it, \
    and displays the summary to the user.

    Returns:
    None
    """
    st.markdown(
        "<h2 style='text-align: center;'>Job Description</h2>",
        unsafe_allow_html=True,
    )
    st.session_state["txt_jd"] = st.text_area(
        "Job Description",
        st.session_state["txt_jd"],
        placeholder="Copy and Paste the job description",
        height=300,
    )
    if st.button("Summary"):
        with st.spinner("Summarying the job ..."):
            if is_valid_url(st.session_state["txt_jd"]):
                scrapped_text = scrap_job_description(
                    st.session_state["txt_jd"]
                )
                if scrapped_text is not None:
                    st.session_state["txt_jd"] = scrapped_text
                    st.rerun()
                else:
                    st.session_state["txt_jd"] = ""
                    st.error("The URL is not valid. Please try again.")
                    st.stop()

            job_analysed = summary_job_description(st.session_state["txt_jd"])

            if job_analysed is not None:
                st.session_state["job_analysed"] = job_analysed

            st.session_state["company_role"] = get_company_role(
                st.session_state["txt_jd"]
            )

    if st.session_state["company_role"] != "":
        new_company_role = st.text_input(
            "__Position:__",
            st.session_state["company_role"],
            key="input_company_role",
        )
        if new_company_role != st.session_state["company_role"]:
            st.session_state["company_role"] = new_company_role
            st.rerun()
    if st.session_state["job_analysed"] != "":
        st.markdown(f"__Summary:__\n {st.session_state['job_analysed']}")


job_description()
