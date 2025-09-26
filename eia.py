import os, requests, pandas as pd
from pathlib import Path

EIA_SERIES_ENDPOINT = "https://api.eia.gov/series/"
DEFAULT_SERIES = "PET.EMD_EPD2D_PTE_NUS_DPG.W"  # US on-highway diesel

def _sample_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sample_data" / "eia_diesel_us_weekly.csv"

def get_diesel_us_weekly(series_id: str = DEFAULT_SERIES, api_key: str | None = None, timeout: int = 20) -> pd.DataFrame:
    api_key = api_key or os.getenv("EIA_API_KEY")
    if api_key:
        try:
            r = requests.get(EIA_SERIES_ENDPOINT, params={"api_key": api_key, "series_id": series_id}, timeout=timeout)
            r.raise_for_status()
            ser = r.json()["series"][0]
            df = pd.DataFrame(ser["data"], columns=["period", "value"])
            # Try daily/weekly/monthly date parsing
            df["date"] = pd.to_datetime(df["period"], format="%Y%m%d", errors="coerce").fillna(
                pd.to_datetime(df["period"], format="%Y%m", errors="coerce")
            )
            df = df.dropna(subset=["date"]).sort_values("date")
            df["series_id"] = ser.get("series_id", series_id)
            df["units"] = ser.get("units", "USD/gal")
            return df[["date","value","series_id","units"]]
        except Exception:
            pass  # fall back to sample
    # fallback
    df = pd.read_csv(_sample_path(), parse_dates=["date"])
    df["series_id"] = series_id
    df["units"] = "USD/gal"
    return df[["date","value","series_id","units"]]
