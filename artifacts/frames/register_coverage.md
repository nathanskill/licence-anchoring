# Frame F2 — offshore register coverage

What was searched for, what was retrievable, and what each register actually
publishes. Protocol reference: `protocol/locked_protocol_v1.0.md` §4 (frame
F2) and §6 (register verification).

**Why several registers rather than one.** §4 defines F2 as "direct
enumeration of offshore securities-dealer registers (**e.g.** the Seychelles
FSA capital-markets register)" and stratifies the sample by offshore
jurisdiction across "Seychelles / Vanuatu / Mauritius / BVI / Belize / SVG /
no offshore entity". Seychelles is the protocol's example, not its
definition, and five of the other strata are named in the frozen text.
Enumerating them realises the frozen design; it is not a scope change and no
amendment is claimed for it.

Only the regulator's own domain was used for every register below. Every
fetch is archived verbatim under `data/registers/` (gitignored) with a
SHA-256 in `artifacts/frames/register_fetch_manifest_*.json`; all parsing
runs against the archived bytes, never against the network.

## 1. Registers enumerated

| Register | URL | Fetched (UTC) | SHA-256 | Rendering | Entries parsed | Committed | Licence numbers published? | Websites published? |
|---|---|---|---|---|---|---|---|---|
| Seychelles FSA — capital markets | `https://fsaseychelles.sc/regulated-entities/capital-markets` | 2026-07-27T04:42:32Z (pinned) | `52d319f3653dd58a…b468b4` | server-rendered HTML (Bootstrap accordion) | 434 | 239 | **No** | Yes — 166 of 239 |
| Vanuatu FSC — Financial Dealers Licensee List | `https://www.vfsc.vu/financial-dealers-licensee-list/` | 2026-08-01T14:04:45Z | `e3a204c11d893f00…8957de` | server-rendered HTML (single table) | 66 | 66 | **No** — company number only | **No** — none |
| Belize FSC — licensed/registered service providers | `https://licensys.belizefsc.org.bz/api/pub/DynamicList?__meta__formId=6928049e24c807681185b908&…&IsCurrent=true` | 2026-08-01T14:04:45Z | `396af7835f06ab5b…eb3ed7` | public keyless JSON endpoint behind a JS front end | 120 | 92 | **Yes** — all 92 | Yes — 74 of 92 |
| SVG FSA — licensed mutual-fund-sector entities | `https://fsasvg.com/docs/mutual-funds/` | 2026-08-01T14:04:45Z | `4fe8720376d878cf…c798376` | server-rendered HTML (6 tables) | 55 | 53 | **No** | **No** — none |

Auxiliary archive (not a register of entities; decodes the licence-type codes
in the Belize payload): Belize FSC licence-type classifier,
`https://licensys.belizefsc.org.bz/api/pub/classifiers/selectSearchByTranslation?ClassifierDomainNaturalIds=LMIS-LIC-TYPE&…`,
fetched 2026-08-01T14:04:45Z, SHA-256 `5d80d764937a91d2…6ae693d`, 29 licence
types.

"Committed" is the row count reaching
`artifacts/frames/frame_f2_offshore_registers.csv`. The difference is the
privacy filter in protocol §7 rule 4 (see §4 below), not a parse failure.

### Per-register notes

**Seychelles FSA (Seychelles).** Unchanged from the original build and
deliberately **pinned** to the 2026-07-27 snapshot: the 162-domain
Chinese-presence probe, the stage-2 extraction, the stage-3 claim units and
the stage-4 verification all derive from those bytes, so re-pointing the
frame at a fresher snapshot would move the population underneath already
committed results. The register was re-fetched on 2026-08-01 as a drift
check and archived beside the pinned copy: **434 entries → 434, 239
institutional → 239, websites 166 → 168**. Drift is two entities gaining a
website field; no entity was added or removed. The frame keeps the pinned
166.

**Vanuatu FSC (Vanuatu).** One server-rendered table of 66 current Financial
Dealers Licence holders: date of licence, company number, name, class of
licence (A/B/C — the Financial Dealers Licensing Act classes covering FX and
derivatives dealing), status. Two consequences, both load-bearing:

- The register publishes **no website field at all**, so entity→brand
  mapping is impossible from this register. It contributes 66 rows to the
  frame and **zero domains** to the Chinese-presence probe. Any Vanuatu
  brand linkage has to arrive through another route.
- The only identifier published is a **company number**, not a licence
  number. It is recorded as `identifier_type = company-number` with
  `has_licence_number = 0` rather than being flattened into a licence
  identifier, because a marketing page presenting that company number as a
  "VFSC licence number" is precisely the protocol's **B-mis-anchor**
  sub-code (§3). Flattening the two would destroy the distinction the
  sub-code is built on.

**Belize FSC (Belize).** The only register in the frame that publishes a
licence number **and** a website, so it is the only one supporting
number-level B-vs-C discrimination and entity→brand mapping at the same
time. The public front end (`licensys.belizefsc.org.bz`) is an Angular
single-page app, but it is driven by an unauthenticated public JSON listing
endpoint on the regulator's own host, discovered from the app's own
`/assets/config/config.json`; the endpoint is fetched once with a page size
above the record count so one archived response is the whole register, and
`--parse` aborts if the register ever outgrows it. Published fields:
registration (licence) number, licence type(s), licensee name, e-mail,
domain name, initial registration date, record status, appointees.

Composition of the 92 committed rows: 15 carry a securities-dealer-type
licence (`in_dealer_frame = 1`) — trading in securities as principal/agent,
arranging transactions in securities, managing securities, providing
investment advice, money broking, trading in commodity-based and financial
instruments — and 77 hold corporate-services, registered-agent, audit,
custody or payment licences. Record status is published and retained: 87
active, 2 pending cancellation, 1 pending surrender, 1 cancelled, 1
annulled. `IsCurrent=true` selects the current version of each record, not
"active" status, so the frame carries non-active records with their status
rather than dropping them silently.

One data-entry error in the source register is handled mechanically and
documented in `CORRECTIONS.md`: one licensee's domain field holds two URLs
concatenated with no separator.

**SVG FSA (St Vincent and the Grenadines).** Included for a negative result
the study needs on the record. The SVG FSA's published licensed-entity
categories are business companies, limited liability companies, virtual
asset businesses, mutual funds, insurance and pensions, international banks,
credit unions and money services businesses — **there is no securities-dealer
or forex register to enumerate, because the authority does not license that
business**. That is the exact condition behind the protocol's
**B-false-anchor** sub-code (§3: "a Chinese page stating an SVG entity is
'regulated by the Financial Services Authority', where the SVG FSA registers
international business companies and does not license forex at all"). The
archived page is evidence for that claim rather than filler.

Because these are fund-sector licensees and not retail-FX onboarding
vehicles, **every SVG row carries `in_dealer_frame = 0`**. Any sample drawn
from the dealer spine must filter on that column; the rows are in the frame
so the jurisdiction's coverage is auditable, not so they can be sampled as
dealers. The register publishes neither licence numbers nor websites.

## 2. Registers that could not be enumerated

| Regulator | Jurisdiction | URL attempted | Outcome |
|---|---|---|---|
| FSC Mauritius | Mauritius | `https://www.fscmauritius.org/en/supervision/online-public-register` and `https://opr.fscmauritius.org/ords/opr/r/fsc-opr/fsc-online-public-register-opr` | **Access failure.** Both hosts return a 212-byte Imperva/Incapsula interstitial (`_Incapsula_Resource` script, `noindex,nofollow`) instead of content, for every HTML path tried, on 2026-08-01. `robots.txt` is served normally and permits the paths; the sitemap it names (`/sitemap-2026.xml`) 404s. No enumerable file, feed or export was reachable. Not machine-enumerable from this vantage. |
| BVI FSC | British Virgin Islands | `https://www.bvifsc.vg/regulated-entities-investment-business`, `https://www.bvifsc.vg/` | **Access failure.** Cloudflare returns HTTP 403 "Sorry, you have been blocked" for every HTML path, on 2026-08-01. Static files under `/sites/default/files/` do serve (200), but the Commission publishes no licensee list as a file there — the Register of Investment Business Licensees is a query-only search interface. Not machine-enumerable from this vantage. |
| Labuan FSA | Labuan (Malaysia) | `.../money-broking/list-of-money-brokers`, `.../capital-markets/list-of-securities-licensees` | **Not machine-enumerable: JS-only.** Both URLs return byte-identical 120,125-byte application shells (they share the canonical page `/financial-institutions-directory`); the directory rows are injected client-side. No JSON endpoint is referenced in the shell. The list is readable in a browser — the stage-1 pilot verification read it live on 2026-08-01 — but not retrievable as bytes to archive and parse. |
| Cayman Islands Monetary Authority | Cayman Islands | `https://www.cima.ky/search-entities-cima` | **Not machine-enumerable as published.** The page renders a search form only; results come from a POST endpoint (`/search-entities-cima/get_search_data`). There is no listing URL that enumerates licensees, so enumeration would require synthesising queries rather than reading a published register. Not pursued. |
| SVG FSA — business companies register | SVG | `https://fsasvg.com/entity-name-search/` | **Not machine-enumerable as published.** Name/number search only, over a database the site states is refreshed weekly. No enumerable listing. (The FSA's *licensed* entities are enumerable and are covered above.) |

No attempt was made to work around the Mauritius or BVI bot protection. Both
are recorded as access failures with the observed status, which is the
honest state of the evidence.

## 3. What each register can and cannot support

| Jurisdiction | B-vs-C discrimination | Entity→brand mapping |
|---|---|---|
| Seychelles | **Name level only** — no licence numbers published (the limitation §6 already documents) | Yes — 166 websites |
| Vanuatu | **Name level only** — company number published, licence number not; a page presenting the company number as a licence number is B-mis-anchor | **No** — no website field |
| Belize | **Name and number level** — licence numbers published for every record | Yes — 74 websites |
| SVG | Not applicable — no securities-dealer register exists; a claim of SVG *forex* regulation is B-false-anchor on its face | **No** — no website field |
| Mauritius, BVI | Undetermined — register not retrievable | Undetermined |

The uniform verification claim the protocol warns against would be false
here: three of four enumerated registers publish no licence number, and two
of four publish no website. The `has_licence_number`, `identifier_type` and
`website` columns carry this per row so no downstream step has to assume it.

## 4. Privacy filter applied to the committed artifact

Protocol §7 rule 4 — no private individuals as units of analysis. The
committed CSV carries institutional entities only and has **no e-mail column
and no appointee/officer column**. The full parse, including e-mail
addresses and appointee names, is written only to
`data/registers/frame_f2_full_local.csv` (gitignored) and stays derivable
byte-for-byte from the archives.

- Seychelles: the register's own category taxonomy separates institutions
  from representatives; the 195 representative rows (named natural persons,
  no websites, no analytical role) stay local-only. Unchanged behaviour.
- Registers with no such taxonomy are filtered by a mechanical legal-form
  test on the licensee name. It is conservative in the safe direction: a
  misclassified company is merely omitted from the committed artifact, while
  a misclassified person would breach the rule. It excluded 28 Belize rows
  (individually named registered agents, individual accountants, and six
  firms whose names carry no legal-form suffix — all registered-agent or
  audit licences, none in the dealer frame) and 2 SVG fund rows (fund names
  with no legal-form suffix, no websites, not in the dealer frame). No row
  with `in_dealer_frame = 1` was excluded by this filter.

## 5. Totals

- Registers enumerated: **4** (Seychelles, Vanuatu, Belize, SVG); registers
  attempted and not enumerable: **5**.
- Registrants parsed: **675**; committed after the privacy filter: **450**.
- Securities-dealer-type rows (`in_dealer_frame = 1`): **312** — 231
  Seychelles, 66 Vanuatu, 15 Belize.
- Rows with a published licence number: **92** (Belize only).
- Rows with a website, i.e. entity→brand mapping possible at all: **240**
  (166 Seychelles + 74 Belize) — 53% of committed rows.
- Distinct domains in the frame: **231** — 162 from Seychelles (all already
  probed), 71 from Belize, of which **2 appear in both registers**: two
  domains are recorded against a Seychelles registrant *and* against a
  differently-named Belize licensee. That is an observable register fact,
  reported here as an entity-relationship observation and nothing more; it
  is exactly the multi-register structure §5 of the protocol tells the
  operative-entity rule to resolve. Derivable from the frame CSV by grouping
  on `website`. Net new domains to probe: **69**.
