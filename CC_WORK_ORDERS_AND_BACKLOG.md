# Claude Code Work Orders + PVP Capability Backlog

Two work orders, one per repo, in dependency order (contract first, then the
agent that consumes it). Plus the running backlog, because this session solved
one challenge, not the whole problem.

---

## Work Order 1 — FHC side (contract + upstream agent)

Paste into a Claude Code session on the repo that owns the contract:

```
Read FHC_CONTRACT_AMENDMENT.md. Plan first, no code until I approve.

1. Amend fhc_output.schema.json: add the required members array and optional
   resolved_conditions to the segment definition, per the amendment doc.
   Reconcile field names against the FHC agent's live export format before
   committing. Add schema_version if absent.
2. Amend the FHC agent spec with the condition sourcing rule from Section 3
   of the amendment doc.
3. Bring the HMA fixture up to the amended contract: stamp the members array
   from the KFF Work Requirements Tracker (state, implementation status, one
   shared source_ref per the tracker). Flag any state whose status you cannot
   read from the tracker rather than guessing.
4. Re-validate the fixture against the amended schema. Report the member
   count and coverage.
End with open questions as a numbered list.
```

## Work Order 2 — MWR side (constitution + agent + fixtures)

Run after Work Order 1 merges, so the agent updates against the amended
contract:

```
Read MWR_CONSTITUTION_AMENDMENT_v1.5.md. Plan first, no code until I approve.

1. Apply all six amendments to MWR_CONSTITUTION.md. Bump to v1.5, update the
   Section 8 version log with the provided entry.
2. Update AGENT.md: Stage 4 drafts from the insight outward (state the
   one-sentence insight and the buyer action first, then draft, then verify
   every specific serves them; check every buyer claim against members and
   resolved_conditions before asserting). Stage 5 grades in dependency order
   per amended Section 7 and applies the entailment rule's three exits.
3. Update mwr_output.schema.json: the scorecard records keystone-cascade
   failures distinctly from independent failures, and the decline's
   what_would_change_the_verdict carries the FHC work order when the
   entailment rule's third exit fires.
4. Replace examples/mwr_output.hma.json with the v1.5-passing rewrite Doug
   provides. Add the rejected first message as
   examples/mwr_output.hma.REJECTED.json with its 2/7 scorecard, labeled as
   the negative golden fixture: ingredient-stuffing without an insight.
5. Update gate.py if it can mechanically check any of the new rules (word
   counts, subject length, buyer-conditional detection via if/whether/may
   have aimed at second person, entailment lookups against members). Keep
   judgment calls out of the script; it stays the bouncer, not the author.
6. Re-run GATE_RUN_CHECKLIST.md end to end. The agent must produce
   insight-led, entailed, under-165-word output unprompted.
7. Tag v1.1 after the gate run passes.
End with open questions as a numbered list.
```

Before running Work Order 2, Doug supplies: the final edited rewrite text
(his pass on the 148-word draft), and rulings on the two open Kahuna calls
below.

---

## PVP Capability Backlog

This session resolved one challenge. The rest of the known list, so nothing
silently drops. Statuses: OPEN (needs a ruling or a build), PARTIAL
(addressed but unproven), WATCH (monitor across runs before acting).

**1. Entailment / conditionals — APPLIED (v1.5), proof pending.** The
entailment rule and the members roster are shipped: constitution v1.5, AGENT.md
Stage 4/5, `gate.py lint-exemplar` (buyer-conditional scan), FHC contract v2.0.
Demonstrated on the HMA fixture (`GATE_RUN_REPORT.v1.5.hma.md`). Still unproven
end to end until a **fresh** FHC artifact with a members roster flows through the
updated agent and Doug ratifies the output. That is the deferred **v1.5 golden
fixture**: it will be produced by the v1.5 agent from a forthcoming **Texada
Software** FHC artifact and ratified by Doug, then committed as
`examples/mwr_output.hma.json`'s successor. Until then, the committed
`examples/mwr_output.hma.json` stays a pre-v1.5 (v1.4-graded) artifact and does
not pass the v1.5 lint (length, buyer-conditional). The negative golden
(`mwr_output.hma.REJECTED.json`) is pending Doug's paste of the rejected 2/7
message.

**2. Insight generation quality — OPEN, and the hard one.** The v1.5 rules
let the grader catch a missing insight. Nothing yet makes the agent reliably
FIND the best insight rather than the first passable one. Candidate
approaches: Stage 4 generates three candidate insights and grades them
against each other before drafting; or a distinct insight-selection stage
with its own criteria. Needs design, not just rules. This is the core PVP
capability and deserves its own session.

**3. GS6 market-knowledge judgment — RULED (2026-07-28).** Ruling: stays a
permanent human call per message. The constitution does NOT encode per-vertical
heuristics and no vertical-context files are added. Recorded as D4 in
`agents/mwr/DECISIONS.md`.

**4. Sender-credential presence — RULED (2026-07-28).** Ruling: no sender
credential in the message body, ever; identity lives in the sender name and
brand alone. Added as a hard format rule in constitution Section 5 (v1.5).
Recorded as D5 in `agents/mwr/DECISIONS.md`.

**5. Self-score inflation — PARTIAL.** The keystone rule and mechanical
checks close the ingredient-stuffing route. The evidence-citation
requirement exists. WATCH across the next several runs: does the agent's
Stage 5 self-score match Doug's Red-hat score? Divergence means the
disqualifiers need more teeth.

**6. Cannonball voice adherence — OPEN.** No mechanical check exists or
likely can. Current control is the model plus the constitution's voice
clause. Consider: a voice checklist derived from the Doug Voice Bible as a
Stage 4 reference, and voice as an explicit line in the reviewer's charge.

**7. Silver/Bronze fixture gap — OPEN, carried from recovery.** Run 2 of the
gate checklist still cannot execute. Resolves free of charge when Work Order
1's fixture re-stamp happens IF a fresh FHC export restores the full segment
set; otherwise still needs synthetic scaffolding.

> **Update (2026-07-27, v2.0 migration):** The HMA fixture's **Bronze** segment
> ("The Warning Notice Window") was **dropped** when the FHC contract went to
> v2.0. The required members roster for Bronze needs real named open-case
> hospitals from the CMS Hospital Price Transparency Enforcement dataset, and
> that data could not be sourced: `data.cms.gov` returns 403 to automated fetch
> and web search yields only aggregates (no named open-case hospitals). Per
> ruling, nothing was fabricated or placeholdered. **Restoration condition:**
> re-add the Bronze segment with a real members roster the moment the CMS data
> path opens — a manual paste of named open-case hospitals with their status, or
> the data.cms.gov dataset API once reachable. The Silver/Bronze demonstration of
> a Standard-7 type-span decline is likewise reduced until Bronze returns.

**8. Multi-segment behavior — WATCH.** Verdict-per-segment is specified but
has only ever run against a one-segment fixture. First multi-segment
artifact should get a deliberate review.

---

## FHC-repo session backlog (from the Texada artifact, 2026-07-28)

These are for the deferred session on the **FHC agent's** repo, not MWR. Raised by
`fixtures/fhc_output.texada.json` and its `_quality_flags`.

**F1. Investigate stage must source telling data separately from finding data.**
Principle: **the EDP finds; it does not tell.** The finding signal (per-member,
first-order retrieval about the recipient, e.g. an OSHA citation) proves membership,
timing, and pain. It must never be the message content, because the buyer's own
record fails GS6 by the expertise barrier and reads as surveillance. The telling
material (the GS6 asymmetry) is second-order synthesis computed **across** entities
from **different** databases (e.g. EMMA bond issuances and FHWA/IIJA awards near the
member's yard, translated into corridor demand). The Investigate stage must source
these two separately and stamp finding-vs-telling. See the Texada Gold `pvp_angle`
(RULED: corridor demand synthesis) and `telling_sources_note`.

**F2. Minimum-viable-segment self-certification bug.** FHC's output check-marked the
sub-$50K-ACV minimum of 1,000 companies for the Texada **Silver** segment while
sizing that segment at **650** companies. 650 < 1,000: the check passed a segment
that violates the rule. Fix the FHC minimum-viable-segment check so it cannot
self-certify below its own threshold, or require an explicit logged exception.

**F3. Access-architecture note (carried).** The Texada Gold roster depends on OSHA
IMIS, whose DOL programmatic API is retired (last working Feb 2026); the UI is
human-usable only, so the members roster is a human/Clay-provider pull, not an agent
fetch. The AED member directory is membership-gated and is classed proprietary (it
cannot seed GS6 asymmetry). Feed both to the FHC access-architecture work.

---

## Federated design session (open contract-design questions, not for action now)

Surfaced by the Texada artifact; neither gets decided mid-flight on v2.0.

**D1. Should the FHC contract permit `_`-prefixed annotation/provenance fields?** The
Texada artifact carried `_conversion_notes`, `_facts_needing_sources`, `_quality_flags`,
and a segment-level `telling_sources_note`, all rejected by `additionalProperties:
false`. For now they live verbatim in a sidecar (`fixtures/fhc_output.texada.NOTES.md`).
The question is whether the contract should have a defined home for provenance and
annotations rather than pushing them to a sidecar.

**D2. Should `verdict.confidence` be per-segment rather than a single enum?** FHC
produced "High for Gold; Medium-High for Silver; Medium for Bronze" plus a validation
recommendation; the contract models one enum (High|Medium|Low). For now confidence was
set to "High" (the recommended Gold segment) and the per-segment detail moved into
`verdict.reasons`. The question is whether confidence should be structured per segment.
