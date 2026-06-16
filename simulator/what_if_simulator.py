import os
import pandas as pd
import numpy as np

class WhatIfSimulator:
    def __init__(self, twin_engine):
        self.twin_engine = twin_engine

    def run_simulation(self, base_state_df, temp_change=0.0, rain_pct_change=0.0):
        """Applies modifications to the base state and evaluates risks and impacts.
        
        Args:
            base_state_df (DataFrame): The current/forecasted state of the digital twin.
            temp_change (float): Additive change in temperature in °C (+1.0, +2.0, +3.0).
            rain_pct_change (float): Percentage change in rainfall (-20.0, -10.0, +10.0, +20.0).
            
        Returns:
            DataFrame: Simulated state with risk scores and impacts.
        """
        if base_state_df.empty:
            return base_state_df
            
        sim_df = base_state_df.copy()
        
        # 1. Apply adjustments
        sim_df['max_temp'] = sim_df['max_temp'] + temp_change
        sim_df['min_temp'] = sim_df['min_temp'] + temp_change
        sim_df['rainfall'] = sim_df['rainfall'] * (1.0 + rain_pct_change / 100.0)
        
        # Round simulated values
        sim_df['max_temp'] = sim_df['max_temp'].round(1)
        sim_df['min_temp'] = sim_df['min_temp'].round(1)
        sim_df['rainfall'] = sim_df['rainfall'].round(1)
        
        # Recalculate anomalies based on simulated values
        sim_df['max_temp_anomaly'] = (sim_df['max_temp'] - sim_df['normal_max_temp']).round(1)
        sim_df['min_temp_anomaly'] = (sim_df['min_temp'] - sim_df['normal_min_temp']).round(1)
        sim_df['rainfall_anomaly'] = (sim_df['rainfall'] - sim_df['normal_rainfall']).round(1)
        
        # 2. Risk Assessment
        heatwave_risks = []
        flood_risks = []
        drought_risks = []
        
        for idx, row in sim_df.iterrows():
            # Heatwave Risk (based on IMD standards adjusted for our model)
            # Threshold: Max Temp >= 40°C and anomaly >= 4.5°C
            if row['max_temp'] >= 40.0:
                if row['max_temp_anomaly'] >= 6.4:
                    heatwave_risks.append('Severe')
                elif row['max_temp_anomaly'] >= 4.5:
                    heatwave_risks.append('Moderate')
                else:
                    heatwave_risks.append('Low')
            elif row['max_temp'] >= 37.0 and row['max_temp_anomaly'] >= 3.0:
                heatwave_risks.append('Low')
            else:
                heatwave_risks.append('None')
                
            # Flood Risk (based on daily rainfall intensity)
            if row['rainfall'] >= 150.0:
                flood_risks.append('Extreme')
            elif row['rainfall'] >= 80.0:
                flood_risks.append('High')
            elif row['rainfall'] >= 40.0:
                flood_risks.append('Moderate')
            else:
                flood_risks.append('None')
                
            # Drought Risk (based on rainfall anomaly and normal baseline)
            # If rainfall is low and below normal, and normal rainfall is not negligible
            if row['normal_rainfall'] > 15.0:
                pct_normal = (row['rainfall'] / row['normal_rainfall']) * 100.0
                if pct_normal <= 15.0:
                    drought_risks.append('Severe')
                elif pct_normal <= 40.0:
                    drought_risks.append('Moderate')
                elif pct_normal <= 70.0:
                    drought_risks.append('Low')
                else:
                    drought_risks.append('None')
            else:
                drought_risks.append('None')
                
        sim_df['heatwave_risk'] = heatwave_risks
        sim_df['flood_risk'] = flood_risks
        sim_df['drought_risk'] = drought_risks
        
        # 3. Impact Modeling
        crop_yields = []
        water_levels = []
        health_impacts = []
        
        for idx, row in sim_df.iterrows():
            # Agriculture Impact (crop yield delta %)
            crop_delta = 0.0
            if row['heatwave_risk'] == 'Severe':
                crop_delta -= np.random.uniform(20.0, 35.0)
            elif row['heatwave_risk'] == 'Moderate':
                crop_delta -= np.random.uniform(10.0, 20.0)
                
            if row['drought_risk'] == 'Severe':
                crop_delta -= np.random.uniform(25.0, 45.0)
            elif row['drought_risk'] == 'Moderate':
                crop_delta -= np.random.uniform(15.0, 25.0)
                
            if row['flood_risk'] == 'Extreme':
                crop_delta -= np.random.uniform(30.0, 60.0) # complete washouts
            elif row['flood_risk'] == 'High':
                crop_delta -= np.random.uniform(15.0, 30.0)
                
            crop_delta = max(-80.0, min(10.0, crop_delta)) # bounds
            crop_yields.append(round(crop_delta, 1))
            
            # Water Resources (Reservoir Capacity %)
            # Base reservoir level is ~60%
            water_level = 60.0
            if row['drought_risk'] == 'Severe':
                water_level -= np.random.uniform(25.0, 40.0)
            elif row['drought_risk'] == 'Moderate':
                water_level -= np.random.uniform(12.0, 20.0)
            elif row['flood_risk'] == 'Extreme' or row['flood_risk'] == 'High':
                water_level += np.random.uniform(20.0, 35.0)
            else:
                # Slight variation
                water_level += np.random.uniform(-5.0, 5.0)
            
            water_level = max(5.0, min(100.0, water_level))
            water_levels.append(round(water_level, 1))
            
            # Human Health Index (100 is optimal health, lower is worse)
            health_score = 100.0
            if row['heatwave_risk'] == 'Severe':
                health_score -= 35.0
            elif row['heatwave_risk'] == 'Moderate':
                health_score -= 15.0
                
            if row['flood_risk'] == 'Extreme':
                health_score -= 25.0
            elif row['flood_risk'] == 'High':
                health_score -= 10.0
                
            health_score = max(30.0, health_score)
            health_impacts.append(int(health_score))
            
        sim_df['crop_yield_impact_pct'] = crop_yields
        sim_df['reservoir_level_pct'] = water_levels
        sim_df['health_index'] = health_impacts
        
        return sim_df

    def generate_impact_report(self, sim_df, temp_change, rain_pct_change):
        """Generates a text-based structured report of the what-if simulation findings."""
        report = []
        report.append("=========================================================================")
        report.append("             ISRO DIGITAL TWIN: CLIMATE IMPACT REPORT")
        report.append("=========================================================================")
        report.append(f"Report Generated On: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Simulation Parameters:")
        report.append(f"  - Temperature Offset: +{temp_change}°C")
        report.append(f"  - Rainfall Percentage Change: {rain_pct_change:+.1f}%")
        report.append("-------------------------------------------------------------------------")
        
        # Risk summaries
        hw_states = sim_df[sim_df['heatwave_risk'].isin(['Moderate', 'Severe'])]
        flood_states = sim_df[sim_df['flood_risk'].isin(['High', 'Extreme'])]
        drought_states = sim_df[sim_df['drought_risk'].isin(['Moderate', 'Severe'])]
        
        report.append("\n[RISK SUMMARY]")
        report.append(f"  * Heatwave Warning States: {len(hw_states)} out of 36")
        for _, r in hw_states.iterrows():
            report.append(f"    - {r['state']}: {r['max_temp']}°C ({r['heatwave_risk']} Heatwave)")
            
        report.append(f"\n  * Flood Alert States: {len(flood_states)} out of 36")
        for _, r in flood_states.iterrows():
            report.append(f"    - {r['state']}: {r['rainfall']}mm ({r['flood_risk']} Flood risk)")
            
        report.append(f"\n  * Agricultural Drought States: {len(drought_states)} out of 36")
        for _, r in drought_states.iterrows():
            report.append(f"    - {r['state']}: {r['rainfall']}mm vs Normal {r['normal_rainfall']:.1f}mm")
            
        report.append("\n-------------------------------------------------------------------------")
        report.append("[SECTORAL IMPACTS]")
        
        # Calculate averages
        avg_crop = sim_df['crop_yield_impact_pct'].mean()
        avg_water = sim_df['reservoir_level_pct'].mean()
        avg_health = sim_df['health_index'].mean()
        
        report.append(f"  1. Agriculture & Crop Yields: Average crop yield impact of {avg_crop:+.1f}%.")
        if avg_crop < -15.0:
            report.append("     STATUS: CRITICAL. Severe crop failure risks detected in major agricultural belts.")
        elif avg_crop < -5.0:
            report.append("     STATUS: WARNING. Moderate yield reductions expected. Monitor rabi/kharif crops.")
        else:
            report.append("     STATUS: NORMAL. Standard crop cycle variations.")
            
        report.append(f"\n  2. Water Resources & Reservoirs: Average reservoir level at {avg_water:.1f}%.")
        if avg_water < 35.0:
            report.append("     STATUS: CRITICAL. Heavy depletion of reservoir basins. Water rationing recommended.")
        elif avg_water < 50.0:
            report.append("     STATUS: WARNING. Water levels running below normal. Conservation measures needed.")
        else:
            report.append("     STATUS: SATISFACTORY. Healthy water reserves across major basins.")
            
        report.append(f"\n  3. Human Health & Energy Grid: Average health index score is {avg_health:.1f}/100.")
        if avg_health < 75.0:
            report.append("     STATUS: CRITICAL. Severe thermal stress risks and grid failure alerts. Implement heat action plans.")
        elif avg_health < 90.0:
            report.append("     STATUS: WARNING. Moderate thermal discomfort and load shedding risk.")
        else:
            report.append("     STATUS: OPTIMAL. Standard seasonal health thresholds.")
            
        report.append("=========================================================================")
        
        return "\n".join(report)
