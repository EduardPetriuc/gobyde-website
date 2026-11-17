#!/usr/bin/env python3
"""Generate the static English pages (en/*.html) from the Romanian source pages.

The Romanian HTML (index.html, aura-clicker.html, turning-tails.html) is the
source of truth. The English dictionary lives in script.js (`translations.en`).
This script applies it to the Romanian markup so that English is real, crawlable
HTML served at /en/..., instead of being injected by JavaScript.

Privacy-policy pages are intentionally NOT handled here.

Usage:  python3 tools/build_en.py          # (re)write en/*.html
        python3 tools/build_en.py --check  # exit 1 if en/*.html are out of date

Requires: python3 and node (to read the dictionary out of script.js).
"""
import html, json, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://gobyde.com"

PAGES = {
    # source file: (ro path, en path, en <title>)
    "index.html": ("/", "/en/", "GoByde — Mobile games and apps"),
    "aura-clicker.html": ("/aura-clicker", "/en/aura-clicker", "Aura Clicker — A GoByde game"),
    "turning-tails.html": ("/turning-tails", "/en/turning-tails", "Turning Tails — A GoByde game"),
}
HREF_MAP = {
    "/": "/en/",
    "/#games": "/en/#games",
    "/#contact": "/en/#contact",
    "/aura-clicker": "/en/aura-clicker",
    "/turning-tails": "/en/turning-tails",
}
LANG_BUTTON_EN = ('\n            <span>RO</span>\n            <span class="language-divider">/</span>\n'
                  '            <span class="language-active">EN</span>\n          ')
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def load_dictionary():
    js = ("const fs=require('fs');const s=fs.readFileSync(process.argv[1],'utf8');"
          "const i=s.indexOf('\\nconst header');"
          "const t=new Function(s.slice(0,i)+';return translations;')();"
          "process.stdout.write(JSON.stringify(t));")
    out = subprocess.run(["node", "-e", js, str(ROOT / "script.js")], check=True, capture_output=True, text=True)
    return json.loads(out.stdout)


def get_attr(raw, name):
    m = re.search(r'\s' + re.escape(name) + r'="([^"]*)"', raw)
    return m.group(1) if m else None


def set_attr(raw, name, value):
    value = html.escape(value, quote=True)
    pat = re.compile(r'(\s' + re.escape(name) + r'=")[^"]*(")')
    if pat.search(raw):
        return pat.sub(lambda m: m.group(1) + value + m.group(2), raw, count=1)
    end = "/>" if raw.rstrip().endswith("/>") else ">"
    head = raw.rstrip()[: -len(end)].rstrip()
    return f'{head} {name}="{value}"{" /" if end == "/>" else ""}>'


def rewrite_hrefs(fragment):
    return re.sub(r'href="([^"]*)"', lambda m: f'href="{HREF_MAP.get(m.group(1), m.group(1))}"', fragment)


class Localizer(HTMLParser):
    def __init__(self, src, en, en_path, ro_path, en_title, mode="en"):
        super().__init__(convert_charrefs=False)
        self.en, self.en_path, self.ro_path, self.en_title = en, en_path, ro_path, en_title
        self.mode = mode          # "en": build English page; "ro": only sync texts with the dictionary
        self.out = []
        self.cap = None           # (tag, depth, start, value) while syncing an element's content (ro mode)
        self.skip = None          # (tag, depth) while replacing an element's content
        self.ldjson = False
        self.meta_description = None
        self.feed(src)
        self.close()

    # -- helpers -------------------------------------------------------
    def emit(self, s):
        if self.skip is None:
            self.out.append(s)

    def transform_start(self, tag, raw):
        d = self.en
        attrs_i18n = {k: get_attr(raw, k) for k in ("data-i18n-aria", "data-i18n-alt", "data-i18n-content")}
        if attrs_i18n["data-i18n-aria"] and d.get(attrs_i18n["data-i18n-aria"]):
            raw = set_attr(raw, "aria-label", d[attrs_i18n["data-i18n-aria"]])
        if attrs_i18n["data-i18n-alt"] and d.get(attrs_i18n["data-i18n-alt"]):
            raw = set_attr(raw, "alt", d[attrs_i18n["data-i18n-alt"]])
        if attrs_i18n["data-i18n-content"] and d.get(attrs_i18n["data-i18n-content"]):
            raw = set_attr(raw, "content", d[attrs_i18n["data-i18n-content"]])
            if get_attr(raw, "name") == "description":
                self.meta_description = d[attrs_i18n["data-i18n-content"]]
        if self.mode == "ro":
            return raw
        if tag == "html":
            raw = set_attr(raw, "lang", "en")
        elif tag == "body":
            raw = set_attr(raw, "data-alt-url", self.ro_path)
        elif tag == "link":
            if get_attr(raw, "rel") == "canonical":
                raw = set_attr(raw, "href", SITE + self.en_path)
            for a in ("href",):
                v = get_attr(raw, a)
                if v and re.match(r"^(assets/|styles\.css)", v):
                    raw = set_attr(raw, a, "/" + v)
        elif tag == "meta":
            prop = get_attr(raw, "property")
            if prop == "og:url":
                raw = set_attr(raw, "content", SITE + self.en_path)
            elif prop == "og:locale":
                raw = set_attr(raw, "content", "en_US")
            elif prop == "og:locale:alternate":
                raw = set_attr(raw, "content", "ro_RO")
        elif tag == "a":
            v = get_attr(raw, "href")
            if v in HREF_MAP:
                raw = set_attr(raw, "href", HREF_MAP[v])
        elif tag in ("img", "script", "source"):
            v = get_attr(raw, "src")
            if v and re.match(r"^(assets/|script\.js)", v):
                raw = set_attr(raw, "src", "/" + v)
        if tag == "button" and get_attr(raw, "data-language") is not None or (tag == "button" and " data-language" in raw):
            raw = set_attr(raw, "aria-label", "Schimbă în română")
        return raw

    # -- HTMLParser hooks ----------------------------------------------
    def handle_decl(self, decl):
        self.emit(f"<!{decl}>")

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        if self.skip:
            if tag == self.skip[0] and tag not in VOID:
                self.skip = (tag, self.skip[1] + 1)
            return
        raw = self.transform_start(tag, raw)
        self.out.append(raw)
        key = get_attr(raw, "data-i18n")
        if self.mode == "ro":
            if self.cap and tag == self.cap[0] and tag not in VOID:
                self.cap = (tag, self.cap[1] + 1, self.cap[2], self.cap[3])
            elif key and self.en.get(key) and not self.cap:
                self.cap = (tag, 1, len(self.out), self.en[key])
            return
        if key and self.en.get(key):
            self.out.append(rewrite_hrefs(self.en[key]))
            self.skip = (tag, 1)
        elif tag == "title":
            self.out.append(html.escape(self.en_title, quote=False))
            self.skip = (tag, 1)
        elif tag == "button" and " data-language" in raw:
            self.out.append(LANG_BUTTON_EN)
            self.skip = (tag, 1)
        elif tag == "script" and 'application/ld+json' in raw:
            self.ldjson = True
            self.ld_buf = []

    def handle_startendtag(self, tag, attrs):
        if self.skip:
            return
        self.out.append(self.transform_start(tag, self.get_starttag_text()))

    def handle_endtag(self, tag):
        if self.cap and tag == self.cap[0]:
            depth = self.cap[1] - 1
            if depth == 0:
                norm = lambda s: re.sub(r"\s+", " ", s).strip()
                if norm("".join(self.out[self.cap[2]:])) != norm(self.cap[3]):
                    self.out[self.cap[2]:] = [self.cap[3]]
                self.cap = None
            else:
                self.cap = (tag, depth, self.cap[2], self.cap[3])
        if self.skip:
            if tag == self.skip[0]:
                depth = self.skip[1] - 1
                self.skip = None if depth == 0 else (tag, depth)
                if depth == 0:
                    self.out.append(f"</{tag}>")
            return
        if self.ldjson and tag == "script":
            self.ldjson = False
            self.out.append("@@LDJSON@@" + "".join(self.ld_buf))
        self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if self.ldjson:
            self.ld_buf.append(data)
        else:
            self.emit(data)

    def handle_entityref(self, name): self.emit(f"&{name};")
    def handle_charref(self, name): self.emit(f"&#{name};")
    def handle_comment(self, data): self.emit(f"<!--{data}-->")
    def handle_pi(self, data): self.emit(f"<?{data}>")


def localize_jsonld(text, desc, page_urls):
    """text is the raw JSON string; swap description + page URLs for English."""
    def walk(node):
        if isinstance(node, dict):
            t = node.get("@type")
            if "description" in node and desc:
                node["description"] = desc
            if t in ("VideoGame", "WebSite") and node.get("url") in page_urls:
                node["url"] = page_urls[node["url"]]
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    data = json.loads(text)
    walk(data)
    body = "\n".join("    " + l for l in json.dumps(data, ensure_ascii=False, indent=2).split("\n"))
    return "\n" + body + "\n    "


def build():
    d = load_dictionary()["en"]
    page_urls = {SITE + ro: SITE + en for ro, en, _ in PAGES.values()}
    results = {}
    for src, (ro_path, en_path, en_title) in PAGES.items():
        p = Localizer((ROOT / src).read_text(), d, en_path, ro_path, en_title)
        text = "".join(p.out)
        text = re.sub(r"@@LDJSON@@(.*?)</script>",
                      lambda m: localize_jsonld(m.group(1), p.meta_description, page_urls) + "</script>", text, flags=re.S)
        results[ROOT / "en" / src] = text
    return results


def sync_ro():
    """Make the static Romanian HTML match translations.ro (what visitors already see)."""
    ro = load_dictionary()["ro"]
    for src, (ro_path, en_path, _) in PAGES.items():
        f = ROOT / src
        before = f.read_text()
        after = "".join(Localizer(before, ro, ro_path, en_path, "", mode="ro").out)
        if after != before:
            f.write_text(after)
            print("synced", src)


if __name__ == "__main__":
    if "--sync-ro" in sys.argv:
        sync_ro()
        sys.exit(0)
    files = build()
    if "--check" in sys.argv:
        stale = [str(f.relative_to(ROOT)) for f, t in files.items() if not f.exists() or f.read_text() != t]
        print("up to date" if not stale else "stale: " + ", ".join(stale))
        sys.exit(1 if stale else 0)
    (ROOT / "en").mkdir(exist_ok=True)
    for f, t in files.items():
        f.write_text(t)
        print("wrote", f.relative_to(ROOT))
