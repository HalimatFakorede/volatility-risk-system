def detect_market_regime(df, stress_threshold=0.9):
    threshold = df["Volatility"].quantile(stress_threshold)
    
    df["Market_Regime"] = df["Volatility"].apply(
        lambda x: "Crisis" if x >= threshold else "Calm"
    )
    return df