# Licence Anchoring (REF-2026-019)

Status: `PROTOCOL FROZEN / COLLECTION AND FIRST VERIFICATION COMPLETE / N=21 VERIFIED UNITS, 35% OF THE PROTOCOL FLOOR — NOT A POPULATION ESTIMATE`

Reached so far: four offshore registers enumerated (450 institutional
registrants committed), 222 register-listed domains probed against the Common
Crawl index for Chinese-language presence (26 carry Chinese pages), 413
archived Chinese-language pages fetched from WARC records, 2,501 licence-claim
sentences extracted, 37 claim units normalised, and 21 units verified against
nine official registers. Class tally over those 21 units: A 3, B 12, C 0, D 6.
That is 35.0% of the protocol's 60-unit floor and 26.3% of its 80-unit target,
so the tally describes the verified units only and is **not** a population
estimate — the limitation is stated in full below and in
`artifacts/verification_v2/verification_report.md` §5.

Chinese-speaking retail clients read "regulated by the FCA" on a broker's page and assume someone will step in if things go wrong. Often a different group entity — registered in St Vincent, Vanuatu or the Seychelles — is the one that actually contracts with them and holds their funds. The licence is genuine; it simply does not cover the reader, and they tend to discover this only when they try to claim.

This study verifies every licence claim on Chinese-language retail FX/CFD pages against the official registers, checks whether the licence holder is the entity that actually onboards the client, and measures how often the two diverge.

Four regulators have named the pattern — ESMA (2019), the FCA's "halo firms" (2024), ASIC REP 828 (2026), and IOSCO FR12/22, which recommended a public register of which entity stands behind a domain and was told by industry that it was infeasible. Nobody has counted it. The point is to turn something people find out afterwards into a number they can see beforehand, and to give regulators a baseline against which remediation can be measured.

- **Protocol**: [`protocol/locked_protocol_v1.0.md`](protocol/locked_protocol_v1.0.md) — frozen before collection (tag `v1.0-protocol-freeze`). Taxonomy, sampling frames, the operative-entity rule and the coding rules are fixed there. Corrections and pinned choices are recorded as numbered amendments in [`protocol/amendments/`](protocol/amendments/) (amendment 1: register count 193→231; crawl pinned to CC-MAIN-2026-25; wording notes) — the frozen file is never edited.
- **Taxonomy**: A direct-licensed / **B cross-entity licence-borrowing** / C clone-or-fabricated / D unverifiable. Class B is the hypothesised dominant form and is reported strictly as an observable entity relationship, never as fraud.
- **What the first 21 units actually show**: 20 of 21 resolved to a real register record. The failure mode of this ecosystem is not fabrication — it is that the divergence sits in **scope** (wholesale-only permissions displayed on a retail-facing page), in **domain** (the register publishes an approved domain that is not the one displaying the claim), and in **identifier type** (a company-registry number occupying a licence-number position). Every class-B count is reported with that three-way split; an undifferentiated total is not presented as a headline. See [`amendment 5`](protocol/amendments/amendment_5_mismatch_structure_and_evidence_rules.md).
- **What this study does not allege**: nothing here can establish that any entity provided financial services without a licence, and the study never says so. The regulatory frame is misleading-or-deceptive conduct (ASIC Act s12DA/s12DB, Corporations Act s1041H, RG 234), not unlicensed operation.
- **Method**: keyless throughout — Common Crawl for the corpus frame, offshore securities-dealer registers for the spine, statutory registers for verification. No account is ever opened and no personal data is ever submitted; only publicly displayed terms pages are read.
- **A methodological note that shaped the design**: at least one brand serves opposite entities on the same Chinese-language path depending on the requester's egress IP. Vantage point is therefore a coded variable, and every brand is collected from at least two vantages — a single-vantage crawler can code the hypothesis backwards.
- **First results exist, and the limitation travels with them.** N = 21 verified claim units, coded A 3 / B 12 / C 0 / D 6 — 35.0% of the protocol's 60-unit floor and 26.3% of its 80-unit target. These counts and shares describe the verified units only. They are **not a population estimate** and must not be read as a rate for the sector, for Chinese-language broker pages generally, or for any register's licensee base. The units are not independent — 7 of the 21 come from a single domain and 3 from another, so a unit-level share is partly a function of how many authorities one page happens to display; selection was archive-driven rather than random; and class C's zero count carries no information about C's prevalence, because four of the nine registers used publish no licence numbers at all, structurally preventing the number-level test that most often separates C from B. Weak or null results will continue to be reported in full.

Related repositories by the same author: [pump-and-dump-replication-audit](https://github.com/nathanskill/pump-and-dump-replication-audit) · [alert-burden-audit](https://github.com/nathanskill/alert-burden-audit) · [leaderboard-survivorship](https://github.com/nathanskill/leaderboard-survivorship) · [evidence-separated-trading-screening](https://github.com/nathanskill/evidence-separated-trading-screening)

License: MIT.
