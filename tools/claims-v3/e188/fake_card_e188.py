#!/usr/bin/env python3
"""E188 (Q165, the kit): synthetic E188 sessions in the box's layout, for the scorer's self-test (selftest_score_e188.py). No card. A port of
tools/claims-v3/e186/fake_card_e186.py (E186's kit) with E188's trains, kinds passes and worlds.

A train block p1881N gets what block_e188.sh and run_e188t.py write there:
  - train.jsonl (14 launch records a process: launches -1 to 12, each kind by the registered schedule, iters set so the work rate is the
    candidates' rate), marks.jsonl (a "train" mark a process), block.json (status ok), config_start.json and config_end.json;
  - the train's anchors as E78 runs: a0/ (fp32.zeros, then fp32.randn) and a1/ (reversed), each a runs.jsonl of 10 launches, a marks.jsonl
    run mark (E78's protocol: start_c 58.0, quiet 2.0 s, on protocol), configs.json (target 58, preheat 59, quiet 2.0) and the tiles dumped
    as E78's runner dumps them, so that E78's reduction (reduce_e78.py, unchanged) reads them as it reads a card's;
  - telemetry.jsonl.gz at 10 Hz for the whole block: the anchors' levels, then the train's processes, whose board_w inside a launch is a
    base plus the kind's truth plus noise refreshed every 155 ms (E182's fake's model), so a quad's sd is about sigma_q (noise-e182.json)
    at scale 1.
A kinds pass (FULL's 18820/18821 or the fallback's 18830-18834) becomes a reduction in E78's output form and a runs.csv in plan-e188.json's
order with each run's registered segment (the tie at -1 and 3). The smoke's train part (B05's two processes, its C log's host, tiles and C
records, the dumps) is written by --smoke. A check of C's output lists every launch with its verdict (PASS unless told otherwise).

Worlds: M12 (every kind at M12's frozen level), M10 (at M10's), POS-6 (M12 with the five one-bit B trains' held price moved linearly with
the bit's place by -1, -1/2, 0, +1/2, +1 times 0.006 W: power_e188.py's stated alternative), PAIR-NB (M12 with PAIR's adjacent kind 0.010 W
above its spaced one: a neighbour cost).

    python3 -B fake_card_e188.py <out dir> --world M12|M10|POS-6|PAIR-NB [--seed N] [--noise-scale X] [--short TRAIN:N] [--cfail TRAIN]
        [--no-anchors] [--full-passes N] [--passes N] [--smoke [--break-schedule]]
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
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e188_common as E  # noqa: E402

PROC_S, LAUNCH_S, GAP_S, CAL_S, SPAWN_S = 6.92, 0.4901, 0.003, 0.011, 0.193
REFRESH_MS, SAMPLE_MS = 155, 100
CPO = {"int8": 318.0, "fp32": 546.0, "fp16": 546.0}
ZLEVEL = {"int8": 25.7, "fp32": 26.0, "fp16": 25.9}            # the zeros' board level, W (any level: D is read against it)
# the random anchors' D, set so that the session's scale reads about 1 (s = 1 is the world the kinds' truths are made in): fp32.randn
# E182's committed D over its scale ratio there (24.839 / 1.0136, the self-test's A1); fp16.randn likewise from a first synthetic read
D_RANDOM = {"fp32.randn": 24.506, "fp16.randn": 21.882, "int8.full": 7.16}
D_ZEROS = {"fp16.zeros": 0.0, "int8.zeros": 0.0}


POS_SHAPE = {"B04": -1.0, "B05": -0.5, "B10": 0.0, "B19": 0.5, "B22": 1.0}


def truths(world):
    """each kind's level above fp32.zeros, by world, from E188's frozen kind levels (forecast-e188.json > kinds; a train's line is its two
    kinds' difference, checked equal for the seven trains)"""
    fc = json.load(open(os.path.join(HERE, "forecast-e188.json")))
    K = fc["kinds"]
    lv = {k: (K[k]["M10_w"] if world == "M10" else K[k]["M12_w"]) for k in E.E188_NAMES}
    if world == "POS-6":
        for tid, f in POS_SHAPE.items():
            lv[fc["trains"][tid]["first"]] += f * 0.006
    if world == "PAIR-NB":
        lv[fc["trains"]["PAIR"]["first"]] += 0.010
    lv["anchor_pi"] = lv["fp32.pi"]               # the tie reads the same words as the pi tile (the models read words)
    return lv


def anchor_runs(d, sub, items, block, t0, base, rng):
    """E78 runs of the given anchors into <d>/<sub>: returns (end time, windows [(t0, t1, level)])"""
    os.makedirs(os.path.join(d, sub, "tiles"), exist_ok=True)
    allit = {it["name"]: it for it in E.load_items()}
    recs, marks, windows = [], [], []
    tt = t0
    for pos, name in enumerate(items):
        it = allit[name]
        ty = it["type"]
        lvl = base + (0.0 if it["kind"] == "zeros" else D_RANDOM[name]) + rng.gauss(0, 0.01)
        nom = 600e6 * 1024 / CPO[ty]
        start = tt + 2000                          # the run's quiet after its approach
        s = start
        for n in range(-1, 10):
            dur = 0.011 if n < 0 else 0.47
            e = s + int(dur * 1000)
            iters = int(round(nom * dur * 0.996 / 1024))
            recs.append({"card": "aifoundry3", "block": block, "pos": pos, "segment": 0, "item": name, "type": ty, "attempt": 1,
                         "launch": n, "iters": iters, "minions": 1024, "cycles_per_op": CPO[ty], "t_start_ms": s, "t_end_ms": e,
                         "ok": True, "tensor_errors": 0, "ghz": 0.5995})
            if n >= 0:
                windows.append((s, e, lvl))
            s = e + 3
        marks.append({"kind": "run", "item": name, "block": block, "t_start_ms": start, "t_end_ms": s, "pos": pos, "segment": 0,
                      "attempt": 1, "rc": 0, "launches": 10, "start_c": 58.0, "start_hot_c": 59.0, "heats": 1, "wait_s": 2.0,
                      "quiet_s": 2.0, "prev_end_ms": tt, "on_protocol": True})
        open(os.path.join(d, sub, "tiles", f"{name}.b{block}.bin"), "wb").write(open(os.path.join(TOP, it["tile"]), "rb").read())
        tt = s + 500
    with open(os.path.join(d, sub, "runs.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, sub, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    json.dump({"card": "aifoundry3", "args": {"target": 58.0, "preheat": 59.0, "quiet_s": 2.0, "first_block": block, "card": "aifoundry3"},
               "items": [allit[n] for n in items], "experiment": "E78"}, open(os.path.join(d, sub, "configs.json"), "w"))
    return tt, windows


def write_train(d, t, lv, rng, sig, scale, nproc=None, t0=1800000000000, anchors=True):
    os.makedirs(d, exist_ok=True)
    ty = t["type"]
    base = ZLEVEL[ty]
    recs, marks, verdicts, windows = [], [], [], []
    n = t["processes"] if nproc is None else nproc
    lev = {"F": lv[t["first"]], "S": lv[t["second"]]}
    tt = t0
    if anchors:
        tt, w = anchor_runs(d, "a0", t["anchors_open"], t["block"], tt, base, rng)
        windows += w
    nom = 600e6 * 1024 / CPO[ty]
    for k in range(n):
        ori = t["orientations"][k]
        ps = tt
        tt += int(SPAWN_S * 1000)
        cs, ce = tt, tt + int(CAL_S * 1000)
        recs.append({"process": k, "orientation": ori, "launch": -1, "t_start_ms": cs, "t_end_ms": ce, "train_kind": ori[0], "ok": True,
                     "abba": ori, "cycles_per_op": CPO[ty], "ghz": 0.5995, "tensor_errors": 0, "iters": int(round(nom * CAL_S / 1024)),
                     "minions": 1024, "first": t["first"], "second": t["second"], "block": t["block"], "train": t["train"],
                     "train_values": "file:" + E.tile_path(t["first"] if ori[0] == "F" else t["second"])})
        tt = ce + 3
        for nn in range(13):
            kind = ori[0] if nn < 1 else ori[(nn - 1) % 4]
            s0, s1 = tt, tt + int(LAUNCH_S * 1000)
            recs.append({"process": k, "orientation": ori, "launch": nn, "t_start_ms": s0, "t_end_ms": s1, "train_kind": kind, "ok": True,
                         "abba": ori, "cycles_per_op": CPO[ty], "ghz": 0.5995, "tensor_errors": 0,
                         "iters": int(round(nom * LAUNCH_S * 0.997 / 1024)), "minions": 1024,
                         "first": t["first"], "second": t["second"], "block": t["block"], "train": t["train"],
                         "train_values": "file:" + E.tile_path(t["first"] if kind == "F" else t["second"])})
            windows.append((s0, s1, base + 2.0 + lev[kind], "train"))
            tt = s1 + int(GAP_S * 1000)
        pe = tt + 47
        marks.append({"kind": "train", "item": t["train"], "block": t["block"], "process": k, "orientation": ori, "t_start_ms": ps,
                      "t_end_ms": pe, "rc": 0, "launches": 14})
        tt = ps + int(PROC_S * 1000)
    if anchors:
        tt, w = anchor_runs(d, "a1", t["anchors_close"], t["block"], tt + 2000, base, rng)
        windows += w
    # the board: a refresh every 155 ms holding the level of the launch at the refresh (idle 23.5 W outside), sampled every 100 ms
    sd = sig * scale * (2 ** 0.5)
    windows.sort()
    samples, wi, cur, last_ref = [], 0, 23.5, None
    tm = t0 - 1000
    end = tt + 1000
    while tm < end:
        ref = tm - (tm % REFRESH_MS)
        if ref != last_ref:
            while wi < len(windows) and windows[wi][1] < ref:
                wi += 1
            inside = wi < len(windows) and windows[wi][0] <= ref <= windows[wi][1]
            if inside:
                w = windows[wi]
                cur = w[2] + (rng.gauss(0, sd) if len(w) > 3 else rng.gauss(0, 0.02))
            else:
                cur = 23.5 + rng.gauss(0, 0.02)
            last_ref = ref
        samples.append({"t_ms": tm, "board_w": round(cur, 3), "since_reset_ms": -1, "sp": {"minion_w": [round(cur * 0.6, 3), 0, 0]},
                        "mhz": {"minion": 600}, "die_mv": {"minion": 522.0}, "temp_c": {"minshire": [58.0, 50.0, 60.0]}})
        tm += SAMPLE_MS
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as f:
        for s in samples:
            f.write(json.dumps(s) + "\n")
    with open(os.path.join(d, "train.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    cfg = {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600, "minion_mv": 523}
    for nm in ("config_start", "config_end"):
        json.dump(cfg, open(os.path.join(d, nm + ".json"), "w"))
    open(os.path.join(d, "block.json"), "w").write(json.dumps({"exp": "e188", "pass": t["block"], "status": "ok"}, separators=(",", ":")) + "\n")
    for r in recs:
        verdicts.append({"t_start_ms": r["t_start_ms"], "t_end_ms": r["t_end_ms"], "verdict": "PASS"})
    for sub in ("a0", "a1"):
        for r in ([json.loads(x) for x in open(os.path.join(d, sub, "runs.jsonl"))] if os.path.exists(os.path.join(d, sub, "runs.jsonl")) else []):
            verdicts.append({"t_start_ms": r["t_start_ms"], "t_end_ms": r["t_end_ms"], "verdict": "PASS"})
    return verdicts


def write_kinds(out, lv, rng, passes, family):
    """kinds passes' reduction in E78's output form: plan-e188.json's order (FULL's 18820, 18821 or the fallback's 18830-...), each run of an
    E188 kind D = its truth + a session term (0.041 W a kind) + a read's noise (0.125 / sqrt 2 W), the tie at the pi tile's truth, the random
    anchors at their D; each row with its registered segment"""
    plan = json.load(open(os.path.join(HERE, "plan-e188.json")))
    rate = json.load(open(os.path.join(HERE, "forecast-e188.json")))["rate_fp32_per_s"]
    src = plan["kinds_passes"] if family == "full" else plan["fallback_passes"]
    pp = sorted(int(p) for p in src)[:passes]
    truth = dict(lv)
    g = {k: rng.gauss(0, 0.041) for k in truth}
    per, rows = {}, []
    for p in pp:
        order = E.order_by_rule(p)
        if [n for n, _ in order] != src[str(p)]:
            raise SystemExit(f"fake: pass {p}'s rule order differs from the plan")
        acc = {}
        for pos, (it, seg) in enumerate(order):
            if it in truth:
                Dv = truth[it] + g[it] + rng.gauss(0, 0.125 / (2 ** 0.5))
            elif it in D_RANDOM:
                Dv = D_RANDOM[it] + rng.gauss(0, 0.02)
            else:
                continue
            rows.append({"pass": p, "segment": seg, "item": it, "pos": pos, "D": Dv})
            acc.setdefault(it, []).append(Dv)
        per[str(p)] = {k: {"D": sum(v) / len(v)} for k, v in acc.items()}
    items = {k: {"rate": {"mean": rate}} for k in truth}
    for k in ("fp32.randn", "fp16.randn"):          # the float random anchors, for the session's scale (E182's route)
        items[k] = {"D": {"mean": D_RANDOM[k] + rng.gauss(0, 0.02)}, "rate": {"mean": rate}, "type": k.split(".")[0]}
    json.dump({"experiment": "E188", "passes": pp, "per_pass": per, "items": items}, open(os.path.join(out, "e188.json"), "w"))
    with open(os.path.join(out, "runs.csv"), "w") as f:
        f.write("pass,segment,item,pos,D\n")
        for r in rows:
            f.write(f"{r['pass']},{r['segment']},{r['item']},{r['pos']},{r['D']}\n")


def write_smoke(d, rng, sig, break_schedule=False):
    """the smoke's train part as block_e188.sh leaves it: <d>/train/ (B05's first two processes), the block's c-log.jsonl with the train
    host's host record, both tile sets and a C record for every launch, binaries.sha256 naming the train host, train.rc 0 and the dumps"""
    t = E.train_of_block(E.SMOKE_PASS)
    td = os.path.join(d, "train")
    write_train(td, t, {t["first"]: 0.2, t["second"]: 0.0}, rng, sig, 1.0, anchors=False)
    recs = [json.loads(x) for x in open(os.path.join(td, "train.jsonl"))]
    if break_schedule:
        recs[3]["train_kind"] = "F" if recs[3]["train_kind"] == "S" else "S"
        with open(os.path.join(td, "train.jsonl"), "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
    har = json.load(open(os.path.join(HERE, "harness-e188.json")))
    kern = har["box_binaries_sha256"]["build/sparsity/kernel/sparsity.elf"]
    host = "f" * 64
    open(os.path.join(d, "binaries.sha256"), "w").write(f"{host}  build/e188host/b/host/sparsity_host\n")
    open(os.path.join(d, "train.rc"), "w").write("0\n")
    os.makedirs(os.path.join(td, "tiles"), exist_ok=True)
    raws = {k: open(os.path.join(TOP, E.tile_path(t[w])), "rb").read() for k, w in (("F", "first"), ("S", "second"))}
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


def write_clog(d, t, recs, host, kern, swap_fnv_at=None):
    """a train block's C log as the C-logging train host writes it: a host record, both tile sets and a C record for every launch with the
    fnv of the tiles it ran (swap_fnv_at: one launch index whose C record carries the other kind's fnv, a fault for the pairing check)"""
    raws = {k: open(os.path.join(TOP, E.tile_path(t[w])), "rb").read() for k, w in (("F", "first"), ("S", "second"))}

    def fnv(b):
        h = 1469598103934665603
        for x in b:
            h ^= x
            h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
        return f"{h:016x}"
    fv = {k: fnv(v) for k, v in raws.items()}
    with open(os.path.join(d, "c-log.jsonl"), "w") as f:
        f.write(json.dumps({"ccheck": 1, "kind": "host", "host_sha256": host, "kernel_sha256": kern}) + "\n")
        for kk in ("F", "S"):
            f.write(json.dumps({"ccheck": 1, "kind": "tiles", "values": "file:" + E.tile_path(t["first" if kk == "F" else "second"]),
                                "fnv": fv[kk]}) + "\n")
        for i, r in enumerate(recs):
            k = r["train_kind"]
            if swap_fnv_at is not None and i == swap_fnv_at:
                k = "F" if k == "S" else "S"
            f.write(json.dumps({"ccheck": 1, "kind": "c", "t_start_ms": r["t_start_ms"], "t_end_ms": r["t_end_ms"], "ok": True,
                                "poison": True, "groups": [{"count": 1024}], "fnv": fv[k]}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--world", default="M12", choices=("M12", "M10", "POS-6", "PAIR-NB"))
    ap.add_argument("--seed", type=int, default=18890)
    ap.add_argument("--noise-scale", type=float, default=1.0)
    ap.add_argument("--short", default=None, help="TRAIN:N - that train runs only N processes")
    ap.add_argument("--cfail", default=None, help="TRAIN - one of its launches FAILs the check of C")
    ap.add_argument("--swap-fnv", default=None, help="TRAIN - one of its C records carries the other kind's tiles (a pairing fault)")
    ap.add_argument("--off-schedule", default=None, help="TRAIN - one launch's train_kind off the schedule, its tiles and C record with it")
    ap.add_argument("--no-anchors", action="store_true", help="the trains' anchor runs left out (the scale is read from the kinds passes)")
    ap.add_argument("--full-passes", type=int, default=2, help="FULL's kinds passes beside the trains (0, 1 or 2)")
    ap.add_argument("--passes", type=int, default=0, help="the fallback: N kinds passes and no train")
    ap.add_argument("--smoke", action="store_true", help="write only the smoke's train part, under <out>/p18801")
    ap.add_argument("--break-schedule", action="store_true", help="with --smoke: one launch's kind off the schedule")
    a = ap.parse_args()
    NZ = json.load(open(os.path.join(TOP, "tools", "claims-v3", "e182", "noise", "noise-e182.json")))
    if a.smoke:
        write_smoke(os.path.join(a.out, "p18801"), random.Random(a.seed), NZ["sigma_q_w"]["float"], a.break_schedule)
        print(f"wrote a synthetic smoke train part in {a.out}")
        return
    lv = truths(a.world)
    rng = random.Random(a.seed)
    raw = os.path.join(a.out, "raw", "e188")
    os.makedirs(a.out, exist_ok=True)
    allv = []
    har = json.load(open(os.path.join(HERE, "harness-e188.json")))
    kern = har["box_binaries_sha256"]["build/sparsity/kernel/sparsity.elf"]
    if a.passes:
        write_kinds(a.out, lv, rng, a.passes, "fallback")
    else:
        if a.full_passes:
            write_kinds(a.out, lv, rng, a.full_passes, "full")
        short = dict([a.short.split(":")]) if a.short else {}
        for i, (b, t) in enumerate(sorted(E.TRAINS.items())):
            sig = NZ["sigma_q_w"]["float"]
            nn = int(short[t["train"]]) if t["train"] in short else None
            d = os.path.join(raw, f"p{b}")
            v = write_train(d, t, lv, rng, sig, a.noise_scale, nn, t0=1800000000000 + i * 900000, anchors=not a.no_anchors)
            recs = [json.loads(x) for x in open(os.path.join(d, "train.jsonl"))]
            if a.off_schedule == t["train"]:
                r = recs[5]
                r["train_kind"] = "F" if r["train_kind"] == "S" else "S"
                r["train_values"] = "file:" + E.tile_path(t["first"] if r["train_kind"] == "F" else t["second"])
                with open(os.path.join(d, "train.jsonl"), "w") as f:
                    for x in recs:
                        f.write(json.dumps(x) + "\n")
            write_clog(d, t, recs, "f" * 64, kern, swap_fnv_at=5 if a.swap_fnv == t["train"] else None)
            if a.cfail == t["train"]:
                v[5]["verdict"] = "FAIL"
            allv += v
    json.dump({"summary": {"launches": len(allv)}, "launches": allv}, open(os.path.join(a.out, "ccheck-all.json"), "w"))
    print(f"wrote a synthetic E188 session ({a.world}) in {a.out}")


if __name__ == "__main__":
    main()
