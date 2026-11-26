#!/usr/bin/env python3
"""Flag paper-internal contradictions and false-positive features in a record.

Implements the machine-checkable subset of
references/paper-internal-contradiction-patterns.md and
references/data-audit-checklist.md.

Input: one JSON file, or a directory of JSON files. Each file is either a single
record object or a list of records. Recognised (all optional) keys:

    record_id            str
    n                    int                      -> M-D1 (n<=3 significance ceiling)
    claimed_p            float                    -> M-D1
    units                {declared, value, alternative, recomputed}  -> M01
    stern_geary          {ba, bc, icorr, rp_reported}                -> M20 (2.303 factor)
    identity             [{product_of:[k1,k2], equals:[col], rows:[{...}]}]  -> M12
    complementary        [{a_value,a_sd,b_value,b_sd,sum}]           -> M13
    extrapolation        {fitted_at, max_observed, axis}             -> M15
    criterion            {name, typical_value, threshold, operator}  -> M16
    magnitude            {claimed, recomputed, label}                -> E5
    constant             {name, reported, expected, tolerance_pct}   -> M19
    derived              {formula_value, reported_value, label}      -> M04

Exit code: 0 if no findings; 1 if any finding (so it can gate a pipeline).
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

# (pattern_id, severity) -- severity: high blocks quantitative reuse
FINDINGS: list[dict] = []


def add(rec_id: str, pattern: str, severity: str, detail: str, basis: str) -> None:
    FINDINGS.append({
        "record_id": rec_id, "pattern": pattern, "severity": severity,
        "detail": detail, "basis": basis,
    })


def approx(a: float, b: float, tol_pct: float = 5.0) -> bool:
    if b == 0:
        return abs(a) < 1e-12
    return abs(a - b) / abs(b) * 100.0 <= tol_pct


def check_record(r: dict) -> None:
    rid = str(r.get("record_id", "?"))

    # --- D1 / significance ceiling for small n ---
    n = r.get("n")
    p = r.get("claimed_p")
    if isinstance(n, int) and isinstance(p, (int, float)):
        if n <= 2:
            floor = 0.333
        elif n == 3:
            floor = 0.100
        elif n == 4:
            floor = 0.029
        else:
            floor = None
        if floor is not None and p < floor:
            add(rid, "D1/M-D1", "high",
                f"n={n} but claimed p={p}; exact two-sided permutation floor is {floor}",
                "injury.2007.07.015: Ti/Ti 4v3 reported p=0.027 while floor is 0.0571")

    # --- M20 / Stern-Geary 2.303 factor ---
    sg = r.get("stern_geary")
    if isinstance(sg, dict) and all(k in sg for k in ("ba", "bc", "icorr", "rp_reported")):
        ba, bc, icorr, rp_rep = sg["ba"], sg["bc"], sg["icorr"], sg["rp_reported"]
        denom = 2.303 * (ba + bc) * icorr
        correct = (ba * bc) / denom if denom else None
        if correct:
            ratio = rp_rep / correct
            if approx(ratio, 1.0, 5):
                pass
            elif approx(ratio, 2.303, 3):
                add(rid, "M20", "high",
                    f"reported R_p / correct R_p = {ratio:.3f} (exactly 2.303) -> formula omits 2.303",
                    "vacuum.2024.113581 Eq.(4): all six tabulated R_p = true value x 2.303")
            else:
                add(rid, "M20/derived_mismatch", "medium",
                    f"reported R_p differs from Stern-Geary recompute by {ratio:.3f}x",
                    "cross-check R_p against b_a, b_c and i_corr")

    # --- M01 / header-unit double reading ---
    u = r.get("units")
    if isinstance(u, dict):
        val = u.get("value")
        recomputed = u.get("recomputed")
        factor = u.get("factor", 1000)
        if isinstance(val, (int, float)) and isinstance(recomputed, (int, float)):
            ok_as_written = approx(val, recomputed, 10)
            ok_scaled = approx(val * factor, recomputed, 10)
            if not ok_as_written and ok_scaled:
                add(rid, "M01", "high",
                    f"value {val} only matches recompute {recomputed} after x{factor} -> header unit is wrong",
                    "apsadv.2024.100622 Table 6 'k ohm/cm' is actually ohm.cm2 (4% vs 1000x)")

    # --- M12 / identity relation treated as corroboration ---
    # A tautology may carry a constant unit scale, so test whether product/rhs is
    # CONSTANT across rows (CV small) rather than whether it equals 1.
    for ident in r.get("identity", []) or []:
        keys = ident.get("product_of") or []
        eq = ident.get("equals") or []
        if len(keys) != 2 or not eq:
            continue
        col = eq[0]
        ratios: list[float] = []
        for row in ident.get("rows", []) or []:
            try:
                lhs = float(row[keys[0]]) * float(row[keys[1]])
                rhs = float(row[eq[0]])
            except (KeyError, TypeError, ValueError):
                continue
            if rhs:
                ratios.append(lhs / rhs)
        if len(ratios) >= 2:
            mean = sum(ratios) / len(ratios)
            if mean:
                cv = (max(ratios) - min(ratios)) / abs(mean) * 100.0
                if cv <= 5.0:
                    add(rid, "M12", "high",
                        f"column '{col}' == {keys[0]} x {keys[1]} with a constant scale "
                        f"{mean:.4g} across {len(ratios)} rows (CV {cv:.2f}%) -> tautology, not corroboration",
                        "jnucmat.2019.151880: third column == crack density x mean length (347*9.7=3366 vs 3.37, i.e. scale 1000)")

    # --- M13 / complementary quantities share the same SD ---
    for c in r.get("complementary", []) or []:
        a_sd, b_sd = c.get("a_sd"), c.get("b_sd")
        a_v, b_v, tot = c.get("a_value"), c.get("b_value"), c.get("sum")
        if None in (a_sd, b_sd, a_v, b_v, tot):
            continue
        if approx(a_v + b_v, tot, 1) and approx(float(a_sd), float(b_sd), 1):
            add(rid, "M13", "medium",
                f"complementary pair (sum={tot}) shares SD {a_sd} -> constructive pseudocorrelation, not two independent observations",
                "s13632-024-01120-y: gamma 41.67+/-2.89 and alpha 58.33+/-2.89")

    # --- M15 / extrapolation beyond observed domain ---
    ex = r.get("extrapolation")
    if isinstance(ex, dict):
        fit, obs = ex.get("fitted_at"), ex.get("max_observed")
        if isinstance(fit, (int, float)) and isinstance(obs, (int, float)) and obs:
            excess = (fit - obs) / abs(obs) * 100.0
            if excess > 20:
                add(rid, "M15", "high",
                    f"fitted/claimed value {fit} exceeds max observed {obs} by {excess:.1f}%"
                    f"{' on ' + str(ex.get('axis')) if ex.get('axis') else ''}",
                    "s0010-938x_01_00039-7: (w/d)_crit 2.1 exceeds max observed 1.60 by 31%")

    # --- M16 / empty criterion (always satisfied) ---
    cr = r.get("criterion")
    if isinstance(cr, dict):
        tv, th = cr.get("typical_value"), cr.get("threshold")
        op = cr.get("operator", ">=")
        if isinstance(tv, (int, float)) and isinstance(th, (int, float)):
            satisfies = tv >= th if op in (">=", ">") else tv <= th
            if satisfies:
                add(rid, "M16", "medium",
                    f"criterion '{cr.get('name','unnamed')}' ({op} {th}) is satisfied by the typical value {tv}"
                    f" -> cannot reject any data point (empty criterion)",
                    "s41529-025-00717-0: B_eff/(W-a) >= 0.264 is met by any standard CT specimen (~1.6)")

    # --- E5 / magnitude claim not reproduced ---
    mg = r.get("magnitude")
    if isinstance(mg, dict):
        cl, re_ = mg.get("claimed"), mg.get("recomputed")
        if isinstance(cl, (int, float)) and isinstance(re_, (int, float)) and re_ and cl:
            ratio = cl / re_
            if ratio >= 3 or ratio <= 1 / 3:
                add(rid, "E5", "high",
                    f"claimed magnitude {cl} vs recomputed {re_} (ratio {ratio:.2f}x)"
                    f"{' for ' + str(mg.get('label')) if mg.get('label') else ''}",
                    "s41377-025-01952-5: claimed 100,000x reduction; Faraday gives ~4 orders of magnitude")

    # --- M19 / wrong constant ---
    cn = r.get("constant")
    if isinstance(cn, dict):
        rep, exp = cn.get("reported"), cn.get("expected")
        tol = cn.get("tolerance_pct", 5)
        if isinstance(rep, (int, float)) and isinstance(exp, (int, float)) and exp:
            if not approx(rep, exp, tol):
                add(rid, "M19", "high",
                    f"constant '{cn.get('name','?')}' reported {rep} vs expected {exp}"
                    f" (off by {abs(rep-exp)/abs(exp)*100:.1f}%)",
                    "molliq.2017.11.142: iron EW used for a Cr-bearing steel")

    # --- M04 / derived value does not follow from the paper's own formula ---
    dv = r.get("derived")
    if isinstance(dv, dict):
        fv, rv = dv.get("formula_value"), dv.get("reported_value")
        if isinstance(fv, (int, float)) and isinstance(rv, (int, float)) and rv:
            if not approx(fv, rv, 15):
                add(rid, "M04", "medium",
                    f"derived '{dv.get('label','?')}': formula gives {fv}, paper reports {rv}"
                    f" ({abs(fv-rv)/abs(rv)*100:.1f}% off)",
                    "corsci.2026.114168: film thickness off by exactly 10x in all four samples")


def iter_records(path: Path):
    if path.is_dir():
        for f in sorted(path.glob("*.json")):
            yield from iter_records(f)
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item
    elif isinstance(data, dict):
        yield data


def main() -> int:
    p = argparse.ArgumentParser(description="Flag contradictions / false-positive features in records.")
    p.add_argument("path", type=Path, help="JSON record file or directory of them")
    p.add_argument("--fmt", choices=["text", "json"], default="text")
    p.add_argument("--only-high", action="store_true", help="report only high-severity findings")
    args = p.parse_args()

    if not args.path.exists():
        print(f"ERROR: not found: {args.path}", file=sys.stderr)
        return 2

    count = 0
    for rec in iter_records(args.path):
        check_record(rec)
        count += 1

    findings = [f for f in FINDINGS if (not args.only_high or f["severity"] == "high")]

    if args.fmt == "json":
        print(json.dumps({"records_scanned": count, "findings": findings}, ensure_ascii=False, indent=2))
        return 1 if findings else 0

    print(f"records scanned: {count}")
    print(f"findings:        {len(findings)}")
    print()
    if not findings:
        print("no contradictions flagged")
        return 0
    for f in findings:
        tag = "HIGH" if f["severity"] == "high" else "med "
        print(f"[{tag}] {f['pattern']}  ({f['record_id']})")
        print(f"        {f['detail']}")
        print(f"        basis: {f['basis']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
