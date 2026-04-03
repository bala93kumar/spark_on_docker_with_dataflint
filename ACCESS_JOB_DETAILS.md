# 🚀 How to Access Job Details & View DataFlint UI

## Quick Summary

**Single address for everything:**
```
http://localhost:18080  ← Spark History Server (with DataFlint UI injected)
```

That's it! Everything is in ONE place now. No more separate ports.

---

## Step-by-Step Guide to Access Job Details

### Step 1: Start the Containers

```bash
cd c:\Users\balak\GitProjects\spark_on_docker_with_dataflint
docker-compose up --build
```

**What you'll see:**
```
[+] Building 5.2s
[+] Running 2/2
  ✓ spark-history
  ✓ spark-etl-app
```

### Step 2: Wait for Job to Complete

Watch logs until you see:
```
spark-etl-app | ✓ Pipeline completed successfully
spark-etl-app | 📊 View results in DataFlint:
spark-etl-app | • Spark History Server: http://localhost:18080
```

**Timeline:**
- **0-5 seconds:** Containers starting
- **5-15 seconds:** History Server initializing (downloading DataFlint JAR)
- **15-45 seconds:** Spark job running with DataFlint monitoring
- **45-50 seconds:** Job completes, event logs written
- **50+ seconds:** History Server reads logs and shows UI

### Step 3: Open Browser and Navigate

Open browser to:
```
http://localhost:18080
```

You'll see **Spark History Server** with a completed job listed.

### Step 4: Click on Your Job

Click on the application ID to open the job details.

You'll now see multiple tabs at the top. The key ones are:

| Tab | What You See |
|-----|--------------|
| **Jobs** | All job stages and execution summary |
| **Stages** | Individual stage details (tasks, shuffle, duration) |
| **DataFlint** | 🎯 **DataFlint UI with DAG, metrics, data quality** |
| **Storage** | Memory and cache info |
| **Environment** | Spark config |

### Step 5: Click "DataFlint" Tab

This is where you'll see:
- 🎨 **Visual DAG** of your Spark job (the 16 stages visualized)
- 📊 **Stage metrics** (shuffle bytes, task counts, durations)
- 🔍 **Data quality metrics** (completeness, distributions)
- 📈 **Performance analysis** (bottlenecks, slow stages)

---

## Where is DataFlint UI?

### Before (with custom Flask UI - NOW REMOVED ❌)
```
Port 5000  → Custom Flask dashboard
Port 18080 → Basic Spark History Server
```

### Now (with DataFlint JAR - CORRECT ✅)
```
Port 18080 → Spark History Server
            ├── Jobs tab
            ├── Stages tab
            ├── DataFlint tab ⭐ ← This is where DataFlint UI appears!
            └── Other tabs
```

**Important:** DataFlint is **embedded** in the Spark History Server UI, not in a separate service.

---

## What's Different?

**Then (with Flask UI):**
- DataFlint UI on http://localhost:5000 (separate service)
- History Server on http://localhost:18080 (separate service)
- Need to check both places

**Now (with DataFlint JAR):**
- Everything on http://localhost:18080 (single service)
- DataFlint UI is built into the Spark UI automatically
- One place to check everything ✅

---

## Detailed Steps to View Each Section

### View Stage Details

1. Go to http://localhost:18080
2. Click on your job
3. Click **"Stages"** tab
4. You'll see a table with all 16 stages:

```
| Stage | Task Count | Shuffle Bytes | Duration | Status |
|-------|-----------|---------------|----------|--------|
| 0     | 2         | 0             | 2s      | SUCCESS|
| 1     | 4         | 5 MB          | 5s      | SUCCESS|
| 2-8   | 6 parallel stages with 50+ MB shuffle
...
```

### View DataFlint Metrics

1. In the same job view, look for **DataFlint** tab (should be visible after tab-scrolling)
2. Or click the **DataFlint icon** if present
3. You'll see:
   - **DAG Visualization:** Your entire 16-stage pipeline visualized
   - **Data Quality:** Completeness %, null counts, distributions
   - **Stage Metrics:** Which stages are slowest, most shuffle, etc.

### View Timeline/Gantt Chart

1. Click **"Timeline"** tab
2. See visual timeline of all stages executing
3. Shows which stages ran in parallel vs sequentially

---

## Key Differences from Spark UI

| Aspect | Spark UI | DataFlint Tab |
|--------|----------|---------------|
| **Shows** | Stages, tasks, executors | DAG design, data flow, quality |
| **Focus** | Performance metrics | Data & business logic |
| **Visualization** | Tables & bars | DAG graph, visual flow |
| **Details** | Task-level | Stage-level & data metrics |

---

## Expected Metrics You'll See

Once job completes and you open DataFlint UI:

```
Job Execution Summary
├─ Total Duration: 35-45 seconds
├─ Stages Executed: 16
├─ Total Tasks: 50-100
├─ Total Shuffle: 50-100 MB
└─ Status: SUCCESS

Data Quality Metrics
├─ Records Processed: 10,000
├─ Data Completeness: 99.5%
├─ Null Count: 50
├─ Duplicate Records: 50
└─ Data Quality Score: 99.5%

Stage Breakdown
├─ Stage 0 (Load): 2 tasks, 2s
├─ Stage 1-2 (Transform): 4 tasks, 5s
├─ Stage 3-8 (6x Aggregations): 24 tasks, 25s
└─ Stage 9-16 (Output): 4 tasks, 3s
```

---

## Troubleshooting

### Can't see DataFlint tab
- Wait 5-10 seconds after job appears (tab loads asynchronously)
- Try scrolling right on the tabs (may be hidden if many tabs)
- Refresh the page (F5)

### Page shows "No applications"
- The job is still running (wait 45+ seconds)
- Check logs: `docker-compose logs spark-etl-app`

### History Server won't load
- DataFlint JAR downloading (can take 10-20s on first run)
- Check docker logs: `docker-compose logs spark-history`
- Verify network: `docker-compose ps`

### Only see default Spark UI, no DataFlint
- JAR may not have downloaded properly
- Check logs for wget errors
- Manual test: `docker exec spark-history-server ls -la /opt/spark/jars/`

---

## File Locations for Reference

**Event Logs** (read by History Server):
```
./data/spark-events/
├── app-20250402T103000Z.eventlog
└── ... (more event logs on future runs)
```

**Output Data** (your ETL results):
```
./data/output/
├── enriched_data.parquet/
├── customer_analytics.parquet/
├── category_analytics.parquet/
├── country_analytics.parquet/
├── segment_analytics.parquet/
├── product_analytics.parquet/
└── daily_revenue.parquet/
```

---

## Summary

**To view job details:**

1. Run: `docker-compose up --build`
2. Wait for job to complete (see "Pipeline completed successfully")
3. Open: `http://localhost:18080`
4. Click on your job
5. View tabs: **Jobs → Stages → DataFlint → Timeline**

**DataFlint UI location:**
- **NOT a separate service** → Integrated into Spark History Server
- Located at: **http://localhost:18080** in the **DataFlint tab**
- Accessible after job completes and event logs are processed

**One URL, everything inside:** 🎯 http://localhost:18080
