#!/usr/bin/env python3
"""
build_cv.py — assemble cv.html (and, via render_pdf.py, cv.pdf) from the
existing, hand-edited site pages.

REQUIREMENTS
------------
pip install -r requirements.txt   (just beautifulsoup4 + playwright)
"""

import re
from pathlib import Path

from bs4 import BeautifulSoup

SITE_DIR = Path(__file__).parent
OUT_FILE = SITE_DIR / "cv.html"

# ----------------------------------------------------------------------
# The one bit of content that isn't scraped from a page — edit by hand
# if it ever changes (name, tagline, contact details).
# ----------------------------------------------------------------------
HEADER = {
    "name": "Chris J. Oates",
    "tagline": "Researcher in statistics, computation, machine learning, and probabilistic AI.",
    "location": (
        "School of Mathematics, Statistics &amp; Physics, Herschel Building, "
        "Newcastle University, NE1 7RU, UK."
    ),
    "web": "https://oates.work",
    "contact": "chris.oates@ncl.ac.uk",
}

# ----------------------------------------------------------------------
# Which sections go into the CV, in order, and where each one comes from.
# "source" is the existing site page; "heading" is the exact <h2> text on
# that page; "title" is the heading to use in the CV (often the same).
# heading == "__ALL__" means: pull every <h2>Year</h2> block on that page,
# in document order (used for papers.html / teaching.html / presentations.html,
# which are just a run of year sections).
# ----------------------------------------------------------------------
# Pages that carry their own "shared icon sprite" (<svg style="display:none">
# containing <symbol id="icon-...">) near the top of <body>, used by the
# small pill-shaped .link-badge buttons (Web / arXiv / Video / etc.). Each
# <use href="#icon-x"/> only resolves against symbols defined in the SAME
# document, so cv.html needs its own merged copy of every symbol used by
# any section it pulls in - see collect_icon_sprite() below.
ICON_SPRITE_PAGES = ["professional.html", "papers.html", "presentations.html", "teaching.html"]

SECTIONS = [
    {"title": "Background", "source": "professional.html", "heading": "Affiliations"},
    {"title": "Achievements", "source": "professional.html", "heading": "Achievements"},
    {"title": "Research Funding", "source": "professional.html", "heading": "Funding"},
    {"title": "Publications", "source": "papers.html", "heading": "__ALL__"},
    {"title": "Supervision — Current Group Members", "source": "index.html", "heading": "Current Group Members"},
    {"title": "Supervision — Former Group Members", "source": "index.html", "heading": "Former Group Members"},
    {"title": "PhD Theses Examined / PhD Defence Committee Member", "source": "professional.html",
     "heading": "PhD Theses Examined / PhD Defence Committee Member"},
    {"title": "Editorial", "source": "professional.html", "heading": "Editorial"},
    {"title": "Committees and Working Groups", "source": "professional.html", "heading": "Committees and Working Groups"},
    {"title": "External Assessor / Interview Panel", "source": "professional.html", "heading": "External Assessor / Interview Panel"},
    {"title": "Reviewing Service", "source": "professional.html", "heading": "Reviewing Service"},
    {"title": "Grant Reviewing Service", "source": "professional.html", "heading": "Grant Reviewing Service"},
    {"title": "Teaching", "source": "teaching.html", "heading": "__ALL__"},
    {"title": "Organised Conferences & Workshops", "source": "professional.html", "heading": "Organised Conferences & Workshops"},
    {"title": "Invited Presentations", "source": "presentations.html", "heading": "__ALL__"},
    {"title": "Media and Engagement", "source": "professional.html", "heading": "Media and Engagement"},
]


def load(name):
    path = SITE_DIR / name
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


_CACHE = {}


def soup_for(name):
    if name not in _CACHE:
        _CACHE[name] = load(name)
    return _CACHE[name]


def find_section(soup, heading_text):
    """Return the list of sibling tags between an <h2> whose text matches
    heading_text and the next <h2> (or end of the containing div)."""
    for h2 in soup.find_all("h2"):
        if h2.get_text(strip=True) == heading_text:
            collected = []
            for sib in h2.find_next_siblings():
                if sib.name == "h2":
                    break
                if sib.name == "footer":
                    break
                collected.append(sib)
            return collected
    return None


def all_year_sections(soup):
    """For pages like papers.html / teaching.html / presentations.html
    that are just a run of <h2>Year</h2> + <ul> blocks with no other
    structure, return them all in document order, each wrapped with its
    own heading."""
    out = []
    for h2 in soup.find_all("h2"):
        body = []
        for sib in h2.find_next_siblings():
            if sib.name == "h2":
                break
            if sib.name == "footer":
                break
            body.append(sib)
        out.append((h2.get_text(strip=True), body))
    return out


def collect_icon_sprite():
    """Merge every <symbol id="icon-..."> from the icon-sprite pages into
    one deduplicated dict (id -> symbol tag), so cv.html can carry a single
    combined sprite and every .link-badge icon it pulled in still renders."""
    symbols = {}
    for name in ICON_SPRITE_PAGES:
        soup = soup_for(name)
        svg = soup.find("svg", style=lambda v: v and "display:none" in v)
        if not svg:
            continue
        for symbol in svg.find_all("symbol"):
            sid = symbol.get("id")
            if sid and sid not in symbols:
                symbols[sid] = symbol.__copy__()
    return symbols


def build():
    out = BeautifulSoup("<!DOCTYPE html><html lang=\"en\"></html>", "html.parser")
    html = out.html

    head = out.new_tag("head")
    meta1 = out.new_tag("meta", charset="UTF-8")
    title = out.new_tag("title")
    title.string = f"{HEADER['name']} — CV"
    link_site_css = out.new_tag("link", rel="stylesheet", href="style.css")
    link_print_css = out.new_tag("link", rel="stylesheet", href="cv-print.css")
    for el in (meta1, title, link_site_css, link_print_css):
        head.append(el)
    html.append(head)

    body = out.new_tag("body")
    body["class"] = "cv-page"
    html.append(body)

    # ---- header ----
    header = out.new_tag("header", **{"class": "cv-header"})
    h1 = out.new_tag("h1")
    h1.string = HEADER["name"]
    header.append(h1)

    tagline = out.new_tag("p", **{"class": "cv-tagline"})
    tagline.string = HEADER["tagline"]
    header.append(tagline)

    meta = out.new_tag("p", **{"class": "cv-meta"})
    meta.append(BeautifulSoup(
        f"<em>Location:</em> {HEADER['location']}<br>"
        f"<em>Web:</em> <a href=\"{HEADER['web']}\">{HEADER['web']}</a><br>"
        f"<em>Contact:</em> <a href=\"mailto:{HEADER['contact']}\">{HEADER['contact']}</a>",
        "html.parser",
    ))
    header.append(meta)
    body.append(header)

    # ---- sections ----
    for sec in SECTIONS:
        src_soup = soup_for(sec["source"])
        if sec["heading"] == "__ALL__":
            wrapper = out.new_tag("section", **{"class": "cv-section"})
            h2 = out.new_tag("h2")
            h2.string = sec["title"]
            wrapper.append(h2)
            for sub_heading, sub_body in all_year_sections(src_soup):
                h3 = out.new_tag("h3")
                h3.string = sub_heading
                wrapper.append(h3)
                for el in sub_body:
                    wrapper.append(el.__copy__())
            body.append(wrapper)
        else:
            elements = find_section(src_soup, sec["heading"])
            if elements is None:
                print(f"WARNING: heading '{sec['heading']}' not found in {sec['source']}; skipping")
                continue
            wrapper = out.new_tag("section", **{"class": "cv-section"})
            h2 = out.new_tag("h2")
            h2.string = sec["title"]
            wrapper.append(h2)
            for el in elements:
                wrapper.append(el.__copy__())
            body.append(wrapper)

    # ---- note (only shown on-screen; hidden when printing) ----
    footer_note = out.new_tag("p", **{"class": "cv-noprint cv-generated-note"})
    footer_note.string = (
        "This page is generated automatically from oates.work — see "
        "professional.html, papers.html, teaching.html, presentations.html "
        "and index.html for the underlying, hand-edited content."
    )
    body.insert(1, footer_note)

    # ---- combined icon sprite for the .link-badge buttons pulled in above
    # (must exist in THIS document for their <use href="#icon-x"/> to
    # resolve - see collect_icon_sprite()). Inserted last so it always ends
    # up first in the body regardless of the inserts above. ----
    icons = collect_icon_sprite()
    if icons:
        sprite = out.new_tag("svg", style="display:none", **{"aria-hidden": "true"})
        for symbol in icons.values():
            sprite.append(symbol)
        body.insert(0, sprite)

    OUT_FILE.write_text(str(out), encoding="utf-8")
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    build()
