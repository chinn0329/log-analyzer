"""
anomaly_detector.py — Stage 4b: Anomaly detection using Isolation Forest.

No labelled data required. Each log entry is scored; entries with
scores below the threshold are flagged as anomalous.

Owner: Roshan George (1RV24CS235)
"""

import numpy as np
from sklearn.ensemble import IsolationForest


def train_model(feature_matrix: list[list[float]], contamination: float = 0.05) -> IsolationForest:
    """
    Train an Isolation Forest model on extracted log features.

    Args:
        feature_matrix: List of feature vectors (one per log entry).
        contamination: Estimated fraction of anomalies in the data.

    Returns:
        Trained IsolationForest model.
    """
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(feature_matrix)
    return model


def score_logs(model: IsolationForest, logs: list[dict]) -> list[dict]:
    """
    Assign anomaly scores and labels to each log entry.

    Args:
        model: Trained IsolationForest model.
        logs: List of log dicts with 'features' key populated.

    Returns:
        Same list with 'anomaly_score' and 'is_anomaly' keys added.
    """
    if not logs:
        return logs

    X = np.array([log["features"] for log in logs])
    scores = model.decision_function(X)   # higher = more normal
    predictions = model.predict(X)        # -1 = anomaly, 1 = normal

    for log, score, pred in zip(logs, scores, predictions):
        log["anomaly_score"] = round(float(score), 4)
        log["is_anomaly"] = pred == -1

    return logs
