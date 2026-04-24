# Memory Efficient Log File Analyzer Using Minimal RAM For Sustainable IT

> **RV College of Engineering — Experiential Learning Project 2024-25**
> Team 57 · Theme: SDG

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents
- [Project Overview](#project-overview)
- [Team](#team)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Running the Pipeline](#running-the-pipeline)
- [Running the Dashboard](#running-the-dashboard)
- [Datasets](#datasets)
- [Evaluation Metrics](#evaluation-metrics)
- [Contributing (Team Guidelines)](#contributing-team-guidelines)
- [Branch Strategy](#branch-strategy)
- [SDG Alignment](#sdg-alignment)

---

## Project Overview

Modern servers, cloud platforms, and IoT devices generate log data in the GB–TB range daily. Tools like ELK Stack and Splunk need 10–20 GB RAM and expensive infrastructure — making them unusable on student laptops, SME servers, or edge devices.

This project builds a **memory-efficient log analysis pipeline** that processes large log files using minimal RAM by:

- Reading logs as a **stream** (never loading the full file into memory)
- **Parsing** unstructured logs into structured templates using Drain3
- **Deduplicating** near-identical entries with SimHash / MinHash
- **Detecting anomalies** with Isolation Forest (no labels required)
- **Storing** compressed results in Parquet format via PyArrow
- **Visualising** trends and anomalies via a Streamlit dashboard

Target: process GB-scale logs on a machine with **< 512 MB RAM**.

---

## Team

| # | USN | Name | Responsibility |
|---|-----|------|----------------|
| 1 | 1RV24CS230 | Riya Aggarwal | Streaming Ingestion + Evaluation |
| 2 | 1RV24CS069 | Chinmayi Siddapur | Log Parsing (Drain3) + Deduplication |
| 3 | 1RV24CS235 | Roshan George | Anomaly Detection + Feature Extraction |
| 4 | 1RV24CI066 | Mayank Bajaj | Dashboard + Storage + Integration |

**Mentors:**
- Dr. Anitha Sandeep, Assistant Professor, CS Dept
- Prof. Manasa M, Assistant Professor, AIML Dept

---

## Architecture

```
Raw Log File (GB scale)
        │
        ▼
┌─────────────────┐
│ Stage 1         │  ← ingestion.py
│ Streaming       │    Line-by-line generator, psutil memory monitor
│ Ingestion       │    Constant RAM regardless of file size
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 2         │  ← parser.py
│ Drain3 Parsing  │    Fixed-depth parse tree
│                 │    Extracts log templates + cluster IDs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 3         │  ← deduplication.py
│ SimHash Dedup   │    Locality Sensitive Hashing
│                 │    Removes near-duplicate log entries
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 4         │  ← feature_extraction.py + anomaly_detector.py
│ Anomaly         │    Isolation Forest on log-level, freq, time features
│ Detection       │    Assigns anomaly score per entry
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 5         │  ← storage.py + dashboard/
│ Parquet Storage │    Columnar compressed storage via PyArrow
│ + Dashboard     │    Streamlit + Plotly visualisation
└─────────────────┘
```

---

## Project Structure

```
log-analyzer/
│
├── data/
│   ├── raw/                  # Original log files (HDFS, BGL, etc.) — not committed to git
│   ├── processed/            # Parquet outputs after pipeline run
│   └── samples/              # Small sample files for dev/testing (committed)
│
├── pipeline/
│   ├── __init__.py
│   ├── ingestion.py          # Generator-based streaming log reader
│   ├── parser.py             # Drain3 wrapper + template storage
│   ├── deduplication.py      # SimHash / MinHash + LSH deduplication
│   ├── feature_extraction.py # Log-level, frequency, timestamp features
│   ├── anomaly_detector.py   # Isolation Forest training and scoring
│   └── storage.py            # PyArrow Parquet write/read helpers
│
├── dashboard/
│   ├── app.py                # Streamlit entry point — run this to launch UI
│   ├── pages/
│   │   ├── overview.py       # Log volume, level distribution charts
│   │   ├── anomalies.py      # Flagged entries table + anomaly scores
│   │   └── performance.py    # RAM usage, processing time, compression ratio
│   └── components/
│       └── charts.py         # Reusable Plotly figure builders
│
├── evaluation/
│   ├── benchmark.py          # Compare pipeline vs baseline (load-all approach)
│   ├── metrics.py            # RAM tracker, F1 score, compression ratio helpers
│   └── reports/              # Auto-generated evaluation reports (CSV/HTML)
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
├── main.py                   # CLI entry — runs the full pipeline end-to-end
└── README.md
```

---

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Language | Python 3.10+ | Core development |
| Log Parsing | `drain3` | Streaming Drain algorithm |
| Deduplication | `datasketch` | MinHash + LSH |
| ML / Anomaly | `scikit-learn` | Isolation Forest |
| Storage | `pyarrow` | Parquet columnar compression |
| Dashboard | `streamlit` + `plotly` | Interactive UI and charts |
| Memory profiling | `psutil`, `memory_profiler`, `tracemalloc` | Live RAM monitoring |
| Data handling | `pandas` (chunked) | Avoid full load into memory |
| Testing | `pytest` | Unit tests per module |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/<your-org>/log-analyzer.git
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

### 4. Add a sample log file

Place any `.log` file inside `data/raw/`. A small sample is already available in `data/samples/` for quick testing.

---

## Running the Pipeline

```bash
# Run the full pipeline on a log file
python main.py --input data/raw/your_file.log

# Run on sample data (for quick testing)
python main.py --input data/samples/sample.log --output data/processed/

# Run with memory profiling enabled
python main.py --input data/samples/sample.log --profile
```

Output will be saved as Parquet files in `data/processed/`.

---

## Running the Dashboard

```bash
streamlit run dashboard/app.py
```

Then open `http://localhost:8501` in your browser.

---

## Datasets

We use publicly available datasets from the [LogHub](https://github.com/logpai/loghub) benchmark collection.

| Dataset | Size | Description | Best For |
|---------|------|-------------|----------|
| HDFS | ~1.5 GB | Hadoop distributed system logs | High volume streaming tests |
| BGL | ~700 MB | BlueGene/L supercomputer logs | Anomaly detection (has labels) |
| OpenStack | ~500 MB | Cloud platform logs | Template parsing tests |
| Apache | ~50 MB | Web server access logs | Quick dev/testing |
| Windows | ~26 MB | Windows event logs | Deduplication tests |

> **Note:** Raw log files are excluded from git (see `.gitignore`). Download datasets from [LogHub](https://github.com/logpai/loghub) and place them in `data/raw/`.

> **BGL is recommended first** — it has ground-truth anomaly labels so you can compute actual F1 scores.

---

## Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Peak RAM (MB) | Max memory during processing | < 512 MB on 1 GB file |
| Processing time (s) | End-to-end pipeline time | Competitive vs ELK |
| Compression ratio | Raw size / Parquet size | > 5× |
| Anomaly F1 score | Precision/recall on BGL labels | > 0.80 |
| Dedup reduction % | Entries removed / total entries | Measured per dataset |

Run the benchmark script to generate a full comparison report:

```bash
python evaluation/benchmark.py --dataset data/raw/BGL.log
```

---

## Contributing (Team Guidelines)

### Before you start coding

1. Always pull latest changes before starting work:
   ```bash
   git pull origin main
   ```
2. Create a new branch for your feature (see Branch Strategy below)
3. Never commit directly to `main`

### Commit message format

Use this format so the team can track progress easily:

```
[module] short description

Examples:
[ingestion] add generator-based chunk reader
[parser] integrate Drain3 with config file
[dashboard] add anomaly score histogram
[tests] add unit tests for deduplication
[docs] update README with dataset instructions
```

### Before opening a pull request

- [ ] Code runs without errors
- [ ] Relevant unit test added or updated in `tests/`
- [ ] No large files committed (no `.log` files, no Parquet files)
- [ ] `requirements.txt` updated if you added a new library

### Code style

- Follow PEP 8
- Add docstrings to every function
- Keep functions short and single-purpose

---

## Branch Strategy

```
main                  ← stable, working code only
│
├── dev               ← integration branch (merge here first)
│   ├── riya/ingestion
│   ├── chinmayi/parser-dedup
│   ├── roshan/anomaly-detection
│   └── mayank/dashboard
```

**Workflow:**
1. Branch off `dev` with your name prefix
2. Finish your feature, test it locally
3. Open a Pull Request into `dev`
4. One other team member reviews and approves
5. Mentor review before merging `dev` → `main`

---

## SDG Alignment

| SDG | Connection |
|-----|-----------|
| **SDG 9** — Industry, Innovation & Infrastructure | Enables affordable log analytics for SMEs and educational institutions without expensive cloud infrastructure |
| **SDG 12** — Responsible Consumption & Production | Reduces computational overhead, storage usage, and energy consumption in log processing |
| **SDG 13** — Climate Action | Lower energy consumption from lightweight processing contributes to green IT practices |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
