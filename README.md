# AI-Powered Digital Twin of India's Climate

An advanced spatial-temporal Proof-of-Concept (PoC) web application developed for the **ISRO Bharatiya Antariksh Hackathon 2026** challenge: **"AI-Powered Digital Twin of India's Climate using India's National Data"**.

This digital twin provides a high-fidelity virtual representation of India's climate system, simulating historical climate parameters, making future recursive predictions using machine learning (XGBoost & Random Forest), and stress-testing ecological vulnerability (drought, flood, and heatwaves) under what-if warming scenarios.

---

## 🌟 Key Features

1. **Integrated Ingestion & Infill Pipeline**: Loads and cleans meteorological datasets (Rainfall, Max Temp, Min Temp) for all 36 Indian states/UTs (from 2010 to 2026), handle missing values chronologically, and engineers rolling sliding features & trigonometric seasonal indicators.
2. **Climate Prediction Engine**: Employs pre-trained Random Forest and XGBoost Regressors to compute future recursive multi-step temperatures and rainfalls for 7-day and 30-day forecasting horizons.
3. **Interactive Operations Room**: Visualizes daily meteorological states and z-score departures on customized Folium heatmaps and interactive bubble maps.
4. **Active Climate Intelligence**: Generates automated warning alert banners (Red/Orange/Yellow cards) for extreme heating, cloudbursts, and crop drought conditions.
5. **What-If Scenario Simulator**: Stress-tests national vulnerability by applying temperature offsets (ΔT ∈ {+1°C, +2°C, +3°C}) and monsoon fluctuations (ΔR ∈ {-20%, -10%, +10%, +20%}) to evaluate crop yield deltas, reservoir depletion rates, and public health thermal indicators.

---

## 📂 Project Structure

```text
climate_twin/
│
├── app.py                      # Main Streamlit Entrypoint
├── requirements.txt            # Package Dependencies
├── README.md                   # Project Overview
├── data/
│   ├── data_pipeline.py        # Ingestion, cleaning, feature engineering
│   └── climate_data.db         # SQLite database containing climate records
├── models/
│   ├── prediction_engine.py    # Training and forecasting using RF/XGBoost
│   ├── temp_rf_model.pkl       # Saved RF temperature model
│   ├── temp_xgb_model.pkl      # Saved XGBoost temperature model
│   ├── rain_rf_model.pkl       # Saved RF rainfall model
│   ├── rain_xgb_model.pkl      # Saved XGBoost rainfall model
│   └── training_metrics.pkl    # Serialized model metrics
├── simulator/
│   ├── digital_twin_engine.py  # Simulation of current and future states
│   ├── what_if_simulator.py    # What-if risk assessment engine
│   └── climate_intelligence.py # AI anomaly detection and warning alerts
├── maps/
│   └── map_renderer.py         # Folium map visualization logic
├── dashboard/
│   ├── styles.py               # Custom CSS and ISRO dark-blue styles
│   └── pages/                  # Modular page content functions
│       ├── home.py
│       ├── overview.py
│       ├── rainfall_analytics.py
│       ├── temperature_analytics.py
│       ├── predictions.py
│       ├── digital_twin.py
│       └── scenario_simulator.py
└── docs/
    ├── system_design.md        # Technical architecture
    ├── installation_guide.md   # Deployment steps
    └── api_documentation.md    # Code interface docs
```

---

## 🛠️ Quick Installation

### Prerequisites
- Python 3.9+
- Pip (Python Package Manager)

### Setup & Run Steps
1. Navigate into the project folder:
   ```bash
   cd climate_twin
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database and populate historical climate records:
   ```bash
   python data/data_pipeline.py
   ```
4. Train the Machine Learning models (generates model checkpoints in `models/`):
   ```bash
   python models/prediction_engine.py
   ```
5. Launch the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Presentation Highlights (For Hackathon Judges)
- **ISRO dark-blue Space Aesthetic**: Built custom theme stylesheets replacing Streamlit's base colors to feel like an orbital operations room dashboard.
- **Glassmorphic Interactive Maps**: The Folium anomaly layer overlays interactive tooltips and styled markers summarizing key regional deviations.
- **Vulnerability Scenario Sandboxing**: Run stress scenarios in real-time and download structured TXT stress report logs instantly.
