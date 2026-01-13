import yfinance as yf

def load_market_data(ticker: str, start_date: str):
    data = yf.download(ticker, start=start_date)
    data = data.dropna()
    return data