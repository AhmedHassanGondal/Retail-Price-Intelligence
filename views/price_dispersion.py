"""
Price Dispersion Page — Product-level price comparison metrics.
Shows CV, IQR, price spread ratio, and RPPI across matched products.
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config
from styles.theme import styled_plotly, PLOTLY_COLORS


def render():
    st.markdown("# 📈 Price Dispersion Analysis")
    st.markdown("Explore how prices vary across stores for the same products")

    # Load data
    metrics_path = os.path.join(config.MATCHED_DIR, "product_metrics.csv")
    matched_path = os.path.join(config.MATCHED_DIR, "matched_products.csv")

    if not os.path.exists(metrics_path):
        st.warning("⚠️ Product metrics not found. Run the analysis pipeline first.")
        return pd.DataFrame(), pd.DataFrame()

    metrics = pd.read_csv(metrics_path)
    matched = pd.read_csv(matched_path, low_memory=False) if os.path.exists(matched_path) else pd.DataFrame()

    # ── Filters ────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        categories = ["All"] + sorted(metrics["category"].dropna().unique().tolist())
        sel_cat = st.selectbox("Category", categories)
    with col_f2:
        brands = ["All"] + sorted(metrics["brand"].dropna().unique().tolist())
        sel_brand = st.selectbox("Brand", brands)
    with col_f3:
        min_stores = st.slider("Min Stores", 2, 3, 2)

    filtered = metrics.copy()
    if sel_cat != "All":
        filtered = filtered[filtered["category"] == sel_cat]
    if sel_brand != "All":
        filtered = filtered[filtered["brand"] == sel_brand]
    filtered = filtered[filtered["stores_count"] >= min_stores]

    # ── KPIs ───────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Matched Groups", f"{len(filtered):,}")
    with k2:
        st.metric("Avg CV (%)", f"{filtered['cv'].mean():.1f}" if len(filtered) > 0 else "N/A")
    with k3:
        st.metric("Avg Price Spread", f"{filtered['price_spread_ratio'].mean():.2f}" if len(filtered) > 0 else "N/A")
    with k4:
        st.metric("Avg IQR (PKR)", f"{filtered['iqr'].mean():.0f}" if len(filtered) > 0 else "N/A")

    st.markdown("---")

    # ── Charts ─────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### CV Distribution")
        if len(filtered) > 0:
            fig = px.histogram(
                filtered, x="cv", nbins=40,
                color_discrete_sequence=[PLOTLY_COLORS[0]],
                labels={"cv": "Coefficient of Variation (%)"},
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("### Price Spread Ratio by Category")
        if len(filtered) > 0:
            cat_spread = filtered.groupby("category")["price_spread_ratio"].mean().sort_values(ascending=True).tail(10)
            fig = px.bar(
                x=cat_spread.values, y=cat_spread.index,
                orientation="h", color_discrete_sequence=[PLOTLY_COLORS[1]],
                labels={"x": "Avg Spread Ratio", "y": "Category"},
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    # ── IQR vs Mean Price ──────────────────────────────────
    st.markdown("### IQR vs Mean Price")
    if len(filtered) > 0:
        fig = px.scatter(
            filtered, x="mean_price", y="iqr",
            color="category", size="stores_count",
            hover_data=["product_name", "brand"],
            color_discrete_sequence=PLOTLY_COLORS,
            labels={"mean_price": "Mean Price (PKR)", "iqr": "IQR (PKR)"},
        )
        fig = styled_plotly(fig)
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

    # ── Top Price Dispersed Products ───────────────────────
    st.markdown("### 🔥 Most Price Dispersed Products")
    if len(filtered) > 0:
        top = filtered.nlargest(15, "cv")[
            ["product_name", "brand", "category", "mean_price",
             "cv", "price_range", "price_spread_ratio", "stores_count"]
        ]
        st.dataframe(
            top.style.format({
                "mean_price": "PKR {:.0f}",
                "cv": "{:.1f}%",
                "price_range": "PKR {:.0f}",
                "price_spread_ratio": "{:.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    # ── RPPI by Store ──────────────────────────────────────
    rppi_path = os.path.join(config.MATCHED_DIR, "rppi.csv")
    if os.path.exists(rppi_path):
        st.markdown("### Relative Price Position Index (RPPI) by Store")
        rppi = pd.read_csv(rppi_path)
        store_rppi = rppi.groupby("store")["rppi"].mean().reset_index()
        fig = px.bar(
            store_rppi, x="store", y="rppi",
            color="store", color_discrete_sequence=PLOTLY_COLORS,
            labels={"rppi": "Avg RPPI (0=cheapest, 1=expensive)", "store": "Store"},
        )
        fig = styled_plotly(fig)
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
