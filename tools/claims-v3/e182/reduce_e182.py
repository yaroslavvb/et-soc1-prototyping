#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E182 reduction (Q153, the kit): two reductions, each read by score_e182.py.

  kinds   E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E182's kinds passes (18220-18229), with
          E182's items installed on the shared e78_common module (e182_common.install()). A copy of tools/claims-v3/e178/reduce_e178.py
          with the items, the registration files and the hash check changed (E182); E178's two labelled options are kept:
            --drop-dips   E82 amendment A2's dips removed once (E182's registered primary, with --leak 0.20563713796102187 --no-refit);
            --gates-off   E78's five pass gates opened in memory.
            python3 tools/claims-v3/e182/reduce_e182.py <pass dir> ... --out e182.json [--drop-dips] [--gates-off] [--csv] [--txt] [...]
  trains  the trains (E182.md section 5.1), with e182_stats.py's functions, unchanged:
            python3 tools/claims-v3/e182/reduce_e182.py trains <train block dir> ... --out trains-e182.json
          per launch the reading in [start + 170 ms, end] of the block's 10 Hz board_w samples after E82 A2's dip rule (2 or more);
          per process its complete quads, signed by its orientation; per unit (processes 2j, 2j + 1) the mean; per train the estimate
          and its 95% interval; reported beside: each orientation's mean, the halves, the carry-over reading (L2 - L3), the quads'
          residual sd, the process times, the anchors' raw levels and the minion rail's level. A launch record not ok, or a process
          that ended on a stop, gives no value (the reducer drops a process with fewer than 13 launches after its calibration).

Before it runs it checks reduce_e78.py, e78_common.py, kinds.json and e182_common.py against harness-e182.json and the registration's
files against their hash list, and refuses on any difference. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
HAR = os.path.join(HERE, "harness-e182.json")
DIP_W = 4.0


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def dips(rows):
    """E82 A2: sample i when board_w[i] < min(board_w[i-2], board_w[i+2]) - 4 W. Returns the set of indices."""
    B = [r.get("board_w") for r in rows]
    bad = set()
    for i in range(2, len(rows) - 2):
        if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - DIP_W:
            bad.add(i)
    return bad


def main():
    har = json.load(open(HAR))
    want = dict(har["card_code_unchanged_sha256"])
    want.update(har["e182_card_files_sha256"])
    flags = {}
    for f in ("--drop-dips", "--gates-off"):
        flags[f] = f in sys.argv
        if flags[f]:
            sys.argv.remove(f)
    bad = []
    rels = ["tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/kinds.json",
            "tools/claims-v3/e182/e182_common.py"]
    for rel in rels:
        have = sha(os.path.join(TOP, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e182_common as e182  # noqa: E402
    e = e182.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code, e182_common.py or the registration's files changed:\n  "
                         + "\n  ".join(bad))
    passes = [os.path.basename(a.rstrip("/")) for a in sys.argv[1:] if os.path.isdir(a)]
    kinds = {e182.block_kind(p[1:]) if p[1:].isdigit() else "?" for p in passes}
    if kinds - {"kinds"}:
        raise SystemExit(f"E182's kinds reduction reads its aifoundry3 kinds passes only (18220-18229), not {sorted(passes)}")
    e182.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install; tools/claims-v3/kinds is on the path)
    if flags["--gates-off"]:
        r.GATES.update({"pass_max_failed_runs": 10 ** 6, "zero_mid_departure_w": 1e9, "zero_range_w": 1e9,
                        "tie_drift_w": 1e9, "random_range_w": 1e9})
    removed = {}
    if flags["--drop-dips"]:
        orig_load = r.load_jsonl

        def load_jsonl(path):
            rows = orig_load(path)
            if os.path.basename(path).startswith("telemetry.jsonl"):
                d = dips(rows)
                gone = d
                removed[os.path.basename(os.path.dirname(path))] = {
                    "samples": len(rows), "board_dips": len(d), "removed": len(gone),
                    "dip_t_ms": [rows[i].get("t_ms") for i in sorted(d)][:200]}
                rows = [x for i, x in enumerate(rows) if i not in gone]
            return rows

        r.load_jsonl = load_jsonl
    out_path = txt_path = None
    for i, x in enumerate(sys.argv):
        if x == "--out" and i + 1 < len(sys.argv):
            out_path = sys.argv[i + 1]
        if x == "--txt" and i + 1 < len(sys.argv):
            txt_path = sys.argv[i + 1]
    r.main()
    parts = [w for f, w in (("--drop-dips", "dips removed (E82 A2)"), ("--gates-off", "pass gates opened")) if flags[f]]
    arm = " + ".join(parts)
    if out_path and os.path.exists(out_path):
        res = json.load(open(out_path))
        res["experiment"] = "E182"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e182/reduce_e182.py",
            "reduce_e78_sha256": sha(os.path.join(e182.KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(e182.KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(e182.KINDS, "kinds.json")),
            "kinds_e182_sha256": sha(e182.KINDS_E182),
            "plan_e182_sha256": sha(e182.PLAN_E182),
            "e182_common_sha256": sha(os.path.join(HERE, "e182_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus E178's six reused tiles and E182's 16 new ones (e182_common.install)",
            "mode": "kinds passes",
            "arm": arm or "primary (nothing changed)",
            "pass_gates": "opened (the labelled gates-off arm)" if flags["--gates-off"] else "E78's, unchanged",
            "dips": "removed (E82 A2's definition, once)" if flags["--drop-dips"] else "kept",
            "samples_removed": removed,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E182: reduce_e78.py unchanged via reduce_e182.py (kinds passes; "
                                  f"{arm or 'dips kept'})\n" + body)


# ------------------------------------------------------------------------------------------------- the trains (E182)
def _jl(path):
    import gzip
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    return out


def _telemetry(d):
    rows = _jl(os.path.join(d, "telemetry.jsonl.gz")) or _jl(os.path.join(d, "telemetry.jsonl"))
    smp = sorted((int(r["t_ms"]), float(r["board_w"]), r) for r in rows
                 if isinstance(r.get("board_w"), (int, float)) and isinstance(r.get("t_ms"), (int, float)))
    return smp


def reduce_train(d, S, train):
    """one train block: its launches' readings, quads, process values, units and estimate (section 5.1), and the reported readings"""
    smp = _telemetry(d)
    kept = S.dips_kept([(t, w) for t, w, _ in smp])
    ts = [t for t, _ in kept]
    ws = [w for _, w in kept]
    recs = _jl(os.path.join(d, "train.jsonl"))
    marks = [m for m in _jl(os.path.join(d, "marks.jsonl")) if m.get("kind") == "train"]
    stopped = os.path.exists(os.path.join(d, "STOP"))
    procs, values, lost, info = [], [], [], []
    for k in range(train["processes"]):
        rr = sorted((r for r in recs if r.get("process") == k), key=lambda r: r["launch"])
        ori = train["orientations"][k]
        launches = [r for r in rr if r["launch"] >= 0]
        why = None
        if len(launches) != 13:
            why = f"{len(launches)} launches after the calibration, not 13"
        elif not all(r.get("ok") for r in rr):
            why = "a launch record not ok"
        elif any(r.get("abba") != ori or r.get("orientation") != ori for r in rr):
            why = "the orientation differs from the plan's"
        if why:
            lost.append({"process": k, "why": why})
            procs.append((ori, []))
            continue
        rd = {r["launch"]: S.launch_reading(ts, ws, r["t_start_ms"], r["t_end_ms"]) for r in launches}
        q = S.quads_of_process(rd, ori)
        procs.append((ori, q))
        l2l3 = []
        for qq in range(3):
            a, b = rd.get(4 * qq + 2), rd.get(4 * qq + 3)
            if a is not None and b is not None:
                l2l3.append(a - b)
        info.append({"process": k, "orientation": ori, "quads": q, "readings": [rd.get(i) for i in range(13)],
                     "l2_minus_l3": l2l3, "t0_ms": launches[0]["t_start_ms"], "t1_ms": launches[-1]["t_end_ms"]})
    units = S.train_units(procs)
    est = S.interval(units)
    half = len(units) // 2
    by_ori = {o: [c for oo, qq in procs if oo == o for c in qq] for o in ("SFFS", "FSSF")}
    ss, dfn = 0.0, 0
    for o, q in by_ori.items():
        if len(q) > 1:
            m = sum(q) / len(q)
            ss += sum((c - m) ** 2 for c in q)
            dfn += len(q) - 1
    pt = [m["t_end_ms"] - m["t_start_ms"] for m in marks]
    starts = sorted(m["t_start_ms"] for m in marks)
    period = [(b - a) / 1000.0 for a, b in zip(starts, starts[1:])]
    carry = {o: [x for i in info if i["orientation"] == o for x in i["l2_minus_l3"]] for o in ("SFFS", "FSSF")}
    anchors = {}
    for sub in ("a0", "a1"):
        for r in _jl(os.path.join(d, sub, "runs.jsonl")):
            if r.get("launch", -1) < 0:
                continue
            w = [x[1] for x in smp if r["t_start_ms"] + 1000 <= x[0] < r["t_start_ms"] + 3000]
            anchors.setdefault(f"{sub}:{r['item']}", []).append(sum(w) / len(w) if w else None)
    rail = [x[2].get("sp", {}).get("minion_w", [None])[0] for x in smp
            if info and info[0]["t0_ms"] <= x[0] <= info[-1]["t1_ms"] and isinstance(x[2].get("sp"), dict)]
    rail = [v for v in rail if isinstance(v, (int, float))]
    return {"train": train["train"], "first": train["first"], "second": train["second"], "type": train["type"], "block": train["block"],
            "processes_planned": train["processes"], "processes_with_value": sum(1 for _, q in procs if q), "processes_lost": lost,
            "units": units, "estimate": est, "stopped": stopped,
            "reported": {"orientation_means": {o: (sum(q) / len(q) if q else None) for o, q in by_ori.items()},
                         "quads_by_orientation": {o: len(q) for o, q in by_ori.items()},
                         "quad_residual_sd": (ss / dfn) ** 0.5 if dfn else None, "quad_residual_df": dfn,
                         "halves": [S.interval(units[:half]), S.interval(units[half:])],
                         "carry_over_l2_minus_l3": {o: S.interval(v) for o, v in carry.items()},
                         "process_wall_s_median": (sorted(pt)[len(pt) // 2] / 1000.0) if pt else None,
                         "process_period_s_median": sorted(period)[len(period) // 2] if period else None,
                         "anchors_raw_board_w": anchors, "minion_rail_mean_w": (sum(rail) / len(rail)) if rail else None,
                         "samples": len(smp), "samples_after_dips": len(kept)},
            "processes": info}


def trains_main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    har = json.load(open(HAR))
    bad = []
    for rel in ("tools/claims-v3/e182/e182_common.py",):
        if sha(os.path.join(TOP, rel)) != har["e182_card_files_sha256"][rel]:
            bad.append(rel)
    for rel in ("tools/claims-v3/e182/e182_stats.py", "tools/claims-v3/e182/plan-e182.json"):
        if sha(os.path.join(TOP, rel)) != har["registration_sha256"][rel]:
            bad.append(rel)
    import e182_common as e182  # noqa: E402
    e = e182.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce the trains - a registered file differs: " + "; ".join(bad))
    import e182_stats as S  # noqa: E402
    out = {"experiment": "E182", "what": "the trains (reduce_e182.py trains; E182.md section 5.1, e182_stats.py unchanged)",
           "e182_stats_sha256": sha(os.path.join(HERE, "e182_stats.py")), "reducer_sha256": sha(os.path.abspath(__file__)), "trains": {}}
    for dname in a.dirs:
        b = os.path.basename(dname.rstrip("/"))
        if not (b.startswith("p") and b[1:].isdigit() and e182.block_kind(b[1:]) == "train"):
            raise SystemExit(f"{dname}: not a train block (p18210-p18215)")
        t = e182.train_of_block(int(b[1:]))
        out["trains"][t["train"]] = reduce_train(dname, S, t)
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    for k, v in sorted(out["trains"].items()):
        e_ = v["estimate"]
        print(f"{k} {v['first']} - {v['second']}: units {e_['n']}, mean {e_['mean']}, 95% [{e_.get('lo')}, {e_.get('hi')}]")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "trains":
        trains_main(sys.argv[2:])
    else:
        main()
