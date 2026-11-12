#!/usr/bin/env python3
"""E188 (Q165, the kit): the trains' pairing check, run at collection over EVERY train block: E188-SCHED (E188.md section 5.3, "E186-PAIR's
gate, renamed: PAIR is an item here"). A port of tools/claims-v3/e186/pairing_e186.py (E186's kit note 1, run on E186's data of 9 Nov
2026, PASS 9,968 of 9,968) with E188's names. It reads the smoke gate's per-launch pairing (smoke_gate_e188.py train()) over every launch
record of every train block the session ran, and it reads the tiles' identity from the REGISTERED BYTES, not from the host's own "tiles"
records:

  for every launch record of <block>/train.jsonl (the calibration launch -1 included):
    1. its process is one of the plan's (0 .. processes - 1) and its launch one of -1 .. 12, once each;
    2. its train_kind is the registered schedule's for that launch (the smoke gate's: launch n < 1 takes the orientation's first letter,
       launch n >= 1 its letter (n - 1) mod 4), so F and S sit where E182's reduction assumes them;
    3. its type is the train's format (fp32 for all seven);
    4. its train_values names the scheduled kind's registered tile (the path ends with the tile's path in the lab tree);
    5. the block's C log holds a C record for it (paired by t_start_ms and t_end_ms, as E188-C and the smoke gate pair them), and that
       record's fnv equals the FNV-1a 64 of the scheduled kind's registered tile bytes (2,048 bytes: A then B; ccheck.py's fnv64), each
       tile first checked against its registered sha256 (e188_common.load_items, which refuses a tile off E188's kinds list).
  A train with any launch failing 1-5 reads NOT SCORED (score_e188.py, E188-SCHED). Nothing is a stop: the result is a reading, recorded in
  the scored file and here. In E188 every train's two kinds give different C words (each pair differs in B's or A's held bits), so the
  check of C also tells the tile sets apart; this check reads the schedule and the record besides.

The C log of a block is read from <block>/c-log.jsonl or c-log.jsonl.gz, else from <ccheck dir>/c-log-p<block>.jsonl(.gz), the
collector's one copy. Standard library only.

    /usr/bin/python3 -B tools/claims-v3/e188/pairing_e188.py check --raw <raw copy> [--ccheck-dir DIR] [--json OUT] [--txt OUT]
Exit 0 when it read (whatever the reading), 2 usage, 9 a registered tile off its sha256 (e188_common refuses).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FIRST_FAILURES = 8          # the failures each train lists in full; every one is counted


def fnv64(b):
    """FNV-1a 64 over the bytes, ccheck.py's fnv64 (the C-logging host's ccFnv) word for word"""
    h = 1469598103934665603
    for x in b:
        h ^= x
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


def jl(path):
    if not path or not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    return out


def schedule(ori, launches=13):
    """the registered schedule of one process, launch -1 .. launches - 1 (smoke_gate_e188.train's, unchanged)"""
    return {n: (ori[0] if n < 1 else ori[(n - 1) % 4]) for n in range(-1, launches)}


def clog_paths(d, block, ccheck_dir=None):
    out = [p for p in (os.path.join(d, "c-log.jsonl"), os.path.join(d, "c-log.jsonl.gz")) if os.path.exists(p)]
    if not out and ccheck_dir:
        out = [p for p in (os.path.join(ccheck_dir, f"c-log-p{block}.jsonl"), os.path.join(ccheck_dir, f"c-log-p{block}.jsonl.gz"))
               if os.path.exists(p)]
    return out[:1]


def check_block(d, train, tiles, clogs, launches=13):
    """one train block against the plan: train = {train, block, type, processes, orientations, first, second}; tiles = {"F": {name,
    tile, fnv}, "S": {...}}; clogs = [the block's C log]. Returns the reading for the train."""
    recs = jl(os.path.join(d, "train.jsonl"))
    cs = {}
    nhost = 0
    for p in clogs:
        for r in jl(p):
            if r.get("kind") == "c":
                cs[(r.get("t_start_ms"), r.get("t_end_ms"))] = r
            elif r.get("kind") == "host":
                nhost += 1
    sched = {k: schedule(train["orientations"][k], launches) for k in range(train["processes"])}
    fails, by, seen = [], {}, set()

    def bad(r, why, key):
        by[key] = by.get(key, 0) + 1
        if len(fails) < FIRST_FAILURES:
            fails.append(f"process {r.get('process')} launch {r.get('launch')}: {why}")
    for r in recs:
        k, n = r.get("process"), r.get("launch")
        if not isinstance(k, int) or k not in sched:
            bad(r, f"process {k!r} is not one of the plan's 0..{train['processes'] - 1}", "process")
            continue
        if not isinstance(n, int) or n not in sched[k]:
            bad(r, f"launch {n!r} is not one of -1..{launches - 1}", "launch")
            continue
        if (k, n) in seen:
            bad(r, "a second record of this launch", "duplicate")
            continue
        seen.add((k, n))
        want = sched[k][n]
        if r.get("train_kind") != want:
            bad(r, f"train_kind {r.get('train_kind')!r} where the schedule says {want}", "train_kind")
            continue
        if r.get("type") is not None and r.get("type") != train["type"]:
            bad(r, f"type {r.get('type')!r}, not the train's {train['type']}", "type")
            continue
        t = tiles[want]
        if not str(r.get("train_values", "")).endswith("/" + t["tile"]) and str(r.get("train_values", "")) != "file:" + t["tile"]:
            bad(r, f"train_values {str(r.get('train_values'))[-90:]!r} is not {t['name']}'s tile {t['tile']}", "train_values")
            continue
        c = cs.get((r.get("t_start_ms"), r.get("t_end_ms")))
        if c is None:
            bad(r, "no C record at its t_start_ms and t_end_ms", "no_c_record")
            continue
        if c.get("fnv") != t["fnv"]:
            other = "F" if want == "S" else "S"
            what = f"{tiles[other]['name']}'s" if c.get("fnv") == tiles[other]["fnv"] else "neither kind's"
            bad(r, f"its C record's fnv {c.get('fnv')} is {what} tile, not {t['name']}'s {t['fnv']}", "c_fnv")
            continue
    nfail = sum(by.values())
    return {"train": train["train"], "block": train["block"], "type": train["type"], "first": tiles["F"]["name"], "second": tiles["S"]["name"],
            "launch_records": len(recs), "launches_paired": len(recs) - nfail, "failures": nfail, "failures_by_check": by,
            "first_failures": fails, "c_log": [os.path.basename(p) for p in clogs], "c_records": len(cs), "c_host_records": nhost,
            "ok": len(recs) > 0 and nfail == 0 and bool(clogs),
            "why": None if (recs and not nfail and clogs) else ("no launch record" if not recs else ("no C log for the block" if not clogs
                                                                                                         else f"{nfail} launch(es) not paired"))}


def tiles_of(train, items, top=TOP):
    out = {}
    for kk, nm in (("F", train["first"]), ("S", train["second"])):
        it = items[nm]
        raw = open(os.path.join(top, it["tile"]), "rb").read()
        if hashlib.sha256(raw).hexdigest() != it["sha256"] or len(raw) != 2048:
            raise SystemExit(f"pairing: {it['tile']} is not {nm}'s registered tile (sha256 or size)")
        out[kk] = {"name": nm, "tile": it["tile"], "fnv": fnv64(raw), "sha256": it["sha256"]}
    return out


def check_raw(raw, ccheck_dir=None):
    """every E188 train block under <raw>/e188/ (p18810-p18816), against plan-e188.json's trains and the registered tiles"""
    sys.path.insert(0, HERE)
    import e188_common as E  # noqa: E402
    items = {it["name"]: it for it in E.load_items()}
    out = {"_note": "E188, pairing_e188.py (E188-SCHED): every train launch's record against the registered schedule and tiles",
           "pairing_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(), "trains": {}, "tiles_fnv": {}}
    for b in sorted(E.TRAINS):
        t = E.TRAINS[b]
        d = os.path.join(raw, "e188", f"p{b}")
        if not os.path.isfile(os.path.join(d, "train.jsonl")):
            continue
        tl = tiles_of(t, items)
        out["tiles_fnv"].update({v["name"]: v["fnv"] for v in tl.values()})
        res = check_block(d, t, tl, clog_paths(d, b, ccheck_dir), E.LAUNCHES)
        try:
            res["block_status"] = json.load(open(os.path.join(d, "block.json"))).get("status")
        except (OSError, ValueError):
            res["block_status"] = None
        out["trains"][t["train"]] = res
    out["trains_checked"] = sorted(out["trains"])
    out["trains_failed"] = sorted(k for k, v in out["trains"].items() if not v["ok"])
    out["ok"] = not out["trains_failed"]
    return out


def text(o):
    L = [f"E188's pairing check (pairing_e188.py, E188-SCHED): {len(o['trains_checked'])} train block(s) read, "
         f"{len(o['trains_failed'])} not paired" + (f": {o['trains_failed']}" if o["trains_failed"] else "")]
    for tid, v in o["trains"].items():
        L.append(f"  {tid:9s} p{v['block']}: {v['launch_records']} launch records, {v['launches_paired']} paired, {v['failures']} not "
                 f"{v['failures_by_check'] or ''}; C log {v['c_log'] or 'NONE'} ({v['c_records']} C records); "
                 f"{'PAIRED' if v['ok'] else 'NOT PAIRED: ' + str(v['why'])}")
        for f in v["first_failures"]:
            L.append(f"      {f}")
    L.append("PAIRING " + ("OK" if o["ok"] else "FAILED") + f" ({len(o['trains_checked'])} trains read)")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("check",))
    ap.add_argument("--raw", required=True)
    ap.add_argument("--ccheck-dir")
    ap.add_argument("--json")
    ap.add_argument("--txt")
    a = ap.parse_args()
    try:
        o = check_raw(a.raw, a.ccheck_dir)
    except SystemExit as e:
        print(f"REFUSED (9): {e}", file=sys.stderr)
        return 9
    if a.json:
        open(a.json, "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
    tx = text(o)
    if a.txt:
        open(a.txt, "w").write(tx)
    sys.stdout.write(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
