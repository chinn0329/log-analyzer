"""Tests for pipeline/anomaly_detector.py"""

from pipeline.feature_extraction import build_features
from pipeline.anomaly_detector import train_model, score_logs


SAMPLE_LOGS = [
    {"raw": "INFO normal operation", "template": "INFO normal operation", "cluster_id": 1},
    {"raw": "INFO normal operation", "template": "INFO normal operation", "cluster_id": 1},
    {"raw": "CRITICAL SYSTEM FAILURE DISK FULL NODE 3", "template": "CRITICAL SYSTEM FAILURE", "cluster_id": 99},
]


def test_score_logs_adds_keys():
    logs = build_features(SAMPLE_LOGS)
    X = [log["features"] for log in logs]
    model = train_model(X, contamination=0.1)
    scored = score_logs(model, logs)
    assert all("anomaly_score" in l for l in scored)
    assert all("is_anomaly" in l for l in scored)


def test_anomaly_scores_are_floats():
    logs = build_features(SAMPLE_LOGS)
    X = [log["features"] for log in logs]
    model = train_model(X)
    scored = score_logs(model, logs)
    assert all(isinstance(l["anomaly_score"], float) for l in scored)
