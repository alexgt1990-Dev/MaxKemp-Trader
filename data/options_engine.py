import yfinance as yf
import pandas as pd
from datetime import datetime


def get_expirations(ticker):
    try:
        stock = yf.Ticker(ticker)
        return list(stock.options)
    except Exception:
        return []


def get_option_chain(ticker, expiration):
    try:
        stock = yf.Ticker(ticker)
        chain = stock.option_chain(expiration)

        calls = chain.calls.copy()
        puts = chain.puts.copy()

        calls["Type"] = "CALL"
        puts["Type"] = "PUT"

        calls["Expiration"] = expiration
        puts["Expiration"] = expiration

        return calls, puts

    except Exception:
        return pd.DataFrame(), pd.DataFrame()


def calculate_days_to_expiration(expiration):
    try:
        exp_date = datetime.strptime(expiration, "%Y-%m-%d")
        today = datetime.today()
        return max((exp_date - today).days, 0)
    except Exception:
        return 0


def calculate_option_score(row, current_price, option_type, expiration):
    score = 0
    reasons = []

    bid = row.get("bid", 0)
    ask = row.get("ask", 0)
    volume = row.get("volume", 0)
    open_interest = row.get("openInterest", 0)
    iv = row.get("impliedVolatility", 0)
    strike = row.get("strike", 0)

    mid = (bid + ask) / 2 if bid and ask else row.get("lastPrice", 0)
    spread = ask - bid if ask and bid else 0
    spread_pct = spread / mid if mid > 0 else 1

    # Liquidity: 20 pts
    if spread_pct <= 0.05:
        score += 20
        reasons.append("Tight spread")
    elif spread_pct <= 0.10:
        score += 15
        reasons.append("Good spread")
    elif spread_pct <= 0.20:
        score += 8
        reasons.append("Acceptable spread")

    # Open Interest: 20 pts
    if open_interest >= 5000:
        score += 20
        reasons.append("Excellent open interest")
    elif open_interest >= 1000:
        score += 15
        reasons.append("Good open interest")
    elif open_interest >= 250:
        score += 8
        reasons.append("Some open interest")

    # Volume: 15 pts
    if volume >= 1000:
        score += 15
        reasons.append("High volume")
    elif volume >= 250:
        score += 10
        reasons.append("Good volume")
    elif volume >= 50:
        score += 5
        reasons.append("Some volume")

    # Strike distance: 15 pts
    if current_price > 0 and strike > 0:
        distance_pct = abs(strike - current_price) / current_price

        if distance_pct <= 0.05:
            score += 15
            reasons.append("Strike near current price")
        elif distance_pct <= 0.10:
            score += 10
            reasons.append("Moderate strike distance")
        elif distance_pct <= 0.20:
            score += 5
            reasons.append("Farther strike")

    # IV: 10 pts
    if 0.20 <= iv <= 0.60:
        score += 10
        reasons.append("Healthy IV")
    elif 0.10 <= iv < 0.20:
        score += 6
        reasons.append("Low IV")
    elif iv > 0.60:
        score += 4
        reasons.append("High IV risk")

    # Time: 20 pts
    days = calculate_days_to_expiration(expiration)

    if 45 <= days <= 180:
        score += 20
        reasons.append("Good expiration window")
    elif 21 <= days < 45:
        score += 12
        reasons.append("Shorter expiration")
    elif days > 180:
        score += 10
        reasons.append("Long dated option")

    score = max(0, min(100, round(score)))

    if score >= 90:
        rating = "Excellent"
    elif score >= 80:
        rating = "Good"
    elif score >= 65:
        rating = "Watch"
    else:
        rating = "Avoid"

    return score, rating, ", ".join(reasons)


def enrich_options(df, current_price, option_type, expiration):
    if df.empty:
        return df

    df = df.copy()

    scores = df.apply(
        lambda row: calculate_option_score(row, current_price, option_type, expiration),
        axis=1
    )

    df["MK Option Score"] = [x[0] for x in scores]
    df["Rating"] = [x[1] for x in scores]
    df["Reasons"] = [x[2] for x in scores]

    df["Break Even"] = df.apply(
        lambda row: row["strike"] + row["ask"] if option_type == "CALL" else row["strike"] - row["ask"],
        axis=1
    )

    return df.sort_values(by="MK Option Score", ascending=False)
