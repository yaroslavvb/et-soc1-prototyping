#!/usr/bin/env python3
"""Q138(b) blind pool 5: the checks behind CORRECTIONS.md (Mon 2 Nov 2026, after the pool's independent verification).

Desk only, numpy only. It reads the frozen pool (blind5.json, its tiles, make_blind5.py), blind pool 4 (blind4.json and
its tiles) and E140's published M6 residuals (scored.json, scored-nodips.json). It changes nothing: the only files it
writes are corrections-check.json and corrections-check.txt, in --out-dir (default: this file's directory).

    python3 -B tools/claims-v3/kinds/blind5/corrections-check.py

1. fp16's C under the rule the card follows. The pool's c_check emulates PRM 9.4's pseudo-code: a two-term update
   a1*b1 + a2*b2 is dropped unless all four halves are nonzero. E36 (LAT-S1, PASS on three cards) found the card adds
   the plain sum ("math"). Here make_blind5.c_check runs unchanged, except that every fp16 update applies. First the
   unchanged c_check is rerun on all 36 tiles and must equal the frozen manifest's, so the environment is the
   designer's.
2. The post-hoc C-flip correlation on blind pool 4, both descriptors (a launch's second op, and the launch-end
   estimate): Pearson r with a Fisher-z 95% interval, Spearman's rho, the within-format r^2, and r without the two
   tiles whose C sits at Inf from the first op, under both fp16 rules.
3. run_checks.decodes_back: which tiles the generator builds from words (make_kinds.from_words), where a decode-back
   check is not defined.
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True   # never leave __pycache__ in the pool's directory

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FP16_CHANGED_FIELDS = ("updates_dropped_per_op", "c_start", "c_launch_end_est", "c_finite_64_ops_exact", "pass")


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=HERE, help="the blind5 directory (default: this file's directory)")
    ap.add_argument("--kinds-dir", default=None, help="the directory holding make_kinds.py and blind4/ (default: the pool's parent)")
    ap.add_argument("--e140", default=None, help="E140's data directory (default: <repo>/docs/reports/data/2026-11-02-e140-blind4)")
    ap.add_argument("--out-dir", default=HERE)
    a = ap.parse_args()
    a.pool = os.path.abspath(a.pool)
    a.kinds_dir = os.path.abspath(a.kinds_dir or os.path.dirname(a.pool))
    top = os.path.dirname(os.path.dirname(os.path.dirname(a.kinds_dir)))   # kinds -> claims-v3 -> tools -> repo
    a.e140 = os.path.abspath(a.e140 or os.path.join(top, "docs", "reports", "data", "2026-11-02-e140-blind4"))
    return a


def load_modules(pool, kinds_dir):
    sys.path.insert(0, kinds_dir)
    sys.path.insert(0, pool)
    import make_kinds   # noqa: E402
    import make_blind5  # noqa: E402
    make_blind5.mk = make_kinds
    return make_kinds, make_blind5


def make_rules(mb):
    """Two versions of make_blind5.steps_of: as frozen (PRM-literal) and the card's (every fp16 update applies)."""
    literal = mb.steps_of

    def math_rule(a, b, type_name):
        st, ap = literal(a, b, type_name)
        if type_name == "fp16":
            ap = [np.ones_like(x, dtype=bool) for x in ap]
        return st, ap

    return {"literal": literal, "math": math_rule}


def c_check_under(mb, rules, rule, raw, type_name):
    mb.steps_of = rules[rule]
    try:
        with np.errstate(all="ignore"):
            return mb.c_check(raw, type_name)
    finally:
        mb.steps_of = rules["literal"]


def half_zero_words(mk, raw):
    """fp16: lane words with exactly one zero half, on A (k pairs of a row) and on B (k pairs of a column)."""
    A, B = mk.decode(raw, "fp16")
    A, B = np.asarray(A, float), np.asarray(B, float)
    za, zb = A == 0, B == 0
    a = int((za[:, 0::2] != za[:, 1::2]).sum())
    b = int((zb[0::2, :] != zb[1::2, :]).sum())
    return {"a": a, "b": b}


def updates_that_differ(mk, mb, rules, raw):
    """fp16: updates an op that the PRM-literal rule drops although their two-term sum is nonzero (the only ones where
    the two rules can disagree; a dropped update whose sum is zero leaves C as the card leaves it)."""
    A, B = mk.decode(raw, "fp16")
    st, ap = rules["literal"](np.asarray(A, float), np.asarray(B, float), "fp16")
    return int(sum(((~x) & (s != 0)).sum() for s, x in zip(st, ap)))


def brief(cc):
    out = {"c_start_flips": cc["c_start"]["c_reg_flips_per_op"],
           "c_end_flips": cc["c_launch_end_est"]["c_reg_flips_per_op"],
           "start_update_change_frac": cc["c_start"]["update_change_frac"],
           "start_moving_frac": cc["c_start"]["moving_frac"],
           "end_update_change_frac": cc["c_launch_end_est"]["update_change_frac"],
           "end_moving_frac": cc["c_launch_end_est"]["moving_frac"],
           "c_finite_64_ops_exact": cc.get("c_finite_64_ops_exact"),
           "launch_end_finite": cc["c_launch_end_est"]["finite"],
           "pass": cc["pass"]}
    if "updates_dropped_per_op" in cc:
        out["updates_dropped_per_op"] = cc["updates_dropped_per_op"]
    return out


def ranks(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    sx = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and sx[j + 1] == sx[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def fisher_ci(r, n):
    z, se = math.atanh(r), 1.0 / math.sqrt(n - 3)
    return [round(math.tanh(z - 1.96 * se), 3), round(math.tanh(z + 1.96 * se), 3)]


def within_format(names, x, err):
    """As side/corr_blind4.py: the slope of error on C flips with each format's means removed, and its r^2."""
    xd, ed = np.array(x, float) / 1000.0, np.array(err, float)
    for ty in ("fp32", "fp16", "int8"):
        m = np.array([n.startswith(ty + ".") for n in names])
        xd[m] -= xd[m].mean()
        ed[m] -= ed[m].mean()
    slope = float((xd * ed).sum() / (xd * xd).sum())
    resid = ed - slope * xd
    return round(slope, 4), round(1 - float((resid ** 2).sum() / (ed ** 2).sum()), 3)


def main():
    a = parse()
    mk, mb = load_modules(a.pool, a.kinds_dir)
    rules = make_rules(mb)
    man = json.load(open(os.path.join(a.pool, "blind5.json")))
    res = {"what": "Q138(b) blind pool 5: checks behind CORRECTIONS.md (2026-11-02)",
           "numpy": np.__version__}
    lines = []
    P = lines.append

    # 0. the unchanged c_check reproduces the frozen manifest on every tile
    same, differ = 0, []
    tiles = {}
    for t in man["tiles"]:
        raw = open(os.path.join(a.pool, t["file"]), "rb").read()
        tiles[t["name"]] = (t, raw)
        cc = c_check_under(mb, rules, "literal", raw, t["type"])
        if json.dumps(cc, sort_keys=True) == json.dumps(t["c_check"], sort_keys=True):
            same += 1
        else:
            differ.append(t["name"])
    res["reproduces_frozen_c_check"] = {"tiles": len(man["tiles"]), "identical": same, "differ": differ}
    P(f"0. make_blind5.c_check, unchanged, rerun on the {len(man['tiles'])} frozen tiles: {same} identical to blind5.json"
      + (f"; DIFFER: {', '.join(differ)}" if differ else ""))

    # 1. fp16 under the card's rule
    P("")
    P("1. fp16 C under E36's rule (the plain sum) against the frozen PRM-literal c_check")
    P(f"   {'tile':30s} {'half-zero words A/B':>19s}  {'dropped/op':>10s}  {'differ/op':>9s}  "
      f"{'C flips start -> end (literal)':>30s}  {'C flips start -> end (card)':>27s}  C changed")
    fp16 = {}
    for name, (t, raw) in tiles.items():
        if t["type"] != "fp16":
            continue
        lit = c_check_under(mb, rules, "literal", raw, "fp16")
        mat = c_check_under(mb, rules, "math", raw, "fp16")
        hz = half_zero_words(mk, raw)
        nd = updates_that_differ(mk, mb, rules, raw)
        changed = [f for f in FP16_CHANGED_FIELDS if json.dumps(lit.get(f), sort_keys=True) != json.dumps(mat.get(f), sort_keys=True)]
        c_changed = [f for f in changed if f != "updates_dropped_per_op"]
        unchanged_rest = all(json.dumps(lit[k], sort_keys=True) == json.dumps(mat[k], sort_keys=True)
                             for k in lit if k not in FP16_CHANGED_FIELDS)
        fp16[name] = {"half_zero_words": hz, "updates_that_differ_per_op": nd,
                      "literal_as_frozen": brief(lit), "math_the_card": brief(mat), "math_c_check": mat,
                      "fields_changed": changed, "c_descriptors_changed": bool(c_changed),
                      "other_fields_unchanged": unchanged_rest}
        bl, bm = brief(lit), brief(mat)
        P(f"   {name:30s} {hz['a']:>9d} / {hz['b']:<7d}  {bl['updates_dropped_per_op']:>10d}  {nd:>9d}  "
          f"{bl['c_start_flips']:>14,d} -> {bl['c_end_flips']:<12,d}  {bm['c_start_flips']:>11,d} -> {bm['c_end_flips']:<12,d}  "
          f"{'YES' if c_changed else 'no'}")
    res["fp16_rule"] = {"rule_frozen": "PRM 9.4 pseudo-code: the two-term update applies only when a1, a2, b1, b2 are all nonzero",
                        "rule_card": "E36 LAT-S1: the plain sum a1*b1 + a2*b2 for every k pair (\"math\", PASS on aifoundry1 card 1, "
                                     "aifoundry2 and aifoundry3, 3 passes each; A-side half zeros tested directly)",
                        "tiles": fp16,
                        "c_descriptors_changed": [n for n, v in fp16.items() if v["c_descriptors_changed"]],
                        "dropped_count_only": [n for n, v in fp16.items() if v["fields_changed"] and not v["c_descriptors_changed"]],
                        "all_pass_under_card_rule": all(v["math_the_card"]["pass"] for v in fp16.values())}
    P(f"   C descriptors change: {', '.join(res['fp16_rule']['c_descriptors_changed'])}")
    P(f"   only the dropped count changes (every dropped update there adds zero): {', '.join(res['fp16_rule']['dropped_count_only'])}")
    P(f"   every fp16 tile passes the C check under the card's rule: {res['fp16_rule']['all_pass_under_card_rule']}")

    # 2. the post-hoc correlation on blind pool 4
    b4dir = os.path.join(a.kinds_dir, "blind4")
    b4 = json.load(open(os.path.join(b4dir, "blind4.json")))
    flips = {"literal": {}, "math": {}}
    op1_nonfinite = {}
    for t in b4["tiles"]:
        raw = open(os.path.join(b4dir, t["file"]), "rb").read()
        for rule in ("literal", "math"):
            cc = c_check_under(mb, rules, rule, raw, t["type"])
            flips[rule][t["name"]] = {"start": cc["c_start"]["c_reg_flips_per_op"], "end": cc["c_launch_end_est"]["c_reg_flips_per_op"]}
        if t["type"] != "int8":
            A, B = mk.decode(raw, t["type"])
            st, ap = mb.steps_of(np.asarray(A, float), np.asarray(B, float), t["type"])
            with np.errstate(all="ignore"):
                c1, _, _ = mb.run_op(np.zeros((16, 16), np.float32), st, ap, t["type"])
            n_bad = int((~np.isfinite(c1)).sum())
            if n_bad:
                op1_nonfinite[t["name"]] = {"nonfinite": n_bad, "nan": int(np.isnan(c1).sum())}
    res["blind4"] = {"tiles": len(b4["tiles"]),
                     "fp16_flips_same_under_both_rules": all(flips["literal"][n] == flips["math"][n] for n in flips["literal"]),
                     "c_op1_nonfinite_of_256": op1_nonfinite, "flips": flips}
    inf_tiles = sorted(op1_nonfinite)
    corr = {}
    P("")
    P("2. blind pool 4: E140's M6 power residuals (measured - predicted) against C-register flips per op (post hoc)")
    P(f"   C non-finite after the first op: " + "; ".join(f"{n} {v['nonfinite']} of 256 (NaN {v['nan']})" for n, v in op1_nonfinite.items()))
    P(f"   fp16 flips identical under both rules on all blind-4 fp16 tiles: {res['blind4']['fp16_flips_same_under_both_rules']}")
    P(f"   {'rule':7s} {'arm':12s} {'descriptor':10s} {'r [95%]':>22s} {'Spearman':>8s} {'r fp32/fp16/int8':>20s} {'wf r2':>6s} "
      f"{'r without the 2 Inf tiles [95%]':>32s}")
    for rule in ("literal", "math"):
        for arm, fn in (("primary", "scored.json"), ("dips_removed", "scored-nodips.json")):
            rows = json.load(open(os.path.join(a.e140, fn)))["primary"]["power"]["rows"]
            names = sorted(rows)
            err = [rows[n]["error"] for n in names]
            for key, label in (("end", "end"), ("start", "start")):
                x = [flips[rule][n][key] for n in names]
                r = pearson(x, err)
                per = {}
                for ty in ("fp32", "fp16", "int8"):
                    m = [i for i, n in enumerate(names) if n.startswith(ty + ".")]
                    per[ty] = round(pearson([x[i] for i in m], [err[i] for i in m]), 3)
                slope, r2 = within_format(names, x, err)
                keep = [i for i, n in enumerate(names) if n not in inf_tiles]
                r_wo = pearson([x[i] for i in keep], [err[i] for i in keep])
                c = {"n": len(names), "r": round(r, 3), "r_95ci": fisher_ci(r, len(names)),
                     "spearman": round(pearson(ranks(x), ranks(err)), 3), "r_by_format": per,
                     "within_format_slope_W_per_1000_flips": slope, "within_format_r2": r2,
                     "n_without_inf_tiles": len(keep), "r_without_inf_tiles": round(r_wo, 3),
                     "r_without_inf_tiles_95ci": fisher_ci(r_wo, len(keep))}
                corr[f"{rule}/{arm}/{key}"] = c
                ci, ciw = c["r_95ci"], c["r_without_inf_tiles_95ci"]
                P(f"   {rule:7s} {arm:12s} {label:10s} {c['r']:>8.3f} [{ci[0]:6.3f}, {ci[1]:5.3f}] {c['spearman']:>8.3f} "
                  f"{per['fp32']:>6.3f}/{per['fp16']:.3f}/{per['int8']:.3f} {r2:>6.3f} "
                  f"{c['r_without_inf_tiles']:>12.3f} [{ciw[0]:6.3f}, {ciw[1]:5.3f}] (n {len(keep)})")
    res["corr"] = corr
    res["corr_note"] = ("post hoc: computed after the pool's design, on one session's 25 tiles, with a derived descriptor; "
                        "the frozen README shows the 'end' rows only, chosen after both descriptors were computed")

    # 3. decodes_back
    words, encoded = [], []
    for name, type_name, case, prio, rule, fn in mb.TILES:
        out = fn(mb.rng_for(name))
        (words if isinstance(out, tuple) and len(out) == 3 and isinstance(out[0], str) and out[0] == "words" else encoded).append(name)
    res["decodes_back"] = {"built_from_words_na": words, "built_from_elements_checked": len(encoded),
                           "note": "make_blind5.py writes decodes_back true for every tile; build_one decodes and compares only the "
                                   "tiles built from elements (make_kinds.encode); for the tiles built from words "
                                   "(make_kinds.from_words) the check is not defined: read it as n/a (defined on words)"}
    P("")
    P(f"3. decodes_back: {len(encoded)} tiles built from elements are decoded and compared at build time; "
      f"n/a (defined on words) for {len(words)}: {', '.join(words)}")

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "corrections-check.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    with open(os.path.join(a.out_dir, "corrections-check.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    ok = not differ and res["fp16_rule"]["all_pass_under_card_rule"]
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
