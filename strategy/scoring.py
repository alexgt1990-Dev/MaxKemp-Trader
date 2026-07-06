def calculate_score(row):
    score = 0
    reasons = []

    # Trend: 30 pts
    if row["Close"] > row["EMA9"]:
        score += 5
    if row["Close"] > row["EMA21"]:
        score += 5
    if row["Close"] > row["EMA50"]:
        score += 5
    if row["Close"] > row["EMA200"]:
        score += 5
    if row["EMA9"] > row["EMA21"] > row["EMA50"]:
        score += 5
        reasons.append("Strong EMA alignment")
    if row["Close"] > row["VWAP"]:
        score += 5
        reasons.append("Price above VWAP")

    # Momentum: 20 pts
    if 50 <= row["RSI"] <= 65:
        score += 10
        reasons.append("Healthy bullish RSI")
    elif 40 <= row["RSI"] < 50:
        score += 5
        reasons.append("RSI recovering")
    elif row["RSI"] > 70:
        score -= 5
        reasons.append("RSI overbought")

    if row["MACD"] > row["MACD_SIGNAL"]:
        score += 10
        reasons.append("MACD bullish")

    # Volume: 15 pts
    if row["REL_VOLUME"] >= 2:
        score += 15
        reasons.append("Very high relative volume")
    elif row["REL_VOLUME"] >= 1.5:
        score += 10
        reasons.append("High relative volume")
    elif row["REL_VOLUME"] >= 1:
        score += 5

    # Volatility / trend strength: 20 pts
    if row["ADX"] >= 30:
        score += 10
        reasons.append("Strong trend strength")
    elif row["ADX"] >= 20:
        score += 5
        reasons.append("Moderate trend strength")

    if row["Close"] > row["BB_MID"]:
        score += 5
    if row["Close"] < row["BB_UPPER"]:
        score += 5
        reasons.append("Not extended above Bollinger band")

    # Risk quality: 15 pts
    atr_pct = row["ATR"] / row["Close"]

    if 0.015 <= atr_pct <= 0.06:
        score += 15
        reasons.append("Good volatility for trading")
    elif atr_pct < 0.015:
        score += 5
        reasons.append("Low volatility")
    else:
        score -= 5
        reasons.append("High volatility risk")

    score = max(0, min(100, round(score)))

    return score, reasons
