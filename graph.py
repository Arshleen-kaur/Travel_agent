from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from datetime import date, time
from langchain_community.tools import DuckDuckGoSearchResults
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from search_tool import SearchTool,web_search
from state import TravelState
from guardrails import extract_preferences
from research_agent import research_agent
from researcher import researcher
from llm_config import llm

load_dotenv()

MAX_CRITIC_ATTEMPTS = 3

search_tool = SearchTool()

graph= StateGraph(TravelState)


def itinerary_planner(state: TravelState) -> TravelState:
    print("Entered itinerary_planner")
    previous_itinerary = state.get("itinerary", "")
    critic_feedback = state.get("critic_feedback", "")

    prompt = f"""
    You are an expert travel planner.

    Destination:
    {state["city"]}

    Start Date: {state["start_date"]}
    End Date: {state["end_date"]}

    Hotel Check-in: {state["hotel_checkin"]}
    Hotel Check-out: {state["hotel_checkout"]}

    Budget:
    {state["budget"]}

    Currency:
    {state["currency"]}

    Preferences:
    {", ".join(state["preferences"])}

    Research:
    {chr(10).join(state["research_results"])}

    Previous Itinerary:
    {previous_itinerary}

    Critic Feedback:
    {critic_feedback}

    Instructions:
    - If the Previous Itinerary is empty, create a brand-new itinerary.
    - If a Previous Itinerary exists, revise and improve it instead of starting from scratch.
    - Address every issue mentioned in the Critic Feedback.
    - Preserve parts of the itinerary that are already good.
    - Create a day-by-day itinerary.
    - Optimize travel time by grouping nearby attractions.
    - Include breakfast, lunch, dinner, and sightseeing.
    - Respect hotel check-in and check-out times.
    - The budget is exclusive of hotel costs, and flights which are already covered.
    - Stay within the given budget.
    - Include approximate timings.
    - Suggest transportation between places.
    - Mention estimated costs whenever possible.
    - End each day with the estimated daily cost.
    - Return ONLY the final improved itinerary in Markdown.
    """
    print("Invoking llm for itinerary planning...")
    response = llm.invoke(prompt)
    print("Itinerary planning completed.")
    state["itinerary"] = response.content
    print("LEAVING itinerary_planner")
    return state

def critic_router(state: TravelState) -> str:
    # Stop if maximum retries have been reached
    if state["critic_attempts"] >= MAX_CRITIC_ATTEMPTS:
        print("✅ Maximum critic attempts reached.")
        return "end"

    feedback = state["critic_feedback"].strip().upper()

    # End only if the feedback starts with APPROVED
    if feedback.startswith("APPROVED"):
        print("✅ Itinerary approved by critic.")
        return "end"

    print(f"🔄 Itinerary not approved. Retrying ({state['critic_attempts']}/{MAX_CRITIC_ATTEMPTS})...")
    return "rewrite"

def critic_agent(state: TravelState) -> TravelState:
    # Initialize if it doesn't exist
    if "critic_attempts" not in state:
        state["critic_attempts"] = 0

    # Stop after 3 attempts
    if state["critic_attempts"] >= MAX_CRITIC_ATTEMPTS:
        return state

    prompt = f"""
    
    You are a travel critic.

    Review the following itinerary and provide feedback.

    Itinerary:
    {state["itinerary"]}

    Instructions:
    - Check for feasibility of the itinerary.
    - Suggest improvements or alternatives.
    - Ensure that the itinerary respects the user's preferences and budget.
    - Provide constructive criticism in a clear and concise manner.
    - Return your feedback in well-formatted Markdown.
    If the itinerary is already excellent and requires no further changes,
    begin your response with exactly the word:

    APPROVED

    Otherwise, begin your response with:

    NOT APPROVED

    followed by detailed feedback.
    """

    response = llm.invoke(prompt)

    state["critic_feedback"] = response.content
    state["critic_attempts"] += 1

    return state
graph.add_node("extract_preferences",extract_preferences)
graph.add_node("research_agent",research_agent)
graph.add_node("itinerary_planner",itinerary_planner)
graph.add_node("critic_agent",critic_agent)

graph.add_edge(START, "extract_preferences")
graph.add_edge("extract_preferences", "research_agent")
graph.add_edge("research_agent", "itinerary_planner")
graph.add_edge("itinerary_planner", "critic_agent")
graph.add_conditional_edges(
    "critic_agent",
    critic_router,
    {
        "rewrite": "itinerary_planner",
        "end": END,
    },
)
app = graph.compile()
result = app.invoke(
    {
        "critic_attempts": 0
    }
)

print(result["itinerary"])
print(result["critic_feedback"])