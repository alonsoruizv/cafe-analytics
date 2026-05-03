"""
Maven Roasters Café - Streamlit Analytics Dashboard.
Imports all data logic from analysis.py and renders four interactive
visualizations to answer key business questions. 
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from analysis import data_processing, overall_metrics, staff_heatmap, revenue_by_product, store_performance, monthly_performance



st.set_page_config(
    page_title="Maven Roasters - Analytics",
    page_icon=":coffee:",
    layout="wide",
)


@st.cache_data
def get_data():
    # Cache the  CSV read so Streamlit does not re-run the whole script on interaction
    return data_processing("data/coffee-shop-sales-revenue.csv")

df, baskets = get_data()
kpis = overall_metrics(df, baskets)



st.title("☕ Maven Roasters — Café Analytics")
st.markdown(
    """
    This report provides insights into Maven Roasters' sales performance 
    based on six months of transactional data. Data set sourced from Kaggle. 
    """
)
st.markdown(
    f"**{kpis['date_from']} to {kpis['date_to']} · "
    f"3 Locations of Maven Roasters Café**"
)
st.divider()


# High Level Metrics
col1, col2, col3 = st.columns(3)


col1.metric(
    label="Total Revenue",
    value=f"${kpis['total_revenue']:,.0f}",
    border=True
)

col2.metric(
    label="Total Transactions",
    # Format with commas for readability
    value=f"{kpis['total_transactions']:,}",
    border = True
)

col3.metric(
    label="Avg. Transaction Value",
    # Basket-level average — corrected for multi-item visits
    value=f"${kpis['avg_transaction_value']:.2f}",
    border = True

)

st.divider()

# Executive Summary
total_rev = f"\\${kpis['total_revenue']:,.0f}"
atv = f"\\${kpis['avg_transaction_value']:.2f}"
transactions = f"{kpis['total_transactions']:,}"


st.subheader("Executive Summary")
st.markdown(
    f"""
    Maven Roasters operates three café locations: Astoria, Hell's Kitchen, 
    and Lower Manhattan. This report analyses **{transactions} customer transactions** 
    recorded between **{kpis['date_from']} and {kpis['date_to']}**, generating 
    **{total_rev}** in total revenue at an average basket value of 
    **{atv} per visit**.

    The analysis surfaces four decisions the business should be making with this data:
    - **Staffing:** Peak footfall is concentrated in the 8am–10am window on weekdays, 
    with Saturday consistently the quietest day, the inverse of common assumptions.
    - **Product mix:** Coffee and Tea drive 66.7% of revenue - the bottom four categories 
    combined account for just 5.3% and warrant a margin review to confirm profitability due to low volume.
    - **Location performance:** All three stores are growing, very little divergence across them. 
    - **Growth trend:** Month-over-month revenue has grown consistently across the full 
    six-month period, suggesting real demand, stabilizied in the last month but worth keeping monitoring.
    """
)
st.divider()

# Heat map for staffing 
st.subheader("How should I schedule my staff?")
st.caption("Customer visits (basket count) by hour and day. Darker = more foot traffic")

pivot = staff_heatmap(baskets)

hmap = go.Figure(
    data=go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in pivot.columns],  # format hours as 07:00 etc.
        y=pivot.index.tolist(),
        colorscale="YlOrBr",       
        colorbar=dict(title="Customer Visits"),
        hoverongaps=False,
        # Hover tooltip shows day, hour, basket count
        hovertemplate="<b>%{y}</b><br>Hour: %{x}<br>Customer visits: %{z:,}<extra></extra>",
    )
)

hmap.update_layout(
    xaxis_title="Hour of Day",
    yaxis_title="",
    height=380,
    margin=dict(t=20, b=40),
)

st.plotly_chart(hmap, width='stretch')

# Insight callout — drawn from the actual data
st.info(
    "**Key Takeaway:** Peak hours are **8am–10am on weekdays**, with 10am as the "
    "busiest time of day and Tuesday the busiest day. Weekdays are consistently busier "
    "than weekends. Saturday is actually the quietest day of the week, which may "
    "challenge assumptions about weekend staffing levels.", icon = '💡'
)

st.divider()


# Revenue by product 
st.subheader("Which products are generating the most revenue?")
st.caption("Revenue share and volume by product category")

product_df = revenue_by_product(df)

product_bars = px.bar(
    product_df,
    x="total_revenue",
    y="product_category",
    orientation="h",                   
    text="revenue_percentage",         
    color="total_revenue",
    color_continuous_scale="YlOrBr",   
    labels={
        "total_revenue": "Total Revenue ($)",
        "product_category": "Product Category",
    },
)

product_bars.update_traces(
    texttemplate="%{text:.1f}%",   
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<br>Share: %{text:.1f}%<extra></extra>",

)

product_bars.update_layout(
    height=420,
    showlegend=False,
    coloraxis_showscale=False,
    yaxis=dict(categoryorder="total ascending"),  
    margin=dict(t=20, r=80),
)

st.plotly_chart(product_bars, width='stretch')

st.info(
    "**Key Takeaway:** Coffee and Tea together account for **66.7% of revenue**. "
    "The bottom 4 categories "
    "combine for just **5.3%**, candidates for menu simplification depending on product margin", icon = '💡'
)

st.divider()


st.subheader("Do the three locations perform differently, or do they have similar sales trends?")
st.caption("Monthly revenue by store — Jan to Jun 2023")

store_df = store_performance(df)

store_lines = px.line(
    store_df,
    x="month",
    y="monthly_revenue",
    color="store_location",
    markers=True,                      
    labels={
        "monthly_revenue": "Monthly Revenue ($)",
        "month": "",
        "store_location": "Location",
    },
    color_discrete_sequence=["#6F4E37", "#C4A35A", "#A0522D"],  
)

store_lines.update_traces(line=dict(width=2.5))

store_lines.update_layout(
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=40, b=20),
)

st.plotly_chart(store_lines, width='stretch')

# Calculate which store leads — derived dynamically from the data
store_totals = df.groupby("store_location")["revenue"].sum().sort_values(ascending=False)
top_store = store_totals.index[0]
bottom_store = store_totals.index[-1]
gap_pct = ((store_totals.iloc[0] - store_totals.iloc[-1]) / store_totals.iloc[-1] * 100)

st.info(
    f"**Key Takeaway:** **{top_store}** leads on total revenue, outpacing "
    f"**{bottom_store}** by **{gap_pct:.0f}%** over the period. "
    f"All three locations show consistent growth through the first half of the year, with no major divergences in sales trends, suggesting similar consumer dynamics across locations.", icon = '💡'
)

st.divider()


st.subheader("Is the business growing over time?")
st.caption("Total monthly revenue across all locations with MoM growth")

monthly_df = monthly_performance(df)

growth_bar_line = go.Figure()

# Revenue bars
growth_bar_line.add_trace(
    go.Bar(
        x=monthly_df["month"],
        y=monthly_df["total_revenue"],
        name="Total Revenue ($)",
        marker_color="#6F4E37",
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    )
)

# MoM growth rate line on secondary axis
growth_bar_line.add_trace(
    go.Scatter(
        x=monthly_df["month"],
        y=monthly_df["mom_growth_percentage"],   
        name="MoM Growth (%)",
        mode="lines+markers",
        line=dict(color="#C4A35A", width=2.5),
        yaxis="y2",                    # secondary y-axis on the right
        hovertemplate="<b>%{x}</b><br>MoM Growth: %{y:.1f}%<extra></extra>",
    )
)

growth_bar_line.update_layout(
    height=420,
    yaxis=dict(title=dict(text="Revenue ($)", font=dict(color="#6F4E37"))),
    yaxis2=dict(
        title=dict(text="MoM Growth (%)", font=dict(color="#C4A35A")),
        overlaying="y",
        side="right",
        zeroline=True,
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=40, b=20),
    bargap=0.3,
)

st.plotly_chart(growth_bar_line, width='stretch')

# Dynamic MoM summary
avg_growth = monthly_df["mom_growth_percentage"].dropna().mean()

st.info(
    f"**Key Takeaway:** Revenue grew every month Jan–Jun 2023, averaging "
    f"**+{avg_growth:.1f}% month-over-month**. This is consistent, organic growth — "
    f"not a seasonal spike — suggesting the business fundamentals are strong.", icon = '💡'
)

st.divider()



st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.85em;'>
    Data source: Maven Roasters dataset (Kaggle) · 
    Analysis by Alonso Ruiz Velasco · 
    Built with Python, Pandas, Plotly & Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)