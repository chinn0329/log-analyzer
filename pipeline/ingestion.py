"""
ingestion.py — Stage 1: Streaming log ingestion.

Reads log files line-by-line using a generator so only a small
chunk of data lives in memory at any time.

"""

import psutil
import gc
from typing import Generator


def stream_logs(filepath: str, chunk_size: int = 500) -> Generator[list[str], None, None]:
    """
    Stream a log file in chunks without loading it fully into memory.

    Args:
        filepath: Path to the log file.
        chunk_size: Number of lines per chunk yielded to the pipeline.

    Yields:
        List of raw log line strings (one chunk at a time).
    """
    chunk = []
    with open(filepath, "r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                chunk.append(line)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
                gc.collect()
        if chunk:
            yield chunk


def get_memory_mb() -> float:
    """Return current process memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def log_memory(label: str) -> None:
    """Print current memory usage with a label."""
    print(f"[MEM] {label}: {get_memory_mb():.2f} MB")
