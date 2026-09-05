from datetime import datetime, timedelta

from analyzer.services.baseline import build_baseline_for_customer

LARGE_TRANSACTION_MULTIPLIERS = {"medium": 1.5, "high": 3.0}

NEW_PAYEE_BURST_MIN_COUNT = 3
NEW_PAYEE_BURST_MAX_WINDOW_DAYS = 3
NEW_PAYEE_RECENT_THRESHOLD_DAYS = 7  # payee must have first appeared this recently

BEHAVIORAL_BREAK_WINDOW_DAYS = 7
BEHAVIORAL_BREAK_AMOUNT_MULTIPLIER = 1.5
BEHAVIORAL_BREAK_CHANNEL_CONCENTRATION = 0.7
BEHAVIORAL_BREAK_PAYEE_UNFAMILIAR_RATIO = 0.5
BEHAVIORAL_BREAK_FREQUENCY_MULTIPLIER = 2.0
BEHAVIORAL_BREAK_MIN_DIMENSIONS = 2

ACTIVITY_BURST_WINDOW_DAYS = 3
ACTIVITY_BURST_MULTIPLIER = 3.0
ACTIVITY_BURST_MIN_COUNT = 4

def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

#Signal 1:
def detect_unusually_large_transactions(transactions, baseline):
    signals = []
    amount_profile = baseline.get("amount_profile", {})
    typical_upper = amount_profile.get("typical_upper")
    maximum = amount_profile.get("maximum")
    history_strength = baseline.get("history_strength")

    if not typical_upper or typical_upper <= 0:
        return signals  # no reliable reference point yet

    for txn in transactions:
        amount = txn["amount"]
        ratio = amount / typical_upper

        if ratio >= LARGE_TRANSACTION_MULTIPLIERS["high"]:
            severity = "high"
        elif ratio >= LARGE_TRANSACTION_MULTIPLIERS["medium"]:
            severity = "medium"
        else:
            continue

        reason = (
            f"Transaction amount ({amount}) is {round(ratio, 1)}x this customer's typical "
            f"upper amount ({typical_upper})."
        )
        if history_strength == "sparse":
            reason += " Based on limited transaction history for this customer."

        signals.append({
            "signal_type": "UNUSUALLY_LARGE_TRANSACTION",
            "transaction_ids": [txn["transaction_id"]],
            "severity": severity,
            "reason": reason,
            "evidence": {
                "amount": amount,
                "typical_upper": typical_upper,
                "historical_maximum": maximum,
                "ratio_to_typical_upper": round(ratio, 2),
            },
        })
    return signals

#Signal 2:
def detect_new_payee_burst(transactions, baseline):
    signals = []
    payees = baseline.get("payee_profile", {}).get("payees", {})
    history_end = baseline.get("history_end")
    if not payees or not history_end:
        return signals

    history_end_date = _parse_date(history_end)
    recent_cutoff = history_end_date - timedelta(days=NEW_PAYEE_RECENT_THRESHOLD_DAYS)
    typical_upper = baseline.get("amount_profile", {}).get("typical_upper") or 0

    for payee_name, info in payees.items():
        count = info["count"]
        first_seen = _parse_date(info["first_seen"])
        last_seen = _parse_date(info["last_seen"])
        window_days = (last_seen - first_seen).days

        if not (
            first_seen >= recent_cutoff
            and window_days <= NEW_PAYEE_BURST_MAX_WINDOW_DAYS
            and count >= NEW_PAYEE_BURST_MIN_COUNT
        ):
            continue

        matching_txns = [
            t for t in transactions
            if t["payee"] == payee_name and first_seen <= _parse_date(t["date"]) <= last_seen
        ]
        total_amount = sum(t["amount"] for t in matching_txns)
        severity = "high" if (count >= NEW_PAYEE_BURST_MIN_COUNT + 2 or total_amount > typical_upper * 2) else "medium"

        signals.append({
            "signal_type": "NEW_PAYEE_BURST",
            "transaction_ids": [t["transaction_id"] for t in matching_txns],
            "severity": severity,
            "reason": (
                f"Payee '{payee_name}' first appeared on {first_seen.isoformat()} and received "
                f"{count} payments within {window_days} day(s), totaling {total_amount}."
            ),
            "evidence": {
                "payee": payee_name,
                "first_seen": first_seen.isoformat(),
                "last_seen": last_seen.isoformat(),
                "transaction_count": count,
                "window_days": window_days,
                "total_amount": total_amount,
            },
        })
    return signals

#Signal 3:
def detect_behavioral_break(customer_id, transactions, baseline):
    signals = []
    history_end = baseline.get("history_end")
    if not history_end or baseline.get("transaction_count", 0) < 2:
        return signals

    history_end_date = _parse_date(history_end)
    window_start = history_end_date - timedelta(days=BEHAVIORAL_BREAK_WINDOW_DAYS)

    recent_txns = [t for t in transactions if _parse_date(t["date"]) > window_start]
    established_txns = [t for t in transactions if _parse_date(t["date"]) <= window_start]

    if not recent_txns or not established_txns:
        return signals  # nothing established to compare against, or nothing recent to evaluate

    established = build_baseline_for_customer(customer_id, established_txns)
    recent = build_baseline_for_customer(customer_id, recent_txns)

    dimensions_flagged = []

    est_typical_upper = established["amount_profile"]["typical_upper"]
    recent_median = recent["amount_profile"]["median"]
    if est_typical_upper and recent_median and recent_median > est_typical_upper * BEHAVIORAL_BREAK_AMOUNT_MULTIPLIER:
        dimensions_flagged.append(f"amount (recent median {recent_median} vs established typical upper {est_typical_upper})")

    est_dominant = established["channel_profile"]["dominant_channel"]
    est_dominant_share = established["channel_profile"]["proportions"].get(est_dominant, 0) if est_dominant else 0
    recent_dominant = recent["channel_profile"]["dominant_channel"]
    if est_dominant and recent_dominant and recent_dominant != est_dominant and est_dominant_share >= BEHAVIORAL_BREAK_CHANNEL_CONCENTRATION:
        dimensions_flagged.append(f"channel (established dominant '{est_dominant}' at {round(est_dominant_share*100)}%, recent dominant '{recent_dominant}')")

    established_payee_names = set(established["payee_profile"]["payees"].keys())
    unfamiliar_recent = [t for t in recent_txns if t["payee"] not in established_payee_names]
    unfamiliar_ratio = len(unfamiliar_recent) / len(recent_txns)
    if unfamiliar_ratio >= BEHAVIORAL_BREAK_PAYEE_UNFAMILIAR_RATIO:
        dimensions_flagged.append(f"payee ({round(unfamiliar_ratio*100)}% of recent transactions involve unfamiliar payees)")

    est_rate_per_week = established["frequency_profile"].get("transactions_per_week")
    if est_rate_per_week:
        recent_days = max((history_end_date - window_start).days, 1)
        recent_rate_per_week = (len(recent_txns) / recent_days) * 7
        if recent_rate_per_week > est_rate_per_week * BEHAVIORAL_BREAK_FREQUENCY_MULTIPLIER:
            dimensions_flagged.append(f"frequency (recent ~{round(recent_rate_per_week,1)}/week vs established ~{round(est_rate_per_week,1)}/week)")

    if len(dimensions_flagged) < BEHAVIORAL_BREAK_MIN_DIMENSIONS:
        return signals  # normal variation, not a meaningful regime change

    severity = "high" if len(dimensions_flagged) >= 3 else "medium"

    signals.append({
        "signal_type": "BEHAVIORAL_BREAK",
        "transaction_ids": [t["transaction_id"] for t in recent_txns],
        "severity": severity,
        "reason": (
            f"Recent activity (last {BEHAVIORAL_BREAK_WINDOW_DAYS} days) differs from established "
            f"behavior across {len(dimensions_flagged)} dimension(s): " + "; ".join(dimensions_flagged)
        ),
        "evidence": {
            "window_days": BEHAVIORAL_BREAK_WINDOW_DAYS,
            "dimensions_flagged": dimensions_flagged,
        },
    })
    return signals

#Signal 4: activity burst
def detect_activity_burst(transactions, baseline):
    signals = []
    expected_per_week = baseline.get("frequency_profile", {}).get("transactions_per_week")
    if not transactions or not expected_per_week:
        return signals

    expected_count_in_window = (expected_per_week / 7) * ACTIVITY_BURST_WINDOW_DAYS

    sorted_txns = sorted(transactions, key=lambda t: t["date"])
    dates = [_parse_date(t["date"]) for t in sorted_txns]

    best = None
    left = 0
    for right in range(len(sorted_txns)):
        while (dates[right] - dates[left]).days > ACTIVITY_BURST_WINDOW_DAYS:
            left += 1
        count = right - left + 1
        if count >= ACTIVITY_BURST_MIN_COUNT and count > expected_count_in_window * ACTIVITY_BURST_MULTIPLIER:
            if best is None or count > best["count"]:
                best = {
                    "count": count,
                    "start": dates[left],
                    "end": dates[right],
                    "transaction_ids": [sorted_txns[i]["transaction_id"] for i in range(left, right + 1)],
                }

    if best:
        severity = "high" if best["count"] > expected_count_in_window * ACTIVITY_BURST_MULTIPLIER * 2 else "medium"
        signals.append({
            "signal_type": "ACTIVITY_BURST",
            "transaction_ids": best["transaction_ids"],
            "severity": severity,
            "reason": (
                f"{best['count']} transactions occurred between {best['start']} and {best['end']} "
                f"({ACTIVITY_BURST_WINDOW_DAYS}-day window), vs an expected ~{round(expected_count_in_window, 1)} "
                f"based on this customer's typical rate of {round(expected_per_week, 2)}/week."
            ),
            "evidence": {
                "window_days": ACTIVITY_BURST_WINDOW_DAYS,
                "observed_count": best["count"],
                "expected_count": round(expected_count_in_window, 2),
                "customer_transactions_per_week": expected_per_week,
                "window_start": best["start"].isoformat(),
                "window_end": best["end"].isoformat(),
            },
        })
    return signals

#general function to actually generate signals and to classify overall based on the signals above
def generate_signals(customer_id, transactions, baseline):
    """Run all four detectors and return a traceability-checked signal list."""
    valid_ids = {t["transaction_id"] for t in transactions}

    signals = []
    signals.extend(detect_unusually_large_transactions(transactions, baseline))
    signals.extend(detect_new_payee_burst(transactions, baseline))
    signals.extend(detect_behavioral_break(customer_id, transactions, baseline))
    signals.extend(detect_activity_burst(transactions, baseline))

    # Defensive traceability guarantee — every ID must trace to real input.
    for signal in signals:
        signal["transaction_ids"] = [tid for tid in signal["transaction_ids"] if tid in valid_ids]

    return [s for s in signals if s["transaction_ids"]]


def classify_overall(signals, baseline):
    """Deterministic, conservative overall classification."""
    if not signals:
        return "NO_ATTENTION"

    if baseline.get("history_strength") == "sparse":
        return "REVIEW_LIMITED_EVIDENCE"

    severities = [s["severity"] for s in signals]
    if len(signals) >= 2 or "high" in severities:
        return "REVIEW_RECOMMENDED"

    return "REVIEW_LIMITED_EVIDENCE"