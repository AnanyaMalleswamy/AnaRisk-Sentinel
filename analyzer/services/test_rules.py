from analyzer.services.baseline import build_baseline_for_customer
from analyzer.services.rules import generate_signals, classify_overall

def txn(tid, date, amount, payee, channel):
    return {"transaction_id": tid, "customer_id": "C01", "date": date,
            "description": "test", "payee": payee, "amount": amount, "channel": channel}

# Routine history + one big outlier transaction
transactions = [
    txn("T1", "2026-01-01", 800, "Fresh Mart", "UPI"),
    txn("T2", "2026-01-03", 900, "Fresh Mart", "UPI"),
    txn("T3", "2026-01-05", 850, "Fresh Mart", "UPI"),
    txn("T4", "2026-01-08", 1000, "Power Co", "UPI"),
    txn("T5", "2026-01-10", 45000, "Fresh Mart", "UPI"),  # unusually large
]

baseline = build_baseline_for_customer("C01", transactions)
signals = generate_signals("C01", transactions, baseline)
classification = classify_overall(signals, baseline)

for s in signals:
    print(s["signal_type"], s["severity"], s["transaction_ids"])
print("OVERALL:", classification)