"""
Store Comparison Page — Store-level aggregated metrics.
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config
from styles.theme import styled_plotly, PLOTLY_COLORS


def render():
    st.markdown("# 🏪 Store Comparison")
    st.markdown("Compare pricing strategies and competitiveness across stores")

    store_path = os.path.join(config.MATCHED_DIR, "store_metrics.csv")
    matched_path = os.path.join(config.MATCHED_DIR, "matched_products.csv")

    if not os.path.exists(store_path):
        st.warning("⚠️ Store metrics not found. Run the analysis pipeline first.")
        return

    store_df = pd.read_csv(store_path)
    matched = pd.read_csv(matched_path, low_memory=False) if os.path.exists(matched_path) else pd.DataFrame()

    # ── KPI Overview ───────────────────────────────────────
    cols = st.columns(len(store_df))
    for i, (_, row) in enumerate(store_df.iterrows()):
        with cols[i]:
            st.markdown(
                f"<div style='text-align:center;padding:1rem;background:rgba(20,20,35,0.85);"
                f"border-radius:16px;border:1px solid rgba(255,255,255,0.08);'>"
                f"<h3 style='color:{PLOTLY_COLORS[i]};margin:0;font-size:1.1rem;'>"
                f"{row['store']}</h3>"
                f"<p style='color:#9aa0a6;margin:0.2rem 0;font-size:0.8rem;'>Products</p>"
                f"<p style='color:#e8eaed;font-size:1.6rem;font-weight:800;margin:0;'>"
                f"{int(row['total_products']):,}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Price Index Comparison ─────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Price Index by Store")
        st.markdown("<small>Index > 1 = above average, < 1 = below average</small>", unsafe_allow_html=True)
        fig = px.bar(
            store_df, x="store", y="avg_price_index",
            color="store", color_discrete_sequence=PLOTLY_COLORS,
            labels={"avg_price_index": "Avg Price Index", "store": ""},
        )
        fig.add_hline(y=1.0, line_dash="dash", line_color="#5f6368",
                      annotation_text="Baseline (1.0)")
        fig = styled_plotly(fig)
        fig.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Volatility Score")
        st.markdown("<small>Average CV of product prices within each store</small>", unsafe_allow_html=True)
        if "volatility_score" in store_df.columns:
            fig = px.bar(
                store_df, x="store", y="volatility_score",
                color="store", color_discrete_sequence=PLOTLY_COLORS,
                labels={"volatility_score": "Volatility Score", "store": ""},
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Leadership & Median Deviation ──────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Price Leadership Frequency")
        if "leadership_pct" in store_df.columns:
            fig = px.pie(
                store_df, names="store", values="leadership_pct",
                color_discrete_sequence=PLOTLY_COLORS,
                hole=0.45,
            )
            fig.update_traces(
                textinfo="percent+label",
                textfont_size=13,
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("### Median Price Deviation (PKR)")
        if "median_deviation" in store_df.columns:
            fig = px.bar(
                store_df, x="store", y="median_deviation",
                color="store", color_discrete_sequence=PLOTLY_COLORS,
                labels={"median_deviation": "Median Deviation (PKR)", "store": ""},
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Detailed Store Metrics Table ───────────────────────
    st.markdown("### 📋 Detailed Store Metrics")
    display_cols = [
        "store", "total_products", "unique_products", "avg_price",
        "median_price", "avg_price_index", "categories", "brands",
        "cities", "volatility_score", "leadership_freq", "leadership_pct",
    ]
    available_cols = [c for c in display_cols if c in store_df.columns]
    st.dataframe(
        store_df[available_cols].style.format({
            "avg_price": "PKR {:.0f}",
            "median_price": "PKR {:.0f}",
            "avg_price_index": "{:.3f}",
            "volatility_score": "{:.2f}",
            "leadership_pct": "{:.1f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ── Box Plot: Price Distribution by Store ──────────────
    if not matched.empty and "price" in matched.columns:
        st.markdown("### Price Distribution by Store")
        trimmed = matched[matched["price"] < matched["price"].quantile(0.95)]
        fig = px.box(
            trimmed, x="store", y="price", color="store",
            color_discrete_sequence=PLOTLY_COLORS,
            labels={"price": "Price (PKR)", "store": ""},
        )
        fig = styled_plotly(fig)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
