import streamlit as st
import pandas as pd
import os

# Set page configurations as the first Streamlit command
st.set_page_config(
    page_title="ISRO Climate Digital Twin - India",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set path environment adjustments
import sys
sys.path.append(os.path.dirname(__file__))

# Import UI components and Styles
from dashboard.styles import apply_custom_styles
from simulator.digital_twin_engine import DigitalTwinEngine

# Import Page functions
from dashboard.pages.home import show_home
from dashboard.pages.overview import show_overview
from dashboard.pages.rainfall_analytics import show_rainfall_analytics
from dashboard.pages.temperature_analytics import show_temperature_analytics
from dashboard.pages.predictions import show_predictions
from dashboard.pages.digital_twin import show_digital_twin
from dashboard.pages.scenario_simulator import show_scenario_simulator

# Apply Custom ISRO Space Styles
apply_custom_styles()

# Initialize and Cache Digital Twin Engine in session state
if 'twin_engine' not in st.session_state:
    try:
        st.session_state.twin_engine = DigitalTwinEngine()
    except Exception as e:
        st.error(f"Error initializing Digital Twin database connection: {e}")
        st.session_state.twin_engine = None

engine = st.session_state.twin_engine

# Sidebar Dashboard Panel
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="color: #38bdf8 !important; margin-bottom: 0px;">ISRO CLIMATE TWIN</h3>
        <p style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">Bharatiya Antariksh Hackathon</p>
        <hr style="border: 0; border-top: 1px solid #1f355c; margin-top: 10px; margin-bottom: 10px;">
    </div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "📂 Navigation Panel",
    [
        "1. Home",
        "2. Climate Overview",
        "3. Rainfall Analytics",
        "4. Temperature Analytics",
        "5. Predictions & ML Models",
        "6. Digital Twin Operations",
        "7. Scenario Simulator"
    ],
    key="nav_panel"
)



# Route Navigation Selection
if page == "1. Home":
    show_home(engine)
elif page == "2. Climate Overview":
    show_overview(engine)
elif page == "3. Rainfall Analytics":
    show_rainfall_analytics(engine)
elif page == "4. Temperature Analytics":
    show_temperature_analytics(engine)
elif page == "5. Predictions & ML Models":
    show_predictions(engine)
elif page == "6. Digital Twin Operations":
    show_digital_twin(engine)
elif page == "7. Scenario Simulator":
    show_scenario_simulator(engine)

# ISRO Orbit Themed Footer
st.markdown("""
    <div class="footer">
        🚀 ISRO Bharatiya Antariksh Hackathon 2026 PoC | Designed by Team DhruvaX<br>
        <span style="font-size: 0.75rem; color: #475569;">Uses IMD Climate Climatological Reanalysis Data Pipeline</span>
    </div>
""", unsafe_allow_html=True)
