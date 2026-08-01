# Licence Anchoring (REF-2026-019)

Status: `PROTOCOL FROZEN / COLLECTION AND FIRST VERIFICATION COMPLETE / SAMPLE BELOW THE PROTOCOL FLOOR`

Reached so far: four offshore registers enumerated (450 institutional
registrants committed), 222 register-listed domains probed against the Common
Crawl index for Chinese-language presence (26 carry Chinese pages), 413
archived Chinese-language pages fetched from WARC records, 2,501 licence-claim
sentences extracted, 37 claim units normalised, and 21 units verified against
nine official registers. Class tally over those 21 units: A 3, B 12, C 0, D 6.
That is 35% of the protocol's 60-unit floor, so the tally describes the
verified units only and is **not** a population estimate — see
`artifacts/verification_v2/` for the full caveat.

Chinese-speaking retail clients read "regulated by the FCA" on a broker's page and assume someone will step in if things go wrong. Often a different group entity — registered in St Vincent, Vanuatu or the Seychelles — is the one that actually contracts with them and holds their funds. The licence is genuine; it simply does not cover the reader, and they tend to discover this only when they try to claim.

This study verifies every licence claim on Chinese-language retail FX/CFD pages against the official registers, checks whether the licence holder is the entity that actually onboards the client, and measures how often the two diverge.

Four regulators have named the pattern — ESMA (2019), the FCA's "halo firms" (2024), ASIC REP 828 (2026), and IOSCO FR12/22, which recommended a public register of which entity stands behind a domain and was told by industry that it was infeasible. Nobody has counted it. The point is to turn something people find out afterwards into a number they can see beforehand, and to give regulators a baseline against which remediation can be measured.

- **Protocol**: [`protocol/locked_protocol_v1.0.md`](protocol/locked_protocol_v1.0.md) — frozen before collection (tag `v1.0-protocol-freeze`). Taxonomy, sampling frames, the operative-entity rule and the coding rules are fixed there. Corrections and pinned choices are recorded as numbered amendments in [`protocol/amendments/`](protocol/amendments/) (amendment 1: register count 193→231; crawl pinned to CC-MAIN-2026-25; wording notes) — the frozen file is never edited.
- **Taxonomy**: A direct-licensed / **B cross-entity licence-borrowing** / C clone-or-fabricated / D unverifiable. Class B is the hypothesised dominant form and is reported strictly as an observable entity relationship, never as fraud.
- **Method**: keyless throughout — Common Crawl for the corpus frame, offshore securities-dealer registers for the spine, statutory registers for verification. No account is ever opened and no personal data is ever submitted; only publicly displayed terms pages are read.
- **A methodological note that shaped the design**: at least one brand serves opposite entities on the same Chinese-language path depending on the requester's egress IP. Vantage point is therefore a coded variable, and every brand is collected from at least two vantages — a single-vantage crawler can code the hypothesis backwards.
- **No results have been produced yet.** Weak or null results will be reported in full when they exist.

Related repositories by the same author: [pump-and-dump-replication-audit](https://github.com/nathanskill/pump-and-dump-replication-audit) · [alert-burden-audit](https://github.com/nathanskill/alert-burden-audit) · [leaderboard-survivorship](https://github.com/nathanskill/leaderboard-survivorship) · [evidence-separated-trading-screening](https://github.com/nathanskill/evidence-separated-trading-screening)

License: MIT.
