#!/usr/bin/env python3
"""Build a Boolean search query with false-positive exclusion for this domain.

Implements the three-layer AND / one-layer NOT structure defined in
references/literature-retrieval-playbook.md 4.1-4.3.

Rules here, execution outside: this script emits a query string; it does not
search anything.
"""

from __future__ import annotations

import sys as _sys

try:
    _sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import json
import sys
from pathlib import Path

MATERIAL = [
    '"stainless steel"', '"316L"', '"304L"', '"316"', '"304"', '"2205"', '"2507"',
    '"duplex stainless"', '"super duplex"', '"17-4PH"', '"AISI 420"', '"AISI 430"',
]

# Laser terms must be surface-treatment flavoured. AM/welding etc. are excluded below.
PROCESS_SURFACE = [
    '"laser surface"', '"laser passivation"', '"laser oxidation"', '"laser remelting"',
    '"laser surface melting"', '"laser surface remelting"', '"LSM"', '"LSR"',
    '"laser shock peening"', '"laser texturing"', '"laser cladding"',
    '"femtosecond laser"', '"nanosecond laser"', '"picosecond laser"',
    '"strong-field laser"', '"filamentation"',
]

CHARACTERISATION = [
    '"corrosion"', '"passive film"', '"passivation"', '"pitting"',
    '"EIS"', '"electrochemical impedance"', '"polarization"', '"potentiodynamic"',
    '"Mott-Schottky"', '"XPS"', '"photoelectron spectroscopy"',
    '"pitting potential"', '"Ecorr"', '"icorr"', '"Rct"',
]

# 15 false-positive classes -> exclusion clauses (playbook 1.a-1.o)
EXCLUSIONS = {
    "a_additive": '( "additive manufacturing" OR "selective laser melting" OR SLM OR LPBF '
                  'OR "powder bed" OR "directed energy" OR DED OR LMD OR "laser metal deposition" )',
    "a_welding": '( "laser welding" OR "laser brazing" OR "spot welding" OR "laser-arc" )',
    "a_hardening": '( "laser hardening" OR "laser annealing" OR "laser polishing" OR "laser marking" )',
    "a_instrument": '( "laser confocal" OR Raman OR "laser speckle" OR "laser profilometry" OR "Kelvin probe" )',
    "a_prime_coating": '( superhydrophobic OR FAS OR PFOTES OR fluorosilane OR "self-assembled monolayer" )',
    "a_prime_chemical": '( "nitric acid" OR "citric acid" OR chromate OR "Cr(VI)" )',
    "a_prime_sensitisation": '( sensitization OR Cr23C6 OR "DL-EPR" OR "degree of sensitization" )',
    "d_medium": '( "neutral salt spray" OR "salt spray" OR "simulated body fluid" OR '
                '"liquid lead-bismuth" OR LBE OR "supercritical water" OR "pressurized water reactor" OR '
                '"boiling water reactor" OR "molten salt" OR "hot corrosion" OR fireside )',
    "f_hydrogen": '( "hydrogen charging" OR "hydrogen embrittlement" OR thiourea OR "cathodic charging" )',
    "m_computational": '( "neural network" OR "machine learning" OR XGBoost OR SHAP OR QSAR '
                       'OR DFT OR "molecular dynamics" )',
    "n_potential_drop": '( "acoustic emission" OR "potential drop" OR "crack growth" OR fretting '
                        'OR "erosion-corrosion" )',
    "b_journal_domain": '( Wear OR "Tribology International" OR "Journal of Nuclear Materials" OR '
                        '"Nuclear Engineering" OR "NDT&E" OR Micron OR "Science of the Total Environment" )',
}

TOPIC_PRESETS = {
    "dose_window": ['"dose"', '"fluence"', '"energy density"', '"overlap"', '"scan speed"'],
    "film": ['"passive film"', '"oxide film"', '"film thickness"', '"XPS depth profile"'],
    "mott_schottky": ['"Mott-Schottky"', '"donor density"', '"flat band"', '"semiconducting"'],
    "pitting": ['"pitting potential"', '"pitting corrosion"', '"metastable pitting"'],
    "eis": ['"EIS"', '"impedance"', '"equivalent circuit"', '"Rct"'],
    "sensitisation": ['"DL-EPR"', '"degree of sensitization"', '"reactivation"'],
}


def build(question: str, preset: str | None, include: list[str], exclude: list[str], fmt: str) -> str:
    mat = " OR ".join(MATERIAL)
    proc = " OR ".join(PROCESS_SURFACE)
    char = " OR ".join(CHARACTERISATION)
    if preset and preset in TOPIC_PRESETS:
        char = char + " OR " + " OR ".join(TOPIC_PRESETS[preset])
    if include:
        char = char + " OR " + " OR ".join(include)

    nots: list[str] = []
    for key in EXCLUSIONS:
        if exclude == ["none"]:
            break
        if exclude and key not in exclude and "all" not in exclude:
            continue
        nots.append("NOT " + EXCLUSIONS[key])

    lines = [
        f"# question: {question}",
        f"# preset:   {preset or '(none)'}",
        f"# exclusions: {exclude or 'all'}",
        "",
        "( " + mat + " )",
        "AND ( " + proc + " )",
        "AND ( " + char + " )",
    ]
    for n in nots:
        lines.append(n)
    query = "\n".join(lines)
    if fmt == "json":
        return json.dumps({
            "question": question,
            "preset": preset,
            "layers": {"material": MATERIAL, "process": PROCESS_SURFACE, "characterisation": CHARACTERISATION},
            "exclusions": nots,
            "query": query,
        }, ensure_ascii=False, indent=2)
    return query


def main() -> int:
    p = argparse.ArgumentParser(description="Build a domain search query with false-positive exclusions.")
    p.add_argument("question", nargs="?", default="laser passivation of stainless steel", help="research question")
    p.add_argument("--preset", choices=sorted(TOPIC_PRESETS), default=None)
    p.add_argument("--include", nargs="*", default=[], help="extra AND-terms for layer 3")
    p.add_argument("--exclude", nargs="*", default=[], help="exclusion class keys to apply; omit for all; pass 'none' to disable")
    p.add_argument("--fmt", choices=["text", "json"], default="text")
    p.add_argument("--list-exclusions", action="store_true", help="print available exclusion keys and exit")
    args = p.parse_args()

    if args.list_exclusions:
        for key, val in EXCLUSIONS.items():
            print(f"{key}\n    {val}\n")
        return 0

    if args.exclude and args.exclude != ["none"]:
        unknown = [k for k in args.exclude if k not in EXCLUSIONS and k != "all"]
        if unknown:
            print(f"ERROR: unknown exclusion key(s): {', '.join(unknown)}", file=sys.stderr)
            print("Use --list-exclusions to see valid keys.", file=sys.stderr)
            return 2

    print(build(args.question, args.preset, args.include, args.exclude, args.fmt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
