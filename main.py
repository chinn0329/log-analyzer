"""
main.py — Entry point for the Memory Efficient Log File Analyzer pipeline.

Usage:
    python main.py --input data/samples/sample.log
    python main.py --input data/raw/BGL.log --output data/processed/ --profile
"""

import argparse
import time
import tracemalloc

def parse_args():
    parser = argparse.ArgumentParser(description="Memory Efficient Log Analyzer")
    parser.add_argument("--input", required=True, help="Path to input log file")
    parser.add_argument("--output", default="data/processed/", help="Output directory for Parquet files")
    parser.add_argument("--profile", action="store_true", help="Enable memory profiling")
    return parser.parse_args()

def run_pipeline(input_path, output_dir, profile=False):
    if profile:
        tracemalloc.start()

    start = time.time()
    print(f"[1/5] Streaming ingestion: {input_path}")
    # from pipeline.ingestion import stream_logs
    # logs = stream_logs(input_path)

    print("[2/5] Parsing logs with Drain3...")
    # from pipeline.parser import parse_logs
    # parsed = parse_logs(logs)

    print("[3/5] Deduplicating with SimHash...")
    # from pipeline.deduplication import deduplicate
    # deduped = deduplicate(parsed)

    print("[4/5] Running anomaly detection...")
    # from pipeline.anomaly_detector import detect_anomalies
    # results = detect_anomalies(deduped)

    print("[5/5] Saving to Parquet...")
    # from pipeline.storage import save_parquet
    # save_parquet(results, output_dir)

    elapsed = time.time() - start
    print(f"\nPipeline complete in {elapsed:.2f}s")

    if profile:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Peak RAM usage: {peak / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.input, args.output, args.profile)
