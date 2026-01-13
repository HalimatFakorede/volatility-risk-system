def _to_scalar(x):
    if hasattr(x, "item"):
        return x.item()
    return x

def latest_risk_snapshot(df, vol_col="Volatility"):
    latest = df.iloc[-1]

    output = {
        "date": latest.name.strftime("%Y-%m-%d"),
        "volatility": float(latest[vol_col].iloc[0]) if hasattr(latest[vol_col], "iloc") else float(latest[vol_col]),
        "risk_level": str(_to_scalar(latest["Risk_Level"])),
        "market_regime": str(_to_scalar(latest["Market_Regime"])),
    }

    if "HMM_Regime" in df.columns:
        output["hmm_regime"] = str(_to_scalar(latest["HMM_Regime"]))

    return output