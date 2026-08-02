#!/usr/bin/env python3
"""
probe_f1.py — Chinese-language presence probe for the F1 draw.

Protocol reference: locked_protocol_v1.0.md §4 (frame F1) with amendments 2-4.
Identical instrument to the F2 probe in frame_chinese.py — the keyless Common
Crawl CDX index, one query for Chinese-primary captures and one for captures
in any language — so the two frames' presence rates are directly comparable.

What this stage measures, and why it is the point: F1 is recall-oriented by
construction (amendment 3), so its precision is unknown until measured. The
yield here IS that measurement. It is published whatever it turns out to be;
the frame is not retuned in response to it.

Politeness: serial, >=1.1 s between queries, exponential backoff on 429/5xx,
per the Common Crawl FAQ. A failed query is never written, so a service error
can never be mistaken later for "checked, no Chinese pages".

Reads:  artifacts/frames/frame_f1_draw.csv
Writes: artifacts/frames/f1_presence_probe.jsonl   (append-only, resumable)
        artifacts/frames/f1_presence_summary.json
"""
import argparse
import csv
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts", "frames")
DRAW = os.path.join(ART, "frame_f1_draw.csv")
OUT = os.path.join(ART, "f1_presence_probe.jsonl")
SUMMARY = os.path.join(ART, "f1_presence_summary.json")

CC_INDEX = "CC-MAIN-2026-25"          # pinned in amendment 1
CC_URL = "https://index.commoncrawl.org/%s-index" % CC_INDEX
UA = ("licence-anchoring-research/1.0 (academic measurement; "
      "contact via github.com/nathanskill/licence-anchoring)")

PAUSE = 1.1
TIMEOUT = 90
MAX_RETRY = 5
BACKOFF = 25.0
ZHO_CAP = 200
ANY_CAP = 1000


def cc_query(domain, zho_only, limit):
    """Return (n_records, sample_urls); -1 signals a service failure."""
    params = {"url": domain, "matchType": "domain", "output": "json",
              "fl": "url,languages,status", "limit": str(limit)}
    url = "%s?%s&filter==status:200" % (CC_URL, urllib.parse.urlencode(params))
    if zho_only:
        url += "&filter=" + urllib.parse.quote("~languages:^zho")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(1, MAX_RETRY + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                body = r.read().decode("utf-8", errors="ignore")
            recs = []
            for line in body.splitlines():
                line = line.strip()
                if line:
                    try:
                        recs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            return len(recs), [x.get("url", "") for x in recs[:3]]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 0, []
            if e.code in (429, 500, 502, 503, 504):
                if attempt == MAX_RETRY:
                    return -1, ["HTTP %d after %d attempts" % (e.code, MAX_RETRY)]
                time.sleep(BACKOFF * attempt)
                continue
            return -1, ["HTTP %d" % e.code]
        except Exception as exc:                      # noqa: BLE001
            if attempt == MAX_RETRY:
                return -1, [str(exc)[:80]]
            time.sleep(BACKOFF * attempt)
    return -1, ["retries exhausted"]


def cmd_probe(limit_n):
    rows = list(csv.DictReader(open(DRAW, newline="")))
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                done.add(json.loads(line)["domain"])
            except Exception:                          # noqa: BLE001
                pass
    todo = [r for r in rows if r["domain"] not in done]
    if limit_n:
        todo = todo[:limit_n]
    print("%d in draw; %d done; %d to probe (~%.0f min)"
          % (len(rows), len(done), len(todo), len(todo) * 2 * PAUSE / 60))

    with open(OUT, "a") as out:
        for i, r in enumerate(todo, 1):
            d = r["domain"]
            n_zho, sample = cc_query(d, True, ZHO_CAP)
            time.sleep(PAUSE)
            if n_zho < 0:
                print("  [%d/%d] %s SERVICE FAILURE, not recorded"
                      % (i, len(todo), d))
                time.sleep(PAUSE)
                continue
            n_any, _ = cc_query(d, False, ANY_CAP)
            if n_any < 0:
                n_any = ""
            out.write(json.dumps({
                "domain": d, "stratum": r.get("stratum", ""),
                "crawl": CC_INDEX, "n_zho_captures_capped": n_zho,
                "n_captures_capped": n_any, "sample_zho_urls": sample}) + "\n")
            out.flush()
            if n_zho > 0 or i % 50 == 0:
                print("  [%d/%d] %-34s zho=%s any=%s%s"
                      % (i, len(todo), d, n_zho, n_any,
                         "  ZHO" if n_zho > 0 else ""))
            time.sleep(PAUSE)
    return cmd_summarise()


def cmd_summarise():
    if not os.path.exists(OUT):
        print("nothing probed yet")
        return 2
    recs = []
    for line in open(OUT):
        try:
            recs.append(json.loads(line))
        except Exception:                              # noqa: BLE001
            pass
    zho = [r for r in recs if r["n_zho_captures_capped"] > 0]
    by_str = Counter(r["stratum"] for r in recs)
    zho_by_str = Counter(r["stratum"] for r in zho)
    summary = {
        "crawl": CC_INDEX,
        "probed": len(recs),
        "with_chinese_presence": len(zho),
        "presence_rate": round(len(zho) / len(recs), 4) if recs else None,
        "by_stratum": {k: {"probed": v, "with_chinese": zho_by_str.get(k, 0)}
                       for k, v in by_str.items()},
        "domains_with_chinese": sorted(r["domain"] for r in zho),
        "caveats": [
            "The presence rate is the measured precision of frame F1 at this "
            "stage. F1 is recall-oriented by construction (amendment 3) and "
            "is not retuned in response to this number.",
            "Rates are not comparable across strata without care: the small "
            "strata are censused and the large one sampled (amendment 4).",
            "Capture tallies are capped CDX record counts, not unique page "
            "counts; only presence (n > 0) is used analytically.",
            "Service failures are not recorded, so absence in the file means "
            "not-yet-probed, never a silent failure.",
        ],
    }
    with open(SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("domains_with_chinese", "caveats")},
                     indent=2))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--probe", action="store_true")
    p.add_argument("--summarise", action="store_true")
    p.add_argument("--limit", type=int, default=0)
    a = p.parse_args()
    if a.probe:
        return cmd_probe(a.limit)
    return cmd_summarise()


if __name__ == "__main__":
    raise SystemExit(main())
