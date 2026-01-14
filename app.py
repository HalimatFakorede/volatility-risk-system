import streamlit as st
import pandas as pd

from src.pipeline import run_pipeline
from src.outputs import latest_risk_snapshot

ASSET_NAMES = {
    "EEM": "Emerging Markets ETF (EEM)",
    "SPY": "S&P 500 ETF (SPY)",
    "BTC-USD": "Bitcoin (BTC-USD)",
}

st.set_page_config(page_title="Volatility & Risk Dashboard", layout="wide")
st.title("Volatility & Risk Dashboard")


# Helper: Color regimes
def color_regime(val):
    if str(val).lower() in ["stress", "crisis"]:
        return "background-color: #ffcccc"   # light red
    elif str(val).lower() == "calm":
        return "background-color: #ccffcc"   # light green
    return ""


# Sidebar Controls
st.sidebar.header("Controls")

ticker = st.sidebar.selectbox(
    "Choose Asset",
    ["EEM", "SPY", "BTC-USD"],
    index=0
)
st.caption(f"Asset: {ASSET_NAMES.get(ticker, ticker)}")

# Run pipeline
with st.spinner(f"Running risk pipeline for {ticker}..."):
    df, alerts = run_pipeline(ticker=ticker)


# DATE FILTERS

df = df.copy()
df["date"] = pd.to_datetime(df.index)
df = df.reset_index(drop=True)

if not alerts.empty:
    alerts["date"] = pd.to_datetime(alerts["date"])

st.sidebar.subheader("Date Filter")

min_date = df["date"].min()
max_date = df["date"].max()

start_date, end_date = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
df_filtered = df.loc[mask]

if not alerts.empty:
    alerts_filtered = alerts[
        (alerts["date"] >= pd.to_datetime(start_date)) &
        (alerts["date"] <= pd.to_datetime(end_date))
    ]
else:
    alerts_filtered = alerts


# Latest Risk Snapshot

st.header("Latest Risk Snapshot")

if df_filtered.empty:
    st.warning("No data available for selected date range.")
    st.stop()

latest = latest_risk_snapshot(df_filtered)

col1, col2 = st.columns(2)

with col1:
    st.subheader("GARCH Volatility (ML)")
    st.metric("Date", latest["date"])
    st.metric("Volatility", round(latest["volatility"], 5))
    st.metric("Risk Level", latest["risk_level"])
    st.metric("Market Regime", latest["market_regime"])
    if "hmm_regime" in latest:
        st.metric("HMM Regime", latest["hmm_regime"])

with col2:
    st.subheader("System Info")
    st.write("**Model:** GARCH(1,1)")
    st.write(f"**Asset:** {ASSET_NAMES.get(ticker, ticker)}")
    st.write("**Risk Engine:** Volatility-based classification")
    st.write("**Regime Detection:** Rule-based + HMM")


# Volatility History

st.header("Volatility History")

df_hist = df_filtered.copy()

# Flatten MultiIndex columns if they exist
if isinstance(df_hist.columns, pd.MultiIndex):
    df_hist.columns = df_hist.columns.get_level_values(0)

st.line_chart(
    df_hist.set_index("date")[["Volatility", "GARCH_Volatility"]]
)

# Download history
st.download_button(
    label="Download Risk History (CSV)",
    data=df_hist.to_csv(index=False),
    file_name="risk_history.csv",
    mime="text/csv"
)


# Market Regime Comparison

st.header("Market Regime Comparison")

regime_cols = ["date", "Market_Regime"]
if "HMM_Regime" in df_hist.columns:
    regime_cols.append("HMM_Regime")

regime_df = df_hist[regime_cols].tail(20)

styled_df = regime_df.style.applymap(
    color_regime,
    subset=[c for c in ["Market_Regime", "HMM_Regime"] if c in regime_df.columns]
)

st.dataframe(styled_df, use_container_width=True)


# Risk Alerts Panel

st.header("Risk Alerts")

if not alerts_filtered.empty:
    st.dataframe(alerts_filtered, use_container_width=True)

    # Download alerts
    st.download_button(
        label="Download Alerts (CSV)",
        data=alerts_filtered.to_csv(index=False),
        file_name="risk_alerts.csv",
        mime="text/csv"
    )
else:
    st.success("No risk alerts triggered.")