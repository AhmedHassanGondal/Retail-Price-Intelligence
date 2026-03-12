"""
Leader Dominance Index Page — LDI charts and category breakdowns.
"""
import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config
from styles.theme import styled_plotly, PLOTLY_COLORS


def render():
    st.markdown("# 🏆 Leader Dominance Index")
    st.markdown("Analyze which stores lead on pricing across products and categories")

    analysis_path = os.path.join(config.MATCHED_DIR, "analysis_results.json")
    if not os.path.exists(analysis_path):
        st.warning("⚠️ Analysis results not found. Run the analysis pipeline first.")
        return

    with open(analysis_path) as f:
        analysis = json.load(f)

    ldi = analysis.get("ldi", {})
    if not ldi:
        st.warning("⚠️ LDI data not available.")
        return

    # ── Standard vs Weighted LDI ───────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Standard LDI")
        st.markdown("<small>% of products where each store has the lowest price</small>", unsafe_allow_html=True)
        std_ldi = ldi.get("standard_ldi", {})
        if std_ldi:
            fig = px.bar(
                x=list(std_ldi.keys()), y=list(std_ldi.values()),
                color=list(std_ldi.keys()),
                color_discrete_sequence=PLOTLY_COLORS,
                labels={"x": "Store", "y": "LDI (%)"},
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Weighted LDI")
        st.markdown("<small>LDI weighted by product value (higher-value products count more)</small>", unsafe_allow_html=True)
        wt_ldi = ldi.get("weighted_ldi", {})
        if wt_ldi:
            fig = px.pie(
                names=list(wt_ldi.keys()), values=list(wt_ldi.values()),
                color_discrete_sequence=PLOTLY_COLORS,
                hole=0.45,
            )
            fig.update_traces(textinfo="percent+label", textfont_size=13)
            fig = styled_plotly(fig)
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── LDI Comparison Table ───────────────────────────────
    st.markdown("### LDI Summary")
    ldi_table = pd.DataFrame({
        "Store": list(std_ldi.keys()),
        "Standard LDI (%)": list(std_ldi.values()),
        "Weighted LDI (%)": [wt_ldi.get(s, 0) for s in std_ldi.keys()],
    })
    ldi_table["Difference"] = (
        ldi_table["Weighted LDI (%)"] - ldi_table["Standard LDI (%)"]
    ).round(2)

    st.dataframe(
        ldi_table.style.format({
            "Standard LDI (%)": "{:.1f}",
            "Weighted LDI (%)": "{:.1f}",
            "Difference": "{:+.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # ── Category-wise LDI ──────────────────────────────────
    st.markdown("### Category-wise LDI Breakdown")
    cat_ldi = ldi.get("category_ldi", {})
    if cat_ldi:
        # Build a DataFrame for the heatmap
        rows = []
        for cat, store_vals in cat_ldi.items():
            for store, val in store_vals.items():
                rows.append({"Category": cat, "Store": store, "LDI (%)": val})

        cat_df = pd.DataFrame(rows)
        if not cat_df.empty:
            # Filter top categories
            sel_categories = st.multiselect(
                "Select categories to display",
                sorted(cat_df["Category"].unique()),
                default=sorted(cat_df["Category"].unique())[:8],
            )

            filtered = cat_df[cat_df["Category"].isin(sel_categories)]
            if not filtered.empty:
                pivot = filtered.pivot_table(
                    values="LDI (%)", index="Category", columns="Store"
                ).fillna(0)

                fig = px.imshow(
                    pivot, text_auto=".1f",
                    color_continuous_scale="RdYlGn",
                    labels={"x": "Store", "y": "Category", "color": "LDI (%)"},
                )
                fig = styled_plotly(fig)
                fig.update_layout(height=max(300, len(sel_categories) * 40))
                st.plotly_chart(fig, use_container_width=True)

            # Grouped bar for selected categories
            st.markdown("### LDI by Category (Bar Chart)")
            fig = px.bar(
                filtered, x="Category", y="LDI (%)", color="Store",
                barmode="group", color_discrete_sequence=PLOTLY_COLORS,
            )
            fig = styled_plotly(fig)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
