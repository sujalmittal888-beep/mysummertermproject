import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration for a Premium Feel
st.set_page_config(
    page_title="Quantum Analytics | Control Tower",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern Dark Theme Injector (Custom CSS for Polish)
st.markdown("""
    <style>
        /* Main background color tuning */
        .stApp { background-color: #0b0f19; color: #f3f4f6; }
        /* Premium custom metric cards styling */
        .metric-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }
        .metric-label { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px; color: #94a3b8; font-weight: 600; }
        .metric-value { font-size: 2.2rem; font-weight: 700; color: #f8fafc; margin: 8px 0; font-family: monospace; }
        .metric-delta { font-size: 0.9rem; font-weight: 500; display: flex; align-items: center; gap: 4px; }
        .delta-up { color: #10b981; }
        .delta-down { color: #ef4444; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Navigation & Branding
with st.sidebar:
    st.markdown("<h2 style='color: #38bdf8; margin-bottom: 0;'>QUANTUM</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.8rem; margin-top: 0; letter-spacing:1px;'>ANALYTICS SYSTEM v4.2</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### 🗺️ Operational Region")
    region = st.selectbox("Select Core Market", ["Global Operations", "North America", "EMEA Hub", "APAC Grid"])
    
    st.markdown("### 🎛️ Simulation Parameters")
    volatility = st.slider("Market Volatility Coefficient", 0.1, 2.0, 0.8, 0.1)
    st.caption("Adjusts synthetic standard deviation parameters dynamically.")
    
    st.divider()
    st.info("💡 **Pro Tip:** Toggle the top-right menu to view this system in fullscreen view.")

# 4. Header Section
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown(f"<h1 style='font-weight: 800; letter-spacing: -0.5px; margin-bottom: 4px;'>Executive Logistics Grid</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #94a3b8; font-size: 1.1rem;'>Real-time operational monitoring for <b>{region}</b></p>", unsafe_allow_html=True)
with col_status:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔄 Sync Live Pipeline", use_container_width=True, type="primary")

st.markdown("<br>", unsafe_allow_html=True)

# 5. High-Fidelity Custom Metric Grid
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-label">📊 Gross Throughput</div>
            <div class="metric-value">1,482.9M</div>
            <div class="metric-delta delta-up">▲ +12.4% <span style='color:#64748b;'>vs last week</span></div>
        </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-label">⚡ Active Nodes</div>
            <div class="metric-value">412 / 415</div>
            <div class="metric-delta delta-up">▲ +2 Active <span style='color:#64748b;'>nodes online</span></div>
        </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏱️ Avg Latency</div>
            <div class="metric-value">{24.3 * volatility:.1f}ms</div>
            <div class="metric-delta delta-down">▼ -4.1% <span style='color:#64748b;'>opt efficiency</span></div>
        </div>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-label">🔒 System Integrity</div>
            <div class="metric-value">99.98%</div>
            <div class="metric-delta delta-up" style="color: #38bdf8;">● Optimal <span style='color:#64748b;'>status check</span></div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. Advanced Visualization Area
graph_col1, graph_col2 = st.columns([2, 1])

# Generate realistic beautiful wave data
chart_days = 30
dates = pd.date_range(start="2026-05-12", periods=chart_days)
np.random.seed(42)
trend = np.linspace(100, 150, chart_days)
noise = np.random.randn(chart_days) * 15 * volatility

with graph_col1:
    st.markdown("<h4 style='font-weight: 600; color: #f1f5f9;'>📈 Predictive Resource Allocation</h4>", unsafe_allow_html=True)
    
    df_chart = pd.DataFrame({
        "Primary Feed": trend + noise,
        "Secondary Fail-safe": (trend * 0.85) + (noise * 0.5)
    }, index=dates)
    
    st.line_chart(
        df_chart, 
        color=["#0284c7", "#38bdf8"], 
        height=320,
        use_container_width=True
    )

with graph_col2:
    st.markdown("<h4 style='font-weight: 600; color: #f1f5f9;'>🎯 Load Distribution</h4>", unsafe_allow_html=True)
    
    df_bar = pd.DataFrame({
        "Capacity": [85, 92, 43, 67, 74]
    }, index=["Alpha Hub", "Beta Transit", "Gamma Node", "Delta Rail", "Epsilon Air"])
    
    st.bar_chart(
        df_bar, 
        color="#38bdf8", 
        height=320,
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# 7. Sleek Interactive Data Table Section
st.markdown("<h4 style='font-weight: 600; color: #f1f5f9;'>🔍 Real-Time Transaction Ledger</h4>", unsafe_allow_html=True)

# Modern interactive sample table
ledger_data = pd.DataFrame({
    "Routing ID": [f"TRK-{i:04d}" for i in range(1024, 1030)],
    "Origin Cluster": ["Munich_E2", "Austin_W1", "Tokyo_N4", "Singapore_S1", "Sydney_E9", "London_M2"],
    "Priority Rating": ["High", "Critical", "Low", "Medium", "High", "Critical"],
    "Payload Load (Tons)": [14.2, 45.1, 4.8, 22.9, 18.3, 31.0],
    "Node Handshake": [True, True, False, True, True, True]
})

# Display clean custom-styled dataframe natively
st.dataframe(
    ledger_data,
    use_container_width=True,
    column_config={
        "Routing ID": st.column_config.TextColumn("Routing Identifier"),
        "Node Handshake": st.column_config.CheckboxColumn("Handshake Verified"),
        "Payload Load (Tons)": st.column_config.NumberColumn(format="%.1f t"),
        "Priority Rating": st.column_config.SelectboxColumn(
            "Priority",
            options=["Low", "Medium", "High", "Critical"]
        )
    },
    hide_index=True
)
