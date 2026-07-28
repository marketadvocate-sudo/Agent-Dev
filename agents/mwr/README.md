# MWR — Messages Worth Receiving Agent

A **binary gate** in the Cannonball GTM agent library. It consumes one FHC output
artifact and, per in-scope Gold segment, returns a verdict: **can a PVP-grade
message be built from this segmentation work, yes or no?** A `yes` is proven by one
cohort-level exemplar that clears all seven Gold Standards; a `no` names the gap.
The verdict is the product. The exemplar is evidence, not a deliverable for scaled
use. See `MWR_CONSTITUTION.md` (v1.4) for the governing law.

## Layout

| Path | What it is |
| --- | --- |
| `MWR_CONSTITUTION.md` | Governing document, v1.4. The agent obeys it; the reviewer rules with it. |
| `AGENT.md` | The agent spec / system prompt encoding Stages 0 to 6. |
| `GATE_RUN_CHECKLIST.md` | The reviewer's repeatable acceptance checklist (constitution Section 7). |
| `GATE_RUN_REPORT.hma.md` | A filled checklist: the HMA gate run, the moment of truth. |
| `DECISIONS.md` | Persistent log of Doug's rulings behind each constitution version. |
| `contracts/fhc_output.schema.json` | **Input** contract. The sole accepted input. |
| `contracts/mwr_output.schema.json` | **Output** contract. Per-segment `pvp_achievable` + `revised`; `run_decline.kind`. |
| `fixtures/fhc_output.example.hma.json` | Stamped HMA fixture (every source carries `publisher` + `access_class`). |
| `fixtures/fhc_output.example.silver_override.json` | Hand-filled Silver segment with type-spanning public facts. |
| `fixtures/fhc_output.example.thin.json` | Data-thin Gold segment (one bare public fact). |
| `fixtures/fhc_output.example.brand_gap.json` | Empty `value_prop` to trigger a run-level decline. |
| `fixtures/fhc_output.example.empty_scope.json` | Complete brand, only a Silver segment: the Gold scope is empty. |
| `examples/mwr_output.*.json` | The gate run over each fixture (see matrix below). |
| `tools/gate.py` | Deterministic harness for the mechanical stages and schema validation. |
| `tools/selftest.py` | Pins expected outcomes for every fixture and validates every artifact. |

## Pipeline (six stages)

0. **Ingest and validate** against the input contract (deterministic).
1. **Brand-profile gate**: empty `value_prop`/`differentiator` -> one run-level decline.
2. **Scope**: Gold by default; Silver/Bronze only by explicit override (instead-of), with a per-message trade-off warning. An empty scoped tier is a run-level `empty_scope` null result, not a decline.
3. **Per-segment sufficiency pre-flight**: no surviving public anchor -> per-segment `no`.
4. **Build one cohort-level exemplar**: no merge fields, no CTA, no em-dashes, Cannonball voice; Standards 3/6/7 on public sources only.
5. **Adversarial self-check**: seven standards yes/no, mechanical source-class + hardening checks, Standard 7 type-span; 0 miss -> yes, 1 miss -> one revision pass, 2+ -> no.
6. **Format enforcement and assembly** into the output contract.

Stages 0, 1, 2, the mechanical sub-checks of 5, and 6 are deterministic. Stages 3,
4, and the standard-by-standard calls in 5 are judgment, bounded by the rules.

## Running the deterministic harness

```sh
pip install jsonschema

# Mechanical gate over the Gold scope of the fixture:
python3 tools/gate.py report fixtures/fhc_output.example.hma.json --tier Gold

# Validate a produced MWR output against the output contract:
python3 tools/gate.py validate-output examples/mwr_output.hma.json

# Run the full regression suite (all fixtures + all outputs):
python3 tools/selftest.py
```

## Demonstration matrix

Every branch of the output contract is exercised by a fixture/output pair:

| Fixture | Scope | Verdict | Demonstrates |
| --- | --- | --- | --- |
| `hma` | Gold (default) | `yes` | PVP achievable; GS6 asymmetry rebuilt on public data only |
| `silver_override` | Silver (override) | `yes` + `override_warning` | Per-message trade-off warning under an instead-of override |
| `thin` | Gold (default) | `no` (GS 6, 7) | Per-segment decline naming the gap and the input that closes it |
| `brand_gap` | Gold (default) | run-level decline (`kind: brand_gap`) | One decline for an empty `value_prop`, not N identical no's |
| `empty_scope` | Gold (default) | run-level decline (`kind: empty_scope`) | Null result: no Gold segment exists, so nothing to gate (not a "no") |

Note on fidelity: the `hma` fixture's Silver segment declines on Standard 7 (its
specifics are all quantities, no name/location/event anchor), so an override would
not lower the bar. The `silver_override` fixture is a hand-filled artifact (a
contract-legitimate input per constitution Section 2) built to carry type-spanning
public facts, so it can reach `yes` and show the warning.

Note on the FHC contract v2.0 (members roster): every segment now carries a required
`members` array (each account with its observed `edp_value` and a stamped source).
The `hma` Gold roster is five real KFF-sourced states; its Silver roster is two real
SEC-sourced MCOs. The other fixtures carry real members where they name a public
entity, and `thin` carries one member explicitly labeled synthetic scaffolding. The
`hma` **Bronze** segment was **dropped** at v2.0 because its roster needs real named
open-case hospitals from the CMS enforcement dataset that could not be sourced; its
restoration is tracked in `CC_WORK_ORDERS_AND_BACKLOG.md` (item 7).

## The moment of truth (HMA Gold segment)

The fixture's FHC-drafted `pvp_angle` fails three ways: it builds asymmetry on the
**proprietary** KFF/HMA survey, anchors on the **vendor_published** (and self-cited)
HMA issue brief, and ends on a **CTA**. The gate strips all three. The rebuilt
exemplar holds the information asymmetry on **public data alone**: the June 1, 2026
CMS interim final rule (which reset medical-frailty exemption assumptions) read
against the public KFF Work Requirements Tracker (Nebraska enforcing early as of
May 1, 2026 while non-movers have no declared path), on the fixed January 1, 2027
clock. Verdict: **`yes`**, cleared on the first pass, all seven standards met from
five public facts spanning five fact types.
