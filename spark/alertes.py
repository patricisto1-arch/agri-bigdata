from pyspark.sql.functions import col, when

def detect_alerts(df):
    return df.withColumn(
        "alerte",
        when(col("temperature") > 50, "CHALEUR EXTREME")
        .when(col("temperature") < 5, "FROID")
        .when(col("ph") > 12, "PH ELEVE")
        .when(col("ph") < 3, "PH BAS")
        .otherwise("OK")
    )