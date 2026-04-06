import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_tool(query):
    url = "https://serpapi.com/search"

    params = {
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "engine": "google"
    }

    res = requests.get(url, params=params)
    data = res.json()

    snippets = []

    for r in data.get("organic_results", [])[:3]:
        snippets.append(r.get("snippet", ""))

    return "\n".join(snippets)