import os
import pickle
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

# Import data pipeline
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.data_pipeline import get_preprocessed_data, STATE_PROFILES

MODELS_DIR = os.path.dirname(__file__)

FEATURE_COLS = [
    'latitude', 'longitude',
    'max_temp_lag_1', 'max_temp_lag_7', 'max_temp_lag_30',
    'min_temp_lag_1', 'min_temp_lag_7', 'min_temp_lag_30',
    'rainfall_lag_1', 'rainfall_lag_7', 'rainfall_lag_30',
    'max_temp_roll_mean_7', 'max_temp_roll_std_7',
    'max_temp_roll_mean_30', 'max_temp_roll_std_30',
    'rainfall_roll_mean_7', 'rainfall_roll_std_7',
    'rainfall_roll_mean_30', 'rainfall_roll_std_30',
    'sin_day_of_year', 'cos_day_of_year'
]

TARGETS = ['max_temp', 'min_temp', 'rainfall']

def train_and_save_models():
    """Trains Random Forest and XGBoost models for temperature and rainfall, prints evaluation metrics, and saves them."""
    print("Loading and preprocessing data for training...")
    df = get_preprocessed_data()
    
    # Train-test split based on years (Train: 2010-2024, Test: 2025)
    # Using 2026 as out-of-sample data
    train_df = df[df['year'] < 2025]
    test_df = df[df['year'] == 2025]
    
    if len(train_df) == 0 or len(test_df) == 0:
        raise ValueError("Data split is empty. Verify that database is initialized with data.")
        
    X_train = train_df[FEATURE_COLS]
    X_test = test_df[FEATURE_COLS]
    
    results = {}
    
    for target in TARGETS:
        print(f"\n--- Training Models for Target: {target} ---")
        y_train = train_df[target]
        y_test = test_df[target]
        
        # 1. Random Forest Model
        print(f"Training Random Forest Regressor for {target}...")
        # Restricting max_depth and estimators to speed up training & reduce file size
        rf = RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        
        rf_preds = rf.predict(X_test)
        rf_mae = mean_absolute_error(y_test, rf_preds)
        rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
        rf_r2 = r2_score(y_test, rf_preds)
        
        print(f"RF Metrics - MAE: {rf_mae:.3f}, RMSE: {rf_rmse:.3f}, R2: {rf_r2:.3f}")
        
        rf_path = os.path.join(MODELS_DIR, f"{target}_rf_model.pkl")
        with open(rf_path, 'wb') as f:
            pickle.dump(rf, f)
        print(f"Saved Random Forest model to {rf_path}")
            
        # 2. XGBoost Model
        print(f"Training XGBoost Regressor for {target}...")
        xgb_reg = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
        xgb_reg.fit(X_train, y_train)
        
        xgb_preds = xgb_reg.predict(X_test)
        xgb_mae = mean_absolute_error(y_test, xgb_preds)
        xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))
        xgb_r2 = r2_score(y_test, xgb_preds)
        
        print(f"XGBoost Metrics - MAE: {xgb_mae:.3f}, RMSE: {xgb_rmse:.3f}, R2: {xgb_r2:.3f}")
        
        xgb_path = os.path.join(MODELS_DIR, f"{target}_xgb_model.pkl")
        with open(xgb_path, 'wb') as f:
            pickle.dump(xgb_reg, f)
        print(f"Saved XGBoost model to {xgb_path}")
            
        results[target] = {
            "rf": {"mae": rf_mae, "rmse": rf_rmse, "r2": rf_r2},
            "xgb": {"mae": xgb_mae, "rmse": xgb_rmse, "r2": xgb_r2}
        }
        
    # Write training metrics to a text file for reference
    metrics_path = os.path.join(MODELS_DIR, "training_metrics.pkl")
    with open(metrics_path, 'wb') as f:
        pickle.dump(results, f)
        
    print("\nModel training completed and saved.")
    return results

def load_model(target, model_type='xgb'):
    """Loads a pre-trained model checkpoint."""
    model_file = os.path.join(MODELS_DIR, f"{target}_{model_type}_model.pkl")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Model file {model_file} not found. Please train models first.")
    with open(model_file, 'rb') as f:
        return pickle.load(f)

def load_metrics():
    """Loads model performance metrics."""
    metrics_path = os.path.join(MODELS_DIR, "training_metrics.pkl")
    if not os.path.exists(metrics_path):
        return None
    with open(metrics_path, 'rb') as f:
        return pickle.load(f)

def forecast_recursive(state, start_date_str, n_days=7, model_type='xgb'):
    """Generates recursive forecasts for a given state starting from start_date for n_days."""
    # Ensure database/data is loaded
    df = get_preprocessed_data()
    
    # Filter for selected state
    state_df = df[df['state'] == state].copy().sort_values(by='date')
    state_df['date_parsed'] = pd.to_datetime(state_df['date'])
    
    start_date = pd.to_datetime(start_date_str)
    
    # We need historical data prior to start_date to construct lags and rolling features
    past_df = state_df[state_df['date_parsed'] < start_date].copy()
    if len(past_df) < 30:
        raise ValueError(f"Insufficient historical data before {start_date_str} for state {state}. Need at least 30 days.")
        
    # Get state coordinates
    lat = STATE_PROFILES[state]["lat"]
    lon = STATE_PROFILES[state]["lon"]
    
    # Load models
    models = {
        'max_temp': load_model('max_temp', model_type),
        'min_temp': load_model('min_temp', model_type),
        'rainfall': load_model('rainfall', model_type)
    }
    
    # Create list to store forecast results
    forecast_results = []
    
    # Keep a running list of recent observations (we need up to 30 days of history to build features)
    history = past_df.tail(40).to_dict('records')
    
    current_date = start_date
    
    for step in range(n_days):
        day_of_year = current_date.timetuple().tm_yday
        sin_doy = np.sin(2 * np.pi * day_of_year / 365.25)
        cos_doy = np.cos(2 * np.pi * day_of_year / 365.25)
        
        # Build features for current step
        # 1. Lags
        val_t_1 = history[-1]
        val_t_7 = history[-7]
        val_t_30 = history[-30]
        
        # 2. Rolling values (last 7 and 30 days in our history buffer)
        last_7_max = [h['max_temp'] for h in history[-7:]]
        last_7_min = [h['min_temp'] for h in history[-7:]]
        last_7_rain = [h['rainfall'] for h in history[-7:]]
        
        last_30_max = [h['max_temp'] for h in history[-30:]]
        last_30_min = [h['min_temp'] for h in history[-30:]]
        last_30_rain = [h['rainfall'] for h in history[-30:]]
        
        features = {
            'latitude': lat,
            'longitude': lon,
            
            'max_temp_lag_1': val_t_1['max_temp'],
            'max_temp_lag_7': val_t_7['max_temp'],
            'max_temp_lag_30': val_t_30['max_temp'],
            
            'min_temp_lag_1': val_t_1['min_temp'],
            'min_temp_lag_7': val_t_7['min_temp'],
            'min_temp_lag_30': val_t_30['min_temp'],
            
            'rainfall_lag_1': val_t_1['rainfall'],
            'rainfall_lag_7': val_t_7['rainfall'],
            'rainfall_lag_30': val_t_30['rainfall'],
            
            'max_temp_roll_mean_7': np.mean(last_7_max),
            'max_temp_roll_std_7': np.std(last_7_max),
            'max_temp_roll_mean_30': np.mean(last_30_max),
            'max_temp_roll_std_30': np.std(last_30_max),
            
            'rainfall_roll_mean_7': np.mean(last_7_rain),
            'rainfall_roll_std_7': np.std(last_7_rain),
            'rainfall_roll_mean_30': np.mean(last_30_rain),
            'rainfall_roll_std_30': np.std(last_30_rain),
            
            'sin_day_of_year': sin_doy,
            'cos_day_of_year': cos_doy
        }
        
        # Convert features to 2D DataFrame for prediction
        feat_df = pd.DataFrame([features])[FEATURE_COLS]
        
        # Predict max_temp, min_temp, rainfall
        pred_max_temp = float(models['max_temp'].predict(feat_df)[0])
        pred_min_temp = float(models['min_temp'].predict(feat_df)[0])
        pred_rainfall = float(models['rainfall'].predict(feat_df)[0])
        
        # Post-process predictions for safety
        pred_rainfall = max(0.0, pred_rainfall)
        pred_max_temp = max(pred_min_temp + 1.0, pred_max_temp)
        
        # Round predictions
        pred_max_temp = round(pred_max_temp, 1)
        pred_min_temp = round(pred_min_temp, 1)
        pred_rainfall = round(pred_rainfall, 1)
        
        # Create a dictionary for this step
        forecast_record = {
            'date': current_date.strftime("%Y-%m-%d"),
            'state': state,
            'latitude': lat,
            'longitude': lon,
            'max_temp': pred_max_temp,
            'min_temp': pred_min_temp,
            'rainfall': pred_rainfall,
            'year': current_date.year,
            'month': current_date.month,
            'day': current_date.day,
            'day_of_year': day_of_year
        }
        
        forecast_results.append(forecast_record)
        
        # Append prediction to history to update rolling and lags for next iterations
        history.append(forecast_record)
        
        # Increment date
        current_date += timedelta(days=1)
        
    return pd.DataFrame(forecast_results)

if __name__ == "__main__":
    train_and_save_models()
