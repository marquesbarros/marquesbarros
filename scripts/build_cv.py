"""Build the two downloadable CVs from their public HTML source.

Run: uv run --no-project --with reportlab python scripts/build_cv.py
ReportLab is an authoring dependency only; the website remains fully static.
"""

import argparse
import re
from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def descendants(self, tag=None):
        for child in self.children:
            if isinstance(child, Element):
                if tag is None or child.tag == tag:
                    yield child
                yield from child.descendants(tag)

    def first(self, tag):
        return next(self.descendants(tag))

    def by_class(self, name):
        return next(
            node for node in self.descendants()
            if name in node.attrs.get("class", "").split()
        )

    def plain(self):
        return "".join(
            child.plain() if isinstance(child, Element) else child
            for child in self.children
        )


class DocumentParser(HTMLParser):
    VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                      "link", "meta", "param", "source", "track", "wbr"})

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Element(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def clean(text):
    text = text.translate(str.maketrans({
        "–": "-", "—": "-", "‑": "-", "−": "-", "↗": "", "↓": "",
        "\u00ad": "", "\u00a0": " ",
    }))
    return re.sub(r"\s+", " ", text).strip()


def rich(node):
    """Retain inline emphasis and public links; discard browser-only markup."""
    if isinstance(node, str):
        return escape(node.translate(str.maketrans({
            "–": "-", "—": "-", "‑": "-", "−": "-", "↗": "", "↓": "",
            "\u00ad": "", "\u00a0": " ",
        })))
    contents = "".join(rich(child) for child in node.children)
    if node.tag in {"strong", "b"}:
        return f"<b>{contents}</b>"
    if node.tag in {"em", "i"}:
        return f"<i>{contents}</i>"
    if node.tag == "a":
        href = node.attrs.get("href", "")
        if href.startswith(("https://", "http://", "mailto:")):
            return f'<a href="{escape(href, quote=True)}" color="#285943">{contents}</a>'
    return contents


def build(source, target, language):
    parser = DocumentParser()
    parser.feed(source.read_text(encoding="utf-8"))
    root = parser.root
    title = root.by_class("inner-top")
    green = colors.HexColor("#285943")
    ink = colors.HexColor("#1d2921")
    muted = colors.HexColor("#535d57")
    line = colors.HexColor("#d4dbd5")

    body = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=9.5, leading=12.1,
        textColor=ink, spaceAfter=4, alignment=TA_LEFT,
        allowWidows=0, allowOrphans=0,
    )
    styles = {
        "body": body,
        "name": ParagraphStyle("Name", parent=body, fontName="Helvetica-Bold",
                               fontSize=24, leading=28, spaceAfter=5),
        "profession": ParagraphStyle("Profession", parent=body, fontSize=12,
                                     leading=16, textColor=green, spaceAfter=8),
        "section": ParagraphStyle("Section", parent=body, fontName="Helvetica-Bold",
                                  fontSize=11, leading=15, textColor=green,
                                  spaceBefore=9, spaceAfter=6),
        "group": ParagraphStyle("Group", parent=body, fontName="Helvetica-Bold",
                                fontSize=9.8, leading=13, textColor=green,
                                spaceBefore=5, spaceAfter=5),
        "entry": ParagraphStyle("Entry", parent=body, fontName="Helvetica-Bold",
                                spaceAfter=3, keepWithNext=True),
        "date": ParagraphStyle("Date", parent=body, fontSize=8.5,
                               leading=11.5, textColor=muted),
        "small": ParagraphStyle("Small", parent=body, fontSize=8.5,
                                leading=11.5, textColor=muted),
    }
    doc = SimpleDocTemplate(
        str(target), pagesize=A4, leftMargin=17 * mm, rightMargin=17 * mm,
        topMargin=17 * mm, bottomMargin=18 * mm,
        title=f'Lucas Marques Barros - {"Currículo" if language == "pt" else "CV"}',
        author="Lucas Marques Barros",
        subject="Geólogo" if language == "pt" else "Geologist",
    )

    def paragraph(node, style="body"):
        return Paragraph(rich(node), styles[style])

    story = [
        Paragraph(escape(clean(title.first("h1").plain()).removesuffix(".")), styles["name"]),
        Paragraph("Geólogo" if language == "pt" else "Geologist", styles["profession"]),
        paragraph(title.first("p")),
        Paragraph(" &nbsp; | &nbsp; ".join(
            rich(link) for link in title.by_class("cv-meta").descendants("a")
        ), styles["small"]),
        Spacer(1, 3),
    ]
    sections = [node for node in root.descendants("section")
                if "cv-section" in node.attrs.get("class", "").split()]
    for section in sections:
        heading = paragraph(section.first("h2"), "section")
        lists = [node for node in section.descendants("ul")
                 if "cv-list" in node.attrs.get("class", "").split()]
        if lists:
            first = True
            for item in lists[0].children:
                if not isinstance(item, Element) or item.tag != "li":
                    continue
                date, details = [child for child in item.children
                                 if isinstance(child, Element)]
                text = [paragraph(details.first("strong"), "entry")]
                text.extend(paragraph(p) for p in details.descendants("p"))
                row = Table([[paragraph(date, "date"), text]],
                            colWidths=[67, doc.width - 67], hAlign="LEFT")
                row.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (0, 0), 10),
                    ("RIGHTPADDING", (1, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]))
                story.append(KeepTogether([heading, row]) if first else row)
                first = False
        elif section.attrs.get("aria-labelledby") == "cv-producao":
            groups = [node for node in section.descendants("div")
                      if "publication-group" in node.attrs.get("class", "").split()]
            pending = [heading]
            for group in groups:
                pending.append(paragraph(group.first("h3"), "group"))
                for item in group.descendants("li"):
                    entry = [paragraph(item.first("h4"), "entry")]
                    entry.extend(paragraph(p) for p in item.descendants("p"))
                    entry.append(Spacer(1, 3))
                    story.append(KeepTogether(pending + entry))
                    pending = []
            story.append(paragraph(section.by_class("publication-note"), "small"))
        elif any("cv-tags" in node.attrs.get("class", "").split()
                 for node in section.descendants("div")):
            tags = section.by_class("cv-tags")
            tags_paragraph = Paragraph(" · ".join(
                escape(clean(tag.plain())) for tag in tags.descendants("span")
            ), body)
            story.append(KeepTogether([heading, tags_paragraph]))
        else:
            first = True
            for p in section.descendants("p"):
                story.append(KeepTogether([heading, paragraph(p)]) if first else paragraph(p))
                first = False

    def page_details(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(line)
        canvas.setLineWidth(0.5)
        canvas.line(document.leftMargin, 13 * mm,
                    A4[0] - document.rightMargin, 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(muted)
        label = "Currículo" if language == "pt" else "CV"
        canvas.drawString(document.leftMargin, 9 * mm, f"Lucas Marques Barros | {label}")
        page_label = "Página" if language == "pt" else "Page"
        canvas.drawRightString(A4[0] - document.rightMargin, 9 * mm,
                               f"{page_label} {document.page}")
        if document.page > 1:
            canvas.setFont("Helvetica", 8)
            canvas.drawString(document.leftMargin, A4[1] - 10 * mm,
                              "Lucas Marques Barros | " + label)
        canvas.restoreState()

    target.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story, onFirstPage=page_details, onLaterPages=page_details)
    print(f"Generated {target}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()
    output = args.out_dir or args.root / "assets"
    for source, filename, language in (
        ("curriculo.html", "Lucas_Marques_Barros_CV_2026.pdf", "pt"),
        ("en/cv.html", "Lucas_Marques_Barros_CV_EN_2026.pdf", "en"),
    ):
        build(args.root / source, output / filename, language)


if __name__ == "__main__":
    main()
