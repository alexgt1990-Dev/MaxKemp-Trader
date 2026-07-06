import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

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
            col1.metric("Price", f"${latest['Close']:,.2f}")
            col2.metric("RSI", f"{latest['RSI']:.2f}")
            col3.metric("MACD", f"{latest['MACD']:.2f}")
            col4.metric("ATR", f"${latest['ATR']:.2f}")
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
                st.success("Bias: 🟢 LONG FUERTE")
            elif score >= 65:
                st.info("Bias: 🔵 LONG MODERADO")
            elif score <= 35:
                st.error("Bias: 🔴 EVITAR / SHORT")
            else:
                st.warning("Bias: 🟡 NEUTRAL")

            st.subheader("Trade Read")

            if reasons:
                for r in reasons:
                    st.write("•", r)
            else:
                st.write("No strong reasons detected.")

            st.subheader("Risk Plan")

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Entry", f"${latest['Close']:,.2f}")
            c2.metric("Stop", f"${plan['stop_loss']:,.2f}")
            c3.metric("TP1", f"${plan['take_profit_1']:,.2f}")
            c4.metric("TP2", f"${plan['take_profit_2']:,.2f}")
            c5.metric("TP3", f"${plan['take_profit_3']:,.2f}")
            c6.metric("Shares", f"{plan['shares']:.0f}")

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

            display_df = df[[
                "Ticker",
                "Score",
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

            display_df["Price"] = display_df["Price"].map(lambda x: f"${x:,.2f}")
            display_df["ATR %"] = display_df["ATR %"].map(lambda x: f"{x:.2f}%")
            display_df["RSI"] = display_df["RSI"].map(lambda x: f"{x:.2f}")
            display_df["ADX"] = display_df["ADX"].map(lambda x: f"{x:.2f}")
            display_df["Rel Volume"] = display_df["Rel Volume"].map(lambda x: f"{x:.2f}x")

            def score_icon(score):
                if score >= 80:
                    return f"🟢 {score}"
                elif score >= 65:
                    return f"🔵 {score}"
                elif score <= 35:
                    return f"🔴 {score}"
                else:
                    return f"🟡 {score}"

            display_df["Score"] = display_df["Score"].map(score_icon)

            def trend_icon(trend):
                if "Bull Strong" in trend:
                    return "🟢 Bull Strong"
                elif trend == "Bull":
                    return "🟢 Bull"
                elif "Bear" in trend:
                    return "🔴 Bear"
                else:
                    return "🟡 Mixed"

            display_df["Trend"] = display_df["Trend"].map(trend_icon)

            def volume_icon(volume):
                if volume == "Very High":
                    return "🔥 Very High"
                elif volume == "High":
                    return "🟢 High"
                elif volume == "Normal":
                    return "🟡 Normal"
                else:
                    return "⚪ Low"

            display_df["Volume"] = display_df["Volume"].map(volume_icon)

            gb = GridOptionsBuilder.from_dataframe(display_df)
            gb.configure_default_column(
                filter=True,
                sortable=True,
                resizable=True,
                autoHeight=True,
                wrapText=True
            )

            gb.configure_column("Ticker", pinned="left", width=100)
            gb.configure_column("Score", width=110)
            gb.configure_column("Price", width=110)
            gb.configure_column("Trend", width=150)
            gb.configure_column("Setup", width=130)
            gb.configure_column("Volume", width=140)
            gb.configure_column("RSI", width=90)
            gb.configure_column("ADX", width=90)
            gb.configure_column("Rel Volume", width=120)
            gb.configure_column("ATR %", width=100)
            gb.configure_column("Reasons", width=600, wrapText=True, autoHeight=True)

            grid_options = gb.build()

            AgGrid(
                display_df,
                gridOptions=grid_options,
                height=520,
                fit_columns_on_grid_load=False,
                allow_unsafe_jscode=True,
                theme="streamlit"
            )

        else:
            st.warning("No valid results.")
