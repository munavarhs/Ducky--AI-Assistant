import os
from datetime import datetime
from typing import Literal, Tuple
from urllib.parse import urlparse

import httpx
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

__IMAGES_BASE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/images')


def get_all_images() -> pd.DataFrame:
    """
    Retrieves a DataFrame containing information about all images stored in a folder.

    Returns:
        pd.DataFrame: A DataFrame with columns 'Image', 'Description', and 'Date Created',
                      where 'Image' is the file path, 'Description' is the associated
                      description, and 'Date Created' is the creation timestamp.

    # AI Generation Prompt:
    # Write a Python function that reads all `.png` image files from a given folder, retrieves
    # their associated descriptions from a `.txt` file with the same name, and returns a pandas
    # DataFrame containing the image file paths, descriptions, and creation timestamps.
    """
    # Create an empty list to store image data
    image_data = []
    
    # Check if the images folder exists
    if not os.path.exists(__IMAGES_BASE_FOLDER):
        os.makedirs(__IMAGES_BASE_FOLDER, exist_ok=True)
        return pd.DataFrame(columns=['Image', 'Description', 'Date Created'])
    
    # Iterate through all files in the images folder
    for filename in os.listdir(__IMAGES_BASE_FOLDER):
        if filename.lower().endswith('.png'):
            image_path = os.path.join(__IMAGES_BASE_FOLDER, filename)
            
            # Get the creation timestamp
            creation_time = datetime.fromtimestamp(os.path.getctime(image_path))
            
            # Get the description from the corresponding .txt file
            description = ""
            txt_path = os.path.splitext(image_path)[0] + '.txt'
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as txt_file:
                    description = txt_file.read().strip()
            
            # Add the image data to the list
            image_data.append({
                'Image': image_path,
                'Description': description,
                'Date Created': creation_time
            })
    
    # Create a DataFrame from the image data
    return pd.DataFrame(image_data)


def delete_image(image_path: str):
    """
    Deletes an image file and its associated description file (if it exists).

    Args:
        image_path (str): The path to the image file to be deleted.

    # AI Generation Prompt:
    # Write a Python function that deletes a given image file and its corresponding `.txt`
    # description file, if the description file exists.
    """
    # Check if the image file exists
    if os.path.exists(image_path):
        # Delete the image file
        os.remove(image_path)
        
        # Check if a corresponding description file exists
        txt_path = os.path.splitext(image_path)[0] + '.txt'
        if os.path.exists(txt_path):
            # Delete the description file
            os.remove(txt_path)


async def generate_image(
    prompt: str,
    model: str = "dall-e-3",
    style: Literal["vivid", "natural"] = "vivid",
    quality: Literal["standard", "hd"] = "hd",
    timeout: int = 100,
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = "1024x1024"
) -> Tuple[str, str]:
    """
    Generates an image based on a given text prompt using the OpenAI DALL-E model
    and saves the image to a local folder.

    Args:
        prompt (str): The description or prompt for generating the image.
        model (str): The model version to use (default is "dall-e-3").
        style (Literal): The style of the image, e.g., "vivid" or "natural".
        quality (Literal): The quality setting, either "standard" or "hd".
        timeout (int): The maximum time (in seconds) to wait for the image to be generated.
        size (Literal): The size of the image, e.g., "1024x1024", "1792x1024", etc.

    Returns:
        Tuple[str, str]: A tuple containing the prompt and the file path of the saved image.

    # AI Generation Prompt:
    # Write a Python asynchronous function that generates an image from a text prompt using the
    # OpenAI DALL-E model, retrieves the image from the resulting URL, and saves it locally in
    # a predefined folder. The function should also save the prompt in a `.txt` file alongside
    # the image.
    """
    # Create the OpenAI client
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_API_BASE_URL')
    )
    
    # Ensure the images directory exists
    os.makedirs(__IMAGES_BASE_FOLDER, exist_ok=True)
    
    try:
        # Generate the image using the DALL-E model
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1
        )
        
        # Get the image URL from the response
        image_url = response.data[0].url
        
        # Download the image
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = response.content
        
        # Generate a unique filename based on the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        file_path = os.path.join(__IMAGES_BASE_FOLDER, filename)
        
        # Save the image to the file system
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Save the prompt to a text file with the same name
        txt_path = os.path.splitext(file_path)[0] + '.txt'
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        return prompt, file_path
    
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        raise


def _extract_filename_from_url(url: str) -> str:
    """
    Extracts the filename from a given URL.

    Args:
        url (str): The URL from which to extract the filename.

    Returns:
        str: The extracted filename.

    # AI Generation Prompt:
    # Write a Python function that takes a URL as input, extracts the file path, and returns
    # the filename from the URL.
    """
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Get the path component of the URL
    path = parsed_url.path
    
    # Extract the filename from the path
    filename = os.path.basename(path)
    
    # If the filename is empty, return a default name
    if not filename:
        return "image.png"
    
    return filename
