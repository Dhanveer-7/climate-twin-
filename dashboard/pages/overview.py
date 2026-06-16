import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.styles import render_header, render_metric_card

def show_overview(engine):
    """Renders the Climate Overview page."""
    render_header("Climate Overview", "Historical Climatological Trends and General Analytics (2010 - 2025)")
    
    # Load raw preprocessed data from SQLite
    df_raw = pd.read_sql_query("SELECT * FROM daily_climate", engine.db_conn)
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    
    # 1. KPI Cards Row
    avg_max_temp = df_raw['max_temp'].mean()
    avg_min_temp = df_raw['min_temp'].mean()
    avg_annual_rain = df_raw.groupby(['state', 'year'])['rainfall'].sum().groupby('state').mean().mean()
    
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        render_metric_card("National Avg Max Temp", f"{avg_max_temp:.1f}", "°C", "Historical baseline: 30.1°C", "up")
    with kpi_col2:
        render_metric_card("National Avg Min Temp", f"{avg_min_temp:.1f}", "°C", "Historical baseline: 18.5°C", "up")
    with kpi_col3:
        render_metric_card("Avg Annual Rainfall", f"{avg_annual_rain:.0f}", "mm", "Standard Monsoon variance", "stable")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. National Climate Warming Trend
    st.subheader("📈 National Warming & Climate Trends")
    
    # Group by year to show average temperatures
    df_year = df_raw.groupby('year').agg({
        'max_temp': 'mean',
        'min_temp': 'mean',
        'rainfall': 'mean'
    }).reset_index()
    
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=df_year['year'], y=df_year['max_temp'],
        mode='lines+markers', name='Avg Max Temp',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=8)
    ))
    fig_temp.add_trace(go.Scatter(
        x=df_year['year'], y=df_year['min_temp'],
        mode='lines+markers', name='Avg Min Temp',
        line=dict(color='#06b6d4', width=3),
        marker=dict(size=8)
    ))
    
    fig_temp.update_layout(
        title="India Annual Temperature Trends (2010 - 2025)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1e293b', title="Year"),
        yaxis=dict(gridcolor='#1e293b', title="Temperature (°C)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_temp, use_container_width=True)
    
    # 3. Two Column Layout for State Comparisons and Rainfall
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🌧️ National Average Daily Rainfall")
        fig_rain = px.bar(
            df_year, x='year', y='rainfall',
            labels={'rainfall': 'Precipitation (mm)', 'year': 'Year'},
            color_discrete_sequence=['#3b82f6']
        )
        fig_rain.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#1e293b'),
            yaxis=dict(gridcolor='#1e293b')
        )
        st.plotly_chart(fig_rain, use_container_width=True)
        
    with col_right:
        st.subheader("🗺️ State/UT Temperature Averages")
        # Compare states sorted by average max temperature
        df_state = df_raw.groupby('state')['max_temp'].mean().reset_index().sort_values(by='max_temp', ascending=False)
        
        # Take top 10 and bottom 10 states for readability
        state_filter = st.selectbox("Select Display Format", ["Top 10 Warmest States", "Top 10 Coolest States", "All States & UTs"])
        
        if state_filter == "Top 10 Warmest States":
            df_display = df_state.head(10)
        elif state_filter == "Top 10 Coolest States":
            df_display = df_state.tail(10)
        else:
            df_display = df_state
            
        fig_state = px.bar(
            df_display, x='state', y='max_temp',
            labels={'max_temp': 'Max Temp (°C)', 'state': 'State/UT'},
            color='max_temp',
            color_continuous_scale=px.colors.sequential.OrRd
        )
        fig_state.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#1e293b', tickangle=45),
            yaxis=dict(gridcolor='#1e293b')
        )
        st.plotly_chart(fig_state, use_container_width=True)
        
    # 4. Seasonal Variation (Monthly Distribution)
    st.subheader("📅 Monthly Seasonality Cycle")
    df_month = df_raw.groupby('month').agg({
        'max_temp': 'mean',
        'min_temp': 'mean',
        'rainfall': 'mean'
    }).reset_index()
    
    # Map month numbers to names
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    df_month['month_name'] = df_month['month'].map(month_names)
    
    fig_seasonal = go.Figure()
    fig_seasonal.add_trace(go.Bar(
        x=df_month['month_name'], y=df_month['rainfall'],
        name='Avg Rainfall (mm)', yaxis='y2',
        marker=dict(color='rgba(59, 130, 246, 0.4)', line=dict(color='#3b82f6', width=1.5))
    ))
    fig_seasonal.add_trace(go.Scatter(
        x=df_month['month_name'], y=df_month['max_temp'],
        name='Avg Max Temp (°C)', mode='lines+markers',
        line=dict(color='#f43f5e', width=3)
    ))
    fig_seasonal.add_trace(go.Scatter(
        x=df_month['month_name'], y=df_month['min_temp'],
        name='Avg Min Temp (°C)', mode='lines+markers',
        line=dict(color='#06b6d4', width=3)
    ))
    
    fig_seasonal.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1e293b'),
        yaxis=dict(title='Temperature (°C)', side='left', gridcolor='#1e293b'),
        yaxis2=dict(title='Rainfall (mm)', side='right', overlaying='y', showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_seasonal, use_container_width=True)
