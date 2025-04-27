import requests
import json

# Replace these with your actual Google API key and Custom Search Engine ID
API_KEY = "AIzaSyAzbZFUzk8TxSs_BtYKHWFBaYcx-WP0Vu0"
CX = "d42f59264d68b487d"

# Function to search Google and get a mixture of regular results, images, and news
def search_google(query, search_type="web"):
    try:
        # Construct the Google Search API URL
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"

        # Add filters based on search type
        if search_type == "image":
            url += "&searchType=image"
        elif search_type == "news":
            url += "&filter=1"

        # Make the API request
        response = requests.get(url)
        data = response.json()

        if "items" in data:
            results = data["items"]
            # Summarize the top results (just the title and link for now)
            summarized_results = []
            for item in results[:5]:  # Get top 5 results
                summary = {
                    "title": item["title"],
                    "link": item["link"],
                    "snippet": item.get("snippet", "No snippet available.")
                }
                summarized_results.append(summary)

            # Check for unsafe content (basic filtering)
            safe_results = [res for res in summarized_results if "unsafe" not in res["snippet"].lower()]

            # Format results for output
            search_output = "\n".join([f"Title: {res['title']}\nLink: {res['link']}\nSnippet: {res['snippet']}\n" for res in safe_results])

            if not search_output:
                search_output = "No relevant or safe results found."
            return search_output
        else:
            return "No results found."

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
