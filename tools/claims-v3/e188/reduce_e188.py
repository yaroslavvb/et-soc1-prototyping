#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E188 reduction (Q165, the kit): three reductions, each read by score_e188.py. A port of tools/claims-v3/e186/reduce_e186.py (E186's,
run on 9 Nov 2026), with E188's items, blocks and harness (E188):

  trains   the trains (E188.md section 5.1, E182's statistic unchanged): E182's reduce_train (tools/claims-v3/e182/reduce_e182.py),
           imported UNCHANGED and called with e182_stats (through e188_stats and e186_stats) and each E188 train's plan entry:
             python3 tools/claims-v3/e188/reduce_e188.py trains <train block dir> ... --out trains-e188.json
           per launch the reading in [start + 170 ms, end] of the block's 10 Hz board_w samples after E82 A2's dip rule; per process its
           complete quads, signed by its orientation; per unit the mean; per train the estimate and its 95% interval; and E182's reported
           readings (orientation means, halves, carry-over, quads' residual sd, process times, anchors' raw levels, the minion rail); and,
           as E186 added, each train's measured rate (rate_per_s): over the processes with a value, the mean of the work of launches 0-12
           (iters x minions, from their own records) over the time from launch 0's start to launch 12's end (E188.md section 4.2, "from its
           own launch records");
  anchors  the float trains' own anchor runs, for the session's float scale s (E188.md section 4.2, E186's route): each train block (all
           seven are fp32) becomes one pass of four E78 runs - its a0's fp32.zeros and fp32.randn and its a1's fp32.randn and fp32.zeros,
           with the block's own telemetry, configs and tile dumps - in a work directory, and E78's registered reduction (reduce_e78.py,
           unchanged, E188's items installed) reads all of them together on E182's registered footing (--leak 0.20563713796102187
           --no-refit, dips removed once):
             python3 tools/claims-v3/e188/reduce_e188.py anchors <train block dir> ... --work <empty dir> --out e188-anchors.json
               --leak 0.20563713796102187 --no-refit --drop-dips [--txt ...]
  kinds    E78's registered reduction, run UNCHANGED on E188's kinds passes - FULL's (18820-18829) or the fallback's (18830-18839), each
           family reduced on its own - with E188's items installed on the shared e78_common module (e188_common.install()); E182's two
           labelled options are kept:
             --drop-dips   E82 amendment A2's dips removed once (the registered primary, with --leak 0.20563713796102187 --no-refit);
             --gates-off   E78's five pass gates opened in memory.
             python3 tools/claims-v3/e188/reduce_e188.py <pass dir> ... --out e188.json [--drop-dips] [--gates-off] [--csv] [--txt] [...]

Before it runs it checks reduce_e78.py, e78_common.py, kinds.json, e188_common.py and E182's reduce_e182.py against harness-e188.json and
E182's lists, and the registration's files against their hash list, and refuses on any difference. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E182D = os.path.join(TOP, "tools", "claims-v3", "e182")
sys.path.insert(0, HERE)
HAR = os.path.join(HERE, "harness-e188.json")
REDUCE_E182 = "tools/claims-v3/e182/reduce_e182.py"
KF = 0.20563713796102187


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def e182_kit_pin(rel):
    """the sha256 E182's kit list (SHA256SUMS-e182-kit, pinned by step 2) gives a file"""
    for line in open(os.path.join(E182D, "SHA256SUMS-e182-kit")):
        if line.strip():
            h, p = line.split(None, 1)
            if p.strip().lstrip("*") == rel:
                return h
    return None


def refuse_unless_frozen(extra_rels=()):
    har = json.load(open(HAR))
    want = dict(har["card_code_unchanged_sha256"])
    want.update(har["e188_card_files_sha256"])
    bad = []
    for rel in ["tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/kinds.json",
                "tools/claims-v3/e188/e188_common.py"] + list(extra_rels):
        have = sha(os.path.join(TOP, rel))
        if have != want.get(rel):
            bad.append(f"{rel}: sha256 {have} != registered {want.get(rel)}")
    have = sha(os.path.join(TOP, REDUCE_E182))
    if have != e182_kit_pin(REDUCE_E182):
        bad.append(f"{REDUCE_E182}: sha256 {have} is not E182's kit list's {e182_kit_pin(REDUCE_E182)}")
    import e188_common as e188  # noqa: E402
    e = e188.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code, E182's reduction, e188_common.py or the registration's files changed:\n  "
                         + "\n  ".join(bad))
    return e188


def _e78_main(dirs_argv, flags, mode, removed_sink):
    """E78's reduction, unchanged, with E188's items installed and E182's two labelled options"""
    import e188_common as e188  # noqa: E402
    e188.install()
    sys.path.insert(0, E182D)
    import reduce_e182 as RD  # noqa: E402  (dips() only, unchanged)
    import reduce_e78 as r  # noqa: E402  (after the check and the install; tools/claims-v3/kinds is on the path)
    if flags["--gates-off"]:
        r.GATES.update({"pass_max_failed_runs": 10 ** 6, "zero_mid_departure_w": 1e9, "zero_range_w": 1e9,
                        "tie_drift_w": 1e9, "random_range_w": 1e9})
    if flags["--drop-dips"]:
        orig_load = r.load_jsonl

        def load_jsonl(path):
            rows = orig_load(path)
            if os.path.basename(path).startswith("telemetry.jsonl"):
                d = RD.dips(rows)
                removed_sink[os.path.basename(os.path.dirname(path))] = {
                    "samples": len(rows), "board_dips": len(d), "removed": len(d), "dip_t_ms": [rows[i].get("t_ms") for i in sorted(d)][:200]}
                rows = [x for i, x in enumerate(rows) if i not in d]
            return rows

        r.load_jsonl = load_jsonl
    sys.argv = ["reduce_e78.py"] + dirs_argv
    r.main()
    return r


def _postfix(out_path, txt_path, flags, mode, removed, e188):
    parts = [w for f, w in (("--drop-dips", "dips removed (E82 A2)"), ("--gates-off", "pass gates opened")) if flags[f]]
    arm = " + ".join(parts)
    if out_path and os.path.exists(out_path):
        res = json.load(open(out_path))
        res["experiment"] = "E188"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e188/reduce_e188.py",
            "reduce_e78_sha256": sha(os.path.join(e188.KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(e188.KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(e188.KINDS, "kinds.json")),
            "kinds_list_sha256": sha(e188.KINDS_E188),
            "plan_e188_sha256": sha(e188.PLAN_E188),
            "e188_common_sha256": sha(os.path.join(HERE, "e188_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus the 13 committed tiles that E188 runs (e188_common.install)",
            "mode": mode,
            "arm": arm or "primary (nothing changed)",
            "pass_gates": "opened (the labelled gates-off arm)" if flags["--gates-off"] else "E78's, unchanged",
            "dips": "removed (E82 A2's definition, once)" if flags["--drop-dips"] else "kept",
            "samples_removed": removed,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E188: reduce_e78.py unchanged via reduce_e188.py ({mode}; {arm or 'dips kept'})\n" + body)


def _flags(argv):
    flags = {}
    for f in ("--drop-dips", "--gates-off"):
        flags[f] = f in argv
        if flags[f]:
            argv.remove(f)
    return flags


def _opt(argv, name):
    for i, x in enumerate(argv):
        if x == name and i + 1 < len(argv):
            return argv[i + 1]
    return None


def kinds_main(argv):
    flags = _flags(argv)
    e188 = refuse_unless_frozen()
    passes = [os.path.basename(a.rstrip("/")) for a in argv if os.path.isdir(a)]
    kinds = {e188.block_kind(p[1:]) if p[1:].isdigit() else "?" for p in passes}
    if kinds - {"kinds"}:
        raise SystemExit(f"E188's kinds reduction reads its aifoundry3 kinds passes only (18820-18839), not {sorted(passes)}")
    fams = {e188.pass_family(p[1:]) for p in passes}
    if len(fams) > 1:
        raise SystemExit(f"E188's kinds reduction reads one family of kinds pass at a time (FULL's 1882x or the fallback's 1883x), not {sorted(passes)}")
    removed = {}
    _e78_main(argv, flags, "kinds passes", removed)
    _postfix(_opt(argv, "--out"), _opt(argv, "--txt"), flags, "kinds passes", removed, e188)


# ------------------------------------------------------------------------------------------------- the float trains' anchors (E188)
def assemble_anchor_pass(block_dir, work):
    """one float train block's four anchor runs as one E78 pass directory in <work>/p<block>: its a0's and a1's runs, marks and tile
    dumps, a0's configs.json, and the block's own telemetry and config reads"""
    b = os.path.basename(block_dir.rstrip("/"))
    dst = os.path.join(work, b)
    if os.path.exists(dst):
        raise SystemExit(f"{dst} exists: the anchors' work directory must be empty")
    os.makedirs(os.path.join(dst, "tiles"))
    tel = [f for f in ("telemetry.jsonl.gz", "telemetry.jsonl") if os.path.exists(os.path.join(block_dir, f))]
    if not tel:
        raise SystemExit(f"{block_dir}: no telemetry")
    shutil.copy(os.path.join(block_dir, tel[0]), os.path.join(dst, tel[0]))
    for f in ("config_start.json", "config_end.json"):
        if os.path.exists(os.path.join(block_dir, f)):
            shutil.copy(os.path.join(block_dir, f), os.path.join(dst, f))
    with open(os.path.join(dst, "runs.jsonl"), "w") as fo, open(os.path.join(dst, "marks.jsonl"), "w") as fm:
        for sub in ("a0", "a1"):
            sd = os.path.join(block_dir, sub)
            if not os.path.isdir(sd):
                raise SystemExit(f"{block_dir}: no {sub}/ (the train's {'opening' if sub == 'a0' else 'closing'} anchors)")
            fo.write(open(os.path.join(sd, "runs.jsonl")).read())
            fm.write(open(os.path.join(sd, "marks.jsonl")).read())
            td = os.path.join(sd, "tiles")
            for t in (os.listdir(td) if os.path.isdir(td) else []):
                q = os.path.join(dst, "tiles", t)
                if os.path.exists(q) and sha(q) != sha(os.path.join(td, t)):
                    raise SystemExit(f"{block_dir}: a0's and a1's dumps of {t} differ")
                shutil.copy(os.path.join(td, t), q)
    shutil.copy(os.path.join(block_dir, "a0", "configs.json"), os.path.join(dst, "configs.json"))
    return dst


def anchors_main(argv):
    flags = _flags(argv)
    work = _opt(argv, "--work")
    if not work:
        raise SystemExit("anchors: --work <an empty directory> is required")
    i = argv.index("--work")
    del argv[i:i + 2]
    e188 = refuse_unless_frozen()
    blocks = [a for a in argv if os.path.isdir(a)]
    if not blocks:
        raise SystemExit("anchors: no train block directory given")
    if os.path.isdir(work) and os.listdir(work):
        raise SystemExit(f"anchors: {work} is not empty")
    os.makedirs(work, exist_ok=True)
    dirs = []
    for d in blocks:
        b = os.path.basename(d.rstrip("/"))
        if not (b.startswith("p") and b[1:].isdigit() and e188.block_kind(b[1:]) == "train"):
            raise SystemExit(f"{d}: not a train block (p18810-p18819)")
        t = e188.train_of_block(int(b[1:]))
        if t["type"] == "int8":
            raise SystemExit(f"{d}: {t['train']} is an int8 train: the scale is read from the float trains' anchors only")
        dirs.append(assemble_anchor_pass(d, work))
    rest = [a for a in argv if a not in blocks]
    removed = {}
    _e78_main(dirs + rest, flags, "the float trains' anchors", removed)
    _postfix(_opt(argv, "--out"), _opt(argv, "--txt"), flags, "the float trains' anchors (E188.md section 4.2)", removed, e188)


# ------------------------------------------------------------------------------------------------- the trains
def train_rate(d, train):
    """E188: the pair's measured rate from its own launch records (minion-ops a second): over processes with 13 launches after the
    calibration, the mean of sum(iters x minions over launches 0-12) / (launch 12's end - launch 0's start)"""
    import reduce_e182 as RD  # noqa: E402
    recs = RD._jl(os.path.join(d, "train.jsonl"))
    vals = []
    for k in range(train["processes"]):
        rr = sorted((r for r in recs if r.get("process") == k and r.get("launch", -1) >= 0), key=lambda r: r["launch"])
        if len(rr) != 13 or not all(r.get("ok") for r in rr):
            continue
        work = sum(float(r["iters"]) * float(r.get("minions", 1024)) for r in rr)
        dt = (rr[-1]["t_end_ms"] - rr[0]["t_start_ms"]) / 1000.0
        if dt > 0:
            vals.append(work / dt)
    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)


def trains_main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    e188 = refuse_unless_frozen()
    sys.path.insert(0, E182D)
    import reduce_e182 as RD  # noqa: E402  (reduce_train and _jl, unchanged)
    import e188_stats as R  # noqa: E402  (imports e182_stats unchanged)
    S = R.S
    out = {"experiment": "E188", "what": "the trains (reduce_e188.py trains; E188.md section 5.1: E182's reduce_train and e182_stats unchanged)",
           "e182_stats_sha256": sha(os.path.join(E182D, "e182_stats.py")), "reduce_e182_sha256": sha(os.path.join(TOP, REDUCE_E182)),
           "reducer_sha256": sha(os.path.abspath(__file__)), "trains": {}}
    for dname in a.dirs:
        b = os.path.basename(dname.rstrip("/"))
        if not (b.startswith("p") and b[1:].isdigit() and e188.block_kind(b[1:]) == "train"):
            raise SystemExit(f"{dname}: not a train block (p18810-p18819)")
        t = e188.train_of_block(int(b[1:]))
        v = RD.reduce_train(dname, S, t)
        rate, n = train_rate(dname, t)
        v["rate_per_s"] = rate
        v["rate_processes"] = n
        out["trains"][t["train"]] = v
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    for k, v in sorted(out["trains"].items()):
        e_ = v["estimate"]
        print(f"{k} {v['first']} - {v['second']}: units {e_['n']}, mean {e_['mean']}, 95% [{e_.get('lo')}, {e_.get('hi')}], rate {v['rate_per_s']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "trains":
        trains_main(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == "anchors":
        anchors_main(sys.argv[2:])
    else:
        kinds_main(sys.argv[1:])
