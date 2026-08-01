#!/usr/bin/env python3
"""
frame_offshore.py — build sampling frame F2 (the spine) from offshore
securities-dealer registers.

Protocol reference: locked_protocol_v1.0.md section 4, frame F2. These
registers enumerate the *onboarding vehicles* directly — the entities that
actually contract with clients — which is why the protocol treats them as
the spine rather than starting from a brand list.

Section 4 defines F2 as "direct enumeration of offshore securities-dealer
registers (e.g. the Seychelles FSA capital-markets register)" and stratifies
the sample by offshore jurisdiction across "Seychelles / Vanuatu / Mauritius
/ BVI / Belize / SVG / no offshore entity". The Seychelles register is the
protocol's *example*, not its definition, so enumerating the other named
jurisdictions realises the frozen design rather than changing it. No
amendment is required and none is claimed.

Keyless throughout: plain HTTP against public register pages. Every fetch is
archived verbatim with a SHA-256 so a reviewer can reproduce the parse from
the same bytes. Parsers read the archived bytes, never the network.

Documented limitation (protocol section 6): most of these registers publish
no licence numbers. Recorded per row in `has_licence_number`, with the
identifier the register actually publishes (if any) in `identifier` /
`identifier_type` — a register-published *company* number presented on a
marketing page as a licence number is the protocol's B-mis-anchor sub-code,
so the distinction is load-bearing and is never flattened.

Privacy minimization (protocol section 7, rule 4: no private individuals as
units of analysis): the COMMITTED artifact contains institutional entities
only and carries no email and no appointee/officer column. Rows that are
named natural persons (the Seychelles register's representative categories;
any new-register licensee name carrying no legal-form suffix), all email
addresses and all appointee names are written only to a local file under
data/ (gitignored), and remain derivable byte-for-byte from the archives.

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
from html import unescape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "registers")
ART = os.path.join(ROOT, "artifacts", "frames")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 "
      "(academic research; contact via repository)")

# Public register endpoints. Each entry:
#   (key, url, jurisdiction, regulator, ext, pin)
# `ext` is the archive extension and records the rendering type actually
# retrieved: "html" for server-rendered pages, "json" for a public keyless
# JSON endpoint. `pin` names one archived snapshot to parse; None means "the
# newest archive for this key". Registers that could not be enumerated at all
# are NOT listed here; they are documented with their access failure in
# artifacts/frames/register_coverage.md.
REGISTERS = [
    # Pinned to the 2026-07-27 snapshot: every downstream artifact already
    # committed (the 162-domain Chinese-presence probe, the stage-2 claim
    # extraction, the stage-3 claim units and the stage-4 verification) was
    # built from these bytes, so re-pointing the frame at a fresher snapshot
    # would silently change the population underneath them. The 2026-08-01
    # re-fetch is archived beside it as a drift check and is reported in
    # register_coverage.md, not silently substituted.
    ("seychelles_securities_dealers",
     "https://fsaseychelles.sc/regulated-entities/capital-markets",
     "Seychelles", "Seychelles FSA", "html",
     "seychelles_securities_dealers_20260727T044232Z.html"),
    ("vanuatu_financial_dealers",
     "https://www.vfsc.vu/financial-dealers-licensee-list/",
     "Vanuatu", "Vanuatu FSC", "html", None),
    # Belize's public register front end is a JavaScript single-page app, but
    # it is backed by an unauthenticated public JSON listing endpoint on the
    # regulator's own host (discovered from the app's own
    # /assets/config/config.json). PageSize is set well above the current
    # record count so one archived response is the whole register; --parse
    # fails loudly if the register outgrows it.
    ("belize_fsc_licensees",
     "https://licensys.belizefsc.org.bz/api/pub/DynamicList"
     "?__meta__formId=6928049e24c807681185b908&Page=1&PageSize=500"
     "&SortBy=RegistrationObjectInfo.InitialRegistrationDate%20desc"
     "&IsCurrent=true",
     "Belize", "Belize FSC", "json", None),
    ("svg_mutual_funds",
     "https://fsasvg.com/docs/mutual-funds/",
     "SVG", "SVG FSA", "html", None),
]

# Auxiliary lookups archived alongside the registers (same manifest, same
# sha256 discipline). Not registers of entities; used only to decode codes
# that appear in a register payload.
AUX_SOURCES = [
    ("belize_fsc_licence_types",
     "https://licensys.belizefsc.org.bz/api/pub/classifiers/"
     "selectSearchByTranslation?ClassifierDomainNaturalIds=LMIS-LIC-TYPE"
     "&IsValid=true&SortBy=RowOrder%20asc&TranslationLanguage=EN"
     "&Page=1&PageSize=200",
     "json"),
]

REQUEST_PAUSE = 2.5     # politeness; these are small public pages
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
    targets = ([(k, u, j, r, e) for k, u, j, r, e, _p in REGISTERS]
               + [(k, u, "", "(auxiliary lookup)", e) for k, u, e in AUX_SOURCES])
    for key, url, juris, regulator, ext in targets:
        try:
            body = fetch(url)
        except Exception as exc:                      # noqa: BLE001
            print(f"FAILED {key}: {exc}")
            manifest.append({"key": key, "url": url, "status": "failed",
                             "error": str(exc), "fetched_utc": stamp})
            time.sleep(REQUEST_PAUSE)
            continue
        path = os.path.join(RAW, f"{key}_{stamp}.{ext}")
        with open(path, "wb") as f:
            f.write(body)
        digest = sha256_bytes(body)
        manifest.append({"key": key, "url": url, "jurisdiction": juris,
                         "regulator": regulator, "status": "ok",
                         "rendering": ext,
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


# Seychelles categories whose rows may appear in the committed artifact. That
# register carries its own category taxonomy, and its representative
# categories list named natural persons; per protocol section 7 rule 4 they
# stay local-only (see module docstring). Unknown category => excluded, which
# is the conservative direction.
INSTITUTIONAL_CATEGORIES = {
    "securities-dealer", "securities-exchange", "securities-facility",
    "clearing-agency", "investment-advisor",
}

# Registers that publish no category taxonomy separating companies from
# natural persons need a mechanical test. A licensee name carrying a legal
# form suffix is an institution; anything else is treated as possibly a
# natural person and kept local-only. Conservative by construction: a
# mis-classified company is merely omitted from the committed artifact, while
# a mis-classified person would breach protocol section 7 rule 4.
LEGAL_FORM_RE = re.compile(
    r"(?:^|[\s(.,&/-])("
    r"ltd|limited|ltda|inc|incorporated|corp|corporation|company|co|llc|l\.l\.c"
    r"|plc|pty|pte|llp|lllp|lp|ag|gmbh|s\.?a|s\.?a\.?r\.?l|b\.?v|n\.?v|a\.?g"
    r"|ibc|scc|spc|cell|foundation|trust|partners|holdings?|group|sdn|bhd"
    r")\.?(?:$|[\s(.,&/-])", re.I)


def looks_institutional(name):
    return bool(LEGAL_FORM_RE.search(" " + (name or "") + " "))


def clean_text(s):
    """Strip tags, collapse whitespace, unescape HTML entities.

    unescape() is applied to every extracted text field: entity names feed
    name-level B-vs-C matching (protocol section 6), so "&amp;" must become
    "&" before any comparison.
    """
    return unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _row(anchor="", entity_name="", website="", email="", appointees="",
         category="", identifier="", identifier_type="none", status="",
         in_dealer_frame=0, has_licence_number=0, institutional=1):
    return {"anchor": anchor, "entity_name": entity_name, "website": website,
            "email": email, "appointees": appointees, "category": category,
            "identifier": identifier, "identifier_type": identifier_type,
            "status": status, "in_dealer_frame": in_dealer_frame,
            "has_licence_number": has_licence_number,
            "institutional": institutional}


def latest_archive(ctx, key, ext, pin=None):
    """Archived file for `key` — parsers read bytes, never the network.

    `pin` selects one named snapshot; without it the newest archive wins.
    """
    if pin:
        p = os.path.join(ctx["raw"], pin)
        if not os.path.exists(p):
            raise SystemExit(f"{key}: pinned archive {pin} is missing")
        return p
    matches = [f for f in ctx["files"]
               if f.startswith(key + "_") and f.endswith("." + ext)]
    return os.path.join(ctx["raw"], matches[-1]) if matches else None


# ---------------------------------------------------------------- Seychelles

def parse_seychelles(text, ctx):
    """Extract (anchor, entity_name, website, email, category) per registrant.

    The register renders each registrant as a Bootstrap accordion card whose
    header button carries the entity name and whose `card-body` carries the
    address, phone, email and website. The website lives in an `<a href>`
    attribute, so a text-only parse silently loses it — parse the card blocks
    structurally instead. The `data-parent="#accordion-<category>"` attribute
    also carries the register category, which is worth keeping.

    Publishes no licence numbers (protocol section 6): has_licence_number = 0.
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

    for m in card_re.finditer(text):
        anchor, name_html, body = m.group(1), m.group(2), m.group(3)
        name = clean_text(name_html)
        if not name or len(name) > 160:
            continue

        website = email = ""
        for href in href_re.findall(body):
            h = unescape(href.strip())
            if h.lower().startswith("mailto:") and not email:
                email = h[7:]
            elif h.lower().startswith("tel:"):
                continue
            elif re.match(r"^(https?://|www\.)", h, re.I) and not website:
                website = h

        cm = cat_re.match(anchor)
        cat = cm.group(1) if cm else anchor
        rows.append(_row(anchor=anchor, entity_name=name, website=website,
                         email=email, category=cat,
                         in_dealer_frame=int(cat == "securities-dealer"),
                         has_licence_number=0,
                         institutional=int(cat in INSTITUTIONAL_CATEGORIES)))

    return dedup_on_anchor(rows)


def dedup_on_anchor(rows):
    """De-duplicate on the register's own unique per-entry key.

    Keying on entity name would wrongly merge distinct natural persons who
    share a name, and would silently drop genuine repeated register entries
    (the archived Seychelles snapshot lists one representative three times
    under three anchors). Rows with no register-supplied key are never
    merged — absence of a key is not evidence of duplication.
    """
    seen, out = set(), []
    for r in rows:
        a = r.get("anchor") or ""
        if a and a in seen:
            continue
        if a:
            seen.add(a)
        out.append(r)
    return out, len(rows)


# ------------------------------------------------------------------- Vanuatu

def parse_vanuatu(text, ctx):
    """VFSC Financial Dealers Licensee List — one server-rendered HTML table.

    Columns: Date of License | Company Number | Name of Licensee |
    Class Of License | License Status. The licence classes A/B/C are the
    Financial Dealers Licensing Act classes that cover FX and derivatives
    dealing, so every row is an onboarding-vehicle candidate.

    Two facts this register fixes, both load-bearing:
      * it publishes NO website field, so entity->brand mapping cannot be
        done from this register at all (it contributes no domains to the
        Chinese-presence probe);
      * the published identifier is a *Company Number*, not a licence
        number. A page displaying it as a "VFSC licence number" is the
        protocol's B-mis-anchor construct, so it is recorded as
        identifier_type="company-number" with has_licence_number = 0 rather
        than being flattened into a licence identifier.
    """
    m = re.search(r"<table.*?</table>", text, re.S | re.I)
    if not m:
        return [], 0
    rows = []
    trs = re.findall(r"<tr.*?</tr>", m.group(0), re.S | re.I)
    for tr in trs:
        cells = [clean_text(c) for c in
                 re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
        if len(cells) < 5:
            continue
        date, company_no, name, klass, status = cells[:5]
        if not name or name.lower().startswith("name of licensee"):
            continue        # header row
        rows.append(_row(anchor=company_no, entity_name=name, website="",
                         category="financial-dealer",
                         identifier=company_no,
                         identifier_type="company-number",
                         status=f"{status} (licensed {date}; class {klass})",
                         in_dealer_frame=1, has_licence_number=0,
                         institutional=int(looks_institutional(name))))
    return dedup_on_anchor(rows)


# -------------------------------------------------------------------- Belize

# Licence types that make the holder a securities-dealer-type onboarding
# vehicle. Codes, not labels, so a wording change upstream cannot silently
# reclassify rows. Custody/administration, audit, marketplace, clearing and
# the corporate-services licences are deliberately excluded.
BELIZE_DEALER_CODES = {
    "LIC-TYPE-L07",   # Money Broking
    "LIC-TYPE-L13",   # Trading in Commodity-Based & Financial Instruments
    "LIC-TYPE-S05",   # Trading in Securities as Agent
    "LIC-TYPE-S06",   # Trading in Securities as Principal
    "LIC-TYPE-S07",   # Managing Securities
    "LIC-TYPE-S08",   # Providing Investment Advice
    "LIC-TYPE-S09",   # Arranging Transactions in Securities
}


def _belize_type_map(ctx):
    """Code -> English label, from the archived classifier lookup."""
    path = latest_archive(ctx, "belize_fsc_licence_types", "json")
    if not path:
        return {}
    with open(path, "rb") as f:
        data = json.loads(f.read().decode("utf-8", errors="ignore"))
    out = {}
    for item in data if isinstance(data, list) else []:
        code = str(item.get("originalLabel", "")).split(".")[-1]
        if code:
            out[code] = item.get("label", code)
    return out


def parse_belize(text, ctx):
    """Belize FSC public register of licensed service providers (JSON).

    Unlike every other register in this frame, Belize publishes BOTH a
    licence number (`RegistrationObjectNumber`) and a website
    (`DomainName`) — so it supports number-level B-vs-C discrimination and
    entity->brand mapping at the same time. It also publishes an email
    address and appointee (officer) names; both are natural-person data and
    stay in the local file only.
    """
    payload = json.loads(text)
    data = payload.get("Data") or []
    total = payload.get("Total")
    if isinstance(total, int) and total > len(data):
        raise SystemExit(
            f"belize: archive holds {len(data)} of {total} records — raise "
            f"PageSize in REGISTERS and re-run --fetch (never paginate at "
            f"parse time; the parse must come from archived bytes)")

    types = _belize_type_map(ctx)
    rows = []
    for d in data:
        name = clean_text(str(d.get("LicenseeInfo.GeneralLicenseeName") or ""))
        if not name:
            continue
        codes = d.get("LicenceInfo.LicenceType.LicenceType") or ""
        codes = codes if isinstance(codes, list) else re.split(r"[,;]\s*", codes)
        codes = [c.strip() for c in codes if c and c.strip()]
        labels = [types.get(c, c) for c in codes]

        # Appointee names are natural persons; keep the names for the local
        # file only and never let them reach the committed artifact.
        appointees = ""
        raw_appo = d.get("Appointees")
        if raw_appo:
            try:
                appointees = "; ".join(
                    str(a.get("NameUnited", "")).strip()
                    for a in json.loads(raw_appo).get("LookupData", []))
            except Exception:                        # noqa: BLE001
                appointees = ""

        status = str(d.get("RegistrationObjectInfo.RegistrationObjectStatusId")
                     or "").replace("RR-STATUS-", "").lower()
        licence_no = clean_text(
            str(d.get("RegistrationObjectInfo.RegistrationObjectNumber") or ""))
        site = clean_text(str(d.get("LicenseeInfo.DomainName") or ""))
        rows.append(_row(
            anchor=str(d.get("__raw_data_id") or ""),
            entity_name=name,
            website=site,
            email=clean_text(str(d.get("LicenseeInfo.Email") or "")),
            appointees=appointees,
            category="; ".join(labels) or "unspecified",
            identifier=licence_no,
            identifier_type="licence-number" if licence_no else "none",
            status=status,
            in_dealer_frame=int(any(c in BELIZE_DEALER_CODES for c in codes)),
            has_licence_number=int(bool(licence_no)),
            institutional=int(looks_institutional(name))))
    return dedup_on_anchor(rows)


# ----------------------------------------------------------------------- SVG

def parse_svg(text, ctx):
    """SVG FSA licensed mutual-fund-sector entities (server-rendered tables).

    Recorded here for a negative reason that the study needs on the record:
    the SVG FSA licenses NO securities dealers. Its published licensed-entity
    categories are mutual funds, insurance and pensions, international banks,
    credit unions, money services and virtual assets — there is no
    securities-dealer or forex register to enumerate. That is exactly the
    condition behind the protocol's B-false-anchor sub-code (section 3), so
    the archived page is evidence, not filler.

    Consequence: every row here carries in_dealer_frame = 0. These entities
    are fund-sector licensees, not retail-FX onboarding vehicles, and a
    sample drawn from the dealer frame must filter on that column.
    """
    rows = []
    for tbl in re.findall(r"<table.*?</table>", text, re.S | re.I):
        for tr in re.findall(r"<tr.*?</tr>", tbl, re.S | re.I):
            cells = [clean_text(c) for c in
                     re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
            if len(cells) < 3:
                continue
            name, kind, status = cells[0], cells[1], cells[2]
            if not name or name.lower().startswith("name of mutual fund"):
                continue    # header row
            cat = re.sub(r"[^a-z0-9]+", "-", kind.lower()).strip("-")
            rows.append(_row(entity_name=name, website="",
                             category=cat or "mutual-fund",
                             status=status, in_dealer_frame=0,
                             has_licence_number=0,
                             institutional=int(looks_institutional(name))))
    # This register publishes no per-entry key, so no anchor-id dedup is
    # possible or attempted (see dedup_on_anchor).
    return dedup_on_anchor(rows)


PARSERS = {
    "seychelles_securities_dealers": parse_seychelles,
    "vanuatu_financial_dealers": parse_vanuatu,
    "belize_fsc_licensees": parse_belize,
    "svg_mutual_funds": parse_svg,
}

# Columns that exist only in the local parse. Both are natural-person data.
LOCAL_ONLY_FIELDS = ["email", "appointees"]

FULL_FIELDS = ["register", "jurisdiction", "regulator", "category",
               "register_anchor_id", "entity_name", "website",
               "email", "appointees",
               "identifier", "identifier_type", "status",
               "in_dealer_frame", "has_licence_number",
               "source_file", "source_sha256"]


def cmd_parse():
    os.makedirs(ART, exist_ok=True)
    if not os.path.isdir(RAW):
        print("no archives; run --fetch first")
        return 2
    files = sorted(os.listdir(RAW))
    ctx = {"raw": RAW, "files": files}
    out_rows = []
    per_register = []
    for key, _url, juris, regulator, ext, pin in REGISTERS:
        path = latest_archive(ctx, key, ext, pin)
        if not path:
            print(f"no archive for {key}")
            per_register.append((key, juris, 0, 0, 0))
            continue
        with open(path, "rb") as f:
            body = f.read()
        text = body.decode("utf-8", errors="ignore")
        rows, n_raw = PARSERS[key](text, ctx)
        latest = os.path.basename(path)
        for r in rows:
            out_rows.append({
                "register": key,
                "jurisdiction": juris,
                "regulator": regulator,
                "category": r["category"],
                "register_anchor_id": r["anchor"],
                "entity_name": r["entity_name"],
                "website": r["website"],
                "email": r["email"],
                "appointees": r["appointees"],
                "identifier": r["identifier"],
                "identifier_type": r["identifier_type"],
                "status": r["status"],
                "in_dealer_frame": r["in_dealer_frame"],
                # Protocol section 6: registers differ on whether a licence
                # number exists to check at all.
                "has_licence_number": r["has_licence_number"],
                "_institutional": r["institutional"],
                "source_file": latest,
                "source_sha256": sha256_bytes(body),
            })
        n_inst = sum(1 for r in rows if r["institutional"])
        # websites counted over COMMITTED rows only, so this line matches the
        # artifact rather than the wider local parse
        n_site = sum(1 for r in rows if r["institutional"] and r["website"])
        per_register.append((key, juris, len(rows), n_inst, n_site))
        print(f"{key}: {n_raw} raw entries, {len(rows)} after key dedup "
              f"({n_raw - len(rows)} duplicate keys), {n_inst} institutional, "
              f"{n_site} with a website — from {latest}")

    # Full parse (all rows, incl. email and appointee names) stays LOCAL under
    # data/ (gitignored) — derivable from the archives at any time.
    local_path = os.path.join(RAW, "frame_f2_full_local.csv")
    with open(local_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FULL_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
    print(f"\nlocal full parse (NOT committed): {local_path} "
          f"({len(out_rows)} rows)")

    # Committed artifact: institutional entities only, no email column and no
    # appointee column (protocol section 7 rule 4 — no private individuals as
    # units of analysis).
    committed_fields = [k for k in FULL_FIELDS if k not in LOCAL_ONLY_FIELDS]
    inst_rows = [{k: v for k, v in r.items() if k in committed_fields}
                 for r in out_rows if r["_institutional"]]
    path = os.path.join(ART, "frame_f2_offshore_registers.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=committed_fields)
        w.writeheader()
        w.writerows(inst_rows)

    n_dealer = sum(1 for r in inst_rows if r["in_dealer_frame"])
    n_number = sum(1 for r in inst_rows if r["has_licence_number"])
    with_site = sum(1 for r in inst_rows if r["website"])
    print(f"written: {path} ({len(inst_rows)} institutional rows; "
          f"{len(out_rows) - len(inst_rows)} rows local-only as possible "
          f"natural persons)")
    print(f"  in dealer frame (onboarding-vehicle candidates): {n_dealer}")
    print(f"  with a published licence number:                 {n_number}")
    print(f"  with a website recorded (entity->brand mapping): {with_site}"
          f" ({with_site / max(1, len(inst_rows)):.0%})")
    print("\nper register (rows / institutional / with website):")
    for key, juris, n, ni, ns in per_register:
        print(f"  {key:<32} {juris:<11} {n:>4} / {ni:>4} / {ns:>4}")
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
