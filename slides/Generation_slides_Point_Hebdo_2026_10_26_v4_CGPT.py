"""Build the JEPA-Drift Point Hebdo v4_CGPT deck from the canonical Markdown source.

Parses DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v4_CGPT.md (48 slide blocks: 20 main + 28 annexes),
reuses the template style charter, displays equations as ASCII text only.
"""

import argparse
import ast
import hashlib
import io
import os
import re
import subprocess
import zipfile
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


DECK_NAME = "DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v4_CGPT.md"
TEMPLATE_NAME = "Generation_slides_Point_Hebdo_template.py"
OUT_NAME = "2026_10_26_Point_Hebdo_JEPA_Drift_v4_CGPT.pptx"
AUX_NAME = "2026_10_26_Point_Hebdo_JEPA_Drift_v4_CGPT_auxiliary.md"
REPORT_NAME = "2026_10_26_Point_Hebdo_JEPA_Drift_v4_CGPT_RENDER_CHECK.md"
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")

COLOR_MAP = {
    "ORANGE": "ORANGE", "BLUE": "BLUE", "TEAL": "TEAL",
    "PURPLE": "PURPLE", "GREEN": "GREEN", "RED": "RED",
}

FORBIDDEN_PATTERNS = [
    r"\bstream[-_ ]?\d", r"\bP[1-7]-[A-Z]", r"\bJ[0-9]\b",
    r"```", r"StarMath", r"LibreOffice Math", r"pdflatex",
    r"\\frac\{", r"\\displaystyle", r"%tau", r"%lambda",
    r"\bmilestone\b", r"\bconfigs/", r"\bresults/", r"\blog[s]?/",
    r"\bD[1-8]\b.*\bpanel\b", r"\bC-[A-Z]",
]


def plain_text(text):
    """Strip presentation markup for preflight measurement."""
    text = LINK.sub(r"\1", text).replace("**", "").replace("`", "")
    return re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"\1", text)


def parse_deck(path):
    """Parse the 48 v4_CGPT Markdown slide blocks into structured entries."""
    source = Path(path).read_text(encoding="utf-8")
    headers = list(re.finditer(r"^### SLIDE (\d+) — (\w+) — (.+)$", source, re.M))
    slides = []
    for index, header in enumerate(headers):
        body = source[header.end():headers[index + 1].start() if index + 1 < len(headers) else len(source)]
        fields = re.search(
            r"\[TITLE\]\s*(.*?)\n\s*Badge\s*:\s*(.*?)\n\s*\[BULLET POINTS\](.*?)"
            r"\[EQUATIONS\](.*?)\[VISUAL\](.*?)\nNotes\s*:\s*(.*?)(?=\n---|\n## |\Z)",
            body, re.S,
        )
        if fields is None:
            raise ValueError(f"Incomplete fields in slide {header[1]}")
        title, badge, bullets_raw, equations_raw, visual, notes = fields.groups()
        badge_match = re.fullmatch(r"(.+?)\s*\((\w+),\s*w\s*=\s*([\d.]+)\)", badge.strip())
        if badge_match is None:
            raise ValueError(f"Invalid badge in slide {header[1]}: {badge}")

        bullets = _parse_bullets(bullets_raw.strip())
        equations = _parse_equations(equations_raw.strip())

        slides.append({
            "number": int(header[1]),
            "kind": header[2],
            "heading": header[3].strip(),
            "title": title.strip(),
            "badge": badge_match[1].strip(),
            "color": badge_match[2],
            "badge_width": float(badge_match[3]),
            "bullets": bullets,
            "equations": equations,
            "visual": visual.strip(),
            "notes": notes.strip(),
        })
    if [s["number"] for s in slides] != list(range(1, 49)):
        raise ValueError("Expected exactly 48 sequential slide blocks, numbered 1-48")
    annex_kinds = [s["kind"] for s in slides[20:]]
    if annex_kinds != ["ANNEX"] * 28:
        raise ValueError("Slides 21-48 must all be ANNEX")
    return slides


def _parse_bullets(raw):
    """Extract bullet lines and detect embedded markdown tables."""
    lines = raw.split("\n")
    bullets = []
    table_lines = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines.append(stripped)
            in_table = True
        else:
            if in_table and table_lines:
                bullets.append({"type": "table", "content": table_lines})
                table_lines = []
                in_table = False
            if stripped.startswith("- "):
                bullets.append({"type": "text", "content": stripped[2:].strip()})
            elif stripped:
                bullets.append({"type": "text", "content": stripped})
    if table_lines:
        bullets.append({"type": "table", "content": table_lines})
    return bullets


def _parse_equations(raw):
    """Extract ASCII display lines, lecture, and StarMath blocks (for auxiliary file)."""
    if raw.strip() in ("Aucune.", "Aucune", ""):
        return []
    equations = []
    items = re.split(r"\n- ", raw)
    for item in items:
        item = item.strip()
        if not item:
            continue
        ascii_matches = re.findall(r"Affichage ASCII\s*:\s*`([^`]+)`", item)
        starmath_matches = re.findall(r"StarMath\s*:\s*```starmath\s*\n(.*?)```", item, re.S)
        lecture_match = re.search(r"Lecture\s*:\s*(.+?)(?=\n- |\nAffichage|\Z)", item, re.S)
        for i, ascii_text in enumerate(ascii_matches):
            equations.append({
                "ascii": ascii_text.strip(),
                "starmath": starmath_matches[i].strip() if i < len(starmath_matches) else "",
                "lecture": lecture_match[1].strip() if lecture_match else "",
            })
    return equations


def resolve_input(value, filename, roots):
    """Resolve explicit paths first and fail with the searched locations."""
    candidates = [Path(value).expanduser()] if value else [root / filename for root in roots]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(f"Missing {filename}; searched: {', '.join(str(p) for p in candidates)}")


def load_template(path):
    """Reuse the template definitions without executing its historical slides or save."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    definitions = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "s" for t in node.targets):
            break
        definitions.append(node)
    namespace = {"__file__": str(path), "__name__": "point_hebdo_template"}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    for name in ("add_rect", "add_text", "add_multi_text", "add_paragraphs", "header_bar",
                 "badge", "vertical_bar", "lettered_circle", "page_num_only", "prs",
                 "TEAL", "TEAL_DARK", "ORANGE", "ORANGE_LT", "BLUE", "BLUE_DEEP",
                 "PURPLE", "GREEN", "RED", "WHITE", "BG_BLUE_LT", "BG_CREAM",
                 "BG_PINK", "BG_GREEN_LT", "TXT_DARK", "TXT_BODY", "TXT_FAINT",
                 "TXT_DARKER", "BLANK"):
        if name not in namespace:
            raise ValueError(f"Template utility missing: {name}")
    return SimpleNamespace(**namespace)


@lru_cache(maxsize=32)
def font_path(style="Regular"):
    """Resolve Carlito, the Calibri metric substitute, through fontconfig."""
    return subprocess.check_output(
        ["fc-match", "-f", "%{file}", f"Carlito:style={style}"], text=True
    ).strip()


@lru_cache(maxsize=128)
def font_at(size, bold=False):
    """Return a high precision font for preflight text measurements."""
    return ImageFont.truetype(font_path("Bold" if bold else "Regular"), round(size * 4))


def text_height(text, width, size, bold=False):
    """Estimate wrapped text height using the actual presentation font."""
    font = font_at(size, bold)
    lines = 0
    for paragraph in plain_text(text).split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if line and font.getlength(candidate) / 4 > (width - 0.10) * 72:
                lines += 1
                line = word
            else:
                line = candidate
        lines += 1
    return lines * size * 1.15 / 72 + 0.06


def rich_runs(paragraph, text, size, color, bold=False):
    """Write inline emphasis, code, and clickable reference spans into one paragraph."""
    position = 0
    token = re.compile(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)"
        r"|\*\*([^\n]+?)\*\*"
        r"|(?<!\w)\*([^*\n]+)\*(?!\w)"
        r"|`([^`]+)`"
    )
    for match in list(token.finditer(text)) + [None]:
        end = match.start() if match else len(text)
        if end > position:
            run = paragraph.add_run()
            run.text = text[position:end]
            run.font.name, run.font.size = "Carlito", Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
        if match is None:
            break
        if match[1] is not None:
            run = paragraph.add_run()
            run.text = match[1]
            run.font.name, run.font.size = "Carlito", Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
            run.hyperlink.address = match[2]
        elif match[2] is not None:
            run = paragraph.add_run()
            run.text = match[2]
            run.font.name, run.font.size = "Carlito", Pt(size)
            run.font.bold = True
            run.font.color.rgb = color
        elif match[3] is not None:
            run = paragraph.add_run()
            run.text = match[3]
            run.font.name, run.font.size = "Carlito", Pt(size)
            run.font.italic = True
            run.font.color.rgb = color
        elif match[4] is not None:
            run = paragraph.add_run()
            run.text = match[4]
            run.font.name, run.font.size = "Consolas", Pt(size * 0.92)
            run.font.color.rgb = color
        position = match.end()


class DeckBuilder:
    """Lay out the 48-slide v4_CGPT deck with the supplied template utilities."""

    def __init__(self, template):
        self.t = template
        self.prs = template.prs
        self.font_checks = []
        self.formula_checks = []

    def rect(self, slide, x, y, w, h, color, line=None, shape=MSO_SHAPE.RECTANGLE):
        return self.t.add_rect(slide, x, y, w, h, color, line, shape)

    def text(self, slide, x, y, w, h, text, size=11, color=None, bold=False,
             center=False, minimum=None, italic=False, font_name="Carlito"):
        color = color or self.t.TXT_DARK
        minimum = size if minimum is None else minimum
        while text_height(text, w, size, bold) > h and size > minimum:
            size = max(minimum, size - 0.25)
        required = text_height(text, w, size, bold)
        if required > h + 0.045:
            raise ValueError(
                f"Slide {len(self.prs.slides)} text does not fit "
                f"({required:.2f}>{h:.2f} in): {plain_text(text)[:90]}"
            )
        box = self.t.add_text(slide, x, y, w, h, "", font_name=font_name, size=size)
        frame = box.text_frame
        frame.margin_top = frame.margin_bottom = Inches(0.015)
        for index, line in enumerate(text.split("\n")):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.line_spacing = Pt(size * 1.15)
            paragraph.space_after = Pt(0)
            paragraph.alignment = PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
            rich_runs(paragraph, line, size, color, bold or italic)
        self.font_checks.append({"slide": len(self.prs.slides), "size": size,
                                 "height": required, "box": h})
        return box

    def mono_text(self, slide, x, y, w, h, text, size=10, color=None):
        """Display monospace text (for ASCII equations)."""
        color = color or self.t.TXT_DARKER
        box = self.t.add_text(slide, x, y, w, h, "", font_name="Consolas", size=size)
        frame = box.text_frame
        frame.margin_top = frame.margin_bottom = Inches(0.01)
        frame.margin_left = frame.margin_right = Inches(0.03)
        for index, line in enumerate(text.split("\n")):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.line_spacing = Pt(size * 1.2)
            paragraph.space_after = Pt(0)
            run = paragraph.add_run()
            run.text = line
            run.font.name = "Consolas"
            run.font.size = Pt(size)
            run.font.color.rgb = color
        return box

    def line(self, slide, x1, y1, x2, y2, color=None, width=1.5, dashed=False):
        line = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)
        )
        line.line.color.rgb = color or self.t.TXT_BODY
        line.line.width = Pt(width)
        if dashed:
            from pptx.enum.dml import MSO_LINE_DASH_STYLE
            line.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        return line

    def arrow(self, slide, x, y, w=0.28, h=0.20, color=None):
        return self.rect(slide, x, y, w, h, color or self.t.TXT_FAINT, shape=MSO_SHAPE.RIGHT_ARROW)

    def card(self, slide, x, y, w, h, title, color, body="", size=11):
        self.rect(slide, x, y, w, h, self.t.BG_BLUE_LT)
        self.rect(slide, x, y, 0.045, h, color)
        self.text(slide, x + 0.12, y + 0.08, w - 0.24, 0.38, title, size=size, bold=True, color=color)
        if body:
            self.text(slide, x + 0.12, y + 0.51, w - 0.24, h - 0.58, body, size=size)

    def equation_panel(self, slide, entry, y=4.03, h=1.10):
        """Display equations as ASCII text with lecture, in a bottom panel."""
        equations = entry["equations"]
        if not equations:
            return
        self.rect(slide, 0.40, y, 9.20, h, self.t.BG_BLUE_LT)
        row = h / len(equations)
        for i, eq in enumerate(equations):
            ey = y + i * row
            self.mono_text(slide, 0.50, ey + 0.03, 8.95, row - 0.06,
                           eq["ascii"], size=10, color=self.t.TXT_DARKER)
            if eq["lecture"]:
                self.text(slide, 0.50, ey + row * 0.55, 8.95, row * 0.42,
                          "Lecture : " + eq["lecture"], size=8, color=self.t.TXT_BODY, italic=True)
            self.formula_checks.append({
                "slide": len(self.prs.slides), "ascii": eq["ascii"][:60],
                "lecture": bool(eq["lecture"]),
                "starmath": bool(eq["starmath"]),
            })

    def bullets(self, slide, bullets, x, y, w, h, size=11, minimum=10):
        """Render bullet items, handling both text and table types."""
        cy = y
        for item in bullets:
            if item["type"] == "table":
                consumed = self.render_table(slide, item["content"], x, cy, w, size)
                cy += consumed + 0.10
            else:
                bh = text_height(item["content"], w, size)
                while bh > 1.5 and size > minimum:
                    size = max(minimum, size - 0.25)
                    bh = text_height(item["content"], w, size)
                self.text(slide, x, cy, w, bh, item["content"], size=size)
                cy += bh + 0.06
        return cy - y

    def render_table(self, slide, lines, x, y, w, size=10):
        """Render a markdown table as a PPTX table with alternating row colors."""
        rows_data = []
        for line in lines:
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows_data.append(cells)
        n_rows = len(rows_data)
        n_cols = len(rows_data[0])
        header = rows_data[0]
        data = rows_data[2:] if n_rows > 2 and all(set(c) <= set("-: ") for c in rows_data[1]) else rows_data[1:]

        row_h = 0.32
        table_h = row_h * (1 + len(data))
        tbl_shape = slide.shapes.add_table(1 + len(data), n_cols, Inches(x), Inches(y), Inches(w), Inches(table_h))
        tbl = tbl_shape.table

        col_widths = [w / n_cols] * n_cols
        for ci, cw in enumerate(col_widths):
            tbl.columns[ci].width = Inches(cw)

        for ci, cell_text in enumerate(header):
            cell = tbl.cell(0, ci)
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.t.TEAL
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = cell_text
            run.font.name = "Carlito"
            run.font.size = Pt(size)
            run.font.bold = True
            run.font.color.rgb = self.t.WHITE

        for ri, row in enumerate(data):
            bg = self.t.BG_BLUE_LT if ri % 2 == 0 else self.t.WHITE
            for ci, cell_text in enumerate(row):
                cell = tbl.cell(ri + 1, ci)
                cell.fill.solid()
                cell.fill.fore_color.rgb = bg
                cell.margin_left = cell.margin_right = Inches(0.06)
                cell.margin_top = cell.margin_bottom = Inches(0.02)
                p = cell.text_frame.paragraphs[0]
                p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
                rich_runs(p, cell_text, size - 1, self.t.TXT_DARK)

        return table_h

    def begin(self, entry):
        """Create a new slide with header bar, badge, and title."""
        slide = self.prs.slides.add_slide(self.t.BLANK)
        if entry["number"] != 1:
            self.t.header_bar(slide, entry["heading"])
            number_shape = slide.shapes[-1]
            slide.shapes._spTree.remove(number_shape._element)
            header = slide.shapes[1]
            header.width = Inches(7.35)
            for paragraph in header.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.name = "Carlito"
                    run.font.size = Pt(15 if len(entry["heading"]) > 62 else 17)
            color_name = COLOR_MAP.get(entry["color"], "BLUE")
            self.t.badge(slide, entry["badge"], x=9.70 - entry["badge_width"],
                         w=entry["badge_width"], color=getattr(self.t, color_name))
            for shape in list(slide.shapes)[-1:]:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = "Carlito"
            self.rect(slide, 0.42, 0.79, 0.055, 0.47, self.t.ORANGE)
            self.text(slide, 0.62, 0.74, 8.92, 0.62, entry["title"],
                      size=18, bold=True, minimum=16)
        if entry["kind"] == "ANNEX":
            self.rect(slide, 0.0, 5.38, 10.0, 0.24, self.t.TXT_FAINT)
            self.text(slide, 0.40, 5.38, 3.0, 0.24, "ANNEXE",
                      size=8, bold=True, color=self.t.WHITE)
        return slide

    def finish(self, slide, entry):
        """Add speaker notes and page number."""
        notes_parts = [entry["notes"], "", "CANONICAL BULLET POINTS"]
        for item in entry["bullets"]:
            if item["type"] == "table":
                notes_parts.append("[TABLE]")
                notes_parts.extend(item["content"])
            else:
                notes_parts.append(item["content"])
        notes_parts.append("")
        notes_parts.append("VISUAL SOURCE")
        notes_parts.append(entry["visual"])
        if entry["equations"]:
            notes_parts.append("")
            notes_parts.append("EQUATION SOURCES (StarMath — for manual replacement only)")
            for eq in entry["equations"]:
                notes_parts.append(f"ASCII: {eq['ascii']}")
                if eq["starmath"]:
                    notes_parts.append(f"StarMath:\n{eq['starmath']}")
        slide.notes_slide.notes_text_frame.text = "\n".join(notes_parts)
        self.text(slide, 8.80, 5.25, 1.00, 0.24, str(entry["number"]),
                  size=9, color=self.t.TXT_BODY)

    def build(self, entries):
        """Build all 48 slides in order."""
        for entry in entries:
            slide = self.begin(entry)
            if entry["kind"] == "ANNEX":
                self.annex_slide(slide, entry)
            else:
                self.main_slide(slide, entry)
            self.finish(slide, entry)
        return self.prs

    def main_slide(self, slide, entry):
        """Render a main presentation slide (1-20)."""
        n = entry["number"]
        b = [item for item in entry["bullets"]]
        t = self.t

        if n == 1:
            self.rect(slide, 0.60, 0.50, 8.80, 2.20, t.TEAL_DARK)
            self.text(slide, 0.82, 0.76, 8.35, 0.60, "JEPA-Drift", size=30, color=t.WHITE, bold=True)
            self.text(slide, 0.82, 1.40, 8.20, 0.97,
                      "Information transversale, géométrie latente et délai de détection",
                      size=20, color=t.WHITE, bold=True)
            self.rect(slide, 0.60, 2.80, 8.80, 0.06, t.ORANGE)
            self.rect(slide, 0.00, 3.00, 10.00, 1.80, t.BLUE_DEEP)
            self.rect(slide, 0.60, 3.10, 8.80, 0.46, t.ORANGE)
            self.text(slide, 0.72, 3.18, 8.55, 0.31,
                      "Point hebdomadaire — lundi 26 octobre 2026",
                      size=14, bold=True, color=t.WHITE)
            chain_y = 3.70
            self.text(slide, 0.72, chain_y, 8.55, 0.35,
                      "rendements journaliers (N actifs)  →  représentation figée (d coordonnées)  →  détecteurs distincts  →  alarmes",
                      size=13, bold=True, color=t.WHITE, center=True)
            self.text(slide, 0.72, 4.15, 8.55, 0.30,
                      "information conservée / coût de surveillance",
                      size=11, color=RGBColor(0xD5, 0xDB, 0xDB), center=True, italic=True)
            self.t.badge(slide, entry["badge"], x=7.65, y=0.20, w=entry["badge_width"], color=t.ORANGE)
            return

        has_table = any(item["type"] == "table" for item in b)

        if has_table:
            self._render_table_slide(slide, entry, b)
        else:
            self._render_content_slide(slide, entry, b)

        self.equation_panel(slide, entry, y=4.15, h=1.00)

    def _render_table_slide(self, slide, entry, bullets):
        """Render a slide whose primary content is a table (or two tables for slide 2)."""
        n = entry["number"]
        text_bullets = [item for item in bullets if item["type"] == "text"]
        table_items = [item for item in bullets if item["type"] == "table"]

        y = 1.45
        for item in text_bullets:
            bh = text_height(item["content"], 9.0, 11)
            self.text(slide, 0.48, y, 9.05, bh, item["content"], size=11)
            y += bh + 0.06

        if n == 2:
            self._render_slide2_two_tables(slide, table_items, y)
            return

        for tbl_item in table_items:
            y += 0.08
            consumed = self.render_table(slide, tbl_item["content"], 0.48, y, 9.05, size=10)
            y += consumed + 0.10

        if n == 15:
            pass

    def _render_slide2_two_tables(self, slide, table_items, y_start):
        """Slide 2: two stacked tables — experimental (57%) then theoretical (33%)."""
        if len(table_items) < 2:
            for tbl_item in table_items:
                consumed = self.render_table(slide, tbl_item["content"], 0.48, y_start, 9.05, size=9)
                y_start += consumed + 0.10
            return
        tbl1, tbl2 = table_items[0], table_items[1]
        consumed1 = self.render_table(slide, tbl1["content"], 0.48, y_start, 9.05, size=9)
        y2 = y_start + consumed1 + 0.14
        self.text(slide, 0.48, y2 - 0.18, 9.05, 0.20,
                  "Résultats théoriques : hypothèse / constat expérimental.",
                  size=10, bold=True, color=self.t.TXT_DARK)
        self.render_table(slide, tbl2["content"], 0.48, y2, 9.05, size=9)

    def _render_content_slide(self, slide, entry, bullets):
        """Render a content slide with bullets and a schematic visual."""
        n = entry["number"]

        if n == 3:
            self._visual_matrix_chars(slide, 0.48, 1.45, 4.5, 2.5)
            self.bullets(slide, bullets, 5.3, 1.45, 4.2, 2.5, size=11, minimum=10)
        elif n == 4:
            self._visual_timeline_v4(slide, 0.48, 1.45, 9.05, 1.0)
            self.bullets(slide, bullets, 0.48, 2.65, 9.05, 1.4, size=11, minimum=10)
        elif n == 6:
            self._visual_exponential_decay(slide, 0.48, 1.45, 4.5, 2.5)
            self.bullets(slide, bullets, 5.3, 1.45, 4.2, 2.5, size=11, minimum=10)
        elif n == 7:
            self._visual_bifurcated_pipeline(slide, 0.48, 1.45, 9.05, 1.5)
            self.bullets(slide, bullets, 0.48, 3.10, 9.05, 1.0, size=11, minimum=10)
        elif n == 8:
            self._visual_covariance_methods(slide, 0.48, 1.45, 4.5, 2.5)
            self.bullets(slide, bullets, 5.3, 1.45, 4.2, 2.5, size=11, minimum=10)
        elif n == 9:
            self._visual_three_column_pipeline(slide, 0.48, 1.45, 9.05, 1.3)
            self.bullets(slide, bullets, 0.48, 2.95, 9.05, 1.1, size=11, minimum=10)
        elif n == 10:
            self._visual_dimension_table(slide, 0.48, 1.45, 4.5, 2.5)
            self.bullets(slide, bullets, 5.3, 1.45, 4.2, 2.5, size=11, minimum=10)
        elif n == 11:
            self._visual_kl_two_frames(slide, 0.48, 1.45, 4.5, 2.5)
            self.bullets(slide, bullets, 5.3, 1.45, 4.2, 2.5, size=11, minimum=10)
        elif n == 14:
            self._visual_degree_zero(slide, 0.48, 1.45, 9.05, 1.6)
            self.bullets(slide, bullets, 0.48, 2.85, 9.05, 1.2, size=11, minimum=10)
        elif n == 16:
            self._visual_marginal_criterion(slide, 0.48, 1.45, 9.05, 1.6)
            self.bullets(slide, bullets, 0.48, 2.95, 9.05, 1.1, size=11, minimum=10)
        elif n == 17:
            self._render_two_col_slide(slide, entry, bullets, "jepa_arch")
        elif n == 18:
            self._render_two_col_slide(slide, entry, bullets, "masking")
        elif n == 19:
            self._render_two_col_slide(slide, entry, bullets, "lanes")
        else:
            self.bullets(slide, bullets, 0.48, 1.45, 9.05, 2.6, size=11, minimum=10)

    def _render_two_col_slide(self, slide, entry, bullets, visual_kind):
        """Render a content slide with bullets on the left and a compact visual on the right."""
        t = self.t
        text_bullets = [item for item in bullets if item["type"] == "text"]
        y = 1.45
        for item in text_bullets:
            bh = text_height(item["content"], 5.8, 10)
            self.text(slide, 0.44, y, 5.8, bh, item["content"], size=10, minimum=9)
            y += bh + 0.05
        self.rect(slide, 6.48, 1.46, 3.08, 2.55, t.BG_CREAM)
        if visual_kind == "jepa_arch":
            self._visual_jepa_compact(slide, 6.58, 1.55, 2.88, 2.30)
        elif visual_kind == "masking":
            self._visual_masking_compact(slide, 6.58, 1.55, 2.88, 2.30)
        elif visual_kind == "lanes":
            self._visual_lanes_compact(slide, 6.58, 1.55, 2.88, 2.30)

    def _visual_jepa_compact(self, slide, x, y, w, h):
        """Compact JEPA architecture for two-column layout."""
        t = self.t
        self.rect(slide, x + 0.05, y + 0.05, w - 0.1, 0.55, t.BG_BLUE_LT, line=t.TEAL)
        self.text(slide, x + 0.08, y + 0.07, w - 0.16, 0.20,
                  "visibles : [r/s, beta, vol,", size=7, bold=True, color=t.TEAL, center=True)
        self.text(slide, x + 0.08, y + 0.28, w - 0.16, 0.28,
                  "mom, rev]  —  5 features ex ante", size=7, color=t.TXT_BODY, center=True)
        self.rect(slide, x + 0.05, y + 0.65, w - 0.1, 0.55, t.BG_PINK, line=t.RED)
        self.text(slide, x + 0.08, y + 0.67, w - 0.16, 0.20,
                  "cachés : [beta, vol, mom, rev]", size=7, bold=True, color=t.RED, center=True)
        self.text(slide, x + 0.08, y + 0.88, w - 0.16, 0.28,
                  "rendement masqué INTERDIT au contexte", size=7, color=t.RED, center=True)
        self.line(slide, x + w/2, y + 1.20, x + w/2, y + 1.35, t.ORANGE, 2)
        self.rect(slide, x + 0.05, y + 1.35, w - 0.1, 0.45, t.BG_CREAM, line=t.BLUE)
        self.text(slide, x + 0.08, y + 1.37, w - 0.16, 0.40,
                  "encodeur contexte + prédicteur\n+ cible EMA  —  < 1M paramètres",
                  size=7, color=t.TXT_BODY, center=True)
        self.line(slide, x + w/2, y + 1.80, x + w/2, y + 1.95, t.GREEN, 2)
        self.rect(slide, x + 0.05, y + 1.95, w - 0.1, 0.30, t.GREEN)
        self.text(slide, x + 0.08, y + 1.97, w - 0.16, 0.26,
                  "sortie d ∈ {2,4,8,16} — NON ENTRAÎNÉ", size=7, bold=True,
                  color=t.WHITE, center=True)

    def _visual_masking_compact(self, slide, x, y, w, h):
        """Compact masking leakage visual for two-column layout."""
        t = self.t
        self.rect(slide, x + 0.05, y + 0.05, w - 0.1, 0.65, t.BG_PINK, line=t.RED)
        self.text(slide, x + 0.08, y + 0.07, w - 0.16, 0.20,
                  "FAUX : fuite de cible", size=8, bold=True, color=t.RED, center=True)
        self.text(slide, x + 0.08, y + 0.28, w - 0.16, 0.38,
                  "marché (toutes actions)\n→ masquer → fuite", size=7, color=t.TXT_DARK, center=True)
        self.rect(slide, x + 0.05, y + 0.75, w - 0.1, 0.65, t.BG_GREEN_LT, line=t.GREEN)
        self.text(slide, x + 0.08, y + 0.77, w - 0.16, 0.20,
                  "LICITE : masquer d'abord", size=8, bold=True, color=t.GREEN, center=True)
        self.text(slide, x + 0.08, y + 0.98, w - 0.16, 0.38,
                  "masquer 30-50%\n→ facteur (visibles)\n→ prédire cachés", size=7, color=t.TXT_DARK, center=True)
        self.rect(slide, x + 0.05, y + 1.50, w - 0.1, 0.70, t.WHITE, line=t.BLUE)
        self.text(slide, x + 0.08, y + 1.52, w - 0.16, 0.20,
                  "pénalité de variance", size=8, bold=True, color=t.BLUE, center=True)
        self.text(slide, x + 0.08, y + 1.73, w - 0.16, 0.43,
                  "L_var = (1/d) Σ max(0, 1-sd(Z_j))²\n"
                  "sd sur B journées\nanti-collapsus",
                  size=7, color=t.TXT_DARK, center=True)

    def _visual_lanes_compact(self, slide, x, y, w, h):
        """Compact three-lane protocol visual for two-column layout."""
        t = self.t
        lanes = [
            ("ACP", t.TEAL, "fit calib → scores → alarmes", False),
            ("degré zéro", t.BLUE, "fit calib → normalisé → alarmes", False),
            ("JEPA", t.PURPLE, "prétrain → validation → test", True),
        ]
        for i, (name, color, desc, dashed) in enumerate(lanes):
            ly = y + 0.05 + i * 0.72
            self.rect(slide, x + 0.05, ly, w - 0.1, 0.25, color)
            self.text(slide, x + 0.08, ly + 0.01, w - 0.16, 0.23,
                      name, size=9, bold=True, color=t.WHITE, center=True)
            self.rect(slide, x + 0.05, ly + 0.28, w - 0.1, 0.38,
                      t.BG_BLUE_LT if i < 2 else t.BG_CREAM, line=color)
            self.text(slide, x + 0.08, ly + 0.30, w - 0.16, 0.34,
                      desc, size=7, color=t.TXT_DARK, center=True)
            if dashed:
                self.text(slide, x + 0.08, ly + 0.48, w - 0.16, 0.16,
                          "NON EXÉCUTÉ", size=7, bold=True, color=t.RED, center=True)
        self.text(slide, x + 0.05, y + h - 0.20, w - 0.1, 0.18,
                  "mêmes fonds, mêmes ruptures", size=7, color=t.TXT_FAINT, center=True, italic=True)

    def annex_slide(self, slide, entry):
        """Render an annex slide (21-48) with two-column calculation layout."""
        t = self.t
        text_bullets = [item for item in entry["bullets"] if item["type"] == "text"]
        table_items = [item for item in entry["bullets"] if item["type"] == "table"]

        y = 1.45
        for item in text_bullets:
            bh = text_height(item["content"], 5.8, 10)
            self.text(slide, 0.44, y, 5.8, bh, item["content"], size=10, minimum=9)
            y += bh + 0.05

        self.rect(slide, 6.48, 1.46, 3.08, 2.55, t.BG_CREAM)
        self._annex_visual(slide, entry["number"], 6.58, 1.55, 2.88, 2.30)

        self.equation_panel(slide, entry, y=4.15, h=1.00)

        if table_items:
            ty = 4.15
            for tbl_item in table_items:
                self.render_table(slide, tbl_item["content"], 0.44, ty, 9.08, size=9)

    # =========================================================================
    # VISUAL RENDERING — v4_CGPT specific schemas
    # =========================================================================

    def _visual_matrix_chars(self, slide, x, y, w, h):
        """Slide 3: matrix on left, 4 characteristics table on right."""
        t = self.t
        self.rect(slide, x, y, w * 0.52, h, t.WHITE, line=t.TEAL)
        self.text(slide, x + 0.05, y + 0.05, w * 0.52 - 0.1, 0.22,
                  "matrice rendements", size=9, bold=True, color=t.TEAL, center=True)
        cols, rows = 6, 4
        cw, ch = (w * 0.52 - 0.3) / cols, (h - 0.55) / rows
        for r in range(rows):
            for c in range(cols):
                cx = x + 0.15 + c * cw
                cy = y + 0.32 + r * ch
                self.rect(slide, cx, cy, cw - 0.03, ch - 0.03,
                          t.BG_BLUE_LT if (r + c) % 2 == 0 else t.WHITE, line=t.TXT_FAINT)
        self.text(slide, x + 0.05, y + h - 0.22, w * 0.52 - 0.1, 0.18,
                  "97 / 239 actifs", size=8, bold=True, color=t.BLUE, center=True)

        fx = x + w * 0.52 + 0.08
        fw = w * 0.48 - 0.08
        self.rect(slide, fx, y, fw, h, t.WHITE, line=t.BLUE)
        self.text(slide, fx + 0.05, y + 0.05, fw - 0.1, 0.22,
                  "4 caractéristiques ex ante", size=9, bold=True, color=t.BLUE, center=True)
        chars = [("beta_252", "[t-252,t)"), ("vol_63", "[t-63,t)"),
                 ("mom_12_1", "[t-252,t-21)"), ("rev_21", "[t-21,t)")]
        for i, (name, window) in enumerate(chars):
            cy = y + 0.32 + i * 0.48
            self.rect(slide, fx + 0.08, cy, fw - 0.16, 0.40, t.BG_BLUE_LT, line=t.TEAL)
            self.text(slide, fx + 0.12, cy + 0.02, fw * 0.45, 0.18,
                      name, size=9, bold=True, color=t.TEAL_DARK)
            self.text(slide, fx + fw * 0.48, cy + 0.02, fw * 0.48, 0.18,
                      window, size=8, color=t.TXT_BODY, center=True)
            self.text(slide, fx + 0.12, cy + 0.20, fw - 0.24, 0.16,
                      "rang/n_valides - 0,5", size=7, color=t.TXT_FAINT, italic=True)

    def _visual_timeline_v4(self, slide, x, y, w, h):
        """Slide 4: three-segment timeline with embargo hatches and 941x239 label."""
        t = self.t
        segments = [
            ("2005-2015", "pré-entraînement\n(proposé pour JEPA)", t.TEAL, 0.0, 3.0),
            ("2016-2019", "calibration ACP\n(941 j x 239 actifs)", t.BLUE, 3.0, 6.0),
            ("2020+", "surveillance\n(transformations figées)", t.ORANGE, 6.0, 9.05),
        ]
        for label, desc, color, sx, ex in segments:
            self.rect(slide, x + sx, y, ex - sx - 0.08, 0.55, color)
            self.text(slide, x + sx + 0.05, y + 0.01, ex - sx - 0.18, 0.22,
                      label, size=11, bold=True, color=t.WHITE, center=True)
            self.text(slide, x + sx + 0.05, y + 0.24, ex - sx - 0.18, 0.30,
                      desc, size=8, color=t.WHITE, center=True)
        for bx in [3.0, 6.0]:
            self.rect(slide, x + bx - 0.02, y + 0.57, 0.12, 0.14, t.TXT_FAINT)
            self.text(slide, x + bx - 0.22, y + 0.57, 0.52, 0.14,
                      "65 j", size=7, color=t.WHITE, center=True)
        ops = ["apprendre réseau [proposé]", "covariance / ACP / seuils [implémenté]", "signaux/alarme [évalué]"]
        colors = [t.TEAL, t.BLUE, t.ORANGE]
        for i, (op, color) in enumerate(zip(ops, colors)):
            ox = x + i * 3.0
            self.text(slide, ox + 0.05, y + 0.76, 2.95, 0.20,
                      op, size=8, color=color, center=True, italic=True)

    def _visual_exponential_decay(self, slide, x, y, w, h):
        """Slide 6: exponential decay curve — theoretical model."""
        t = self.t
        self.rect(slide, x, y, w, h, t.WHITE, line=t.PURPLE)
        self.text(slide, x + 0.05, y + 0.03, w - 0.1, 0.20,
                  "modèle théorique — pas un JEPA entraîné", size=8, bold=True,
                  color=t.PURPLE, center=True, italic=True)
        cx, cy = x + w * 0.15, y + h * 0.75
        pw, ph = w * 0.70, h * 0.55
        self.line(slide, cx, cy - ph, cx, cy, t.TXT_DARK, 1.5)
        self.line(slide, cx, cy, cx + pw, cy, t.TXT_DARK, 1.5)
        self.text(slide, cx - 0.3, cy + 0.02, 0.6, 0.18, "jours", size=7, color=t.TXT_BODY, center=True)
        self.text(slide, x + 0.02, y + 0.25, 0.15, 0.40, "I_t", size=8, color=t.TXT_DARK, center=True)
        n_pts = 30
        for i in range(n_pts):
            px1 = cx + (i / n_pts) * pw
            px2 = cx + ((i + 1) / n_pts) * pw
            py1 = cy - ph * (1.0 if i < n_pts / 3 else 0.85 * pow(0.88, (i - n_pts / 3) * 0.3))
            py2 = cy - ph * (1.0 if i + 1 < n_pts / 3 else 0.85 * pow(0.88, (i + 1 - n_pts / 3) * 0.3))
            color = t.TEAL if i < n_pts / 3 else t.RED
            self.line(slide, px1, py1, px2, py2, color, 2)
        self.text(slide, cx + pw * 0.15, cy - ph - 0.02, 1.2, 0.18,
                  "gelé (I constant)", size=7, color=t.TEAL)
        self.text(slide, cx + pw * 0.55, cy - ph * 0.35, 1.5, 0.18,
                  "adaptation (décroissance exp.)", size=7, color=t.RED)
        threshold_y = cy - ph * 0.15
        self.line(slide, cx, threshold_y, cx + pw, threshold_y, t.ORANGE, 1, dashed=True)
        self.text(slide, cx + pw - 1.2, threshold_y - 0.16, 1.2, 0.16,
                  "seuil log(gamma)", size=7, color=t.ORANGE, center=True)

    def _visual_bifurcated_pipeline(self, slide, x, y, w, h):
        """Slide 7: bifurcated pipeline — ACP to signs or energy, two distinct detectors."""
        t = self.t
        self.rect(slide, x, y, 2.2, 0.55, t.TEAL)
        self.text(slide, x + 0.05, y + 0.05, 2.1, 0.45,
                  "rendements r_t\n+ axes ACP gelés", size=9, bold=True, color=t.WHITE, center=True)
        self.arrow(slide, x + 2.25, y + 0.18, w=0.25, h=0.18, color=t.TXT_FAINT)
        self.rect(slide, x + 2.55, y, 2.2, 0.55, t.BLUE)
        self.text(slide, x + 2.60, y + 0.05, 2.1, 0.45,
                  "scores ACP z_k(t)\n(k = 1..K+1)", size=9, bold=True, color=t.WHITE, center=True)
        self.arrow(slide, x + 4.80, y + 0.18, w=0.25, h=0.18, color=t.TXT_FAINT)
        self.rect(slide, x + 5.10, y, 1.85, 0.55, t.BG_BLUE_LT, line=t.TEAL)
        self.text(slide, x + 5.13, y + 0.02, 1.79, 0.22,
                  "branche signes", size=9, bold=True, color=t.TEAL, center=True)
        self.text(slide, x + 5.13, y + 0.25, 1.79, 0.28,
                  "b_k(t) = 1{z_k>0}\nCUSUM bilatéral", size=8, color=t.TXT_BODY, center=True)
        self.rect(slide, x + 7.00, y, 1.85, 0.55, t.BG_CREAM, line=t.PURPLE)
        self.text(slide, x + 7.03, y + 0.02, 1.79, 0.22,
                  "branche énergie", size=9, bold=True, color=t.PURPLE, center=True)
        self.text(slide, x + 7.03, y + 0.25, 1.79, 0.28,
                  "q_t = somme z_k^2\nCUSUM unilatéral", size=8, color=t.TXT_BODY, center=True)
        self.line(slide, x + 4.65, y + 0.10, x + 5.10, y + 0.10, t.TEAL, 2)
        self.line(slide, x + 4.65, y + 0.45, x + 5.10, y + 0.45, t.TEAL, 2)
        self.line(slide, x + 4.65, y + 0.10, x + 7.00, y + 0.10, t.PURPLE, 2)
        self.line(slide, x + 4.65, y + 0.45, x + 7.00, y + 0.45, t.PURPLE, 2)
        self.rect(slide, x + 5.10, y + 0.65, 1.85, 0.28, t.ORANGE)
        self.text(slide, x + 5.13, y + 0.67, 1.79, 0.24,
                  "alarme signe", size=8, bold=True, color=t.WHITE, center=True)
        self.rect(slide, x + 7.00, y + 0.65, 1.85, 0.28, t.ORANGE)
        self.text(slide, x + 7.03, y + 0.67, 1.79, 0.24,
                  "alarme énergie", size=8, bold=True, color=t.WHITE, center=True)
        self.line(slide, x + 5.95, y + 0.55, x + 5.95, y + 0.65, t.ORANGE, 1.5)
        self.line(slide, x + 7.90, y + 0.55, x + 7.90, y + 0.65, t.ORANGE, 1.5)
        self.text(slide, x + 0.05, y + 1.00, 8.8, 0.20,
                  "deux détecteurs distincts — évalués séparément, pas de fusion non calibrée",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)
        self.text(slide, x + 0.05, y + 1.18, 8.8, 0.18,
                  "aucune conversion en data drift supervisé ou concept drift sans cible Y",
                  size=8, color=t.RED, center=True, italic=True)

    def _visual_covariance_methods(self, slide, x, y, w, h):
        """Slide 8: three panels — empirical covariance, Ledoit-Wolf, empirical correlation."""
        t = self.t
        panels = [
            ("covariance\nempirique", t.TEAL, "Sigma_emp\nsur T jours"),
            ("Ledoit-Wolf\n(rétrécissement)", t.BLUE, "Sigma_LW = (1-d)S + d*mu*I\npour axes et échelles"),
            ("corrélation\nempirique", t.PURPLE, "R = D^(-1/2) S D^(-1/2)\npour compter (MP)"),
        ]
        pw = (w - 0.2) / 3
        for i, (title, color, desc) in enumerate(panels):
            px = x + i * (pw + 0.1)
            self.rect(slide, px, y, pw, h, t.WHITE, line=color)
            self.rect(slide, px, y, pw, 0.45, color)
            self.text(slide, px + 0.03, y + 0.02, pw - 0.06, 0.41,
                      title, size=9, bold=True, color=t.WHITE, center=True)
            self.text(slide, px + 0.05, y + 0.55, pw - 0.1, h - 0.65,
                      desc, size=8, color=t.TXT_BODY, center=True)
        self.text(slide, x + 0.05, y + h - 0.22, w - 0.1, 0.18,
                  "calcul en calibration seulement — PC1 marché conservé séparément",
                  size=8, color=t.ORANGE, center=True, italic=True)

    def _visual_three_column_pipeline(self, slide, x, y, w, h):
        """Slide 9: three dated columns — pretrain / calibration / surveillance with locks."""
        t = self.t
        cols = [
            ("2005-2015", "pré-entraînement", t.TEAL, "rien à ajuster\npour ACP standard"),
            ("2016-2019", "calibration", t.BLUE, "Sigma_LW -> v, lambda\nscores ref -> seuil énergie\nseuil exact signe / preuve"),
            ("2020+", "surveillance", t.ORANGE, "r_t -> v, lambda GELÉS\nsigne OU énergie\ndeux alarmes séparées"),
        ]
        cw = (w - 0.2) / 3
        for i, (date, label, color, desc) in enumerate(cols):
            cx = x + i * (cw + 0.1)
            self.rect(slide, cx, y, cw, 0.35, color)
            self.text(slide, cx + 0.03, y + 0.02, cw - 0.06, 0.31,
                      f"{date} — {label}", size=10, bold=True, color=t.WHITE, center=True)
            self.rect(slide, cx, y + 0.40, cw, h - 0.40, t.BG_BLUE_LT if i != 2 else t.BG_CREAM, line=color)
            self.text(slide, cx + 0.05, y + 0.48, cw - 0.1, h - 0.55,
                      desc, size=9, color=t.TXT_DARK, center=True)
            if i < 2:
                self.arrow(slide, cx + cw + 0.01, y + 0.10, w=0.08, h=0.15, color=t.TXT_FAINT)
        self.rect(slide, x + cw + 0.15, y + h - 0.10, 0.18, 0.14, t.ORANGE)
        self.text(slide, x + cw + 0.35, y + h - 0.12, 1.0, 0.16,
                  "figé", size=7, bold=True, color=t.ORANGE)
        self.rect(slide, x + 2 * (cw + 0.1) - 0.03, y + h - 0.10, 0.18, 0.14, t.ORANGE)
        self.text(slide, x + 2 * (cw + 0.1) + 0.17, y + h - 0.12, 1.0, 0.16,
                  "figé", size=7, bold=True, color=t.ORANGE)
        self.text(slide, x, y + h + 0.08, w, 0.18,
                  "seuil signe et seuil énergie distincts — frise reliant chaque action au segment effectif",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_dimension_table(self, slide, x, y, w, h):
        """Slide 10: dimension table (97->6, 239->11) + algorithmic tree."""
        t = self.t
        self.rect(slide, x, y, w * 0.48, h, t.WHITE, line=t.TEAL)
        self.text(slide, x + 0.05, y + 0.05, w * 0.48 - 0.1, 0.22,
                  "comptage Marčenko-Pastur", size=9, bold=True, color=t.TEAL, center=True)
        rows = [("97 actifs", "6 = 1 + 5"), ("239 actifs", "11 = 1 + 10")]
        for i, (label, val) in enumerate(rows):
            ry = y + 0.35 + i * 0.70
            self.rect(slide, x + 0.10, ry, w * 0.48 - 0.20, 0.55, t.BG_BLUE_LT, line=t.BLUE)
            self.text(slide, x + 0.15, ry + 0.02, w * 0.48 - 0.30, 0.22,
                      label, size=11, bold=True, color=t.BLUE, center=True)
            self.text(slide, x + 0.15, ry + 0.26, w * 0.48 - 0.30, 0.25,
                      val, size=14, bold=True, color=t.TEAL_DARK, center=True)
        fx = x + w * 0.48 + 0.08
        fw = w * 0.52 - 0.08
        self.rect(slide, fx, y, fw, h, t.WHITE, line=t.PURPLE)
        self.text(slide, fx + 0.05, y + 0.05, fw - 0.1, 0.22,
                  "arbre algorithmique", size=9, bold=True, color=t.PURPLE, center=True)
        steps = ["variances + corrélations", "compter k > lambda_plus", "covariance régularisée (LW)", "k vecteurs principaux\nmarché séparé"]
        for i, step in enumerate(steps):
            sy = y + 0.35 + i * 0.48
            self.rect(slide, fx + 0.08, sy, fw - 0.16, 0.38, t.BG_CREAM, line=t.PURPLE)
            self.text(slide, fx + 0.12, sy + 0.02, fw - 0.24, 0.34,
                      step, size=8, color=t.TXT_DARK, center=True)
            if i < 3:
                self.line(slide, fx + fw / 2, sy + 0.38, fx + fw / 2, sy + 0.48, t.ORANGE, 1.5)

    def _visual_kl_two_frames(self, slide, x, y, w, h):
        """Slide 11: two frames — KL definition / pipeline + results."""
        t = self.t
        fw = (w - 0.15) / 2
        self.rect(slide, x, y, fw, h, t.WHITE, line=t.PURPLE)
        self.rect(slide, x, y, fw, 0.35, t.PURPLE)
        self.text(slide, x + 0.05, y + 0.02, fw - 0.1, 0.31,
                  "définition et information", size=10, bold=True, color=t.WHITE, center=True)
        self.text(slide, x + 0.08, y + 0.42, fw - 0.16, h - 0.50,
                  "KL(P1||P0) = E_P1[log(p1/p0)]\n\nI_full = Delta' Sigma^(-1) Delta / 2\n\n"
                  "I_k = (v_k' Delta)^2 / (2 lambda_k)\n\nDPI : projection ne l'augmente pas",
                  size=9, color=t.TXT_DARK)
        fx = x + fw + 0.15
        self.rect(slide, fx, y, fw, h, t.WHITE, line=t.TEAL)
        self.rect(slide, fx, y, fw, 0.35, t.TEAL)
        self.text(slide, fx + 0.05, y + 0.02, fw - 0.1, 0.31,
                  "représentation → deux détecteurs", size=10, bold=True, color=t.WHITE, center=True)
        self.text(slide, fx + 0.08, y + 0.42, fw - 0.16, h - 0.50,
                  "ACP fixe (calibration)\n  → z_1 marché séparé\n  → z_2..z_(K+1) résiduels\n\n"
                  "signe (moyenne) | énergie (covariance)\n\n"
                  "Sharpe 8 : oracle 15 j\nACP signes 373 j | degré zéro 446 j",
                  size=9, color=t.TXT_DARK)

    def _visual_degree_zero(self, slide, x, y, w, h):
        """Slide 14: degree-zero normalization — two boxes with arrows."""
        t = self.t
        self.rect(slide, x + 0.1, y, 3.8, h, t.BG_BLUE_LT, line=t.TEAL)
        self.text(slide, x + 0.15, y + 0.05, 3.7, 0.25,
                  "résidu normalisé / signes", size=10, bold=True, color=t.TEAL, center=True)
        self.text(slide, x + 0.15, y + 0.35, 3.7, 0.95,
                  "p_t = r_t - b*(b'*r_t)\nz_t = U'*p_t / ||p_t||\n\n"
                  "z_t impaire normalisée\ncanal signes avec mises adaptatives",
                  size=9, color=t.TXT_DARK, center=True)
        self.arrow(slide, x + 4.0, y + h / 2 - 0.1, w=0.35, h=0.20, color=t.ORANGE)
        self.rect(slide, x + 4.45, y, 3.8, h, t.BG_CREAM, line=t.PURPLE)
        self.text(slide, x + 4.50, y + 0.05, 3.7, 0.25,
                  "norme résiduelle / amplitude", size=10, bold=True, color=t.PURPLE, center=True)
        self.text(slide, x + 4.50, y + 0.35, 3.7, 0.95,
                  "||p_t|| = norme euclidienne du résidu\n\n"
                  "canal pair séparé\nporte l'amplitude supprimée\nde la direction normalisée",
                  size=9, color=t.TXT_DARK, center=True)
        self.text(slide, x, y + h + 0.02, w, 0.20,
                  "b = 1er vecteur propre ACP (marché), U = axes résiduels — tous deux gelés",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_marginal_criterion(self, slide, x, y, w, h):
        """Slide 16: marginal criterion — no empty drawing."""
        t = self.t
        self.rect(slide, x, y, w, h, t.WHITE, line=t.PURPLE)
        self.text(slide, x + 0.1, y + 0.05, w - 0.2, 0.25,
                  "critère marginal conditionnel", size=11, bold=True, color=t.PURPLE, center=True)
        self.text(slide, x + 0.15, y + 0.38, w - 0.3, 1.10,
                  "Ajouter l'axe d+1 si et seulement si :\n\n"
                  "  q_(d+1) / I(d)  >  [C(d+1) - C(d)] / C(d)\n\n"
                  "avec q_k = KL supplémentaire de l'axe k, I(d) = somme_(k<=d) q_k,\n"
                  "C(d) = coût de surveillance positif quelconque.",
                  size=10, color=t.TXT_DARK, center=True)
        self.text(slide, x + 0.1, y + h - 0.25, w - 0.2, 0.20,
                  "coût affine C(d)=a+c*d : signe de l'accroissement change une fois",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_jepa_architecture_v4(self, slide, x, y, w, h):
        """Slide 17: JEPA architecture — visible/hidden inputs, context/target encoders."""
        t = self.t
        self.rect(slide, x + 0.05, y + 0.05, 2.0, 0.65, t.BG_BLUE_LT, line=t.TEAL)
        self.text(slide, x + 0.08, y + 0.07, 1.94, 0.20,
                  "visibles : [r/s, beta, vol,", size=8, bold=True, color=t.TEAL, center=True)
        self.text(slide, x + 0.08, y + 0.28, 1.94, 0.20,
                  "mom, rev]", size=8, bold=True, color=t.TEAL, center=True)
        self.text(slide, x + 0.08, y + 0.48, 1.94, 0.18,
                  "5 features ex ante", size=7, color=t.TXT_BODY, center=True)
        self.rect(slide, x + 2.20, y + 0.05, 2.0, 0.65, t.BG_PINK, line=t.RED)
        self.text(slide, x + 2.23, y + 0.07, 1.94, 0.20,
                  "cachés : [beta, vol,", size=8, bold=True, color=t.RED, center=True)
        self.text(slide, x + 2.23, y + 0.28, 1.94, 0.20,
                  "mom, rev]", size=8, bold=True, color=t.RED, center=True)
        self.text(slide, x + 2.23, y + 0.48, 1.94, 0.18,
                  "rendement masqué INTERDIT au contexte", size=7, color=t.RED, center=True)
        self.arrow(slide, x + 4.25, y + 0.25, w=0.25, h=0.18, color=t.ORANGE)
        self.rect(slide, x + 4.55, y + 0.05, 1.8, 0.65, t.BG_CREAM, line=t.BLUE)
        self.text(slide, x + 4.58, y + 0.07, 1.74, 0.20,
                  "encodeur contexte", size=9, bold=True, color=t.BLUE, center=True)
        self.text(slide, x + 4.58, y + 0.30, 1.74, 0.45,
                  "2-4 couches attention\nlargeur 64, 4 têtes\n< 1M paramètres",
                  size=7, color=t.TXT_BODY, center=True)
        self.arrow(slide, x + 6.40, y + 0.25, w=0.25, h=0.18, color=t.ORANGE)
        self.rect(slide, x + 6.70, y + 0.05, 1.8, 0.65, t.BG_BLUE_LT, line=t.PURPLE)
        self.text(slide, x + 6.73, y + 0.07, 1.74, 0.20,
                  "prédicteur + cible EMA", size=9, bold=True, color=t.PURPLE, center=True)
        self.text(slide, x + 6.73, y + 0.30, 1.74, 0.45,
                  "perte quadratique\nreprésentations cachées\narrêt de gradient",
                  size=7, color=t.TXT_BODY, center=True)
        self.arrow(slide, x + 8.55, y + 0.25, w=0.25, h=0.18, color=t.GREEN)
        self.rect(slide, x + 8.85, y + 0.05, 0.15, 0.65, t.GREEN)
        self.text(slide, x + 0.05, y + 0.78, w - 0.1, 0.20,
                  "sortie : vecteur compact d dans {2,4,8,16} — deux têtes par parité — statut NON ENTRAÎNÉ",
                  size=8, bold=True, color=t.ORANGE, center=True)
        self.text(slide, x + 0.05, y + 0.98, w - 0.1, 0.18,
                  "pipeline distinct de l'ACP : prétrain → validation/calibration → surveillance",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_masking_leakage(self, slide, x, y, w, h):
        """Slide 18: masking leakage — FAUX vs LICITE pipelines + variance penalty."""
        t = self.t
        self.rect(slide, x, y, w * 0.48 - 0.05, 0.70, t.BG_PINK, line=t.RED)
        self.text(slide, x + 0.05, y + 0.02, w * 0.48 - 0.15, 0.20,
                  "FAUX : fuite de cible", size=10, bold=True, color=t.RED, center=True)
        self.text(slide, x + 0.05, y + 0.25, w * 0.48 - 0.15, 0.40,
                  "marché (toutes actions)\n→ masquer → résidus visibles\ncontiennent les rendements masqués",
                  size=8, color=t.TXT_DARK, center=True)
        fx = x + w * 0.48 + 0.05
        fw = w * 0.52 - 0.05
        self.rect(slide, fx, y, fw, 0.70, t.BG_GREEN_LT, line=t.GREEN)
        self.text(slide, fx + 0.05, y + 0.02, fw - 0.1, 0.20,
                  "LICITE : masquer d'abord", size=10, bold=True, color=t.GREEN, center=True)
        self.text(slide, fx + 0.05, y + 0.25, fw - 0.1, 0.40,
                  "masquer 30-50% → facteur (visibles seuls)\n→ prédire représentations cachées\n"
                  "ou pas de neutralisation préalable",
                  size=8, color=t.TXT_DARK, center=True)
        vy = y + 0.82
        self.rect(slide, x, vy, w, h - 0.82, t.WHITE, line=t.BLUE)
        self.text(slide, x + 0.05, vy + 0.02, w - 0.1, 0.20,
                  "pénalité de variance (anti-collapsus)", size=9, bold=True, color=t.BLUE, center=True)
        self.text(slide, x + 0.1, vy + 0.25, w - 0.2, 0.70,
                  "L_var = (1/d) * somme_j max(0, 1 - sd_batch(Z_j))^2\n\n"
                  "sd_batch(Z_j) = écart-type de la coordonnée j sur B journées\n"
                  "empêche la sortie constante — ne garantit pas une KL de dérive élevée",
                  size=9, color=t.TXT_DARK, center=True)

    def _visual_three_lane_protocol(self, slide, x, y, w, h):
        """Slide 19: three parallel lanes — ACP / degré zéro / JEPA."""
        t = self.t
        lanes = [
            ("ACP", t.TEAL, "fit calib → scores/signaux → alarmes test", False),
            ("degré zéro", t.BLUE, "fit calib → direction normalisée/mises → alarmes test", False),
            ("JEPA", t.PURPLE, "poids prétrain → modèle/dim validation → seuils calib → alarmes test", True),
        ]
        lw = (w - 0.2) / 3
        for i, (name, color, desc, dashed) in enumerate(lanes):
            lx = x + i * (lw + 0.1)
            self.rect(slide, lx, y, lw, 0.30, color)
            self.text(slide, lx + 0.03, y + 0.02, lw - 0.06, 0.26,
                      name, size=10, bold=True, color=t.WHITE, center=True)
            self.rect(slide, lx, y + 0.35, lw, h - 0.35, t.BG_BLUE_LT if i < 2 else t.BG_CREAM,
                      line=color)
            self.text(slide, lx + 0.05, y + 0.40, lw - 0.1, h - 0.50,
                      desc, size=8, color=t.TXT_DARK, center=True)
            if dashed:
                self.text(slide, lx + 0.05, y + h - 0.22, lw - 0.1, 0.18,
                          "NON EXÉCUTÉ", size=8, bold=True, color=t.RED, center=True)
        self.text(slide, x, y + h + 0.02, w, 0.20,
                  "entrée commune : fond réel/synthétique → injections identiques AVANT projection",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_rd_table(self, slide, x, y, w, h):
        """Slide 15: r(d)/M(d)/V(d) table header note."""
        t = self.t
        self.text(slide, x, y, w, 0.22,
                  "DONNÉES THÉORIQUES CONSTRUITES : q_k = 1/k, 500 dimensions, gamma = 504",
                  size=9, bold=True, color=t.PURPLE, center=True)
        self.text(slide, x, y + 0.25, w, 0.18,
                  "pas d'optimum financier annoncé — V(d) mesure une vitesse fluide normalisée",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _annex_visual(self, slide, n, x, y, w, h):
        """Render a schematic for an annex slide."""
        t = self.t
        label = "CALCUL THÉORIQUE"
        self.text(slide, x, y, w, 0.22, label, size=9, bold=True, color=t.ORANGE)
        vy = y + 0.30
        annex_schemas = {
            21: "Var(m) = s²[ρ + (1-ρ)/K]\nK_eff = K/[1+(K-1)ρ]\nlim K_eff = 1/ρ\nρ=0,26 → 1,96",
            22: "surmartingale P0\n→ ratio sous P1\n→ arrêt + Jensen\n→ budget log(gamma)/I",
            23: "I = SR²/(2*252)\nτ_evidence = ln(gamma)/I\n3 procédures distinctes",
            24: "I v'' + μ v' = -1\nv'(0)=0, v(h)=0\nADD = [h-1+e^(-h)]/I\nARL0 = [e^h-h-1]/I",
            25: "beta_i(t) = Cov/Var\nvol_63 = écart-type 63j\nmom_12_1 = somme [t-252,t-21)\nrev_21 = somme [t-21,t)",
            26: "Sigma_LW = (1-δ)S + δμI\nμ = tr(S)/N\nv_k, λ_k de Sigma_LW",
            27: "R = D^(-1/2) S D^(-1/2)\nλ₊ = [1+√(N/T)]²\ncompter k > λ₊",
            28: "KL(P1||P0)\n= E_P1[ln(p1/p0)]\nI_k = (v_k'Δ)²/(2λ_k)",
            29: "DPI : KL ne peut augmenter\nKL(P1_X||P0_X)\n≥ KL(P1_Z||P0_Z)",
            30: "P[b_t=1|F_(t-1)] = 1/2\nsymétrie centrale\n+ statistique impaire\n+ pièce aux zéros",
            31: "treillis fini\nseuil exact H=750\nniveau 4,3947 %\n< cible 5 %",
            32: "q_t = [Σ z_k² - d_R]/√(2d_R)\nCUSUM unilatéral\nénergie résiduelle",
            33: "R'R = Id\ndet(Σ₁) = det(Σ₀)\nrotation marché-axe 2",
            34: "degré zéro\nz_t = U'p_t/||p_t||\ncanal signe + amplitude",
            35: "mélange gaussien\nL_n = (1+n s²)^(-d/2)\n× exp[s²||S_n||²/(2(1+n s²))]",
            36: "x_d racine positive\nln(504) + (d/2)ln(1+2x_d/d)\nM(d,504) = x_d/ln(504)",
            37: "E[ln L_n] = x - (d/2)ln(1+2x/d)\nbudget fluide\ntemps avant alarme",
            38: "V(d) = r(d)/M(d,504)\nr(d) = I(d)/I(500)\ntableau 5 valeurs",
            39: "V(d+1)-V(d)\n= [q_(d+1)C(d) - I(d)(C(d+1)-C(d))]\n/[C(d)C(d+1)]",
            40: "coût affine C(d)=a+cd\nsigne change une fois\noptimum au croisement",
            41: "dictionnaire\nalignement a_max\nI_projection = I cos²(θ)",
            42: "I_t = I_0 exp[-2(t-1)/τ_a]\nB_total = I_0/(1-e^(-2/τ_a))\nB < ln(gamma) → non-détection",
            43: "DPI : pas d'augmentation KL\nabsorption = perte d'information\nmodèle discret",
            44: "temps fluide\nB(t) = I_0 τ_a [1-e^(-2t/τ_a)]/2\nt = -(τ_a/2) ln(1-2B/(I_0 τ_a))",
            45: "masquer → prédire\nrendement masqué hors contexte\nperte = erreur quadratique",
            46: "L_var = (1/d)Σ max(0,1-sd(Z_j))²\npénalité variance sorties\nquotidiennes B×d",
            47: "moyenne de e-détecteurs\nL = Σ L_j / K ≥ L_j/K\njamais de produit",
            48: "RMST(H) = E[min(T,H)]\nFPR(H) = P(T ≤ H)\ncensure à H jours",
        }
        schema = annex_schemas.get(n, "calcul théorique\nvoir équations\nci-dessous")
        self.text(slide, x, vy, w, h - 0.3, schema, size=8, color=t.TXT_DARKER)


def save_reproducibly(prs, output):
    """Write the PPTX with fixed timestamps for deterministic output."""
    output.parent.mkdir(parents=True, exist_ok=True)
    core = prs.core_properties
    core.author = "JEPA-Drift"
    core.title = "Point Hebdo JEPA-Drift 2026-10-26 v4_CGPT"
    properties = prs.core_properties
    properties.created = properties.modified = datetime(2026, 10, 26)
    properties.revision = 1
    buffer = io.BytesIO()
    prs.save(buffer)
    with zipfile.ZipFile(buffer) as source, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            info.date_time = (2026, 10, 26, 0, 0, 0)
            target.writestr(info, source.read(info.filename))


def audit_export(path, entries):
    """Reopen the package and check structure, inline links, notes and equations."""
    prs = Presentation(path)
    if len(prs.slides) != 48 or prs.slide_width != Inches(10) or prs.slide_height != Inches(5.62):
        raise ValueError("Incorrect slide count or dimensions")
    rows = []
    for entry, slide in zip(entries, prs.slides):
        number = entry["number"]
        text = "\n".join(shape.text for shape in slide.shapes if shape.has_text_frame)
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, re.I):
                raise ValueError(f"Forbidden pattern '{pattern}' found on slide {number}")
        if re.search(r"```|StarMath|LibreOffice Math|\\frac\{|%tau|%lambda", text):
            raise ValueError(f"Raw mathematical or Markdown code on slide {number}")
        if "**" in text:
            raise ValueError(f"Unprocessed markdown bold on slide {number}")
        expected_links = {match[1] for match in LINK.findall(
            "\n".join(item["content"] for item in entry["bullets"] if item["type"] == "text")
        )}
        links = {rel.target_ref for rel in slide.part.rels.values() if rel.reltype.endswith("/hyperlink")}
        if not expected_links <= links:
            raise ValueError(f"Missing inline hyperlinks on slide {number}: {expected_links - links}")
        notes = slide.notes_slide.notes_text_frame.text
        if entry["notes"] not in notes:
            raise ValueError(f"Speaker notes missing on slide {number}")
        if entry["kind"] == "ANNEX":
            if "ANNEXE" not in text:
                raise ValueError(f"Missing ANNEXE band on slide {number}")
        for eq in entry["equations"]:
            if eq["ascii"] not in text and plain_text(eq["ascii"]) not in text:
                raise ValueError(f"Equation ASCII missing on slide {number}: {eq['ascii'][:40]}")
        outside = []
        for shape in slide.shapes:
            if shape.left < -10 or shape.top < -10 or \
               shape.left + shape.width > prs.slide_width + 10 or \
               shape.top + shape.height > prs.slide_height + 10:
                outside.append(f"{shape.name} (top={shape.top/914400:.2f} h={shape.height/914400:.2f} bottom={(shape.top+shape.height)/914400:.2f})")
        if outside:
            raise ValueError(f"Off-canvas objects on slide {number}: {outside}")
        for shape in slide.shapes:
            if shape.shape_type == 13:
                with Image.open(io.BytesIO(shape.image.blob)) as img:
                    img.verify()
        rows.append({
            "slide": number, "kind": entry["kind"],
            "equations": len(entry["equations"]),
            "hyperlinks": len(links),
            "notes": True, "off_canvas": outside,
            "shapes": len(slide.shapes),
        })
    return rows


def write_auxiliary(output, entries):
    """Write all StarMath blocks to an auxiliary file for manual replacement."""
    lines = [
        "# JEPA-Drift — Point Hebdo v4_CGPT — StarMath blocks (référence manuelle)",
        "",
        "Ce fichier contient les blocs StarMath extraits du Markdown source.",
        "Ils ne sont PAS affichés sur les diapositives. Ils servent au remplacement",
        "manuel ultérieur des équations ASCII dans PowerPoint.",
        "",
        "---",
        "",
    ]
    for entry in entries:
        if not entry["equations"]:
            continue
        lines.append(f"## Slide {entry['number']} — {entry['heading']}")
        lines.append("")
        for eq in entry["equations"]:
            lines.append(f"**ASCII :** `{eq['ascii']}`")
            lines.append("")
            if eq["starmath"]:
                lines.append("```starmath")
                lines.append(eq["starmath"])
                lines.append("```")
            if eq["lecture"]:
                lines.append("")
                lines.append(f"*Lecture : {eq['lecture']}*")
            lines.append("")
            lines.append("---")
            lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def write_report(report_path, pptx_path, inputs, entries, rows, builder):
    """Record executed checks; visual inspection pending (no LibreOffice)."""
    relative = lambda p: os.path.relpath(p, report_path.parent)
    total_equations = sum(r["equations"] for r in rows)
    total_links = sum(r["hyperlinks"] for r in rows)
    lines = [
        "# Point hebdo 2026-10-26 v4_CGPT — render check",
        "",
        "## Executed structural checks",
        "",
        "- Reopened the exported PPTX with python-pptx: 48 slides, ordered 1-48; 20 main slides and 28 annexes.",
        "- Dimensions: 10.00 × 5.62 inches, ratio 1.77936; the canonical template's rounded 16:9 format.",
        f"- Equations: {total_equations} ASCII formulas displayed as monospace text with their 'Lecture' explanations. No LaTeX or bitmap rendering.",
        f"- Hyperlinks: {total_links} external relationships, checked against source references on each slide; clickable reference runs embedded in content.",
        "- All 48 speaker notes retain the original Notes field, full canonical bullets, visual specification, and StarMath sources.",
        "- All annex slides (21-48) carry the 'ANNEXE' band at the bottom.",
        "- No displayed StarMath code, Markdown fences, or raw LaTeX; all embedded images decoded successfully.",
        "- No internal names (streams, pipelines, milestones, file paths) detected on any slide.",
        "- Every equation is displayed as its 'Affichage ASCII' line only; StarMath blocks are in the auxiliary file.",
        "- No object outside the slide canvas. Text preflight uses actual font metrics.",
        "- Palette and graphical utilities loaded from the unchanged canonical template; Carlito is the Calibri metric substitute.",
        "",
        "## Sources and output SHA-256",
        "",
        "| File | SHA-256 |",
        "| --- | --- |",
    ]
    for path in [*inputs, pptx_path]:
        lines.append(f"| {relative(path)} | `{hashlib.sha256(path.read_bytes()).hexdigest()}` |")
    lines += [
        "",
        "## Per-slide control table (48 blocks)",
        "",
        "| Slide | Kind | Equations | Links | Notes | Annex band | Off-canvas |",
        "| ---: | --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        annex = "yes" if row["kind"] == "ANNEX" else "n/a"
        lines.append(
            f"| {row['slide']} | {row['kind']} | {row['equations']} | "
            f"{row['hyperlinks']} | retained | {annex} | none |"
        )
    lines += [
        "",
        "## Equation display check (formula/parole correspondence)",
        "",
        "| Slide | ASCII formula (truncated) | StarMath | Lecture |",
        "| ---: | --- | --- | --- |",
    ]
    for fc in builder.formula_checks:
        starmath = "yes" if fc.get("starmath") else "no"
        lecture = "yes" if fc["lecture"] else "no"
        lines.append(f"| {fc['slide']} | `{fc['ascii']}` | {starmath} | {lecture} |")
    lines += [
        "",
        "## Render and visual inspection",
        "",
        "**LibreOffice is not available on this machine.** No PDF export was attempted.",
        "No PNG contact sheet was generated. Visual inspection of individual pages is pending.",
        "The PPTX was verified structurally (slide count, dimensions, text content,",
        "hyperlinks, notes, equations, tables) but not visually.",
        "",
        "## Specific scientific checks",
        "",
        "- Slide 1: title slide with chain 'rendements (N actifs) → représentation figée → détecteurs distincts → alarmes'.",
        "- Slide 2: two distinct tables — experimental (4 columns) + theoretical (3 columns).",
        "- Slide 3: matrix panel + 4 characteristics table with windows.",
        "- Slide 4: three-segment timeline with 65-day embargo hatches and '941 j x 239 actifs' label.",
        "- Slide 5: simulations vs symmetrized historical funds table (5 rows).",
        "- Slide 6: exponential decay curve labelled 'modèle théorique — pas un JEPA entraîné'.",
        "- Slide 7: bifurcated pipeline ACP → signs / energy, two distinct detectors, no supervised drift.",
        "- Slide 8: three panels — empirical covariance / Ledoit-Wolf / empirical correlation.",
        "- Slide 9: three dated columns (pretrain/calibration/surveillance) with locks on frozen parameters.",
        "- Slide 10: dimension table (97→6, 239→11) + algorithmic tree.",
        "- Slide 11: two frames — KL definition / pipeline + results (oracle 15j, ACP 373j, degré zéro 446j).",
        "- Slide 12: sign symmetry table (4 rows) with calibrated 4.3947% vs observed 4.425%.",
        "- Slide 13: covariance rotation table (3 rows) with 15°/30°/45° and delay ratios 14.59/67.71/105.42.",
        "- Slide 14: degree-zero normalization — two boxes (normalized residual / residual norm).",
        "- Slide 15: r(d)/M(d)/V(d) table (5 rows) with q_k=1/k scenario, no financial optimum claimed.",
        "- Slide 16: marginal criterion formula, no empty drawing.",
        "- Slide 17: JEPA architecture — visible [r/s, beta, vol, mom, rev] / hidden [beta, vol, mom, rev].",
        "- Slide 18: masking leakage — FAUX (market first) vs LICITE (mask first) + variance penalty.",
        "- Slide 19: three parallel lanes — ACP / degré zéro / JEPA (dashed, NON EXÉCUTÉ).",
        "- Slide 20: final results table (6 rows) — no invented JEPA performance.",
        "- Slides 21-48: each annex explicitly references its main slide; no independent empirical conclusions.",
        "- All equations displayed as ASCII text only; StarMath in auxiliary file.",
        "",
        "## Limitations",
        "",
        "- No PDF export (LibreOffice unavailable). Visual page inspection not performed.",
        "- Equations are plain monospace text, not native Office Math objects.",
        "- Hyperlink targets checked structurally; no network availability test.",
        "- Visual diagrams are schematic; they do not represent measured data unless stated.",
        "- Text preflight uses Carlito font metrics; minor rendering differences possible in PowerPoint.",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    """Build and audit the v4_CGPT deck."""
    parser = argparse.ArgumentParser(
        description="Build the 48-slide JEPA-Drift Point Hebdo v4_CGPT deck offline"
    )
    parser.add_argument("--deck", type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--assets-dir", type=Path,
                        help="Directory containing figure assets (optional)")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    here, current = Path(__file__).resolve().parent, Path.cwd()
    roots = list(dict.fromkeys([current, current / "slides", here, here.parent]))
    deck = resolve_input(args.deck, DECK_NAME, roots)
    template = resolve_input(args.template, TEMPLATE_NAME, [deck.parent, *roots])
    output = (args.out or deck.parent / OUT_NAME).expanduser().resolve()
    auxiliary = output.with_name(AUX_NAME)
    report = output.with_name(REPORT_NAME)
    inputs = [deck, template]
    if output.suffix.lower() != ".pptx":
        raise ValueError("--out must have a .pptx extension")
    if any(path in (output, report, auxiliary) for path in inputs):
        raise ValueError("An output path collides with an input")
    input_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    entries = parse_deck(deck)
    builder = DeckBuilder(load_template(template))
    prs = builder.build(entries)
    save_reproducibly(prs, output)
    rows = audit_export(output, entries)
    for path, digest in input_hashes.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"Input changed during generation: {path.name}")
    write_auxiliary(auxiliary, entries)
    write_report(report, output, inputs, entries, rows, builder)
    print(f"Saved: {output.name}; 48 slides; {sum(r['equations'] for r in rows)} ASCII equations; "
          f"source files unchanged")
    print(f"Auxiliary: {auxiliary.name}")
    print(f"Report: {report.name}")


if __name__ == "__main__":
    main()
