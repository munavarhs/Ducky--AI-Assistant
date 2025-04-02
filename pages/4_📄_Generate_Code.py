import streamlit as st
from streamlit_ace import st_ace

import helpers.sidebar
import helpers.util
import services.extract
import services.llm
import services.prompts
from helpers import util
import random 

st.set_page_config(
    page_title="Generate Code",
    page_icon="📄",
    layout="wide"
)

# Add comments to explain the purpose of the code sections

# Show sidebar
helpers.sidebar.show()

st.markdown("""
# TODO

## Implement the following use cases

Using Streamlit, and any other Python components or libraries of your choice, implement the following use cases on the "generate code" page of the application.  It is assumed and required that the application uses an LLM to assist behind-the-scenes.

* Provide a feature to review code.  The use case is for a developer to provide some code, and to ask for a code review.


* Provide a feature to debug code.  The use case is for a developer to provide some code, along with an optional error string, and to ask for help debugging the code, assuming that the error string was associated with execution of the code.


* Provide a feature to modify or change the code using natural language conversationally.  The use case is for a developer to ask an LLM assistant to take some code, and some modification instructions.  The LLM assistant should provide modified code, and an explanation of the changes made.  Assuming the LLM is not perfect, the feature will allow the conversation to continue with more modification requests.

* Provide a feature to reset the page, to allow all existing code and history to be cleared; this effectively starts a new conversation about possibly new code.
""")

# Initialize session state variables
if "code" not in st.session_state:
    st.session_state.code = ""  # Stores the code entered by the user
if "conversation" not in st.session_state:
    st.session_state.conversation = []  # Stores conversation history
if "response" not in st.session_state:
    st.session_state.response = ""
if "history" not in st.session_state:
    st.session_state.history = []

if "editor_key" not in st.session_state:
    st.session_state.editor_key = "code_editor"

if "error_message" not in st.session_state:
    st.session_state.error_message = ""

if "modification_request" not in st.session_state:
    st.session_state.modification_request = ""

st.title("Generate Code with AI")

# Code Editor
st.subheader("Write or Paste Your Code")
# Load the session state value into the code editor
code = st_ace(
    value=st.session_state.code,
    language="python",
    theme="monokai",
    keybinding="vscode",
    font_size=14,
    tab_size=4,
    show_gutter=True,
    wrap=False,
    auto_update=True,
    key=st.session_state.editor_key
)

# Store the latest code input back into session state
st.session_state.code = code

# Feature: Code Review
if st.button("Review Code"):
    with st.spinner("Reviewing code..."):
        review = services.llm.call_llm(prompt=f"Review the following code:\n{st.session_state.code}")
        st.session_state.conversation.append(("Review", review))
        st.write(review)

# Feature: Debug Code
st.subheader("Debugging Assistance")
error_message = st.text_area("Paste an error message (optional)")
if st.button("Debug Code"):
    with st.spinner("Analyzing issue..."):
        debug_prompt = f"Debug the following code:\n{st.session_state.code}\nError: {error_message}"
        debug_response = services.llm.call_llm(prompt=debug_prompt)
        st.session_state.conversation.append(("Debug", debug_response))
        st.write(debug_response)

# Feature: Modify Code Conversationally
st.subheader("Modify Code")
modification_request = st.text_area("Describe modifications you want to make")
if st.button("Modify Code"):
    with st.spinner("Modifying code..."):
        modify_prompt = f"Modify the following code:\n{st.session_state.code}\nInstructions: {modification_request}"
        modified_code = services.llm.call_llm(prompt=modify_prompt)
        st.session_state.conversation.append(("Modify", modification_request, modified_code))
        st.session_state.code = modified_code
        st.write("### Modified Code:")
        st.code(modified_code, language="python")

# Feature: Reset Page
if st.button("Reset Page"):
    # Reinitialize essential variables
    st.session_state.code = ""
    st.session_state.error_message = ""
    st.session_state.response = ""
    st.session_state.history = []  # Ensure history is cleared
    st.session_state.conversation = []  # If conversation history exists
    st.session_state.modification_request = ""

    # Refresh the code editor to prevent caching issues
    st.session_state.editor_key = f"code_editor_{random.randint(0, 100000)}"

    # Rerun the script to reflect changes
    st.rerun()

# Display Conversation History
st.subheader("Conversation History")
for item in st.session_state.conversation:
    if item[0] == "Review":
        st.markdown(f"**Review:** {item[1]}")
    elif item[0] == "Debug":
        st.markdown(f"**Debugging Analysis:** {item[1]}")
    elif item[0] == "Modify":
        st.markdown(f"**Modification Request:** {item[1]}")
        st.code(item[2], language="python")

