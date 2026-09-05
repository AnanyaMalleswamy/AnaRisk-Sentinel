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
