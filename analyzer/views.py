from django.shortcuts import render
from analyzer.services.parser import CSVValidationError, parse_transactions_csv
# Create your views here.
def index(request):
    return render(request, "index.html")

from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def analyze(request):
    """Parses and validates the uploaded CSV. No risk logic yet."""
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

    return JsonResponse({
        "status": "success",
        "transaction_count": len(transactions),
        "preview": transactions[:5],
    })