"""Tests for pipeline/ingestion.py — Owner: Riya Aggarwal"""

import os
import tempfile
import pytest
from pipeline.ingestion import stream_logs, get_memory_mb


def make_temp_log(lines):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
    f.write("\n".join(lines))
    f.close()
    return f.name


def test_stream_logs_yields_all_lines():
    lines = [f"INFO line {i}" for i in range(100)]
    path = make_temp_log(lines)
    collected = []
    for chunk in stream_logs(path, chunk_size=20):
        collected.extend(chunk)
    os.unlink(path)
    assert len(collected) == 100


def test_stream_logs_chunk_size():
    lines = [f"INFO line {i}" for i in range(50)]
    path = make_temp_log(lines)
    chunks = list(stream_logs(path, chunk_size=10))
    os.unlink(path)
    assert all(len(c) <= 10 for c in chunks)


def test_get_memory_mb_returns_positive():
    assert get_memory_mb() > 0
