import pandas as pd


def build_temporal_features(orders: pd.DataFrame) -> pd.DataFrame:
    """Extract features that are known at the time of purchase."""

    required_columns = [
        "order_id",
        "order_purchase_timestamp",
    ]

    df = orders[required_columns].copy()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce",
    )

    purchase_date = df["order_purchase_timestamp"]

    df["purchase_month"] = purchase_date.dt.month
    df["purchase_weekday"] = purchase_date.dt.dayofweek
    df["purchase_hour"] = purchase_date.dt.hour
    df["purchase_year"] = purchase_date.dt.year
    df["purchase_is_weekend"] = (
        purchase_date.dt.dayofweek >= 5
    ).astype("int8")

    return df.drop(columns=["order_purchase_timestamp"])
