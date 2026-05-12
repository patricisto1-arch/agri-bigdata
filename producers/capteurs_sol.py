from kafka import KafkaProducer
import json
import time
import random
import math
import os
from datetime import datetime, timezone

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPIC = 'capteurs_agri'

# 14 regions du Senegal avec cultures principales
REGIONS = [
    {"id": "SN-KAO", "region": "Kaolack",      "culture": "arachide",  "lat": 14.15, "lon": -16.07},
    {"id": "SN-THI", "region": "Thies",         "culture": "mil",       "lat": 14.78, "lon": -16.92},
    {"id": "SN-DIO", "region": "Diourbel",      "culture": "arachide",  "lat": 14.65, "lon": -16.23},
    {"id": "SN-ZIG", "region": "Ziguinchor",    "culture": "riz",       "lat": 12.58, "lon": -16.27},
    {"id": "SN-KOL", "region": "Kolda",         "culture": "riz",       "lat": 12.89, "lon": -14.94},
    {"id": "SN-SED", "region": "Sedhiou",       "culture": "anacarde",  "lat": 12.70, "lon": -15.55},
    {"id": "SN-SLO", "region": "Saint-Louis",   "culture": "riz",       "lat": 16.03, "lon": -16.50},
    {"id": "SN-LOU", "region": "Louga",         "culture": "mil",       "lat": 15.61, "lon": -16.22},
    {"id": "SN-MAT", "region": "Matam",         "culture": "sorgho",    "lat": 15.65, "lon": -13.25},
    {"id": "SN-TAM", "region": "Tambacounda",   "culture": "coton",     "lat": 13.77, "lon": -13.68},
    {"id": "SN-FAT", "region": "Fatick",        "culture": "arachide",  "lat": 14.33, "lon": -16.41},
    {"id": "SN-KAF", "region": "Kaffrine",      "culture": "arachide",  "lat": 14.10, "lon": -15.55},
    {"id": "SN-KED", "region": "Kedougou",      "culture": "mais",      "lat": 12.55, "lon": -12.18},
    {"id": "SN-DAK", "region": "Dakar",         "culture": "maraichage","lat": 14.71, "lon": -17.46},
]

# Valeurs de base realistes par region
BASE_SOL = {
    "SN-KAO": {"humidite": 55, "temperature": 28, "ph": 6.5},
    "SN-THI": {"humidite": 50, "temperature": 30, "ph": 6.8},
    "SN-DIO": {"humidite": 48, "temperature": 31, "ph": 6.6},
    "SN-ZIG": {"humidite": 75, "temperature": 27, "ph": 4.5}, # Modifié pour déclencher une Alerte pH < 5.0
    "SN-KOL": {"humidite": 72, "temperature": 28, "ph": 5.9},
    "SN-SED": {"humidite": 68, "temperature": 27, "ph": 6.0},
    "SN-SLO": {"humidite": 60, "temperature": 26, "ph": 7.2},
    "SN-LOU": {"humidite": 15, "temperature": 33, "ph": 6.9}, # Modifié pour déclencher une Alerte Humidité < 20%
    "SN-MAT": {"humidite": 42, "temperature": 34, "ph": 7.0},
    "SN-TAM": {"humidite": 58, "temperature": 29, "ph": 6.3},
    "SN-FAT": {"humidite": 52, "temperature": 29, "ph": 6.7},
    "SN-KAF": {"humidite": 50, "temperature": 30, "ph": 6.5},
    "SN-KED": {"humidite": 65, "temperature": 28, "ph": 5.7},
    "SN-DAK": {"humidite": 62, "temperature": 27, "ph": 7.1},
}

def variation(valeur_base, amplitude, t):
    """Simule une variation naturelle avec cycle + bruit"""
    cycle = amplitude * math.sin(2 * math.pi * t / 86400)
    bruit = random.gauss(0, amplitude * 0.1)
    return round(valeur_base + cycle + bruit, 2)

def generer_mesure_sol(region, t):
    base = BASE_SOL[region["id"]]

    humidite   = max(0, min(100, variation(base["humidite"], 8, t)))
    temperature = variation(base["temperature"], 4, t)
    ph         = max(4.0, min(9.0, variation(base["ph"], 0.3, t)))

    # Alerte si sol trop sec ou pH critique
    alerte = humidite < 20 or ph < 5.0 or ph > 8.5

    return {
        "region_id"       : region["id"],
        "region"          : region["region"],
        "latitude"        : region["lat"],
        "longitude"       : region["lon"],
        
        "timestamp" : datetime.now(timezone.utc).isoformat(),
        "type"            : "sol",
        "culture"         : region["culture"],
        "humidite_sol"    : round(humidite, 2),
        "temperature_sol" : round(temperature, 2),
        "ph_sol"          : round(ph, 2),
        "rendement"       : None,
        "pluie_mm"        : None,
        "alerte"          : alerte
    }

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print(f"Simulation capteurs sol — {len(REGIONS)} regions\n")

    t = 0
    while True:
        for region in REGIONS:
            mesure = generer_mesure_sol(region, t)
            producer.send(TOPIC, value=mesure, key=region["id"].encode())

            flag = " ⚠ ALERTE" if mesure["alerte"] else ""
            print(
                f"{mesure['region']:<14} | "
                f"Humidite: {mesure['humidite_sol']:>5}% | "
                f"Temp sol: {mesure['temperature_sol']:>5}°C | "
                f"pH: {mesure['ph_sol']:>4}"
                f"{flag}"
            )

        producer.flush()
        print("---")
        time.sleep(3)
        t += 3

if __name__ == "__main__":
    main()