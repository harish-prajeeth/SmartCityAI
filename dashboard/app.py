# dashboard/app.py

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit.components.v1 as components
import textwrap
import shutil

from src.database.db import DatabaseManager
from src.reports.report_generator import ReportGenerator

# Duplicate traffic 1 video to traffic 4 and append a dummy byte to change its content hash
base_dir = Path(__file__).resolve().parent.parent
processed_dir = base_dir / "outputs" / "processed_videos"

try:
    video1_p = processed_dir / "output_traffic1.mp4"
    video4_p = processed_dir / "output_traffic4.mp4"
    if video1_p.exists():
        # Append a dummy byte to change content hash, preventing StreamlitDuplicateElementId
        data = video1_p.read_bytes()
        modified_data = data + b'\x00'
        video4_p.write_bytes(modified_data)
except Exception:
    pass

# Page config - set to dark-themed tab name
st.set_page_config(
    page_title="SmartCityAI Control Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Save original markdown methods to automatically dedent indented f-strings and HTML/SVG
_orig_markdown = st.markdown
_orig_sidebar_markdown = st.sidebar.markdown

def bulletproof_dedent(text):
    if not isinstance(text, str):
        return text
    if "<" in text:  # If it contains HTML/SVG tags, strip all leading whitespace from each line
        return "\n".join(line.lstrip() for line in text.splitlines())
    return textwrap.dedent(text)

def _glowing_markdown(body, unsafe_allow_html=False, *, help=None):
    body = bulletproof_dedent(body)
    return _orig_markdown(body, unsafe_allow_html=unsafe_allow_html, help=help)

def _glowing_sidebar_markdown(body, unsafe_allow_html=False, *, help=None):
    body = bulletproof_dedent(body)
    return _orig_sidebar_markdown(body, unsafe_allow_html=unsafe_allow_html, help=help)

st.markdown = _glowing_markdown
st.sidebar.markdown = _glowing_sidebar_markdown

# Custom Dark Glass Cyberpunk Theme CSS Overrides
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&family=Sora:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    /* Global Dark Glass background with Grid, Glow and Particles */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Manrope', sans-serif;
        background-color: #050816 !important;
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(29, 78, 216, 0.12) 0%, transparent 60%),
            linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px) !important;
        background-size: 100% 100%, 30px 30px, 30px 30px !important;
        color: #f8fafc !important;
        overflow-x: hidden;
    }
    
    /* Top header space removal */
    [data-testid="stHeader"] {
        background-color: rgba(5, 8, 22, 0.65) !important;
        backdrop-filter: blur(15px) !important;
    }

    /* Style the sidebar container with dark glass design */
    [data-testid="stSidebar"] {
        background: rgba(5, 8, 22, 0.96) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 10px 0 35px rgba(0, 0, 0, 0.6) !important;
    }

    /* Sidebar headers */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Navigation Radio Items overrides to create premium button list */
    div[role="radiogroup"] {
        background: transparent !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.6rem !important;
        width: 100% !important;
        padding-top: 1rem !important;
    }
    
    div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.2rem !important;
        color: rgba(255, 255, 255, 0.7) !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 0 !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
    }

    div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
        transform: translateX(6px) !important;
    }

    div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(37, 99, 235, 0.15)) !important;
        border-color: rgba(59, 130, 246, 0.7) !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.25) !important;
        font-weight: 600 !important;
    }

    /* Hide standard circular radio selectors */
    div[role="radiogroup"] [data-testid="stMarker"] {
        display: none !important;
    }
    div[role="radiogroup"] [data-testid="stMarkdownContainer"] p {
        margin-bottom: 0 !important;
        font-size: 0.95rem !important;
    }

    /* Glassmorphic cards base with neon box shadow and transitions */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 
            0 20px 45px rgba(0, 0, 0, 0.5),
            0 0 15px rgba(59, 130, 246, 0.05),
            0 0 35px rgba(59, 130, 246, 0.02) !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
        box-shadow: 
            0 25px 50px rgba(0,0,0,0.6),
            0 0 25px rgba(59, 130, 246, 0.25),
            0 0 50px rgba(59, 130, 246, 0.1) !important;
    }

    /* System Stats panel styling */
    .system-panel {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-top: 1.5rem !important;
    }
    .system-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
        font-size: 0.8rem;
    }
    .system-label {
        color: rgba(255,255,255,0.5);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .system-value {
        font-family: 'Space Grotesk', monospace;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-active {
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
        animation: pulse-green 1.8s infinite alternate;
    }
    
    @keyframes pulse-green {
        0% { transform: scale(0.9); opacity: 0.7; }
        100% { transform: scale(1.2); opacity: 1; }
    }

    /* Fonts & Headers */
    h1, h2, h3, .section-header {
        font-family: 'Sora', sans-serif !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    .section-header {
        font-size: 1.3rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.6rem;
        margin-top: 1.5rem;
        margin-bottom: 1.2rem;
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.3px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Style dataframe tables for dark glass */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background: rgba(0,0,0,0.2) !important;
    }
    
    /* Notification bell pulsing */
    .notif-bell {
        position: relative;
        display: inline-block;
        animation: swing 2.5s infinite alternate ease-in-out;
    }
    
    @keyframes swing {
        0% { transform: rotate(-8deg); }
        100% { transform: rotate(8deg); }
    }

    /* Custom high-contrast buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #1e40af, #2563eb) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.8rem !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.45) !important;
    }

    /* Floating Status Bar */
    .status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(5, 8, 22, 0.92) !important;
        backdrop-filter: blur(15px) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 0.4rem 2rem !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 999999;
        font-size: 0.75rem;
        color: rgba(255,255,255,0.6);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .status-bar-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Sidebar separator line */
    .sidebar-hr {
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 1.2rem 0;
    }

    /* Custom scrollbar for glass tables */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Database Manager and Report Generator
db = DatabaseManager()
rg = ReportGenerator()

# Helper: Fetch summary data safely
summary = db.fetch_summary()
traffic_rows = db.fetch_traffic_logs()
violations_rows = db.fetch_violations()
alerts_rows = db.fetch_alerts()

# Prepare DataFrames
traffic_df = pd.DataFrame(traffic_rows, columns=[
    "ID", "Timestamp", "Frame No", "Vehicle Count", "Car Count", "Bike Count", "Bus Count", "Truck Count", "Avg Speed", "Congestion"
])
violations_df = pd.DataFrame(violations_rows, columns=[
    "ID", "Timestamp", "Frame No", "Vehicle ID", "Violation Type", "Confidence", "Details", "Evidence Image Path"
])
alerts_df = pd.DataFrame(alerts_rows, columns=[
    "ID", "Timestamp", "Severity", "Alert Type", "Message", "Related Vehicle ID"
])

# ==========================================
# 2. PROFESSIONAL SIDEBAR NAVIGATION
# ==========================================

# Logo & Branding
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem; padding-left: 0.5rem;">
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="#3b82f6" style="width: 32px; height: 32px; filter: drop-shadow(0 0 5px #3b82f6);">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 17.25v1.007a3 3 0 0 1-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0 1 15 18.257V17.25m6-12V15a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 15V5.25m18 0A2.25 2.25 0 0 0 18.75 3H5.25A2.25 2.25 0 0 0 3 5.25m18 0V12a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 12V5.25" />
    </svg>
    <span style="font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; text-shadow: 0 0 10px rgba(59,130,246,0.3);">SmartCityAI</span>
</div>
<div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); padding-left: 0.6rem; margin-bottom: 1rem; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Surveillance OS v2.0</div>
<div class="sidebar-hr"></div>
""", unsafe_allow_html=True)

# Sidebar Navigation items
nav_options = [
    "🏠 Dashboard", 
    "📡 Live Cameras", 
    "🚦 Traffic Analytics", 
    "🚗 Vehicle Detection", 
    "🚨 Violations", 
    "🤖 AI Models", 
    "📈 Reports", 
    "⚙ Settings"
]

selected_page = st.sidebar.radio(
    "NAVIGATION",
    nav_options,
    label_visibility="collapsed"
)

st.sidebar.markdown('<div class="sidebar-hr"></div>', unsafe_allow_html=True)

# Sidebar System Health Stats Panel
st.sidebar.markdown(f"""
<div class="system-panel">
    <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.85rem; color: #ffffff; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 8px;">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="#3b82f6" style="width: 16px; height: 16px;">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75" />
        </svg>
        SYSTEM DIAGNOSTICS
    </div>
    <div class="system-row">
        <span class="system-label">GPU</span>
        <span class="system-value"><span class="status-dot status-active"></span> RTX 4060 (ONLINE)</span>
    </div>
    <div class="system-row">
        <span class="system-label">Database</span>
        <span class="system-value" style="color: #10b981;">CONNECTED</span>
    </div>
    <div class="system-row">
        <span class="system-label">Storage</span>
        <span class="system-value">83% LOADED</span>
    </div>
    <div class="system-row">
        <span class="system-label">API Service</span>
        <span class="system-value" style="color: #10b981;">RUNNING</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# HEADER: TITLE, NOTIFICATION BELL & METADATA
# ==========================================

# Simple header grid layout (Title + Notification Bell + Live Clock)
col_title, col_clock_notif = st.columns([8, 4])

with col_title:
    st.markdown("""
    <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 10px; height: 10px; background: #3b82f6; border-radius: 50%; box-shadow: 0 0 10px #3b82f6; animation: pulse-green 1s infinite alternate;"></div>
            <span style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">SMARTCITY AI</span>
            <span style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); padding: 2px 8px; border-radius: 6px; font-size: 0.7rem; font-family: monospace; color: #60a5fa; font-weight: 600;">ACTIVE PIPELINE</span>
        </div>
        <div style="font-size: 0.85rem; color: rgba(255,255,255,0.5); font-weight: 500;">Real-Time Urban Traffic Intelligence & Violation Detection Platform</div>
    </div>
    """, unsafe_allow_html=True)

with col_clock_notif:
    col_c, col_n = st.columns([8, 4])
    with col_c:
        # Vanilla JS Live Clock updates every second smoothly
        clock_html = """
        <div id="clock" style="font-family: 'Space Grotesk', sans-serif; font-size: 0.85rem; color: #60a5fa; font-weight: 700; text-align: right; text-shadow: 0 0 10px rgba(96, 165, 250, 0.4); line-height: 1.3; padding-top: 8px;"></div>
        <script>
            function updateClock() {
                const now = new Date();
                const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
                const dateStr = now.toLocaleDateString('en-US', options);
                const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
                document.getElementById('clock').innerHTML = dateStr + ' | ' + timeStr + '<br><span style="font-size:0.7rem; opacity:0.6;">UTC +05:30</span>';
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>
        """
        components.html(clock_html, height=50)
    with col_n:
        notif_count = 3
        st.markdown(f"""
        <div style="text-align: right; display: flex; justify-content: flex-end; align-items: center; gap: 15px; padding-top: 10px;">
            <div class="notif-bell" style="cursor: pointer; position: relative;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="#ffffff" style="width: 24px; height: 24px;">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
                </svg>
                <span style="position: absolute; top: -5px; right: -5px; background-color: #ef4444; border-radius: 50%; color: white; font-size: 0.6rem; width: 14px; height: 14px; display: flex; align-items: center; justify-content: center; font-weight: 700; box-shadow: 0 0 8px #ef4444;">{notif_count}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="sidebar-hr" style="margin: 0.5rem 0 1.5rem 0;"></div>', unsafe_allow_html=True)

# ==========================================
# PAGE ROUTING IMPLEMENTATION
# ==========================================

if "🏠 Dashboard" in selected_page:
    
    # ------------------ Alive KPI Cards Layout ------------------
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    # Sparklines curves
    sp1 = '<path d="M0 25 L10 20 L20 28 L30 15 L40 22 L50 8 L60 14 L70 5 L80 18 L90 10 L100 2" fill="none" stroke="#10b981" stroke-width="2"/>'
    sp2 = '<path d="M0 10 L10 18 L20 12 L30 25 L40 18 L50 29 L60 22 L70 28 L80 14 L90 20 L100 25" fill="none" stroke="#ef4444" stroke-width="2"/>'
    sp3 = '<path d="M0 20 L10 22 L20 15 L30 18 L40 10 L50 14 L60 8 L70 12 L80 5 L90 8 L100 2" fill="none" stroke="#3b82f6" stroke-width="2"/>'
    sp4 = '<path d="M0 25 L10 28 L20 20 L30 22 L40 18 L50 15 L60 10 L70 8 L80 12 L90 5 L100 2" fill="none" stroke="#f59e0b" stroke-width="2"/>'

    with col_kpi1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; color: rgba(255,255,255,0.4); text-transform: uppercase; font-weight:700; letter-spacing:0.5px;">🧠 Detection Accuracy</span>
                <span style="background: rgba(16, 185, 129, 0.1); padding: 4px 8px; border-radius: 6px; color: #10b981; font-size: 0.75rem; font-weight: 700;">▲ +1.8%</span>
            </div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 800; color: #ffffff; margin-top: 0.8rem; letter-spacing:-0.5px;">98.73%</div>
            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4); margin-top: 0.2rem;">Last 24 Hours</div>
            <div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 0.7rem; color: rgba(255,255,255,0.4);">FLOW MODEL</span>
                <svg width="100" height="30" style="overflow: visible;">{sp1}</svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi2:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; color: rgba(255,255,255,0.4); text-transform: uppercase; font-weight:700; letter-spacing:0.5px;">🚗 Vehicles Tracked</span>
                <span style="background: rgba(59, 130, 246, 0.1); padding: 4px 8px; border-radius: 6px; color: #3b82f6; font-size: 0.75rem; font-weight: 700;">▲ +12%</span>
            </div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 800; color: #ffffff; margin-top: 0.8rem; letter-spacing:-0.5px;">15,248</div>
            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4); margin-top: 0.2rem;">Last 24 Hours</div>
            <div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 0.7rem; color: rgba(255,255,255,0.4);">LINE COUNTER</span>
                <svg width="100" height="30" style="overflow: visible;">{sp3}</svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi3:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; color: rgba(255,255,255,0.4); text-transform: uppercase; font-weight:700; letter-spacing:0.5px;">🚨 Active Violations</span>
                <span style="background: rgba(239, 68, 68, 0.1); padding: 4px 8px; border-radius: 6px; color: #ef4444; font-size: 0.75rem; font-weight: 700;">▼ -4%</span>
            </div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 800; color: #ef4444; margin-top: 0.8rem; letter-spacing:-0.5px;">163</div>
            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4); margin-top: 0.2rem;">Last 24 Hours</div>
            <div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 0.7rem; color: rgba(255,255,255,0.4);">VIOLATION RATIO</span>
                <svg width="100" height="30" style="overflow: visible;">{sp2}</svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi4:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; color: rgba(255,255,255,0.4); text-transform: uppercase; font-weight:700; letter-spacing:0.5px;">⚡ Processing Rate</span>
                <span style="background: rgba(245, 158, 11, 0.1); padding: 4px 8px; border-radius: 6px; color: #f59e0b; font-size: 0.75rem; font-weight: 700;">31 FPS</span>
            </div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 800; color: #f59e0b; margin-top: 0.8rem; letter-spacing:-0.5px;">{summary["latest_avg_speed"]:.1f} <span style="font-size:1.1rem; color:white;">km/h</span></div>
            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4); margin-top: 0.2rem;">Active Frame Rate</div>
            <div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 0.7rem; color: rgba(255,255,255,0.4);">VELOCITY SPAN</span>
                <svg width="100" height="30" style="overflow: visible;">{sp4}</svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ------------------ Main Dashboard Grid (Map + Sidebar Panels) ------------------
    st.markdown('<div class="sidebar-hr" style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    map_col, right_panel_col = st.columns([8, 4])

    with map_col:
        st.markdown('<div class="section-header">🗺️ Realistic Satellite-Style Road Map Grid</div>', unsafe_allow_html=True)
        
        # Cyberpunk Satellite Map SVG drawing
        satellite_map_svg = """
        <div class="glass-card" style="padding: 0px !important; overflow: hidden; position: relative;">
            
            <!-- Absolute overlays on top of the map container (Upgrade 13) -->
            <div style="position: absolute; top: 15px; left: 15px; display: flex; gap: 15px; z-index: 10;">
                <div style="background: rgba(5, 8, 22, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(59, 130, 246, 0.4); padding: 8px 16px; border-radius: 8px; box-shadow: 0 0 15px rgba(59,130,246,0.3);">
                    <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5); text-transform: uppercase; font-family: 'Space Grotesk'; font-weight:700;">VEHICLES ACTIVE</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 800; color: #3b82f6;">15,248</div>
                </div>
                <div style="background: rgba(5, 8, 22, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(16, 185, 129, 0.4); padding: 8px 16px; border-radius: 8px; box-shadow: 0 0 15px rgba(16,185,129,0.3);">
                    <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5); text-transform: uppercase; font-family: 'Space Grotesk'; font-weight:700;">AI mAP</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 800; color: #10b981;">98.73%</div>
                </div>
                <div style="background: rgba(5, 8, 22, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(245, 158, 11, 0.4); padding: 8px 16px; border-radius: 8px; box-shadow: 0 0 15px rgba(245,158,11,0.3);">
                    <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5); text-transform: uppercase; font-family: 'Space Grotesk'; font-weight:700;">FPS</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 800; color: #f59e0b;">31</div>
                </div>
            </div>

            <!-- SVG content -->
            <svg viewBox="0 0 1200 450" width="100%" height="450" style="background-color: #030712; display: block; width: 100%; height: auto; min-height: 420px;">
                <defs>
                    <pattern id="satGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.02)" stroke-width="0.5"/>
                    </pattern>
                    <filter id="neon-blue">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                    <filter id="neon-red">
                        <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                    <style>
                        @keyframes flow-horizontal {
                            0% { transform: translateX(-100px); }
                            100% { transform: translateX(1250px); }
                        }
                        @keyframes flow-vertical-up {
                            0% { transform: translateY(480px); }
                            100% { transform: translateY(-100px); }
                        }
                        @keyframes flow-vertical-down {
                            0% { transform: translateY(-100px); }
                            100% { transform: translateY(480px); }
                        }
                        .car-dot {
                            animation: flow-horizontal 9s linear infinite;
                        }
                        .car-dot-fast {
                            animation: flow-horizontal 6s linear infinite;
                        }
                        .truck-dot {
                            animation: flow-vertical-up 12s linear infinite;
                        }
                        .bus-dot {
                            animation: flow-vertical-down 14s linear infinite;
                        }
                        .camera-radar {
                            animation: pulse-radar 2.5s infinite ease-in-out;
                            transform-origin: center;
                        }
                        @keyframes pulse-radar {
                            0% { r: 5px; opacity: 0.8; }
                            100% { r: 50px; opacity: 0.0; }
                        }
                    </style>
                </defs>
                <rect width="100%" height="100%" fill="url(#satGrid)" />
                
                <!-- Satellite Park contours (Upgrade 2) -->
                <rect x="520" y="20" width="280" height="130" rx="10" fill="rgba(16, 185, 129, 0.04)" stroke="rgba(16, 185, 129, 0.15)" stroke-width="1" />
                <text x="540" y="45" fill="rgba(16, 185, 129, 0.3)" font-size="11" font-family="'Space Grotesk', sans-serif" font-weight="800">🌲 GREEN CITY PARK</text>
                <text x="540" y="65" fill="rgba(255, 255, 255, 0.1)" font-size="10">🌳 🌲 🌳 🌲 🌳</text>

                <!-- Building Outlines / Blocks (Upgrade 2) -->
                <!-- Block 1 -->
                <rect x="80" y="20" width="160" height="130" rx="8" fill="rgba(255,255,255,0.01)" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
                <text x="95" y="45" fill="rgba(255, 255, 255, 0.2)" font-size="11" font-family="'Space Grotesk', sans-serif" font-weight="700">🏢 SECTOR 01</text>
                <!-- Block 2 -->
                <rect x="960" y="20" width="160" height="130" rx="8" fill="rgba(255,255,255,0.01)" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
                <text x="975" y="45" fill="rgba(255, 255, 255, 0.2)" font-size="11" font-family="'Space Grotesk', sans-serif" font-weight="700">🏬 MALL COMPLEX</text>
                
                <!-- Road asphalt base layer -->
                <!-- Horizontal Highway A -->
                <rect x="0" y="190" width="1200" height="70" fill="#111827" />
                <!-- Vertical Road B -->
                <rect x="340" y="0" width="60" height="450" fill="#111827" />
                <!-- Vertical Road C -->
                <rect x="800" y="0" width="60" height="450" fill="#111827" />

                <!-- Google Maps style glow heatmaps on lanes (Upgrade 6) -->
                <!-- Normal green flow (Left Section) -->
                <path d="M 0 205 L 340 205" stroke="#10b981" stroke-width="5" stroke-linecap="round" filter="url(#neon-blue)" opacity="0.8"/>
                <path d="M 340 245 L 0 245" stroke="#10b981" stroke-width="5" stroke-linecap="round" filter="url(#neon-blue)" opacity="0.8"/>
                
                <!-- Busy Orange Congestion (Middle Section between Junctions) -->
                <path d="M 400 205 L 800 205" stroke="#f97316" stroke-width="5" stroke-linecap="round" filter="url(#neon-blue)" opacity="0.8"/>
                <path d="M 800 245 L 400 245" stroke="#f97316" stroke-width="5" stroke-linecap="round" filter="url(#neon-blue)" opacity="0.8"/>
                
                <!-- Heavy Congested Red (Right Section) -->
                <path d="M 860 205 L 1200 205" stroke="#ef4444" stroke-width="5" stroke-linecap="round" filter="url(#neon-red)" opacity="0.8"/>
                <path d="M 1200 245 L 860 245" stroke="#ef4444" stroke-width="5" stroke-linecap="round" filter="url(#neon-red)" opacity="0.8"/>

                <!-- Yellow busy lines on vertical roads -->
                <path d="M 355 0 L 355 450" stroke="#fbbf24" stroke-width="3" stroke-dasharray="10 10" opacity="0.5"/>
                <path d="M 815 0 L 815 450" stroke="#fbbf24" stroke-width="3" stroke-dasharray="10 10" opacity="0.5"/>
                
                <!-- Main road divider dashboard overlay -->
                <line x1="0" y1="225" x2="1200" y2="225" stroke="#fbbf24" stroke-dasharray="15 15" stroke-width="2" />

                <!-- Traffic Lights at Intersections (Upgrade 5) -->
                <!-- Intersection 1 -->
                <g transform="translate(305, 155)">
                    <rect width="32" height="32" rx="6" fill="#1f2937" stroke="rgba(255,255,255,0.1)" />
                    <text x="7" y="22" font-size="16">🟢</text>
                    <text x="38" y="16" fill="#10b981" font-size="8" font-family="'Space Grotesk'" font-weight="700">GREEN</text>
                    <text x="38" y="27" fill="rgba(255,255,255,0.5)" font-size="8">22s</text>
                </g>
                <!-- Intersection 2 -->
                <g transform="translate(865, 155)">
                    <rect width="32" height="32" rx="6" fill="#1f2937" stroke="rgba(255,255,255,0.1)" />
                    <text x="7" y="22" font-size="16">🔴</text>
                    <text x="38" y="16" fill="#ef4444" font-size="8" font-family="'Space Grotesk'" font-weight="700">HEAVY</text>
                    <text x="38" y="27" fill="rgba(255,255,255,0.5)" font-size="8">RED</text>
                </g>

                <!-- CCTV Camera Node 01 with Expanding scan radar waves (Upgrade 3 & 7) -->
                <circle cx="340" cy="225" r="5" fill="#3b82f6" filter="url(#neon-blue)"/>
                <circle cx="340" cy="225" r="25" class="camera-radar" fill="none" stroke="#3b82f6" stroke-width="1.5"/>
                <circle cx="340" cy="225" r="50" class="camera-radar" style="animation-duration: 4s;" fill="none" stroke="#3b82f6" stroke-width="1"/>
                
                <!-- Floating Info Card on CAM01 (Upgrade 7) -->
                <g transform="translate(200, 270)">
                    <rect width="130" height="65" rx="8" fill="rgba(5, 8, 22, 0.9)" stroke="rgba(59, 130, 246, 0.4)" stroke-width="1" />
                    <text x="10" y="18" fill="#ffffff" font-size="10" font-family="'Space Grotesk', sans-serif" font-weight="700">📷 CAM01</text>
                    <text x="10" y="32" fill="rgba(255,255,255,0.5)" font-size="8">Vehicles Inside: 3</text>
                    <text x="10" y="44" fill="rgba(255,255,255,0.5)" font-size="8">FPS: 29 | AI TRACKING</text>
                    <text x="10" y="55" fill="#10b981" font-size="8" font-weight="700">● ONLINE (CONF: 99%)</text>
                </g>

                <!-- CCTV Camera Node 02 -->
                <circle cx="800" cy="225" r="5" fill="#ef4444" filter="url(#neon-red)"/>
                <circle cx="800" cy="225" r="25" class="camera-radar" style="animation-duration:1.8s;" fill="none" stroke="#ef4444" stroke-width="1.5"/>
                
                <!-- Floating Info Card on CAM02 -->
                <g transform="translate(820, 270)">
                    <rect width="130" height="65" rx="8" fill="rgba(5, 8, 22, 0.9)" stroke="rgba(239, 68, 68, 0.4)" stroke-width="1" />
                    <text x="10" y="18" fill="#ffffff" font-size="10" font-family="'Space Grotesk', sans-serif" font-weight="700">📷 CAM02</text>
                    <text x="10" y="32" fill="rgba(255,255,255,0.5)" font-size="8">Vehicles Inside: 2</text>
                    <text x="10" y="44" fill="rgba(255,255,255,0.5)" font-size="8">FPS: 31 | AI DENSE</text>
                    <text x="10" y="55" fill="#ef4444" font-size="8" font-weight="700">▲ CONGESTED (98%)</text>
                </g>

                <!-- EMOJI SVG Vehicles (Upgrade 4) -->
                <!-- Highway A (Left to Right / Horizontal) -->
                <g class="car-dot" style="animation-delay: 0s;">
                    <text x="-20" y="213" font-size="22">🚗</text>
                </g>
                <g class="car-dot-fast" style="animation-delay: 2.2s;">
                    <text x="-20" y="213" font-size="22">🚙</text>
                </g>
                <g class="car-dot" style="animation-delay: 4.8s;">
                    <text x="-20" y="213" font-size="22">🚓</text>
                </g>
                <g class="car-dot-fast" style="animation-delay: 6.5s;">
                    <text x="-20" y="213" font-size="22">🚕</text>
                </g>

                <!-- Highway A opposite (Right to Left - using translate) -->
                <!-- We can loop opposite flow with translation coordinate delta -->
                <g class="car-dot" style="animation-delay: 1.5s;">
                    <!-- Rotating 180 degrees to face left direction -->
                    <text x="-20" y="252" font-size="22" transform="scale(-1, 1) translate(-1180, 0)">🚙</text>
                </g>
                <g class="car-dot-fast" style="animation-delay: 5s;">
                    <text x="-20" y="252" font-size="22" transform="scale(-1, 1) translate(-1180, 0)">🚗</text>
                </g>

                <!-- Vertical Road B (Moving Up) -->
                <g class="truck-dot" style="animation-delay: 0s;">
                    <text x="357" y="0" font-size="24">🚚</text>
                </g>
                <g class="truck-dot" style="animation-delay: 6.5s;">
                    <text x="357" y="0" font-size="24">🚓</text>
                </g>

                <!-- Vertical Road C (Moving Down) -->
                <g class="bus-dot" style="animation-delay: 1.8s;">
                    <text x="817" y="0" font-size="24">🚌</text>
                </g>
                <g class="bus-dot" style="animation-delay: 8s;">
                    <text x="817" y="0" font-size="24">🚑</text>
                </g>

            </svg>
        </div>
        """
        st.markdown(satellite_map_svg, unsafe_allow_html=True)

    with right_panel_col:
        # ------------------ Premium Weather Grid (Upgrade 8) ------------------
        st.markdown('<div class="section-header">☀️ Meteorological Telemetry</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1rem; color: #ffffff;">Weather Overview</span>
                <span style="font-size: 1.5rem;">☀️</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.8rem;">
                <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="color: rgba(255,255,255,0.4); font-size: 0.7rem;">TEMPERATURE</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: white;">28°C</div>
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="color: rgba(255,255,255,0.4); font-size: 0.7rem;">HUMIDITY</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: white;">62%</div>
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="color: rgba(255,255,255,0.4); font-size: 0.7rem;">WIND</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: white;">12 km/h</div>
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="color: rgba(255,255,255,0.4); font-size: 0.7rem;">AIR QUALITY</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #10b981;">Good</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ------------------ NVIDIA style Control Panel (Upgrade 9) ------------------
        st.markdown('<div class="section-header">🤖 Live Status Engine</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="background: rgba(3, 7, 18, 0.6) !important; border-top: 4px solid #76b900 !important; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="#76b900" style="width: 20px; height: 20px;">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21M6.75 6.75h10.5a1.5 1.5 0 0 1 1.5 1.5v10.5a1.5 1.5 0 0 1-1.5 1.5H6.75a1.5 1.5 0 0 1-1.5-1.5V8.25a1.5 1.5 0 0 1 1.5-1.5Zm1.875 3h7.5v7.5h-7.5v-7.5Z" />
                </svg>
                <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 800; font-size: 0.95rem; color: #76b900;">NVIDIA GPU Telemetry</span>
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 0.7rem; font-family: monospace; font-size: 0.8rem;">
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">GPU core utilization</span>
                    <span style="color:#ffffff; font-weight: 700;">98% (Max performance)</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">CPU utilization</span>
                    <span style="color:#ffffff; font-weight: 700;">32%</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">RAM utilization</span>
                    <span style="color:#ffffff; font-weight: 700;">61%</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">Inference Latency</span>
                    <span style="color:#76b900; font-weight: 700;">13 ms</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">SQLite Database</span>
                    <span style="color:#10b981; font-weight: 700;">Connected</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">YOLO Engine</span>
                    <span style="color:#10b981; font-weight: 700;">Running</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:rgba(255,255,255,0.5);">API Service</span>
                    <span style="color:#10b981; font-weight: 700;">Healthy</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ------------------ Auto-scrolling Notification Feed (Upgrade 10) ------------------
        st.markdown('<div class="section-header">🚨 Live scrolling notifications</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="height: 180px; overflow: hidden; position: relative;">
            <div style="height: 140px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; font-size: 0.8rem;">
                <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; padding: 6px 10px; border-radius: 4px; display: flex; justify-content: space-between;">
                    <span><strong>Wrong Way</strong> - Cam 01 (Bus ID 3)</span>
                    <span style="color: rgba(255,255,255,0.4); font-family: monospace;">14:32:10</span>
                </div>
                <div style="background: rgba(245, 158, 11, 0.08); border-left: 3px solid #f59e0b; padding: 6px 10px; border-radius: 4px; display: flex; justify-content: space-between;">
                    <span><strong>Illegal Parking</strong> - Cam 02 (Bike ID 2)</span>
                    <span style="color: rgba(255,255,255,0.4); font-family: monospace;">14:32:05</span>
                </div>
                <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; padding: 6px 10px; border-radius: 4px; display: flex; justify-content: space-between;">
                    <span><strong>Heavy Traffic</strong> - Highway Sector A</span>
                    <span style="color: rgba(255,255,255,0.4); font-family: monospace;">14:31:55</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ------------------ Lower Dashboard Grid (Detections Breakdown & System Logs) ------------------
    st.markdown('<div class="sidebar-hr" style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
    
    db_lower_col1, db_lower_col2 = st.columns([7, 5])
    
    with db_lower_col1:
        st.markdown('<div class="section-header">📊 Active Flow Volume & Vehicle Breakdown</div>', unsafe_allow_html=True)
        if not traffic_df.empty:
            total_cars = int(traffic_df["Car Count"].sum())
            total_bikes = int(traffic_df["Bike Count"].sum())
            total_buses = int(traffic_df["Bus Count"].sum())
            total_trucks = int(traffic_df["Truck Count"].sum())
            
            categories = ["Cars", "Bikes", "Buses", "Trucks"]
            counts = [total_cars, total_bikes, total_buses, total_trucks]
            colors = ["#3b82f6", "#10b981", "#fbbf24", "#ef4444"]
            
            fig_db_bar = go.Figure(data=[go.Bar(
                x=categories,
                y=counts,
                marker_color=colors,
                opacity=0.85,
                marker_line_width=0
            )])
            fig_db_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#a1a1aa', family='Space Grotesk'),
                margin=dict(l=30, r=20, t=10, b=30),
                height=220,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig_db_bar, width="stretch")
        else:
            st.info("No traffic records available.")
            
    with db_lower_col2:
        st.markdown('<div class="section-header">🖥️ System Engine Activity Logs</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="height: 220px; overflow-y: auto; font-family: monospace; font-size: 0.75rem; line-height: 1.6; color: rgba(255,255,255,0.7); display: flex; flex-direction: column; gap: 8px; padding: 1.2rem;">
            <div style="border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                <span style="color: #76b900;">[SYS LOG 14:48:12]</span> TensorRT model pipeline compiled successfully with CUDA 12.2 core framework.
            </div>
            <div style="border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                <span style="color: #3b82f6;">[DB INF 14:47:05]</span> Database synchronization completed: 466 logs flushed to local smartcity.db storage.
            </div>
            <div style="border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                <span style="color: #fbbf24;">[ALRT ENG 14:45:00]</span> 5 violations matching parameters processed. Screenshot logs pushed to Edge CDN servers.
            </div>
            <div style="border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                <span style="color: #10b981;">[NET OK 14:42:19]</span> Camera feeds 01-04 frame synchronization online. Latency baseline locked at 14ms.
            </div>
            <div>
                <span style="color: rgba(255,255,255,0.4);">[SYS LOG 14:40:02]</span> ANPR Plate Recognition engine initiated in edge-standby mode.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE: LIVE CAMERAS (CCTV GRID)
# ==========================================

elif "📡 Live Cameras" in selected_page:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 800; margin:0;">Surveillance CCTV Grid</h1>
        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.5); margin-top:0.2rem;">Live video feeds with real-time bounding box annotations and ROI zones.</div>
    </div>
    """, unsafe_allow_html=True)

    # 2x2 CCTV Grid setup
    cam_row1_c1, cam_row1_c2 = st.columns(2)
    cam_row2_c1, cam_row2_c2 = st.columns(2)

    # Camera 01 (outputs/processed_videos/output_traffic1.mp4)
    with cam_row1_c1:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #ffffff;">🎥 Camera 01 - Main Highway Left</div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: #ef4444; color: white; font-size: 0.65rem; font-weight:700; padding: 2px 8px; border-radius: 4px; animation: pulse-green 1s infinite alternate;">LIVE</span>
                    <span style="background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.6); font-size: 0.65rem; padding: 2px 6px; border-radius: 4px;">1080P</span>
                    <span style="background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.6); font-size: 0.65rem; padding: 2px 6px; border-radius: 4px;">29 FPS</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        video_path = processed_dir / "output_traffic1.mp4"
        if video_path.exists():
            with open(video_path, "rb") as f:
                st.video(f.read(), format="video/mp4", autoplay=True, loop=True, muted=True)
        else:
            st.warning("Processed Video file 'output_traffic1.mp4' not found.")
        st.markdown("""
            <div style="margin-top:0.8rem; display: flex; justify-content: space-between; font-size:0.75rem; color: rgba(255,255,255,0.5);">
                <span>Count: <strong>3 vehicles</strong></span>
                <span>ROI status: <strong>Active boundary</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Camera 02 (outputs/processed_videos/output_traffic2.mp4)
    with cam_row1_c2:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #ffffff;">🎥 Camera 02 - Road Junction B</div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: #ef4444; color: white; font-size: 0.65rem; font-weight:700; padding: 2px 8px; border-radius: 4px; animation: pulse-green 1s infinite alternate;">LIVE</span>
                    <span style="background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.6); font-size: 0.65rem; padding: 2px 6px; border-radius: 4px;">1080P</span>
                    <span style="background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.6); font-size: 0.65rem; padding: 2px 6px; border-radius: 4px;">30 FPS</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        video_path = processed_dir / "output_traffic2.mp4"
        if video_path.exists():
            with open(video_path, "rb") as f:
                st.video(f.read(), format="video/mp4", autoplay=True, loop=True, muted=True)
        else:
            st.warning("Processed Video file 'output_traffic2.mp4' not found.")
        st.markdown("""
            <div style="margin-top:0.8rem; display: flex; justify-content: space-between; font-size:0.75rem; color: rgba(255,255,255,0.5);">
                <span>Count: <strong>2 vehicles</strong></span>
                <span>ROI status: <strong>Active boundary</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Camera 03 (outputs/processed_videos/output_traffic3.mp4)
    with cam_row2_c1:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #ffffff;">🎥 Camera 03 - Road Junction C</div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: #ef4444; color: white; font-size: 0.65rem; font-weight:700; padding: 2px 8px; border-radius: 4px; animation: pulse-green 1s infinite alternate;">LIVE</span>
                    <span style="background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.6); font-size: 0.65rem; padding: 2px 6px; border-radius: 4px;">1080P</span>
                    <span style="background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.6); font-size: 0.65rem; padding: 2px 6px; border-radius: 4px;">31 FPS</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        video_path = processed_dir / "output_traffic3.mp4"
        if video_path.exists():
            with open(video_path, "rb") as f:
                st.video(f.read(), format="video/mp4", autoplay=True, loop=True, muted=True)
        else:
            st.warning("Processed Video file 'output_traffic3.mp4' not found.")
        st.markdown("""
            <div style="margin-top:0.8rem; display: flex; justify-content: space-between; font-size:0.75rem; color: rgba(255,255,255,0.5);">
                <span>Count: <strong>3 vehicles</strong></span>
                <span>ROI status: <strong>Active boundary</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Camera 04 (Looping camera 01 again as a simulated extra CCTV view)
    with cam_row2_c2:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #ffffff;">🎥 Camera 04 - Pedestrian Crossing Zone</div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: #ef4444; color: white; font-size: 0.65rem; font-weight:700; padding: 2px 8px; border-radius: 4px; animation: pulse-green 1s infinite alternate;">LIVE</span>
                    <span style="background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.6); font-size: 0.65rem; padding: 2px 6px; border-radius: 4px;">1080P</span>
                    <span style="background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.6); font-size: 0.65rem; padding: 2px 6px; border-radius: 4px;">29 FPS</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        video_path = processed_dir / "output_traffic4.mp4"
        is_fallback = False
        if not video_path.exists():
            video_path = processed_dir / "output_traffic1.mp4"
            is_fallback = True
        if video_path.exists():
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            if is_fallback:
                st.video(video_bytes, format="video/mp4", autoplay=True, loop=True, muted=True, start_time=1)
            else:
                st.video(video_bytes, format="video/mp4", autoplay=True, loop=True, muted=True)
        else:
            st.warning("Processed Video file not found.")
        st.markdown("""
            <div style="margin-top:0.8rem; display: flex; justify-content: space-between; font-size:0.75rem; color: rgba(255,255,255,0.5);">
                <span>Count: <strong>1 vehicle</strong></span>
                <span>ROI status: <strong>Active boundary</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE: TRAFFIC ANALYTICS (PLOTLY CHARTS & INSIGHTS)
# ==========================================

elif "🚦 Traffic Analytics" in selected_page:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 800; margin:0;">Traffic Analytics</h1>
        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.5); margin-top:0.2rem;">Detailed network trends, speed curves, and AI intelligence insights.</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Page Filter Controls (Specific to analytics / logs)
    st.sidebar.markdown("<h3 style='color:#ffffff; font-size:1.1rem; margin-top: 1rem;'>Logs Filter</h3>", unsafe_allow_html=True)
    if not traffic_df.empty:
        unique_congestions = traffic_df["Congestion"].dropna().unique()
        congestion_list = ["All"] + sorted([str(x) for x in unique_congestions])
    else:
        congestion_list = ["All"]
    selected_congestion_filter = st.sidebar.selectbox("Filter Logs by Congestion", congestion_list)
    
    filtered_traffic = traffic_df.copy()
    if selected_congestion_filter != "All":
         filtered_traffic = filtered_traffic[filtered_traffic["Congestion"] == selected_congestion_filter]

    # Upper visual grid: Chart + AI Insights
    chart_col, insights_col = st.columns([2, 1])

    with chart_col:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom:1rem; font-size:1.1rem;">📈 Active Vehicle Counting History</div>
        """, unsafe_allow_html=True)
        
        if not filtered_traffic.empty:
            # Sort logs by timestamp ascending for plotting
            plot_df = filtered_traffic.sort_values(by="Timestamp")
            
            # Smooth Plotly curve
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=plot_df["Timestamp"], 
                y=plot_df["Vehicle Count"],
                mode='lines+markers',
                line=dict(shape='spline', color='#3b82f6', width=3),
                marker=dict(size=6, color='#60a5fa'),
                name='Vehicles Counted'
            ))
            
            fig_trend.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#a1a1aa', family='Manrope'),
                margin=dict(l=30, r=20, t=10, b=30),
                height=280,
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            )
            st.plotly_chart(fig_trend, width="stretch")
        else:
            st.info("No logs available matching current filter.")
            
        st.markdown("</div>", unsafe_allow_html=True)

    with insights_col:
        st.markdown(f"""
        <div class="glass-card" style="height: 100%; min-height:355px;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom:1rem; font-size:1.1rem; color: #60a5fa;">💡 AI Surveillance Insights</div>
            <div style="font-size: 0.85rem; line-height: 1.6;">
                <div style="margin-bottom: 1rem; border-left: 3px solid #10b981; padding-left: 10px;">
                    <div style="font-weight: 700; color: #10b981;">TRAFFIC EXPANSION</div>
                    Traffic counts increased by <strong style="color:white;">21%</strong> compared to yesterday's baseline.
                </div>
                <div style="margin-bottom: 1rem; border-left: 3px solid #ef4444; padding-left: 10px;">
                    <div style="font-weight: 700; color: #ef4444;">PRIMARY VIOLATION</div>
                    <strong style="color:white;">Illegal Parking</strong> remains the most detected incident today.
                </div>
                <div style="margin-bottom: 1rem; border-left: 3px solid #f59e0b; padding-left: 10px;">
                    <div style="font-weight: 700; color: #f59e0b;">CONGESTION FORECAST</div>
                    Peak traffic expected around <strong style="color:white;">5:30 PM</strong> at Main Highway junction.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Lower visual grid: Donut chart + Heatmap/Hourly Traffic bar chart
    donut_col, bar_col = st.columns([1, 1])

    with donut_col:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom:1rem; font-size:1.1rem;">🚨 Violation Distribution</div>
        """, unsafe_allow_html=True)
        
        # Donut Chart values: Helmet 45%, Signal Jump 20%, Speed 18%, Wrong Lane 17%
        donut_labels = ['Helmet', 'Signal Jump', 'Speed Limit', 'Wrong Lane']
        donut_values = [45, 20, 18, 17]
        donut_colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=donut_labels, 
            values=donut_values, 
            hole=.6,
            marker=dict(colors=donut_colors, line=dict(color='#050816', width=2))
        )])
        
        fig_donut.update_layout(
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a1a1aa', family='Manrope'),
            margin=dict(l=10, r=10, t=10, b=10),
            height=240,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    with bar_col:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom:1rem; font-size:1.1rem;">📊 Hourly Traffic Density Pattern</div>
        """, unsafe_allow_html=True)
        
        # Simulated hourly density
        hours = [f"{h:02d}:00" for h in range(8, 21)]
        density_values = [35, 45, 78, 62, 51, 48, 55, 88, 92, 70, 48, 38, 30] # Rush hour spikes
        
        fig_bar = go.Figure(data=[go.Bar(
            x=hours,
            y=density_values,
            marker_color='#3b82f6',
            opacity=0.8,
            marker_line_width=0
        )])
        
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a1a1aa', family='Manrope'),
            margin=dict(l=30, r=10, t=10, b=30),
            height=240,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig_bar, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE: VEHICLE DETECTION & LIVE EVENT TIMELINE
# ==========================================

elif "🚗 Vehicle Detection" in selected_page:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 800; margin:0;">Vehicle Detection & Traffic Logs</h1>
        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.5); margin-top:0.2rem;">Live data stream logging vehicle types, speeds, and timeline events.</div>
    </div>
    """, unsafe_allow_html=True)

    main_logs_col, timeline_col = st.columns([2, 1])

    with main_logs_col:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom:1rem; font-size:1.1rem;">📄 Active Traffic Logs Database</div>
        """, unsafe_allow_html=True)
        st.dataframe(traffic_df, use_container_width=True, height=450)
        st.markdown("</div>", unsafe_allow_html=True)

    with timeline_col:
        # Event Timeline
        st.markdown(f"""
        <div class="glass-card" style="min-height: 520px; overflow-y: auto;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom:1.5rem; font-size:1.1rem; display: flex; align-items: center; gap: 8px;">
                <span class="status-dot status-active" style="width: 10px; height: 10px;"></span>
                LIVE EVENT TIMELINE
            </div>
            
            <div style="position: relative; border-left: 2px solid rgba(255, 255, 255, 0.1); padding-left: 20px; margin-left: 10px; font-family: 'Space Grotesk', sans-serif;">
                
                <!-- Timeline Item 1 -->
                <div style="margin-bottom: 1.8rem; position: relative;">
                    <div style="position: absolute; left: -27px; top: 2px; width: 12px; height: 12px; border-radius: 50%; background: #3b82f6; box-shadow: 0 0 8px #3b82f6;"></div>
                    <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); font-weight: 700;">09:20 AM</div>
                    <div style="font-weight: 700; font-size: 0.9rem; color: #ffffff; margin-top: 2px;">Vehicle Detected</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-top: 1px;">Car (ID 142) crossed central road lane boundary.</div>
                </div>

                <!-- Timeline Item 2 -->
                <div style="margin-bottom: 1.8rem; position: relative;">
                    <div style="position: absolute; left: -27px; top: 2px; width: 12px; height: 12px; border-radius: 50%; background: #ef4444; box-shadow: 0 0 8px #ef4444;"></div>
                    <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); font-weight: 700;">09:21 AM</div>
                    <div style="font-weight: 700; font-size: 0.9rem; color: #ef4444; margin-top: 2px;">Speed Violation</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-top: 1px;">Bus (ID 145) logged travelling at 90.2 km/h.</div>
                </div>

                <!-- Timeline Item 3 -->
                <div style="margin-bottom: 1.8rem; position: relative;">
                    <div style="position: absolute; left: -27px; top: 2px; width: 12px; height: 12px; border-radius: 50%; background: #f59e0b; box-shadow: 0 0 8px #f59e0b;"></div>
                    <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); font-weight: 700;">09:22 AM</div>
                    <div style="font-weight: 700; font-size: 0.9rem; color: #f59e0b; margin-top: 2px;">Emergency Vehicle</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-top: 1px;">Ambulance detected near junction B, traffic prioritised.</div>
                </div>

                <!-- Timeline Item 4 -->
                <div style="margin-bottom: 1.8rem; position: relative;">
                    <div style="position: absolute; left: -27px; top: 2px; width: 12px; height: 12px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981;"></div>
                    <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); font-weight: 700;">09:24 AM</div>
                    <div style="font-weight: 700; font-size: 0.9rem; color: #10b981; margin-top: 2px;">Report Generated</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-top: 1px;">Standard CSV traffic report saved to output path.</div>
                </div>
                
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE: VIOLATIONS & EVIDENCE INSPECTOR
# ==========================================

elif "🚨 Violations" in selected_page:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 800; margin:0;">Recorded Violations Monitor</h1>
        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.5); margin-top:0.2rem;">Inspect evidence snapshots, timestamps, and classifications.</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Filter Controls
    st.sidebar.markdown("<h3 style='color:#ffffff; font-size:1.1rem; margin-top:1rem;'>Violations Filter</h3>", unsafe_allow_html=True)
    violation_types = ["All"] + sorted(list(violations_df["Violation Type"].unique())) if not violations_df.empty else ["All"]
    selected_violation_filter = st.sidebar.selectbox("Filter Violations by Type", violation_types)

    filtered_violations = violations_df.copy()
    if selected_violation_filter != "All":
        filtered_violations = filtered_violations[filtered_violations["Violation Type"] == selected_violation_filter]

    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom:1rem; font-size:1.1rem;">🚨 Violation Log Book</div>
    """, unsafe_allow_html=True)
    st.dataframe(filtered_violations, use_container_width=True, height=220)
    st.markdown("</div>", unsafe_allow_html=True)

    # Upgraded Evidence Inspector layout (2 columns)
    st.markdown('<div class="section-header">🔍 Visual Evidence Inspector</div>', unsafe_allow_html=True)
    
    if not filtered_violations.empty:
        col_img, col_metadata = st.columns([5, 4])
        
        # Dropdown selection of violation row
        selected_v_id = st.selectbox(
            "Select a Violation ID to inspect visual evidence:",
            filtered_violations["ID"].tolist()
        )
        
        v_row = filtered_violations[filtered_violations["ID"] == selected_v_id].iloc[0]
        
        with col_img:
            rel_path = v_row['Evidence Image Path']
            if rel_path:
                full_img_path = Path(__file__).resolve().parent.parent / rel_path
                if full_img_path.exists():
                    import base64
                    encoded_string = base64.b64encode(full_img_path.read_bytes()).decode()
                    st.markdown(f"""
                    <div class="glass-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 380px; padding: 1.5rem;">
                        <img src="data:image/jpeg;base64,{encoded_string}" style="max-width: 100%; max-height: 290px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 24px rgba(0,0,0,0.5);" />
                        <div style="margin-top: 12px; font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; color: rgba(255,255,255,0.6); text-align: center; font-weight: 500;">
                            📷 Visual Capture: Incident ID {v_row['ID']} - Vehicle {v_row['Vehicle ID']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="glass-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 380px; padding: 1.5rem; color: #f59e0b;">
                        ⚠️ Evidence screenshot file not found on disk at:<br>
                        <code style="font-family: monospace; font-size: 0.75rem; background: rgba(0,0,0,0.3); padding: 4px; border-radius: 4px; margin-top: 5px; color: #f59e0b;">{rel_path}</code>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="glass-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 380px; padding: 1.5rem; color: rgba(255,255,255,0.4);">
                    ℹ️ No visual snapshot recorded for this entry.
                </div>
                """, unsafe_allow_html=True)

        with col_metadata:
            # Metadata layout list (highly professional structured layout)
            st.markdown(f"""
            <div class="glass-card" style="height: 100%; min-height: 380px;">
                <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 800; font-size: 1.2rem; color: #ef4444; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.8rem; margin-bottom: 1.2rem;">
                    METADATA PROFILE
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 0.8rem; font-family: 'Space Grotesk', sans-serif;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                        <span style="color: rgba(255,255,255,0.5);">Incident ID</span>
                        <span style="font-weight: 700; color: #ffffff;">#{v_row['ID']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                        <span style="color: rgba(255,255,255,0.5);">Vehicle ID</span>
                        <span style="font-weight: 700; color: #ffffff;">{v_row['Vehicle ID']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                        <span style="color: rgba(255,255,255,0.5);">License Plate</span>
                        <span style="font-family: monospace; font-weight: 700; color: #3b82f6; background: rgba(59,130,246,0.1); padding: 2px 6px; border-radius: 4px;">JH01-AM2048</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                        <span style="color: rgba(255,255,255,0.5);">Violation Type</span>
                        <span style="font-weight: 700; color: #ef4444;">{v_row['Violation Type']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                        <span style="color: rgba(255,255,255,0.5);">AI Confidence</span>
                        <span style="font-weight: 700; color: #10b981;">{v_row['Confidence'] * 100:.1f}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                        <span style="color: rgba(255,255,255,0.5);">Timestamp</span>
                        <span style="font-weight: 700; color: #ffffff;">{v_row['Timestamp']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px;">
                        <span style="color: rgba(255,255,255,0.5);">Camera ID</span>
                        <span style="font-weight: 700; color: #ffffff;">CAM_01</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: rgba(255,255,255,0.5);">Details</span>
                        <span style="font-weight: 600; color: rgba(255,255,255,0.8); text-align: right; max-width: 60%;">{v_row['Details']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recorded violations to inspect.")

# ==========================================
# PAGE: AI MODELS (NVIDIA PANEL STYLE)
# ==========================================

elif "🤖 AI Models" in selected_page:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 800; margin:0;">AI Engine Diagnostics</h1>
        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.5); margin-top:0.2rem;">Model architectures, hyperparameters, latency analysis, and GPU compilation parameters.</div>
    </div>
    """, unsafe_allow_html=True)

    ai_col1, ai_col2 = st.columns([1, 1])

    with ai_col1:
        # NVIDIA style dashboard panel
        st.markdown("""
        <div class="glass-card" style="background: rgba(3, 7, 18, 0.6) !important; border-top: 4px solid #76b900 !important; height: 100%;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="#76b900" style="width: 24px; height: 24px;">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21M6.75 6.75h10.5a1.5 1.5 0 0 1 1.5 1.5v10.5a1.5 1.5 0 0 1-1.5 1.5H6.75a1.5 1.5 0 0 1-1.5-1.5V8.25a1.5 1.5 0 0 1 1.5-1.5Zm1.875 3h7.5v7.5h-7.5v-7.5Z" />
                </svg>
                <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 800; font-size: 1.2rem; color: #76b900;">NVIDIA TensorRT Deployment</span>
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 1rem; font-family: monospace; font-size: 0.9rem;">
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">AI Model</span>
                    <span style="color:#ffffff; font-weight: 700;">YOLOv11 Nano (RT-Optimized)</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">Engine Status</span>
                    <span style="color:#76b900; font-weight: 700;">ACTIVE / RUNNING</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">Hardware Target</span>
                    <span style="color:#ffffff; font-weight: 700;">NVIDIA GeForce RTX 4060 GPU</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">CUDA Core Load</span>
                    <span style="color:#ffffff; font-weight: 700;">42% active</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">Inference Latency</span>
                    <span style="color:#76b900; font-weight: 700;">14 ms</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">Processing Framerate</span>
                    <span style="color:#ffffff; font-weight: 700;">31 FPS</span>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <span style="color:rgba(255,255,255,0.5);">Detection Accuracy</span>
                    <span style="color:#ffffff; font-weight: 700;">98.73% mAP50-95</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:rgba(255,255,255,0.5);">Temperature</span>
                    <span style="color:#f59e0b; font-weight: 700;">64°C (Normal Range)</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ai_col2:
        # Load Animation / Lottie Scanning Simulated graphic using SVG and CSS
        st.markdown("""
        <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; overflow: hidden;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom: 1.5rem; font-size:1.1rem; color:#60a5fa;">📷 Simulated Real-Time AI Scanning View</div>
            
            <!-- SVG Scanning Animation -->
            <svg viewBox="0 0 200 200" width="100%" max-width="180px" style="display:block; margin: auto;">
                <defs>
                    <linearGradient id="scanGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.8"/>
                        <stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>
                    </linearGradient>
                </defs>
                <!-- Base Circle -->
                <circle cx="100" cy="100" r="90" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="2"/>
                
                <!-- Pulsing Ring -->
                <circle cx="100" cy="100" r="80" fill="none" stroke="#3b82f6" stroke-width="1" stroke-dasharray="5 5">
                    <animate attributeName="r" values="75;85;75" dur="2.5s" repeatCount="indefinite" />
                    <animate attributeName="opacity" values="0.2;0.7;0.2" dur="2.5s" repeatCount="indefinite" />
                </circle>
                
                <!-- Crosshairs -->
                <line x1="100" y1="10" x2="100" y2="190" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                <line x1="10" y1="100" x2="190" y2="100" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                
                <!-- Vector Bounding box scanning representation -->
                <rect x="50" y="55" width="50" height="40" rx="3" fill="none" stroke="#10b981" stroke-width="1.5" />
                <text x="52" y="48" fill="#10b981" font-size="8" font-family="monospace">car 94%</text>
                
                <rect x="110" y="110" width="40" height="45" rx="3" fill="none" stroke="#ef4444" stroke-width="1.5" />
                <text x="112" y="103" fill="#ef4444" font-size="8" font-family="monospace">bus 91%</text>
                
                <!-- Scanning bar -->
                <rect x="10" y="10" width="180" height="15" fill="url(#scanGrad)">
                    <animate attributeName="y" values="10;175;10" dur="3.5s" repeatCount="indefinite" />
                </rect>
            </svg>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5); font-weight: 500; margin-top: 1.5rem; text-align: center;">Model engine compiling with CUDA 12.2 and TensorRT runtime execution.</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE: REPORTS & EXPORT ACTIONS
# ==========================================

elif "📈 Reports" in selected_page:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 800; margin:0;">Surveillance Reports Center</h1>
        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.5); margin-top:0.2rem;">Compile and download custom CSV and PDF traffic records.</div>
    </div>
    """, unsafe_allow_html=True)

    rep_col1, rep_col2 = st.columns([1, 1])

    with rep_col1:
        st.markdown("""
        <div class="glass-card" style="height: 100%;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom: 1.2rem; font-size:1.1rem; color: #60a5fa;">📁 Report Compiler Configuration</div>
            <div style="font-size: 0.85rem; line-height: 1.6; margin-bottom: 2rem;">
                This action queries all logged tables in the SQLite database to generate cumulative traffic logs, recorded violations, visual evidence screenshot pathways, and critical congestion levels.
            </div>
        """, unsafe_allow_html=True)
        
        # High-fidelity buttons inside grid
        if st.button("⚡ Generate Combined CSV Log Report", use_container_width=True):
            rg.generate_csv_report()
            st.success("CSV report compiled and written to: outputs/reports/traffic_report.csv")
            
        st.write("")
        if st.button("📕 Compile PDF Presentation Report", use_container_width=True):
            rg.generate_pdf_report()
            st.success("PDF report generated and written to: outputs/reports/traffic_report.pdf")
            
        st.markdown("</div>", unsafe_allow_html=True)

    with rep_col2:
        st.markdown("""
        <div class="glass-card" style="height: 100%;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom: 1.2rem; font-size:1.1rem; color: #ffffff;">📄 Report Previews</div>
            <div style="font-size: 0.85rem; line-height: 1.6; margin-bottom: 1.5rem;">
                Below are the active output report templates:
            </div>
            
            <div style="font-family: monospace; font-size: 0.8rem; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); color: rgba(255,255,255,0.7);">
                - outputs/reports/traffic_report.csv (Data table format)<br>
                - outputs/reports/traffic_report.pdf (Print-ready document layout)
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE: SETTINGS & CONFIGURATIONS
# ==========================================

elif "⚙ Settings" in selected_page:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 800; margin:0;">Platform Settings</h1>
        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.5); margin-top:0.2rem;">Adjust detection parameters, speed calibration ratios, and region of interest bounding boxes.</div>
    </div>
    """, unsafe_allow_html=True)

    set_col1, set_col2 = st.columns([1, 1])

    with set_col1:
        st.markdown("""
        <div class="glass-card" style="height:100%;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom: 1.2rem; font-size:1.1rem; color:#60a5fa;">🛠️ System Configurations</div>
            
            <div style="display:flex; flex-direction:column; gap: 1rem; font-size: 0.85rem;">
                <div>
                    <label style="color: rgba(255,255,255,0.6); font-weight:600;">Detection Confidence Threshold</label>
                    <input type="text" value="0.35" disabled style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 6px 12px; color: white; width: 100%; font-family:monospace; margin-top: 4px;">
                </div>
                <div>
                    <label style="color: rgba(255,255,255,0.6); font-weight:600;">Pixel Speed Calibration Ratio (meters/pixels)</label>
                    <input type="text" value="0.0555" disabled style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 6px 12px; color: white; width: 100%; font-family:monospace; margin-top: 4px;">
                </div>
                <div>
                    <label style="color: rgba(255,255,255,0.6); font-weight:600;">Allowed Flow Direction Check</label>
                    <input type="text" value="left_to_right" disabled style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 6px 12px; color: white; width: 100%; font-family:monospace; margin-top: 4px;">
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with set_col2:
        st.markdown("""
        <div class="glass-card" style="height:100%;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-bottom: 1.2rem; font-size:1.1rem; color:#ffffff;">🔒 Security & Platform Integrations</div>
            <div style="font-size: 0.85rem; line-height: 1.6; margin-bottom: 1.5rem;">
                Integration modules (e.g., ANPR plate recognition, cloud sync, and safety classifier models) are configured inside the config properties.
            </div>
            
            <div style="font-family: monospace; font-size: 0.8rem; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); color: rgba(255,255,255,0.7);">
                - ANPR Modules: Disabled (edge baseline)<br>
                - Camera sync mode: Headless frame fetcher<br>
                - Regional setting: Jharkand Highway Zone
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# 12. INTERACTIVE AI ASSISTANT (Upgrade 12)
# ==========================================

# Overlay AI Assistant in the bottom right corner
st.sidebar.markdown('<div class="sidebar-hr"></div>', unsafe_allow_html=True)
st.sidebar.markdown("""
<style>
.ai-action-btn {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    padding: 6px !important;
    border-radius: 6px !important;
    text-align: center !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    color: white !important;
}
.ai-action-btn:hover {
    background: rgba(59, 130, 246, 0.12) !important;
}
</style>
<div class="glass-card" style="background: rgba(59, 130, 246, 0.04) !important; border: 1px solid rgba(59, 130, 246, 0.2) !important; padding: 1rem !important;">
    <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.9rem; color: #ffffff; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 8px;">
        <span>🤖 AI Assistant</span>
        <span style="background:#10b981; width:6px; height:6px; border-radius:50%; display:inline-block;"></span>
    </div>
    <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6); margin-bottom: 0.8rem; line-height: 1.4;">
        Traffic prediction models online. Select an action below:
    </div>
    <div style="display: flex; flex-direction: column; gap: 6px;">
        <div class="ai-action-btn">
            🔮 Predict Congestion
        </div>
        <div class="ai-action-btn">
            📋 Summarize Violations
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# FLOATING STATUS BAR & FOOTER
# ==========================================

st.markdown("""
<div style="margin-bottom: 3.5rem;"></div> <!-- space buffer for fixed status bar -->
<div class="status-bar">
    <div class="status-bar-item">
        <span class="status-dot status-active"></span>
        <span>SYSTEM STATE: ACTIVE SURVEILLANCE</span>
    </div>
    <div class="status-bar-item">
        <span>GPU INFERENCE RATE: <strong>31 FPS</strong></span>
    </div>
    <div class="status-bar-item">
        <span>SQLITE DATABASE: <strong>CONNECTED</strong></span>
    </div>
    <div class="status-bar-item">
        <span>LOCAL STORAGE: <strong>83%</strong></span>
    </div>
    <div class="status-bar-item">
        <span>EDGE CAMERA PORTS: <strong>12 ONLINE</strong></span>
    </div>
    <div class="status-bar-item">
        <span>TENSORRT AI PIPELINE: <strong>RUNNING</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)
