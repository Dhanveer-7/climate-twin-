import os
import folium
from folium.plugins import HeatMap

def render_rainfall_heatmap(df_state):
    """Creates a Folium heatmap showing rainfall intensity across India."""
    # Center map on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB dark_matter")
    
    # Extract coordinates and rainfall value
    # Filter out dry states to keep map clean
    heat_data = [
        [row['latitude'], row['longitude'], row['rainfall']] 
        for _, row in df_state.iterrows() 
        if pd.notna(row['rainfall']) and row['rainfall'] > 0
    ]
    
    if heat_data:
        # We define a blue/purple gradient for rainfall
        HeatMap(
            data=heat_data,
            radius=28,
            blur=18,
            max_zoom=10,
            gradient={0.1: 'lightblue', 0.5: 'blue', 1.0: 'purple'}
        ).add_to(m)
        
    return m

def render_temperature_heatmap(df_state):
    """Creates a Folium heatmap showing temperature levels across India."""
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB dark_matter")
    
    # Extract coordinates and max temp
    heat_data = [
        [row['latitude'], row['longitude'], row['max_temp']] 
        for _, row in df_state.iterrows() 
        if pd.notna(row['max_temp'])
    ]
    
    if heat_data:
        # Standard thermal gradient: blue (cool) -> green -> yellow -> orange -> red (hot)
        # Normalize weights so they show colors beautifully
        max_temp_val = df_state['max_temp'].max()
        min_temp_val = df_state['max_temp'].min()
        temp_range = max_temp_val - min_temp_val if max_temp_val != min_temp_val else 1.0
        
        normalized_heat_data = [
            [lat, lon, (temp - min_temp_val) / temp_range]
            for lat, lon, temp in heat_data
        ]
        
        HeatMap(
            data=normalized_heat_data,
            radius=32,
            blur=20,
            max_zoom=10,
            gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'}
        ).add_to(m)
        
    return m

def render_anomaly_map(df_state):
    """Creates a Folium map with interactive custom markers indicating temperature and rainfall anomalies."""
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB dark_matter")
    
    for _, row in df_state.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        state = row['state']
        max_t = row['max_temp']
        min_t = row['min_temp']
        rain = row['rainfall']
        
        t_normal = row.get('normal_max_temp', max_t)
        r_normal = row.get('normal_rainfall', rain)
        
        t_anomaly = row.get('max_temp_anomaly', 0.0)
        r_anomaly = row.get('rainfall_anomaly', 0.0)
        
        # Color coding markers based on temperature anomaly threshold
        if t_anomaly >= 4.0:
            color = 'red'
            icon_name = 'exclamation-circle'
        elif t_anomaly >= 2.0:
            color = 'orange'
            icon_name = 'chevron-up'
        elif t_anomaly <= -4.0:
            color = 'darkblue'
            icon_name = 'snowflake'
        elif t_anomaly <= -2.0:
            color = 'blue'
            icon_name = 'chevron-down'
        else:
            color = 'green'
            icon_name = 'circle'
            
        # Build HTML tooltip/popup
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; width: 220px; color: #1a202c; padding: 5px;">
            <div style="font-weight: bold; border-bottom: 2px solid #3182ce; padding-bottom: 3px; margin-bottom: 8px; font-size: 14px;">
                {state}
            </div>
            <table style="width: 100%; text-align: left; border-spacing: 0 4px;">
                <tr>
                    <td style="font-weight: 500; color: #718096;">Max Temp:</td>
                    <td style="font-weight: 600;">{max_t:.1f}°C</td>
                </tr>
                <tr>
                    <td style="font-weight: 500; color: #718096;">Temp Anomaly:</td>
                    <td style="font-weight: 600; color: {'#e53e3e' if t_anomaly > 0 else '#3182ce'};">
                        {t_anomaly:+.1f}°C
                    </td>
                </tr>
                <tr>
                    <td style="font-weight: 500; color: #718096;">Rainfall:</td>
                    <td style="font-weight: 600;">{rain:.1f} mm</td>
                </tr>
                <tr>
                    <td style="font-weight: 500; color: #718096;">Rain Anomaly:</td>
                    <td style="font-weight: 600; color: {'#38a169' if r_anomaly > 0 else '#dd6b20'};">
                        {r_anomaly:+.1f} mm
                    </td>
                </tr>
            </table>
        </div>
        """
        
        iframe = folium.IFrame(popup_html, width=230, height=130)
        popup = folium.Popup(iframe, max_width=250)
        
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=f"{state} ({max_t:.1f}°C, {rain:.1f}mm)",
            icon=folium.Icon(color=color, icon=icon_name, prefix='glyphicon')
        ).add_to(m)
        
    return m

# Import pandas dynamically for inline testing
import pandas as pd
