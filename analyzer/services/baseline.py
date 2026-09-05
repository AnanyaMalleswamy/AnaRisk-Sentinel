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

def classify_history_strength(transaction_count, history_days):
    """Deterministic strength label based on centralized thresholds."""
    strong = HISTORY_STRENGTH_RULES["strong"]
    moderate = HISTORY_STRENGTH_RULES["moderate"]

    if transaction_count >= strong["min_count"] and history_days >= strong["min_days"]:
        return "strong"
    if transaction_count >= moderate["min_count"] and history_days >= moderate["min_days"]:
        return "moderate"
    return "sparse"


def _build_amount_profile(amounts):
    amounts_sorted = sorted(amounts)
    count = len(amounts_sorted)
    median = statistics.median(amounts_sorted)
    minimum = amounts_sorted[0]
    maximum = amounts_sorted[-1]

    if count >= MIN_COUNT_FOR_QUARTILES:
        # Interquartile range: robust to a handful of extreme outliers.
        q1, _, q3 = statistics.quantiles(amounts_sorted, n=4, method="inclusive")
        typical_lower, typical_upper = q1, q3
    else:
        # Not enough data to trust quartiles — use the observed range.
        typical_lower, typical_upper = minimum, maximum

    return {
        "median": round(median, 2),
        "typical_lower": round(typical_lower, 2),
        "typical_upper": round(typical_upper, 2),
        "minimum": round(minimum, 2),
        "maximum": round(maximum, 2),
    }
