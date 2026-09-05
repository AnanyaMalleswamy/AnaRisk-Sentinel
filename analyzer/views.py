from django.shortcuts import render
from analyzer.services.parser import CSVValidationError, parse_transactions_csv
from analyzer.services.baseline import build_baseline_for_customer
from analyzer.services.rules import generate_signals, classify_overall
# Create your views here.
def index(request):
    return render(request, "index.html")

from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def analyze(request):
    """Orchestrates parse -> baseline -> signals -> classification. No algorithms live here."""
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {"status": "error", "message": "No file was uploaded."},
            status=400,
        )

    try:
        transactions = parse_transactions_csv(uploaded_file)
    except CSVValidationError as exc:
        return JsonResponse(
            {"status": "error", "message": str(exc)},
            status=400,
        )

    # This phase assumes a single customer per uploaded file.
    customer_id = transactions[0]["customer_id"]
    baseline = build_baseline_for_customer(customer_id, transactions)
    signals = generate_signals(customer_id, transactions, baseline)
    classification = classify_overall(signals, baseline)

    return JsonResponse({
        "status": "success",
        "transaction_count": len(transactions),
        "classification": classification,
        "baseline": baseline,
        "signals": signals,
        "preview": transactions[:5],
    })