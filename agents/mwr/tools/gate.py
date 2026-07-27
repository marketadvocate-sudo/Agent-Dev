#!/usr/bin/env python3
"""MWR gate — deterministic harness.

Executes the mechanical, no-judgment portions of MWR_CONSTITUTION.md v1.4:

  Stage 0  validate the FHC artifact against the input contract
  Stage 1  brand-profile gate (run-level decline)
  Stage 2  scope selection (Gold default; Silver/Bronze override)
  Stage 5  source-class hardening checks (public-only, no self-citation,
           url present) and the Standard 7 type-spanning test

What it does NOT do: write the message or grade Standards 1-6 (judgment, the
agent's job). It reports, per in-scope segment, which specific_facts survive as
usable public anchors and whether Standard 7's type-spanning rule can be met. A
segment with no surviving public facts is a deterministic per-segment "no".

It can also validate an MWR output artifact against the output contract.

Usage:
  gate.py report  <fhc_artifact.json>            [--tier Gold|Silver|Bronze]
  gate.py validate-output <mwr_output.json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
CONTRACTS = HERE.parent / "contracts"
FHC_SCHEMA = CONTRACTS / "fhc_output.schema.json"
MWR_SCHEMA = CONTRACTS / "mwr_output.schema.json"


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def validate_against(schema_path: Path, instance: dict) -> list[str]:
    validator = Draft202012Validator(load(schema_path))
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def domain(url: str) -> str:
    if not url:
        return ""
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def source_survives_public(source: dict, brand: dict) -> tuple[bool, str]:
    """The Stage 5 mechanical gate. Returns (survives, reason_if_not).

    A source may support Standards 3, 6, 7 only if it is public-classed, not
    self-cited (publisher != company and domain != vendor domain), and carries a
    resolvable-looking url.
    """
    ac = source.get("access_class")
    if ac != "public":
        return False, f"access_class={ac} (only 'public' earns 3/6/7)"
    company = (brand.get("company") or "").strip().lower()
    publisher = (source.get("publisher") or "").strip().lower()
    if publisher and company and publisher == company:
        return False, "self-citation: publisher matches brand_profile.company"
    vendor_domain = domain(brand.get("url", ""))
    src_domain = domain(source.get("url", ""))
    if vendor_domain and src_domain and src_domain == vendor_domain:
        return False, "self-citation: source url domain belongs to the vendor"
    if not (source.get("url") or "").strip():
        return False, "public source carries no url (not reachable by the buyer)"
    return True, ""


# Standard 7: specifics must span >=2 fact_types, with >=1 of name/location/event.
ANCHOR_TYPES = {"name", "location", "event"}


def type_span_ok(fact_types: list[str]) -> bool:
    return len(set(fact_types)) >= 2 and bool(set(fact_types) & ANCHOR_TYPES)


def report(args) -> int:
    artifact = load(args.artifact)

    print("== Stage 0: validate FHC artifact against input contract ==")
    errors = validate_against(FHC_SCHEMA, artifact)
    if errors:
        for e in errors:
            print(f"  REJECT {e}")
        return 1
    print("  OK: conforms to fhc_output.schema.json")

    brand = artifact.get("brand_profile", {})

    print("\n== Stage 1: brand-profile gate ==")
    missing = [f for f in ("value_prop", "differentiator") if not (brand.get(f) or "").strip()]
    if missing:
        print(f"  RUN-LEVEL DECLINE: brand profile incomplete, missing {missing}.")
        print("  Every segment fails Standard 2 identically. One decline, not N.")
        return 0
    print("  OK: value_prop and differentiator present")

    tier = args.tier
    print(f"\n== Stage 2: scope = {tier} ==")
    segments = [s for s in artifact["segments"] if s.get("tier") == tier]
    if not segments:
        print(f"  RUN-LEVEL empty_scope: no {tier} segments in the artifact.")
        print("  Null result, not a 'no' on any segment. Nothing to gate at this")
        print(f"  scope. Add a {tier} segment, or override to a populated tier.")
        return 0
    # recommended first
    segments.sort(key=lambda s: not s.get("recommended", False))
    print(f"  {len(segments)} segment(s) in scope: {[s['segment_id'] for s in segments]}")

    print("\n== Stage 3/5 (mechanical): per-segment public-anchor survival ==")
    deterministic_no = []
    for seg in segments:
        print(f"\n  segment: {seg['segment_id']}  ({seg.get('name','')})")

        edp_src = seg.get("edp", {}).get("source", {})
        ok, why = source_survives_public(edp_src, brand)
        print(f"    edp.source [{edp_src.get('publisher','?')}]: "
              f"{'PUBLIC-OK' if ok else 'INVALID -> ' + why}")

        surviving = []
        for f in seg.get("specific_facts", []):
            src = f.get("source", {})
            ok, why = source_survives_public(src, brand)
            tag = "PUBLIC-OK" if ok else f"no-credit ({why})"
            print(f"      [{f.get('fact_type'):>6}] {f.get('value','')!r:<22} "
                  f"src={src.get('publisher','?')} -> {tag}")
            if ok:
                surviving.append(f)

        span_ok = type_span_ok([f["fact_type"] for f in surviving])
        print(f"    surviving public facts: {len(surviving)}  | "
              f"Standard-7 type-span: {'OK' if span_ok else 'FAIL'} "
              f"(types={sorted({f['fact_type'] for f in surviving})})")

        if not surviving or not span_ok:
            deterministic_no.append(seg["segment_id"])
            print("    => DETERMINISTIC 'no' (insufficient public anchors for 3/6/7).")
        else:
            print("    => eligible for 'yes' pending judgment on Standards 1-6.")

    print("\n== Summary ==")
    if deterministic_no:
        print(f"  Deterministic 'no' (data gap): {deterministic_no}")
    eligible = [s["segment_id"] for s in segments if s["segment_id"] not in deterministic_no]
    print(f"  Eligible for PVP (await judgment): {eligible}")
    return 0


def validate_output(args) -> int:
    out = load(args.output)
    print("== Validate MWR output against output contract ==")
    errors = validate_against(MWR_SCHEMA, out)
    if errors:
        for e in errors:
            print(f"  INVALID {e}")
        return 1
    print("  OK: conforms to mwr_output.schema.json")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="MWR deterministic gate harness")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("report", help="run mechanical gate over an FHC artifact")
    pr.add_argument("artifact", type=Path)
    pr.add_argument("--tier", default="Gold", choices=["Gold", "Silver", "Bronze"])
    pr.set_defaults(func=report)

    pv = sub.add_parser("validate-output", help="validate an MWR output artifact")
    pv.add_argument("output", type=Path)
    pv.set_defaults(func=validate_output)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
