#!/bin/bash
# 0. Quitter safe mode si besoin
hdfs dfsadmin -safemode leave || true

hdfs dfsadmin -safemode leave || true

echo "⏳ Waiting for DataNode to register..."
MAX_TRIES=12
TRY=0
while [ $TRY -lt $MAX_TRIES ]; do
  # On récupère d'abord la ligne contenant "Live datanodes", puis on extrait le chiffre entre parenthèses
  LIVE=$(hdfs dfsadmin -report \
         | grep -E "Live datanodes" \
         | grep -Eo "\([0-9]+\)" \
         | grep -Eo "[0-9]+")
  if [ -n "$LIVE" ] && [ "$LIVE" -ge 1 ]; then
    echo "✅ Found $LIVE DataNode(s)."
    break
  fi
  echo "  → no DataNode yet (try $((TRY+1))/$MAX_TRIES)…"
  sleep 5
  TRY=$((TRY+1))
done

if [ -z "$LIVE" ] || [ "$LIVE" -lt 1 ]; then
  echo "❌ Timeout waiting for DataNode."
  exit 1
fi

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
