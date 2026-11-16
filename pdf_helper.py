"""PDF generation helper for the AI Skill Roadmap Generator."""

from io import BytesIO
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from xml.sax.saxutils import escape


def _to_text(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def _paragraph(text, style):
    safe = escape(_to_text(text)).replace("\n", "<br/>")
    return Paragraph(safe or " ", style)


def generate_roadmap_pdf(roadmap, *args, **kwargs):
    """Return a PDF as bytes. Accepts a dict, list, string, or SQLite row-like object."""
    if hasattr(roadmap, "keys"):
        try:
            data = {key: roadmap[key] for key in roadmap.keys()}
        except Exception:
            data = dict(roadmap)
    elif isinstance(roadmap, dict):
        data = roadmap
    else:
        data = {"Roadmap": roadmap}

    # Unpack a JSON roadmap stored by the app, when possible.
    for key in ("roadmap_json", "roadmap_data", "content"):
        raw = data.get(key)
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, (dict, list)):
                    data["Roadmap Details"] = parsed
            except (ValueError, TypeError):
                pass

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=0.65 * inch, leftMargin=0.65 * inch,
        topMargin=0.65 * inch, bottomMargin=0.65 * inch,
        title="AI Skill Roadmap"
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "RoadmapTitle", parent=styles["Title"], alignment=TA_CENTER,
        textColor=colors.HexColor("#174A8B"), spaceAfter=18
    )
    heading_style = ParagraphStyle(
        "RoadmapHeading", parent=styles["Heading2"],
        textColor=colors.HexColor("#174A8B"), spaceBefore=12, spaceAfter=6
    )
    body_style = styles["BodyText"]
    story = [Paragraph("AI Skill Development Roadmap", title_style)]

    preferred_order = [
        "roadmap_title", "full_name", "career_goal", "skill_level",
        "daily_time", "budget", "preferred_language", "created_at"
    ]
    labels = {
        "roadmap_title": "Roadmap Title", "full_name": "Student Name",
        "career_goal": "Career Goal", "skill_level": "Skill Level",
        "daily_time": "Daily Study Time", "budget": "Budget",
        "preferred_language": "Preferred Language", "created_at": "Created On"
    }
    rows = []
    for key in preferred_order:
        if key in data and data[key] not in (None, ""):
            rows.append([labels.get(key, key.replace("_", " ").title()), _to_text(data[key])])
    if rows:
        table = Table(rows, colWidths=[1.65 * inch, 4.9 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2FC")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#202A35")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C8D7EA")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([table, Spacer(1, 14)])

    excluded = set(preferred_order) | {"roadmap_json", "roadmap_data", "content"}
    for key, value in data.items():
        if key in excluded or value in (None, ""):
            continue
        story.append(_paragraph(key.replace("_", " ").title(), heading_style))
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for subkey, subvalue in item.items():
                        story.append(_paragraph(f"{subkey.replace('_', ' ').title()}: {_to_text(subvalue)}", body_style))
                    story.append(Spacer(1, 5))
                else:
                    story.append(_paragraph(f"• {_to_text(item)}", body_style))
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                story.append(_paragraph(subkey.replace("_", " ").title(), heading_style))
                story.append(_paragraph(subvalue, body_style))
        else:
            story.append(_paragraph(value, body_style))
        story.append(Spacer(1, 7))

    if len(story) == 1:
        story.append(_paragraph(data, body_style))

    doc.build(story)
    return buffer.getvalue()
