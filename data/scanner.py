from data.market_data import get_price_data
from indicators.trend import add_trend_indicators
from indicators.momentum import add_momentum_indicators
from indicators.volatility import add_volatility_indicators
from indicators.volume import add_volume_indicators
from strategy.scoring import calculate_score

def analyze_ticker(ticker):
    data = get_price_data(ticker)

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
        "Price": round(latest["Close"], 2),
        "RSI": round(latest["RSI"], 2),
        "MACD": round(latest["MACD"], 2),
        "ATR": round(latest["ATR"], 2),
        "Rel Volume": round(latest["REL_VOLUME"], 2),
        "Score": score,
        "Reasons": ", ".join(reasons),
    }
