# Installation & Deployment Guide

This guide describes how to install, configure, and launch the **AI-Powered Digital Twin of India's Climate** application.

---

## 1. System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+ recommended).
- **Python Version**: Python 3.9, 3.10, 3.11, or 3.12.
- **Memory (RAM)**: Minimum 4GB (8GB recommended for model training).
- **Disk Space**: ~1.5GB of free space (database + model checkpoints + environment).

---

## 2. Step-by-Step Installation

### Step A: Clone or Navigate to the Workspace
Open your terminal (PowerShell, Command Prompt, or bash) and navigate to the project directory:
```bash
cd "c:/Users/Dhanveer/OneDrive/Desktop/AI-Powered Digital Twin of India's Climate/climate_twin"
```

### Step B: Create a Virtual Environment (Optional but Recommended)
It is best practice to use a virtual environment to avoid package version conflicts.

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step C: Install Package Dependencies
Install the required scientific packages (Pandas, Numpy, Scikit-Learn, XGBoost, Plotly, Folium, and Streamlit):
```bash
pip install -r requirements.txt
```

---

## 3. Ingestion & Model Training

Before launching the web app, you must create the SQLite database and train the machine learning models.

### Step A: Initialize Database & Ingest Climate Records
Run the data pipeline to generate synthetic IMD-style daily weather data for all 36 Indian states from 2010 to 2026:
```bash
python data/data_pipeline.py
```
*This creates the `climate_data.db` database inside the `data/` directory.*

### Step B: Train the Prediction Models
Train Random Forest and XGBoost regressors on years 2010–2024 to predict Max Temperature, Min Temperature, and Rainfall.
```bash
python models/prediction_engine.py
```
*This saves trained models (`.pkl` format) and `training_metrics.pkl` inside the `models/` directory.*

---

## 4. Run the Streamlit Application

Launch the Streamlit web dashboard locally:
```bash
streamlit run app.py
```

Streamlit will automatically launch the dashboard in your default browser at:
`http://localhost:8501`

---

## 5. Troubleshooting & FAQs

### Q1: `ModuleNotFoundError: No module named 'xgboost'`
**Solution**: Ensure you are running python in the correct virtual environment where `requirements.txt` was installed. Try running `pip show xgboost` to verify.

### Q2: XGBoost fails to install on Windows
**Solution**: XGBoost requires the Microsoft Visual C++ Redistributable. If it fails, install the Visual Studio Build Tools or install precompiled wheels:
```bash
pip install xgboost --only-binary=:all:
```

### Q3: Streamlit runs but page shows "Waiting for database initialization"
**Solution**: The database file `climate_data.db` is missing or empty. Stop Streamlit and run `python data/data_pipeline.py` first to initialize it.
