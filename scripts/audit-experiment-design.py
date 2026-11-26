#!/usr/bin/env python3
"""Audit an experimental-design description against the 8 minimum requirements.

Requirements come from references/experimental-design-checklist.md (D1-D8),
each derived from a real counterexample in the 1215-paper pool.
"""

from __future__ import annotations

import sys as _sys

try:
    _sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import json
import re
import sys
from pathlib import Path

CHECKS = [
    ("D1", "untreated control (as-received)", [
        r"as[- ]received", r"untreated", r"baseline", r"未处理", r"原始态", r"母材", r"as[- ]polished control",
    ], "surfin.2024.104167: laser texturing lowered Ep 0.460 -> 0.150 V"),
    ("D2", "dose window with >= 3 levels", [
        r"dose", r"fluence", r"energy density", r"overlap", r"剂量", r"能量密度", r"搭接",
    ], "apsusc.2013.09.086: 70% overlap +340 mV, 90% overlap passive region vanishes"),
    ("D3", "as-treated vs post-treated state declared", [
        r"as[- ]treated", r"ablation layer", r"removed .* ?(um|µm|micron|mm)", r"polish(ed)? after",
        r"烧蚀层", r"磨除", r"as[- ]melted",
    ], "cja.2025.103799: as-treated Epit = -167 mV; after removing 3.5 um, Rct 2.54e6 ohm.cm2"),
    ("D4", "power AND fluence both reported (not interchangeable)", [
        r"power", r"W\b", r"scan speed", r"spot", r"hatch", r"pass(es)?", r"pulse",
        r"功率", r"扫描速度", r"光斑", r"道次",
    ], "electacta.2025.145913: same 2000 J/cm2, 150 W beat 300 W"),
    ("D5", "atmosphere recorded", [
        r"argon", r"\bAr\b", r"nitrogen", r"\bN2\b", r"vacuum", r"air\b", r"water .*(layer|film|constrain)",
        r"气氛", r"氩气", r"空气", r"水约束",
    ], "mi13071089: air texturing worst (Rf 1.56e-5 MOhm.cm2); argon best (0.598)"),
    ("D6", "independent repeats n >= 4", [
        r"\bn\s*=\s*[4-9]", r"\bn\s*=\s*1[0-9]", r"at least (four|4)", r"重复.*[4-9]", r"\b[4-9]\s*(specimens|samples|试样)",
    ], "n=3 -> two-sided minimum p = 2/C(6,3) = 0.100; p<0.05 unreachable"),
    ("D7", "long immersion (>= 24 h) reported", [
        r"24\s*h", r"48\s*h", r"72\s*h", r"168\s*h", r"[0-9]+\s*days?", r"long[- ]term",
        r"长时间", r"长时浸泡", r"[0-9]+\s*天",
    ], "mi13071089: superhydrophobic lost at 24 h; s41377 kept i_corr 5e-10 A/cm2 for >6500 h"),
    ("D8", "conventional-passivation control", [
        r"nitric", r"citric", r"electropolish", r"mechanically polished", r"passivation (bath|treatment)",
        r"硝酸", r"柠檬酸", r"电解抛光", r"传统钝化",
    ], "jmapro.2026.06.043: Epit 0.205 -> chemical 0.751 -> laser 1.371 V"),
]


def main() -> int:
    p = argparse.ArgumentParser(description="Audit an experimental design against the 8 minimum requirements.")
    p.add_argument("design", type=Path, help="design description file (.md/.txt)")
    p.add_argument("--fmt", choices=["text", "json"], default="text")
    args = p.parse_args()

    if not args.design.exists():
        print(f"ERROR: file not found: {args.design}", file=sys.stderr)
        return 2
    text = args.design.read_text(encoding="utf-8", errors="ignore")
    low = text.lower()

    results = []
    for code, name, patterns, basis in CHECKS:
        hits = []
        for pat in patterns:
            for m in re.finditer(pat, text, re.I):
                hits.append(m.group(0))
        status = "pass" if hits else "missing"
        results.append({
            "id": code, "requirement": name, "status": status,
            "evidence_hits": sorted(set(hits))[:6], "counterexample_basis": basis,
        })

    n_pass = sum(1 for r in results if r["status"] == "pass")
    verdict = "COMPLIANT" if n_pass == len(CHECKS) else ("PARTIAL" if n_pass >= 5 else "INSUFFICIENT")

    if args.fmt == "json":
        print(json.dumps({"verdict": verdict, "passed": n_pass, "total": len(CHECKS), "checks": results},
                         ensure_ascii=False, indent=2))
        return 0

    print(f"verdict: {verdict}  ({n_pass}/{len(CHECKS)} passed)")
    print()
    for r in results:
        mark = "PASS   " if r["status"] == "pass" else "MISSING"
        print(f"{mark} {r['id']}  {r['requirement']}")
        if r["status"] != "pass":
            print(f"          why it matters: {r['counterexample_basis']}")
        elif r["evidence_hits"]:
            print(f"          seen: {', '.join(r['evidence_hits'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
