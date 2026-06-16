import streamlit as st

def apply_custom_styles():
    """Injects custom CSS to style the Streamlit app with an ISRO space-themed dark aesthetic."""
    st.markdown("""
        <style>
        /* Main Application Styles */
        .stApp {
            background-color: #050b14;
            color: #e2e8f0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #091224 !important;
            border-right: 1px solid #1f355c;
        }
        section[data-testid="stSidebar"] .stMarkdown {
            color: #94a3b8;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #38bdf8 !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px;
        }
        
        /* Glowing Cards (Glassmorphism + Space Theme) */
        .metric-card {
            background: linear-gradient(135deg, #0e1e38 0%, #081326 100%);
            border: 1px solid #1e3a6c;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            border-color: #0ea5e9;
            box-shadow: 0 4px 25px 0 rgba(14, 165, 233, 0.15);
            transform: translateY(-2px);
        }
        
        .metric-title {
            font-size: 0.875rem;
            color: #94a3b8;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #f8fafc;
            display: flex;
            align-items: baseline;
        }
        
        .metric-unit {
            font-size: 1rem;
            color: #38bdf8;
            margin-left: 4px;
        }
        
        .metric-delta {
            font-size: 0.875rem;
            margin-top: 4px;
            font-weight: 500;
        }
        .delta-up {
            color: #f43f5e; /* Red for warming/abnormal rain */
        }
        .delta-down {
            color: #06b6d4; /* Blue for cooling */
        }
        .delta-stable {
            color: #10b981; /* Green for stable/normal */
        }

        /* Warnings & Alert Cards */
        .alert-card {
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
            border-left: 5px solid;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }
        
        .alert-RED {
            background-color: rgba(220, 38, 38, 0.12);
            border-color: #dc2626;
            color: #fca5a5;
            border-left-color: #dc2626;
        }
        .alert-ORANGE {
            background-color: rgba(217, 119, 6, 0.12);
            border-color: #d97706;
            color: #fde047;
            border-left-color: #d97706;
        }
        .alert-YELLOW {
            background-color: rgba(202, 138, 4, 0.1);
            border-color: #ca8a04;
            color: #fef08a;
            border-left-color: #ca8a04;
        }
        
        /* Tabs styling overrides */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #091224;
            padding: 4px;
            border-radius: 8px;
            border: 1px solid #1e3a6c;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            border-radius: 6px;
            color: #94a3b8;
            background-color: transparent;
            border: none;
            padding: 10px 16px;
            transition: all 0.2s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #38bdf8;
            background-color: #11203c;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1d3557 !important;
            color: #38bdf8 !important;
            font-weight: 600;
        }
        
        /* Buttons styling */
        .stButton>button {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%) !important;
            color: #ffffff !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.5) !important;
            border-color: #60a5fa !important;
            transform: scale(1.02);
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            padding: 20px 0;
            margin-top: 40px;
            border-top: 1px solid #1e3a6c;
            color: #64748b;
            font-size: 0.875rem;
        }
        
        /* Grid background look */
        .grid-bg {
            background-image: 
                linear-gradient(rgba(30, 58, 108, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(30, 58, 108, 0.05) 1px, transparent 1px);
            background-size: 20px 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_metric_card(title, value, unit="", delta="", delta_type="stable"):
    """Helper to render a styled key performance indicator (KPI) metric card."""
    delta_class = "delta-stable"
    delta_prefix = ""
    
    if delta_type == "up":
        delta_class = "delta-up"
        delta_prefix = "▲"
    elif delta_type == "down":
        delta_class = "delta-down"
        delta_prefix = "▼"
        
    delta_html = f'<div class="metric-delta {delta_class}">{delta_prefix} {delta}</div>' if delta else ''
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">
                {value}
                <span class="metric-unit">{unit}</span>
            </div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def render_alert_card(alert_type, message, level="YELLOW"):
    """Helper to render a custom warning/alert card."""
    st.markdown(f"""
        <div class="alert-card alert-{level}">
            <div style="font-weight: 700; font-size: 1rem; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
                <span>⚠️ {alert_type}</span>
                <span style="font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; background: rgba(0,0,0,0.2);">{level} ALERT</span>
            </div>
            <div style="font-size: 0.9rem; line-height: 1.4;">{message}</div>
        </div>
    """, unsafe_allow_html=True)

def render_header(title, subtitle=""):
    """Helper to render a futuristic orbit/space stylized page header."""
    subtitle_html = f'<div style="color: #94a3b8; font-size: 1rem; margin-top: 4px; margin-bottom: 25px;">{subtitle}</div>' if subtitle else '<div style="margin-bottom: 20px;"></div>'
    st.markdown(f"""
        <div style="border-left: 4px solid #0ea5e9; padding-left: 15px; margin-top: 10px;">
            <h2 style="margin: 0; padding: 0; color: #f8fafc !important; font-size: 1.8rem;">{title}</h2>
        </div>
        {subtitle_html}
    """, unsafe_allow_html=True)
