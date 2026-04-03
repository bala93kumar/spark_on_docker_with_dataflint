#!/bin/bash

set -e

echo "=========================================="
echo "Starting Spark ETL Pipeline with DataFlint"
echo "=========================================="
echo ""

# Create required directories
mkdir -p /data/spark-events
mkdir -p /data/output

# Generate test data
echo "📊 Generating test data..."
python3 /app/generate_data.py
echo ""

# Run Spark ETL job with event logging + DataFlint monitoring
echo "🚀 Running ETL pipeline with DataFlint monitoring..."
spark-submit \
    --master local[4] \
    --driver-memory 2g \
    --executor-memory 2g \
    --jars /app/spark_2.12-0.8.8.jar \
    --conf spark.eventLog.enabled=true \
    --conf spark.eventLog.dir=/data/spark-events \
    --conf spark.eventLog.compress=false \
    /app/spark_etl_app.py

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
echo "Container staying alive for 1 hour..."
echo "You can inspect data with: docker exec spark-etl-app <command>"
sleep 3600
