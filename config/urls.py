"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from analyzer.views import analyze, index
from analyzer.views import analyze, generate_report, index
from analyzer.views import generate_pdf_report

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", lambda request: render(request, "index.html")),
    path("api/analyze/", analyze, name="analyze"),
    path("api/generate-report/", generate_report, name="generate_report")
    path("api/generate-pdf/",generate_pdf_report,name="generate_pdf_report",),
]
