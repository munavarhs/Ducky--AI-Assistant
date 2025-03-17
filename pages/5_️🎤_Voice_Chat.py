import streamlit as st

st.set_page_config(
    page_title="Voice Chat",
    page_icon="🎤",
    layout="wide"
)

import helpers.sidebar

helpers.sidebar.show()

st.header("Voice Chat")

st.write("Get instant answers to your software development and coding questions using the microphone.")

# The UI should have a big red record button stating we will record for 5 seconds.
# When clicked, let's show a spinner stating we are processing the audio.
# If we click the button, we should record for 5 seconds and then transcribe the audio to text,
# send it to chatGPT and then speak the text asynchronously - all using the audio.py module and methods inside this project


