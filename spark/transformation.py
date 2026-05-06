import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, when
from pyspark.sql.types import StructType, StringType, DoubleType, LongType

os.environ["PYSPARK_PYTHON"] = "python"

spark = SparkSession.builder \
    .appName("AgriPipeline") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

schema = StructType() \
    .add("capteur_id", StringType()) \
    .add("temperature", DoubleType()) \
    .add("humidite", DoubleType()) \
    .add("ph", DoubleType()) \
    .add("timestamp", LongType())

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "redpanda:9092") \
    .option("subscribe", "capteurs_agri") \
    .load()

df = df.selectExpr("CAST(value AS STRING)")

df_parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

df_clean = df_parsed.filter(
    (col("temperature").between(0, 60)) &
    (col("humidite").between(0, 100)) &
    (col("ph").between(0, 14))
)

df_alert = df_clean.withColumn(
    "alerte",
    when(col("temperature") > 50, "CHALEUR")
    .when(col("humidite") > 90, "HUMIDITE")
    .when(col("ph") < 4, "SOL ACIDE")
    .otherwise("OK")
)

query = df_alert.selectExpr(
    "to_json(struct(*)) AS value"
).writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "redpanda:9092") \
    .option("topic", "alertes_agri") \
    .option("checkpointLocation", "/tmp/checkpoint_agri") \
    .start()

query.awaitTermination()