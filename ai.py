import os
from dotenv import load_dotenv

load_dotenv()


def build_prompt(
    selected_city: str,
    congestion_score: float,
    download_speed: float,
    latency: float,
    selected_segment: str,
    churn_probability: float,
    revenue_at_risk: float,
    capex_millions: float,
    devices: int,
    pricing_tier: str,
    annual_revenue: float,
    roi_percentage: float,
    qos_score: float,
    sla_risk: str,
    churn_reduction: float,
    saved_revenue: float,
) -> str:
    return f"""You are a senior telecom strategy consultant advising a Product Manager at a major US carrier.

Based on this analysis, write a concise executive business case recommendation in 3 paragraphs:

NETWORK ANALYSIS:
- Target City: {selected_city}
- Congestion Score: {congestion_score}/100
- Current Download Speed: {download_speed} Mbps
- Current Latency: {latency} ms

CUSTOMER RISK:
- Target Segment: {selected_segment}
- Current Churn Probability: {churn_probability * 100:.1f}%
- Annual Revenue at Risk: ${revenue_at_risk:,.0f}

INVESTMENT SIMULATION:
- CAPEX Investment: ${capex_millions}M
- Devices Supported: {devices:,}
- Pricing Tier: {pricing_tier}
- Projected Annual Revenue: ${annual_revenue:,.0f}
- Projected ROI: {roi_percentage:.1f}%
- QoS Score: {qos_score:.0f}/100
- SLA Risk: {sla_risk}
- Churn Reduction: {churn_reduction * 100:.1f}%
- Saved Revenue from Churn Prevention: ${saved_revenue:,.0f}

Write:
Paragraph 1: The problem — what the network data shows and what it is costing the business
Paragraph 2: The recommendation — what to invest, where, and why it makes financial sense
Paragraph 3: The risk assessment — SLA risk, what could go wrong, and why this investment is still justified

Keep it executive-level, specific, and under 250 words. Use the actual numbers provided."""


def generate_recommendation(prompt: str) -> str:
    """Call OpenAI and return the recommendation text. Returns an error string on failure."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "⚠️ **OpenAI API key not found.**\n\n"
            "Add `OPENAI_API_KEY=your-key-here` to your `.env` file and restart the app."
        )
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as exc:  # noqa: BLE001
        return f"⚠️ **Error generating recommendation:** {exc}"
