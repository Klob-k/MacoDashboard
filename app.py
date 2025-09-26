import streamlit as st

st.set_page_config(page_title="Freight Macro Dashboard", layout="wide")
st.title("Freight Macro Dashboard")

st.markdown(
    "Use the **Pages** menu (left sidebar) to navigate: Overview, Fuel, Capacity, Demand, Cross-Border."
)
st.info("Tip: provide API keys via environment variables for live data. Without keys, the app uses sample data.")
