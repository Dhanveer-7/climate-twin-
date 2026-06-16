import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dashboard.styles import render_header, render_metric_card

def show_temperature_analytics(engine):
    """Renders the Temperature Analytics page."""
    render_header("Temperature Analytics", "Monitoring Thermal Gradients, Heatwaves, and Diurnal Temperature Spans")
    
    # Load raw data
    df_raw = pd.read_sql_query("SELECT * FROM daily_climate", engine.db_conn)
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    
    # State selection
    states = sorted(df_raw['state'].unique())
    selected_state = st.selectbox("Select State/UT for Temperature Analysis", states)
    
    # Filter data for selected state
    df_state = df_raw[df_raw['state'] == selected_state].copy()
    
    # Calculate state statistics
    avg_max_temp = df_state['max_temp'].mean()
    avg_min_temp = df_state['min_temp'].mean()
    highest_temp = df_state['max_temp'].max()
    lowest_temp = df_state['min_temp'].min()
    total_years = df_state['year'].nunique()
    
    # Diurnal temperature range (DTR) = max_temp - min_temp
    df_state['dtr'] = df_state['max_temp'] - df_state['min_temp']
    avg_dtr = df_state['dtr'].mean()
    
    # Display state-level metrics
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        render_metric_card("Historical Avg Max / Min Temp", f"{avg_max_temp:.1f} / {avg_min_temp:.1f}", "°C", f"Lowest recorded: {lowest_temp:.1f}°C", "stable")
    with m_col2:
        render_metric_card("Highest Recorded Temperature", f"{highest_temp:.1f}", "°C", "Includes extreme anomalies", "up")
    with m_col3:
        render_metric_card("Avg Diurnal Temp Range (DTR)", f"{avg_dtr:.1f}", "°C", "Max Temp minus Min Temp", "stable")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Temperature Warming Trend (Plotly Line Chart)
    st.subheader(f"📈 Long-Term Temperature Trends: {selected_state}")
    
    df_year_state = df_state.groupby('year').agg({
        'max_temp': 'mean',
        'min_temp': 'mean'
    }).reset_index()
    
    fig_temp_trend = go.Figure()
    fig_temp_trend.add_trace(go.Scatter(
        x=df_year_state['year'], y=df_year_state['max_temp'],
        mode='lines+markers', name='Avg Max Temp',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=6)
    ))
    fig_temp_trend.add_trace(go.Scatter(
        x=df_year_state['year'], y=df_year_state['min_temp'],
        mode='lines+markers', name='Avg Min Temp',
        line=dict(color='#0ea5e9', width=3),
        marker=dict(size=6)
    ))
    
    # Fit linear trends to show warming rates
    z_max = np.polyfit(df_year_state['year'], df_year_state['max_temp'], 1)
    p_max = np.poly1d(z_max)
    fig_temp_trend.add_trace(go.Scatter(
        x=df_year_state['year'], y=p_max(df_year_state['year']),
        mode='lines', name=f'Max Temp Slope (+{z_max[0]*10:.3f}°C/Decade)',
        line=dict(color='#b91c1c', width=1.5, dash='dash')
    ))
    
    fig_temp_trend.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1e293b', title='Year'),
        yaxis=dict(gridcolor='#1e293b', title='Temperature (°C)'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_temp_trend, use_container_width=True)
    
    # 3. Monthly Climatology and Distribution
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📅 Monthly Thermal Cycle")
        df_month = df_state.groupby('month').agg({
            'max_temp': 'mean',
            'min_temp': 'mean'
        }).reset_index()
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                       7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        df_month['month_name'] = df_month['month'].map(month_names)
        
        fig_monthly_temp = go.Figure()
        fig_monthly_temp.add_trace(go.Scatter(
            x=df_month['month_name'], y=df_month['max_temp'],
            name='Max Temp', mode='lines+markers',
            line=dict(color='#ef4444', width=2)
        ))
        fig_monthly_temp.add_trace(go.Scatter(
            x=df_month['month_name'], y=df_month['min_temp'],
            name='Min Temp', mode='lines+markers',
            line=dict(color='#3b82f6', width=2)
        ))
        fig_monthly_temp.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#1e293b'),
            yaxis=dict(gridcolor='#1e293b', title='Temperature (°C)'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_monthly_temp, use_container_width=True)
        
    with col_right:
        st.subheader("📊 Temperature Distribution Curves")
        
        fig_dist_temp = go.Figure()
        fig_dist_temp.add_trace(go.Histogram(
            x=df_state['max_temp'], name='Max Temp Distribution',
            marker_color='#ef4444', opacity=0.6, nbinsx=40
        ))
        fig_dist_temp.add_trace(go.Histogram(
            x=df_state['min_temp'], name='Min Temp Distribution',
            marker_color='#3b82f6', opacity=0.6, nbinsx=40
        ))
        
        fig_dist_temp.update_layout(
            barmode='overlay',
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#1e293b', title='Temperature (°C)'),
            yaxis=dict(gridcolor='#1e293b', title='Frequency (Days)'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_dist_temp, use_container_width=True)
        
    # Heatwave anomaly stats
    st.subheader("🔥 Heat stress analysis")
    hot_days = len(df_state[df_state['max_temp'] >= 40.0])
    extreme_hot_days = len(df_state[df_state['max_temp'] >= 45.0])
    cold_nights = len(df_state[df_state['min_temp'] <= 5.0])
    
    st.write(f"Thermal indices breakdown for **{selected_state}**:")
    idx_col1, idx_col2, idx_col3 = st.columns(3)
    with idx_col1:
        st.info(f"☀️ Days Above 40°C: **{hot_days}** (approx {hot_days/total_years:.1f} days/year)")
    with idx_col2:
        st.warning(f"🔥 Days Above 45°C: **{extreme_hot_days}** (approx {extreme_hot_days/total_years:.1f} days/year)")
    with idx_col3:
        st.success(f"❄️ Cold Nights Below 5°C: **{cold_nights}** (approx {cold_nights/total_years:.1f} nights/year)")
