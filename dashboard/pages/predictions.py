import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dashboard.styles import render_header, render_metric_card
from models.prediction_engine import load_metrics, forecast_recursive

def show_predictions(engine):
    """Renders the Climate Predictions & model evaluation page."""
    render_header("Climate Prediction Engine", "Evaluate ML Models (XGBoost vs Random Forest) and Sandbox Forecast Performance")
    
    # 1. Load Training Metrics
    metrics = load_metrics()
    
    if metrics is None:
        st.warning("⚠️ Machine Learning models have not been trained yet. Please run the training script or click below to train.")
        if st.button("🚀 Train ML Prediction Engine"):
            with st.spinner("Training Random Forest and XGBoost models for Max Temp, Min Temp, and Rainfall. This may take a few minutes..."):
                from models.prediction_engine import train_and_save_models
                try:
                    metrics = train_and_save_models()
                    engine.refresh_normals() # update normals
                    st.success("Models trained successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error training models: {e}")
        return
        
    st.subheader("📊 Model Performance Metrics (Test Set: Year 2025)")
    
    # Convert metrics dictionary to structured table
    metric_rows = []
    for target, models in metrics.items():
        for m_name, vals in models.items():
            metric_rows.append({
                "Target Variable": target.replace("_", " ").title(),
                "Model Type": "Random Forest" if m_name == "rf" else "XGBoost",
                "Mean Absolute Error (MAE)": f"{vals['mae']:.3f}",
                "Root Mean Sq Error (RMSE)": f"{vals['rmse']:.3f}",
                "R-Squared (R2)": f"{vals['r2']:.3f}"
            })
            
    df_metrics = pd.DataFrame(metric_rows)
    st.table(df_metrics)
    
    st.markdown("---")
    
    # 2. Interactive Prediction Sandbox
    st.subheader("🔮 Interactive Recursive Forecast Sandbox")
    st.write("Select a state, a starting date in 2025, and run forecasts. The engine will compare predictions against actual ground-truth observations.")
    
    # Get states and dates
    df_raw = pd.read_sql_query("SELECT * FROM daily_climate WHERE year = 2025", engine.db_conn)
    states = sorted(df_raw['state'].unique())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sandbox_state = st.selectbox("Select State/UT", states, key="sb_state")
    with col2:
        # Available start dates in 2025 (select a range where we have at least 30 days of data after it, e.g. June 2025)
        sandbox_date = st.date_input("Forecast Start Date", pd.to_datetime("2025-06-01"))
    with col3:
        model_type = st.selectbox("Model Type", ["XGBoost", "Random Forest"], key="sb_model")
        
    model_key = 'xgb' if model_type == "XGBoost" else 'rf'
    
    if st.button("🔮 Run Forecast & Compare"):
        start_date_str = sandbox_date.strftime("%Y-%m-%d")
        
        with st.spinner("Generating recursive multi-step forecast..."):
            try:
                # 30-day forecast horizon
                df_pred = forecast_recursive(sandbox_state, start_date_str, n_days=30, model_type=model_key)
                
                # Fetch actual ground truth from DB
                end_date = sandbox_date + pd.Timedelta(days=29)
                end_date_str = end_date.strftime("%Y-%m-%d")
                
                query = """
                    SELECT date, max_temp, min_temp, rainfall 
                    FROM daily_climate 
                    WHERE state = ? AND date BETWEEN ? AND ?
                    ORDER BY date
                """
                df_actual = pd.read_sql_query(query, engine.db_conn, params=(sandbox_state, start_date_str, end_date_str))
                df_actual['date'] = pd.to_datetime(df_actual['date'])
                df_pred['date'] = pd.to_datetime(df_pred['date'])
                
                # Merge actual and predicted
                df_compare = pd.merge(df_actual, df_pred, on='date', suffixes=('_actual', '_pred'))
                
                # Plot comparisons
                # Tab layout for Max Temp, Min Temp, Rainfall
                t_max, t_min, t_rain = st.tabs(["Maximum Temperature", "Minimum Temperature", "Rainfall"])
                
                with t_max:
                    fig_max = go.Figure()
                    fig_max.add_trace(go.Scatter(x=df_compare['date'], y=df_compare['max_temp_actual'], name='Actual Max Temp', line=dict(color='#94a3b8', width=2)))
                    fig_max.add_trace(go.Scatter(x=df_compare['date'], y=df_compare['max_temp_pred'], name=f'Predicted Max Temp ({model_type})', line=dict(color='#ef4444', width=3, dash='dash')))
                    fig_max.update_layout(
                        title=f"30-Day Max Temperature Forecast for {sandbox_state}",
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor='#1e293b'), yaxis=dict(gridcolor='#1e293b', title="Temp (°C)"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_max, use_container_width=True)
                    
                with t_min:
                    fig_min = go.Figure()
                    fig_min.add_trace(go.Scatter(x=df_compare['date'], y=df_compare['min_temp_actual'], name='Actual Min Temp', line=dict(color='#94a3b8', width=2)))
                    fig_min.add_trace(go.Scatter(x=df_compare['date'], y=df_compare['min_temp_pred'], name=f'Predicted Min Temp ({model_type})', line=dict(color='#0ea5e9', width=3, dash='dash')))
                    fig_min.update_layout(
                        title=f"30-Day Min Temperature Forecast for {sandbox_state}",
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor='#1e293b'), yaxis=dict(gridcolor='#1e293b', title="Temp (°C)"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_min, use_container_width=True)
                    
                with t_rain:
                    fig_rain = go.Figure()
                    fig_rain.add_trace(go.Bar(x=df_compare['date'], y=df_compare['rainfall_actual'], name='Actual Rainfall', marker_color='rgba(148, 163, 184, 0.4)'))
                    fig_rain.add_trace(go.Scatter(x=df_compare['date'], y=df_compare['rainfall_pred'], name=f'Predicted Rainfall ({model_type})', line=dict(color='#3b82f6', width=3, dash='dot')))
                    fig_rain.update_layout(
                        title=f"30-Day Rainfall Forecast for {sandbox_state}",
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor='#1e293b'), yaxis=dict(gridcolor='#1e293b', title="Rainfall (mm)"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_rain, use_container_width=True)
                    
                # Calculate Sandbox Metrics
                mae_max = np.mean(np.abs(df_compare['max_temp_actual'] - df_compare['max_temp_pred']))
                mae_rain = np.mean(np.abs(df_compare['rainfall_actual'] - df_compare['rainfall_pred']))
                
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.metric(f"Sandbox MAE Max Temp", f"{mae_max:.2f}°C")
                with sc2:
                    st.metric(f"Sandbox MAE Rainfall", f"{mae_rain:.2f} mm")
                    
            except Exception as e:
                st.error(f"Error executing forecast: {e}")
