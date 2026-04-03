# Quick Reference Guide

## 🚀 Start Here

### Windows Users
```powershell
# Navigate to project directory
cd c:\Users\balak\GitProjects\spark_on_docker_with_dataflint

# Run quick start (double-click or run in PowerShell)
.\quickstart.bat

# Or use Docker commands directly
docker-compose up --build
```

### Mac/Linux Users
```bash
# Navigate to project directory
cd spark_on_docker_with_dataflint

# Make script executable
chmod +x quickstart.sh

# Run quick start
./quickstart.sh

# Or use Docker commands directly
docker-compose up --build
```

## 📍 What's in This Project

```
spark_on_docker_with_dataflint/
│
├── app/
│   ├── spark_etl_app.py          ← Main ETL Pipeline (500 lines, 16 stages)
│   └── generate_data.py           ← Data generator (500 customers, 10K transactions)
│
├── config/
│   └── dataflint_ui_server.py     ← DataFlint UI Server (Flask)
│
├── Dockerfile                     ← Spark application container
├── Dockerfile.dataflint           ← DataFlint UI container
├── docker-compose.yml             ← Orchestration (start both services)
│
├── README.md                      ← Full documentation
├── UNDERSTANDING_DAG.md           ← Complex DAG explanation
├── DATAFLINT_GUIDE.md            ← DataFlint features & benefits
├── QUICK_REFERENCE.md            ← This file
│
├── requirements.txt               ← Python dependencies (pip)
├── requirements.txt               ← All dependencies
│
├── .gitignore                     ← Git ignore patterns
├── .dockerignore                  ← Docker ignore patterns
│
├── quickstart.sh                  ← Linux/Mac quick start
└── quickstart.bat                 ← Windows quick start
```

## 🎯 What This Does

### The ETL Pipeline
1. **Loads** 10,000 transactions + 500 customers from CSV
2. **Transforms** data (cleaning, type conversion, deduplication)
3. **Enriches** by joining transactions with customer info
4. **Aggregates** in 6 parallel stages:
   - Customer-level metrics
   - Category analytics
   - Country/geographic analysis
   - Customer segment statistics
   - Product rankings
   - Daily revenue trends
5. **Outputs** 7 Parquet files with rich analytics

### Complex DAG Features
- ✓ 16 execution stages
- ✓ 6 parallel aggregations
- ✓ Multiple join operations
- ✓ Window functions (ROW_NUMBER, DENSE_RANK)
- ✓ 45MB+ shuffle operations
- ✓ ~30 second execution time

## 🌐 Access Points

Once running (docker-compose up --build):

```
DataFlint UI          http://localhost:5000
  ├─ Dashboard        Shows job status, metrics, DAG
  ├─ API Stats        http://localhost:5000/api/stats
  └─ Health Check     http://localhost:5000/health

Spark UI              http://localhost:4040
  ├─ Jobs             Running and completed jobs
  ├─ Stages           Execution stages and timing
  ├─ DAG              Visual execution plan
  └─ Executors        Resource usage

Spark Master          http://localhost:8080
  └─ Applications     Running/completed apps
```

## 📊 Sample Output

After running, check output:
```bash
# List output files
docker exec spark-etl-app ls -lh /data/output/

# View record counts (in container)
docker exec spark-etl-app python3 -c "
import os
for f in os.listdir('/data/output'):
    path = f'/data/output/{f}'
    if os.path.isdir(path):
        files = os.listdir(path)
        print(f'{f}: {len(files)} partitions')
"
```

**Expected Output**:
```
customer_aggregations: 1 partitions
category_aggregations: 1 partitions
country_aggregations: 1 partitions
segment_aggregations: 1 partitions
enriched_transactions: 1 partitions
product_analytics: 1 partitions
daily_revenue: 1 partitions
```

## 🔍 Monitoring the Job

### Real-Time Logs
```bash
# Follow logs as job runs
docker logs -f spark-etl-app

# Look for these indicators:
# ✓ "Loading raw data"
# ✓ "Transforming transactions"
# ✓ "Enriching transaction data"
# ✓ "Aggregating by"
# ✓ "Written"
# ✓ "ETL Pipeline Completed Successfully"
```

### Check Data Quality
```bash
# View sample customer data
docker exec spark-etl-app head -5 /data/customers.csv

# View sample transaction data
docker exec spark-etl-app head -5 /data/transactions.csv

# Count records in output
docker exec spark-etl-app python3 << 'EOF'
import pandas as pd
for table in ['enriched_transactions', 'customer_aggregations', 'category_aggregations']:
    try:
        df = pd.read_parquet(f'/data/output/{table}')
        print(f"{table}: {len(df)} records")
    except: pass
EOF
```

## 🛠️ Common Commands

### Start Services
```bash
# Build and start
docker-compose up --build

# Start without rebuild
docker-compose up -d

# Start specific service
docker-compose up spark-etl
```

### Stop Services
```bash
# Stop all (keep data)
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### View Logs
```bash
# Spark ETL logs
docker logs spark-etl-app

# DataFlint UI logs
docker logs dataflint-ui-server

# Follow in real-time
docker logs -f spark-etl-app

# Get last 100 lines
docker logs --tail 100 spark-etl-app
```

### Execute Commands in Container
```bash
# Run Python script
docker exec spark-etl-app python3 /app/generate_data.py

# Check file system
docker exec spark-etl-app ls -la /data/

# View output folder
docker exec spark-etl-app ls -lh /data/output/

# Run Spark command
docker exec spark-etl-app spark-submit --version
```

## 🧪 Testing & Verification

### Verify Services are Running
```bash
curl http://localhost:5000/health   # DataFlint health
curl http://localhost:5000/api/stats # Get stats

docker ps  # List running containers
```

### Check Container Resources
```bash
# CPU and memory usage
docker stats

# Inspect a container
docker inspect spark-etl-app
```

### Verify Output Files
```bash
# Inside container
docker exec spark-etl-app \
  find /data/output -name "*.parquet" -exec ls -lh {} \;

# Check Parquet schema
docker exec spark-etl-app python3 -c "
import pandas as pd
df = pd.read_parquet('/data/output/enriched_transactions')
print(df.dtypes)
"
```

## 💡 Tips & Tricks

### Tip 1: Adjust Resources
```yaml
# In docker-compose.yml, increase Spark memory:
environment:
  - SPARK_DRIVER_MEMORY=4g    # was 2g
  - SPARK_EXECUTOR_MEMORY=4g  # was 2g
```

### Tip 2: Customize Data Volume
```python
# In app/generate_data.py:
NUM_CUSTOMERS = 1000        # was 500
NUM_TRANSACTIONS = 50000    # was 10000
```

### Tip 3: Run Locally Without Docker
```bash
# Install dependencies
pip install -r requirements.txt

# Generate data
python3 app/generate_data.py

# Run ETL
python3 app/spark_etl_app.py
```

### Tip 4: Extend the DAG
Add more aggregations to app/spark_etl_app.py:
```python
def aggregate_by_email_domain(enriched_df):
    return enriched_df.groupBy("email_domain").agg(
        count("transaction_id").alias("domain_transactions"),
        sum("amount").alias("domain_revenue")
    )

# Then call it and write output
email_agg = aggregate_by_email_domain(enriched_data)
write_output(email_agg, output_path, "email_domain_aggregations")
```

## 🐛 Troubleshooting

### Issue: Port Already in Use
```bash
# Find what's using port 5000
lsof -i :5000                  # Mac/Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess  # Windows

# Change ports in docker-compose.yml
ports:
  - "6000:5000"  # Use 6000 instead of 5000
```

### Issue: Out of Memory
```bash
# Increase Docker memory limit
docker update --memory 4g spark-etl-app

# Or reduce data volume in generate_data.py
NUM_CUSTOMERS = 100        # was 500
NUM_TRANSACTIONS = 1000    # was 10000
```

### Issue: Container Won't Start
```bash
# Check logs for errors
docker logs spark-etl-app

# Try rebuilding
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Issue: No DataFlint UI
```bash
# Check if UI container is running
docker ps | grep dataflint

# Restart the UI service
docker-compose restart dataflint-ui

# Check UI logs
docker logs dataflint-ui-server
```

## 📚 Documentation Files

**Start with these in order:**

1. **This file (QUICK_REFERENCE.md)** ← You are here
   - Quick commands and tips
   
2. **README.md**
   - Full project documentation
   - Architecture overview
   - Detailed setup instructions
   
3. **UNDERSTANDING_DAG.md**
   - What is a DAG?
   - Why this DAG is complex
   - How to read the DAG in Spark UI
   - DAG optimization insights
   
4. **DATAFLINT_GUIDE.md**
   - What DataFlint does
   - Key features and benefits
   - Metrics explained
   - How to use DataFlint effectively

## 🎓 Learning Path

```
1. Run the Application
   ↓
2. Check DataFlint UI (http://localhost:5000)
   ↓
3. View Spark DAG (http://localhost:4040)
   ↓
4. Examine Output Data (check /data/output/)
   ↓
5. Read UNDERSTANDING_DAG.md
   ↓
6. Read DATAFLINT_GUIDE.md
   ↓
7. Understand the pipeline code (spark_etl_app.py)
   ↓
8. Experiment - modify and re-run
```

## 🤔 FAQ

**Q: How long does it take to run?**
A: ~30-45 seconds for the complete pipeline

**Q: Can I inspect the output data?**
A: Yes! Output is in Parquet format in /data/output/

**Q: What if ports are already in use?**
A: Modify docker-compose.yml to use different ports

**Q: Can I make the DAG more complex?**
A: Yes! Add more aggregations or transformations to spark_etl_app.py

**Q: How much disk space does it need?**
A: ~500MB for Docker images + ~1GB for data and outputs

**Q: Can I run this on Windows?**
A: Yes! With Docker for Windows. Use quickstart.bat

**Q: What version of Spark?**
A: Spark 3.4.1 with Python 3.9

---

**Need more help?** Check the relevant markdown file or run:
```bash
docker logs spark-etl-app -f
```
