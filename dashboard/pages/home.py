import streamlit as st
import pandas as pd
from dashboard.styles import render_header, render_metric_card

def show_home(engine):
    """Renders the dashboard home page."""
    # Custom Space Header Hero
    st.markdown("""
        <div style="background: linear-gradient(135deg, #091224 0%, #1e3a6c 100%); padding: 30px; border-radius: 15px; border: 1px solid #3b82f6; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="font-size: 0.9rem; color: #38bdf8; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px;">
                🚀 Bharatiya Antariksh Hackathon 2026
            </div>
            <h1 style="color: #ffffff !important; font-size: 2.3rem; margin: 0 0 10px 0; font-weight: 800;">
                AI-Powered Digital Twin of India's Climate
            </h1>
            <div style="color: #94a3b8; font-size: 1.1rem; max-width: 750px; margin: 0 auto; line-height: 1.6;">
                A high-fidelity virtual representation of India's climate, utilizing advanced machine learning models (XGBoost, Random Forest) and historical data to monitor, predict, and simulate climate extremes.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Columns for Key Objectives
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌐 What is a Climate Digital Twin?")
        st.write("""
        A Digital Twin is a dynamic virtual replica of a physical system—in this case, India's climate. 
        It integrates historical records, ingests real-time observations, runs continuous ML predictions, 
        and allows researchers and policymakers to run "what-if" simulations to assess hazards like droughts, heatwaves, and floods.
        """)
        
        st.subheader("🛠️ Core Engine Components")
        st.markdown(r"""
        * **Module 1: Ingestion & Infill Pipeline**: Reads daily meteorological values, performs linear interpolation for data cleaning, and extracts sliding lags & trig-seasonal indicators.
        * **Module 2: ML Prediction Engine**: Trains Random Forest and XGBoost algorithms recursively to predict thermal gradients and precipitation patterns.
        * **Module 3: Visual Intelligence Map**: Renders dynamic heatmaps and spatial z-score anomalies across India's 36 States and UTs.
        * **Module 4: What-If Risk Simulator**: Models regional vulnerability changes (e.g. $+2^\circ\text{C}$ warming, $-20\%$ rain) to estimate reservoir depletion, crop yields, and thermal stress.
        """)
        
    with col2:
        # Mini Interactive Telemetry Board (using June 15, 2025 as default PoC date)
        st.subheader("📡 Live Digital Twin Telemetry")
        st.caption("Observed Climate State: 2025-06-15")
        
        try:
            df_state = engine.get_current_state("2025-06-15")
            if not df_state.empty:
                avg_max = df_state['max_temp'].mean()
                avg_min = df_state['min_temp'].mean()
                total_rain = df_state['rainfall'].sum()
                
                # Active warnings count
                hw_count = len(df_state[df_state['max_temp'] >= 40.0])
                flood_count = len(df_state[df_state['rainfall'] >= 50.0])
                
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    render_metric_card("Avg Max Temp", f"{avg_max:.1f}", "°C", "+0.4°C vs Normal", "up")
                    render_metric_card("Avg Min Temp", f"{avg_min:.1f}", "°C", "+0.2°C vs Normal", "up")
                with m_col2:
                    render_metric_card("Total Rainfall", f"{total_rain:.1f}", "mm", "Seasonal Normal", "stable")
                    
                    # Alert level indicator
                    status_color = "red" if hw_count > 0 or flood_count > 0 else "green"
                    status_text = "WARNING" if hw_count > 0 or flood_count > 0 else "NOMINAL"
                    st.markdown(f"""
                        <div class="metric-card" style="border-color: {'#ef4444' if status_color == 'red' else '#10b981'};">
                            <div class="metric-title">System Status</div>
                            <div class="metric-value" style="color: {'#ef4444' if status_color == 'red' else '#10b981'} !important;">{status_text}</div>
                            <div class="metric-delta" style="color: #94a3b8;">
                                {hw_count} Heatwave Alerts<br>
                                {flood_count} High Rain Alerts
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Ingest historical data to display live telemetry.")
        except Exception as e:
            st.error(f"Waiting for database initialization: {e}")
            
    st.markdown("---")
    
    # Architecture Showcase
    st.subheader("🖥️ Digital Twin Architecture")
    st.markdown("""
    ```mermaid
    graph TD
        A[IMD Climate Datasets] --> B[Data Ingestion & Cleaning]
        B --> C[SQLite Database]
        C --> D[Feature Engineering Lags/Rolling/Trig]
        D --> E[ML Prediction Engine RF / XGBoost]
        E --> F[Digital Twin Virtual State]
        F --> G[Folium Map Visualization]
        F --> H[What-If Scenario Simulator]
        F --> I[AI Anomaly Alert Engine]
        G & H & I --> J[Streamlit ISRO Space Dashboard]
    ```
    """, unsafe_allow_html=True)
    
    st.info("💡 Pro Tip: Use the sidebar navigation menu to explore Climate Analytics, trigger predictions, run what-if simulations, and view live geographic anomalies.")
