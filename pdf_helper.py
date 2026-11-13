
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)


def generate_roadmap_pdf(user_input, roadmap):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=27,
        textColor=colors.HexColor("#7653C5"),
        alignment=TA_CENTER,
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#7653C5"),
        spaceBefore=12,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=6
    )

    story = []

    def safe_text(value):
        return escape(str(value or "")).encode(
            "ascii", "xmlcharrefreplace"
        ).decode("ascii")

    # Title
    story.append(Paragraph(
        "AI Skill Development Roadmap Generator",
        title_style
    ))

    story.append(Paragraph(
        "Your Personalized Learning Plan",
        ParagraphStyle(
            "Subtitle",
            parent=normal_style,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#777777")
        )
    ))

    story.append(Spacer(1, 20))

    # Student details
    story.append(Paragraph("Student Information", heading_style))

    details = [
        ["Student Name", safe_text(user_input.get("full_name", ""))],
        ["Career Goal", safe_text(user_input.get("career_goal", ""))],
        ["Skill Level", safe_text(user_input.get("skill_level", ""))],
        ["Daily Learning Time", safe_text(user_input.get("daily_time", ""))],
        ["Budget", safe_text(user_input.get("budget", ""))],
        ["Language", safe_text(user_input.get("preferred_language", ""))]
    ]

    details_table = Table(
        details,
        colWidths=[150, 310]
    )

    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEE9FF")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#493477")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8D0EE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(details_table)
    story.append(Spacer(1, 18))

    # Roadmap details
    story.append(Paragraph("Your Learning Roadmap", heading_style))

    story.append(Paragraph(
        safe_text(roadmap.get("title", "Learning Roadmap")),
        normal_style
    ))

    story.append(Paragraph(
        safe_text(roadmap.get("description", "")),
        normal_style
    ))

    # Weekly plans
    for week in roadmap.get("weeks", []):

        week_number = week.get("week_number", "")
        theme = safe_text(week.get("theme", "Learning Week"))

        week_content = []

        week_content.append(Paragraph(
            f"Week {safe_text(week_number)}: {theme}",
            heading_style
        ))

        week_content.append(Paragraph(
            "<b>Topics to Learn:</b>",
            normal_style
        ))

        topics = week.get("topics", [])

        if topics:
            for topic in topics:
                week_content.append(Paragraph(
                    f"- {safe_text(topic)}",
                    normal_style
                ))
        else:
            week_content.append(Paragraph(
                "No topics provided.",
                normal_style
            ))

        assignment = safe_text(
            week.get("practical_assignment", "")
        )

        if assignment:
            week_content.append(Paragraph(
                f"<b>Practical Assignment:</b> {assignment}",
                normal_style
            ))

        mini_project = safe_text(
            week.get("mini_project", "")
        )

        if mini_project:
            week_content.append(Paragraph(
                f"<b>Mini Project:</b> {mini_project}",
                normal_style
            ))

        story.append(KeepTogether(week_content))
        story.append(Spacer(1, 10))

    # Footer
    story.append(Spacer(1, 15))

    story.append(Paragraph(
        "Generated by AI Skill Development Roadmap Generator",
        ParagraphStyle(
            "Footer",
            parent=normal_style,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#777777"),
            fontSize=8
        )
    ))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
