def calculate_score(row):
    score = 0
    reasons = []

    if row["Close"] > row["SMA20"]:
        score += 1
        reasons.append("Price above SMA20")
    else:
        score -= 1
        reasons.append("Price below SMA20")

    if row["Close"] > row["SMA50"]:
        score += 1
        reasons.append("Price above SMA50")
    else:
        score -= 1
        reasons.append("Price below SMA50")

    if row["Close"] > row["SMA200"]:
        score += 1
        reasons.append("Price above SMA200")
    else:
        score -= 1
        reasons.append("Price below SMA200")

    if row["MACD"] > row["MACD_SIGNAL"]:
        score += 1
        reasons.append("MACD bullish")
    else:
        score -= 1
        reasons.append("MACD bearish")

    if 45 <= row["RSI"] <= 65:
        score += 1
        reasons.append("RSI healthy")
    elif row["RSI"] > 70:
        score -= 1
        reasons.append("RSI overbought")
    elif row["RSI"] < 30:
        score += 1
        reasons.append("RSI oversold bounce zone")

    if row["REL_VOLUME"] > 1.5:
        score += 1
        reasons.append("High relative volume")

    return score, reasons
