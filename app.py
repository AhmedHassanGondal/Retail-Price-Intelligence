"""
Main Streamlit dashboard application.
Entry point: streamlit run app.py
"""
import streamlit as st
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from styles.theme import apply_theme

st.set_page_config(
    page_title="SuperScrape Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# ── Sidebar Navigation ────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🛒 SuperScrape")
    st.markdown("**Retail Price Intelligence**")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard Overview",
            "📈 Price Dispersion",
            "🏪 Store Comparison",
            "🏆 Leader Dominance",
            "🔗 Correlation Analysis",
            "🔍 Product Compare",
            "⚙️ Pipeline Status",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<p style='color: #5f6368; font-size: 0.75rem;'>"
        "Powered by SuperScrape Pipeline<br>"
        "Data Engineering Project</p>",
        unsafe_allow_html=True,
    )

# ── Page Routing ──────────────────────────────────────────────
if "Dashboard" in page:
    from views.dashboard import render
    render()
elif "Price Dispersion" in page:
    from views.price_dispersion import render
    render()
elif "Store Comparison" in page:
    from views.store_comparison import render
    render()
elif "Leader Dominance" in page:
    from views.leader_dominance import render
    render()
elif "Correlation" in page:
    from views.correlation_analysis import render
    render()
elif "Product Compare" in page:
    from views.product_compare import render
    render()
elif "Pipeline" in page:
    from views.pipeline_status import render
    render()
