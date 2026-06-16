import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.data_pipeline import get_connection, load_raw_data, clean_data
from models.prediction_engine import forecast_recursive

class DigitalTwinEngine:
    def __init__(self):
        self.db_conn = get_connection()
        self.historical_normals = None
        self._calculate_historical_normals()
        
    def _calculate_historical_normals(self):
        """Calculates monthly climatology normals (mean max_temp, min_temp, rainfall) for each state."""
        print("Calculating historical climatological normals...")
        query = """
            SELECT state, month, AVG(max_temp) as normal_max_temp, 
                   AVG(min_temp) as normal_min_temp, AVG(rainfall) as normal_rainfall
            FROM daily_climate
            WHERE year < 2025
            GROUP BY state, month
        """
        try:
            self.historical_normals = pd.read_sql_query(query, self.db_conn)
            print("Historical normals calculated successfully.")
        except Exception as e:
            print(f"Error calculating historical normals: {e}. SQLite database might not be fully initialized yet.")
            # Fallback placeholder structure
            self.historical_normals = pd.DataFrame(columns=['state', 'month', 'normal_max_temp', 'normal_min_temp', 'normal_rainfall'])

    def refresh_normals(self):
        """Refreshes historical normals (useful after db reload)."""
        self._calculate_historical_normals()

    def get_state_normals(self, state, month):
        """Returns the normal values for a specific state and month."""
        if self.historical_normals is None or len(self.historical_normals) == 0:
            self._calculate_historical_normals()
            
        res = self.historical_normals[(self.historical_normals['state'] == state) & 
                                      (self.historical_normals['month'] == month)]
        if len(res) > 0:
            row = res.iloc[0]
            return {
                'max_temp': float(row['normal_max_temp']),
                'min_temp': float(row['normal_min_temp']),
                'rainfall': float(row['normal_rainfall'])
            }
        # Generic fallback
        return {'max_temp': 30.0, 'min_temp': 20.0, 'rainfall': 2.0}

    def get_current_state(self, date_str):
        """Retrieves the observed climate state for all states on a specific date."""
        query = "SELECT * FROM daily_climate WHERE date = ?"
        df_date = pd.read_sql_query(query, self.db_conn, params=(date_str,))
        
        if len(df_date) == 0:
            # If the database does not have this date, return an empty DataFrame or search closest date
            return pd.DataFrame()
            
        # Join with historical normals to calculate anomalies
        df_merged = pd.merge(df_date, self.historical_normals, on=['state', 'month'], how='left')
        
        # Calculate anomalies
        df_merged['max_temp_anomaly'] = df_merged['max_temp'] - df_merged['normal_max_temp']
        df_merged['min_temp_anomaly'] = df_merged['min_temp'] - df_merged['normal_min_temp']
        df_merged['rainfall_anomaly'] = df_merged['rainfall'] - df_merged['normal_rainfall']
        
        # Round values
        for col in ['max_temp_anomaly', 'min_temp_anomaly', 'rainfall_anomaly']:
            df_merged[col] = df_merged[col].round(1)
            
        return df_merged

    def get_forecast_state(self, start_date_str, n_days=7, model_type='xgb'):
        """Generates forecasts for all 36 states starting from start_date for n_days."""
        # Run recursive forecasts for all states and concatenate results
        states = list(self.historical_normals['state'].unique())
        if not states:
            # Fallback if normals not loaded
            states = ["Delhi", "Maharashtra", "Kerala", "Rajasthan", "Meghalaya"] # basic sample
            
        forecasts = []
        for state in states:
            try:
                state_forecast = forecast_recursive(state, start_date_str, n_days, model_type)
                forecasts.append(state_forecast)
            except Exception as e:
                print(f"Error forecasting for state {state}: {e}")
                
        if not forecasts:
            return pd.DataFrame()
            
        df_forecast = pd.concat(forecasts, ignore_index=True)
        
        # Merge normals to calculate forecasted anomalies
        df_forecast = pd.merge(df_forecast, self.historical_normals, on=['state', 'month'], how='left')
        
        df_forecast['max_temp_anomaly'] = df_forecast['max_temp'] - df_forecast['normal_max_temp']
        df_forecast['min_temp_anomaly'] = df_forecast['min_temp'] - df_forecast['normal_min_temp']
        df_forecast['rainfall_anomaly'] = df_forecast['rainfall'] - df_forecast['normal_rainfall']
        
        # Round values
        for col in ['max_temp_anomaly', 'min_temp_anomaly', 'rainfall_anomaly']:
            df_forecast[col] = df_forecast[col].round(1)
            
        return df_forecast

    def close(self):
        self.db_conn.close()

if __name__ == "__main__":
    # Test digital twin engine
    engine = DigitalTwinEngine()
    print("Testing get_current_state for 2025-06-15...")
    state_df = engine.get_current_state("2025-06-15")
    print(state_df.head())
    engine.close()
