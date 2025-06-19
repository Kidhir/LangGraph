def format_response(state):
    response = "🧠 Competitor Report:\n"
    for store, data in state["insights"].items():
        response += f"- {store}: Footfall - {data['footfall']}, Peak Hours - {data['peak_hours']}\n"
    return {"response": response}
