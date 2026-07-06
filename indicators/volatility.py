import pandas as pd

def add_volatility_indicators(data):
    high_low = data["High"] - data["Low"]
    high_close = abs(data["High"] - data["Close"].shift())
    low_close = abs(data["Low"] - data["Close"].shift())

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    data["ATR"] = tr.rolling(14).mean()

    data["BB_MID"] = data["Close"].rolling(20).mean()
    data["BB_STD"] = data["Close"].rolling(20).std()
    data["BB_UPPER"] = data["BB_MID"] + 2 * data["BB_STD"]
    data["BB_LOWER"] = data["BB_MID"] - 2 * data["BB_STD"]

    up_move = data["High"].diff()
    down_move = -data["Low"].diff()

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

    plus_di = 100 * (plus_dm.rolling(14).mean() / data["ATR"])
    minus_di = 100 * (minus_dm.rolling(14).mean() / data["ATR"])

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    data["ADX"] = dx.rolling(14).mean()

    return data
