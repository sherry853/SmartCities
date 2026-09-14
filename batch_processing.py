from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, max, min, count

spark = (
    SparkSession.builder
    .appName("SmartCityBatch")
    .getOrCreate()
)

df = spark.read.csv(
    "hdfs://localhost:9000/smartcity/traffic/traffic.csv",
    header=True,
    inferSchema=True
)

df.show()

# Average traffic by location
traffic_summary = (
    df.groupBy("location")
      .agg(
          avg("vehicle_count").alias("average_vehicle_count"),
          avg("average_speed").alias("average_speed"),
          count("*").alias("record_count")
      )
)

traffic_summary.show()

# Highest traffic locations
highest_traffic = (
    df.groupBy("location")
      .agg(
          max("vehicle_count").alias("maximum_vehicle_count")
      )
      .orderBy("maximum_vehicle_count", ascending=False)
)

highest_traffic.show()

spark.stop()