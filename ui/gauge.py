import plotly.graph_objects as go
import streamlit as st


def render_mk_gauge(mk):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=mk.total,
        number={
            "suffix": "/100",
            "font": {"size": 42}
        },
        title={
            "text": f"<b>MK Confidence™</b><br><span style='font-size:16px'>{mk.confidence}</span>",
            "font": {"size": 20}
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickmode": "array",
                "tickvals": [0, 25, 50, 75, 100],
            },
            "bar": {"thickness": 0.25},
            "steps": [
                {"range": [0, 45], "color": "#ffe5e5"},
                {"range": [45, 65], "color": "#fff3cd"},
                {"range": [65, 80], "color": "#dbeafe"},
                {"range": [80, 100], "color": "#dcfce7"},
            ],
            "threshold": {
                "line": {"width": 4},
                "thickness": 0.8,
                "value": mk.total
            },
        }
    ))

    fig.update_layout(
        height=240,
        margin=dict(l=10, r=10, t=45, b=5)
    )

    st.plotly_chart(fig, use_container_width=True)
