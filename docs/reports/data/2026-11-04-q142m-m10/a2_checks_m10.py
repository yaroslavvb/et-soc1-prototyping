#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(m), dated amendment A2: the verifier's minor items, each re-derived here from committed files with fit_m10.py's own
functions (unchanged). None of them changes a term, a number of M10, a rule or a verdict; they correct wording.

    python3 -B a2_checks_m10.py [--out <dir>]   # writes a2-checks-m10.json and a2-checks-output.txt in <dir>, else this directory

1. A1-1's sentence: where docs/reports/data/2026-11-04-q140m-m9/nested-m9.json keeps `M9_frozen_form_loko`, and B's machinery on
   M9's 855 rows (leave one kind out, M9's frozen terms) against that key's per-row values (pool 6's rows).
2. REGISTRATION.md § 3a's sessions: which experiments hold fp32.randn, fp16.randn and int8.full as rows of rows-m9.json.
3. The rate: each pool-6 and pool-7 session's measured rate (every row M10 reads from E153, E157, E163, E164) against the nominal
   rate the models carry (fit_m5's RATE), per session and format.
4. Byte twins: tiles of one format carrying more than one kind label among the 959 rows, and the held-out figures and the (a)/(b)
   entry readings with each twin group held out as one kind (B, B+a, B+b, B+a+b floats; B, B+a int8).

Standard library and numpy 1.26. SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fit_m10 as FM  # noqa: E402  (the registered fit, unchanged)

fam_of = FM.fam_of
POOLS = ("E153", "E157", "E163", "E164")
LOG = []


def log(s):
    print(s, flush=True)
    LOG.append(s)


def rmsv(e):
    e = np.asarray(e, float)
    e = e[~np.isnan(e)]
    return float(math.sqrt(np.mean(e * e))) if len(e) else None


def check_a1_1(rows, m9):
    nm9 = FM.load(os.path.join(FM.M9D, "nested-m9.json"))
    where = {}

    def walk(o, p):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "M9_frozen_form_loko":
                    q = p.split("/")
                    tag = "/".join(q[:3]) + ("/pool6_rows[]" if "pool6_rows" in p else "/same_folds/<cell>")
                    where[tag] = where.get(tag, 0) + 1
                walk(v, p + "/" + k)
        elif isinstance(o, list):
            for v in o:
                walk(v, p + "[]")
    walk(nm9, "")
    out = {"occurrences": sum(where.values()), "by_place": where, "per_row_check": {}}
    for fam in ("float", "int8"):
        r9 = [r for r in rows if fam_of(r["type"]) == fam and r["src"] == "rows-m9.json"]
        terms = m9["families"][fam]["terms"]
        e = FM.Fit10(r9, terms, {}, False).loko()[0]
        idx = {(r["exp"], r["card"], r["key"]): float(e[i]) for i, r in enumerate(r9)}
        diffs, signs, n = [], 0, 0
        for p in nm9["families"][fam]["pool6_rows"]:
            v = p.get("M9_frozen_form_loko")
            k = (p["exp"], p["card"], p["key"])
            if v is None or k not in idx:
                continue
            n += 1
            diffs.append(abs(float(v) - idx[k]))
            signs += int((float(v) >= 0) == (idx[k] >= 0) or abs(float(v)) < 5e-5)
        out["per_row_check"][fam] = {"rows": n, "max_abs_diff_w": max(diffs) if diffs else None, "signs_agree": signs,
                                     "file_rounding": "1e-4 W", "within_rounding": bool(diffs and max(diffs) <= 5.0001e-5)}
    return out


def check_3a(m9rows):
    return {n: sorted({r["exp"] for r in m9rows if r["key"] == n}) for n in ("fp32.randn", "fp16.randn", "int8.full")}


def check_rate(rows):
    out = {"nominal_rate_per_s": {t: FM.F.RATE[t] for t in ("fp32", "fp16", "int8")}, "by_session_format": {}, "by_session": {},
           "by_format": {}}
    sel = [r for r in rows if r["exp"] in POOLS]
    for s in POOLS:
        xs = [100 * (r["rate"] / FM.F.RATE[r["type"]] - 1) for r in sel if r["exp"] == s]
        out["by_session"][s] = {"n": len(xs), "mean_pct": round(float(np.mean(xs)), 3), "min_pct": round(min(xs), 3), "max_pct": round(max(xs), 3)}
        for t in ("fp32", "fp16", "int8"):
            xt = [100 * (r["rate"] / FM.F.RATE[t] - 1) for r in sel if r["exp"] == s and r["type"] == t]
            if xt:
                out["by_session_format"][f"{s} {t}"] = {"n": len(xt), "mean_pct": round(float(np.mean(xt)), 3)}
    for t in ("fp32", "fp16", "int8"):
        ms = [v["mean_pct"] for k, v in out["by_session_format"].items() if k.endswith(" " + t)]
        out["by_format"][t] = {"session_means_pct": [min(ms), max(ms)]}
    return out


def twin_groups(rows):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    by = {}
    for r in rows:
        if r.get("tile_sha256"):
            by.setdefault((r["type"], r["tile_sha256"]), set()).add(r["kind"])
    tiles = {k: sorted(v) for k, v in by.items() if len(v) > 1}
    for ks in tiles.values():
        for k in ks[1:]:
            parent[find(k)] = find(ks[0])
    groups = {}
    for k in {k for ks in tiles.values() for k in ks}:
        groups.setdefault(find(k), set()).add(k)
    relabel = {}
    for g in groups.values():
        lab = "twins:" + "+".join(sorted(g))
        for k in g:
            relabel[k] = lab
    return tiles, groups, relabel


def check_twins(rows, anchors, rc, m9, rowsout):
    tiles, groups, relabel = twin_groups(rows)
    reg = {(r["exp"], r["card"], r["key"]): r["err_w"] for r in rowsout}
    out = {"tiles_with_more_than_one_kind_label": len(tiles), "kind_labels_on_them": len({k for ks in tiles.values() for k in ks}),
           "groups": sorted(sorted(g) for g in groups.values()), "families": {}}
    for fam in ("float", "int8"):
        fr = [dict(r, kind=relabel.get(r["kind"], r["kind"])) for r in rows if fam_of(r["type"]) == fam]
        anc = {s: [dict(x, kind=(relabel.get(x["kind"], x["kind"]) if x["kind"] else None)) for x in v if fam_of(x["type"]) == fam]
               for s, v in anchors.items()}
        terms = m9["families"][fam]["terms"]
        over = {i: rc[r["key"]]["fN"] for i, r in enumerate(fr) if r["S_class"]} if fam == "float" else {}
        variants = {"B": (False, None), "B+a": (True, None)}
        if fam == "float":
            variants.update({"B+b": (False, over), "B+a+b": (True, over)})
        aff = np.array([r["kind"].startswith("twins:") for r in fr])
        cds = np.array([r["card"] for r in fr])
        scl = np.array([r["S_class"] for r in fr])
        errs, rec, kid = {}, {}, None
        for vn, (us, ov) in variants.items():
            ft = FM.Fit10(fr, terms, anc, us, ov)
            e = ft.loko()[0]
            kid = ft.kid
            errs[vn] = e
            e_reg = np.array([reg[(r["exp"], r["card"], r["key"])][vn] if reg[(r["exp"], r["card"], r["key"])][vn] is not None else np.nan
                              for r in fr], float)
            rec[vn] = {"rms_registered_kinds_w": rmsv(e_reg), "rms_twins_merged_w": rmsv(e), "affected_rows": int(aff.sum()),
                       "affected_rms_registered_w": rmsv(e_reg[aff]) if aff.any() else None,
                       "affected_rms_merged_w": rmsv(e[aff]) if aff.any() else None}
        t = FM.boot(kid, errs["B+a"], errs["B"])
        pc = {c: FM.boot(kid[cds == c], errs["B+a"][cds == c], errs["B"][cds == c]) for c in ("a3", "c1")}
        rec["rule_a_twins_merged"] = {"pooled": t, "per_card": pc,
                                      "enters": bool(t["d_rms_w"] <= -0.005 and t["hi95"] < 0 and all(pc[c]["d_rms_w"] < 0 for c in pc))}
        if fam == "float":
            tb = FM.boot(kid, errs["B+b"], errs["B"])
            ts = FM.boot(kid[scl], errs["B+b"][scl], errs["B"][scl])
            tsc = {c: FM.boot(kid[scl & (cds == c)], errs["B+b"][scl & (cds == c)], errs["B"][scl & (cds == c)]) for c in ("a3", "c1")}
            rec["rule_b_twins_merged"] = {"S_class": ts, "S_class_per_card": tsc, "pooled": tb,
                                          "enters": bool(ts["d_rms_w"] <= -0.05 and ts["hi95"] < 0 and all(tsc[c]["d_rms_w"] < 0 for c in tsc)
                                                         and tb["d_rms_w"] <= 0.001)}
        out["families"][fam] = rec
    return out


def main():
    t0 = time.time()
    outdir = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else HERE
    os.makedirs(outdir, exist_ok=True)
    n_in = FM.check_inputs()
    log(f"a2_checks_m10 (Q142(m) A2): numpy {np.__version__}; registered inputs {n_in} hash as committed")
    m9 = FM.load(os.path.join(FM.M9D, "m9.json"))
    rows, _ = FM.assemble()
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    anchors, _ = FM.assemble_anchors(rows, zeros, zr)
    rc = FM.recount(os.path.join(HERE, "bench"), zeros, zr)
    rowsout = FM.load(os.path.join(HERE, "rows-m10.json"))
    m9rows = FM.load(os.path.join(FM.M9D, "rows-m9.json"))
    out = {"_note": "Q142(m) amendment A2: the verifier's minor items re-derived (tools/claims-v3/m10/REGISTRATION.md.dated-note-2.md)",
           "A1_1_nested_m9_key": check_a1_1(rows, m9), "section_3a_anchor_rows": check_3a(m9rows), "rate": check_rate(rows),
           "byte_twins": check_twins(rows, anchors, rc, m9, rowsout)}
    a1 = out["A1_1_nested_m9_key"]
    log(f"1. nested-m9.json holds M9_frozen_form_loko {a1['occurrences']} times: {a1['by_place']}; per-row check {a1['per_row_check']}")
    log(f"2. section 3a: the anchors as rows of rows-m9.json: {out['section_3a_anchor_rows']}")
    log(f"3. rate against the nominal, per format (session means, %): {out['rate']['by_format']}; per session {out['rate']['by_session']}")
    bt = out["byte_twins"]
    log(f"4. byte twins: {bt['tiles_with_more_than_one_kind_label']} tiles carry {bt['kind_labels_on_them']} kind labels")
    for fam, rec in bt["families"].items():
        for vn in ("B", "B+a", "B+b", "B+a+b"):
            if vn in rec:
                v = rec[vn]
                log(f"   {fam} {vn}: rms {v['rms_registered_kinds_w']:.5f} -> twins merged {v['rms_twins_merged_w']:.5f} W; affected rows "
                    f"{v['affected_rows']}")
        log(f"   {fam} rule a with the twins merged: {rec['rule_a_twins_merged']['pooled']} enters {rec['rule_a_twins_merged']['enters']}")
        if "rule_b_twins_merged" in rec:
            log(f"   {fam} rule b with the twins merged: {rec['rule_b_twins_merged']['S_class']} enters {rec['rule_b_twins_merged']['enters']}")
    json.dump(out, open(os.path.join(outdir, "a2-checks-m10.json"), "w"), indent=1, sort_keys=True)
    log(f"wrote a2-checks-m10.json, a2-checks-output.txt ({time.time() - t0:.1f} s)")
    open(os.path.join(outdir, "a2-checks-output.txt"), "w").write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
