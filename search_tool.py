from langchain_community.tools import DuckDuckGoSearchResults
from langchain_tavily import TavilySearch
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
from langchain_core.tools import tool
import requests
import os
from state import TravelState
load_dotenv()


class ZenserpSearch:
    def __init__(self):
        self.api_key = os.getenv("ZENSERP_API_KEY")
        self.url = "https://app.zenserp.com/api/v2/search"

    def invoke(self, query: str):
        headers = {
            "apikey": self.api_key
        }

        params = {
            "q": query,
            "engine": "google"
        }

        response = requests.get(
            self.url,
            headers=headers,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # Return only the organic results
        return data.get("organic", [])


class SearchTool:
    def __init__(self):
        self.ddg = DuckDuckGoSearchResults(output_format="list")
        self.tavily = TavilySearch(max_results=5)
        self.zenserp = ZenserpSearch()
        self.serper = GoogleSerperAPIWrapper()

    def search(self, query: str):

        # 1. DuckDuckGo
        try:
            print("Using DuckDuckGo...")
            return self.ddg.invoke(query)
        except Exception as e:
            print(f"DuckDuckGo failed: {e}")

        # 2. Tavily
        try:
            print("Using Tavily...")
            return self.tavily.invoke(query)
        except Exception as e:
            print(f"Tavily failed: {e}")

        # 3. Zenserp
        try:
            print("Using Zenserp...")
            return self.zenserp.invoke(query)
        except Exception as e:
            print(f"Zenserp failed: {e}")

        # 4. Serper
        try:
            print("Using Serper...")
            return self.serper.results(query)
        except Exception as e:
            print(f"Serper failed: {e}")

        raise Exception("All search providers failed.")


@tool
def web_search(query: str) -> str:
    """Search the web for travel-related information."""
    return str(SearchTool().search(query))