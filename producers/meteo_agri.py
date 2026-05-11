import os
import json
import time
import requests
from datetime import datetime, timezone
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'redpanda:9092')
TOPIC = 'meteo-agricole'
OWM_API_KEY = os.getenv('OWM_API_KEY', '')

REGIONS = [
    {"id": "SN-KAO", "region": "Kaolack", "lat": 14.15, "lon": -16.07},
    {"id": "SN-THI", "region": "Thies", "lat": 14.78, "lon": -16.92},
    {"id": "SN-DIO", "region": "Diourbel", "lat": 14.65, "lon": -16.23},
    {"id": "SN-ZIG", "region": "Ziguinchor", "lat": 12.58, "lon": -16.27},
    {"id": "SN-KOL", "region": "Kolda", "lat": 12.89, "lon": -14.94},
    {"id": "SN-SED", "region": "Sedhiou", "lat": 12.70, "lon": -15.55},
    {"id": "SN-SLO", "region": "Saint-Louis", "lat": 16.03, "lon": -16.50},
    {"id": "SN-LOU", "region": "Louga", "lat": 15.61, "lon": -16.22},
    {"id": "SN-MAT", "region": "Matam", "lat": 15.65, "lon": -13.25},
    {"id": "SN-TAM", "region": "Tambacounda", "lat": 13.77, "lon": -13.68},
    {"id": "SN-FAT", "region": "Fatick", "lat": 14.33, "lon": -16.41},
    {"id": "SN-KAF", "region": "Kaffrine", "lat": 14.10, "lon": -15.55},
    {"id": "SN-KED", "region": "Kedougou", "lat": 12.55, "lon": -12.18},
    {"id": "SN-DAK", "region": "Dakar", "lat": 14.71, "lon": -17.46},
]

def fetch_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erreur API OWM: {e}")
    return None

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print(f"Démarrage Simulateur Météo - {len(REGIONS)} régions")
    
    while True:
        for r in REGIONS:
            weather = None
            if OWM_API_KEY and OWM_API_KEY != 'votre_cle_api_ici':
                weather = fetch_weather(r['lat'], r['lon'])
            
            # Simulated fallback if no API key or API fails
            temp = weather['main']['temp'] if weather else 30.0 + (5 - (int(time.time()) % 10))
            rain = weather.get('rain', {}).get('1h', 0) if weather else (0 if int(time.time()) % 2 == 0 else 5.5)

            alerte = rain < 1.0 and temp > 35.0

            msg = {
                "region_id": r["id"],
                "region": r["region"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "meteo",
                "humidite_sol": None,
                "temperature_sol": None,
                "ph_sol": None,
                "rendement": None,
                "surface_ha": None,
                "production_t": None,
                "temperature_air": temp,
                "pluie_mm": rain,
                "alerte": alerte
            }
            producer.send(TOPIC, value=msg, key=r["id"].encode('utf-8'))
            print(f"[{r['region']}] Envoi: Temp {temp}°C, Pluie {rain}mm, Alerte Sécheresse: {alerte}")
        
        producer.flush()
        time.sleep(60) # Toutes les minutes en réalité, ou modéré

if __name__ == "__main__":
    main()
