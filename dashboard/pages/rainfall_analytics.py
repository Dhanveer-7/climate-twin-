import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dashboard.styles import render_header, render_metric_card

def show_rainfall_analytics(engine):
    """Renders the Rainfall Analytics page."""
    render_header("Rainfall Analytics", "Deep Dive into Precipitation Cycles, Monsoons, and Drought Indices")
    
    # Load raw data
    df_raw = pd.read_sql_query("SELECT * FROM daily_climate", engine.db_conn)
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    
    # State selection
    states = sorted(df_raw['state'].unique())
    selected_state = st.selectbox("Select State/UT for Analysis", states)
    
    # Filter data for selected state
    df_state = df_raw[df_raw['state'] == selected_state].copy()
    
    # Calculate state statistics
    total_years = df_state['year'].nunique()
    annual_rains = df_state.groupby('year')['rainfall'].sum()
    avg_annual_rain = annual_rains.mean()
    max_daily_rain = df_state['rainfall'].max()
    
    # Rainy days defined as rainfall > 2.5mm (standard IMD definition of a rainy day)
    rainy_days = df_state[df_state['rainfall'] >= 2.5]
    avg_rainy_days_per_year = len(rainy_days) / total_years
    
    # Display state-level metrics
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        render_metric_card(f"Avg Annual Rainfall ({selected_state})", f"{avg_annual_rain:.0f}", "mm", "Based on 16-year history", "stable")
    with m_col2:
        render_metric_card("Highest Daily Rainfall", f"{max_daily_rain:.1f}", "mm", "Extreme weather anomaly", "up")
    with m_col3:
        render_metric_card("Avg Rainy Days / Year", f"{avg_rainy_days_per_year:.1f}", "days", "Precipitation threshold >= 2.5mm", "stable")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Annual Rainfall Trend (Plotly Bar Chart)
    st.subheader(f"📅 Annual Rainfall Trajectory: {selected_state}")
    
    fig_annual_trend = px.bar(
        x=annual_rains.index, y=annual_rains.values,
        labels={'x': 'Year', 'y': 'Total Rainfall (mm)'},
        color_discrete_sequence=['#0ea5e9']
    )
    
    # Add trend line
    z = np.polyfit(annual_rains.index, annual_rains.values, 1)
    p = np.poly1d(z)
    
    fig_annual_trend.add_trace(go.Scatter(
        x=annual_rains.index, y=p(annual_rains.index),
        mode='lines', name='Long-term Trend',
        line=dict(color='#ef4444', width=2, dash='dash')
    ))
    
    fig_annual_trend.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1e293b'),
        yaxis=dict(gridcolor='#1e293b'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_annual_trend, use_container_width=True)
    
    # 3. Monthly Climatology and Intensity Distribution
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Monthly Climatological Normal")
        df_month = df_state.groupby('month')['rainfall'].mean().reset_index()
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                       7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        df_month['month_name'] = df_month['month'].map(month_names)
        
        fig_monthly_rain = px.bar(
            df_month, x='month_name', y='rainfall',
            labels={'rainfall': 'Avg Rainfall (mm)', 'month_name': 'Month'},
            color_discrete_sequence=['#6366f1']
        )
        fig_monthly_rain.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#1e293b'),
            yaxis=dict(gridcolor='#1e293b')
        )
        st.plotly_chart(fig_monthly_rain, use_container_width=True)
        
    with col_right:
        st.subheader("🌧️ Rainfall Intensity Distribution")
        # Filter for days when it actually rained to show intensity spread
        df_rainy_days = df_state[df_state['rainfall'] > 0.1]
        
        fig_dist = px.histogram(
            df_rainy_days, x='rainfall',
            nbins=30,
            labels={'rainfall': 'Precipitation Intensity (mm)', 'count': 'Frequency'},
            color_discrete_sequence=['#10b981'],
            log_y=True # Use log scale because light rain is far more frequent than cloudbursts
        )
        fig_dist.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#1e293b', title='Precipitation Amount (mm)'),
            yaxis=dict(gridcolor='#1e293b', title='Log Count (Days)')
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        
    # Extra: Drought vs Flood Risk classification summary
    st.subheader("📊 Wet/Dry Extremes Classification")
    st.write(f"Based on historical daily records for **{selected_state}**:")
    
    extreme_dry = len(df_state[df_state['rainfall'] == 0.0])
    light_rain = len(df_state[(df_state['rainfall'] > 0) & (df_state['rainfall'] < 10)])
    mod_rain = len(df_state[(df_state['rainfall'] >= 10) & (df_state['rainfall'] < 50)])
    heavy_rain = len(df_state[(df_state['rainfall'] >= 50) & (df_state['rainfall'] < 100)])
    extreme_rain = len(df_state[df_state['rainfall'] >= 100])
    
    # Render table
    data_dict = {
        "Precipitation Class": ["No Rain (Dry Days)", "Light Rain (<10mm)", "Moderate Rain (10-50mm)", "Heavy Rain (50-100mm)", "Extreme Rain (>=100mm)"],
        "Count (Days)": [extreme_dry, light_rain, mod_rain, heavy_rain, extreme_rain],
        "Percentage (%)": [
            f"{extreme_dry/len(df_state)*100:.2f}%", 
            f"{light_rain/len(df_state)*100:.2f}%", 
            f"{mod_rain/len(df_state)*100:.2f}%", 
            f"{heavy_rain/len(df_state)*100:.2f}%", 
            f"{extreme_rain/len(df_state)*100:.2f}%"
        ]
    }
    
    st.table(pd.DataFrame(data_dict))
