from search_tool import web_search
from state import TravelState
from langchain.agents import create_agent
from llm_config import llm

researcher = create_agent(
    model=llm,
    tools=[web_search],
    system_prompt="""
You are a travel research agent.
Use the search tool to research the user's travel preferences.
Return concise recommendations.
"""
)