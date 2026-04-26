# Memory Efficient Log File Analyzer Using Minimal RAM For Sustainable IT
 
> **RV College of Engineering — Experiential Learning Project 2024-25**
> Team 57 · Theme: SDG
 
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
 
---
 
## Table of Contents
- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [How It Works — Pipeline Explained](#how-it-works--pipeline-explained)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Running the Pipeline](#running-the-pipeline)
- [Running the Dashboard](#running-the-dashboard)
- [Running Tests](#running-tests)
- [Running the Benchmark](#running-the-benchmark)
- [Datasets](#datasets)
- [Evaluation Metrics](#evaluation-metrics)
- [SDG Alignment](#sdg-alignment)
---
 
## Project Overview
 
Modern computing systems — web servers, cloud platforms, IoT devices — generate log data continuously, often reaching GB to TB scale per day. These logs are essential for monitoring system health, detecting failures, and identifying security anomalies.
 
However, existing tools like **ELK Stack** and **Splunk** require 10–20 GB of RAM and significant infrastructure investment, making them completely impractical for student laptops, small enterprises, and edge devices.
 
This project proposes a **Memory-Efficient Log File Analyzer** that processes large-scale log files using minimal RAM. By combining streaming techniques, structured parsing, deduplication, and lightweight machine learning, the system can analyze GB-scale logs on a machine with less than 512 MB of available RAM — without sacrificing accuracy or performance.
 
**Team:**
 
| # | USN | Name |
|---|-----|------|
| 1 | 1RV24CS230 | Riya Aggarwal |
| 2 | 1RV24CS069 | Chinmayi Siddapur |
| 3 | 1RV24CS235 | Roshan George |
| 4 | 1RV24CI066 | Mayank Bajaj |
 
**Mentors:**
- Dr. Anitha Sandeep, Assistant Professor, CS Dept
- Prof. Manasa M, Assistant Professor, AIML Dept
---
 
## Problem Statement
 
Log analysis is a critical part of maintaining any computing system, but it comes with a significant resource cost:
 
- Industry-standard tools require **high memory and expensive infrastructure**, ruling them out for resource-constrained environments.
- Most research solutions focus on **individual tasks** (just parsing, or just anomaly detection) rather than a complete end-to-end pipeline.
- There is a clear gap where users on **low-resource systems** — student laptops, SME servers, IoT edge devices — cannot perform full log analysis efficiently.
This project addresses that gap by designing a complete, memory-efficient pipeline capable of handling large-scale logs without expensive hardware.
 
---
 
## How It Works — Pipeline Explained
 
The system is built as a **5-stage sequential pipeline**. Each stage performs a specific transformation on the data, passing only what is needed to the next stage. At no point is the entire log file loaded into memory.
 
---
 
### Stage 1 — Streaming Ingestion
 
**File:** `pipeline/ingestion.py`
 
The first challenge with large log files is simply reading them without running out of memory. Traditional approaches load the entire file at once — this is what makes tools like ELK Stack so memory-hungry.
 
Our solution uses a **Python generator** that reads the file line by line and yields small chunks (e.g., 500 lines at a time) to the rest of the pipeline. Once a chunk is processed, it is released from memory via garbage collection. This means **memory usage stays constant** regardless of how large the input file is.
 
`psutil` and `tracemalloc` are used throughout to monitor and report actual RAM usage in real time.
 
---
 
### Stage 2 — Log Parsing with Drain3
 
**File:** `pipeline/parser.py`
 
Raw log lines are unstructured text — each one looks slightly different even if they represent the same type of event. For example:
 
```
INFO  Connected to database at 192.168.1.10
INFO  Connected to database at 10.0.0.5
INFO  Connected to database at 172.16.0.3
```
 
These three lines are logically identical but textually different. Downstream analysis would treat them as three separate events.
 
**Drain3** solves this by parsing each log line through a fixed-depth parse tree, extracting a generalised **template** and replacing variable parts with placeholders:
 
```
INFO  Connected to database at <IP>
```
 
Every log entry is assigned a **cluster ID** based on its template. This dramatically reduces the variety of data that needs to be stored and analysed. Drain3 is specifically designed to work in a streaming context, making it ideal for our pipeline.
 
---
 
### Stage 3 — Deduplication with SimHash / MinHash
 
**File:** `pipeline/deduplication.py`
 
Even after parsing, log data contains massive amounts of redundancy. A single event (like a heartbeat or a routine info message) can appear thousands of times with only minor variations.
 
We use **MinHash with Locality Sensitive Hashing (LSH)** from the `datasketch` library to efficiently detect near-duplicate log templates. Instead of comparing every pair of entries (which would be O(n²)), LSH groups similar entries into the same hash bucket, making deduplication extremely fast even on large datasets.
 
Duplicate entries are either removed or aggregated with a frequency count. This stage can reduce the number of stored entries by 60–90% on typical server logs.
 
---
 
### Stage 4 — Feature Extraction and Anomaly Detection
 
**Files:** `pipeline/feature_extraction.py`, `pipeline/anomaly_detector.py`
 
With parsed and deduplicated logs, we now need to identify which entries represent abnormal system behaviour.
 
**Feature Extraction** converts each structured log entry into a numerical vector based on:
- Log level (DEBUG=0, INFO=1, WARN=2, ERROR=3, CRITICAL=4)
- Cluster frequency (how often this template appeared)
- Hour of day (extracted from timestamp)
- Template length (a proxy for message complexity)
**Isolation Forest** (from scikit-learn) is then trained on these feature vectors. Isolation Forest works by randomly partitioning the feature space — anomalous entries are isolated more quickly than normal ones, resulting in a lower anomaly score. Crucially, it requires **no labelled training data**, making it practical for real-world log files where anomalies are not pre-tagged.
 
Each log entry is assigned an anomaly score and a boolean `is_anomaly` flag.
 
---
 
### Stage 5 — Compressed Storage and Visualisation
 
**Files:** `pipeline/storage.py`, `dashboard/`
 
Processed results are saved in **Parquet format** using PyArrow. Parquet is a columnar storage format that compresses log data far more efficiently than plain text — typically achieving 5–10× compression. It also supports fast column-level queries, meaning the dashboard can load only the columns it needs rather than the entire file.
 
The **Streamlit dashboard** provides three interactive views:
- **Overview** — log volume, level distribution, most frequent templates
- **Anomalies** — flagged entries with their anomaly scores, filterable and searchable
- **Performance** — RAM usage, processing time, and compression ratio compared to the naive baseline
---
 
## Architecture
 
```
Raw Log File (GB scale)
        │
        ▼
┌─────────────────────────────────────────┐
│ Stage 1 — Streaming Ingestion           │
│ pipeline/ingestion.py                   │
│                                         │
│ • Line-by-line generator (no full load) │
│ • Constant RAM regardless of file size  │
│ • psutil + tracemalloc memory monitor   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ Stage 2 — Log Parsing (Drain3)          │
│ pipeline/parser.py                      │
│                                         │
│ • Fixed-depth parse tree                │
│ • Extracts log templates + cluster IDs  │
│ • Variable parts replaced with <tokens> │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ Stage 3 — Deduplication (MinHash + LSH) │
│ pipeline/deduplication.py               │
│                                         │
│ • MinHash signatures per template       │
│ • LSH finds near-duplicates efficiently │
│ • 60–90% entry reduction typical        │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ Stage 4 — Anomaly Detection             │
│ pipeline/feature_extraction.py          │
│ pipeline/anomaly_detector.py            │
│                                         │
│ • Numerical feature vectors per entry   │
│ • Isolation Forest (no labels needed)   │
│ • Anomaly score + is_anomaly flag       │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ Stage 5 — Storage + Visualisation       │
│ pipeline/storage.py + dashboard/        │
│                                         │
│ • Parquet columnar compression (5–10×)  │
│ • Streamlit + Plotly dashboard          │
│ • Overview, Anomalies, Performance tabs │
└─────────────────────────────────────────┘
```
 
---
 
## Project Structure
 
```
log-analyzer/
│
├── data/
│   ├── raw/                  # Original log files — not committed to git
│   ├── processed/            # Parquet outputs after pipeline run
│   └── samples/              # Small sample file for quick testing
│
├── pipeline/
│   ├── ingestion.py          # Stage 1 — generator-based streaming reader
│   ├── parser.py             # Stage 2 — Drain3 log parsing
│   ├── deduplication.py      # Stage 3 — SimHash / MinHash + LSH
│   ├── feature_extraction.py # Stage 4a — numerical feature vectors
│   ├── anomaly_detector.py   # Stage 4b — Isolation Forest scoring
│   └── storage.py            # Stage 5 — PyArrow Parquet write/read
│
├── dashboard/
│   ├── app.py                # Streamlit entry point
│   ├── pages/
│   │   ├── overview.py       # Log volume and level distribution
│   │   ├── anomalies.py      # Flagged entries and anomaly scores
│   │   └── performance.py    # RAM, time, compression metrics
│   └── components/
│       └── charts.py         # Reusable Plotly figure builders
│
├── evaluation/
│   ├── benchmark.py          # Pipeline vs baseline RAM/time comparison
│   ├── metrics.py            # RAM tracker, F1 score, compression ratio
│   └── reports/              # Generated benchmark reports (CSV)
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_parser.py
│   ├── test_dedup.py
│   └── test_anomaly.py
│
├── configs/
│   └── drain3.ini            # Drain3 config (depth, similarity threshold)
│
├── notebooks/
│   ├── EDA.ipynb             # Dataset exploration
│   └── model_tuning.ipynb    # Isolation Forest hyperparameter search
│
├── .gitignore
├── requirements.txt
├── main.py                   # CLI entry point — runs full pipeline
└── README.md
```
 
---
 
## Tech Stack
 
| Layer | Tool | Why We Chose It |
|-------|------|-----------------|
| Language | Python 3.10+ | Native generator support for memory-efficient streaming |
| Log Parsing | `drain3` | Designed for streaming; fixed-depth tree keeps memory bounded |
| Deduplication | `datasketch` | Probabilistic MinHash + LSH — sub-linear time and memory |
| ML / Anomaly | `scikit-learn` Isolation Forest | No labels required; lightweight; works on CPU only |
| Storage | `pyarrow` + Parquet | Columnar compression; 5–10× smaller than raw text |
| Dashboard | `streamlit` + `plotly` | Rapid interactive UI with no frontend code required |
| Memory profiling | `psutil`, `memory_profiler`, `tracemalloc` | Accurate per-stage RAM measurement |
| Data handling | `pandas` (chunked mode) | Prevents full file loads during analysis |
| Testing | `pytest` | Simple unit tests per pipeline module |
 
---
 
## Getting Started
 
### 1. Clone the repo
 
```bash
git clone https://github.com/chinn0329/log-analyzer.git
cd log-analyzer
```
 
### 2. Create a virtual environment
 
```bash
python -m venv venv
 
# On Windows
venv\Scripts\activate
 
# On Mac/Linux
source venv/bin/activate
```
 
### 3. Install dependencies
 
```bash
pip install -r requirements.txt
```
 
### 4. Verify installation
 
```bash
pip list
```
 
All of the following should appear: `drain3`, `datasketch`, `scikit-learn`, `pyarrow`, `streamlit`, `plotly`, `psutil`, `memory-profiler`, `pytest`.
 
---
 
## Running the Pipeline
 
```bash
# Quick test on the included sample
python main.py --input data/samples/sample.log
 
# Run on a full dataset with output directory specified
python main.py --input data/raw/BGL.log --output data/processed/
 
# Run with memory profiling to see peak RAM usage
python main.py --input data/raw/BGL.log --profile
```
 
Processed output is saved as a Parquet file in `data/processed/`.
 
---
 
## Running the Dashboard
 
```bash
streamlit run dashboard/app.py
```
 
Open `http://localhost:8501` in your browser. Upload the Parquet file generated by the pipeline to explore results interactively.
 
---
 
## Running Tests
 
```bash
# Run all tests
pytest tests/
 
# Run a specific test file
pytest tests/test_ingestion.py -v
 
# Run with coverage report
pytest tests/ --cov=pipeline
```
 
---
 
## Running the Benchmark
 
Compares the streaming pipeline against a naive baseline that loads the entire file into memory at once:
 
```bash
python evaluation/benchmark.py --dataset data/samples/sample.log
```
 
Results are printed to the terminal and saved to `evaluation/reports/benchmark_results.csv`.
 
---
 
## Datasets
 
We use publicly available datasets from the [LogHub](https://github.com/logpai/loghub) benchmark collection, widely used in log analysis research.
 
| Dataset | Size | Description | Best For |
|---------|------|-------------|----------|
| HDFS | ~1.5 GB | Hadoop distributed system logs | High volume streaming tests |
| BGL | ~700 MB | BlueGene/L supercomputer logs | Anomaly detection — has ground truth labels |
| OpenStack | ~500 MB | Cloud platform logs | Template parsing tests |
| Apache | ~50 MB | Web server access logs | Quick dev and testing |
| Windows | ~26 MB | Windows event logs | Deduplication tests |
 
> Raw log files are excluded from git via `.gitignore`. Download from [LogHub](https://github.com/logpai/loghub) and place in `data/raw/`.
 
> **Start with BGL** — it has ground-truth anomaly labels, allowing real F1 score computation rather than qualitative evaluation.
 
---
 
## Evaluation Metrics
 
| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Peak RAM (MB) | Maximum memory used during pipeline execution | < 512 MB on a 1 GB log file |
| Processing time (s) | End-to-end wall-clock time for the full pipeline | Faster than or competitive with ELK |
| Compression ratio | Raw log size ÷ Parquet output size | > 5× |
| Anomaly F1 score | Precision and recall of anomaly detection on BGL labels | > 0.80 |
| Dedup reduction % | Percentage of entries removed as near-duplicates | Measured per dataset |
 
---
 
## SDG Alignment
 
This project directly contributes to three UN Sustainable Development Goals:
 
**SDG 9 — Industry, Innovation and Infrastructure**
By making log analytics accessible on low-cost hardware, the system enables small and medium enterprises, educational institutions, and IoT deployments to monitor their systems without expensive cloud infrastructure.
 
**SDG 12 — Responsible Consumption and Production**
The pipeline reduces computational overhead, storage consumption, and energy usage compared to traditional tools. Processing the same data with less hardware means less energy consumed per analysis.
 
**SDG 13 — Climate Action**
Reduced energy consumption in IT infrastructure directly contributes to lower carbon emissions. Lightweight, efficient software is a practical contribution to green computing.
 
---
 
## License
 
MIT License — see [LICENSE](LICENSE) for details.
 