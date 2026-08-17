# Auto-generated CV (cv.pdf)

This adds a "Download CV (PDF)" link to the site that always reflects
whatever is currently on `professional.html`, `papers.html`,
`teaching.html`, `presentations.html` and `index.html` — no separate
LaTeX file to keep in sync by hand.

## How it works

1. You keep editing the site exactly as before — same files, same
   plain-text workflow described in the main `README.md`. Nothing about
   day-to-day editing changes.
2. `build_cv.py` reads those pages, pulls out the CV-relevant sections
   (affiliations, achievements, funding, publications, supervision,
   editorial roles, committees, teaching, talks, media), and assembles
   them — in the order the old `CV.tex` used — into one new page,
   `cv.html`, styled with `cv-print.css` to look like a dense academic
   CV rather than the website's normal layout.
3. `render_pdf.py` opens `cv.html` in headless Chrome and prints it to
   `cv.pdf`, with a running footer (name + page numbers).
4. `.github/workflows/build-cv.yml` runs both scripts automatically,
   via GitHub Actions, every time you push a change to any of the
   pages listed above, and commits the refreshed `cv.html`/`cv.pdf`
   back into the repository. You never have to run anything yourself.

The button on the site just needs to link straight to the file:

```html
<p><a href="cv.pdf">Download CV (PDF)</a></p>
```

A ready-to-paste version of this is in `index-snippet.html` in this
delivery — see the comment there for exactly where to put it.

## One-time setup

This needs the repository to be hosted on GitHub with Actions enabled
(GitHub Pages, or Netlify/Cloudflare linked to the same GitHub repo —
either is fine, since Actions runs independently of where the site is
served from). If the site is currently only published via Netlify
Drop (dragging the folder onto netlify.com/drop, as described in the
main README's "Option A"), this won't run, because there's no
repository for Actions to attach to. **Option B in the main README
(GitHub Pages) needs to be followed first**, or the existing repo
needs to be connected to Netlify's git-based deploys instead of Drop.

Once the repo is on GitHub:

1. Copy these files into the repository, alongside the existing
   `index.html`, `professional.html`, etc.:
   - `build_cv.py`
   - `render_pdf.py`
   - `cv-print.css`
   - `requirements.txt`
   - `.github/workflows/build-cv.yml` (keep this exact folder path —
     GitHub only looks for workflows in `.github/workflows/`)
2. Add the download link from `index-snippet.html` to `index.html`
   (and anywhere else a link would be useful, e.g. `professional.html`).
3. Commit and push. Check the "Actions" tab of the repository on
   GitHub — you should see a "Build CV PDF" run start automatically.
   When it finishes (a minute or two), `cv.html` and `cv.pdf` will
   appear in the repo, and the download link on the live site will
   start working after the next deploy.
4. From then on: edit the site pages as usual, push, and the PDF
   updates itself within a couple of minutes. No further action needed.

## Testing it locally (optional)

If Python is installed:

```bash
pip install -r requirements.txt
python -m playwright install chromium
python3 build_cv.py
python3 render_pdf.py
```

This writes `cv.html` and `cv.pdf` right there in the folder, so you
can check the result before pushing.

## Adjusting what's on the CV

- **Wrong or outdated content in a section** — edit the source page as
  normal (`professional.html`, `papers.html`, etc.). `build_cv.py`
  doesn't need touching.
- **Add, remove, or reorder a whole section** — edit the `SECTIONS`
  list near the top of `build_cv.py`. Each entry says which page and
  which `<h2>` heading to pull from.
- **Name, tagline, address, contact details at the top of the CV** —
  edit the `HEADER` dict near the top of `build_cv.py`. This is the
  one piece of content that isn't pulled automatically from a page,
  since it doesn't live in a tidy bullet list anywhere on the site.
- **Look and feel of the PDF** (fonts, spacing, margins, page size) —
  edit `cv-print.css`.

## A one-time reconciliation worth doing first

The old `CV.tex` and the current website have already drifted apart in
a few places (a 2025 "REF Unit of Assessment Lead" entry and a couple
of funding-figure corrections exist on the site but not in the old
LaTeX file). Since the website is about to become the single source of
truth, it's worth a quick read-through of `professional.html` before
switching this on, to confirm everything on it is exactly as wanted —
after that, `cv.pdf` will always match it automatically.
