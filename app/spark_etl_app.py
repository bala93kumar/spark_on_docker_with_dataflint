"""
Spark ETL Application for DataFlint Testing
Clean, lazy DataFrame operations for better DAG visualization
"""

import sys
import logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, expr, upper, lower, split, 
    sum as spark_sum, avg, count, max as spark_max, min as spark_min,
    row_number, stddev, count_distinct
)
from pyspark.sql.window import Window

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spark_session(app_name="DataFlint-ETL-Test"):
    """Create Spark session"""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.default.parallelism", "8") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info(f"✓ Spark Session created")
    return spark


def main():
    """Main ETL pipeline - single lazy evaluation"""
    spark = None
    try:
        logger.info("=" * 60)
        logger.info("Starting Spark ETL Pipeline")
        logger.info("=" * 60)
        
        spark = create_spark_session()
        
        data_path = "/data"
        output_path = "/data/output"
        
        # === LOAD ===
        logger.info("Loading data...")
        customers_df = spark.read \
            .option("header", "true") \
            .csv(f"{data_path}/customers.csv")
        
        transactions_df = spark.read \
            .option("header", "true") \
            .csv(f"{data_path}/transactions.csv")
        
        # === TRANSFORM TRANSACTIONS ===
        logger.info("Transforming transactions...")
        transactions_df = transactions_df \
            .withColumn("amount", col("amount").cast("double")) \
            .withColumn("transaction_date", col("timestamp").cast("timestamp")) \
            .withColumn("transaction_type", 
                when(col("amount") > 1000, "high_value")
                .when(col("amount") > 100, "medium_value")
                .otherwise("small_value")) \
            .withColumn("year", expr("year(transaction_date)")) \
            .withColumn("month", expr("month(transaction_date)")) \
            .withColumn("day", expr("day(transaction_date)")) \
            .dropDuplicates(["transaction_id"])
        
        # === TRANSFORM CUSTOMERS ===
        logger.info("Transforming customers...")
        customers_df = customers_df \
            .withColumn("customer_name_clean", upper(col("customer_name"))) \
            .withColumn("email_domain", split(col("email"), "@").getItem(1)) \
            .withColumn("lifecycle_stage",
                when(col("segment") == "VIP", "high_value")
                .when(col("segment") == "Regular", "active")
                .otherwise("at_risk"))
        
        # === ENRICH (JOIN) ===
        logger.info("Enriching data with join...")
        enriched_df = transactions_df.join(
            customers_df.select("customer_id", "customer_name_clean", "email_domain", 
                               "lifecycle_stage", "segment", "country"),
            on="customer_id",
            how="left"
        )
        
        # === PRODUCT ANALYSIS (Final Output - Rich DAG) ===
        logger.info("Final analysis: Product category performance...")
        final_analysis = enriched_df \
            .filter(col("category").isNotNull()) \
            .filter(col("amount") > 0) \
            .groupBy("category", "product_id", "country") \
            .agg(
                count_distinct("customer_id").alias("unique_buyers"),
                count("*").alias("units_sold"),
                spark_sum("amount").alias("total_revenue"),
                avg("amount").alias("avg_price"),
                spark_min("amount").alias("min_price"),
                spark_max("amount").alias("max_price"),
                stddev("amount").alias("price_stddev")
            ) \
            .filter(col("units_sold") > 2) \
            .withColumn("revenue_rank", 
                row_number().over(Window.partitionBy("category").orderBy(col("total_revenue").desc()))) \
            .filter(col("revenue_rank") <= 20) \
            .orderBy(col("total_revenue").desc(), col("units_sold").desc())
        
        # === SINGLE WRITE (Triggers Complete DAG Evaluation) ===
        logger.info("Writing final analysis output...")
        final_analysis.write.mode("overwrite").parquet(f"{output_path}/final_product_analysis")
        
        logger.info("=" * 60)
        logger.info("✓ ETL Pipeline Completed Successfully")
        logger.info("=" * 60)
        logger.info("Results at: http://localhost:18080")
        logger.info("✓ Container exiting.")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            spark.stop()


if __name__ == "__main__":
    main()
