import streamlit as st
import pandas as pd

from st_aggrid import AgGrid, GridOptionsBuilder

from config import APP_NAME, DEFAULT_TICKERS
from data.scanner import analyze_ticker
from ui.dashboard import render_dashboard

st.set_page_config(page_title=APP_NAME, layout="wide")

st.title(APP_NAME)

tab1, tab2 = st.tabs(["Dashboard", "Scanner"])

with tab1:
    render_dashboard()

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
