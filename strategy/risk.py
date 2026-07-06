def risk_plan(price, atr, capital, risk_pct):
    risk_amount = capital * (risk_pct / 100)

    stop_loss = price - (atr * 1.5)
    take_profit_1 = price + (atr * 2)
    take_profit_2 = price + (atr * 3)
    take_profit_3 = price + (atr * 4)

    risk_per_share = price - stop_loss
    shares = risk_amount / risk_per_share if risk_per_share > 0 else 0

    rr1 = (take_profit_1 - price) / risk_per_share if risk_per_share > 0 else 0
    rr2 = (take_profit_2 - price) / risk_per_share if risk_per_share > 0 else 0
    rr3 = (take_profit_3 - price) / risk_per_share if risk_per_share > 0 else 0

    return {
        "risk_amount": risk_amount,
        "stop_loss": stop_loss,
        "take_profit_1": take_profit_1,
        "take_profit_2": take_profit_2,
        "take_profit_3": take_profit_3,
        "shares": shares,
        "rr1": rr1,
        "rr2": rr2,
        "rr3": rr3,
    }
