import pandas as pd

def data_processing (file_path: str = 'data/coffee-shop-sales-revenue.csv') -> pd.DataFrame:
    """
    Reads csv file, performs data manipulation and returns a cleaned DataFrame along a new DataFrame basket-level.
    Includes calculations for revenue, hour of day, day of week, month, and groups transactions by basket.
    """
    # Load the data
    df = pd.read_csv(file_path, sep="|", parse_dates=["transaction_date"])
    
    df['revenue'] = df['transaction_qty'] * df['unit_price']

    df["hour"] = pd.to_datetime(df["transaction_time"], format="%H:%M:%S").dt.hour

    df["day_of_week"] = df["transaction_date"].dt.day_name()

    df["month"] = df["transaction_date"].dt.to_period("M").astype(str)

    ## Group transactions by basket / transacion since original df is item level. Identifiable via same timestamp & store.

    transaction_id_cols = ["transaction_date", "transaction_time", "store_id", "store_location"]
    basket = (
        df.groupby(transaction_id_cols, as_index=False)
        .agg(
            basket_revenue=("revenue", "sum"),   # total spend per basket
            items_ordered=("transaction_qty", "sum"),  # total items per basket
        )
    )

    return df,basket 


## High level metrics - overview
def overall_metrics(df: pd.DataFrame, baskets: pd.DataFrame) -> dict:
    """
    Returns a small dict of headline numbers for the dashboard KPI cards.
    """
 
    return {
        "total_revenue": df["revenue"].sum(),
        # True transaction count = number of baskets, not item level 
        "total_transactions": len(baskets),
        # Average transaction value / how much is a customer spending per visit. 
        "avg_transaction_value": baskets["basket_revenue"].mean(),
        # Date range - what's the period we are loooking at 
        "date_from": df["transaction_date"].min().strftime("%b %Y"),
        "date_to": df["transaction_date"].max().strftime("%b %Y"),
    }


## Business Question - How should I schedule my staff based on sales patterns?
def staff_heatmap(baskets: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a pivot table to analyze sales patterns by hour and day of the week.
    This can help in scheduling staff based on peak sales times, key metric is basket count as we care
    how many customers visited the shop.
    """

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    baskets = baskets.copy()
    baskets["hour"] = pd.to_datetime(baskets["transaction_time"], format="%H:%M:%S").dt.hour
    baskets["day_of_week"] = pd.to_datetime(baskets["transaction_date"]).dt.day_name()

    heatmap_data = (
    baskets.groupby(["day_of_week", "hour"])
    .size()                        
    .reset_index(name="basket_count"))

    pivot = heatmap_data.pivot(index="day_of_week", columns="hour", values="basket_count")

    pivot = pivot.reindex([d for d in day_order if d in pivot.index])

    return pivot


# What products are generating the most revenue?

def revenue_by_product(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates total revenue and transaction count by product and product category 
    to identify which items are generating the most revenue.
    """

    product_summary = (
        df.groupby("product_category").agg(
            total_revenue=("revenue", "sum"),
            total_transactions=("transaction_id", "count"),  # line-item count
        ).sort_values("total_revenue", ascending=False).reset_index()
    )

    product_summary["revenue_percentage"] = (
        product_summary["total_revenue"] / product_summary["total_revenue"].sum() * 100
    ).round(1)
 
    return product_summary

# How are the locations performing? 

def store_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Answers if the locatios are performing different or the same, if they have different sales trends too. 
    6 Months worth of data so hard to identify seasonality without more data, but can see initial patterns
    """

    store_monthly = (
        df.groupby(["month", "store_location"])["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"revenue": "monthly_revenue"})
    )
 
    store_monthly = store_monthly.sort_values("month")
 
    return store_monthly

# Is the business growing overtime?
def monthly_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    What is the overall revenue trend MoM? Are we seeing growth, decline, or stability in sales over the 6 month period?
    """

    monthly = (
        df.groupby("month")
        .agg(
            total_revenue=("revenue", "sum"),
            total_transactions=("transaction_id", "count"),
        )
        .reset_index()
        .sort_values("month")
    )

    # Calculate month-over-month revenue growth %
    monthly["mom_growth_percentage"] = monthly["total_revenue"].pct_change() * 100

    return monthly
    

if __name__ == "__main__":
    print()
