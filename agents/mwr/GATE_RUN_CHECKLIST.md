# MWR Gate Run Checklist

**Purpose:** the repeatable procedure a human reviewer (Red / Kahuna) runs against
one MWR gate output before accepting it. It operationalizes the Reviewer's Charge
in `MWR_CONSTITUTION.md` v1.5 Section 7. The reviewer rules against the constitution,
not against taste. Any failure routes back to the agent with the specific failed
criterion named.

Fill one copy per run. A filled example is in `GATE_RUN_REPORT.hma.md`.

---

## 0. Run identity

- FHC artifact under test: `________________________`
- Scope requested (Gold default; Silver/Bronze only by explicit override): `______`
- `mwr_version` graded against: `______` (current constitution is `1.5`)
- Reviewer / date: `________________________`

## 1. Input check (constitution Section 2)

- [ ] The agent accepted **only** the FHC output artifact. No supplementary input.
- [ ] It did **not** invent or infer sender/buyer context absent from the artifact.
- [ ] It did **not** mine prose (`systemic_condition`, `buyer_motivation`,
      `pain_buyer_perspective`) for new factual claims. Facts come only from
      `specific_facts`, `edp`, `data_sources`, `brand_profile`.

Result: PASS / FAIL. If FAIL, name what was invented: `________________`

## 2. Scope check (constitution Section 3)

- [ ] Default run gated **Gold only**. Silver/Bronze appear only under an explicit
      override, and the override **replaced** Gold scope (instead-of, not in-addition).
- [ ] `scope_used` and `override` in the output match what was requested.
- [ ] Every exemplar produced under an override carries the per-message
      `override_warning` (the three Section 3 trade-offs). The warning is
      per message, not once per run.
- [ ] If the scoped tier was empty, the run returned a single `run_decline` with
      `kind: "empty_scope"` and a `scoped_tier`, and **no** per-segment verdicts.
      (This is a null result, not a "no.")

Result: PASS / FAIL. Notes: `________________`

## 3. Standards check (constitution Section 4, graded in dependency order) — per shipped exemplar

Grade in dependency order (v1.5). No partial credit. Grade Standard 4 first; if it
fails, mark 5, 6, 7 as `keystone_cascade` failures (four misses) before anything else.
Then grade 1, 2, 3 independently. Then grade 5, 6, 7 on merit only if 4 passed.

| Order | # | Standard | MET / MISS | failure_type | Basis or reason |
|-------|---|----------|------------|--------------|-----------------|
| 1st | 4 | Translates to meaningful insight — the one-sentence directive lens (keystone) | | | |
| then | 1 | Independently useful — passes the action test ("after reading, the buyer would ___") | | | |
| then | 2 | Relates to the value prop — through the insight, no body credential | | | |
| then | 3 | Based on public data (public-classed source only) | | | |
| if 4 ok | 5 | Goes beyond pain identification | | | |
| if 4 ok | 6 | Creates information asymmetry (public sources only) | | | |
| if 4 ok | 7 | Concrete and specific (type-spanning, see below) | | | |

Mechanical gates the reviewer confirms held (constitution Section 4):
- [ ] **Keystone:** if Standard 4 missed, Standards 5/6/7 are recorded failed
      (`failure_type: keystone_cascade`), not judged on their own.
- [ ] Standards **3, 6, 7** rest only on `public`-classed sources.
- [ ] No self-citation: no cited public source has `publisher` == `brand_profile.company`
      or a url domain belonging to the vendor.
- [ ] Every cited public source carries a resolvable url.
- [ ] **Standard 7 type-span:** the specifics the exemplar actually uses span at
      least two `fact_type` values, and at least one is a `name`, `location`, or
      `event`. (Two bare quantities do not clear it.)

**Grade by miss count:**
- 0 misses → **PVP**, ships.
- exactly 1 miss → **borderline**: one revision pass aimed at the missed standard.
      Cleared on the second attempt ships with `revised: true`; still missing → "no".
- 2+ misses → **PQS**, rejected; the agent declines and names the gap. (A failed
      keystone is four misses, so a failed Standard 4 is always a "no".)

Verdict recorded in the output (`pvp_achievable`, `revised`): `______`
Reviewer agrees? PASS / FAIL. If FAIL, name the standard(s): `________________`

## 4. Format check (constitution Section 5)

- [ ] One-step only (single message; no drip, cadence, or "if no reply").
- [ ] Exactly one subject line and one eyebrow line.
- [ ] **No CTA** anywhere. The message ends on the value.
- [ ] **No credential in the body** (no "our consultants...", "we have helped...").
      Identity lives in the sender name and brand alone.
- [ ] **No em-dashes** in subject, eyebrow, or body.
- [ ] **Length:** body at most 150 words (165 hard ceiling); subject at most 8 words;
      the insight lands within the first two sentences of the body.
- [ ] **Entailment:** no unresolved buyer-conditional (a second-person claim hedged
      with if / whether / may have / likely / probably / in case, not entailed by
      `members` or a `resolved_conditions` signal). Any that survives is an automatic
      format failure with three exits: rewrite, resolve, or decline.
- [ ] Cannonball voice throughout.

The mechanical slice of this section runs as `gate.py lint-exemplar <output.json>
[--fhc <artifact.json>]` (word counts, em-dash, buyer-conditional scan, members
presence). It is the bouncer, not the author; the insight and voice stay human.

Result: PASS / FAIL. Notes: `________________`

## 5. Honesty check (constitution Section 6)

- [ ] Where a segment's data was thin, the agent **declined and named the gap**
      (failed standard number(s), what is missing, the input that would close it)
      rather than padding or fabricating to force a "yes".
- [ ] A run-level brand gap (`value_prop`/`differentiator` empty) produced **one**
      `run_decline` with `kind: "brand_gap"`, not N identical per-segment "no"s.

Result: PASS / FAIL. Notes: `________________`

## 6. Disposition

- [ ] All five checks PASS → accept the run.
- [ ] Any FAIL → route back to the agent with the named criterion. If the dispute
      cannot be resolved against the criteria above, the criteria are underspecified
      and the constitution gets amended (Section 7). The document is the system.

---

## Reference: expected outcomes on the shipped fixtures

The regression suite (`tools/selftest.py`) pins these. A gate run should reproduce them.

| Fixture | Scope | Expected outcome |
|---------|-------|------------------|
| `hma` | Gold (default) | `yes`, cleared first pass, GS6 rebuilt on public data only |
| `silver_override` | Silver (override) | `yes` + `override_warning` |
| `thin` | Gold (default) | per-segment `no` (Standards 6, 7), gap named |
| `brand_gap` | Gold (default) | run-level `run_decline`, `kind: brand_gap` |
| `empty_scope` | Gold (default) | run-level `run_decline`, `kind: empty_scope` (null result) |
