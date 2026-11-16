import pandas as pd


def build_targets(orders: pd.DataFrame) -> pd.DataFrame:
    """Extract historical targets for delivered orders."""

    required_dates = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    df = orders.loc[
        (orders["order_status"] == "delivered")
        & orders[required_dates].notna().all(axis=1)
    ].copy()

    df["delivery_time_days"] = (
        df["order_delivered_customer_date"]
        - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    df = df.loc[
        df["delivery_time_days"] >= 0
    ].copy()

    df["is_delayed"] = (
        df["order_delivered_customer_date"].dt.normalize()
        > df["order_estimated_delivery_date"].dt.normalize()
    ).astype("int8")

    return df[
        [
            "order_id",
            "delivery_time_days",
            "is_delayed",
        ]
    ]
