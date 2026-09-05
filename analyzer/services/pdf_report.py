from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
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
    HRFlowable,
)


# =========================================================
# COLOR PALETTE
# =========================================================

NAVY = colors.HexColor("#0B1220")
BLUE = colors.HexColor("#2563EB")
BLUE_LIGHT = colors.HexColor("#EFF6FF")
RED = colors.HexColor("#DC2626")
RED_LIGHT = colors.HexColor("#FEF2F2")
AMBER = colors.HexColor("#F59E0B")
AMBER_LIGHT = colors.HexColor("#FFFBEB")
GREEN = colors.HexColor("#16A34A")
GREEN_LIGHT = colors.HexColor("#F0FDF4")

TEXT = colors.HexColor("#1E293B")
MUTED = colors.HexColor("#64748B")
BORDER = colors.HexColor("#E2E8F0")
LIGHT = colors.HexColor("#F8FAFC")
WHITE = colors.white


# =========================================================
# MAIN PDF GENERATOR
# =========================================================

def generate_pdf(report_data):
    """
    Generates a maximum two-page investigator-facing PDF.

    Page 1:
        Case overview
        Customer / priority
        Why this needs attention
        Important transactions
        Available baseline information

    Page 2:
        AI-generated investigation report
        Recommended review
        Investigator note

    Gemini is NEVER called from this function.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=13 * mm,
        bottomMargin=15 * mm,
        title="Banking Transaction Investigation Report",
        author="Transaction Risk Investigation Assistant",
    )

    styles = getSampleStyleSheet()

    # =====================================================
    # STYLES
    # =====================================================

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=21,
        textColor=NAVY,
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=10,
        textColor=MUTED,
        spaceAfter=7,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=11,
        textColor=NAVY,
        spaceBefore=7,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.2,
        leading=11,
        textColor=TEXT,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9,
        textColor=MUTED,
    )

    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.8,
        leading=8,
        textColor=MUTED,
    )

    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=NAVY,
    )

    customer_style = ParagraphStyle(
        "Customer",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=17,
        textColor=NAVY,
    )

    priority_high_style = ParagraphStyle(
        "PriorityHigh",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=15,
        alignment=TA_RIGHT,
        textColor=RED,
    )

    priority_moderate_style = ParagraphStyle(
        "PriorityModerate",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=15,
        alignment=TA_RIGHT,
        textColor=AMBER,
    )

    priority_low_style = ParagraphStyle(
        "PriorityLow",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=15,
        alignment=TA_RIGHT,
        textColor=GREEN,
    )

    finding_id_style = ParagraphStyle(
        "FindingID",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=RED,
    )

    transaction_header_style = ParagraphStyle(
        "TransactionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=8,
        textColor=WHITE,
    )

    transaction_style = ParagraphStyle(
        "Transaction",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9,
        textColor=TEXT,
    )

    transaction_id_style = ParagraphStyle(
        "TransactionID",
        parent=transaction_style,
        fontName="Helvetica-Bold",
        textColor=RED,
    )

    transaction_amount_style = ParagraphStyle(
        "TransactionAmount",
        parent=transaction_style,
        fontName="Helvetica-Bold",
        textColor=RED,
        alignment=TA_RIGHT,
    )

    ai_heading_style = ParagraphStyle(
        "AIHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=19,
        textColor=NAVY,
        spaceAfter=3,
    )

    ai_subheading_style = ParagraphStyle(
        "AISubheading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=BLUE,
        spaceBefore=6,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=8,
        firstLineIndent=-6,
        spaceAfter=3,
    )

    story = []

    # =====================================================
    # DATA
    # =====================================================

    customer_id = report_data.get("customer_id", "Unknown")
    classification = report_data.get("classification", "UNKNOWN")
    baseline = report_data.get("baseline") or {}
    signals = report_data.get("signals") or []
    transactions = report_data.get("transactions") or []
    narrative = report_data.get("narrative") or {}

    # =====================================================
    # HELPERS
    # =====================================================

    def safe(value):
        if value is None:
            return ""

        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def amount(value):
        try:
            return f"₹{float(value):,.2f}"
        except (TypeError, ValueError):
            return "₹—"

    def first_value(*keys):
        for key in keys:
            value = baseline.get(key)

            if value is not None and value != "":
                return value

        return None

    def priority_from_data():
        priority = narrative.get("investigator_priority")
        signal_count=len(signals)
        if signal_count >= 4 or "HIGH" in str(classification).upper() or "CRITICAL" in str(classification).upper():
            return "HIGH"
        elif signal_count > 1 or "ELEVATED" in str(classification).upper() or "MEDIUM" in str(classification).upper():
            return "MODERATE"
        else:
            return "LOW"

    priority = priority_from_data()

    # =====================================================
    # FLAGGED TRANSACTIONS
    # =====================================================

    flagged_ids = set()

    for signal in signals:
        for transaction_id in signal.get("transaction_ids", []) or []:
            flagged_ids.add(str(transaction_id))

    flagged_transactions = [
        transaction
        for transaction in transactions
        if str(transaction.get("transaction_id")) in flagged_ids
    ]

    flagged_transactions.sort(
        key=lambda x: (
            str(x.get("date", "")),
            str(x.get("transaction_id", "")),
        )
    )

    # =====================================================
    # PAGE 1 — CASE OVERVIEW
    # =====================================================

    # Header
    header_left = [
        Paragraph(
            "BANKING TRANSACTION<br/>INVESTIGATION REPORT",
            title_style,
        ),
        Paragraph(
            "Transaction Risk Investigation Assistant · Track PS06",
            subtitle_style,
        ),
    ]

    if priority == "HIGH":
        priority_style = priority_high_style
        priority_label = "HIGH"
    elif priority == "MODERATE":
        priority_style = priority_moderate_style
        priority_label = "MODERATE"
    else:
        priority_style = priority_low_style
        priority_label = "LOW"

    header_right = [
        Paragraph(
            "INVESTIGATION PRIORITY",
            label_style,
        ),
        Paragraph(
            priority_label,
            priority_style,
        ),
        Paragraph(
            "REVIEW",
            label_style,
        ),
    ]

    header_table = Table(
        [[header_left, header_right]],
        colWidths=[112 * mm, 53 * mm],
    )

    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    story.append(header_table)

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=BORDER,
            spaceBefore=3,
            spaceAfter=8,
        )
    )

    # =====================================================
    # CUSTOMER / CASE IDENTIFIER
    # =====================================================

    customer_block = Table(
        [
            [
                Paragraph("CUSTOMER ID", label_style),
                Paragraph("CASE STATUS", label_style),
            ],
            [
                Paragraph(safe(customer_id), customer_style),
                Paragraph(safe(classification), value_style),
            ],
        ],
        colWidths=[82.5 * mm, 82.5 * mm],
    )

    customer_block.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(customer_block)

    # =====================================================
    # WHY THIS NEEDS ATTENTION
    # =====================================================

    story.append(
        Paragraph(
            "WHY THIS NEEDS ATTENTION",
            section_style,
        )
    )

    findings = narrative.get("key_findings") or []

    if findings:
        finding_rows = []

        for finding in findings[:5]:
            finding_rows.append(
                [
                    Paragraph("●", finding_id_style),
                    Paragraph(safe(finding), body_style),
                ]
            )

        findings_table = Table(
            finding_rows,
            colWidths=[7 * mm, 158 * mm],
        )

        findings_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), RED_LIGHT),
                    ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#FECACA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        story.append(findings_table)

    elif signals:
        for index, signal in enumerate(signals[:5], start=1):
            reason = (
                signal.get("reason")
                or signal.get("description")
                or signal.get("signal_type")
                or "Behavioral anomaly detected"
            )

            ids = ", ".join(
                str(x)
                for x in signal.get("transaction_ids", []) or []
            )

            text = safe(reason)

            if ids:
                text += f" <b>({safe(ids)})</b>"

            story.append(
                Paragraph(
                    f"● &nbsp; {text}",
                    bullet_style,
                )
            )

    else:
        story.append(
            Paragraph(
                "No transaction activity currently requires additional attention.",
                body_style,
            )
        )

    # =====================================================
    # IMPORTANT TRANSACTIONS
    # =====================================================

    story.append(
        Paragraph(
            "IMPORTANT TRANSACTIONS",
            section_style,
        )
    )

    if flagged_transactions:
        transaction_rows = [
            [
                Paragraph("TRANSACTION", transaction_header_style),
                Paragraph("DATE", transaction_header_style),
                Paragraph("PAYEE", transaction_header_style),
                Paragraph("AMOUNT", transaction_header_style),
                Paragraph("CHANNEL", transaction_header_style),
            ]
        ]

        for transaction in flagged_transactions[:12]:
            transaction_rows.append(
                [
                    Paragraph(
                        safe(transaction.get("transaction_id")),
                        transaction_id_style,
                    ),
                    Paragraph(
                        safe(transaction.get("date")),
                        transaction_style,
                    ),
                    Paragraph(
                        safe(transaction.get("payee")),
                        transaction_style,
                    ),
                    Paragraph(
                        amount(transaction.get("amount")),
                        transaction_amount_style,
                    ),
                    Paragraph(
                        safe(transaction.get("channel")),
                        transaction_style,
                    ),
                ]
            )

        transaction_table = Table(
            transaction_rows,
            colWidths=[
                31 * mm,
                28 * mm,
                48 * mm,
                29 * mm,
                29 * mm,
            ],
            repeatRows=1,
        )

        transaction_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
                    ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(transaction_table)

        if len(flagged_transactions) > 12:
            story.append(
                Spacer(1, 3)
            )
            story.append(
                Paragraph(
                    f"Showing 12 of {len(flagged_transactions)} flagged transactions. "
                    "All transaction IDs remain traceable to the uploaded data.",
                    small_style,
                )
            )

    else:
        story.append(
            Paragraph(
                "No transactions were flagged for review.",
                body_style,
            )
        )

    # =====================================================
    # AVAILABLE CUSTOMER BASELINE
    # =====================================================

    baseline_items = []

    median_amount = first_value(
        "median_amount",
        "amount_median",
    )

    typical_range = first_value(
        "typical_amount_range",
        "robust_typical_range",
        "typical_range",
    )

    frequency = first_value(
        "transactions_per_week",
        "median_transactions_per_week",
        "avg_transactions_per_week",
    )

    history_strength = first_value(
        "history_strength",
        "history_quality",
    )

    history_start = first_value(
        "history_start",
        "start_date",
    )

    history_end = first_value(
        "history_end",
        "end_date",
    )

    usual_channel = first_value(
        "usual_channel",
        "most_common_channel",
        "primary_channel",
    )

    if median_amount is not None:
        baseline_items.append(
            ("MEDIAN AMOUNT", safe(median_amount))
        )

    if typical_range is not None:
        baseline_items.append(
            ("TYPICAL RANGE", safe(typical_range))
        )

    if frequency is not None:
        baseline_items.append(
            ("FREQUENCY", f"{safe(frequency)} / week")
        )

    if history_strength is not None:
        baseline_items.append(
            ("HISTORY", safe(history_strength))
        )

    if history_start is not None or history_end is not None:
        start = safe(history_start or "—")
        end = safe(history_end or "—")

        baseline_items.append(
            ("ANALYSIS PERIOD", f"{start} → {end}")
        )

    if usual_channel is not None:
        baseline_items.append(
            ("USUAL CHANNEL", safe(usual_channel))
        )

    # Only show the section if information actually exists.
    if baseline_items:
        story.append(
            Paragraph(
                "CUSTOMER BASELINE",
                section_style,
            )
        )

        baseline_rows = []

        # Maximum four columns across the page.
        for start in range(0, len(baseline_items), 4):
            chunk = baseline_items[start:start + 4]

            labels = [
                Paragraph(item[0], label_style)
                for item in chunk
            ]

            values = [
                Paragraph(item[1], body_style)
                for item in chunk
            ]

            while len(labels) < 4:
                labels.append("")
                values.append("")

            baseline_rows.append(labels)
            baseline_rows.append(values)

        baseline_table = Table(
            baseline_rows,
            colWidths=[41.25 * mm] * 4,
        )

        baseline_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                    ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(baseline_table)

    # =====================================================
    # PAGE 2 — AI REPORT
    # =====================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "AI-GENERATED<br/>INVESTIGATION REPORT",
            ai_heading_style,
        )
    )

    story.append(
        Paragraph(
            f"Customer {safe(customer_id)} · Investigator-facing analysis",
            subtitle_style,
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=BORDER,
            spaceBefore=2,
            spaceAfter=7,
        )
    )

    # =====================================================
    # AI REPORT EXISTS
    # =====================================================

    if narrative:

        ai_assessment = narrative.get("assessment")

        if ai_assessment:
            story.append(
                Paragraph(
                    "ASSESSMENT",
                    ai_subheading_style,
                )
            )

            assessment_box = Table(
                [
                    [
                        Paragraph(
                            safe(ai_assessment),
                            body_style,
                        )
                    ]
                ],
                colWidths=[165 * mm],
            )

            assessment_box.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            BLUE_LIGHT,
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.7,
                            colors.HexColor("#BFDBFE"),
                        ),
                        ("LEFTPADDING", (0, 0), (-1, -1), 9),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )

            story.append(assessment_box)

        # -------------------------------------------------
        # AI KEY FINDINGS
        # -------------------------------------------------

        ai_findings = narrative.get("key_findings") or []

        if ai_findings:
            story.append(
                Paragraph(
                    "KEY FINDINGS",
                    ai_subheading_style,
                )
            )

            for finding in ai_findings[:6]:
                story.append(
                    Paragraph(
                        f"• &nbsp; {safe(finding)}",
                        bullet_style,
                    )
                )

        # -------------------------------------------------
        # BEHAVIORAL CHANGE
        # -------------------------------------------------

        behavioral_change = narrative.get("behavioral_change")

        if behavioral_change:
            story.append(
                Paragraph(
                    "BEHAVIORAL CHANGE",
                    ai_subheading_style,
                )
            )

            story.append(
                Paragraph(
                    safe(behavioral_change),
                    body_style,
                )
            )

        # -------------------------------------------------
        # PRIORITY
        # -------------------------------------------------

        ai_priority = narrative.get("investigator_priority")

        if ai_priority:
            story.append(
                Paragraph(
                    "INVESTIGATOR PRIORITY",
                    ai_subheading_style,
                )
            )

            if str(ai_priority).upper() == "HIGH":
                ai_priority_color = RED
                ai_priority_background = RED_LIGHT
            elif str(ai_priority).upper() == "MODERATE":
                ai_priority_color = AMBER
                ai_priority_background = AMBER_LIGHT
            else:
                ai_priority_color = GREEN
                ai_priority_background = GREEN_LIGHT

            ai_priority_style = ParagraphStyle(
                "AIPriority",
                parent=priority_style,
                textColor=ai_priority_color,
                fontSize=15,
                leading=17,
            )

            priority_box = Table(
                [
                    [
                        Paragraph(
                            safe(ai_priority),
                            ai_priority_style,
                        )
                    ]
                ],
                colWidths=[165 * mm],
            )

            priority_box.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            ai_priority_background,
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.7,
                            ai_priority_color,
                        ),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )

            story.append(priority_box)

        # -------------------------------------------------
        # RECOMMENDED REVIEW
        # -------------------------------------------------

        recommendations = narrative.get("recommended_review") or []

        if recommendations:
            story.append(
                Paragraph(
                    "RECOMMENDED REVIEW",
                    ai_subheading_style,
                )
            )

            for recommendation in recommendations[:6]:
                story.append(
                    Paragraph(
                        f"□ &nbsp; {safe(recommendation)}",
                        bullet_style,
                    )
                )

    # =====================================================
    # AI REPORT DOES NOT EXIST
    # =====================================================

    else:

        not_generated = Table(
            [
                [
                    Paragraph(
                        "<b>AI REPORT NOT GENERATED</b><br/><br/>"
                        "The deterministic transaction analysis is available "
                        "on page 1. An AI-generated investigation narrative has "
                        "not been generated for this case.<br/><br/>"
                        "Generate the AI report from the investigation dashboard "
                        "to include the investigator-facing analysis here.",
                        body_style,
                    )
                ]
            ],
            colWidths=[165 * mm],
        )

        not_generated.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        LIGHT,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.8,
                        BORDER,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        14,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        14,
                    ),
                ]
            )
        )

        story.append(
            Spacer(1, 10)
        )

        story.append(not_generated)

    # =====================================================
    # INVESTIGATOR NOTE
    # =====================================================

    story.append(
        Spacer(1, 10)
    )

    disclaimer = Table(
        [
            [
                Paragraph(
                    "<b>INVESTIGATOR NOTE</b><br/>"
                    "This report identifies behavioral anomalies and supporting "
                    "evidence for investigator review. It does not establish "
                    "that fraud occurred. Final judgment remains with the "
                    "investigator.",
                    small_style,
                )
            ]
        ],
        colWidths=[165 * mm],
    )

    disclaimer.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(disclaimer)

    # =====================================================
    # FOOTER
    # =====================================================

    def draw_footer(canvas, document):
        canvas.saveState()

        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)

        canvas.line(
            14 * mm,
            10 * mm,
            A4[0] - 14 * mm,
            10 * mm,
        )

        canvas.setFont("Helvetica", 6.8)
        canvas.setFillColor(MUTED)

        canvas.drawString(
            14 * mm,
            6 * mm,
            "Transaction Risk Investigation Assistant · PS06",
        )

        canvas.drawRightString(
            A4[0] - 14 * mm,
            6 * mm,
            f"Page {document.page} of 2",
        )

        canvas.restoreState()

    # =====================================================
    # BUILD
    # =====================================================

    doc.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )

    buffer.seek(0)

    return buffer