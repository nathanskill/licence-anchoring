# REF-2026-019 — Secondary analysis: coverage audit of ASIC's AFS-licensee website-address field

**Mandate:** `protocol/amendments/amendment_5_mismatch_structure_and_evidence_rules.md` §3
**Protocol:** `locked_protocol_v1.0.md` (register verification §6, language discipline §8); amendment 5 §2 (instruments), §4.1–4.2 (evidence rules)
**Check date for every fact in this report:** 2026-08-02
**Units audited:** 4 — every verified claim unit in `verification_v1` + `verification_v2` whose displayed authority is ASIC
**Population coverage rate:** not obtainable; see §3

---

## 1. The premise, verified against ASIC's own documents

Amendment 5 §3 was written from a secondary report. Before anything was built on it, every element was checked against the primary sources. **No element of the premise was wrong.**

| Element as recorded in amendment 5 | What ASIC's own documents say | Verdict |
|---|---|---|
| Media release 26-122MR, 17 June 2026 | "Published 17 June 2026" | confirmed |
| AFS licensees' website addresses added to the professional registers | "ASIC is collecting and publishing website addresses of AFS licensees on its Professional Registers Search (PRS)" | confirmed |
| Collection opened 4 May 2026 | "From **4 May 2026**, ASIC will begin to collect AFS licensee website addresses"; "ASIC will start collecting website addresses from 4 May 2026" | confirmed — the exact date is on the guidance page; the media release says only "since launching in early May" |
| Publication from June 2026 | "commenced displaying the website addresses on the PRS **from June 2026**" | confirmed |
| Over 6,500 licensees invited | "more than 6,500 AFS licensees invited to provide their website details since launching in early May" | confirmed; independently corroborated — the data.gov.au AFS Licensee snapshot of 2026-07-29 carries **6,525** AFS Licence rows |
| Supply is voluntary | "ASIC will begin to collect AFS licensee website addresses for all existing AFS licensees via the Regulatory Portal **on a voluntary basis**" | confirmed |
| Authorised representatives out of scope | "Website addresses for authorised representatives are not included in the initiative." The guidance page adds that it does not apply to Australian Credit Licensees, authorised representatives or other non-licensed entities "at this time" | confirmed |
| Stated purpose includes digital and social media platforms | "It will also support businesses, **including digital and social media platforms**, to strengthen verification processes for financial services advertising." | confirmed verbatim |

**Sources.** ASIC media release 26-122MR, `https://www.asic.gov.au/about-asic/news-centre/find-a-media-release/2026-releases/26-122mr-asic-helps-strengthen-the-fight-against-imposter-scams-in-financial-services/`, retrieved 2026-08-02 (`raw/mr_26-122mr.html`). ASIC, *AFS licensees: Providing and updating website addresses through the Regulatory Portal*, `https://www.asic.gov.au/for-finance-professionals/afs-licensees/changing-details-and-lodging-afs-forms/afs-licensees-providing-and-updating-website-addresses-through-the-regulatory-portal/`, retrieved 2026-08-02 (`raw/afs_website_addresses_portal.html`).

**Three things the amendment did not record, which the primary documents do.** These are additions, not corrections.

1. **Voluntariness is expressly conditional.** ASIC states: "We may consider using compulsory powers to achieve a complete register, if required." Amendment 5 treats voluntary supply as a fixed property of the mechanism; on ASIC's own account it is a current setting.
2. **The field is tri-state, not binary.** ASIC states the PRS shows (a) a principal website and other websites if provided, (b) whether a licensee **does not operate** a website, and (c) whether a licensee **has not yet supplied** addresses. Coverage therefore has three cells, and "no website shown" is not by itself evidence of non-participation.
3. **ASIC's own FAQ promises a bulk route.** "How can businesses and consumers get a downloadable list of all AFS Licensee website addresses? Data will be available to download as a list via the Australian government's data.gov.au." As at 2026-08-02 the website field is not in that dataset — see §3.

**Evidence rules.** Amendment 5 §4.1: the release is dated 17 June 2026, before the 2 August 2026 retrieval date — admissible. §4.2: no trade-press characterisation is relied on anywhere in this report; every element above comes from ASIC's own pages.

---

## 2. Where the data lives, and what is machine-readable

### 2.1 Per-licensee lookup — the only place the field exists

The website field is published on the **ASIC Professional Registers Search**, `https://service.asic.gov.au/search/`. Observed structure:

- a **Principal website** line in the record summary; and
- a **Websites** section carrying "Principal website" and "Other websites", which is rendered **only where the licensee holds more than the principal address** — it is absent from the two records showing no website and from the record showing a principal website alone.

Three properties limit what can be done with it:

- **The register is a client-rendered application.** The HTTP response body for a record URL is a 2,217-byte shell containing no register data (`raw/prs_374409.html`). All register content arrives from a separate call after script execution.
- **The underlying JSON endpoint refuses non-browser clients.** `POST /search/screenservices/Search/Detail/EntityDetail/DataActionGetEntityDetail` returns a structured `Website` object (`HasWebsite`, `PrincipalWebsiteUrl`, `WebsiteUrlSummary`) to the application, and **HTTP 403** to a direct request (`raw/prs_screenservice_endpoint_response.html`). It was not circumvented. The free-text search is reCAPTCHA-protected.
- **The website field is not searchable.** Searching the exact string the register itself publishes as AFSL 385620's principal website — `fusionmarkets.com.au` — returns **"No results found."** (`raw/prs_search_domain_fusionmarkets_com_au.txt`). The search accepts name, licence number, registration number, ACN or ABN. Domain → licensee reverse lookup is not supported.

### 2.2 Bulk / downloadable form — does not carry the field

ASIC publishes 12 datasets on data.gov.au. The relevant one is **`asic-afs-licensee`** (*ASIC – Australian Financial Services Licensee Dataset*), refreshed weekly. The snapshot parsed here is `afs_lic_202607.csv`, resource `last_modified` 2026-07-29, sha256 `3876269a…`:

| Property | Value |
|---|---|
| Columns | **13** |
| Column names | `REGISTER_NAME`, `AFS_LIC_NUM`, `AFS_LIC_NAME`, `AFS_LIC_ABN_ACN`, `AFS_LIC_START_DT`, `AFS_LIC_PRE_FSR`, `AFS_LIC_ADD_LOCAL`, `AFS_LIC_ADD_STATE`, `AFS_LIC_ADD_PCODE`, `AFS_LIC_ADD_COUNTRY`, `AFS_LIC_LAT`, `AFS_LIC_LNG`, `AFS_LIC_CONDITION` |
| Data rows | **6,525** |
| Website column | **none** |
| TSV and XLSX variants | identical 13-column schema |
| Dataset's own documented field list | does not mention a website field |

**So:** what is machine-readable is the AFS licensee register *minus* the website field — a weekly 6,525-row CSV. What is not machine-readable is the website field itself. **Two months after publication began, the downloadable list ASIC's FAQ describes is not there.**

---

## 3. Population coverage rate — not obtainable, and what would fix that

**No coverage rate is reported, because none can honestly be computed.** The share of AFS licensees that have supplied a website is the headline number the mechanism's stated purpose calls for, and nobody has published it — ASIC included. Producing it from the register as currently published would require roughly 6,525 individual lookups against a reCAPTCHA-protected application. This audit does not do that, and records the gap instead.

What would make the number computable, in order of cost:

1. **Add the website columns to the existing weekly data.gov.au dataset.** Three fields suffice: principal website, other websites, and the supply-status flag distinguishing *provided* / *does not operate a website* / *not yet supplied*. The dataset, its cadence and its 6,525-row frame already exist; ASIC's own FAQ already states the data "will be available to download as a list via data.gov.au". This turns the coverage rate into a one-line computation, recomputable weekly by anyone.
2. **Or a documented public read API** for the website field on the PRS.

Either route also enables the reverse lookup identified in §2.1, which is the operation the stated purpose actually describes.

---

## 4. Unit-level results

The four ASIC units are the complete set across both verification batches, confirmed by enumerating all 21 verified units. Full data: `per_unit_website_coverage.csv`.

| # | Claim unit | Observation domain | Licensee on the register | AFSL | Register website field | Relationship |
|---|---|---|---|---|---|---|
| 1 | `xs-ASIC-374409` | xs.com | XS PRIME LTD (CURRENT) | 374409 | **"No website supplied"** | **ABSENCE** |
| 2 | `iux-ASIC-529610` | iux.com | IUX MARKETS AU PTY LTD. (CURRENT) | 529610 | `https://iux.com.au/en` | **MISMATCH** |
| 3 | `fusionmarkets-ASIC-nonumber` | fusionmarkets.com | FMGP TRADING GROUP PTY LTD (CURRENT) | 385620 | principal `https://fusionmarkets.com.au`; other `https://globalprime.com.au` | **MISMATCH** |
| 4 | `fpmarkets-ASIC-nonumber` | fpmarkets.com | no record under the displayed brand string ("FP Markets" → "No results found.") | none on page | n/a | **NOT APPLICABLE** |

**Totals: matches 0 · mismatches 2 · absences 1 · not applicable 1.**

Reported separately, as the amendment requires:

- **Match** — the observation domain appears in the register's website field for the licensee whose licence the page displays. **Zero units.**
- **Mismatch** — the register publishes at least one website for the licensee and the observation domain is not among them. **Units 2 and 3.**
- **Absence** — the register publishes no website for that licensee, so it makes **no statement either way** about the observation domain. **Unit 1.** This is a statement about the register's published fields, not about the domain.
- **Not applicable** — unit 4 is the study's `anchor-no-number` observation: the page names ASIC with no licence number and no entity, so there is no licensee record whose website field could be compared. Recorded separately: the nearest name-level candidate identified in `verification_v2`, FIRST PRUDENTIAL MARKETS PTY LTD (AFSL 286354, CURRENT), publishes "No website supplied". No inference is drawn from the similarity of the two brand strings.

Among the four licensee records actually looked up, **two publish a website and two do not** (529610 and 385620 supplied; 374409 and 286354 not).

**The observation that matters most is on unit 3.** `fusionmarkets-ASIC-nonumber` is the one ASIC unit where the licence holder *is* the operative entity for the domain — it is coded **class A** in `verification_v2`. Its observation domain still does not appear in the register's website field, because the register publishes the licensee's **.com.au** address and the Chinese-language observation domain is the **.com**. The same .com / .com.au split appears at unit 2. This is a property of what the field records — a licensee's own Australian-facing addresses — and not a finding about either firm. It bears directly on the mechanism's usefulness for the audience this study observes: a Chinese-language page can display a genuine AFSL held by the entity that in fact stands behind it, and the register's website field will still not corroborate the domain.

**Tri-state limitation.** For both records showing no website, the PRS displays the string "No website supplied". Which of ASIC's two published non-supply states applies — *does not operate a website* or *has not yet supplied* — is **UNVERIFIABLE-TODAY** from the rendered field. In the one record where the underlying payload was observable (374409) the `HasWebsite` flag was empty, which is consistent with "not yet supplied" but is not asserted as a finding.

---

## 5. Limitations

**N = 4. This is not a population estimate.** Four units, drawn from three brand domains, selected because they are the ASIC-authority units the study had already verified — not by any sampling rule. The counts in §4 describe these four units and nothing else. They are **not** a rate for AFS licensees, for the retail FX/CFD sector, or for any register's licensee base, and they carry no information about the coverage of ASIC's new field.

**No population estimate was possible**, because no bulk source exposes the field (§3). Had one existed, the coverage rate would have been computed against the full 6,525-row frame and reported as the headline number; it is recorded as not obtainable rather than approximated.

**Unit dependence.** Two of the four units come from domains that carry several other authority claims each, so the unit is a *display*, not a firm.

**Two register facts carried forward, not re-derived.** The operative-entity determinations and the A/B/C/D codings are those of `verification_v1` and `verification_v2`; this analysis adds only the website field and does not revisit any coding.

---

## 6. Two structural gaps in the mechanism, and a third observed here

Stated as observations about the mechanism. None of this is a criticism of any firm, and none of it bears on whether any firm has complied with anything.

1. **Supply is voluntary, so coverage is unknown.** Two of the four ASIC licensee records this study looked up publish no website. Because the field is absent from every bulk source, no one outside ASIC can state the coverage rate, and ASIC has not published one. The gap between "more than 6,500 invited" and an unknown number supplied is the whole of the mechanism's current reliability, and it is unmeasurable from outside. ASIC states it may consider compulsory powers if required.

2. **Authorised representatives' websites are out of scope.** This study's own frame shows why that boundary is load-bearing: authorised-representative records appear against these licensees, and `verification_v2` recorded a second, *ceased* record for one of them on the authorised-representatives register. A domain operated under an AR appointment cannot be checked against this field at all — and the study's `verification_v1` batch already contains a unit whose underlying record was an appointed-representative registration rather than a licence, a distinction a page's text does not convey.

3. **A third gap, not previously recorded anywhere in this study: the field is not searchable by domain.** The PRS accepts name, licence number, registration number, ACN or ABN. Searching a string that the register itself publishes as a licensee's principal website returns no results (§2.1). The verification the stated purpose describes — a platform or a consumer holding a domain from an advertisement and asking which licensee it belongs to — is a **reverse lookup the register does not support**. Every check must begin from a licensee identity the enquirer already has, which is the identity an imposter site supplies. This is the cheapest of the three to close, and closing it would follow automatically from publishing the field in bulk.

Recorded constructively: this is an audit of a two-month-old regulator tool, it produces exactly the feedback the tool's stated purpose calls for, and its central finding is a fix ASIC has already said it intends to make.

---

## 7. Language discipline (§8)

Every statement in this report is of the form "this domain does / does not appear in this register field", with the register URL and the check date. No brand named here is described as fraudulent, fake, misleading or a scam. Absence from a register field is recorded as an observation about the register's published content, never as a finding about a firm. No inference of unlicensed operation is drawn anywhere, and **Corporations Act s911A is not cited** (amendment 5 §2) — nothing in this method could establish it. Where a published field cannot answer a question, the answer is recorded as UNVERIFIABLE-TODAY and never guessed.

---

## 8. Archive

`manifest.json` lists 18 archived files with sha256, source URL, retrieval method and check date.

- **Byte-exact HTTP archives** (curl): the media release, the AFS-licensee guidance page, ASIC's data.gov.au page, four data.gov.au CKAN API responses, the PRS application shell, and the 403 response from the internal endpoint.
- **Per-licensee register captures**: the PRS is a client-rendered application, so the raw HTTP body carries no register data. Each record was captured as rendered DOM text, hashed **in the browser at capture time**, and transcribed to the archive; the archive file's sha256 was then recomputed locally and **matches the capture-time hash for all four records**, so the chain from the live register to the parsed file is verifiable. The capture-time sha256 of the full rendered HTML is recorded alongside in `raw/prs_dom_captures_index.json`.
- **Bulk dataset**: `afs_lic_202607.{csv,tsv,xlsx}` (21 MB) are archived locally and fingerprinted in `raw/afs_lic_202607_fingerprint.json` — sha256, byte size, header, row count and source URL — rather than committed. All parsing in §2.2 was done against those local files; the recorded sha256 pins the exact snapshot.
- **Rate discipline**: one pass per resource, human-speed, no volume crawling, no endpoint hammering, no bot-detection circumvented.
