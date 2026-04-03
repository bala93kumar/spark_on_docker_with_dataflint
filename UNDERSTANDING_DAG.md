# Understanding the Complex DAG and DataFlint

## What is a DAG?

A **DAG (Directed Acyclic Graph)** is Spark's execution plan that shows:
- All transformation and action operations
- Data dependencies between operations
- Order of execution
- Parallelization opportunities

## Our Complex DAG Structure

```
                          ┌─ Load customers.csv
                          │
Start → CSV Files ────────┼─ Load transactions.csv
                          │
                          └─ Parse & Validate
                          
                          ┌─ Transform Transactions
                          │  (parse timestamp, add categories)
                          │
Transformations ──────────┼─ Transform Customers
                          │  (clean names, extract domain)
                          │
                          └─ Enrich Data
                          |  (join customers + transactions)
                          
                          ┌─ Aggregate by Customer (500 records)
                          │
                          ├─ Aggregate by Category (10 records)
                          │
Parallel ─────────────────┼─ Aggregate by Country (10 records)
Aggregations              │
                          ├─ Aggregate by Segment (12 records)
                          │
                          ├─ Product Analytics (100 ranked products)
                          │
                          └─ Time Series (365 daily records)
                          
                          ┌─ Write enriched_transactions.parquet
                          │
                          ├─ Write customer_aggregations.parquet
                          │
Write Outputs ────────────┼─ Write category_aggregations.parquet
                          │
                          ├─ Write country_aggregations.parquet
                          │
                          ├─ Write segment_aggregations.parquet
                          │
                          ├─ Write product_analytics.parquet
                          │
                          └─ Write daily_revenue.parquet
                          
                          ↓
                          ✓ Pipeline Complete
```

## Why This DAG is Complex

### 1. **Multiple Branches**
- 6 independent aggregation operations run in parallel
- Spark optimizes which tasks to execute concurrently
- Maximum parallelism = more throughput

### 2. **Deep Dependency Chain**
- Data must flow: Load → Transform → Enrich → Aggregate → Write
- Each stage depends on previous completion
- Window functions add complexity

### 3. **Multiple Output Paths**
- 7 different output files from single enriched dataset
- Spark tracks which output comes from which transformation
- Demonstrates data lineage

### 4. **Computational Complexity**
- Window functions (ROW_NUMBER, DENSE_RANK)
- Multiple aggregation types (SUM, AVG, COUNT)
- Broadcast joins for efficiency
- Deduplication operations

## Visualizing the DAG in Spark UI

When the job runs, you can see the DAG in two places:

### 1. **Spark Master UI** (http://localhost:8080)
Shows:
- Running applications
- Completed stages
- Executor details

### 2. **Spark Application UI** (http://localhost:4040)
Shows:
- DAG visualization (pipeline diagram)
- Stage details (tasks, duration, data size)
- Task execution timeline
- Shuffle operations
- Memory usage per stage

### What to Look For

```
Stage 0: Read CSV
├─ Parallelism: 1
└─ Shuffle: None

Stage 1: Transform Transactions
├─ Parallelism: 4
└─ Shuffle: None

Stage 2: Transform Customers
├─ Parallelism: 4
└─ Shuffle: None

Stage 3: Join Enrichment
├─ Parallelism: 4
├─ Shuffle: Yes (broadcast join)
└─ Data: ~50MB → Exchange → 50MB

Stage 4-9: Parallel Aggregations
├─ Parallelism: 4
├─ Shuffle: Yes (group by shuffle)
└─ Data: ~50MB → Exchange → ~1-10MB each

Stage 10-16: Write Outputs
├─ Parallelism: 1
├─ Shuffle: None
└─ Format: Parquet
```

## DataFlint's Role

DataFlint enhances DAG visibility by:

### 1. **Enhanced Visualization**
```
Standard Spark UI        ↓ DataFlint ↓         DataFlint UI
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Basic DAG Graph  │─→ │ Data Quality     │─→ │ Rich Dashboard   │
│ Stage Details    │   │ Metrics          │   │ Historical Trends│
│ Task Metrics     │   │ Lineage Tracking │   │ Alert System     │
└──────────────────┘   └──────────────────┘   └──────────────────┘
```

### 2. **Data Quality Metrics**
- Record counts per stage
- NULL value detection
- Duplicate detection
- Data type validation
- Freshness monitoring

### 3. **Performance Metrics**
- Stage execution time
- Shuffle operations analysis
- Memory utilization
- CPU efficiency
- I/O patterns

### 4. **Lineage Tracking**
Track data from source to destination:
```
customers.csv
    ↓
Transform ← (column add, type conversion)
    ↓
Enrich ← (join with transactions)
    ↓
├─→ Customer Agg (5 fields transformed)
├─→ Category Agg (4 fields transformed)
├─→ Country Agg (5 fields transformed)
├─→ Segment Agg (4 fields transformed)
├─→ Product Analytics (5 fields transformed)
└─→ Daily Revenue (3 fields transformed)
    ↓
Parquet Output (7 datasets)
```

## How to Interpret the DAG

### Reading Time: Timeline at bottom shows:
- Vertical lines = stages executing sequentially
- Horizontal width = stage duration
- Gaps = wait times between stages

### Memory Shuffle: Indicates
- Repartitioning operations
- Data movement between executors
- Network I/O

### Parallelism: Shows
- How many tasks run in parallel
- Our setup uses 4 cores (configurable in docker-compose.yml)

## Complex DAG Benefits

1. **Realistic Testing**
   - Tests DataFlint with real-world complexity
   - Shows handling of 6+ parallel branches
   - Demonstrates deep execution chains

2. **Performance Optimization Learning**
   - Identifies bottleneck stages
   - Shows shuffle overhead
   - Demonstrates Spark's optimization (AQE)

3. **Data Quality Understanding**
   - Multiple aggregations = multiple quality checks
   - Different aggregation types = different failure modes
   - Rich lineage = understand impact of issues

## Key Metrics to Monitor

### In DataFlint Dashboard:

1. **Throughput**
   ```
   Records processed per second
   = Total records / Total time
   = 10,000 records / Time
   ```

2. **Data Quality Score**
   ```
   = (Valid records / Total records) × 100
   Good target: > 99%
   ```

3. **Stage Performance**
   ```
   Slow stages = High shuffle data
   Fast stages = Efficient transformations
   ```

4. **Aggregation Accuracy**
   ```
   Sum(all agg outputs) vs Expected
   Detects data loss/duplication
   ```

## Customization Ideas

### Make DAG Even More Complex:

```python
# Add window functions
from pyspark.sql.window import Window
window = Window.partitionBy("customer_id").orderBy("transaction_date")
df.withColumn("running_total", sum("amount").over(window))

# Add complex calculations
df.withColumn("percentile_90", percentile_approx("amount", 0.9).over(window))

# Add multiple joins
df.join(table1, ...).join(table2, ...).join(table3, ...)

# Add conditional aggregations
.agg(
    sum(when(cond1, amount)),
    sum(when(cond2, amount)),
    sum(when(cond3, amount))
)
```

## References

- [Spark DAG Documentation](https://spark.apache.org/docs/latest/rdd-programming-guide.html#understanding-closures)
- [Spark SQL Optimization](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [DataFlint Documentation](https://github.com/dataflint/dataflint)
