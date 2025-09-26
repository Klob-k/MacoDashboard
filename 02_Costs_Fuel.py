import streamlit as st
import plotly.express as px
from data_sources.eia import get_diesel_us_weekly
from utils.transforms import add_growth

st.title("Costs – Fuel (EIA)")
df = get_diesel_us_weekly()
df = add_growth(df, "value")
subtitle = "Live EIA" if "Sample" not in st.session_state.get("fuel_subtitle","") else "Sample (offline)"
st.caption(subtitle if subtitle else ("Units: " + (df.get("units") if isinstance(df, dict) else "USD/gal")))

st.plotly_chart(px.line(df, x="date", y="value", title="US On-Highway Diesel ($/gal)"), use_container_width=True)
st.plotly_chart(px.bar(df.tail(104), x="date", y="YoY_%", title="YoY% – last 2 years"), use_container_width=True)
