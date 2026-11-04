#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E163 reduction (Q141): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E163's passes (blind pool 7
and the 16 re-run tiles on aifoundry3 card 0) or on its E151 blocks, with E163's items installed on the shared e78_common module
(e163_common.install()). A copy of tools/claims-v3/e153/reduce_e153.py (E153, pool 6 on this card) with the items, the registration
file and the hash check changed (E163), and one mode added (E163 change 1). E153's two labelled options are kept:

  --drop-dips   the board-meter dips removed from the telemetry before the reduction reads it, with E82 amendment A2's definition,
                board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W. E163's REGISTERED PRIMARY applies it once, with --leak
                0.20563713796102187 --no-refit (Q139(u)'s frozen aifoundry3 slope; collect_e163.sh).
  --gates-off   E78's five pass gates opened in memory (every per-run gate stays), to show what a set-aside moved.
  E163 change 1, --e151 [--rail-filter]: the E151 blocks (16350-16359), reduced as E151's registered primary reduces its blocks
                (tools/claims-v3/e151/reduce_e151.py: --drop-dips --rail-filter, leakage auto): --rail-filter removes E151's rail
                glitches with E151's railfilter_e151.py, unchanged (F1, the rail more than 4.0 W above both samples two steps away; F2,
                the rail equal to the running maximum the sample reports), and the union with the dips is removed. The step over
                each item's own zero is E151's Book's, in score_e163.py, from the per-run table this writes (--csv).

    python3 tools/claims-v3/e163/reduce_e163.py <pass dir> ... --out e163.json [--drop-dips] [--gates-off] [--e151 [--rail-filter]]
        [--csv] [--txt] [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]   (every reduce_e78.py option)

Before it runs it checks reduce_e78.py, e78_common.py, kinds.json and e163_common.py (and, with --rail-filter, railfilter_e151.py)
against harness-e163.json and the pools' frozen files against their sha256, and refuses on any difference. After reduce_e78 writes
--out, its "experiment" becomes "E163" (or "E163-E151") and a "reducer" block records the code, the hashes, the arm and every sample
removed; the --txt file gets a header line.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
HAR = os.path.join(HERE, "harness-e163.json")
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
    want.update(har["e163_card_files_sha256"])
    want.update(har["reused_e151_sha256"])
    flags = {}
    for f in ("--drop-dips", "--gates-off", "--e151", "--rail-filter"):
        flags[f] = f in sys.argv
        if flags[f]:
            sys.argv.remove(f)
    if flags["--rail-filter"] and not flags["--e151"]:
        raise SystemExit("--rail-filter is E151's, for the E151 blocks only (--e151)")
    bad = []
    rels = ["tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/kinds.json",
            "tools/claims-v3/e163/e163_common.py"]
    if flags["--rail-filter"]:
        rels.append("tools/claims-v3/e151/railfilter_e151.py")
    for rel in rels:
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e163_common as e163  # noqa: E402
    e = e163.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code, e163_common.py, the rail filter or the pools' frozen files changed:\n  "
                         + "\n  ".join(bad))
    passes = [os.path.basename(a.rstrip("/")) for a in sys.argv[1:] if os.path.isdir(a)]
    kinds = {e163.block_kind(p[1:]) if p[1:].isdigit() else "?" for p in passes}
    if flags["--e151"] and kinds - {"e151"}:
        raise SystemExit(f"--e151 reduces E151 blocks only (16350-16359), not {sorted(passes)}")
    if not flags["--e151"] and kinds & {"e151"}:
        raise SystemExit("an E151 block is not a kinds pass: reduce it with --e151 --rail-filter")
    rf = None
    if flags["--rail-filter"]:
        sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e151"))
        import railfilter_e151 as rf  # noqa: E402  (E151's registered filter, unchanged)
    e163.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install; tools/claims-v3/kinds is on the path)
    if flags["--gates-off"]:
        r.GATES.update({"pass_max_failed_runs": 10 ** 6, "zero_mid_departure_w": 1e9, "zero_range_w": 1e9,
                        "tie_drift_w": 1e9, "random_range_w": 1e9})
    removed = {}
    if flags["--drop-dips"] or rf is not None:
        orig_load = r.load_jsonl

        def load_jsonl(path):
            rows = orig_load(path)
            if os.path.basename(path).startswith("telemetry.jsonl"):
                d = dips(rows) if flags["--drop-dips"] else set()
                fl = rf.flags(rows) if rf is not None else {"F1": set(), "F2": set(), "union": set()}
                gone = d | fl["union"]
                removed[os.path.basename(os.path.dirname(path))] = {
                    "samples": len(rows), "board_dips": len(d), "rail_F1": len(fl["F1"]), "rail_F2": len(fl["F2"]),
                    "rail_union": len(fl["union"]), "removed": len(gone),
                    "rail_t_ms": [rows[i].get("t_ms") for i in sorted(fl["union"])][:200],
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
    parts = [w for f, w in (("--drop-dips", "dips removed (E82 A2)"), ("--rail-filter", "rail glitches removed (E151's filter)"),
                            ("--gates-off", "pass gates opened")) if flags[f]]
    arm = " + ".join(parts)
    if out_path and os.path.exists(out_path):
        res = json.load(open(out_path))
        res["experiment"] = "E163-E151" if flags["--e151"] else "E163"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e163/reduce_e163.py",
            "reduce_e78_sha256": sha(os.path.join(e163.KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(e163.KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(e163.KINDS, "kinds.json")),
            "blind7_json_sha256": sha(e163.POOL_JSON),
            "e163_common_sha256": sha(os.path.join(HERE, "e163_common.py")),
            "railfilter_e151_sha256": sha(os.path.join(ROOT, "tools/claims-v3/e151/railfilter_e151.py")) if rf is not None else None,
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus blind pool 7's 61 tiles, the 16 re-run tiles and E151's 26 (e163_common.install)",
            "mode": "E151 blocks (E151's trains, its registered primary reduction)" if flags["--e151"] else "kinds passes",
            "arm": arm or "primary (nothing changed)",
            "pass_gates": "opened (the labelled gates-off arm)" if flags["--gates-off"] else "E78's, unchanged",
            "dips": "removed (E82 A2's definition, once)" if flags["--drop-dips"] else "kept",
            "samples_removed": removed,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E163: reduce_e78.py unchanged via reduce_e163.py ({'E151 blocks' if flags['--e151'] else 'kinds passes'}; "
                                  f"{arm or 'dips kept'})\n" + body)


if __name__ == "__main__":
    main()
