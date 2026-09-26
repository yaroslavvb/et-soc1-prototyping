#!/usr/bin/env python3
"""V3-GS helpers shared by block.sh and reduce.py (off-card only: they read files, never the card).

    python3 tools/claims-v3/gs/gslib.py plan --root <tree> --block KS [--data-root <dir>] [--smoke] [--dry]
        the block's configurations and seeds as JSON. K = pass 1-9; S = 0 check (C), 1 energy (E), 2 rate (R).
        E and R leave out every configuration whose verify launch failed in this card's latest C block
        (<data-root>/gs/p<K>0/check.json, the highest K with status ok or checkfail); no C block -> an error.
    python3 tools/claims-v3/gs/gslib.py missing <block-dir>
        configurations of the block's configs.json with no launch in its runs.jsonl (comma list; empty if none)
    python3 tools/claims-v3/gs/gslib.py check <block-dir> --kind C|E|R|smoke --card <id> --gov-free 0|1 --root <tree>
        the post-block check: writes <block-dir>/check.json and prints "<status> <note>"
          C:     ok (every configuration printed a verify line with ok true) | checkfail (some did not; listed, and
                 E/R leave them out) | fail (no data, or more than half without a launch)
          E:     catfull's check (tools/claims-v3/catfull/cflib.py check(), imported unchanged: bursts cut by
                 analyze_catalogue.bursts_of, the governor-free clock rules): ok | offclock | partial | fail, plus the
                 gs counts (launches with gsc_progress != 0 at exit, launches not ok)
          R:     rate only (bursts are 1 s with 1 s gaps, too short for idle brackets): per launch, governor-free
                 cards drop a launch whose implied clock (cycles_max / wall_s) is outside 0.595-0.605 GHz or whose
                 busy telemetry samples are not all at 600 MHz; ok | offclock | partial | fail
          smoke: the verify lines must pass and the timed ones must have launched
Every rule here was fixed with the README before any gs data existed.
"""
import argparse
import gzip
import importlib
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = {0: "C", 1: "E", 2: "R"}
CLOCK_LO, CLOCK_HI = 0.595, 0.605
_MOD = {}


def seed_run(k, s):
    return int(f"60{k}{s}")


def _enercat(root, name):
    key = (root, name)
    if key not in _MOD:
        sys.path.insert(0, os.path.join(root, "workloads", "enercat"))
        try:
            _MOD[key] = importlib.import_module(name)
        finally:
            sys.path.pop(0)
    return _MOD[key]


def cflib(root):
    """tools/claims-v3/catfull/cflib.py of the tree, imported unchanged (burst cutting, drop rules, statistics)."""
    key = (root, "cflib")
    if key not in _MOD:
        sys.path.insert(0, os.path.join(root, "tools", "claims-v3", "catfull"))
        try:
            _MOD[key] = importlib.import_module("cflib")
        finally:
            sys.path.pop(0)
    return _MOD[key]


def jl(path):
    if os.path.exists(path + ".gz"):
        return [json.loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    if os.path.exists(path):
        return [json.loads(l) for l in open(path) if l.startswith("{")]
    return []


def jload(path, default=None):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def load_block_json(path):
    try:
        txt = open(path).read()
    except OSError:
        return None
    try:
        return json.loads(txt)
    except ValueError:
        try:
            return json.loads(re.sub(r'":\s*(?=[,}])', '":null', txt))
        except ValueError:
            return None


# ---------------- the plan ----------------
def latest_check(data_root):
    """(block dir, check.json) of this card's latest usable C block, or (None, None)."""
    base = os.path.join(data_root, "gs")
    best = None
    if os.path.isdir(base):
        for name in os.listdir(base):
            m = re.fullmatch(r"p(\d)0", name)
            if not m:
                continue
            d = os.path.join(base, name)
            bj = load_block_json(os.path.join(d, "block.json")) or {}
            cj = jload(os.path.join(d, "check.json"))
            if bj.get("status") in ("ok", "checkfail") and cj:
                if best is None or int(m.group(1)) > best[0]:
                    best = (int(m.group(1)), d, cj)
    return (best[1], best[2]) if best else (None, None)


def plan(root, ks=None, data_root=None, smoke=False, dry=False):
    gc = _enercat(root, "gs_catalogue")
    if smoke:
        cfgs = gc.configs("smoke")
        names = [c["cfg"] for c in cfgs]
        return {"block": "smoke", "kind": "smoke", "pass": 0, "part": None, "seed_run": 1, "n": len(names), "names": names,
                "excluded": [], "check_block": None}
    if not re.fullmatch(r"[1-9][0-2]", str(ks)):
        raise SystemExit(f"block {ks}: need KS with pass K 1-9 and S 0 (check), 1 (energy) or 2 (rate)")
    k, s = int(str(ks)[0]), int(str(ks)[1])
    kind = KINDS[s]
    cfgs = gc.configs(kind)
    names = [c["cfg"] for c in cfgs]
    excluded, check_block = [], None
    if kind in ("E", "R"):
        if not data_root:
            raise SystemExit("an E or R block needs --data-root (its C block's check.json)")
        d, cj = latest_check(data_root)
        if cj is None and not dry:
            raise SystemExit(f"no C block with a check.json under {data_root}/gs/p<K>0 (run 'gs 10' first)")
        if cj is None:   # V3_DRY: a dry C block writes no check.json; nothing is excluded
            cj, d = {"failed": []}, "(dry: no check)"
        failed = {f["cfg"] for f in cj.get("failed", [])}
        check_block = d
        keep = []
        for n in names:
            if gc.check_of(n) in failed:
                excluded.append({"cfg": n, "why": f"its verify launch {gc.check_of(n)} failed in {os.path.basename(d)}"})
            else:
                keep.append(n)
        names = keep
    all_names = [c["cfg"] for c in gc.configs("all")]
    amb = [n for n in names if sum(1 for m in all_names if m.startswith(n)) != 1]
    if amb:
        raise SystemExit(f"names that do not select exactly one configuration: {amb[:5]}")
    return {"block": str(ks), "kind": kind, "pass": k, "part": s, "seed_run": seed_run(k, s), "n": len(names),
            "names": names, "excluded": excluded, "check_block": check_block, "n_set": len(cfgs)}


def missing(d):
    cj = jload(os.path.join(d, "configs.json"), {}) or {}
    have = {r["cfg"] for r in jl(os.path.join(d, "runs.jsonl"))}
    return [c["cfg"] for c in cj.get("cfgs", []) if c["cfg"] not in have]


def gs_counts(runs):
    return {"launches": len(runs),
            "gsc_nonzero_launches": sum(1 for r in runs if (r.get("gs") or {}).get("gsc_nonzero", 0)),
            "gsc_nonzero_harts": sum(int((r.get("gs") or {}).get("gsc_nonzero", 0)) for r in runs),
            "not_ok_launches": sum(1 for r in runs if not r.get("ok")),
            "missing_harts": sum(int((r.get("gs") or {}).get("missing", 0)) for r in runs)}


# ---------------- post-block checks ----------------
def check_c(d, card):
    runs = jl(os.path.join(d, "runs.jsonl"))
    cj = jload(os.path.join(d, "configs.json"), {}) or {}
    expected = [c["cfg"] for c in cj.get("cfgs", [])]
    last = {}
    for r in runs:
        last[r["cfg"]] = r   # a retried configuration: its last line counts
    passed, failed = [], []
    winners = defaultdict(Counter)
    probe = None
    for n in expected:
        r = last.get(n)
        if r is None:
            failed.append({"cfg": n, "why": "no launch"})
            continue
        v = r.get("verify") or {}
        if v.get("ok") is True and r.get("ok"):
            passed.append(n)
        else:
            failed.append({"cfg": n, "why": f"verify {v.get('mismatches')} mismatches of {v.get('checked')}, gsc_nonzero "
                                            f"{v.get('gsc_nonzero')}: {v.get('first', '')[:160]}"})
        for lane, cnt in (v.get("winners") or {}).items():
            winners[n.split("/")[2]][lane] += cnt
        if v.get("probe") is not None:
            probe = {"cfg": n, **v["probe"]}
    miss = [f for f in failed if f["why"] == "no launch"]
    res = {"card": card, "kind": "C", "expected": len(expected), "passed": len(passed), "failed": failed,
           "winners_by_op": {k: dict(v) for k, v in winners.items()}, "probe": probe, **gs_counts(runs)}
    if not runs or len(miss) > len(expected) // 2:
        st, note = "fail", f"no data ({len(runs)} launches, {len(miss)} of {len(expected)} configurations without one)"
    elif failed:
        st, note = "checkfail", f"{len(failed)} of {len(expected)} verify launches failed: " + ",".join(f["cfg"] for f in failed)[:300]
    else:
        st, note = "ok", f"{len(passed)}/{len(expected)} verify launches passed"
    w = ";".join(f"{op}:{dict(c)}" for op, c in sorted(winners.items()))
    if w:
        note += f"; conflict lanes {w}"
    res.update({"status": st, "note": note})
    json.dump(res, open(os.path.join(d, "check.json"), "w"), indent=1)
    return st, note


def check_e(d, card, gov, root):
    st, note = cflib(root).check(d, card, gov, root)
    res = jload(os.path.join(d, "check.json"), {}) or {}
    runs = jl(os.path.join(d, "runs.jsonl"))
    cnt = gs_counts(runs)
    res.update({"kind": "E", **cnt})
    if cnt["gsc_nonzero_launches"]:
        note += f"; {cnt['gsc_nonzero_launches']} launches with gsc_progress != 0 (erratum 1.3)"
    if cnt["not_ok_launches"]:
        note += f"; {cnt['not_ok_launches']} launches not ok"
    res["note"] = note
    json.dump(res, open(os.path.join(d, "check.json"), "w"), indent=1)
    return st, note


def launch_clock_ok(r, tel_t, tel_mhz, gov):
    """(ok, why) for one launch of an R block."""
    if not gov:
        return True, None
    g = r["cycles_max"] / r["wall_s"] / 1e9 if r.get("wall_s") else 0.0
    if not (CLOCK_LO <= g <= CLOCK_HI):
        return False, f"implied clock {g:.4f} GHz"
    lo, hi = r["t_start_ms"] / 1000.0 + 0.1, r["t_end_ms"] / 1000.0
    busy = [m for t, m in zip(tel_t, tel_mhz) if lo <= t <= hi]
    if busy and any(m != 600 for m in busy):
        return False, f"busy samples off 600 MHz ({sorted(set(busy))})"
    return True, None


def check_r(d, card, gov):
    runs = jl(os.path.join(d, "runs.jsonl"))
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    tel_t = [s["t_ms"] / 1000.0 for s in tel]
    tel_mhz = [s["mhz"]["minion"] for s in tel]
    cj = jload(os.path.join(d, "configs.json"), {}) or {}
    expected = [c["cfg"] for c in cj.get("cfgs", [])]
    kept, dropped = Counter(), []
    for r in runs:
        ok, why = launch_clock_ok(r, tel_t, tel_mhz, gov)
        if ok and r.get("ok"):
            kept[r["cfg"]] += 1
        else:
            dropped.append({"cfg": r["cfg"], "why": why or "launch not ok"})
    miss = [n for n in expected if n not in {r["cfg"] for r in runs}]
    none_kept = [n for n in expected if n not in miss and not kept[n]]
    res = {"card": card, "kind": "R", "gov_free": bool(gov), "expected": len(expected), "missing": miss,
           "cfgs_with_kept_launch": sum(1 for n in expected if kept[n]), "dropped_launches": dropped,
           "no_kept_launch": none_kept, "n_tel": len(tel), **gs_counts(runs)}
    if not runs or len(miss) > len(expected) // 2:
        st, note = "fail", f"no data ({len(runs)} launches, {len(miss)} of {len(expected)} without one)"
    elif gov and none_kept:
        st, note = "offclock", f"{len(none_kept)} configurations with no launch at 600 MHz: {','.join(none_kept)[:200]}"
    elif miss:
        st, note = "partial", f"{len(miss)} of {len(expected)} configurations have no launch: {','.join(miss)[:200]}"
    else:
        st, note = "ok", f"{res['cfgs_with_kept_launch']}/{len(expected)} configurations, {sum(kept.values())} launches kept"
    if dropped:
        note += f", {len(dropped)} launches dropped"
    if res["gsc_nonzero_launches"]:
        note += f"; {res['gsc_nonzero_launches']} launches with gsc_progress != 0"
    res.update({"status": st, "note": note})
    json.dump(res, open(os.path.join(d, "check.json"), "w"), indent=1)
    return st, note


def check_smoke(d, card):
    runs = jl(os.path.join(d, "runs.jsonl"))
    cj = jload(os.path.join(d, "configs.json"), {}) or {}
    expected = [c["cfg"] for c in cj.get("cfgs", [])]
    have = Counter(r["cfg"] for r in runs)
    bad = []
    for n in expected:
        rs = [r for r in runs if r["cfg"] == n]
        if not rs:
            bad.append(f"{n}: no launch")
        elif "/SMC/" in n and not all((r.get("verify") or {}).get("ok") for r in rs):
            bad.append(f"{n}: verify {(rs[-1].get('verify') or {}).get('first', '')[:120]}")
        elif not all(r.get("ok") for r in rs):
            bad.append(f"{n}: launch not ok")
    res = {"card": card, "kind": "smoke", "expected": len(expected), "launches": dict(have), "bad": bad, **gs_counts(runs)}
    st = "ok" if not bad and runs else "fail"
    note = f"{len(expected) - len(bad)}/{len(expected)} smoke configurations ok" + (f"; {bad[0]}" if bad else "")
    res.update({"status": st, "note": note})
    json.dump(res, open(os.path.join(d, "check.json"), "w"), indent=1)
    return st, note


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "missing", "check"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--root")
    ap.add_argument("--block")
    ap.add_argument("--data-root")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry", action="store_true", help="V3_DRY: an E/R plan without a C check excludes nothing")
    ap.add_argument("--kind", choices=["C", "E", "R", "smoke"])
    ap.add_argument("--card")
    ap.add_argument("--gov-free", type=int, choices=[0, 1])
    a = ap.parse_args()
    if a.cmd == "plan":
        print(json.dumps(plan(a.root, a.block, a.data_root, a.smoke, a.dry)))
    elif a.cmd == "missing":
        print(",".join(missing(a.dir)))
    else:
        if not a.kind or a.card is None or (a.kind in ("E", "R") and a.gov_free is None) or (a.kind == "E" and not a.root):
            raise SystemExit("check needs --kind, --card, and for E/R --gov-free (E also --root)")
        if a.kind == "C":
            st, note = check_c(a.dir, a.card)
        elif a.kind == "E":
            st, note = check_e(a.dir, a.card, a.gov_free, a.root)
        elif a.kind == "R":
            st, note = check_r(a.dir, a.card, a.gov_free)
        else:
            st, note = check_smoke(a.dir, a.card)
        print(f"{st} {note}")
