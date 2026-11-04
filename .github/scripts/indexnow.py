#!/usr/bin/env python3
"""Submit changed pages to IndexNow (Bing, Yandex, Seznam, ...).

Changed repo paths are read from stdin (one per line, e.g. `git diff --name-only`).
Each path is mapped to a URL and kept only if the live sitemap lists it, so
assets, drafts and the 404 page are never submitted. With --all, every URL in
the sitemap is submitted.

Never fails the caller: errors are printed and the exit code is 0, because a
missed ping must not block a deploy.
"""
import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
ENDPOINT = "https://api.indexnow.org/indexnow"
UA = "embra-indexnow/1"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def sitemap_urls(url, depth=0):
    root = ET.fromstring(fetch(url))
    if root.tag == NS + "sitemapindex" and depth < 2:
        out = []
        for loc in root.iter(NS + "loc"):
            out += sitemap_urls(loc.text.strip(), depth + 1)
        return out
    return [loc.text.strip() for loc in root.iter(NS + "loc")]


def path_to_url(path, mode, host):
    """Map a repo file to the page URL it produces, or None."""
    if mode == "starlight":
        m = re.fullmatch(r"src/content/docs/(.+)\.mdx?", path)
        if not m:
            return None
        slug = re.sub(r"(^|/)index$", "", m.group(1))
    else:  # static site served from the repo root
        if not path.endswith(".html"):
            return None
        if path == "index.html" or path.endswith("/index.html"):
            slug = path[: -len("index.html")].rstrip("/")
        else:
            return f"https://{host}/{path}"
    return f"https://{host}/{slug}/" if slug else f"https://{host}/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--sitemap", required=True)
    ap.add_argument("--mode", choices=["starlight", "static"], required=True)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    try:
        live = sitemap_urls(a.sitemap)
    except Exception as e:  # noqa: BLE001
        print(f"indexnow: cannot read sitemap {a.sitemap}: {e}")
        return 0

    if a.all:
        urls = live
    else:
        live_set = set(live)
        mapped = {path_to_url(p.strip(), a.mode, a.host) for p in sys.stdin if p.strip()}
        urls = sorted(u for u in mapped if u in live_set)

    if not urls:
        print("indexnow: no sitemap page changed, nothing to submit")
        return 0

    print(f"indexnow: {len(urls)} URL(s)")
    for u in urls:
        print("  " + u)
    if a.dry_run:
        return 0

    body = json.dumps({
        "host": a.host,
        "key": a.key,
        "keyLocation": f"https://{a.host}/{a.key}.txt",
        "urlList": urls[:10000],
    }).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"indexnow: HTTP {r.status}")
    except urllib.error.HTTPError as e:
        # 200/202 are success; 403 = key not found on host, 422 = URL/host mismatch, 429 = too many.
        print(f"indexnow: HTTP {e.code} {e.read()[:300]!r}")
    except Exception as e:  # noqa: BLE001
        print(f"indexnow: request failed: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
