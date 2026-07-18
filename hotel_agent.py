from datetime import date
from serpapi import GoogleSearch
from state import TravelState
import os
from dotenv import load_dotenv

load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


def _format_date(value):
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def search_hotels(city, check_in, check_out, adults=2):

    if not SERPAPI_API_KEY:
        print("SerpAPI key is not configured. Set SERPAPI_API_KEY in your environment or .env file.")
        return []

    params = {
        "engine": "google_hotels",
        "q": city,
        "check_in_date": _format_date(check_in),
        "check_out_date": _format_date(check_out),
        "adults": adults,
        "currency": "INR",
        "hl": "en",
        "gl": "in",
        "api_key": SERPAPI_API_KEY,
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as exc:
        print(f"Hotel search request failed: {exc}")
        return []

    if results.get("error"):
        print(f"Hotel search API error: {results.get('error')}")
        return []

    if not results.get("properties"):
        print(
            "No hotels found. The API returned no properties; check the city, dates, or API key."
        )
        return []

    hotels = []

    for hotel in results.get("properties", []):
        gps_coordinates = hotel.get("gps_coordinates") or {}
        hotels.append({
            "name": hotel.get("name"),
            "rating": hotel.get("overall_rating"),
            "reviews": hotel.get("reviews"),
            "price_per_night": hotel.get("rate_per_night", {}).get("lowest"),
            "address": hotel.get("address"),
            "type": hotel.get("type"),
            "amenities": hotel.get("amenities", []),
            "gps": gps_coordinates,
            "latitude": gps_coordinates.get("latitude") if "latitude" in gps_coordinates else gps_coordinates.get("lat"),
            "longitude": gps_coordinates.get("longitude") if "longitude" in gps_coordinates else gps_coordinates.get("lng"),
        })

    return hotels

def hotel_agent(state: TravelState) -> TravelState:
    """
    If the user already has a hotel, keep it.
    Otherwise search hotels, let the user choose one,
    and save the chosen hotel into the state.
    """

    # User already has a hotel
    if state["has_hotel"]:
        print(f"\nUsing hotel: {state['hotel_name']}")
        return state

    print("\nSearching hotels...")

    adults = state.get("members", state.get("number_of_members", 2))

    hotels = search_hotels(
        city=state["city"],
        check_in=state["start_date"],
        check_out=state["end_date"],
        adults=adults,
    )

    if not hotels:
        print("No hotels found.")
        return state

    print("\nAvailable Hotels:\n")

    for i, hotel in enumerate(hotels, start=1):
        print(
            f"{i}. {hotel['name']}\n"
            f"   ⭐ {hotel['rating']}\n"
            f"   ₹{hotel['price_per_night']}/night\n"
            f"   {hotel['address']}\n"
        )

    while True:
        try:
            choice = int(input("Choose a hotel (number): "))

            if 1 <= choice <= len(hotels):
                selected = hotels[choice - 1]
                break

            print("Invalid choice.")

        except ValueError:
            print("Enter a valid number.")

    state["hotel_name"] = selected["name"]
    state["hotel_address"] = selected["address"]
    state["hotel_latitude"] = selected.get("latitude")
    state["hotel_longitude"] = selected.get("longitude")

    print(f"\nSelected hotel: {selected['name']}")

    return state
