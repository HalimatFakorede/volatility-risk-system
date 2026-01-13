from fastapi import FastAPI
import pandas as pd
from src.pipeline import run_pipeline
from src.outputs import latest_risk_snapshot

def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flattens a DataFrame with MultiIndex columns into single-level columns.
    Example: ('close', 'eem') -> 'close_eem'
    """
    df = df.copy()
    df.columns = [
        "_".join([str(c) for c in col if str(c) != ""]).strip() 
        if isinstance(col, tuple) else str(col) 
        for col in df.columns
    ]
    return df

def to_json_safe(val):
    if pd.isna(val):
        return None
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    if hasattr(val, "item"):
        return val.item()
    if isinstance(val, (int, float, bool)):
        return val
    return str(val)

app = FastAPI(
    title="Emerging Markets Volatility & Risk API",
    description="Provides volatility-based risk signals and market regime detection",
    version="1.0"
)

# Lazy-load pipeline: only run when first request comes in
df, alerts = None, None


def get_pipeline_data():
    global df, alerts
    if df is None or alerts is None:
        df, alerts = run_pipeline()
    return df, alerts

@app.get("/")
def root():
    return {
        "message": "Welcome to the Volatility & Risk API!",
        "endpoints": [
            "/health",
            "/risk/latest",
            "/risk/latest-garch",
            "/risk/history",
            "/alerts"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/risk/latest")
def get_latest_risk():
    df, _ = get_pipeline_data()
    return latest_risk_snapshot(df)


@app.get("/risk/latest-garch")
def get_latest_garch_risk():
    df, _ = get_pipeline_data()
    return latest_risk_snapshot(df, vol_col="GARCH_Volatility")

@app.get("/risk/history")
def get_risk_history():
    df, _ = get_pipeline_data()

    cols = ["Volatility", "GARCH_Volatility", "Risk_Level", "Market_Regime"]
    if "HMM_Regime" in df.columns:
        cols.append("HMM_Regime")

    history = df[cols].tail(250).copy()
    history = history.reset_index()
    history = flatten_columns(history)

    records = []
    for _, row in history.iterrows():
        record = {
            col.lower(): to_json_safe(row[col])
            for col in history.columns
        }
        records.append(record)

    return records


@app.get("/alerts")
def get_alerts():
    _, alerts = get_pipeline_data()

    alerts = alerts.tail(50).copy()
    alerts = alerts.reset_index()
    alerts = flatten_columns(alerts)

    records = []
    for _, row in alerts.iterrows():
        record = {
            col.lower(): to_json_safe(row[col])
            for col in alerts.columns
        }
        records.append(record)

    return records