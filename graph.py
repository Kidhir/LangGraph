import requests
import random
from langgraph.graph import StateGraph


def generate_insight(state):
    location = state.get("location", "Koramangala, Bangalore")

    # Step 1: Geocode using Nominatim (OpenStreetMap)
    geo_url = "https://nominatim.openstreetmap.org/search"
    geo_params = {"q": location, "format": "json", "limit": 1}
    try:
        geo_res = requests.get(geo_url, params=geo_params, headers={"User-Agent": "LangGraphApp"}).json()
    except Exception as e:
        return {"response": f"Geocoding error: {e}"}

    if not geo_res:
        return {"response": f"Could not find the location: {location}"}

    lat, lon = float(geo_res[0]['lat']), float(geo_res[0]['lon'])

    # Step 2: Overpass API to find nearby clothing stores
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["shop"="clothes"](around:1500,{lat},{lon});
      way["shop"="clothes"](around:1500,{lat},{lon});
      relation["shop"="clothes"](around:1500,{lat},{lon});
    );
    out center;
    """
    try:
        res = requests.get(overpass_url, params={"data": query}, timeout=30)
        if res.status_code != 200:
            return {"response": f"Overpass API error: {res.status_code}"}
        data = res.json()
    except Exception as e:
        return {"response": f"Overpass error: {e}"}

    store_names = [el["tags"]["name"] for el in data.get("elements", []) if "tags" in el and "name" in el["tags"]][:5]

    # Step 3: Simulate footfall/peak hours
    mock_hours = ["11AM–2PM", "2PM–5PM", "5PM–8PM", "6PM–9PM", "Weekend Only"]
    store_peak_hours = {store: random.choice(mock_hours) for store in store_names}

    # Step 4: Response summary
    response = f"📍 Competitor insights for {location}:\n\n👕 Clothing Stores Nearby:\n"
    response += "\n".join([f"• {store}" for store in store_names]) or "• None found"
    response += "\n\n⏰ Estimated Peak Hours:\n"
    response += "\n".join([f"• {store}: {store_peak_hours[store]}" for store in store_peak_hours])

    return {
        "response": response,
        "location": location,
        "store_names": store_names,
        "store_peak_hours": store_peak_hours,
    }


def generate_strategy(state):
    store_names = state.get("store_names", [])
    store_peak_hours = state.get("store_peak_hours", {})
    location = state.get("location", "")

    prompt = f"""
You are a retail business strategist.

A new clothing store wants to open in {location}.
Nearby competitors include: {store_names}
Their estimated peak hours are: {store_peak_hours}

Suggest 3 smart strategies for the new store to succeed in this area.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",  # You can also try llama3, gemma, etc.
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()
        return {"strategy": result.get("response", "No strategy generated.")}
    except Exception as e:
        return {"strategy": f"Error calling local LLM: {e}"}


# Build LangGraph pipeline
builder = StateGraph(input="location", output="strategy")

builder.add_node("insight_generator", generate_insight)
builder.add_node("strategy_generator", generate_strategy)

builder.set_entry_point("insight_generator")
builder.add_edge("insight_generator", "strategy_generator")
builder.set_finish_point("strategy_generator")

graph = builder.compile()
