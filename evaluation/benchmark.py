"""
benchmark.py — Compare the streaming pipeline vs a naive baseline (load-all).

Generates a CSV and printed summary report.

Usage:
    python evaluation/benchmark.py --dataset data/samples/sample.log

"""

import argparse
import csv
import os
from datetime import datetime
from evaluation.metrics import track_memory, track_time, compression_ratio


def baseline_load_all(filepath: str) -> list[str]:
    """Naive baseline: load entire file into memory at once."""
    with open(filepath, "r", errors="replace") as f:
        return f.readlines()


def streaming_load(filepath: str, chunk_size: int = 500):
    """Streaming approach: generator-based chunk reader."""
    import gc
    chunk = []
    with open(filepath, "r", errors="replace") as f:
        for line in f:
            chunk.append(line.strip())
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
                gc.collect()
    if chunk:
        yield chunk


def run_benchmark(dataset_path: str) -> dict:
    print(f"\nBenchmarking on: {dataset_path}")
    print("=" * 50)

    # --- Baseline ---
    print("\n[Baseline] Loading entire file into memory...")
    with track_memory() as mem_base, track_time() as t_base:
        lines = baseline_load_all(dataset_path)
        line_count = len(lines)
        del lines

    print(f"  Lines: {line_count:,}")
    print(f"  Peak RAM: {mem_base['peak_mb']} MB")
    print(f"  Time: {t_base['elapsed_s']} s")

    # --- Streaming pipeline ---
    print("\n[Pipeline] Streaming chunk-by-chunk...")
    with track_memory() as mem_pipe, track_time() as t_pipe:
        total = 0
        for chunk in streaming_load(dataset_path):
            total += len(chunk)

    print(f"  Lines processed: {total:,}")
    print(f"  Peak RAM: {mem_pipe['peak_mb']} MB")
    print(f"  Time: {t_pipe['elapsed_s']} s")

    # --- Summary ---
    ram_saved = mem_base["peak_mb"] - mem_pipe["peak_mb"]
    speedup = t_base["elapsed_s"] / t_pipe["elapsed_s"] if t_pipe["elapsed_s"] > 0 else 1

    results = {
        "timestamp": datetime.now().isoformat(),
        "dataset": os.path.basename(dataset_path),
        "line_count": line_count,
        "baseline_peak_ram_mb": mem_base["peak_mb"],
        "pipeline_peak_ram_mb": mem_pipe["peak_mb"],
        "ram_saved_mb": round(ram_saved, 3),
        "baseline_time_s": t_base["elapsed_s"],
        "pipeline_time_s": t_pipe["elapsed_s"],
        "speedup": round(speedup, 2),
    }

    print("\n--- Summary ---")
    print(f"  RAM saved:  {ram_saved:.2f} MB")
    print(f"  Speedup:    {speedup:.2f}x")

    return results


def save_report(results: dict, output_dir: str = "evaluation/reports/"):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "benchmark_results.csv")
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(results)
    print(f"\nReport saved to: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark the log analysis pipeline")
    parser.add_argument("--dataset", required=True, help="Path to log file")
    args = parser.parse_args()

    results = run_benchmark(args.dataset)
    save_report(results)
