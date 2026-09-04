from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "index.html")

from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def analyze(request):
    """Minimal pipeline-test endpoint. No analysis logic here."""
    return JsonResponse({
        "status": "success",
        "message": "Django backend connection successful",
    })