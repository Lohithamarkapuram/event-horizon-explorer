import os
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
NASA_API_KEY = os.getenv("NASA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- NASA API Function ---

def get_datasets(keywords: list) -> list:
    """
    Searches the NASA CMR API for datasets matching a list of keywords.

    Args:
        keywords: A list of strings to use as search terms.

    Returns:
        A list of dictionaries, where each dictionary represents a dataset.
    """
    if not keywords:
        return []

    # The URL for the NASA CMR search endpoint
    NASA_CMR_URL = "https://cmr.earthdata.nasa.gov/search/collections.json"
    
    # Join the list of keywords into a single, space-separated string
    search_string = ' '.join(keywords)
    
    params = {
        'keyword': search_string,
        'page_size': 5,  # Get the top 5 most relevant results
        'sort_key': "-score" # Sort by relevance score
    }

    print(f"Searching NASA for datasets with keywords: '{search_string}'...")
    
    try:
        response = requests.get(NASA_CMR_URL, params=params)
        response.raise_for_status()
        raw_data = response.json()

        # --- REFINEMENT LOGIC STARTS HERE ---
        clean_datasets = []
        entries = raw_data.get('feed', {}).get('entry', [])

        for entry in entries:
            clean_item = {
                "title": entry.get('title', 'No Title Available'),
                "summary": entry.get('summary', 'No summary available.').strip(),
                # Find the DOI link, which is often the most stable one
                "link": next((link['href'] for link in entry.get('links', []) if 'doi.org' in link.get('href', '')), None)
            }
            clean_datasets.append(clean_item)
        
        return clean_datasets # Return the clean list, not the raw data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return [] # Return an empty list on error

# --- Gemini API Function ---

def get_explanation(title: str, summary: str) -> str:
    """
    Uses the Gemini API to generate a simple explanation for a dataset.

    Args:
        title: The title of the dataset.
        summary: The technical summary of the dataset.

    Returns:
        A simplified explanation string, or an error message if the API call fails.
    """
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY not found. Please check your .env file."

    GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
    Your role is a NASA science communicator.
    Your task is to explain a complex dataset to a curious high school student.
    Be clear, concise, and engaging. Do not exceed three sentences.

    Dataset Title: "{title}"
    Dataset Description: "{summary}"

    Explanation:
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    print(f"Asking Gemini for an explanation of '{title}'...")

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=20)
        response.raise_for_status()

        data = response.json()
        explanation = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Sorry, I couldn't generate an explanation.")
        return explanation.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return "Error: Could not connect to the explanation service."
    except (KeyError, IndexError) as e:
        print(f"Error parsing Gemini response: {e}")
        return "Error: The explanation service gave an unexpected response."