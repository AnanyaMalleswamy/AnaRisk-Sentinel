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

