#!/usr/bin/env python3
"""E116 (Q133): read the accumulators back on aifoundry3 card 0, once per E88 tile. E104's readback_e104.py with three
changes: the binary is E116's own build (build/e116/b/host/sparsity_host, E104's one-flag patch, built by
build_host_e116.sh), the plan is expect-e116.json's (E88's 22 tiles, tools/claims-v3/rpath/tiles/, one length each),
and each read is compared on the spot with accum.c's 256 words, frozen in expect-e116.json before the claim.
Standard library only. Run by block_readback_e116.sh under the card lock.

    python3 tools/claims-v3/e116/readback_e116.py <out-dir> [--dry] [--only name,name] [--first-only]

For each tile: one launch of exactly n ops and nothing else: `build/e116/b/host/sparsity_host --test fma --type <t>
--pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --iters <n> --seconds 0 --dump-c <file>
--kernel <the existing build's ELF>`, under `timeout 10`. `--seconds 0` runs one launch of --iters ops, so C holds
what n ops left. The card is not heated first: the accumulators are arithmetic.

It writes <out-dir>/readback.jsonl, one line per read: the tile, n, the SPARSITY record's cycles per op, clock and ok,
the sha256 of each distinct 1,024-byte C among the 1,024 minions with how many minions hold it, the first minion's C in
hex, and whether every minion's C equals accum.c's (`equal_accum`). The whole dump is not kept: 1 MB a read.

No knob is written. No governor, TDP, threshold or clock set, no reset, no --reset-ms, no PMIC command.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HOST = os.path.join(ROOT, "build", "e116", "b", "host", "sparsity_host")
KERNEL = os.path.join(ROOT, "build", "sparsity", "kernel", "sparsity.elf")
TILES = os.path.join(ROOT, "tools", "claims-v3", "rpath")
MINIONS = 1024


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--first-only", action="store_true", help="just the first tile: a test of the path")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "expect-e116.json")))
    only = set(x for x in a.only.split(",") if x)
    plan = [(name, v["n"]) for name, v in spec["tiles"].items() if not only or name in only]
    if a.first_only:
        plan = plan[:1]
    os.makedirs(a.out, exist_ok=True)
    dump = os.path.join(a.out, "c.bin")
    t0 = time.time()
    n_equal = 0
    with open(os.path.join(a.out, "readback.jsonl"), "a") as out:
        for name, n in plan:
            v = spec["tiles"][name]
            path = os.path.join(TILES, v["file"])
            raw = open(path, "rb").read()
            assert hashlib.sha256(raw).hexdigest() == v["sha256"], name
            cmd = [HOST, "--test", "fma", "--type", v["type"], "--pattern", "none", "--values", "file:" + path,
                   "--shires", "0xffffffff", "--per-shire", "32", "--iters", str(n), "--seconds", "0",
                   "--dump-c", dump, "--kernel", KERNEL]
            if a.dry:
                print("DRY timeout 10", " ".join(cmd))
                continue
            if os.path.exists(dump):
                os.remove(dump)
            t1 = time.time()
            p = subprocess.run(["timeout", "10"] + cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
            rec = {"tile": name, "n": n, "rc": p.returncode, "wall_s": round(time.time() - t1, 3), "t": round(t1, 3)}
            for line in p.stdout.splitlines():
                if line.startswith("SPARSITY "):
                    r = json.loads(line[len("SPARSITY "):])
                    rec["sparsity"] = {q: r.get(q) for q in ("iters", "cycles_per_op", "ghz", "minions", "ok", "result",
                                                             "tensor_errors", "values")}
            if os.path.exists(dump) and os.path.getsize(dump) == MINIONS * 1024:
                d = open(dump, "rb").read()
                groups = {}
                for m in range(MINIONS):
                    c = d[m * 1024:(m + 1) * 1024]
                    h = hashlib.sha256(c).hexdigest()
                    g = groups.setdefault(h, {"minions": 0, "first_minion": m, "hex": c.hex()})
                    g["minions"] += 1
                rec["distinct_c"] = len(groups)
                rec["groups"] = groups
                rec["accum_sha256"] = v["accum_sha256"]
                rec["equal_accum"] = (len(groups) == 1 and next(iter(groups)) == v["accum_sha256"])
                n_equal += rec["equal_accum"]
            else:
                rec["distinct_c"] = None
                rec["stderr_tail"] = p.stderr[-400:]
            out.write(json.dumps(rec) + "\n")
            out.flush()
            big = max(rec.get("groups", {"x": {"minions": 0}}).values(), key=lambda g: g["minions"])
            print(f"{name:14s} n {n:7d} rc {p.returncode} {rec['wall_s']:5.2f} s distinct {rec['distinct_c']} "
                  f"largest group {big['minions']} equal_accum {rec.get('equal_accum')} ok {rec.get('sparsity', {}).get('ok')} "
                  f"cpo {rec.get('sparsity', {}).get('cycles_per_op')} ghz {rec.get('sparsity', {}).get('ghz')}", flush=True)
            if p.returncode != 0 or rec["distinct_c"] is None:
                print("stopping: a read failed", flush=True)
                sys.exit(1)
            stop = [f for f in ("build/claims-v3/STOP", "build/rpath-STOP") if os.path.exists(os.path.join(ROOT, f))]
            if stop:
                print("stopping:", stop, flush=True)
                sys.exit(0)
    if os.path.exists(dump):
        os.remove(dump)
    print(f"reads {len(plan)} in {time.time() - t0:.1f} s; equal to accum.c: {n_equal}", flush=True)


if __name__ == "__main__":
    main()
