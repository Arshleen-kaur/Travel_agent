from langchain_community.tools import DuckDuckGoSearchResults
from langchain_tavily import TavilySearch
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

class SearchTool:
    def __init__(self):
        self.ddg = DuckDuckGoSearchResults(output_format="list")

        # Requires TAVILY_API_KEY
        self.tavily = TavilySearch(max_results=5)

        # Requires SERPER_API_KEY
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

        # 3. Serper
        try:
            print("Using Serper...")
            return self.serper.results(query)
        except Exception as e:
            print(f"Serper failed: {e}")

        raise Exception("All search providers failed.")



print(TavilySearch(max_results=5).invoke("Love in chandigarh"))