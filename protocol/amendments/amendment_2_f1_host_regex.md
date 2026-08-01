# Amendment 2 — the frozen host regex for sampling frame F1

Status: **declared before execution.** This file, and the pattern constants in
`src/frame_corpus.py` that it fixes, were committed before the regex was run
against any host list, so the pattern cannot have been tuned to the brands it
selects. The frozen protocol is not edited.

## Why this amendment exists

`locked_protocol_v1.0.md` §4 defines frame F1 as the Common Crawl corpus
"filtered to Chinese-primary pages … in the retail FX/CFD vertical **by a
frozen URL/host regex**", but the protocol does not contain the regex. That is
a gap in the frozen text: the discipline it promises (a pattern fixed in
advance) cannot be verified against a pattern that was never written down.
This amendment closes it in the only honest direction available — by fixing
the pattern now, publicly, before use, and accepting whatever it returns.

## Realisation of F1 (and why not the columnar index)

The protocol names the columnar Parquet index as the F1 instrument. It is not
usable here: the parquet files are keyed by opaque UUID filenames that require
an S3 listing (not served on the public HTTPS mirror in this environment), no
parquet reader is installed, and a column scan of one crawl is on the order of
tens of gigabytes. `cluster.idx` (101 MB) is reachable but records only block
boundaries, i.e. a ~0.02 % sample of the SURT space, which cannot enumerate a
vertical.

The realisation used instead is Common Crawl's **domain-level web-graph
vertices** file for the release covering the pinned crawl:

    projects/hyperlinkgraph/cc-main-2026-may-jun-jul/domain/
      cc-main-2026-may-jun-jul-domain-vertices.txt.gz   (879 MB gz)

It enumerates every domain Common Crawl saw in the underlying crawls, one per
line as `<id>\t<reversed-domain>\t<n_hosts>`, and is streamed and filtered in
memory without being stored. The host regex is applied to the reconstructed
domain name. Chinese-language presence is then established per candidate by
the same keyless CDX presence probe already used for F2, so the
`content_languages` filter the protocol specifies is applied — just at the
domain step rather than inside a columnar scan.

**Consequence for claims, stated plainly:** F1 as realised enumerates domains
whose *name* matches the vertical pattern. A retail FX/CFD site whose domain
name carries no vertical token is invisible to it. F1 is therefore a
name-pattern frame, not an exhaustive vertical census, and the paper must say
so wherever F1 coverage is described. Frames F2 and F3 remain as specified.

## The frozen pattern

Applied case-insensitively to the full domain name (label boundaries respected
so that substrings inside unrelated words do not match).

**Vertical tokens** — a domain qualifies if it contains any of:

    forex, fx, cfd, mt4, mt5, metatrader, broker, brokers, trader, traders,
    trading, invest, investing, capital, markets, market, prime, securities,
    fintech, exchange, gold, xau, futures, margin, leverage, spread,
    waihui, wh, huiyin, jinrong, waihuiwang

The last five are Hanyu Pinyin transliterations that appear in Chinese-facing
domains (外汇 → waihui; 汇银 → huiyin; 金融 → jinrong; 外汇网 → waihuiwang).
`fx` and `wh` are matched only as a whole label or bounded by a separator or
digit, never as a substring inside a longer word, because two-letter tokens
otherwise match almost everything.

**Exclusions** — a domain is dropped, before any Chinese-presence probe, if it
matches any of:

    (a) the author's employer's brand and all associated domains;
    (b) properties owned by the author;
    (c) news, wiki, forum, blog, education, government and regulator hosts, by
        suffix (.gov, .gov.au, .edu, .edu.au, .ac.uk, .org.au) or by an
        explicit host list of major financial media;
    (d) obvious non-vertical uses of the ambiguous tokens: "supermarket",
        "marketplace", "flea-market", "gold-jewellery" and similar, by a
        frozen negative-token list.

Exclusions (a) and (b) implement protocol §7 rules 1–2. Every exclusion is
counted and the counts are published; names are withheld only for (a) and (b),
as §7 requires.

## Sampling from F1

The matched-domain list is not the sample. As §4 requires, sampling is
**stratified random with the seed fixed here and published**:

    seed = 20260723   (the protocol freeze date, as used throughout)

Strata are offshore jurisdiction where determinable from the F2 join, and
"no offshore entity" otherwise — which is exactly the stratum §4 names and
which F2 cannot supply by construction. Allocation is proportional to stratum
size, capped so no single stratum exceeds 40 % of the drawn sample.

## What this amendment does not do

It does not alter the taxonomy, the operative-entity rule, the two-step
register verification, the language discipline, or the N = 80 target / 60
floor. It does not revise any figure already reported: units verified under
frames F2 and F3 keep their coding and their claim ids, and F1-derived units
will be reported with their frame recorded so the two can be separated by any
reader who wants to.

Recorded 2026-08-02, before execution.
