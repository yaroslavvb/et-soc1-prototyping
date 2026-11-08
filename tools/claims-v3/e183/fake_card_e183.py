#!/usr/bin/env python3
"""E183 (Q155, the kit): synthetic sessions in the box's layout, for the scorer's self-test (selftest_score_e183.py). Never a card.

    /usr/bin/python3 -B tools/claims-v3/e183/fake_card_e183.py <raw dir> [--b W] [--c W] [--sigma W] [--seed N] [--plan FULL|SHORT]
        [--cut T3:12] [--bad-launch T1:5] [--flip-orientation T2:7] [--override T6:0.08]

It writes <raw>/e183/p<block>/ for every train block of the plan as block_e183.sh and run_e183.py would leave them after gzip: configs.json
(the runner's: the anchors and the planned processes with their orientations), block.json (status ok), marks.jsonl, telemetry.jsonl.gz (10 Hz
samples with the fields analyze_catalogue.bursts_of and the reduction read), runs.jsonl.gz (the anchors' 8 launches each) and
train.jsonl.gz (13 launches a process, each launch's kind, image, orientation and number by the registered schedule).
THE TRUTH: a train's two kinds sit x = b dR + c dO apart (or --override); every launch of the train reads 35.5 W, plus x on its F launches,
plus a launch offset drawn N(0, sigma) (sigma_q by default: a quad's sd is then sigma), plus 0.002 W of sample jitter; the anchors read
35.5 W (zeros) and 44.0 W (random) over a 26.0 W idle; the die holds 55 C, the clock 600 MHz. The timing is the plan's: a 10 s lead, each
anchor after a 4.5 s gap, 6 s before the train, launches 0.4014 s apart, 0.3 s between processes, a 7.5 s tail.
--cut T:n keeps only that train's first n processes; --bad-launch T:k marks launch 5 of process k not ok; --flip-orientation T:k writes
process k's records with the other orientation. Deterministic: random.Random(seed). Standard library only.
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
import e183_common as E  # noqa: E402

IDLE, ZEROS, RANDOM, BASE = 26.0, 35.5, 44.0, 35.5
PERIOD, LAUNCH, GAP_PROC = 0.4014, 0.4004, 0.3
OPS = 4.59e11


def enercat_fields(operands):
    """an ENERCAT record's own fields, as the catalogue's host prints them for a 0.4 s launch of fadd.ps on both harts of 1,024 minions"""
    ops = OPS * LAUNCH
    return {"pattern": "fadd.ps", "unit": "instruction", "operands": operands, "harts": 2, "shires": 32, "participants": 2048,
            "shire_mask_used": "0xffffffff", "ops": ops, "bytes": 0, "cycles_max": 240000000, "cycles_mean": 240000000,
            "ops_per_s": OPS, "bytes_per_s": 0.0, "ops_per_cycle_per_hart": 0.3735, "scp": False, "slice_bytes": 262144,
            "minion_mask": "0x0", "stride": 64, "access_bytes": 64, "region": 262144, "jump_every": 0, "jump_bytes": 0,
            "hop_distance": 0, "hop_axis": "any", "mean_hops": 0.0, "targets": "", "target_map": ""}


def sample(t_ms, w):
    return {"t_ms": int(t_ms), "took_ms": 21, "since_reset_ms": -1, "board_w": round(w, 3),
            "sp": {"minion_w": [round(0.7 * w - 11, 3), 0, 0], "sram_w": [1.9, 0, 0], "noc_w": [2.1, 0, 0]},
            "temp_c": {"minshire": [55, 50, 60]}, "mhz": {"minion": 600}}


def write_block(d, t, processes, b, c, sigma, rng, opts):
    os.makedirs(d, exist_ok=True)
    x = opts["override"].get(t["train"], b * t["dR"] + c * t["dO"])
    segs = []          # (t0_ms, t1_ms, level) busy segments; everything else idles
    runs, train, marks = [], [], []
    t_ms = 1_800_000_000_000
    clock = t_ms + int(E.LEAD_S * 1000)

    def burst(kind, side, clock):
        clock += int(E.GAP_S * 1000)
        cfg = E.anchor_cfg(kind, t["block"], side)
        lvl = ZEROS if kind.endswith("zeros") else RANDOM
        t0 = clock
        for k in range(8):
            a0 = clock + int(k * PERIOD * 1000)
            runs.append({"host": "aifoundry3", "pass": t["block"], "cfg": cfg, "kind": kind, **enercat_fields(kind), "t_start_ms": a0,
                         "t_end_ms": a0 + int(LAUNCH * 1000), "ok": True, "wall_s": LAUNCH})
        t1 = clock + int(8 * PERIOD * 1000)
        segs.append((t0, t1, lvl, None))
        marks.append({"kind": "burst", "cfg": cfg, "item": kind, "t_start_ms": t0, "t_end_ms": t1, "rc": 0, "launches": 8})
        return t1 + 300

    for kind in t["anchors_open"]:
        clock = burst(kind, "open", clock)
    clock += int(E.POST_ANCHOR_GAP_S * 1000)
    for k, ori in processes:
        clock += int(GAP_PROC * 1000)
        rec_ori = ori
        if opts["flip"].get(t["train"]) == k:
            rec_ori = "FSSF" if ori == "SFFS" else "SFFS"
        sched = E.schedule(ori)
        p0 = clock
        for n in range(E.LAUNCHES):
            a0 = clock + int(n * PERIOD * 1000)
            kind = sched[n]
            lvl = BASE + (x if kind == "F" else 0.0) + rng.gauss(0, sigma)
            segs.append((a0, a0 + int(LAUNCH * 1000), None, lvl))
            img = E.image_rel(t["first"] if kind == "F" else t["second"])
            ok = not (opts["bad"].get(t["train"]) == k and n == 5)
            train.append({"host": "aifoundry3", "block": t["block"], "train": t["train"], "process": k, "orientation": rec_ori,
                          "first": t["first"], "second": t["second"], **enercat_fields("file:" + img), "t_start_ms": a0,
                          "t_end_ms": a0 + int(LAUNCH * 1000), "ok": ok, "wall_s": LAUNCH, "train_kind": kind,
                          "train_operands": "file:" + img, "abba": rec_ori, "launch": n})
        clock += int(E.LAUNCHES * PERIOD * 1000)
        marks.append({"kind": "train", "item": t["train"], "block": t["block"], "process": k, "orientation": ori, "t_start_ms": p0,
                      "t_end_ms": clock, "rc": 0, "launches": E.LAUNCHES})
    for kind in t["anchors_close"]:
        clock = burst(kind, "close", clock)
    end = clock + int((E.GAP_S + 3) * 1000)
    # the 10 Hz samples: a launch's own level inside it, an anchor burst's level inside it, idle elsewhere
    segs.sort(key=lambda s: s[0])
    tel, j = [], 0
    for tm in range(t_ms, end, 100):
        while j < len(segs) and segs[j][1] < tm:
            j += 1
        w = IDLE
        for s in segs[j:j + 3]:
            if s[0] <= tm <= s[1]:
                w = s[2] if s[2] is not None else s[3]
                break
        tel.append(sample(tm, w + rng.gauss(0, 0.002)))
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as f:
        for s in tel:
            f.write(json.dumps(s) + "\n")
    with gzip.open(os.path.join(d, "runs.jsonl.gz"), "wt") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")
    with gzip.open(os.path.join(d, "train.jsonl.gz"), "wt") as f:
        for r in train:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    json.dump({"host": "aifoundry3", "pass": t["block"], "smoke": False, "train": t["train"], "lead_s": E.LEAD_S, "gap_s": E.GAP_S,
               "stop_w": 65.0, "stop_c": 70.0, "host_bin": E.HOST_BIN,
               "cfgs": [{"cfg": E.anchor_cfg(kd, t["block"], sd), "kind": kd, "args": E.anchor_args(kd), "burst_s": E.BURST_S}
                        for sd, ks in (("open", t["anchors_open"]), ("close", t["anchors_close"])) for kd in ks],
               "processes": [{"process": k, "orientation": o} for k, o in processes]}, open(os.path.join(d, "configs.json"), "w"), indent=1)
    json.dump({"exp": "e183", "pass": t["block"], "card": "aifoundry3", "status": "ok", "note": "synthetic (fake_card_e183.py)"},
              open(os.path.join(d, "block.json"), "w"))
    json.dump({"pass": t["block"], "exp": "e183", "processes_cap": None}, open(os.path.join(d, "pass.json"), "w"))


def parse_kv(v, cast):
    out = {}
    for item in v or []:
        k, val = item.split(":")
        out[k] = cast(val)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--b", type=float, default=0.0)
    ap.add_argument("--c", type=float, default=0.0)
    ap.add_argument("--sigma", type=float, default=None)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--plan", default="FULL")
    ap.add_argument("--cut", action="append")
    ap.add_argument("--bad-launch", action="append")
    ap.add_argument("--flip-orientation", action="append")
    ap.add_argument("--override", action="append")
    a = ap.parse_args()
    plan = E.plan()
    sigma = plan["sigma_q_w"] if a.sigma is None else a.sigma
    opts = {"cut": parse_kv(a.cut, int), "bad": parse_kv(a.bad_launch, int), "flip": parse_kv(a.flip_orientation, int),
            "override": parse_kv(a.override, float)}
    rng = random.Random(a.seed)
    keep = set(plan["plans"][a.plan]["trains"])
    for t in plan["trains"]:
        if t["train"] not in keep:
            continue
        n = opts["cut"].get(t["train"], t["processes"])
        procs = list(enumerate(t["orientations"][:n]))
        write_block(os.path.join(a.raw, "e183", f"p{t['block']}"), t, procs, a.b, a.c, sigma, rng, opts)
    print(f"wrote a synthetic {a.plan} session under {a.raw}/e183 (b {a.b:+.6f}, c {a.c:+.6f}, sigma {sigma:.5f}, seed {a.seed})")


if __name__ == "__main__":
    main()
