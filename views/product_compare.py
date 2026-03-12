"""
Product Compare Page — Direct side-by-side comparison of a specific product.
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px

import config
from styles.theme import styled_plotly, PLOTLY_COLORS


def render():
    st.markdown("# 🔍 Product Compare")
    st.markdown("Directly compare the exact same product's price across different stores and cities.")

    matched_path = os.path.join(config.MATCHED_DIR, "matched_products.csv")

    if not os.path.exists(matched_path):
        st.warning("⚠️ Matched data not found. Run the matching pipeline first.")
        return

    # Load data
    df = pd.read_csv(matched_path, low_memory=False)

    # We only care about products matched across at least 2 stores
    groups = df.groupby("match_id").filter(lambda x: x["store"].nunique() > 1)

    if groups.empty:
        st.warning("⚠️ No cross-store matched products found.")
        return

    # Create a clean display name combining brand, category, and name
    groups["display_name"] = groups["brand"] + " - " + groups["product_name"] + " (" + groups["category"] + ")"
    
    # Get unique products for the dropdown
    unique_products = groups[["match_id", "display_name"]].drop_duplicates().sort_values("display_name")

    # ── Search / Selection ─────────────────────────────────
    st.markdown("### Select Product")
    
    # Create an index mapping for the selectbox
    product_options = dict(zip(unique_products["display_name"], unique_products["match_id"]))
    
    selected_name = st.selectbox(
        "Search or select a product to compare:",
        options=list(product_options.keys())
    )
    
    if not selected_name:
        return

    selected_id = product_options[selected_name]
    product_data = groups[groups["match_id"] == selected_id].copy()

    # ── KPI Cards ──────────────────────────────────────────
    min_price = product_data["price"].min()
    max_price = product_data["price"].max()
    avg_price = product_data["price"].mean()
    spread = ((max_price - min_price) / min_price) * 100

    cheapest_store = product_data.loc[product_data["price"].idxmin()]["store"]
    cheapest_city = product_data.loc[product_data["price"].idxmin()]["city"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Lowest Price", f"PKR {min_price:,.0f}", f"at {cheapest_store}")
    with c2:
        st.metric("Highest Price", f"PKR {max_price:,.0f}")
    with c3:
        st.metric("Average Price", f"PKR {avg_price:,.0f}")
    with c4:
        st.metric("Price Spread", f"{spread:.1f}%")

    st.markdown("---")

    # ── Side-by-Side Comparison ────────────────────────────
    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        st.markdown("### Price Comparison")
        fig = px.bar(
            product_data, x="store", y="price",
            color="store",
            color_discrete_sequence=PLOTLY_COLORS,
            text="price",
            hover_data=["city", "product_name"],
            labels={"price": "Price (PKR)", "store": "Store"}
        )
        fig.update_traces(texttemplate='PKR %{text:,.0f}', textposition='outside')
        fig = styled_plotly(fig)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("### Detailed Listings")
        display_df = product_data[["store", "city", "product_name", "price"]].sort_values("price")
        
        # Add a visual indicator for the cheapest option
        display_df["Status"] = ["🏆 Best Deal" if i == 0 else "" for i in range(len(display_df))]

        st.dataframe(
            display_df.style.format({"price": "PKR {:,.0f}"}),
            use_container_width=True,
            hide_index=True
        )

    # ── Price Diff Matrix ──────────────────────────────────
    st.markdown("### Price Difference Matrix (%)")
    st.markdown("<small>Read as: The store in the Row is [X]% more/less expensive than the store in the Column.</small>", unsafe_allow_html=True)
    
    # Calculate % difference between every store combination for this product
    pivot = product_data.groupby("store")["price"].mean()
    matrix = pd.DataFrame(index=pivot.index, columns=pivot.index)
    
    for store_a in pivot.index:
        for store_b in pivot.index:
            if store_a == store_b:
                matrix.loc[store_a, store_b] = 0.0
            else:
                price_a = pivot[store_a]
                price_b = pivot[store_b]
                diff_pct = ((price_a - price_b) / price_b) * 100
                matrix.loc[store_a, store_b] = diff_pct

    # Ensure matrix is numeric for imshow
    matrix = matrix.astype(float)
    
    fig_matrix = px.imshow(
        matrix, text_auto=".1f",
        color_continuous_scale="RdYlGn_r", # Reverse so red is "more expensive"
        labels={"x": "Compared to", "y": "Store", "color": "% Difference"},
    )
    fig_matrix = styled_plotly(fig_matrix)
    fig_matrix.update_layout(height=400)
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    st.markdown("---")
    st.markdown("**Note:** If the same store appears multiple times (e.g. across different cities), the matrix averages their prices for the comparison.")
