import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
from dashboard.styles import render_header, render_metric_card
from simulator.what_if_simulator import WhatIfSimulator

def show_scenario_simulator(engine):
    """Renders the What-If Scenario Simulator page."""
    render_header("What-If Scenario Simulator", "Assess the Climate Vulnerability of India's Agriculture, Water Basin Networks, and Public Health")
    
    # Initialize What-If Simulator
    simulator = WhatIfSimulator(engine)
    
    # 1. Sidebar Controls
    st.sidebar.markdown("### 🎛️ Climate Stress Parameters")
    temp_offset = st.sidebar.slider(
        "Temperature Anomalies Increase (ΔT)",
        min_value=0.0, max_value=3.0, value=1.0, step=1.0,
        format="+%d°C"
    )
    
    rain_pct_offset = st.sidebar.slider(
        "Monsoon Rainfall Variance (ΔR)",
        min_value=-20.0, max_value=20.0, value=-10.0, step=10.0,
        format="%+d%%"
    )
    
    st.markdown("### 🧬 Stress Simulation Model Configuration")
    st.write("Configure the baseline climate state date to apply global stress parameters:")
    
    # Date selection
    sim_date = st.date_input("Select Base State Date", pd.to_datetime("2025-06-15"))
    date_str = sim_date.strftime("%Y-%m-%d")
    
    # Fetch base state
    with st.spinner("Fetching baseline telemetry..."):
        df_base = engine.get_current_state(date_str)
        
    if df_base.empty:
        st.error(f"Failed to retrieve climate state for baseline date {date_str}. Database might be missing records.")
        return
        
    # Trigger simulation
    if st.button("🚀 Run Vulnerability Simulation"):
        with st.spinner("Simulating climate risk thresholds..."):
            df_sim = simulator.run_simulation(df_base, temp_change=temp_offset, rain_pct_change=rain_pct_offset)
            
        # 2. Results Dashboard
        # Metrics row
        st.markdown("---")
        st.subheader("📊 Simulated India Climate Stress Metrics")
        
        # Calculate counts
        severe_hw_count = len(df_sim[df_sim['heatwave_risk'] == 'Severe'])
        severe_drought_count = len(df_sim[df_sim['drought_risk'] == 'Severe'])
        severe_flood_count = len(df_sim[df_sim['flood_risk'] == 'Extreme'])
        
        sm1, sm2, sm3 = st.columns(3)
        with sm1:
            render_metric_card("Severe Heatwave States", f"{severe_hw_count}", "States", "Departure >= 6.4°C", "up" if severe_hw_count > 0 else "stable")
        with sm2:
            render_metric_card("Severe Drought States", f"{severe_drought_count}", "States", "Rainfall < 15% of Normal", "up" if severe_drought_count > 0 else "stable")
        with sm3:
            render_metric_card("Severe Flood States", f"{severe_flood_count}", "States", "Precipitation >= 150mm", "up" if severe_flood_count > 0 else "stable")
            
        # 3. Visualization: Gauges for Sectoral Impacts
        st.markdown("#### 🌾 Estimated Sectoral Impacts")
        
        avg_crop_yield = df_sim['crop_yield_impact_pct'].mean()
        avg_water_res = df_sim['reservoir_level_pct'].mean()
        avg_health_idx = df_sim['health_index'].mean()
        
        g1, g2, g3 = st.columns(3)
        
        with g1:
            fig_crop = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_crop_yield,
                title = {'text': "Crop Yield Delta (%)"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [-50, 10], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#ef4444" if avg_crop_yield < 0 else "#10b981"},
                    'steps': [
                        {'range': [-50, -20], 'color': "rgba(239, 68, 68, 0.2)"},
                        {'range': [-20, 0], 'color': "rgba(245, 158, 11, 0.2)"},
                        {'range': [0, 10], 'color': "rgba(16, 185, 129, 0.2)"}
                    ]
                }
            ))
            fig_crop.update_layout(template="plotly_dark", height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_crop, use_container_width=True)
            
        with g2:
            fig_water = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_water_res,
                title = {'text': "Reservoir Capacity (%)"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#3b82f6" if avg_water_res > 40 else "#f59e0b"},
                    'steps': [
                        {'range': [0, 30], 'color': "rgba(239, 68, 68, 0.2)"},
                        {'range': [30, 60], 'color': "rgba(245, 158, 11, 0.2)"},
                        {'range': [60, 100], 'color': "rgba(59, 130, 246, 0.2)"}
                    ]
                }
            ))
            fig_water.update_layout(template="plotly_dark", height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_water, use_container_width=True)
            
        with g3:
            fig_health = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_health_idx,
                title = {'text': "Human Health Index"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#10b981" if avg_health_idx > 70 else "#ef4444"},
                    'steps': [
                        {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.2)"},
                        {'range': [50, 80], 'color': "rgba(245, 158, 11, 0.2)"},
                        {'range': [80, 100], 'color': "rgba(16, 185, 129, 0.2)"}
                    ]
                }
            ))
            fig_health.update_layout(template="plotly_dark", height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_health, use_container_width=True)
            
        # 4. Simulated Risk Heat Map
        st.subheader("🗺️ Spatial Distribution of Simulated Risks")
        
        try:
            m_sim = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB dark_matter")
            
            for _, row in df_sim.iterrows():
                lat = row['latitude']
                lon = row['longitude']
                state = row['state']
                
                # Risk levels
                hw = row['heatwave_risk']
                flood = row['flood_risk']
                drought = row['drought_risk']
                
                # Determine marker color based on highest risk
                if hw == 'Severe' or flood == 'Extreme' or drought == 'Severe':
                    color = 'red'
                    fill_color = '#dc2626'
                elif hw == 'Moderate' or flood == 'High' or drought == 'Moderate':
                    color = 'orange'
                    fill_color = '#d97706'
                elif hw == 'Low' or flood == 'Moderate' or drought == 'Low':
                    color = 'yellow'
                    fill_color = '#ca8a04'
                else:
                    color = 'green'
                    fill_color = '#059669'
                    
                tooltip_text = f"""
                <b>{state}</b><br>
                - Max Temp: {row['max_temp']}°C ({hw} Heatwave)<br>
                - Rainfall: {row['rainfall']}mm ({flood} Flood Risk)<br>
                - Drought Risk: {drought}
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=12,
                    color=color,
                    fill=True,
                    fill_color=fill_color,
                    fill_opacity=0.6,
                    tooltip=tooltip_text
                ).add_to(m_sim)
                
            folium_static(m_sim, width=800, height=450)
        except Exception as e:
            st.error(f"Error rendering simulated map: {e}")
            
        # 5. Text Impact Report Generator & Downloader
        st.subheader("📄 Generated Climate Stress Impact Report")
        
        report_text = simulator.generate_impact_report(df_sim, temp_offset, rain_pct_offset)
        
        # Display report in code box
        st.text_area("Stress Report Preview", report_text, height=300)
        
        # Download button
        st.download_button(
            label="💾 Download Full Impact Report (.txt)",
            data=report_text,
            file_name=f"climate_twin_stress_report_{date_str}.txt",
            mime="text/plain"
        )
