import os
import pandas as pd
import numpy as np

class ClimateIntelligence:
    def __init__(self):
        pass
        
    def generate_alerts(self, df_state):
        """Analyzes a state climate dataframe (observed or forecasted) and generates a list of alert events."""
        alerts = []
        if df_state.empty:
            return alerts
            
        for _, row in df_state.iterrows():
            state = row['state']
            max_temp = row['max_temp']
            min_temp = row['min_temp']
            rainfall = row['rainfall']
            
            # Extract anomalies if present in columns, else default to 0
            max_temp_anomaly = row.get('max_temp_anomaly', 0.0)
            rainfall_anomaly = row.get('rainfall_anomaly', 0.0)
            
            # 1. Extreme Temperature / Heatwave Warnings
            if max_temp >= 45.0:
                alerts.append({
                    "state": state,
                    "level": "RED",
                    "type": "Extreme Heatwave",
                    "message": f"Critical heatwave warning for {state}: Temperature reached {max_temp}°C. Avoid outdoor activity."
                })
            elif max_temp >= 40.0 and max_temp_anomaly >= 4.5:
                alerts.append({
                    "state": state,
                    "level": "ORANGE",
                    "type": "Heatwave Warning",
                    "message": f"Heatwave warning for {state}: Max Temp is {max_temp}°C ({max_temp_anomaly:+.1f}°C departure from normal)."
                })
            elif max_temp_anomaly >= 5.0:
                alerts.append({
                    "state": state,
                    "level": "YELLOW",
                    "type": "Thermal Anomaly",
                    "message": f"Unusual warming in {state}: Temp is {max_temp_anomaly:+.1f}°C above seasonal norms."
                })
                
            # 2. Extreme Rainfall / Flash Flood Warnings
            if rainfall >= 150.0:
                alerts.append({
                    "state": state,
                    "level": "RED",
                    "type": "Severe Flash Flood",
                    "message": f"Extremely heavy rainfall warning for {state}: {rainfall}mm of precipitation recorded/predicted. Risk of flash floods."
                })
            elif rainfall >= 75.0:
                alerts.append({
                    "state": state,
                    "level": "ORANGE",
                    "type": "Heavy Rainfall",
                    "message": f"Heavy rain alert for {state}: {rainfall}mm expected. Urban flooding and water logging risk."
                })
            elif rainfall > 0 and rainfall_anomaly >= 40.0:
                alerts.append({
                    "state": state,
                    "level": "YELLOW",
                    "type": "Precipitation Anomaly",
                    "message": f"High rainfall anomaly in {state}: Precipitation is {rainfall_anomaly:+.1f}mm above normal."
                })
                
            # 3. Severe Drought Warnings
            # Only trigger if normal rainfall is significant (>15mm), indicating we are in a wet season but receiving no rain
            normal_rainfall = row.get('normal_rainfall', 0.0)
            if normal_rainfall > 15.0 and rainfall == 0.0:
                alerts.append({
                    "state": state,
                    "level": "ORANGE",
                    "type": "Agricultural Drought",
                    "message": f"Severe dry spell in {state}: Zero rainfall against monthly normal of {normal_rainfall:.1f}mm."
                })
                
        return alerts

    def detect_anomalies_statistically(self, df_history, current_state_df):
        """Uses statistical thresholding (z-scores) on historical data to find significant climate anomalies."""
        anomalies = []
        if df_history.empty or current_state_df.empty:
            return anomalies
            
        # Group history by state & month to calculate mean & standard deviation
        stats = df_history.groupby(['state', 'month']).agg({
            'max_temp': ['mean', 'std'],
            'rainfall': ['mean', 'std']
        })
        stats.columns = ['_'.join(col) for col in stats.columns]
        stats = stats.reset_index()
        
        # Merge with current state
        merged = pd.merge(current_state_df, stats, on=['state', 'month'], how='left')
        
        for _, row in merged.iterrows():
            state = row['state']
            
            # Temperature anomaly Z-score
            t_mean = row['max_temp_mean']
            t_std = row['max_temp_std']
            if pd.notna(t_std) and t_std > 0:
                t_z = (row['max_temp'] - t_mean) / t_std
                if abs(t_z) > 2.5:
                    direction = "warming" if t_z > 0 else "cooling"
                    anomalies.append({
                        "state": state,
                        "metric": "Temperature",
                        "value": row['max_temp'],
                        "z_score": round(t_z, 2),
                        "description": f"Statistical outlier: {state} is showing extreme {direction} (Z-Score = {t_z:.2f})."
                    })
                    
            # Rainfall anomaly Z-score
            r_mean = row['rainfall_mean']
            r_std = row['rainfall_std']
            if pd.notna(r_std) and r_std > 0 and row['rainfall'] > 0:
                r_z = (row['rainfall'] - r_mean) / r_std
                if r_z > 3.0:
                    anomalies.append({
                        "state": state,
                        "metric": "Rainfall",
                        "value": row['rainfall'],
                        "z_score": round(r_z, 2),
                        "description": f"Statistical outlier: {state} has abnormal precipitation intensity (Z-Score = {r_z:.2f})."
                    })
                    
        return anomalies
