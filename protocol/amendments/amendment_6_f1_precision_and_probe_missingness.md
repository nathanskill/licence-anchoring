# Amendment 6 — F1 precision measured; the probe's missingness is not at random; and a caveat in the frozen text is false as written

**Date:** 2026-08-04
**Status:** post-hoc. The F1 presence probe had already been executed when this amendment was written. Nothing here retunes frame F1 — amendment 3 forbids that, and the prohibition is honoured: the frame, its `VERTICAL_TOKENS`, its `SHORT_TOKENS` and its draw are untouched.
**Sequence, stated first so a reader does not have to reconstruct it:** the probe ran to completion over the full 1,000-domain draw; the summary was written; the analysis below was then performed on the resulting artifact; this amendment records what it found.

---

## 1. The measurement F1 was built to produce

`probe_f1.py`'s header states the commitment being discharged here:

> F1 is recall-oriented by construction (amendment 3), so its precision is unknown until measured. The yield here IS that measurement. It is published whatever it turns out to be; the frame is not retuned in response to it.

It has now been measured.

| Stratum | In draw | Probed | Chinese-present | Rate |
|---|---|---|---|---|
| Belize | 7 | 7 (censused) | 2 | — |
| Seychelles | 27 | 27 (censused) | 1 | — |
| no offshore entity | 966 | 777 | 7 | 0.90% |
| **Total** | **1000** | **810** | **10** | **1.23%** |

Per-stratum rates are not comparable without care (amendment 4): the two small strata are censused, the large one sampled. Both small strata are now complete.

The ten domains with Chinese-language captures in CC-MAIN-2026-25:

`3h-trading.com`, `capital.com`, `gold-money.cn`, `m4markets.com`, `markets.com`,
`wh-hw.com`, `wh-sinobest.com`, `wh10176.cn`, `wing-fx.com`, `world-trader.com`

**Nine of the ten are new to the claim corpus** (only `m4markets.com` was already carrying claim units). The corpus domain base goes from 15 to 24, a 60% expansion. Two — `gold-money.cn` and `wh10176.cn` — are `.cn` domains, which a register-anchored frame such as F2 structurally cannot reach; reaching them is the entire reason F1 exists.

Two of the hits (`wh-hw.com`, `wh-sinobest.com`) were drawn by the `wh` token in the frozen `SHORT_TOKENS`, i.e. the Pinyin initials of 外汇. The frozen vocabulary paid out on live data.

**Two of the ten (`capital.com`, `markets.com`) are large mainstream regulated brands** that a register-based frame would reach anyway. The distinctive, F2-unreachable contribution is therefore smaller than nine, and should be described that way rather than as nine.

---

## 2. The missing 190 are not missing at random, and the direction of the bias is identifiable

810 of 1,000 domains were probed. The remaining 190 (all in the sampled "no offshore entity" stratum) are service failures. Per the frozen design, a failed query is never written, so these are correctly "not yet probed" rather than false negatives. A retry pass recovered 39 of them and added **no** new Chinese-present domains.

A live diagnostic on six of the persistent failures returned, in every case, **HTTP 504 Gateway Time-out** from the Common Crawl CDX index. The failures spread across TLDs roughly in proportion to the draw (`.com` 79/389, `.ru` 18/57, `.de` 6/40), so this is not a TLD artifact.

A 504 on a CDX index is a server-side timeout on an expensive query, and query cost rises with the number of captures held for the domain. Capture count is in turn a strong predictor of Chinese presence in the data we do have:

| Capped total captures | n | Chinese-present | Rate |
|---|---|---|---|
| 0 | 519 | 0 | 0.00% |
| 1–9 | 144 | 1 | 0.69% |
| **10–99** | **61** | **5** | **8.20%** |
| 100–999 | 17 | 1 | 5.88% |
| 1000+ | 2 | 0 | 0.00% |

**Therefore the 190 unprobed domains are plausibly enriched for high capture counts, and hence enriched for Chinese presence. 1.23% is a lower bound, not a point estimate.**

Bounding it explicitly:

| Assumption about the 190 | Implied overall rate |
|---|---|
| None has Chinese content (hard floor) | 10/1000 = **1.00%** |
| They behave like the probed stratum (0.90%) | 11.7/1000 = **1.17%** |
| They behave like the 10–99 capture band (8.20%) | 25.5/1000 = **2.55%** |

The defensible statement is that F1's precision on this draw lies **between roughly 1.0% and 2.6%**, with the lower end assuming the timeouts are uninformative and the upper end assuming they are maximally informative. This range is reported instead of the bare 1.23%.

This bias is a property of the instrument (the keyless CDX index), not of the frame, and no change to F1 would remove it.

---

## 3. Defect: a caveat in the frozen summary is false as written

`f1_presence_summary.json` carries this caveat, which is emitted by frozen code:

> Service failures are not recorded, so absence in the file means not-yet-probed, never a silent failure.

**This is false for the total-capture field.** The probe issues two queries per domain — Chinese-only, then any-language. The write path is:

```python
n_any, _ = cc_query(d, False, ANY_CAP)
if n_any < 0:
    n_any = ""
out.write(json.dumps({... "n_captures_capped": n_any ...}))
```

When the Chinese-only query succeeds and the any-language query fails, the row **is** written, with the service failure silently downgraded to an empty string. **34 rows in the sampled stratum (4.4%) carry `n_captures_capped: ""`.**

Scope of the damage:

- **The primary endpoint is unaffected.** Presence is defined on `n_zho_captures_capped > 0` alone (caveat 3: "only presence (n > 0) is used analytically"), and that field is never downgraded — a failed Chinese-only query skips the row entirely. The 1.23% figure and the ten domains stand.
- **The secondary analysis in §2 loses those 34 rows**, which is why the capture-count table above is computed on 743 rather than 777 domains. It is reported on that basis.
- **The caveat's guarantee does not hold for `n_captures_capped`** and must not be relied on for it.

Corrected caveat text, to be used wherever the summary's caveats are quoted:

> Service failures on the Chinese-only query are not recorded, so absence of a domain from the file means not-yet-probed, never a silent failure. Service failures on the any-language query **are** recorded, as an empty `n_captures_capped`; that field is therefore missing-not-at-random and must not be read as a count of zero.

The frozen file is not edited. Consistent with the discipline of this project, the correction lives here and the code fix — writing an explicit `null` with a `capture_query_failed: true` flag rather than `""` — is deferred to a future run rather than applied retroactively to existing rows.

---

## 4. Consequence for the study, stated without softening

F1's precision is of order one per cent. Reaching the 60-unit floor through F1 alone would require a draw an order of magnitude larger than the present one, at roughly 2.2 seconds of politeness-bounded querying per domain.

**F1 is a reach instrument, not a volume instrument.** It was never designed to be efficient; it was designed to reach a stratum that a register-anchored frame structurally cannot see, and on this evidence it does exactly that and little else — nine new domains, two of them `.cn`.

The 60-unit floor therefore needs a route other than enlarging F1. Enlarging F1 in response to a disappointing yield is precisely the retuning that amendment 3 prohibits, and it is not done here.

---

## 5. Artifacts

- `artifacts/frames/f1_presence_probe.jsonl` — 810 rows, append-only, resumable
- `artifacts/frames/f1_presence_summary.json` — regenerated after the retry pass
- `artifacts/frames/frame_f1_draw.csv` — 1,000 domains, unchanged
