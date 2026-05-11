# ============================================================
# MINIO UPLOAD — Stockage des données BRUTES
# Source : topic Redpanda "capteurs_agri" (Thierno)
# ============================================================

from minio import Minio
from kafka import KafkaConsumer
import pandas as pd
import json
import io

# PARTIE 1 : Connexion à MinIO 
client = Minio(
    client = Minio("minio:9000", access_key="admin", secret_key="password", secure=False),
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

#PARTIE 2 : Créer le bucket s'il n'existe pas
if not client.bucket_exists("agri-data"):
    client.make_bucket("agri-data")

#PARTIE 3 : Lire les données BRUTES depuis Redpanda
# On lit depuis "capteurs_agri" — le topic de Thierno
# Ce sont les données brutes, non traitées par Spark
consumer = KafkaConsumer(
    "capteurs_agri",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

donnees_brutes = []
for message in consumer:
    donnees_brutes.append(message.value)
    if len(donnees_brutes) >= 10:
        break

df = pd.DataFrame(donnees_brutes)
print(f"{len(df)} messages récupérés depuis capteurs_agri")

#PARTIE 4 : Convertir en Parquet et uploader
buffer = io.BytesIO()               # fichier virtuel en mémoire
df.to_parquet(buffer, index=False)  # conversion en format Parquet
buffer.seek(0)                      # remettre le curseur au début

client.put_object(
    "agri-data",                        # nom du bucket
    "capteurs/donnees_brutes.parquet",  # chemin dans le bucket
    buffer,                             # contenu du fichier
    length=buffer.getbuffer().nbytes    # taille en bytes
)

print("Upload MinIO réussi.")