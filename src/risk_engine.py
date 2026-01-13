import numpy as np
from src.config import HIGH_RISK_Q, MID_RISK_Q

def assign_risk_levels(df, vol_col="Volatility"):
    vol_high = df[vol_col].quantile(HIGH_RISK_Q)
    vol_mid = df[vol_col].quantile(MID_RISK_Q)

    df["Risk_Level"] = np.where(
        df[vol_col] >= vol_high, "High",
        np.where(df[vol_col] >= vol_mid, "Medium", "Low")
    )
    return df