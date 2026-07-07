def generate_ai_summary(ticker, latest, mk, plan):
    trend_text = "bullish" if latest["Close"] > latest["EMA50"] else "weak or mixed"
    ema_text = "above the major moving averages" if latest["Close"] > latest["EMA21"] else "below short-term momentum levels"
    macd_text = "positive" if latest["MACD"] > latest["MACD_SIGNAL"] else "negative"
    volume_text = "above average" if latest["REL_VOLUME"] >= 1 else "below average"
    rr_text = "favorable" if plan["rr2"] >= 2 else "limited"

    return f"""
**Overall Assessment:** {mk.confidence}

{ticker} is currently showing a **{trend_text}** technical structure. Price is trading **{ema_text}**, while MACD momentum is **{macd_text}**.

Relative volume is **{volume_text}**, suggesting {'stronger participation' if latest["REL_VOLUME"] >= 1 else 'limited participation'} compared with its recent average.

The current trade plan offers a **{rr_text}** risk/reward profile, with TP2 offering approximately **{plan["rr2"]:.2f}x** reward versus risk.

**Preferred Action:** {'Look for a controlled entry or pullback setup.' if mk.total >= 65 else 'Wait for stronger confirmation before entering.'}
"""
