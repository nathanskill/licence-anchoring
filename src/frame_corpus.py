#!/usr/bin/env python3
"""
frame_corpus.py — sampling frame F1: the retail FX/CFD vertical enumerated
from Common Crawl's domain-level web-graph vertices.

Protocol reference: locked_protocol_v1.0.md section 4 (frame F1) and
protocol/amendments/amendment_2_f1_host_regex.md, which fixes the pattern
below. The amendment was committed BEFORE this module was ever run against a
host list, so the pattern cannot have been tuned to the brands it selects.

Why F1 matters alongside F2: the register frame can only see brands that
appear in an offshore register we were able to enumerate, and two of the named
jurisdictions (Mauritius, BVI) could not be enumerated at all. F1 is
brand-driven from the corpus instead, so it reaches the "no offshore entity"
stratum that F2 cannot supply by construction.

What F1 is NOT: an exhaustive census of the vertical. It enumerates domains
whose NAME carries a vertical token, so a retail FX/CFD site with a
non-descriptive domain is invisible to it. Stated in the amendment and to be
stated in the paper.

The vertices file is streamed and filtered in memory; nothing is stored.

Usage:
    python3 src/frame_corpus.py --scan            # stream + filter the vertices
    python3 src/frame_corpus.py --sample          # draw the stratified sample
"""
import argparse
import csv
import gzip
import io
import json
import os
import random
import re
import urllib.request
import zlib
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts", "frames")
F2 = os.path.join(ART, "frame_f2_offshore_registers.csv")
OUT_MATCHES = os.path.join(ART, "frame_f1_matched_domains.csv")
OUT_SUMMARY = os.path.join(ART, "frame_f1_summary.json")

VERTICES_URL = ("https://data.commoncrawl.org/projects/hyperlinkgraph/"
                "cc-main-2026-may-jun-jul/domain/"
                "cc-main-2026-may-jun-jul-domain-vertices.txt.gz")
UA = ("licence-anchoring-research/1.0 (academic measurement; "
      "contact via github.com/nathanskill/licence-anchoring)")

SEED = 20260723
STRATUM_CAP = 0.40          # no stratum may exceed this share of the sample

# ---- FROZEN PATTERN (amendment 2; do not edit without a new amendment) ----

# Multi-character vertical tokens, matched at label boundaries.
VERTICAL_TOKENS = [
    "forex", "cfd", "mt4", "mt5", "metatrader", "brokers", "broker",
    "traders", "trader", "trading", "investing", "invest", "capital",
    "markets", "market", "prime", "securities", "fintech", "exchange",
    "gold", "xau", "futures", "margin", "leverage", "spread",
    "waihuiwang", "waihui", "huiyin", "jinrong",
]
# Two-letter tokens: whole label, or bounded by a separator or a digit only.
SHORT_TOKENS = ["fx", "wh"]

TOKEN_RE = re.compile(
    r"(?:^|[.\-_0-9])(" + "|".join(VERTICAL_TOKENS) + r")(?:$|[.\-_0-9])",
    re.I)
SHORT_RE = re.compile(
    r"(?:^|[.\-_0-9])(" + "|".join(SHORT_TOKENS) + r")(?:$|[.\-_0-9])", re.I)

# Negative tokens: ordinary non-vertical uses of the ambiguous words.
NEGATIVE_TOKENS = [
    "supermarket", "marketplace", "hypermarket", "minimarket", "fleamarket",
    "flea-market", "nightmarket", "farmersmarket", "goldsmith", "goldjewel",
    "goldenret", "marketingagency", "goldmine", "goldfish", "marketresearch",
]
NEGATIVE_RE = re.compile("|".join(NEGATIVE_TOKENS), re.I)

# Institutional / media suffixes and hosts excluded before any probe.
EXCLUDED_SUFFIXES = (".gov", ".gov.au", ".gov.uk", ".edu", ".edu.au",
                     ".ac.uk", ".org.au", ".mil")
EXCLUDED_HOSTS = {
    "reuters.com", "bloomberg.com", "ft.com", "wsj.com", "cnbc.com",
    "marketwatch.com", "investing.com", "tradingview.com", "yahoo.com",
    "forbes.com", "businessinsider.com", "seekingalpha.com", "morningstar.com",
    "wikipedia.org", "baidu.com", "sina.com.cn", "sohu.com", "163.com",
    "eastmoney.com", "hexun.com", "jrj.com.cn", "cnfol.com", "10jqka.com.cn",
    "fx678.com", "financemagnates.com", "leaprate.com", "financefeeds.com",
}

# Protocol section 7 rules 1-2: employer and author properties. Read from an
# untracked local file so the names never enter the public repository; the
# COUNT of exclusions is published, the names are not.
COI_EXCLUSIONS_FILE = os.path.join(ROOT, "data", "coi_excluded_domains.txt")

# --------------------------------------------------------------------------


def load_coi_exclusions():
    if not os.path.exists(COI_EXCLUSIONS_FILE):
        return set()
    out = set()
    with open(COI_EXCLUSIONS_FILE) as f:
        for line in f:
            d = line.strip().lower()
            if d and not d.startswith("#"):
                out.add(d)
    return out


def unreverse(rev):
    """'com.example.www' -> 'example.com' (vertices are reversed domains)."""
    return ".".join(reversed(rev.split(".")))


def name_part(domain):
    """The registrable-name part, i.e. everything before the public suffix.

    Amendment 3: a token occurring only in the public-suffix position does not
    place a domain in F1, because the suffix is a string chosen by the
    registry rather than by the registrant. Six generic TLDs are spelled as
    vertical vocabulary (.cfd .capital .market .exchange .gold .markets) and
    carried 42.4% of the raw matches.
    """
    parts = domain.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else domain


def classify(domain, coi):
    """Return (matched, reason). reason is the exclusion code when not matched."""
    d = domain.lower()
    if d in coi or any(d.endswith("." + c) for c in coi):
        return False, "coi"
    if d in EXCLUDED_HOSTS or any(d.endswith("." + h) for h in EXCLUDED_HOSTS):
        return False, "media-or-portal"
    if d.endswith(EXCLUDED_SUFFIXES):
        return False, "institutional-suffix"
    if not (TOKEN_RE.search(d) or SHORT_RE.search(d)):
        return False, "no-vertical-token"
    nm = name_part(d)
    if not (TOKEN_RE.search(nm) or SHORT_RE.search(nm)):
        return False, "suffix-position-only"
    if NEGATIVE_RE.search(d):
        return False, "negative-token"
    return True, ""


def stream_vertices():
    """Yield reversed-domain strings from the gzipped vertices file."""
    req = urllib.request.Request(VERTICES_URL, headers={"User-Agent": UA})
    resp = urllib.request.urlopen(req, timeout=300)
    dec = zlib.decompressobj(zlib.MAX_WBITS | 16)
    tail = b""
    while True:
        chunk = resp.read(1 << 20)
        if not chunk:
            break
        data = tail + dec.decompress(chunk)
        *lines, tail = data.split(b"\n")
        for ln in lines:
            parts = ln.split(b"\t")
            if len(parts) >= 2:
                yield parts[1].decode("utf-8", "ignore")
    if tail:
        parts = tail.split(b"\t")
        if len(parts) >= 2:
            yield parts[1].decode("utf-8", "ignore")


def cmd_scan():
    os.makedirs(ART, exist_ok=True)
    coi = load_coi_exclusions()
    reasons = Counter()
    matched = []
    n = 0
    for rev in stream_vertices():
        n += 1
        dom = unreverse(rev)
        ok, why = classify(dom, coi)
        if ok:
            matched.append(dom)
        else:
            reasons[why] += 1
        if n % 20_000_000 == 0:
            print(f"  scanned {n/1e6:.0f}M domains, {len(matched)} matched")

    matched.sort()
    with open(OUT_MATCHES, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["domain"])
        w.writerows([[d] for d in matched])

    summary = {
        "source": VERTICES_URL,
        "domains_scanned": n,
        "matched": len(matched),
        "match_rate": round(len(matched) / n, 8) if n else None,
        "matched_unrestricted": len(matched) + reasons.get(
            "suffix-position-only", 0),
        "frame_definition": ("registrable-name position only; see "
                             "protocol/amendments/amendment_3_f1_suffix_"
                             "position.md, which publishes both figures"),
        "excluded": {
            # 'no-vertical-token' is the overwhelming majority and is not an
            # exclusion in the protocol sense; it is simply non-membership.
            k: v for k, v in reasons.most_common()
        },
        "coi_exclusions_applied": reasons.get("coi", 0),
        "pattern": {
            "vertical_tokens": VERTICAL_TOKENS,
            "short_tokens": SHORT_TOKENS,
            "negative_tokens": NEGATIVE_TOKENS,
            "frozen_by": "protocol/amendments/amendment_2_f1_host_regex.md",
        },
        "caveats": [
            "F1 enumerates domains whose NAME carries a vertical token; a "
            "retail FX/CFD site with a non-descriptive domain is invisible to "
            "it. F1 is a name-pattern frame, not a census of the vertical.",
            "The employer and author-property exclusions are applied from an "
            "untracked local list; only the count is published, per protocol "
            "section 7.",
            "Matching a domain name says nothing about whether the site is "
            "Chinese-facing or carries a licence claim; both are established "
            "downstream by the keyless presence probe and the extractor.",
            "F1 is recall-oriented and imprecise by construction: the "
            "retained set still contains many domains unrelated to retail "
            "FX/CFD. Precision is supplied downstream, and the yield at each "
            "stage is published rather than the frame being tuned.",
        ],
    }
    with open(OUT_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("pattern", "caveats", "excluded")}, indent=2))
    print("top exclusion reasons:", reasons.most_common(6))
    return 0


def cmd_sample():
    if not os.path.exists(OUT_MATCHES):
        print("run --scan first")
        return 2
    doms = [r["domain"] for r in csv.DictReader(open(OUT_MATCHES, newline=""))]
    # Stratify by offshore jurisdiction where the F2 join supplies one.
    juris = {}
    if os.path.exists(F2):
        for r in csv.DictReader(open(F2, newline="")):
            site = (r.get("website") or "").lower()
            for d in doms:
                if d and d in site:
                    juris[d] = r.get("jurisdiction", "")
    strata = {}
    for d in doms:
        strata.setdefault(juris.get(d, "no offshore entity"), []).append(d)
    rng = random.Random(SEED)
    print("F1 strata:")
    for k, v in sorted(strata.items(), key=lambda x: -len(x[1])):
        print(f"  {k:<24} {len(v)}")
    print(f"\nseed {SEED}; cap {STRATUM_CAP:.0%} per stratum "
          f"(draw size is set at sampling time against the N=80 target)")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--scan", action="store_true")
    g.add_argument("--sample", action="store_true")
    a = p.parse_args()
    return cmd_scan() if a.scan else cmd_sample()


if __name__ == "__main__":
    raise SystemExit(main())
