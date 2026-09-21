
import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Page settings
st.set_page_config(
    page_title="SmartCities Dashboard",
    page_icon="🏙️",
    layout="wide"
)

# Simple styling
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fb;
    }

    h1, h2, h3 {
        color: #20304a;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e3e8f0;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stSidebar"] {
        background-color: #edf2f8;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #e3e8f0;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Connect to MongoDB
@st.cache_resource
def connect_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    return client["smartcity"]

db = connect_mongodb()
traffic_collection = db["traffic_readings"]

# Header
st.title("🏙️ SmartCities")
st.caption("Smart City Traffic Monitoring")
st.markdown("---")

# Refresh button
if st.button("🔄 Refresh data"):
    st.cache_data.clear()
    st.rerun()

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
    st.info("No traffic data available yet. Start your Kafka producer and Spark Streaming.")
    st.stop()

# Clean and prepare data
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])

df["vehicle_count"] = pd.to_numeric(
    df["vehicle_count"], errors="coerce"
)
df["average_speed"] = pd.to_numeric(
    df["average_speed"], errors="coerce"
)
df = df.dropna(subset=["vehicle_count", "average_speed"])

# Sidebar filter
st.sidebar.header("Dashboard Filters")

locations = sorted(df["location"].dropna().unique())

selected_locations = st.sidebar.multiselect(
    "Select location",
    locations,
    default=locations
)

filtered_df = df[
    df["location"].isin(selected_locations)
].copy()

if filtered_df.empty:
    st.warning("No data for the selected locations.")
    st.stop()

# Summary metrics
st.subheader("Traffic Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Vehicles",
    f"{int(filtered_df['vehicle_count'].sum()):,}"
)

col2.metric(
    "Average Speed",
    f"{filtered_df['average_speed'].mean():.1f} km/h"
)

col3.metric(
    "High Congestion Events",
    int((filtered_df["congestion_level"] == "High").sum())
)

col4.metric(
    "Locations",
    filtered_df["location"].nunique()
)

st.markdown("")

# Charts
st.subheader("Traffic Trends")

left, right = st.columns(2)

with left:
    st.markdown("#### Vehicle Count Over Time")

    chart_data = (
        filtered_df
        .sort_values("timestamp")
        .set_index("timestamp")[["vehicle_count"]]
    )

    st.line_chart(chart_data)

with right:
    st.markdown("#### Average Speed by Location")

    speed_data = (
        filtered_df
        .groupby("location")["average_speed"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(speed_data)

# Congestion breakdown
st.markdown("---")
st.subheader("Congestion Summary")

congestion_counts = (
    filtered_df["congestion_level"]
    .value_counts()
    .rename_axis("Congestion Level")
    .reset_index(name="Events")
)

left, right = st.columns([1, 2])

with left:
    st.dataframe(
        congestion_counts,
        hide_index=True,
        use_container_width=True
    )

with right:
    st.bar_chart(
        congestion_counts.set_index("Congestion Level")
    )

# Recent records
st.markdown("---")
st.subheader("Recent Traffic Readings")

recent_df = (
    filtered_df
    .sort_values("timestamp", ascending=False)
    .head(20)
    .copy()
)

recent_df["timestamp"] = (
    recent_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
)

st.dataframe(
    recent_df,
    hide_index=True,
    use_container_width=True
)

st.caption("SmartFlow | Big Data Technologies Project")