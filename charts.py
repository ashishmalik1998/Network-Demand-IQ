import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # noqa: F401

TELECOM_BLUE = "#0066CC"
FONT_FAMILY  = "Inter, Arial, sans-serif"

_BASE_LAYOUT = dict(
    font=dict(family=FONT_FAMILY, size=13),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
)


def congestion_bar_chart(df: pd.DataFrame) -> go.Figure:
    df_sorted = df.sort_values("congestion_score", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=df_sorted["congestion_score"],
            y=df_sorted["city"],
            orientation="h",
            marker_color=df_sorted["risk_color"].tolist(),
            text=df_sorted["congestion_score"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Congestion Score: %{x:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        **_BASE_LAYOUT,
        title=dict(text="Congestion Score by City", font=dict(size=16, color=TELECOM_BLUE)),
        xaxis=dict(title="Congestion Score (0-100)", range=[0, 115], gridcolor="#E8EEF4"),
        yaxis=dict(title="", tickfont=dict(size=11)),
        height=520,
        showlegend=False,
    )
    return fig


def churn_bar_chart(df: pd.DataFrame) -> go.Figure:
    df_sorted = df.sort_values("churn_probability", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=df_sorted["churn_probability"] * 100,
            y=df_sorted["segment"],
            orientation="h",
            marker_color=df_sorted["risk_color"].tolist(),
            text=df_sorted["churn_probability"].apply(lambda v: f"{v*100:.0f}%"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Churn Probability: %{x:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        **_BASE_LAYOUT,
        title=dict(text="Churn Probability by Customer Segment", font=dict(size=16, color=TELECOM_BLUE)),
        xaxis=dict(title="Churn Probability (%)", range=[0, 65], gridcolor="#E8EEF4"),
        yaxis=dict(title="", tickfont=dict(size=11)),
        height=380,
        showlegend=False,
    )
    return fig


def simulation_comparison_chart(
    annual_revenue: float,
    total_benefit: float,
    saved_revenue: float,
    capex_dollars: float,
) -> go.Figure:
    categories = ["CAPEX Investment", "Projected Annual Revenue", "Saved Churn Revenue", "Total Benefit"]
    values     = [capex_dollars, annual_revenue, saved_revenue, total_benefit]
    colors     = ["#E63946", TELECOM_BLUE, "#2A9D8F", "#264653"]

    fig = go.Figure(
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"${v/1_000_000:.2f}M" for v in values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        **_BASE_LAYOUT,
        title=dict(text="Investment vs. Projected Returns", font=dict(size=16, color=TELECOM_BLUE)),
        xaxis=dict(title=""),
        yaxis=dict(title="Amount (USD)", gridcolor="#E8EEF4", tickformat="$,.0f"),
        height=380,
        showlegend=False,
    )
    return fig


def qos_gauge_chart(qos_score: float) -> go.Figure:
    bar_color = "#2A9D8F" if qos_score >= 80 else ("#F4A261" if qos_score >= 60 else "#E63946")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=qos_score,
            delta={"reference": 80, "increasing": {"color": "#2A9D8F"}, "decreasing": {"color": "#E63946"}},
            number={"suffix": "/100", "font": {"size": 28, "color": TELECOM_BLUE}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#555"},
                "bar": {"color": bar_color, "thickness": 0.3},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "#CBD5E0",
                "steps": [
                    {"range": [0,  60],  "color": "#FDECEA"},
                    {"range": [60, 80],  "color": "#FFF3E0"},
                    {"range": [80, 100], "color": "#E8F5E9"},
                ],
                "threshold": {
                    "line": {"color": "#333", "width": 4},
                    "thickness": 0.8,
                    "value": 80,
                },
            },
            title={"text": "QoS Score", "font": {"size": 16, "color": TELECOM_BLUE}},
        )
    )
    # No **_BASE_LAYOUT spread here — avoids duplicate `margin` keyword
    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=13),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=20, r=20, t=60, b=10),
    )
    return fig


def city_geo_map(df: pd.DataFrame, selected_city: str | None = None) -> go.Figure:
    """Scatter-geo bubble map of all 20 cities coloured by congestion score."""
    hover_texts = [
        f"<b>{r['city']}</b><br>"
        f"Congestion Score: {r['congestion_score']:.1f}<br>"
        f"Download Speed: {r['download_speed_mbps']:.1f} Mbps<br>"
        f"Latency: {r['latency_ms']:.1f} ms<br>"
        f"Devices: {r['device_count']:,}<br>"
        f"Risk: {r['risk_level']}"
        for _, r in df.iterrows()
    ]

    scatter = go.Scattergeo(
        lat=df["lat"],
        lon=df["lon"],
        text=hover_texts,
        hoverinfo="text",
        mode="markers+text",
        textposition="top center",
        textfont=dict(size=9, color="#1E293B"),
        marker=dict(
            size=df["device_count"] / 1_500,
            color=df["congestion_score"],
            colorscale=[[0.0, "#2A9D8F"], [0.40, "#F4A261"], [1.0, "#E63946"]],
            cmin=0, cmax=100,
            colorbar=dict(
                title=dict(text="Congestion<br>Score", font=dict(size=12)),
                thickness=14, len=0.7, x=1.01,
            ),
            line=dict(width=1.2, color="white"),
            opacity=0.88,
        ),
        name="Cities",
    )

    traces = [scatter]

    if selected_city:
        sel = df[df["city"] == selected_city]
        if not sel.empty:
            row = sel.iloc[0]
            traces.append(
                go.Scattergeo(
                    lat=[row["lat"]], lon=[row["lon"]],
                    mode="markers",
                    marker=dict(
                        size=row["device_count"] / 1_500 + 10,
                        color="rgba(0,0,0,0)",
                        line=dict(width=3, color="#0066CC"),
                    ),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(text="Network Congestion — US City Map", font=dict(size=16, color=TELECOM_BLUE), x=0),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,      landcolor="#F1F5F9",
            showlakes=True,     lakecolor="#DBEAFE",
            showcoastlines=True, coastlinecolor="#CBD5E0",
            showsubunits=True,  subunitcolor="#E2E8F0",
            bgcolor="rgba(0,0,0,0)",
        ),
        font=dict(family=FONT_FAMILY, size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=44, b=0),
        height=480,
        showlegend=False,
    )
    return fig
