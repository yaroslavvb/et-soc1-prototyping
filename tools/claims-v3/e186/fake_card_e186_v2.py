#!/usr/bin/env python3
"""E186 kit note 1 (Q158, fix-e186): synthetic E186 sessions for the scorer v2's self-test. No card.

It runs fake_card_e186.py's main, UNCHANGED (the same arguments, the same seed, so the same session byte for byte), then gives every train
block the C log a card's block holds (fake_card_e186.py writes one for the smoke only): a host record, one "tiles" record a kind with the
registered tile bytes and their FNV-1a 64 (pairing_e186.fnv64, ccheck.py's), and a "c" record for every launch record of train.jsonl,
paired by t_start_ms and t_end_ms and carrying the fnv of the tile its record names. Then, at most one each, the pairing faults the
self-test reads (each on one launch of the named train, launch 5 of process 2, a launch of a quad):
  --pair-kind TRAIN    the launch ran the other kind's tiles with its records consistent (train_kind, train_values and the C record's fnv
                       all the other kind's): the host's records agree with each other, not with the schedule;
  --pair-values TRAIN  the launch's train_values names the other kind's tile (its train_kind and C record as scheduled);
  --pair-fnv TRAIN     the launch's C record carries the other kind's fnv (its train_kind and train_values as scheduled);
  --pair-noc TRAIN     the launch's C record left out of the C log;
  --no-clog TRAIN      the train block's C log left out altogether.
The check of C's verdict list (ccheck-all.json) is fake_card_e186.py's (every launch PASS unless --cfail), so E186-C cannot see these.

    python3 -B fake_card_e186_v2.py <out dir> <fake_card_e186.py's arguments> [--pair-kind T] [--pair-values T] [--pair-fnv T] [--pair-noc T]
        [--no-clog T]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e186_common as E  # noqa: E402
import fake_card_e186 as F  # noqa: E402  (its main, unchanged)
import pairing_e186 as PR  # noqa: E402

TAMPER = (2, 5)          # (process, launch) of the faulted launch


def write_clogs(out, faults):
    raw = os.path.join(out, "raw", "e186")
    items = {it["name"]: it for it in E.load_items()}
    n = 0
    for b, t in sorted(E.TRAINS.items()):
        d = os.path.join(raw, f"p{b}")
        if not os.path.isfile(os.path.join(d, "train.jsonl")):
            continue
        tl = PR.tiles_of(t, items)
        if faults.get("no_clog") == t["train"]:
            continue
        recs = [json.loads(x) for x in open(os.path.join(d, "train.jsonl")) if x.strip()]
        tid = t["train"]
        if tid in (faults.get("pair_kind"), faults.get("pair_values")):
            for r in recs:
                if (r["process"], r["launch"]) == TAMPER:
                    other = "F" if r["train_kind"] == "S" else "S"
                    if tid == faults.get("pair_kind"):
                        r["train_kind"] = other
                    r["train_values"] = "file:" + tl[other]["tile"]
            with open(os.path.join(d, "train.jsonl"), "w") as f:
                for r in recs:
                    f.write(json.dumps(r) + "\n")
        with open(os.path.join(d, "c-log.jsonl"), "w") as f:
            f.write(json.dumps({"ccheck": 1, "kind": "host", "host": "build/e186host/b/host/sparsity_host", "host_sha256": "0" * 64,
                                "kernel": "build/sparsity/kernel/sparsity.elf", "kernel_sha256": "0" * 64, "kernel_from": "default"}) + "\n")
            for kk in ("F", "S"):
                raw_t = open(os.path.join(TOP, tl[kk]["tile"]), "rb").read()
                f.write(json.dumps({"ccheck": 1, "kind": "tiles", "type": t["type"], "values": "file:" + tl[kk]["tile"], "fnv": tl[kk]["fnv"],
                                    "a": raw_t[:1024].hex(), "b": raw_t[1024:].hex()}) + "\n")
            for r in recs:
                kk = r["train_kind"]
                fnv = tl[kk]["fnv"]
                if (r["process"], r["launch"]) == TAMPER:
                    if tid == faults.get("pair_noc"):
                        continue
                    if tid == faults.get("pair_fnv"):
                        fnv = tl["F" if kk == "S" else "S"]["fnv"]
                f.write(json.dumps({"ccheck": 1, "kind": "c", "type": t["type"], "launch": r["launch"], "t_start_ms": r["t_start_ms"],
                                    "t_end_ms": r["t_end_ms"], "ok": True, "poison": True, "use_mask": 0, "b_stream": 0,
                                    "groups": [{"count": 1024}], "fnv": fnv}) + "\n")
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser(add_help=False)
    for o in ("--pair-kind", "--pair-values", "--pair-fnv", "--pair-noc", "--no-clog"):
        ap.add_argument(o)
    mine, rest = ap.parse_known_args()
    faults = {k: v for k, v in vars(mine).items() if v}
    sys.argv = [os.path.join(HERE, "fake_card_e186.py")] + rest
    F.main()
    out = rest[0]
    if "--smoke" in rest or any(x == "--passes" for x in rest):
        return
    n = write_clogs(out, faults)
    print(f"fake_card_e186_v2: C logs written in {n} train block(s); faults {faults or 'none'}")


if __name__ == "__main__":
    main()
