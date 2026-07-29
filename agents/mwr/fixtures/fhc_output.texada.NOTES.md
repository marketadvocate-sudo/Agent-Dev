# fhc_output.texada.json — Annotation Sidecar

These annotation fields were carried on the Texada FHC artifact but are not part of the v2.0 FHC contract (which sets `additionalProperties: false`). They were moved here **verbatim** so the artifact validates while nothing is lost. **The rulings in these notes remain binding on any consumer of `fhc_output.texada.json`.**

## `_conversion_notes`

> PROVENANCE (July 28, 2026): Converted by Claude from the FHC agent v0.5 Beta prose output for Texada Software. All segment content, scores, sizes, EDPs, and pvp_angles are the agent's own findings, restructured into the v2.0 contract shape. STATUS: intentionally INCOMPLETE. (1) MEMBERS ABSENT on all three segments: the FHC run predates the members requirement and named zero accounts; the Gold roster requires a manual OSHA IMIS pull (the DOL enforcement API is retired per the FHC output itself), Silver requires the deal tracker, Bronze requires the EMMA/Census cross-reference. This artifact FAILS v2.0 validation on exactly those three points, by design, until rosters are stamped. (2) SOURCE STAMPS: source_refs below are stamped by the converter, not by FHC; several FHC claims carried no identifiable publisher (e.g. 73% vs 96% audit pass rates, 937/2,057 establishment counts, revenue filters) and were EXCLUDED from specific_facts rather than stamped on faith. See _facts_needing_sources. (3) KAHUNA FLAGS in _quality_flags require Doug's ruling before this artifact is treated as a golden input.

## `_facts_needing_sources`

- Paper-based systems achieve 73% audit pass rates vs 96% for digital (no publisher named)
- 937 companies verified-active under NAICS 532412; 7,534 under NAICS 423820; 2,057 under SIC 7353 (no publisher named; figures also mutually inconsistent)
- Insurance premium increases of 30-50% post-citation (no publisher named)
- Work stoppages costing $25,000-$75,000 per day (no publisher named)
- 92% of construction firms having trouble finding qualified workers; $2.2B annual technician-shortage losses (publishers likely AGC and AED Foundation; not confirmed by FHC)

## `_quality_flags`

- SILVER SIZE CONTRADICTION: segment sized at 650 companies but the output checkmarks the sub-$50K ACV minimum of 1,000. 650 < 1,000. Either the minimum-viable-segment rule is violated (Silver should not have shipped as-is) or the exception needs an explicit ruling.
- AED directory access: full directory requires membership; classed proprietary here, not public. Facts relying on it cannot seed GS6 asymmetry under MWR rules.
- OSHA IMIS data path: UI is human-usable; the DOL programmatic API is retired (last working Feb 2026 per FHC output). Members roster is a human-pull or Clay-provider task, not an agent fetch. Feed this to the access-architecture backlog item.
- GS6 RULING (Doug, July 28, 2026): the FHC output's original Gold pvp_angle (citation-anchored messaging with audit-failure statistics) fails GS6 by the expertise barrier: the buyer's own citation record can never be the asymmetry, and the supporting statistics were unsourced. Replaced with corridor demand synthesis (see gold pvp_angle). Generalized principle for the FHC agent spec: the EDP finds; it does not tell. Investigate stage must source telling data (cross-entity synthesis) separately from finding data (per-member signals).

## `segments[0].telling_sources_note` (Gold: The Compliance Cliff Operators)

> Corridor telling data comes from the Bronze segment's data_sources (MSRB EMMA, FHWA IIJA tracker, USAspending.gov). Finding and telling sources are deliberately different databases: GS6 material is second-order synthesis computed across entities, never first-order retrieval about the recipient.

