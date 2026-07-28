#!/usr/bin/env python3
"""MWR self-test: pins the deterministic gate outcomes and validates every artifact.

Run from anywhere:  python3 agents/mwr/tools/selftest.py
Exits non-zero on any failure, so it is safe to wire into CI.

It asserts:
  * every fixture conforms to the input contract (v2.0)
  * the mechanical gate reaches the expected deterministic outcome per fixture/tier
  * the v2.0 membership roster: every segment carries >=1 stamped member, the thin
    fixture's synthetic member is labeled and cannot earn public credit, and a
    pre-v2.0 artifact (no members) fails validation loudly
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

# Smoke-test only, NOT the agent's real Stage-1 CTA grader (that is judgment).
# A question mark, or any of these lowercase asks, flags a likely CTA so an
# obvious "ask" cannot slip into an exemplar unnoticed.
CTA_PHRASES = (
    "let me know", "happy to", "would you", "worth a", "book a", "schedule a",
    "reach out", "get in touch", "20 minutes", "twenty minutes", "hop on",
    "set up a call", "grab time", "connect for",
)


def looks_like_cta(body: str) -> bool:
    low = body.lower()
    return "?" in body or any(p in low for p in CTA_PHRASES)


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
        "fhc_output.example.empty_scope.json": [],
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
    # Bronze segment was dropped when the FHC contract went to v2.0: its members
    # roster requires real named open-case hospitals from the CMS enforcement
    # dataset, which could not be sourced. Restoration is tracked in
    # CC_WORK_ORDERS_AND_BACKLOG.md (backlog item 7). Do not re-add without data.

    sv = arts["fhc_output.example.silver_override.json"]
    check("silver_override Silver eligible (yes under override)",
          segment_eligible(sv, "Silver", "silver-margin-bleed-mcos"))

    thin = arts["fhc_output.example.thin.json"]
    check("thin Gold declines (single bare public fact)",
          not segment_eligible(thin, "Gold", "gold-thin-evidence"))

    bg = arts["fhc_output.example.brand_gap.json"]
    check("brand_gap triggers run-level decline", brand_incomplete(bg))

    es = arts["fhc_output.example.empty_scope.json"]
    check("empty_scope has complete brand profile (not a brand gap)", not brand_incomplete(es))
    check("empty_scope has no Gold segment (default scope is empty)",
          not any(s["tier"] == "Gold" for s in es["segments"]))
    check("empty_scope has a populated non-Gold tier available for override",
          any(s["tier"] in ("Silver", "Bronze") for s in es["segments"]))

    print("\n== v2.0 membership roster ==")
    for fn, art in arts.items():
        check(f"{fn}: schema_version is 2.0", art.get("schema_version") == "2.0")
        check(f"{fn}: every segment carries >=1 member",
              all(isinstance(s.get("members"), list) and len(s["members"]) >= 1
                  for s in art["segments"]))
        check(f"{fn}: every member carries a stamped source",
              all(m.get("source", {}).get("name") and m["source"].get("publisher")
                  and m["source"].get("access_class") in ("public", "vendor_published", "proprietary")
                  for s in art["segments"] for m in s["members"]))
    # The thin fixture's one member is synthetic scaffolding: it must be labeled as
    # such in the entry and must not be able to earn public credit.
    thin_mem = thin["segments"][0]["members"][0]
    check("thin member is labeled synthetic scaffolding",
          "synthetic" in thin_mem["name"].lower()
          or "synthetic" in thin_mem["source"].get("name", "").lower())
    check("thin synthetic member is not access_class public",
          thin_mem["source"].get("access_class") != "public")
    # A pre-v2.0 artifact (schema_version 1.0, no members) must fail loudly.
    legacy = json.loads((FIX / "fhc_output.example.hma.json").read_text())
    legacy["schema_version"] = "1.0"
    for s in legacy["segments"]:
        s.pop("members", None)
    check("pre-v2.0 artifact fails loudly (version const + missing members)",
          bool(gate.validate_against(gate.FHC_SCHEMA, legacy)))

    print("\n== Output contract: examples validate ==")
    outputs = ["hma", "silver_override", "thin", "brand_gap", "empty_scope"]
    outs = {}
    for o in outputs:
        data = json.loads((EX / f"mwr_output.{o}.json").read_text())
        outs[o] = data
        errs = gate.validate_against(gate.MWR_SCHEMA, data)
        check(f"mwr_output.{o}.json conforms to output schema", not errs, "; ".join(errs[:2]))

    print("\n== Run-level decline kinds ==")
    bg_rd = outs["brand_gap"].get("run_decline", {})
    check("brand_gap output is kind=brand_gap with missing_fields",
          bg_rd.get("kind") == "brand_gap" and bool(bg_rd.get("missing_fields")))
    check("brand_gap output has empty segment_verdicts",
          outs["brand_gap"].get("segment_verdicts") == [])
    es_rd = outs["empty_scope"].get("run_decline", {})
    check("empty_scope output is kind=empty_scope with scoped_tier",
          es_rd.get("kind") == "empty_scope" and bool(es_rd.get("scoped_tier")))
    check("empty_scope output carries no missing_fields (not a brand gap)",
          "missing_fields" not in es_rd)
    check("empty_scope output has empty segment_verdicts",
          outs["empty_scope"].get("segment_verdicts") == [])

    print("\n== Format + warning invariants on exemplars ==")
    for o, data in outs.items():
        override = data.get("override", False)
        for v in data.get("segment_verdicts", []):
            ex = v.get("exemplar")
            if not ex:
                continue
            text = " ".join([ex["subject_line"], ex["eyebrow_line"], ex["message_body"]])
            check(f"{o}/{v['segment_id']} no em-dash", "—" not in text and "–" not in text)
            check(f"{o}/{v['segment_id']} no CTA in body", not looks_like_cta(ex["message_body"]))
            check(f"{o}/{v['segment_id']} override_warning iff override",
                  ("override_warning" in ex) == override)

    print("\n== v1.5 constitution + agent version ==")
    const = (MWR / "MWR_CONSTITUTION.md").read_text()
    check("constitution is v1.5", "**Version:** 1.5" in const)
    check("constitution carries the keystone rule", "keystone rule" in const)
    check("constitution carries the entailment rule", "entailment rule" in const)
    check("constitution carries the no-body-credential rule", "No credential in the body" in const)
    agent_md = (MWR / "AGENT.md").read_text()
    check("AGENT.md encodes v1.5", "MWR_CONSTITUTION.md v1.5" in agent_md)

    print("\n== v1.5 mechanical checks (gate.lint helpers) ==")
    # buyer-conditional detector: catches a second-person hedge, ignores world-conditionals
    check("buyer-conditional detected (second-person + hedge)",
          bool(gate.buyer_conditionals("If your exemption planning predates the rule, the math moved.")))
    check("world-conditional not flagged (no second person)",
          not gate.buyer_conditionals("If the deadline holds, states will file on time."))
    check("clean assertion not flagged",
          not gate.buyer_conditionals("Nebraska began enforcing early on May 1, 2026."))
    # word-count gate
    check("body over 165 words flagged", gate.word_count("w " * 200) > gate.BODY_MAX)
    check("subject over 8 words flagged", gate.word_count("one two three four five six seven eight nine") > gate.SUBJECT_MAX)
    # the committed v1.4 golden is a pre-v1.5 artifact: it must FAIL the v1.5 lint
    # (over-length body and a buyer-conditional). This pins its known pre-v1.5 status.
    hma_ex = outs["hma"]["segment_verdicts"][0]["exemplar"]
    check("v1.4 hma golden is pre-v1.5 (fails v1.5 lint: length or buyer-conditional)",
          gate.word_count(hma_ex["message_body"]) > gate.BODY_MAX
          or bool(gate.buyer_conditionals(hma_ex["message_body"])))

    print("\n== Negative golden fixture (hma.REJECTED) ==")
    rej = json.loads((EX / "mwr_output.hma.REJECTED.json").read_text())
    errs = gate.validate_against(gate.MWR_SCHEMA, rej)
    check("mwr_output.hma.REJECTED.json conforms to output schema", not errs, "; ".join(errs[:2]))
    rv = rej["segment_verdicts"][0]
    check("REJECTED verdict is 'no'", rv["pvp_achievable"] == "no")
    check("REJECTED carries a rejected_exemplar and no exemplar",
          "rejected_exemplar" in rv and "exemplar" not in rv)
    check("REJECTED is PQS (>=2 failed standards)", len(rv["gap"]["failed_standards"]) >= 2)
    sc = rv["rejected_exemplar"]["seven_standard_check"]
    gs4 = next(s for s in sc if s["standard"] == 4)
    check("REJECTED Standard 4 (keystone) failed", not gs4["met"])
    check("REJECTED records a keystone cascade on 5/6/7",
          all(next(s for s in sc if s["standard"] == n).get("failure_type") == "keystone_cascade"
              for n in (5, 6, 7)))
    body = rv["rejected_exemplar"]["message_body"]
    check("REJECTED body actually fails the v1.5 lint (over-length or buyer-conditional)",
          gate.word_count(body) > gate.BODY_MAX or bool(gate.buyer_conditionals(body)))

    print()
    if failures:
        print(f"SELFTEST FAILED: {len(failures)} check(s) failed -> {failures}")
        return 1
    print("SELFTEST PASSED: all checks green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
