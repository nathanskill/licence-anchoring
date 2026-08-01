#!/usr/bin/env python3
"""
normalise_claims.py — stage 3 of REF-2026-019: turn raw extracted sentences
into codable claim units.

Protocol reference: locked_protocol_v1.0.md sections 3 and 6. The extractor
(stage 2) is recall-oriented and returns every claim-bearing sentence on
every archived page, so the same footer recurs across dozens of pages. The
unit of analysis is not the sentence but the CLAIM: a (brand, authority,
licence identifier, named holder entity) tuple. This stage deduplicates to
that unit and prepares the register-verification worksheet.

Nothing here codes A/B/C/D. Coding requires register verification (stage 4)
and the operative-entity determination (OE-1..3); this stage only produces
the units to be verified, plus the operative-entity candidates found on the
pages.

Reads:  artifacts/claims/claims_cc.jsonl
Writes: artifacts/claims/claim_units.csv          one row per claim unit
        artifacts/claims/operative_candidates.csv per-brand operative sentences
        artifacts/claims/normalisation_summary.json
"""
import csv
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts", "claims")
SRC = os.path.join(ART, "claims_cc.jsonl")

# Authority names as they appear in Chinese-language pages, mapped to the
# register that would verify them. Order matters: longer/more specific first.
AUTHORITIES = [
    ("FCA", r"FCA|金融行为监管局|英国金融行为监管局", "UK FCA Financial Services Register"),
    ("ASIC", r"ASIC|澳大利亚证券(?:与|和)投资委员会|澳洲证券投资委员会", "ASIC Professional Registers"),
    ("CySEC", r"CySEC|塞浦路斯证券(?:交易)?委员会", "CySEC regulated entities register"),
    ("FSC-MU", r"毛里求斯[^。\n]{0,12}金融服务委员会|Mauritius\s+FSC|FSC\s*\(?Mauritius", "Mauritius FSC Online Public Register"),
    ("FSA-SC", r"塞舌尔[^。\n]{0,12}金融服务管理局|Seychelles\s+FSA", "Seychelles FSA capital-markets register"),
    ("VFSC", r"VFSC|瓦努阿图[^。\n]{0,12}金融服务委员会", "Vanuatu FSC register"),
    ("LFSA", r"LFSA|纳闽[^。\n]{0,12}金融服务管理局|Labuan\s+FSA", "Labuan FSA financial institutions directory"),
    ("FSCA", r"FSCA|南非[^。\n]{0,12}金融行为监管局", "South Africa FSCA FSP register"),
    ("SCA-AE", r"阿联酋[^。\n]{0,12}(?:资本市场管理局|证券(?:与|和)商品管理局)|\bSCA\b|UAE\s+CMA", "UAE securities regulator register"),
    ("DFSA", r"DFSA|迪拜金融服务管理局", "DFSA public register"),
    ("CIMA", r"CIMA|开曼群岛金融管理局", "Cayman CIMA register"),
    ("FSA-SVG", r"圣文森特[^。\n]{0,20}(?:金融服务管理局|FSA)|SVG\s+FSA", "SVG FSA (note: does not license forex)"),
    ("BVI-FSC", r"BVI[^。\n]{0,12}金融服务委员会|英属维尔京群岛[^。\n]{0,12}金融服务委员会", "BVI FSC register"),
    ("FINRA-NFA", r"NFA|美国全国期货协会", "NFA BASIC register"),
    ("FSC-BZ", r"伯利兹[^。\n]{0,12}(?:国际)?金融服务委员会|Belize\s+FSC", "Belize FSC register"),
]

# Licence-identifier patterns, most specific first. Each yields (scheme, value).
ID_PATTERNS = [
    ("FRN", r"(?:FCA|FRN)[^0-9\n]{0,30}?(\d{6,7})\b"),
    ("AFSL", r"AFSL[^0-9\n]{0,12}(\d{5,7})\b"),
    ("CySEC", r"\b(\d{2,3}/\d{2})\b"),
    ("SD", r"\bSD\s*[#:/-]?\s*(\d{2,4})\b"),
    ("GB", r"\bGB\s*(\d{6,12})\b"),
    ("MB", r"\bMB\s*/\s*(\d{2}\s*/\s*\d{3,5})\b"),
    ("C-MU", r"\b(C\d{9,12})\b"),
    ("FSP", r"FSP[^0-9\n]{0,12}(\d{4,7})\b"),
    # Chinese pages commonly write "牌照编号为 X" / "许可证编号：X"; the
    # separator may be 为/是/:/：/whitespace, so all are admitted.
    ("GENERIC", r"(?:牌照|监管|许可证?|注册|授权)(?:编?号|号码)?[为是::\s]*([A-Z]{0,4}[\s#:/-]?\d{3,12})\b"),
]

ENTITY_RE = re.compile(
    r"([A-Z][A-Za-z0-9&.,'()\- ]{2,70}?"
    r"(?:LLC|Ltd|Limited|LP|LLP|Inc|Corp|Pty\s+Ltd|Pty)\.?"
    r"(?:\s*\((?:SC|SV|VC|BZ|MU|VU|CY|UK|AU|SA|EU|MENA|Seychelles|Mauritius|Cyprus|Australia|Global)\))?)")

OPERATIVE_RE = re.compile(
    r"(?:是|为)\s*([^。\n]{2,80}?)\s*(?:的交易名称|的商业名称|的注册商标|旗下品牌|经批准使用的交易名称)"
    r"|\btrading name of\s+([^.\n,;]{2,80})")


def norm_space(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def find_authority(text):
    for code, pat, register in AUTHORITIES:
        if re.search(pat, text, re.I):
            return code, register
    return "", ""


# When a bare number is found next to a named authority, the identifier
# scheme is implied by the authority even though the page does not spell it
# out (e.g. "受 ASIC 监管，监管牌照编号：374409" is an AFSL number).
AUTHORITY_SCHEME = {"ASIC": "AFSL", "FCA": "FRN", "FSCA": "FSP",
                    "FSA-SC": "SD", "FSC-MU": "GB", "LFSA": "MB"}


def find_identifier(text, authority=""):
    for scheme, pat in ID_PATTERNS:
        m = re.search(pat, text, re.I)
        if m:
            val = norm_space(m.group(1)).replace(" ", "")
            if scheme == "GENERIC" and authority in AUTHORITY_SCHEME:
                # Strip an authority acronym the generic pattern may have
                # swallowed (e.g. "ASIC374409" -> "374409").
                val = re.sub(r"^[A-Z]{2,5}(?=\d)", "", val)
                scheme = AUTHORITY_SCHEME[authority] + "?"
            return scheme, val
    return "", ""


def find_entity(text):
    m = ENTITY_RE.search(text)
    if not m:
        return ""
    ent = norm_space(m.group(1))
    # Drop leading connector words the regex may have swallowed.
    ent = re.sub(r"^(?:and|by|of|the|受|由)\s+", "", ent, flags=re.I)
    return ent if 4 <= len(ent) <= 80 else ""


def main():
    rows = [json.loads(l) for l in open(SRC)]

    # claim unit key -> record
    units = {}
    vague = defaultdict(dict)
    operatives = defaultdict(dict)
    pages_per_domain = defaultdict(set)

    for r in rows:
        dom = r["domain"]
        pages_per_domain[dom].add(r["url"])
        for h in r["claims"]:
            kind, text = h["kind"], norm_space(h["text"])

            if kind in ("operative_cn", "operative_en"):
                m = OPERATIVE_RE.search(text)
                holder = norm_space(m.group(1) or m.group(2)) if m else ""
                if holder:
                    key = (dom, holder.lower())
                    prev = operatives[dom].get(key)
                    operatives[dom][key] = {
                        "domain": dom, "named_operator": holder,
                        "sentence": text,
                        "n_pages": (prev["n_pages"] + 1) if prev else 1,
                        "example_url": prev["example_url"] if prev else r["url"],
                    }
                continue

            if kind not in ("regulated_cn", "regulated_en", "licence_no",
                            "fca_frn", "asic_afsl", "cysec_no", "offshore_reg"):
                continue

            auth, register = find_authority(text)
            scheme, ident = find_identifier(text, auth)
            entity = find_entity(text)
            if not auth and not ident:
                # Regulatory language naming no authority and no identifier
                # (e.g. "regulated by global authoritative regulators", or an
                # FAQ heading). Nothing to verify against any register; kept
                # as a separate, weaker category than anchor-no-number.
                if kind in ("regulated_cn", "regulated_en"):
                    vague[dom].setdefault(text, {"domain": dom,
                                                 "sentence": text[:280],
                                                 "n_pages": 0,
                                                 "example_url": r["url"]})
                    vague[dom][text]["n_pages"] += 1
                continue

            key = (dom, auth, scheme, ident, entity.lower())
            u = units.get(key)
            if u:
                u["n_pages"] += 1
            else:
                units[key] = {
                    "domain": dom, "authority": auth, "register": register,
                    "id_scheme": scheme, "identifier": ident,
                    "named_entity": entity, "n_pages": 1,
                    "example_sentence": text[:280], "example_url": r["url"],
                    "has_authority": int(bool(auth)),
                    "has_identifier": int(bool(ident)),
                    "has_entity": int(bool(entity)),
                }

    # A recall-oriented extractor emits overlapping fragments of the same
    # sentence, so the same claim can appear twice: once with the named
    # entity captured and once without. Merge on (domain, authority, scheme,
    # identifier), keeping the richer record.
    merged = {}
    for u in units.values():
        k = (u["domain"], u["authority"], u["id_scheme"].rstrip("?"),
             u["identifier"])
        prev = merged.get(k)
        if prev is None:
            merged[k] = u
        else:
            keep = prev if len(prev["named_entity"]) >= len(u["named_entity"]) else u
            drop = u if keep is prev else prev
            keep["n_pages"] = max(keep["n_pages"], drop["n_pages"])
            if not keep["id_scheme"].endswith("?"):
                pass
            elif not drop["id_scheme"].endswith("?"):
                keep["id_scheme"] = drop["id_scheme"]
            keep["has_entity"] = int(bool(keep["named_entity"]))
            merged[k] = keep
    units = merged

    os.makedirs(ART, exist_ok=True)
    out = sorted(units.values(),
                 key=lambda u: (u["domain"], u["authority"], u["identifier"]))
    with open(os.path.join(ART, "claim_units.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "domain", "authority", "register", "id_scheme", "identifier",
            "named_entity", "n_pages", "has_authority", "has_identifier",
            "has_entity", "example_sentence", "example_url"])
        w.writeheader()
        w.writerows(out)

    ops = [v for d in operatives.values() for v in d.values()]
    ops.sort(key=lambda o: (o["domain"], -o["n_pages"]))
    with open(os.path.join(ART, "operative_candidates.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=["domain", "named_operator",
                                          "n_pages", "sentence", "example_url"])
        w.writeheader()
        w.writerows(ops)

    vagues = [v for d in vague.values() for v in d.values()]
    vagues.sort(key=lambda v: (v["domain"], -v["n_pages"]))
    with open(os.path.join(ART, "vague_assertions.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=["domain", "n_pages", "sentence",
                                          "example_url"])
        w.writeheader()
        w.writerows(vagues)

    by_dom = defaultdict(int)
    for u in out:
        by_dom[u["domain"]] += 1
    complete = [u for u in out if u["has_authority"] and u["has_identifier"]]
    anchor_no_number = [u for u in out if u["has_authority"]
                        and not u["has_identifier"]]

    summary = {
        "source_pages": len(rows),
        "domains": len(pages_per_domain),
        "raw_sentences": sum(len(r["claims"]) for r in rows),
        "claim_units": len(out),
        "units_with_authority_and_identifier": len(complete),
        "units_authority_only": len(anchor_no_number),
        "vague_assertions": len(vagues),
        "domains_with_vague_only": len(
            {v["domain"] for v in vagues} - {u["domain"] for u in out}),
        "domains_with_operative_sentence": len(operatives),
        "operative_candidates": len(ops),
        "units_per_domain": dict(sorted(by_dom.items(),
                                        key=lambda kv: -kv[1])),
        "note": ("Claim units are (domain, authority, identifier scheme, "
                 "identifier, named entity) tuples deduplicated across pages; "
                 "n_pages records how many archived pages carried the unit. "
                 "No A/B/C/D coding is applied here: coding requires register "
                 "verification and the operative-entity determination "
                 "(protocol sections 5-6)."),
    }
    with open(os.path.join(ART, "normalisation_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in summary.items()
                      if k != "units_per_domain"}, indent=2,
                     ensure_ascii=False))
    print("\nunits per domain:")
    for d, n in sorted(by_dom.items(), key=lambda kv: -kv[1]):
        print(f"  {d:<24} {n}")


if __name__ == "__main__":
    main()
