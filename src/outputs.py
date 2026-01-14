import pandas as pd

def _to_scalar(x):
    if isinstance(x, pd.Series):
        return x.iloc[0]
    if hasattr(x, "item"):
        return x.item()
    return x


def latest_risk_snapshot(df, vol_col="GARCH_Volatility"):
    latest = df.iloc[-1]

    # Handle date safely whether it's index, column, or Series
    if "date" in df.columns:
        date_val = latest["date"]
    else:
        date_val = latest.name

    date_val = _to_scalar(date_val)
    date_val = pd.to_datetime(date_val).strftime("%Y-%m-%d")

    output = {
        "date": date_val,
        "volatility": float(latest[vol_col]),
        "risk_level": str(_to_scalar(latest["Risk_Level"])),
        "market_regime": str(_to_scalar(latest["Market_Regime"])),
    }

    if "HMM_Regime" in df.columns:
        output["hmm_regime"] = str(_to_scalar(latest["HMM_Regime"]))

    return output