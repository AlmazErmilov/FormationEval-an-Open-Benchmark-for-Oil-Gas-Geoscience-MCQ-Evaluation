#!/usr/bin/env python3
"""
Export FormationEval benchmark JSON to a readable PDF.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Iterable
import unicodedata
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Flowable,
)


DEFAULT_INPUT = Path("data/benchmark/formationeval_v0.1.json")
DEFAULT_OUTPUT = Path("data/benchmark/formationeval_v0.1.pdf")
DEFAULT_FONT_DIR = Path("assets/fonts")

PALETTE = {
    "page_bg": colors.HexColor("#F6F5F2"),
    "accent_band": colors.HexColor("#E3E0DB"),
    "ink": colors.HexColor("#1F1F1F"),
    "ink_muted": colors.HexColor("#5E5B57"),
    "accent": colors.HexColor("#2B2A28"),
    "rule": colors.HexColor("#C9C4BE"),
    "meta_bg": colors.HexColor("#EEEAE4"),
    "answer_label_bg": colors.HexColor("#DFF3EA"),
}

SPACE_XS = 4
SPACE_SM = 6
SPACE_MD = 10
SPACE_LG = 14
SPACE_XL = 18
BAND_WIDTH = 8 * mm
FOOTER_OFFSET = 8 * mm
BASE_FONT_NAME = "NotoSans"
BOLD_FONT_NAME = "NotoSans-Bold"
MATH_FONT_NAME = "NotoSansMath"
SYMBOL_FALLBACK_CHARS: set[str] = set()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export FormationEval benchmark JSON to a styled PDF."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to benchmark JSON (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to output PDF (default: %(default)s)",
    )
    parser.add_argument(
        "--font-dir",
        type=Path,
        default=DEFAULT_FONT_DIR,
        help="Directory containing NotoSans-Regular.ttf, NotoSans-Bold.ttf, and NotoSansMath-Regular.ttf",
    )
    parser.add_argument(
        "--page-size",
        choices=["A4", "LETTER"],
        default="A4",
        help="Page size (default: %(default)s)",
    )
    parser.add_argument(
        "--questions-per-page",
        type=int,
        default=1,
        help="Number of questions per page (default: %(default)s)",
    )
    parser.add_argument(
        "--max-questions",
        type=int,
        default=0,
        help="Optional limit for quick runs (0 = all)",
    )
    parser.add_argument(
        "--group-by",
        choices=["none", "domain", "topic"],
        default="none",
        help="Group questions by domain or topic",
    )
    parser.add_argument(
        "--no-cover",
        action="store_true",
        help="Skip the cover page",
    )
    return parser.parse_args()


def register_fonts(font_dir: Path) -> dict[str, str]:
    regular = font_dir / "NotoSans-Regular.ttf"
    bold = font_dir / "NotoSans-Bold.ttf"
    math = font_dir / "NotoSansMath-Regular.ttf"
    if not regular.exists() or not bold.exists() or not math.exists():
        missing = [str(p) for p in (regular, bold, math) if not p.exists()]
        raise FileNotFoundError(
            "Missing font files: "
            + ", ".join(missing)
            + ". Download Noto Sans and Noto Sans Math or set --font-dir."
        )

    pdfmetrics.registerFont(TTFont(BASE_FONT_NAME, str(regular)))
    pdfmetrics.registerFont(TTFont(BOLD_FONT_NAME, str(bold)))
    pdfmetrics.registerFont(TTFont(MATH_FONT_NAME, str(math)))
    return {"base": BASE_FONT_NAME, "bold": BOLD_FONT_NAME, "math": MATH_FONT_NAME}


def normalize_text(text: str) -> str:
    if text is None:
        return ""
    raw = str(text)
    normalized = unicodedata.normalize("NFKD", raw)
    return normalized.encode("ascii", "ignore").decode("ascii")


def escape_text(text: str) -> str:
    if text is None:
        return ""
    raw = str(text)
    if not SYMBOL_FALLBACK_CHARS:
        return escape(raw).replace("\n", "<br/>")
    parts = []
    for ch in raw:
        if ch in SYMBOL_FALLBACK_CHARS:
            parts.append(f'<font face="{MATH_FONT_NAME}">{escape(ch)}</font>')
        else:
            parts.append(escape(ch))
    return "".join(parts).replace("\n", "<br/>")


def format_bool(value: bool | None) -> str:
    if value is None:
        return "unknown"
    return "yes" if value else "no"


def format_list(values: Iterable[str] | None) -> str:
    if not values:
        return "N/A"
    return ", ".join(values)


def build_styles(fonts: dict[str, str]) -> dict[str, ParagraphStyle]:
    return {
        "title": ParagraphStyle(
            "title",
            fontName=fonts["bold"],
            fontSize=24,
            leading=28,
            textColor=PALETTE["accent"],
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName=fonts["base"],
            fontSize=12,
            leading=16,
            textColor=PALETTE["ink_muted"],
            spaceAfter=16,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            fontName=fonts["bold"],
            fontSize=12,
            leading=16,
            textColor=PALETTE["accent"],
            spaceBefore=10,
            spaceAfter=6,
        ),
        "group_header": ParagraphStyle(
            "group_header",
            fontName=fonts["bold"],
            fontSize=15,
            leading=19,
            textColor=PALETTE["accent"],
            spaceBefore=SPACE_MD,
            spaceAfter=SPACE_SM,
        ),
        "meta_label": ParagraphStyle(
            "meta_label",
            fontName=fonts["bold"],
            fontSize=8.5,
            leading=11,
            textColor=PALETTE["ink_muted"],
        ),
        "meta_value": ParagraphStyle(
            "meta_value",
            fontName=fonts["base"],
            fontSize=9.5,
            leading=12,
            textColor=PALETTE["ink"],
        ),
        "question_index": ParagraphStyle(
            "question_index",
            fontName=fonts["bold"],
            fontSize=11,
            leading=14,
            textColor=PALETTE["accent"],
        ),
        "question_id": ParagraphStyle(
            "question_id",
            fontName=fonts["base"],
            fontSize=9,
            leading=12,
            textColor=PALETTE["ink_muted"],
            alignment=2,
        ),
        "question_text": ParagraphStyle(
            "question_text",
            fontName=fonts["bold"],
            fontSize=12.5,
            leading=16,
            textColor=PALETTE["ink"],
            spaceAfter=6,
        ),
        "choice_label": ParagraphStyle(
            "choice_label",
            fontName=fonts["bold"],
            fontSize=10,
            leading=12,
            textColor=PALETTE["accent"],
        ),
        "choice_text": ParagraphStyle(
            "choice_text",
            fontName=fonts["base"],
            fontSize=10.5,
            leading=13,
            textColor=PALETTE["ink"],
        ),
        "answer_label": ParagraphStyle(
            "answer_label",
            fontName=fonts["bold"],
            fontSize=10,
            leading=13,
            textColor=PALETTE["ink"],
        ),
        "answer_line": ParagraphStyle(
            "answer_line",
            fontName=fonts["base"],
            fontSize=10.5,
            leading=13,
            textColor=PALETTE["ink"],
            spaceBefore=4,
            spaceAfter=6,
        ),
        "rationale_text": ParagraphStyle(
            "rationale_text",
            fontName=fonts["base"],
            fontSize=10,
            leading=14,
            textColor=PALETTE["ink"],
        ),
        "source_title": ParagraphStyle(
            "source_title",
            fontName=fonts["bold"],
            fontSize=9.5,
            leading=12,
            textColor=PALETTE["accent"],
            spaceAfter=4,
        ),
        "source_label": ParagraphStyle(
            "source_label",
            fontName=fonts["bold"],
            fontSize=8.5,
            leading=10.5,
            textColor=PALETTE["ink_muted"],
        ),
        "source_text": ParagraphStyle(
            "source_text",
            fontName=fonts["base"],
            fontSize=9,
            leading=12,
            textColor=PALETTE["ink"],
        ),
        "cover_stat_label": ParagraphStyle(
            "cover_stat_label",
            fontName=fonts["bold"],
            fontSize=10,
            leading=12,
            textColor=PALETTE["accent"],
        ),
        "cover_stat_value": ParagraphStyle(
            "cover_stat_value",
            fontName=fonts["base"],
            fontSize=10,
            leading=12,
            textColor=PALETTE["ink"],
        ),
    }


def slugify(value: str) -> str:
    slug = normalize_text(value).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "group"


def truncate_text(text: str, limit: int = 70) -> str:
    cleaned = normalize_text(text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


class BookmarkFlowable(Flowable):
    def __init__(self, key: str, title: str, level: int = 0) -> None:
        super().__init__()
        self.key = key
        self.title = title
        self.level = level

    def wrap(self, availWidth, availHeight):
        return (0, 0)

    def draw(self):
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.title, self.key, level=self.level, closed=False)


def group_items(data: list[dict], group_by: str) -> list[tuple[str | None, list[dict]]]:
    if group_by == "none":
        return [(None, data)]

    key_field = "domains" if group_by == "domain" else "topics"
    grouped: dict[str, list[dict]] = {}
    order: list[str] = []
    for item in data:
        values = item.get(key_field) or []
        group_key = values[0] if values else "Unknown"
        if group_key not in grouped:
            grouped[group_key] = []
            order.append(group_key)
        grouped[group_key].append(item)
    return [(key, grouped[key]) for key in order]


def iter_text_values(data: list[dict]) -> Iterable[str]:
    for item in data:
        yield item.get("id", "")
        yield item.get("version", "")
        yield item.get("question", "")
        for choice in item.get("choices", []):
            yield choice
        yield item.get("rationale", "")
        for value in item.get("domains", []) or []:
            yield value
        for value in item.get("topics", []) or []:
            yield value
        for key in ("difficulty", "language", "derivation_mode"):
            yield item.get(key, "")
        metadata = item.get("metadata", {})
        for value in metadata.values():
            if isinstance(value, str):
                yield value
        for src in item.get("sources", []):
            for value in src.values():
                if isinstance(value, str):
                    yield value


def build_symbol_fallback(
    data: list[dict], base_font_name: str, math_font_name: str
) -> set[str]:
    base_font = pdfmetrics.getFont(base_font_name)
    math_font = pdfmetrics.getFont(math_font_name)
    base_chars = base_font.face.charWidths
    math_chars = math_font.face.charWidths

    missing = set()
    for text in iter_text_values(data):
        for ch in text:
            code = ord(ch)
            if code <= 127:
                continue
            if code not in base_chars and code in math_chars:
                missing.add(ch)
    return missing
def build_cover_page(
    data: list[dict],
    styles: dict[str, ParagraphStyle],
    content_width: float,
    input_path: Path,
) -> list:
    story: list = []
    story.append(Paragraph("FormationEval v0.1", styles["title"]))
    story.append(
        Paragraph(
            "Benchmark questions, answers, rationales, and sources.",
            styles["subtitle"],
        )
    )

    source_counts: Counter[str] = Counter()
    source_titles: dict[str, str] = {}
    for item in data:
        sources = item.get("sources", [])
        if not sources:
            source_counts["unknown"] += 1
            continue
        for src in sources:
            source_id = src.get("source_id", "unknown")
            source_counts[source_id] += 1
            if src.get("source_id"):
                source_titles[source_id] = src.get("source_title", source_id)

    stats = [
        ("Questions", str(len(data))),
        ("Source IDs", str(len(source_counts))),
        ("Generated", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
        ("Input file", str(input_path)),
    ]
    stat_rows = [
        [
            Paragraph(label, styles["cover_stat_label"]),
            Paragraph(escape_text(value), styles["cover_stat_value"]),
        ]
        for label, value in stats
    ]
    stat_table = Table(stat_rows, colWidths=[30 * mm, content_width - 30 * mm])
    stat_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALETTE["meta_bg"]),
                ("BOX", (0, 0), (-1, -1), 0.5, PALETTE["rule"]),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, PALETTE["rule"]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(stat_table)
    story.append(Spacer(1, SPACE_LG))
    story.append(Paragraph("Sources used", styles["section_header"]))

    source_rows = []
    for source_id, count in sorted(source_counts.items()):
        title = source_titles.get(source_id, source_id)
        source_rows.append(
            Paragraph(
                f"{escape_text(title)} ({escape_text(source_id)}) - {count} references",
                styles["source_text"],
            )
        )
    story.extend(source_rows)
    return story


def build_metadata_table(
    item: dict, styles: dict[str, ParagraphStyle], content_width: float
) -> Table:
    metadata = item.get("metadata", {})
    meta_rows = [
        ("ID", item.get("id", "unknown")),
        ("Domains", format_list(item.get("domains"))),
        ("Topics", format_list(item.get("topics"))),
        ("Difficulty", item.get("difficulty", "unknown")),
        ("Language", item.get("language", "unknown")),
        ("Derivation", item.get("derivation_mode", "unknown")),
        ("Calc required", format_bool(metadata.get("calc_required"))),
        ("Contamination risk", metadata.get("contamination_risk", "unknown")),
    ]

    rows = [
        [
            Paragraph(escape_text(label), styles["meta_label"]),
            Paragraph(escape_text(value), styles["meta_value"]),
        ]
        for label, value in meta_rows
    ]

    table = Table(rows, colWidths=[32 * mm, content_width - 32 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALETTE["meta_bg"]),
                ("BOX", (0, 0), (-1, -1), 0.5, PALETTE["rule"]),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, PALETTE["rule"]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def build_choices_table(
    item: dict, styles: dict[str, ParagraphStyle], content_width: float
) -> Table:
    choices = item.get("choices", [])
    letters = ["A", "B", "C", "D"]

    rows = []
    for idx, choice in enumerate(choices):
        label = Paragraph(f"<b>{letters[idx]}</b>", styles["choice_label"])
        text = Paragraph(escape_text(choice), styles["choice_text"])
        rows.append([label, text])

    table = Table(rows, colWidths=[12 * mm, content_width - 12 * mm])
    style = TableStyle(
        [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, PALETTE["rule"]),
        ]
    )
    table.setStyle(style)
    return table


def build_sources_block(
    sources: list[dict],
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> list:
    story: list = []
    for idx, src in enumerate(sources, 1):
        title = escape_text(src.get("source_title", "Unknown source"))
        url = src.get("source_url", "")
        if url:
            title_html = f'<link href="{url}">{title}</link>'
        else:
            title_html = title

        story.append(
            Paragraph(f"Source {idx}: {title_html}", styles["source_title"])
        )

        ref = src.get("chapter_ref") or src.get("lecture_ref") or ""
        details = [
            ("Source ID", src.get("source_id", "")),
            ("Year", str(src.get("year", ""))),
            ("Type", src.get("source_type", "")),
            ("License", src.get("license", "")),
            ("Attribution", src.get("attribution", "")),
            ("Reference", ref),
            ("Retrieved", src.get("retrieved_at", "")),
            ("URL", src.get("source_url", "")),
            ("Notes", src.get("notes", "")),
        ]
        rows = []
        for label, value in details:
            if not value:
                continue
            rows.append(
                [
                    Paragraph(escape_text(label), styles["source_label"]),
                    Paragraph(escape_text(value), styles["source_text"]),
                ]
            )
        if rows:
            table = Table(rows, colWidths=[28 * mm, content_width - 28 * mm])
            table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ("LINEBELOW", (0, 0), (-1, -1), 0.25, PALETTE["rule"]),
                    ]
                )
            )
            story.append(table)
        story.append(Spacer(1, SPACE_SM))
    return story


def build_question_block(
    item: dict,
    index: int,
    total: int,
    styles: dict[str, ParagraphStyle],
    content_width: float,
    outline_level: int,
) -> list:
    story: list = []
    bookmark_title = f"Q{index}: {truncate_text(item.get('question', ''))}"
    story.append(BookmarkFlowable(f"q{index}", bookmark_title, level=outline_level))
    header_table = Table(
        [
            [
                Paragraph(f"Question {index} of {total}", styles["question_index"]),
                Paragraph(f"ID: {escape_text(item.get('id', 'unknown'))}", styles["question_id"]),
            ]
        ],
        colWidths=[content_width * 0.55, content_width * 0.45],
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(header_table)
    story.append(build_metadata_table(item, styles, content_width))
    story.append(Spacer(1, SPACE_MD))
    story.append(Paragraph(escape_text(item.get("question", "")), styles["question_text"]))
    story.append(build_choices_table(item, styles, content_width))

    letters = ["A", "B", "C", "D"]
    answer_index = item.get("answer_index")
    if answer_index is None and item.get("answer_key") in letters:
        answer_index = letters.index(item["answer_key"])
    answer_letter = letters[answer_index] if answer_index is not None else "?"
    answer_text = ""
    choices = item.get("choices", [])
    if answer_index is not None and 0 <= answer_index < len(choices):
        answer_text = choices[answer_index]

    answer_label = Paragraph("Correct answer:", styles["answer_label"])
    answer_value = Paragraph(
        f"{answer_letter} - {escape_text(answer_text)}", styles["answer_line"]
    )
    answer_table = Table(
        [[answer_label, answer_value]],
        colWidths=[34 * mm, content_width - 34 * mm],
    )
    answer_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), PALETTE["answer_label_bg"]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(answer_table)
    story.append(Paragraph("Rationale", styles["section_header"]))
    story.append(Paragraph(escape_text(item.get("rationale", "")), styles["rationale_text"]))
    story.append(Paragraph("Sources", styles["section_header"]))
    story.extend(build_sources_block(item.get("sources", []), styles, content_width))
    return story


def on_page_factory(version: str, fonts: dict[str, str], include_cover: bool):
    def on_page(canvas, doc):
        width, height = doc.pagesize
        canvas.saveState()
        canvas.setFillColor(PALETTE["page_bg"])
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.setFillColor(PALETTE["accent_band"])
        canvas.rect(0, 0, BAND_WIDTH, height, fill=1, stroke=0)
        canvas.setFillColor(PALETTE["ink_muted"])
        canvas.setFont(fonts["base"], 8)
        if not (include_cover and doc.page == 1):
            canvas.drawString(doc.leftMargin, FOOTER_OFFSET, f"FormationEval {version}")
            canvas.drawRightString(
                width - doc.rightMargin, FOOTER_OFFSET, f"Page {doc.page}"
            )
        canvas.restoreState()

    return on_page


def main() -> None:
    args = parse_args()
    fonts = register_fonts(args.font_dir)
    styles = build_styles(fonts)

    with args.input.open("r", encoding="utf-8") as f:
        data = json.load(f)

    global SYMBOL_FALLBACK_CHARS
    SYMBOL_FALLBACK_CHARS = build_symbol_fallback(
        data, fonts["base"], fonts["math"]
    )

    if args.max_questions and args.max_questions > 0:
        data = data[: args.max_questions]

    page_size = A4 if args.page_size == "A4" else LETTER
    doc = SimpleDocTemplate(
        str(args.output),
        pagesize=page_size,
        leftMargin=20 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="FormationEval v0.1 benchmark",
        author="FormationEval",
    )
    content_width = page_size[0] - doc.leftMargin - doc.rightMargin

    story: list = []
    if not args.no_cover:
        story.extend(build_cover_page(data, styles, content_width, args.input))
        story.append(PageBreak())

    total = len(data)
    questions_per_page = max(args.questions_per_page, 1)
    grouped = group_items(data, args.group_by)
    question_outline_level = 1 if args.group_by != "none" else 0
    questions_on_page = 0
    global_index = 0

    for group_index, (group_name, items) in enumerate(grouped):
        if group_name:
            if group_index != 0:
                story.append(PageBreak())
            group_title = f"{group_name} ({len(items)} questions)"
            story.append(
                BookmarkFlowable(
                    f"group-{slugify(group_name)}",
                    truncate_text(group_title, 80),
                    level=0,
                )
            )
            story.append(Paragraph(group_title, styles["group_header"]))
            story.append(Spacer(1, SPACE_SM))
            questions_on_page = 0

        for item in items:
            global_index += 1
            story.extend(
                build_question_block(
                    item,
                    global_index,
                    total,
                    styles,
                    content_width,
                    outline_level=question_outline_level,
                )
            )

            is_last = global_index == total
            questions_on_page += 1
            if not is_last:
                if questions_per_page == 1 or questions_on_page >= questions_per_page:
                    story.append(PageBreak())
                    questions_on_page = 0
                else:
                    story.append(Spacer(1, SPACE_MD))
                    story.append(
                        HRFlowable(
                            width="100%", thickness=0.5, color=PALETTE["rule"]
                        )
                    )
                    story.append(Spacer(1, SPACE_MD))

    version = data[0].get("version", "v0.1") if data else "v0.1"
    doc.build(
        story,
        onFirstPage=on_page_factory(version, fonts, not args.no_cover),
        onLaterPages=on_page_factory(version, fonts, not args.no_cover),
    )


if __name__ == "__main__":
    main()
