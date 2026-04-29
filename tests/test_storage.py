"""
test_storage.py — Unit tests for pipeline/storage.py
Run with: pytest tests/test_storage.py -v
"""

import os
import tempfile
import pytest
from pipeline.storage import save_parquet, load_parquet

SAMPLE_LOGS = [
    {
        "raw": "2024-01-15 08:00:01 INFO Server started on port 8080",
        "template": "<TIMESTAMP> INFO Server started on port <NUM>",
        "cluster_id": 1,
        "anomaly_score": 0.12,
        "is_anomaly": False,
        "features": [1, 3, 8, 5],
    },
    {
        "raw": "2024-01-15 08:00:14 CRITICAL DISK USAGE EXCEEDED 95%",
        "template": "<TIMESTAMP> CRITICAL DISK USAGE EXCEEDED <NUM>%",
        "cluster_id": 9,
        "anomaly_score": -0.34,
        "is_anomaly": True,
        "features": [4, 1, 8, 6],
    },
    {
        "raw": "2024-01-15 08:00:10 ERROR Connection refused at node 192.168.1.55",
        "template": "<TIMESTAMP> ERROR Connection refused at node <IP>",
        "cluster_id": 6,
        "anomaly_score": -0.21,
        "is_anomaly": True,
        "features": [3, 2, 8, 7],
    },
]


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


# --- save_parquet tests ---

def test_save_creates_file(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    assert os.path.exists(path)

def test_save_returns_valid_path(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    assert path.endswith(".parquet")

def test_save_creates_output_dir_if_missing(tmp_dir):
    new_dir = os.path.join(tmp_dir, "nested", "output")
    path = save_parquet(SAMPLE_LOGS, new_dir)
    assert os.path.exists(path)

def test_saved_file_is_nonzero(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    assert os.path.getsize(path) > 0


# --- load_parquet tests ---

def test_load_returns_list(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    loaded = load_parquet(path)
    assert isinstance(loaded, list)

def test_load_returns_correct_count(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    loaded = load_parquet(path)
    assert len(loaded) == len(SAMPLE_LOGS)

def test_load_preserves_raw(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    loaded = load_parquet(path)
    raws = [l["raw"] for l in loaded]
    for original in SAMPLE_LOGS:
        assert original["raw"] in raws

def test_load_preserves_template(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    loaded = load_parquet(path)
    templates = [l["template"] for l in loaded]
    for original in SAMPLE_LOGS:
        assert original["template"] in templates

def test_load_preserves_cluster_id(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    loaded = load_parquet(path)
    ids = [l["cluster_id"] for l in loaded]
    for original in SAMPLE_LOGS:
        assert original["cluster_id"] in ids

def test_load_preserves_is_anomaly(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    loaded = load_parquet(path)
    anomaly_flags = [l["is_anomaly"] for l in loaded]
    assert True in anomaly_flags
    assert False in anomaly_flags

def test_load_preserves_anomaly_score(tmp_dir):
    path = save_parquet(SAMPLE_LOGS, tmp_dir)
    loaded = load_parquet(path)
    for l in loaded:
        assert isinstance(l["anomaly_score"], float)

def test_save_empty_list(tmp_dir):
    path = save_parquet([], tmp_dir)
    loaded = load_parquet(path)
    assert loaded == []

def test_compression_reduces_size(tmp_dir):
    """Parquet file should be smaller than naive estimate of raw text size."""
    big_logs = SAMPLE_LOGS * 100
    path = save_parquet(big_logs, tmp_dir)
    parquet_size = os.path.getsize(path)
    raw_size = sum(len(l["raw"].encode()) for l in big_logs)
    assert parquet_size < raw_size