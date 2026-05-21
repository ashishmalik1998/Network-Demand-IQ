# Network Demand IQ

**A decision dashboard for telecom product managers.**

Network Demand IQ links network performance, churn risk, and ROI simulations so you can identify the right hotspots to invest in — and walk into capex reviews with numbers, not guesses.

---

## What It Does

Telecom PMs typically spend 3–5 days gathering data from NOC engineers, customer analytics teams, and finance before they can propose a single network investment. Network Demand IQ compresses that into one sitting.

The app has three tabs that walk you through a complete investment decision:

| Tab | What You Do |
|-----|-------------|
| 📡 **Congestion Risk** | See which US cities have the highest network stress using a live bubble map and ranked bar chart. Drill into any city for speed, latency, and device metrics. |
| 👥 **Churn Risk** | Understand which customer segments are most at risk of leaving due to poor network quality, and how much annual revenue that puts at risk. |
| 💰 **Scenario Simulator** | Input a proposed CAPEX investment and instantly see projected annual revenue, ROI, QoS score, SLA risk, and churn reduction. Generate an AI-written executive business case with one click. |

---

## Tech Stack

- [Streamlit](https://streamlit.io/) — UI framework
- [Plotly](https://plotly.com/python/) — interactive charts and US geo map
- [Pandas](https://pandas.pydata.org/) + [NumPy](https://numpy.org/) — data generation
- [OpenAI GPT-4o-mini](https://platform.openai.com/) — AI business case generation
- Synthetic telecom data (reproducible, seeded with `numpy.random`)

---

## Project Structure

```
network-demand-iq/
├── app.py            Main Streamlit application — layout, tabs, session state
├── data.py           Synthetic data generation for 20 US cities and 8 customer segments
├── charts.py         All Plotly chart functions (geo map, bar charts, gauge)
├── ai.py             OpenAI API integration and prompt builder
├── requirements.txt  Python dependencies
├── .gitignore        Excludes .env and virtual environment
└── README.md
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/ashishmalik1998/Network-Demand-IQ.git
cd Network-Demand-IQ
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Mac / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=your-key-here" > .env
```

> Get a key at https://platform.openai.com/api-keys  
> The app runs fully without a key — only the "Generate AI Business Case" button requires it.

### 5. Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## How to Use

**Step 1 — Congestion Risk tab**
Select a city from the dropdown to drill into its network metrics. The bubble map highlights it and the bar chart ranks all 20 cities by congestion score.

**Step 2 — Churn Risk tab**
Review which customer segments are at highest risk. The city you selected in Step 1 carries over automatically.

**Step 3 — Scenario Simulator tab**
Adjust the input sliders (devices, bandwidth, CAPEX, latency target, pricing tier) and watch the projected ROI, QoS score, and churn reduction update live. When you're ready, click **Generate AI Business Case** to get a 3-paragraph executive recommendation.

---

## Congestion Score Formula

```
congestion_score = (
    (1 - (download_speed_mbps - 15) / 135) * 0.40   # speed component
  + ((latency_ms - 20) / 100)              * 0.35   # latency component
  + ((device_count - 5000) / 45000)        * 0.25   # density component
) * 100
```

| Score | Risk Level |
|-------|-----------|
| ≥ 70  | 🔴 High |
| 40–69 | 🟠 Medium |
| < 40  | 🟢 Low |

---

## Notes

- All data is **synthetic** and generated programmatically with a fixed random seed for reproducibility. No real network data is used.
- The `.env` file is excluded from git. Never commit your API key.
- The virtual environment (`.venv/`) is also excluded — always recreate it locally using the steps above.
