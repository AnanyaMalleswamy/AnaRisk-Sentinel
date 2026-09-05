import statistics
from collections import defaultdict
from datetime import datetime, date
from itertools import groupby

# we need a minimum number of these many days to see a pattern in the transaction historyand come to a conclusion
HISTORY_STRENGTH_RULES = {
    "strong": {"min_count": 15, "min_days": 30},
    "moderate": {"min_count": 5, "min_days": 7},
}

# Minimum transaction count required before we trust quartile-based
# (IQR) amount boundaries. Below this we go back to min/max.
MIN_COUNT_FOR_QUARTILES = 4

# How many top recurring payees to surface explicitly.
TOP_RECURRING_PAYEES_LIMIT = 5

def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _empty_baseline(customer_id=None):
    """Safe, well-defined baseline for zero transactions."""
    return {
        "customer_id": customer_id,
        "transaction_count": 0,
        "history_start": None,
        "history_end": None,
        "history_days": 0,
        "history_strength": "sparse",
        "amount_profile": {
            "median": None,
            "typical_lower": None,
            "typical_upper": None,
            "minimum": None,
            "maximum": None,
        },
        "payee_profile": {
            "unique_payee_count": 0,
            "payees": {},
            "recurring_payees": [],
        },
        "channel_profile": {
            "distribution": {},
            "proportions": {},
            "dominant_channel": None,
        },
        "frequency_profile": {
            "average_gap_days": None,
            "median_gap_days": None,
            "transactions_per_week": None,
        },
    }
