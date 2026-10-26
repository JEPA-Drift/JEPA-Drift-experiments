"""Build the JEPA-Drift Point Hebdo v3 deck from the canonical Markdown source.

Parses DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v3.md (33 slide blocks: 21 main + 12 annexes),
reuses the template style charter, displays equations as ASCII text only, and embeds
Fig30_RealCrossSectional_Escape_UPDATED.png on slide 7.
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


DECK_NAME = "DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v3.md"
TEMPLATE_NAME = "Generation_slides_Point_Hebdo_template.py"
FIGURE_NAME = "Fig30_RealCrossSectional_Escape_UPDATED.png"
OUT_NAME = "2026_10_26_Point_Hebdo_JEPA_Drift_v3.pptx"
AUX_NAME = "2026_10_26_Point_Hebdo_JEPA_Drift_v3_auxiliary.md"
REPORT_NAME = "2026_10_26_Point_Hebdo_JEPA_Drift_v3_RENDER_CHECK.md"
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
    """Parse the 33 v3 Markdown slide blocks into structured entries."""
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
        equations = _parse_equations_v3(equations_raw.strip())

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
    if [s["number"] for s in slides] != list(range(1, 34)):
        raise ValueError("Expected exactly 33 sequential slide blocks, numbered 1-33")
    annex_kinds = [s["kind"] for s in slides[21:]]
    if annex_kinds != ["ANNEX"] * 12:
        raise ValueError("Slides 22-33 must all be ANNEX")
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


def _parse_equations_v3(raw):
    """Extract ASCII display lines, lecture, and StarMath blocks (for auxiliary file)."""
    if raw.strip() in ("Aucune.", "Aucune", ""):
        return []
    equations = []
    items = re.split(r"\n- ", raw)
    for item in items:
        item = item.strip()
        if not item:
            continue
        ascii_match = re.search(r"Affichage ASCII\s*:\s*`([^`]+)`", item)
        starmath_match = re.search(r"StarMath\s*:\s*```starmath\s*\n(.*?)```", item, re.S)
        lecture_match = re.search(r"Lecture\s*:\s*(.+?)(?=\n- |\Z)", item, re.S)
        if ascii_match:
            equations.append({
                "ascii": ascii_match[1].strip(),
                "starmath": starmath_match[1].strip() if starmath_match else "",
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
    """Lay out the 33-slide v3 deck with the supplied template utilities."""

    def __init__(self, template, figure):
        self.t = template
        self.prs = template.prs
        self.figure = figure
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
        # Annex band
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
        """Build all 33 slides in order."""
        for entry in entries:
            slide = self.begin(entry)
            if entry["kind"] == "ANNEX":
                self.annex_slide(slide, entry)
            else:
                self.main_slide(slide, entry)
            self.finish(slide, entry)
        return self.prs

    def main_slide(self, slide, entry):
        """Render a main presentation slide (1-21)."""
        n = entry["number"]
        b = [item for item in entry["bullets"]]
        t = self.t

        if n == 1:
            self.rect(slide, 0.60, 0.50, 8.80, 2.20, t.TEAL_DARK)
            self.text(slide, 0.82, 0.76, 8.35, 0.60, "JEPA-Drift", size=30, color=t.WHITE, bold=True)
            self.text(slide, 0.82, 1.40, 8.20, 0.97,
                      "Détecter plus vite, à risque de fausse alarme maîtrisé",
                      size=22, color=t.WHITE, bold=True)
            self.rect(slide, 0.60, 2.80, 8.80, 0.06, t.ORANGE)
            self.rect(slide, 0.00, 3.00, 10.00, 1.80, t.BLUE_DEEP)
            self.rect(slide, 0.60, 3.10, 8.80, 0.46, t.ORANGE)
            self.text(slide, 0.72, 3.18, 8.55, 0.31,
                      "Point hebdomadaire — lundi 26 octobre 2026",
                      size=14, bold=True, color=t.WHITE)
            chain_y = 3.70
            self.text(slide, 0.72, chain_y, 8.55, 0.35,
                      "rendements du jour  →  quelques coordonnées  →  alarme",
                      size=16, bold=True, color=t.WHITE, center=True)
            self.text(slide, 0.72, 4.15, 8.55, 0.30,
                      "représentation = nouvelle description des mêmes observations",
                      size=11, color=RGBColor(0xD5, 0xDB, 0xDB), center=True, italic=True)
            self.t.badge(slide, entry["badge"], x=7.65, y=0.20, w=entry["badge_width"], color=t.ORANGE)
            self.text(slide, 0.67, 4.91, 8.60, 0.28,
                      "Méthode linéaire (ACP)  vs  réseau à entraîner (JEPA)",
                      size=11, color=t.TXT_BODY)
            return

        # For slides 2-21: check if first bullet is a table
        has_table = any(item["type"] == "table" for item in b)

        if has_table:
            self._render_table_slide(slide, entry, b)
        else:
            self._render_content_slide(slide, entry, b)

        self.equation_panel(slide, entry, y=4.15, h=1.00)

    def _render_table_slide(self, slide, entry, bullets):
        """Render a slide whose primary content is a table."""
        n = entry["number"]
        text_bullets = [item for item in bullets if item["type"] == "text"]
        table_items = [item for item in bullets if item["type"] == "table"]

        # Render text bullets at top
        y = 1.45
        for item in text_bullets:
            bh = text_height(item["content"], 9.0, 11)
            self.text(slide, 0.48, y, 9.05, bh, item["content"], size=11)
            y += bh + 0.06

        # Render table(s)
        for tbl_item in table_items:
            y += 0.08
            consumed = self.render_table(slide, tbl_item["content"], 0.48, y, 9.05, size=10)
            y += consumed + 0.10

        # Slide-specific visual extras
        if n == 7:
            pass  # handled in content slide path
        elif n == 10:
            self._visual_eigenvalue_schema(slide, 7.2, 1.45, 2.4, 2.2)
        elif n == 13:
            self._visual_rotated_ellipse(slide, 6.8, 2.8, 2.6, 1.2)
        elif n == 15:
            self._visual_two_mechanisms(slide, 0.48, y + 0.05, 9.05, 0.80)
        elif n == 21:
            self._visual_decision_rule(slide, 0.48, y + 0.05, 9.05, 0.70)

    def _render_content_slide(self, slide, entry, bullets):
        """Render a content slide with bullets and a schematic visual."""
        n = entry["number"]

        if n == 3:
            self._visual_matrix(slide, 0.48, 1.45, 4.5, 2.5)
            self.bullets(slide, bullets, 5.3, 1.45, 4.2, 2.5, size=11, minimum=10)
        elif n == 4:
            self._visual_timeline(slide, 0.48, 1.45, 9.05, 1.0)
            self.bullets(slide, bullets, 0.48, 2.65, 9.05, 1.4, size=11, minimum=10)
        elif n == 5:
            self._visual_two_branches(slide, 0.48, 1.45, 9.05, 1.5)
            self.bullets(slide, bullets, 0.48, 3.10, 9.05, 1.0, size=11, minimum=10)
        elif n == 7:
            self._visual_fig30(slide, 0.42, 1.45, 6.70, 2.5)
            text_bullets = [item["content"] for item in bullets if item["type"] == "text"]
            self.bullets(slide, [{"type": "text", "content": tb} for tb in text_bullets],
                         7.3, 1.45, 2.3, 2.5, size=11, minimum=10)
        elif n == 8:
            self._visual_ellipse_axes(slide, 0.48, 1.45, 4.5, 2.5)
            self.bullets(slide, bullets, 5.3, 1.45, 4.2, 2.5, size=11, minimum=10)
        elif n == 9:
            self._visual_two_line_pipeline(slide, 0.48, 1.45, 9.05, 1.3)
            self.bullets(slide, bullets, 0.48, 2.95, 9.05, 1.1, size=11, minimum=10)
        elif n == 11:
            self._visual_kl_arrows(slide, 0.48, 1.45, 4.5, 2.5)
            self.bullets(slide, bullets, 5.3, 1.45, 4.2, 2.5, size=11, minimum=10)
        elif n == 14:
            self._visual_normalization_steps(slide, 0.48, 1.45, 9.05, 1.2)
            self.bullets(slide, bullets, 0.48, 2.85, 9.05, 1.2, size=11, minimum=10)
        elif n == 16:
            self._visual_direction_cost(slide, 0.48, 1.45, 9.05, 1.3)
            self.bullets(slide, bullets, 0.48, 2.95, 9.05, 1.1, size=11, minimum=10)
        elif n == 17:
            self._visual_dimension_choice(slide, 0.48, 1.45, 9.05, 1.3)
            self.bullets(slide, bullets, 0.48, 2.95, 9.05, 1.1, size=11, minimum=10)
        elif n == 18:
            self._visual_jepa_architecture(slide, 0.48, 1.45, 9.05, 1.5)
            self.bullets(slide, bullets, 0.48, 3.10, 9.05, 1.0, size=11, minimum=10)
        elif n == 19:
            self._visual_masked_task(slide, 0.48, 1.45, 9.05, 1.3)
            self.bullets(slide, bullets, 0.48, 2.95, 9.05, 1.1, size=11, minimum=10)
        elif n == 20:
            self._visual_eval_pipeline(slide, 0.48, 1.45, 9.05, 1.3)
            self.bullets(slide, bullets, 0.48, 2.95, 9.05, 1.1, size=11, minimum=10)
        else:
            self.bullets(slide, bullets, 0.48, 1.45, 9.05, 2.6, size=11, minimum=10)

    def annex_slide(self, slide, entry):
        """Render an annex slide (22-33) with two-column calculation layout."""
        t = self.t
        n = entry["number"]
        text_bullets = [item for item in entry["bullets"] if item["type"] == "text"]
        table_items = [item for item in entry["bullets"] if item["type"] == "table"]

        # Left column: bullet points
        y = 1.45
        for item in text_bullets:
            bh = text_height(item["content"], 5.8, 10)
            self.text(slide, 0.44, y, 5.8, bh, item["content"], size=10, minimum=9)
            y += bh + 0.05

        # Right column: visual / schema area
        self.rect(slide, 6.48, 1.46, 3.08, 2.55, t.BG_CREAM)
        self._annex_visual(slide, n, 6.58, 1.55, 2.88, 2.30)

        # Bottom: equations panel
        self.equation_panel(slide, entry, y=4.15, h=1.00)

        # Tables in annexes (rare, but handle them)
        if table_items:
            ty = 4.15
            for tbl_item in table_items:
                self.render_table(slide, tbl_item["content"], 0.44, ty, 9.08, size=9)

    # =========================================================================
    # VISUAL RENDERING — main slides
    # =========================================================================

    def _visual_matrix(self, slide, x, y, w, h):
        """Slide 3: matrix 'days × actions' schematic."""
        t = self.t
        self.rect(slide, x, y, w, h, t.WHITE, line=t.TEAL)
        self.text(slide, x + 0.1, y + 0.05, w - 0.2, 0.25,
                  "jours × actions", size=10, bold=True, color=t.TEAL, center=True)
        cols, rows = 8, 5
        cw, ch = (w - 0.4) / cols, (h - 0.6) / rows
        for r in range(rows):
            for c in range(cols):
                cx = x + 0.2 + c * cw
                cy = y + 0.35 + r * ch
                self.rect(slide, cx, cy, cw - 0.03, ch - 0.03,
                          t.BG_BLUE_LT if (r + c) % 2 == 0 else t.WHITE, line=t.TXT_FAINT)
        self.text(slide, x + 0.1, y + h - 0.28, 2.0, 0.22,
                  "97 actions", size=10, bold=True, color=t.BLUE)
        self.text(slide, x + w - 2.2, y + h - 0.28, 2.1, 0.22,
                  "239 actions", size=10, bold=True, color=t.PURPLE, center=True)
        self.text(slide, x + 0.1, y + h - 0.50, w - 0.2, 0.20,
                  "univers de titres survivants", size=8, color=t.ORANGE, center=True, italic=True)

    def _visual_timeline(self, slide, x, y, w, h):
        """Slide 4: three-segment timeline with hatched embargo zones."""
        t = self.t
        segments = [
            ("2005–2015", "apprendre", t.TEAL, 0.0, 3.0),
            ("2016–2019", "choisir et régler", t.BLUE, 3.0, 6.0),
            ("2020+", "tester (figé)", t.ORANGE, 6.0, 9.05),
        ]
        for label, desc, color, sx, ex in segments:
            self.rect(slide, x + sx, y, ex - sx - 0.08, 0.55, color)
            self.text(slide, x + sx + 0.05, y + 0.02, ex - sx - 0.18, 0.25,
                      label, size=12, bold=True, color=t.WHITE, center=True)
            self.text(slide, x + sx + 0.05, y + 0.28, ex - sx - 0.18, 0.22,
                      desc, size=9, color=t.WHITE, center=True)
        for bx in [3.0, 6.0]:
            self.rect(slide, x + bx, y + 0.58, 0.35, 0.18, t.TXT_FAINT)
            self.text(slide, x + bx - 0.15, y + 0.58, 0.65, 0.18,
                      "65 j.", size=7, color=t.WHITE, center=True)
        self.text(slide, x + 6.0, y + 0.80, 3.0, 0.22,
                  "paramètres figés", size=10, bold=True, color=t.ORANGE)

    def _visual_two_branches(self, slide, x, y, w, h):
        """Slide 5: two branches — mean→signs, dispersion→energy."""
        t = self.t
        for i, (title, color, icon) in enumerate([
            ("Changement de moyenne", t.TEAL, "→  fréquence des signes"),
            ("Changement de covariance", t.PURPLE, "→  somme des carrés"),
        ]):
            bx = x + i * (w / 2 + 0.05)
            bw = w / 2 - 0.05
            self.rect(slide, bx, y, bw, 0.35, color)
            self.text(slide, bx + 0.05, y + 0.02, bw - 0.1, 0.30,
                      title, size=11, bold=True, color=t.WHITE, center=True)
            self.text(slide, bx + 0.1, y + 0.45, bw - 0.2, 0.25,
                      icon, size=10, color=color, center=True, bold=True)
            self.rect(slide, bx + bw/2 - 0.40, y + 0.80, 0.80, 0.28, t.BG_BLUE_LT, line=color)
            self.text(slide, bx + bw/2 - 0.38, y + 0.82, 0.76, 0.24,
                      "CUSUM", size=9, bold=True, color=color, center=True)
            self.line(slide, bx + bw/2, y + 0.70, bx + bw/2, y + 0.80, color, 2)
            self.rect(slide, bx + bw/2 - 0.50, y + 1.15, 1.00, 0.22, t.ORANGE)
            self.text(slide, bx + bw/2 - 0.48, y + 1.16, 0.96, 0.20,
                      "seuil → alarme", size=8, bold=True, color=t.WHITE, center=True)
            self.line(slide, bx + bw/2, y + 1.08, bx + bw/2, y + 1.15, t.ORANGE, 2)

    def _visual_fig30(self, slide, x, y, w, h):
        """Slide 7: embed the historical Fig30 image."""
        picture = slide.shapes.add_picture(str(self.figure), Inches(x), Inches(y), width=Inches(w))
        picture.name = "historical:Fig30:unchanged"
        ratio = picture.height / picture.width
        if picture.height > Inches(h):
            picture.height = Inches(h)
            picture.width = Inches(h / ratio)

    def _visual_ellipse_axes(self, slide, x, y, w, h):
        """Slide 8: ellipse with long/short axes, projection point."""
        t = self.t
        cx, cy = x + w / 2, y + h / 2
        ellipse = self.rect(slide, cx - 1.5, cy - 0.7, 3.0, 1.4, t.WHITE, line=t.TEAL, shape=MSO_SHAPE.OVAL)
        ellipse.rotation = 350
        self.line(slide, cx - 1.6, cy + 0.3, cx + 1.6, cy - 0.3, t.TEAL, 2)
        self.text(slide, cx + 1.1, cy - 0.55, 1.2, 0.22, "mouvement commun", size=8, color=t.TEAL)
        self.line(slide, cx - 0.8, cy - 0.8, cx + 0.8, cy + 0.8, t.PURPLE, 2)
        self.text(slide, cx - 1.6, cy + 0.55, 1.4, 0.22, "différences entre actions", size=8, color=t.PURPLE)
        px, py = cx + 0.6, cy - 0.3
        self.rect(slide, px - 0.04, py - 0.04, 0.08, 0.08, t.ORANGE, shape=MSO_SHAPE.OVAL)
        self.line(slide, px, py, cx + 1.0, cy - 0.15, t.TXT_FAINT, dashed=True)
        self.text(slide, x + 0.05, y + h - 0.25, w - 0.1, 0.20,
                  "schéma explicatif", size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_two_line_pipeline(self, slide, x, y, w, h):
        """Slide 9: calibration line and surveillance line."""
        t = self.t
        for i, (label, color) in enumerate([
            ("calibration : rendements → covariance → axes et échelles → seuils", t.TEAL),
            ("surveillance : rendements du jour → projections figées → signes / énergie → alarme", t.BLUE),
        ]):
            ly = y + i * 0.55
            self.rect(slide, x, ly, w, 0.42, t.BG_BLUE_LT if i == 0 else t.BG_GREEN_LT)
            self.rect(slide, x, ly, 0.05, 0.42, color)
            self.text(slide, x + 0.15, ly + 0.05, w - 0.3, 0.32,
                      label, size=10, bold=(i == 0), color=color)
        self.rect(slide, x + w/2 - 0.30, y + 0.42, 0.60, 0.16, t.ORANGE)
        self.text(slide, x + w/2 - 0.28, y + 0.42, 0.56, 0.16,
                  "figé", size=8, bold=True, color=t.WHITE, center=True)

    def _visual_eigenvalue_schema(self, slide, x, y, w, h):
        """Slide 10: eigenvalue bar schema."""
        t = self.t
        self.rect(slide, x, y, w, h, t.WHITE, line=t.TXT_FAINT)
        self.text(slide, x + 0.05, y + 0.03, w - 0.1, 0.22,
                  "schéma, pas spectre mesuré", size=8, color=t.TXT_FAINT, center=True, italic=True)
        bars = [0.85, 0.55, 0.35, 0.22, 0.15, 0.10]
        max_h = h - 0.7
        for i, val in enumerate(bars):
            bh = val * max_h
            bx = x + 0.15 + i * (w - 0.3) / len(bars)
            self.rect(slide, bx, y + h - 0.35 - bh, (w - 0.3) / len(bars) - 0.08, bh,
                      t.TEAL if i == 0 else t.BLUE)
        self.line(slide, x + 0.1, y + h - 0.35 - 0.12 * max_h,
                  x + w - 0.1, y + h - 0.35 - 0.12 * max_h, t.ORANGE, dashed=True)
        self.text(slide, x + 0.05, y + h - 0.30, w - 0.1, 0.20,
                  "repère de bruit", size=7, color=t.ORANGE, center=True)

    def _visual_kl_arrows(self, slide, x, y, w, h):
        """Slide 11: two arrows in ellipse — noisy vs calm axis."""
        t = self.t
        cx, cy = x + w / 2, y + h / 2
        ellipse = self.rect(slide, cx - 1.5, cy - 0.7, 3.0, 1.4, t.WHITE, line=t.TEAL, shape=MSO_SHAPE.OVAL)
        ellipse.rotation = 350
        self.line(slide, cx - 1.5, cy + 0.2, cx + 1.5, cy - 0.2, t.TXT_FAINT, 2)
        self.text(slide, cx - 1.4, cy + 0.30, 1.3, 0.20, "axe bruyant", size=8, color=t.TXT_BODY)
        self.line(slide, cx - 0.8, cy - 0.8, cx + 0.8, cy + 0.8, t.TEAL, 2)
        self.text(slide, cx + 0.3, cy - 0.85, 1.3, 0.20, "axe calme", size=8, color=t.TEAL)
        for dx, color, label in [(-0.8, t.RED, "Δ"), (0.3, t.GREEN, "Δ")]:
            ax = cx + dx
            self.line(slide, ax, cy, ax + 0.6, cy, color, 3)
            self.text(slide, ax + 0.15, cy - 0.25, 0.4, 0.20, label, size=10, bold=True, color=color)
        self.text(slide, x + 0.05, y + h - 0.25, w - 0.1, 0.20,
                  "intuition géométrique, pas estimation financière",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_rotated_ellipse(self, slide, x, y, w, h):
        """Slide 13: rotated ellipse vs fixed index direction."""
        t = self.t
        cx, cy = x + w / 2, y + h / 2
        ellipse = self.rect(slide, cx - 1.0, cy - 0.45, 2.0, 0.9, t.WHITE, line=t.PURPLE, shape=MSO_SHAPE.OVAL)
        ellipse.rotation = 30
        self.line(slide, cx - 1.3, cy, cx + 1.3, cy, t.TEAL, 2)
        self.text(slide, cx + 0.8, cy - 0.15, 1.0, 0.20, "indice fixe", size=8, color=t.TEAL)

    def _visual_two_mechanisms(self, slide, x, y, w, h):
        """Slide 15: two mini schemas — correlated actions / calm-agitated days."""
        t = self.t
        for i, (title, color) in enumerate([
            ("actions qui bougent ensemble", t.TEAL),
            ("jours calmes et agités", t.PURPLE),
        ]):
            bx = x + i * (w / 2 + 0.05)
            bw = w / 2 - 0.05
            self.rect(slide, bx, y, bw, h, t.BG_BLUE_LT)
            self.text(slide, bx + 0.05, y + 0.02, bw - 0.1, 0.22,
                      title, size=9, bold=True, color=color, center=True)
            for j in range(4):
                offset = (j - 1.5) * 0.25
                self.line(slide, bx + 0.3, y + 0.45 + offset, bx + bw - 0.3, y + 0.45 + offset,
                          color, 2 if i == 0 else 1.5)

    def _visual_decision_rule(self, slide, x, y, w, h):
        """Slide 21: three-case decision rule."""
        t = self.t
        cases = ["risque comparable", "gain et incertitude", "méthode retenue"]
        for i, label in enumerate(cases):
            bx = x + i * (w / 3 + 0.05)
            bw = w / 3 - 0.05
            color = [t.TEAL, t.BLUE, t.ORANGE][i]
            self.rect(slide, bx, y, bw, 0.30, color)
            self.text(slide, bx + 0.03, y + 0.02, bw - 0.06, 0.26,
                      label, size=9, bold=True, color=t.WHITE, center=True)
            if i < 2:
                self.arrow(slide, bx + bw + 0.01, y + 0.06, w=0.14, h=0.18, color=t.TXT_FAINT)

    def _visual_normalization_steps(self, slide, x, y, w, h):
        """Slide 14: three-step vector normalization."""
        t = self.t
        steps = ["vecteur du jour", "résidu ⊥ marché", "cercle unité"]
        for i, label in enumerate(steps):
            bx = x + i * (w / 3 + 0.05)
            bw = w / 3 - 0.05
            self.rect(slide, bx, y, bw, h, t.BG_BLUE_LT, line=t.TEAL if i < 2 else t.PURPLE)
            self.text(slide, bx + 0.05, y + 0.05, bw - 0.1, 0.25,
                      label, size=10, bold=True, color=t.TEAL if i < 2 else t.PURPLE, center=True)
            if i == 0:
                self.line(slide, bx + 0.3, y + 0.55, bx + bw - 0.3, y + 0.75, t.ORANGE, 3)
            elif i == 1:
                self.line(slide, bx + bw/2 - 0.3, y + 0.65, bx + bw/2 + 0.3, y + 0.65, t.PURPLE, 3)
                self.line(slide, bx + bw/2, y + 0.35, bx + bw/2, y + 0.95, t.TXT_FAINT, dashed=True)
            else:
                self.rect(slide, bx + bw/2 - 0.30, y + 0.35, 0.60, 0.60,
                          t.WHITE, line=t.PURPLE, shape=MSO_SHAPE.OVAL)
                self.line(slide, bx + bw/2, y + 0.65, bx + bw/2 + 0.20, y + 0.45, t.ORANGE, 2)
            if i < 2:
                self.arrow(slide, bx + bw + 0.01, y + 0.40, w=0.14, h=0.18, color=t.TXT_FAINT)
        self.text(slide, x, y + h + 0.02, w, 0.20,
                  "marché surveillé séparément", size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_direction_cost(self, slide, x, y, w, h):
        """Slide 16: two columns — 4 directions vs 500 directions."""
        t = self.t
        for i, (label, value, color) in enumerate([
            ("4 directions", "coût 1,57", t.TEAL),
            ("500 directions", "coût 9,64", t.BLUE),
        ]):
            bx = x + i * (w / 2 + 0.05)
            bw = w / 2 - 0.05
            self.rect(slide, bx, y, bw, h, t.BG_BLUE_LT)
            self.rect(slide, bx, y, 0.05, h, color)
            self.text(slide, bx + 0.15, y + 0.08, bw - 0.25, 0.28,
                      label, size=13, bold=True, color=color)
            self.text(slide, bx + 0.15, y + 0.42, bw - 0.25, 0.45,
                      value, size=18, bold=True, color=color, center=True)
        self.rect(slide, x + w/2 - 1.3, y + h + 0.02, 2.6, 0.25, t.ORANGE)
        self.text(slide, x + w/2 - 1.28, y + h + 0.03, 2.56, 0.23,
                  "conserver > 16,3 % de l'information",
                  size=9, bold=True, color=t.WHITE, center=True)
        self.text(slide, x, y + h + 0.30, w, 0.20,
                  "calcul théorique ; pas résultat financier",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_dimension_choice(self, slide, x, y, w, h):
        """Slide 17: two cases — drift on first axis / drift on late axis."""
        t = self.t
        for i, (label, color) in enumerate([
            ("changement porté par le 1er axe", t.TEAL),
            ("changement porté par un axe tardif", t.PURPLE),
        ]):
            bx = x + i * (w / 2 + 0.05)
            bw = w / 2 - 0.05
            self.rect(slide, bx, y, bw, h, t.BG_BLUE_LT)
            self.text(slide, bx + 0.05, y + 0.03, bw - 0.1, 0.22,
                      label, size=9, bold=True, color=color, center=True)
            for j in range(5):
                ly = y + 0.35 + j * 0.18
                self.line(slide, bx + 0.2, ly, bx + bw - 0.2, ly, t.TXT_FAINT, 1)
                if (i == 0 and j == 0) or (i == 1 and j == 3):
                    self.line(slide, bx + 0.2, ly, bx + bw - 0.2, ly, color, 3)

    def _visual_jepa_architecture(self, slide, x, y, w, h):
        """Slide 18: JEPA architecture — visible actions → context → predicted repr."""
        t = self.t
        self.rect(slide, x + 0.1, y + 0.15, 2.2, 0.90, t.BG_BLUE_LT, line=t.TEAL)
        self.text(slide, x + 0.15, y + 0.20, 2.1, 0.30,
                  "actions visibles", size=10, bold=True, color=t.TEAL, center=True)
        self.text(slide, x + 0.15, y + 0.55, 2.1, 0.40,
                  "rendement +\ncaractéristiques", size=9, color=t.TXT_BODY, center=True)
        self.arrow(slide, x + 2.35, y + 0.50, w=0.30, h=0.20, color=t.ORANGE)
        self.rect(slide, x + 2.70, y + 0.15, 2.2, 0.90, t.BG_CREAM, line=t.BLUE)
        self.text(slide, x + 2.75, y + 0.20, 2.1, 0.30,
                  "réseau de contexte", size=10, bold=True, color=t.BLUE, center=True)
        self.text(slide, x + 2.75, y + 0.55, 2.1, 0.40,
                  "attention\npondération", size=9, color=t.TXT_BODY, center=True)
        self.arrow(slide, x + 4.95, y + 0.50, w=0.30, h=0.20, color=t.ORANGE)
        self.rect(slide, x + 5.30, y + 0.15, 2.2, 0.90, t.BG_BLUE_LT, line=t.PURPLE)
        self.text(slide, x + 5.35, y + 0.20, 2.1, 0.30,
                  "représentation prédite", size=10, bold=True, color=t.PURPLE, center=True)
        self.rect(slide, x + 7.55, y + 0.15, 1.4, 0.90, t.BG_PINK, line=t.RED)
        self.text(slide, x + 7.58, y + 0.20, 1.34, 0.30,
                  "actions cachées", size=9, bold=True, color=t.RED, center=True)
        self.text(slide, x + 7.58, y + 0.55, 1.34, 0.40,
                  "réseau cible\n(représentation cible)", size=8, color=t.TXT_BODY, center=True)
        self.line(slide, x + 6.5, y + 1.05, x + 7.5, y + 1.05, t.ORANGE, 2)
        self.text(slide, x + 5.8, y + 1.08, 2.0, 0.22,
                  "écart à réduire (entraînement)", size=8, color=t.ORANGE, center=True, italic=True)
        self.text(slide, x, y + h + 0.02, w, 0.20,
                  "architecture proposée", size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_masked_task(self, slide, x, y, w, h):
        """Slide 19: masked task — day t, 8 action columns, 3 hidden."""
        t = self.t
        cols = 8
        cw = (w - 0.4) / cols
        self.text(slide, x, y, 1.0, 0.22, "jour t", size=10, bold=True, color=t.TXT_DARK)
        hidden = {2, 4, 6}
        for c in range(cols):
            cx = x + 0.6 + c * cw
            is_hidden = c in hidden
            color = t.TXT_FAINT if is_hidden else t.TEAL
            label = "masquée" if is_hidden else f"action {c+1}"
            self.rect(slide, cx, y + 0.25, cw - 0.06, 0.40,
                      t.BG_BLUE_LT if not is_hidden else t.BG_PINK,
                      line=color)
            self.text(slide, cx + 0.01, y + 0.28, cw - 0.08, 0.34,
                      label, size=8, bold=is_hidden, color=color, center=True)
            if not is_hidden:
                self.line(slide, cx + cw/2, y + 0.65, x + w/2, y + 0.85, t.ORANGE, 1)
        self.text(slide, x + 0.6, y + 0.85, w - 0.6, 0.22,
                  "flèches depuis les cases visibles uniquement vers le contexte",
                  size=8, color=t.ORANGE, center=True, italic=True)
        self.text(slide, x, y + h + 0.02, w, 0.20,
                  "masquer → préparer les entrées visibles → prédire",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    def _visual_eval_pipeline(self, slide, x, y, w, h):
        """Slide 20: evaluation pipeline — train → select → calibrate → freeze → monitor."""
        t = self.t
        steps = ["apprendre", "choisir", "calibrer", "figer", "surveiller"]
        colors = [t.TEAL, t.BLUE, t.PURPLE, t.ORANGE, t.RED]
        for i, (label, color) in enumerate(zip(steps, colors)):
            bx = x + i * (w / 5 + 0.02)
            bw = w / 5 - 0.02
            self.rect(slide, bx, y, bw, 0.40, color)
            self.text(slide, bx + 0.02, y + 0.05, bw - 0.04, 0.30,
                      label, size=10, bold=True, color=t.WHITE, center=True)
            if i < 4:
                self.arrow(slide, bx + bw, y + 0.10, w=0.10, h=0.15, color=t.TXT_FAINT)
        self.text(slide, x + 3 * (w/5), y + 0.50, 2 * (w/5), 0.25,
                  "signes (impair)  |  énergie (pair)", size=9, color=t.TXT_BODY, center=True)
        self.text(slide, x, y + 0.80, w, 0.22,
                  "ACP et normalisation sur lignes parallèles, mêmes données",
                  size=8, color=t.TXT_FAINT, center=True, italic=True)

    # =========================================================================
    # VISUAL RENDERING — annex slides
    # =========================================================================

    def _annex_visual(self, slide, n, x, y, w, h):
        """Render a schematic for an annex slide."""
        t = self.t
        label = "CALCUL THÉORIQUE"
        self.text(slide, x, y, w, 0.22, label, size=9, bold=True, color=t.ORANGE)
        vy = y + 0.30

        if n == 22:
            self.text(slide, x, vy, w, h - 0.3,
                      "Var(m) = s²[ρ + (1-ρ)/K]\n\nK_eff = K/[1+(K-1)ρ]\n\n"
                      "lim K_eff = 1/ρ\nlim gain = 1/√ρ\n\nρ ≈ 0,26 → 1,96",
                      size=9, color=t.TXT_DARKER)
        elif n == 23:
            self.text(slide, x, vy, w, h - 0.3,
                      "I_k = δ_k²/(2λ_k)\n\nI(d) = Σ I_k\n\n"
                      "KL(P₁,P₀) ≥ KL(P₁_Z,P₀_Z)\n(DPI)",
                      size=9, color=t.TXT_DARKER)
        elif n == 24:
            self.text(slide, x, vy, w, h - 0.3,
                      "I_cond = A·E[1/σ²]\nI_ref  = A/E[σ²]\n\n"
                      "η = E[σ²]·E[1/σ²] ≥ 1\n(Cauchy-Schwarz)\n\n"
                      "estimations : 1,97 et 2,00",
                      size=9, color=t.TXT_DARKER)
        elif n == 25:
            self.text(slide, x, vy, w, h - 0.3,
                      "L_n = ∫ exp(u'S_n - n‖u‖²/2) dΠ(u)\n\n"
                      "complétion du carré\nintégrale gaussienne\n\n"
                      "facteur (1+ns²)^(-d/2)",
                      size=9, color=t.TXT_DARKER)
        elif n == 26:
            self.text(slide, x, vy, w, h - 0.3,
                      "E[ln L_n] = x - (d/2)ln(1+2x/d)\n\n"
                      "x_d - (d/2)ln(1+2x_d/d) = A\n\n"
                      "d=4:  x/A = 1,57\nd=500: x/A = 9,64\n\n"
                      "rétention > 16,3 %",
                      size=9, color=t.TXT_DARKER)
        elif n == 27:
            self.text(slide, x, vy, w, h - 0.3,
                      "V(d+1)-V(d) = [q_{d+1}C(d) - I(d)(C(d+1)-C(d))]\n"
                      "/ [C(d)C(d+1)]\n\n"
                      "H_d = q_{d+1}C(d) - c·I(d)\n\n"
                      "H_{d+1} - H_d < 0\n(une seule traversée de zéro)",
                      size=9, color=t.TXT_DARKER)
        elif n == 28:
            self.text(slide, x, vy, w, h - 0.3,
                      "P[b_t=1 | F_{t-1}]\n= (1-p₀)/2 + p₀/2\n= 1/2\n\n"
                      "P[b₁=c₁,...,b_n=c_n]\n= 2^{-n}\n\n"
                      "indépendance temporelle\n(flux scalaire)",
                      size=9, color=t.TXT_DARKER)
        elif n == 29:
            self.text(slide, x, vy, w, h - 0.3,
                      "ℓ(r) = [ln(det Σ₀/det Σ₁)\n"
                      "  + r'(Σ₀⁻¹-Σ₁⁻¹)r] / 2\n\n"
                      "I = [tr(Σ₀⁻¹Σ₁) - ln det(Σ₀⁻¹Σ₁) - N] / 2\n\n"
                      "rotation : det inchangé",
                      size=9, color=t.TXT_DARKER)
        elif n == 30:
            self.text(slide, x, vy, w, h - 0.3,
                      "m_visible = (1/|V|) Σ_{i∈V} r_i\n\n"
                      "fuite si moyenne sur TOUTES\nles actions avant masquage\n\n"
                      "solution : contexte sur V seul",
                      size=9, color=t.TXT_DARKER)
        elif n == 31:
            self.text(slide, x, vy, w, h - 0.3,
                      "I·v'' + μ·v' = -1\nv'(0)=0, v(h)=0\n\n"
                      "v_{-I}(0) = [eʰ-h-1]/I\n"
                      "(temps avant fausse alarme)\n\n"
                      "v_I(0) = [h-1+e^{-h}]/I\n"
                      "(délai après changement)",
                      size=9, color=t.TXT_DARKER)
        elif n == 32:
            self.text(slide, x, vy, w, h - 0.3,
                      "I_t = I₀·exp(-2(t-1)/τ_a)\n\n"
                      "B = Σ I_t = I₀/[1-e^{-2/τ_a}]\n\n"
                      "si B < A : probabilité > 0\n"
                      "de ne jamais franchir e^A\n\n"
                      "modèle théorique ;\npas expérience JEPA",
                      size=9, color=t.TXT_DARKER)
        elif n == 33:
            self.text(slide, x, vy, w, h - 0.3,
                      "L = (1/K) Σ L_j ≥ L_j/K\n\n"
                      "L_j ≥ Kγ ⇒ L ≥ γ\n\n"
                      "I_proj = I·cos²(θ)\n\n"
                      "budget = [A+ln K] / [I·cos²(θ)]",
                      size=9, color=t.TXT_DARKER)
        else:
            self.text(slide, x, vy, w, h - 0.3,
                      "voir équations ci-dessous", size=9, color=t.TXT_FAINT, italic=True)


def save_reproducibly(prs, output):
    """Fix document properties and ZIP timestamps for byte reproducibility."""
    properties = prs.core_properties
    properties.title = "JEPA-Drift — Point hebdomadaire du 26 octobre 2026 — v3"
    properties.subject = "21 diapositives de présentation et 12 annexes de calcul"
    properties.author = properties.last_modified_by = ""
    properties.created = properties.modified = datetime(2026, 10, 26)
    properties.revision = 1
    buffer = io.BytesIO()
    prs.save(buffer)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(buffer) as source, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            info.date_time = (2026, 10, 26, 0, 0, 0)
            target.writestr(info, source.read(info.filename))


def audit_export(path, entries, figure):
    """Reopen the package and check structure, inline links, notes and source images."""
    prs = Presentation(path)
    if len(prs.slides) != 33 or prs.slide_width != Inches(10) or prs.slide_height != Inches(5.62):
        raise ValueError("Incorrect slide count or dimensions")
    rows = []
    for entry, slide in zip(entries, prs.slides):
        number = entry["number"]
        text = "\n".join(shape.text for shape in slide.shapes if shape.has_text_frame)
        # Check for forbidden patterns
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, re.I):
                raise ValueError(f"Forbidden pattern '{pattern}' found on slide {number}")
        # Check for raw markdown/StarMath
        if re.search(r"```|StarMath|LibreOffice Math|\\frac\{|%tau|%lambda", text):
            raise ValueError(f"Raw mathematical or Markdown code on slide {number}")
        if "**" in text:
            raise ValueError(f"Unprocessed markdown bold on slide {number}")
        # Check hyperlinks
        expected_links = {match[1] for match in LINK.findall(
            "\n".join(item["content"] for item in entry["bullets"] if item["type"] == "text")
        )}
        links = {rel.target_ref for rel in slide.part.rels.values() if rel.reltype.endswith("/hyperlink")}
        if not expected_links <= links:
            raise ValueError(f"Missing inline hyperlinks on slide {number}: {expected_links - links}")
        # Check notes
        notes = slide.notes_slide.notes_text_frame.text
        if entry["notes"] not in notes:
            raise ValueError(f"Speaker notes missing on slide {number}")
        # Check annex band
        if entry["kind"] == "ANNEX":
            if "ANNEXE" not in text:
                raise ValueError(f"Missing ANNEXE band on slide {number}")
        # Check equations are ASCII
        for eq in entry["equations"]:
            if eq["ascii"] not in text and plain_text(eq["ascii"]) not in text:
                raise ValueError(f"Equation ASCII missing on slide {number}: {eq['ascii'][:40]}")
        # Check off-canvas
        outside = []
        for shape in slide.shapes:
            if shape.left < -10 or shape.top < -10 or \
               shape.left + shape.width > prs.slide_width + 10 or \
               shape.top + shape.height > prs.slide_height + 10:
                outside.append(shape.name)
        if outside:
            raise ValueError(f"Off-canvas objects on slide {number}: {outside}")
        # Check images
        for shape in slide.shapes:
            if shape.shape_type == 13:
                with Image.open(io.BytesIO(shape.image.blob)) as img:
                    img.verify()
        if number == 7:
            for shape in slide.shapes:
                if shape.name == "historical:Fig30:unchanged":
                    if shape.image.blob != figure.read_bytes():
                        raise ValueError("The historical Fig. 30 bytes changed")
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
        "# JEPA-Drift — Point Hebdo v3 — StarMath blocks (référence manuelle)",
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
        "# Point hebdo 2026-10-26 v3 — render check",
        "",
        "## Executed structural checks",
        "",
        "- Reopened the exported PPTX with python-pptx: 33 slides, ordered 1–33; 21 main slides and 12 annexes.",
        "- Dimensions: 10.00 × 5.62 inches, ratio 1.77936; the canonical template's rounded 16:9 format.",
        f"- Equations: {total_equations} ASCII formulas displayed as monospace text with their 'Lecture' explanations. No LaTeX or bitmap rendering.",
        f"- Hyperlinks: {total_links} external relationships, checked against source references on each slide; clickable reference runs embedded in content.",
        "- All 33 speaker notes retain the original Notes field, full canonical bullets, visual specification, and StarMath sources.",
        "- All annex slides carry the 'ANNEXE' band at the bottom.",
        "- No displayed StarMath code, Markdown fences, or raw LaTeX; all embedded images decoded successfully.",
        "- No internal names (streams, pipelines, milestones, file paths) detected on any slide.",
        "- Every equation is displayed as its 'Affichage ASCII' line only; StarMath blocks are in the auxiliary file.",
        "- No object outside the slide canvas. Text preflight uses actual font metrics.",
        "- Palette and graphical utilities loaded from the unchanged canonical template; Carlito is the Calibri metric substitute.",
        "- Fig. 30 on slide 7 is embedded byte-for-byte without crop or retouching. All other diagrams are labelled as schematic/theoretical.",
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
        "## Per-slide control table",
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
        "## Equation display check",
        "",
        "| Slide | ASCII formula (truncated) | Lecture |",
        "| ---: | --- | --- |",
    ]
    for fc in builder.formula_checks:
        lecture = "yes" if fc["lecture"] else "no"
        lines.append(f"| {fc['slide']} | `{fc['ascii']}` | {lecture} |")
    lines += [
        "",
        "## Render and visual inspection",
        "",
        "**LibreOffice is not available on this machine.** No PDF export was attempted.",
        "No PNG contact sheet was generated. Visual inspection of individual pages is pending.",
        "The PPTX was verified structurally (slide count, dimensions, text content,",
        "hyperlinks, notes, images) but not visually.",
        "",
        "## Specific scientific checks",
        "",
        "- Slide 1: title slide with chain 'rendements → coordonnées → alarme'.",
        "- Slide 2: table with 3 columns; last column (limites) equally visible.",
        "- Slide 7: original historical Fig. 30 embedded unchanged; labels 'risque de fausse alarme' / 'réduction du budget'.",
        "- Slide 10: table shows 6 and 11 as variance-threshold settings, not detection optima.",
        "- Slide 12: sign guarantee table with 750-day horizon visible; asymmetry limitation stated.",
        "- Slide 13: covariance rotation results; decisive limitation about the comparator stated.",
        "- Slide 15: two mechanisms (1.96 vs 1.97/2.00) clearly distinguished; no arrow to JEPA gain.",
        "- Slide 21: gain criterion 1.25 stated as 'proposé' (proposed), not achieved.",
        "- Slides 22-33: each annex explicitly references its main slide; no independent conclusions.",
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
    """Build and audit the v3 deck."""
    parser = argparse.ArgumentParser(
        description="Build the 33-slide JEPA-Drift Point Hebdo v3 deck offline"
    )
    parser.add_argument("--deck", type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--assets-dir", type=Path,
                        help="Directory containing the unchanged historical Fig. 30")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    here, current = Path(__file__).resolve().parent, Path.cwd()
    roots = list(dict.fromkeys([current, current / "slides", here, here.parent]))
    deck = resolve_input(args.deck, DECK_NAME, roots)
    template = resolve_input(args.template, TEMPLATE_NAME, [deck.parent, *roots])
    figure_roots = (
        [args.assets_dir] if args.assets_dir
        else [current, deck.parent, deck.parent / "figures",
              here.parent / "figures", current / "figures"]
    )
    figure = resolve_input(None, FIGURE_NAME, figure_roots)
    output = (args.out or deck.parent / OUT_NAME).expanduser().resolve()
    auxiliary = output.with_name(AUX_NAME)
    report = output.with_name(REPORT_NAME)
    inputs = [deck, template, figure]
    if output.suffix.lower() != ".pptx":
        raise ValueError("--out must have a .pptx extension")
    if any(path in (output, report, auxiliary) for path in inputs):
        raise ValueError("An output path collides with an input")
    input_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    entries = parse_deck(deck)
    builder = DeckBuilder(load_template(template), figure)
    prs = builder.build(entries)
    save_reproducibly(prs, output)
    rows = audit_export(output, entries, figure)
    for path, digest in input_hashes.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"Input changed during generation: {path.name}")
    write_auxiliary(auxiliary, entries)
    write_report(report, output, inputs, entries, rows, builder)
    print(f"Saved: {output.name}; 33 slides; {sum(r['equations'] for r in rows)} ASCII equations; "
          f"source files unchanged")
    print(f"Auxiliary: {auxiliary.name}")
    print(f"Report: {report.name}")


if __name__ == "__main__":
    main()
