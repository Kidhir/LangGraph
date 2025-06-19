def search_nearby_stores(state):
    location = state["parsed_location"]
    # Stub: Later connect to Google Places API
    dummy_stores = ["Zara", "H&M", "Levi's"]
    print(f"🛍️ Found Stores: {dummy_stores}")
    return {**state, "stores": dummy_stores}
