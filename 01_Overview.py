import streamlit as st
import pandas as pd
import plotly.express as px

from data_sources.aggregator import load_all, build_composite
from utils.ui import sidebar_controls

st.title("Overview")

cfg = sidebar_controls()
data = load_all(cfg["years_back"])

comp = build_composite(data, cfg["weights"])

st.subheader("Composite Freight Conditions Index (prototype)")
st.caption("Positive = tighter/more supportive for carrier pricing; Negative = looser/weaker.")
st.plotly_chart(px.line(comp, x="date", y="freight_conditions_idx", title="Freight Conditions Index"), use_container_width=True)

# KPIs
st.divider()
st.subheader("Headline KPIs (latest)")
left, mid, right = st.columns(3)

diesel = data["diesel"].sort_values("date")
emp = data["employment"].sort_values("date")
retail = data["retail"].sort_values("date")

def fmt_delta(cur, prev):
    if pd.isna(prev): return "n/a"
    pct = (cur/prev - 1.0) * 100
    return f"{pct:+.1f}%"

with left:
    cur = diesel["value"].iloc[-1]; prev_w = diesel["value"].iloc[-53] if len(diesel) > 53 else float("nan")
    st.metric("Diesel ($/gal)", f"{cur:.2f}", fmt_delta(cur, prev_w))
with mid:
    cur = emp["value"].iloc[-1]; prev_y = emp["value"].iloc[-13] if len(emp) > 13 else float("nan")
    st.metric("Trucking Employment", f"{cur:,.0f}", fmt_delta(cur, prev_y))
with right:
    cur = retail["value"].iloc[-1]; prev_y = retail["value"].iloc[-13] if len(retail) > 13 else float("nan")
    st.metric("Retail Sales (SA, $M)", f"{cur:,.0f}", fmt_delta(cur, prev_y))

st.caption("If you see 'Sample (offline)' in page subtitles, the chart is using bundled sample data. Provide API keys for live data.")
