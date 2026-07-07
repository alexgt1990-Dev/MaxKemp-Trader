import plotly.graph_objects as go
import streamlit as st


def render_mk_gauge(mk):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=mk.total,
        number={"suffix": "/100"},
        title={"text": f"MK Confidence™<br><b>{mk.confidence}</b>"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"thickness": 0.25},
            "steps": [
                {"range": [0, 45]},
                {"range": [45, 65]},
                {"range": [65, 80]},
                {"range": [80, 100]},
            ],
        }
    ))

    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)
