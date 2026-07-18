import sqlite3
from state import TravelState
from researcher import researcher

conn = sqlite3.connect("travel_cache.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS research_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    preference TEXT NOT NULL,
    result TEXT NOT NULL,
    UNIQUE(city, preference)
)
""")

conn.commit()
def get_cached_result(city: str, preference: str):
    cursor.execute(
        "SELECT result FROM research_cache WHERE city=? AND preference=?",
        (city.lower(), preference.lower())
    )

    row = cursor.fetchone()
    if row:
        return row[0]
    return None


def save_result(city: str, preference: str, result: str):
    cursor.execute("""
        INSERT OR REPLACE INTO research_cache
        (city, preference, result)
        VALUES (?, ?, ?)
    """, (
        city.lower(),
        preference.lower(),
        result
    ))
    conn.commit()

def research_agent(state: TravelState) -> TravelState:
    print("entered research_agent")
    city = state["city"]
    preferences = state["preferences"]

    research_results = []

    for preference in preferences:

        # Check cache first
        cached = get_cached_result(city, preference)

        if cached:
            print(f"📦 Using cached result for {preference} in {city}")
            research_results.append(cached)
            continue

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

        result = response["messages"][-1].content

        print(f"💾 Saving {preference} in cache")

        save_result(city, preference, result)

        research_results.append(result)

    state["research_results"] = research_results
    print("✅ Research completed and cached.")
    return state