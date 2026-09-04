from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "index.html")

from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def analyze(request):
    """Temporary mock investigation response. No real analysis logic here."""
    mock_response = {
        "status": "success",
        "classification": "REVIEW_RECOMMENDED",
        "message": "Mock investigation completed",
        "findings": [
            {
                "rule": "UNUSUALLY_LARGE_TRANSACTION",
                "severity": "HIGH",
                "transaction_id": "T004",
                "explanation": "Transaction amount is significantly above the customer's typical activity.",
            },
            {
                "rule": "RAPID_SUCCESSION_TRANSFERS",
                "severity": "MEDIUM",
                "transaction_id": "T007",
                "explanation": "Multiple transfers occurred within a short time window.",
            },
        ],
    }
    return JsonResponse(mock_response)