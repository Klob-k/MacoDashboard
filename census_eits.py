import requests, pandas as pd
from pathlib import Path

def _sample_path(name: str) -> Path:
    return Path(__file__).resolve().parents[1] / "sample_data" / name

def _safe_request(url: str, params: dict, timeout: int = 20):
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r

def get_retail_sales_sa():
    # Attempt Census EITS Retail Sales (SA, total). If it fails, fallback.
    base = "https://api.census.gov/data/timeseries/eits/rs"
    params = {
        "get": "cell_value,time",
        "time": "from 2015",
        "seasonally_adjusted": "Yes",
        "time_slot_id": "1",
        "data_type_code": "SM",   # sales, millions (subject to change in API)
        "category_code": "44X72"  # retail & food services total
    }
    try:
        r = _safe_request(base, params)
        raw = r.json()
        cols, rows = raw[0], raw[1:]
        df = pd.DataFrame(rows, columns=cols)
        df["date"] = pd.to_datetime(df["time"])
        df["value"] = pd.to_numeric(df["cell_value"], errors="coerce")
        df["series_id"] = "CENSUS_RS_SA_TOTAL"
        return df[["date","value","series_id"]].sort_values("date")
    except Exception:
        df = pd.read_csv(_sample_path("census_rs_monthly.csv"), parse_dates=["date"])
        df["series_id"] = "CENSUS_RS_SA_TOTAL"
        return df[["date","value","series_id"]]

def get_m3_shipments_sa():
    # Attempt Census M3 shipments. Fallback to sample if request fails.
    base = "https://api.census.gov/data/timeseries/eits/m3"
    params = {
        "get": "cell_value,time",
        "time": "from 2015",
        "seasonally_adjusted": "Yes",
        "category_code": "SHIP"
    }
    try:
        r = _safe_request(base, params)
        raw = r.json()
        cols, rows = raw[0], raw[1:]
        df = pd.DataFrame(rows, columns=cols)
        df["date"] = pd.to_datetime(df["time"])
        df["value"] = pd.to_numeric(df["cell_value"], errors="coerce")
        df["series_id"] = "CENSUS_M3_SHIP_SA"
        return df[["date","value","series_id"]].sort_values("date")
    except Exception:
        df = pd.read_csv(_sample_path("census_m3_shipments_monthly.csv"), parse_dates=["date"])
        df["series_id"] = "CENSUS_M3_SHIP_SA"
        return df[["date","value","series_id"]]
