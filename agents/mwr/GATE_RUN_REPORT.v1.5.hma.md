# MWR Gate Run Report — HMA Fixture, under Constitution v1.5

A run of `GATE_RUN_CHECKLIST.md` against the HMA Gold segment with the v1.5 agent
(insight-first drafting, dependency-ordered grading, the entailment rule, and the
v1.5 format rules: length, no body credential). Behavior is reported against the
checklist. Per the work order, no editorializing on whether the v1.5 or v1.4 verdict
is "better," and this run does **not** replace the committed golden
`examples/mwr_output.hma.json`; the ratified v1.5 golden will come from a forthcoming
Texada Software artifact.

## 0. Run identity
- FHC artifact: `fixtures/fhc_output.example.hma.json` (v2.0, Gold + Silver, Bronze deferred)
- Scope: Gold (default) · `mwr_version` graded against: **1.5**
- Segment: `gold-january-sprinters` (5 KFF-sourced members)

## 1. What changed in behavior from v1.4 to v1.5

Running the committed v1.4 golden (`examples/mwr_output.hma.json`) through the new
mechanical lint shows why v1.5 produces a different message:

```
$ gate.py lint-exemplar examples/mwr_output.hma.json --fhc fixtures/fhc_output.example.hma.json
  [FAIL] body <= 165 words  (256 words)
  [FAIL] no buyer-conditional (entailment)
         -> "If your exemption planning predates that rule, the assumptions under it moved, ..."
```

The v1.4 message is 256 words, carries a **buyer-conditional** ("If your exemption
planning predates that rule..."), and closes on a **credential sentence** ("HMA's
consultants came out of state Medicaid director and senior policy roles..."). Under
v1.5 each of those is a format failure. So the v1.5 agent rebuilds.

## 2. The v1.5 agent's output for this segment

**One-sentence insight (Standard 4, stated first):** the June 1 rule reset the
exemption baseline the whole cohort planned around, and the public tracker shows the
readiness gap widening on a fixed clock.
**Buyer action (Standard 1):** re-audit exemption logic against the new frailty
definition before the outreach window closes.

- **Subject:** The June 1 frailty rule reset exemption baselines
- **Eyebrow:** The public tracker shows the cohort splitting on a fixed clock
- **Body (146 words):**

> On June 1, 2026, CMS narrowed medical frailty in an interim final rule, resetting
> the exemption assumptions every affected state built its work-requirements plan on.
> The public KFF tracker shows the cohort is not moving together: Nebraska is
> enforcing early under a May 1, 2026 state plan amendment, Montana and Arkansas from
> July 1, Iowa from December 1, and Georgia's existing waiver expires December 31,
> while other states have no declared path against the same January 1, 2027 deadline.
>
> That spread is the exposure. States that locked exemption logic before June 1 now
> carry the most rework, and the outreach window from June 30 to August 31, 2026 is
> already open. Iowa's build alone runs a minimum of $20 million. The reconciliation
> an IT vendor does not do, aligning the new frailty definition with exemption and
> eligibility rules, is the work sitting on that fixed clock.

## 3. Entailment check (v1.5)

Every buyer claim is entailed by segment membership. The cohort is defined by KFF
tracker implementation status, and its members are named states with those statuses;
the message asserts only public, cohort-level facts (the federal June 1 rule applies
to all affected states; the per-state movements are the members' own `edp_value`s).
The v1.4 "if your exemption planning predates..." was rewritten away (exit 1): the
fixture carries no `resolved_conditions` signal for a per-state exemption-guidance
date, so exit 2 was unavailable, and the claim was reduced to what membership
entails. No buyer-conditional survives.

## 4. Standards check (dependency order)

| # | Standard | Verdict |
|---|----------|---------|
| **4** | Translates to meaningful insight (keystone, graded first) | **MET** |
| 1 | Independently useful (action test) | MET |
| 2 | Relates to the value prop (through the insight, no body credential) | MET |
| 3 | Based on public data | MET |
| 5 | Goes beyond pain identification | MET |
| 6 | Creates information asymmetry (human GS6 call; structurally public-only) | MET |
| 7 | Concrete and specific (Nebraska, June 1 2026, Aug 31 2026, $20M; type-span clears) | MET |

**Miss count: 0 → `pvp_achievable: "yes"`.** No keystone cascade (Standard 4 passed).

## 5. Format checks (mechanical, from `gate.py lint-exemplar`)

```
  [ok] subject <= 8 words  (8 words)
  [ok] body <= 165 words  (146 words)
  [ok] no em-dash
  [ok] no buyer-conditional (entailment)
  [ok] segment carries members (entailment possible)  (5 members)
  1 exemplar(s) linted, 0 mechanical failure(s).
```

Plus: one-step, one subject + one eyebrow, no CTA, no credential in the body, insight
within the first two sentences.

## 6. Behavior summary (no editorializing)

Under v1.5 the gate **produced a different message** than v1.4 for this segment: a
rewritten, entailed, 146-word, credential-free exemplar, verdict `yes`, seven for
seven, cleared on the first pass. The v1.4 golden remains committed and unchanged as
a pre-v1.5 artifact; it does not pass the v1.5 mechanical lint (length, buyer-
conditional). The ratified v1.5 golden fixture is deferred to the Texada Software run.

## Reproduce
```sh
python3 tools/gate.py lint-exemplar examples/mwr_output.hma.json --fhc fixtures/fhc_output.example.hma.json   # v1.4 golden: fails v1.5 lint
python3 tools/selftest.py                                                                                      # suite green
```
