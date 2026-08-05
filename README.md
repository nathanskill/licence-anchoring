# Licence Anchoring (REF-2026-019)

Status: `PROTOCOL FROZEN · 21 VERIFIED CLAIM UNITS — 35.0% OF THE 60-UNIT FLOOR, NOT A POPULATION ESTIMATE · FRAME F1 EXECUTED, DISTINCTIVE USABLE YIELD ≤4/979, REPORTED AS A NEGATIVE RESULT · MANUSCRIPT DRAFT v0.1, §7 DELIBERATELY UNWRITTEN`

## The question

Chinese-speaking retail clients read "regulated by the FCA" on a broker's page and assume someone will step in if things go wrong. Often a different group entity — registered in St Vincent, Vanuatu or the Seychelles — is the one that actually contracts with them and holds their funds. The licence is genuine; it simply does not cover the reader, and they tend to discover this only when they try to claim.

This study asks a narrow, checkable question about those pages: when a page displays an authority and a licence number, what does the regulator's own register say the number is attached to? Every display is normalised into a claim unit (brand domain × named authority × identifier × named holder) and checked against the issuing register in two separate steps — does the record exist, and is the register's published holder the same entity that onboards the client — with the two answers recorded independently. Where a register publishes no field capable of answering, the unit is coded `UNVERIFIABLE-TODAY` with the reason, never inferred.

Four regulators have named the pattern: ESMA (2019), the FCA's "halo firms" (2024), ASIC REP 828 (2026), and IOSCO FR12/22, which recommended a public register of which entity stands behind a domain and was told by industry it was infeasible. Nobody has counted it. The aim is to turn something readers find out afterwards into a number they can see beforehand, and to give regulators a baseline against which remediation can be measured.

## What exists in this repository

| Stage | State | Where |
|---|---|---|
| Protocol | Frozen before any collection (tag `v1.0-protocol-freeze`); changed only by numbered amendment, never by editing the frozen file. Six amendments to date. | [`protocol/`](protocol/) |
| Register spine (frame F2) | Four offshore registers enumerated — Seychelles, Vanuatu, Belize, SVG: 675 registrants parsed, 450 committed after the privacy filter, 231 distinct domains. Five further registers attempted and recorded as not machine-enumerable, each with the observed failure. | [`artifacts/frames/register_coverage.md`](artifacts/frames/register_coverage.md) |
| Chinese-presence probe over F2 | 222 of the 231 register-listed domains probed against the keyless Common Crawl CDX index; 26 carry Chinese-language pages. | [`artifacts/frames/cc_chinese_probe.jsonl`](artifacts/frames/cc_chinese_probe.jsonl) |
| Pilot verification | 12 claims from 6 brands checked live against 8 registers on 2026-08-01; divergence concentrated in scope, domain and instrument rather than existence, which set the design. | [`artifacts/pilot_verification/`](artifacts/pilot_verification/) |
| Claim corpus | 413 archived Chinese-language pages across 22 domains (CC-MAIN-2026-25 WARC records, per-payload SHA-256 manifest); 2,501 licence-claim sentences; 37 claim units, of which 19 pair an authority with an identifier. Completeness is recorded in five states, not a boolean. | [`artifacts/claims/`](artifacts/claims/) |
| Verification, batches v1 + v2 | 21 units across 9 brand domains checked against 9 official registers on 2026-08-01/02, each fact with its register URL or reproduction recipe and check date. Class tally: A 3, B 12, C 0, D 6. | [`artifacts/verification_v1/`](artifacts/verification_v1/), [`artifacts/verification_v2/`](artifacts/verification_v2/) |
| Frame F1 (vocabulary-anchored) | 117,963,409 domains streamed from the Common Crawl web-graph vertices; 96,141 matched the frozen pattern; a 1,000-domain draw probed to 979; 14 Chinese-presence hits (1.43%). Distinctive usable yield: at most 4. Reported as a frame failure — see below. | [`artifacts/frames/frame_f1_summary.json`](artifacts/frames/frame_f1_summary.json), [`artifacts/frames/f1_presence_summary.json`](artifacts/frames/f1_presence_summary.json) |
| ASIC website-field audit | Coverage audit of ASIC's new AFS-licensee website field (amendment 5 §3): the premise checks out against ASIC's own documents, but the field is voluntary, not searchable, and absent from the 6,525-row bulk dataset, so no coverage rate can honestly be computed. The report records the gap and what would close it. | [`artifacts/asic_website_coverage/coverage_report.md`](artifacts/asic_website_coverage/coverage_report.md) |
| Paper | Manuscript draft v0.1, eight sections. §7 — the route to the pre-declared 60-unit floor — is deliberately unwritten: that decision must be recorded as an amendment before it is executed, not narrated after. | [`paper/manuscript_draft_v0.1.md`](paper/manuscript_draft_v0.1.md) |

## What the 21 verified units show

Fabrication is not the failure mode of this ecosystem. Class C — clone or fabricated — stands at zero across 21 units. Where a claim and a register diverge, the divergence sits in **scope** (wholesale-only or consultation-only permissions behind a retail-facing page), in **domain** (the register publishes an approved website that is not the one displaying the claim), or in **identifier type** (a company-registry number occupying a licence-number position). Every class-B count is reported with that three-way split; an undifferentiated total is never presented as a headline. The split, and the evidence rules that came with it, are recorded in [amendment 5](protocol/amendments/amendment_5_mismatch_structure_and_evidence_rules.md).

The finding that motivates the paper is about registers, not operators: the register frequently cannot answer the question a licence number appears to answer. Four of the nine registers used publish no licence numbers at all. Several publish no scope, client-type or website field. Verification depth is therefore recorded per unit: number-level two-step completed for 9 units, name-level only for 10, one resolved through an ABN printed in the same sentence, and one with no identifier on the page at all — a codeable `anchor-no-number` observation, not an extraction failure. Against the industry position that IOSCO's recommended register is infeasible, one counter-example is now on the record: Vanuatu, with 66 licensed dealers, publishes an identifier-to-holder mapping that this study used to resolve a claim at number level.

Classification is made against the operative entity — the one that would actually be the client's counterparty — under a frozen evidence ladder. Where no rung resolves, the unit is coded indeterminate rather than assigned by inference; two of the nine verified domains are in that state.

**The limitation travels with the numbers.** N = 21 is 35.0% of the protocol's 60-unit floor and 26.3% of its 80-unit target. The counts describe the verified units only. They are not a population estimate and must not be read as a rate for the sector, for Chinese-language broker pages generally, or for any register's licensee base. The units are not independent — 7 of the 21 come from one domain and 3 from another, so unit-level shares partly reflect how many authorities one page happens to display. Selection was archive-driven rather than random. And class C's zero carries no information about C's prevalence, because four of the nine registers publish no licence numbers, structurally preventing the number-level test that most often separates C from B. Weak or null results will continue to be reported in full.

## The sampling frame that failed

Frame F1 exists to reach operators that no register lists — including `.cn` domains, which a register-anchored frame structurally cannot see. Its host-name pattern, exclusions, seed and stratum rule were frozen before the scan ran (amendments 2–4), with one commitment attached: the yield would be published whatever it turned out to be, and the frame would not be retuned in response.

It turned out badly, and it is published. Of 979 domains probed from the 1,000-domain draw, 14 carry Chinese-language captures — but presence is not relevance. Three of the 14 are demonstrably not financial sites (one sells audio channel strips; the `fx` is audio effects). Four short-token hits read as Wuhan (武汉), not waihui (外汇). Three are large regulated brands a register frame reaches anyway. The distinctive usable yield — relevant and not otherwise reachable — is at most 4 domains in 979, pending a content check on the four unconfirmed ones. The frozen tokens stay: removing them after seeing which domains they caught is exactly the retuning the pre-registration prohibits. The route to the 60-unit floor is not F1, and the paper says so.

[Amendment 6](protocol/amendments/amendment_6_f1_precision_and_probe_missingness.md) carries this analysis and two self-corrections made in the open. Its own first version, written against an incomplete run, drew two conclusions the completed run superseded; Revision 1 records both rather than replacing the text. It also withdraws a claim the first version made — that the `wh` token had "paid out on live data" — as unsupported and probably backwards. And it documents a caveat emitted by the study's own frozen code that turned out to be false for one field, with the corrected wording and the exact scope of the damage.

## The discipline

The frozen protocol fixes the taxonomy (A direct-licensed / B cross-entity licence-borrowing / C clone-or-fabricated / D unverifiable), the sampling frames, the coding rules and the operative-entity rule. Corrections and pinned choices are numbered amendments in [`protocol/amendments/`](protocol/amendments/):

1. Seychelles dealer count corrected 193 → 231; crawl pinned to CC-MAIN-2026-25.
2. F1's host regex, exclusions, seed and stratum cap declared before execution.
3. F1's suffix-position rule — made after seeing the match composition, and saying so; both figures published (166,825 unrestricted / 96,141 retained); retuning F1 in response to its yield prohibited.
4. The pre-registered 40% stratum cap cannot bind on the realised frame; the consequence (F1 counts are not projectable by scaling) fixed before any F1 number existed.
5. The three-way class-B structure; the regulatory instruments the study may cite, with s911A expressly barred because nothing in this method can establish unlicensed operation; two evidence rules — future-dated sources are inadmissible, and trade-press characterisations of regulatory documents are leads, not evidence.
6. F1's measured precision, the probe's informative missingness, a false caveat in frozen output, and Revision 1's supersessions and withdrawal, described above.

Three extraction defects found after freezing were corrected in the open, each with an ablation showing exactly what it moved (the fullwidth-colon defect alone recovered 5 complete units; two units were withdrawn by the self-reference filter and are recorded as withdrawn, not silently dropped). Every correction so far has made the corpus smaller or more qualified, not larger.

One methodological note that shaped the design: at least one brand serves opposite entities on the same Chinese-language path depending on the requester's egress IP. Vantage point is therefore a coded variable and every brand is collected from at least two vantages — a single-vantage crawler can code the hypothesis backwards.

## Reproducing

The pipeline is keyless throughout: Common Crawl for the corpus frame, offshore securities-dealer registers for the spine, statutory registers for verification. No account is ever opened and no personal data is submitted; only publicly displayed pages are read. In order: `src/frame_offshore.py` (F2 spine), `src/frame_corpus.py` (F1 scan), `src/probe_f1.py` and `src/frame_chinese.py` (presence probes), `src/extract_claims.py` (stage 2), `src/normalise_claims.py` (stage 3). Stage-4 verification is manual register work; every fact in the verification reports carries its register URL — or, where a register has no per-record permalink, the exact reproduction recipe — and its check date. Register fetches are archived verbatim with SHA-256 manifests, and all parsing runs against the archived bytes, never the live network. The corpus is pinned to CC-MAIN-2026-25 so results cannot drift under a re-run.

## What this study does not claim

Nothing here can establish that any entity provided financial services without a licence, and the study never says so; amendment 5 bars citing s911A in coding for exactly this reason. No brand is described as fraudulent, fake or a scam — class B is an observable entity relationship, nothing more. No prevalence estimate is made at N = 21, and none of the frame counts is projectable by scaling. Where a register publishes no field capable of testing a claim, that is recorded as `UNVERIFIABLE-TODAY`, never treated as absence.

## Related repositories

By the same author: [pump-and-dump-replication-audit](https://github.com/nathanskill/pump-and-dump-replication-audit) · [alert-burden-audit](https://github.com/nathanskill/alert-burden-audit) · [leaderboard-survivorship](https://github.com/nathanskill/leaderboard-survivorship) · [evidence-separated-trading-screening](https://github.com/nathanskill/evidence-separated-trading-screening)

License: MIT.
