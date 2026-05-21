import numpy as np
import pandas as pd

RANDOM_SEED = 42

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Dallas",
    "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Seattle",
    "Denver", "Boston", "Atlanta", "Miami", "Detroit",
    "Minneapolis", "Portland", "Las Vegas", "Nashville", "Austin",
]

CITY_COORDS = {
    "New York":      (40.71, -74.01),
    "Los Angeles":   (34.05, -118.24),
    "Chicago":       (41.88, -87.63),
    "Houston":       (29.76, -95.37),
    "Dallas":        (32.78, -96.80),
    "Phoenix":       (33.45, -112.07),
    "Philadelphia":  (39.95, -75.17),
    "San Antonio":   (29.42, -98.49),
    "San Diego":     (32.72, -117.16),
    "Seattle":       (47.61, -122.33),
    "Denver":        (39.74, -104.98),
    "Boston":        (42.36, -71.06),
    "Atlanta":       (33.75, -84.39),
    "Miami":         (25.77, -80.19),
    "Detroit":       (42.33, -83.05),
    "Minneapolis":   (44.98, -93.27),
    "Portland":      (45.52, -122.68),
    "Las Vegas":     (36.17, -115.14),
    "Nashville":     (36.17, -86.78),
    "Austin":        (30.27, -97.74),
}

CUSTOMER_SEGMENTS = [
    {"segment": "High Value Postpaid",  "monthly_charges": 120, "contract_type": "Month-to-month", "tenure_months": 8,  "complaint_count": 4, "churn_probability": 0.42},
    {"segment": "Mid Value Postpaid",   "monthly_charges": 75,  "contract_type": "Month-to-month", "tenure_months": 14, "complaint_count": 3, "churn_probability": 0.31},
    {"segment": "Low Value Postpaid",   "monthly_charges": 45,  "contract_type": "Month-to-month", "tenure_months": 24, "complaint_count": 1, "churn_probability": 0.18},
    {"segment": "High Value Contract",  "monthly_charges": 110, "contract_type": "Two year",        "tenure_months": 18, "complaint_count": 3, "churn_probability": 0.12},
    {"segment": "Mid Value Contract",   "monthly_charges": 70,  "contract_type": "One year",        "tenure_months": 22, "complaint_count": 2, "churn_probability": 0.09},
    {"segment": "Enterprise SMB",       "monthly_charges": 250, "contract_type": "One year",        "tenure_months": 11, "complaint_count": 5, "churn_probability": 0.38},
    {"segment": "FWA Customer",         "monthly_charges": 60,  "contract_type": "Month-to-month", "tenure_months": 6,  "complaint_count": 6, "churn_probability": 0.51},
    {"segment": "Prepaid",              "monthly_charges": 35,  "contract_type": "Month-to-month", "tenure_months": 4,  "complaint_count": 2, "churn_probability": 0.28},
]

PRICING_TIERS = {
    "Basic ($45/mo)":       45,
    "Standard ($75/mo)":    75,
    "Premium ($120/mo)":    120,
    "Enterprise ($250/mo)": 250,
}


def generate_city_data() -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    download_speeds = rng.uniform(15, 150, len(CITIES))
    latencies       = rng.uniform(20, 120, len(CITIES))
    device_counts   = rng.integers(5000, 50001, len(CITIES))

    congestion_scores = (
        (1 - (download_speeds - 15) / 135) * 0.4
        + ((latencies - 20) / 100) * 0.35
        + ((device_counts - 5000) / 45000) * 0.25
    ) * 100

    lats = [CITY_COORDS[c][0] for c in CITIES]
    lons = [CITY_COORDS[c][1] for c in CITIES]

    df = pd.DataFrame({
        "city":               CITIES,
        "lat":                lats,
        "lon":                lons,
        "download_speed_mbps": download_speeds.round(1),
        "latency_ms":         latencies.round(1),
        "device_count":       device_counts.astype(int),
        "congestion_score":   congestion_scores.round(1),
    })

    df["risk_level"] = df["congestion_score"].apply(
        lambda s: "High" if s > 70 else ("Medium" if s >= 40 else "Low")
    )
    df["risk_color"] = df["risk_level"].map({"High": "#E63946", "Medium": "#F4A261", "Low": "#2A9D8F"})

    return df.sort_values("congestion_score", ascending=False).reset_index(drop=True)


def generate_churn_data() -> pd.DataFrame:
    df = pd.DataFrame(CUSTOMER_SEGMENTS)
    df["annual_revenue_at_risk"] = (
        df["churn_probability"] * df["monthly_charges"] * 12
    ).round(2)
    df["risk_level"] = df["churn_probability"].apply(
        lambda p: "High" if p >= 0.35 else ("Medium" if p >= 0.15 else "Low")
    )
    df["risk_color"] = df["risk_level"].map({"High": "#E63946", "Medium": "#F4A261", "Low": "#2A9D8F"})
    return df


def calculate_simulation(
    devices: int,
    bandwidth_gbps: float,
    pricing_tier_label: str,
    capex_millions: float,
    latency_target: int,
    selected_segment: str,
    churn_df: pd.DataFrame,
) -> dict:
    pricing_value = PRICING_TIERS[pricing_tier_label]

    monthly_revenue = devices * pricing_value
    annual_revenue  = monthly_revenue * 12

    seg_row    = churn_df[churn_df["segment"] == selected_segment].iloc[0]
    base_churn = float(seg_row["churn_probability"])

    churn_reduction      = min(0.15, bandwidth_gbps / 100 * 0.2)
    new_churn_probability = max(0.05, base_churn - churn_reduction)
    saved_revenue        = (base_churn - new_churn_probability) * annual_revenue

    total_benefit = annual_revenue + saved_revenue
    capex_dollars = capex_millions * 1_000_000
    roi_percentage = ((total_benefit - capex_dollars) / capex_dollars) * 100

    qos_score = min(100, (bandwidth_gbps / devices * 10_000) * 0.5 + (1 - latency_target / 100) * 50)

    if qos_score >= 80:
        sla_risk, sla_color = "Low",    "green"
    elif qos_score >= 60:
        sla_risk, sla_color = "Medium", "orange"
    else:
        sla_risk, sla_color = "High",   "red"

    return {
        "annual_revenue":       annual_revenue,
        "roi_percentage":       roi_percentage,
        "qos_score":            qos_score,
        "sla_risk":             sla_risk,
        "sla_color":            sla_color,
        "churn_reduction":      churn_reduction,
        "new_churn_probability": new_churn_probability,
        "saved_revenue":        saved_revenue,
        "total_benefit":        total_benefit,
        "capex_dollars":        capex_dollars,
        "base_churn":           base_churn,
        "pricing_value":        pricing_value,
        "monthly_revenue":      monthly_revenue,
    }
