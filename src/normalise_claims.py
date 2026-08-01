#!/usr/bin/env python3
"""
normalise_claims.py — stage 3 of REF-2026-019: turn raw extracted sentences
into codable claim units.

Protocol reference: locked_protocol_v1.0.md sections 3, 5, 6 and 8. The
extractor (stage 2) is recall-oriented and returns every claim-bearing
sentence on every archived page, so the same footer recurs across dozens of
pages. The unit of analysis is not the sentence but the CLAIM: a statement
the page makes about the regulatory status of the operator or its group,
reduced to a (brand, authority, licence identifier, named holder entity)
tuple.

Nothing here codes A/B/C/D. Coding requires register verification (stage 4)
and the operative-entity determination (OE-1..3); this stage only produces
the units to be verified, the operative-entity candidates found on the
pages, and an auditable record of every sentence the self-reference filter
removed.

Three corrections applied at this revision, each reported separately in the
summary so their yields are not conflated:

  FIX 1 — same-sentence identifier pairing. The Chinese identifier pattern
  admitted the separator characters 为 / 是 / ASCII colon, and the ASCII
  colon was written twice where the FULLWIDTH colon U+FF1A was intended.
  Chinese pages overwhelmingly write "牌照编号：374409" with the fullwidth
  colon, so every identifier introduced that way failed to pair with the
  authority named in the same sentence, and the unit was recorded as an
  authority with no number while the number sat a few characters away.
  English introducers ("licence number", "company number") were also absent.

  FIX 2 — self-reference filter (protocol §5: the unit of analysis is a
  statement about the regulatory status of the operator or its group). The
  corpus includes blog, academy, education and comparison pages, whose
  sentences were entering the frame: reader advice, conditionals, questions,
  third-party comparisons and definitions are not claims about the operator.
  Every predicating sentence is now tested and its decision recorded; the
  excluded and queued sentences are written to
  artifacts/claims/excluded_non_self_referential.csv so the exclusion rate is
  inspectable. Page type is recorded from URL path but is NEVER used to
  exclude — a footer claim on a blog page is still a claim, and the split is
  reported instead.

  FIX 3 — completeness is no longer a single boolean. "The page names an
  authority and publishes no number anywhere" (protocol §3 sub-code
  `anchor-no-number`, a codeable observation) is a different fact from "the
  number is on the page but in another sentence" and from "the extractor's
  window cut the number off". Those three now have distinct values.

Reads:  artifacts/claims/claims_cc.jsonl
Writes: artifacts/claims/claim_units.csv                    one row per claim unit
        artifacts/claims/excluded_non_self_referential.csv   filter audit trail
        artifacts/claims/operative_candidates.csv            per-brand operative sentences
        artifacts/claims/vague_assertions.csv                self-referential but unverifiable
        artifacts/claims/normalisation_summary.json
"""
import csv
import json
import os
import re
import urllib.parse
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts", "claims")
SRC = os.path.join(ART, "claims_cc.jsonl")

FW_COLON = "："          # ：  U+FF1A
FW_EQUALS = "＝"         # ＝  U+FF1D

# Authority names as they appear in Chinese-language pages, mapped to the
# register that would verify them. Order matters: longer/more specific first.
AUTHORITIES = [
    ("FCA", r"FCA|金融行为监管局|英国金融行为监管局", "UK FCA Financial Services Register"),
    ("ASIC", r"ASIC|澳大利亚证券(?:与|和)投资委员会|澳洲证券投资委员会", "ASIC Professional Registers"),
    ("CySEC", r"CySEC|塞浦路斯证券(?:交易)?委员会", "CySEC regulated entities register"),
    ("FSC-MU", r"毛里求斯[^。\n]{0,12}金融服务委员会|Mauritius\s+FSC|FSC\s*\(?Mauritius", "Mauritius FSC Online Public Register"),
    # FIX 1b: the English long forms of the Seychelles authority were absent,
    # so sentences that named the authority and the SD number together were
    # recorded as an identifier with no authority.
    ("FSA-SC", r"塞舌尔[^。\n]{0,12}金融服务管理局|Seychelles\s+FSA"
               r"|Financial\s+Services\s+Authority\s+of\s+Seychelles"
               r"|Seychelles\s+Financial\s+Services\s+Authority", "Seychelles FSA capital-markets register"),
    ("VFSC", r"VFSC|瓦努阿图[^。\n]{0,12}金融服务委员会", "Vanuatu FSC register"),
    ("LFSA", r"LFSA|纳闽[^。\n]{0,12}金融服务管理局|Labuan\s+FSA", "Labuan FSA financial institutions directory"),
    ("FSCA", r"FSCA|南非[^。\n]{0,12}金融行为监管局", "South Africa FSCA FSP register"),
    # FIX 1b: pages write the UAE regulator's full Chinese name
    # (阿拉伯联合酋长国证券与商品管理局) as often as the abbreviation.
    ("SCA-AE", r"阿联酋[^。\n]{0,12}(?:资本市场管理局|证券(?:与|和)商品管理局)"
               r"|阿拉伯联合酋长国[^。\n]{0,12}证券(?:与|和)商品管理局"
               r"|\bSCA\b|UAE\s+CMA", "UAE Securities and Commodities Authority register"),
    ("DFSA", r"DFSA|迪拜金融服务管理局", "DFSA public register"),
    ("CIMA", r"CIMA|开曼群岛金融管理局", "Cayman CIMA register"),
    ("FSA-SVG", r"圣文森特[^。\n]{0,20}(?:金融服务管理局|FSA)|SVG\s+FSA", "SVG FSA (note: does not license forex)"),
    ("BVI-FSC", r"BVI[^。\n]{0,12}金融服务委员会|英属维尔京群岛[^。\n]{0,12}金融服务委员会", "BVI FSC register"),
    ("FINRA-NFA", r"NFA|美国全国期货协会", "NFA BASIC register"),
    ("FSC-BZ", r"伯利兹[^。\n]{0,12}(?:国际)?金融服务委员会|Belize\s+FSC", "Belize FSC register"),
]

# Separator between an identifier-introducing phrase and the identifier.
# FIX 1: the fullwidth colon U+FF1A is the normal Chinese form and was the
# character the previous class was meant to carry; it had been typed as a
# second ASCII colon.
SEP = r"[为是:" + FW_COLON + r"=" + FW_EQUALS + r"\s]*"
NUM = r"([A-Z]{0,4}[\s#:/-]?\d{3,12})\b"

# Licence-identifier patterns, most specific first. Each yields (scheme, value).
# Patterns whose scheme appears in COMPANY_SCHEMES capture a company-registry
# number rather than a licence number; the distinction is carried into the
# output because a company number displayed in a licence-number position is
# the protocol §3 sub-code B-mis-anchor, and must never be silently counted
# as a licence identifier.
ID_PATTERNS = [
    ("FRN", r"(?:FCA|FRN)[^0-9\n]{0,30}?(\d{6,7})\b"),
    ("AFSL", r"AFSL[^0-9\n]{0,12}(\d{5,7})\b"),
    ("CySEC", r"\b(\d{2,3}/\d{2})\b"),
    ("SD", r"\bSD\s*[#:/-]?\s*(\d{2,4})\b"),
    ("GB", r"\bGB\s*(\d{6,12})\b"),
    ("MB", r"\bMB\s*/\s*(\d{2}\s*/\s*\d{3,5})\b"),
    ("C-MU", r"\b(C\d{9,12})\b"),
    ("FSP", r"FSP[^0-9\n]{0,12}(\d{4,7})\b"),
    # Chinese pages write "牌照编号：X" / "许可证号为 X" / "监管牌照编号：X".
    ("CN-LIC", r"(?:牌照|执照|许可证?|授权|监管)(?:编?号|号码)?" + SEP + NUM),
    ("EN-LIC", r"\blicen[cs]e\s*(?:number|no\.?|#)\s*[:" + FW_COLON + r"]?\s*" + NUM),
    # Company-registry numbers. Kept, but labelled.
    ("CN-REG", r"(?:注册|登记)(?:编?号|号码)?" + SEP + NUM),
    ("EN-COMPANY", r"\bcompany\s+(?:registration\s+)?number\s*[:" + FW_COLON + r"]?\s*(\d{3,12})\b"),
    ("EN-REG", r"\bregistration\s+(?:number|no\.?)\s*[:" + FW_COLON + r"]?\s*" + NUM),
]

COMPANY_SCHEMES = {"CN-REG", "EN-COMPANY", "EN-REG"}

# An identifier-introducing phrase with nothing after it: the stage-2
# extraction window (300 chars) cut the number off. This is a third, distinct
# state from "number paired" and "no number on the page".
TRUNCATED_RE = re.compile(
    r"(?:Licen[cs]e\s*(?:No\.?|Number)|Financial\s+Services\s+Licen[cs]e"
    r"|牌照(?:编?号|号码)?|许可证?(?:编?号|号码)?|注册号|编号|FRN|AFSL|FSP)"
    r"\s*[:" + FW_COLON + r"]?\s*$", re.I)

ENTITY_RE = re.compile(
    r"([A-Z][A-Za-z0-9&.,'()\- ]{2,70}?"
    r"(?:\(Pty\)\s*Ltd|Pty\.?\s*Ltd|L\.L\.C|LLC|Limited|Ltd|LLP|LP|Inc|Corp|Pty)\.?"
    r"(?:\s*\((?:SC|SV|VC|BZ|MU|VU|CY|UK|AU|SA|EU|MENA|Seychelles|Mauritius|Cyprus|Australia|Global)\))?)")

OPERATIVE_RE = re.compile(
    r"(?:是|为)\s*([^。\n]{2,80}?)\s*(?:的交易名称|的商业名称|的注册商标|旗下品牌|经批准使用的交易名称)"
    r"|\btrading name of\s+([^.\n,;]{2,80})")

# --------------------------------------------------------------------------
# Self-reference test (protocol §5). A sentence qualifies as a claim only if
# it predicates regulatory status OF THE OPERATOR OR ITS GROUP.
# --------------------------------------------------------------------------

# The regulatory predicate itself, and where it starts in the sentence. An
# entity名 that sits AFTER 受 is in the agent slot (the regulator), not the
# subject slot, so it does not make the sentence self-referential.
PREDICATE_RE = re.compile(
    r"受(?=[^。\n]{0,60}?(?:监管|授权|许可|管理))"
    r"|\b(?:regulated|authori[sz]ed|licen[cs]ed|registered)\s+(?:and\s+\w+\s+)?(?:by|with|in)\b",
    re.I)

FIRST_PERSON_RE = re.compile(r"我们|我司|本公司|本网站|本集团|敝公司|\bwe\s+(?:are|hold)\b|\bour\s+(?:company|firm)\b", re.I)

OPERATIVE_CONSTRUCTION_RE = re.compile(
    r"的交易名称|的商业名称|的注册商标|旗下品牌|经批准使用的交易名称|\btrading name of\b|\bas\s+[A-Z][\w ]{2,40}\s+is\s+a\s+registered\b",
    re.I)

# Looser than ENTITY_RE: used ONLY to decide whether a named legal entity
# occupies the subject slot. It admits continental legal forms (SA, S.A.,
# GmbH, Pte Ltd) that the identifier-bearing ENTITY_RE deliberately does not,
# because a looser pattern there would corrupt the named_entity field.
SUBJECT_ENTITY_RE = re.compile(
    r"[A-Z][A-Za-z0-9&.,'()\- ]{2,70}?"
    r"(?:\(Pty\)\s*Ltd|Pty\.?\s*Ltd|Pte\.?\s*Ltd|L\.L\.C|LLC|Limited|Ltd|LLP|LP"
    r"|Inc|Corp|GmbH|N\.V\.|B\.V\.|S\.A\.|SA|Pty)(?=[\s,.，。)（）]|$)")

# Exclusion triggers. HARD triggers defeat every inclusion signal except the
# two decisive ones (SR-1 named entity in subject slot, SR-3 trading-name
# construction) — a question or a piece of reader advice is not a claim about
# the operator even when the operator's own brand appears in it. SOFT
# triggers describe a third-party or generic subject and are therefore
# overridden by any self-reference signal.
HARD_EXCLUSIONS = [
    ("question", re.compile(r"[?？]|吗[?？]?$|呢[?？]?$")),
    ("reader-advice", re.compile(
        r"提示\s*\d|温馨提示|建议您|建议投资者|务必|请务必|应该|应当|需要注意|注意事项"
        r"|如何选择|选择.{0,6}时|确保您|寻找一个|寻找一家|核实|检查您的|您应该|您可以检查"
        r"|\btip\s*\d|\byou\s+should\b|\bmake\s+sure\b|\bensure\s+that\b|\balways\s+check\b")),
    ("conditional", re.compile(r"如果|倘若|若[^干]|是否|\bwhether\b|\bif\s+you\b")),
    ("negated-regulation", re.compile(r"不受[^。\n]{0,20}(?:监管|管辖)|未受[^。\n]{0,20}监管|\bnot\s+regulated\b", re.I)),
    ("definition", re.compile(r"什么是|何谓|是指|指的是|定义为|的流程$|是一种")),
]
SOFT_EXCLUSIONS = [
    ("generic-class-subject", re.compile(
        r"通常|一般来说|大多|大部分|多数|往往|普遍"
        r"|受[^。\n]{0,30}(?:监管|授权|许可)的(?:经纪商|平台|机构|券商|公司|交易商|中介商|经纪人)"
        r"|(?:这个|该|此)(?:经纪商|平台|券商|交易商|机构)"
        r"|与信誉良好")),
    ("anaphoric-third-party", re.compile(r"^[^。\n]{0,12}它|因为它|他们的|其严肃性")),
]

# Third-party subject markers that block SR-4: if the sentence hands the
# subject slot to someone other than the operator, a licence number in it is
# not the operator's claim.
THIRD_PARTY_SUBJECT_RE = re.compile(
    r"^[^。\n]{0,12}它|因为它|(?:这个|该|此)(?:经纪商|平台|券商|交易商|机构)|竞争对手|其他经纪商")

# URL path heuristics. Page type is RECORDED, never used to exclude: a
# site-wide footer claim rendered on a blog page is still a claim about the
# operator. The split is reported so a reader can separate a claim on a terms
# page from a mention in a blog post.
PAGE_TYPE_RULES = [
    ("legal-or-corporate", (
        "/legal", "/terms", "/term-", "/about", "/company", "/regulation",
        "/regulatory", "/disclaimer", "/policy", "/policies", "/privacy",
        "/documents", "/aml", "/compliance", "/client-agreement", "/contact",
        "/risk-", "/risk-disclosure", "/licence", "/license", "/who-we-are",
        "/订单执行政策", "/公司和牌照")),
    ("editorial", (
        "/blog", "/news", "/academy", "/education", "/learn", "/category",
        "/tag/", "/analysis", "/knowledge-base", "/help-center", "/helpcenter",
        "/infocentre", "/info-centre", "/posts", "/courses", "/insights",
        "/article", "/market-news", "/glossary", "/faq", "/people",
        "/currency-converter", "/tools", "/forex/")),
    ("product-or-account", (
        "/accounts", "/account", "/products", "/platforms", "/platform",
        "/trading-markets", "/markets", "/invest", "/partners", "/promo",
        "/services", "/spreads", "/pricing")),
]


def norm_space(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def brand_tokens(domain):
    """Tokens that count as the brand naming itself, derived from the host."""
    stem = domain.split(".")[0]
    toks = {stem}
    # fusionmarkets -> "fusion markets"; m4markets -> "m4 markets"
    for word in ("markets", "market", "brokers", "broker", "trade", "trading",
                 "invest", "investing", "capital", "prime", "west", "quo",
                 "centrum"):
        if stem.endswith(word) and len(stem) > len(word):
            toks.add(stem[:-len(word)] + " " + word)
        if stem.startswith(word) and len(stem) > len(word):
            toks.add(word + " " + stem[len(word):])
    toks.add(re.sub(r"[^a-z0-9]", "", stem))
    return {t for t in toks if len(t) >= 2}


def page_type(url):
    path = urllib.parse.unquote(urllib.parse.urlparse(url).path or "").lower()
    if path.strip("/") == "" :
        return "home"
    # Strip a leading locale segment so "/zh-hans/about-zfx/" reads as legal.
    probe = path if path.startswith("/") else "/" + path
    for label, needles in PAGE_TYPE_RULES:
        if any(n in probe for n in needles):
            return label
    return "other"


def find_authority(text):
    for code, pat, register in AUTHORITIES:
        if re.search(pat, text, re.I):
            return code, register
    return "", ""


# When a bare number is found next to a named authority, the identifier
# scheme is implied by the authority even though the page does not spell it
# out (e.g. "受 ASIC 监管，监管牌照编号：374409" is an AFSL number).
AUTHORITY_SCHEME = {"ASIC": "AFSL", "FCA": "FRN", "FSCA": "FSP",
                    "FSA-SC": "SD", "FSC-MU": "GB", "LFSA": "MB",
                    "CySEC": "CySEC"}

# Which identifier schemes could belong to which authority. Used only to
# decide whether a number sitting elsewhere on the same page could be THIS
# authority's number: an SD number on a page also naming ASIC is not an
# unpaired ASIC identifier, it is a different authority's number, and the
# ASIC claim on that page genuinely carries no number.
UNATTRIBUTED_SCHEMES = {"CN-LIC", "EN-LIC"}

# Prefix carried into the stable claim id where the register's identifier
# series is written with one.
SCHEME_PREFIX = {"SD": "SD", "GB": "GB", "MB": "MB", "FSP": "FSP", "C-MU": ""}


def find_identifier(text, authority=""):
    """Return (scheme, value, kind) for the first identifier in the sentence.

    kind is 'licence-number' or 'company-registry-number'. The two are
    reported separately: a company-registry number displayed where a licence
    number belongs is a codeable observation (§3 B-mis-anchor), not an
    identifier that can be looked up in a licence register.
    """
    for scheme, pat in ID_PATTERNS:
        m = re.search(pat, text, re.I)
        if m:
            val = norm_space(m.group(1)).replace(" ", "")
            kind = ("company-registry-number" if scheme in COMPANY_SCHEMES
                    else "licence-number")
            if scheme in ("CN-LIC", "EN-LIC") and authority in AUTHORITY_SCHEME:
                # Strip an authority acronym the generic pattern may have
                # swallowed (e.g. "ASIC374409" -> "374409").
                val = re.sub(r"^[A-Z]{2,5}(?=\d)", "", val)
                scheme = AUTHORITY_SCHEME[authority] + "?"
            return scheme, val, kind
    return "", "", ""


def find_entity(text):
    m = ENTITY_RE.search(text)
    if not m:
        return ""
    ent = norm_space(m.group(1))
    ent = re.sub(r"^(?:and|by|of|the|受|由)\s+", "", ent, flags=re.I)
    return ent if 4 <= len(ent) <= 80 else ""


def self_reference(text, domain, identifier=""):
    """Apply the protocol §5 unit-of-analysis test to one sentence.

    Returns (decision, basis) where decision is 'include', 'exclude' or
    'queue'. 'queue' means a human decides: the sentence carries neither a
    decisive self-reference signal nor a decisive exclusion signal, and the
    protocol forbids auto-including it.
    """
    pred = PREDICATE_RE.search(text)

    # SR-3: the operative / trading-name construction is self-referential by
    # definition under §5 step 1, and outranks every exclusion trigger.
    if OPERATIVE_CONSTRUCTION_RE.search(text):
        return "include", "SR-3 operative/trading-name construction"

    # SR-1: a named legal entity in the SUBJECT slot of a regulatory
    # predicate. The entity must start before the predicate marker; an entity
    # after 受 is the regulator being named, not the regulated party.
    ent_m = SUBJECT_ENTITY_RE.search(text)
    if ent_m and pred and ent_m.start() < pred.start():
        return "include", f"SR-1 named legal entity in subject slot ({norm_space(ent_m.group(0))[:60]})"

    for code, pat in HARD_EXCLUSIONS:
        if pat.search(text):
            return "exclude", code

    # SR-2: the brand names itself, or speaks in the first person.
    low = text.lower()
    squashed = re.sub(r"[^a-z0-9]", "", low)
    for tok in brand_tokens(domain):
        if tok in low or (len(tok) >= 4 and tok.replace(" ", "") in squashed):
            return "include", f"SR-2 brand self-reference ({tok})"
    if FIRST_PERSON_RE.search(text):
        return "include", "SR-2 first-person self-reference"

    # SR-4: subject-elided operator footer. Chinese footers routinely drop the
    # subject — "受毛里求斯金融服务委员会 (FSC) 监管，牌照编号为：GB25204845" — but a
    # sentence that both predicates regulation AND states a specific licence
    # identifier, with no third party in the subject slot, is a statement
    # about the operator. Reader advice, comparisons and definitions do not
    # carry the operator's own licence number; the hard exclusions above have
    # already removed those forms.
    if pred and identifier and not THIRD_PARTY_SUBJECT_RE.search(text):
        return "include", "SR-4 subject-elided operator footer (regulatory predicate + own licence identifier)"

    for code, pat in SOFT_EXCLUSIONS:
        if pat.search(text):
            return "exclude", code

    if pred:
        return "queue", "no decisive self-reference signal; manual decision required"
    return "queue", "no regulatory predication detected"


def claim_id(domain, authority, scheme, identifier):
    brand = domain.split(".")[0]
    auth = (authority or "NOAUTH").replace("-", "")
    if not identifier:
        return f"{brand}-{auth}-nonumber"
    base = scheme.rstrip("?")
    prefix = SCHEME_PREFIX.get(base, "")
    ident = identifier
    if prefix and not ident.upper().startswith(prefix):
        ident = prefix + ident
    return f"{brand}-{auth}-{ident.replace('/', '-')}"


# --------------------------------------------------------------------------
# Ablation. The pre-fix patterns are kept here verbatim so the yield of each
# correction is recomputed from the corpus every run rather than asserted in
# prose. PRE_FIX_GENERIC is the exact string that shipped before: note the
# separator class [为是::\s], in which the ASCII colon appears twice and the
# fullwidth colon U+FF1A — the character Chinese pages actually use — never.
# --------------------------------------------------------------------------
PRE_FIX_GENERIC = ("GENERIC", r"(?:牌照|监管|许可证?|注册|授权)(?:编?号|号码)?"
                              r"[为是::\s]*([A-Z]{0,4}[\s#:/-]?\d{3,12})\b")
PRE_FIX_FSA_SC = r"塞舌尔[^。\n]{0,12}金融服务管理局|Seychelles\s+FSA"
PRE_FIX_SCA_AE = (r"阿联酋[^。\n]{0,12}(?:资本市场管理局|证券(?:与|和)商品管理局)"
                  r"|\bSCA\b|UAE\s+CMA")

CLAIM_KINDS = ("regulated_cn", "regulated_en", "licence_no", "fca_frn",
               "asic_afsl", "cysec_no", "offshore_reg")


def _pairs(rows, id_patterns, authorities):
    """Distinct (domain, authority, scheme, identifier) pairs found within a
    single sentence, under a given pattern set."""
    global ID_PATTERNS, AUTHORITIES
    keep_i, keep_a = ID_PATTERNS, AUTHORITIES
    ID_PATTERNS, AUTHORITIES = id_patterns, authorities
    try:
        found = set()
        for r in rows:
            for h in r["claims"]:
                if h["kind"] not in CLAIM_KINDS:
                    continue
                t = norm_space(h["text"])
                a, _ = find_authority(t)
                s, i, _k = find_identifier(t, a)
                if a and i:
                    found.add((r["domain"], a, s.rstrip("?"), i))
        return found
    finally:
        ID_PATTERNS, AUTHORITIES = keep_i, keep_a


def ablation(rows):
    pre_id = [p for p in ID_PATTERNS
              if p[0] not in ("CN-LIC", "EN-LIC", "CN-REG", "EN-COMPANY",
                              "EN-REG")] + [PRE_FIX_GENERIC]
    pre_auth = [(c, PRE_FIX_FSA_SC if c == "FSA-SC" else
                 PRE_FIX_SCA_AE if c == "SCA-AE" else p, g)
                for c, p, g in AUTHORITIES]
    base = _pairs(rows, pre_id, pre_auth)
    id_only = _pairs(rows, ID_PATTERNS, pre_auth)
    auth_only = _pairs(rows, pre_id, AUTHORITIES)
    both = _pairs(rows, ID_PATTERNS, AUTHORITIES)
    fmt = lambda ss: sorted(f"{d}|{a}|{s}|{i}" for d, a, s, i in ss)
    return {
        "same_sentence_authority_identifier_pairs_before_fix": len(base),
        "after_identifier_pairing_fix_only": len(id_only),
        "after_authority_longform_fix_only": len(auth_only),
        "after_both_fixes": len(both),
        "pairs_recovered": fmt(both - base),
        "pairs_recovered_by_identifier_pairing_fix": fmt(id_only - base),
        "pairs_recovered_by_authority_longform_fix": fmt(auth_only - base),
        "pairs_present_before_and_absent_after": fmt(base - both),
        "note": ("Counted at the sentence level, before fragment merging, so "
                 "a pair already reachable by merging two fragments still "
                 "appears here as recovered. The unit-level effect is in "
                 "units_with_authority_and_identifier."),
    }


def main():
    rows = [json.loads(l) for l in open(SRC)]

    units = {}
    vague = defaultdict(dict)
    operatives = defaultdict(dict)
    pages_per_domain = defaultdict(set)
    excluded = {}
    decisions = Counter()
    decisions_unit_bearing = Counter()
    excl_by_pagetype = defaultdict(Counter)
    # Every identifier seen anywhere on a page, to tell "no number on the
    # page" apart from "number on the page but in another sentence".
    ids_on_page = defaultdict(set)

    PREDICATING = ("regulated_cn", "regulated_en")
    ID_TOKEN = ("licence_no", "fca_frn", "asic_afsl", "cysec_no", "offshore_reg")

    # Pass 1 — collect every identifier present on each page.
    for r in rows:
        for h in r["claims"]:
            if h["kind"] in PREDICATING + ID_TOKEN:
                s, i, k = find_identifier(norm_space(h["text"]))
                if i:
                    ids_on_page[r["url"]].add((s.rstrip("?"), i, k))

    # Pass 2 — units.
    for r in rows:
        dom, url = r["domain"], r["url"]
        ptype = page_type(url)
        pages_per_domain[dom].add(url)
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
                        "example_url": prev["example_url"] if prev else url,
                    }
                continue

            if kind not in PREDICATING + ID_TOKEN:
                continue

            auth, register = find_authority(text)
            scheme, ident, ikind = find_identifier(text, auth)
            entity = find_entity(text)

            # FIX 2 — self-reference filter. Only predicating sentences are
            # tested: a bare identifier token ("FRN 591361", "许可证号 SD055")
            # predicates nothing and cannot be self-referential or not; it is
            # carried as an identifier token and marked as such, so that a
            # unit resting only on tokens is visible as resting only on
            # tokens.
            if kind in PREDICATING:
                decision, basis = self_reference(text, dom, ident)
            else:
                decision, basis = "id-token", "identifier token, not a predication"

            decisions[decision] += 1
            if auth or ident:
                decisions_unit_bearing[decision] += 1
            if decision in ("exclude", "queue"):
                excl_by_pagetype[decision][ptype] += 1
                k = (dom, text)
                e = excluded.get(k)
                if e is None:
                    e = excluded[k] = {
                        "domain": dom, "decision": decision, "reason": basis,
                        "page_type": ptype, "kind": kind,
                        "authority_detected": auth,
                        "identifier_detected": ident,
                        "n_hits": 0, "pages": set(), "page_type_counts": Counter(),
                        "sentence": text[:300], "example_url": url,
                    }
                e["n_hits"] += 1
                e["pages"].add(url)
                e["page_type_counts"][ptype] += 1
                continue

            if not auth and not ident:
                if kind in PREDICATING:
                    v = vague[dom].setdefault(text, {
                        "domain": dom, "sentence": text[:280], "n_pages": 0,
                        "page_type": ptype, "example_url": url,
                        "self_ref_basis": basis})
                    v["n_pages"] += 1
                continue

            key = (dom, auth, scheme, ident, entity.lower())
            u = units.get(key)
            if u is None:
                u = units[key] = {
                    "domain": dom, "authority": auth, "register": register,
                    "id_scheme": scheme, "identifier": ident,
                    "identifier_kind": ikind, "named_entity": entity,
                    "pages": set(), "n_sentences": 0,
                    "sentences": set(), "page_type_counts": Counter(),
                    "example_sentence": text[:300], "example_url": url,
                    "self_ref_basis": basis,
                    "pairing_basis": ("same-sentence" if (auth and ident)
                                      else ""),
                    "from_predication": kind in PREDICATING,
                    "truncated": bool(TRUNCATED_RE.search(text)),
                }
            u["pages"].add(url)
            u["sentences"].add(text)
            u["n_sentences"] += 1
            u["page_type_counts"][ptype] += 1
            u["from_predication"] = u["from_predication"] or kind in PREDICATING
            u["truncated"] = u["truncated"] or bool(TRUNCATED_RE.search(text))
            if len(text) > len(u["example_sentence"]):
                u["example_sentence"] = text[:300]

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
            continue
        keep = prev if len(prev["named_entity"]) >= len(u["named_entity"]) else u
        drop = u if keep is prev else prev
        keep["pages"] |= drop["pages"]
        keep["sentences"] |= drop["sentences"]
        keep["n_sentences"] += drop["n_sentences"]
        keep["page_type_counts"] += drop["page_type_counts"]
        keep["from_predication"] = keep["from_predication"] or drop["from_predication"]
        keep["truncated"] = keep["truncated"] or drop["truncated"]
        if keep["id_scheme"].endswith("?") and not drop["id_scheme"].endswith("?"):
            keep["id_scheme"] = drop["id_scheme"]
        if not keep["pairing_basis"]:
            keep["pairing_basis"] = drop["pairing_basis"]
        if len(drop["example_sentence"]) > len(keep["example_sentence"]):
            keep["example_sentence"] = drop["example_sentence"]
            keep["example_url"] = drop["example_url"]
        merged[k] = keep
    units = merged

    # Second merge pass: an authority-only unit whose own sentences contain
    # the identifier of a complete unit for the same (domain, authority) is
    # the SAME claim seen through a shorter fragment. This is still a
    # same-sentence pairing — it never pairs across sentences.
    complete_by_da = defaultdict(list)
    for k, u in units.items():
        if u["authority"] and u["identifier"]:
            complete_by_da[(u["domain"], u["authority"])].append(u)
    folded = 0
    for k in list(units):
        u = units[k]
        if not (u["authority"] and not u["identifier"]):
            continue
        for c in complete_by_da[(u["domain"], u["authority"])]:
            if any(c["identifier"] in s.replace(" ", "") for s in u["sentences"]):
                c["pages"] |= u["pages"]
                c["sentences"] |= u["sentences"]
                c["n_sentences"] += u["n_sentences"]
                c["page_type_counts"] += u["page_type_counts"]
                c["named_entity"] = c["named_entity"] or u["named_entity"]
                del units[k]
                folded += 1
                break

    # Third merge pass: a bare identifier fragment ("GB25204786") carrying no
    # authority is the same claim as a complete unit on the same domain with
    # the identical scheme and identifier string. Folding these is a string
    # identity, not an inference across sentences.
    complete_by_id = {}
    for u in units.values():
        if u["authority"] and u["identifier"]:
            complete_by_id.setdefault(
                (u["domain"], u["id_scheme"].rstrip("?"), u["identifier"]),
                []).append(u)
    folded_id = 0
    for k in list(units):
        u = units[k]
        if u["authority"] or not u["identifier"]:
            continue
        cands = complete_by_id.get(
            (u["domain"], u["id_scheme"].rstrip("?"), u["identifier"]), [])
        if len(cands) == 1:
            c = cands[0]
            c["pages"] |= u["pages"]
            c["sentences"] |= u["sentences"]
            c["n_sentences"] += u["n_sentences"]
            c["page_type_counts"] += u["page_type_counts"]
            del units[k]
            folded_id += 1

    # Completeness (FIX 3). Four distinct states, never one boolean.
    for u in units.values():
        auth, ident = u["authority"], u["identifier"]
        page_ids = set()
        for p in u["pages"]:
            page_ids |= ids_on_page.get(p, set())
        want = AUTHORITY_SCHEME.get(auth)
        others = []
        if auth and not ident:
            compatible = {(s, i, k) for s, i, k in page_ids
                          if k == "licence-number"
                          and (s in UNATTRIBUTED_SCHEMES or (want and s == want))}
            others = sorted({f"{s}:{i}" for s, i, _k in compatible})
        u["same_page_id_candidates"] = "; ".join(others[:6])
        if auth and ident:
            u["completeness"] = "authority+identifier"
        elif auth and not ident:
            if u["truncated"]:
                u["completeness"] = "identifier-truncated-at-extraction"
            elif others:
                u["completeness"] = "identifier-unpaired-same-page"
            else:
                u["completeness"] = "anchor-no-number"
        elif ident and not auth:
            u["completeness"] = "identifier-no-authority"
        else:
            u["completeness"] = "empty"

        sub = []
        if u["completeness"] == "anchor-no-number":
            sub.append("anchor-no-number")
        if u["identifier_kind"] == "company-registry-number":
            sub.append("candidate-B-mis-anchor")
        u["subcode"] = "; ".join(sub)
        u["claim_basis"] = ("self-referential-predication" if u["from_predication"]
                            else "identifier-token-only")
        u["claim_id"] = claim_id(u["domain"], u["authority"], u["id_scheme"],
                                 u["identifier"])
        u["n_pages"] = len(u["pages"])
        # Page types are counted over DISTINCT pages carrying the unit, not
        # over sentence hits, so the components sum to n_pages.
        u["page_type_counts"] = Counter(page_type(p) for p in u["pages"])
        u["page_types"] = "; ".join(
            f"{t}:{n}" for t, n in sorted(u["page_type_counts"].items(),
                                          key=lambda kv: -kv[1]))
        u["page_type_example"] = page_type(u["example_url"])

    os.makedirs(ART, exist_ok=True)
    out = sorted(units.values(),
                 key=lambda u: (u["domain"], u["authority"], u["identifier"]))
    FIELDS = ["claim_id", "domain", "authority", "register", "id_scheme",
              "identifier", "identifier_kind", "named_entity", "completeness",
              "subcode", "pairing_basis", "claim_basis",
              "same_page_id_candidates", "n_pages", "n_sentences",
              "page_types", "page_type_example", "self_ref_basis",
              "example_sentence", "example_url"]
    with open(os.path.join(ART, "claim_units.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    for e in excluded.values():
        e["n_pages"] = len(e["pages"])
        e["page_types"] = "; ".join(
            f"{t}:{n}" for t, n in sorted(
                Counter(page_type(p) for p in e["pages"]).items(),
                key=lambda kv: -kv[1]))
    exc = sorted(excluded.values(),
                 key=lambda e: (e["decision"], e["domain"], -e["n_pages"]))
    with open(os.path.join(ART, "excluded_non_self_referential.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "domain", "decision", "reason", "kind", "authority_detected",
            "identifier_detected", "n_pages", "n_hits", "page_types",
            "sentence", "example_url"], extrasaction="ignore")
        w.writeheader()
        w.writerows(exc)

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
        w = csv.DictWriter(f, fieldnames=["domain", "n_pages", "page_type",
                                          "self_ref_basis", "sentence",
                                          "example_url"])
        w.writeheader()
        w.writerows(vagues)

    by_dom = Counter(u["domain"] for u in out)
    comp = Counter(u["completeness"] for u in out)
    complete = [u for u in out if u["completeness"] == "authority+identifier"]
    complete_pre = complete
    n_excluded = sum(e["n_hits"] for e in exc if e["decision"] == "exclude")
    n_queued = sum(e["n_hits"] for e in exc if e["decision"] == "queue")
    tested = decisions["include"] + decisions["exclude"] + decisions["queue"]

    summary = {
        "source_pages": len(rows),
        "domains": len(pages_per_domain),
        "raw_sentences": sum(len(r["claims"]) for r in rows),
        "claim_units": len(out),
        "completeness_breakdown": dict(comp.most_common()),
        "units_with_authority_and_identifier": len(complete),
        "units_anchor_no_number": comp.get("anchor-no-number", 0),
        "units_identifier_unpaired_same_page": comp.get("identifier-unpaired-same-page", 0),
        "units_identifier_truncated_at_extraction": comp.get("identifier-truncated-at-extraction", 0),
        "units_identifier_no_authority": comp.get("identifier-no-authority", 0),
        "units_company_registry_number_in_licence_position": sum(
            1 for u in out if u["identifier_kind"] == "company-registry-number"),
        "fragment_units_folded_by_same_sentence_pairing": folded,
        "bare_identifier_fragments_folded_into_complete_units": folded_id,
        "pairing_fix_ablation": ablation(rows),
        "self_reference_filter": {
            "predicating_sentence_hits_tested": tested,
            "included": decisions["include"],
            "excluded": decisions["exclude"],
            "queued_for_manual_decision": decisions["queue"],
            "exclusion_rate_of_tested": round(decisions["exclude"] / tested, 4) if tested else None,
            "queue_rate_of_tested": round(decisions["queue"] / tested, 4) if tested else None,
            "distinct_excluded_sentences": sum(1 for e in exc if e["decision"] == "exclude"),
            "distinct_queued_sentences": sum(1 for e in exc if e["decision"] == "queue"),
            "excluded_sentence_page_hits": n_excluded,
            "queued_sentence_page_hits": n_queued,
            "unit_bearing_sentences_tested": sum(decisions_unit_bearing[d] for d in ("include", "exclude", "queue")),
            "unit_bearing_excluded": decisions_unit_bearing["exclude"],
            "unit_bearing_queued": decisions_unit_bearing["queue"],
            "identifier_tokens_passed_through_untested": decisions["id-token"],
            "excluded_by_page_type": dict(excl_by_pagetype["exclude"].most_common()),
            "queued_by_page_type": dict(excl_by_pagetype["queue"].most_common()),
        },
        # How many units are carried by at least one page of each type, and
        # how many (unit x distinct page) observations fall in each type.
        "units_appearing_on_page_type": dict(Counter(
            t for u in out for t in u["page_type_counts"]).most_common()),
        "unit_page_observations_by_page_type": dict(sum(
            (u["page_type_counts"] for u in out), Counter()).most_common()),
        "complete_units_appearing_on_page_type": dict(Counter(
            t for u in complete_pre for t in u["page_type_counts"]).most_common()),
        "distinct_pages_by_page_type": dict(Counter(
            page_type(r["url"]) for r in rows).most_common()),
        "vague_assertions": len(vagues),
        "domains_with_vague_only": len(
            {v["domain"] for v in vagues} - {u["domain"] for u in out}),
        "domains_with_operative_sentence": len(operatives),
        "operative_candidates": len(ops),
        "units_per_domain": dict(by_dom.most_common()),
        "note": (
            "Claim units are (domain, authority, identifier scheme, identifier, "
            "named entity) tuples deduplicated across pages; n_pages records how "
            "many DISTINCT archived pages carried the unit and n_sentences how "
            "many extracted sentence hits produced it. No A/B/C/D coding is "
            "applied here: coding requires register verification and the "
            "operative-entity determination (protocol sections 5-6). "
            "completeness distinguishes four states that an earlier revision "
            "conflated into one boolean: an authority paired with an identifier; "
            "an authority with no identifier anywhere on the pages carrying it "
            "(protocol section 3 sub-code anchor-no-number, a codeable "
            "observation and not an extraction failure); an authority whose "
            "page carries an identifier in a different sentence; and an "
            "authority whose identifier was cut off by the stage-2 extraction "
            "window. identifier_kind separates licence numbers from "
            "company-registry numbers displayed in a licence-number position. "
            "page_type is recorded but never used to exclude a sentence."),
    }
    with open(os.path.join(ART, "normalisation_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("units_per_domain", "note")}, indent=2,
                     ensure_ascii=False))
    print("\nunits per domain:")
    for d, n in by_dom.most_common():
        print(f"  {d:<24} {n}")


if __name__ == "__main__":
    main()
