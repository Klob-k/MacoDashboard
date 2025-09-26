import streamlit as st
import pandas as pd
import plotly.express as px
from data_sources.bts_socrata import get_transborder_trucks
from utils.transforms import add_growth

st.title("Cross-Border Flows (BTS – Transborder Trucks)")

df = get_transborder_trucks()
df = df.sort_values(["country","date"]).reset_index(drop=True)

# Add growth by country
out = []
for c, g in df.groupby("country"):
    out.append(add_growth(g, "value"))
df = pd.concat(out, ignore_index=True)

st.caption("US–Canada and US–Mexico monthly truck flows (sum). Fallback to Sample (offline) if API not available.")

st.plotly_chart(px.line(df, x="date", y="value", color="country", title="Trucks entering the U.S. by country"), use_container_width=True)
st.plotly_chart(px.bar(df.tail(60), x="date", y="YoY_%", color="country", title="YoY% – last 5 years"), use_container_width=True)
