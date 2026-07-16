from datetime import date, time
from langchain_protocol import TypedDict


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