# 🚀 Step-by-Step Guide: Starting Containers & Accessing DataFlint UI

## Phase 1: Start the Containers

### Step 1: Open Terminal in Project Directory

```bash
cd c:\Users\balak\GitProjects\spark_on_docker_with_dataflint
```

### Step 2: Build and Start All Containers

```bash
docker-compose up --build
```

**What you'll see:**
```
[+] Building 5.2s
[+] Running 2/2
  ✓ spark-history
  ✓ spark-etl-app
Attaching to spark-history-server, spark-etl-app
```

### Step 3: Wait for Startup Messages

Watch for these key messages:

```
spark-history-server | 📥 Downloading DataFlint plugin...
spark-history-server | ✓ DataFlint plugin downloaded
spark-history-server | 🚀 Starting Spark History Server (port 18080)...

spark-etl-app   | ✅ Generated 500 customers and 10,000 transactions
spark-etl-app   | 🚀 Running ETL pipeline with DataFlint monitoring...
spark-etl-app   | ✓ Pipeline completed successfully
spark-etl-app   | 📊 View results in DataFlint:
spark-etl-app   | • Spark History Server: http://localhost:18080
```

**⏱️ Expected Timeline:**
- **0-5 seconds:** Containers starting
- **5-15 seconds:** History Server downloading DataFlint JAR (0.8.8)
- **15-45 seconds:** Spark job running with DataFlint monitoring
- **45-50 seconds:** Job completes, event logs written to disk
- **50+ seconds:** History Server processes event logs and becomes fully ready

---

## Phase 2: Access the Four UIs

### UI #1: DataFlint UI (Dashboard & Current Metrics)

**Purpose:** See latest job run metrics, data quality, and real-time DAG

**Access:**
1. Open browser: http://localhost:5000
2. You'll see a dashboard with:
   - 🟢 Latest Job Run metrics (at top)
   - 📊 Quick stats cards:
     - Records Processed
     - Duration
     - Stages Completed
     - Data Quality Score
   - 📈 Job History table (scroll down)
   - 🔗 Quick links to other UIs

**What to Explore:**
- **Metrics Cards:** Click each card to see details
- **Latest Run Section:** Shows:
  - Job duration (typically 30-45 seconds)
  - Total records: ~10,000
  - Data completeness: 99.5%
  - Duplicate records: ~50
- **Job History Table:** Shows all previous runs with timestamps
- **Stage Metrics:** Click `/api/runs/latest/stages` to see each stage's metrics

**Example JSON Response** (if you click the stage metrics link):
```json
{
  "latest_run": {
    "run_id": 1,
    "start_time": "2025-04-02 10:30:45",
    "duration_seconds": 38,
    "total_records": 10000,
    "completeness_percent": 99.5,
    "duplicate_count": 50
  },
  "stage_metrics": [
    {"stage_id": 0, "name": "Load", "tasks": 2, "shuffle_bytes": 0},
    {"stage_id": 1, "name": "Transform", "tasks": 4, "shuffle_bytes": 50000000},
    ...
  ]
}
```

---

## Phase 2: Access the DataFlint UI

**Everything is in ONE place:** http://localhost:18080

This is the **Spark History Server** with **DataFlint JAR embedded** - giving you a unified interface.

### Step 1: Open the History Server

1. Wait for job to complete (see "Pipeline completed successfully" in logs)
2. Open browser: **http://localhost:18080**
3. You'll see "Spark History" page with completed applications

### Step 2: Click on Your Spark Application

You'll see a completed job listed. Click on it to open the job details page.

### Step 3: Explore the Tabs

Once inside the job, you'll see multiple tabs at the top:

| Tab | Contains |
|-----|----------|
| **Jobs** | Overall job summary, timeline |
| **Stages** | All 16 stages with metrics (tasks, shuffle, duration) |
| **DataFlint** ⭐ | **DAG visualization, data quality, performance analysis** |
| **Storage** | Memory and cache usage |
| **Environment** | Spark configuration |
| **Timeline** | Visual Gantt chart of stage execution |

### Step 4: Click the "DataFlint" Tab

This is where you see the **DataFlint UI** integrated directly into Spark History Server.

You'll see:
- 🎨 **Visual DAG** - Your 16-stage pipeline visualized as a graph
- 📊 **Stage Metrics** - Shuffle bytes, task counts, durations per stage
- 🔍 **Data Quality** - Completeness %, null counts, distributions
- 📈 **Performance Analysis** - Bottleneck identification
- 🔗 **Data Lineage** - How data flows through transformations

---

## Phase 3: Understand the Architecture

```
┌──────────────────────────────────────┐
│   Your Spark ETL Job                 │
│  (with DataFlint 0.8.8 plugin)       │
│                                      │
│  • Loads data                        │
│  • Transforms (16 stages)            │
│  • Outputs to Parquet                │
│  DataFlint monitors everything ✅    │
└────────────┬─────────────────────────┘
             │
             ↓ writes
        /data/spark-events/
   (event logs with DataFlint metadata)
             │
             ↓ reads
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

**Key Point:** No separate services needed anymore. DataFlint UI is **built into** the Spark History Server.

---

## Phase 4: What You'll See in DataFlint Tab

### DAG Visualization
```
Your pipeline visualized as a graph:

CSV Input
   ↓
[Stage 0: Load]
   ↓
[Stage 1-2: Transform] ← cleaned data
   ↓
[Stage 3-8: Parallel Aggregations] ← 6 branches
   ├─ Customer Analytics
   ├─ Category Analytics
   ├─ Country Analytics
   ├─ Segment Analytics
   ├─ Product Analytics
   └─ Daily Revenue
   ↓
[Stage 9-16: Output to Parquet]
   ↓
Parquet Files
```

### Data Quality Metrics
```
Job Summary:
├─ Records Processed: 10,000
├─ Data Completeness: 99.5%
├─ Null Count: 50
├─ Duplicate Records: 50
└─ Data Quality Score: 99.5%

Shuffle Analysis:
├─ Total Shuffle Read: 50 MB
├─ Total Shuffle Write: 100 MB
└─ Most Expensive Stage: Stage 5 (25s)
```

### Performance Metrics
```
Stage Details:
├─ Stage 0: Load (2 tasks, 2s, 0 MB shuffle)
├─ Stage 1: Transform Timestamps (4 tasks, 3s, 5 MB shuffle)
├─ Stage 2: Deduplicate (4 tasks, 2s, 5 MB shuffle)
├─ Stage 3: Customer Agg (4 tasks, 5s, 8 MB shuffle)
├─ Stage 4: Category Agg (4 tasks, 5s, 8 MB shuffle)
├─ Stage 5: Country Agg (4 tasks, 5s, 8 MB shuffle)
├─ Stage 6: Segment Agg (4 tasks, 5s, 8 MB shuffle)
├─ Stage 7: Product Agg (4 tasks, 5s, 8 MB shuffle)
├─ Stage 8: Time Series Agg (4 tasks, 5s, 8 MB shuffle)
└─ Stage 9-16: Output (4 tasks, 3s, 0 MB shuffle)
```

- 📊 **Tasks:** Individual task progress bars
- 💾 **Executors:** Memory and CPU usage
- 🔗 **Environment:** Spark configuration

**Note:** Once job completes and container keeps running, Spark UI won't be available, but Spark History Server will have all the data.

---

### UI #4: DataFlint History UI (Job Run History with Metrics)

**Purpose:** View historical metrics, compare runs, track data quality over time

**Access:**
1. Go to http://localhost:5000
2. Scroll down to **"Job Run History"** table
3. Click on any row to see details

**What You'll See:**

```
Job Run History
─────────────────────────────────────────────────────────────────
Run ID | Timestamp           | Duration | Records  | Completeness
─────────────────────────────────────────────────────────────────
7      | 2025-04-02 10:50:15 | 38s      | 10,000   | 99.5%
6      | 2025-04-02 10:45:22 | 36s      | 10,000   | 99.5%
5      | 2025-04-02 10:40:10 | 40s      | 10,000   | 99.5%
4      | 2025-04-02 10:35:05 | 37s      | 10,000   | 99.5%
```

**Database Queries:** The UI queries `/data/metrics.db` with 3 tables:
- **runs:** Job execution summary (timestamps, duration, record counts)
- **stage_metrics:** Performance per stage (tasks, shuffle bytes)
- **data_quality:** Data completeness and duplicate counts

---

## Phase 5: Recommended Timeline

### Time: 0-5 seconds
```
docker-compose up --build
```

### Time: 5-15 seconds
```
Services starting, DataFlint JAR downloading from Maven...
```

### Time: 15-45 seconds
```
Spark job running!
If you want to see live Spark UI, open: http://localhost:4040
(but it disappears after job completes)
```

### Time: 45-50 seconds (JOB COMPLETED!)
```
Event logs written to /data/spark-events/
History Server processing the logs...
```

### Time: 50-60 seconds
```
READY! Open http://localhost:18080 in your browser
Click on your application → Explore tabs → Go to DataFlint tab ⭐
```

---

## Phase 6: Container Inspection Commands

### Check if containers are running
```bash
docker-compose ps
```

Output:
```
NAME                  STATUS
spark-history-server  Up X seconds
spark-etl-app         Up X seconds
```

### View logs for any container
```bash
# ETL job logs
docker-compose logs spark-etl-app

# History Server logs (shows DataFlint JAR download)
docker-compose logs spark-history
```

### Inspect output files
```bash
# List generated CSV files
docker exec spark-etl-app ls -la /data/

# List Parquet output files
docker exec spark-etl-app ls -la /data/output/

# Check event logs
docker exec spark-etl-app ls -la /data/spark-events/
```

### Copy output files to your machine
```bash
# Copy Parquet files
docker cp spark-etl-app:/data/output ./local-output

# Copy all data
docker cp spark-etl-app:/data ./local-data
```

---

## Phase 7: Troubleshooting

### "No applications" showing at http://localhost:18080
- **Reason:** Job still running or just completed
- **Solution:** Wait 60+ seconds, then refresh page
- **Check logs:** `docker-compose logs spark-etl-app`

### Can't open http://localhost:18080
- **Reason:** History Server not ready yet
- **Solution:** Wait 20 seconds and try again
- **Check logs:** `docker-compose logs spark-history`

### No DataFlint tab visible
- **Reason:** JAR didn't download properly
- **Solution:** Check "History Server" logs for wget errors
- **Manual check:** `docker exec spark-history-server ls -la /opt/spark/jars/`

### Something went wrong with the job
- **Check Docker logs:** `docker-compose logs spark-etl-app`
- **Restart:** `docker-compose down && docker-compose up --build`

---

## Phase 8: File Locations
```bash
# DataFlint UI logs
docker-compose logs dataflint-ui

# Spark ETL logs
docker-compose logs spark-etl-app

# History Server logs
docker-compose logs spark-history
```

### Inspect output files inside spark-etl container
```bash
# List generated CSV files
docker exec spark-etl-app ls -la /data/

# List Parquet output files
docker exec spark-etl-app ls -la /data/output/

# Check metrics database
docker exec spark-etl-app sqlite3 /data/metrics.db ".tables"
docker exec spark-etl-app sqlite3 /data/metrics.db "SELECT * FROM runs LIMIT 5;"
```

### Copy files to your machine
```bash
# Copy output files
docker cp spark-etl-app:/data/output ./local-output

# Copy metrics database
docker cp spark-etl-app:/data/metrics.db ./
```

**Event logs** (read by History Server):
```
./data/spark-events/
├── app-20250402T103000Z.eventlog
└── ... (more on future runs)
```

**Output Parquet files** (your ETL results):
```
./data/output/
├── enriched_data/ (main enriched transaction dataset)
├── customer_analytics/ (customer-level metrics)
├── category_analytics/ (product category analysis)
├── country_analytics/ (geographic breakdown)
├── segment_analytics/ (customer segment metrics)
├── product_analytics/ (product performance)
└── daily_revenue/ (time-series daily metrics)
```

---

## Summary: The New Simplified Architecture

**Before (removed):**
- ❌ dataflint-ui service on port 5000
- ❌ store_metrics.py (SQLite persistence)
- ❌ Multiple separate UIs to check

**Now (correct):**
- ✅ Spark ETL on port 4040 (live job UI)
- ✅ Spark History Server on port 18080 (with DataFlint JAR embedded)
- ✅ Everything integrated in **one address: http://localhost:18080**

**All you need:**
1. Run: `docker-compose up --build`
2. Wait: ~45 seconds for job to complete
3. Visit: http://localhost:18080
4. Click: Your application
5. Explore: DataFlint tab for DAG and metrics

**Data persists in:**
- `/data/spark-events/` - Event logs (read by History Server)
- `/data/output/` - Parquet files (your job output)

**Containers:**
- `spark-history-server` - Permanent (reads event logs)
- `spark-etl-app` - Runs job once, exits cleanly

Enjoy exploring DataFlint! 🚀
