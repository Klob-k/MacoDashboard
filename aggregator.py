import os, pandas as pd
from .eia import get_diesel_us_weekly
from .bls import get_bls_series, TRUCK_EMP_SERIES
from .census_eits import get_retail_sales_sa, get_m3_shipments_sa
from .bts_socrata import get_transborder_trucks
from ..utils.transforms import zscore, infer_yoy_periods

def _trim_years(df: pd.DataFrame, years_back: int) -> pd.DataFrame:
    if df.empty: return df
    cutoff = pd.Timestamp.today() - pd.DateOffset(years=years_back)
    return df[df["date"] >= cutoff].copy()

def load_all(years_back: int = 10) -> dict:
    diesel = get_diesel_us_weekly()
    emp = get_bls_series([TRUCK_EMP_SERIES])
    retail = get_retail_sales_sa()
    m3 = get_m3_shipments_sa()
    bts = get_transborder_trucks()

    return {
        "diesel": _trim_years(diesel, years_back),
        "employment": _trim_years(emp, years_back),
        "retail": _trim_years(retail, years_back),
        "m3_ship": _trim_years(m3, years_back),
        "bts": _trim_years(bts, years_back),
    }

def build_composite(data: dict, weights: dict) -> pd.DataFrame:
    # Expect keys: diesel, employment, retail, m3_ship
    # Compute YoY for signals; align to a common weekly or monthly index by resampling monthly to weekly.
    # We'll compute on a **weekly** grid to allow diesel (weekly) to align with monthly series (ffill).
    # Prepare weekly index
    import numpy as np
    idx = pd.date_range(start=min([
        data["diesel"]["date"].min(),
        data["employment"]["date"].min(),
        data["retail"]["date"].min(),
        data["m3_ship"]["date"].min(),
    ]), end=pd.Timestamp.today(), freq="W-SUN")

    # Diesel YoY%
    d = data["diesel"].set_index("date")["value"].resample("W-SUN").mean().ffill()
    d_yoy = d.pct_change(52) * 100

    # Employment YoY%
    e = data["employment"].set_index("date")["value"].resample("M").mean().asfreq("W-SUN").ffill()
    e_yoy = e.pct_change(52) * 100  # approx yearly on weekly grid

    # Demand proxy: average of Retail and M3 shipments YoY%
    r = data["retail"].set_index("date")["value"].resample("M").mean().asfreq("W-SUN").ffill()
    m = data["m3_ship"].set_index("date")["value"].resample("M").mean().asfreq("W-SUN").ffill()
    demand_yoy = pd.concat([r.pct_change(52)*100, m.pct_change(52)*100], axis=1).mean(axis=1)

    df = pd.concat([d_yoy.rename("diesel_yoy"), e_yoy.rename("emp_yoy"), demand_yoy.rename("demand_yoy")], axis=1).reindex(idx).dropna()

    # Z-score & combine
    comp = (
        weights.get("demand",1.0) * ( (df["demand_yoy"] - df["demand_yoy"].mean()) / (df["demand_yoy"].std(ddof=0) or 1) )
        - weights.get("capacity",1.0) * ( (df["emp_yoy"] - df["emp_yoy"].mean()) / (df["emp_yoy"].std(ddof=0) or 1) )
        - weights.get("cost",1.0) * ( (df["diesel_yoy"] - df["diesel_yoy"].mean()) / (df["diesel_yoy"].std(ddof=0) or 1) )
    )
    out = df.copy()
    out["freight_conditions_idx"] = comp
    out = out.reset_index().rename(columns={"index":"date"})
    return out
