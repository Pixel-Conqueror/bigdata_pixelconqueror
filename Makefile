# Makefile

# 1. Lancer l'environnement Docker
up:
	docker compose up -d --build --wait

# 2. Arrêter & nettoyer
down:
	docker compose down

# 2.1 Création de l'environnement virtuel
venv:
	python3 -m venv venv
	chmod +x venv/bin/activate
	chmod 755 venv/bin/activate
	. venv/bin/activate && pip install -r requirements.txt

# clean:
# 	docker compose down --rmi all --volumes --remove-orphans
# 	docker system prune -af

# 3. Voir les logs
logs:
	docker-compose logs -f

# 4. Ingestion des CSV bruts dans HDFS
init_hdfs:
	@echo "▶️  Initialisation HDFS et ingestion des CSV…"
	docker-compose exec namenode bash /scripts/init_hdfs.sh

# 5. ETL batch (nettoyage + enrichment + écriture CSV)
batch_etl:
	@echo "▶️  Lancement de l'ETL batch…"
	docker exec -it spark-master spark-submit \
	  --master local[*] \
	  --driver-memory 4g \
	  --conf spark.driver.maxResultSize=2g \
	  /scripts/etl_batch.py

batch_etl_light:
	@echo "▶️  Lancement de l'ETL batch…"
	docker exec -it spark-master spark-submit \
	  --master local[*] \
	  --driver-memory 4g \
	  --conf spark.driver.maxResultSize=2g \
	  /scripts/etl_batch_light.py

#5.1 ingestion des données dans mongodb
load_to_mongo:
	docker exec -it spark-master spark-submit \
	  --master local[*] \
	  --driver-memory 4g \
	  --conf spark.driver.maxResultSize=2g \
	  /scripts/ingest_to_mongo.py



# 6. Entraînement ALS
train_als:
	@echo "▶️  Entraînement du modèle ALS…"
	docker exec -it spark-master spark-submit \
	  --master local[*] \
	  --driver-memory 4g \
	  --conf spark.driver.maxResultSize=2g \
	  /scripts/train_als.py

# 7. Lancer le streaming
streaming:
	@echo "▶️  Démarrage du job streaming…"
	docker-compose exec spark-master spark-submit \
	  --master local[*] \
	  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
	  /scripts/streaming_recommendations.py


# 8. Pipelines complètes
pipeline: clean up init_hdfs batch_etl load_to_mongo train_als generate_recs streaming
	@echo "✅ Pipeline complète terminée !"

pipeline_light: clean up init_hdfs batch_etl_light load_to_mongo train_als generate_recs streaming
	@echo "✅ Pipeline light complète terminée !"


generate_recs:
	@echo "▶️  Génération de toutes les recommandations…"
	docker-compose exec spark-master spark-submit \
	  --master local[*] \
	  /scripts/generate_all_recommendations.py
test_update:
	@echo "▶️  Test mise à jour pour un utilisateur…"
	docker-compose exec jupyter python3 /scripts/test_update_user.py
# Backend commands
backend-shell:
	docker exec -it api bash

backend-logs:
	docker logs -f api

mongo-shell:
	docker exec -it mongo-db mongosh movies

# Kafka commands
kafka-topics:
	docker exec -it kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Jupyter commands
jupyter-token:
	docker exec -it jupyter jupyter notebook list

.PHONY: up down logs clean init_hdfs batch_etl batch_etl_light train_als streaming pipeline pipeline_light backend-shell backend-logs mongo-shell kafka-topics jupyter-token
