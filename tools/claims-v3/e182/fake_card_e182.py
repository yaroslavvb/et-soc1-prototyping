#!/usr/bin/env python3
"""E182 (Q153, the kit): synthetic E182 sessions in the box's layout, for the scorer's self-test (selftest_score_e182.py). No card.

A train block p1821N gets what run_e182t.py and the block write: train.jsonl (14 launch records a process: launches -1 to 12, each kind by
the registered schedule), marks.jsonl (a "train" mark a process) and telemetry.jsonl.gz at 10 Hz, whose board_w is the idle level between
processes and, inside a launch, a base level plus the launch's kind's truth plus noise, refreshed every 155 ms (the SP's pass) so samples
repeat as the board's do. The noise is set so that a quad's sd is about sigma_q (noise-e182.json) at scale 1. A kinds pass becomes a reduction
in E78's output form (passes, per_pass[p][kind]["D"], items[kind]["rate"]) and a runs.csv (pass, segment, item, pos, D) in plan-e182.json's
order. A check of C's output lists every launch with its verdict (PASS unless told otherwise).

    python3 -B fake_card_e182.py <out dir> --world <name> [--seed N] [--noise-scale X] [--short TRAIN:N] [--cfail TRAIN] [--passes N]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e182_common as E  # noqa: E402

PROC_S, LAUNCH_S, GAP_S, CAL_S, SPAWN_S = 6.92, 0.4901, 0.003, 0.011, 0.193
REFRESH_MS, SAMPLE_MS = 155, 100


def truths(world, F):
    """each kind's level above its zeros, by world: 'E' (arm E's levels: B-ONLY at E's price), 'AB' (arm E's levels with the int8 B-side
    TenB price moved half onto A: T3 kept, T2 = 0), 'P' (P's levels)"""
    ks = F["kinds"]
    if world == "P":
        return {k: ks[k]["P_w"]["a3"] for k in ks}
    lv = {k: ks[k]["E_w"]["a3"] for k in ks}
    if world == "AB":
        bE = F["held_bit_split"]["E_a3"]["beta_B_w_per_bit"]
        for k, v in ks.items():
            if v["type"] == "int8":
                ha, hb = v["popcount_a_word"] / 4.0, v["popcount_b_word"] / 4.0
                lv[k] = lv[k] - bE * hb + (bE / 2) * (ha + hb)
    return lv


def write_train(d, t, lv, rng, sig, scale, nproc=None, t0=1800000000000):
    os.makedirs(d, exist_ok=True)
    base = {"int8": 29.0, "fp32": 35.0}[t["type"]]
    recs, marks, samples, verdicts = [], [], [], []
    n = t["processes"] if nproc is None else nproc
    lev = {"F": lv[t["first"]], "S": lv[t["second"]]}
    windows = []
    tt = t0
    for k in range(n):
        ori = t["orientations"][k]
        ps = tt
        tt += int(SPAWN_S * 1000)
        cs, ce = tt, tt + int(CAL_S * 1000)
        recs.append({"process": k, "orientation": ori, "launch": -1, "t_start_ms": cs, "t_end_ms": ce, "train_kind": ori[0], "ok": True,
                     "abba": ori, "cycles_per_op": 318.0 if t["type"] == "int8" else 546.0, "ghz": 0.5995, "tensor_errors": 0,
                     "first": t["first"], "second": t["second"], "block": t["block"], "train": t["train"],
                     "train_values": "file:" + E.tile_path(t["first"] if ori[0] == "F" else t["second"])})
        tt = ce + 3
        for nn in range(13):
            kind = ori[0] if nn < 1 else ori[(nn - 1) % 4]
            s0, s1 = tt, tt + int(LAUNCH_S * 1000)
            recs.append({"process": k, "orientation": ori, "launch": nn, "t_start_ms": s0, "t_end_ms": s1, "train_kind": kind, "ok": True,
                         "abba": ori, "cycles_per_op": 318.0 if t["type"] == "int8" else 546.0, "ghz": 0.5995, "tensor_errors": 0,
                         "first": t["first"], "second": t["second"], "block": t["block"], "train": t["train"],
                         "train_values": "file:" + E.tile_path(t["first"] if kind == "F" else t["second"])})
            windows.append((s0, s1, base + lev[kind]))
            tt = s1 + int(GAP_S * 1000)
        pe = tt + 47
        marks.append({"kind": "train", "item": t["train"], "block": t["block"], "process": k, "orientation": ori, "t_start_ms": ps,
                      "t_end_ms": pe, "rc": 0, "launches": 14})
        tt = ps + int(PROC_S * 1000)
    # the board: a refresh every 155 ms holding the level of the launch at the refresh (idle 23.5 W outside), sampled every 100 ms
    sd = sig * scale * (2 ** 0.5)       # a launch's window holds about two distinct refreshes, so its reading's sd is about sig
    wi = 0
    cur = 23.5
    last_ref = None
    t = t0 - 1000
    end = tt + 1000
    while t < end:
        ref = t - (t % REFRESH_MS)
        if ref != last_ref:
            while wi < len(windows) and windows[wi][1] < ref:
                wi += 1
            inside = wi < len(windows) and windows[wi][0] <= ref <= windows[wi][1]
            cur = (windows[wi][2] if inside else 23.5) + rng.gauss(0, sd)
            last_ref = ref
        samples.append({"t_ms": t, "board_w": round(cur, 2), "since_reset_ms": -1, "sp": {"minion_w": [round(cur * 0.6, 3), 0, 0]},
                        "temp_c": {"minshire": [58, 50, 60]}})
        t += SAMPLE_MS
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as f:
        for s in samples:
            f.write(json.dumps(s) + "\n")
    with open(os.path.join(d, "train.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    for r in recs:
        verdicts.append({"t_start_ms": r["t_start_ms"], "t_end_ms": r["t_end_ms"], "verdict": "PASS"})
    return verdicts


def write_kinds(out, lv, rng, passes, F):
    """a kinds pass's reduction in E78's output form: plan-e182.json's order (the tie, three segments of 22 runs, the tie), each run of an
    E182 kind D = its truth + a session term (0.041 W a kind) + a read's noise (0.125 / sqrt 2 W); a pass's D the mean of its runs"""
    ks = F["kinds"]
    plan = json.load(open(os.path.join(HERE, "plan-e182.json")))
    pp = [18220 + i for i in range(passes)]
    g = {k: rng.gauss(0, 0.041) for k in ks}
    per, rows = {}, []
    for p in pp:
        order = plan["kinds_passes"][str(p)]
        acc = {}
        for pos, it in enumerate(order):
            if it not in ks:
                continue
            D = lv[it] + g[it] + rng.gauss(0, 0.125 / (2 ** 0.5))
            rows.append({"pass": p, "segment": (pos - 1) // 22, "item": it, "pos": pos, "D": D})
            acc.setdefault(it, []).append(D)
        per[str(p)] = {k: {"D": sum(v) / len(v)} for k, v in acc.items()}
    items = {k: {"rate": {"mean": F["rate"][ks[k]["type"]]}} for k in ks}
    json.dump({"experiment": "E182", "passes": pp, "per_pass": per, "items": items}, open(os.path.join(out, "e182.json"), "w"))
    with open(os.path.join(out, "runs.csv"), "w") as f:
        f.write("pass,segment,item,pos,D\n")
        for r in rows:
            f.write(f"{r['pass']},{r['segment']},{r['item']},{r['pos']},{r['D']}\n")


def write_smoke(d, rng, sig, break_schedule=False):
    """the smoke's train part as block_e182.sh leaves it: <d>/train/ (T1's first two processes), the block's c-log.jsonl with the train
    host's host record, both tile sets and a C record for every launch, binaries.sha256 naming the train host, train.rc 0 and the dumps"""
    import hashlib
    t = E.train_of_block(E.SMOKE_PASS)
    td = os.path.join(d, "train")
    write_train(td, t, {t["first"]: 0.07, t["second"]: 0.0}, rng, sig, 1.0)
    recs = [json.loads(x) for x in open(os.path.join(td, "train.jsonl"))]
    if break_schedule:
        recs[3]["train_kind"] = "F" if recs[3]["train_kind"] == "S" else "S"
        with open(os.path.join(td, "train.jsonl"), "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
    har = json.load(open(os.path.join(HERE, "harness-e182.json")))
    kern = har["box_binaries_sha256"]["build/sparsity/kernel/sparsity.elf"]
    host = "f" * 64
    open(os.path.join(d, "binaries.sha256"), "w").write(f"{host}  build/e182host/b/host/sparsity_host\n")
    open(os.path.join(d, "train.rc"), "w").write("0\n")
    os.makedirs(os.path.join(td, "tiles"), exist_ok=True)
    raws = {k: open(os.path.join(E.TOP, E.tile_path(t[w])), "rb").read() for k, w in (("F", "first"), ("S", "second"))}
    open(os.path.join(td, "tiles", f"train.b{E.SMOKE_PASS}.bin"), "wb").write(raws["F"])
    open(os.path.join(td, "tiles", f"train.b{E.SMOKE_PASS}.bin.S"), "wb").write(raws["S"])

    def fnv(b):
        h = 1469598103934665603
        for x in b:
            h ^= x
            h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
        return f"{h:016x}"
    with open(os.path.join(d, "c-log.jsonl"), "w") as f:
        for k in range(2):
            f.write(json.dumps({"ccheck": 1, "kind": "host", "host_sha256": host, "kernel_sha256": kern}) + "\n")
            for kk in ("F", "S"):
                f.write(json.dumps({"ccheck": 1, "kind": "tiles", "values": "file:" + E.tile_path(t["first" if kk == "F" else "second"]),
                                    "fnv": fnv(raws[kk])}) + "\n")
            for r in recs:
                if r["process"] == k:
                    f.write(json.dumps({"ccheck": 1, "kind": "c", "t_start_ms": r["t_start_ms"], "t_end_ms": r["t_end_ms"], "ok": True,
                                        "poison": True, "groups": [{"count": 1024}], "fnv": fnv(raws[r["train_kind"]])}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--world", default="E", choices=("E", "AB", "P"))
    ap.add_argument("--seed", type=int, default=18290)
    ap.add_argument("--noise-scale", type=float, default=1.0)
    ap.add_argument("--short", default=None, help="TRAIN:N - that train runs only N processes")
    ap.add_argument("--cfail", default=None, help="TRAIN - one of its launches FAILs the check of C")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--smoke", action="store_true", help="write only the smoke's train part, under <out>/p18201")
    ap.add_argument("--break-schedule", action="store_true", help="with --smoke: one launch's kind off the schedule")
    a = ap.parse_args()
    if a.smoke:
        NZ = json.load(open(os.path.join(HERE, "noise", "noise-e182.json")))
        write_smoke(os.path.join(a.out, "p18201"), random.Random(a.seed), NZ["sigma_q_w"]["int8"], a.break_schedule)
        print(f"wrote a synthetic smoke train part in {a.out}")
        return
    F = json.load(open(os.path.join(HERE, "forecast-e182.json")))
    NZ = json.load(open(os.path.join(HERE, "noise", "noise-e182.json")))
    lv = truths(a.world, F)
    rng = random.Random(a.seed)
    raw = os.path.join(a.out, "raw", "e182")
    allv = []
    short = dict([a.short.split(":")]) if a.short else {}
    for b, t in sorted(E.TRAINS.items()):
        sig = NZ["sigma_q_w"]["int8" if t["type"] == "int8" else "float"]
        n = int(short[t["train"]]) if t["train"] in short else None
        v = write_train(os.path.join(raw, f"p{b}"), t, lv, rng, sig, a.noise_scale, n, t0=1800000000000 + (b - 18210) * 900000)
        if a.cfail == t["train"]:
            v[5]["verdict"] = "FAIL"
        allv += v
    write_kinds(a.out, lv, rng, a.passes, F)
    json.dump({"summary": {"launches": len(allv)}, "launches": allv}, open(os.path.join(a.out, "ccheck-all.json"), "w"))
    print(f"wrote a synthetic E182 session ({a.world}) in {a.out}")


if __name__ == "__main__":
    main()
