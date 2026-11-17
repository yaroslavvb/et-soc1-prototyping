#!/usr/bin/env python3
"""data-e212 (Q208, Tue 17 Nov 2026): the lab's check P of one released E212 (1117-mmsweep2) session: its tiles, for THE
OPERAND-PATTERN RULE (E212.md section 11: a session with an operand-pattern arm, an arm whose data is one of the plan's 21 tiles, is
committed only once E210's registration is on GitHub main) and for E210's tile files byte for byte. Reads only; Python's own modules.

    /usr/bin/python3 -I -B patterns_e212.py <session dir> <src dir> <E210 tiles dir> --kinds <the lab's kinds tiles dir> \
        --out p.json --txt p.txt

What it reads: every run record's schedule entry and every device process's argv (`--values gemmL..:<gen>:<file>[,<file>...]`), the
smoke's arms (the schedule's smoke list), the tile files in the src copy (sha256 against arms.json's listed sha256 for the plan's
tiles, and against the lab's own kinds tiles, tools/claims-v3/kinds/tiles/, for the nine the kit copied), and the sha256 of every
tile file under the E210 folder given (E210's registration's tiles; its output names no E210 file).

  P1 the operand-pattern arms: a run is an operand-pattern run when any tile file it names is not one of the nine kinds tiles the
     kit copied from the lab (fp32 and fp16 randn, zeros, ones; int8 full, zeros, ones), i.e. one of the plan's 21 tiles (the
     registration's stricter reading). Reported: the count, the runs, the tiles.
  P2 E210's tile files: whether any tile file the session ran equals, byte for byte, any tile file of E210's registration
     (the count of E210 files read and the sha256 of their sorted sha256 list, E212.md section 11's digest, are printed; no E210
     file is named).
"""
import argparse
import collections
import hashlib
import json
import os
import sys

KINDS = {"src/tiles/fp32/randn.bin", "src/tiles/fp32/zeros.bin", "src/tiles/fp32/ones.bin",
         "src/tiles/fp16/randn.bin", "src/tiles/fp16/zeros.bin", "src/tiles/fp16/ones.bin",
         "src/tiles/int8/full.bin", "src/tiles/int8/zeros.bin", "src/tiles/int8/ones.bin"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tiles_of(values):
    if not values:
        return []
    p = values.split(":")
    return p[2].split(",") if len(p) >= 3 else []


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("src")
    ap.add_argument("e210")
    ap.add_argument("--kinds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    S, top = a.session, os.path.dirname(os.path.normpath(a.src))
    arms_json = json.load(open(os.path.join(a.src, "arms.json")))
    listed = {t["file"]: t["sha256"] for t in arms_json["tiles"].values()}
    e210_all = []
    for dirpath, _, files in os.walk(a.e210):
        for f in files:
            if f.endswith(".bin"):
                e210_all.append(sha(open(os.path.join(dirpath, f), "rb").read()))
    e210, n_e210 = set(e210_all), len(e210_all)
    # the digest E212.md section 11 prints: the sha256 of the sorted list of every file's sha256, one hex digest a line, each ended by
    # a newline
    e210_digest = sha("".join(h + "\n" for h in sorted(e210_all)).encode()) if e210_all else None
    q = json.load(open(os.path.join(S, "queue.json")))
    sched = json.load(open(os.path.join(a.src, "sched", q["sched"])))
    used = collections.defaultdict(list)  # tile file -> runs
    argv_bad = []
    for k in sorted(os.listdir(os.path.join(S, "runs"))):
        r = json.load(open(os.path.join(S, "runs", k, "run.json")))
        v = (r.get("sched") or {}).get("values")
        for t in tiles_of(v):
            used[t].append(k)
        for p in r.get("procs") or []:
            av = p.get("argv") or []
            pv = av[av.index("--values") + 1] if "--values" in av else None
            if pv != v:
                argv_bad.append(f"{k}/{p.get('name')}: argv values {pv} != schedule {v}")
    for s_ in sched.get("smoke") or []:
        for t in tiles_of(s_.get("values")):
            used[t].append("smoke " + s_.get("arm", "?"))
    R, L = {}, []

    def rec(key, verdict, **kw):
        R[key] = dict(verdict=verdict, **kw)
        L.append(f"{key} {verdict}: " + "; ".join(f"{x} {y}" for x, y in kw.items()))

    pat_tiles = sorted(t for t in used if t not in KINDS)
    pat_runs = sorted({k for t in pat_tiles for k in used[t] if not k.startswith("smoke")})
    pat_smoke = sorted({k for t in pat_tiles for k in used[t] if k.startswith("smoke")})
    sha_bad = []
    tiles = {}
    for t in sorted(used):
        p = os.path.join(top, t)
        b = open(p, "rb").read() if os.path.exists(p) else None
        h = sha(b) if b is not None else None
        if b is None:
            sha_bad.append(f"{t}: ABSENT in the src copy")
        if t in listed and listed[t] != h:
            sha_bad.append(f"{t}: file {h} != arms.json {listed[t]}")
        if t in KINDS:
            kp = os.path.join(a.kinds, t[len("src/tiles/"):])
            if not os.path.exists(kp):
                sha_bad.append(f"{t}: the lab's kinds tile not read")
            elif sha(open(kp, "rb").read()) != h:
                sha_bad.append(f"{t}: differs from the lab's kinds tile")
        elif t not in listed:
            sha_bad.append(f"{t}: neither a kinds tile nor one of arms.json's plan tiles")
        tiles[t] = {"sha256": h, "plan_tile": t not in KINDS, "runs": len(used[t]), "equal_to_an_e210_tile": h in e210}
    rec("P1_operand_pattern_arms", "NONE" if not pat_runs and not pat_smoke else "PRESENT",
        runs_on_a_plan_tile=len(pat_runs), smoke_on_a_plan_tile=len(pat_smoke), plan_tiles=pat_tiles or "none",
        runs=pat_runs[:40] or "none", tiles_read=len(used), kinds_tiles=sorted(t for t in used if t in KINDS),
        argv_values_equal_schedule=("yes" if not argv_bad else argv_bad[:5]),
        tile_sha256=("plan tiles = arms.json, kinds tiles = the lab's" if not sha_bad else sha_bad[:5]))
    eq = sorted(t for t, v in tiles.items() if v["equal_to_an_e210_tile"])
    rec("P2_e210_tile_bytes", "NONE" if not eq else "EQUAL", e210_tile_files_read=n_e210, e210_distinct=len(e210),
        e210_sorted_sha256_list_sha256=e210_digest, session_tiles_equal_to_an_e210_tile=eq or "none")
    ok = not argv_bad and not sha_bad
    out = {"what": "data-e212's check P (the operand-pattern rule; E210's tile files byte for byte) of one E212 session (reads only)",
           "session": os.path.basename(os.path.normpath(S)), "schedule": q["sched"], "checks": R, "tiles": tiles,
           "records_consistent": ok, "operand_pattern_session": bool(pat_runs or pat_smoke), "e210_tile_equal": bool(eq),
           "python": sys.version.split()[0], "interpreter": sys.executable}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    with open(a.txt, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
