# Locked Protocol v1.0 — Licence Anchoring in Chinese-Language Retail FX/CFD Marketing

Status: **FROZEN at the commit that introduces this file.** Changes require a numbered amendment. Amendments may restrict claims; they may not alter the taxonomy, the sampling frames, the coding rules, or the operative-entity rule once collection has begun.

Author: Zhennan (Nathan) Yu, independent researcher, Sydney.

## 1. Research question

On Chinese-language retail FX/CFD marketing pages, how do displayed regulatory-licence claims **anchor** to real regulatory records — and how often is the entity holding the displayed licence a *different* entity from the one that actually contracts with, onboards, and holds funds for the reader?

## 2. The phenomenon, and why it has not been measured

Offshore retail FX/CFD brands rarely fabricate licences. They display a genuine Tier-1 licence (ASIC, FCA, CySEC) as a public-facing anchor while onboarding clients from certain markets under a different group entity registered in a light-touch jurisdiction (Vanuatu, Seychelles, SVG, Mauritius, BVI). The client agreement, funds custody and trading servers sit with the offshore entity. Every individual statement is literally true; the reader's inference — that the displayed regulator stands behind their account — is not.

Four regulators have named the pattern. ESMA's 2019 public statement (ESMA35-36-1743, ¶18–19) describes EU-licensed CFD firms "marketing the possibility for retail clients to move their accounts to an intra-group third-country entity", including IP-based redirection. The FCA's 2024 CFD strategy calls these "halo firms" — entities that "exist purely to provide an FCA 'halo' to wider groups", giving false comfort to "global retail clients who see the FCA association but contract with an offshore group entity". ASIC's REP 828 (January 2026) found issuers "using ASIC regulation as a marketing tool ... on offshore related entity websites"; 46 of 52 reviewed issuers changed their websites, one amending close to 1,000 pages. IOSCO's FR12/22 Measure 7 recommends that authorities require disclosure of "who the underlying legal entity is offering the product and under what license (and from which jurisdiction)", and consider "keeping an open register which could enable the public to check and confirm whether a website belongs to a firm authorised to provide services in the jurisdiction". Industry called that register operationally infeasible; four years on, no member has implemented one.

**Named by regulators, remediated case by case, never counted.** Two structural reasons explain the absence of a prevalence figure:

1. **Regulator visibility is jurisdictional.** ASIC reviews Australian-facing sites, the FCA UK-facing ones. The pattern is defined by serving *different* content to *different* jurisdictions; no single regulator has the remit or the incentive to inspect Chinese-language pages.
2. **Broker-side datasets are blind by construction.** Every granular CFD study — Pelster (2024, *JBF* 162:107150), Heimer & Simsek (2019, *JFE* 132(3)) — draws on data from inside one licensed broker, which cannot observe a client routed to the group's offshore sibling. That client never enters the dataset. Pelster establishes that constrained risk relocates *across assets*; relocation *across legal entities* has never been tested.

This study attacks the question from the web side, where the divergence is publicly stated, and verifies it against statutory registers.

## 3. Taxonomy (frozen; the study's central measured object)

Each licence claim is coded into exactly one primary class:

| Class | Definition | Verification signal |
|---|---|---|
| **A — direct-licensed** | The claimed licence exists AND the licence holder is the entity that onboards the reader | Register record found; entity name and domain match the onboarding entity |
| **B — cross-entity licence-borrowing** | The claimed licence **genuinely exists** but the holder is not the onboarding entity | Register record found; onboarding entity differs (parent, sibling, technology provider, offshore shell) |
| **C — clone or fabricated** | The licence number does not exist, or appropriates an unrelated registrant's record | No register record, or record demonstrably unrelated to the claimant |
| **D — unverifiable** | The claim cannot be located in any register | No number, no named authority, or authority does not exist |

Orthogonal sub-codes (may co-occur with a primary class):

- **B-mis-anchor** — the displayed "registration number" is a company-registry number presented as a licence number. Observed instance: a page giving an FCA entity's "registration number OC376560", which is a Companies House LLP number, not an FCA Firm Reference Number.
- **B-false-anchor** — the named authority does not license this business in that jurisdiction. Observed instance: a Chinese page stating an SVG entity is "regulated by the Financial Services Authority", where the SVG FSA registers international business companies and does not license forex at all. Verifiable and countable.
- **B-portfolio** — the page displays licences of multiple group entities while a single offshore entity onboards. Observed instances: eight entities on one page; six on another.
- **anchor-no-number** — regulation asserted with no licence number on the same page.

**Central hypothesis, frozen as a hypothesis and not a conclusion:** class B is the dominant form in this ecosystem, substantially exceeding class C, while public and regulatory attention concentrates on class C. The study is equally prepared to report that B is marginal.

## 4. Sampling frames (mechanical; no manual selection)

Three frames, enumerated by rule, with overlap reported:

- **F1 — corpus frame.** Common Crawl columnar index, filtered to Chinese-primary pages (`content_languages` beginning `zho`, available since CC-MAIN-2018-39) in the retail FX/CFD vertical by a frozen URL/host regex. Verified reachable without any API key: CDX API, columnar Parquet index, `cluster.idx`, and WARC byte-range requests all return HTTP 200/206. Measured scale: ≈2.1 billion records per crawl, ≈25.4 million Chinese-primary pages, of which the FX/CFD slice is ≈72,000 pages and ≈0.9 GB compressed.
- **F2 — offshore-register frame (spine).** Direct enumeration of offshore securities-dealer registers (e.g. the Seychelles FSA capital-markets register, 193 entries), which lists the onboarding vehicles themselves. Each entry carries a website URL, enabling entity→brand mapping.
- **F3 — warning-list frame.** ASIC Investor Alert List, FCA Warning List, IOSCO I-SCAN. **Used only for validity checks and a lower bound on class C — never as a primary frame**, because it selects on class C by construction.

**Sample:** stratified random sampling by offshore jurisdiction (Seychelles / Vanuatu / Mauritius / BVI / Belize / SVG / no offshore entity). The random seed is fixed in this protocol and published. **Target N = 80; floor N = 60.** The reduction from an earlier target of 150 follows directly from access testing: of 14 brands probed live, roughly 2 were cleanly retrievable; archive rescue recovered 2 of 8 blocked brands. Browser-based collection is the default path, not an exception.

## 5. Jurisdiction-differential procedure

For each sampled brand:

1. Record the entity named in the operative sentence on the **Chinese-language** page ("X 是 Y 的商业名称" / "X is a trading name of Y") together with any licence numbers displayed.
2. Record the same for the brand's **UK/AU/EU-facing** pages.
3. Record the entity named on the **client agreement / terms page reached through the onboarding flow**, and its jurisdiction.
4. A divergence between (1)/(3) and (2) is the evidence of class B.

**Hard rules, non-negotiable:** no account is opened; no personal data is submitted at any point; only publicly displayed terms and agreement pages are read; robots.txt is respected and requests are rate-limited to human speed.

**Vantage point is a first-class coded variable.** Access testing established that at least one brand serves *opposite* entities on the same Chinese-language path depending on the requester's egress IP — a naive single-vantage crawler codes the hypothesis backwards. Every brand is therefore collected from at least two vantage points, and "entity shown to this vantage" is recorded separately from "entity shown on this locale path". Geo-routing is itself a reportable finding.

**Operative-entity rule (deterministic; required because pages may name several).** Where multiple entities each claim to operate the site, the operative entity is determined in this order: (OE-1) the entity named in the client agreement reached through the onboarding flow for a Chinese-language visitor; failing that, (OE-2) the entity named in the footer "business name / trading name" sentence on the Chinese page; failing that, (OE-3) the entity named as site operator for the visitor's declared region. Cases unresolved by OE-1..3 are coded D with reason `multi-entity-indeterminate`.

## 6. Register verification

Two steps: (i) does the record exist; (ii) does the licence-holder name match the operative entity. Mechanical string/domain matching is applied first with rules frozen here; edge cases go to a manual queue.

**Documented limitation, stated in the paper:** some offshore registers publish no licence numbers. The Seychelles FSA capital-markets register (193 securities-dealer entries) carries entity name, address, contact and website only — no `SD###` field. For such registers, B-versus-C discrimination is **name-level only**, and a class-C impostor copying a registrant's name would pass. This limitation is reported wherever it applies rather than being concealed by a uniform verification claim.

**Manual verification budget:** n = 200 stratified claims verified by the author. Recognising white-label structures is domain expertise the author holds from working in the industry (which "regulation" is a parent's licence; which onboarding entities sit in Vanuatu or the Seychelles). This is declared as a positionality statement in the methods section, not presented as neutral automation.

## 7. Mechanical exclusions (frozen; counts disclosed, names withheld)

1. The author's employer's brand and all associated domains.
2. All properties owned by the author.
3. Any domain whose affiliate funnel terminates at the employer or at brokers partnered with the author's properties.
4. Personal blogs below a traffic threshold (no private individuals as units of analysis).

Excluded items are reported only as aggregate counts ("excluded n = X by rule Y").

## 8. Language discipline (defamation safety; mandatory)

Class B is reported as an **observable entity relationship** — "the licence is held by an entity other than the one that contracts with the client" — and is **never** described as fraud, fake, or a scam. Class C requires archived register evidence for every instance. All findings are reported at the level of what a page states and what a register records, with timestamps and archived copies retained.

## 9. What this design can and cannot claim

**Can:** the prevalence of each anchoring class across the sampled frame; the frequency of jurisdiction-differential onboarding; the frequency of false and mis-anchored identifiers; a demonstration that a public register of "which entity stands behind this domain" is technically feasible.

**Cannot:** any claim about how many clients are affected (exposure is not measured); any claim that a class-B arrangement is unlawful (it generally is not); any causal claim about harm; any statement about firms outside the sampled frame. Dropping the original search-ranking layer means the sample is **not** exposure-weighted: this measures the ecosystem's composition, not what any particular searcher sees.

## 10. Conflict-of-interest disclosure (in all outputs)

The author is employed full-time in a business-development role at a retail FX/CFD brokerage in Sydney and operates independent Chinese-language trading-education web properties. No employer data, systems, or client information is used at any point. Employer-connected and author-connected domains are excluded by the mechanical rules in §7, with counts disclosed. Research data does not enter the author's commercial content channels before publication.

## 11. Venue

WEIS 2027 (primary); APWG eCrime 2027 (secondary); arXiv cs.CY cross-listed cs.CR on completion.
