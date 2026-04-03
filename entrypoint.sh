#!/bin/bash

set -e

echo "=========================================="
echo "Starting Spark ETL Pipeline with DataFlint"
echo "=========================================="
echo ""

# Create output directories
mkdir -p /data/spark-events
mkdir -p /data/output

# Ensure write permissions in container
chmod -R 777 /data/spark-events 2>/dev/null || true
chmod -R 777 /data/output 2>/dev/null || true

# Remove stale event logs
rm -rf /data/spark-events/* 2>/dev/null || true

# Generate data only if it doesn't exist
if [ ! -f /data/customers.csv ] || [ ! -f /data/transactions.csv ]; then
    echo "📊 Generating dataset (500K transactions)..."
    python3 /app/generate_data.py
    echo ""
else
    echo "✓ Using existing data files"
    echo ""
fi

# Run Spark ETL job with event logging + DataFlint monitoring
echo "🚀 Running ETL pipeline with DataFlint monitoring..."
spark-submit \
    --master local[8] \
    --driver-memory 2g \
    --executor-memory 2g \
    --jars /app/spark_2.12-0.8.8.jar \
    --conf spark.eventLog.enabled=true \
    --conf spark.eventLog.dir=/data/spark-events \
    --conf spark.eventLog.compress=false \
    --conf spark.sql.shuffle.partitions=16 \
    /app/spark_etl_app.py

# Make event logs readable by other users (History Server runs as spark user)
chmod 644 /data/spark-events/*

echo ""
echo "=========================================="
echo "✓ Pipeline completed successfully"
echo "=========================================="
echo ""
echo "📊 View results in DataFlint:"
echo "  • Spark History Server: http://localhost:18080"
echo "    (Shows DataFlint UI with DAG, metrics, data quality)"
echo ""
echo "📁 Output files:"
echo "  • Parquet data:  /data/output/"
echo "  • Event logs:    /data/spark-events/"
echo ""
echo "✓ Container exiting."
