"""
feature_extraction.py — Stage 4a: Convert parsed logs into numerical feature vectors.

Features used for anomaly detection:
  - log level (encoded as integer)
  - cluster ID frequency
  - hour of day (from timestamp if available)
  - template length (proxy for message complexity)

Owner: Roshan George (1RV24CS235)
"""

import re
from collections import Counter

LEVEL_MAP = {"DEBUG": 0, "INFO": 1, "WARN": 2, "WARNING": 2, "ERROR": 3, "CRITICAL": 4, "FATAL": 4}


def extract_level(raw: str) -> int:
    """Extract log level as an integer from a raw log line."""
    for level, code in LEVEL_MAP.items():
        if level in raw.upper():
            return code
    return 1  # default to INFO


def extract_hour(raw: str) -> int:
    """Extract hour of day from common timestamp formats (0-23), or -1 if not found."""
    match = re.search(r"\b(\d{2}):\d{2}:\d{2}\b", raw)
    return int(match.group(1)) if match else -1


def build_features(logs: list[dict]) -> list[dict]:
    """
    Add a 'features' key to each log dict containing a numeric feature vector.

    Args:
        logs: List of parsed log dicts.

    Returns:
        Same list with 'features' key added to each entry.
    """
    cluster_counts = Counter(log.get("cluster_id", -1) for log in logs)

    for log in logs:
        cid = log.get("cluster_id", -1)
        raw = log.get("raw", "")
        template = log.get("template", raw)
        log["features"] = [
            extract_level(raw),
            cluster_counts[cid],
            extract_hour(raw),
            len(template.split()),
        ]
    return logs
