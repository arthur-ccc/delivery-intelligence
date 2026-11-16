import numpy as np
import pandas as pd


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth using the Haversine formula."""

    radius_km = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(delta_lon / 2) ** 2
    )

    a = np.clip(a, 0, 1)

    return 2 * radius_km * np.arcsin(np.sqrt(a))


def build_zip_coordinates(geolocation):
    """Consolidate coordinates by CEP prefix."""

    geo = geolocation.copy()

    # Approximate limits for coordinate filtering
    # of the Brazilian territory.
    valid_coordinates = (
        geo["geolocation_lat"].between(-34, 6)
        & geo["geolocation_lng"].between(-74, -34)
    )

    geo = geo.loc[valid_coordinates].copy()

    coordinates = (
        geo
        .groupby("geolocation_zip_code_prefix")
        .agg(
            latitude=("geolocation_lat", "median"),
            longitude=("geolocation_lng", "median"),
        )
        .reset_index()
    )

    return coordinates


def build_geographic_features(
    orders,
    order_items,
    customers,
    sellers,
    geolocation,
):
    """Build geographic features by order."""

    coordinates = build_zip_coordinates(geolocation)

    customer_geo = (
        customers[
            ["customer_id", "customer_zip_code_prefix",
             "customer_state"]
        ]
        .merge(
            coordinates,
            left_on="customer_zip_code_prefix",
            right_on="geolocation_zip_code_prefix",
            how="left",
            validate="many_to_one",
        )
        .rename(
            columns={
                "latitude": "customer_lat",
                "longitude": "customer_lng",
            }
        )
    )

    seller_geo = (
        sellers[
            ["seller_id", "seller_zip_code_prefix",
             "seller_state"]
        ]
        .merge(
            coordinates,
            left_on="seller_zip_code_prefix",
            right_on="geolocation_zip_code_prefix",
            how="left",
            validate="many_to_one",
        )
        .rename(
            columns={
                "latitude": "seller_lat",
                "longitude": "seller_lng",
            }
        )
    )

    # one line per order-seller pair, since some orders have multiple sellers
    order_sellers = (
        order_items[["order_id", "seller_id"]]
        .drop_duplicates()
    )

    order_sellers = order_sellers.merge(
        orders[["order_id", "customer_id"]],
        on="order_id",
        how="left",
        validate="many_to_one",
    )

    order_sellers = order_sellers.merge(
        customer_geo[
            ["customer_id", "customer_state",
             "customer_lat", "customer_lng"]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    order_sellers = order_sellers.merge(
        seller_geo[
            ["seller_id", "seller_state",
             "seller_lat", "seller_lng"]
        ],
        on="seller_id",
        how="left",
        validate="many_to_one",
    )

    order_sellers["distance_km"] = haversine_distance(
        order_sellers["customer_lat"],
        order_sellers["customer_lng"],
        order_sellers["seller_lat"],
        order_sellers["seller_lng"],
    )

    # Do not classify orders with missing state information as same-state or different-state.
    known_states = (
        order_sellers["customer_state"].notna()
        & order_sellers["seller_state"].notna()
    )

    order_sellers["same_state"] = (
        order_sellers["customer_state"]
        .eq(order_sellers["seller_state"])
        .astype("boolean")
        .where(known_states, pd.NA)
    )

    geographic_features = (
        order_sellers
        .groupby("order_id")
        .agg(
            min_distance_km=("distance_km", "min"),
            avg_distance_km=("distance_km", "mean"),
            max_distance_km=("distance_km", "max"),
            sellers_with_coordinates=(
                "distance_km", "count"
            ),
            sellers_with_known_states=(
                "same_state", "count"
            ),
            all_sellers_same_state=(
                "same_state", "all"
            ),
        )
        .reset_index()
    )

    seller_counts = (
        order_sellers.groupby("order_id")["seller_id"]
        .nunique()
        .rename("total_sellers")
        .reset_index()
    )

    geographic_features = geographic_features.merge(
        seller_counts,
        on="order_id",
        how="left",
        validate="one_to_one",
    )

    geographic_features["has_complete_coordinates"] = (
        geographic_features["sellers_with_coordinates"]
        == geographic_features["total_sellers"]
    )

    # Partial coordinates are not enough to compute distances, so we set them to NaN.
    distance_columns = [
        "min_distance_km",
        "avg_distance_km",
        "max_distance_km",
    ]

    geographic_features.loc[
        ~geographic_features["has_complete_coordinates"],
        distance_columns,
    ] = np.nan

    incomplete_states = (
    geographic_features["sellers_with_known_states"]
    != geographic_features["total_sellers"]
)

    geographic_features["all_sellers_same_state"] = (
        geographic_features["all_sellers_same_state"]
        .astype("boolean")
    )

    geographic_features.loc[
        incomplete_states,
        "all_sellers_same_state",
    ] = pd.NA

    return geographic_features.drop(
        columns=[
            "sellers_with_coordinates",
            "sellers_with_known_states",
            "total_sellers",
        ]
    )
