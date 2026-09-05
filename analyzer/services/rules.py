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
