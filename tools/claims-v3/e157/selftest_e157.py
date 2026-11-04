#!/usr/bin/env python3
"""E157's self-test (Q139), before the claim: the registered scorer score_e157.py run end to end on simulated sessions built from the frozen
predictions (nothing here is a measurement). A smaller port of tools/claims-v3/e142/selftest_e142.py: 30 sessions a world, three passes,
0.05 W / 0.05 C pass noise, bootstrap draws cut to 2,000 for speed. Worlds: M8 as good as its nested score (each tile's error drawn from
M8's own card-1 reference errors), twice as bad, a -0.3 W bias on the floats at 1x, and M6 right (M8 wrong by M8 - M6). It also checks the
C-check and K1 paths: all PASS reads PC, K1C and PCa PASS; one ROUNDING launch on a K1 tile reads K1C FAIL with the critic's literal
reading PASS; one unrecorded launch reads FAIL; a FAIL on a pool-6 tile takes it out of the scored set (and only it); a K1 tile moved
0.3 W reads K1D and K1W FAIL; X1/X2 at M8's own card ratio read PASS. Standard library only.

    python3 tools/claims-v3/e157/selftest_e157.py > tools/claims-v3/e157/selftest.txt
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e157 as S  # noqa: E402

REG = json.load(open(os.path.join(HERE, "predictions-e157.json")))
REG["plan"]["bootstrap"] = {"draws": 2000, "seed": 15700}
PASSES = [15710, 15711, 15712]
EXTRA = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full")


def session(rng, world, k1_shift=0.0, scale=1.0):
    ref = REG["reference_errors"]["power_card1"]
    hs = REG["model"]["heat_pool_card1_rms_c"]
    true = {}
    for t, P in REG["tiles"].items():
        f = P["type"]
        e = ref[f][rng.randrange(len(ref[f]))] * (2.0 if world == "twice" else 1.0)
        if world == "bias" and f != "int8":
            e -= 0.3
        if world == "m6_right":
            e = P["M6"]["D_w"] - P["M8"]["D_w"] + rng.gauss(0, 0.05)
        true[t] = ((P["M8"]["D_w"] + e) * scale, P["M8"]["dT_win_c"] + rng.gauss(0, hs[f]), P["M8"]["S_w"] + e)
    k1 = {t: (REG["k1"][t]["E142_q139u_footing"]["D"]["mean"] + (k1_shift if t == "int8.gray_a" else 0.0)) for t in REG["k1"]}
    pp = {}
    for p in PASSES:
        d = {}
        for t, (D, T, Sw) in true.items():
            d[t] = {"D": D + rng.gauss(0, 0.05), "dT_win": T + rng.gauss(0, 0.05), "S": Sw + rng.gauss(0, 0.05)}
        for t, D in k1.items():
            d[t] = {"D": D + rng.gauss(0, 0.05), "dT_win": 1.0, "S": D + 1.8}
        for a in EXTRA:
            d[a] = {"D": 0.0, "dT_win": 0.2, "S": 1.8}
        pp[str(p)] = d
    return {"passes": PASSES, "per_pass": pp, "leak": {"mode": "selftest"}, "reducer": {}}


def c_files(tmp, items, spoil=None):
    """Synthetic runs.jsonl and a ccheck verdict file: every item 9 launches in pass 15710, all PASS unless spoiled."""
    runs, launches, t = [], [], 1793700000000
    for it in items:
        for L in range(-1, 8):
            runs.append({"item": it, "block": 15710, "launch": L, "t_start_ms": t, "t_end_ms": t + 490})
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


def main():
    rng = random.Random(15799)
    counts = {}
    for world in ("as_good", "twice", "bias", "m6_right"):
        c = {}
        for _ in range(30):
            s = S.score(session(rng, world), REG)
            for rid, v in S.verdicts(s).items():
                c.setdefault(rid, {}).setdefault(v, 0)
                c[rid][v] += 1
        counts[world] = c
    print("E157 self-test: score_e157.score on simulated sessions (30 a world, 3 passes, 0.05 W pass noise, 2,000 draws); nothing "
          "here is a measurement")
    for w, c in counts.items():
        print(f"\n[{w}]")
        for rid in sorted(c):
            if rid.startswith(("E157-X", "E157-S")):
                continue
            print(f"  {rid}: " + ", ".join(f"{k} {v}" for k, v in sorted(c[rid].items())))
    tmp = os.path.join(HERE, "__selftest_tmp")
    os.makedirs(tmp, exist_ok=True)
    items = list(REG["sets"]["k1"]) + sorted(REG["tiles"]) + list(EXTRA) + ["anchor_pi"]
    print("\n[C check and K1]")
    for label, spoil in (("all PASS", None), ("one ROUNDING launch on fp16.exp_only (K1)", ("fp16.exp_only", 3, "ROUNDING")),
                         ("one unrecorded launch on fp32.c_absorbed", ("fp32.c_absorbed", 2, "unrecorded")),
                         ("one FAIL launch on int8.gray_a (K1)", ("int8.gray_a", 0, "FAIL")),
                         ("one FAIL launch on fp32.zeros (frame)", ("fp32.zeros", 1, "FAIL"))):
        rj, cj = c_files(tmp, items, spoil)
        per, notpass, n = S.c_join([rj], [cj])
        summ = S.c_summary(per, {15710})
        k = S.c_rule(summ, REG["sets"]["k1"], "K1")
        pc = S.c_rule(summ, sorted(REG["tiles"]), "PC")
        pca = S.c_rule(summ, list(S.E78_FRAME), "PCa")
        s = S.score(session(random.Random(5), "as_good"), REG, cstat=summ)
        print(f"  {label}: K1C {k['verdict']} (critic's literal {k['critic_literal_exact_or_rounding']}), PC {pc['verdict']}, "
              f"PCa {pca['verdict']}; scored set {s['tiles_scored']} of 50, excluded {s['c_excluded']}; "
              f"not PASS {[(x['item'], x['class']) for x in notpass]}")
    for shift in (0.0, 0.3):
        res = session(random.Random(1), "as_good", k1_shift=shift)
        out = S.k1_frames(REG, [("q139u_footing", res, "E142_q139u_footing")])["q139u_footing"]
        print(f"  K1 with int8.gray_a moved {shift:+.1f} W: K1D {out['within_0p05']['verdict']} (outside {out['within_0p05']['outside']}), "
              f"K1W {out['welch']['verdict']} (outside {out['welch']['outside']})")
    a3 = copy.deepcopy(session(random.Random(2), "as_good"))
    for p in a3["per_pass"].values():
        for t in p:
            p[t]["D"] = p[t]["D"] / REG["model"]["card_term_applied"]["M8"]
    s = S.score(session(random.Random(2), "as_good"), REG, e153=a3)
    print("  X1/X2/S1/S2 at M8's own card ratio (0.9616): " + json.dumps({k: v for k, v in S.verdicts(s).items() if k[5] in "XS"}) +
          f"; S1 predicted {s['rules']['E157-S1'].get('predicted')}, measured {s['rules']['E157-S1'].get('measured')}")
    a3b = copy.deepcopy(session(random.Random(2), "as_good"))
    for p in a3b["per_pass"].values():
        for t in p:
            p[t]["D"] = p[t]["D"] / 0.9707
    s = S.score(session(random.Random(2), "as_good"), REG, e153=a3b)
    print("  X1/X2/S1/S2 at the zeros level's predicted ratio (0.9707): " +
          json.dumps({k: v for k, v in S.verdicts(s).items() if k[5] in "XS"}))
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
