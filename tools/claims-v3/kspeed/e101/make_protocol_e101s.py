#!/usr/bin/env python3
"""E101, session 2 (Q132): writes protocol.json (the session's blocks), protocol-dry.json (the same order with short runs, for the dry run of the queue and the reducer) and start-modes.json, by the rule E101.md froze, from session 1's
measured watts. No card.

    python3 make_protocol_e101s.py --e101 <session 1's e101.json | the frozen predictions: --from-frozen> > protocol.txt

THE RULE (E101.md, "Why the plan depends on session 1"). A cell's c on aifoundry2 is c_zeros(t) + (S - S_res(t, zeros)) / xfer, its board power at 800 MHz P_800 = B_800 + 1.905 c, with S session 1's measured S.
  P_800 <= 88 W: a COOL BURST (die <= 55 C) and a COOL SUSTAINED start (die <= 57 C), E80's.
  P_800 >  88 W: a WARM BURST (E64's `hot` start at 60 C, resident random fp32 launches of 2 s, so the power loop has taken the clock off 800 MHz when the work starts), labelled, and a HOT SUSTAINED start (66 C, resident random fp32
  launches of 8 s, in the thermal loop).
The session still ends on 97 W x 3 samples or 85 C (run_hpl.py), whatever this file says.

THE BLOCKS. SMOKE: the idle card with no launch for the rest reading, then 2 s of gemm1 fp32 zeros, mm16 int8 zeros, gemm1 fp16 zeros, each below every limit. BURST: 33 cells x 2 passes, each pass shuffled (order_seed 101), the cells above the limit in the last third
of their pass. SUS: nine 8 s processes, about 76 s, in the fixed order below, so a cut by the slot takes its tail:
  G1  gemm1 zeros and random in each format        G2  gemm1 ones, sparse50, real in each format        G3  mm16 zeros and random in each format
  G4  resident fp32 random and int8 full           G5  replicates: gemm1 fp32 random, fp32 zeros, int8 full, int8 zeros        G6  mm16 ones in each format, if the clock allows
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "kinds"))
import e78_common as ec  # noqa: E402
import e101_common as e101  # noqa: E402

TYPES = ("fp32", "fp16", "int8")
LIMIT_W = 88.0
FIVE = ("zeros", "ones", "random", "sparse50", "real")
FOUR = ("zeros", "ones", "random", "sparse50")
ORDER_SEED = 101


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e101", help="session 1's reduction")
    ap.add_argument("--from-frozen", action="store_true", help="the dry run before session 1: the frozen S")
    ap.add_argument("--slot-note", default="")
    a = ap.parse_args()
    reg = json.load(open(os.path.join(HERE, "..", "..", "kinds", "predictions-e101.json")))
    REL = reg["clock"]["relation"]
    B800, S800 = REL["B_registered_w"]["800"], REL["s_f"]["800"]
    xfer, cz = REL["xfer"], REL["c_zeros_w"]
    items = {it["name"]: it for it in e101.load_items()}
    S1 = None if a.from_frozen else json.load(open(a.e101))["items"]

    def res_name(t, k):
        return f"{t}.{e101.kind_name(t, k)}"

    def arm_name(arm, t, k):
        return f"{arm}.{t}.{e101.kind_name(t, k)}"

    def measured(n, t, k, arm):
        if S1 is not None and n in S1 and S1[n]["S"]["mean"] is not None:
            return S1[n]["S"]["mean"], "session 1"
        if arm == "res":
            return reg["S_res"][t][k][0], "E78"
        return reg["cells"][n]["S_w"], "frozen, session 1 has no value"

    def zero_s(t):
        n = res_name(t, "zeros")
        if S1 is not None and n in S1 and S1[n]["S"]["mean"] is not None:
            return S1[n]["S"]["mean"]
        return reg["S_res"][t]["zeros"][0]

    modes = {}

    def cell(arm, t, k):
        if arm == "res":
            n = res_name(t, k)
            values = "file:" + items[n]["tile"]
        else:
            n = arm_name(arm, t, k)
            values = items[n]["values"]
        s, src = measured(n, t, k, arm)
        c = cz[t] + (s - zero_s(t)) / xfer
        p800 = B800 + S800 * c
        high = p800 > LIMIT_W
        label = f"{arm}-{t}-{e101.kind_name(t, k)}"
        modes[label] = {"S_w": round(s, 2), "source": src, "c_w": round(c, 2), "p800_w": round(p800, 1), "mode": "warm/hot" if high else "cool"}
        return {"type": t, "values": values, "label": label}, high, c

    dry = {}
    burst_low, burst_high = [], []
    for arm, kinds in (("gemm1", FIVE), ("mm16", FOUR), ("res", ("zeros", "random"))):
        for t in TYPES:
            for k in kinds:
                r, high, c = cell(arm, t, k)
                dry[r["values"]] = round(c, 3)
                if high:
                    r = dict(r, start={"mode": "hot", "hot_c": 60, "heat_s": 2, "max_heats": 12})
                    burst_high.append(r)
                else:
                    burst_low.append(r)
    rng = random.Random(ORDER_SEED)
    burst_runs = []
    for _pass in (1, 2):         # each pass shuffled, the cells above the limit last in it
        rng.shuffle(burst_low)
        rng.shuffle(burst_high)
        burst_runs += [dict(x) for x in burst_low] + [dict(x) for x in burst_high]

    def sus(arm, t, k, suffix=""):
        r, high, c = cell(arm, t, k)
        r = dict(r, label=r["label"] + suffix)
        if high:
            r["start"] = {"mode": "hot", "hot_c": 66, "heat_s": 8, "max_heats": 8}
        return r
    groups = []
    G1 = [sus("gemm1", t, k) for t in TYPES for k in ("zeros", "random")]
    G2 = [sus("gemm1", t, k) for t in TYPES for k in ("ones", "sparse50", "real")]
    G3 = [sus("mm16", t, k) for t in TYPES for k in ("zeros", "random")]
    G4 = [sus("res", "fp32", "random"), sus("res", "int8", "random")]
    G5 = [sus("gemm1", "fp32", "random", "-rep2"), sus("gemm1", "fp32", "zeros", "-rep2"), sus("gemm1", "int8", "random", "-rep2"), sus("gemm1", "int8", "zeros", "-rep2")]
    G6 = [sus("mm16", t, "ones") for t in TYPES]
    for g in (G1, G2, G3, G4, G5):
        rng.shuffle(g)
    order = []
    for name, g in (("G1", G1), ("G2", G2), ("G3", G3), ("G4", G4), ("G5", G5), ("G6", G6)):
        for x in g:
            order.append(dict(x, group=name))
    smoke = []
    for arm, t, k in (("gemm1", "fp32", "zeros"), ("mm16", "int8", "zeros"), ("gemm1", "fp16", "zeros")):
        r, _, _ = cell(arm, t, k)
        smoke.append(r)
    # the cycles the smoke must read, from session 1 (kept to 2%), or E37's for mm16
    cyc = {}
    for r in smoke:
        arm, t, kk = r["label"].split("-", 2)
        n = f"{arm}.{t}.{kk}"
        cyc[r["label"]] = S1[n]["cycles_per_op"] if S1 is not None and n in S1 else reg["inputs"]["cpo"][arm][t]

    def proto(burst, susd, smoke_tail, cap, note):
        return {"experiment": "E101", "session": 2, "request": "Q132", "card": "aifoundry2", "order_seed": ORDER_SEED, "note": note,
                "tools": {"heater": "build/e101/host/sparsity_host", "kernel": "build/e101/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
                "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": "tools/claims-v3/kinds/predictions-e101.json",
                "sampler": {"every_ms": 100}, "safety": {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3}, "caps": {"max_card_min": cap},
                "smoke_cycles": cyc, "dry_c_w": dry, "limit_p800_w": LIMIT_W,
                "blocks": [
                    {"name": "SMOKE", "title": "the idle card with no launch (its last 60 s are the session's rest reading), then one 2 s launch of three cells below every limit (not analysed)",
                     "default": False, "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3,
                     "runs": [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": smoke_tail}] + smoke},
                    {"name": "BURST", "title": "one 6 s process from a die reading <= 55 C, the first block's cells; the cells above the limit from a warm start (make_protocol_e101s.py), run last in a pass",
                     "passes": 1, "shuffle": False, "start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}, "launch": burst["launch"], "tail_s": burst["tail_s"],
                     "runs": burst_runs},
                    {"name": "SUS", "title": "sustained: nine back-to-back 8 s processes (~76 s) from a die reading <= 57 C, or the hot start above the limit, in the order make_protocol_e101s.py fixed",
                     "passes": 1, "shuffle": False, "start": {"mode": "cool", "max_c": 57, "max_wait_s": 300}, "launch": susd["launch"], "tail_s": susd["tail_s"], "runs": order}]}
    src = "the frozen S (dry run before session 1)" if a.from_frozen else "session 1's measured S"
    note = f"E80's design on E101's streaming arms; nothing is set on the card; start modes by the rule of E101.md from {src}"
    full = proto({"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}, {"launch": {"seconds": 8, "budget": 9.5, "processes": 9}, "tail_s": 6}, 75, 72, note)
    dryp = proto({"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5}, {"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5}, 3, 72, "THE DRY SHAPE, toy card only: the same order with short runs, for the queue and the reducer")
    json.dump(full, open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(dryp, open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    json.dump({"limit_p800_w": LIMIT_W, "source": src, "modes": modes}, open(os.path.join(HERE, "start-modes.json"), "w"), indent=1)
    print(f"source: {src}; cool burst cells {len(burst_low)}, warm burst cells {len(burst_high)}, x 2 passes; sustained {len(order)} runs")
    for k in sorted(modes, key=lambda x: -modes[x]["p800_w"]):
        print(f"  {k:26s} S {modes[k]['S_w']:6.2f} W ({modes[k]['source']}), c {modes[k]['c_w']:6.2f} W, P800 {modes[k]['p800_w']:6.1f} W: {modes[k]['mode']}")
    print("sustained order:", [x["label"] for x in order])


if __name__ == "__main__":
    main()
