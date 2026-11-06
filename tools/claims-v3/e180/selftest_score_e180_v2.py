#!/usr/bin/env python3
"""The self-test of E180's v2 reduction and scorer (the kit's dated note 1, KIT.md.dated-note-1.md section 2), on synthetic sessions.

    /usr/bin/python3 tools/claims-v3/e180/selftest_score_e180_v2.py [--root .] > logs/selftest-score-e180-v2.txt   # exit 0 if all pass

It needs a python3 with numpy (analyze_catalogue.py's): on the Intel /usr/bin/python3 (3.9, numpy 1.26.4), as step 22 uses.
  V1  every registered rule reads as v1's on v1's own synthetic sessions (selftest_score_e180.py's session(): truths P, C, E, F, A, the
      operand-bit term, fadd.pi returning to zero, no difference, one kept pass, card 1 with a pass set aside): verdict for verdict, and
      the same SIGN, SIZE, interval and arms inside, for all eight rules and the owner's sentence;
  V2  the reported arms on a session that carries R, D_FL1 and D_E60 (truth P; the rail at 0.7741 of the board, each footing's D at P's
      price on that footing): RA1, RA2 and RA3 read P inside on R and on each footing, and C outside on R;
  V3  A1-7: check_elf_e180.py FAIL for 261 makes E180-A NOT SCORED (v1's record kept), UNREAD labels it "walk not verified", PASS
      "walk verified by disassembly", FAIL for 262 marks fadd.pi.acc only;
  V4  A1-1: E180-L read with P's slope within 0.002 W a bit of its interval's edge is flagged footing-limited (passes at 1.010-1.014 x P),
      and not when P sits mid-interval with a half-width near the registered one (0.975-1.025 x P: 0.0047 W a bit);
  V5  A1-5: an E180-A truth 1.3 x P's (inside P's offset band) reads SIZE FAIL LOW, "not separated from the harts' start offset";
  V6  raw passes through reduce_e180_v2.py: v1's D, kept passes and set-aside returned unchanged; with a flat die D_FL1 = D_E60 = D and
      R = R_raw = the synthetic rail's rise / 0.94; with a die that steps up during each burst, D_FL1 - D = (k21 - k_FL1) x rise and
      D_E60 - D = (k21 - 0.2026) x rise, and R_raw - R = 0.81 x k21 x the filtered rise / 0.94, the filtered rise 0.8-0.95 of the step
      (a first-order lag of 1.235 s reaches about 0.89 of a 3 s step at the rails' window, less the previous burst's tail in the idle).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import gzip
import json
import math
import os
import random
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e180 as s1  # noqa: E402
import score_e180_v2 as s2  # noqa: E402
import selftest_score_e180 as t1  # noqa: E402  (v1's synthetic sessions)


def load(n):
    return json.load(open(os.path.join(HERE, n)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    a = ap.parse_args()
    fc, foot, off, noise = load("forecast-e180.json"), load("footing-e180-a1.json"), load("offset-e180-a1.json"), load("noise/noise-e180.json")
    K = fc["kinds"]
    elf0 = {"261": "UNREAD", "262": "UNREAD", "file": False}
    res = []

    def case(name, cond, detail):
        res.append(bool(cond))
        print(f"{name}: {'PASS' if cond else 'FAIL'} - {detail}")

    arm = lambda a_: (lambda nm, card: K[nm]["W"][card][a_])
    op = lambda nm, card: K[nm]["W"][card]["P"] + (0.05 * K[nm]["operand_popcount"] if K[nm]["mode"] == "fadd.ps" and K[nm]["operand_popcount"] else 0.0)
    rz = lambda nm, card: (0.1649 * K[nm]["result_popcount"] if K[nm]["mode"] == "fadd.pi" and K[nm]["result_popcount"] else K[nm]["W"][card]["P"])
    truths = [("P", arm("P"), {}), ("C", arm("C"), {}), ("E", arm("E"), {}), ("F", arm("F"), {}), ("A", arm("A"), {}),
              ("op", op, {}), ("rz", rz, {}), ("null", lambda nm, card: 0.0, {}), ("one pass", arm("P"), {"passes": t1.PASSES[:1]}),
              ("card 1", arm("P"), {"card": "aifoundry1-c1", "drop": ("18012", "fadd.ps/f_7")})]
    same, n = 0, 0
    diffs = []
    for name, f, kw in truths:
        card = kw.get("card", "aifoundry3")
        red = t1.session(fc, f, **kw)
        v1 = s1.score(copy.deepcopy(red), fc, card)
        v2 = s2.score(copy.deepcopy(red), fc, card, foot, off, elf0, noise)
        for rule, r in v1["rules"].items():
            n += 1
            q = v2["rules"][rule]
            ok = q["verdict"] == r["verdict"] and all(q.get(k) == r.get(k) for k in ("sign", "size", "lo", "hi", "mean", "arms_inside"))
            same += ok
            if not ok:
                diffs.append(f"{name}/{rule}")
        n += 1
        same += v1.get("owners_sentence_measured") == v2.get("owners_sentence_measured")
    case("V1 v1's rules on v1's synthetic sessions", same == n, f"{same} of {n} rule readings identical (10 sessions){'; differ: ' + ', '.join(diffs) if diffs else ''}")

    # V2: the reported arms
    red = {"card": "aifoundry3", "passes": {}, "set_aside": {}}           # P's truth scaled by +-1% alternately: every mean is P's own
    for p, g in zip(t1.PASSES, [1.01, 0.99, 1.01, 0.99, 1.01, 0.99]):
        D = {nm: 26.0 + g * K[nm]["W"]["aifoundry3"]["P"] for nm in K}
        red["passes"][p] = {"D": D, "runs": {nm: [{"w": v, "ops_per_s": 4.58e11}] for nm, v in D.items()}}
    pP = fc["prices"]["P@aifoundry3"]["pN_fJ"]
    gFL = foot["F2_prices_by_footing"]["FL1"]["P_pN_fJ"] / pP          # each footing's truth: P at that footing's price
    gE = foot["F2_prices_by_footing"]["E60_inrun"]["P_pN_fJ"] / pP
    for p, rec in red["passes"].items():
        rec["R"] = {nm: 0.7741 * (v - 26.0) for nm, v in rec["D"].items()}
        rec["D_FL1"] = {nm: 26.0 + gFL * (v - 26.0) for nm, v in rec["D"].items()}
        rec["D_E60"] = {nm: 26.0 + gE * (v - 26.0) for nm, v in rec["D"].items()}
        rec["rise"] = {nm: 0.0824 * (v - 26.0) for nm, v in rec["D"].items()}
    v2 = s2.score(red, fc, "aifoundry3", foot, off, elf0, noise)["reported_v2"]
    ra1, ra2, ra3 = v2["RA1_const_minus_zeros"], v2["RA2_his_pair"], v2["RA3_ladder_slope"]
    ok = (ra1["R"]["where"]["P"] == "inside" and ra1["R"]["where"]["C"] != "inside" and ra2["R"]["where"]["P"] == "inside"
          and ra3["R"]["where"]["P"] == "inside" and ra3["R"]["where"]["C"] == "above" and ra3["D_FL1"]["where"]["P"] == "inside"
          and ra3["D_E60"]["where"]["P"] == "inside" and ra2["D_E60"]["where"]["P"] == "inside")
    case("V2 the reported arms read P on the rail and on each footing", ok,
         f"RA1 R {ra1['R']['mean']:+.4f} (P {ra1['R']['forecast']['P']:+.4f} {ra1['R']['where']['P']}, C {ra1['R']['where']['C']}); "
         f"RA3 R {ra3['R']['mean']:.5f} (P {ra3['R']['forecast']['P']:.5f} {ra3['R']['where']['P']}); RA3 E60 {ra3['D_E60']['mean']:.5f} "
         f"(P {ra3['D_E60']['forecast']['P']:.5f} {ra3['D_E60']['where']['P']})")

    # V3: A1-7
    red = t1.session(fc, arm("P"))
    out = {}
    for tag, elf in (("FAIL261", {"261": "FAIL", "262": "PASS", "file": True}), ("UNREAD", elf0),
                     ("PASS", {"261": "PASS", "262": "PASS", "file": True}), ("FAIL262", {"261": "PASS", "262": "FAIL", "file": True})):
        out[tag] = s2.score(copy.deepcopy(red), fc, "aifoundry3", foot, off, elf, noise)
    A = {k: v["rules"]["E180-A"] for k, v in out.items()}
    ok = (A["FAIL261"]["verdict"] == "NOT SCORED" and "v1" in A["FAIL261"] and A["UNREAD"]["walk"] == "walk not verified"
          and A["PASS"]["walk"] == "walk verified by disassembly" and A["FAIL262"]["walk"] == "walk verified by disassembly"
          and out["FAIL262"]["reported_v2"]["walk_labels"]["fadd.pi.acc"] == "the sums do not walk as registered"
          and all(out[k]["rules"]["E180-H"]["verdict"] == out["UNREAD"]["rules"]["E180-H"]["verdict"] for k in out))
    case("V3 A1-7, the disassembly's reading", ok, "; ".join(f"{k}: A {v['verdict']} ({v.get('walk', v.get('why', ''))[:60]})" for k, v in A.items()))

    # V4: A1-1, footing-limited: sessions whose passes scale P's truth by stated factors, so L's interval is known in advance
    def scaled(factors):
        red = {"card": "aifoundry3", "passes": {}, "set_aside": {}}
        for p, g in zip(t1.PASSES, factors):
            D = {nm: 26.0 + g * K[nm]["W"]["aifoundry3"]["P"] for nm in K}
            red["passes"][p] = {"D": D, "runs": {nm: [{"w": v, "ops_per_s": 4.58e11}] for nm, v in D.items()}}
        return red
    lim = s2.score(scaled([1.010, 1.014, 1.010, 1.014, 1.010, 1.014]), fc, "aifoundry3", foot, off, elf0, noise)   # P just under L
    mid = s2.score(scaled([1.025, 0.975, 1.025, 0.975, 1.025, 0.975]), fc, "aifoundry3", foot, off, elf0, noise)   # P mid-interval
    L1, L2 = lim["rules"]["E180-L"], mid["rules"]["E180-L"]
    case("V4 A1-1, E180-L footing-limited near its edge", L1["footing_limited"] and not L2["footing_limited"],
         f"P x 1.010-1.014: L {L1['verdict']} [{L1['lo']:.5f}, {L1['hi']:.5f}] flagged {L1['footing_limited']}; P x 0.975-1.025: "
         f"L {L2['verdict']} [{L2['lo']:.5f}, {L2['hi']:.5f}] flagged {L2['footing_limited']}")

    # V5: A1-5, E180-A inside P's offset band
    aa = ("fadd.ps.acc/f_4",)
    trA = lambda nm, card: K[nm]["W"][card]["P"] * (1.3 if nm in aa else 1.0)
    A5 = s2.score(t1.session(fc, trA), fc, "aifoundry3", foot, off, elf0, noise)["rules"]["E180-A"]
    case("V5 A1-5, E180-A inside P's offset band", A5["size"]["P"] == "FAIL LOW" and A5["size_reading"] == "not separated from the harts' start offset",
         f"A {A5['verdict']}, mean {A5['mean']:+.3f} W, band {A5['offset_band_P_W']}, reading: {A5['size_reading']}")

    # V6: raw passes through reduce_e180_v2.py
    plan = load("plan-e180.json")
    cfgs = load("cfgs-e180.json")
    kind = {c["cfg"]: c["kind"] for c in cfgs["cfgs"]}
    truthW = {nm: K[nm]["W"]["aifoundry3"]["P"] + 10.0 for nm in K}
    for variant in ("flat", "step"):
        with tempfile.TemporaryDirectory() as t:
            data = os.path.join(t, "e180")
            rng = random.Random(7)
            for p in ("18010", "18011"):
                d = os.path.join(data, f"p{p}")
                os.makedirs(d)
                tel, runs = [], []
                tms = [1_800_000_000_000]
                idle = 26.0

                def sample(w, die):
                    tel.append({"t_ms": tms[0], "board_w": w + rng.gauss(0, 0.05), "temp_c": {"minshire": [die]},
                                "mhz": {"minion": 600}, "sp": {"minion_w": [8.0 + 0.7741 * (w - idle)] * 3, "sram_w": [2.3] * 3,
                                                                "noc_w": [2.5] * 3}, "took_ms": 22})
                    tms[0] += 100
                for _ in range(100):
                    sample(idle, 58.0)
                for name in plan["order"][p]:
                    for _ in range(45):
                        sample(idle, 58.0)
                    t0 = tms[0]
                    die = 58.0 + (0.1 * truthW[kind[name]] if variant == "step" else 0.0)
                    for _ in range(30):
                        sample(idle + truthW[kind[name]], die)
                    for L in range(7):
                        runs.append({"host": "aifoundry3", "pass": int(p), "cfg": name, "kind": kind[name], "pattern": "x",
                                     "unit": "instruction", "operands": "file", "harts": 2, "scp": False, "participants": 2048,
                                     "shires": 32, "t_start_ms": t0 + L * 400, "t_end_ms": t0 + L * 400 + 399, "ops": 10 ** 11,
                                     "bytes": 0, "cycles_max": 240000000, "ops_per_cycle_per_hart": 0.373, "wall_s": 0.4})
                for _ in range(60):
                    sample(idle, 58.0)
                with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as f:
                    f.write("".join(json.dumps(x) + "\n" for x in tel))
                with gzip.open(os.path.join(d, "runs.jsonl.gz"), "wt") as f:
                    f.write("".join(json.dumps(x) + "\n" for x in runs))
                json.dump({"status": "ok"}, open(os.path.join(d, "block.json"), "w"))
            o1, o2 = os.path.join(t, "r1.json"), os.path.join(t, "r2.json")
            p1 = subprocess.run([sys.executable, "-B", os.path.join(HERE, "reduce_e180.py"), "--data", data, "--out", o1, "--root", a.root],
                                capture_output=True, text=True)
            p2 = subprocess.run([sys.executable, "-B", os.path.join(HERE, "reduce_e180_v2.py"), "--data", data, "--out", o2, "--root", a.root],
                                capture_output=True, text=True)
            if p1.returncode or p2.returncode:
                case(f"V6 raw passes ({variant})", False, f"rc {p1.returncode} / {p2.returncode}: {p1.stderr[-200:]} {p2.stderr[-300:]}")
                continue
            r1, r2 = json.load(open(o1)), json.load(open(o2))
            v1same = all(r2[g][p][k] == r1[g][p][k] for g in ("passes", "set_aside") for p in r1[g] for k in r1[g][p]) and \
                set(r2["passes"]) == set(r1["passes"]) and set(r2["set_aside"]) == set(r1["set_aside"])
            q = r2["v2"]["footing_law_quad_w"]
            errs, rails, hfr = [], [], []
            for p, rec in r2["passes"].items():
                for nm, runs_ in rec["runs_v2"].items():
                    for e, vr in zip(runs_, rec["runs"][nm]):
                        if variant == "flat":
                            errs.append(abs(e["D_FL1"] - vr["w"]) + abs(e["D_E60"] - vr["w"]) + abs(e["R"] - e["R_raw"]))
                            rails.append(abs(e["R_raw"] - 0.7741 * truthW[nm] / 0.94))
                        else:
                            tm = 58.0 + e["rise"] / 2
                            k21 = 23.257 / 36 * math.exp((tm - 80) / 36)
                            kfl = 2 * q[0] * tm + q[1]
                            errs.append(abs((e["D_FL1"] - vr["w"]) - (k21 - kfl) * e["rise"]) + abs((e["D_E60"] - vr["w"]) - (k21 - 0.2026) * e["rise"]))
                            kr = 23.257 / 36 * math.exp((0.5 * (e["t_rails_window_c"] + e["t_rails_idle_c"]) - 80) / 36)
                            rails.append(abs((e["R_raw"] - e["R"]) - 0.81 * kr * e["rise_rails_filtered_c"] / 0.94))
                            if e["rise"] > 0.3:
                                hfr.append(e["rise_rails_filtered_c"] / e["rise"])
            detail = f"v1's fields unchanged {v1same}; max formula error {max(errs):.2e} W; max rail error {max(rails):.2e} W"
            ok = v1same and max(errs) < 1e-9 and (max(rails) < 0.05 if variant == "flat" else max(rails) < 1e-9)
            if variant == "step":
                fr = sum(hfr) / len(hfr)
                detail += f"; filtered rise / step {fr:.3f} over {len(hfr)} bursts (want 0.8-0.95)"
                ok = ok and 0.8 < fr < 0.95
            case(f"V6 raw passes through reduce_e180_v2 ({variant} die)", ok, detail)
    print(f"SELFTEST-V2 {'PASS' if all(res) else 'FAIL'}: {sum(res)} of {len(res)}")
    sys.exit(0 if all(res) else 1)


if __name__ == "__main__":
    main()
