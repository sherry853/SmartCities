from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)

from pymongo import MongoClient


# Create Spark Session
spark = (
    SparkSession.builder
    .appName("SmartCityStreaming")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# Define traffic data schema
schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("sensor_id", StringType(), True),
    StructField("location", StringType(), True),
    StructField("vehicle_count", IntegerType(), True),
    StructField("average_speed", DoubleType(), True),
    StructField("congestion_level", StringType(), True)
])


# Read data from Kafka
stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "traffic")
    .option("startingOffsets", "latest")
    .load()
)


# Convert Kafka JSON into columns
traffic = (
    stream
    .selectExpr("CAST(value AS STRING) AS json")
    .select(from_json(col("json"), schema).alias("data"))
    .select("data.*")
)


# Validate incoming data
valid_data = traffic.filter(
    (col("vehicle_count") >= 0) &
    (col("average_speed") >= 0) &
    col("location").isNotNull()
)


# Function to write each Spark partition to MongoDB
def write_partition(rows):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["smartcity"]
    collection = db["traffic_readings"]
    documents = []

    for row in rows:
        documents.append(row.asDict())

    if documents:
        collection.insert_many(
            documents,
            ordered=False
        )
    client.close()


# Write each micro-batch to MongoDB
def write_to_mongodb(batch_df, batch_id):
    print(f"Processing batch: {batch_id}")
    batch_df.foreachPartition(write_partition)

# Start streaming query
query = (
    valid_data.writeStream
    .foreachBatch(write_to_mongodb)
    .outputMode("append")
    .start()
)


print("Spark Streaming is running...")
print("Waiting for Kafka traffic data...")


query.awaitTermination()