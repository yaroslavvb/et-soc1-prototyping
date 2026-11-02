#!/usr/bin/env python3
"""E122 (Q134): write predictions-e122.json, the frozen numbers of E108's sign-location designs replicated on a second card
(aifoundry3 card 0, 600 MHz), with the accumulators read back as E104 and E108 read them. Every number is read from a
committed file named below (each checked by sha256), copied or computed, never retyped. Registration: E122.md beside this
file.

    python3 tools/claims-v3/e122/make_predictions_e122.py            # writes predictions-e122.json
    python3 tools/claims-v3/e122/make_predictions_e122.py --check    # recomputes and compares, writes nothing

What it freezes:
  * E108's thirteen rules with E108's own lines (predictions-e108.json > rules), scored by score_e108.py's functions,
    unchanged; three of E108's references are card 1's and are replaced by this card's, each from a committed file:
      - R2 (the step): E108's own step on card 1 (scored.json > primary > quantities > fp32.step, fp16.step) times
        E82's per-type card scale (aifoundry3 over card 1), in place of E106's steps on card 1; E108's +-1 W band;
      - S1 (the session tie): E78's cells on aifoundry3 (e78.json > items > <cell> > D) with E108's bands, in place
        of E82's on card 1;
      - M4 (R11 and every quantity's M): the model's own prediction on the card it was fitted on, E108's frozen M
        divided by E108's card-1 scale (predictions-e108.json > model > card1_scale): M4 was fitted on E78, which ran
        on aifoundry3, and E108 multiplied it by that scale for card 1. The 95% limits are divided the same way;
  * the cross-card rules X-<quantity>: E108's per-pass quantity on card 1 (mean, 95% half-width, per-pass sd) times the
    card scale (W contrasts; ratios and differences of ratios carry no scale), with a tolerance w; their power by
    simulation at E108's per-pass sd;
  * E108's verdicts, and what I expect on this card.
Standard library only.
"""
import copy
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "predictions-e122.json")
SL = "tools/claims-v3/signloc"
D108 = "docs/reports/data/2026-11-01-e108-sign-located"

SOURCES = {
    "e108_predictions": (f"{SL}/predictions-e108.json", "735edb15",
                         "13a704d486ecdf843dca1623451a4abf6cb424ca16f1089932d2397eabc57564"),
    "e108_scored": (f"{D108}/scored.json", "a3488b5e",
                    "756d7cfd7676f2a88d72ffeba1463bc7fe396049f611b42adb5cfb566f811ece"),
    "e108_reduction": (f"{D108}/e108.json", "a3488b5e",
                       "9fe5ae20b1a582e453302ccb49370e74feb0ab5a8243bf728ab3d286b3709d1a"),
    "e78_reduction": ("docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json", "410c56f6",
                      "b7463b6c2c159eb70bd59418f729c4c9144f6eec778126ef660fe781cc724da5"),
    "e82_scored": ("docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json", "0a041356",
                   "498d5c70f01778248c7800d7d1d7e07b033db35f29b897d40f5a21787bef0b53"),
}
# the card code E122 runs unchanged: E78's (lib.sh, run_e78.py, e78_common.py, kinds.json, reduce_e78.py, which
# run_e108.py and reduce_e108.py check themselves) and E108's (its block, runner, items, tiles, read-back code)
CARD_CODE = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
             "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json",
             f"{SL}/e108_common.py", f"{SL}/run_e108.py", f"{SL}/block_e108.sh", f"{SL}/readback_e108.py",
             f"{SL}/predictions-e108.json", f"{SL}/e108/e108.json"]
DESK_CODE = [f"{SL}/reduce_e108.py", f"{SL}/score_e108.py"]
E122_FILES = ["tools/claims-v3/e122/run_e122.sh", "tools/claims-v3/e122/session_e122.sh",
              "tools/claims-v3/e122/block_readback_e122.sh", "tools/claims-v3/e122/readback_e122.py",
              "tools/claims-v3/e122/score_e122.py", "tools/claims-v3/e122/collect_e122.sh",
              "tools/claims-v3/e122/selftest_e122.py"]
# the read-back host E116 built on aifoundry3 from E104's one-flag patch (tools/claims-v3/e116/README.md: 92d15e46...)
READBACK_HOST = {"path": "build/e116/b/host/sparsity_host",
                 "sha256": "92d15e46781093a83359b37f3ba9c6e3c294a6fd8bb577e1cbf6b519ea2992b5",
                 "kernel": "build/sparsity/kernel/sparsity.elf",
                 "kernel_sha256": "d521e43248d00b4da455ada7020741f39b8940e52bbbce05380beccedcd17d19",
                 "power_host_sha256": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0"}

# the cross-card rules: which E108 quantities, and their tolerance w
X_W = ["fp32.step", "fp16.step", "fp32.held_z", "fp16.held_z", "fp32.held_abs", "fp32.Bz_het", "fp32.Bz_rest",
       "fp32.het_mx", "fp32.rest", "fp32.ex_over_sg", "fp32.mx_over_ex", "fp32.alt_held", "fp32.alt_walk",
       "fp16.alt_walk", "fp32.A_on_B_held", "fp32.A_on_B_walk", "A_vs_B_priced"]
X_SHARE = ["fp32.share_z", "fp16.share_z", "fp32.share_abs", "formats_z", "design_fp32", "fp32.share_het",
           "fp32.share_het_z"]
X_OTHER = {"fp32.alt_ratio": 0.30, "alt_walk_ratio": 0.60}
W_W, W_SHARE = 0.75, 0.15
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}
EXPECT = {"E108-R1": "PASS", "E108-R2": "PASS", "E108-R3": "ALIKE", "E108-R4": "ABSORBED HIGHER",
          "E108-R5": "PRICED ALIKE", "E108-R6": "INCONCLUSIVE / NOTHING MEASURABLE", "E108-R7": "MOST",
          "E108-R12": "MOST", "E108-R8": "RISES / RISES", "E108-R9": "FALLS", "E108-R10": "INCONCLUSIVE",
          "E108-R11": "PASS", "E108-S1": "PASS"}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(key):
    rel, commit, want = SOURCES[key]
    have = sha(rel)
    if have != want:
        raise SystemExit(f"{rel}: sha256 {have} != the one this freeze was written from ({want})")
    return json.load(open(os.path.join(ROOT, rel)))


def qtype(name):
    return "fp16" if name.startswith("fp16.") else "fp32"


def sim_x(mean, h108, s, sd, w, delta, n, rng, N=4000):
    """P(PASS, FAIL, INCONCLUSIVE) of one X rule: E122's per-pass values ~ Normal(s*mean + delta, s*sd), n passes."""
    p = f = 0
    tq = T95[n - 1]
    for _ in range(N):
        v = [rng.gauss(s * mean + delta, s * sd) for _ in range(n)]
        m = sum(v) / n
        sdv = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
        h = math.sqrt((tq * sdv / math.sqrt(n)) ** 2 + (s * h108) ** 2)
        d = m - s * mean
        if abs(d) + h <= w:
            p += 1
        elif abs(d) - h > w:
            f += 1
    return [round(p / N, 3), round(f / N, 3), round(1 - (p + f) / N, 3)]


def build():
    p108 = load("e108_predictions")
    s108 = load("e108_scored")
    load("e108_reduction")
    e78 = load("e78_reduction")
    e82 = load("e82_scored")
    # E108's own card code must still be byte-identical to its freeze (E122 runs it unchanged)
    h = p108["harness"]
    bad = [f for f, w in h["e108_files_sha256"].items() if sha(f) != w]
    bad += [f for f, w in h["reused_unchanged_sha256"].items() if sha(f) != w]
    if sha(f"{SL}/e108/e108.json") != h["e108_json_sha256"]:
        bad.append("e108.json")
    if bad:
        raise SystemExit(f"E108's frozen code changed: {bad}")
    scale = e82["cross_card"]["primary"]["x3"]["per_type_median"]
    c1 = p108["model"]["card1_scale"]
    prim = s108["primary"]
    Q108 = prim["quantities"]

    # --- the substitutions into E108's registration for this card ---
    tiles = {}
    for n, t in p108["tiles"].items():
        pr = t["pred"]
        tiles[n] = {"M": pr["M"] / c1, "lo95": pr["lo95"] / c1, "hi95": pr["hi95"] / c1,
                    "e108_card1": {"M": pr["M"], "lo95": pr["lo95"], "hi95": pr["hi95"]}}
    qm = {}

    def m_of(name):
        if name in qm:
            return qm[name]
        q = p108["quantities"][name]
        if q["form"] == "contrast":
            v = {"M": q["M"] / c1, "half95": None if q.get("half95") is None else q["half95"] / c1, "unit": "W"}
        elif q["form"] == "ratio":
            v = {"M": m_of(q["a"])["M"] / m_of(q["b"])["M"], "half95": None, "unit": "ratio"}
        else:
            k = q.get("k", 1.0)
            v = {"M": m_of(q["a"])["M"] - k * m_of(q["b"])["M"], "half95": None,
                 "unit": m_of(q["a"])["unit"]}
        qm[name] = v
        return v

    for n in p108["quantities"]:
        m_of(n)
    step_ref = {t: round(Q108[f"{t}.step"]["mean"] * scale[t], 4) for t in ("fp32", "fp16")}
    tie = {}
    for cell, v in p108["session_tie"]["cells"].items():
        d = e78["items"][cell]["D"]
        tie[cell] = {"ref_w": round(d["mean"], 4), "band_w": v["band_w"], "ci95_w": round(d["ci95"], 4),
                     "e108_card1_ref_w": v["ref_w"]}

    # --- the cross-card rules ---
    rng = random.Random("E122|power")
    xr = []
    for name in X_W + X_SHARE + list(X_OTHER):
        q = Q108[name]
        pp = list(q["per_pass"].values())
        m = sum(pp) / len(pp)
        sd = math.sqrt(sum((x - m) ** 2 for x in pp) / (len(pp) - 1))
        if name in X_W:
            s, w, unit = scale[qtype(name)], W_W, "W"
        elif name in X_SHARE:
            s, w, unit = 1.0, W_SHARE, "ratio"
        else:
            s, w, unit = 1.0, X_OTHER[name], "ratio"
        power = {}
        for n in (2, 3, 4):
            for delta in ((0.0, 0.5, 1.0, 1.5) if unit == "W" else (0.0, round(w / 2, 3), w, round(1.5 * w, 3))):
                power[f"n{n}_delta{delta}"] = sim_x(q["mean"], q["ci95"], s, sd, w, delta, n, rng)
        xr.append({"id": f"X-{name}", "of": name, "unit": unit, "scale": s,
                   "e108": {"mean": round(q["mean"], 4), "ci95": round(q["ci95"], 4), "n": q["n"],
                            "per_pass_sd": round(sd, 4)},
                   "predicted": round(s * q["mean"], 4), "w": w, "power_pass_fail_inconclusive": power})
    agg = {}
    for n in (2, 3, 4):
        k = f"n{n}_delta0.0"
        P = [x["power_pass_fail_inconclusive"][k] for x in xr]
        rng2 = random.Random(f"E122|agg|{n}")
        ok = badn = 0
        N = 20000
        for _ in range(N):
            npass = nfail = 0
            for (pp_, pf_, _pi) in P:
                u = rng2.random()
                if u < pp_:
                    npass += 1
                elif u < pp_ + pf_:
                    nfail += 1
            if nfail == 0 and npass >= len(xr) // 2:
                ok += 1
            elif nfail >= 3:
                badn += 1
        agg[f"n{n}"] = {"P_aggregate_PASS": round(ok / N, 3), "P_aggregate_FAIL": round(badn / N, 3)}

    reg = {
        "experiment": "E122",
        "registration": "tools/claims-v3/e122/E122.md",
        "registered": "2026-11-01",
        "answers": "the kinds page's section 11 item 5, 'Where a random sign's ~5 W goes' "
                   "(https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): E108's location "
                   "and like for like, on one card, replicated on a second",
        "card": {"name": "aifoundry3", "device": 0, "clock_mhz": 600, "mv_expected": round(e78["v_mean"] * 1000, 1),
                 "config_expected": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600},
                 "lock": "/run/lock/etsoc-shire0.lock", "V3_DEVICE": None},
        "inputs_frozen": {k: {"path": v[0], "commit": v[1], "sha256": v[2]} for k, v in SOURCES.items()},
        "harness": {
            "card_code_unchanged_sha256": {r: sha(r) for r in CARD_CODE},
            "desk_code_unchanged_sha256": {r: sha(r) for r in DESK_CODE},
            "e122_files_sha256": {r: sha(r) for r in E122_FILES if os.path.exists(os.path.join(ROOT, r))},
            "readback_host": READBACK_HOST,
            "order": "e108_common.pass_order unchanged with this card's name: Random('E108|aifoundry3|<pass>'), the tie, "
                     "three segments of E78's six anchors and a third of E108's 23 tiles and E78's two ones, the tie; "
                     "two burn-ins",
        },
        "plan": {"smoke": 12201, "readback": 12202, "dry": 12200, "passes_planned": [12210, 12211, 12212, 12213],
                 "runs_per_pass": p108["plan"]["runs_per_pass"],
                 "min_kept_passes_scored": p108["plan"]["min_kept_passes_scored"],
                 "min_tile_passes": p108["plan"]["min_tile_passes"],
                 "readback_reads": sum(len(v) for v in p108["rules"]["E108-R1"]["reads"].values())},
        "primary": {"leak_w_per_c": 0.1994, "dips": "removed (E82 A2's definition, reduce_e108.py's primary)",
                    "reduction": "tools/claims-v3/signloc/reduce_e108.py unchanged (reduce_e78.py with E108's items); on "
                                 "aifoundry3 its card-1 config substitution never fires (the card reads 0/65, which E78's "
                                 "gate accepts as it stands); --leak 0.1994, E78's own fit on this card (E108 froze its "
                                 "card's own fit, 0.2414, the same way)",
                    "arms": {"dips_kept": ["--keep-dips", "--leak", "0.1994", "--no-refit"],
                             "gates_off": ["--gates-off", "--leak", "0.1994", "--no-refit"],
                             "auto": ["--leak", "auto", "--no-refit"],
                             "leak0.2414": ["--leak", "0.2414", "--no-refit"],
                             "leak0.3803": ["--leak", "0.3803", "--no-refit"],
                             "leak0.545": ["--leak", "0.545", "--no-refit"],
                             "leak0": ["--leak", "0", "--no-refit"]}},
        "substitutions": {
            "rules.E108-R2.e106_w": {"value": step_ref,
                                     "what": "the step on a second card: signs - ones in each format against E108's own "
                                             "step on card 1 times E82's card scale (score_e108.py reads the key "
                                             "'e106_w'; the values are these)",
                                     "e108_card1_step": {t: round(Q108[f'{t}.step']['mean'], 4) for t in ("fp32", "fp16")},
                                     "band_w": p108["rules"]["E108-R2"]["band_w"]},
            "session_tie.cells": tie,
            "session_tie.reference": SOURCES["e78_reduction"][0] + " > items > <cell> > D (aifoundry3, 31 Oct, E78's "
                                                                   "primary: dips kept, leakage auto 0.1994)",
            "tiles.pred": tiles,
            "quantities.M": qm,
            "model.card_scale_removed": c1,
        },
        "e108_verdicts": {r: v["verdict"] for r, v in prim["rules"].items()},
        "expect": EXPECT,
        "card_scale": {"per_type": scale, "source": SOURCES["e82_scored"][0] + " > cross_card > primary > x3 > "
                                                     "per_type_median (D on aifoundry3 over D on card 1, 32 kinds >= 5 W)",
                       "median": e82["cross_card"]["primary"]["x3"]["median_ratio"],
                       "iqr": e82["cross_card"]["primary"]["x3"]["iqr"]},
        "cross_card": {"rules": xr, "w": {"W": W_W, "share": W_SHARE, **X_OTHER},
                       "verdict": "per rule: d = Q122 - s*Q108, h = sqrt(h122^2 + (s*h108)^2); PASS if |d| + h <= w, "
                                  "FAIL if |d| - h > w, else INCONCLUSIVE; UNRESOLVED if Q122 has fewer than 2 passes",
                       "aggregate": f"PASS if no X rule FAILs and at least {len(xr) // 2} of {len(xr)} PASS; FAIL if 3 "
                                    "or more FAIL; else INCONCLUSIVE",
                       "aggregate_min_pass": len(xr) // 2,
                       "aggregate_power_true_delta0": agg},
        "tiles_e108": {n: {"D_w": round(v["D"], 4), "ci95_w": None if v["ci95"] is None else round(v["ci95"], 4),
                           "scaled_w": round(v["D"] * scale["fp16" if n.startswith("fp16.") else "fp32"], 4)}
                       for n, v in prim["table"].items()},
        "budget": {"card_minutes": 40, "anchor": "the claim edit's time (E122_T0)", "session_budget_s": 2400,
                   "reserve_s": 240, "first_pass_estimate_s": 450, "gap_s": 15,
                   "deadline": "2026-11-01 23:15 PST", "claim_hold": "for 1 h"},
    }
    return reg


def main():
    reg = build()
    txt = json.dumps(reg, indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        old = json.loads(open(OUT).read())
        new = json.loads(txt)
        for k in ("harness",):
            old.pop(k, None), new.pop(k, None)
        print("predictions-e122.json reproduces (harness hashes aside):", old == new)
        sys.exit(0 if old == new else 1)
    open(OUT, "w").write(txt)
    print("wrote", OUT, hashlib.sha256(txt.encode()).hexdigest())
    for x in reg["cross_card"]["rules"]:
        pw = x["power_pass_fail_inconclusive"]
        print(f"{x['id']:22s} e108 {x['e108']['mean']:+8.3f} ± {x['e108']['ci95']:.3f} sd {x['e108']['per_pass_sd']:.3f} "
              f"pred {x['predicted']:+8.3f} w {x['w']}  n4 d0 {pw['n4_delta0.0']}")
    print("aggregate:", reg["cross_card"]["aggregate_power_true_delta0"])
    print("R2 refs:", reg["substitutions"]["rules.E108-R2.e106_w"]["value"])
    print("tie:", {k: v["ref_w"] for k, v in reg["substitutions"]["session_tie.cells"].items()})


if __name__ == "__main__":
    main()
