import os, requests, pandas as pd
from dateutil.relativedelta import relativedelta
from pathlib import Path

BLS_TIMESERIES = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
TRUCK_EMP_SERIES = "CES4348400001"  # All employees, Truck Transportation (SA)

def _sample_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sample_data" / "bls_truck_employment_monthly.csv"

def get_bls_series(series_ids, start_year: int | None = None, end_year: int | None = None, api_key: str | None = None, timeout: int = 30) -> pd.DataFrame:
    if isinstance(series_ids, str): series_ids = [series_ids]
    end_year = end_year or pd.Timestamp.today().year
    start_year = start_year or (pd.Timestamp.today() - relativedelta(years=15)).year
    payload = {"seriesid": series_ids, "startyear": str(start_year), "endyear": str(end_year)}
    if api_key or os.getenv("BLS_API_KEY"):
        payload["registrationkey"] = api_key or os.getenv("BLS_API_KEY")
    try:
        r = requests.post(BLS_TIMESERIES, json=payload, timeout=timeout)
        r.raise_for_status()
        js = r.json()["Results"]["series"]
        frames = []
        for s in js:
            sid = s["seriesID"]
            df = pd.DataFrame(s["data"])
            df = df[df["period"].str.startswith("M")]
            df["date"] = pd.to_datetime(df["year"] + "-" + df["period"].str[1:] + "-01")
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df["series_id"] = sid
            frames.append(df[["date","value","series_id"]])
        out = pd.concat(frames, ignore_index=True).sort_values(["series_id","date"])
        return out
    except Exception:
        # fallback
        df = pd.read_csv(_sample_path(), parse_dates=["date"])
        df["series_id"] = series_ids[0]
        return df[["date","value","series_id"]]
