#!/usr/bin/env python3
"""E164's self-test on simulated sessions (Q141(b)), before the claim: the registered scorer score_e164.py run end to end on sessions
built from the frozen predictions (nothing here is a measurement). selftest_e157.py's form: 20 sessions a world, four passes,
0.05 W / 0.05 C pass noise, the interval bootstrap cut to 2,000 draws and the paired one to 1,000 for speed. Worlds: M9 as good as its
nested score (each tile's error drawn from M9's own card-1 reference errors), twice as bad, a -0.3 W bias on the floats, and M6 right
(M9 wrong by M9 - M6). It also checks the paths only E164 has, at 0.01 W pass noise: rank 7's K7 with no change, with a 2% session
gain (the per-session anchor scale must remove it), with one and with two tiles moved 0.3 W; the C paths (all PASS; one ROUNDING launch
on a K7 tile; one unrecorded launch on a pool-7 tile, which leaves the scored set alone; a FAIL on one of pool 6's scale anchors, which
PCa must catch); and X1/X2 with an aifoundry3 session at M9's own card ratio (PASS) and at 0.98 (FAIL). Standard library only.

    python3 -B tools/claims-v3/e164/selftest_e164.py > tools/claims-v3/e164/selftest-sim.txt
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e164 as S  # noqa: E402

REG = json.load(open(os.path.join(HERE, "predictions-e164.json")))
REG["plan"]["bootstrap"] = {"draws": 2000, "seed": 16400}
REG["plan"]["paired_draws"] = 1000
PASSES = [16410, 16411, 16412, 16413]
FRAME = ("fp32.zeros", "fp16.zeros", "int8.zeros")


def session(rng, world, noise=0.05, gain=1.0, k7_shift=None):
    ref = REG["reference_errors"]["power_card1"]
    hs = REG["model"]["heat_pool_card1_rms_c"]
    true = {}
    for t, P in REG["tiles"].items():
        f = P["type"]
        e = ref[f][rng.randrange(len(ref[f]))] * (2.0 if world == "twice" else 1.0)
        if world == "bias" and f != "int8":
            e -= 0.3
        if world == "m6_right":
            e = P["M6"]["D_w"] - P["M9"]["D_w"] + rng.gauss(0, 0.05)
        true[t] = (P["M9"]["D_w"] + e, P["M9"]["dT_win_c"] + rng.gauss(0, hs[f]), P["M9"]["S_w"] + e)
    k7 = {t: v["E157"]["mean"] / gain + (k7_shift or {}).get(t, 0.0) for t, v in REG["k7"]["tiles"].items()}
    anc = {a: v["mean"] / gain for a, v in REG["k7"]["scale_anchors_E157"].items()}
    pp = {}
    for p in PASSES:
        d = {}
        for t, (D, T, Sw) in true.items():
            d[t] = {"D": D + rng.gauss(0, noise), "dT_win": T + rng.gauss(0, noise), "S": Sw + rng.gauss(0, noise)}
        for t, D in list(k7.items()) + list(anc.items()):
            d[t] = {"D": D + rng.gauss(0, noise), "dT_win": 1.0, "S": D + 1.8}
        for a in FRAME:
            d[a] = {"D": 0.0, "dT_win": 0.2, "S": 1.8}
        pp[str(p)] = d
    return {"passes": PASSES, "per_pass": pp, "leak": {"mode": "selftest"}, "reducer": {}}


def c_files(tmp, items, spoil=None):
    """Synthetic runs.jsonl and a ccheck verdict file: every item 9 launches in pass 16410, all PASS unless spoiled."""
    runs, launches, t = [], [], 1793800000000
    for it in items:
        for L in range(-1, 8):
            runs.append({"item": it, "block": 16410, "launch": L, "t_start_ms": t, "t_end_ms": t + 490})
            v = "PASS"
            if spoil and spoil[0] == it and spoil[1] == L:
                v = spoil[2]
            if v != "unrecorded":
                launches.append({"t_start_ms": t, "t_end_ms": t + 490, "verdict": v, "type": "fp32", "n": 536000})
            t += 500
    rj = os.path.join(tmp, "runs.jsonl")
    open(rj, "w").write("\n".join(json.dumps(r) for r in runs) + "\n")
    cj = os.path.join(tmp, "cc.json")
    json.dump({"summary": {}, "launches": launches}, open(cj, "w"))
    return rj, cj


def k7_line(label, res):
    k = S.k7_frames(REG, [("q139u_footing", res)], S.scheme_of(REG)["repeat"])["q139u_footing"]
    sc = {f: round(v["s"], 4) for f, v in k["scale"].items() if "s" in v}
    print(f"  K7, {label}: scale {sc}; K7D {k['within_0p05']['verdict']} ({k['within_0p05']['inside']} of {k['within_0p05']['n']} "
          f"within 0.05 W; outside {k['within_0p05']['outside']}), K7W {k['welch']['verdict']} (outside {k['welch']['outside']})")


def main():
    rng = random.Random(16499)
    counts = {}
    for world in ("as_good", "twice", "bias", "m6_right"):
        c = {}
        for _ in range(20):
            s = S.score(session(rng, world), REG)
            for rid, v in S.verdicts(s).items():
                c.setdefault(rid, {}).setdefault(v, 0)
                c[rid][v] += 1
        counts[world] = c
    print("E164 self-test: score_e164.score on simulated sessions (20 a world, 4 passes, 0.05 W pass noise, 2,000 interval draws, "
          "1,000 paired draws); nothing here is a measurement")
    for w, c in counts.items():
        print(f"\n[{w}]")
        for rid in sorted(c):
            if rid.startswith("E164-X"):
                continue
            print(f"  {rid}: " + ", ".join(f"{k} {v}" for k, v in sorted(c[rid].items())))
    print("\n[K7: rank 7's repeat, 0.01 W pass noise]")
    k7_line("no change", session(random.Random(3), "as_good", noise=0.01))
    k7_line("a 2% session gain (D 2% lower in every tile and anchor)", session(random.Random(3), "as_good", noise=0.01, gain=1.02))
    k7_line("int8.bheld_bit4 moved +0.3 W", session(random.Random(3), "as_good", noise=0.01, k7_shift={"int8.bheld_bit4": 0.3}))
    k7_line("two tiles moved +0.3 W", session(random.Random(3), "as_good", noise=0.01,
                                              k7_shift={"int8.bheld_bit4": 0.3, "fp16.real_qwen_qk": 0.3}))
    s0 = session(random.Random(3), "as_good", noise=0.01)
    for p in s0["per_pass"].values():
        p.pop("int8.anchor6_full")
    k7_line("int8.anchor6_full not measured (the int8 scale lacks an anchor)", s0)
    tmp = os.path.join(HERE, "__selftest_tmp")
    os.makedirs(tmp, exist_ok=True)
    sch = S.scheme_of(REG)
    items = list(REG["sets"]["k7"]) + sorted(REG["tiles"]) + list(sch["frame_c"])
    print("\n[C check]")
    for label, spoil in (("all PASS", None), ("one ROUNDING launch on fp16.real_qwen_qk (K7)", ("fp16.real_qwen_qk", 3, "ROUNDING")),
                         ("one unrecorded launch on fp32.exp_b_alt_nib (pool 7)", ("fp32.exp_b_alt_nib", 2, "unrecorded")),
                         ("one FAIL launch on int8.anchor6_full (the scale's anchor)", ("int8.anchor6_full", 0, "FAIL"))):
        rj, cj = c_files(tmp, items, spoil)
        per, notpass, n = S.c_join([rj], [cj])
        summ = S.c_summary(per, {16410})
        k = S.c_rule(summ, REG["sets"]["k7"], "K7")
        pc = S.c_rule(summ, sorted(REG["tiles"]), "PC")
        pca = S.c_rule(summ, list(sch["frame_c"]), "PCa")
        s = S.score(session(random.Random(5), "as_good"), REG, cstat=summ)
        print(f"  {label}: K7C {k['verdict']} (literal {k['critic_literal_exact_or_rounding']}), PC {pc['verdict']}, PCa {pca['verdict']}; "
              f"scored set {s['tiles_scored']} of 61, excluded {s['c_excluded']}; not PASS {[(x['item'], x['class']) for x in notpass]}")
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    print("\n[X1/X2: the card term with an aifoundry3 session]")
    term = REG["model"]["card_term_applied"]
    for label, rf, ri in (("M9's own terms", term["M9"], term["M9_int8"]), ("0.98", 0.98, 0.98)):
        c1 = session(random.Random(2), "as_good")
        a3 = copy.deepcopy(c1)
        for p in a3["per_pass"].values():
            for t in p:
                p[t]["D"] = p[t]["D"] / (ri if t.startswith("int8.") else rf)
        s = S.score(c1, REG, other=a3)
        x1, x2 = s["rules"]["E164-X1"], s["rules"]["E164-X2"]
        print(f"  aifoundry3 at card 1 / {label}: " + json.dumps({k: v for k, v in S.verdicts(s).items() if "-X" in k}) +
              f"; X1 median {x1.get('median_ratio'):.6f} against {x1.get('card_term'):.6f}, X2 {x2.get('median_ratio'):.6f} against "
              f"{x2.get('card_term'):.6f}")


if __name__ == "__main__":
    main()
