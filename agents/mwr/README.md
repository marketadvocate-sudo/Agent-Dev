# MWR — Messages Worth Receiving Agent

A **binary gate** in the Cannonball GTM agent library. It consumes one FHC output
artifact and, per in-scope Gold segment, returns a verdict: **can a PVP-grade
message be built from this segmentation work, yes or no?** A `yes` is proven by one
cohort-level exemplar that clears all seven Gold Standards; a `no` names the gap.
The verdict is the product. The exemplar is evidence, not a deliverable for scaled
use. See `MWR_CONSTITUTION.md` (v1.3) for the governing law.

## Layout

| Path | What it is |
| --- | --- |
| `MWR_CONSTITUTION.md` | Governing document, v1.3. The agent obeys it; the reviewer rules with it. |
| `AGENT.md` | The agent spec / system prompt encoding Stages 0 to 6. |
| `contracts/fhc_output.schema.json` | **Input** contract. The sole accepted input. |
| `contracts/mwr_output.schema.json` | **Output** contract. Per-segment `pvp_achievable` + `revised`. |
| `fixtures/fhc_output.example.hma.json` | Stamped HMA fixture (every source carries `publisher` + `access_class`). |
| `examples/mwr_output.hma.json` | The gate run over the fixture: Gold segment returns `yes`. |
| `tools/gate.py` | Deterministic harness for the mechanical stages and schema validation. |

## Pipeline (six stages)

0. **Ingest and validate** against the input contract (deterministic).
1. **Brand-profile gate**: empty `value_prop`/`differentiator` -> one run-level decline.
2. **Scope**: Gold by default; Silver/Bronze only by explicit override (instead-of), with a per-message trade-off warning.
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
```

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
