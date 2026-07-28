#!/usr/bin/env python3
"""MWR gate — deterministic harness.

Executes the mechanical, no-judgment portions of MWR_CONSTITUTION.md v1.5:

  Stage 0  validate the FHC artifact against the input contract
  Stage 1  brand-profile gate (run-level decline)
  Stage 2  scope selection (Gold default; Silver/Bronze override)
  Stage 5  source-class hardening checks (public-only, no self-citation,
           url present) and the Standard 7 type-spanning test
  Stage 6  (lint-exemplar) v1.5 format checks over a produced message:
           body/subject word counts, em-dash, and buyer-conditional detection
           (the entailment alarm), optionally confirming members are present.

What it does NOT do: write the message, grade Standards 1-6, or judge the
insight (all judgment, the agent's job). The buyer-conditional scan raises an
alarm; whether a flagged conditional is truly unentailed is the agent's call.

It can also validate an MWR output artifact against the output contract.

Usage:
  gate.py report  <fhc_artifact.json>            [--tier Gold|Silver|Bronze]
  gate.py validate-output <mwr_output.json>
  gate.py lint-exemplar   <mwr_output.json>      [--fhc <fhc_artifact.json>]
"""
from __future__ import annotations

import argparse
import json
import re
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


# --- v1.5 mechanical exemplar checks (the bouncer; judgment stays out) ---

BODY_MAX = 165          # constitution v1.5: 150 target, 165 hard ceiling
BODY_TARGET = 150
SUBJECT_MAX = 8         # words
SECOND_PERSON = re.compile(r"\b(you|your|yours|you're|youre)\b", re.I)
# Hedges that, aimed at the buyer, mark a buyer-conditional (entailment alarm).
HEDGE = re.compile(r"\b(if|whether|may have|may be|might|maybe|likely|probably|perhaps|in case|could have|possibly)\b", re.I)


def word_count(text: str) -> int:
    return len(text.split())


def split_sentences(text: str) -> list[str]:
    # Good enough for a smoke check: split on sentence punctuation and newlines.
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [s.strip() for s in parts if s.strip()]


def buyer_conditionals(body: str) -> list[str]:
    """Sentences that hedge a claim AND address the buyer in the second person.
    A mechanical alarm for the entailment rule, not a verdict: the agent's
    judgment decides whether the conditional is truly unentailed."""
    flagged = []
    for s in split_sentences(body):
        if SECOND_PERSON.search(s) and HEDGE.search(s):
            flagged.append(s)
    return flagged


def lint_exemplar(args) -> int:
    out = load(args.output)
    fhc = load(args.fhc) if getattr(args, "fhc", None) else None
    members_by_seg = {}
    if fhc:
        for s in fhc.get("segments", []):
            members_by_seg[s.get("segment_id")] = len(s.get("members", []) or [])

    print("== v1.5 mechanical exemplar lint ==")
    failures = 0
    exemplars = 0
    for v in out.get("segment_verdicts", []):
        ex = v.get("exemplar")
        if not ex:
            continue
        exemplars += 1
        seg = v.get("segment_id", "?")
        subj_wc = word_count(ex.get("subject_line", ""))
        body_wc = word_count(ex.get("message_body", ""))
        text = " ".join([ex.get("subject_line", ""), ex.get("eyebrow_line", ""), ex.get("message_body", "")])
        emdash = ("—" in text) or ("–" in text)
        conds = buyer_conditionals(ex.get("message_body", ""))
        print(f"\n  segment: {seg}")
        def line(ok, label, detail=""):
            nonlocal failures
            if not ok:
                failures += 1
            print(f"    [{'ok' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))
        line(subj_wc <= SUBJECT_MAX, f"subject <= {SUBJECT_MAX} words", f"({subj_wc} words)")
        line(body_wc <= BODY_MAX, f"body <= {BODY_MAX} words", f"({body_wc} words)"
             + ("  [over 150 target, within ceiling]" if BODY_TARGET < body_wc <= BODY_MAX else ""))
        line(not emdash, "no em-dash")
        line(not conds, "no buyer-conditional (entailment)",
             "" if not conds else "-> " + " | ".join(conds))
        if fhc is not None:
            n = members_by_seg.get(seg, 0)
            line(n >= 1, "segment carries members (entailment possible)", f"({n} members)")
    if exemplars == 0:
        print("  (no exemplars in this output; nothing to lint)")
    print(f"\n  {exemplars} exemplar(s) linted, {failures} mechanical failure(s).")
    return 1 if failures else 0


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

    pl = sub.add_parser("lint-exemplar", help="v1.5 mechanical checks over an MWR output's exemplars")
    pl.add_argument("output", type=Path)
    pl.add_argument("--fhc", type=Path, default=None,
                    help="optional FHC artifact, to confirm each segment carries members")
    pl.set_defaults(func=lint_exemplar)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
