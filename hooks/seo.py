"""SEO hook: index only finished chapters, and give every page a real description.

A page is "unfinished" when its nav title carries "(planned)", the same label
readers see. Unfinished pages get <meta name="robots" content="noindex"> and are
dropped from sitemap.xml; removing the label when a chapter ships indexes it.

Descriptions come from the italic gloss line under each H1 (or the first
paragraph when there is none), so chapters never carry SEO front matter, which
GitHub's file view would render as a table.

For search and answer engines it also derives, and never invents:
- created/updated dates from git history (shown at the page foot, used in
  JSON-LD and as sitemap <lastmod>); a shallow clone yields no dates, not wrong ones
- JSON-LD: WebSite, Person (site_author), Book, and per finished page a
  TechArticle, CollectionPage or WebPage with a BreadcrumbList from the nav
- /llms.txt (nav-ordered index of finished pages) and /llms-full.txt (their
  full markdown with relative links made absolute), per llmstxt.org
"""

import gzip
import html
import json
import posixpath
import re
import subprocess
from datetime import datetime
from pathlib import Path

PLANNED = "(planned)"
MAX_DESC = 160
AUTHOR_PAGE = "about/author.md"
# Person facts, each traceable to the author page or the author site. Edit them
# together with docs/about/author.md, never one without the other.
AUTHOR_SAME_AS = [
    "https://author.agentic-engineering.work/",
    "https://github.com/AbhiramDwivedi",
    "https://www.linkedin.com/in/ram-dwivedi/",
]
AUTHOR_JOB_TITLE = "Senior Architect"
AUTHOR_EMPLOYER = "Publicis Sapient"
AUTHOR_KNOWS_ABOUT = ["Platform architecture", "Distributed systems",
                      "Agentic AI systems", "AI platform engineering", "DevOps"]
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
SOCIAL_IMAGE = "images/social-card.png"

_planned: set[str] = set()
_pages: dict[str, dict] = {}   # src_uri -> title, url, description, markdown, dates
_nav = None
_git_ok = False


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


def _git(*args, cwd):
    try:
        out = subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                             text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def on_config(config):
    global _git_ok
    _planned.clear()
    _planned.update(_walk(config["nav"]))
    _pages.clear()
    root = Path(config["config_file_path"]).parent
    # a shallow clone would date every page to the latest commit: emit nothing instead
    _git_ok = _git("rev-parse", "--is-shallow-repository", cwd=root) == "false"
    return config


def on_nav(nav, config, files):
    global _nav
    _nav = nav
    return nav


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


def _dates(page):
    if not _git_ok or not page.file.abs_src_path:
        return None, None
    src = Path(page.file.abs_src_path)
    updated = _git("log", "-1", "--format=%cI", "--", src.name, cwd=src.parent)
    added = _git("log", "--follow", "--diff-filter=A", "--format=%cI", "--",
                 src.name, cwd=src.parent).splitlines()
    return (added[-1] if added else None), (updated or None)


def _human(iso):
    d = datetime.fromisoformat(iso)
    return f'<time datetime="{iso}">{d:%B} {d.day}, {d.year}</time>'


def on_page_markdown(markdown, page, config, files):
    planned = page.file.src_uri in _planned
    if planned:
        page.meta["robots"] = "noindex, follow"
    if "description" not in page.meta:
        desc = _description(markdown)
        if desc:
            # Material writes meta into attributes unescaped; a stray quote truncates it
            page.meta["description"] = html.escape(desc)
    created, updated = (None, None) if planned else _dates(page)
    if updated:
        page.meta["date_modified"] = updated
        page.meta["revision_date"] = _human(updated)            # Material's page-foot "updated"
    if created:
        page.meta["date_published"] = created
        page.meta["git_creation_date_localized"] = _human(created)
    _pages[page.file.src_uri] = {
        "title": page.title, "url": page.canonical_url, "planned": planned,
        "description": html.unescape(str(page.meta.get("description", ""))),
        "markdown": markdown, "created": created, "updated": updated,
    }
    return markdown


# --- JSON-LD ---------------------------------------------------------------

_CHAPTER = re.compile(r"^(\d+\.\d+|[A-J]\.) ")


def _entities(config):
    base = config["site_url"]
    desc = " ".join(config["site_description"].split())
    author_url = base + AUTHOR_PAGE.removesuffix(".md") + "/"
    author = {"@type": "Person", "@id": base + "#author", "name": config["site_author"],
              "alternateName": "Ram Dwivedi", "url": author_url, "sameAs": AUTHOR_SAME_AS,
              "jobTitle": AUTHOR_JOB_TITLE,
              "worksFor": {"@type": "Organization", "name": AUTHOR_EMPLOYER},
              "knowsAbout": AUTHOR_KNOWS_ABOUT}
    website = {"@type": "WebSite", "@id": base + "#website", "url": base,
               "name": config["site_name"], "description": desc, "inLanguage": "en",
               "publisher": {"@id": author["@id"]}}
    book = {"@type": "Book", "@id": base + "#book", "url": base, "name": config["site_name"],
            "description": desc, "author": {"@id": author["@id"]},
            "publisher": {"@id": author["@id"]}, "inLanguage": "en",
            "license": LICENSE_URL, "image": base + SOCIAL_IMAGE}
    return base, author, website, book


def _breadcrumbs(page, base):
    crumbs = [("Home", base)]
    for section in reversed(page.ancestors):
        index = next((c for c in section.children
                      if getattr(c, "is_index", False) and getattr(c, "url", None) is not None),
                     None)
        if index is not None and index is not page:
            crumbs.append((section.title, index.canonical_url))
    crumbs.append((page.title, page.canonical_url))
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": u}
        for i, (n, u) in enumerate(crumbs, 1)]}


def _jsonld(page, config):
    base, author, website, book = _entities(config)
    if page.is_homepage:
        return [website, author, book]
    info = _pages.get(page.file.src_uri)
    if not info or info["planned"]:
        return None
    if page.file.src_uri == AUTHOR_PAGE:
        kind = "ProfilePage"
    elif _CHAPTER.match(page.title or ""):
        kind = "TechArticle"
    elif page.is_index:
        kind = "CollectionPage"
    else:
        kind = "WebPage"
    node = {"@type": kind, "@id": page.canonical_url + "#page", "url": page.canonical_url,
            "name": page.title, "inLanguage": "en", "isPartOf": {"@id": website["@id"]},
            "image": base + SOCIAL_IMAGE, "license": LICENSE_URL,
            "author": {"@id": author["@id"]}}
    if kind == "TechArticle":
        node.update({"headline": page.title, "mainEntityOfPage": page.canonical_url,
                     "publisher": {"@id": author["@id"]},
                     "isPartOf": [{"@id": website["@id"]}, {"@id": book["@id"]}]})
    if kind == "ProfilePage":
        node["mainEntity"] = {"@id": author["@id"]}
    if info["description"]:
        node["description"] = info["description"]
    if info["created"]:
        node["datePublished"] = info["created"]
    if info["updated"]:
        node["dateModified"] = info["updated"]
    node["breadcrumb"] = _breadcrumbs(page, base)
    return [node, website, author, book]


def on_post_page(output, page, config):
    graph = _jsonld(page, config)
    if not graph:
        return output
    data = json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tag = f'<script type="application/ld+json">{data}</script>\n'
    return output.replace("</head>", tag + "</head>", 1)


# --- llms.txt --------------------------------------------------------------

_LINK = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)(\))")
_CODE = re.compile(r"(^[ \t]*(?:```|~~~).*?^[ \t]*(?:```|~~~)[ \t]*$|`[^`\n]+`)", re.M | re.S)


def _absolute_links(markdown, src_uri, base):
    def fix(m):
        target = m.group(2)
        if re.match(r"^([a-z][a-z0-9+.-]*:|#|/)", target):
            return m.group(0)
        path, _, frag = target.partition("#")
        path = posixpath.normpath(posixpath.join(posixpath.dirname(src_uri), path))
        if path.endswith(".md"):
            path = path[: -len(".md")]
            if path == "index":
                path = ""
            elif path.endswith("/index"):
                path = path[: -len("index")]
            else:
                path += "/"
        url = base + path + ("#" + frag if frag else "")
        return m.group(1) + url + m.group(3)
    # leave code alone: `handlers[kind](event)` is a call, not a link
    parts = _CODE.split(markdown)
    return "".join(p if i % 2 else _LINK.sub(fix, p) for i, p in enumerate(parts))


def _nav_items(items, depth=0):
    """Yield ('section', title, depth) and ('page', src_uri, depth) in nav order."""
    for item in items:
        if item.is_section:
            yield "section", item.title, depth
            yield from _nav_items(item.children, depth + 1)
        elif item.is_page:
            yield "page", item.file.src_uri, depth


def _write_llms(config, site):
    base = config["site_url"]
    summary = " ".join(config["site_description"].split())
    lines = [f"# {config['site_name']}", "", f"> {summary}", "",
             f"Written by {config['site_author']}. Prose is CC BY 4.0, code is MIT; "
             f"source at {config['repo_url']}. Chapters still marked planned are omitted. "
             f"Every page listed here, in full as markdown: {base}llms-full.txt"]
    full = [f"# {config['site_name']}: full text", "", f"> {summary}"]
    heading, pending = None, []

    def flush():
        if pending:
            lines.extend(["", f"## {heading}", "", *pending])
            pending.clear()

    for kind, value, depth in _nav_items(_nav.items if _nav else []):
        if kind == "section":
            if depth == 0:
                flush()
                heading = value
            continue
        info = _pages.get(value)
        if not info or info["planned"]:
            continue
        if depth == 0:   # top-level page outside any part
            flush()
            heading = "Optional" if value == "contributing.md" else info["title"]
        entry = f"- [{info['title']}]({info['url']})"
        if info["description"]:
            entry += f": {info['description']}"
        pending.append(entry)
        full.extend(["", "---", "", f"Source: {info['url']}"])
        if info["updated"]:
            full.append(f"Last updated: {info['updated'][:10]}")
        full.extend(["", _absolute_links(info["markdown"], value, base).strip()])
    flush()
    (site / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (site / "llms-full.txt").write_text("\n".join(full) + "\n", encoding="utf-8")


def on_post_build(config):
    site = Path(config["site_dir"])
    _write_llms(config, site)
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
    # lastmod = the page's last commit, not the build date MkDocs stamps on every URL
    lastmod = {i["url"]: i["updated"][:10] for i in _pages.values() if i["updated"]}
    xml = re.sub(
        r"(<loc>([^<]+)</loc>\s*<lastmod>)([^<]*)(</lastmod>)",
        lambda m: m.group(1) + lastmod.get(m.group(2), m.group(3)) + m.group(4),
        xml,
    )
    sitemap.write_text(xml, encoding="utf-8")
    with gzip.open(site / "sitemap.xml.gz", "wb") as gz:
        gz.write(xml.encode("utf-8"))
