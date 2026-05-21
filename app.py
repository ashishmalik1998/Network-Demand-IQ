import streamlit as st
import pandas as pd

from data import (
    generate_city_data,
    generate_churn_data,
    calculate_simulation,
    CITIES,
    PRICING_TIERS,
)
from charts import (
    congestion_bar_chart,
    churn_bar_chart,
    simulation_comparison_chart,
    qos_gauge_chart,
    city_geo_map,
)
from ai import build_prompt, generate_recommendation

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Network Demand IQ",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Hero */
    .hero-header {
        background: linear-gradient(135deg, #0066CC 0%, #003D7A 100%);
        padding: 2rem 2.5rem 1.6rem; border-radius: 14px;
        margin-bottom: 1rem; color: white;
    }
    .hero-header h1 { font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
    .hero-header .pitch {
        font-size: 1rem; margin: 0.65rem 0 0; opacity: 0.92;
        line-height: 1.7; max-width: 740px;
    }

    /* Progress bar */
    .progress-wrapper {
        display: flex; align-items: center; gap: 12px;
        background: #F0F4FA; border-radius: 10px;
        padding: 0.65rem 1.2rem; margin-bottom: 0.8rem;
    }
    .progress-label { font-size: 0.8rem; color: #555; font-weight: 500; white-space: nowrap; }
    .step-badge {
        font-size: 0.72rem; font-weight: 600; padding: 2px 10px;
        border-radius: 20px; white-space: nowrap;
    }
    .step-done   { background: #DCFCE7; color: #15803D; }
    .step-active { background: #DBEAFE; color: #1D4ED8; }
    .step-todo   { background: #F1F5F9; color: #94A3B8; }

    /* Radio tab bar: collapse its bottom margin to match the top gap */
    [data-testid="stRadio"] {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Also collapse the iframe wrapper that components.html injects */
    [data-testid="stCustomComponentV1"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
    }

    /* AI panel */
    .ai-panel {
        background: linear-gradient(135deg, #EBF4FF 0%, #DBEAFE 100%);
        border: 1.5px solid #93C5FD; border-radius: 14px;
        padding: 1.6rem 2rem; margin-top: 2rem;
    }
    .ai-panel h3 { color: #1D4ED8; font-size: 1.1rem; margin: 0 0 0.8rem; }
    .ai-panel .placeholder { color: #6B7280; font-style: italic; }
    .ai-panel .recommendation { color: #1E293B; line-height: 1.75; white-space: pre-wrap; }

    /* Hover tooltip icon */
    .tip-wrap {
        display: inline-block; position: relative;
        cursor: help; font-size: 1.1rem; margin-left: 6px; vertical-align: middle;
    }
    .tip-box {
        visibility: hidden; opacity: 0;
        background: #1E293B; color: #F1F5F9;
        font-size: 0.8rem; line-height: 1.55;
        padding: 0.55rem 0.85rem; border-radius: 7px;
        position: absolute; z-index: 9999;
        bottom: 140%; left: 50%; transform: translateX(-50%);
        width: 300px; pointer-events: none;
        transition: opacity 0.18s ease;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    }
    .tip-box::after {
        content: ""; position: absolute;
        top: 100%; left: 50%; transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: #1E293B;
    }
    .tip-wrap:hover .tip-box { visibility: visible; opacity: 1; }

    /* Warning box */
    .warning-box {
        background: #FFF8F0; border-left: 4px solid #F4A261;
        border-radius: 6px; padding: 0.9rem 1.2rem; margin: 1rem 0;
        color: #7C3A00; font-size: 0.92rem;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #F8FAFC; border: 1px solid #E2E8F0;
        border-radius: 10px; padding: 0.8rem 1rem;
    }

    /* Primary CTA button */
    .stButton > button {
        background: linear-gradient(135deg, #0066CC, #0052A3);
        color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 600 !important;
        font-size: 1rem !important; padding: 0.7rem 2rem !important;
        width: 100% !important; transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.88 !important; }

    .stDataFrame { border-radius: 8px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
_defaults = {
    "active_tab":        0,
    "selected_city":     None,
    "congestion_score":  None,
    "download_speed":    None,
    "latency":           None,
    "ai_recommendation": None,
    "tab3_completed":    False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Data ──────────────────────────────────────────────────────────────────────
city_df  = generate_city_data()
churn_df = generate_churn_data()

# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-header">
        <h1>📡 Network Demand IQ</h1>
        <p class="pitch">
            Network Demand IQ is a decision dashboard for telecom product managers.
            It links network performance, churn risk, and simple ROI simulations
            so you can pick the right hotspots to invest in and walk into capex reviews
            with numbers, not guesses.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("ℹ️ How to use this platform"):
    st.markdown(
        """
        **Step 1 — Congestion Risk:**
        Open the Congestion Risk tab to see which cities in your network are under stress and need immediate attention.

        **Step 2 — Churn Risk:**
        Move to the Churn Risk tab to understand which customer segments are at risk of leaving due to poor network experience and how much revenue that puts at risk.

        **Step 3 — Scenario Simulator:**
        Open the Scenario Simulator, input your proposed investment, and instantly see projected ROI, QoS score, and SLA risk.

        **Step 4 — Generate Business Case:**
        Click Generate Business Case to receive an AI-powered executive recommendation you can take directly to leadership.
        """
    )

# ── Progress bar ──────────────────────────────────────────────────────────────
# Read from the radio widget's own session key — it's set by Streamlit BEFORE
# this script line runs on every rerun, so it's always up-to-date.
_TAB_LABELS = ["📡  Congestion Risk", "👥  Churn Risk", "💰  Scenario Simulator"]
_current_radio = st.session_state.get("tab_radio")
if _current_radio in _TAB_LABELS:
    _tab = _TAB_LABELS.index(_current_radio)
else:
    _tab = st.session_state.get("active_tab", 0)
_ai  = st.session_state.ai_recommendation is not None

if _ai:
    pct, pct_color, pct_label = 100, "#2A9D8F", "✅ Business Case Ready"
elif _tab == 2:
    pct, pct_color, pct_label = 100, "#0066CC", "Step 3 — Simulator"
elif _tab == 1:
    pct, pct_color, pct_label = 66,  "#0066CC", "Step 2 — Churn Risk"
else:
    pct, pct_color, pct_label = 33,  "#0066CC", "Step 1 — Congestion"

def _badge(label: str, state: str) -> str:
    return f'<span class="step-badge step-{state}">{label}</span>'

b = ["done" if _tab > i else ("active" if _tab == i else "todo") for i in range(3)]
if _ai:
    b = ["done", "done", "done"]

st.markdown(
    f"""
    <div class="progress-wrapper">
        <span class="progress-label">Progress:</span>
        <div style="flex:1;background:#CBD5E0;border-radius:6px;height:10px;overflow:hidden;">
            <div style="width:{pct}%;height:100%;background:{pct_color};
                        border-radius:6px;transition:width 0.35s ease;"></div>
        </div>
        {_badge("1 · Congestion", b[0])}
        {_badge("2 · Churn", b[1])}
        {_badge("3 · Simulator", b[2])}
        <span class="progress-label" style="color:{pct_color};font-weight:600;">{pct_label}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Tab navigation ────────────────────────────────────────────────────────────
selected_label = st.radio(
    "tab_nav",
    _TAB_LABELS,
    index=_tab,
    horizontal=True,
    label_visibility="collapsed",
    key="tab_radio",
)

active = _TAB_LABELS.index(selected_label)
st.session_state.active_tab = active

# JavaScript directly styles the radio DOM — bypasses all CSS selector uncertainty.
# Runs immediately + retries at 100ms/400ms to catch late renders.
import streamlit.components.v1 as _cv1
_cv1.html(f"""
<script>
(function(){{
  var ACTIVE = {active};
  var TAB_BG   = ["#EBF4FF","#F1F5F9","#F1F5F9"];
  var TAB_CLR  = ["#0066CC","#374151","#374151"];
  // rotate so active slot is first
  TAB_BG  = TAB_BG.map(function(v,i){{ return i===ACTIVE?"#EBF4FF":"#F1F5F9"; }});
  TAB_CLR = TAB_CLR.map(function(v,i){{ return i===ACTIVE?"#0066CC":"#374151"; }});

  function apply(){{
    var doc  = window.parent.document;
    var root = doc.querySelector('[data-testid="stRadio"]');
    if(!root) return false;

    // Find the flex container — try every known selector path
    var grp = root.querySelector('[data-baseweb="radio-group"]')
           || root.querySelector('[role="radiogroup"]')
           || (root.children[root.children.length-1] &&
               root.children[root.children.length-1].firstElementChild);
    if(!grp) return false;

    // Container: full-width flex row
    grp.style.display        = "flex";
    grp.style.flexDirection  = "row";
    grp.style.width          = "100%";
    grp.style.gap            = "4px";
    grp.style.borderBottom   = "2px solid #D1D9E6";
    grp.style.marginBottom   = "0";

    var labels = grp.querySelectorAll("label");
    labels.forEach(function(lbl, i){{
      // Equal-width tab
      lbl.style.flex            = "1 1 0";
      lbl.style.minWidth        = "0";
      lbl.style.boxSizing       = "border-box";
      lbl.style.background      = TAB_BG[i]  || "#F1F5F9";
      lbl.style.border          = "1px solid #D1D9E6";
      lbl.style.borderBottom    = "none";
      lbl.style.borderRadius    = "8px 8px 0 0";
      lbl.style.padding         = "0.65rem 0.5rem";
      lbl.style.display         = "flex";
      lbl.style.alignItems      = "center";
      lbl.style.justifyContent  = "center";
      lbl.style.cursor          = "pointer";
      lbl.style.marginBottom    = "-2px";
      lbl.style.transition      = "background 0.15s";

      // Hide the radio dot (first child div)
      var dot = lbl.querySelector("div:first-child");
      if(dot) dot.style.display = "none";

      // Colour every text node inside the label
      lbl.querySelectorAll("*").forEach(function(el){{
        if(el.tagName !== "INPUT"){{
          el.style.color      = TAB_CLR[i] || "#374151";
          el.style.fontWeight = i===ACTIVE ? "700" : "500";
          el.style.fontSize   = "0.92rem";
        }}
      }});
    }});
    return true;
  }}

  if(!apply()){{
    var t1 = setTimeout(function(){{ if(!apply()) setTimeout(apply, 300); }}, 100);
  }}
}})();
</script>
""", height=0, scrolling=False)

st.markdown("<div style='margin-top:-1rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 0 — CONGESTION RISK
# ─────────────────────────────────────────────────────────────────────────────
if active == 0:
    st.subheader("Network Congestion Risk Map", divider="blue")

    avg_speed   = city_df["download_speed_mbps"].mean()
    avg_latency = city_df["latency_ms"].mean()
    total_dev   = city_df["device_count"].sum()
    high_risk_n = (city_df["risk_level"] == "High").sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⚡ Avg Network Speed",   f"{avg_speed:.1f} Mbps")
    m2.metric("📶 Avg Latency",         f"{avg_latency:.1f} ms")
    m3.metric("📱 Devices Monitored",   f"{total_dev:,}")
    m4.metric("🔴 Cities at High Risk", str(high_risk_n))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── City selector ABOVE charts ────────────────────────────────────────────
    city_options = ["— Select a city —"] + \
        city_df.sort_values("congestion_score", ascending=False)["city"].tolist()
    default_idx = (
        city_options.index(st.session_state.selected_city)
        if st.session_state.selected_city in city_options else 0
    )
    sel_col, detail_col = st.columns([1, 2])
    with sel_col:
        st.markdown("#### 🔍 Drill into a City")
        chosen_city = st.selectbox(
            "Choose city:", city_options, index=default_idx,
            key="city_selectbox_tab0", label_visibility="collapsed",
        )
        if chosen_city != "— Select a city —":
            row = city_df[city_df["city"] == chosen_city].iloc[0]
            st.session_state.selected_city    = chosen_city
            st.session_state.congestion_score = float(row["congestion_score"])
            st.session_state.download_speed   = float(row["download_speed_mbps"])
            st.session_state.latency          = float(row["latency_ms"])

    with detail_col:
        if st.session_state.selected_city and chosen_city != "— Select a city —":
            row = city_df[city_df["city"] == chosen_city].iloc[0]
            risk_emoji = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}[row["risk_level"]]
            st.info(
                f"**{chosen_city}** &nbsp; {risk_emoji} **{row['risk_level']} Risk**\n\n"
                f"- Congestion Score: **{row['congestion_score']:.1f} / 100**\n"
                f"- Download Speed: **{row['download_speed_mbps']:.1f} Mbps**\n"
                f"- Latency: **{row['latency_ms']:.1f} ms**\n"
                f"- Devices on Network: **{row['device_count']:,}**"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Geo map + bar chart side by side ─────────────────────────────────────
    map_col, bar_col = st.columns(2, gap="medium")
    with map_col:
        st.plotly_chart(
            city_geo_map(city_df, selected_city=st.session_state.selected_city),
            width="stretch",
        )
    with bar_col:
        st.plotly_chart(congestion_bar_chart(city_df), width="stretch")


    st.markdown("#### All Cities — Congestion Data")
    display_df = city_df[["city", "download_speed_mbps", "latency_ms",
                           "device_count", "congestion_score", "risk_level"]].copy()
    display_df.columns = ["City", "Speed (Mbps)", "Latency (ms)",
                           "Devices", "Congestion Score", "Risk Level"]
    st.dataframe(
        display_df.sort_values("Congestion Score", ascending=False),
        use_container_width=True, hide_index=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — CHURN RISK
# ─────────────────────────────────────────────────────────────────────────────
elif active == 1:
    st.subheader("Customer Churn Risk Analysis", divider="blue")

    # City selector — same session state as Tab 0, different widget key
    city_options_t1 = ["— Select a city —"] + \
        city_df.sort_values("congestion_score", ascending=False)["city"].tolist()
    default_idx_t1 = (
        city_options_t1.index(st.session_state.selected_city)
        if st.session_state.selected_city in city_options_t1 else 0
    )
    churn_sel_col, churn_detail_col = st.columns([1, 2])
    with churn_sel_col:
        st.markdown("#### 🔍 Drill into a City")
        chosen_city_t1 = st.selectbox(
            "Choose city:", city_options_t1, index=default_idx_t1,
            key="city_selectbox_tab1", label_visibility="collapsed",
        )
        if chosen_city_t1 != "— Select a city —":
            row_t1 = city_df[city_df["city"] == chosen_city_t1].iloc[0]
            st.session_state.selected_city    = chosen_city_t1
            st.session_state.congestion_score = float(row_t1["congestion_score"])
            st.session_state.download_speed   = float(row_t1["download_speed_mbps"])
            st.session_state.latency          = float(row_t1["latency_ms"])
    with churn_detail_col:
        if st.session_state.selected_city and chosen_city_t1 != "— Select a city —":
            st.success(f"📍 Analyzing churn risk for customers in: **{st.session_state.selected_city}**")

    total_rev_at_risk = churn_df["annual_revenue_at_risk"].sum()
    highest_risk_seg  = churn_df.loc[churn_df["churn_probability"].idxmax(), "segment"]
    avg_churn         = churn_df["churn_probability"].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💸 Annual Revenue at Risk", f"${total_rev_at_risk * 1000:,.0f}")
    m2.metric("⚠️ Highest Risk Segment",   highest_risk_seg)
    m3.metric("📊 Avg Churn Probability",  f"{avg_churn*100:.1f}%")
    m4.metric("👥 Customers Analyzed",     "250,000")

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(churn_bar_chart(churn_df), width="stretch")


    top3 = churn_df.nlargest(3, "churn_probability")["segment"].tolist()
    st.markdown(
        f'<div class="warning-box">⚠️ <strong>Top 3 Highest-Risk Segments:</strong> '
        f'{" &nbsp;|&nbsp; ".join(top3)}<br>'
        "These segments require immediate intervention. Consider targeted retention campaigns "
        "and network quality improvements in congested areas.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### All Segments — Churn & Revenue Risk")
    table_df = churn_df[["segment", "contract_type", "tenure_months", "complaint_count",
                          "churn_probability", "monthly_charges", "annual_revenue_at_risk"]].copy()
    table_df.columns = ["Segment", "Contract Type", "Tenure (mo)", "Complaints",
                         "Churn Prob.", "Monthly Charges ($)", "Annual Revenue at Risk ($)"]
    table_df["Churn Prob."] = table_df["Churn Prob."].apply(lambda v: f"{v*100:.0f}%")
    st.dataframe(
        table_df.sort_values("Annual Revenue at Risk ($)", ascending=False),
        use_container_width=True, hide_index=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — SCENARIO SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────
elif active == 2:
    st.subheader("Network Investment Scenario Simulator", divider="blue")

    inp_col, out_col = st.columns([1, 2], gap="large")

    with inp_col:
        st.markdown("##### 📍 Target")
        city_default_idx = CITIES.index(st.session_state.selected_city) \
            if st.session_state.selected_city in CITIES else 0
        sim_city    = st.selectbox("Target City",    CITIES,                       index=city_default_idx, key="sim_city")
        sim_segment = st.selectbox("Target Segment", churn_df["segment"].tolist(), key="sim_segment")

        st.markdown("##### 📶 Network Parameters")
        sim_devices        = st.slider("Devices to Support",          1_000, 50_000, 10_000, 500, key="sim_devices")
        sim_bandwidth      = st.slider("Bandwidth Allocation (Gbps)", 1,     100,    20,     1,   key="sim_bw")
        sim_latency_target = st.slider("Latency Target (ms)",         10,    100,    30,     1,   key="sim_lat")

        st.markdown("##### 💰 Financial Parameters")
        sim_pricing = st.selectbox("Pricing Tier",          list(PRICING_TIERS.keys()), key="sim_pricing")
        sim_capex   = st.slider("CAPEX Investment ($M)", 0.5, 20.0, 2.0, 0.1,           key="sim_capex")

    r = calculate_simulation(
        devices=sim_devices,
        bandwidth_gbps=sim_bandwidth,
        pricing_tier_label=sim_pricing,
        capex_millions=sim_capex,
        latency_target=sim_latency_target,
        selected_segment=sim_segment,
        churn_df=churn_df,
    )

    with out_col:
        st.markdown("##### 📊 Projected Results")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("💰 Annual Revenue", f"${r['annual_revenue']:,.0f}")
        k2.metric("📈 Projected ROI",  f"{r['roi_percentage']:.1f}%",
                  delta=f"{r['roi_percentage']:.1f}% vs break-even" if r["roi_percentage"] > 0 else None)
        k3.metric("📶 QoS Score",      f"{r['qos_score']:.0f} / 100")
        k4.metric("🛡️ SLA Risk",       r["sla_risk"])

        st.markdown("<br>", unsafe_allow_html=True)
        cc, gc = st.columns([2, 1])
        with cc:
            st.plotly_chart(
                simulation_comparison_chart(
                    annual_revenue=r["annual_revenue"],
                    total_benefit=r["total_benefit"],
                    saved_revenue=r["saved_revenue"],
                    capex_dollars=r["capex_dollars"],
                ),
                width="stretch",
            )
        with gc:
            st.plotly_chart(qos_gauge_chart(r["qos_score"]), width="stretch")

    st.markdown("#### Simulation Summary")
    st.dataframe(
        pd.DataFrame({
            "Parameter": [
                "Target City", "Target Segment", "Devices Supported",
                "Bandwidth (Gbps)", "Pricing Tier", "CAPEX ($M)", "Latency Target (ms)",
                "Annual Revenue", "Saved Churn Revenue", "Total Benefit",
                "ROI", "QoS Score", "SLA Risk",
                "Churn Rate (Before)", "Churn Rate (After)", "Churn Reduction",
            ],
            "Value": [
                sim_city, sim_segment, f"{sim_devices:,}",
                str(sim_bandwidth), sim_pricing, f"${sim_capex}M", f"{sim_latency_target} ms",
                f"${r['annual_revenue']:,.0f}", f"${r['saved_revenue']:,.0f}", f"${r['total_benefit']:,.0f}",
                f"{r['roi_percentage']:.1f}%", f"{r['qos_score']:.0f}/100", r["sla_risk"],
                f"{r['base_churn']*100:.1f}%", f"{r['new_churn_probability']*100:.1f}%",
                f"{r['churn_reduction']*100:.1f}%",
            ],
        }),
        use_container_width=True, hide_index=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🤖 Generate AI Business Case", key="gen_ai"):
        city_row = city_df[city_df["city"] == sim_city]
        city_row = city_row.iloc[0] if not city_row.empty else city_df.iloc[0]
        seg_row  = churn_df[churn_df["segment"] == sim_segment].iloc[0]

        prompt = build_prompt(
            selected_city=sim_city,
            congestion_score=float(city_row["congestion_score"]),
            download_speed=float(city_row["download_speed_mbps"]),
            latency=float(city_row["latency_ms"]),
            selected_segment=sim_segment,
            churn_probability=float(seg_row["churn_probability"]),
            revenue_at_risk=float(seg_row["annual_revenue_at_risk"]),
            capex_millions=sim_capex,
            devices=sim_devices,
            pricing_tier=sim_pricing,
            annual_revenue=r["annual_revenue"],
            roi_percentage=r["roi_percentage"],
            qos_score=r["qos_score"],
            sla_risk=r["sla_risk"],
            churn_reduction=r["churn_reduction"],
            saved_revenue=r["saved_revenue"],
        )

        with st.spinner("Generating AI recommendation…"):
            recommendation = generate_recommendation(prompt)

        st.session_state.ai_recommendation = recommendation
        st.session_state.tab3_completed    = True
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PERSISTENT AI RECOMMENDATION PANEL
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.ai_recommendation:
    panel_body = f'<p class="recommendation">{st.session_state.ai_recommendation}</p>'
else:
    panel_body = (
        '<p class="placeholder">Complete all three tabs to generate your AI-powered business case. '
        "Select a city in Congestion Risk, review Churn Risk, then run the Scenario Simulator "
        "and click <strong>Generate AI Business Case</strong>.</p>"
    )

st.markdown(
    f"""
    <div class="ai-panel">
        <h3>🤖 AI Business Case Recommendation</h3>
        {panel_body}
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.ai_recommendation:
    if st.button("🗑️ Clear Recommendation", key="clear_rec"):
        st.session_state.ai_recommendation = None
        st.session_state.tab3_completed    = False
        st.rerun()
