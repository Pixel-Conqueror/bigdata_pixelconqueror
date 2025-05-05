# 🎬 Système de Recommandation de Films

## 🌍 Vue d'ensemble

Ce projet implémente un système de recommandation de films utilisant une architecture Big Data avec :

- **Hadoop HDFS** pour le stockage distribué
- **Spark** pour le traitement des données
- **Kafka** pour le streaming en temps réel
- **MongoDB** pour le stockage des données nettoyées
- **ALS (Alternating Least Squares)** pour l'algorithme de recommandation

## 🚀 Démarrage rapide

### Prérequis

- Docker et Docker Compose
- Python 3.x

### Installation

Vous avez le choix entre deux approches :

#### 1. Approche automatisée (recommandée)

```bash
# Pipeline complète
make pipeline

# ou version allégée
make pipeline_light
```

#### 2. Approche manuelle (étape par étape)

1. **Lancer l'environnement Docker**

```bash
make up
```

2. **Initialiser HDFS et ingérer les données**

```bash
make init_hdfs
```

3. **Nettoyer et enrichir les données (ETL)**

```bash
make batch_etl
# ou version allégée
make batch_etl_light
```

4. **Charger les données dans MongoDB**

```bash
make load_to_mongo
```

5. **Entraîner le modèle ALS**

```bash
make train_als
```

6. **Générer les recommandations**

```bash
make generate_recs
```

7. **Lancer le streaming**

```bash
make streaming
```

````

## 🛠️ Commandes utiles

### Gestion de l'environnement

```bash
# Arrêter l'environnement
make down

# Voir les logs
make logs
````

### Backend

```bash
# Accéder au shell du backend
make backend-shell

# Voir les logs du backend
make backend-logs
```

### MongoDB

```bash
# Accéder au shell MongoDB
make mongo-shell
```

### Kafka

```bash
# Lister les topics Kafka
make kafka-topics
```

### Jupyter

```bash
# Obtenir le token Jupyter
make jupyter-token
```

## 📊 Architecture

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:5001
- **MongoDB** : localhost:27017
- **Hadoop HDFS Namenode UI** : http://localhost:9870
- **Spark Master UI** : http://localhost:8080
- **Kafka** : localhost:9092
- **Jupyter Notebook** : http://localhost:8888

## 📁 Structure du projet

```
/
|-- Dockerfile
|-- docker-compose.yml
|-- Makefile
|-- requirements.txt
|-- config/
|   |-- hadoop/
|-- scripts/
    |-- etl_batch.py
    |-- etl_batch_light.py
    |-- generate_all_recommendations.py
    |-- ingest_to_mongo.py
    |-- init_hdfs.sh
    |-- streaming_recommendations.py
    |-- test_update_user.py
    |-- train_als.py
```

## 🔔 Notes importantes

- Assurez-vous d'avoir suffisamment de mémoire disponible pour Spark (4GB minimum)
- Les données doivent être correctement formatées avant l'ingestion
- Le modèle ALS nécessite des données nettoyées pour un bon entraînement

---

Made with ❤️ by Robin, Thomas et Sonny
