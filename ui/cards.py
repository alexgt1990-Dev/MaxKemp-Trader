import streamlit as st


def get_grade(score):
    if score >= 95:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 85:
        return "A-"
    if score >= 80:
        return "B+"
    if score >= 70:
        return "B"
    if score >= 65:
        return "B-"
    if score >= 55:
        return "C"
    if score >= 45:
        return "D"
    return "F"


def render_card(title, value, subtitle=""):
    st.markdown(
        f"""
        <div style="
            padding: 18px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.04);
            box-shadow: 0 4px 18px rgba(0,0,0,0.18);
            margin-bottom: 12px;
        ">
            <div style="font-size: 13px; opacity: 0.75;">{title}</div>
            <div style="font-size: 30px; font-weight: 700; margin-top: 6px;">{value}</div>
            <div style="font-size: 14px; opacity: 0.75; margin-top: 4px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_score_cards(mk):
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        render_card("Grade", get_grade(mk.total), "MK Trade Grade")
    with c2:
        render_card("Trend", f"{mk.trend}/30", "Market direction")
    with c3:
        render_card("Momentum", f"{mk.momentum}/20", "RSI + MACD")
    with c4:
        render_card("Volume", f"{mk.volume}/15", "Relative volume")
    with c5:
        render_card("Risk", f"{mk.risk}/15", "Trade quality")
    with c6:
        render_card("Setup", f"{mk.setup}/10", "Technical setup")
