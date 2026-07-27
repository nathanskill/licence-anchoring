#!/usr/bin/env python3
"""
frame_offshore.py — build sampling frame F2 (the spine) from offshore
securities-dealer registers.

Protocol reference: locked_protocol_v1.0.md section 4, frame F2. These
registers enumerate the *onboarding vehicles* directly — the entities that
actually contract with clients — which is why the protocol treats them as
the spine rather than starting from a brand list.

Keyless throughout: plain HTTP against public register pages. Every fetch is
archived verbatim with a SHA-256 so a reviewer can reproduce the parse from
the same bytes.

Documented limitation (protocol section 6): the Seychelles register carries
entity name, address, contact and website but NO licence number. Frames built
from it therefore support name-level matching only, and that limitation is
recorded per-row in the `has_licence_number` column rather than hidden.

Usage:
    python3 src/frame_offshore.py --fetch      # archive raw register pages
    python3 src/frame_offshore.py --parse      # parse archives into frame CSV
"""
import argparse
import csv
import hashlib
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "registers")
ART = os.path.join(ROOT, "artifacts", "frames")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 "
      "(academic research; contact via repository)")

# Public register endpoints. Each entry: (key, url, jurisdiction, regulator).
REGISTERS = [
    ("seychelles_securities_dealers",
     "https://fsaseychelles.sc/regulated-entities/capital-markets",
     "Seychelles", "Seychelles FSA"),
]

REQUEST_PAUSE = 2.0     # politeness; these are small public pages
TIMEOUT = 60


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def cmd_fetch():
    os.makedirs(RAW, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest = []
    for key, url, juris, regulator in REGISTERS:
        try:
            body = fetch(url)
        except Exception as exc:                      # noqa: BLE001
            print(f"FAILED {key}: {exc}")
            manifest.append({"key": key, "url": url, "status": "failed",
                             "error": str(exc), "fetched_utc": stamp})
            continue
        path = os.path.join(RAW, f"{key}_{stamp}.html")
        with open(path, "wb") as f:
            f.write(body)
        digest = sha256_bytes(body)
        manifest.append({"key": key, "url": url, "jurisdiction": juris,
                         "regulator": regulator, "status": "ok",
                         "bytes": len(body), "sha256": digest,
                         "file": os.path.basename(path),
                         "fetched_utc": stamp})
        print(f"ok {key}: {len(body)} bytes, sha256 {digest[:16]}")
        time.sleep(REQUEST_PAUSE)

    os.makedirs(ART, exist_ok=True)
    mpath = os.path.join(ART, f"register_fetch_manifest_{stamp}.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)
    print("manifest:", mpath)


def strip_tags(html):
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", "\n", html)
    html = html.replace("&amp;", "&").replace("&nbsp;", " ")
    html = html.replace("&#039;", "'").replace("&quot;", '"')
    return html


def parse_seychelles(html):
    """Extract (entity_name, website, email, category) per registrant.

    The register renders each registrant as a Bootstrap accordion card whose
    header button carries the entity name and whose `card-body` carries the
    address, phone, email and website. The website lives in an `<a href>`
    attribute, so a text-only parse silently loses it — parse the card blocks
    structurally instead. The `data-parent="#accordion-<category>"` attribute
    also carries the register category, which is worth keeping.
    """
    rows = []
    # Each collapse block is one registrant's body; the preceding button text
    # is the entity name.
    card_re = re.compile(
        r'<button class="btn btn-link"[^>]*data-target="#collapse-([^"]+)"[^>]*>'
        r'(?:\s*<span[^>]*></span>)?\s*(.*?)\s*</button>.*?'
        r'<div id="collapse-\1"[^>]*>(.*?)</div>\s*</div>\s*</div>',
        re.S)
    href_re = re.compile(r'href="([^"]+)"', re.I)
    cat_re = re.compile(r"^([a-z-]+?)-\d+$")

    for m in card_re.finditer(html):
        anchor, name_html, body = m.group(1), m.group(2), m.group(3)
        name = re.sub(r"<[^>]+>", "", name_html)
        name = re.sub(r"\s+", " ", name).strip()
        if not name or len(name) > 160:
            continue

        website = email = ""
        for href in href_re.findall(body):
            h = href.strip()
            if h.lower().startswith("mailto:") and not email:
                email = h[7:]
            elif h.lower().startswith("tel:"):
                continue
            elif re.match(r"^(https?://|www\.)", h, re.I) and not website:
                website = h

        cm = cat_re.match(anchor)
        rows.append({"entity_name": name, "website": website,
                     "email": email,
                     "category": cm.group(1) if cm else anchor})

    # De-duplicate on (name, category), preserving first-seen order.
    seen, out = set(), []
    for r in rows:
        k = (r["entity_name"].lower(), r["category"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


PARSERS = {"seychelles_securities_dealers": parse_seychelles}


def cmd_parse():
    os.makedirs(ART, exist_ok=True)
    if not os.path.isdir(RAW):
        print("no archives; run --fetch first")
        return 2
    files = sorted(os.listdir(RAW))
    out_rows = []
    for key, _url, juris, regulator in REGISTERS:
        matches = [f for f in files if f.startswith(key) and f.endswith(".html")]
        if not matches:
            print(f"no archive for {key}")
            continue
        latest = matches[-1]
        with open(os.path.join(RAW, latest), "rb") as f:
            body = f.read()
        html = body.decode("utf-8", errors="ignore")
        rows = PARSERS[key](html)
        for r in rows:
            out_rows.append({
                "register": key,
                "jurisdiction": juris,
                "regulator": regulator,
                "category": r.get("category", ""),
                "entity_name": r["entity_name"],
                "website": r["website"],
                "email": r.get("email", ""),
                # Protocol section 6: this register publishes no licence
                # numbers, so B-vs-C discrimination is name-level only.
                "has_licence_number": 0,
                "source_file": latest,
                "source_sha256": sha256_bytes(body),
            })
        print(f"{key}: parsed {len(rows)} entities from {latest}")

    path = os.path.join(ART, "frame_f2_offshore_registers.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "register", "jurisdiction", "regulator", "category",
            "entity_name", "website", "email",
            "has_licence_number", "source_file", "source_sha256"])
        w.writeheader()
        w.writerows(out_rows)
    print(f"written: {path} ({len(out_rows)} rows)")
    with_site = sum(1 for r in out_rows if r["website"])
    print(f"entities with a website recorded: {with_site}"
          f" ({with_site / max(1, len(out_rows)):.0%})")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--fetch", action="store_true")
    g.add_argument("--parse", action="store_true")
    a = p.parse_args()
    if a.fetch:
        cmd_fetch()
        return 0
    return cmd_parse()


if __name__ == "__main__":
    raise SystemExit(main())
