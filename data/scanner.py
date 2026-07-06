from data.market_data import get_price_data
from indicators.trend import add_trend_indicators
from indicators.momentum import add_momentum_indicators
from indicators.volatility import add_volatility_indicators
from indicators.volume import add_volume_indicators
from strategy.scoring import calculate_score


def classify_trend(row):
    if row["Close"] > row["EMA9"] > row["EMA21"] > row["EMA50"]:
        return "Bull Strong"
    elif row["Close"] > row["EMA50"]:
        return "Bull"
    elif row["Close"] < row["EMA9"] < row["EMA21"] < row["EMA50"]:
        return "Bear Strong"
    else:
        return "Mixed"


def classify_setup(row):
    if row["Close"] > row["BB_UPPER"] and row["REL_VOLUME"] > 1.5:
        return "Breakout"
    elif row["Close"] > row["EMA21"] and row["RSI"] < 65:
        return "Pullback"
    elif row["MACD"] > row["MACD_SIGNAL"] and row["RSI"] > 50:
        return "Momentum"
    elif row["Close"] > row["EMA50"]:
        return "Trend"
    else:
        return "Wait"


def classify_volume(row):
    if row["REL_VOLUME"] >= 2:
        return "Very High"
    elif row["REL_VOLUME"] >= 1.5:
        return "High"
    elif row["REL_VOLUME"] >= 1:
        return "Normal"
    else:
        return "Low"


def analyze_ticker(ticker):
    data = get_price_data(ticker, period="1y")

    if data.empty or len(data) < 200:
        return None

    data = add_trend_indicators(data)
    data = add_momentum_indicators(data)
    data = add_volatility_indicators(data)
    data = add_volume_indicators(data)
    data = data.dropna()

    if data.empty:
        return None

    latest = data.iloc[-1]
    score, reasons = calculate_score(latest)

    return {
        "Ticker": ticker,
        "Score": score,
        "Price": round(latest["Close"], 2),
        "Trend": classify_trend(latest),
        "Setup": classify_setup(latest),
        "Volume": classify_volume(latest),
        "RSI": round(latest["RSI"], 2),
        "ADX": round(latest["ADX"], 2),
        "Rel Volume": round(latest["REL_VOLUME"], 2),
        "ATR %": round((latest["ATR"] / latest["Close"]) * 100, 2),
        "Reasons": ", ".join(reasons),
    }
