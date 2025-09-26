import streamlit as st
import pandas as pd
import plotly.express as px
from data_sources.census_eits import get_retail_sales_sa, get_m3_shipments_sa
from utils.transforms import add_growth

st.title("Demand Proxies (Census)")

ret = get_retail_sales_sa()
m3 = get_m3_shipments_sa()
ret = add_growth(ret, "value")
m3 = add_growth(m3, "value")

st.caption("Retail (SA, Total) and M3 Shipments. Fallback to Sample (offline) if API not available.")

tabs = st.tabs(["Retail Sales", "M3 Shipments"])
with tabs[0]:
    st.plotly_chart(px.line(ret, x="date", y="value", title="Retail Sales (SA, $ Millions)"), use_container_width=True)
    st.plotly_chart(px.bar(ret.tail(60), x="date", y="YoY_%", title="YoY% – last 5 years"), use_container_width=True)
with tabs[1]:
    st.plotly_chart(px.line(m3, x="date", y="value", title="M3 Shipments (SA, $ Millions)"), use_container_width=True)
    st.plotly_chart(px.bar(m3.tail(60), x="date", y="YoY_%", title="YoY% – last 5 years"), use_container_width=True)
