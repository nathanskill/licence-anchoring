# What a Licence Number Anchors: Register-Level Verification of Regulatory Claims on Chinese-Language Retail FX Websites

**REF-2026-019 — manuscript draft v0.1**
**Status: DRAFT. Not submitted. Section 7 is deliberately unwritten pending a design decision; see §7.**
**Protocol:** `protocol/locked_protocol_v1.0.md`, amendments 1–6.

---

## Abstract

Retail foreign-exchange and CFD websites addressed to Chinese-reading audiences routinely display regulatory authorities and licence numbers. We ask a narrow, checkable question about those displays: **when a page shows an authority and a number, what does the regulator's own register say the number is attached to?**

We build a claim corpus from archived Chinese-language pages, normalise each display into a unit of *brand domain × named authority × identifier scheme × identifier × named entity*, and check each unit against the issuing regulator's own register in two separate steps — (i) does the record exist, and (ii) is the register's published holder name the same as the entity named on the page — recording each answer independently and recording `UNVERIFIABLE-TODAY` with a reason wherever a register does not publish the field required to answer.

From 413 archived pages across 22 domains and 2,501 extracted sentences, 37 claim units were normalised, of which 19 pair an authority with an identifier. Twenty-one units across nine brand domains have been verified against seven registers in two batches.

The result that motivates the paper is not that claims are false. It is that **the register frequently cannot answer the question a licence number appears to answer.** Of the seven registers checked, several publish no scope field, no client-type field, and no website field, so "is this licence for this activity, for these clients, on this domain?" is not answerable from the register at all — a property of the registers, not of the operators. Where the register *is* informative, the units separate cleanly into three structurally different kinds of mismatch — of scope, of domain, and of instrument — which prior work, focused on whether a claim is true or false, does not distinguish.

We also report, against ourselves, that our recall-oriented sampling frame largely failed. Its measured Chinese-presence rate is 1.43% (14 of 979 domains probed), but presence is not relevance: three hits are large brands a register-anchored frame reaches anyway, three are demonstrably not financial sites at all, and four short-token hits read as Wuhan (武汉) rather than waihui (外汇). The frame's distinctive usable yield is **at most 4 domains in 979**. We publish this because the frame's pre-registration required the yield to be published whatever it turned out to be, and we do not retune the frame in response to it.

Every register fact is stated as of a recorded check date with a reproduction recipe, because several of these registers have no GET-addressable permalink. Three extraction defects found and corrected after freezing are reported with the ablation showing exactly what each moved.

---

## 1. Introduction

A licence number on a website is an anchor: it invites a reader to believe that a named authority has authorised something, and that the something is what the page is offering. This paper asks what the anchor actually holds, using only what the issuing regulator itself publishes.

The question is narrow on purpose. We do not assess whether any operator has breached any law; we do not code any unit as a contravention; we make no claim about any operator's conduct. We record two things and keep them apart: **what the page displays**, and **what the register publishes**. Where they differ, we describe the difference structurally, and where the register is silent we say so rather than inferring.

### 1.1 Contributions

1. **A register-anchored verification protocol, frozen before execution.** Two-step verification (record existence, then holder-name identity) with the two answers recorded separately, so that "the number exists but names a different company" is a distinguishable state rather than a collapsed "unverified".

2. **An operative-entity evidence ladder.** A brand domain typically names several entities across several jurisdictions. Classification is made against the entity that would actually be the client's counterparty, established under a frozen ladder — OE-1 a publicly posted client agreement, OE-2 a footer trading-name sentence, OE-3 an explicit site-operator sentence — and where no rung resolves, the unit is coded `operative-indeterminate` rather than assigned by inference. Two of the nine verified domains are indeterminate, and we report them that way.

3. **A three-way mismatch structure.** Where a claim and a register diverge, the divergence is of scope (the record exists and names the right entity, but the register's published permissions do not cover what the page offers), of domain (the record exists and names the right entity, but the register publishes a different website, or publishes none), or of instrument (the number exists but is a company-registry number, or belongs to a different company). These have different implications and different evidentiary requirements, and collapsing them loses the finding.

4. **A recall-oriented sampling frame that reaches what register-anchored sampling structurally cannot**, together with its measured precision and an analysis showing its missingness is informative rather than random (§3.2, §6.2).

5. **A complete, dated amendment trail**, including three extraction defects found after freezing and corrected in the open, with the ablation showing exactly what each correction moved.

### 1.2 What this paper does not do

We do not estimate prevalence. The corpus is not a probability sample of the retail FX web, and no number here should be read as "X% of brokers do Y". We do not characterise any display as misleading, deceptive, or unlawful; those are determinations for a court or a regulator, not for a measurement paper. We do not cite trade-press characterisations as evidence of any register fact (amendment 5 §5), and we do not use any source dated after a unit's recorded check date.

---

## 2. Background and related work

### 2.1 Why the register, and only the register

The obvious way to check a licence claim is to search the internet for the broker's name. This produces trade-press articles, review sites and forum posts, all of which are downstream of the same primary source and none of which is reliable about scope, status or dates. The protocol therefore admits only the issuing regulator's own published register as evidence of a register fact, and records the exact retrieval route.

This is more burdensome than it sounds. Of the seven registers used here, **the South African FSCA publishes no GET-addressable permalink per licensee** — the record is reachable only by a two-step form POST, which the protocol records as a reproduction recipe in place of a citation. Others require searching a downloadable list rather than a per-record page. A study design that assumes every regulator offers a stable per-record URL will silently drop the registers that do not.

### 2.2 The gap this paper addresses

Existing work on retail FX and CFD promotion tends to ask whether a firm is regulated, treating the answer as binary. The binary framing is where the information is lost. A record can exist, name exactly the entity on the page, be current, and still not answer the question the page's reader is asking, because the register publishes no scope field, no client-type field, and no website field. In that case the honest finding is not "verified" and not "false" — it is **that the register cannot answer**, and we introduce `UNVERIFIABLE-TODAY` with a mandatory reason as a first-class outcome for exactly this.

---

## 3. Method

### 3.1 Corpus construction

Pages are archived Chinese-language regulatory and "about" pages from Common Crawl capture sets. Two sampling frames are used and kept separate throughout:

- **F2, register-anchored.** Domains reached from regulator registers. High precision, but structurally blind to any operator with no offshore register entry — including `.cn` domains.
- **F1, vocabulary-anchored.** Domains drawn by matching a frozen vertical vocabulary against a domain-level web-graph vertex set of 117,963,409 domains, reduced to 166,825 unrestricted matches and 96,141 after the frozen suffix-position rule (amendment 3). F1 is recall-oriented by construction and its precision is unknown until measured.

The frozen F1 vocabulary includes Pinyin tokens (`waihui`, `huiyin`, `jinrong`, `waihuiwang`) and the short tokens `fx` and `wh`. §4.5 reports what those tokens actually caught, which is not what they were intended to catch.

### 3.2 F1's Chinese-presence rate, and why the residual missingness barely matters

A 1,000-domain draw was probed against the keyless Common Crawl CDX index for the presence of Chinese-primary captures. **979 domains were probed; 14 carry Chinese-language captures (1.43%);** both small strata are censused complete.

Twenty-one domains remain unprobed. They are service failures — a live diagnostic returned HTTP 504 Gateway Time-out in every sampled case — and per the frozen design a failed query is never written, so they are "not yet probed" rather than false negatives.

**That missingness is informative, and we can show the direction.** A CDX timeout falls on an expensive query, and query cost rises with capture count, which is itself a strong predictor of Chinese presence:

| Capped total captures | n | Chinese-present | Rate |
|---|---|---|---|
| 0 | 642 | 0 | 0.00% |
| 1–9 | 162 | 2 | 1.23% |
| 10–99 | 72 | 6 | 8.33% |
| 100–999 | 23 | 3 | 13.04% |
| 1000+ | 2 | 0 | 0.00% |

So the timeouts are enriched for exactly the outcome being measured. With only 21 domains outstanding, however, the practical consequence is small: bounding them between "none has Chinese content" and "they behave like the 10–99 band" gives **1.40%–1.57%**.

We record this because an earlier, incomplete pass of the same probe (810 rows) implied a bound of 1.0%–2.6%, and the wide interval was an artifact of incompleteness rather than a property of the instrument. The mechanism is real; the uncertainty it appeared to imply was not. Per amendment 3, F1 was **not** retuned in response to any of this.

### 3.3 Extraction, normalisation, and the self-reference filter

Sentences predicating regulatory status are extracted and normalised into claim units. From 413 pages and 2,501 raw sentences, 37 units result, distributed across 15 domains, with `xs.com` (7) and `m4markets.com` (6) carrying the most.

Completeness is recorded in **five** states, not as a boolean:

| Completeness state | Units |
|---|---|
| authority + identifier | 19 |
| identifier, no authority | 14 |
| identifier unpaired, same page | 2 |
| anchor, no number | 1 |
| identifier truncated at extraction | 1 |

The distinction matters. `anchor-no-number` — the page names an authority and publishes no number anywhere on the pages carrying it — is a **codeable observation under the frozen taxonomy, not an extraction failure**, and an earlier revision that used a boolean could not tell it apart from "the number is on the page but in another sentence".

**The self-reference filter.** The corpus is 413 pages of which 282 are editorial. Reader advice, conditionals, questions, third-party comparisons and definitions from those pages predicate nothing about the operator and must not enter the frame. Of 562 predicating sentence hits tested, 477 were included, 70 excluded and 15 queued for manual decision. Two units present in an earlier table were withdrawn by this filter and are recorded as withdrawn rather than silently dropped:

- a `zfx.com` sentence whose grammatical subject is the anaphor 它, on an academy page about the CAC 40 index — no legal entity and no brand token appears;
- two `fxcentrum.com` sentences that are advice to the reader (「务必核实该平台是否受 FCA 或同等机构监管」) and a generalisation about FCA-regulated brokers as a class.

Page type is recorded but **never** used to exclude a sentence; it is used only to describe where units appear.

### 3.4 Two-step verification

For each unit with an authority and an identifier, against the issuing regulator's register only, on a recorded date:

1. **Does the record exist?** Answered independently of (2).
2. **Is the register's published holder name the same as the entity named on the page?** Recorded as exact / exact-modulo-case / different / n/a.

Then, wherever the register publishes them: scope, client type, status, dates, and approved domain. Wherever it does not, `UNVERIFIABLE-TODAY` plus the reason.

### 3.5 The operative-entity ladder

Classification is against the operative entity — the entity that would be the client's counterparty — under the frozen ladder OE-1 > OE-2 > OE-3. Resolved examples include Raw Trading Ltd (`icmarkets.sc`, OE-2), XS Ltd (`xs.com`, OE-3), IUX Markets Limited (`iux.com`, OE-1), Trinota Markets (Global) Limited (`m4markets.com`, OE-1). Two domains resolve to **indeterminate** and are coded as such rather than assigned: `darwinex.com` (candidates Tradeslide Trading Tech Ltd; Tradeslide Global Ltd; Sapiens Markets EU SV SA) and `fpmarkets.com` (candidates FP Markets Ltd, Saint Lucia; First Prudential Markets Limited, Seychelles).

---

## 4. Results

All register facts below were checked on the dates recorded in `artifacts/verification_v1/` (2026-08-01) and `artifacts/verification_v2/` (2026-08-02), against the register URLs and reproduction recipes given there. No third-party site was used to establish any fact.

### 4.1 The register often cannot answer

This is the headline and it is about registers, not operators.

- The **FSA Seychelles** securities-dealer listing publishes no scope, no status and no dates. Two units (`fusionmarkets` SD096, `tradequo` SD140) are therefore name-level verifiable and **number-level `UNVERIFIABLE-TODAY`**: a sweep of the whole register page for SD-number strings returned zero matches. The number displayed on the page is not a field the register publishes in a checkable form.
- The **FSCA** record for `xs.com` publishes an approvals grid but **no client-type field and no territorial field**, so client scope is `UNVERIFIABLE-TODAY`; and no trading-name or website field, so approved domain is `UNVERIFIABLE-TODAY`.
- The **VFSC** publishes no website, scope or client-type field on either of its relevant registers.

A reader who takes a licence number as an answer to "is this firm authorised to offer me this product?" is, for these registers, taking it as an answer to a question the register does not ask.

### 4.2 Mismatch of instrument

**`fusionmarkets.com`, VFSC 40256.** The page displays 40256 as a company number. The number resolves **at number level** on two Vanuatu registers — and both publish it under a different company: the Financial Dealers Licensee List gives Date of License 6-Jan-23, Company Number 40256, Name of Licensee **Gleneagle Securities Pty Limited**, Class of License A, B, C, Status Active; the International Companies register gives GLENEAGLE SECURITIES PTY LIMITED (40256), Port Vila, Entity Status Registered, Registered 19-Apr-2017. A search of all four Vanuatu registers for "Fusion Markets" returns **No results found**.

We state this as a fact about two registers on 2026-08-02 and code it as an instrument mismatch. We do not characterise it further.

Separately, five units across the corpus display a **company-registry number in a licence-number position**; `identifier_kind` separates these from licence numbers so the two are never conflated.

### 4.3 Mismatch of scope, where the regulator says so itself

**`xs.com`, UAE SCA, 20200000339.** The page brands the authority as CMA. The register record for XSTRADE FINANCIAL CONSULTATION L.L.C is name-level exact; the number is `UNVERIFIABLE-TODAY` because the register's own key is CP-0001567 and **no licence-number field exists**. Licences granted are **Financial Consultations, Introduction, Promotion** — all Active, nothing else.

The regulator's own record page carries a Notice that the company *"is not licensed by the Securities and Commodities Authority (SCA) to conduct brokerage activities in financial derivatives contracts, unregulated commodity contracts, or spot foreign exchange (Spot FX) trading"* and *"holds only a Category 5 license"*.

This is the cleanest case in the corpus, because the scope determination is made by the regulator in the register itself. We reproduce it and add nothing.

Note also that the operative entity for `xs.com` is XS Ltd (Seychelles, OE-3), which is **not** the holder of either the FSCA or the SCA record.

### 4.4 Mismatch of domain, and the ASIC website-coverage audit

**`fusionmarkets.com`, ASIC, `anchor-no-number`.** The sentence ends "…Australian Financial Services License No" with no number, but carries ABN 74 146 086 017 in the same sentence. That ABN matches FMGP TRADING GROUP PTY LTD **digit for digit**, and FMGP is the operative entity. The register is informative here: conditions as at 21/10/2025 authorise **retail and wholesale clients on every row**, including issuing derivatives and FX contracts and making a market; AFSL 385620 CURRENT since 05/01/2011; name history GLOBAL PRIME PTY LIMITED to 13/08/2023; business names "Fusion Markets" (04/09/2023) and "Global Prime" (15/08/2023); AFCA member 24605.

But the principal website ASIC publishes is **`fusionmarkets.com.au`**, other website `globalprime.com.au` — **the observation domain `fusionmarkets.com` appears on neither.**

**`fpmarkets.com`, ASIC, `anchor-no-number`.** Searching ASIC for "FP Markets" returns **No results found**. The nearest name-level candidate is FIRST PRUDENTIAL MARKETS PTY LTD, AFSL 286354, CURRENT since 31/05/2005, whose conditions authorise dealing including issuing derivatives/FX/securities and market making to retail and wholesale clients — and whose principal website field reads "No website supplied". The registered business names are "FIRST PRUDENTIAL" and "FIRST PRUDENTIAL MARKETS"; **the string "FP Markets" is registered nowhere on the ASIC registers.** The operative entity for this domain is indeterminate, so the unit is coded `operative-indeterminate` and no attribution is made.

**Why the domain axis needs an audit before it can be used.** A domain mismatch is only evidence if the register's website field is reliable. It is not. Amendment 5 §3 therefore required an audit of ASIC's AFS-licensee website-address coverage before any domain-mismatch code could be assigned, and that audit (`artifacts/asic_website_coverage/`, checked 2026-08-02) establishes that supplying a website address is **voluntary** for AFS licensees. A licensee's absence from a website field is therefore not evidence of anything about that licensee, and the domain axis is reported descriptively rather than as a finding about any operator. Two contrasting rows in the corpus make the point: the FSA Seychelles row for `fusionmarkets.com` publishes the observation domain itself, and the row for `tradequo.com` publishes `https://www.tradequo.com` plus trade names TRADE QUO and QuoMarkets — both brand strings used on that page correspond to published trade names.

### 4.5 What F1 delivered, stated against ourselves

This is the section the frame's pre-registration obliged us to write. F1 was frozen before execution precisely so that its yield could be published whatever it turned out to be. It turned out badly.

Fourteen domains carry Chinese-language captures. **Chinese-language presence is not relevance, and the probe only measures the former.** Reading the stored sample URLs domain by domain:

| Domain | Read | Evidence (stored sample URLs only) |
|---|---|---|
| capital.com | FX/CFD broker | `/zh-hans/analysis/` — F2-reachable |
| markets.com | FX/CFD broker | `/zh/`, `/zh-tw/` — F2-reachable |
| m4markets.com | FX/CFD broker | already in the claim corpus |
| 3h-trading.com | plausible, unconfirmed | path `/fudengwangpeizi/` transliterates 配资 (margin financing) |
| gold-money.cn | plausible, unconfirmed | `/wp/` only |
| wh10176.cn | plausible, unconfirmed | generic CMS paths |
| world-trader.com | plausible, unconfirmed | root only, 2 captures |
| **wing-fx.com** | **not financial** | `/channel-fx/even-channel-strip`, `/master-channel-strip` — audio channel strips; the `fx` is *effects* |
| **canine-prime.com** | **not financial** | canine |
| **gold-skin.co.kr** | **not financial** | `cn.` subdomain of a Korean cosmetics domain |
| wh-hw.com | likely not financial | `wh-` reads as Wuhan (武汉), not waihui |
| wh-sinobest.com | likely not financial | "wh-sinobest" reads as Wuhan Sinobest |
| ks-wh.com.cn | likely not financial | `.com.cn`, `wh-` reads as Wuhan |
| wh-lz.com | likely not financial | `wh-` reads as Wuhan |

| Measure | Count | Rate |
|---|---|---|
| Chinese-presence hits | 14 / 979 | 1.43% |
| Relevant at best case (brokers + all four unconfirmed) | 7 / 979 | 0.72% |
| **Distinctive — relevant AND not F2-reachable** | **≤ 4 / 979** | **≤ 0.41%** |

The four unconfirmed domains have not had their content checked; the figures above are therefore upper bounds and a content check is required before they are final.

**The two short tokens are the failure mode.** `wh` was intended as the Pinyin initials of 外汇 and fires instead on Wuhan, a common prefix for companies in that city. `fx` fires on audio effects. Between them they account for five of the fourteen hits and none of the confirmed relevant ones.

**We do not remove them.** Removing tokens after seeing which domains they caught is exactly the retuning amendment 3 prohibits. The failure is reported as a property of the frozen instrument, which is the only way a pre-registered frame can produce an honest negative result.

The lesson generalises beyond this study: a short romanised token drawn from one language's transliteration will collide with place names, product categories and unrelated abbreviations at a rate that cannot be estimated from the vocabulary alone. It has to be measured, and the measurement has to be capable of coming back negative.

---

## 5. The amendment trail as method

Three extraction defects were found *after* the protocol was frozen, and each was corrected in the open with an ablation showing what it moved.

**Defect 1 — the fullwidth colon.** The Chinese identifier pattern's separator class was written `[为是::\s]`: the ASCII colon twice, and never U+FF1A, which is the character Chinese pages actually use. Every identifier introduced as `牌照编号：X` silently failed to attach to the authority named a few characters earlier in the same sentence. Two further same-sentence failures sat beside it: English identifier introducers had no pattern at all, and the Seychelles authority's English long forms were missing from the authority table.

The ablation is published in full: same-sentence authority–identifier pairs went 14 → 16 (identifier fix alone) → 16 (authority fix alone) → **19 (both)**, with the seven recovered pairs listed individually. Two pairs present before and absent after are also listed, because a correction that only adds is a correction that has not been checked.

**Defect 2 — non-self-referential sentences.** Described in §3.3.

**Defect 3 — completeness as a boolean.** Described in §3.3.

**A defect in the reporting layer, found while writing this paper.** The F1 probe's emitted summary carries the caveat "Service failures are not recorded, so absence in the file means not-yet-probed, never a silent failure." This is **false for the total-capture field**: when the Chinese-only query succeeds and the any-language query fails, the row is written with the failure downgraded to an empty string. 45 rows carry it, 44 of them in the sampled stratum. The primary endpoint is unaffected — presence is defined on the Chinese-only count alone, and that field is never downgraded — but the capture-count analysis in §3.2 is computed on 901 rather than 945 domains, and is reported on that basis. Amendment 6 records the corrected caveat text; the frozen file is not edited and the rows are not rewritten.

**A finding we got wrong in our own amendment, and corrected.** Amendment 6 as first committed asserted that two `wh-` domains were drawn by the Pinyin initials of 外汇 and that "the frozen vocabulary paid out on live data". Revision 1 of that amendment withdraws the claim: the inference was unsupported and is probably backwards (§4.5). The withdrawal is appended to the amendment rather than replacing its text, so that what was claimed and what survives are both on the record.

We report these because a protocol that only ever confirms itself has not been tested. Every correction above made the corpus **smaller or more qualified**, not larger.

---

## 6. Limitations

**6.1 No prevalence claim.** The corpus is not a probability sample. Nothing here supports a statement of the form "X% of retail FX sites do Y".

**6.2 F1's missingness is informative.** §3.2. The 190 timeouts are plausibly enriched for the outcome measured.

**6.3 Registers are snapshots.** Every fact is stated as of its check date. Several registers publish no permalink, so a future reader reproduces via the recorded recipe, not a URL. The ASIC Professional Registers Search states AFS licensee data is the latest available and other registers current as of 05:00 AEST 01 August 2026.

**6.4 Archive-only access for part of the corpus.** `web.archive.org` was not fetchable from the verification environment and three domains were additionally blocked live; those units rest on Common Crawl captures alone.

**6.5 N.** Twenty-one verified units across nine domains is small. The consequences are discussed in §7.

**6.6 We do not code contraventions.** No unit is coded as a breach of any provision. Amendment 5 bans citation of s 911A in coding for this reason: a determination that a person carried on a financial services business without a licence is not a measurement, and this study does not make it.

---

## 7. Reaching the pre-declared N floor — *deliberately unwritten*

The protocol declares a floor of 60 verified units. We have 21.

F1's distinctive usable yield is at most 4 domains in 979 (§4.5) — and each of those still has to survive extraction, self-reference filtering and register verification before it becomes a unit. Reaching 60 through F1 alone is not a matter of enlarging the draw by an order of magnitude; on this evidence the frame does not produce the input at all. **Enlarging F1 in response to a disappointing yield is in any case precisely the retuning amendment 3 prohibits**, and it is not done.

This section is left unwritten because the route to the floor is a design decision that must be made and recorded *before* it is executed, not narrated after. Candidate routes, none yet selected:

1. **Deepen within reached domains.** 37 units exist and 21 are verified; verifying the remainder is the cheapest path and adds no sampling frame.
2. **A third frame, pre-declared and frozen before execution**, targeting a stratum both F1 and F2 miss.
3. **Restate the floor with a published justification** — legitimate only if the restatement is argued on measurement grounds and recorded as an amendment, never as a silent adjustment.

Whichever is chosen becomes an amendment before any data is touched.

---

## 8. Data availability

`protocol/locked_protocol_v1.0.md` and amendments 1–6; `artifacts/frames/` (draw, probe, summary); `artifacts/claims/` (units, excluded sentences, vague assertions, operative candidates, fetch manifest, normalisation summary); `artifacts/verification_v1/` and `artifacts/verification_v2/` (register facts and reports); `artifacts/asic_website_coverage/` (audit, manifest, fingerprints). Bulk ASIC files are fingerprinted by SHA-256 rather than committed, and are re-downloadable from the URLs recorded in the fingerprint file.

---

## Appendix A — page-type distribution

| Page type | Distinct pages | Units appearing | Complete units |
|---|---|---|---|
| editorial | 282 | 23 | 12 |
| other | 80 | 20 | 7 |
| product-or-account | 26 | 18 | 7 |
| legal-or-corporate | 23 | 18 | 9 |
| home | 2 | 1 | 0 |

Editorial pages dominate the corpus by volume and carry the most unit observations (578 of 763), which is exactly why the self-reference filter of §3.3 is load-bearing rather than cosmetic.
