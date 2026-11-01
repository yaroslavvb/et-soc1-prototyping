#!/usr/bin/env python3
"""E106 (Q132): read the accumulators back on the card. Run by run_e106.sh, under the card lock, on aifoundry1 card 1 at 600 MHz. Standard library only.

    python3 tools/claims-v3/kinds/readback_e106.py <out-dir> [--dry] [--only name,name] [--first-only]

For each tile and length in e106/e106.json, one launch of exactly that many ops and nothing else: `build/e104/b/host/sparsity_host --test fma --type <t> --pattern none
--values file:<tile> --shires 0xffffffff --per-shire 32 --iters <n> --seconds 0 --dump-c <file> --kernel <the existing build's ELF>`, under `timeout 10`. `--seconds 0` means repeatFor
runs one launch of --iters ops and returns (workloads/sparsity/host/main.cpp), so C holds what n ops left. A launch is at most 0.5 s. The card is not heated first: the accumulators are arithmetic,
and an op either ran or did not.

It writes <out-dir>/readback.jsonl, one line per read: the tile, n, the SPARSITY record's cycles per op, clock and ok, the sha256 of each distinct 1,024-byte C among the 1,024 minions with how
many minions hold it, and the first minion's C in hex. The whole dump is not kept: 1 MB a read, and if the minions agree the hex is all of it. A minion that disagrees keeps its own hex.

No knob is written. No governor, TDP, threshold or clock set, no reset, no --reset-ms.
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
HOST = os.path.join(ROOT, "build", "e104", "b", "host", "sparsity_host")
KERNEL = os.path.join(ROOT, "build", "sparsity", "kernel", "sparsity.elf")
MINIONS = 1024


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--first-only", action="store_true", help="just the first tile and length: a test of the path")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "e106", "e106.json")))
    only = set(x for x in a.only.split(",") if x)
    plan = []
    for name, lens in spec["readback"].items():
        if only and name not in only:
            continue
        for n in lens:
            plan.append((name, n))
    if a.first_only:
        plan = plan[:1]
    os.makedirs(a.out, exist_ok=True)
    dump = os.path.join(a.out, "c.bin")
    t0 = time.time()
    with open(os.path.join(a.out, "readback.jsonl"), "a") as out:
        for name, n in plan:
            v = spec["tiles"][name]
            path = os.path.join(HERE, "e106", v["file"])
            raw = open(path, "rb").read()
            assert hashlib.sha256(raw).hexdigest() == v["sha256"], name
            cmd = [HOST, "--test", "fma", "--type", v["type"], "--pattern", "none", "--values", "file:" + path, "--shires", "0xffffffff", "--per-shire", "32", "--iters", str(n), "--seconds", "0",
                   "--dump-c", dump, "--kernel", KERNEL]
            if a.dry:
                print("DRY timeout 10", " ".join(cmd))
                continue
            if os.path.exists(dump):
                os.remove(dump)
            t1 = time.time()
            p = subprocess.run(["timeout", "10"] + cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
            rec = {"tile": name, "n": n, "rc": p.returncode, "wall_s": round(time.time() - t1, 3), "t": round(t1, 3)}
            for l in p.stdout.splitlines():
                if l.startswith("SPARSITY "):
                    r = json.loads(l[len("SPARSITY "):])
                    rec["sparsity"] = {q: r.get(q) for q in ("iters", "cycles_per_op", "ghz", "minions", "ok", "result", "tensor_errors", "values")}
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
            else:
                rec["distinct_c"] = None
                rec["stderr_tail"] = p.stderr[-400:]
            out.write(json.dumps(rec) + "\n")
            out.flush()
            big = max(rec.get("groups", {"x": {"minions": 0}}).values(), key=lambda g: g["minions"])
            print(f"{name:14s} n {n:7d} rc {p.returncode} {rec['wall_s']:5.2f} s distinct {rec['distinct_c']} largest group {big['minions']} ok {rec.get('sparsity', {}).get('ok')} cpo {rec.get('sparsity', {}).get('cycles_per_op')} ghz {rec.get('sparsity', {}).get('ghz')}", flush=True)
            if p.returncode != 0 or rec["distinct_c"] is None:
                print("stopping: a read failed", flush=True)
                sys.exit(1)
            stop = [f for f in ("build/claims-v3/STOP", "build/kinds-STOP") if os.path.exists(os.path.join(ROOT, f))]
            if stop:
                print("stopping:", stop, flush=True)
                sys.exit(0)
    if os.path.exists(dump):
        os.remove(dump)
    print(f"reads {len(plan)} in {time.time() - t0:.1f} s", flush=True)


if __name__ == "__main__":
    main()
