import requests
from datetime import date, time
from dotenv import load_dotenv
import os
load_dotenv()
from state import TravelState
import requests


def is_gibberish(text: str) -> bool:
    """
    Returns True if the input is detected as gibberish.
    """
    # 1. Point to the correct Gibberish Detector endpoint
    url = "https://api.apiverve.com/v1/gibberishdetector"

    headers = {
        "x-api-key": os.getenv("APIVERVE_API_KEY"),
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 2. Structure the data as a payload rather than URL params
    payload = {
        "text": text
    }

    try:
        # 3. Use requests.post() instead of requests.get()
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            response_json = response.json()

            # 4. Extract 'isGibberish' from inside the 'data' dictionary
            return response_json.get("data", {}).get("isGibberish", False)

        else:
            print(f"Warning: Gibberish API unavailable. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Gibberish API Error: {e}")
        return False

def validated_text_input(prompt: str) -> str:
    while True:
        text = input(prompt).strip()

        if not text:
            print("Input cannot be empty.")
            continue

        if is_gibberish(text):
            print("The entered text appears to be gibberish. Please enter a valid value.")
            continue

        return text
    
def extract_preferences(state: TravelState) -> TravelState:

    state["country"] = validated_text_input(
        "Enter the country you want to travel to: "
    )

    state["city"] = validated_text_input(
        "Enter the city you want to travel to: "
    )

    state["budget"] = float(
        input("Enter your budget for the trip (excluding hotel and flight costs): ")
    )

    state["currency"] = validated_text_input(
        "Enter your preferred currency (e.g., USD, EUR): "
    )

    state["number_of_members"] = int(
        input("Enter the number of members traveling: ")
    )

    prefs = validated_text_input(
        "Enter your preferences (comma-separated): "
    )

    state["preferences"] = [
        p.strip() for p in prefs.split(",") if p.strip()
    ]

    state["start_date"] = date.fromisoformat(
        input("Enter the start date (YYYY-MM-DD): ")
    )

    state["end_date"] = date.fromisoformat(
        input("Enter the end date (YYYY-MM-DD): ")
    )

    state["hotel_checkin"] = time.fromisoformat(
        input("Enter hotel check-in time (HH:MM): ")
    )

    state["hotel_checkout"] = time.fromisoformat(
        input("Enter hotel check-out time (HH:MM): ")
    )

    return state