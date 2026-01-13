import pandas as pd

def generate_risk_alerts(df, vol_spike_threshold=0.5):
    """
    Generates alerts for:
    - Risk level changes
    - Market regime switches
    - Volatility spikes
    """

    df = df.copy()

    # Create lag features
    df["Prev_Risk"] = df["Risk_Level"].shift()
    df["Prev_Regime"] = df["Market_Regime"].shift()
    df["Prev_Volatility"] = df["Volatility"].shift()

    alerts = []

    for idx, row in df.iterrows():

        # --- Safely extract scalars ---
        def to_scalar(x):
            if hasattr(x, "iloc"):
                return x.iloc[0]
            return x

        risk = to_scalar(row["Risk_Level"])
        prev_risk = to_scalar(row["Prev_Risk"])

        regime = to_scalar(row["Market_Regime"])
        prev_regime = to_scalar(row["Prev_Regime"])

        vol = to_scalar(row["Volatility"])
        prev_vol = to_scalar(row["Prev_Volatility"])

        messages = []

        # 1️⃣ Risk level change
        if pd.notna(prev_risk) and risk != prev_risk:
            messages.append(f"Risk changed: {prev_risk} → {risk}")

        # 2️⃣ Regime change
        if pd.notna(prev_regime) and regime != prev_regime:
            messages.append(f"Regime switched: {prev_regime} → {regime}")

        # 3️⃣ Volatility spike
        if pd.notna(prev_vol) and prev_vol > 0:
            pct_change = (vol - prev_vol) / prev_vol
            if pct_change >= vol_spike_threshold:
                messages.append(f"Volatility spike: {pct_change:.1%}")

        # Save alert if anything triggered
        if messages:
            alerts.append({
                "date": idx,
                "risk_level": risk,
                "market_regime": regime,
                "volatility": vol,
                "alert": " | ".join(messages)
            })

    return pd.DataFrame(alerts)