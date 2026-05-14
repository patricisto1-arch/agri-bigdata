from pyspark.sql.functions import col, when

def detect_alerts(df):
    return df.withColumn(
        "alerte",
        when(col("temperature_sol") > 50, "CHALEUR")
        .when(col("humidite_sol") < 20,   "SECHERESSE")
        .when(col("ph_sol") < 5.0,        "SOL ACIDE")
        .when(col("ph_sol") > 8.5,        "SOL ALCALIN")
        .otherwise("OK")
    )