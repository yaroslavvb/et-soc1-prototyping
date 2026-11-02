#!/usr/bin/env python3
"""E123 (Q134): self-test of score_e123.py on synthetic reductions in reduce_e78's per_pass format (no card, no telemetry).
Standard library only. Nothing it prints is data.

    python3 tools/claims-v3/e123/selftest_e123.py > tools/claims-v3/e123/selftest_e123.txt

Worlds: law (every draw where the frozen slope puts it, small noise; committed tiles at E94's frozen gate-law offsets),
off (every committed tile 3 W above its kind, 1 W in int8), steep (the draws follow twice the frozen slope: R5 must FAIL
and class G must switch to the fitted slope), wild (draws scattered at SD 1.5 W with no relation to the gate share),
single (one kept pass: the fallback scores), none (no pass: NOT SCORED).
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e123 as sc  # noqa: E402

REG = json.load(open(os.path.join(HERE, "predictions-e123.json")))
RN = REG["rules_of_number"]
TILES = REG["tiles"]
ZEROS = {"fp32": 1.2, "fp16": 1.1, "int8": 2.4}
RATE = {"fp32": 1.12e9, "fp16": 1.12e9, "int8": 1.93e9}


def world(name, passes=(12310, 12311), seed=1):
    rnd = random.Random(f"E123-selftest|{name}|{seed}")
    per = {}
    shift = {p: rnd.gauss(0, 0.15) for p in passes}
    mu = {}
    for c, r in RN.items():
        mu[c] = r["e78_a3"]["D_w"] - (r["desk_table_e94"]["gate_law_offset_w"] or 0.0)
    for p in passes:
        e = {}
        for c, r in RN.items():
            t = r["type"]
            gb = r["rule_gate_share"]["mean"]
            off = r["desk_table_e94"]["gate_law_offset_w"] or 0.0
            if name == "off":
                off = 3.0 if t != "int8" else 1.0
            dc = mu[c] + off + shift[p] + rnd.gauss(0, 0.08)
            e[c] = {"D": dc, "S": dc + ZEROS[t]}
            for d in r["draws"]:
                g = TILES[d]["gated_lane_frac"]
                b = r["cv_slope_w_per_unit"] * (2.0 if (name == "steep" and r["class"] == "G") else 1.0)
                tile = random.Random(f"{name}|{d}").gauss(0, 1.5 if name == "wild" else 0.05)
                y = mu[c] - (0.0 if name == "wild" else b * (g - gb)) + tile + shift[p] + rnd.gauss(0, 0.08)
                e[d] = {"D": y, "S": y + ZEROS[t]}
        # the bridge draws on the card-1 scale relation (R8 holds), in the law world only
        for d, o1 in REG["bridge"]["card1_offsets_w"].items():
            if name == "law":
                e[d] = {"D": e["fp32.nn_like"]["D"] + o1 * REG["bridge"]["card_scale_fp32"] + rnd.gauss(0, 0.06)}
                e[d]["S"] = e[d]["D"] + ZEROS["fp32"]
        for c, t in REG["session_tie"]["cells"].items():
            if c not in e:
                e[c] = {"D": t["ref_w"] + rnd.gauss(0, 0.05), "S": t["ref_w"] + 1.0}
        per[str(p)] = e
    items = {c: {"rate": {"mean": RATE[r["type"]]}} for c, r in RN.items()}
    return {"experiment": "E123", "passes": list(passes), "per_pass": per, "items": items, "leak": {"mode": "fixed"}}


def main():
    checks = []

    def chk(what, ok):
        checks.append((what, bool(ok)))

    law = sc.score(world("law"), REG)
    R = law["rules"]
    chk("law: R5 PASS (the frozen slope is right)", R["E123-R5"]["verdict"] == "PASS")
    chk("law: class G uses the frozen slope", law["primary_by_class"]["G"]["slope"] == "frozen beta")
    chk("law: fp32.nn_like NO CORRECTION", R["E123-R2:fp32.nn_like"]["verdict"] == "NO CORRECTION")
    chk("law: fp16.wsparse90 NO CORRECTION", R["E123-R2:fp16.wsparse90"]["verdict"] == "NO CORRECTION")
    chk("law: fp16.sparse50's offset near +0.52", abs(R["E123-R2:fp16.sparse50"]["offset_w"] - 0.517) < 0.25)
    chk("law: R6 PASS", R["E123-R6"]["verdict"] == "PASS")
    chk("law: R7 gate law PASS", R["E123-R7:gate_law"]["verdict"] == "PASS")
    chk("law: R8 PASS", R["E123-R8"]["verdict"] == "PASS")
    chk("law: S1 PASS", R["E123-S1"]["verdict"] == "PASS")
    chk("law: R4 LF PASS", R["E123-R4:LF"]["verdict"] == "PASS")
    chk("law: R4 LI PASS or INCONCLUSIVE", R["E123-R4:LI"]["verdict"] in ("PASS", "INCONCLUSIVE"))
    chk("law: the kind's S is the committed S less the offset",
        abs(law["rules_of_number"]["fp16.sparse50"]["kind_S_w"]["mean_w"]
            - (law["rules_of_number"]["fp16.sparse50"]["committed_S_w"]["mean"] - R["E123-R2:fp16.sparse50"]["offset_w"])) < 1e-9)
    chk("law: E94-form secondary present for k >= 3", "e94_form" in law["rules_of_number"]["fp16.sparse50"])
    chk("law: no E94-form for k = 2", "e94_form" not in law["rules_of_number"]["int8.ternary"])
    off = sc.score(world("off"), REG)
    chk("off: every float rule CORRECTION", all(off["rules"][f"E123-R2:{c}"]["verdict"] == "CORRECTION"
                                               for c, r in RN.items() if r["type"] != "int8"))
    chk("off: every int8 rule CORRECTION", all(off["rules"][f"E123-R2:{c}"]["verdict"] == "CORRECTION"
                                              for c, r in RN.items() if r["type"] == "int8"))
    chk("off: S1 FAIL", off["rules"]["E123-S1"]["verdict"] == "FAIL")
    chk("off: R7 gate law FAIL", off["rules"]["E123-R7:gate_law"]["verdict"] == "FAIL")
    steep = sc.score(world("steep"), REG)
    chk("steep: R5 FAIL", steep["rules"]["E123-R5"]["verdict"] == "FAIL")
    chk("steep: class G switches to the fitted slope", steep["primary_by_class"]["G"]["slope"].startswith("fitted"))
    chk("steep: fitted slope recovers fp32.nn_like (NO CORRECTION)", steep["rules"]["E123-R2:fp32.nn_like"]["verdict"] == "NO CORRECTION")
    wild = sc.score(world("wild"), REG)
    chk("wild: R4 LF FAIL or INCONCLUSIVE", wild["rules"]["E123-R4:LF"]["verdict"] in ("FAIL", "INCONCLUSIVE"))
    chk("wild: R4 LI FAIL", wild["rules"]["E123-R4:LI"]["verdict"] == "FAIL")
    chk("wild: R6 FAIL or INCONCLUSIVE", wild["rules"]["E123-R6"]["verdict"] in ("FAIL", "INCONCLUSIVE"))
    chk("wild: no R2 says NO CORRECTION in class G", all(wild["rules"][f"E123-R2:{c}"]["verdict"] != "NO CORRECTION"
                                                        for c, r in RN.items() if r["class"] == "G"))
    single = sc.score(world("law", passes=(12310,)), REG)
    chk("single: scored with the fallback", single["single_pass_fallback"] and
        single["rules"]["E123-R2:fp32.nn_like"]["verdict"] != "NOT SCORED")
    chk("single: labelled single pass", single["rules"]["E123-R2:fp32.nn_like"].get("label") == "single pass")
    none = sc.score(world("law", passes=()), REG)
    chk("none: NOT SCORED", set(none["tally"]) == {"NOT SCORED"})
    for w, s in (("law", law), ("off", off), ("steep", steep), ("wild", wild)):
        print(f"[{w}] tally {s['tally']}")
        for rid, v in s["rules"].items():
            if not v.get("secondary"):
                print(f"   {rid:28s} {v['verdict']}")
    n_ok = sum(ok for _, ok in checks)
    print()
    for what, ok in checks:
        print(("ok   " if ok else "FAIL ") + what)
    print(f"\n{n_ok} of {len(checks)} checks pass")
    sys.exit(0 if n_ok == len(checks) else 1)


if __name__ == "__main__":
    main()
