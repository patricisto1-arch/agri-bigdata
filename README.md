# 🌱 Projet Big Data — Agriculture de Précision

## 📌 Description

Ce projet consiste à concevoir une architecture Big Data capable de collecter, traiter et stocker des données agricoles en temps réel.

Les données proviennent de capteurs IoT placés dans les champs (température, humidité, pH) et d’API météo externes.  
L’objectif est d’analyser ces données afin d’optimiser la production agricole et d’aider à la prise de décision.

---

## 🏗️ Architecture

Le projet repose sur une architecture Big Data en trois couches :

### 🔹 Sources de données
- Capteurs IoT (température, humidité du sol, pH)
- API météo (OpenWeatherMap)
- (Optionnel) Images satellites

### 🔹 Traitement
- **Redpanda** : ingestion des données en streaming
- **Apache Spark** : traitement, nettoyage et analyse des données
- Détection d’anomalies (ex : sécheresse)

### 🔹 Stockage
- **MinIO** : Data Lake pour les données brutes
- **PostgreSQL** : base de données pour les données structurées

---

## 🔄 Flux de données

Sources → Redpanda → Spark → MinIO + PostgreSQL

---

## ⚙️ Technologies utilisées

- Redpanda : streaming temps réel
- Apache Spark : traitement des données
- MinIO : stockage des données (Data Lake)
- PostgreSQL : base de données relationnelle
- Docker : orchestration des services
- Jupyter Notebook : documentation et démonstration
