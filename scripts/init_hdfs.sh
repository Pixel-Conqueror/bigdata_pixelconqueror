#!/bin/bash
# /scripts/init_hdfs.sh

# 0. Quitter safe mode si besoin
hdfs dfsadmin -safemode leave || true

# 1. Zones raw
hdfs dfs -mkdir -p /movielens/raw/movies /movielens/raw/ratings

# 2. Zones processed (batch + streaming)
hdfs dfs -mkdir -p /movielens/processed/batch/movies /movielens/processed/batch/ratings
hdfs dfs -mkdir -p /movielens/processed/streaming/ratings

# 3. Archive
hdfs dfs -mkdir -p /movielens/archive/movies /movielens/archive/ratings

# 4. Droits généraux
hdfs dfs -chmod -R 777 /movielens

# 5. Ingestion des CSV raw
hdfs dfs -put -f /data/movies.csv  /movielens/raw/movies/
hdfs dfs -put -f /data/ratings.csv /movielens/raw/ratings/

echo "✓ HDFS structuré et CSV bruts en place"
