# Maven Roasters — Café Sales Analysis

A data analytics dashboard built for Maven Roasters, a fictional 3-location coffee shop chain. The dataset covers 6 months of transaction data (Jan–Jun 2023) across Astoria, Hell's Kitchen, and Lower Manhattan. Sourced from Kaggle. 

**Live app →** https://cafe-analytics-alonso-ruiz.streamlit.app/ 

---

## Business Context

Maven Roasters is growing but flying blind on a few operational questions. The owner has raw transaction data but no easy way to answer: when should I staff up? What's actually driving revenue? Are my three stores performing differently?

This dashboard turns that transaction log into four actionable answers.

---

## Questions

1. To inform on staffing decisions, when are customers coming in ?  does it vary by day? is it more on the weekends?
2. Which product categories are carrying the revenue and which ones are just sitting in the shop?
3. Are the three store locations performing the same? Is one driving the success or all trending similar?
4. Is the business growing month over month, decreasing on demand or just holding steady?

---

## Key Findings

**Staffing** — Peak traffic is 8–10am on weekdays, not weekends. Saturday and Sunday are notably quieter in the morning. If you're scheduling the same staff for a Tuesday 9am as a Sunday 9am, you're probably overstaffed one and underprepared the other.

**Product mix** — Coffee and tea together account for ~67% of revenue. Packaged goods and food are there, but they're not moving the needle the same way.

**Store performance** — All three locations track almost identically in monthly growth. No one location is pulling ahead or falling behind. That's likely a sign the brand is consistent and markets are the same (same customer behaviour).

**Growth** — The business revenue grew significantly over March to May (+20% each month), with a single digit growth during June. Overall trending possitively after a slow start in February.  

---

## Recommendations

- **Shift weekday morning staffing up, weekend morning staffing down.** 
- **Double down on coffee and tea. Review if other categories are worth stocking** 
- **Keey an eye on MoM growth** 


---

## Stack

- **Python** — Pandas for data processing, Plotly + Matplotlib/Seaborn for charts
- **Streamlit** — dashboard and interactivity


