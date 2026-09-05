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

def _build_payee_profile(transactions):
    payees = defaultdict(lambda: {"count": 0, "first_seen": None, "last_seen": None})

    for txn in transactions:
        payee = txn["payee"]
        txn_date = txn["date"]  # already an ISO string from parser.py
        entry = payees[payee]
        entry["count"] += 1
        if entry["first_seen"] is None or txn_date < entry["first_seen"]:
            entry["first_seen"] = txn_date
        if entry["last_seen"] is None or txn_date > entry["last_seen"]:
            entry["last_seen"] = txn_date

    recurring = sorted(
        (name for name, info in payees.items() if info["count"] > 1),
        key=lambda name: payees[name]["count"],
        reverse=True,
    )[:TOP_RECURRING_PAYEES_LIMIT]

    return {
        "unique_payee_count": len(payees),
        "payees": dict(payees),
        "recurring_payees": recurring,
    }


def _build_channel_profile(transactions):
    distribution = defaultdict(int)
    for txn in transactions:
        distribution[txn["channel"]] += 1

    total = sum(distribution.values())
    proportions = {
        channel: round(count / total, 3)
        for channel, count in distribution.items()
    }
    dominant_channel = max(distribution, key=distribution.get)

    return {
        "distribution": dict(distribution),
        "proportions": proportions,
        "dominant_channel": dominant_channel,
    }


def _build_frequency_profile(transaction_dates, history_days, transaction_count):
    sorted_dates = sorted(transaction_dates)

    if len(sorted_dates) < 2:
        return {
            "average_gap_days": None,
            "median_gap_days": None,
            "transactions_per_week": None,
        }

    gaps = [
        (sorted_dates[i] - sorted_dates[i - 1]).days
        for i in range(1, len(sorted_dates))
    ]

    average_gap = round(statistics.mean(gaps), 2)
    median_gap = round(statistics.median(gaps), 2)

    transactions_per_week = (
        round(transaction_count / (history_days / 7), 2)
        if history_days > 0
        else None  # all activity on a single day — rate is undefined, not zero
    )

    return {
        "average_gap_days": average_gap,
        "median_gap_days": median_gap,
        "transactions_per_week": transactions_per_week,
    }


def build_baseline_for_customer(customer_id, transactions):
    if not transactions:
        return _empty_baseline(customer_id)

    amounts = [txn["amount"] for txn in transactions]
    dates = [_parse_date(txn["date"]) for txn in transactions]

    history_start = min(dates)
    history_end = max(dates)
    history_days = (history_end - history_start).days
    transaction_count = len(transactions)

    return {
        "customer_id": customer_id,
        "transaction_count": transaction_count,
        "history_start": history_start.isoformat(),
        "history_end": history_end.isoformat(),
        "history_days": history_days,
        "history_strength": classify_history_strength(transaction_count, history_days),
        "amount_profile": _build_amount_profile(amounts),
        "payee_profile": _build_payee_profile(transactions),
        "channel_profile": _build_channel_profile(transactions),
        "frequency_profile": _build_frequency_profile(dates, history_days, transaction_count),
    }
def build_customer_baselines(transactions):
    by_customer = defaultdict(list)
    for txn in transactions:
        by_customer[txn["customer_id"]].append(txn)

    return {
        customer_id: build_baseline_for_customer(customer_id, customer_txns)
        for customer_id, customer_txns in by_customer.items()
    }
