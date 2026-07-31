#!/usr/bin/env python3
"""
frame_chinese.py — intersect frame F2 (offshore registrants) with frame F1
(Common Crawl Chinese-language corpus) to produce the study sample.

Protocol reference: locked_protocol_v1.0.md section 4. F2 enumerates the
onboarding vehicles; F1 tells us which of them maintain Chinese-language
pages. The intersection is the population of interest: offshore-registered
entities that market to Chinese-speaking readers.

Why the Common Crawl index rather than probing the brands directly: it is
keyless, it does not touch the brands' own servers at all, and it answers the
Chinese-presence question from a public archive. Direct collection happens
later and only for sampled brands, under the vantage-point rules in protocol
section 5.

Politeness: index.commoncrawl.org is a shared free service. The Common Crawl
FAQ asks for serial requests and no multithreading from one IP; a 503 means
slow down, and repeated abuse earns a 24h IP block. One request per second,
single-threaded, with backoff.

Usage:
    python3 src/frame_chinese.py --probe        # query CC index per domain
    python3 src/frame_chinese.py --summarise    # build the sample frame
"""
import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts", "frames")
F2 = os.path.join(ART, "frame_f2_offshore_registers.csv")
PROBE_OUT = os.path.join(ART, "cc_chinese_probe.jsonl")
SAMPLE_OUT = os.path.join(ART, "frame_sample_chinese_offshore.csv")

# Frozen at protocol freeze: the crawl queried for Chinese presence.
CC_INDEX = "CC-MAIN-2026-25"
CC_URL = "https://index.commoncrawl.org/%s-index" % CC_INDEX

UA = ("licence-anchoring-research/1.0 (academic measurement; "
      "contact via github.com/nathanskill/licence-anchoring)")

PAUSE = 1.1          # >= 1 req/s per Common Crawl FAQ
TIMEOUT = 90
MAX_RETRY = 3
BACKOFF = 20.0


def domain_of(url):
    u = re.sub(r"^https?://", "", (url or "").strip().lower())
    u = re.sub(r"^www\.", "", u)
    return u.split("/")[0].split("?")[0]


def cc_query(domain, zho_only=True, limit=200):
    """Query the CC index for a domain. Returns (n_records, sample_urls).

    `filter=~languages:^zho` selects pages whose PRIMARY language is Chinese.
    The languages field is regex-filterable server-side, so this costs one
    request per domain rather than a bulk download.
    """
    params = {
        "url": domain,
        "matchType": "domain",
        "output": "json",
        "fl": "url,languages,status",
        "limit": str(limit),
    }
    qs = urllib.parse.urlencode(params)
    filters = "&filter==status:200"
    if zho_only:
        filters += "&filter=" + urllib.parse.quote("~languages:^zho")
    url = f"{CC_URL}?{qs}{filters}"

    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(1, MAX_RETRY + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                body = r.read().decode("utf-8", errors="ignore")
            recs = []
            for line in body.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    recs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            return len(recs), [x.get("url", "") for x in recs[:5]]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 0, []            # no captures for this domain
            if e.code in (429, 503):
                time.sleep(BACKOFF * attempt)
                continue
            return -1, [f"HTTP {e.code}"]
        except Exception as exc:        # noqa: BLE001
            if attempt == MAX_RETRY:
                return -1, [str(exc)[:80]]
            time.sleep(BACKOFF * attempt)
    return -1, ["retries exhausted"]


def cmd_probe():
    rows = list(csv.DictReader(open(F2, newline="")))
    domains = sorted({domain_of(r["website"]) for r in rows if r["website"]})
    domains = [d for d in domains if d and "." in d]

    done = set()
    if os.path.exists(PROBE_OUT):
        with open(PROBE_OUT) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["domain"])
                except Exception:       # noqa: BLE001
                    pass
    todo = [d for d in domains if d not in done]
    print(f"{len(domains)} domains in F2; {len(done)} already probed; "
          f"{len(todo)} to go (~{len(todo) * PAUSE / 60:.0f} min)")

    with open(PROBE_OUT, "a") as out:
        for i, d in enumerate(todo, 1):
            n_zho, sample = cc_query(d, zho_only=True)
            time.sleep(PAUSE)
            n_all, _ = cc_query(d, zho_only=False, limit=1000)
            rec = {"domain": d, "crawl": CC_INDEX,
                   "n_zho_pages": n_zho, "n_pages_any_lang": n_all,
                   "sample_zho_urls": sample}
            out.write(json.dumps(rec) + "\n")
            out.flush()
            flag = "ZHO" if n_zho > 0 else ("err" if n_zho < 0 else "-")
            print(f"[{i}/{len(todo)}] {d:<34} zho={n_zho:<5} any={n_all:<5} {flag}")
            time.sleep(PAUSE)
    return 0


def cmd_summarise():
    if not os.path.exists(PROBE_OUT):
        print("no probe output; run --probe first")
        return 2
    probes = {}
    with open(PROBE_OUT) as f:
        for line in f:
            try:
                r = json.loads(line)
                probes[r["domain"]] = r
            except Exception:           # noqa: BLE001
                pass

    f2 = list(csv.DictReader(open(F2, newline="")))
    by_domain = {}
    for r in f2:
        d = domain_of(r["website"])
        if d:
            by_domain.setdefault(d, []).append(r)

    rows = []
    for d, p in sorted(probes.items()):
        ents = by_domain.get(d, [])
        rows.append({
            "domain": d,
            "n_zho_pages": p["n_zho_pages"],
            "n_pages_any_lang": p["n_pages_any_lang"],
            "has_chinese_presence": int(p["n_zho_pages"] > 0),
            "n_register_entities": len(ents),
            "register_entities": " | ".join(
                e["entity_name"] for e in ents)[:400],
            "jurisdiction": ents[0]["jurisdiction"] if ents else "",
            "sample_zho_url": (p.get("sample_zho_urls") or [""])[0],
        })

    with open(SAMPLE_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    zho = [r for r in rows if r["has_chinese_presence"]]
    err = [r for r in rows if r["n_zho_pages"] < 0]
    print(f"written: {SAMPLE_OUT}")
    print(f"domains probed:            {n}")
    print(f"with Chinese-language pages: {len(zho)} "
          f"({len(zho) / max(1, n - len(err)):.0%} of successfully probed)")
    print(f"probe errors:              {len(err)}")
    print("\ntop by Chinese page count:")
    for r in sorted(zho, key=lambda x: -x["n_zho_pages"])[:15]:
        print(f"  {r['domain']:<32} {r['n_zho_pages']:>4} zho pages   "
              f"{r['register_entities'][:52]}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--probe", action="store_true")
    g.add_argument("--summarise", action="store_true")
    a = p.parse_args()
    return cmd_probe() if a.probe else cmd_summarise()


if __name__ == "__main__":
    raise SystemExit(main())
