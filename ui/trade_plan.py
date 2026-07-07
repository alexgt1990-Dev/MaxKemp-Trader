import streamlit as st
from ui.cards import render_card


def render_trade_plan(latest, plan):
    st.subheader("Trade Plan")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_card("Entry", f"${latest['Close']:,.2f}", "Current price")
    with c2:
        render_card("Stop", f"${plan['stop_loss']:,.2f}", "ATR based")
    with c3:
        render_card("Risk", f"${plan['risk_amount']:,.2f}", "Max loss")
    with c4:
        render_card("Shares", f"{plan['shares']:.0f}", "Position size")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        render_card("TP1", f"${plan['take_profit_1']:,.2f}", f"{plan['rr1']:.2f}x RR")
    with c6:
        render_card("TP2", f"${plan['take_profit_2']:,.2f}", f"{plan['rr2']:.2f}x RR")
    with c7:
        render_card("TP3", f"${plan['take_profit_3']:,.2f}", f"{plan['rr3']:.2f}x RR")
    with c8:
        render_card("Best RR", f"{plan['rr3']:.2f}x", "Target 3")
