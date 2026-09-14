from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)

spark = (
    SparkSession.builder
    .appName("SmartCityStreaming")
    .getOrCreate()
)

schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("sensor_id", StringType(), True),
    StructField("location", StringType(), True),
    StructField("vehicle_count", IntegerType(), True),
    StructField("average_speed", DoubleType(), True),
    StructField("congestion_level", StringType(), True)
])

stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "traffic")
    .option("startingOffsets", "latest")
    .load()
)

traffic = (
    stream
    .selectExpr("CAST(value AS STRING) AS json")
    .select(from_json(col("json"), schema).alias("data"))
    .select("data.*")
)

valid_data = traffic.filter(
    (col("vehicle_count") >= 0) &
    (col("average_speed") >= 0)
)

query = (
    valid_data.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", False)
    .start()
)

query.awaitTermination()