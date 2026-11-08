#!/usr/bin/env python3
"""E183 (Q155, the kit's dated note 1): synthetic sessions in the box's layout for the reduction v2's self-test (selftest_score_e183_v2.py).
Never a card. It runs fake_card_e183.py's generator (v1, cc597bf2, imported unchanged) block by block, then changes only what v2's cases
need:
  - every block.json carries t0_ms and t1_ms, as lib.sh's block_end writes them (the block's first and last sample times; --t0-ms moves
    the first);
  - --stop T:k[:n]   a live stop in train T's process k: the runner's stop.json names "train T process k (<ori>)"; process k keeps its
                     first n launch records (7 by default; 13 = a stop that fired after its last launch); later processes, the closing
                     anchors and the samples after the stop are gone; block.json reads status "stop", as block_e183.sh writes it on the
                     runner's exit 5;
  - --stop-anchor T  a live stop at train T's first closing anchor (fadd.ps/random, close): every process kept, the closing anchors gone;
  - --stop-no-json T status "stop" with no stop.json;
  - --wrong-image T:k  process k's F launches name the S image (train_operands);
  - --stale T:<ms>   that block's t0_ms set to <ms> (an earlier session's block);  --no-t0 T  that block.json without t0_ms;
  - --box-check      the box's post-block check (check_e183.py block, unchanged) run on each block, writing its check.json, with the
                     block's status and note set from it as block_e183.sh does (a stop overrides the status).
Everything else is v1's: the truth, the noise, the timing, the plan, --cut, --bad-launch, --flip-orientation, --override. Deterministic.

    /usr/bin/python3 -B tools/claims-v3/e183/fake_card_e183_v2.py <raw dir> [v1's options] [v2's options]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import contextlib
import gzip
import io
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e183_common as E      # noqa: E402
import fake_card_e183 as F1  # noqa: E402

BASE_MS = 1_800_000_000_000      # v1's synthetic clock: every block's samples start here


def rj(path):
    return [json.loads(l) for l in gzip.open(path, "rt") if l.strip()]


def wj(path, recs):
    with gzip.open(path, "wt") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def kv(items, cast=str):
    out = {}
    for it in items or []:
        k, v = it.split(":", 1)
        out[k] = cast(v)
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
    ap.add_argument("--t0-ms", type=int, default=BASE_MS)
    ap.add_argument("--stop", action="append")
    ap.add_argument("--stop-anchor", action="append")
    ap.add_argument("--stop-no-json", action="append")
    ap.add_argument("--wrong-image", action="append")
    ap.add_argument("--stale", action="append")
    ap.add_argument("--no-t0", action="append")
    ap.add_argument("--box-check", action="store_true")
    a = ap.parse_args()
    plan = E.plan()
    sigma = plan["sigma_q_w"] if a.sigma is None else a.sigma
    opts = {"cut": F1.parse_kv(a.cut, int), "bad": F1.parse_kv(a.bad_launch, int), "flip": F1.parse_kv(a.flip_orientation, int),
            "override": F1.parse_kv(a.override, float)}
    stops = kv(a.stop)
    wrong = F1.parse_kv(a.wrong_image, int)
    stale = F1.parse_kv(a.stale, int)
    rng = random.Random(a.seed)
    keep = set(plan["plans"][a.plan]["trains"])
    if a.box_check:
        import check_e183 as C   # noqa: E402  (the box's own post-block check, unchanged)
    for t in plan["trains"]:
        if t["train"] not in keep:
            continue
        n = opts["cut"].get(t["train"], t["processes"])
        procs = list(enumerate(t["orientations"][:n]))
        d = os.path.join(a.raw, "e183", f"p{t['block']}")
        F1.write_block(d, t, procs, a.b, a.c, sigma, rng, opts)          # v1's block, unchanged
        T = t["train"]
        tel = rj(os.path.join(d, "telemetry.jsonl.gz"))
        train = rj(os.path.join(d, "train.jsonl.gz"))
        runs = rj(os.path.join(d, "runs.jsonl.gz"))
        bj = json.load(open(os.path.join(d, "block.json")))
        stop = None
        if T in wrong:
            k = wrong[T]
            for r in train:
                if r["process"] == k and r["train_kind"] == "F":
                    r["train_operands"] = "file:" + E.image_rel(t["second"])
            wj(os.path.join(d, "train.jsonl.gz"), train)
        if T in stops:
            parts = stops[T].split(":")
            k, keepn = int(parts[0]), (int(parts[1]) if len(parts) > 1 else 7)
            ori = t["orientations"][k]
            mine = sorted((r for r in train if r["process"] == k and r["launch"] < keepn), key=lambda r: r["launch"])
            t_stop = (mine[-1]["t_end_ms"] if mine else min(r["t_start_ms"] for r in train if r["process"] == k)) + 100
            train = [r for r in train if r["process"] < k] + mine
            runs = [r for r in runs if not r["cfg"].endswith("-close") and r["t_end_ms"] <= t_stop]
            tel = [s for s in tel if s["t_ms"] <= t_stop + 400]
            stop = {"pass": t["block"], "where": f"train {T} process {k} ({ori})", "why": "board 65.12 W >= 65 W", "t_ms": t_stop}
        if T in (a.stop_anchor or []):
            cfg = E.anchor_cfg("fadd.ps/random", t["block"], "close")
            t_stop = max(r["t_end_ms"] for r in train) + int((E.GAP_S + 0.5) * 1000)
            runs = [r for r in runs if r["cfg"] not in (cfg, E.anchor_cfg("fadd.ps/zeros", t["block"], "close"))]
            tel = [s for s in tel if s["t_ms"] <= t_stop + 400]
            stop = {"pass": t["block"], "where": cfg, "why": "minshire[0] 70.1 C >= 70 C", "t_ms": t_stop}
        if stop is not None:
            wj(os.path.join(d, "train.jsonl.gz"), train)
            wj(os.path.join(d, "runs.jsonl.gz"), runs)
            wj(os.path.join(d, "telemetry.jsonl.gz"), tel)
            json.dump(stop, open(os.path.join(d, "stop.json"), "w"))
        st, note = bj["status"], bj["note"]
        if a.box_check:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                C.block(d, E.CARD, TOP)                 # writes check.json and prints "<status> <note>"
            res = buf.getvalue().strip().splitlines()[-1]
            st, note = res.split(" ", 1)
        if stop is not None:
            st, note = "stop", f"a live stop fired: {json.dumps(stop)}; {note}".replace('"', "'")
        if T in (a.stop_no_json or []):
            st, note = "stop", "a live stop fired: ; (desk test: stop.json withheld)"
        bj.update({"status": st, "note": note, "t0_ms": stale.get(T, a.t0_ms), "t1_ms": max(s["t_ms"] for s in tel)})
        if T in (a.no_t0 or []):
            bj.pop("t0_ms")
        json.dump(bj, open(os.path.join(d, "block.json"), "w"))
    print(f"wrote a synthetic {a.plan} session (v2) under {a.raw}/e183 (b {a.b:+.6f}, c {a.c:+.6f}, sigma {sigma:.5f}, seed {a.seed};"
          f" t0_ms {a.t0_ms}; stops {sorted(stops) + sorted(a.stop_anchor or []) + sorted(a.stop_no_json or [])}; wrong images "
          f"{sorted(wrong)}; stale {sorted(stale)}; no t0 {sorted(a.no_t0 or [])}; box check {a.box_check})")


if __name__ == "__main__":
    main()
