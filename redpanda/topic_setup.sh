#!/bin/bash

# Création topics Redpanda (Kafka compatible)

rpk topic create capteurs_agri --brokers localhost:9092 || true
rpk topic create meteo_externe --brokers localhost:9092 || true
rpk topic create alertes_agri --brokers localhost:9092 || true
rpk topic create production_agricole --brokers localhost:9092 || true

echo "Topics créés avec succès"