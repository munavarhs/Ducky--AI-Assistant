import csv
import os
import json
from typing import List, Tuple, Dict, Any
import tiktoken as tkn
from PyPDF2 import PdfReader
from openai import OpenAI
from sklearn.neighbors import NearestNeighbors
import numpy as np
import services.llm
from pdf2image import convert_from_path
from PIL import Image
import io

# Global configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI's best embeddings as of Feb 2024
CSV_FILE_PATH = "data/ThePragmaticProgrammer.embeddings.csv"

async def ask_book(query: str, return_image: bool = False):
    """
    Main RAG (Retrieval Augmented Generation) implementation.
    Takes a query about the book and returns relevant information with optional page image.
    
    Returns:
    {
        "answer": str,           # Generated response using context
        "page_number": int,      # Page where context was found
        "context": str,          # Text chunk used for answer
        "image_data": bytes      # Optional PNG of page if return_image=True
    }
    """
    # Keep the OpenAI client configuration
    client = OpenAI(
        base_url=os.getenv('OPENAI_API_BASE_URL'),
        api_key=os.getenv('OPENAI_API_KEY')
    )

    # Source PDF path
    pdf_path = "data/ThePragmaticProgrammer.pdf"
    
    # Step 1: Check if embeddings exist, otherwise create them
    embeddings_data = []
    if os.path.exists(CSV_FILE_PATH):
        print("Loading existing embeddings from CSV...")
        embeddings_data = load_embeddings_from_csv(CSV_FILE_PATH)
    else:
        print("Generating new embeddings...")
        # Extract text from PDF
        pages_text = __extract_text_from_pdf(pdf_path)
        
        # Chunk the text - using one chunk per page for simplicity
        chunked_pages = await __chunk_prompt(pages_text)
        
        # Extract page numbers and contexts
        page_numbers = [page_num for page_num, _ in chunked_pages]
        contexts = [text for _, text in chunked_pages]
        
        # Calculate embeddings
        embeddings = await __calculate_embeddings(client, contexts)
        
        # Save embeddings to CSV
        save_embeddings_to_csv(
            CSV_FILE_PATH, 
            "ThePragmaticProgrammer", 
            page_numbers, 
            embeddings, 
            contexts
        )
        
        # Format data for further processing
        embeddings_data = [
            {
                "document_name": "ThePragmaticProgrammer",
                "page_number": page_num,
                "embedding": emb,
                "context": ctx
            }
            for page_num, emb, ctx in zip(page_numbers, embeddings, contexts)
        ]
    
    # Step 2: Perform semantic search
    # Get embedding for the query
    query_embedding = await __calculate_embeddings(client, [query])
    query_embedding = query_embedding[0]  # Get the first (and only) embedding
    
    # Extract embeddings and metadata for nearest neighbors search
    embeddings_matrix = np.array([json.loads(data["embedding"]) if isinstance(data["embedding"], str) 
                                 else data["embedding"] for data in embeddings_data])
    
    # Set up nearest neighbors search
    nn = NearestNeighbors(n_neighbors=3, metric='cosine')
    nn.fit(embeddings_matrix)
    
    # Find most similar chunks
    distances, indices = nn.kneighbors([query_embedding], n_neighbors=3)
    
    # Get the most relevant context
    most_relevant_idx = indices[0][0]  # First result is most relevant
    most_relevant_page = embeddings_data[most_relevant_idx]["page_number"]
    most_relevant_context = embeddings_data[most_relevant_idx]["context"]
    
    # Get additional contexts for better context
    relevant_contexts = [embeddings_data[idx]["context"] for idx in indices[0][:3]]
    combined_context = "\n\n".join(relevant_contexts)
    
    # Step 3: Generate answer using LLM
    prompt = f"""
    You are an expert on The Pragmatic Programmer book. 
    Answer the following question based ONLY on the provided context from the book.
    If the context doesn't contain enough information to answer the question fully, 
    say so and answer with what you can from the context.
    
    CONTEXT:
    {combined_context}
    
    QUESTION:
    {query}
    
    ANSWER:
    """
    
    # Use the LLM service to get a response
    messages = [{"role": "user", "content": prompt}]
    response, _ = services.llm.converse_sync(prompt, None)
    
    # Step 4: Extract page image if requested
    image_data = None
    if return_image:
        image_data = __extract_page_as_image(pdf_path, most_relevant_page)
    
    # Return the complete result
    return {
        "answer": response,
        "page_number": most_relevant_page,
        "context": most_relevant_context,
        "image_data": image_data
    }

def __extract_text_from_pdf(pdf_path: str) -> List[Tuple[int, str]]:
    """
    Extract text content from each page of the PDF.
    Returns: List of (page_number, page_text) tuples
    """
    result = []
    
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        pdf = PdfReader(file)
        
        # Extract text from each page
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            
            # Add to result if text exists (skip empty pages)
            if text.strip():
                # Page numbers in PDFs typically start at 0, but we want to start at 1
                result.append((i + 1, text))
    
    return result

def __extract_page_as_image(pdf_path: str, page_number: int) -> bytes:
    """
    Convert a specific PDF page to a PNG image.
    Returns: Raw PNG image data as bytes
    """
    # Convert PDF page to image (page_number is 1-indexed, but convert_from_path is 0-indexed)
    images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)
    
    if not images:
        return None
    
    # Get the first (and only) image
    image = images[0]
    
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

async def __chunk_prompt(pages_text: List[Tuple[int, str]], chunk_size: int = 1500, overlap: int = 50) -> List[Tuple[int, str]]:
    """
    Split text into chunks suitable for embedding.
    
    For simplicity, we'll use one chunk per page as suggested in the hint.
    This makes it easier to track context and display relevant pages.
    
    Args:
        pages_text: List of (page_number, text) tuples
        chunk_size: Target size for each chunk in tokens (not used in this implementation)
        overlap: Number of tokens to overlap between chunks (not used in this implementation)
    
    Returns: List of (page_number, chunk_text) tuples
    """
    # For simplicity, we'll use one chunk per page
    return pages_text

async def __calculate_embeddings(client: OpenAI, documents: List[str], batch_size: int = 20) -> List[List[float]]:
    """
    Get embeddings for text chunks using OpenAI's API.
    
    Args:
        client: OpenAI client instance
        documents: List of text chunks to embed
        batch_size: Number of chunks to process at once
    
    Returns: List of embedding vectors (each vector is List[float])
    """
    all_embeddings = []
    
    # Process documents in batches
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        
        # Get embeddings for the batch
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch
        )
        
        # Extract embeddings from response
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
    
    return all_embeddings

def save_embeddings_to_csv(file_path: str, document_name: str, page_numbers: List[int], embeddings: List[List[float]], contexts: List[str]):
    """
    Cache embeddings to CSV for faster future lookups.
    
    CSV Format:
    document_name, page_number, embedding, context
    
    Args:
        file_path: Where to save the CSV
        document_name: Identifier for the source document
        page_numbers: List of page numbers for each chunk
        embeddings: List of embedding vectors
        contexts: List of text chunks
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['document_name', 'page_number', 'embedding', 'context'])
        
        # Write data rows
        for doc_name, page_num, embedding, context in zip(
            [document_name] * len(page_numbers),
            page_numbers,
            embeddings,
            contexts
        ):
            # Convert embedding to JSON string
            embedding_json = json.dumps(embedding)
            
            writer.writerow([doc_name, page_num, embedding_json, context])

def load_embeddings_from_csv(file_path: str) -> List[dict]:
    """
    Load previously cached embeddings from CSV.
    
    Returns: List of dicts with keys:
        - document_name: str
        - page_number: int  
        - embedding: List[float]
        - context: str
    """
    result = []
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Convert page_number to int
            page_number = int(row['page_number'])
            
            # Parse embedding from JSON string
            embedding = json.loads(row['embedding'])
            
            # Add to result
            result.append({
                'document_name': row['document_name'],
                'page_number': page_number,
                'embedding': embedding,
                'context': row['context']
            })
    
    return result
