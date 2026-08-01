# REF-2026-019 — Stage-4 Verification Report, batch v2

**Protocol:** locked_protocol_v1.0.md (taxonomy §3, two-step verification §6, operative-entity rule §5, language discipline §8)
**Verification date for all register facts in this batch:** 2026-08-02
**Verified claim units in this batch:** 7, across 4 brand domains
**Units carried forward unchanged from batch v1:** 14 (not re-checked; see `artifacts/verification_v1/`)

---

## 1. Why this batch exists

Batch v1 verified the 14 claim units that the stage-3 normaliser had marked complete. Inspection of the normaliser then found two defects and one schema conflation:

1. **Same-sentence identifier pairing failed.** The Chinese identifier pattern's separator class was written `[为是::\s]` — the ASCII colon twice, and never the fullwidth colon U+FF1A, which is the character Chinese pages actually use. Every identifier introduced as `牌照编号：X` failed to attach to the authority named a few characters earlier in the same sentence. Two further same-sentence failures sat alongside it: English identifier introducers had no pattern at all, and the Seychelles authority's English long forms were missing from the authority table, so sentences naming both the authority and the SD number were recorded as a number with no authority.
2. **Non-self-referential sentences were entering the frame.** The corpus is 413 pages of which 282 are editorial, and reader advice, conditionals, questions, third-party comparisons and definitions from those pages were being counted as claims about the operator.
3. **Completeness was a single boolean**, so "the page names an authority and publishes no number anywhere" — the frozen taxonomy's codeable `anchor-no-number` observation — could not be told apart from "the number is on the page but in another sentence" or from "the extraction window cut the number off".

After the fixes, complete units went from 14 to 19 and the total unit count from 43 to 37 (bare identifier fragments now fold into the complete unit carrying the same string). All 14 v1 claim ids survive under their existing ids and are **not** re-verified here. Five units became complete for the first time, and the two ASIC units that the fixes reclassified as codeable anchor observations were verified at name level as well, giving the 7 units below.

Two units that existed in the previous table were **withdrawn** by the self-reference filter and are therefore not verified. They are recorded in `register_facts.json` under `units_withdrawn_by_self_reference_filter` so the withdrawal is visible rather than silent:

| Withdrawn unit | Sentence | Filter reason |
|---|---|---|
| zfx.com FCA | 然而，它的严肃性是不容置疑的，因为它受到英国金融行为监管局的监管 — on an academy page about the CAC 40 index | `anaphoric-third-party`: the subject is the anaphor 它, no legal entity and no brand token appears |
| fxcentrum.com FCA | 提示 1：…务必核实该平台是否受 FCA 或同等机构监管… and 受 FCA 监管的经纪商通常能为英国客户提供更严格的监管… | `reader-advice` and `generic-class-subject`: advice to the reader, and a generalisation about FCA-regulated brokers as a class |

Neither predicates regulatory status of the operator or its group, so neither is a unit of analysis under §5. zfx.com now carries **no** claim unit at all; its regulatory assertions in the corpus are the operative sentence naming Zeal Capital Market (Seychelles) Limited and a bare `受FSA监管` footer string that names no resolvable authority and sits in the manual queue.

---

## 2. Fact table

| # | Claim id | Brand domain | Authority | Identifier | (i) Record exists | Official holder name | (ii) Name match | Holder = operative entity? | Scope / approved-domain / status (register-published only) |
|---|---|---|---|---|---|---|---|---|---|
| 15 | xs-FSCA-FSP53199 | xs.com | FSCA (ZA) | 53199 | Yes, exactly 1 FSP | XS ZA (PTY) LTD | exact (case only) | **No** — OE is XS Ltd | Category I. Approvals marked **only** in "Intermediary Other" for Derivative instruments, Long-term Deposits and Short-term Deposits; "Advice Automated", "Advice Non-automated" and "Intermediary Scripted" blank on every row. No client-type or territorial field published → client scope UNVERIFIABLE-TODAY. Status "Authorized", date authorised 17/10/2023, SA company reg. 2023/608801/07. No trading name, no website field → approved domain UNVERIFIABLE-TODAY. One key individual; no representatives. |
| 16 | xs-SCAAE-20200000339 | xs.com | UAE SCA (site branded CMA) | 20200000339 | Name-level **yes**; number-level **UNVERIFIABLE-TODAY** | XSTRADE FINANCIAL CONSULTATION L.L.C | exact (case/spacing) | **No** — OE is XS Ltd | Licences granted: **Financial Consultations, Introduction, Promotion** — all Active, nothing else. Accredited-employee category "Fifth category: Arrangement and advice". The record page carries a regulator Notice that the company "is not licensed by the Securities and Commodities Authority (SCA) to conduct brokerage activities in financial derivatives contracts, unregulated commodity contracts, or spot foreign exchange (Spot FX) trading" and "holds only a Category 5 license". Status Active, established 24-Apr-2025, Dubai. No approved-domain field; register contact email `superusersca@xs.com` is on the observation domain. Register's own key is CP-0001567; no licence-number field exists. |
| 17 | fusionmarkets-FSASC-SD096 | fusionmarkets.com | FSA Seychelles | SD096 | Name-level **yes**; number-level **UNVERIFIABLE-TODAY** | Fusion Markets International Ltd | exact | **No** — OE is FMGP Trading Group Pty Ltd (see caveat §4) | Scope/status/dates not published by this register. Register publishes **https://fusionmarkets.com** — the observation domain — against this holder, plus address and email. This row carries **no trade-name field, no telephone and no associated-individual field**, unlike the Trade Quo row on the same register. A sweep of the whole register page for SD-number strings returned zero matches. |
| 18 | fusionmarkets-VFSC-40256 | fusionmarkets.com | VFSC (Vanuatu) | 40256 (page calls it a company number) | **Yes, at number level** | **Gleneagle Securities Pty Limited** | **No** — the registers publish this number under a different company name | **No** under every page-named candidate | VFSC Financial Dealers Licensee List row: Date of License 6-Jan-23, Company Number 40256, Name of Licensee "Gleneagle Securities Pty Limited", Class of License "A, B, C", Status "Active". Vanuatu International Companies register: "GLENEAGLE SECURITIES PTY LIMITED (40256), Govant Building, Kumul Highway, 1st Floor, Port Vila. Entity Status Registered. Registered Date 19-Apr-2017." A search of all four Vanuatu registers for "Fusion Markets" returns **No results found**. No website, scope or client-type field on either register. |
| 19 | fusionmarkets-ASIC-nonumber | fusionmarkets.com | ASIC (AU) | not in corpus — sentence ends "…Australian Financial Services License No"; ABN 74 146 086 017 is in the same sentence | Yes | FMGP TRADING GROUP PTY LTD | exact, **and the ABN matches digit for digit** | **Yes** (see caveat §4) | Conditions as at 21/10/2025: **retail and wholesale clients on every row**, including issuing derivatives and FX contracts and making a market. Status CURRENT, AFSL 385620 commenced 05/01/2011, ABN 74 146 086 017, ACN 146 086 017. Name history GLOBAL PRIME PTY LIMITED to 13/08/2023. Principal website **https://fusionmarkets.com.au**, other website globalprime.com.au — the observation domain fusionmarkets.com appears on neither. Business names "Fusion Markets" (04/09/2023) and "Global Prime" (15/08/2023). AFCA member 24605. A second record for the same name on the authorised-representatives register is Ceased. |
| 20 | tradequo-FSASC-SD140 | tradequo.com | FSA Seychelles | SD140 | Name-level **yes**; number-level **UNVERIFIABLE-TODAY** | Trade Quo Global Ltd | exact | **Indeterminate** — no OE rung resolves | Scope/status/dates not published. Register publishes "Trade Name: TRADE QUO, QuoMarkets", telephone, email admin@tradequo.com and website **https://www.tradequo.com** — the observation domain — plus an associated individual. Both brand strings used on the page correspond to published trade names. |
| 21 | fpmarkets-ASIC-nonumber | fpmarkets.com | ASIC (AU) | **none on the page** (`anchor-no-number`) | **No record under the displayed brand string** | no ASIC record named "FP Markets"; nearest name-level candidate FIRST PRUDENTIAL MARKETS PTY LTD, AFSL 286354 | n/a — the page names no entity for this element | **Indeterminate** — OE unresolved in v1 | Search "FP Markets" → "No results found." Search "First Prudential" → 10 records, of which one current AFS licensee. Candidate record: status CURRENT, AFSL 286354 commenced 31/05/2005, ABN 16 112 600 281; conditions as at 13/11/2017 authorise advice, dealing including issuing derivatives/FX/securities, and market making **to retail and wholesale clients**. Principal website field reads "No website supplied". Business names registered: "FIRST PRUDENTIAL" and "FIRST PRUDENTIAL MARKETS" — the string "FP Markets" is registered nowhere on the ASIC registers. AFCA member 12084. |

### Register sources actually checked (all 2026-08-02)

| # | Register URL(s) / reproduction recipe |
|---|---|
| 15 | `https://www2.fsca.co.za/Fais/Search_FSP.htm` → POST `https://www2.fsca.co.za/MagicScripts/mgrqispi.dll` with `APPNAME=Web`, `PRGNAME=Display_Search_Results`, `ARGUMENTS=Search_FSP_No,Search_FSP_Name,Search_FSP_Postal_Code,Search_Rep_ID`, `Search_FSP_No=53199`; then `PRGNAME=Display Details`, `ARGUMENTS=FSP_No`, `FSP_No=53199`. **No GET-addressable permalink exists per FSP** — this recipe replaces the citation, as v1 open item 9 required. |
| 16 | `https://www.uaecma.gov.ae/en/open-data/licensed-companies.aspx` (list, searched "XS" → exactly 1 match) → `https://www.uaecma.gov.ae/en/open-data/licensed-companies?q=CP-0001567` |
| 17, 20 | `https://fsaseychelles.sc/regulated-entities/capital-markets` (Securities Dealers section) |
| 18 | `https://www.vfsc.vu/financial-dealers-licensee-list/` and `https://registry.vfsc.vu/vanuatu-master/` Entity Search (queries `40256` and `Fusion Markets`, register `-- All Registers --`) |
| 19 | `https://service.asic.gov.au/search/` (search "FMGP Trading Group Pty Ltd") → `https://service.asic.gov.au/search/EntityDetail?LicenceNumber=385620&PermissionType=Australian%20financial%20services%20licensees&licenceName=FMGP%20TRADING%20GROUP%20PTY%20LTD` |
| 21 | `https://service.asic.gov.au/search/` (searches "FP Markets" and "First Prudential") → `https://service.asic.gov.au/search/EntityDetail?LicenceNumber=286354&PermissionType=Australian%20financial%20services%20licensees&licenceName=FIRST%20PRUDENTIAL%20MARKETS%20PTY%20LTD` |

No third-party site was used to establish any fact in this batch. The ASIC Professional Registers Search states that AFS licensee data is the latest available and that all other registers are current as of 5:00 AM AEST 01 August 2026.

---

## 3. Coding table

| # | Claim id | Primary class | Sub-codes / qualifiers | Justification tied to the facts |
|---|---|---|---|---|
| 15 | xs-FSCA-FSP53199 | **B** | B-portfolio; scope-observation | FSP 53199 exists and is held by XS ZA (PTY) LTD; the operative entity for xs.com is XS Ltd (Seychelles, OE-3) — a different entity in the same group. Every product approval on the licence sits in the "Intermediary Other" column with both advice columns blank, the same structural pattern recorded for fpmarkets FSP 50926 in v1. |
| 16 | xs-SCAAE-20200000339 | **B** | B-portfolio; scope-observation; identifier-not-published | An entity of exactly the displayed name is on the UAE regulator's licensed-companies register with Financial Consultations, Introduction and Promotion active; the operative entity for xs.com is XS Ltd — a different entity. The register displays a Notice on this record stating the holder is not licensed for spot-FX or derivatives brokerage and holds only a Category 5 licence. **The same Notice text appears on at least one other Category 5 record** (ATFX MENA, pilot claim AE-1), so it is recorded as a category-level notice the register publishes, not as a company-specific finding. The claimed number cannot be tested: the register exposes no licence-number field. |
| 17 | fusionmarkets-FSASC-SD096 | **B** | B-portfolio; identifier-not-published; verification level: name-level only | Fusion Markets International Ltd is on the Seychelles Securities Dealer register and the register publishes the observation domain against it; the operative entity recorded for the domain in v1 is FMGP Trading Group Pty Ltd (Australia, OE-2) — a different entity. SD096 itself is unverifiable: this register publishes no numbers. |
| 18 | fusionmarkets-VFSC-40256 | **B** | B-portfolio; identifier resolvable at number level; **B-mis-anchor considered and NOT asserted** | The page states that the brand is a registered Vanuatu company with company number 40256 and is regulated by the VFSC. Both Vanuatu registers publish that number against a company registered as Gleneagle Securities Pty Limited, and the VFSC financial-dealers licence carrying it (Class A, B, C, Active, 6-Jan-2023) stands in that name. No Vanuatu register carries any entity named "Fusion Markets". The holder of record is therefore a different entity from the brand the page names and from the domain's operative entity. B-mis-anchor is **not** asserted: the page calls 40256 a company number, which is what it is, and the VFSC's own licence list is keyed on company number — the anchor is accurate and resolvable, it simply resolves to a differently named holder. Whether the two companies are related is not determinable from these registers and is not asserted. |
| 19 | fusionmarkets-ASIC-nonumber | **A** | identifier-truncated-at-extraction; jurisdictional-qualifier | AFSL 385620 is current and held by FMGP TRADING GROUP PTY LTD, which is the operative entity for the domain under v1's OE-2, and the ABN printed on the page matches the register's ABN digit for digit, so the record is identified even though the page-side licence number was clipped by the stage-2 extraction window. Client scope is retail and wholesale across issuing derivatives and FX, so there is no scope divergence. Recorded because it goes to the study's core question: the sentence carrying this claim begins **"Australian Clients Only:"**, and two further sentences in the same footer assign a Seychelles and a Vanuatu entity to other readers. |
| 20 | tradequo-FSASC-SD140 | **D-operative-indeterminate** | multi-entity; identifier-not-published; verification level: name-level only | Trade Quo Global Ltd is on the Seychelles register, its published trade names are "TRADE QUO" and "QuoMarkets" and its published website is the observation domain — all three corroborate the page. But no operative-entity rung resolves: no trading-name or site-operator sentence was captured, and the archived pages name three entities (Trade Quo Global Ltd, Quo Markets LLC, Tqbg Ltd). **OE-1 or OE-2 would resolve it:** Trade Quo Global Ltd → class A; either of the other two → class B. Coded D rather than assigned, per the frozen rule. |
| 21 | fpmarkets-ASIC-nonumber | **D** | anchor-no-number; D-operative-indeterminate; brand-string-absent-from-register | A genuine anchor-no-number observation: the page asserts ASIC regulation for the brand with no number and no entity for that element, and no ASIC-compatible identifier appears anywhere on that page. Step (i) can only be run at brand-string level, where ASIC's search returns no record for "FP Markets"; a current name-level candidate exists under a different name (FIRST PRUDENTIAL MARKETS PTY LTD, AFSL 286354), whose registered business names are "First Prudential" and "First Prudential Markets". Step (ii) is not performable — the page names no entity. The operative entity for fpmarkets.com was indeterminate in v1. No inference is drawn from the similarity of the two brand strings. |

---

## 4. Coding caveat that a reader must see: fusionmarkets.com's operative entity

Units 17, 18 and 19 are all coded against the operative entity recorded for fusionmarkets.com in verification_v1: **FMGP Trading Group Pty Ltd, OE-2, footer trading-name sentence.** The sentence that supplies that determination reads, in full as captured:

> "Australian Clients Only: Fusion Markets is a trading name of FMGP Trading Group Pty Ltd (ABN 74 146 086 017) and is regulated by ASIC and licensed to carry on a financial services…"

The rung is expressly scoped to Australian clients, and the same footer carries two further entity sentences — one naming the Seychelles securities dealer, one naming the Vanuatu company — that are not so scoped. For a Chinese-language reader, OE-2 arguably does not resolve to a single entity at all; this is exactly the multi-entity situation §5's ladder exists to settle, and it settles it only if one footer sentence is unqualified. The v1 determination is left untouched and used as recorded, but the sensitivity is stated here:

- If OE-1 confirms **FMGP Trading Group Pty Ltd** for a Chinese-language visitor: 19 = A, 17 = B, 18 = B (as coded).
- If OE-1 resolves to **Fusion Markets International Ltd** (Seychelles): 17 = A, 19 = B, 18 = B.
- If OE-1 resolves to the **Vanuatu** entity: 18 becomes a question of whether the operative company is the one bearing number 40256; 17 and 19 = B.

Unit 18 is class B under every one of these resolutions, because no Vanuatu register carries any entity named "Fusion Markets" and the holder of record is Gleneagle Securities Pty Limited under all three. Units 17 and 19 are the ones that move.

---

## 5. Prevalence summary — verified units only

**This batch (v2), N = 7**

| Class | Units | Share of 7 |
|---|---|---|
| **A** direct-licensed | 1 | 14.3% |
| **B** cross-entity licence-borrowing | 4 | 57.1% |
| **C** clone/fabricated | 0 | 0.0% |
| **D** unverifiable (incl. D-operative-indeterminate) | 2 | 28.6% |

**Combined v1 + v2, N = 21**

| Class | Definition (protocol §3) | v1 | v2 | Total | Share of 21 |
|---|---|---|---|---|---|
| **A** direct-licensed | record exists AND holder = operative entity | 2 | 1 | **3** | 14.3% |
| **B** cross-entity licence-borrowing | record exists, holder is a different entity from the operative one | 8 | 4 | **12** | 57.1% |
| **C** clone or fabricated | record does not exist, or is demonstrably unrelated | 0 | 0 | **0** | 0.0% |
| **D** unverifiable | including D-operative-indeterminate | 4 | 2 | **6** | 28.6% |
| | | 14 | 7 | **21** | 100% |

Sub-code frequencies across the 12 class-B units: B-portfolio 12/12; approved-domain divergence 3; scope observation or mismatch 5; status-not-current 1; identifier not published by the register 5. B-false-anchor: 0 observed. B-mis-anchor: 0 asserted (two candidates raised, v1 #10 left open and v2 #18 explicitly withdrawn on the evidence). `anchor-no-number`: 1 unit (v2 #21), the first in the study.

Verification depth across the 21 units: **number-level two-step completed for 9** (FCA ×2, ASIC ×2, CySEC ×2, FSCA ×2, VFSC ×1 — the VFSC unit being the first offshore register in the study able to support it); **name-level only for 10** (Seychelles ×5, Mauritius ×3, Labuan ×1, UAE ×1); **one** (#19) resolved by the ABN printed in the same sentence rather than by a licence number, because the page-side number was clipped at extraction; and **one** (#21) with no identifier on the page and no record under the displayed brand string.

**Explicit limitation.** N = 21 verified claim units. The protocol's target sample is **N = 80 with a 60-unit floor**, so this stands at **35.0% of the floor and 26.3% of the target**. These counts and shares describe the verified units only. They are **not a population estimate** and must not be read as a rate for the sector, for Chinese-language broker pages generally, or for any register's licensee base. Four further reasons the shares are not projectable: (a) the units are not independent — 7 of 21 come from one domain (xs.com) and 3 from another (fusionmarkets.com), so the unit-level share is partly a function of how many authorities each page displays; (b) selection was archive-driven rather than random; (c) the class shares in this batch are numerically identical to v1's, which is a coincidence of small numbers and carries no evidential weight; and (d) class C's zero count still carries no information about C's prevalence, especially because four of the nine registers used across both batches publish no licence numbers, structurally preventing the number-level test that most often discriminates C from B.

---

## 6. What this batch added to the method

**A register that can actually discriminate B from C offshore.** The **VFSC financial-dealers licensee list is the first offshore register in this study that publishes an identifier-to-holder mapping** for an identifier the pages themselves display: its five columns include *Company Number*, and the Vanuatu company register resolves the same number independently. Seychelles, Mauritius and Labuan publish none. That is why unit 18 is the only offshore unit so far resolved at number level rather than name level, and it is the direct counter-example to the industry claim that IOSCO FR12/22 Measure 7's "open register" is operationally infeasible: a jurisdiction with 66 licensed dealers already runs one.

**Register-side scope, again the sharpest field.** Two of the four new class-B units turn on what the register publishes about scope rather than on existence: an FSCA Category I approval marked only in "Intermediary Other" with both advice columns blank, and a UAE record whose granted activities are Financial Consultations, Introduction and Promotion, displayed with a standing notice that the licence does not authorise spot-FX or derivatives brokerage. Neither fact is visible from the page.

**The self-reference filter changed the frame, not just the count.** Of 562 predicating sentence hits tested, 70 (12.5%) were excluded and 15 (2.7%) queued for manual decision. Only 4 excluded hits were unit-bearing — but those 4 were the whole of two units, both FCA claims, both on editorial pages, and both would have gone to a UK register lookup that had nothing to do with either operator. 63 of the 70 excluded hits are on editorial pages. The corresponding positive finding is that **page type must not be used as a filter**: xs.com's seven units are all carried on 40 blog pages, because the claims sit in a site-wide footer. Excluding blog pages would have deleted a third of the study's verified units.

**The FSCA reproducibility defect now has a recipe.** v1 open item 9 asked for one; §2 of this report records the exact POST fields, since the register has no per-FSP permalink.

---

## 7. Open items carried forward

Items 1–11 of the v1 report stand except where noted. New or changed:

1. **Obtain OE-1 for fusionmarkets.com.** It is now the highest-value single determination in the study: it moves two coded units and it tests the "Australian Clients Only" qualifier directly (§4).
2. **Obtain OE-1/OE-2 for tradequo.com.** Three entity names appear on the archived pages; the register-published trade names and website both point at Trade Quo Global Ltd, which would make unit 20 the study's fourth class-A unit.
3. **v1 open item 9 (FSCA reproducibility) is closed** — the POST recipe is recorded in §2.
4. **Extend the identifier grammar to acronym-introduced numbers.** One corpus string is still unread: `FSA: 3171` on tradequo.com, the only `AUTHORITY: number` form in the whole corpus that the current patterns miss. Left unchanged deliberately — a bare "FSA" is ambiguous across Seychelles, SVG and Japan, and the protocol's B-false-anchor sub-code exists precisely because that ambiguity is itself a finding. Resolve it by determining which authority the page means before adding a pattern.
5. **Decide the treatment of multi-authority sentences.** `find_authority` takes the first authority in a sentence, so `FP Markets 是一个受多重监管的品牌，获得 ASIC、CySec、FSCA…` yields one unit, not three. This under-counts B-portfolio by construction. Changing it would materially change the unit population and should be an explicit, recorded decision rather than a silent patch.
6. **Two identifiers are extraction-truncated, not absent:** fusionmarkets' AFSL (recovered here via the ABN) and dbinvesting's `许可证号 20200000`, which is exactly eight digits — the stage-2 `licence_no` pattern's ceiling — while xs.com's UAE number in the same series is eleven digits. Re-extraction with a wider window would settle whether dbinvesting's UAE number is also truncated.
7. **The stage-2 extractor carries the same fullwidth-colon typo** in its `licence_no` pattern. It did not cost this study any data, because the recall-oriented `regulated_cn` pattern captured the same sentences whole, but it should be corrected before the next crawl. Not corrected in this pass because re-running stage 2 requires refetching WARC records and the corpus is pinned to CC-MAIN-2026-25.

---

## 8. Language discipline statement (§8)

Every finding above is stated as what a page displays and what a register publishes, with the register URL and the check date. Class B is reported as an observable entity relationship — the licence is held by an entity other than the one recorded as operative for the domain — and no brand in this study is described as fraudulent, fake, misleading or a scam. Where a register publishes no field capable of testing a claim, that is recorded as UNVERIFIABLE-TODAY and never as absence. Where a mechanical sub-code flag was not borne out by the register evidence (unit 18's `candidate-B-mis-anchor`), the flag is withdrawn in writing rather than left standing.
