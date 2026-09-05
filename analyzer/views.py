from django.shortcuts import render
from django.tasks import signals
import json
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
from django.http import FileResponse, request
from .services.pdf_report import generate_pdf
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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

@require_POST
def generate_pdf_report(request):
    """Generate a PDF from deterministic analysis data and optional AI narrative."""

    # ---------------------------------------------------------
    # Optional existing AI narrative
    # ---------------------------------------------------------
    narrative = {}

    narrative_raw = request.POST.get("narrative", "").strip()

    if narrative_raw:
        try:
            parsed_narrative = json.loads(narrative_raw)

            if isinstance(parsed_narrative, dict):
                narrative = parsed_narrative

        except json.JSONDecodeError:
            narrative = {}

    # ---------------------------------------------------------
    # Uploaded CSV
    # ---------------------------------------------------------
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {
                "status": "error",
                "message": "No file was uploaded.",
            },
            status=400,
        )

    # ---------------------------------------------------------
    # Parse CSV
    # ---------------------------------------------------------
    try:
        transactions = parse_transactions_csv(uploaded_file)

    except CSVValidationError as exc:
        return JsonResponse(
            {
                "status": "error",
                "message": str(exc),
            },
            status=400,
        )

    # ---------------------------------------------------------
    # Deterministic analysis
    # ---------------------------------------------------------
    customer_id = transactions[0]["customer_id"]

    baseline = build_baseline_for_customer(
        customer_id,
        transactions,
    )

    signals = generate_signals(
        customer_id,
        transactions,
        baseline,
    )

    threads = build_evidence_threads(
        customer_id,
        transactions,
        signals,
        baseline,
    )

    classification = classify_overall(
        signals,
        baseline,
    )

    # ---------------------------------------------------------
    # Build PDF data
    # ---------------------------------------------------------
    report_data = {
        "customer_id": customer_id,
        "classification": classification,
        "baseline": baseline,
        "signals": signals,
        "threads": threads,
        "transactions": transactions,
        "narrative": narrative,
    }

    # ---------------------------------------------------------
    # Generate PDF
    # ---------------------------------------------------------
    pdf_buffer = generate_pdf(report_data)

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"investigation_report_{customer_id}.pdf",
        content_type="application/pdf",
    )

def run_analysis(csv_file):
    """
    Mock or real signal processing execution.
    Returns signal array and baseline metrics.
    """
    # Sample calculated signals
    signals = [
        {"signal_type": "Velocity Spike", "severity": "High", "reason": "Rapid succession of large transfers", "transaction_ids": ["TX101", "TX102"]},
        {"signal_type": "Off-Hours Activity", "severity": "Medium", "reason": "Execution outside typical local time profile", "transaction_ids": ["TX103"]},
        {"signal_type": "Amount Outlier", "severity": "High", "reason": "300% higher than historical upper bound", "transaction_ids": ["TX104"]},
        {"signal_type": "New Beneficiary", "severity": "High", "reason": "Unrecognized cross-border endpoint", "transaction_ids": ["TX105"]}
    ]
    
    # 4 signals = High Risk classification
    classification = "HIGH RISK" if len(signals) >= 4 else "ELEVATED RISK"

    baseline = {
        "history_strength": "High (90 days data)",
        "transaction_count": 142,
        "history_days": 90,
        "amount_profile": {"typical_lower": "$20.00", "typical_upper": "$250.00"},
        "channel_profile": {"dominant_channel": "Mobile App"},
        "frequency_profile": {"transactions_per_week": 11}
    }

    threads = [
        {
            "thread_id": "TH-01",
            "priority": "P1 - Critical",
            "time_range": {"start": "2026-09-01", "end": "2026-09-05"},
            "transaction_ids": ["TX101", "TX102", "TX104", "TX105"],
            "signal_types": ["Velocity Spike", "Amount Outlier", "New Beneficiary"]
        }
    ]

    return {
        "status": "success",
        "classification": classification,
        "transaction_count": 142,
        "signals": signals,
        "baseline": baseline,
        "threads": threads
    }

@csrf_exempt
def analyze_view(request):
    if request.method == "POST" and request.FILES.get("file"):
        csv_file = request.FILES["file"]
        result = run_analysis(csv_file)
        return JsonResponse(result)
    
    return JsonResponse({"status": "error", "message": "No CSV file provided."}, status=400)