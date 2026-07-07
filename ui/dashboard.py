import streamlit as st

from data.market_data import get_price_data
from indicators.trend import add_trend_indicators
from indicators.momentum import add_momentum_indicators
from indicators.volatility import add_volatility_indicators
from indicators.volume import add_volume_indicators
from strategy.mk_confidence import calculate_mk_confidence
from strategy.risk import risk_plan
from strategy.ai_summary import generate_ai_summary

from ui.gauge import render_mk_gauge
from ui.cards import render_score_cards, render_card
from ui.charts import render_price_chart
from ui.trade_plan import render_trade_plan


def render_dashboard():
    ticker = st.text_input("Ticker", "NVDA").upper()
    period = st.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)
    capital = st.number_input("Capital", value=5000.0)
    risk_pct = st.slider("Risk %", 1, 10, 2)

    data = get_price_data(ticker, period=period)

    if data.empty:
        st.error("No data found.")
        return

    data = add_trend_indicators(data)
    data = add_momentum_indicators(data)
    data = add_volatility_indicators(data)
    data = add_volume_indicators(data)
    data = data.dropna()

    if data.empty:
        st.error("Not enough data to calculate indicators.")
        return

    latest = data.iloc[-1]
    mk = calculate_mk_confidence(latest)
    plan = risk_plan(latest["Close"], latest["ATR"], capital, risk_pct)

    top1, top2, top3, top4 = st.columns(4)

    with top1:
        render_card("Ticker", ticker, "Selected asset")
    with top2:
        render_card("Price", f"${latest['Close']:,.2f}", "Last close")
    with top3:
        render_card("ATR", f"${latest['ATR']:,.2f}", "Volatility")
    with top4:
        render_card("Decision", mk.confidence, "MK Signal")

    st.subheader("MK Confidence™")

    left, right = st.columns([0.9, 2.1])

    with left:
        render_mk_gauge(mk)

    with right:
        st.subheader("AI Summary")
        summary = generate_ai_summary(ticker, latest, mk, plan)
        st.markdown(summary)

    st.subheader("Score Breakdown")
    render_score_cards(mk)

    st.subheader("Chart")
    render_price_chart(data)

    render_trade_plan(latest, plan)
