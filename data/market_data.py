import yfinance as yf

def get_price_data(ticker, period="1y", interval="1d"):
    data = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
    return data.dropna()
