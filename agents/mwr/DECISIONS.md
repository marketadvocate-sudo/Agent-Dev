# MWR Decisions Log

Rulings that persist across sessions. Recorded per the build brief ("when Doug rules,
record the ruling so it persists"). The constitution remains the governing document;
this log captures the reasoning and the brief-vs-constitution reconciliations behind
specific constitution versions.

---

## 2026-07-27 — Reconciliation of the build brief against constitution v1.3

Reviewer: Doug. Context: a resumed session reread the whole agent against the
constitution and surfaced three items. Rulings:

### D1. Keep the one-miss revision pass (PQS boundary)

The build brief summarized the standard as "7/7 = TRUE PVP and anything less = PQS,"
and noted a stricter boundary had been discussed. The constitution v1.3 Sections 4 and 7
say something more forgiving: 7/7 ships; **exactly one miss is borderline** and gets one
revision pass, shipping with `revised: true` if it clears; only **two or more** misses is
PQS. **Ruling: the constitution's revision-pass model stands.** The stricter
"anything short of 7/7 is PQS, no revision" boundary is **not** adopted. The build
already implemented the constitution correctly; no logic change. Recorded in the v1.4
changelog so it does not resurface.

### D2. Generalize `run_decline` to cover empty scope (constitution → v1.4)

A reachable, valid input produced an unrepresentable output: an artifact with a complete
brand profile but **no segment in the scoped tier** (e.g. only Silver/Bronze, no override).
`AGENT.md` Stage 2 told the agent to emit empty `segment_verdicts`, which the output
schema rejects (it demands either a `run_decline` or at least one verdict). **Ruling:
generalize `run_decline`** with a `kind` discriminator (`brand_gap` | `empty_scope`);
`empty_scope` carries `scoped_tier` and is framed as a **null result** (nothing to gate),
explicitly distinct from the brand-gap decline (a real "no"). Because this adds a third
run-level outcome to the constitution's Section 6 taxonomy, it is a constitutional
amendment: **bumped to v1.4**, and `mwr_version` moves to `1.4` across AGENT.md and all
example outputs.

### D3. Draft `GATE_RUN_CHECKLIST.md`

The build order referenced a `GATE_RUN_CHECKLIST.md` that did not exist in the repo.
**Ruling: draft it** from the constitution Section 7 reviewer charge plus the
demonstration matrix, and produce a filled HMA run in that format
(`GATE_RUN_REPORT.hma.md`).

### Not adopted / deferred

- The self-test CTA check was tightened from a bare `?`-only heuristic to a small
  phrase blocklist. This is a smoke test only; the agent's real CTA guard remains the
  Stage-1 judgment call in `AGENT.md`.
