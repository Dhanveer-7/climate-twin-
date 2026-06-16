import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# List of 36 States/UTs of India with Lat/Lon centers and climatological profiles
STATE_PROFILES = {
    "Andaman & Nicobar Islands": {"lat": 11.74, "lon": 92.65, "t_max_base": 30.5, "t_min_base": 23.5, "t_amp": 1.5, "rain_annual": 2900, "monsoon_peak": 7.0, "monsoon_width": 2.2},
    "Andhra Pradesh": {"lat": 15.91, "lon": 79.74, "t_max_base": 33.5, "t_min_base": 23.0, "t_amp": 6.5, "rain_annual": 950, "monsoon_peak": 8.0, "monsoon_width": 1.8},
    "Arunachal Pradesh": {"lat": 28.21, "lon": 94.72, "t_max_base": 24.0, "t_min_base": 14.5, "t_amp": 8.0, "rain_annual": 2800, "monsoon_peak": 7.0, "monsoon_width": 1.8},
    "Assam": {"lat": 26.20, "lon": 92.93, "t_max_base": 29.5, "t_min_base": 20.0, "t_amp": 7.0, "rain_annual": 2300, "monsoon_peak": 7.0, "monsoon_width": 1.8},
    "Bihar": {"lat": 25.09, "lon": 85.31, "t_max_base": 31.5, "t_min_base": 19.5, "t_amp": 9.5, "rain_annual": 1200, "monsoon_peak": 7.5, "monsoon_width": 1.5},
    "Chandigarh": {"lat": 30.73, "lon": 76.77, "t_max_base": 30.0, "t_min_base": 17.5, "t_amp": 11.5, "rain_annual": 1050, "monsoon_peak": 7.8, "monsoon_width": 1.3},
    "Chhattisgarh": {"lat": 21.27, "lon": 81.86, "t_max_base": 32.5, "t_min_base": 20.5, "t_amp": 8.0, "rain_annual": 1300, "monsoon_peak": 7.8, "monsoon_width": 1.4},
    "Dadra & Nagar Haveli and Daman & Diu": {"lat": 20.39, "lon": 72.83, "t_max_base": 32.0, "t_min_base": 21.0, "t_amp": 4.5, "rain_annual": 2000, "monsoon_peak": 7.5, "monsoon_width": 1.3},
    "Delhi": {"lat": 28.61, "lon": 77.23, "t_max_base": 32.5, "t_min_base": 19.0, "t_amp": 11.5, "rain_annual": 700, "monsoon_peak": 7.8, "monsoon_width": 1.3},
    "Goa": {"lat": 15.29, "lon": 74.12, "t_max_base": 31.5, "t_min_base": 23.5, "t_amp": 2.5, "rain_annual": 2900, "monsoon_peak": 6.8, "monsoon_width": 1.5},
    "Gujarat": {"lat": 22.25, "lon": 71.19, "t_max_base": 34.0, "t_min_base": 20.5, "t_amp": 7.5, "rain_annual": 800, "monsoon_peak": 7.8, "monsoon_width": 1.3},
    "Haryana": {"lat": 29.05, "lon": 76.08, "t_max_base": 31.5, "t_min_base": 18.0, "t_amp": 12.0, "rain_annual": 600, "monsoon_peak": 7.8, "monsoon_width": 1.3},
    "Himachal Pradesh": {"lat": 31.10, "lon": 77.17, "t_max_base": 22.0, "t_min_base": 10.5, "t_amp": 10.0, "rain_annual": 1250, "monsoon_peak": 7.8, "monsoon_width": 1.4},
    "Jammu & Kashmir": {"lat": 33.77, "lon": 76.57, "t_max_base": 19.5, "t_min_base": 8.0, "t_amp": 12.5, "rain_annual": 1000, "monsoon_peak": 7.5, "monsoon_width": 1.5},
    "Jharkhand": {"lat": 23.61, "lon": 85.27, "t_max_base": 31.0, "t_min_base": 19.5, "t_amp": 8.5, "rain_annual": 1200, "monsoon_peak": 7.8, "monsoon_width": 1.4},
    "Karnataka": {"lat": 15.31, "lon": 75.71, "t_max_base": 32.0, "t_min_base": 21.0, "t_amp": 4.5, "rain_annual": 1200, "monsoon_peak": 7.2, "monsoon_width": 1.8},
    "Kerala": {"lat": 10.85, "lon": 76.27, "t_max_base": 31.0, "t_min_base": 23.0, "t_amp": 2.0, "rain_annual": 3000, "monsoon_peak": 6.5, "monsoon_width": 1.7},
    "Ladakh": {"lat": 34.15, "lon": 77.57, "t_max_base": 11.5, "t_min_base": -2.0, "t_amp": 15.0, "rain_annual": 100, "monsoon_peak": 8.0, "monsoon_width": 1.5},
    "Lakshadweep": {"lat": 10.56, "lon": 72.64, "t_max_base": 31.0, "t_min_base": 24.5, "t_amp": 1.5, "rain_annual": 1600, "monsoon_peak": 6.8, "monsoon_width": 1.8},
    "Madhya Pradesh": {"lat": 22.97, "lon": 78.65, "t_max_base": 33.0, "t_min_base": 19.5, "t_amp": 9.5, "rain_annual": 1050, "monsoon_peak": 7.8, "monsoon_width": 1.3},
    "Maharashtra": {"lat": 19.75, "lon": 75.71, "t_max_base": 32.5, "t_min_base": 20.5, "t_amp": 6.5, "rain_annual": 1150, "monsoon_peak": 7.5, "monsoon_width": 1.5},
    "Manipur": {"lat": 24.66, "relative_path": "", "lon": 93.90, "t_max_base": 26.0, "t_min_base": 16.0, "t_amp": 6.5, "rain_annual": 1500, "monsoon_peak": 7.0, "monsoon_width": 1.8},
    "Meghalaya": {"lat": 25.46, "lon": 91.36, "t_max_base": 21.5, "t_min_base": 13.0, "t_amp": 6.0, "rain_annual": 4500, "monsoon_peak": 7.0, "monsoon_width": 2.0},
    "Mizoram": {"lat": 23.16, "lon": 92.93, "t_max_base": 26.5, "t_min_base": 17.5, "t_amp": 6.5, "rain_annual": 2500, "monsoon_peak": 7.0, "monsoon_width": 1.8},
    "Nagaland": {"lat": 26.15, "lon": 94.56, "t_max_base": 25.0, "t_min_base": 15.5, "t_amp": 7.0, "rain_annual": 1900, "monsoon_peak": 7.0, "monsoon_width": 1.8},
    "Odisha": {"lat": 20.95, "lon": 83.39, "t_max_base": 32.0, "t_min_base": 21.5, "t_amp": 7.0, "rain_annual": 1450, "monsoon_peak": 7.8, "monsoon_width": 1.4},
    "Puducherry": {"lat": 11.94, "lon": 79.80, "t_max_base": 32.5, "t_min_base": 24.0, "t_amp": 4.0, "rain_annual": 1300, "monsoon_peak": 10.8, "monsoon_width": 1.5},
    "Punjab": {"lat": 31.14, "lon": 75.34, "t_max_base": 31.5, "t_min_base": 17.5, "t_amp": 12.0, "rain_annual": 650, "monsoon_peak": 7.8, "monsoon_width": 1.3},
    "Rajasthan": {"lat": 27.02, "lon": 74.21, "t_max_base": 34.5, "t_min_base": 19.5, "t_amp": 11.0, "rain_annual": 350, "monsoon_peak": 7.8, "monsoon_width": 1.2},
    "Sikkim": {"lat": 27.53, "lon": 88.51, "t_max_base": 19.5, "t_min_base": 11.5, "t_amp": 7.0, "rain_annual": 2700, "monsoon_peak": 7.0, "monsoon_width": 1.9},
    "Tamil Nadu": {"lat": 11.12, "lon": 78.65, "t_max_base": 33.5, "t_min_base": 23.5, "t_amp": 4.0, "rain_annual": 950, "monsoon_peak": 10.5, "monsoon_width": 1.6},
    "Telangana": {"lat": 18.11, "lon": 79.01, "t_max_base": 33.5, "t_min_base": 22.0, "t_amp": 7.0, "rain_annual": 900, "monsoon_peak": 7.8, "monsoon_width": 1.6},
    "Tripura": {"lat": 23.94, "lon": 91.98, "t_max_base": 30.0, "t_min_base": 20.5, "t_amp": 6.5, "rain_annual": 2200, "monsoon_peak": 7.0, "monsoon_width": 1.8},
    "Uttar Pradesh": {"lat": 26.84, "lon": 80.88, "t_max_base": 32.0, "t_min_base": 18.5, "t_amp": 11.0, "rain_annual": 950, "monsoon_peak": 7.8, "monsoon_width": 1.4},
    "Uttarakhand": {"lat": 30.06, "lon": 79.01, "t_max_base": 23.0, "t_min_base": 11.0, "t_amp": 10.0, "rain_annual": 1400, "monsoon_peak": 7.8, "monsoon_width": 1.4},
    "West Bengal": {"lat": 22.98, "lon": 87.85, "t_max_base": 31.5, "t_min_base": 21.5, "t_amp": 7.5, "rain_annual": 1700, "monsoon_peak": 7.5, "monsoon_width": 1.6}
}

DB_PATH = os.path.join(os.path.dirname(__file__), "climate_data.db")

def get_connection():
    """Establishes connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def generate_synthetic_data(start_year=2010, end_year=2026):
    """Generates daily synthetic climate data for 36 States/UTs with climate trends and noise."""
    print(f"Generating synthetic climate data from {start_year} to {end_year}...")
    np.random.seed(42)
    
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    num_days = delta.days + 1
    
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    records = []
    
    for state, p in STATE_PROFILES.items():
        lat, lon = p["lat"], p["lon"]
        t_max_base, t_min_base = p["t_max_base"], p["t_min_base"]
        t_amp = p["t_amp"]
        rain_annual = p["rain_annual"]
        mon_peak = p["monsoon_peak"]
        mon_w = p["monsoon_width"]
        
        # Pre-calculate baseline values using vectorized operations for speed
        days_of_year = np.array([d.timetuple().tm_yday for d in dates])
        months = np.array([d.month for d in dates])
        years = np.array([d.year for d in dates])
        days = np.array([d.day for d in dates])
        
        # Temperature modeling: baseline + cosine annual wave + climate change warming trend + random noise
        # Cozy cycle: peak temperatures in late May (day of year ~ 145)
        cos_t = np.cos(2 * np.pi * (days_of_year - 145) / 365.25)
        
        # Long term warming trend: +0.02°C per year starting from start_year
        warming = (years - start_year) * 0.02
        
        # Base daily temperature paths
        t_max_vals = t_max_base + t_amp * cos_t + warming + np.random.normal(0, 1.5, num_days)
        t_min_vals = t_min_base + t_amp * cos_t + warming + np.random.normal(0, 1.2, num_days)
        
        # Enforce that max_temp is always higher than min_temp
        t_max_vals = np.maximum(t_max_vals, t_min_vals + 2.0)
        
        # Rainfall modeling: based on Gaussian distribution around monsoon peak month
        # Convert month to daily coordinates (month decimal: month + (day-1)/30)
        month_dec = months + (days - 1) / 30.0
        
        # Probability of rain modeled as Gaussian distribution centered at peak monsoon
        rain_prob = np.exp(-0.5 * ((month_dec - mon_peak) / mon_w) ** 2)
        
        # For states like Tamil Nadu/Puducherry, there is also a smaller secondary peak in summer (SW monsoon)
        if state in ["Tamil Nadu", "Puducherry", "Andhra Pradesh"]:
            # SW Monsoon secondary peak in July (month 7)
            rain_prob_sw = 0.35 * np.exp(-0.5 * ((month_dec - 7.5) / 1.2) ** 2)
            rain_prob = np.maximum(rain_prob, rain_prob_sw)
            
        # Daily average rain amount when it rains
        daily_avg_rain = (rain_annual / (365.25 * rain_prob.mean() + 1e-5)) * rain_prob
        
        # Decide if it rains on each day
        rain_event = np.random.rand(num_days) < np.minimum(0.8, rain_prob * 1.5)
        
        # Exponential rainfall distribution for rainy days
        rain_vals = np.where(rain_event, np.random.exponential(daily_avg_rain / 0.5), 0.0)
        # Round values for cleanliness
        rain_vals = np.round(rain_vals, 1)
        t_max_vals = np.round(t_max_vals, 1)
        t_min_vals = np.round(t_min_vals, 1)
        
        # Inject occasional extreme anomalies (e.g. cloudbursts, severe heatwaves)
        # 0.1% chance of cloudburst (extreme rainfall)
        extreme_rain_idx = np.random.rand(num_days) < 0.001
        rain_vals[extreme_rain_idx] += np.random.uniform(80, 150, np.sum(extreme_rain_idx))
        rain_vals = np.round(rain_vals, 1)
        
        # 0.1% chance of severe heatwave in summer months
        extreme_heat_idx = (np.random.rand(num_days) < 0.003) & np.isin(months, [4, 5, 6])
        t_max_vals[extreme_heat_idx] += np.random.uniform(4, 7, np.sum(extreme_heat_idx))
        t_max_vals = np.round(t_max_vals, 1)
        
        for idx in range(num_days):
            records.append((
                dates[idx].strftime("%Y-%m-%d"),
                state,
                lat,
                lon,
                float(t_max_vals[idx]),
                float(t_min_vals[idx]),
                float(rain_vals[idx]),
                int(years[idx]),
                int(months[idx]),
                int(days[idx]),
                int(days_of_year[idx])
            ))
            
    df = pd.DataFrame(records, columns=[
        "date", "state", "latitude", "longitude", "max_temp", "min_temp", 
        "rainfall", "year", "month", "day", "day_of_year"
    ])
    
    # Introduce small percentage of missing values (0.05%) to demonstrate handling missing values
    for col in ["max_temp", "min_temp", "rainfall"]:
        mask = np.random.rand(len(df)) < 0.0005
        df.loc[mask, col] = np.nan
        
    return df

def initialize_database():
    """Generates the synthetic data and writes it to SQLite database."""
    df = generate_synthetic_data()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("DROP TABLE IF EXISTS daily_climate")
    cursor.execute("""
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
        )
    """)
    
    # Insert records
    print("Writing data to database table 'daily_climate'...")
    df.to_sql("daily_climate", conn, if_exists="append", index=False)
    
    # Create indexes for fast lookup
    cursor.execute("CREATE INDEX idx_date ON daily_climate (date)")
    cursor.execute("CREATE INDEX idx_state ON daily_climate (state)")
    cursor.execute("CREATE INDEX idx_state_date ON daily_climate (state, date)")
    
    conn.commit()
    conn.close()
    print("Database initialization complete.")

def load_raw_data():
    """Loads all data from the SQLite database."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM daily_climate ORDER BY state, date", conn)
    conn.close()
    return df

def clean_data(df):
    """Cleans data by parsing dates and handling missing values using interpolation."""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Handle missing values by interpolating linearly per state
    # Sort first to ensure chronological interpolation
    df = df.sort_values(by=['state', 'date'])
    
    # We group by state and interpolate missing temperatures and rainfall
    df['max_temp'] = df.groupby('state')['max_temp'].transform(lambda x: x.interpolate(method='linear').bfill().ffill())
    df['min_temp'] = df.groupby('state')['min_temp'].transform(lambda x: x.interpolate(method='linear').bfill().ffill())
    df['rainfall'] = df.groupby('state')['rainfall'].transform(lambda x: x.fillna(0.0)) # fill rain NAs with 0
    
    return df

def engineer_features(df):
    """Engineers lag, rolling, and seasonal trigonometric features for prediction modeling."""
    df = df.copy()
    df = df.sort_values(by=['state', 'date'])
    
    # Lag Features (1-day, 7-day, 30-day)
    for lag in [1, 7, 30]:
        df[f'max_temp_lag_{lag}'] = df.groupby('state')['max_temp'].shift(lag)
        df[f'min_temp_lag_{lag}'] = df.groupby('state')['min_temp'].shift(lag)
        df[f'rainfall_lag_{lag}'] = df.groupby('state')['rainfall'].shift(lag)
        
    # Rolling Statistics (7-day and 30-day rolling mean & standard deviation)
    for window in [7, 30]:
        # Temp rolling stats
        df[f'max_temp_roll_mean_{window}'] = df.groupby('state')['max_temp'].transform(lambda x: x.rolling(window, min_periods=1).mean())
        df[f'max_temp_roll_std_{window}'] = df.groupby('state')['max_temp'].transform(lambda x: x.rolling(window, min_periods=1).std().fillna(0.0))
        
        # Rainfall rolling stats
        df[f'rainfall_roll_mean_{window}'] = df.groupby('state')['rainfall'].transform(lambda x: x.rolling(window, min_periods=1).mean())
        df[f'rainfall_roll_std_{window}'] = df.groupby('state')['rainfall'].transform(lambda x: x.rolling(window, min_periods=1).std().fillna(0.0))

    # Trigonometric seasonal features
    # Day of year sine/cosine models annual cyclic nature
    df['sin_day_of_year'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
    df['cos_day_of_year'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
    
    # Fill remaining NaNs (caused by lags) with backfill/forward fill per state
    features_cols = [col for col in df.columns if 'lag_' in col]
    for col in features_cols:
        df[col] = df.groupby('state')[col].transform(lambda x: x.bfill().ffill())
        
    return df

def get_preprocessed_data():
    """Full preprocessing pipeline: Load -> Clean -> Feature Engineering."""
    raw_df = load_raw_data()
    cleaned_df = clean_data(raw_df)
    final_df = engineer_features(cleaned_df)
    return final_df

# Enable Streamlit caching dynamically if running inside a Streamlit app to speed up queries
try:
    import streamlit as st
    get_preprocessed_data = st.cache_data(get_preprocessed_data)
except Exception:
    pass

if __name__ == "__main__":
    initialize_database()
    # Test feature engineering
    df = get_preprocessed_data()
    print(f"Preprocessed DataFrame shape: {df.shape}")
    print(df.head())
