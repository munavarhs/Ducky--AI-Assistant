import streamlit as st
import helpers.sidebar
import asyncio
import os
from PIL import Image
from services.images import generate_image, get_all_images, delete_image

st.set_page_config(
    page_title="Images",
    page_icon="🏞️",
    layout="wide"
)

helpers.sidebar.show()

st.header("Image Generation")

# Create tabs for Image Generation and Image List
tab1, tab2 = st.tabs(["Image Generation", "Image List"])

# Image Generation Tab
with tab1:
    st.subheader("Generate a new image")
    
    # Text input for the prompt
    prompt = st.text_area(
        "Prompt", 
        placeholder="Enter a prompt for the image generation model",
        height=100
    )
    
    # Model parameters (optional - could be expanded)
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("Style", ["vivid", "natural"], index=0)
    with col2:
        quality = st.selectbox("Quality", ["standard", "hd"], index=1)
    
    col1, col2 = st.columns(2)
    with col1:
        size = st.selectbox(
            "Size", 
            ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"], 
            index=2
        )
    
    # Generate button
    if st.button("Generate Image"):
        if prompt:
            with st.spinner("Generating image..."):
                try:
                    # Call the generate_image function
                    result = asyncio.run(generate_image(
                        prompt=prompt,
                        style=style,
                        quality=quality,
                        size=size
                    ))
                    
                    # Display the generated image
                    st.success("Image generated successfully!")
                    st.image(result[1], caption=result[0], use_column_width=True)
                    
                    # Add a download button
                    with open(result[1], "rb") as file:
                        st.download_button(
                            label="Download Image",
                            data=file,
                            file_name=os.path.basename(result[1]),
                            mime="image/png"
                        )
                except Exception as e:
                    st.error(f"Error generating image: {str(e)}")
        else:
            st.warning("Please enter a prompt to generate an image.")

# Image List Tab
with tab2:
    st.subheader("Your Generated Images")
    
    # Add a refresh button
    if st.button("Refresh Image List"):
        st.rerun()
    
    # Get all images
    images_df = get_all_images()
    
    if images_df.empty:
        st.info("No images found. Generate some images in the 'Image Generation' tab.")
    else:
        # Format the date for display
        images_df['Formatted Date'] = images_df['Date Created'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Create a container for each image
        for index, row in images_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 1])
                
                # Display thumbnail in column 1
                with col1:
                    try:
                        st.image(row['Image'], width=150)
                    except Exception:
                        st.error("Could not load image")
                
                # Display description and date in column 2
                with col2:
                    st.markdown(f"**Description:** {row['Description']}")
                    st.markdown(f"**Created:** {row['Formatted Date']}")
                
                # Display action buttons in column 3
                with col3:
                    # View button - opens the image in a new tab/window
                    if st.button("View", key=f"view_{index}"):
                        try:
                            img = Image.open(row['Image'])
                            st.session_state[f"view_image_{index}"] = True
                        except Exception as e:
                            st.error(f"Error opening image: {str(e)}")
                    
                    # Delete button
                    if st.button("Delete", key=f"delete_{index}"):
                        try:
                            delete_image(row['Image'])
                            st.success("Image deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting image: {str(e)}")
                
                # Display the full-size image if view button was clicked
                if st.session_state.get(f"view_image_{index}", False):
                    with st.expander("Full Image", expanded=True):
                        st.image(row['Image'], use_column_width=True)
                        if st.button("Close", key=f"close_{index}"):
                            st.session_state[f"view_image_{index}"] = False
                            st.rerun()
                
                st.divider()
