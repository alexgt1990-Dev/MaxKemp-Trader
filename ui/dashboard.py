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
    st.markdown("### Control Panel")

    c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1.2, 1.2, 1])

    with c1:
        ticker = st.text_input("Ticker", "NVDA").upper()

    with c2:
        period = st.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)

    with c3:
        capital = st.number_input("Capital", value=5000.0)

    with c4:
        risk_pct = st.slider("Risk %", 1, 10, 2)

    with c5:
        st.write("")
        st.write("")
        analyze = st.button("🚀 Analyze", use_container_width=True)

    if not analyze:
        st.info("Set your inputs and click Analyze.")
        return

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
    previous = data.iloc[-2] if len(data) > 1 else latest

    mk = calculate_mk_confidence(latest)
    plan = risk_plan(latest["Close"], latest["ATR"], capital, risk_pct)

    price = latest["Close"]
    prev_close = previous["Close"]
    change = price - prev_close
    change_pct = (change / prev_close) * 100 if prev_close else 0

    rel_volume = latest["REL_VOLUME"]
    volume = latest["Volume"]

    st.markdown("### Market Snapshot")

    s1, s2, s3, s4, s5, s6 = st.columns(6)

    with s1:
        render_card("Price", f"${price:,.2f}", ticker)

    with s2:
        direction = "▲" if change >= 0 else "▼"
        render_card("Change", f"{direction} {change_pct:.2f}%", f"${change:,.2f}")

    with s3:
        render_card("ATR", f"${latest['ATR']:,.2f}", "Volatility")

    with s4:
        render_card("MK Score", f"{mk.total}/100", mk.confidence)

    with s5:
        render_card("Volume", f"{volume:,.0f}", f"{rel_volume:.2f}x Rel Vol")

    with s6:
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
