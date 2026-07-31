# Artifact corrections log

Corrections to committed frame artifacts. The frozen protocol
(`protocol/locked_protocol_v1.0.md`) and the tagged freeze commit are
untouched; substantive scope changes are recorded as numbered amendments
under `protocol/amendments/`.

## 2026-07-31 — eurotrader.com probe row corrected (bug artifact)

The register's website field for Eurotrade RGB (Seychelles) Ltd reads
`https://www.eurotrader.com;` (trailing semicolon, multi-value field
formatting). `domain_of()` did not sanitize hostnames, so the Common Crawl
CDX index was queried for the invalid host `eurotrader.com;`, which
guarantees a 404 recorded as 0 captures. That 0 was a bug artifact, not
evidence of absence.

Fix: hostnames are now sanitized (trailing `;`/`,`/`:`/whitespace stripped;
multi-URL fields split on `;`/`,`). The corrected host `eurotrader.com` was
re-probed against the same crawl (CC-MAIN-2026-25) on 2026-07-31:

- `n_zho_captures_capped = 0` — no Chinese-primary captures
- `n_captures_capped = 260` — the domain is present in the index, so the
  zho result is now a valid negative rather than a lookup failure

`has_chinese_presence` for eurotrader.com remains 0; the presence count
(26 of 162 domains) is unchanged. The corrected record in
`cc_chinese_probe.jsonl` carries an inline `note` field. No other probed
domain was affected (eurotrader.com was the only malformed hostname).

## 2026-07-31 — capture-tally fields renamed (they are not page counts)

`n_zho_pages` → `n_zho_captures_capped` and `n_pages_any_lang` →
`n_captures_capped` in `cc_chinese_probe.jsonl` and
`frame_sample_chinese_offshore.csv`. The values are CDX **capture records**
returned up to the query limits (200 for the zho query, 1000 for the
any-language query, no `collapse=urlkey`): 4 domains sit exactly at the zho
cap and 8 at the any-language cap, and repeat captures of one URL are
counted separately. The old names overstated what was measured.

Analytical use is unchanged: only the presence indicator
`has_chinese_presence = (n_zho_captures_capped > 0)` is used, exactly as
before. The `--summarise` report no longer ranks domains by these censored
tallies; it lists presence domains alphabetically.
