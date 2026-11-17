#!/usr/bin/python3
"""E208 data, dated note 1 (post hoc, Mon 16 Nov 2026): which runs are capped, and which runs' energy the registered rule reads.

The lab's lane fix-e208d (round Q200) wrote this after the data commit, to answer the data verifier's two README findings. It reads
only, with Python's own modules, and it imports nothing from the kit or from the registered reducer: it is its own code, written from
the registered rule's words (E208.md section 7; the constants re-typed from the kit's mms_common.py).

1. It re-derives every run's capped flag from the raw launch records (session/runs/*/run.json and each process's SPARSITY lines):
   on a governed card (aifoundry2 card 0, aifoundry1 card 0), of the launches starting 1.0 s or more after their own process's
   launch 0, fewer than 80% in the 800 MHz band (790-810 MHz by cycles max / wall) is capped; a null run is never capped; a run with
   no launch at 800 MHz and every launch in the 600 MHz band is read in band600 and never capped (no_step); card 1 is never capped.
   A launch counts when its test is fma, launch >= 0, ok, wall >= 0.1 s and passes >= 1.
2. It compares that flag and the share with the committed reduction's own (the reducer's `capped`, `frac_800_after_step`).
3. It counts the runs whose energy the registered rule reads (ran; role arm or anchor; not a null; not capped; the primary view not
   thin and with a power figure), beside the runs whose primary view merely carries a power figure (a capped run's does too).
4. It gives the anchor's figures over the anchor runs read for energy and over every anchor run, from the committed reduction's
   primary view (time an op, power over idle, energy over idle an op), and the reducer's own anchor-arm entry beside them.

Usage:  python3 -I -B posthoc_note1_e208.py <session dir> <data-e208-<session>.json> [--json <out.json>]
Exit 0 when every re-derived capped flag and share equals the committed reduction's; 1 otherwise.

SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import statistics
import sys

BANDS = {"800": (790.0, 810.0), "700": (690.0, 710.0), "600": (590.0, 610.0)}
GOVERNED = {"a2c0": True, "a1c0": True, "a1c1": False}
WIN_LO_S = 1.0
CAPPED_FRAC = 0.8


def band(L):
    w = L.get("wall_s") or 0
    if w <= 0:
        return None
    f = (L.get("cycles_max") or 0) / w / 1e6
    for b, (lo, hi) in BANDS.items():
        if lo <= f <= hi:
            return b
    return None


def ok_launch(L):
    n = L.get("launch")
    return L.get("test") == "fma" and (n if n is not None else -9) >= 0 and bool(L.get("ok")) and (L.get("wall_s") or 0) >= 0.1 \
        and bool(L.get("passes"))


def sparsity(path):
    out = []
    if not os.path.exists(path):
        return out
    for ln in open(path, encoding="utf-8", errors="replace").read().splitlines():
        if ln.startswith("SPARSITY "):
            try:
                out.append(json.loads(ln[9:]))
            except ValueError:
                pass
    return out


def capped_of(rdir, rec, governed, sc):
    """(capped, share, in band, after the step, no_step) for one run, from its raw records"""
    if rec.get("form", "burst") == "null" or not governed:
        return False, None, None, None, False
    launches = []
    for k, p in enumerate(rec.get("procs") or []):
        path = os.path.join(rdir, p.get("name", "proc") + ".out")
        if not os.path.exists(path):
            path = os.path.join(rdir, "proc.out")
        launches += [dict(L, proc=k) for L in sparsity(path) if ok_launch(L)]
    after = []
    for k in sorted({L["proc"] for L in launches}):
        Lk = [L for L in launches if L["proc"] == k]
        t0 = min(Lk, key=lambda L: L["launch"])["t_start_ms"] / 1000.0
        after += [L for L in Lk if L["t_start_ms"] / 1000.0 - t0 >= WIN_LO_S * sc]
    n_in = sum(1 for L in after if band(L) == "800")
    share = n_in / len(after) if after else None
    capped = bool(after) and share < CAPPED_FRAC
    if launches and not any(band(L) == "800" for L in launches) and all(band(L) == "600" for L in launches):
        return False, share, n_in, len(after), True
    return capped, share, n_in, len(after), False


def stats(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {"n": len(v), "min": min(v), "max": max(v), "mean": statistics.mean(v), "sd": statistics.stdev(v) if len(v) > 1 else None}


def main(argv):
    if len(argv) < 3:
        print(__doc__.split("Usage:")[1].split("\n")[0].strip())
        return 2
    sdir, red_path = argv[1], argv[2]
    jout = argv[argv.index("--json") + 1] if "--json" in argv else None
    red = json.load(open(red_path))
    q = json.load(open(os.path.join(sdir, "queue.json")))
    card = q.get("card")
    governed = GOVERNED[card]
    sc = float(q.get("scale") or 1.0)
    rr = {r["run"]: r for r in red["runs"]}
    rows, mism = [], []
    rd = os.path.join(sdir, "runs")
    for key in sorted(os.listdir(rd)):
        rp = os.path.join(rd, key, "run.json")
        if not os.path.exists(rp):
            continue
        rec = json.load(open(rp))
        r = rr.get(rec["run"])
        if r is None:
            mism.append(f"{rec['run']}: not in the reduction")
            continue
        if not rec.get("ran"):
            rows.append({"run": rec["run"], "role": rec["role"], "form": rec.get("form", "burst"), "ran": False})
            continue
        cap, share, n_in, n_after, no_step = capped_of(os.path.join(rd, key), rec, governed, sc)
        if cap != bool(r.get("capped")):
            mism.append(f"{rec['run']}: capped {cap} here, {r.get('capped')} in the reduction")
        rs = r.get("frac_800_after_step")
        if governed and rec.get("form", "burst") != "null" and not no_step and \
                ((share is None) != (rs is None) or (share is not None and abs(share - rs) > 1e-12)):
            mism.append(f"{rec['run']}: share {share} here, {rs} in the reduction")
        p = (r.get("views") or {}).get(r.get("primary_view")) or {}
        power = p.get("dP_w") is not None
        read = rec.get("form", "burst") != "null" and rec["role"] in ("arm", "anchor") and not cap and not p.get("thin") and power
        rows.append({"run": rec["run"], "i": rec["i"], "arm": rec["arm"], "role": rec["role"], "form": rec.get("form", "burst"),
                     "ran": True, "capped": cap, "share_800_after_step": share, "in_band_after_step": n_in, "after_step": n_after,
                     "no_step": no_step, "primary_view": r.get("primary_view"), "power_figure": power, "energy_read": read,
                     "T_op_us": p.get("T_op_us"), "dP_w": p.get("dP_w"), "J_op_nJ": p["J_op"] * 1e9 if p.get("J_op") is not None else None,
                     "J_op_corr_nJ": p["J_op_corr"] * 1e9 if p.get("J_op_corr") is not None else None})
    ran = [x for x in rows if x["ran"]]
    roles = {}
    for x in ran:
        roles[x["role"]] = roles.get(x["role"], 0) + 1
    aa = [x for x in ran if x["role"] in ("arm", "anchor")]
    capped = [x for x in ran if x.get("capped")]
    anc = [x for x in ran if x["role"] == "anchor"]
    anc_read = [x for x in anc if x["energy_read"]]
    arm_entry = {}
    for arm in sorted({x["arm"] for x in anc}):
        b = ((red.get("arms") or {}).get(arm) or {}).get("views", {}).get(red.get("primary_view")) or {}
        arm_entry[arm] = {"n_runs": b.get("n_runs"), "n_energy_runs": b.get("n_energy_runs"),
                          "J_op_nJ_mean": b["J_op"] * 1e9 if b.get("J_op") is not None else None, "dP_w_mean": b.get("dP_w")}
    res = {"session": red.get("session"), "card": card, "governed": governed, "primary_view": red.get("primary_view"),
           "runs_ran": len(ran), "roles": roles, "compared": len(ran), "mismatches": mism,
           "arm_and_anchor_runs": len(aa), "with_a_power_figure": sum(1 for x in aa if x["power_figure"]),
           "energy_read": sum(1 for x in aa if x["energy_read"]),
           "capped_by_role": {k: sum(1 for x in capped if x["role"] == k) for k in sorted({x["role"] for x in ran})},
           "capped_runs": [{k: x[k] for k in ("run", "role", "in_band_after_step", "after_step", "share_800_after_step")} for x in capped],
           "no_step_runs": [x["run"] for x in ran if x.get("no_step")],
           "anchor_runs_read": {"T_op_us": stats([x["T_op_us"] for x in anc_read]), "dP_w": stats([x["dP_w"] for x in anc_read]),
                                "J_op_nJ": stats([x["J_op_nJ"] for x in anc_read]), "J_op_corr_nJ": stats([x["J_op_corr_nJ"] for x in anc_read])},
           "anchor_runs_all": {"T_op_us": stats([x["T_op_us"] for x in anc]), "dP_w": stats([x["dP_w"] for x in anc]),
                               "J_op_nJ": stats([x["J_op_nJ"] for x in anc])},
           "anchor_arm_in_the_reduction": arm_entry, "die_slope_n_anchors": (red.get("die_slope") or {}).get("n_anchors"),
           "runs": rows}
    f = lambda v, d: "-" if v is None else f"{v:.{d}f}"  # noqa: E731
    print(f"E208 dated note 1 (post hoc): session {res['session']}, card {card} ({'governed' if governed else 'not governed'}), "
          f"primary view {res['primary_view']}; runs ran {len(ran)} ({', '.join(f'{k} {v}' for k, v in sorted(roles.items()))})")
    print(f"capped re-derived from the raw launch records against the reduction's: {len(ran)} runs compared, {len(mism)} mismatches")
    for m in mism:
        print("  MISMATCH", m)
    print(f"capped runs: {len(capped)} ({', '.join(f'{k} {v}' for k, v in res['capped_by_role'].items() if v) or 'none'})")
    for x in capped:
        print(f"  {x['run']:28s} {x['role']:6s} {x['in_band_after_step']} of {x['after_step']} launches past {WIN_LO_S:.1f} s in the 800 MHz "
              f"band ({x['share_800_after_step']:.3f} < {CAPPED_FRAC})")
    if res["no_step_runs"]:
        print(f"no_step runs (read in band600, never capped): {', '.join(res['no_step_runs'])}")
    print(f"arm and anchor runs {len(aa)}: with a power figure in the primary view {res['with_a_power_figure']}; "
          f"energy read by the registered rule {res['energy_read']}")
    nt = roles.get("time", 0)
    if nt:
        print(f"time-only runs {nt} (never read for energy): {res['capped_by_role'].get('time', 0)} of them capped")
    for lab, A in (("anchor runs read for energy", res["anchor_runs_read"]), ("every anchor run", res["anchor_runs_all"])):
        t, P, J = A["T_op_us"], A["dP_w"], A["J_op_nJ"]
        if not J:
            continue
        print(f"{lab} (n {J['n']}): time an op {f(t['min'], 4)}-{f(t['max'], 4)} us; power over idle {f(P['min'], 2)}-{f(P['max'], 2)} W; "
              f"energy over idle {f(J['min'], 2)}-{f(J['max'], 2)} nJ an op (mean {f(J['mean'], 2)}, sd {f(J['sd'], 2)})"
              + (f"; die-corrected {f(A['J_op_corr_nJ']['min'], 2)}-{f(A['J_op_corr_nJ']['max'], 2)} nJ (mean {f(A['J_op_corr_nJ']['mean'], 2)})"
                 if A.get("J_op_corr_nJ") else ""))
    for arm, e in arm_entry.items():
        print(f"the reduction's anchor arm {arm}: n_runs {e['n_runs']}, n_energy_runs {e['n_energy_runs']}, energy over idle "
              f"{f(e['J_op_nJ_mean'], 2)} nJ an op (the .txt row), power over idle {f(e['dP_w_mean'], 2)} W; die slope over "
              f"{res['die_slope_n_anchors']} anchors")
    for x in anc:
        print(f"  anchor {x['run']:28s} capped {str(x['capped']):5s} read {str(x['energy_read']):5s} T {f(x['T_op_us'], 4)} us "
              f"dP {f(x['dP_w'], 2)} W J {f(x['J_op_nJ'], 2)} nJ J_corr {f(x['J_op_corr_nJ'], 2)} nJ")
    if jout:
        with open(jout, "w") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
            fh.write("\n")
    return 0 if not mism else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
