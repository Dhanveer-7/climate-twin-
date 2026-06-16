# System Design: Climate Digital Twin

This document details the software architecture, database design, feature engineering equations, machine learning algorithms, and vulnerability stress models of the **AI-Powered Digital Twin of India's Climate**.

---

## 1. System Architecture

The digital twin is built upon a modular data-to-simulation pipeline:

```text
  [IMD Raw Files]
        │
        ▼ (data_pipeline.py)
  [Interpolation & Cleaning]
        │
        ▼ (SQLite: climate_data.db)
  [SQLite Data Store]
        │
        ├───────────────────────────┐
        ▼ (prediction_engine.py)     ▼ (digital_twin_engine.py)
  [Lag / Rolling Features]      [Historical Baselines (16-yr Normal)]
        │                                   │
        ▼                                   ▼
  [ML Forecasting Models] ────────> [State Vector (Observed + Predicted)]
  (Random Forest & XGBoost)                 │
                                            ├───────────────────────────┐
                                            ▼ (what_if_simulator.py)    ▼ (climate_intelligence.py)
                                      [Stress Testing]             [AI Warning Alerts]
                                      (Crop, Water, Health)
                                            │                           │
                                            └─────────────┬─────────────┘
                                                          ▼
                                                   [Streamlit GUI]
```

---

## 2. Data Store & Features Engineering

### SQLite Table Schema
The database contains the `daily_climate` table:
```sql
CREATE TABLE daily_climate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    state TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    max_temp REAL,
    min_temp REAL,
    rainfall REAL,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_year INTEGER
);
```

### Engineered Features
1. **Lag Variables**:
   $$X_{t, \text{lag}} = [Y_{t-1}, Y_{t-7}, Y_{t-30}]$$
2. **Rolling Statistics**:
   $$\mu_{t, N} = \frac{1}{N}\sum_{i=0}^{N-1} Y_{t-i}, \quad \sigma_{t, N} = \sqrt{\frac{1}{N}\sum_{i=0}^{N-1} (Y_{t-i} - \mu_{t, N})^2}$$
   where $N \in \{7, 30\}$ days.
3. **Seasonal Trigonometric Components**:
   $$\theta = \frac{2\pi \cdot \text{day\_of\_year}}{365.25}$$
   $$S = \sin(\theta), \quad C = \cos(\theta)$$

---

## 3. Climate Prediction Engine

The system uses **XGBoost** and **Random Forest Regressors** to predict future states recursively.

### Recursive Multi-Step Forecast Loop
Because our models use autoregressive lag and rolling features, predicting multiple steps ($H$ steps) ahead requires a recursive loop:

Given history $H_t$ up to time $t$:
1. For step $h = 1 \dots H$:
   - Construct feature vector $\mathbf{x}_{t+h}$ from buffer $H_{t+h-1}$ (using coordinates, lags $h-1, h-7, h-30$, rolling mean/std, and trigonometric day of year).
   - Feed $\mathbf{x}_{t+h}$ into trained models:
     $$\hat{T}_{\text{max}, t+h} = f_{\text{model}}(\mathbf{x}_{t+h})$$
     $$\hat{T}_{\text{min}, t+h} = g_{\text{model}}(\mathbf{x}_{t+h})$$
     $$\hat{P}_{t+h} = h_{\text{model}}(\mathbf{x}_{t+h})$$
   - Post-process predictions:
     $$\hat{P}_{t+h} = \max(0.0, \hat{P}_{t+h})$$
     $$\hat{T}_{\text{max}, t+h} = \max(\hat{T}_{\text{min}, t+h} + 1.0, \hat{T}_{\text{max}, t+h})$$
   - Append predicted values $\{\hat{T}_{\text{max}, t+h}, \hat{T}_{\text{min}, t+h}, \hat{P}_{t+h}\}$ back to buffer $H_{t+h}$.
2. Return predicted series.

---

## 4. What-If Stress Testing Models

The simulator applies offsets to observed/predicted states to calculate sectoral risk.

### Risk Rules
1. **Heatwave Risk (IMD adjusted)**:
   $$\text{If } T_{\text{max}} \ge 40^\circ\text{C}: \begin{cases} 
      \Delta T_{\text{anomaly}} \ge 6.4^\circ\text{C} & \rightarrow \text{Severe Risk} \\
      \Delta T_{\text{anomaly}} \ge 4.5^\circ\text{C} & \rightarrow \text{Moderate Risk} \\
      \text{Otherwise} & \rightarrow \text{Low Risk} 
   \end{cases}$$
2. **Flood Risk**:
   $$\text{Precipitation } P \ge 150\text{ mm} \rightarrow \text{Extreme Risk}$$
   $$\text{Precipitation } 80\text{ mm} \le P < 150\text{ mm} \rightarrow \text{High Risk}$$
   $$\text{Precipitation } 40\text{ mm} \le P < 80\text{ mm} \rightarrow \text{Moderate Risk}$$
3. **Drought Risk**:
   $$\text{If } \text{Normal Rainfall } R_{\text{normal}} > 15\text{ mm} \text{ and } P < 0.3 \cdot R_{\text{normal}}: \text{Drought Alert}$$

### Sectoral Impact Models
- **Crop Yield Impact %**: Accumulates negative yield reductions depending on active risks:
  $$\Delta Y_{\text{crop}} = \text{Penalty}_{\text{heatwave}} + \text{Penalty}_{\text{drought}} + \text{Penalty}_{\text{flood}}$$
- **Reservoir Capacity %**: Models depletion under dry periods or accumulation under storm events.
- **Human Health Index**: Evaluates thermal and storm hazards on a score out of 100.
