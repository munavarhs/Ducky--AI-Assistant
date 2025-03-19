import streamlit as st
import streamlit.components.v1 as components
import os
from datetime import datetime

st.set_page_config(
    page_title="Voice Chat",
    page_icon="🎤",
    layout="wide"
)

# Create audio directory if it doesn't exist
audio_dir = os.path.join('data', 'audio')
os.makedirs(audio_dir, exist_ok=True)

# Hide the file uploader but keep it functional
hide_streamlit_style = """
<style>
div[data-testid="stFileUploader"] {
    display: none;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# File uploader for audio blob
uploaded_file = st.file_uploader("Audio", type=['wav'], key='audio_upload', label_visibility="hidden")
if uploaded_file:
    # Generate timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}.wav"
    filepath = os.path.join(audio_dir, filename)
    
    # Save the file
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Store the filepath in session state for transcription
    st.session_state.audio_data = uploaded_file.getvalue()

import helpers.sidebar
helpers.sidebar.show()

st.header("Voice Chat")
st.write("Get instant answers to your software development and coding questions using the microphone.")

# Initialize session state
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

# HTML/JavaScript audio recorder component
recorder_html = """
<div style="text-align: center;">
    <button id="recordButton" style="
        background-color: #ff0000;
        color: white;
        font-size: 20px;
        padding: 20px 40px;
        border-radius: 50px;
        border: none;
        margin: 20px 0;
        width: 100%;
        cursor: pointer;">
        🎤 Click to Record
    </button>
    <div id="recordingStatus" style="margin: 10px 0;"></div>
    <audio id="audioPlayback" controls style="display: none; width: 100%; margin: 10px 0;"></audio>
</div>

<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
const recordButton = document.getElementById('recordButton');
const recordingStatus = document.getElementById('recordingStatus');
const audioPlayback = document.getElementById('audioPlayback');

async function setupRecorder() {
    try {
        // Check if mediaDevices is available
        if (!navigator.mediaDevices) {
            throw new Error("MediaDevices API not available in this browser or context");
        }
        
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            // Keep the audio player hidden
            // audioPlayback.style.display = 'block';
            recordButton.style.backgroundColor = '#ff0000';
            recordButton.textContent = '🎤 Click to Record';
            recordingStatus.textContent = 'Recording complete. Click play to review.';
            
            // Create a FormData object and append the audio blob
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            
            // Create a file input element
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.style.display = 'none';
            
            // Create a File object from the Blob
            const file = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });
            
            // Create a DataTransfer object and add the file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            // Trigger Streamlit's file uploader
            const uploadElement = window.parent.document.querySelector('input[type="file"]');
            uploadElement.files = fileInput.files;
            uploadElement.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Force a rerun to process the uploaded file
            window.parent.postMessage({
                type: 'streamlit:rerun'
            }, '*');
        };

        recordButton.disabled = false;
    } catch (error) {
        console.error('Error accessing microphone:', error);
        recordingStatus.textContent = 'Error accessing microphone: ' + error.message + '. Please ensure you have a microphone connected, have granted permission to use it, and are using a supported browser (Chrome/Firefox/Edge) with HTTPS.';
        recordButton.disabled = true;
        recordButton.style.backgroundColor = '#cccccc';
        recordButton.textContent = '🎤 Microphone Access Error';
    }
}

recordButton.addEventListener('click', () => {
    if (!mediaRecorder) {
        recordingStatus.textContent = 'Microphone access is not available. Please try using a different browser or check your microphone permissions.';
        return;
    }
    
    if (!isRecording) {
        // Start recording
        audioChunks = [];
        mediaRecorder.start();
        isRecording = true;
        recordButton.style.backgroundColor = '#4CAF50';
        recordButton.textContent = '⏺️ Recording... Click to Stop';
        recordingStatus.textContent = 'Recording in progress...';
        audioPlayback.style.display = 'none';
    } else {
        // Stop recording
        mediaRecorder.stop();
        isRecording = false;
    }
});

// Initialize the recorder
setupRecorder();
</script>
"""

from services.audio import transcribe_audio, generate_gpt_response, speak_text

# Create a container for the transcription and response
result_container = st.container()

# Display the HTML/JavaScript recorder
components.html(recorder_html, height=200)

# Add a text input fallback option
st.write("---")
st.write("### No microphone? Type your question instead:")
text_input = st.text_input("Your question", key="text_question")
text_submit = st.button("Submit Question")

# Process text input
if text_submit and text_input:
    with result_container:
        st.write("**Your Question:**")
        st.write(text_input)
        
        with st.spinner("Generating response..."):
            response = generate_gpt_response(text_input)
            if response:
                st.write("**Assistant's Response:**")
                st.write(response)
                
                # Get audio response
                audio_response = speak_text(response)
                if audio_response:
                    # Also show regular player for replay
                    st.audio(audio_response, format='audio/mp3', autoplay=True)
            else:
                st.error("Failed to generate response. Please try again.")

# Process any recorded audio
if st.session_state.audio_data:
    with result_container:
        with st.spinner("Transcribing audio..."):
            transcribed_text = transcribe_audio(st.session_state.audio_data)
            if transcribed_text:
                st.write("**Your Question:**")
                st.write(transcribed_text)
                
                with st.spinner("Generating response..."):
                    response = generate_gpt_response(transcribed_text)
                    if response:
                        st.write("**Assistant's Response:**")
                        st.write(response)
                        
                        # Get audio response
                        audio_response = speak_text(response)
                        if audio_response:
                            # Also show regular player for replay
                            st.audio(audio_response, format='audio/mp3', autoplay=True)
                    else:
                        st.error("Failed to generate response. Please try again.")
            else:
                st.error("Failed to transcribe audio. Please try again.")
    
    # Clear the audio data
    st.session_state.audio_data = None
