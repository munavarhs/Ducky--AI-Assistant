import os
import base64
import tempfile
import datetime

from dotenv import load_dotenv
from gtts import gTTS
from openai import OpenAI

from services import llm

# Load .env file
load_dotenv()

# Initialize the OpenAI client with the modern API pattern
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
)

def transcribe_audio(audio_data):
    """
    Transcribe the audio data using OpenAI's Whisper model.

    Args:
        audio_data (bytes): Raw audio data in WAV format

    Returns:
        str: The transcription of the audio file.
    """
    try:
        # Create a temporary file to store the audio data
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        # Transcribe the audio using OpenAI's Whisper model
        with open(temp_audio_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1"
            )
        
        # Clean up the temporary file
        os.unlink(temp_audio_path)
        
        # Return the transcription text
        return transcription.text
    
    except Exception as e:
        print(f"Error in transcribe_audio: {e}")
        return None

def generate_gpt_response(prompt, messages=None):
    """
    Send transcribed text to GPT-4 for a response.

    Args:
        prompt (str): The prompt or input text.
        messages (list, optional): The context messages for the GPT-4 API.

    Returns:
        str: The GPT-4 response.

    # AI Generation Prompt:
    # Write a Python function that takes a prompt and an optional list of context messages,
    # sends it to GPT-4 using the OpenAI API, and returns the generated response.
    """
    try:
        # Use the llm module's converse_sync function to get a response
        response, _ = llm.converse_sync(
            prompt=prompt,
            messages=messages,
            model=os.getenv('OPENAI_API_MODEL', 'gpt-4-turbo-preview')
        )
        
        return response
    
    except Exception as e:
        print(f"Error in generate_gpt_response: {e}")
        return None

def speak_text(text, lang="en"):
    """
    Convert text to speech using gTTS and return the audio as base64.

    Args:
        text (str): The text to be spoken.
        lang (str): Language for speech (default is "en" for English).
    
    Returns:
        str: Base64 encoded audio data that can be played in the browser
    """
    try:
        # Convert text to speech
        tts = gTTS(text=text, lang=lang)
        
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            tts.save(temp_audio.name)
            
            # Read the file and convert to base64
            with open(temp_audio.name, 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            # Clean up the temporary file
            os.unlink(temp_audio.name)
            
            return f"data:audio/mp3;base64,{base64_audio}"
    except Exception as e:
        print(f"Error in speak_text: {e}")
        return None
