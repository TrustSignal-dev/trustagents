from __future__ import annotations

from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "proposal" / "grant-application.md"
OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT_FILE = OUTPUT_DIR / "trustagents-grant-application.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#10243E"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Kicker",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#3C617D"),
            spaceAfter=10,
            tracking=0.6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#10243E"),
            spaceBefore=12,
            spaceAfter=7,
            borderWidth=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCopy",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#1F2933"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Lead",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11.5,
            leading=15,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#23384D"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ListCopy",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#1F2933"),
        )
    )
    return styles


def escape_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("`", "")
    )


def parse_markdown(lines: list[str], styles) -> list:
    story = [
        Paragraph("TrustAgents", styles["Kicker"]),
        Paragraph("OpenAI Cybersecurity Grant Application Draft", styles["DocTitle"]),
        Paragraph(
            "Defensive-security research scaffold for synthetic compliance evidence integrity evaluation.",
            styles["Lead"],
        ),
        Spacer(1, 0.08 * inch),
    ]

    paragraph_buffer: list[str] = []
    bullet_buffer: list[str] = []
    number_buffer: list[str] = []

    def flush_paragraph():
        nonlocal paragraph_buffer
        if paragraph_buffer:
            text = " ".join(part.strip() for part in paragraph_buffer if part.strip())
            if text:
                story.append(Paragraph(escape_text(text), styles["BodyCopy"]))
            paragraph_buffer = []

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            items = [
                ListItem(Paragraph(escape_text(item), styles["ListCopy"]))
                for item in bullet_buffer
            ]
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    bulletFontName="Helvetica",
                    bulletFontSize=9,
                    leftIndent=16,
                    bulletOffsetY=3,
                )
            )
            story.append(Spacer(1, 0.08 * inch))
            bullet_buffer = []

    def flush_numbers():
        nonlocal number_buffer
        if number_buffer:
            items = [
                ListItem(Paragraph(escape_text(item), styles["ListCopy"]))
                for item in number_buffer
            ]
            story.append(
                ListFlowable(
                    items,
                    bulletType="1",
                    start="1",
                    leftIndent=18,
                )
            )
            story.append(Spacer(1, 0.08 * inch))
            number_buffer = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("# "):
            continue

        if not stripped:
            flush_paragraph()
            flush_bullets()
            flush_numbers()
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            flush_bullets()
            flush_numbers()
            story.append(Paragraph(escape_text(stripped[3:]), styles["SectionHeading"]))
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            flush_numbers()
            bullet_buffer.append(stripped[2:].strip())
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            flush_bullets()
            number_buffer.append(re.sub(r"^\d+\.\s+", "", stripped))
            continue

        paragraph_buffer.append(stripped)

    flush_paragraph()
    flush_bullets()
    flush_numbers()
    return story


def draw_page(canvas, doc):
    canvas.saveState()
    width, height = LETTER
    canvas.setStrokeColor(colors.HexColor("#D7E3EC"))
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, height - 0.55 * inch, width - doc.rightMargin, height - 0.55 * inch)
    canvas.line(doc.leftMargin, 0.6 * inch, width - doc.rightMargin, 0.6 * inch)

    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(colors.HexColor("#3C617D"))
    canvas.drawString(doc.leftMargin, height - 0.42 * inch, "TrustAgents")

    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(colors.HexColor("#6B7C8F"))
    canvas.drawRightString(width - doc.rightMargin, height - 0.42 * inch, "Grant Application Draft")
    canvas.drawString(doc.leftMargin, 0.42 * inch, "Synthetic data only. Defensive-security scope.")
    canvas.drawRightString(width - doc.rightMargin, 0.42 * inch, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source_text = SOURCE.read_text(encoding="utf-8").splitlines()
    styles = build_styles()

    doc = BaseDocTemplate(
        str(OUTPUT_FILE),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        title="TrustAgents Grant Application Draft",
        author="TrustSignal-Dev",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="grant", frames=[frame], onPage=draw_page)])

    story = parse_markdown(source_text, styles)
    doc.build(story)
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
