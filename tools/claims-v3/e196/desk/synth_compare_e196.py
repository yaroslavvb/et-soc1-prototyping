#!/usr/bin/env python3
"""E196 (Q185, lane reg-e196): set the reduction's output beside the values a synthetic session put in (desk check of code).

    /usr/bin/python3 -I -B synth_compare_e196.py INJECTED.json X14.json GEN/arms.json [--exact] [--tol-se 4] [--tol-abs 0.02]

INJECTED.json is synth_session_e196.py's (arbitrary test values: not a forecast, not a measurement). What is compared, each
against what the injected levels imply (the die held at 58 C, so every leakage term is zero and Bc = idle + S):
  per pass arm: S_W, D_W and D_bracketed_W (against the arm's reference in arms.json);
  derived: every ladder step (W), the W-per-row slopes, the held ladder's middle-step ratio, the zero ladder's first-step
  ratio, the spread contrasts, the three mask-0 contrasts, B through gated micro-ops, the zero shares and r, and the ties
  given in W (zeros S, pi S, ones, random, A-zero, sparse50 and B-sign D);
  trains: D_W (F - S) and that each is scored.
The quantities in pJ (they divide by the device-counted rate) are checked for consistency only: each is recomputed from the
output's own per-arm S and ops_per_s means. --exact: tolerance 1e-6 W (1e-6 relative for ratios); else |diff| <= tol-se x SE +
tol-abs. Prints one line per check and a verdict, CONSISTENT or NOT CONSISTENT (with the failing lines).
"""
import argparse
import json


def lsq(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return b, my - b * mx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("injected")
    ap.add_argument("x14")
    ap.add_argument("arms")
    ap.add_argument("--exact", action="store_true")
    ap.add_argument("--tol-se", type=float, default=4.0)
    ap.add_argument("--tol-abs", type=float, default=0.02)
    a = ap.parse_args()
    inj = json.load(open(a.injected))
    out = json.load(open(a.x14))
    table = {x["name"]: x for x in json.load(open(a.arms))["arms"]}
    S = inj["S_W"]
    dropped = set(inj.get("dropped", []))
    bad, n = [], 0

    def check(name, got, want, ratio=False):
        nonlocal n
        n += 1
        if got is None:
            if want is None:
                print("  %-60s empty, as expected" % name)
                return
            bad.append(name)
            print("  %-60s MISSING (want %.6f)" % (name, want))
            return
        if want is None:
            bad.append(name)
            print("  %-60s present but expected empty" % name)
            return
        m = got.get("mean") if isinstance(got, dict) else got
        se = got.get("se", 0.0) if isinstance(got, dict) else 0.0
        if a.exact:
            tol = 1e-6 * max(1.0, abs(want)) if ratio else 1e-6
        else:
            tol = a.tol_se * (se or 0.0) + a.tol_abs * (max(1.0, abs(want)) if ratio else 1.0)
        ok = abs(m - want) <= tol
        if not ok:
            bad.append(name)
        print("  %-60s got %+.6f want %+.6f diff %+.2e se %.2e %s" % (name, m, want, m - want, se, "ok" if ok else "OFF"))

    rows = lambda arm: 16 if table[arm]["row_mask"] is None else bin(int(table[arm]["row_mask"], 16)).count("1")
    have = lambda x: x in S and x not in dropped
    print("== per pass arm")
    for arm, t in table.items():
        if not t.get("in_passes", True):
            continue
        rec = out["arms"].get(arm)
        if arm in dropped:
            check("arm %s S_W" % arm, rec.get("S_W") if rec else None, None)
            continue
        check("arm %s S_W" % arm, rec["S_W"], S[arm])
        if t["ref"]:
            want = S[arm] - S[t["ref"]] if have(t["ref"]) else None
            check("arm %s D_W" % arm, rec.get("D_W"), want)
            check("arm %s D_bracketed_W" % arm, rec.get("D_bracketed_W"), want)
    d = out["derived"]
    print("== derived (W forms, against the injected levels)")
    for tile, lad in (("H", ["I.H.m0000", "I.H.m000F", "I.H.m00FF", "I.H.m0FFF", "I.H.full"]),
                      ("Z", ["I.Z.m0000", "I.Z.m000F", "I.Z.m00FF", "I.Z.m0FFF", "I.Z.full"]),
                      ("R", ["I.R.m0000", "I.R.m00FF", "I.R.full"])):
        for i in range(len(lad) - 1):
            x0, x1 = lad[i], lad[i + 1]
            check("ladder_%s_step_%s_to_%s_W" % (tile, x0, x1), d.get("ladder_%s_step_%s_to_%s_W" % (tile, x0, x1)),
                  S[x1] - S[x0] if have(x0) and have(x1) else None)
        mid = lad[1:4] if tile != "R" else lad
        check("ladder_%s_slope_W_per_row" % tile, d.get("ladder_%s_slope_W_per_row" % tile),
              lsq([rows(x) for x in mid], [S[x] for x in mid])[0] if all(have(x) for x in mid) else None)
    check("held_ladder_middle_step_ratio", d.get("held_ladder_middle_step_ratio"),
          (S["I.H.m0FFF"] - S["I.H.m00FF"]) / (S["I.H.m00FF"] - S["I.H.m000F"]), ratio=True)
    check("zero_ladder_first_step_ratio", d.get("zero_ladder_first_step_ratio"),
          (S["I.Z.m000F"] - S["I.Z.m0000"]) / (S["I.Z.m00FF"] - S["I.Z.m000F"]), ratio=True)
    for x in ("I.H.m0F0F", "I.H.m3333", "I.H.m5555"):
        check("spread_%s_minus_I.H.m00FF_W" % x, d.get("spread_%s_minus_I.H.m00FF_W" % x), S[x] - S["I.H.m00FF"])
    for x in ("I.H.m0000", "I.R.m0000", "Z.a0.m0000"):
        check("mask0_%s_minus_zero_W" % x, d.get("mask0_%s_minus_zero_W" % x), S[x] - S["I.Z.m0000"])
    check("b_through_gated_micro_ops_W", d.get("b_through_gated_micro_ops_W"),
          (S["Z.a0"] - S["I.Z.full"]) - (S["Z.a0.m0000"] - S["I.Z.m0000"]))
    share = lambda z: (S[z] - S["I.Z.full"]) / (S["I.R.full"] - S["I.Z.full"])
    for z in ("Z.a50", "Z.b50", "Z.ab50"):
        g = table[z]["counts"]["gated_fraction"]
        check("share_%s" % z, d.get("share_%s" % z), share(z) if have(z) else None, ratio=True)
        check("r_from_%s" % z, d.get("r_from_%s" % z), (share(z) - (1 - g)) / g if have(z) else None, ratio=True)
    check("tie_zeros_S_W", d.get("tie_zeros_S_W"), S["I.Z.full"])
    check("tie_pi_S_W", d.get("tie_pi_S_W"), S["K.pi"])
    check("tie_ones_D_W", d.get("tie_ones_D_W"), S["K.ones"] - S["I.Z.full"])
    check("tie_random_D_W", d.get("tie_random_D_W"), S["I.R.full"] - S["I.Z.full"])
    check("tie_a_zero_D_W", d.get("tie_a_zero_D_W"), S["Z.a0"] - S["I.Z.full"])
    check("tie_sparse50_D_W", d.get("tie_sparse50_D_W"), S["Z.ab50"] - S["I.Z.full"])
    check("tie_b_sign_D_W", d.get("tie_b_sign_D_W"), S["F.Bs"] - S["F.B0"])
    print("== derived in pJ: consistency with the output's own per-arm S and ops_per_s means")
    ar = out["arms"]
    epo = lambda x: ar[x]["S_W"]["mean"] / ar[x]["ops_per_s"]["mean"] * 1e12
    if have("I.H.mFFFF"):
        check("msk_null (pJ per op, from the per-arm means)", d.get("msk_null_I.H.mFFFF_minus_I.H.full_pJ_per_op"),
              epo("I.H.mFFFF") - epo("I.H.full"), ratio=True)
    check("lanes_clock_plus_accumulator_writes_per_mac_board_pJ", d.get("lanes_clock_plus_accumulator_writes_per_mac_board_pJ"),
          (epo("I.H.full") - epo("I.Z.full")) / 4096, ratio=True)
    check("data_part_per_issued_mac_random_board_pJ", d.get("data_part_per_issued_mac_random_board_pJ"),
          (epo("I.R.full") - epo("I.H.full")) / 4096, ratio=True)
    print("== trains")
    for name, want in inj["trains_D_W"].items():
        tr = out["trains"].get(name, {})
        check("train %s D_W (F - S)" % name, tr.get("D_W"), want)
        n += 1
        if not tr.get("scored"):
            bad.append("train %s scored" % name)
        print("  %-60s units %s, scored %s, processes with a value %s of %s, excluded %d, anchor drift %s" % (
            "train %s" % name, tr.get("units"), tr.get("scored"), tr.get("processes_with_value"), tr.get("processes"),
            len(tr.get("excluded", [])), tr.get("anchor_drift_W")))
    print("== the run's bookkeeping: passes kept %s; set aside %d run(s); dips dropped %d (injected %s); readback_gate %s" % (
        [p["pass"] for p in out["passes"] if p["kept"]], len(out["set_aside"]), out["dips_dropped"], inj.get("dips_injected"),
        json.dumps({k: v for k, v in out.get("readback_gate", {}).items() if k != "exempt"}) if "readback_gate" in out else "absent"))
    for r in out["set_aside"]:
        print("     set aside: pass %s seq %s %s: %s" % (r.get("pass"), r.get("seq"), r.get("arm"), r.get("gates_failed")))
    print("VERDICT: %s (%d checks, %d off)%s" % ("CONSISTENT" if not bad else "NOT CONSISTENT", n, len(bad),
                                                 "" if not bad else ": " + ", ".join(bad[:20])))


if __name__ == "__main__":
    main()
