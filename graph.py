import os
import requests
from langgraph.graph import StateGraph

HF_API_KEY = os.getenv("HF_API_KEY")  # Secret stored in Streamlit Cloud

def get_coordinates(location):
    """Geocode location using Nominatim (OpenStreetMap)"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    headers = {"User-Agent": "CompetitorAnalyzerApp"}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if not data:
        return None

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    return lat, lon


def find_nearby_stores(state):
    location = state.get("location", "Koramangala, Bangalore")
    coords = get_coordinates(location)

    if not coords:
        return {"response": f"Could not find coordinates for {location}"}

    lat, lon = coords

    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["shop"="clothes"](around:1500,{lat},{lon});
      way["shop"="clothes"](around:1500,{lat},{lon});
      relation["shop"="clothes"](around:1500,{lat},{lon});
    );
    out center;
    """

    response = requests.post(overpass_url, data=query)
    data = response.json()

    store_names = []
    peak_hours = {}

    for element in data["elements"]:
        tags = element.get("tags", {})
        name = tags.get("name")
        if name:
            store_names.append(name)
            peak_hours[name] = "5PM - 9PM"  # Mocked, can improve later
        if len(store_names) >= 5:
            break

    return {
        "store_names": store_names,
        "store_peak_hours": peak_hours,
        "location": location
    }


def generate_strategy(state):
    store_names = state.get("store_names", [])
    peak_hours = state.get("store_peak_hours", {})
    location = state.get("location", "")

    prompt = f"""
A new clothing store wants to open in {location}.
Nearby competitors include: {store_names}
Their estimated peak hours are: {peak_hours}

Suggest 3 smart strategies for the new store to succeed in this area.
"""

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            headers=headers,
            json={"inputs": prompt}
        )
        result = response.json()

        if isinstance(result, list):
            return {"strategy": result[0].get("generated_text", "").strip()}
        elif "generated_text" in result:
            return {"strategy": result["generated_text"].strip()}
        else:
            return {"strategy": str(result)}

    except Exception as e:
        return {"strategy": f"⚠️ Error calling Hugging Face API: {e}"}


# Define the LangGraph pipeline
builder = StateGraph(input="location", output="strategy")
builder.add_node("store_finder", find_nearby_stores)
builder.add_node("strategy_generator", generate_strategy)

builder.set_entry_point("store_finder")
builder.add_edge("store_finder", "strategy_generator")

graph = builder.compile()
