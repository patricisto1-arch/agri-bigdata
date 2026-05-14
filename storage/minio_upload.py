from minio import Minio
from kafka import KafkaConsumer
import pandas as pd
import json
import io
import time

# ============================================================
# MINIO UPLOAD — Stockage des données BRUTES en continu
# Source : topic Redpanda "capteurs_agri"
# Stratégie : batch toutes les 60s ou 100 messages
# ============================================================

BATCH_SIZE     = 100   # uploader tous les 100 messages
BATCH_INTERVAL = 60    # ou toutes les 60 secondes

# PARTIE 1 : Connexion à MinIO
client = Minio("minio:9000", access_key="admin", secret_key="password", secure=False)

# PARTIE 2 : Créer le bucket s'il n'existe pas
if not client.bucket_exists("agri-data"):
    client.make_bucket("agri-data")
    print("Bucket 'agri-data' créé.")

# PARTIE 3 : Consumer Redpanda continu
consumer = KafkaConsumer(
    "capteurs_agri",
    bootstrap_servers="redpanda:9092",
    auto_offset_reset="earliest",
    group_id="minio-uploader",        # offset tracking
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    # pas de consumer_timeout_ms → tourne indéfiniment
)

print("En écoute sur capteurs_agri → MinIO...")

batch        = []
last_upload  = time.time()
file_counter = 0

for message in consumer:
    batch.append(message.value)

    elapsed = time.time() - last_upload
    should_upload = len(batch) >= BATCH_SIZE or elapsed >= BATCH_INTERVAL

    if should_upload and batch:
        df = pd.DataFrame(batch)

        # Convertir en Parquet et uploader
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        # Nom de fichier unique avec timestamp
        timestamp  = time.strftime("%Y%m%d_%H%M%S")
        object_name = f"capteurs/brutes_{timestamp}_{file_counter}.parquet"

        try:
            client.put_object(
                "agri-data",
                object_name,
                buffer,
                length=buffer.getbuffer().nbytes,
                content_type="application/octet-stream"
            )
            print(f"Upload MinIO OK : {object_name} ({len(df)} lignes)")
            file_counter += 1
        except Exception as e:
            print(f"Erreur upload MinIO : {e}")

        # Reset batch
        batch       = []
        last_upload = time.time()
