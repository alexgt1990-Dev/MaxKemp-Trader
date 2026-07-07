import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from st_aggrid import AgGrid, GridOptionsBuilder

from config import APP_NAME, DEFAULT_TICKERS
from data.market_data import get_price_data
from data.scanner import analyze_ticker
from indicators.trend import add_trend_indicators
from indicators.momentum import add_momentum_indicators
from indicators.volatility import add_volatility_indicators
from indicators.volume import add_volume_indicators
from strategy.mk_confidence import calculate_mk_confidence
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
            mk = calculate_mk_confidence(latest)
            plan = risk_plan(latest["Close"], latest["ATR"], capital, risk_pct)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Price", f"${latest['Close']:,.2f}")
            col2.metric("RSI", f"{latest['RSI']:.2f}")
            col3.metric("MACD", f"{latest['MACD']:.2f}")
            col4.metric("ATR", f"${latest['ATR']:.2f}")
            col5.metric("MK Score", f"{mk.total}/100")

            st.subheader("MK Confidence™")
            st.progress(mk.total / 100)
            st.write(f"**{'★' * mk.stars}**")
            st.write(f"**{mk.confidence}**")

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

            st.subheader("Score Breakdown")

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Trend", f"{mk.trend}/30")
            c2.metric("Momentum", f"{mk.momentum}/20")
            c3.metric("Volume", f"{mk.volume}/15")
            c4.metric("Volatility", f"{mk.volatility}/10")
            c5.metric("Risk", f"{mk.risk}/15")
            c6.metric("Setup", f"{mk.setup}/10")

            st.subheader("Trade Read")

            if mk.reasons:
                for reason in mk.reasons:
                    st.write("•", reason)
            else:
                st.write("No strong reasons detected.")

            st.subheader("Risk Plan")

            r1, r2, r3, r4, r5, r6 = st.columns(6)
            r1.metric("Entry", f"${latest['Close']:,.2f}")
            r2.metric("Stop", f"${plan['stop_loss']:,.2f}")
            r3.metric("TP1", f"${plan['take_profit_1']:,.2f}")
            r4.metric("TP2", f"${plan['take_profit_2']:,.2f}")
            r5.metric("TP3", f"${plan['take_profit_3']:,.2f}")
            r6.metric("Shares", f"{plan['shares']:.0f}")

            st.write(f"Risk Amount: **${plan['risk_amount']:,.2f}**")
            st.write(f"Risk/Reward TP1: **{plan['rr1']:.2f}x**")
            st.write(f"Risk/Reward TP2: **{plan['rr2']:.2f}x**")
            st.write(f"Risk/Reward TP3: **{plan['rr3']:.2f}x**")

with tab2:
    st.subheader("Market Scanner")

    tickers_text = st.text_area(
        "Tickers separated by comma",
        ",".join(DEFAULT_TICKERS)
    )

    tickers = [ticker.strip().upper() for ticker in tickers_text.split(",") if ticker.strip()]

    if st.button("Run Scanner"):
        results = []

        with st.spinner("Scanning..."):
            for ticker in tickers:
                result = analyze_ticker(ticker)
                if result:
                    results.append(result)

        if results:
            df = pd.DataFrame(results)

            df = df.sort_values(
                by=["MK Score", "Rel Volume"],
                ascending=[False, False]
            )

            display_df = df[[
                "Ticker",
                "Stars",
                "MK Score",
                "Confidence",
                "Price",
                "Trend",
                "Setup",
                "Volume",
                "RSI",
                "ADX",
                "Rel Volume",
                "ATR %",
                "Reasons"
            ]].copy()

            display_df["ATR %"] = display_df["ATR %"].map(lambda x: f"{x:.2f}%")
            display_df["RSI"] = display_df["RSI"].map(lambda x: f"{x:.2f}")
            display_df["ADX"] = display_df["ADX"].map(lambda x: f"{x:.2f}")
            display_df["Rel Volume"] = display_df["Rel Volume"].map(lambda x: f"{x:.2f}x")

            gb = GridOptionsBuilder.from_dataframe(display_df)

            gb.configure_default_column(
                filter=True,
                sortable=True,
                resizable=True,
                wrapText=True,
                autoHeight=True
            )

            gb.configure_column("Ticker", pinned="left", width=100)
            gb.configure_column("Stars", width=110)
            gb.configure_column("MK Score", width=120)
            gb.configure_column("Confidence", width=140)

            gb.configure_column(
                "Price",
                width=120,
                type=["numericColumn"],
                valueFormatter="x.toLocaleString('en-US',{style:'currency',currency:'USD'})"
            )

            gb.configure_column("Trend", width=150)
            gb.configure_column("Setup", width=130)
            gb.configure_column("Volume", width=140)
            gb.configure_column("RSI", width=90)
            gb.configure_column("ADX", width=90)
            gb.configure_column("Rel Volume", width=120)
            gb.configure_column("ATR %", width=100)
            gb.configure_column("Reasons", width=700, wrapText=True, autoHeight=True)

            grid_options = gb.build()

            AgGrid(
                display_df,
                gridOptions=grid_options,
                height=540,
                fit_columns_on_grid_load=False,
                theme="streamlit"
            )

        else:
            st.warning("No valid results.")
