"""Minimal PDF writer + remediation report template.

Pure stdlib. Generates a clean A4 multi-page report with header bar,
severity KPI strip and per-vulnerability cards (severity stripe, CVSS chip,
description, correctif). Auto pagination, French-friendly via WinAnsi.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable


PAGE_W, PAGE_H = 595, 842
MARGIN_X = 48
MARGIN_TOP = 48
MARGIN_BOTTOM = 60
CONTENT_W = PAGE_W - 2 * MARGIN_X

PALETTE = {
    "critical": (0.624, 0.176, 0.176),
    "high":     (0.604, 0.357, 0.094),
    "medium":   (0.325, 0.420, 0.184),
    "low":      (0.298, 0.392, 0.478),
    "ink":      (0.094, 0.094, 0.094),
    "muted":    (0.502, 0.482, 0.439),
    "rule":     (0.835, 0.812, 0.769),
    "paper":    (0.992, 0.984, 0.965),
}

SEVERITY_LABEL = {"critical": "CRITIQUE", "high": "HAUTE", "medium": "MOYENNE", "low": "FAIBLE"}
STATUS_LABEL = {"ouverte": "Ouverte", "en_cours": "En cours", "a_verifier": "À vérifier", "corrigee": "Corrigée", "acceptee": "Acceptée"}

VERDICT_LABEL = {"validated": "CORRECTION VALIDÉE", "rejected": "CORRECTION NON VALIDÉE", "bypass": "BYPASS IDENTIFIÉ"}
VERDICT_COLOR = {"validated": PALETTE["medium"], "rejected": PALETTE["high"], "bypass": PALETTE["critical"]}
VERDICT_NEXT = {
    "validated": "La vulnérabilité est marquée corrigée. Aucune action supplémentaire requise.",
    "rejected": "La correction est insuffisante. La vulnérabilité repasse en cours côté client.",
    "bypass": "Un bypass de votre correctif a été identifié. La vulnérabilité est réouverte avec contexte ci-dessous.",
}

HELV_WIDTHS_BASE = {
    " ": 278, "!": 278, "\"": 355, "#": 556, "$": 556, "%": 889, "&": 667, "'": 191,
    "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278,
    "0": 556, "1": 556, "2": 556, "3": 556, "4": 556, "5": 556, "6": 556, "7": 556,
    "8": 556, "9": 556, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584, "?": 556,
    "@": 1015, "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778,
    "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944,
    "X": 667, "Y": 667, "Z": 611, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556,
    "`": 333, "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556,
    "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556, "o": 556,
    "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556, "v": 500, "w": 722,
    "x": 500, "y": 500, "z": 500, "{": 334, "|": 260, "}": 334, "~": 584,
}


def char_width(c: str, size: float, bold: bool) -> float:
    base = HELV_WIDTHS_BASE.get(c, 500)
    scale = 1.05 if bold else 1.0
    return base / 1000.0 * size * scale


def text_width(text: str, size: float, bold: bool = False) -> float:
    return sum(char_width(c, size, bold) for c in text)


def wrap_text(text: str, max_width: float, size: float, bold: bool = False) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines() or [""]:
        words = raw_line.split()
        if not words:
            lines.append("")
            continue
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if text_width(candidate, size, bold) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def _escape(text: str) -> bytes:
    encoded = text.encode("cp1252", "replace")
    return encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


class PDFBuilder:
    def __init__(self) -> None:
        self._streams: list[bytes] = []
        self._current: list[bytes] = []
        self._y_top = PAGE_H - MARGIN_TOP
        self.cursor_y = self._y_top
        self.page_no = 0
        self._start_page()

    def _start_page(self) -> None:
        if self._current:
            self._streams.append(b"\n".join(self._current))
        self._current = []
        self.page_no += 1
        self.cursor_y = self._y_top
        self._draw_header_band()

    def _draw_header_band(self) -> None:
        self.fill_rect(0, PAGE_H - 36, PAGE_W, 36, PALETTE["ink"])
        self.draw_text(MARGIN_X, PAGE_H - 23, "YOps Cybersecurity", size=11, bold=True, color=PALETTE["paper"])
        right = "RAPPORT · VULNÉRABILITÉS À CORRIGER"
        rx = PAGE_W - MARGIN_X - text_width(right, 9, bold=True)
        self.draw_text(rx, PAGE_H - 23, right, size=9, bold=True, color=PALETTE["paper"])
        self.cursor_y = PAGE_H - 36 - 28

    def _draw_footer(self) -> None:
        y = MARGIN_BOTTOM - 28
        self.fill_rect(MARGIN_X, y + 18, CONTENT_W, 0.5, PALETTE["rule"])
        self.draw_text(MARGIN_X, y, "YOps Portal · Document interne", size=8, color=PALETTE["muted"])
        right = f"Page {self.page_no}"
        rx = PAGE_W - MARGIN_X - text_width(right, 8)
        self.draw_text(rx, y, right, size=8, color=PALETTE["muted"])

    def ensure_space(self, needed: float) -> None:
        if self.cursor_y - needed < MARGIN_BOTTOM:
            self._draw_footer()
            self._start_page()

    def fill_rect(self, x: float, y: float, w: float, h: float, color: tuple[float, float, float]) -> None:
        r, g, b = color
        self._current.append(f"{r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f".encode("ascii"))

    def draw_text(self, x: float, y: float, text: str, size: float = 10, bold: bool = False, color: tuple[float, float, float] = (0, 0, 0)) -> None:
        font = "F2" if bold else "F1"
        r, g, b = color
        body = b"BT %b %b Tf %b %b Td %b rg (%b) Tj ET" % (
            f"/{font}".encode("ascii"),
            f"{size:.2f}".encode("ascii"),
            f"{x:.2f}".encode("ascii"),
            f"{y:.2f}".encode("ascii"),
            f"{r:.3f} {g:.3f} {b:.3f}".encode("ascii"),
            _escape(text),
        )
        self._current.append(body)

    def chip(self, x: float, y_baseline: float, label: str, color: tuple[float, float, float], text_color: tuple[float, float, float] = (1, 1, 1), size: float = 8) -> float:
        pad_x, pad_y = 6, 3
        tw = text_width(label, size, bold=True)
        w = tw + pad_x * 2
        h = size + pad_y * 2
        self.fill_rect(x, y_baseline - pad_y, w, h, color)
        self.draw_text(x + pad_x, y_baseline + 1, label, size=size, bold=True, color=text_color)
        return w

    def rule(self, y: float, color: tuple[float, float, float] = None) -> None:
        self.fill_rect(MARGIN_X, y, CONTENT_W, 0.5, color or PALETTE["rule"])

    def build(self) -> bytes:
        self._draw_footer()
        self._streams.append(b"\n".join(self._current))
        return _assemble_pdf(self._streams)


def _assemble_pdf(streams: list[bytes]) -> bytes:
    objects: list[bytes] = []

    def add(obj_bytes: bytes) -> int:
        objects.append(obj_bytes)
        return len(objects)

    n_pages = len(streams)
    catalog_id = 1
    pages_id = 2
    font_regular_id = 3
    font_bold_id = 4

    placeholders = [b"", b"", b"", b""]
    objects.extend(placeholders)

    page_ids: list[int] = []
    content_ids: list[int] = []
    for stream in streams:
        content = b"<< /Length %d >>\nstream\n%b\nendstream" % (len(stream), stream)
        cid = add(content)
        content_ids.append(cid)
        page_body = (
            b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %d %d] "
            b"/Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> "
            b"/Contents %d 0 R >>"
        ) % (pages_id, PAGE_W, PAGE_H, font_regular_id, font_bold_id, cid)
        page_ids.append(add(page_body))

    objects[catalog_id - 1] = b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id
    kids = b" ".join(b"%d 0 R" % pid for pid in page_ids)
    objects[pages_id - 1] = b"<< /Type /Pages /Kids [%b] /Count %d >>" % (kids, n_pages)
    objects[font_regular_id - 1] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    objects[font_bold_id - 1] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: list[int] = []
    for idx, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%b\nendobj\n" % (idx, body)
    xref_offset = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1, catalog_id, xref_offset,
    )
    return bytes(out)


def _line_height(size: float) -> float:
    return size * 1.32


def build_remediation_report(vulnerabilities: Iterable, generated_by: str, scope: str | None = None) -> bytes:
    vulns = list(vulnerabilities)
    pdf = PDFBuilder()

    title = f"Rapport de remédiation — {scope}" if scope else "Vulnérabilités à corriger"
    for line in wrap_text(title, CONTENT_W, size=22, bold=True):
        pdf.draw_text(MARGIN_X, pdf.cursor_y, line, size=22, bold=True, color=PALETTE["ink"])
        pdf.cursor_y -= 26
    pdf.cursor_y -= 2
    subtitle = f"Généré le {date.today().strftime('%d/%m/%Y')} · par {generated_by} · {len(vulns)} entrée{'s' if len(vulns) > 1 else ''}"
    pdf.draw_text(MARGIN_X, pdf.cursor_y, subtitle, size=10, color=PALETTE["muted"])
    pdf.cursor_y -= 24

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in vulns:
        counts[v.severity] = counts.get(v.severity, 0) + 1

    kpi_w = (CONTENT_W - 18) / 4
    kpi_h = 56
    for i, key in enumerate(("critical", "high", "medium", "low")):
        x = MARGIN_X + i * (kpi_w + 6)
        y = pdf.cursor_y - kpi_h
        pdf.fill_rect(x, y, kpi_w, kpi_h, PALETTE["paper"])
        pdf.fill_rect(x, y, 3, kpi_h, PALETTE[key])
        pdf.draw_text(x + 14, y + kpi_h - 18, SEVERITY_LABEL[key], size=8, bold=True, color=PALETTE["muted"])
        pdf.draw_text(x + 14, y + 14, str(counts[key]), size=22, bold=True, color=PALETTE[key])
    pdf.cursor_y -= kpi_h + 24

    pdf.draw_text(MARGIN_X, pdf.cursor_y, "Détail des vulnérabilités à corriger", size=12, bold=True, color=PALETTE["ink"])
    pdf.cursor_y -= 6
    pdf.rule(pdf.cursor_y)
    pdf.cursor_y -= 18

    if not vulns:
        pdf.draw_text(MARGIN_X, pdf.cursor_y, "Aucune vulnérabilité ouverte. Bon travail.", size=10, color=PALETTE["muted"])
        return pdf.build()

    for vuln in vulns:
        _draw_vuln_card(pdf, vuln)

    return pdf.build()


def build_verification_report(vuln, verdict: str, admin_message: str, admin_name: str, client_name: str, summary: dict | None = None) -> bytes:
    pdf = PDFBuilder()
    pdf.draw_text(MARGIN_X, pdf.cursor_y, "Vérification de correction", size=22, bold=True, color=PALETTE["ink"])
    pdf.cursor_y -= 26
    subtitle = f"{client_name} · le {date.today().strftime('%d/%m/%Y')} · par {admin_name}"
    pdf.draw_text(MARGIN_X, pdf.cursor_y, subtitle, size=10, color=PALETTE["muted"])
    pdf.cursor_y -= 26

    verdict_color = VERDICT_COLOR.get(verdict, PALETTE["muted"])
    verdict_label = VERDICT_LABEL.get(verdict, verdict.upper())
    block_h = 56
    pdf.fill_rect(MARGIN_X, pdf.cursor_y - block_h, CONTENT_W, block_h, verdict_color)
    pdf.draw_text(MARGIN_X + 18, pdf.cursor_y - 22, "VERDICT YOPS", size=9, bold=True, color=PALETTE["paper"])
    pdf.draw_text(MARGIN_X + 18, pdf.cursor_y - 44, verdict_label, size=18, bold=True, color=PALETTE["paper"])
    pdf.cursor_y -= block_h + 22

    pdf.draw_text(MARGIN_X, pdf.cursor_y, "Vulnérabilité concernée", size=11, bold=True, color=PALETTE["ink"])
    pdf.cursor_y -= 6
    pdf.rule(pdf.cursor_y)
    pdf.cursor_y -= 18
    _draw_vuln_card(pdf, vuln)

    pdf.ensure_space(120)
    pdf.draw_text(MARGIN_X, pdf.cursor_y, "Décision et message de l'analyste", size=11, bold=True, color=PALETTE["ink"])
    pdf.cursor_y -= 6
    pdf.rule(pdf.cursor_y)
    pdf.cursor_y -= 18

    message = admin_message.strip() or "Aucun message complémentaire."
    for line in wrap_text(message, CONTENT_W - 12, size=10):
        pdf.draw_text(MARGIN_X + 12, pdf.cursor_y, line, size=10, color=PALETTE["ink"])
        pdf.cursor_y -= _line_height(10)
    pdf.cursor_y -= 8

    next_step = VERDICT_NEXT.get(verdict, "")
    pdf.draw_text(MARGIN_X, pdf.cursor_y, "Étapes suivantes", size=11, bold=True, color=PALETTE["ink"])
    pdf.cursor_y -= 6
    pdf.rule(pdf.cursor_y)
    pdf.cursor_y -= 18
    for line in wrap_text(next_step, CONTENT_W - 12, size=10):
        pdf.draw_text(MARGIN_X + 12, pdf.cursor_y, line, size=10, color=PALETTE["ink"])
        pdf.cursor_y -= _line_height(10)
    pdf.cursor_y -= 8

    if summary:
        pdf.ensure_space(70)
        pdf.draw_text(MARGIN_X, pdf.cursor_y, "Récapitulatif du portefeuille de vulnérabilités", size=11, bold=True, color=PALETTE["ink"])
        pdf.cursor_y -= 6
        pdf.rule(pdf.cursor_y)
        pdf.cursor_y -= 18
        kpi_w = (CONTENT_W - 18) / 4
        kpi_h = 50
        for i, key in enumerate(("ouverte", "en_cours", "a_verifier", "corrigee")):
            x = MARGIN_X + i * (kpi_w + 6)
            y = pdf.cursor_y - kpi_h
            pdf.fill_rect(x, y, kpi_w, kpi_h, PALETTE["paper"])
            pdf.fill_rect(x, y, 3, kpi_h, PALETTE["ink"])
            pdf.draw_text(x + 14, y + kpi_h - 16, STATUS_LABEL.get(key, key).upper(), size=8, bold=True, color=PALETTE["muted"])
            pdf.draw_text(x + 14, y + 12, str(summary.get(key, 0)), size=20, bold=True, color=PALETTE["ink"])
        pdf.cursor_y -= kpi_h + 12

    return pdf.build()


def _draw_vuln_card(pdf: PDFBuilder, vuln) -> None:
    severity_color = PALETTE.get(vuln.severity, PALETTE["muted"])
    text_w = CONTENT_W - 18

    title_lines = wrap_text(vuln.title, text_w, size=12, bold=True)
    meta = f"{vuln.client_name} · {vuln.audit_title} · Actif : {vuln.asset}"
    meta_lines = wrap_text(meta, text_w, size=9)
    desc_lines = wrap_text(vuln.description, text_w, size=10)
    fix_lines = wrap_text(vuln.recommendation, text_w, size=10)

    header_h = 34
    body_h = (
        len(title_lines) * _line_height(12)
        + len(meta_lines) * _line_height(9)
        + 14 + len(desc_lines) * _line_height(10)
        + 14 + len(fix_lines) * _line_height(10)
        + 24
    )
    needed = header_h + body_h + 12
    pdf.ensure_space(needed)

    card_top = pdf.cursor_y
    card_bottom = card_top - needed + 8
    pdf.fill_rect(MARGIN_X, card_bottom, 3, card_top - card_bottom, severity_color)

    chip_baseline = card_top - 15
    x = MARGIN_X + 12
    used = pdf.chip(x, chip_baseline, SEVERITY_LABEL[vuln.severity], severity_color, text_color=(1, 1, 1))
    x += used + 6
    used = pdf.chip(x, chip_baseline, f"CVSS {float(vuln.cvss_score):.1f}", PALETTE["ink"], text_color=PALETTE["paper"])
    x += used + 6
    pdf.chip(x, chip_baseline, STATUS_LABEL.get(vuln.status, vuln.status), PALETTE["paper"], text_color=PALETTE["ink"])

    y = card_top - header_h
    for line in title_lines:
        pdf.draw_text(MARGIN_X + 12, y, line, size=12, bold=True, color=PALETTE["ink"])
        y -= _line_height(12)

    for line in meta_lines:
        pdf.draw_text(MARGIN_X + 12, y, line, size=9, color=PALETTE["muted"])
        y -= _line_height(9)

    y -= 6
    pdf.draw_text(MARGIN_X + 12, y, "Description", size=8, bold=True, color=PALETTE["muted"])
    y -= _line_height(9)
    for line in desc_lines:
        pdf.draw_text(MARGIN_X + 12, y, line, size=10, color=PALETTE["ink"])
        y -= _line_height(10)

    y -= 6
    pdf.draw_text(MARGIN_X + 12, y, "Correctif recommandé", size=8, bold=True, color=PALETTE["muted"])
    y -= _line_height(9)
    for line in fix_lines:
        pdf.draw_text(MARGIN_X + 12, y, line, size=10, color=PALETTE["ink"])
        y -= _line_height(10)

    pdf.cursor_y = y - 12
    pdf.rule(pdf.cursor_y + 4)
    pdf.cursor_y -= 8
