import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

from data.data_engine import DataEngine
from data.options_engine import get_expirations, get_option_chain, enrich_options


def render_options_lab():
    st.subheader("Options Lab")

    ticker = st.text_input("Options Ticker", "NVDA").upper()

    engine = DataEngine()
    current_price = engine.get_current_price(ticker)

    if current_price is None:
        st.error("No price data found.")
        return

    st.write(f"Current Price: **${current_price:,.2f}**")

    expirations = get_expirations(ticker)

    if not expirations:
        st.warning("No options expirations found.")
        return

    expiration = st.selectbox("Expiration", expirations)

    calls, puts = get_option_chain(ticker, expiration)

    if calls.empty and puts.empty:
        st.warning("No option chain available.")
        return

    calls = enrich_options(calls, current_price, "CALL", expiration)
    puts = enrich_options(puts, current_price, "PUT", expiration)

    tab_calls, tab_puts = st.tabs(["Calls", "Puts"])

    with tab_calls:
        render_options_table(calls, "CALL")

    with tab_puts:
        render_options_table(puts, "PUT")


def render_options_table(df, option_type):
    if df.empty:
        st.warning(f"No {option_type} data.")
        return

    columns = [
        "contractSymbol",
        "strike",
        "lastPrice",
        "bid",
        "ask",
        "volume",
        "openInterest",
        "impliedVolatility",
        "Break Even",
        "MK Option Score",
        "Rating",
        "Reasons"
    ]

    display_df = df[[col for col in columns if col in df.columns]].copy()

    display_df = display_df.rename(columns={
        "contractSymbol": "Contract",
        "strike": "Strike",
        "lastPrice": "Last",
        "bid": "Bid",
        "ask": "Ask",
        "volume": "Volume",
        "openInterest": "Open Interest",
        "impliedVolatility": "IV"
    })

    if "IV" in display_df.columns:
        display_df["IV"] = display_df["IV"].map(lambda x: f"{x * 100:.2f}%")

    gb = GridOptionsBuilder.from_dataframe(display_df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        wrapText=True,
        autoHeight=True
    )

    for col in ["Strike", "Last", "Bid", "Ask", "Break Even"]:
        if col in display_df.columns:
            gb.configure_column(
                col,
                width=110,
                type=["numericColumn"],
                valueFormatter="x.toLocaleString('en-US',{style:'currency',currency:'USD'})"
            )

    gb.configure_column("Contract", pinned="left", width=220)
    gb.configure_column("MK Option Score", width=150)
    gb.configure_column("Rating", width=120)
    gb.configure_column("Reasons", width=500, wrapText=True, autoHeight=True)

    grid_options = gb.build()

    AgGrid(
        display_df,
        gridOptions=grid_options,
        height=540,
        fit_columns_on_grid_load=False,
        theme="streamlit"
    )
