import streamlit as st
from graph import graph

st.set_page_config(page_title="🧠 Competitor Analyzer", layout="centered")
st.title("🧠 Competitor Analyzer")

st.markdown(
    "Analyze clothing store competitors in any location — powered by OpenStreetMap + Local LLM (Mistral via Ollama)."
)

location = st.text_input("📍 Enter a location:", value="Koramangala, Bangalore")

if st.button("Get Competitor Insights"):
    with st.spinner("Analyzing competitors and generating strategy..."):
        try:
            result = graph.invoke({"location": location})

            # Extract returned data
            store_list = result.get("store_names", [])
            peak_hours = result.get("store_peak_hours", {})
            strategy = result.get("strategy", "")
            location_name = result.get("location", "")

            # UI Output
            st.subheader(f"📍 Competitor Analysis: {location_name}")

            # Store names
            st.markdown("### 👕 Top Clothing Stores Nearby")
            if store_list:
                for store in store_list:
                    st.markdown(f"- **{store}**")
            else:
                st.info("No clothing stores found nearby.")

            # Peak hours
            st.markdown("### ⏰ Estimated Peak Hours")
            if peak_hours:
                for store, hours in peak_hours.items():
                    st.markdown(f"- **{store}**: {hours}")
            else:
                st.info("No peak hour estimates available.")

            # Strategy
            st.markdown("### 💡 Business Strategy Recommendations")
            if strategy:
                st.success(strategy)
            else:
                st.warning("No strategy was generated.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
