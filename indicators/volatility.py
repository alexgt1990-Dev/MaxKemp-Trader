import pandas as pd

def add_volatility_indicators(data):
    high_low = data["High"] - data["Low"]
    high_close = abs(data["High"] - data["Close"].shift())
    low_close = abs(data["Low"] - data["Close"].shift())

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    data["ATR"] = tr.rolling(14).mean()

    data["BB_MID"] = data["Close"].rolling(20).mean()
    data["BB_UPPER"] = data["BB_MID"] + 2 * data["Close"].rolling(20).std()
    data["BB_LOWER"] = data["BB_MID"] - 2 * data["Close"].rolling(20).std()

    return data
