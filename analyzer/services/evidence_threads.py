from datetime import datetime, timedelta

TEMPORAL_PROXIMITY_DAYS = 3

THREAD_PRIORITY_HIGH_MIN_SIGNAL_TYPES = 3
THREAD_PRIORITY_HIGH_MIN_SIGNALS_WITH_HIGH_SEVERITY = 1
THREAD_PRIORITY_HIGH_MIN_SIGNAL_COUNT = 3
THREAD_PRIORITY_MEDIUM_MIN_SIGNAL_COUNT = 2

def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _signal_date_range(signal, txn_dates_by_id):
    dates = [txn_dates_by_id[tid] for tid in signal["transaction_ids"] if tid in txn_dates_by_id]
    if not dates:
        return None, None
    return min(dates), max(dates)

def _signals_are_related(signal_a, range_a, signal_b, range_b):
    """Two signals are related if they share a transaction OR fall within
    TEMPORAL_PROXIMITY_DAYS of each other."""
    shared_txns = set(signal_a["transaction_ids"]) & set(signal_b["transaction_ids"])
    if shared_txns:
        return True

    start_a, end_a = range_a
    start_b, end_b = range_b
    if start_a is None or start_b is None:
        return False

    # Gap between the two signals' date ranges (0 if they already overlap)
    if end_a < start_b:
        gap_days = (start_b - end_a).days
    elif end_b < start_a:
        gap_days = (start_a - end_b).days
    else:
        gap_days = 0

    return gap_days <= TEMPORAL_PROXIMITY_DAYS


def _cluster_signals(signals, txn_dates_by_id):
    """Union-find style clustering into connected components."""
    n = len(signals)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    ranges = [_signal_date_range(s, txn_dates_by_id) for s in signals]

    for i in range(n):
        for j in range(i + 1, n):
            if _signals_are_related(signals[i], ranges[i], signals[j], ranges[j]):
                union(i, j)

    clusters = {}
    for i in range(n):
        root = find(i)
        clusters.setdefault(root, []).append(signals[i])

    return list(clusters.values())
