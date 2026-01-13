def compute_returns(df):
    df["Return"] = df["Close"].pct_change()
    return df

def compute_volatility(df, window=20):
    df["Volatility"] = df["Return"].rolling(window).std()
    return df