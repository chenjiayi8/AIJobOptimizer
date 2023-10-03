"""This module provides a function for creating a copy button and textarea \
that copies the specified string to the clipboard on click.

The function `copy_button` takes two arguments: `str_to_copy` (a string to be \
copied to the clipboard) and `button_text` (the text to display on the copy \
button).

The function generates HTML and CSS code for a button and a hidden textarea, \
and uses JavaScript to copy the string to the clipboard when the button is \
clicked.

The returned value is a string containing the entire HTML code for the copy \
button and textarea.
"""

import uuid
import re


def copy_button(str_to_copy: str, label: str = "", tips: str = "") -> str:
    """
    Return an HTML string containing code for a copy button and hidden \
    textarea.

    The copy button copies the specified `str_to_copy` string to the \
    clipboard on click. The `button_text` argument specifies the text to \
    display on the copy button. The function generates HTML and CSS code for \
    a button and a hidden textarea, and uses JavaScript to copy the string to \
    the clipboard when the button is clicked.

    Args:
        str_to_copy (str): the string to be copied to the clipboard.
        button_text (str): the text to display on the copy button.

    Returns:
        str: a string containing the entire HTML code for the copy button and \
        textarea.
    """
    button_uuid = str(uuid.uuid4()).replace("-", "")
    button_id = re.sub(r"\d+", "", button_uuid)
    custom_css = f"""
        <style>
            #btn_{button_id} {{
                position: absolute;
                top: 50%;
                left: 50%;
                font-size: 12px;
                transform: translate(-50%, -50%);
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 8px 14px 8px 14px;
                margin-top: 5px;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;

            }}
            #btn_{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #btn_{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    if len(tips) > 0:
        button_str = f"""
                    <button title="{tips}" id="btn_{button_id}">{label}</button>
                    """
    else:
        button_str = f"""
            <button id="btn_{button_id}">{label}</button>
            """
    my_copy_button = f"""
        {custom_css}
        {button_str}
        <textarea id="textarea_{button_id}" style="display:none;">{str_to_copy}</textarea>
        <script>
            document.getElementById("btn_{button_id}").addEventListener("click", function() {{
            const el = document.getElementById("textarea_{button_id}");
            el.style.display = "block";
            el.select();
            document.execCommand('copy');
            el.style.display = "none";
        }});
        </script>
    """

    return my_copy_button
