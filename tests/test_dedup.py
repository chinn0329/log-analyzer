"""Tests for pipeline/deduplication.py — Owner: Chinmayi Siddapur"""

from pipeline.deduplication import build_lsh, deduplicate_chunk


DUPLICATE_LOGS = [
    {"raw": "INFO server started port 8080", "template": "INFO server started port <NUM>", "cluster_id": 1},
    {"raw": "INFO server started port 9090", "template": "INFO server started port <NUM>", "cluster_id": 1},
    {"raw": "ERROR disk full on node 3",     "template": "ERROR disk full on node <NUM>", "cluster_id": 2},
]


def test_duplicates_are_removed():
    lsh = build_lsh(threshold=0.8)
    unique = deduplicate_chunk(lsh, DUPLICATE_LOGS)
    assert len(unique) < len(DUPLICATE_LOGS)


def test_unique_logs_are_kept():
    lsh = build_lsh(threshold=0.8)
    unique = deduplicate_chunk(lsh, DUPLICATE_LOGS)
    templates = [u["template"] for u in unique]
    assert "ERROR disk full on node <NUM>" in templates
