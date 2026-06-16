# API Documentation

This document describes the function signatures, class interfaces, parameters, and return values of the core modules of the Climate Digital Twin project.

---

## 1. Data Ingestion Module (`data/data_pipeline.py`)

### `generate_synthetic_data(start_year=2010, end_year=2026)`
Generates daily historical climate records for all 36 States/UTs.
- **Parameters**:
  - `start_year` (int): Beginning year.
  - `end_year` (int): Ending year.
- **Returns**: `pandas.DataFrame` containing daily date, coordinates, max_temp, min_temp, and rainfall.

### `initialize_database()`
Generates the synthetic dataset and inserts records into SQLite table `daily_climate`. Creates tables and indexes.
- **Returns**: `None`

### `clean_data(df)`
Parses dates and fills missing values.
- **Parameters**: `df` (DataFrame)
- **Returns**: `pandas.DataFrame` (cleaned)

### `engineer_features(df)`
Extracts autoregressive lags, rolling statistics, and seasonal sine/cosine components.
- **Parameters**: `df` (DataFrame)
- **Returns**: `pandas.DataFrame` containing engineered features.

---

## 2. Prediction Engine (`models/prediction_engine.py`)

### `train_and_save_models()`
Loads preprocessed data, trains Random Forest and XGBoost models for Max Temp, Min Temp, and Rainfall targets on data prior to 2025, evaluates on year 2025, and saves serialized models.
- **Returns**: `dict` containing test performance metrics (MAE, RMSE, R2).

### `forecast_recursive(state, start_date_str, n_days=7, model_type='xgb')`
Generates recursive multi-step forecasting by feeding predicted states back into the autoregressive feature vectors.
- **Parameters**:
  - `state` (str): State name.
  - `start_date_str` (str): Starting date YYYY-MM-DD.
  - `n_days` (int): Forecast horizon (typically 7 or 30).
  - `model_type` (str): `'xgb'` (XGBoost) or `'rf'` (Random Forest).
- **Returns**: `pandas.DataFrame` with forecast predictions.

---

## 3. Digital Twin Engine (`simulator/digital_twin_engine.py`)

### `class DigitalTwinEngine()`
Main class representing the virtual state system. Establishes the database connection.

#### `get_state_normals(state, month)`
Retrieves the monthly normal baseline computed from pre-2025 data.
- **Returns**: `dict` with keys `'max_temp'`, `'min_temp'`, and `'rainfall'`.

#### `get_current_state(date_str)`
Loads observed metrics for all states on a specific date and merges anomaly departures.
- **Parameters**: `date_str` (str) - YYYY-MM-DD.
- **Returns**: `pandas.DataFrame`.

#### `get_forecast_state(start_date_str, n_days=7, model_type='xgb')`
Generates predictive states for all 36 states starting from `start_date_str` for `n_days` ahead.
- **Returns**: `pandas.DataFrame`.

---

## 4. What-If Simulator (`simulator/what_if_simulator.py`)

### `class WhatIfSimulator(twin_engine)`
Manages climate vulnerability stress simulations.

#### `run_simulation(base_state_df, temp_change=0.0, rain_pct_change=0.0)`
Applies modifications and computes simulated warnings, agricultural yield shifts, and water capacity levels.
- **Parameters**:
  - `base_state_df` (DataFrame)
  - `temp_change` (float): Additive temperature offset (°C).
  - `rain_pct_change` (float): Percent change in rainfall (-20% to +20%).
- **Returns**: `pandas.DataFrame` containing simulated risk flags.

#### `generate_impact_report(sim_df, temp_change, rain_pct_change)`
Formats simulation outputs into a text-based Impact Report.
- **Returns**: `str` (formatted report text).

---

## 5. Climate Intelligence (`simulator/climate_intelligence.py`)

### `class ClimateIntelligence()`
Implements alert rule engines.

#### `generate_alerts(df_state)`
Flags active hazards (extreme heat, storm cloudbursts, severe agricultural drought) on a per-state level based on climatology.
- **Parameters**: `df_state` (DataFrame)
- **Returns**: `list` of dicts containing keys `'state'`, `'level'`, `'type'`, and `'message'`.
