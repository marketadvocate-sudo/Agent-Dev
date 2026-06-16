#!/usr/bin/env python3
"""MWR self-test: pins the deterministic gate outcomes and validates every artifact.

Run from anywhere:  python3 agents/mwr/tools/selftest.py
Exits non-zero on any failure, so it is safe to wire into CI.

It asserts:
  * every fixture conforms to the input contract
  * the mechanical gate reaches the expected deterministic outcome per fixture/tier
  * every example output conforms to the output contract
  * no exemplar contains an em-dash or a CTA, and override warnings appear iff override
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import gate  # same directory

HERE = Path(__file__).resolve().parent
MWR = HERE.parent
FIX = MWR / "fixtures"
EX = MWR / "examples"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def brand_incomplete(artifact: dict) -> bool:
    b = artifact.get("brand_profile", {})
    return not (b.get("value_prop") or "").strip() or not (b.get("differentiator") or "").strip()


def segment_eligible(artifact: dict, tier: str, seg_id: str) -> bool:
    """Reproduce the mechanical gate decision for one segment: surviving public
    facts exist and the Standard 7 type-span holds."""
    brand = artifact["brand_profile"]
    seg = next(s for s in artifact["segments"] if s["segment_id"] == seg_id and s["tier"] == tier)
    surviving = [f for f in seg["specific_facts"]
                 if gate.source_survives_public(f["source"], brand)[0]]
    return bool(surviving) and gate.type_span_ok([f["fact_type"] for f in surviving])


def main() -> int:
    print("== Input contract: fixtures validate ==")
    fixtures = {
        "fhc_output.example.hma.json": [],
        "fhc_output.example.silver_override.json": [],
        "fhc_output.example.thin.json": [],
        "fhc_output.example.brand_gap.json": [],
    }
    arts = {}
    for fn in fixtures:
        art = json.loads((FIX / fn).read_text())
        arts[fn] = art
        errs = gate.validate_against(gate.FHC_SCHEMA, art)
        check(f"{fn} conforms to fhc schema", not errs, "; ".join(errs[:2]))

    print("\n== Deterministic gate outcomes ==")
    hma = arts["fhc_output.example.hma.json"]
    check("hma Gold january-sprinters eligible (yes)",
          segment_eligible(hma, "Gold", "gold-january-sprinters"))
    check("hma Silver margin-bleed declines (type-span fail)",
          not segment_eligible(hma, "Silver", "silver-margin-bleed-mcos"))
    check("hma Bronze warning-notice declines (type-span fail)",
          not segment_eligible(hma, "Bronze", "bronze-warning-notice-window"))

    sv = arts["fhc_output.example.silver_override.json"]
    check("silver_override Silver eligible (yes under override)",
          segment_eligible(sv, "Silver", "silver-margin-bleed-mcos"))

    thin = arts["fhc_output.example.thin.json"]
    check("thin Gold declines (single bare public fact)",
          not segment_eligible(thin, "Gold", "gold-thin-evidence"))

    bg = arts["fhc_output.example.brand_gap.json"]
    check("brand_gap triggers run-level decline", brand_incomplete(bg))

    print("\n== Output contract: examples validate ==")
    outputs = ["hma", "silver_override", "thin", "brand_gap"]
    outs = {}
    for o in outputs:
        data = json.loads((EX / f"mwr_output.{o}.json").read_text())
        outs[o] = data
        errs = gate.validate_against(gate.MWR_SCHEMA, data)
        check(f"mwr_output.{o}.json conforms to output schema", not errs, "; ".join(errs[:2]))

    print("\n== Format + warning invariants on exemplars ==")
    for o, data in outs.items():
        override = data.get("override", False)
        for v in data.get("segment_verdicts", []):
            ex = v.get("exemplar")
            if not ex:
                continue
            text = " ".join([ex["subject_line"], ex["eyebrow_line"], ex["message_body"]])
            check(f"{o}/{v['segment_id']} no em-dash", "—" not in text and "–" not in text)
            check(f"{o}/{v['segment_id']} no CTA in body", "?" not in ex["message_body"])
            check(f"{o}/{v['segment_id']} override_warning iff override",
                  ("override_warning" in ex) == override)

    print()
    if failures:
        print(f"SELFTEST FAILED: {len(failures)} check(s) failed -> {failures}")
        return 1
    print("SELFTEST PASSED: all checks green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
