from dataclasses import dataclass


@dataclass
class MKScore:

    total: int

    trend: int

    momentum: int

    volume: int

    volatility: int

    risk: int

    setup: int

    confidence: str

    stars: int

    reasons: list


def calculate_mk_confidence(row):

    trend = 0
    momentum = 0
    volume = 0
    volatility = 0
    risk = 0
    setup = 0

    reasons = []

    ##################################
    # TREND (30)
    ##################################

    if row["Close"] > row["EMA9"]:
        trend += 5

    if row["Close"] > row["EMA21"]:
        trend += 5

    if row["Close"] > row["EMA50"]:
        trend += 5

    if row["Close"] > row["EMA200"]:
        trend += 5

    if row["EMA9"] > row["EMA21"] > row["EMA50"]:
        trend += 5
        reasons.append("Strong EMA Alignment")

    if row["Close"] > row["VWAP"]:
        trend += 5
        reasons.append("Trading Above VWAP")

    ##################################
    # MOMENTUM (20)
    ##################################

    if row["MACD"] > row["MACD_SIGNAL"]:
        momentum += 10
        reasons.append("Bullish MACD")

    if 50 <= row["RSI"] <= 65:
        momentum += 10
        reasons.append("Healthy RSI")

    ##################################
    # VOLUME (15)
    ##################################

    if row["REL_VOLUME"] >= 2:
        volume = 15
        reasons.append("Very High Relative Volume")

    elif row["REL_VOLUME"] >= 1.5:
        volume = 10
        reasons.append("High Relative Volume")

    elif row["REL_VOLUME"] >= 1:
        volume = 5

    ##################################
    # VOLATILITY (10)
    ##################################

    atr_pct = row["ATR"] / row["Close"]

    if 0.02 <= atr_pct <= 0.05:
        volatility = 10
        reasons.append("Healthy Volatility")

    elif atr_pct < 0.02:
        volatility = 6

    else:
        volatility = 3

    ##################################
    # RISK (15)
    ##################################

    risk = 15

    ##################################
    # SETUP (10)
    ##################################

    if row["ADX"] >= 30:
        setup += 5
        reasons.append("Strong Trend")

    if row["Close"] > row["BB_MID"]:
        setup += 5
        reasons.append("Above Bollinger Mid")

    ##################################

    total = trend + momentum + volume + volatility + risk + setup

    total = min(100, total)

    ##################################

    if total >= 90:
        confidence = "STRONG BUY"
        stars = 5

    elif total >= 80:
        confidence = "BUY"
        stars = 4

    elif total >= 65:
        confidence = "WATCH"
        stars = 3

    elif total >= 45:
        confidence = "NEUTRAL"
        stars = 2

    else:
        confidence = "AVOID"
        stars = 1

    return MKScore(
        total,
        trend,
        momentum,
        volume,
        volatility,
        risk,
        setup,
        confidence,
        stars,
        reasons,
    )
