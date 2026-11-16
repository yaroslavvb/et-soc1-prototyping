#!/usr/bin/env python3
"""The registered reducer's output on synth_session_e195.py's session, set beside the injected test values (a desk check
of code: it says nothing about a card; the values are arbitrary test values, not a forecast and not a measurement).

    python3 -I -B synth_compare_e195.py <injected.json> <gen dir> <x09.json> [<x09 with p901 given>.json]

Every expected value is computed here from the injected prices and the manifest's designed counts by request.md section 4's
words (the registered convention), independently of reduce_x09.py's code. It checks: the headline passes and the pass set
aside, the clock gate, the leakage slope, every registered price (exact to 1e-9 relative or 1e-6 pJ, the floors and what
depends on them by the reducer's own reading: see the note), the rails' and the board's per-line values of one contrast
and their electrons, the write-over-read ratios, the rate tests, every verdict the injected values imply, the checks C1-C6
and the sensitivity arms. With the second output (the reducer also given the smoke p901) it shows what that does to the
headline. Exit 0 when everything holds as stated.
"""
import json
import sys

import numpy as np

inj = json.load(open(sys.argv[1]))
man = {it["name"]: it for it in json.load(open(sys.argv[2] + "/manifest.json"))["items"]}
res = json.load(open(sys.argv[3]))
res_smoke = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
P, ZL, SCP, RATE = inj["prices"], inj["zero_line"], inj["scp_store"], inj["rate"]
E_CH = 1.602176634e-19
bad, n_ok = [], 0


def check(cond, msg):
    global n_ok
    if cond:
        n_ok += 1
    else:
        bad.append(msg)
    print(("  ok   " if cond else "  FAIL ") + msg)


def eq(a, b, rel=1e-9, ab=1e-6):
    return a is not None and b is not None and (abs(a - b) <= ab or abs(a - b) <= rel * abs(b))


def c(arm):
    return man["x9_" + arm.replace(".", "_")]["designed"]


def E(arm):
    """pJ a line over its family's zeros arm, by the injected prices (inversion live: the encoded counts)."""
    d = "wr" if arm.startswith("wr") else "rd"
    k, p = c(arm), P[d]
    if k["w"] == 0:
        return 0.0
    return (p["floor"] + p["one"] * k["w"] + p["pin"] * k["hi"] + p["toggle"] * (k["t_enc"] + k["tx_enc"]) +
            p["path64"] * k["p64"] + p["path256"] * k["half"] + p["channel"] * k["k_chan"])


T = lambda arm: c(arm)["t_enc"] + c(arm)["tx_enc"]
exp = {}
for d in ("rd", "wr"):
    p = P[d]
    exp[f"{d}.pin"] = p["pin"]
    exp[f"{d}.pin_K"] = p["pin"]
    exp[f"{d}.one_tie"] = p["one"]
    exp[f"{d}.one_solve"] = p["one"]
    exp[f"{d}.pin_solve"] = p["pin"]
    exp[f"{d}.toggle"] = p["toggle"]
    exp[f"{d}.toggle_within_line"] = p["toggle"] * 512 / 496
    exp[f"{d}.toggle_off"] = p["toggle"]          # no rail carries a toggle in the synthetic
    # the floor as registered: w1 - z less one one, one pin and two toggles (w1's in-line path bits stay in it)
    exp[f"{d}.floor_w1"] = E(f"{d}.w1") - p["one"] - p["pin"] - 2 * p["toggle"]
    rn = f"{d}.rnd"
    exp[f"{d}.rnd_less_floor_ones_pins_toggles"] = E(rn) - (exp[f"{d}.floor_w1"] + c(rn)["w"] * p["one"] +
                                                            c(rn)["hi"] * p["pin"] + T(rn) * p["toggle"])
    # the tent's joint fit (reported): least squares of [1, w, hi] over the tent items present in each pass; on the write
    # side pass 912 has no x9_wr_u2 (the clock fault), so its fit is over the other five, and the mean is over 6 passes
    def fit(arms):
        X = np.array([[1.0, c(a)["w"], c(a)["hi"]] for a in arms])
        return np.linalg.lstsq(X, np.array([E(a) for a in arms]), rcond=None)[0]
    tent = [f"{d}.{s}" for s in ("w1", "u2", "u4", "u7", "u8", "l08")]
    b = fit(tent)
    if d == "wr":
        b = (5 * b + fit([a for a in tent if a != "wr.u2"])) / 6
    exp[f"{d}.floor_fit"], exp[f"{d}.one_fit"], exp[f"{d}.pin_fit"] = (float(x) for x in b)
w = P["wr"]
a64e = w["path64"] * 448 / 512
exp["wr.path64"] = exp["wr.path64_off"] = w["path64"]
exp["wr.path64_both_edges"] = a64e
exp["wr.path256"] = exp["wr.path256_off"] = w["path256"]
a256e = (w["path64"] * 64 + w["path256"] * 256 - a64e * 128) / 512
exp["wr.path256_both_edges"] = a256e
exp["wr.channel"] = exp["wr.channel_off"] = w["channel"]
exp["wr.channel_mesh_rail"] = 0.0                  # c44 and u4 carry the same ones: the NoC share does not move
exp["wr.channel_beyond_both_edges"] = (w["channel"] * 256 - a64e * 32 - a256e * 128) / 256
exp["wr.rnd_less_all_terms"] = exp["wr.rnd_less_floor_ones_pins_toggles"] - c("wr.rnd")["p64"] * w["path64"] - \
    c("wr.rnd")["half"] * w["path256"] - c("wr.rnd")["k_chan"] * w["channel"]
exp["wr.inversion_toggle_ratio"] = (T("wr.a08") - T("wr.l08")) / (T("wr.a44") - T("wr.u4"))
exp["rd.zero_line"] = ZL["rd"]
exp["wr.zero_line_scp"] = ZL["wr"] - SCP
exp["wr.zero_line_nst"] = ZL["wr"]
exp["wr.scratchpad_store"] = SCP
exp["rd.any_line"] = ZL["rd"] + exp["rd.floor_w1"]
exp["wr.any_line_scp"] = exp["wr.zero_line_scp"] + exp["wr.floor_w1"]
exp["wr.any_line_nst"] = ZL["wr"] + exp["wr.floor_w1"]

F = inj["faults"]
print("1. the passes and the gates")
check(res["headline"] == [911, 912, 914, 915, 916, 917], f"headline {res['headline']} (want 911, 912, 914-917)")
check(list(res["set_aside"]) == [str(F["drift_pass"])] and "anchor drift +0.500" in res["set_aside"][str(F["drift_pass"])],
      f"set aside {res['set_aside']} (want pass {F['drift_pass']} on its 0.5 W anchor drift)")
check(res["warmup"] == 910, f"warm-up {res['warmup']}")
check(res["gates"]["by_reason"]["clock"] == 1 and res["gates"]["failed"] == 1,
      f"gates {res['gates']} (want the one run off the clock, {F['off_clock']})")
check(res["leak_runs"] == 0 and res["clock_mhz"] == 600, f"leak {res['leak_W_per_C']} W/C from {res['leak_runs']} runs; clock "
      f"{res['clock_mhz']} (the die steady: no run warms, the auto slope falls back and corrects nothing)")

print("2. the registered prices (pJ), every pass's terms present")
pr, ppp = res["prices_pJ"], res["prices_per_pass"]
AS_CODED = {"wr.floor_w1", "wr.any_line_scp", "wr.any_line_nst"}
for k in sorted(exp):
    if k in AS_CODED:
        continue
    got = pr.get(k, {}).get("mean")
    tol = dict(rel=1e-6, ab=1e-4) if k.endswith("_fit") else {}
    check(eq(got, exp[k], **tol), f"{k}: reducer {got}, injected {exp[k]:.9g}")
# the write floor, as the reducer computes it: pass 912 lacks wr.one_tie and wr.one_solve (its x9_wr_u2 run failed the
# clock gate), and the reducer then takes the one price as 0 in that pass's floor (`(one or 0.0)`), so that pass's floor
# reads one one's price high; the other passes are exact.
off_pass = str(F["off_clock"][0])
fl = ppp.get("wr.floor_w1", {})
check(eq(fl.get(off_pass), exp["wr.floor_w1"] + c("wr.w1")["w"] * w["one"]),
      f"wr.floor_w1 in pass {off_pass} (no one price there): reducer {fl.get(off_pass)}, injected floor + one one's price "
      f"{exp['wr.floor_w1'] + w['one']:.9g} (the missing term taken as 0)")
check(all(eq(v, exp["wr.floor_w1"]) for p_, v in fl.items() if p_ != off_pass),
      f"wr.floor_w1 in the other headline passes: {sorted(set(round(v, 9) for p_, v in fl.items() if p_ != off_pass))}, "
      f"injected {exp['wr.floor_w1']:.9g}")
n = len(fl)
want_mean = exp["wr.floor_w1"] + w["one"] / n
check(eq(pr["wr.floor_w1"]["mean"], want_mean), f"wr.floor_w1 mean over {n} passes: reducer {pr['wr.floor_w1']['mean']}, "
      f"as coded {want_mean:.9g} (the design's {exp['wr.floor_w1']:.9g} + {w['one']}/{n})")
for k, z in (("wr.any_line_scp", exp["wr.zero_line_scp"]), ("wr.any_line_nst", ZL["wr"])):
    check(eq(pr[k]["mean"], z + want_mean), f"{k}: reducer {pr[k]['mean']}, as coded (zero line + that floor) {z + want_mean:.9g}")

print("3. one contrast's board, rails, off-rail value and electrons (R.u2: 128 ones, 128 high pins over zeros)")
cu = res["contrasts"]["R.u2"]
e_u2 = E("rd.u2")
noc, sram = inj["noc_one_share"] * P["rd"]["one"] * 128, inj["sram_floor_share"] * P["rd"]["floor"]
check(eq(cu["pJ_per"]["mean"], e_u2), f"R.u2 board {cu['pJ_per']['mean']} pJ a line, injected {e_u2}")
check(eq(cu["pJ_per_rail"]["noc"], noc) and eq(cu["pJ_per_rail"]["sram"], sram) and eq(cu["pJ_per_rail"]["minion"], 0.0),
      f"R.u2 rails {cu['pJ_per_rail']} (want NoC {noc}, SRAM {sram}, minion 0)")
off = e_u2 - 1.294 * noc - 1.043 * sram
check(eq(cu["pJ_per_off_rails_less_in_step"], off), f"R.u2 off the rails less the in-step losses {cu['pJ_per_off_rails_less_in_step']}, "
      f"injected {off:.9g}")
check(eq(cu["electrons_12V_per"], e_u2 * 1e-12 / (E_CH * 12.0)), f"R.u2 electrons at 12 V {cu['electrons_12V_per']:.6g}")
ev_fixed = noc * 1e-12 / (E_CH * 0.484)
ev_tel = noc * 1e-12 / (E_CH * 0.490)
check(eq(cu["electrons_rail_per"]["noc"], ev_fixed) and not eq(cu["electrons_rail_per"]["noc"], ev_tel),
      f"R.u2 NoC electrons {cu['electrons_rail_per']['noc']:.6g} = at the reducer's fixed 0.484 V ({ev_fixed:.6g}), not at "
      f"the telemetry's 490 mV ({ev_tel:.6g})")

print("4. ratios and rate tests")
dr = res["direction"]
for k, v in (("pin", P["wr"]["pin"] / P["rd"]["pin"]), ("one", P["wr"]["one"] / P["rd"]["one"]),
             ("toggle", P["wr"]["toggle"] / P["rd"]["toggle"])):
    check(eq(dr[k]["mean"], v), f"write/read {k}: reducer {dr[k]['mean']}, injected {v:.9g}")
for k in ("rd.u4", "rd.rnd", "wr.u4", "wr.rnd"):
    check(eq(res["rate_tests"][k]["mean"], 1.0), f"rate test {k}: {res['rate_tests'][k]['mean']} (want 1: the same pJ a line paced)")

print("5. the verdicts the injected values imply")
want_v = {"R0_tie": "NOT TIED", "R1_write_inversion": "LIVE", "R1b_write_pin": "TERMINATED",
          "R2_pin_write_over_read": "SAME", "R3_one_write_over_read": "WRITE HIGHER", "R4_toggle_write_over_read": "SAME",
          "R5_path64_write": "PAYS", "R6_path256_write": "BOTH DIRECTIONS", "R7_channel_write": "PAYS",
          "R8_rate_random": "rd.rnd: PER LINE, wr.rnd: PER LINE", "R8b_rate_0x0F": "rd.u4: PER LINE, wr.u4: PER LINE",
          "checks": "PASS"}
for k, v in want_v.items():
    check(res["verdicts"][k]["verdict"] == v, f"{k}: {res['verdicts'][k]['verdict']} (want {v})")
loc = res["verdicts"]["R12_ddr_rail"]["why"]
want_loc = {"W.p64x": "still", "W.h256x": "still", "W.tog": "moves", "W.inv": "still", "W.c44x": "still",
            "W.rnd": "still", "R.tog": "moves", "R.rnd": "still", "W.tie27": "still", "R.tie27": "still"}
check(all(f"{k} {v}" in loc for k, v in want_loc.items()), f"R12 classes: {loc}")
check(all(x["verdict"] == "PASS" for x in res["checks"].values()), f"C1-C6: {[(k, x['verdict']) for k, x in res['checks'].items()]}")

print("6. the sensitivity arms")
diff = res["sensitivity"]["differs_from_primary"]
check(diff["leak_0.2936"] == [] and diff["leak_0.3803"] == [], f"leakage arms differ on {diff['leak_0.2936']}, {diff['leak_0.3803']}")
print(f"  (reported) the unfiltered arm, which keeps pass {F['dip'][0]}'s 9 W dip in {F['dip'][1]}, differs on {diff['unfiltered']}")

if res_smoke is not None:
    print("7. the same session with the smoke pass p901 also given (--warmup 910)")
    check(901 in res_smoke["headline"] and len(res_smoke["headline"]) == len(res["headline"]) + 1,
          f"headline {res_smoke['headline']}: the smoke counts as a headline pass")
    same_prices = all(eq(res_smoke["prices_pJ"][k]["mean"], res["prices_pJ"][k]["mean"]) for k in res["prices_pJ"]
                      if res["prices_pJ"][k]["mean"] is not None)
    print(f"  (reported) every price the same with p901 given: {same_prices}: no contrast has both its items in the smoke, "
          f"but the minimum of {5} headline passes counts it")

print(f"\n{n_ok} hold, {len(bad)} fail")
print("SYNTH CHECK " + ("CONSISTENT" if not bad else "INCONSISTENT"))
sys.exit(1 if bad else 0)
