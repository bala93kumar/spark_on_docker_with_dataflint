"""
Complex Spark ETL Application for DataFlint Testing
This app demonstrates multiple data transformations to generate complex DAGs
"""

import sys
import logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, expr, concat, lit, sum, avg, count, 
    window, split, explode, row_number, dense_rank, 
    broadcast, coalesce, substring, upper, lower
)
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

# Import DataFlint
try:
    from dataflint.spark import init_dataflint
except ImportError:
    logger_init = logging.getLogger(__name__)
    logger_init.warning("DataFlint not installed via Python - using JAR approach")
    init_dataflint = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spark_session(app_name="DataFlint-ETL-Test"):
    """Create and configure Spark session with DataFlint"""
    try:
        spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.shuffle.partitions", "4") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("INFO")
        logger.info(f"✓ Spark Session created: {app_name}")
        return spark
    except Exception as e:
        logger.error(f"Failed to create Spark session: {e}")
        sys.exit(1)


def load_raw_data(spark, data_path):
    """Load raw customer and transaction data"""
    logger.info("Loading raw data...")
    
    # Schema for transactions
    transactions_schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("category", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("timestamp", StringType(), True)
    ])
    
    # Schema for customer data
    customer_schema = StructType([
        StructField("customer_id", StringType(), True),
        StructField("customer_name", StringType(), True),
        StructField("email", StringType(), True),
        StructField("country", StringType(), True),
        StructField("segment", StringType(), True)
    ])
    
    # Load data
    transactions_df = spark.read.schema(transactions_schema).option("header", "true").csv(f"{data_path}/transactions.csv")
    customers_df = spark.read.schema(customer_schema).option("header", "true").csv(f"{data_path}/customers.csv")
    
    logger.info(f"✓ Loaded {transactions_df.count()} transactions")
    logger.info(f"✓ Loaded {customers_df.count()} customers")
    
    return transactions_df, customers_df


def transform_transactions(transactions_df):
    """Transform and validate transactions"""
    logger.info("Transforming transactions...")
    
    # Parse timestamp
    transactions_df = transactions_df.withColumn(
        "transaction_date",
        col("timestamp").cast("timestamp")
    )
    
    # Add transaction type based on amount
    transactions_df = transactions_df.withColumn(
        "transaction_type",
        when(col("amount") > 1000, "high_value")
        .when(col("amount") > 100, "medium_value")
        .otherwise("small_value")
    )
    
    # Add year, month, day columns for partitioning
    transactions_df = transactions_df.withColumn("year", expr("year(transaction_date)")) \
        .withColumn("month", expr("month(transaction_date)")) \
        .withColumn("day", expr("day(transaction_date)"))
    
    # Remove duplicates
    transactions_df = transactions_df.dropDuplicates(["transaction_id"])
    
    logger.info(f"✓ Transformed {transactions_df.count()} transactions")
    return transactions_df


def transform_customers(customers_df):
    """Transform and enrich customer data"""
    logger.info("Transforming customers...")
    
    # Clean and standardize names
    customers_df = customers_df.withColumn(
        "customer_name_clean",
        upper(col("customer_name"))
    )
    
    # Extract domain from email
    customers_df = customers_df.withColumn(
        "email_domain",
        split(col("email"), "@").getItem(1)
    )
    
    # Add customer lifecycle stage
    customers_df = customers_df.withColumn(
        "lifecycle_stage",
        when(col("segment") == "VIP", "high_value")
        .when(col("segment") == "Regular", "active")
        .otherwise("at_risk")
    )
    
    logger.info(f"✓ Transformed {customers_df.count()} customers")
    return customers_df


def enrich_data(transactions_df, customers_df):
    """Join transactions with customer data"""
    logger.info("Enriching transaction data with customer info...")
    
    enriched_df = transactions_df.join(
        customers_df.select("customer_id", "customer_name_clean", "email_domain", 
                           "lifecycle_stage", "segment", "country"),
        on="customer_id",
        how="left"
    )
    
    logger.info(f"✓ Enriched {enriched_df.count()} records")
    return enriched_df


def aggregate_by_customer(enriched_df):
    """Calculate customer-level aggregations"""
    logger.info("Aggregating by customer...")
    
    customer_agg = enriched_df.groupBy("customer_id", "customer_name_clean") \
        .agg(
            count("transaction_id").alias("transaction_count"),
            sum("amount").alias("total_spent"),
            avg("amount").alias("avg_transaction_amount"),
            count(when(col("transaction_type") == "high_value", 1)).alias("high_value_count")
        ) \
        .withColumn("customer_lifetime_value", col("total_spent")) \
        .withColumn("is_high_value_customer", 
                   when(col("total_spent") > 5000, "yes").otherwise("no"))
    
    logger.info(f"✓ Created {customer_agg.count()} customer aggregations")
    return customer_agg


def aggregate_by_category(enriched_df):
    """Calculate category-level aggregations"""
    logger.info("Aggregating by category...")
    
    category_agg = enriched_df.groupBy("category") \
        .agg(
            count("transaction_id").alias("transaction_count"),
            sum("amount").alias("total_revenue"),
            avg("amount").alias("avg_price"),
            count(when(col("transaction_type") == "high_value", 1)).alias("premium_transactions")
        )
    
    logger.info(f"✓ Created {category_agg.count()} category aggregations")
    return category_agg


def aggregate_by_country(enriched_df):
    """Calculate country-level aggregations"""
    logger.info("Aggregating by country...")
    
    country_agg = enriched_df.groupBy("country") \
        .agg(
            count("transaction_id").alias("total_transactions"),
            sum("amount").alias("total_revenue"),
            count(when(col("transaction_type") == "high_value", 1)).alias("premium_count"),
            count("customer_id").alias("unique_customers")
        ) \
        .withColumn("avg_transaction_value", col("total_revenue") / col("total_transactions"))
    
    logger.info(f"✓ Created {country_agg.count()} country aggregations")
    return country_agg


def aggregate_by_segment(enriched_df):
    """Calculate customer segment aggregations"""
    logger.info("Aggregating by segment...")
    
    segment_agg = enriched_df.groupBy("segment", "lifecycle_stage") \
        .agg(
            count("customer_id").alias("customer_count"),
            count("transaction_id").alias("transaction_count"),
            sum("amount").alias("segment_revenue"),
            avg("amount").alias("avg_transaction_value")
        )
    
    logger.info(f"✓ Created {segment_agg.count()} segment aggregations")
    return segment_agg


def create_product_analytics(enriched_df):
    """Create product-level analytics with ranking"""
    logger.info("Creating product analytics...")
    
    product_stats = enriched_df.groupBy("product_id", "category") \
        .agg(
            count("transaction_id").alias("units_sold"),
            sum("amount").alias("total_revenue"),
            avg("amount").alias("avg_price")
        )
    
    # Add ranking
    window_spec = Window.partitionBy("category").orderBy(col("total_revenue").desc())
    product_ranked = product_stats.withColumn(
        "revenue_rank",
        row_number().over(window_spec)
    ).withColumn(
        "is_top_product",
        when(col("revenue_rank") <= 5, "yes").otherwise("no")
    )
    
    logger.info(f"✓ Created product analytics for {product_ranked.count()} products")
    return product_ranked


def create_time_series(enriched_df):
    """Create time series aggregations"""
    logger.info("Creating time series data...")
    
    daily_revenue = enriched_df.groupBy("year", "month", "day") \
        .agg(
            count("transaction_id").alias("daily_transactions"),
            sum("amount").alias("daily_revenue"),
            count(when(col("transaction_type") == "high_value", 1)).alias("high_value_transactions")
        ) \
        .orderBy("year", "month", "day")
    
    logger.info(f"✓ Created {daily_revenue.count()} daily revenue records")
    return daily_revenue


def write_output(df, output_path, table_name, mode="overwrite"):
    """Write DataFrame to output location"""
    try:
        df.coalesce(1).write.mode(mode).parquet(f"{output_path}/{table_name}")
        logger.info(f"✓ Written {df.count()} records to {table_name}")
    except Exception as e:
        logger.error(f"Failed to write {table_name}: {e}")


def main():
    """Main ETL pipeline execution"""
    spark = None
    try:
        logger.info("=" * 60)
        logger.info("Starting Complex Spark ETL Pipeline for DataFlint Testing")
        logger.info("=" * 60)
        
        # Initialize DataFlint BEFORE creating SparkSession (critical for live SQL monitoring)
        if init_dataflint:
            try:
                init_dataflint()
                logger.info("✓ DataFlint initialized (Python API)")
            except Exception as e:
                logger.warning(f"DataFlint Python API init failed: {e}. Using JAR approach instead.")
        else:
            logger.info("✓ DataFlint JAR will be used (attached via --jars flag)")
        
        # Initialize Spark
        spark = create_spark_session()
        
        # Define paths
        data_path = "/data"
        output_path = "/data/output"
        
        # Load raw data
        transactions_df, customers_df = load_raw_data(spark, data_path)
        
        # Transform data
        transactions_transformed = transform_transactions(transactions_df)
        customers_transformed = transform_customers(customers_df)
        
        # Enrich data
        enriched_data = enrich_data(transactions_transformed, customers_transformed)
        
        # Create multiple aggregations for complex DAG
        customer_agg = aggregate_by_customer(enriched_data)
        category_agg = aggregate_by_category(enriched_data)
        country_agg = aggregate_by_country(enriched_data)
        segment_agg = aggregate_by_segment(enriched_data)
        product_ranked = create_product_analytics(enriched_data)
        daily_revenue = create_time_series(enriched_data)
        
        # Write outputs
        write_output(enriched_data, output_path, "enriched_transactions")
        write_output(customer_agg, output_path, "customer_aggregations")
        write_output(category_agg, output_path, "category_aggregations")
        write_output(country_agg, output_path, "country_aggregations")
        write_output(segment_agg, output_path, "segment_aggregations")
        write_output(product_ranked, output_path, "product_analytics")
        write_output(daily_revenue, output_path, "daily_revenue")
        
        logger.info("=" * 60)
        logger.info("✓ ETL Pipeline Completed Successfully")
        logger.info("=" * 60)
        logger.info(f"Execution time: {datetime.now()}")
        logger.info("")
        logger.info("🔍 View Spark History and DataFlint UI at:")
        logger.info("   • Spark History Server: http://localhost:18080")
        logger.info("")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            spark.stop()
            logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
