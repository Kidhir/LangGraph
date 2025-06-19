def fetch_store_insights(state):
    insights = {
        store: {"footfall": "high", "peak_hours": "5 PM - 8 PM"}
        for store in state["stores"]
    }
    print(f"📊 Insights: {insights}")
    return {**state, "insights": insights}
