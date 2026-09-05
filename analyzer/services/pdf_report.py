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

# investigation overview

    story.append(
        Paragraph(
            "BANKING TRANSACTION<br/>INVESTIGATION REPORT",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Transaction Risk Investigation Assistant · Track PS06",
            subtitle_style,
        )
    )

    # Header information
    priority = narrative.get(
        "investigator_priority",
        "NO_ATTENTION" if classification == "NO_ATTENTION" else "REVIEW",
    )

    header_data = [
        [
            Paragraph("<b>CUSTOMER</b><br/>" + str(customer_id), body_style),
            Paragraph("<b>ASSESSMENT</b><br/>" + str(classification), body_style),
            Paragraph("<b>PRIORITY</b><br/>" + str(priority), priority_style),
        ]
    ]

    header_table = Table(
        header_data,
        colWidths=[55 * mm, 65 * mm, 45 * mm],
    )

    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F5F8")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#D9DEE7")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9DEE7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )

    story.append(header_table)
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "BANKING TRANSACTION<br/>INVESTIGATION REPORT",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Transaction Risk Investigation Assistant · Track PS06",
            subtitle_style,
        )
    )

    # Header information
    priority = narrative.get(
        "investigator_priority",
        "NO_ATTENTION" if classification == "NO_ATTENTION" else "REVIEW",
    )

    header_data = [
        [
            Paragraph("<b>CUSTOMER</b><br/>" + str(customer_id), body_style),
            Paragraph("<b>ASSESSMENT</b><br/>" + str(classification), body_style),
            Paragraph("<b>PRIORITY</b><br/>" + str(priority), priority_style),
        ]
    ]

    header_table = Table(
        header_data,
        colWidths=[55 * mm, 65 * mm, 45 * mm],
    )

    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F5F8")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#D9DEE7")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9DEE7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )

    story.append(header_table)
    story.append(Spacer(1, 10))


    story.append(
        Paragraph(
            "BANKING TRANSACTION<br/>INVESTIGATION REPORT",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Transaction Risk Investigation Assistant · Track PS06",
            subtitle_style,
        )
    )

    # Header information
    priority = narrative.get(
        "investigator_priority",
        "NO_ATTENTION" if classification == "NO_ATTENTION" else "REVIEW",
    )

    header_data = [
        [
            Paragraph("<b>CUSTOMER</b><br/>" + str(customer_id), body_style),
            Paragraph("<b>ASSESSMENT</b><br/>" + str(classification), body_style),
            Paragraph("<b>PRIORITY</b><br/>" + str(priority), priority_style),
        ]
    ]

    header_table = Table(
        header_data,
        colWidths=[55 * mm, 65 * mm, 45 * mm],
    )

    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F5F8")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#D9DEE7")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9DEE7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )

    story.append(header_table)
    story.append(Spacer(1, 10))



    story.append(PageBreak())

    story.append(
        Paragraph("BEHAVIORAL EVIDENCE & REVIEW", title_style)
    )

    story.append(
        Paragraph(
            f"Customer {customer_id} · Evidence-backed investigation details",
            subtitle_style,
        )
    )

    # ---------------------------------------------------------
    # TRANSACTIONS OF INTEREST
    # ---------------------------------------------------------

    story.append(Paragraph("TRANSACTIONS OF INTEREST", section_style))

    flagged_ids = set()

    for signal in signals:
        flagged_ids.update(signal.get("transaction_ids", []))

    interesting_transactions = [
        txn for txn in transactions
        if txn.get("transaction_id") in flagged_ids
    ]

    if interesting_transactions:
        transaction_rows = [
            [
                Paragraph("<b>ID</b>", small_style),
                Paragraph("<b>DATE</b>", small_style),
                Paragraph("<b>PAYEE</b>", small_style),
                Paragraph("<b>AMOUNT</b>", small_style),
                Paragraph("<b>CHANNEL</b>", small_style),
            ]
        ]

        for txn in interesting_transactions:
            transaction_rows.append(
                [
                    Paragraph(str(txn.get("transaction_id", "")), body_style),
                    Paragraph(str(txn.get("date", "")), body_style),
                    Paragraph(str(txn.get("payee", "")), body_style),
                    Paragraph(f"₹{txn.get('amount', '')}", body_style),
                    Paragraph(str(txn.get("channel", "")), body_style),
                ]
            )

        transaction_table = Table(
            transaction_rows,
            colWidths=[25 * mm, 28 * mm, 48 * mm, 32 * mm, 32 * mm],
            repeatRows=1,
        )

        transaction_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172033")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9DEE7")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        story.append(transaction_table)
    else:
        story.append(
            Paragraph(
                "No transactions were flagged for review.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # INVESTIGATION THREADS
    # ---------------------------------------------------------

    story.append(Paragraph("INVESTIGATION THREADS", section_style))

    if threads:
        for thread in threads:
            thread_text = (
                f"<b>{thread.get('thread_id', 'THREAD')}</b> · "
                f"Priority: <b>{thread.get('priority', 'N/A')}</b><br/>"
                f"Transactions: {', '.join(thread.get('transaction_ids', []))}<br/>"
                f"Signals: {', '.join(thread.get('signal_types', []))}<br/>"
                f"Time range: "
                f"{thread.get('time_range', {}).get('start', 'N/A')} → "
                f"{thread.get('time_range', {}).get('end', 'N/A')}"
            )

            thread_table = Table(
                [[Paragraph(thread_text, body_style)]],
                colWidths=[165 * mm],
            )

            thread_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D9DEE7")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 9),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )

            story.append(thread_table)
            story.append(Spacer(1, 5))
    else:
        story.append(
            Paragraph(
                "No investigation threads identified.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # BEHAVIORAL CHANGE
    # ---------------------------------------------------------

    story.append(Paragraph("BEHAVIORAL CHANGE", section_style))

    behavioral_change = narrative.get(
        "behavioral_change",
        "No additional behavioral change narrative was generated.",
    )

    story.append(
        Table(
            [[Paragraph(str(behavioral_change), body_style)]],
            colWidths=[165 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D9DEE7")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        )
    )

    # ---------------------------------------------------------
    # RECOMMENDED REVIEW
    # ---------------------------------------------------------

    story.append(Paragraph("RECOMMENDED REVIEW", section_style))

    recommendations = narrative.get("recommended_review", [])

    if recommendations:
        for recommendation in recommendations:
            story.append(
                Paragraph(
                    f"□  {recommendation}",
                    body_style,
                )
            )
            story.append(Spacer(1, 4))
    else:
        story.append(
            Paragraph(
                "No additional review actions were generated.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # DISCLAIMER / FOOTER
    # ---------------------------------------------------------

    story.append(Spacer(1, 10))

    disclaimer = (
        "<b>INVESTIGATOR NOTE</b><br/>"
        "This report identifies behavioral anomalies and supporting evidence "
        "for investigator review. It does not establish that fraud occurred. "
        "Final judgment remains with the investigator."
    )

    story.append(
        Table(
            [[Paragraph(disclaimer, small_style)]],
            colWidths=[165 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F5F8")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D9DEE7")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        )
    )

    def add_page_number(canvas, document):
        canvas.saveState()

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#687386"))

        canvas.drawString(
            16 * mm,
            8 * mm,
            "Transaction Risk Investigation Assistant · PS06",
        )

        canvas.drawRightString(
            A4[0] - 16 * mm,
            8 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    buffer.seek(0)
    return buffer