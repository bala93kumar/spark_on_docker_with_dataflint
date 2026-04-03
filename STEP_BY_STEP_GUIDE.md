# 🚀 Step-by-Step Guide: Running Spark ETL & Viewing Results

## Phase 1: Start the Pipeline

### Step 1: Open Terminal in Project Directory

```bash
cd c:\Users\balak\GitProjects\spark_on_docker_with_dataflint
```

### Step 2: Build and Start Containers

```bash
docker-compose up --build
```

**What you'll see:**
```
[+] Building 5.2s
[+] Running 2/2
  ✓ spark-history-server
  ✓ spark-etl-app
Attaching to spark-history-server, spark-etl-app
```

### Step 3: Watch for Completion

Watch for these messages in stdout:

```
spark-etl-app       | ✅ Generated 500 customers and 10,000 transactions
spark-etl-app       | 🚀 Running ETL pipeline with DataFlint monitoring...
spark-etl-app       | ✓ Pipeline completed successfully
spark-etl-app       | ✓ Container exiting.
spark-history-server| (continues running to serve Spark History)
```

**⏱️ Expected Timeline:**
- **0-5 seconds:** Containers starting
- **5-15 seconds:** History Server preparing
- **15-45 seconds:** Spark ETL job running with DataFlint monitoring
- **45 seconds:** ETL job completes, container exits
- **45+ seconds:** Spark History Server processes event logs (ready at 18080)

---

## Phase 2: View Results in Spark History Server

### All results are in ONE place: http://localhost:18080

The **Spark History Server** with **DataFlint JAR embedded** gives you a unified interface for all metrics and visualizations.

### Step 1: Open Spark History Server

1. After job completes (see "✓ Container exiting" in logs)
2. Open browser: **http://localhost:18080**
3. You'll see "Spark History" page with your completed application

### Step 2: Click on Your Application

Look for an application named starting with "DataFlint-ETL-Test". Click it to open the job details.

### Step 3: Explore the Tabs

Inside the job, you'll see multiple tabs:

| Tab | Purpose |
|-----|---------|
| **Jobs** | Overall job summary and timeline |
| **Stages** | All stages with metrics (tasks, shuffle, duration) |
| **DataFlint** ⭐ | **DAG visualization, data quality, performance** |
| **Storage** | Memory and cache usage |
| **Environment** | Spark configuration |
| **Timeline** | Visual Gantt chart of execution |

### Step 4: Click "DataFlint" Tab

This is the main view showing:
- 🎨 **Visual DAG** - Your multi-stage pipeline as a graph
- 📊 **Stage Metrics** - Shuffle bytes, task counts, durations
- 🔍 **Data Quality** - Record counts, completeness %, null analysis
- 📈 **Performance** - Bottleneck identification
- 🔗 **Lineage** - How data flows through transformations

---

## Phase 3: Understanding the Architecture

```
┌──────────────────────────────────────┐
│   Spark ETL Job                      │
│  (with DataFlint 0.8.8 JAR)          │
│                                      │
│  • Generates test data               │
│  • Transforms (6 parallel branches)  │
│  • Outputs to Parquet                │
│  DataFlint monitors everything ✅    │
└────────────┬─────────────────────────┘
             │
             ↓ writes event logs
        /data/spark-events/
   (Parquet + DataFlint metadata)
             │
             ↓ reads & analyzes
┌──────────────────────────────────────┐
│  Spark History Server (port 18080)   │
│        + DataFlint JAR                │
│                                      │
│  Shows:                              │
│  • Jobs tab (overview)               │
│  • Stages tab (performance)          │
│  • DataFlint tab (DAG + quality) ⭐  │
│  • Storage, Environment, Timeline    │
└──────────────────────────────────────┘
         http://localhost:18080
```

**Key Points:**
- DataFlint JAR is embedded in Spark History Server
- All monitoring data persists in event logs
- Spark History Server stays running indefinitely
- ETL container exits cleanly after job completes

---

## Phase 4: What You'll See in DataFlint Tab

### DAG Visualization

Your complete pipeline displayed as a directed graph:

```
Input Data (CSV)
   ↓
[Stage 0: Load]
   ↓
[Stage 1-2: Transform & Clean] 
   ├─ Timestamp conversion
   ├─ Type classification 
   └─ Deduplication
   ↓
[Stage 3: Enrich (Join)]
   ├─ Merge with customer data
   └─ Add customer attributes
   ↓
[Stage 4-9: Parallel Aggregations]
   ├─ Customer Analytics
   ├─ Category Analytics
   ├─ Country Analytics
   ├─ Segment Analytics
   ├─ Product Analytics
   └─ Daily Revenue
   ↓
[Stage 10-16: Output to Parquet]
   ↓
Output Files (Parquet)
```

### Data Quality Metrics

You'll see:
```
Job Summary:
├─ Records Processed: 10,000
├─ Data Completeness: 99.5%
├─ Duplicate Records Removed: 50
└─ Data Quality Score: 99.5%

Shuffle Analysis:
├─ Total Shuffle Read: ~50 MB
├─ Total Shuffle Write: ~100 MB
└─ Most Costly Stage: Parallel Aggregations
```

### Performance Metrics

Per-stage breakdown:
```
Stage Details:
├─ Stage 0: Load (2 tasks, ~2s)
├─ Stage 1-2: Transform (4 tasks, ~5s, 5 MB shuffle)
├─ Stage 3: Enrich/Join (4 tasks, ~8s, 15 MB shuffle)
├─ Stage 4-9: Aggregations (4 tasks each, ~5s, 8 MB shuffle)
└─ Stage 10-16: Output (4 tasks, ~3s)

Total Duration: ~45 seconds
```

---

## Phase 5: Container Management

### Check Container Status

```bash
docker-compose ps
```

Output:
```
NAME                  STATUS
spark-history-server  Up (running)
spark-etl-app         Exited (0)
```

The ETL app exits after the job completes. History Server continues running to serve the UI.

### View Logs

```bash
# View ETL job output
docker-compose logs spark-etl-app

# View History Server logs
docker-compose logs spark-history-server
```

### Inspect Output Files

```bash
# List all generated data
docker exec spark-etl-app ls -la /data/

# List Parquet output files
docker exec spark-etl-app ls -la /data/output/

# List event logs
docker exec spark-etl-app ls -la /data/spark-events/
```

### Copy Output Files to Your Machine

```bash
# Copy all output data
docker cp spark-etl-app:/data/output ./local-output

# Copy event logs
docker cp spark-etl-app:/data/spark-events ./local-spark-events
```

---

## Phase 6: Troubleshooting

### No applications showing at http://localhost:18080
- **Reason:** History Server still processing logs
- **Solution:** Wait another 10-15 seconds, refresh page
- **Check:** `docker-compose logs spark-history-server`

### Can't reach http://localhost:18080
- **Reason:** History Server may not be ready
- **Solution:** Wait 30 seconds and retry
- **Check:** `docker-compose logs spark-history-server | grep Started`

### No DataFlint tab visible in History Server
- **Reason:** JAR file didn't load properly
- **Solution:** Check history server logs for errors
- **Manual check:** `docker exec spark-history-server ls -la /opt/spark/jars/`

### ETL job failed
- **Check logs:** `docker-compose logs spark-etl-app`
- **Restart:** `docker-compose down && docker-compose up --build`

---

## Phase 7: File Locations
