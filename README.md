# Spark & DataFlint ETL Application

A complex Spark ETL pipeline designed to demonstrate DataFlint's capabilities for DAG visualization and data quality monitoring.

## 📋 Project Overview

This project demonstrates:
- **Complex ETL Pipeline**: Multi-stage data transformations with parallel aggregations
- **Large Dataset Processing**: 10,000+ transactions across 500+ customers
- **Rich DAG Structure**: 7+ parallel aggregation stages for complex visualization
- **DataFlint Integration**: Monitor data quality and performance metrics
- **Docker Containerization**: Easy deployment and reproducibility

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Docker Compose Setup                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │   Spark ETL App      │      │   DataFlint UI       │    │
│  │  (spark-etl)         │─────→│  (dataflint-ui)      │    │
│  │                      │      │                      │    │
│  │ • Load Data          │      │ • Monitoring        │    │
│  │ • Transform          │      │ • DAG Visualization │    │
│  │ • Enrich             │      │ • Performance Stats  │    │
│  │ • Aggregate (7x)     │      │ • Web UI (port 5000)│    │
│  │ • Output Parquet     │      │                      │    │
│  │                      │      │                      │    │
│  │ Ports: 4040, 7077    │      │ Ports: 5000, 5001   │    │
│  └──────────────────────┘      └──────────────────────┘    │
│          ↓                              ↓                    │
│     /data (volume)           /data (shared volume)          │
└─────────────────────────────────────────────────────────────┘
```

## 📊 ETL Pipeline Stages

### Data Flow

```
Raw Data (CSV)
    ↓
┌─────────────────────────┐
│  1. Load raw data       │
│     - Customers         │
│     - Transactions      │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│  2. Transform           │
│     - Parse timestamps  │
│     - Add categories    │
│     - Clean names       │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│  3. Enrich              │
│     - Join with customer│
│     - Add customer info │
└─────────────────────────┘
    ↓
    ├─→ 4. Customer Aggregations
    ├─→ 5. Category Aggregations
    ├─→ 6. Country Aggregations
    ├─→ 7. Segment Aggregations
    ├─→ 8. Product Analytics
    └─→ 9. Time Series Data
    ↓
Output (Parquet Format)
```

## 🚀 Quick Start

### Prerequisites

- Docker (v20.10+)
- Docker Compose (v1.29+)
- At least 4GB RAM available
- Disk space: 2GB for data and outputs

### Installation & Execution

#### Option 1: Using Docker Compose (Recommended)

```bash
# Clone or navigate to the project
cd spark_on_docker_with_dataflint

# Build and start all services
docker-compose up --build

# In another terminal, check logs
docker logs spark-etl-app -f

# Access DataFlint UI
# Open in your browser: http://localhost:5000
```

#### Option 2: Build and Run Separately

```bash
# Build Spark ETL image
docker build -t spark-etl:latest .

# Build DataFlint UI image
docker build -f Dockerfile.dataflint -t dataflint-ui:latest .

# Run Spark ETL
docker run --name spark-etl \
  -v $(pwd)/data:/data \
  -p 4040:4040 \
  spark-etl:latest

# Run DataFlint UI (in another terminal)
docker run --name dataflint-ui \
  -v $(pwd)/data:/data \
  -p 5000:5000 \
  dataflint-ui:latest
```

#### Option 3: Run Locally (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Generate data
python3 app/generate_data.py

# Run ETL pipeline
python3 app/spark_etl_app.py
```

## 🎯 Understanding the Complex DAG

The pipeline creates a complex DAG by:

1. **Parallel Aggregations**: 6 independent aggregation stages running simultaneously
   - Customer-level: 500+ customer statistics
   - Category-level: 10+ category analytics
   - Country-level: 10+ country metrics
   - Segment-level: 3x4 segment combinations
   - Product-level: 100+ products with ranking
   - Time-series: 365+ daily aggregations

2. **Multiple Transformations**: Each stage includes filtering, grouping, and calculations

3. **Window Functions**: Rankings and row_number operations create additional complexity

4. **Broadcast Operations**: Large tables broadcast to workers

## 📊 DataFlint Features

### What DataFlint Helps With:

1. **DAG Visualization**: See the complete execution plan
2. **Data Quality Metrics**: Track transformations and data completeness
3. **Performance Monitoring**: Identify bottlenecks in your pipeline
4. **Lineage Tracking**: Understand data dependencies
5. **Anomaly Detection**: Catch data quality issues early

### Accessing DataFlint

```
Web UI:        http://localhost:5000
Spark UI:      http://localhost:4040
Health Check:  http://localhost:5000/health
API Endpoint:  http://localhost:5000/api/stats
```

## 📁 Project Structure

```
spark_on_docker_with_dataflint/
├── app/
│   ├── spark_etl_app.py           # Main Spark ETL pipeline
│   └── generate_data.py            # Data generation script
├── config/
│   └── dataflint_ui_server.py      # DataFlint UI server
├── data/
│   ├── customers.csv               # Generated customer data
│   ├── transactions.csv            # Generated transaction data
│   ├── output/                     # Pipeline outputs (Parquet)
│   └── logs/                       # Job logs
├── Dockerfile                      # Spark ETL container
├── Dockerfile.dataflint            # DataFlint UI container
├── docker-compose.yml              # Orchestration config
├── requirements.txt                # Production dependencies
├── requirements.txt                # All dependencies
├── .dockerignore                   # Docker build exclusions
└── README.md                       # This file
```

## 🔍 Monitoring & Debugging

### View Logs

```bash
# Spark ETL logs
docker logs spark-etl-app

# DataFlint UI logs
docker logs dataflint-ui-server

# Follow logs in real-time
docker logs -f spark-etl-app
```

### Check Output Data

```bash
# List output files
docker exec spark-etl-app ls -lah /data/output/

# Check record counts (Parquet)
docker exec spark-etl-app python3 -c "
import pandas as pd
for f in ['enriched_transactions', 'customer_aggregations', 'category_aggregations']:
    df = pd.read_parquet(f'/data/output/{f}')
    print(f'{f}: {len(df)} records')
"

# View sample data
docker exec spark-etl-app head /data/customers.csv
docker exec spark-etl-app head /data/transactions.csv
```

### Check Spark UI

While the job is running:
```bash
# Access Spark Master UI
http://localhost:8080

# Access Spark Application UI
http://localhost:4040
```

## 🧪 Dataset Information

### Generated Data

- **Customers**: 500 records
  - Fields: ID, Name, Email, Country, Segment
  - Segments: VIP, Regular, New
  
- **Transactions**: 10,000 records
  - Fields: ID, Customer ID, Product ID, Category, Amount, Timestamp
  - Categories: Electronics, Fashion, Home, Sports, Books, Beauty, Toys, Food, Automotive, Health
  - Amount Range: $10 - $5,000
  - Date Range: Last 365 days

### Output Files (Parquet Format)

1. **enriched_transactions.parquet** - All transactions with customer info
2. **customer_aggregations.parquet** - Customer-level metrics
3. **category_aggregations.parquet** - Category revenue and stats
4. **country_aggregations.parquet** - Geographic analysis
5. **segment_aggregations.parquet** - Customer segment metrics
6. **product_analytics.parquet** - Product rankings and revenue
7. **daily_revenue.parquet** - Time-series daily aggregations

## 🛠️ Customization

### Adjust Data Volume

Edit `app/generate_data.py`:
```python
NUM_CUSTOMERS = 500    # Change customer count
NUM_TRANSACTIONS = 10000  # Change transaction count
```

### Modify ETL Logic

Edit `app/spark_etl_app.py`:
- Add new transformation functions
- Modify aggregation logic
- Add custom metrics

### Change Spark Configuration

Edit `docker-compose.yml` or `Dockerfile`:
```bash
SPARK_DRIVER_MEMORY=2g  # Increase as needed
SPARK_EXECUTOR_MEMORY=2g  # Increase as needed
```

## 📈 Performance Tips

1. **Increase Partitions**: For larger datasets, adjust in `create_spark_session()`
2. **Enable AQE**: Adaptive Query Execution is already enabled
3. **Use Caching**: Add `.cache()` for reused DataFrames
4. **Broadcast Small Tables**: For dimension tables < 1GB

## 🐛 Troubleshooting

### Container won't start
```bash
# Check for port conflicts
docker ps
lsof -i :5000  # Check port 5000
lsof -i :4040  # Check port 4040
```

### Out of memory errors
```bash
# Increase Docker memory allocation
docker update --memory 4g spark-etl-app
docker update --memory 2g dataflint-ui-server
```

### Data not generated
```bash
# Run data generation separately
docker exec spark-etl-app python3 /app/generate_data.py
```

### Check container health
```bash
docker ps --filter "name=spark"
docker inspect spark-etl-app
```

## 📚 Learning Resources

### DataFlint Documentation
- Official Docs: https://dataflint.io
- GitHub: https://github.com/dataflint/dataflint

### Spark Documentation
- Spark SQL: https://spark.apache.org/docs/latest/sql-programming-guide.html
- Spark Performance: https://spark.apache.org/docs/latest/tuning.html

## 🎓 Key Concepts Demonstrated

1. **Data Transformation**: Multiple transformation stages
2. **Window Functions**: Ranking products by revenue
3. **Complex Joins**: Enrichment with customer data
4. **Parallel Processing**: Multiple aggregations simultaneously
5. **Data Quality**: Deduplication and validation
6. **Scalability**: Handles large datasets efficiently

## 📝 License

This project is provided as-is for educational and testing purposes.

## 🤝 Contributing

Feel free to extend this project:
- Add more complex transformations
- Implement additional data quality checks
- Create custom monitoring dashboards
- Add machine learning pipelines

## 📧 Support

For issues or questions:
1. Check logs: `docker logs spark-etl-app`
2. Review DataFlint documentation
3. Check Spark logs in `/data/logs/`

---

**Last Updated**: 2024  
**Spark Version**: 3.4.1  
**DataFlint Version**: 0.3.2  
**Python**: 3.9
