import pandas as pd


def build_order_features(order_items: pd.DataFrame) -> pd.DataFrame:
    """Extract features from order items."""

    features = (
        order_items
        .groupby("order_id")
        .agg(
            items_quantity=("order_item_id", "count"),
            unique_products=("product_id", "nunique"),
            sellers_quantity=("seller_id", "nunique"),
            total_price=("price", "sum"),
            total_freight=("freight_value", "sum"),
        )
        .reset_index()
    )

    return features
