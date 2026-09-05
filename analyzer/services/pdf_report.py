from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

def generate_pdf(report_data):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Banking Transaction Investigation Report",
        author="Transaction Risk Investigation Assistant",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#172033"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#687386"),
        spaceAfter=12,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#172033"),
        spaceBefore=8,
        spaceAfter=7,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#303949"),
    )

    small_style = ParagraphStyle(
        "Small",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#687386"),
    )

    finding_style = ParagraphStyle(
        "Finding",
        parent=body_style,
        fontSize=9,
        leading=12,
    )

    priority_style = ParagraphStyle(
        "Priority",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#9B1C1C"),
        alignment=TA_CENTER,
    )

    story = []

    customer_id = report_data.get("customer_id", "Unknown")
    classification = report_data.get("classification", "UNKNOWN")
    baseline = report_data.get("baseline", {})
    signals = report_data.get("signals", [])
    threads = report_data.get("threads", [])
    transactions = report_data.get("transactions", [])
    narrative = report_data.get("narrative") or {}
