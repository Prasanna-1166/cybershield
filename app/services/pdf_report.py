"""
pdf_report.py
--------------
WHAT: Renders the same data as dashboard/report.html into a downloadable
      PDF, using reportlab (a lightweight pure-Python library — no system
      dependencies like wkhtmltopdf/Cairo, so it works on any host without
      extra setup).
WHY:  The brief asks for a print-friendly report; a real PDF export is a
      small addition on top of that using data we already compute in
      report_service.build_report(), not a new data source.
WHERE: app/services/pdf_report.py — called from GET /report/pdf in
       app/routes/main.py.
"""

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#0b1a2b")
ACCENT = colors.HexColor("#1f9d8f")
MUTED = colors.HexColor("#566072")


def build_report_pdf(user_display_name: str, data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
        title="CyberShield Cyber Safety Report",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CSTitle", parent=styles["Title"], textColor=NAVY, fontSize=20)
    h2 = ParagraphStyle("CSH2", parent=styles["Heading2"], textColor=NAVY, spaceBefore=14, fontSize=13)
    body = ParagraphStyle("CSBody", parent=styles["BodyText"], textColor=colors.black, fontSize=10.5, leading=15)
    muted = ParagraphStyle("CSMuted", parent=styles["BodyText"], textColor=MUTED, fontSize=9.5)

    story = [
        Paragraph("CyberShield — Personalized Cyber Safety Report", title_style),
        Paragraph(f"Prepared for {user_display_name}", muted),
        Spacer(1, 10 * mm),
    ]

    summary_rows = [
        ["Cyber Safety Score", f"{data.get('security_score', 0)} / 100 — {data.get('security_score_classification', '')}"],
        ["Rank", data.get("rank", "Newcomer")],
        ["Overall Score (XP)", str(data.get("overall_score", 0))],
        ["Training Accuracy", f"{data.get('overall_accuracy_percent', 0)}%"],
        ["Levels Completed", f"{data.get('levels_completed', 0)} / {data.get('total_levels', 0)}"],
        ["Hints Used", str(data.get("hints_used", 0))],
        ["Avg Response Time", f"{data.get('avg_response_time_seconds', 0)}s"],
    ]
    table = Table(summary_rows, colWidths=[70 * mm, 90 * mm])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e1e6ec")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    if data.get("before_assessment_percent") is not None and data.get("after_assessment_percent") is not None:
        story.append(Paragraph("Before / After Assessment", h2))
        improvement = data.get("improvement_percent", 0)
        sign = "+" if improvement is not None and improvement >= 0 else ""
        story.append(Paragraph(
            f"Before training: <b>{data['before_assessment_percent']}%</b> &rarr; "
            f"After training: <b>{data['after_assessment_percent']}%</b> &rarr; "
            f"Improvement: <b>{sign}{improvement}%</b>",
            body,
        ))

    story.append(Paragraph("Performance by Level", h2))
    level_rows = [["Level", "Attempts", "Accuracy"]]
    for entry in data.get("per_level_performance", []):
        level_rows.append([entry["level_name"], str(entry["attempts"]), f"{entry['accuracy_percent']}%"])
    if len(level_rows) > 1:
        level_table = Table(level_rows, colWidths=[90 * mm, 30 * mm, 30 * mm])
        level_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e1e6ec")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(level_table)
    else:
        story.append(Paragraph("No training attempts yet.", muted))

    story.append(Paragraph("Security Strengths", h2))
    strong = data.get("strong_areas") or []
    story.append(
        ListFlowable([ListItem(Paragraph(a, body)) for a in strong], bulletType="bullet")
        if strong else Paragraph("Keep training to build strong areas.", muted)
    )

    story.append(Paragraph("Areas Needing Improvement", h2))
    weak = data.get("weak_areas") or []
    story.append(
        ListFlowable([ListItem(Paragraph(a, body)) for a in weak], bulletType="bullet")
        if weak else Paragraph("No weak areas detected yet.", muted)
    )

    recs = data.get("recommended_lesson_categories") or []
    if recs:
        story.append(Paragraph("Recommended Lessons", h2))
        story.append(ListFlowable(
            [ListItem(Paragraph(cat.replace("_", " ").title(), body)) for cat in recs],
            bulletType="bullet",
        ))

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        "CyberShield is an educational platform. This report reflects in-app training and "
        "assessment activity only and is not a professional security audit.",
        muted,
    ))

    doc.build(story)
    return buffer.getvalue()
