#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E178 reduction (Q146, the kit): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E178's passes (the 40
one-number kinds on aifoundry3 card 0), with E178's items installed on the shared e78_common module (e178_common.install()). A copy of
tools/claims-v3/e171/reduce_e171.py with the items, the registration files and the hash check changed (E178). E171's (E153's) two labelled
options are kept:

  --drop-dips   the board-meter dips removed from the telemetry before the reduction reads it, with E82 amendment A2's definition,
                board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W. E178's REGISTERED PRIMARY (E178.md section 5, "E171's registered
                footing") applies it once, with --leak 0.20563713796102187 --no-refit (Q139(u)'s frozen aifoundry3 slope; collect_e178.sh).
  --gates-off   E78's five pass gates opened in memory (every per-run gate stays), to show what a set-aside moved.

    python3 tools/claims-v3/e178/reduce_e178.py <pass dir> ... --out e178.json [--drop-dips] [--gates-off] [--csv] [--txt]
        [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]   (every reduce_e78.py option)

A kind run several times in a pass (E78's six anchors and the eight core kinds, once a segment) takes the mean of its kept runs in the
pass's per_pass entry, as E78's reduction does (E178.md section 5); the per-run values are in the --csv file, which the scorer reads for
the core couples. Card 1 (A1-7's footing, E172's reducer) is not this file's: it refuses any pass outside aifoundry3's 17810-17819.

Before it runs it checks reduce_e78.py, e78_common.py, kinds.json and e178_common.py against harness-e178.json and the registration's files
against their hash lists, and refuses on any difference. After reduce_e78 writes --out, its "experiment" becomes "E178" and a "reducer"
block records the code, the hashes, the arm and every sample removed; the --txt file gets a header line.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
HAR = os.path.join(HERE, "harness-e178.json")
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
    want.update(har["e178_card_files_sha256"])
    flags = {}
    for f in ("--drop-dips", "--gates-off"):
        flags[f] = f in sys.argv
        if flags[f]:
            sys.argv.remove(f)
    bad = []
    rels = ["tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/kinds.json",
            "tools/claims-v3/e178/e178_common.py"]
    for rel in rels:
        have = sha(os.path.join(TOP, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e178_common as e178  # noqa: E402
    e = e178.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code, e178_common.py or the registration's files changed:\n  "
                         + "\n  ".join(bad))
    passes = [os.path.basename(a.rstrip("/")) for a in sys.argv[1:] if os.path.isdir(a)]
    kinds = {e178.block_kind(p[1:], "aifoundry3") if p[1:].isdigit() else "?" for p in passes}
    if kinds - {"kinds"}:
        raise SystemExit(f"E178's kit reduces its aifoundry3 kinds passes only (17810-17819), not {sorted(passes)}")
    e178.install()
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
        res["experiment"] = "E178"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e178/reduce_e178.py",
            "reduce_e78_sha256": sha(os.path.join(e178.KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(e178.KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(e178.KINDS, "kinds.json")),
            "kinds_e178_sha256": sha(e178.KINDS_E178),
            "plan_e178_sha256": sha(e178.PLAN_E178),
            "e178_common_sha256": sha(os.path.join(HERE, "e178_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus E178's 34 new one-number tiles (e178_common.install)",
            "mode": "kinds passes",
            "arm": arm or "primary (nothing changed)",
            "pass_gates": "opened (the labelled gates-off arm)" if flags["--gates-off"] else "E78's, unchanged",
            "dips": "removed (E82 A2's definition, once)" if flags["--drop-dips"] else "kept",
            "samples_removed": removed,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E178: reduce_e78.py unchanged via reduce_e178.py (kinds passes; "
                                  f"{arm or 'dips kept'})\n" + body)


if __name__ == "__main__":
    main()
