import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Volatility & Risk Dashboard", layout="wide")
st.title("Emerging Markets Risk Dashboard")

# Helper: Color regimes
def color_regime(val):
    if str(val).lower() in ["stress", "crisis"]:
        return "background-color: #ffcccc"   # light red
    elif str(val).lower() == "calm":
        return "background-color: #ccffcc"   # light green
    return ""

# Latest Risk Snapshot
st.header("Latest Risk Snapshot")

latest = requests.get(f"{API_URL}/risk/latest").json()
latest_garch = requests.get(f"{API_URL}/risk/latest-garch").json()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Standard Volatility")
    st.metric("Date", latest["date"])
    st.metric("Volatility", round(latest["volatility"], 5))
    st.metric("Risk Level", latest["risk_level"])
    st.metric("Market Regime", latest["market_regime"])
    st.metric("HMM Regime", latest["hmm_regime"])

with col2:
    st.subheader("GARCH Volatility")
    st.metric("Date", latest_garch["date"])
    st.metric("Volatility", round(latest_garch["volatility"], 5))
    st.metric("Risk Level", latest_garch["risk_level"])
    st.metric("Market Regime", latest_garch["market_regime"])
    st.metric("HMM Regime", latest_garch["hmm_regime"])

# Volatility History
st.header("Volatility History")

history = requests.get(f"{API_URL}/risk/history").json()
df_hist = pd.DataFrame(history)
df_hist["date"] = pd.to_datetime(df_hist["date"])

st.line_chart(
    df_hist.set_index("date")[["volatility", "garch_volatility"]]
)

# Market Regime Comparison (Colored)
st.header("Market Regime Comparison")

regime_df = df_hist[["date", "market_regime", "hmm_regime"]].tail(20)

styled_df = regime_df.style.applymap(
    color_regime,
    subset=["market_regime", "hmm_regime"]
)

st.dataframe(styled_df, use_container_width=True)

# Risk Alerts Panel
st.header("Risk Alerts")

alerts = requests.get(f"{API_URL}/alerts").json()
df_alerts = pd.DataFrame(alerts)

st.dataframe(df_alerts, use_container_width=True)