from src.data_loader import load_market_data
from src.features import compute_returns, compute_volatility
from src.risk_engine import assign_risk_levels
from src.regime import detect_market_regime
from src.hmm_regime import detect_hmm_regime
from src.signals import generate_risk_alerts
from src.ml import compute_garch_volatility


def run_pipeline(ticker="EEM", start_date="2010-01-01"):
    # 1. Load data
    df = load_market_data(ticker, start_date)

    # 2. Feature engineering
    df = compute_returns(df)
    df = compute_volatility(df)

    # 3. ML volatility (GARCH)
    df["GARCH_Volatility"] = compute_garch_volatility(df["Return"])

    # 4. Clean
    df = df.dropna()

    # 5. Risk levels (based on GARCH volatility)
    df = assign_risk_levels(df, vol_col="GARCH_Volatility")

    # 6. Regime detection
    df = detect_market_regime(df)   # Rule-based regime
    df = detect_hmm_regime(df)       # ML-based regime

    # 7. Alerts
    alerts = generate_risk_alerts(df)

    return df, alerts