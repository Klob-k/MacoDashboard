import streamlit as st
import plotly.express as px
from data_sources.bls import get_bls_series, TRUCK_EMP_SERIES
from utils.transforms import add_growth

st.title("Capacity & Labor (BLS)")
df = get_bls_series([TRUCK_EMP_SERIES])
df = add_growth(df, "value")
st.caption("If API keys are missing or request fails, this page uses Sample (offline).")

st.plotly_chart(px.line(df, x="date", y="value", title="Truck Transportation Employment (SA)"), use_container_width=True)
st.plotly_chart(px.bar(df.tail(60), x="date", y="YoY_%", title="YoY% – last 5 years"), use_container_width=True)
