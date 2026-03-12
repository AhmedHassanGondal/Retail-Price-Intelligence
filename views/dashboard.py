"""
Dashboard Overview Page — KPIs, summary charts, and data quality overview.
"""
import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config
from styles.theme import styled_plotly, PLOTLY_COLORS


def load_data():
    """Load all available data files."""
    data = {}

    # Cleaned data
    cleaned_path = os.path.join(config.PROCESSED_DIR, "all_products_cleaned.csv")
    if os.path.exists(cleaned_path):
        data["cleaned"] = pd.read_csv(cleaned_path, low_memory=False)

    # Matched data
    matched_path = os.path.join(config.MATCHED_DIR, "matched_products.csv")
    if os.path.exists(matched_path):
        data["matched"] = pd.read_csv(matched_path, low_memory=False)

    # Product metrics
    metrics_path = os.path.join(config.MATCHED_DIR, "product_metrics.csv")
    if os.path.exists(metrics_path):
        data["product_metrics"] = pd.read_csv(metrics_path)

    # Store metrics
    store_path = os.path.join(config.MATCHED_DIR, "store_metrics.csv")
    if os.path.exists(store_path):
        data["store_metrics"] = pd.read_csv(store_path)

    # Validation report
    val_path = os.path.join(config.PROCESSED_DIR, "validation_report.json")
    if os.path.exists(val_path):
        with open(val_path) as f:
            data["validation"] = json.load(f)

    # Analysis results
    analysis_path = os.path.join(config.MATCHED_DIR, "analysis_results.json")
    if os.path.exists(analysis_path):
        with open(analysis_path) as f:
            data["analysis"] = json.load(f)

    return data


def render():
    st.markdown("# 📊 Dashboard Overview")
    st.markdown("Real-time insights from Pakistani supermarket price intelligence pipeline")

    data = load_data()

    if not data.get("cleaned") is not None:
        st.warning("⚠️ No data available. Run the pipeline first!")
        st.code("python -m scrapers.alfatah_scraper\npython -m scrapers.metro_scraper\npython -m scrapers.naheed_scraper\npython -m pipeline.cleaner\npython -m pipeline.matcher\npython -m pipeline.analyzer", language="bash")
        return

    df = data.get("cleaned", pd.DataFrame())
    matched = data.get("matched", pd.DataFrame())

    # ── KPI Cards ──────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Products", f"{len(df):,}")
    with col2:
        st.metric("Stores", df["store"].nunique() if "store" in df.columns else 0)
    with col3:
        st.metric("Cities", df["city"].nunique() if "city" in df.columns else 0)
    with col4:
        matched_count = (matched["match_id"] > 0).sum() if "match_id" in matched.columns else 0
        st.metric("Matched Products", f"{matched_count:,}")
    with col5:
        brands = df["brand"].nunique() if "brand" in df.columns else 0
        st.metric("Brands", f"{brands:,}")

    st.markdown("---")

    # ── Charts Row 1 ───────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Products by Store")
        if "store" in df.columns:
            store_counts = df["store"].value_counts().reset_index()
            store_counts.columns = ["Store", "Products"]
            fig = px.bar(
                store_counts, x="Store", y="Products",
                color="Store", color_discrete_sequence=PLOTLY_COLORS,
            )
            fig = styled_plotly(fig)
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("### Price Distribution")
        if "price" in df.columns:
            fig = px.histogram(
                df[df["price"] < df["price"].quantile(0.95)],
                x="price", nbins=50, color_discrete_sequence=[PLOTLY_COLORS[0]],
                labels={"price": "Price (PKR)"},
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    # ── Charts Row 2 ───────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("### Products by City")
        if "city" in df.columns:
            city_counts = df.groupby(["city", "store"]).size().reset_index(name="count")
            fig = px.bar(
                city_counts, x="city", y="count", color="store",
                barmode="group", color_discrete_sequence=PLOTLY_COLORS,
                labels={"city": "City", "count": "Products", "store": "Store"},
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.markdown("### Category Distribution")
        if "category" in df.columns:
            top_cats = df["category"].value_counts().head(12).reset_index()
            top_cats.columns = ["Category", "Count"]
            fig = px.pie(
                top_cats, names="Category", values="Count",
                color_discrete_sequence=PLOTLY_COLORS,
                hole=0.4,
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    # ── Average Price by Store & Category ──────────────────
    st.markdown("### Average Price by Store & Category")
    if "category" in df.columns and "store" in df.columns:
        top_cats = df["category"].value_counts().head(8).index.tolist()
        heatmap_data = df[df["category"].isin(top_cats)].pivot_table(
            values="price", index="category", columns="store", aggfunc="mean"
        ).round(0)
        fig = px.imshow(
            heatmap_data, text_auto=True,
            color_continuous_scale="Viridis",
            labels={"x": "Store", "y": "Category", "color": "Avg Price (PKR)"},
        )
        fig = styled_plotly(fig)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # ── Data Quality ───────────────────────────────────────
    if data.get("validation"):
        st.markdown("### 🔍 Data Quality Summary")
        val = data["validation"]
        q1, q2, q3 = st.columns(3)
        with q1:
            st.metric("Overall Status", val.get("overall", "N/A"))
        with q2:
            outlier_info = val.get("outliers", {})
            st.metric("Z-Score Outliers", f"{outlier_info.get('z_score_pct', 0)}%")
        with q3:
            dup_info = val.get("duplicates", {})
            st.metric("Duplicate Rate", f"{dup_info.get('duplicate_pct', 0)}%")
