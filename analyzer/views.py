from django.shortcuts import render
from django.tasks import signals
from analyzer.services import baseline
from analyzer.services.parser import CSVValidationError, parse_transactions_csv
from analyzer.services.baseline import build_baseline_for_customer
from analyzer.services.rules import generate_signals, classify_overall
from analyzer.services.evidence_threads import build_evidence_threads
from analyzer.services.gemini import (
    GeminiConfigError,
    GeminiRequestError,
    GeminiResponseError,
    build_evidence_payload,
    generate_investigation_narrative,
)
from django.http import FileResponse
from .services.pdf_report import generate_pdf
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
    threads = build_evidence_threads(customer_id, transactions, signals, baseline)
    classification = classify_overall(signals, baseline)

    return JsonResponse({
        "status": "success",
        "transaction_count": len(transactions),
        "classification": classification,
        "baseline": baseline,
        "signals": signals,
        "threads": threads,
        "preview": transactions[:5],
    })

@require_POST
def generate_report(request):
    """Separate, explicit action. Calls Gemini exactly once per request."""
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"status": "error", "message": "No file was uploaded."}, status=400)

    try:
        transactions = parse_transactions_csv(uploaded_file)
    except CSVValidationError as exc:
        return JsonResponse({"status": "error", "message": str(exc)}, status=400)

    customer_id = transactions[0]["customer_id"]
    baseline = build_baseline_for_customer(customer_id, transactions)
    signals = generate_signals(customer_id, transactions, baseline)
    threads = build_evidence_threads(customer_id, transactions, signals, baseline)
    classification = classify_overall(signals, baseline)

    evidence_payload = build_evidence_payload(
        customer_id, transactions, baseline, signals, threads, classification
    )

    try:
        narrative = generate_investigation_narrative(evidence_payload)
    except GeminiConfigError as exc:
        return JsonResponse({"status": "error", "message": str(exc)}, status=503)
    
    except GeminiRequestError as exc:
        print("🔥 GEMINI REQUEST ERROR:", repr(exc))
        return JsonResponse(
        {
            "status": "error",
            "message": str(exc),
        },
        status=502,
    )

    except GeminiResponseError as exc:
        return JsonResponse({"status": "error", "message": str(exc)}, status=502)

    return JsonResponse({"status": "success", "narrative": narrative})

def generate_pdf_report(request):
    if request.method != "GET":
        return JsonResponse(
            {"status": "error", "message": "GET request required."},
            status=405,
        )

    pdf_buffer = generate_pdf()

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename="investigation_report.pdf",
        content_type="application/pdf",
    )