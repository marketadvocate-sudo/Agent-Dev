# fhc_output.texada.silver_only.json — Staging Derivative (header note)

**This is a staging derivative, not a production FHC artifact.** It is a copy of
`fhc_output.texada.json` reduced to **only the Silver segment**
(`silver-rollup-casualties`), created to test **override-mode** behavior of the MWR
v1.5 agent (Silver instead of Gold).

- **All content is verbatim from the parent** `fhc_output.texada.json` (same
  `brand_profile`, `industry_analysis`, `verdict`, and the Silver segment as-is),
  with one addition: the Silver segment's `members` array, stamped from the segment's
  own `specific_facts` (Tuckahoe Holdings and Wolter), each sourced with the existing
  trade-press `source_ref` from those facts. No external data was used.
- **Why this note lives in a sidecar, not the JSON:** the v2.0 FHC contract sets
  `additionalProperties: false`, so any in-file comment/header field would fail
  validation. The task required both a header note and a fully-valid (zero-failure)
  fixture; those cannot both live inside the JSON, so the note is here and the label
  is also carried by the filename. (Flagged for Doug.)
- **Dangling reference (verbatim consequence):** the inherited `verdict`
  `recommended_segment_id` is `gold-compliance-cliff`, which is not present in this
  Silver-only derivative. Kept verbatim per instruction; it is not load-bearing for
  an override-mode Silver run and is not a validation error.
- The rulings in `fhc_output.texada.NOTES.md` (corridor demand synthesis; the EDP
  finds, it does not tell) remain binding on any consumer of this derivative.
