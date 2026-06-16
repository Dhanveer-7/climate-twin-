import os
import sys
import pandas as pd

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.data_pipeline import get_preprocessed_data, DB_PATH
from models.prediction_engine import forecast_recursive, MODELS_DIR
from simulator.digital_twin_engine import DigitalTwinEngine
from simulator.what_if_simulator import WhatIfSimulator
from simulator.climate_intelligence import ClimateIntelligence

def test_pipeline():
    print("==================================================")
    print("      AUTOMATED SYSTEM INTEGRATION TESTING")
    print("==================================================")
    
    # 1. Database Check
    print("1. Checking Database Existence...")
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database at {DB_PATH} not found!")
    print(f"   Success: Database found at {DB_PATH}.")

    # 2. Check Pre-trained models exist
    print("\n2. Checking Saved Model Checkpoints...")
    required_models = [
        "max_temp_rf_model.pkl", "max_temp_xgb_model.pkl",
        "min_temp_rf_model.pkl", "min_temp_xgb_model.pkl",
        "rainfall_rf_model.pkl", "rainfall_xgb_model.pkl",
        "training_metrics.pkl"
    ]
    for model_file in required_models:
        model_path = os.path.join(MODELS_DIR, model_file)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file {model_file} not found in {MODELS_DIR}!")
    print("   Success: All 6 model checkpoints and training metrics exist.")

    # 3. Test Digital Twin Engine Loading
    print("\n3. Testing Digital Twin Engine and Climatological Norms...")
    engine = DigitalTwinEngine()
    if engine.historical_normals is None or len(engine.historical_normals) == 0:
        raise ValueError("Historical normals dataframe is empty!")
    print(f"   Success: Norms computed for {len(engine.historical_normals)} state-month pairs.")

    # 4. Test Recursive Forecasting
    print("\n4. Testing 7-Day Recursive Prediction Loop (State: Maharashtra)...")
    df_fc = forecast_recursive("Maharashtra", "2025-06-15", n_days=7, model_type='xgb')
    if df_fc.empty:
        raise ValueError("Forecasting returned an empty dataframe!")
    if len(df_fc) != 7:
        raise ValueError(f"Forecasting returned {len(df_fc)} rows instead of 7!")
    print("   Success: Forecast returned predictions.")
    print(df_fc[['date', 'max_temp', 'min_temp', 'rainfall']])

    # 5. Test What-If Risk Simulator
    print("\n5. Testing What-If Simulator (+2°C Temp, -10% Rainfall)...")
    df_base = engine.get_current_state("2025-06-15")
    if df_base.empty:
        raise ValueError("Baseline state is empty!")
        
    simulator = WhatIfSimulator(engine)
    df_sim = simulator.run_simulation(df_base, temp_change=2.0, rain_pct_change=-10.0)
    
    if df_sim.empty:
        raise ValueError("Simulated state dataframe is empty!")
    print(f"   Success: Simulation finished. Average simulated max temp: {df_sim['max_temp'].mean():.1f}°C.")
    
    # 6. Test Climate Intelligence Warning Generator
    print("\n6. Testing Climate Intelligence Alerts...")
    intel = ClimateIntelligence()
    alerts = intel.generate_alerts(df_sim)
    print(f"   Success: Found {len(alerts)} simulated hazard warning events.")
    
    engine.close()
    print("\n==================================================")
    print("   ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    try:
        test_pipeline()
        sys.exit(0)
    except Exception as e:
        print(f"\n[TEST FAILURE]: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
