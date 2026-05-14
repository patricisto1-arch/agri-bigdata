import psycopg2
import json
import time
from kafka import KafkaConsumer

# ============================================================
# POSTGRES INSERT — Stockage des données TRAITÉES en continu
# Source : topic Redpanda "alertes_agri" (sortie Spark)
# ============================================================

def get_connection():
    return psycopg2.connect(
        host='postgres', port=5432,
        database='agri', user='admin', password='admin'
    )

def create_table(conn):
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS capteurs (
            region_id       VARCHAR(10),
            region          VARCHAR(50),
            latitude        FLOAT,
            longitude       FLOAT,
            timestamp       VARCHAR(50),
            culture         VARCHAR(50),
            humidite_sol    FLOAT,
            temperature_sol FLOAT,
            ph_sol          FLOAT,
            alerte          VARCHAR(20)
        )
    ''')
    conn.commit()
    cur.close()
    print("Table capteurs prête.")

def main():
    # Retry loop — attend que Postgres soit prêt
    conn = None
    for attempt in range(10):
        try:
            conn = get_connection()
            break
        except Exception as e:
            print(f"Postgres pas encore prêt ({attempt+1}/10): {e}")
            time.sleep(3)
    if conn is None:
        raise RuntimeError("Impossible de se connecter à PostgreSQL.")

    create_table(conn)

    # Consumer continu — pas de consumer_timeout_ms
    consumer = KafkaConsumer(
        'alertes_agri',
        bootstrap_servers='redpanda:9092',
        auto_offset_reset='earliest',
        group_id='postgres-inserter',   # offset tracking
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("En écoute sur alertes_agri → PostgreSQL...")
    cur = conn.cursor()

    for message in consumer:
        d = message.value
        try:
            cur.execute(
                '''INSERT INTO capteurs
                   (region_id, region, latitude, longitude, timestamp, culture,
                    humidite_sol, temperature_sol, ph_sol, alerte)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (d['region_id'], d['region'], d['latitude'], d['longitude'],
                 d['timestamp'], d['culture'], d['humidite_sol'],
                 d['temperature_sol'], d['ph_sol'], str(d['alerte']))
            )
            conn.commit()
            print(f"Inséré: {d['region']} | {d['timestamp']} | alerte: {d['alerte']}")
        except KeyError as e:
            print(f"Champ manquant: {e} — message ignoré")
            conn.rollback()
        except Exception as e:
            print(f"Erreur insertion: {e}")
            conn.rollback()
            # Reconnexion si la connexion est perdue
            try:
                conn = get_connection()
                cur  = conn.cursor()
            except Exception:
                pass

if __name__ == '__main__':
    main()
