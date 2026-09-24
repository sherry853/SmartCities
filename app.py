
import streamlit as st
import pandas as pd
from pathlib import Path
from pymongo import MongoClient


# Page Configuration
st.set_page_config(
    page_title="SmartCities Dashboard",
    page_icon="🚦",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .dashboard-title {
        font-size: 32px;
        font-weight: 700;
        color: #17365d;
    }

    .dashboard-subtitle {
        font-size: 16px;
        color: #64748b;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    h2, h3 {
        color: #17365d;
    }
</style>
""", unsafe_allow_html=True)

# Dashboard Header
st.markdown(
    '<div class="dashboard-title">🚦 SmartCities</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Smart City Traffic Monitoring Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

# Connect to MongoDB
@st.cache_resource
def connect_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    return client["smartcity"]

db = connect_mongodb()
traffic_collection = db["traffic_readings"]

# Load latest traffic data
@st.cache_data(ttl=5)
def load_traffic():
    data = list(
        traffic_collection.find(
            {},
            {"_id": 0}
        ).sort("timestamp", -1).limit(500)
    )
    return pd.DataFrame(data)

df = load_traffic()

if df.empty:
    st.warning(
        "No traffic data found. Please check that "
        "historical_traffic.csv is in your project folder."
    )
    st.stop()

# Clean and Prepare Data
if "sensor_id" in df.columns:
    df = df.drop(columns=["sensor_id"])

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

numeric_columns = [
    "vehicle_count",
    "average_speed",
    "speed"
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

if "timestamp" in df.columns:
    df = df.dropna(subset=["timestamp"])

if "vehicle_count" in df.columns:
    df = df.dropna(subset=["vehicle_count"])

# Sidebar Filters
st.sidebar.title("Dashboard Filters")

filtered_df = df.copy()

if "location" in filtered_df.columns:
    locations = sorted(
        filtered_df["location"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_locations = st.sidebar.multiselect(
        "Select Location",
        options=locations,
        default=locations
    )

    if selected_locations:
        filtered_df = filtered_df[
            filtered_df["location"].astype(str).isin(
                selected_locations
            )
        ]
    else:
        filtered_df = filtered_df.iloc[0:0]

if "timestamp" in filtered_df.columns and not filtered_df.empty:
    min_date = filtered_df["timestamp"].min().date()
    max_date = filtered_df["timestamp"].max().date()

    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates

        filtered_df = filtered_df[
            (filtered_df["timestamp"].dt.date >= start_date)
            & (filtered_df["timestamp"].dt.date <= end_date)
        ]

st.sidebar.divider()

st.sidebar.caption(
    "Smart City Data Pipeline"
)

# Check Filtered Data
if filtered_df.empty:
    st.info("No traffic records match the selected filters.")
    st.stop()

# Key Traffic Metrics
st.subheader("Traffic Overview")

total_records = len(filtered_df)
total_vehicles = filtered_df["vehicle_count"].sum()
average_vehicles = filtered_df["vehicle_count"].mean()

if "average_speed" in filtered_df.columns:
    avg_speed = filtered_df["average_speed"].mean()
elif "speed" in filtered_df.columns:
    avg_speed = filtered_df["speed"].mean()
else:
    avg_speed = None

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{total_records:,}"
)

col2.metric(
    "Total Vehicles",
    f"{total_vehicles:,.0f}"
)

col3.metric(
    "Average Vehicle Count",
    f"{average_vehicles:.1f}"
)

if avg_speed is not None and pd.notna(avg_speed):
    col4.metric(
        "Average Speed",
        f"{avg_speed:.1f} km/h"
    )
else:
    col4.metric(
        "Average Speed",
        "Not available"
    )

st.divider()

# Traffic Charts
st.subheader("Traffic Analysis")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### Vehicle Count Over Time")

    if "timestamp" in filtered_df.columns:
        traffic_over_time = (
            filtered_df
            .sort_values("timestamp")
            .set_index("timestamp")
        )

        st.line_chart(
            traffic_over_time["vehicle_count"],
            use_container_width=True
        )
    else:
        st.info("Timestamp data is unavailable.")

with chart_col2:
    st.markdown("### Average Speed by Location")

    speed_column = None

    if "average_speed" in filtered_df.columns:
        speed_column = "average_speed"
    elif "speed" in filtered_df.columns:
        speed_column = "speed"

    if speed_column and "location" in filtered_df.columns:
        speed_by_location = (
            filtered_df
            .groupby("location")[speed_column]
            .mean()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            speed_by_location,
            use_container_width=True
        )
    else:
        st.info("Speed or location data is unavailable.")

st.divider()

# Congestion Summary
st.subheader("Congestion Summary")

if "vehicle_count" in filtered_df.columns:
    congestion_threshold = 50

    congested_records = filtered_df[
        filtered_df["vehicle_count"] >= congestion_threshold
    ]

    congestion_percentage = (
        len(congested_records) / len(filtered_df)
    ) * 100

    congestion_col1, congestion_col2 = st.columns(2)

    congestion_col1.metric(
        "High Traffic Records",
        f"{len(congested_records):,}"
    )

    congestion_col2.metric(
        "High Traffic Percentage",
        f"{congestion_percentage:.1f}%"
    )

    st.caption(
        "High traffic is defined here as 50 or more vehicles "
        "in one record. This is a simple project threshold, "
        "not an official traffic classification."
    )

    if "location" in filtered_df.columns:
        st.markdown("### High Traffic by Location")

        congestion_by_location = (
            filtered_df.assign(
                High_Traffic=(
                    filtered_df["vehicle_count"]
                    >= congestion_threshold
                )
            )
            .groupby("location")["High_Traffic"]
            .sum()
            .sort_values(ascending=False)
        )

        congestion_by_location.index.name = "Location"
        congestion_by_location.name = "High Traffic Records"

        st.bar_chart(
            congestion_by_location,
            use_container_width=True
        )

st.divider()

# Recent Traffic Records
st.subheader("Recent Traffic Records")

display_df = filtered_df.copy()

if "timestamp" in display_df.columns:
    display_df["timestamp"] = (
        display_df["timestamp"]
        .dt.strftime("%d %b %Y, %I:%M %p")
    )

column_names = {
    "timestamp": "Date and Time",
    "location": "Location",
    "vehicle_count": "Vehicle Count",
    "average_speed": "Average Speed (km/h)",
    "speed": "Speed (km/h)",
    "congestion": "Congestion Level"
}

display_df = display_df.rename(
    columns=column_names
)

display_df = display_df.drop(
    columns=["sensor_id"],
    errors="ignore"
)

if "Date and Time" in display_df.columns:
    display_df = display_df.sort_values(
        "Date and Time",
        ascending=False
    )

st.dataframe(
    display_df.head(20),
    use_container_width=True,
    hide_index=True
)

# Footer
st.divider()

st.caption(
    "Smart City Traffic Monitoring System"
)