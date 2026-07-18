from datetime import date, time
from langchain_protocol import TypedDict


class TravelState(TypedDict):
    city: str
    country: str
    itinerary: str
    budget: float
    currency: str
    preferences: list[str]
    members: int
    number_of_members: int
    start_date: date
    end_date: date
    hotel_checkin: time
    hotel_checkout: time
    research_results: list[str]
    critic_feedback: str
    critic_attempts: int
    has_hotel: bool
    hotel_name: str
    hotel_address: str
    hotel_latitude: float
    hotel_longitude: float