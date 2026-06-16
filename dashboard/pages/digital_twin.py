import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
from dashboard.styles import render_header, render_metric_card, render_alert_card
from maps.map_renderer import render_rainfall_heatmap, render_temperature_heatmap, render_anomaly_map
from simulator.climate_intelligence import ClimateIntelligence

def show_digital_twin(engine):
    """Renders the core Digital Twin interactive dashboard."""
    render_header("Digital Twin Operations Room", "Monitor Live and Forecasted Climatic Telemetry Across Indian Regions")
    
    # 1. Sidebar Map Controls
    st.sidebar.markdown("### 🗺️ Digital Twin Map Controls")
    map_type = st.sidebar.radio(
        "Select Layer Layer", 
        ["Climate Anomaly Map", "Temperature Heatmap", "Rainfall Heatmap"],
        key="dt_map_layer"
    )
    
    # Date selection - using dates in 2025 where we have full records
    st.markdown("### 📅 Temporal Simulation Control")
    st.write("Slide to change the state of the Digital Twin. The system will retrieve historical records and generate predictive warnings.")
    
    selected_date = st.slider(
        "Simulation Date",
        min_value=pd.to_datetime("2025-01-01").date(),
        max_value=pd.to_datetime("2025-12-31").date(),
        value=pd.to_datetime("2025-06-15").date(),
        format="YYYY-MM-DD"
    )
    
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Load state data for the selected date
    with st.spinner("Retrieving virtual state data..."):
        df_state = engine.get_current_state(date_str)
        
    if df_state.empty:
        st.error(f"Failed to load Digital Twin state for {date_str}. Database might be missing records.")
        return
        
    # Initialize Climate Intelligence alert engine
    intel = ClimateIntelligence()
    alerts = intel.generate_alerts(df_state)
    
    # 2. Main Layout: Map (Left) and Metrics/Alerts (Right)
    col_map, col_details = st.columns([5, 3])
    
    with col_map:
        st.markdown(f"#### Spatial Climate Visualizer ({map_type} - {date_str})")
        
        # Render map using Folium based on selection
        try:
            if map_type == "Temperature Heatmap":
                m = render_temperature_heatmap(df_state)
            elif map_type == "Rainfall Heatmap":
                m = render_rainfall_heatmap(df_state)
            else:
                m = render_anomaly_map(df_state)
                
            folium_static(m, width=650, height=450)
        except Exception as e:
            st.error(f"Error rendering map: {e}")
            
    with col_details:
        st.markdown("#### 📡 System Telemetry Cards")
        
        national_avg_temp = df_state['max_temp'].mean()
        national_avg_rain = df_state['rainfall'].mean()
        anomaly_max_state = df_state.loc[df_state['max_temp_anomaly'].idxmax()]
        
        render_metric_card("National Avg Max Temp", f"{national_avg_temp:.1f}", "°C")
        render_metric_card("National Avg Rainfall", f"{national_avg_rain:.1f}", "mm")
        render_metric_card("Peak Warm Anomaly State", 
                           f"{anomaly_max_state['state']}", 
                           "", 
                           f"Departure: {anomaly_max_state['max_temp_anomaly']:+.1f}°C", 
                           "up" if anomaly_max_state['max_temp_anomaly'] > 0 else "stable")
        
    st.markdown("---")
    
    # 3. Bottom Row: Alerts and Predictions
    col_alerts, col_trends = st.columns(2)
    
    with col_alerts:
        st.markdown("#### ⚠️ Active Climate Warnings")
        if not alerts:
            st.success("🟢 System nominal. No active warning alerts detected across states.")
        else:
            # Show up to 5 warnings in scrollable box
            for alert in alerts[:5]:
                render_alert_card(alert['type'], alert['message'], alert['level'])
            if len(alerts) > 5:
                st.caption(f"...and {len(alerts) - 5} other warning(s) active.")
                
    with col_trends:
        st.markdown("#### 🔮 7-Day Forecasting Forecast")
        st.write("Select a state/region to see the 7-day recursive prediction trend from this date.")
        
        forecast_state = st.selectbox("Select Region for Forecast", sorted(df_state['state'].unique()), key="dt_fc_state")
        
        if st.button("🔮 Run 7-Day Recursive Forecast"):
            with st.spinner("Generating prediction timeline..."):
                try:
                    df_fc = engine.get_forecast_state(date_str, n_days=7)
                    df_fc_state = df_fc[df_fc['state'] == forecast_state]
                    
                    if not df_fc_state.empty:
                        # Draw temperature forecast curve
                        fig_fc = go.Figure()
                        fig_fc.add_trace(go.Scatter(
                            x=df_fc_state['date'], y=df_fc_state['max_temp'],
                            mode='lines+markers', name='Predicted Max Temp',
                            line=dict(color='#ef4444', width=3)
                        ))
                        fig_fc.add_trace(go.Scatter(
                            x=df_fc_state['date'], y=df_fc_state['min_temp'],
                            mode='lines+markers', name='Predicted Min Temp',
                            line=dict(color='#0ea5e9', width=2)
                        ))
                        fig_fc.update_layout(
                            template="plotly_dark",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(gridcolor='#1e293b'),
                            yaxis=dict(gridcolor='#1e293b', title="Temp (°C)"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig_fc, use_container_width=True)
                    else:
                        st.error("No forecast predictions found for selected state.")
                except Exception as e:
                    st.error(f"Forecast engine failed: {e}")
