# Makefile

# 1. Lancer l’environnement Docker
up:
	docker-compose up -d

# 2. Arrêter & nettoyer
down:
	docker-compose down


clean:
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -af

# 3. Voir les logs
logs:
	docker-compose logs -f


# 4. Ingestion des CSV bruts dans HDFS
init_hdfs:
	@echo "▶️  Initialisation HDFS et ingestion des CSV…"
	docker exec -it namenode bash /scripts/init_hdfs.sh


# 5. ETL batch (nettoyage + enrichment + écriture CSV)
batch_etl:
	@echo "▶️  Lancement de l’ETL batch…"
	docker exec -it spark-master spark-submit \
	  --master local[*] \
	  --driver-memory 4g \
	  --conf spark.driver.maxResultSize=2g \
	  /scripts/etl_batch.py

batch_etl_light:
	@echo "▶️  Lancement de l’ETL batch…"
	docker exec -it spark-master spark-submit \
	  --master local[*] \
	  --driver-memory 4g \
	  --conf spark.driver.maxResultSize=2g \
	  /scripts/etl_batch_light.py

# 6. Entraînement ALS
train_als:
	@echo "▶️  Entraînement du modèle ALS…"
	docker exec -it spark-master spark-submit \
	  --master local[*] \
	  --driver-memory 4g \
	  --conf spark.driver.maxResultSize=2g \
	  /scripts/train_als.py

# 8. Lancer le streaming
streaming:
	@echo "▶️  Démarrage du job streaming…"
	docker exec -d spark-master spark-submit \
	  --master local[*] \
	  --driver-memory 2g \
	  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 \
	  /scripts/streaming_recommendations.py


pipeline: clean up init_hdfs batch_etl train_als streaming
	@echo "✅ Pipeline complète terminée !"

pipeline_light: clean up init_hdfs batch_etl_light train_als streaming
	@echo "✅ Pipeline light complète terminée !"

.PHONY: up down logs ingest_etl train_als pipeline
