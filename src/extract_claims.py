#!/usr/bin/env python3
"""
extract_claims.py — stage 2 of REF-2026-019: fetch archived Chinese-language
pages of frame brands from Common Crawl WARC records and extract
licence-claim sentences.

Protocol reference: locked_protocol_v1.0.md sections 5-6. This stage reads
ONLY the public Common Crawl archive (byte-range requests against
data.commoncrawl.org); it never contacts the brands' servers, opens no
accounts, and submits no data. The archive's crawler is itself a collection
vantage and is recorded as such (vantage="commoncrawl") per the protocol's
vantage-as-variable rule.

Politeness: serial requests, >=1.1s pause, exponential backoff on 429/5xx
per the Common Crawl FAQ.

Outputs (append-only, resumable by URL):
  artifacts/claims/claims_cc.jsonl       one row per page: url, claims found
  artifacts/claims/fetch_manifest.csv    warc coordinates + payload sha256
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts")
PROBE = os.path.join(ART, "frames", "cc_chinese_probe.jsonl")
OUT_DIR = os.path.join(ART, "claims")
CLAIMS_OUT = os.path.join(OUT_DIR, "claims_cc.jsonl")
MANIFEST = os.path.join(OUT_DIR, "fetch_manifest.csv")

# Same crawl as the presence probe (amendment 1 pins it).
CC_INDEX = "CC-MAIN-2026-25"
IDX = f"https://index.commoncrawl.org/{CC_INDEX}-index"
DATA = "https://data.commoncrawl.org/"
UA = {"User-Agent": ("licence-anchoring-research/1.0 (academic measurement; "
                     "contact via github.com/nathanskill/licence-anchoring)")}

PAUSE = 1.2
MAX_RETRY = 5
BACKOFF = 25.0
TIMEOUT = 120
PAGES_PER_DOMAIN = 40      # unique URL paths per domain (index query cap 200)

# Claim-bearing sentence patterns (Chinese + English). Extraction is
# deliberately recall-oriented; coding into A/B/C/D happens later under the
# frozen taxonomy, not here.
PATTERNS = [
    ("operative_cn", re.compile(r"[^。\n]{0,60}(?:是|为)[^。\n]{2,80}?(?:的交易名称|的商业名称|的注册商标|旗下品牌|经批准使用的交易名称)[^。\n]{0,40}")),
    ("operative_en", re.compile(r"[^.\n]{0,80}\btrading name of\b[^.\n]{2,120}", re.I)),
    ("regulated_cn", re.compile(r"[^。\n]{0,60}受[^。\n]{2,60}?(?:监管|授权|许可)[^。\n]{0,60}")),
    ("regulated_en", re.compile(r"[^.\n]{0,80}\b(?:regulated|authori[sz]ed|licen[cs]ed)\s+(?:and\s+\w+\s+)?by\b[^.\n]{2,120}", re.I)),
    ("licence_no", re.compile(r"(?:牌照|监管|注册|许可证?|授权)(?:编?号|号码)?[::\s]*[A-Z]{0,6}[\s#:]*\d{3,8}")),
    ("fca_frn", re.compile(r"\bFCA\b[^.。\n]{0,40}?\d{5,7}|\bFRN\b[:\s]*\d{5,7}", re.I)),
    ("asic_afsl", re.compile(r"\bAFSL\b[:\s#]*\d{5,7}|\bASIC\b[^.。\n]{0,40}?\d{5,7}", re.I)),
    ("cysec_no", re.compile(r"\bCySEC\b[^.。\n]{0,40}?\d{2,3}/\d{2}|\b\d{2,3}/\d{2}\b(?=[^.。\n]{0,30}(?:CySEC|塞浦路斯))", re.I)),
    ("offshore_reg", re.compile(r"\b(?:SD|IB|GB|SIBA|VFSC|FSC|FSA|MB)[\s#:/]*\d{3,10}\b")),
    ("entity_name", re.compile(r"[A-Z][A-Za-z0-9&., ]{2,60}(?:LLC|Ltd|Limited|LP|Inc|Pty)\.?(?:\s*\((?:SC|SV|VC|BZ|MU|VU|CY|UK|AU)\))?")),
]

STRIP = re.compile(r"(?is)<(script|style|noscript).*?</\1>")
TAGS = re.compile(r"(?s)<[^>]+>")

MANIFEST_FIELDS = ["domain", "url", "warc_filename", "warc_offset",
                   "warc_length", "payload_sha256", "n_claims", "fetched_utc"]


def retrying(fn, *a, **kw):
    last = None
    for attempt in range(1, MAX_RETRY + 1):
        try:
            return fn(*a, **kw)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(BACKOFF * attempt)
                continue
            raise
        except Exception as exc:            # noqa: BLE001
            last = exc
            time.sleep(BACKOFF * attempt)
    raise last


def index_records(domain):
    """Unique-path zho page records for a domain, up to PAGES_PER_DOMAIN."""
    q = urllib.parse.urlencode({
        "url": domain, "matchType": "domain", "output": "json",
        "fl": "url,filename,offset,length,languages,status", "limit": "200",
    })
    url = f"{IDX}?{q}&filter==status:200&filter=" + urllib.parse.quote("~languages:^zho")

    def _once():
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read().decode("utf-8", errors="ignore")
    try:
        body = retrying(_once)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise
    recs, seen = [], set()
    for line in body.splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        path = urllib.parse.urlparse(rec["url"]).path.rstrip("/")
        if path in seen:
            continue
        seen.add(path)
        recs.append(rec)
        if len(recs) >= PAGES_PER_DOMAIN:
            break
    return recs


def fetch_warc_payload(rec):
    start = int(rec["offset"])
    end = start + int(rec["length"]) - 1

    def _once():
        req = urllib.request.Request(
            DATA + rec["filename"], headers={**UA, "Range": f"bytes={start}-{end}"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read()
    raw = retrying(_once)
    try:
        payload = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    except OSError:
        payload = raw
    parts = payload.split(b"\r\n\r\n", 2)
    body = parts[2] if len(parts) == 3 else payload
    return body, hashlib.sha256(payload).hexdigest()


def visible_text(html_bytes):
    for enc in ("utf-8", "gb18030", "big5"):
        try:
            html = html_bytes.decode(enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        html = html_bytes.decode("utf-8", errors="ignore")
    txt = TAGS.sub("\n", STRIP.sub(" ", html))
    txt = txt.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#39;", "'")
    return re.sub(r"\n{2,}", "\n", txt)


def extract(txt):
    hits, seen = [], set()
    for kind, pat in PATTERNS:
        for m in pat.finditer(txt):
            s = re.sub(r"\s+", " ", m.group(0)).strip()
            if not (6 <= len(s) <= 300):
                continue
            k = (kind, s)
            if k in seen:
                continue
            seen.add(k)
            hits.append({"kind": kind, "text": s})
    return hits[:60]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--limit-domains", type=int, default=0,
                   help="process at most N domains (0 = all)")
    args = p.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    domains = []
    for line in open(PROBE):
        r = json.loads(line)
        n = r.get("n_zho_captures_capped", r.get("n_zho_pages", 0))
        if n > 0:
            domains.append(r["domain"])
    domains.sort()
    if args.limit_domains:
        domains = domains[:args.limit_domains]

    done_urls = set()
    if os.path.exists(CLAIMS_OUT):
        for line in open(CLAIMS_OUT):
            try:
                done_urls.add(json.loads(line)["url"])
            except Exception:               # noqa: BLE001
                pass

    new_manifest = not os.path.exists(MANIFEST)
    mf = open(MANIFEST, "a", newline="")
    mw = csv.DictWriter(mf, fieldnames=MANIFEST_FIELDS)
    if new_manifest:
        mw.writeheader()

    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(CLAIMS_OUT, "a") as out:
        for di, dom in enumerate(domains, 1):
            try:
                recs = index_records(dom)
            except Exception as exc:        # noqa: BLE001
                print(f"[{di}/{len(domains)}] {dom}: index failed: {exc}")
                continue
            time.sleep(PAUSE)
            todo = [r for r in recs if r["url"] not in done_urls]
            print(f"[{di}/{len(domains)}] {dom}: {len(recs)} pages, "
                  f"{len(todo)} to fetch")
            for rec in todo:
                try:
                    body, digest = fetch_warc_payload(rec)
                    hits = extract(visible_text(body))
                except Exception as exc:    # noqa: BLE001
                    print(f"    fetch failed {rec['url'][:60]}: {exc}")
                    time.sleep(PAUSE)
                    continue
                out.write(json.dumps({
                    "domain": dom, "url": rec["url"], "crawl": CC_INDEX,
                    "vantage": "commoncrawl", "n_claims": len(hits),
                    "claims": hits}, ensure_ascii=False) + "\n")
                out.flush()
                mw.writerow({"domain": dom, "url": rec["url"],
                             "warc_filename": rec["filename"],
                             "warc_offset": rec["offset"],
                             "warc_length": rec["length"],
                             "payload_sha256": digest,
                             "n_claims": len(hits), "fetched_utc": stamp})
                mf.flush()
                time.sleep(PAUSE)
    mf.close()
    print("done")


if __name__ == "__main__":
    main()
