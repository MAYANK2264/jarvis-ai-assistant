import requests
import json
import os
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Load environment variables
load_dotenv()

# Get API credentials from environment variables
API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")


# Function to search Google and get a mixture of regular results, images, and news
def search_google(query, search_type="web"):
    """Search Google using Custom Search API.
    
    Args:
        query: Search query string
        search_type: Type of search (web, image, or news)
        
    Returns:
        str: Formatted search results or error message
    """
    try:
        if not API_KEY or not CX:
            return "Error: Google Search API credentials not configured. Please set GOOGLE_API_KEY and GOOGLE_CX environment variables."

        # Extract command from query if present
        if "search" in query:
            query = query.replace("search", "").strip()

        # Construct the Google Search API URL
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"

        # Add filters based on search type
        if search_type == "image":
            url += "&searchType=image"
        elif search_type == "news":
            url += "&filter=1"

        # Make the API request with SSL verification disabled (for development only)
        response = requests.get(url, verify=False)
        data = response.json()

        if "items" in data:
            results = data["items"]
            # Summarize the top results
            summarized_results = []
            for item in results[:3]:  # Get top 3 results
                summary = {
                    "title": item["title"],
                    "link": item["link"],
                    "snippet": item.get("snippet", "No snippet available."),
                }
                summarized_results.append(summary)

            # Format results for output
            search_output = "\n\n".join(
                [
                    f"Title: {res['title']}\nLink: {res['link']}\nSummary: {res['snippet']}"
                    for res in summarized_results
                ]
            )

            if not search_output:
                return "No relevant results found."
            return search_output
        else:
            return "No results found."

    except requests.exceptions.RequestException as e:
        return f"Network error during search: {str(e)}"
    except Exception as e:
        return f"Error during search: {str(e)}"


# Function to search for web pages
def search_web(query):
    return search_google(query, search_type="web")


# Function to search for images
def search_images(query):
    return search_google(query, search_type="image")


# Function to search for news articles
def search_news(query):
    return search_google(query, search_type="news")
