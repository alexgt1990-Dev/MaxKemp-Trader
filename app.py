import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from config import APP_NAME, DEFAULT_TICKERS
from data.market_data import get_price_data
from data.scanner import analyze_ticker
from indicators.trend import add_trend_indicators
from indicators.momentum import add_momentum_indicators
from indicators.volatility import add_volatility_indicators
from indicators.volume import add_volume_indicators
from strategy.scoring import calculate_score
from strategy.risk import risk_plan

st.set_page_config(page_title=APP_NAME, layout="wide")

st.title(APP_NAME)

tab1, tab2 = st.tabs(["Dashboard", "Scanner"])

with tab1:
    ticker = st.text_input("Ticker", "NVDA").upper()
    period = st.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)
    capital = st.number_input("Capital", value=5000.0)
    risk_pct = st.slider("Risk %", 1, 10, 2)

    data = get_price_data(ticker, period=period)

    if data.empty:
        st.error("No data found.")
    else:
        data = add_trend_indicators(data)
        data = add_momentum_indicators(data)
        data = add_volatility_indicators(data)
        data = add_volume_indicators(data)
        data = data.dropna()

        if data.empty:
            st.error("Not enough data to calculate indicators.")
        else:
            latest = data.iloc[-1]
            score, reasons = calculate_score(latest)
            plan = risk_plan(latest["Close"], latest["ATR"], capital, risk_pct)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Price", f"${latest['Close']:.2f}")
            col2.metric("RSI", f"{latest['RSI']:.2f}")
            col3.metric("MACD", f"{latest['MACD']:.2f}")
            col4.metric("ATR", f"{latest['ATR']:.2f}")
            col5.metric("Score", f"{score}/100")

            fig = go.Figure()

            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="Price"
            ))

            fig.add_trace(go.Scatter(x=data.index, y=data["SMA20"], name="SMA20"))
            fig.add_trace(go.Scatter(x=data.index, y=data["SMA50"], name="SMA50"))
            fig.add_trace(go.Scatter(x=data.index, y=data["SMA200"], name="SMA200"))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA9"], name="EMA9"))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA21"], name="EMA21"))

            if "VWAP" in data.columns:
                fig.add_trace(go.Scatter(x=data.index, y=data["VWAP"], name="VWAP"))

            if "BB_UPPER" in data.columns:
                fig.add_trace(go.Scatter(x=data.index, y=data["BB_UPPER"], name="BB Upper"))

            if "BB_LOWER" in data.columns:
                fig.add_trace(go.Scatter(x=data.index, y=data["BB_LOWER"], name="BB Lower"))

            fig.update_layout(height=650, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            if score >= 80:
                st.success("Bias: LONG FUERTE")
            elif score >= 65:
                st.info("Bias: LONG MODERADO")
            elif score <= 35:
                st.error("Bias: EVITAR / SHORT")
            else:
                st.warning("Bias: NEUTRAL")

            st.subheader("Trade Read")

            if reasons:
                for r in reasons:
                    st.write("•", r)
            else:
                st.write("No strong reasons detected.")

            st.subheader("Risk Plan")

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Entry", f"${latest['Close']:.2f}")
            c2.metric("Stop", f"${plan['stop_loss']:.2f}")
            c3.metric("TP1", f"${plan['take_profit_1']:.2f}")
            c4.metric("TP2", f"${plan['take_profit_2']:.2f}")
            c5.metric("TP3", f"${plan['take_profit_3']:.2f}")
            c6.metric("Shares", f"{plan['shares']:.0f}")

            st.write(f"Risk/Reward TP1: **{plan['rr1']:.2f}**")
            st.write(f"Risk/Reward TP2: **{plan['rr2']:.2f}**")
            st.write(f"Risk/Reward TP3: **{plan['rr3']:.2f}**")

with tab2:
    st.subheader("Market Scanner")

    tickers_text = st.text_area(
        "Tickers separated by comma",
        ",".join(DEFAULT_TICKERS)
    )

    tickers = [t.strip().upper() for t in tickers_text.split(",") if t.strip()]

    if st.button("Run Scanner"):
        results = []

        with st.spinner("Scanning..."):
            for ticker in tickers:
                result = analyze_ticker(ticker)
                if result:
                    results.append(result)

        if results:
            df = pd.DataFrame(results)
            df = df.sort_values(by=["Score", "Rel Volume"], ascending=False)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.warning("No valid results.")
            
