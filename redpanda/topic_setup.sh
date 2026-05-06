#!/bin/bash

# Création topics Redpanda (Kafka compatible)

rpk topic create capteurs_agri --brokers localhost:9092
rpk topic create meteo_externe --brokers localhost:9092
rpk topic create alertes_agri --brokers localhost:9092

echo "Topics créés avec succès"