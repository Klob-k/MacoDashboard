import os, requests, pandas as pd
from pathlib import Path

def _sample_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sample_data" / "bts_transborder_trucks_monthly.csv"

def get_transborder_trucks(limit: int = 50000, timeout: int = 30) -> pd.DataFrame:
    # Socrata endpoint for vehicles entering (includes trucks); simplified monthly country totals
    url = "https://data.bts.gov/resource/btpt-uxhx.json"
    headers = {}
    tok = os.getenv("SOCRATA_APP_TOKEN")
    if tok: headers["X-App-Token"] = tok
    params = {
        "$select": "date, country, sum(value) as value",
        "$where": "measure='Trucks'",
        "$group": "date, country",
        "$order": "date",
        "$limit": limit,
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=timeout)
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        if df.empty:
            raise RuntimeError("Empty BTS response")
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df[["date","country","value"]].sort_values(["country","date"])
    except Exception:
        return pd.read_csv(_sample_path(), parse_dates=["date"])[["date","country","value"]]
