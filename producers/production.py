from kafka import KafkaProducer
import csv
import json
import time
import random
import os
from datetime import datetime, timezone

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPIC        = 'production-agricole'
CSV_FILE     = os.path.join(os.path.dirname(__file__), '../data/fao_senegal.csv')

# Cultures principales par region
CULTURES_PAR_REGION = {
    "Kaolack"     : ["Groundnuts, excluding shelled", "Millet", "Sorghum"],
    "Thies"       : ["Groundnuts, excluding shelled", "Millet", "Tomatoes"],
    "Diourbel"    : ["Groundnuts, excluding shelled", "Millet", "Cow peas, dry"],
    "Ziguinchor"  : ["Rice", "Mangoes, guavas and mangosteens", "Cashew nuts, in shell"],
    "Kolda"       : ["Rice", "Maize (corn)", "Seed cotton, unginned"],
    "Sedhiou"     : ["Rice", "Cashew nuts, in shell", "Groundnuts, excluding shelled"],
    "Saint-Louis" : ["Rice", "Tomatoes", "Onions and shallots, dry (excluding dehydrated)"],
    "Louga"       : ["Millet", "Groundnuts, excluding shelled", "Cow peas, dry"],
    "Matam"       : ["Sorghum", "Millet", "Cow peas, dry"],
    "Tambacounda" : ["Maize (corn)", "Seed cotton, unginned", "Sesame seed"],
    "Fatick"      : ["Groundnuts, excluding shelled", "Rice", "Millet"],
    "Kaffrine"    : ["Groundnuts, excluding shelled", "Millet", "Sorghum"],
    "Kedougou"    : ["Maize (corn)", "Rice", "Sesame seed"],
    "Dakar"       : ["Tomatoes", "Onions and shallots, dry (excluding dehydrated)", "Eggplants (aubergines)"],
}

REGIONS = [
    {"id": "SN-KAO", "region": "Kaolack"},
    {"id": "SN-THI", "region": "Thies"},
    {"id": "SN-DIO", "region": "Diourbel"},
    {"id": "SN-ZIG", "region": "Ziguinchor"},
    {"id": "SN-KOL", "region": "Kolda"},
    {"id": "SN-SED", "region": "Sedhiou"},
    {"id": "SN-SLO", "region": "Saint-Louis"},
    {"id": "SN-LOU", "region": "Louga"},
    {"id": "SN-MAT", "region": "Matam"},
    {"id": "SN-TAM", "region": "Tambacounda"},
    {"id": "SN-FAT", "region": "Fatick"},
    {"id": "SN-KAF", "region": "Kaffrine"},
    {"id": "SN-KED", "region": "Kedougou"},
    {"id": "SN-DAK", "region": "Dakar"},
]

def charger_fao(fichier):
    """Charge les données FAO depuis le CSV"""
    donnees = {}
    with open(fichier, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            culture = row['Item']
            annee   = int(row['Year'])
            valeur  = float(row['Value']) if row['Value'] else 0
            if culture not in donnees:
                donnees[culture] = {}
            donnees[culture][annee] = valeur
    return donnees

def rendement_simule(surface_ha, culture):
    """
    Simule un rendement realiste en tonnes/ha
    base sur les moyennes senegalaises
    """
    rendements_base = {
        "Groundnuts, excluding shelled" : 1.2,
        "Rice"                          : 2.8,
        "Millet"                        : 0.8,
        "Sorghum"                       : 0.9,
        "Maize (corn)"                  : 1.8,
        "Seed cotton, unginned"         : 1.0,
        "Sesame seed"                   : 0.6,
        "Tomatoes"                      : 12.0,
        "Mangoes, guavas and mangosteens": 5.0,
        "Cashew nuts, in shell"         : 0.8,
        "Cow peas, dry"                 : 0.5,
        "Eggplants (aubergines)"        : 8.0,
        "Onions and shallots, dry (excluding dehydrated)": 10.0,
    }
    base = rendements_base.get(culture, 1.0)
    variation = random.gauss(0, base * 0.1)
    return round(max(0.1, base + variation), 3)

def main():
    # Charger les données FAO
    print("Chargement des donnees FAO...")
    if not os.path.exists(CSV_FILE):
        print(f"ERREUR: Fichier CSV introuvable: {CSV_FILE}")
        exit(1)
    donnees_fao = charger_fao(CSV_FILE)
    print(f"{len(donnees_fao)} cultures chargees\n")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print(f"Simulation production agricole — {len(REGIONS)} regions\n")

    while True:
        for region in REGIONS:
            cultures = CULTURES_PAR_REGION.get(region["region"], [])

            for culture in cultures:
                # Surface reelle depuis FAO (derniere annee disponible)
                surface_ha = 0
                if culture in donnees_fao:
                    annees = sorted(donnees_fao[culture].keys())
                    if annees:
                        surface_ha = donnees_fao[culture][annees[-1]]
                        # Repartir la surface nationale par region (approximation)
                        surface_ha = round(surface_ha / 14 * random.uniform(0.5, 1.5), 0)

                rendement = rendement_simule(surface_ha, culture)
                production = round(surface_ha * rendement, 1)

                message = {
                    "region_id"   : region["id"],
                    "region"      : region["region"],
                    # Nouvelle ligne
                    "timestamp" : datetime.now(timezone.utc).isoformat(),   
                    "type"        : "production",
                    "culture"     : culture,
                    "surface_ha"  : surface_ha,
                    "rendement"   : rendement,
                    "production_t": production,
                    "humidite_sol": None,
                    "temperature_sol": None,
                    "ph_sol"      : None,
                    "pluie_mm"    : None,
                    "alerte"      : rendement < 0.3
                }

                producer.send(TOPIC, value=message, key=region["id"].encode())
                print(
                    f"{region['region']:<14} | "
                    f"{culture[:25]:<25} | "
                    f"Surface: {surface_ha:>8.0f} ha | "
                    f"Rendement: {rendement:>5.2f} t/ha | "
                    f"Production: {production:>10.1f} t"
                )

        producer.flush()
        print("---")
        time.sleep(10)

if __name__ == "__main__":
    main()