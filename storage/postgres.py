# ============================================================
# POSTGRES INSERT — Stockage des données TRAITÉES
# Source : topic Redpanda "alertes_agri" (Fatou/Spark)
# ============================================================

import psycopg2
import pandas as pd
from kafka import KafkaConsumer
import json

# PARTIE 1 : Connexion à PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="agridb",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()  # le curseur exécute les commandes SQL

# PARTIE 2 : Créer la table si elle n'existe pas
# Colonnes basées sur ce que Spark (Fatou) produit dans alertes_agri :
# capteur_id, temperature, humidite, ph, timestamp, alerte
cur.execute("""
    CREATE TABLE IF NOT EXISTS capteurs (
        capteur_id  VARCHAR(10),
        temperature FLOAT,
        humidite    FLOAT,
        ph          FLOAT,
        timestamp   BIGINT,
        alerte      VARCHAR(20)
    )
""")

# PARTIE 3 : Lire les données TRAITÉES depuis Redpanda
# On lit depuis "alertes_agri" — la sortie de Spark de Fatou
# Ces données sont déjà nettoyées et enrichies avec les alertes
consumer = KafkaConsumer(
    "alertes_agri",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

donnees_traitees = []
for message in consumer:
    donnees_traitees.append(message.value)
    if len(donnees_traitees) >= 10:  # on récupère 10 messages puis on stoppe
        break

df = pd.DataFrame(donnees_traitees)
print(f"{len(df)} messages récupérés depuis alertes_agri")

# PARTIE 4 : Insérer chaque ligne dans PostgreSQL
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO capteurs VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        row["capteur_id"],
        row["temperature"],
        row["humidite"],
        row["ph"],
        row["timestamp"],
        row["alerte"]
    ))

# PARTIE 5 : Valider et fermer
conn.commit()   # OBLIGATOIRE — sans ça rien n'est sauvegardé
cur.close()     # fermer le curseur
conn.close()    # fermer la connexion

print("Insertion PostgreSQL réussie.")