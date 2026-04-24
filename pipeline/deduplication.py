"""
deduplication.py — Stage 3: Near-duplicate log removal using SimHash / MinHash.

Uses Locality Sensitive Hashing (LSH) to efficiently detect and
remove near-identical log templates without comparing all pairs.

"""

from datasketch import MinHash, MinHashLSH


def build_lsh(threshold: float = 0.8, num_perm: int = 64) -> MinHashLSH:
    """
    Create an LSH index for near-duplicate detection.

    Args:
        threshold: Jaccard similarity threshold (0-1). Higher = stricter.
        num_perm: Number of permutations for MinHash. Higher = more accurate.

    Returns:
        Empty MinHashLSH index.
    """
    return MinHashLSH(threshold=threshold, num_perm=num_perm)


def make_minhash(text: str, num_perm: int = 64) -> MinHash:
    """
    Generate a MinHash signature for a log template string.

    Args:
        text: Log template string.
        num_perm: Must match the LSH index's num_perm.

    Returns:
        MinHash object representing the text.
    """
    m = MinHash(num_perm=num_perm)
    for token in text.lower().split():
        m.update(token.encode("utf8"))
    return m


def deduplicate_chunk(lsh: MinHashLSH, parsed_logs: list[dict], num_perm: int = 64) -> list[dict]:
    """
    Filter near-duplicate entries from a parsed log chunk.

    Args:
        lsh: MinHashLSH index (shared across chunks).
        parsed_logs: List of parsed log dicts from parser.py.
        num_perm: Must match the LSH index's num_perm.

    Returns:
        List of unique parsed log dicts (duplicates removed).
    """
    unique = []
    for i, log in enumerate(parsed_logs):
        template = log.get("template", log.get("raw", ""))
        mh = make_minhash(template, num_perm)
        key = f"{log.get('cluster_id', 'x')}_{i}"
        result = lsh.query(mh)
        if not result:
            lsh.insert(key, mh)
            unique.append(log)
    return unique
