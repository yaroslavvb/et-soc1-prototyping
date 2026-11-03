#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E141 reduction (Q138): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E141's passes
(blind pool 5 on aifoundry3 card 0), with E141's items installed on the shared e78_common module (e141_common.install(): E78's 51
kinds and the tie plus blind pool 5's 36 tiles); a copy of tools/claims-v3/e140/reduce_e140.py (E140, pool 4 on this card) with the
pool, the registration file and the hash check changed (E141), so that the per-run gates (the dumped tile equal to the item's registered sha256
among them), the pass gates (E78's six anchors, three times a pass, and the tie), the interpolation of each type's zeros,
D = p80 - Z_type(t0), S, the rail, pJ per op / MAC / flop, the heat column and every statistic are E78's own. A port of
tools/claims-v3/kinds/reduce_e95.py, with two labelled arms ported from reduce_e103.py, each registered in README.md
before any E115 data:

  --drop-dips   the board-meter dips removed from the telemetry before the reduction reads it, with E82 amendment A2's
                definition, board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W (E86's, E95's and E103's arm). The
                reading reported if the primary keeps fewer than 2 passes.
  --gates-off   E78's five pass gates opened in memory (every per-run gate stays), to show what the set-aside moved.

    python3 tools/claims-v3/e141/reduce_e141.py <pass dir> ... --out e141.json [--drop-dips] [--gates-off]
        [--csv] [--txt] [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]   (every reduce_e78.py option)

Before it runs it checks reduce_e78.py, e78_common.py, kinds.json and e141_common.py against predictions-e141.json and blind pool
5's frozen files against their sha256, and refuses on any difference. After reduce_e78 writes --out, its
"experiment" becomes "E141" and a "reducer" block records the code, the hashes and the arm; the --txt file gets a header line.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e141.json")
DIP_W = 4.0


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def drop_dips(rows):
    """E82 A2: drop sample i when board_w[i] < min(board_w[i-2], board_w[i+2]) - 4 W. Returns (kept, dropped idx)."""
    B = [r.get("board_w") for r in rows]
    bad = set()
    for i in range(2, len(rows) - 2):
        if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - DIP_W:
            bad.add(i)
    return [r for i, r in enumerate(rows) if i not in bad], sorted(bad)


def main():
    reg = json.load(open(REG))
    want = dict(reg["harness"]["card_code_unchanged_sha256"])
    want.update(reg["harness"]["e141_card_files_sha256"])
    bad = []
    for rel in ("tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py",
                "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e141/e141_common.py"):
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e141_common as e140  # noqa: E402  (E141: the name kept)
    e = e140.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code, e141_common.py or blind pool 5's frozen files changed:\n  " + "\n  ".join(bad))
    dips_arm = "--drop-dips" in sys.argv
    if dips_arm:
        sys.argv.remove("--drop-dips")
    gates_off = "--gates-off" in sys.argv
    if gates_off:
        sys.argv.remove("--gates-off")
    e140.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install; tools/claims-v3/kinds is on the path)
    if gates_off:
        r.GATES.update({"pass_max_failed_runs": 10 ** 6, "zero_mid_departure_w": 1e9, "zero_range_w": 1e9,
                        "tie_drift_w": 1e9, "random_range_w": 1e9})
    dips = {}
    if dips_arm:
        orig_load = r.load_jsonl

        def load_jsonl(path):
            rows = orig_load(path)
            if os.path.basename(path).startswith("telemetry.jsonl"):
                rows2, idx = drop_dips(rows)
                dips[os.path.basename(os.path.dirname(path))] = {"samples_removed": len(idx),
                                                                  "t_ms": [rows[i].get("t_ms") for i in idx][:200]}
                rows = rows2
            return rows

        r.load_jsonl = load_jsonl
    out_path = txt_path = None
    for i, x in enumerate(sys.argv):
        if x == "--out" and i + 1 < len(sys.argv):
            out_path = sys.argv[i + 1]
        if x == "--txt" and i + 1 < len(sys.argv):
            txt_path = sys.argv[i + 1]
    r.main()
    arm = ("dips removed (E82 A2)" if dips_arm else "") + (" + " if dips_arm and gates_off else "") + \
          ("pass gates opened" if gates_off else "")
    if out_path and os.path.exists(out_path):
        res = json.load(open(out_path))
        res["experiment"] = "E141"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e141/reduce_e141.py",
            "reduce_e78_sha256": sha(os.path.join(e140.KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(e140.KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(e140.KINDS, "kinds.json")),
            "blind5_json_sha256": sha(e140.POOL_JSON),
            "e141_common_sha256": sha(os.path.join(HERE, "e141_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus blind pool 5's 36 tiles (e141_common.install)",
            "arm": arm or "primary (nothing changed)",
            "pass_gates": "opened (the labelled gates-off arm)" if gates_off else "E78's, unchanged",
            "dips": "removed (E82 A2's definition; the labelled dips arm)" if dips_arm else "kept (E78's primary on aifoundry3)",
            "dip_samples_removed": dips,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E141: reduce_e78.py unchanged via reduce_e141.py (blind pool 5's items; {arm or 'primary'})\n" + body)


if __name__ == "__main__":
    main()
