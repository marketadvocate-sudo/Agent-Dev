# MWR Gate Run Report — HMA Fixture

Filled instance of `GATE_RUN_CHECKLIST.md` (constitution v1.4 Section 7), run against
the golden healthcare fixture. This is the critical test from the build brief: rebuild
the Gold segment's Gold Standard 6 (information asymmetry) on public data alone, after
the mechanical source checks strip the proprietary survey and the vendor-published,
self-cited issue brief.

## 0. Run identity

- FHC artifact under test: `fixtures/fhc_output.example.hma.json`
- Scope requested: **Gold** (default)
- `mwr_version` graded against: **1.4**
- Output under review: `examples/mwr_output.hma.json`
- Reviewer / date: Doug (Red / Kahuna), gate self-run

## 1. Input check — PASS

- Only the FHC artifact was consumed; no supplementary input.
- No sender/buyer context was invented. Every fact traces to a structured field.
- Prose fields were used for tone only, not mined for new factual claims. The five
  facts used all come from `specific_facts`.

## 2. Scope check — PASS

- Gated **Gold only**. The Silver ("Margin Bleed MCOs") and Bronze ("Warning Notice
  Window") segments were ignored, as the default requires.
- `scope_used: "Gold"`, `override: false` in the output. Correct.
- No override, so no `override_warning` is required, and none is present.
- The Gold tier was populated, so `empty_scope` does not apply.

## 3. Standards check — one exemplar, `gold-january-sprinters`

The gate first stripped three items the FHC `pvp_angle` leaned on:

1. **"We surveyed your peers"** rests on the KFF/HMA Annual Survey, which is
   `proprietary` (in-house to HMA). No credit for Standards 3, 6, 7. Invisible.
2. **"Anchored to HMA's June 5 issue brief"** is `vendor_published` **and** self-cited
   (`publisher` = Health Management Associates = `brand_profile.company`). No credit for
   3, 6, 7; it may inform Standard 2 only.
3. **"Would a 20-minute call be useful?"** is a CTA. Automatic Standard 1 miss. Stripped.

The rebuild draws asymmetry from public sources only.

| # | Standard | MET / MISS | Basis |
|---|----------|-----------|-------|
| 1 | Independently useful | **MET** | Delivers a usable read with no ask; ends on the value. |
| 2 | Relates to the value prop | **MET** | Closes on HMA's insider-practitioner value_prop and differentiator, distinct from the IT vendor. |
| 3 | Based on public data | **MET** | Every claim traces to a surviving public source (KFF, CMS/Federal Register, U.S. Congress, WI/IA filings). The HMA brief is deliberately unused. |
| 4 | Translates to meaningful insight | **MET** | Turns the June 1 rule plus the tracker into a conclusion the buyer had not drawn: pre-June-1 exemption math is now wrong. |
| 5 | Goes beyond pain identification | **MET** | Advances to the real exposure: policy navigation under the IT build, on an already-open window. |
| 6 | Creates information asymmetry | **MET** | The June 1 CMS frailty redefinition read against per-state movement on the public KFF tracker (Nebraska live May 1 vs non-movers). Public sources only. |
| 7 | Concrete and specific | **MET** | Specifics span five fact_types with name/event anchors: Nebraska (name), June 1 2026 (event), 43 (number), Aug 31 2026 (date), $20M (amount). |

Mechanical gates confirmed held:
- Standards 3, 6, 7 rest only on `public`-classed sources. Confirmed.
- No self-citation: none of the five cited sources is published by HMA or on its domain.
- Every cited public source carries a resolvable url.
- Standard 7 type-span: 5 distinct `fact_type` values, including `name` and `event`. Clears.

**Miss count: 0 → PVP.** Output records `pvp_achievable: "yes"`, `revised: false`.
Reviewer agrees: **PASS**.

## 4. Format check — PASS

- One-step single message. No drip or cadence.
- Exactly one subject line and one eyebrow line.
- No CTA; the body ends on the value (the insider read on the rule).
- No em-dashes in subject, eyebrow, or body (confirmed by `selftest.py`).
- Cannonball voice throughout.

## 5. Honesty check — PASS

- No padding: the proprietary and vendor-published items were dropped rather than
  laundered into the message to inflate the fact count.
- Not a brand gap (brand profile is complete), so no `run_decline` applies here.

## 6. Disposition — ACCEPT

All five checks PASS. The gate proves a PVP is achievable for the January Sprinters
cohort on public data alone, which is the moment of truth the brief set. Verdict `yes`,
cleared on the first pass, seven for seven.

## How to reproduce

```sh
python3 tools/gate.py report fixtures/fhc_output.example.hma.json --tier Gold
python3 tools/gate.py validate-output examples/mwr_output.hma.json
python3 tools/selftest.py
```
