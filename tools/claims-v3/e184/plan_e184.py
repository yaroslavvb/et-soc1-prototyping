#!/usr/bin/env python3
"""E184's plan: every pass of both arms, item by item, in the order the card runs them (registration, desk only).

    /usr/bin/python3 -B tools/claims-v3/e184/plan_e184.py > tools/claims-v3/e184/plan-e184.json
    /usr/bin/python3 -B tools/claims-v3/e184/plan_e184.py --check tools/claims-v3/e184/plan-e184.json   # re-made byte for byte

Arm S, aifoundry3 card 0 at 600 MHz (the staircase): fadd.ps on both harts of every minion of the active shires, a zeros base, and
n minions switched to random [0.5, 2) operands by a host-only change (the operand image). One item is one quad: one host process
under timeout 10, S + A B B A or B A A B (e184_common.py). Arm B, aifoundry1 card 1 at 600 MHz (the SRAM-rail test): stock enercat
configurations as bursts and holds, the statistics reset only in pass 18441.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e184_common as c  # noqa: E402

QUAD_S = 8.3          # one quad's wall time: 18 launches of 0.4 s, the device's open and close, the runner's 0.3 s gap and checks

# ---- arm S -------------------------------------------------------------------------------------------------------------------------
# The ladder: nine steps in a geometric series from 3 minions (about 0.025 W, under one IMON code of 0.033 W) to 121 (about +1.0 W
# at E180's 8.26 mW a minion), round(3 x (121/3)^(k/8)), k = 0..8, and the null level n = 0. "Small" are the steps under 0.2 W.
L_LEVELS = [0] + [int(round(3 * (121 / 3.0) ** (k / 8.0))) for k in range(9)]
L_SMALL, L_LARGE = [n for n in L_LEVELS[1:] if n * 0.008256 < 0.2], [n for n in L_LEVELS[1:] if n * 0.008256 >= 0.2]
L_QUADS = dict([(0, 12)] + [(n, 16) for n in L_SMALL] + [(n, 4) for n in L_LARGE])     # per visit
# The operating point: steps of 0.5, 1, 2 and 3 times E178's int8 pair as measured (+0.0532 W, E178-H-int8) in minions at
# 8.256 mW a minion, round(k x 6.44); the ladder's top step (121) as its large step; and its own null level.
P_SMALL = [int(round(k * 0.0532 / 0.008256)) for k in (0.5, 1, 2, 3)]
P_LARGE = [121]
P_LEVELS = [0] + P_SMALL + P_LARGE
P_QUADS = dict([(0, 8)] + [(n, 16) for n in P_SMALL] + [(121, 8)])
C_LEVELS = list(range(0, 289, 12))     # 25 scan levels, 12 minions apart
C_REF = 144
C_QUADS = 6                            # per level per sweep
CAL_MASKS = [16, 24]
OP_TARGET_RULE = "inputs-e184.json > e178_op.target_board_w (E178's int8 4s and 5s board level)"
SCAN_START_W = 32.4                    # the scan's zeros base: 0.38 W under the carry band's low end (11.7 V)
M_OP_RANGE, M_S_RANGE = (10, 24), (16, 30)


def quads_for(part, mask, levels, per, ref=0, visit=0, seq0=0):
    """Items for one visit or sweep: each level's quads consecutively, orientation alternating, the first one ABBA when
    (visit + level index) is even."""
    items, k = [], seq0
    for li, n in enumerate(levels):
        q = per[n] if isinstance(per, dict) else per
        for j in range(q):
            orient = "ABBA" if (visit + li + j) % 2 == 0 else "BAAB"
            items.append({"seq": k, "part": part, "mask_m": mask, "n": n, "ref": ref, "orient": orient,
                          "img_a": c.image_name(mask, ref) if isinstance(mask, int) else "m{M}_n%03d.bin" % ref,
                          "img_b": c.image_name(mask, n) if isinstance(mask, int) else "m{M}_n%03d.bin" % n})
            k += 1
    return items


def arm_s():
    passes = []
    passes.append({"pass": 18402, "what": "the stop-path test: no launch; the board and die stops must each fire before an item and in "
                   "the in-run watcher, on live samples", "items": [], "est_s": 30})
    smoke = [{"seq": 0, "part": "smoke", "mask_m": 32, "n": 0, "ref": 0, "orient": "ABBA"},
             {"seq": 1, "part": "smoke", "mask_m": 32, "n": 121, "ref": 0, "orient": "BAAB"},
             {"seq": 2, "part": "smoke", "mask_m": 32, "n": 1024, "ref": 0, "orient": "ABBA"},
             {"seq": 3, "part": "smoke", "mask_m": 16, "n": 19, "ref": 0, "orient": "BAAB"}]
    for it in smoke:
        it["img_a"], it["img_b"] = c.image_name(it["mask_m"], it["ref"]), c.image_name(it["mask_m"], it["n"])
    passes.append({"pass": 18401, "what": "the smoke: four quads (the null, n = 121, every minion switched, 16 shires n = 19)",
                   "items": smoke, "est_s": round(3 + 4 * QUAD_S)})
    orders = [("up", L_LEVELS), ("down", L_LEVELS[::-1]), ("up", L_LEVELS)]
    for v, (dirn, lv) in enumerate(orders):
        its = quads_for("L", 32, lv, L_QUADS, 0, v)
        passes.append({"pass": 18410 + v, "what": "the main ladder at 32 shires, visit %d (%s), the null level n = 0 inside it" % (v + 1, dirn),
                       "items": its, "est_s": round(10 + len(its) * QUAD_S)})
    cal = [{"seq": i, "part": "Cal", "mask_m": m, "n": 0, "ref": 0, "orient": "ABBA" if i % 2 == 0 else "BAAB",
            "img_a": c.image_name(m, 0), "img_b": c.image_name(m, 0)} for i, m in enumerate(CAL_MASKS)]
    passes.append({"pass": 18413, "what": "the calibration: one null quad at 16 and at 24 shires; it writes cal.json (M_op, M_s)",
                   "items": cal, "est_s": round(10 + len(cal) * QUAD_S)})
    porders = [("up", P_LEVELS), ("down", P_LEVELS[::-1]), ("up", P_LEVELS)]
    for v, (dirn, lv) in enumerate(porders):
        its = quads_for("P", "M_op", lv, P_QUADS, 0, v)
        passes.append({"pass": 18414 + v, "what": "the int8 pair's operating point at M_op shires (cal.json), visit %d (%s)" % (v + 1, dirn),
                       "items": its, "est_s": round(10 + len(its) * QUAD_S)})
    for v, (dirn, lv) in enumerate((("up", C_LEVELS), ("down", C_LEVELS[::-1]))):
        its = quads_for("C", "M_s", lv, C_QUADS, C_REF, v)
        passes.append({"pass": 18417 + v, "what": "the interleaved scan across the IMON reading's 1024 carry at M_s shires (cal.json), "
                       "sweep %d (%s), against the fixed reference n = %d" % (v + 1, dirn, C_REF), "items": its,
                       "est_s": round(10 + len(its) * QUAD_S)})
    images = set()
    for p in passes:
        for it in p["items"]:
            if isinstance(it["mask_m"], int):
                images.add((it["mask_m"], it["n"]))
                images.add((it["mask_m"], it["ref"]))
    return passes, sorted(images)


# ---- arm B -------------------------------------------------------------------------------------------------------------------------
B1_CFGS = {  # E46's SRAM-dominated set, three with no scratchpad prefill (workloads/enercat/run_catalogue.py's arguments)
    "tstore/scp/random": ["--pattern", "tstore", "--operands", "random", "--slice-bytes", "32K", "--scp"],
    "fswl.ps/random/h2": ["--pattern", "fswl.ps", "--operands", "random", "--harts", "2"],
    "flwl.ps/random/h2": ["--pattern", "flwl.ps", "--operands", "random", "--harts", "2"]}
B1_MASKS = [8, 16, 32]
HOLD_S, HOLD_PROC_S, B_GAP_S = 20.0, 6.4, 4.5
B3_CFGS = {  # E46's set (inputs-e184.json > catalogue.sram_set) less the twelve that need a scratchpad prefill
    "amoaddl.d/random/h2": ["--pattern", "amoaddl.d", "--operands", "random", "--harts", "2"],
    "amoaddl.d/zeros/h2": ["--pattern", "amoaddl.d", "--operands", "zeros", "--harts", "2"],
    "amoaddl.w/random/h2": ["--pattern", "amoaddl.w", "--operands", "random", "--harts", "2"],
    "amoaddl.w/zeros/h2": ["--pattern", "amoaddl.w", "--operands", "zeros", "--harts", "2"],
    "amomaxl.w/random/h2": ["--pattern", "amomaxl.w", "--operands", "random", "--harts", "2"],
    "amomaxl.w/zeros/h2": ["--pattern", "amomaxl.w", "--operands", "zeros", "--harts", "2"],
    "amoorl.w/random/h2": ["--pattern", "amoorl.w", "--operands", "random", "--harts", "2"],
    "amoorl.w/zeros/h2": ["--pattern", "amoorl.w", "--operands", "zeros", "--harts", "2"],
    "amoswapl.w/random/h2": ["--pattern", "amoswapl.w", "--operands", "random", "--harts", "2"],
    "amoswapl.w/zeros/h2": ["--pattern", "amoswapl.w", "--operands", "zeros", "--harts", "2"],
    "flwl.ps/random/h2": ["--pattern", "flwl.ps", "--operands", "random", "--harts", "2"],
    "fswl.ps/random/h2": ["--pattern", "fswl.ps", "--operands", "random", "--harts", "2"],
    "fswl.ps/zeros/h2": ["--pattern", "fswl.ps", "--operands", "zeros", "--harts", "2"],
    "tstore/scp/const": ["--pattern", "tstore", "--operands", "const", "--slice-bytes", "32K", "--scp"],
    "tstore/scp/random": ["--pattern", "tstore", "--operands", "random", "--slice-bytes", "32K", "--scp"],
    "tstore/scp/zeros": ["--pattern", "tstore", "--operands", "zeros", "--slice-bytes", "32K", "--scp"]}


def arm_b():
    r = random.Random(c.SEED_B)
    levels = [{"cfg": "idle", "mask_m": 0, "args": []}]
    for cfg, args in B1_CFGS.items():
        for m in B1_MASKS:
            levels.append({"cfg": cfg, "mask_m": m, "args": args + ["--shires", "0x%x" % c.mask_of(m)]})
    passes = [{"pass": 18432, "what": "the stop-path test: no launch", "items": [], "est_s": 30, "sampler": "plain"}]
    smoke = [{"seq": i, "kind": "burst", "cfg": k, "mask_m": 32, "args": v + ["--shires", "0xffffffff"], "burst_s": 2.0, "gap_s": 4.5}
             for i, (k, v) in enumerate(B1_CFGS.items())]
    passes.append({"pass": 18431, "what": "the smoke: each of B1's three configurations once, 2 s, on 32 shires", "items": smoke,
                   "est_s": 3 + 3 * 7, "sampler": "plain"})
    for pn, sampler in ((18440, "plain"), (18441, "reset1000")):
        lv = [dict(x) for x in levels]
        r.shuffle(lv)
        items = []
        for i, x in enumerate(lv):
            items.append({"seq": i, "kind": "hold", "cfg": x["cfg"], "mask_m": x["mask_m"], "args": x["args"], "hold_s": HOLD_S,
                          "proc_s": HOLD_PROC_S, "gap_s": B_GAP_S})
        passes.append({"pass": pn, "what": "B1, the SRAM rail's reset windows at three loads on three masks and idle, %s sampler" %
                       ("the plain" if sampler == "plain" else "the statistics-reset (--reset-ms 1000)"), "items": items,
                       "est_s": round(10 + len(items) * (HOLD_S + B_GAP_S + 1.5)), "sampler": sampler})
    b2 = []
    for i, bs in enumerate([2.0, 4.0, 2.0, 4.0, 2.0, 4.0]):
        b2.append({"seq": i, "kind": "burst", "cfg": "tstore/scp/random", "mask_m": 32,
                   "args": B1_CFGS["tstore/scp/random"] + ["--shires", "0xffffffff"], "burst_s": bs, "gap_s": 7.0})
    passes.append({"pass": 18442, "what": "B2, the SRAM rail's step response: square bursts of 2.0 and 4.0 s with 7 s of idle before each",
                   "items": b2, "est_s": round(10 + sum(x["burst_s"] + 7.0 + 0.6 for x in b2) + 7), "sampler": "plain"})
    for pn in (18443, 18444):
        ks = sorted(B3_CFGS)
        r.shuffle(ks)
        items = [{"seq": i, "kind": "burst", "cfg": k, "mask_m": 32, "args": B3_CFGS[k] + ["--shires", "0xffffffff"], "burst_s": 3.0,
                  "gap_s": 4.5} for i, k in enumerate(ks)]
        passes.append({"pass": pn, "what": "B3, the cross-card set: sixteen of E46's SRAM-dominated configurations, the catalogue's timing",
                       "items": items, "est_s": round(10 + len(items) * (3.0 + 4.5 + 0.6)), "sampler": "plain"})
    return passes


def build():
    s_passes, images = arm_s()
    b_passes = arm_b()
    s_est = sum(p["est_s"] for p in s_passes)
    b_est = sum(p["est_s"] for p in b_passes)
    return {
        "what": "E184's plan (plan_e184.py): arm S on aifoundry3 card 0, arm B on aifoundry1 card 1, every item in order",
        "design": {"quad_s": QUAD_S, "launch_s": c.LAUNCH_S, "window_cycles": c.WINDOW_CYCLES, "settle_launches": c.SETTLE_LAUNCHES,
                   "block_launches": c.BLOCK_LAUNCHES, "discard_s": c.DISCARD_S, "min_refreshes": c.MIN_REFRESHES,
                   "shire_order": c.shire_order(), "slot_order": c.slot_order(),
                   "L": {"levels": L_LEVELS, "small": L_SMALL, "large": L_LARGE, "quads_per_visit": L_QUADS, "visits": ["up", "down", "up"]},
                   "P": {"levels": P_LEVELS, "small": P_SMALL, "large": P_LARGE, "quads_per_visit": P_QUADS, "visits": ["up", "down", "up"],
                         "mask_rule": "M_op = round((T - a) / z) clipped to %s, T = %s; a, z the least-squares line through the "
                                      "calibration's base readings at 16 and 24 shires and the ladder's base at 32 (the A blocks of pass "
                                      "18412)" % (list(M_OP_RANGE), OP_TARGET_RULE)},
                   "C": {"levels": C_LEVELS, "ref": C_REF, "quads_per_level_per_sweep": C_QUADS, "sweeps": ["up", "down"],
                         "scan_start_w": SCAN_START_W,
                         "mask_rule": "M_s = round((%.1f - a) / z) clipped to %s, with the same a, z" % (SCAN_START_W, list(M_S_RANGE))},
                   "cal_masks": CAL_MASKS, "B1": {"cfgs": B1_CFGS, "masks": B1_MASKS, "hold_s": HOLD_S, "proc_s": HOLD_PROC_S},
                   "B3": {"cfgs": sorted(B3_CFGS)}},
        "arm_S": {"card": "aifoundry3", "passes": s_passes, "est_s": s_est, "images_fixed_mask": [list(x) for x in images],
                  "quads": sum(len(p["items"]) for p in s_passes)},
        "arm_B": {"card": "aifoundry1-c1", "passes": b_passes, "est_s": b_est},
    }


if __name__ == "__main__":
    txt = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        same = open(sys.argv[2]).read() == txt
        print("plan_e184 --check: %s" % ("IDENTICAL" if same else "DIFFERS"))
        sys.exit(0 if same else 1)
    sys.stdout.write(txt)
