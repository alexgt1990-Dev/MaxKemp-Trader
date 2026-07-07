import plotly.graph_objects as go
import streamlit as st


def render_price_chart(data):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price"
    ))

    for col in ["SMA20", "SMA50", "SMA200", "EMA9", "EMA21", "VWAP", "BB_UPPER", "BB_LOWER"]:
        if col in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data[col], name=col))

    fig.update_layout(
        height=650,
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
