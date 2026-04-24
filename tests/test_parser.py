"""Tests for pipeline/parser.py — Owner: Chinmayi Siddapur"""

import pytest
from pipeline.parser import parse_chunk, build_parser


SAMPLE_LOGS = [
    "2024-01-01 10:00:00 INFO Server started on port 8080",
    "2024-01-01 10:00:01 INFO Server started on port 9090",
    "2024-01-01 10:00:02 ERROR Connection refused at 192.168.1.1",
]


def test_parse_chunk_returns_dicts():
    miner = build_parser()
    results = parse_chunk(miner, SAMPLE_LOGS)
    assert len(results) == 3
    assert all("template" in r for r in results)
    assert all("cluster_id" in r for r in results)


def test_similar_logs_get_same_template():
    miner = build_parser()
    results = parse_chunk(miner, SAMPLE_LOGS[:2])
    assert results[0]["template"] == results[1]["template"]
