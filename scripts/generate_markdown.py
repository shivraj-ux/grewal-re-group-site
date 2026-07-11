#!/usr/bin/env python3
"""Generate a clean .md sibling for an .html page — mechanical extraction only,
no rewriting. Skips site chrome (nav/header/footer/forms/scripts) and keeps
headings, paragraphs, lists, quotes, tables, and links from the real content.

Usage: python3 scripts/generate_markdown.py <file1.html> [file2.html ...]
       python3 scripts/generate_markdown.py --all   (every page in AEO_TARGETS)
"""
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Elements whose entire subtree is skipped outright (chrome, scripts, forms).
SKIP_TAGS = {"script", "style", "svg", "form", "noscript", "template", "nav"}
# Any element carrying one of these classes (or id) is skipped as chrome.
SKIP_CLASS_PREFIXES = ("gh-",)
SKIP_CLASSES = {"cm-signup", "back-to-top", "reading-progress"}
SKIP_IDS = {"gh-header", "gh-primary-nav"}

HEADING_TAGS = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}
BLOCK_TAGS = {"p", "li", "blockquote", "tr", "figcaption", "dt", "dd"} | set(HEADING_TAGS)
INLINE_WRAP = {"strong": "**", "b": "**", "em": "_", "i": "_"}
# HTML5 void elements: no closing tag exists, and pages here don't self-close
# them (e.g. `<img src="...">` not `<img src="..." />`), so HTMLParser never
# fires handle_endtag for these tag names.
VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
                 "link", "meta", "param", "source", "track", "wbr"}


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.blocks = []          # list of finished block strings (already formatted)
        self._buf = []            # current inline text buffer
        self._tag_stack = []      # (tag, skip_depth_marker)
        self._skip_depth = 0
        self._in_title = False
        self._list_stack = []     # 'ul' | 'ol'
        self._table_rows = []     # rows of current table (list[list[str]])
        self._in_table = False
        self._link_href = None
        self._wrap_stack = []

    # ---- helpers ----
    def _flush_inline(self):
        text = "".join(self._buf).strip()
        self._buf = []
        return re.sub(r"\s+", " ", text)

    def _emit_block(self, text, prefix=""):
        text = text.strip()
        if text:
            self.blocks.append(prefix + text)

    def _is_skippable(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if any(c in SKIP_CLASSES for c in classes):
            return True
        if any(c.startswith(p) for c in classes for p in SKIP_CLASS_PREFIXES):
            return True
        if attrs.get("id") in SKIP_IDS:
            return True
        if attrs.get("aria-hidden") == "true":
            return True
        return tag in SKIP_TAGS

    # ---- HTMLParser hooks ----
    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        # Void elements (img, br, meta, link, ...) are frequently written
        # without a self-closing slash, so HTMLParser never calls
        # handle_endtag for them. If one were allowed to bump _skip_depth
        # like a normal container, that +1 would never be paid back and
        # every skip region would leak open for the rest of the document.
        if tag in VOID_ELEMENTS:
            if self._skip_depth:
                return
        elif self._skip_depth:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
            return
        if tag == "meta":
            if attrs_d.get("name") == "description":
                self.description = attrs_d.get("content", "").strip()
            return
        if tag == "link" and attrs_d.get("rel") == "canonical":
            self.canonical = attrs_d.get("href", "").strip()
            return
        if tag not in VOID_ELEMENTS and self._is_skippable(tag, attrs):
            self._skip_depth = 1
            return
        if tag in ("div", "section", "article", "header", "footer"):
            # Block-level containers (breadcrumbs, bylines, cards, ...) start
            # a fresh block so their text doesn't run into whatever heading
            # or paragraph comes next.
            self._emit_block(self._flush_inline())
            return
        if tag in ("ul", "ol"):
            self._list_stack.append(tag)
            return
        if tag == "table":
            self._in_table = True
            self._table_rows = []
            return
        if tag == "tr" and self._in_table:
            self._table_rows.append([])
            return
        if tag in ("td", "th") and self._in_table:
            self._buf = []
            return
        if tag == "br":
            self._buf.append("\n")
            return
        if tag == "hr":
            self._emit_block(self._flush_inline())
            self.blocks.append("---")
            return
        if tag == "a":
            self._link_href = attrs_d.get("href", "")
            self._buf.append("[")
            return
        if tag in INLINE_WRAP:
            self._buf.append(INLINE_WRAP[tag])
            self._wrap_stack.append(INLINE_WRAP[tag])
            return
        if tag == "summary":
            self._buf.append("**Q: ")
            return

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            # Only reachable if the source self-closed a void tag (`<img .../>`),
            # in which case handle_starttag already deliberately left
            # _skip_depth untouched for it — so this end tag must too.
            return
        if self._skip_depth:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
            return
        if tag in HEADING_TAGS:
            text = self._flush_inline()
            self._emit_block(text, HEADING_TAGS[tag] + " ")
            return
        if tag == "p":
            self._emit_block(self._flush_inline())
            return
        if tag == "li":
            marker = "- "
            self._emit_block(self._flush_inline(), marker)
            return
        if tag in ("ul", "ol"):
            if self._list_stack:
                self._list_stack.pop()
            return
        if tag in ("div", "section", "article", "header", "footer"):
            self._emit_block(self._flush_inline())
            return
        if tag == "blockquote":
            self._emit_block(self._flush_inline(), "> ")
            return
        if tag in ("td", "th"):
            if self._table_rows:
                self._table_rows[-1].append(self._flush_inline())
            return
        if tag == "tr":
            return
        if tag == "table":
            self._in_table = False
            if self._table_rows:
                rows = [r for r in self._table_rows if any(r)]
                if rows:
                    header, *rest = rows
                    lines = ["| " + " | ".join(header) + " |",
                             "|" + "|".join(["---"] * len(header)) + "|"]
                    for r in rest:
                        r = (r + [""] * len(header))[:len(header)]
                        lines.append("| " + " | ".join(r) + " |")
                    self.blocks.append("\n".join(lines))
            self._table_rows = []
            return
        if tag == "a":
            text = "".join(self._buf[self._buf.index("[") + 1:]) if "[" in self._buf else None
            # simpler: rebuild from buffer since "[" was appended as a literal marker
            joined = "".join(self._buf)
            self._buf = [joined + f"]({self._link_href})"] if self._link_href else [joined + "]"]
            self._link_href = None
            return
        if tag in INLINE_WRAP:
            if self._wrap_stack:
                w = self._wrap_stack.pop()
                self._buf.append(w)
            return
        if tag == "summary":
            self._buf.append(":** ")
            return

    def handle_data(self, data):
        if self._skip_depth:
            return
        if self._in_title:
            self.title += data
            return
        self._buf.append(data)


def extract(html_path: Path) -> str:
    raw = html_path.read_text(encoding="utf-8")
    ex = Extractor()
    ex.feed(raw)
    title = html.unescape(ex.title).strip()
    desc = html.unescape(ex.description).strip()
    canonical = ex.canonical.strip()

    lines = []
    lines.append(f"# {title}" if title else "# Grewal RE Group")
    if desc:
        lines.append(f"\n> {desc}")
    if canonical:
        lines.append(f"\nSource: [{canonical}]({canonical}) · Markdown rendering for AI agents "
                      f"(request `Accept: text/markdown` on the page URL, or read this file directly).")
    lines.append("")
    seen = set()
    for b in ex.blocks:
        key = b.strip()
        if not key or key in seen and len(key) < 40:
            # allow repeated long paragraphs (rare, legit) but collapse tiny repeated noise
            pass
        lines.append(b)
    body = "\n\n".join(lines)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    failures = []
    thin = []
    for arg in argv:
        p = ROOT / arg if not Path(arg).is_absolute() else Path(arg)
        if not p.exists():
            print(f"skip (not found): {p}")
            continue
        try:
            md = extract(p)
        except Exception as e:  # noqa: BLE001 - one bad file must not kill the batch
            failures.append(str(p.relative_to(ROOT)))
            print(f"FAILED {p.relative_to(ROOT)}: {e}")
            continue
        out = p.with_suffix(".md")
        out.write_text(md, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(md)} bytes)")
        if len(md) < 600:
            thin.append(str(out.relative_to(ROOT)))
    if failures:
        print(f"\n{len(failures)} FAILURES:")
        for f in failures:
            print(f"  {f}")
    if thin:
        print(f"\n{len(thin)} SUSPICIOUSLY THIN (<600 bytes, check manually):")
        for t in thin:
            print(f"  {t}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
