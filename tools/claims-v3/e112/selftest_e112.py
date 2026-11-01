#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E112 self-test: E112's desk code on SYNTHETIC passes with known answers, before any E112 data.

    python3 tools/claims-v3/e112/selftest_e112.py <scratch dir> [--passes 4] [--seed 112]

Part 1, the card-1 view: every watt figure a frozen claim reads is the frozen figure divided by E82's scale of its type,
and every ratio, live share and r threshold is unchanged.
Part 2, (b): fake card-1 passes in E95's 53-run order (E78's own generator, selftest_e78.make_pass, after
e95_common.install()), card 1's configuration reads (TDP 65, threshold 65, 499 mV) and card 1's meter artifact injected
(selftest_e91.inject_dips: pairs of board_w samples 8-14 W low inside run windows). Two worlds:
  "shared": E78's kinds at E82's card-1 D, E95's tiles at E95's dips-removed D / E82's per-type scale: X4 and X5 must
            PASS, X1 must PASS, every claim must be scored, C9 must PASS, the ports' thresholds must be the scaled ones;
  "unshared": E95's tiles at E95's dips-removed D x 1.03 (card 1 reading them 3% above aifoundry3, E91's self-test's
            world): X4 must FAIL (median about 0.97).
reduce_e112b.py (primary, dips kept, one leakage arm) and score_e112b.py run on both.
Part 3, (a): tools/claims-v3/kinds/selftest_e91.py, unchanged, on its own synthetic passes (E91's code, reused as is).
The queue's budget rule is tested on the box by `run_e112.sh setup` (stub blocks; it needs GNU date).
NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, K)
import e95_common as e95  # noqa: E402

e95.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402
import selftest_e91 as s91  # noqa: E402  (its import installs E86's items: E95's go back on below)

e95.install()

REG = json.load(open(os.path.join(HERE, "predictions-e112.json")))
FIRST = 11250


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def part1():
    F = load(REG["inputs_frozen"]["real2_predictions"]["path"])
    G = load(REG["b"]["card1_view"]["path"])
    s = REG["b"]["card_scale_e82"]
    worst = 0.0
    checked = 0
    for k, t in F["tiles"].items():
        ty = k.split("/")[0]
        a, b = t["a_aifoundry3_600mhz"], G["tiles"][k]["a_aifoundry3_600mhz"]
        for x, y in [(a["D_w"], b["D_w"])] + list(zip(a["scoring_interval_w"], b["scoring_interval_w"])):
            worst = max(worst, abs(x / s[ty] - y)); checked += 1
        if "c_gate_law" in t:
            c, d = t["c_gate_law"], G["tiles"][k]["c_gate_law"]
            for x, y in [(c["D_w"], d["D_w"])] + list(zip(c["scoring_interval_w"], d["scoring_interval_w"])):
                worst = max(worst, abs(x / s[ty] - y)); checked += 1
            same = c["g"] == d["g"] and c["live_share"] == d["live_share"]
            if not same:
                return {"card-1 view: g and live share unchanged": (False, k)}
    C, D = F["claims"]["E95"], G["claims"]["E95"]
    pairs = [(C["C6_calibration_lever"]["threshold_w"] / s["int8"], D["C6_calibration_lever"]["threshold_w"]),
             (0.40 / s["int8"], D["C7_calibration_rank"]["e112_threshold_w"]),
             (0.5 / s["int8"], D["C8_asym_turns_the_gate_off"]["e112_threshold_w"]),
             (C["C9_negative_zero"]["prediction_if_gate_took_numeric_zero"]["scoring_interval_w"][1] / s["fp32"],
              D["C9_negative_zero"]["prediction_if_gate_took_numeric_zero"]["scoring_interval_w"][1]),
             (C["C11_fp16_forward"]["band_w"] / s["fp16"], D["C11_fp16_forward"]["band_w"]),
             (F["gate_law"]["per_type"]["fp32"]["L_w"] / s["fp32"], G["gate_law"]["per_type"]["fp32"]["L_w"])]
    for x, y in pairs:
        worst = max(worst, abs(x - y)); checked += 1
    ratios_same = (C["C1_within_2pct"]["band"] == D["C1_within_2pct"]["band"]
                   and C["C10_bf16_weights"]["threshold_r"] == D["C10_bf16_weights"]["threshold_r"]
                   and C["C3b_live_share_slope"]["band_slope_over_L"] == D["C3b_live_share_slope"]["band_slope_over_L"])
    return {"card-1 view: watts = frozen / scale (rounded to 1e-4)": (worst <= 5.1e-5, f"{checked} figures, worst {worst:.2e}"),
            "card-1 view: ratio thresholds unchanged (C1, C3b, C10)": (ratios_same, ratios_same)}


def truth(world):
    e82 = load(REG["inputs_frozen"]["e82_reduction"]["path"])
    nod = load(REG["inputs_frozen"]["e95_nodips"]["path"])
    D = {n: v["D"]["mean"] for n, v in e82["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    s = REG["b"]["card_scale_e82"]
    for n in e95.POOL:
        d = nod["items"][n]["D"]["mean"]
        D[n] = d / s[n.split(".")[0]] if world == "shared" else d * 1.03
    return D


def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        sys.exit(f"failed: {args[0]}")
    return r


def run_world(scratch, world, passes, seed):
    rng = np.random.default_rng(seed)
    items = ec.load_items()
    D = truth(world)
    base = os.path.join(scratch, world, "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs, injected = [], {}
    for i in range(passes):
        p = FIRST + i
        d = os.path.join(base, f"p{p}")
        os.makedirs(d)
        st.make_pass(d, p, D, rng, items)
        cf = json.load(open(os.path.join(d, "configs.json")))
        cf["card"] = "aifoundry1-c1"
        json.dump(cf, open(os.path.join(d, "configs.json"), "w"))
        for nm in ("config_start", "config_end"):
            json.dump({"tdp_w": 65, "temp_threshold_c": 65, "power_state": 1, "power_state_name": "managed_power",
                       "minion_mhz": 600, "minion_mv": 499}, open(os.path.join(d, nm + ".json"), "w"))
        injected[str(p)] = s91.inject_dips(d, rng)
        dirs.append(d)
    out = {}
    for arm, extra in (("primary", []), ("dipskept", ["--keep-dips"]), ("leak0.545", ["--leak", "0.545", "--no-refit"])):
        j = os.path.join(scratch, f"{world}-{arm}.json")
        run([os.path.join(HERE, "reduce_e112b.py"), *dirs, "--out", j, *extra, "--txt", os.path.join(scratch, f"{world}-{arm}.txt")])
        out[arm] = j
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e112b.py"), "--e112b", out["primary"], "--arm", f"dips_kept={out['dipskept']}",
         "--arm", f"leak0.545={out['leak0.545']}", "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(out["primary"])), json.load(open(s)), D, injected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--seed", type=int, default=112)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = part1()
    e, sc, D, inj = run_world(a.scratch, "shared", a.passes, a.seed)
    names = list(e95.POOL)
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in names)
    removed = {k: v["samples_removed"] for k, v in (e["reducer"]["dip_samples_removed"] or {}).items()}
    C, X = sc["claims"], sc["cross_card"]["primary"]
    view = REG["b"]["card1_view"]["path"]
    G = load(view)
    checks.update({
        "shared: dips injected": (sum(inj.values()) > 0, inj),
        "shared: the primary removes them": (sum(removed.values()) >= sum(inj.values()), removed),
        "shared: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "shared: every pass kept": (len(e["passes"]) == a.passes, e["passes"]),
        "shared: 53 runs a pass, all kept": (e["runs"] == 53 * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "shared: D recovered within 0.15 W": (worst <= 0.15, round(worst, 4)),
        "shared: no claim NOT SCORED": (all(v["verdict"] != "NOT SCORED" for v in C.values()), {k: v["verdict"] for k, v in C.items()}),
        "shared: C9 PASS (D far above the gated reading)": (C["C9"]["verdict"] == "PASS", C["C9"]["threshold_w"]),
        "shared: C7 port reads the scaled threshold": (C["C7"]["threshold_w"] == G["claims"]["E95"]["C7_calibration_rank"]["e112_threshold_w"], C["C7"]["threshold_w"]),
        "shared: C8 port reads the scaled threshold": (C["C8"]["threshold_w"] == G["claims"]["E95"]["C8_asym_turns_the_gate_off"]["e112_threshold_w"], C["C8"]["threshold_w"]),
        "shared: unscaled verdicts reported beside": (all("at_frozen_thresholds_unscaled_labelled" in v for v in C.values()), True),
        "shared: X1 PASS": (X["x1"]["verdict"] == "PASS", {t: round(v["rho"], 3) for t, v in X["x1"]["by_type"].items()}),
        "shared: X4 PASS": (X["x4"]["verdict"] == "PASS", X["x4"]["median_ratio"]),
        "shared: X5 PASS": (X["x5"]["verdict"] == "PASS", f"{X['x5']['agree']}/{X['x5']['resolved']}"),
        "shared: arms scored beside": (set(sc["arms"]) == {"dips_kept", "leak0.545"}, list(sc["arms"])),
    })
    e2, sc2, D2, _ = run_world(a.scratch, "unshared", a.passes, a.seed + 1)
    X2 = sc2["cross_card"]["primary"]
    checks.update({"unshared: X4 FAIL (median about 0.97)": (X2["x4"]["verdict"] == "FAIL", X2["x4"]["median_ratio"])})
    r = subprocess.run([sys.executable, os.path.join(K, "selftest_e91.py"), os.path.join(a.scratch, "e91")], capture_output=True, text=True)
    print("--- tools/claims-v3/kinds/selftest_e91.py (unchanged), its own output:")
    print(r.stdout.strip())
    checks["(a): E91's own self-test passes on this desk"] = (r.returncode == 0, r.returncode)
    ok_all = True
    print("--- E112's checks:")
    for k, (ok, v) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {v}")
    print("informational (synthetic): claims", sc["tally"], "cross", sc["tally_cross_card"], "| unshared:", sc2["tally"], sc2["tally_cross_card"])
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
