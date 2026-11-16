"""SEO hook: index only finished chapters, and give every page a real description.

A page is "unfinished" when its nav title carries "(planned)", the same label
readers see. Unfinished pages get <meta name="robots" content="noindex"> and are
dropped from sitemap.xml; removing the label when a chapter ships indexes it.

Descriptions come from the italic gloss line under each H1 (or the first
paragraph when there is none), so chapters never carry SEO front matter, which
GitHub's file view would render as a table.
"""

import gzip
import re
from pathlib import Path

PLANNED = "(planned)"
MAX_DESC = 160

_planned: set[str] = set()


def _walk(nav):
    """Yield planned pages. A section's untitled index page counts as planned
    when every titled page in that section is planned (a part with nothing shipped)."""
    indexes, titled, planned = [], [], []
    for item in nav or []:
        if isinstance(item, str):
            indexes.append(item)
        elif isinstance(item, dict):
            for title, value in item.items():
                if isinstance(value, list):
                    yield from _walk(value)
                else:
                    titled.append(str(value))
                    if PLANNED in str(title):
                        planned.append(str(value))
    yield from planned
    if titled and len(planned) == len(titled):
        yield from indexes


def on_config(config):
    _planned.clear()
    _planned.update(_walk(config["nav"]))
    return config


def _plain(text):
    text = re.sub(r"\[\^[^\]]+\]", "", text)                 # footnote refs
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)   # links/images
    text = re.sub(r"[*_`>]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _truncate(text):
    if len(text) <= MAX_DESC:
        return text
    cut = text[: MAX_DESC - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


def _description(markdown):
    body = markdown.split("\n# ", 1)[-1] if not markdown.startswith("# ") else markdown
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body)[1:]]
    for p in paragraphs:
        if p.startswith(("#", "<", "|", "```", "---")) or p.startswith("> **Stub"):
            continue
        text = _plain(p)
        if len(text) > 40:
            return _truncate(text)
    return None


def on_page_markdown(markdown, page, config, files):
    if page.file.src_uri in _planned:
        page.meta["robots"] = "noindex, follow"
    if "description" not in page.meta:
        desc = _description(markdown)
        if desc:
            page.meta["description"] = desc
    return markdown


def on_post_build(config):
    site = Path(config["site_dir"])
    sitemap = site / "sitemap.xml"
    if not sitemap.exists():
        return
    base = config["site_url"].rstrip("/") + "/"
    drop = {base + p[: -len(".md")] + "/" for p in _planned}
    drop |= {u.replace("/index/", "/") for u in drop}
    xml = sitemap.read_text(encoding="utf-8")
    xml = re.sub(
        r"\s*<url>\s*<loc>([^<]+)</loc>.*?</url>",
        lambda m: "" if m.group(1) in drop else m.group(0),
        xml,
        flags=re.S,
    )
    sitemap.write_text(xml, encoding="utf-8")
    with gzip.open(site / "sitemap.xml.gz", "wb") as gz:
        gz.write(xml.encode("utf-8"))
