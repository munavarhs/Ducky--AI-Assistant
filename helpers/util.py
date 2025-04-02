from typing import List, Dict, Union, Tuple

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import services.llm

async def run_conversation(messages: List[Dict[str, str]], message_placeholder: Union[DeltaGenerator, None] = None) \
        -> Tuple[List[Dict[str, str]], str]:
    full_response = ""

    # Filter out messages with 'evidence' role before sending to the LLM
    filtered_messages = [msg for msg in messages if msg.get("role") != "evidence"]
    
    chunks = services.llm.converse(filtered_messages)
    chunk = await anext(chunks, "END OF CHAT")
    while chunk != "END OF CHAT":
        print(f"Received chunk from LLM service: {chunk}")
        if chunk.startswith("EXCEPTION"):
            full_response = ":red[We are having trouble generating advice.  Please wait a minute and try again.]"
            break
        full_response = full_response + chunk

        if message_placeholder is not None:
            message_placeholder.code(full_response + "▌")

        chunk = await anext(chunks, "END OF CHAT")

    if message_placeholder is not None:
        message_placeholder.code(full_response)

    messages.append({"role": "assistant", "content": full_response})
    return messages, full_response


# Chat with the LLM, and update the messages list with the response.
# Handles the chat UI and partial responses along the way.
async def chat(messages, prompt):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add the user's prompt to the messages list
    messages.append({"role": "user", "content": prompt})

    message_placeholder = st.empty()
    spinner_placeholder = st.empty()

    with st.chat_message("assistant"):
        # Step 1: Display spinner while processing the response
        with spinner_placeholder:
            with st.spinner("Receiving response..."):
                messages, response = await run_conversation(messages, message_placeholder)

        message_placeholder.empty()  # Clear the streamed chunks
        spinner_placeholder.empty()  # Clear the spinner

        # Display the final response
        st.write(response)

        st.session_state.messages = messages
    return messages

async def ask_book(messages, prompt):
    # Display the user's prompt in the chat UI
    with st.chat_message("user"):
        st.markdown(prompt)

    # Create an empty placeholder for the spinner
    spinner_placeholder = st.empty()
    message_placeholder = st.empty()

    with st.chat_message("assistant"):
        # Show a loading spinner with message
        with spinner_placeholder:
            with st.spinner("Asking the Pragmatic Programmer book..."):
                # Call the RAG service to get answer and evidence
                rag_result = await services.rag.ask_book(prompt, return_image=True)
                
                # Extract values from rag_result
                answer = rag_result["answer"]
                context = rag_result["context"]
                page_number = rag_result["page_number"]
                image_data = rag_result["image_data"]
        
        # Clear the spinner placeholder
        spinner_placeholder.empty()
        
        # Display the answer
        st.write(f"{answer}")
        
        # Handle the image data
        if image_data:
            import base64
            # Convert bytes to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            # Create HTML img tag
            image_html = f'<img src="data:image/png;base64,{image_base64}" style="max-width: 100%;">'
        else:
            image_html = "No image available."
        
        # Create evidence section
        evidence_html = f"""
        <div style="color: gray; font-size: 10pt;">Page Number: {page_number}</div>
        {image_html}
        """
        
    # Update the chat history
    # Append the answer to messages
    messages.append({"role": "assistant", "content": answer})
    
    # Append the evidence to messages
    messages.append({
        "role": "evidence",
        "content": evidence_html,
        "page_number": page_number
    })
    
    # Update session state
    st.session_state.messages = messages
    
    # Return the messages list for chat history
    return messages
