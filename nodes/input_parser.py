def parse_location(state):
    location = state.get("location", "Koramangala, Bangalore")
    print(f"📍 User Location: {location}")
    return {**state, "parsed_location": location}
