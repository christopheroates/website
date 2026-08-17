#!/usr/bin/env python3
"""
render_pdf.py — render cv.html to cv.pdf using headless Chrome (via
Playwright), with a running header/footer (name + page numbers) that
CSS @page rules alone can't produce reliably in Chromium's print engine.

Usage:
    python3 build_cv.py      # regenerate cv.html from the site pages
    python3 render_pdf.py    # render cv.html -> cv.pdf

Requires: pip install -r requirements.txt, then
          python -m playwright install chromium
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

SITE_DIR = Path(__file__).parent
HTML_FILE = SITE_DIR / "cv.html"
PDF_FILE = SITE_DIR / "cv.pdf"

HEADER_TEMPLATE = """
<div style="font-size:8px; width:100%; padding:0 16mm; color:#888; font-family:Georgia,serif;">
</div>
"""

FOOTER_TEMPLATE = """
<div style="font-size:8px; width:100%; padding:0 16mm; color:#888; font-family:Georgia,serif;
            display:flex; justify-content:space-between;">
  <span>Chris J. Oates — Curriculum Vitae</span>
  <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>
"""


def render():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(HTML_FILE.as_uri())
        page.pdf(
            path=str(PDF_FILE),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template=HEADER_TEMPLATE,
            footer_template=FOOTER_TEMPLATE,
            margin={"top": "20mm", "bottom": "18mm", "left": "16mm", "right": "16mm"},
        )
        browser.close()
    print(f"Wrote {PDF_FILE}")


if __name__ == "__main__":
    render()
