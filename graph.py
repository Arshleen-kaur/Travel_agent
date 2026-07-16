from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from datetime import date, time
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchResults
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from search_tool import SearchTool
load_dotenv()

MAX_CRITIC_ATTEMPTS = 3

search_tool = SearchTool()

llm = ChatOpenAI(
    model="tencent/hy3:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.8,
    streaming=True
)
researcher = create_agent(
    model=llm,
    tools=[search_tool],
    system_prompt="""
You are a travel research agent.
Use the search tool to research the user's travel preferences.
Return concise recommendations.
"""
)
class TravelState(TypedDict):
    city: str
    country: str
    itinerary: str
    budget: float
    currency: str
    preferences: list[str]
    start_date: date
    end_date: date
    hotel_checkin: time
    hotel_checkout: time
    research_results: list[str]
    critic_feedback: str
    critic_attempts: int
 
graph= StateGraph(TravelState)

def extract_preferences(state: TravelState) -> TravelState:
    def input_country()-> str:
        return input("Enter the country you want to travel to: ")
    state["country"] = input_country()
    def input_city()-> str:
        return input("Enter the city you want to travel to: ")
    state["city"] = input_city()
    def input_budget()-> float:
        return float(input("Enter your budget for the trip (excluding hotel and flight costs): "))
    state["budget"] = input_budget()
    def input_currency()-> str:
        return input("Enter your preferred currency (e.g., USD, EUR): ")
    state["currency"] = input_currency()
    def input_number_of_members()-> int:
        return int(input("Enter the number of members traveling: "))
    state["number_of_members"] = input_number_of_members()
    def input_preferences()-> list[str]:
        return input("Enter your preferences for the trip (comma-separated): ").split(",")
    state["preferences"] = input_preferences()
    def input_start_date()-> date:
        return date.fromisoformat(input("Enter the start date for the trip (YYYY-MM-DD): "))
    state["start_date"] = input_start_date()
    def input_end_date()-> date:
        return date.fromisoformat(input("Enter the end date for the trip (YYYY-MM-DD): "))
    state["end_date"] = input_end_date()
    def input_hotel_checkin()-> time:
        return time.fromisoformat(input("Enter the hotel check-in time (HH:MM): "))
    state["hotel_checkin"] = input_hotel_checkin()
    def input_hotel_checkout()-> time:
        return time.fromisoformat(input("Enter the hotel check-out time (HH:MM): "))
    state["hotel_checkout"] = input_hotel_checkout()
    return state

def research_agent(state: TravelState) -> TravelState:
    city = state["city"]
    preferences = state["preferences"]

    research_results = []

    for preference in preferences:
        print(f"🔍 Searching {preference} in {city}...")
        prompt = f"""
        Search the web for the best {preference} in {city}.
        Include:
        - Top places
        - Why they are recommended
        - Approximate timings if available
        - Approximate cost if available
        """
        response = researcher.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
            }
        )
        print(f"✅ Finished searching {preference}")

        research_results.append(response["messages"][-1].content)

    state["research_results"] = research_results
    return state

def itinerary_planner(state: TravelState) -> TravelState:
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

    response = llm.invoke(prompt)

    state["itinerary"] = response.content

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