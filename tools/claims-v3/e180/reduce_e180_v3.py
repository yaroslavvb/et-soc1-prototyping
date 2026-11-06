#!/usr/bin/env python3
"""E180's reduction, v3 (the kit's dated note 2, KIT.md.dated-note-2.md section 3): reduce_e180_v2.py's reduction with one change, made
before any E180 datum: a pass whose files cannot be read is set aside with the reason, and the reduction goes on to the other passes.

    python3 tools/claims-v3/e180/reduce_e180_v3.py --data <card data dir: .../e180> --out reduced-e180-v3.json [--card aifoundry3]

The fault (the kit verifier kitv-e180, Fri 6 Nov 2026, fault 4): v1 and v2 parse every pass directory before their set-aside rule, so one
unreadable file (a gzip that ends early, a partial last line, or a sample ettelem printed without a field because that request failed,
tools/ettelem/ettelem.cpp lines 165-200) raised EOFError, JSONDecodeError or KeyError and lost every pass's score, not only that pass's.
v3 runs v1's per-pass reduction (reduce_e180.reduce_pass, imported unchanged) and v2's per-burst readings (reduce_e180_v2.extras, imported
unchanged) one pass at a time, exactly as v1's and v2's mains do, and:
  - when v1's reduction of a pass raises, that pass is set aside, its "why" reading "unreadable: <the file and its first bad line>"
    (named by a scan of the pass's telemetry and runs for what bursts_of reads: every '{' line JSON, a sample's t_ms, board_w,
    temp_c.minshire[0], mhz.minion and sp's minion_w, sram_w and noc_w first values numbers; a run's cfg, pass and numeric fields), or
    the exception itself when the scan names nothing; its record holds no D and no runs;
  - when v2's readings of a kept pass raise, the pass stays kept with v1's D unchanged, and every one of its bursts is listed in
    "v2_unread" (the reported arms then come from the other passes, as for any burst v2 cannot read);
  - a data directory that is not there gives no pass, never an error.
For every input v2 reduces without an error, v3's output is v2's, field for field, plus one "v3" record naming what it set aside; so the
registered rules read exactly what v2 (and v1) would give them. Nothing here changes a registered rule or reading. The box's own
post-block check (check_e180_v2.py block) is unchanged and stays fail-closed: one unreadable sample there ends the session's queue.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import numbers
import os
import re
import statistics as st
import sys
import zlib

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e180 as r1  # noqa: E402  (v1, unchanged)
import reduce_e180_v2 as r2  # noqa: E402  (v2, unchanged)

RUN_NUM = ("t_start_ms", "t_end_ms", "ops", "bytes", "cycles_max", "ops_per_cycle_per_hart")
RUN_ANY = ("cfg", "pass", "pattern", "unit", "operands", "harts", "scp", "participants", "shires")


def _num(x):
    return isinstance(x, numbers.Real) and not isinstance(x, bool)


def tel_missing(x):
    """the first field bursts_of reads that a telemetry sample lacks (or holds a non-number in), else None"""
    if not isinstance(x, dict):
        return "an object"
    for k in ("t_ms", "board_w"):
        if not _num(x.get(k)):
            return k
    try:
        if not _num(x["temp_c"]["minshire"][0]):
            return "temp_c.minshire[0]"
    except (KeyError, IndexError, TypeError):
        return "temp_c.minshire[0]"
    try:
        if not _num(x["mhz"]["minion"]):
            return "mhz.minion"
    except (KeyError, TypeError):
        return "mhz.minion"
    for k in ("minion_w", "sram_w", "noc_w"):
        try:
            if not _num(x["sp"][k][0]):
                return f"sp.{k}[0]"
        except (KeyError, IndexError, TypeError):
            return f"sp.{k}[0]"
    return None


def run_missing(x):
    """the first field bursts_of reads that a run record lacks (or holds a non-number in), else None"""
    if not isinstance(x, dict):
        return "an object"
    for k in RUN_ANY:
        if k not in x:
            return k
    for k in RUN_NUM:
        if not _num(x.get(k)):
            return k
    return None


def scan(d):
    """None, or why the pass's telemetry or runs cannot be read as v1 reads them (the file, and its first bad line)"""
    for base, need in (("telemetry.jsonl", tel_missing), ("runs.jsonl", run_missing)):
        p = os.path.join(d, base)
        path = p + ".gz" if os.path.exists(p + ".gz") else p if os.path.exists(p) else None
        if path is None:
            continue                       # v1 reads an absent file as empty: its own rule sets the pass aside
        n, bad = 0, []
        try:
            with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
                for k, line in enumerate(f, 1):
                    if not line.startswith("{"):
                        continue
                    n += 1
                    try:
                        miss = need(json.loads(line))
                    except ValueError:
                        miss = "JSON (a partial or garbled line)"
                    if miss:
                        bad.append((k, miss))
        except (OSError, EOFError, zlib.error, UnicodeDecodeError) as e:
            return f"{os.path.basename(path)} cannot be read to its end ({type(e).__name__}: {e})"
        if bad:
            return (f"{os.path.basename(path)}: {len(bad)} of {n} '{{' lines unreadable (the first, line {bad[0][0]}: no {bad[0][1]})")
    return None


def reduce_all(data, root, card, plan_path):
    """v1's main loop (reduce_e180.main), pass by pass, with the guard; then v2's readings (reduce_e180_v2.main), with the guard"""
    plan = json.load(open(plan_path or os.path.join(HERE, "plan-e180.json")))
    kinds = sorted({r1.kind_of(c) for c in plan["order"]["18010"]})
    ac = r1.analyzer(root)
    out = {"card": card, "passes": {}, "set_aside": {}}
    unreadable, v2err = {}, {}
    names = sorted(os.listdir(data)) if os.path.isdir(data) else []
    for name in names:
        m = re.match(r"^p(\d+)$", name)
        if not m or not plan["order"].get(m.group(1)):
            continue
        d = os.path.join(data, name)
        blk = {}
        try:
            blk = json.load(open(os.path.join(d, "block.json")))
        except (OSError, ValueError):
            pass
        if not isinstance(blk, dict):
            blk = {}
        try:
            kept, dropped, info = r1.reduce_pass(d, ac)
        except Exception as e:  # noqa: BLE001  (any error reading one pass: that pass only)
            why = scan(d) or f"the reduction of this pass raised {type(e).__name__}: {e}"
            unreadable[m.group(1)] = why
            out["set_aside"][m.group(1)] = {"why": f"unreadable: {why}", "block_status": blk.get("status"), "dropped": [],
                                            "missing": kinds, "n_tel": None, "n_runs": None, "D": {}, "runs": {}}
            continue
        missing = [k for k in kinds if k not in kept]
        rec = {"block_status": blk.get("status"), "dropped": dropped, "missing": missing, **info,
               "D": {k: st.mean(r["w"] for r in v) for k, v in kept.items()}, "runs": kept}
        if blk.get("status") not in ("ok", "partial"):
            out["set_aside"][m.group(1)] = {"why": f"block status {blk.get('status')}", **rec}
        elif missing:
            out["set_aside"][m.group(1)] = {"why": f"{len(missing)} kinds with no kept burst: {', '.join(missing[:6])}", **rec}
        else:
            out["passes"][m.group(1)] = rec
    aside = ", ".join("%s (%s)" % (p, v["why"]) for p, v in out["set_aside"].items()) or "none"
    print(f"{len(out['passes'])} kept passes ({', '.join(out['passes'])}); set aside: {aside}")
    red = json.loads(json.dumps(out, sort_keys=True))      # v2 re-reads v1's output from its json file: the same values here
    q = json.load(open(os.path.join(root, "tools/claims-v3/footing-law/footing-law.json")))["laws"][r2.LAWKEY.get(card, "aifoundry3")]["quad_w"]
    red["v2"] = {"what": "reduce_e180_v2.py: v1's reduction unchanged, plus A1 section 4.1's per-burst readings", "card": card,
                 "footing_law_quad_w": q, "rail_tau_s": r2.TAU.get(card, 1.235), "c_rb": r2.C_RB, "reach": r2.REACH,
                 "e60_slope": r2.E60_SLOPE}
    for group in ("passes", "set_aside"):
        for p, rec in red[group].items():
            ex = {}
            if p not in unreadable:
                try:
                    ex = r2.extras(os.path.join(data, f"p{p}"), ac, card, q)
                except Exception as e:  # noqa: BLE001
                    v2err[p] = f"{type(e).__name__}: {e}"
                    ex = {}
            rec["runs_v2"], rec["v2_unread"] = {}, []
            for key in r2.KEYS:
                rec[key] = {}
            for k, runs in rec.get("runs", {}).items():
                vals = []
                for r in runs:
                    e = ex.get(r["cfg"])
                    if e is None or e["R"] is None:
                        rec["v2_unread"].append(r["cfg"])
                    if e is not None:
                        vals.append(e)
                rec["runs_v2"][k] = vals
                for key in r2.KEYS:
                    xs = [e[key] for e in vals if e.get(key) is not None]
                    if xs:
                        rec[key][k] = st.mean(xs)
    n_unread = sum(len(v["v2_unread"]) for g in ("passes", "set_aside") for v in red[g].values())
    print(f"v2: the per-burst readings added for {len(red['passes'])} kept passes; bursts v2 could not read: {n_unread}")
    red["v3"] = {"what": "reduce_e180_v3.py (KIT.md.dated-note-2.md section 3): reduce_e180_v2.py's reduction, pass by pass; a pass whose "
                         "files cannot be read is set aside with the reason, and the reduction goes on",
                 "unreadable_passes": unreadable, "v2_readings_failed": v2err}
    print(f"v3: passes set aside as unreadable: {', '.join(f'{p} ({w})' for p, w in unreadable.items()) or 'none'}; "
          f"kept passes whose v2 readings failed: {', '.join(v2err) or 'none'}")
    return red


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="the card's e180 directory, holding p<P>/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--plan", default=None)
    a = ap.parse_args()
    red = reduce_all(a.data, a.root, a.card, a.plan)
    json.dump(red, open(a.out, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
