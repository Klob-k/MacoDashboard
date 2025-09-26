# Freight Macro Dashboard (Streamlit)

A lightweight, data-driven **Streamlit** dashboard for monitoring U.S. **trucking market conditions** using **free government data** (fuel, capacity/labor, demand proxies, cross-border flows). It supports live API pulls (EIA, BLS, Census EITS, BTS/Socrata) **with automatic fallback to included sample data** so you can run it immediately.

---

## Features
- **Composite “Freight Conditions” index** blending demand, capacity, and cost with user-adjustable weights.
- Pages for:
  - **Overview** (composite index + headline KPIs)
  - **Costs – Fuel** (EIA diesel)
  - **Capacity & Labor** (BLS Truck Transportation employment)
  - **Demand Proxies** (Census Retail Sales, M3 Shipments)
  - **Cross-Border Flows** (BTS Transborder trucks, US–CA/MX)
- **MoM/YoY deltas**, rolling averages, and trends.
- **Caching** for daily refresh; **fallback sample data** for offline/demo.

> This scaffold prioritizes simplicity and reliability. APIs are wrapped with graceful fallbacks to `sample_data/` if env keys are missing or requests fail.

---

## Quickstart (Replit or local)

1) **Upload** this project folder (or unzip it) into your Replit project.
2) **Install dependencies** (Replit will read `requirements.txt` automatically; locally run `pip install -r requirements.txt`).
3) **(Optional) Set API keys** in environment variables (Replit “Secrets” or local `.env`):
   - `EIA_API_KEY` (recommended)
   - `BLS_API_KEY` (optional; helpful for higher rate limits)
   - `SOCRATA_APP_TOKEN` (optional; increases BTS rate limits)
4) **Run**: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT` (Replit) or just `streamlit run app.py` locally.
5) Open the URL Streamlit prints.

If no keys are provided, the app **still runs** with the included **synthetic sample data** (clearly labeled).

---

## Data sources (live when keys available)
- **Fuel (Costs)**: EIA U.S. On-Highway Diesel (weekly).
- **Capacity/Labor**: BLS Truck Transportation Employment (CES, NAICS 484).
- **Demand proxies**: U.S. Census Economic Indicators (Retail Sales, M3 Shipments).
- **Cross-border flows**: DOT/BTS Transborder truck volumes (Socrata).
- **(Optional later)**: USDA AMS Specialty Crops Truck Rate (perishables season proxy), TSI – Freight, BEA GDP by industry, PPI Truck Transportation.

---

## Project structure

```
freight_macro_dashboard/
  app.py
  requirements.txt
  .env.example
  README.md
  data_sources/
    __init__.py
    eia.py
    bls.py
    census_eits.py
    bts_socrata.py
    aggregator.py
  utils/
    transforms.py
    ui.py
  pages/
    01_Overview.py
    02_Costs_Fuel.py
    03_Capacity_Labor.py
    04_Demand_Proxies.py
    05_CrossBorder_Flows.py
  sample_data/
    eia_diesel_us_weekly.csv
    bls_truck_employment_monthly.csv
    census_rs_monthly.csv
    census_m3_shipments_monthly.csv
    bts_transborder_trucks_monthly.csv
```

---

## Environment Variables

Copy `.env.example` to `.env` (if running locally) and fill values, or set them in Replit “Secrets”:

```
EIA_API_KEY=your_eia_key_here
BLS_API_KEY=optional_bls_key
SOCRATA_APP_TOKEN=optional_socrata_app_token
```

> Without keys the app will read `sample_data/` and clearly note “Sample (offline)” in chart subtitles.

---

## How the composite index works (prototype)

```
Index = w_demand * z( YoY% of demand proxy )
      - w_capacity * z( YoY% of trucking employment )
      - w_cost     * z( YoY% of diesel price )
```

- **Demand proxy**: Retail Sales (SA) and M3 Shipments (if available); otherwise 0 until APIs succeed.
- **Capacity**: higher employment → looser capacity → subtracts from index.
- **Cost**: higher diesel → higher costs → subtracts from index.
- We standardize each signal (z-score) and allow the user to set weights in the sidebar.

---

## Notes & Enhancements
- Add state/PADD breakdowns for diesel, PPI Truck Transportation, TSI Freight.
- Add alerts (e.g., diesel YoY > +10%, retail sales MoM < −1%).
- Persist API pulls to DuckDB/Parquet for history & faster reload.
- Add USDA AMS Truck Rate (FVWTRK) parsing or API mapping for seasonal produce pressure.

---

## License
For internal analytics use. Verify each data provider’s terms of service.
