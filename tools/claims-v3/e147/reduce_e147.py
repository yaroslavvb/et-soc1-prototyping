#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E147 reduction (Q138): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E147's blocks
(aifoundry3 card 0), with E147's items installed on the shared e78_common module (e147_common.install(): E78's 51 kinds and
the tie plus E147's 73 fp32 tiles), so that the per-run gates (600 MHz, the voltage band, the records, cycles per op, the
window's samples and duty, the dumped tile equal to the item's registered sha256) and every per-run quantity (p_raw, p80,
rail_raw, the rate) are E78's own. E147's blocks are trains with no anchors and no tie, so E78's anchor and tie pass gates
have nothing to act on; its failed-run and configuration gates still apply. The step over each item's OWN zero and every
rule are score_e147.py's, from the per-run table this writes (--csv). A port of tools/claims-v3/e134/reduce_e134.py (itself
E127's), each arm registered in README.md before any E147 data; the one change is the dip line, --dip-w (E147 change 1):

  --drop-dips   the board-meter dips removed from the telemetry before the reduction reads it, with E82 amendment A2's
                definition, board_w[i] < min(board_w[i-2], board_w[i+2]) - DIP_W (E86's, E95's, E103's and E134's arm).
  --dip-w W     the dip line, default 2.0 W (E147 change 1: E134's correction C1 found 2-4 W meter dips under E82 A2's 4 W
                line setting aside E134's first A block and widening its R2, and asked that a re-run register a line that
                catches them first). E147's REGISTERED PRIMARY is --drop-dips at 2.0 W; --dip-w 4.0 is E134's own line (the
                labelled frame arm); without --drop-dips, the dips-kept arm.
  --gates-off   E78's five pass gates opened in memory (every per-run gate stays), to show what the set-aside moved; the
                labelled gates-off arm (with score_e147.py's train gate off too).

    python3 tools/claims-v3/e147/reduce_e147.py <pass dir> ... --out e147.json [--drop-dips] [--gates-off]
        [--csv] [--txt] [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]   (every reduce_e78.py option)

Before it runs it checks reduce_e78.py, e78_common.py and kinds.json against predictions-e147.json (E78's freeze values) and
E147's tile manifest against its frozen sha256, and refuses on any difference. After reduce_e78 writes --out, its
"experiment" becomes "E147" and a "reducer" block records the code, the hashes and the arm; the --txt file gets a header line.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e147.json")
DIP_W = 2.0          # E147 change 1 (E134 C1); E82 A2's and E134's 4.0 W is the frame arm (--dip-w 4.0)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def drop_dips(rows):
    """E82 A2's rule at the line DIP_W: drop sample i when board_w[i] < min(board_w[i-2], board_w[i+2]) - DIP_W.
    Returns (kept, dropped idx)."""
    B = [r.get("board_w") for r in rows]
    bad = set()
    for i in range(2, len(rows) - 2):
        if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - DIP_W:
            bad.add(i)
    return [r for i, r in enumerate(rows) if i not in bad], sorted(bad)


def main():
    reg = json.load(open(REG))
    want = reg["harness"]["reused_unchanged_sha256"]
    bad = []
    for rel in ("tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py",
                "tools/claims-v3/kinds/kinds.json"):
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e147_common as e147  # noqa: E402
    tj = "tools/claims-v3/e147/e147/e147-tiles.json"
    if sha(os.path.join(ROOT, tj)) != reg["harness"]["e147_tiles_sha256"][tj]:
        bad.append(f"{tj}: sha256 differs from the freeze")
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code or E147's tile manifest changed:\n  " + "\n  ".join(bad))
    dips_arm = "--drop-dips" in sys.argv
    if dips_arm:
        sys.argv.remove("--drop-dips")
    global DIP_W
    if "--dip-w" in sys.argv:                                    # E147 change 1
        i = sys.argv.index("--dip-w")
        DIP_W = float(sys.argv[i + 1])
        del sys.argv[i:i + 2]
    gates_off = "--gates-off" in sys.argv
    if gates_off:
        sys.argv.remove("--gates-off")
    e147.install()
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
    arm = (f"dips removed (E82 A2's rule at {DIP_W:g} W)" if dips_arm else "") + (" + " if dips_arm and gates_off else "") + \
          ("pass gates opened" if gates_off else "")
    if out_path and os.path.exists(out_path):
        res = json.load(open(out_path))
        res["experiment"] = "E147"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e147/reduce_e147.py",
            "reduce_e78_sha256": sha(os.path.join(e147.KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(e147.KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(e147.KINDS, "kinds.json")),
            "e147_tiles_json_sha256": sha(e147.TILES_JSON),
            "e147_common_sha256": sha(os.path.join(HERE, "e147_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus E147's 73 fp32 tiles (e147_common.install)",
            "dip_line_w": DIP_W if dips_arm else None,
            "arm": arm or "primary (nothing changed)",
            "pass_gates": "opened (the labelled gates-off arm)" if gates_off else "E78's, unchanged",
            "dips": f"removed (E82 A2's definition at {DIP_W:g} W)" if dips_arm else "kept (the labelled dips-kept arm)",
            "dip_samples_removed": dips,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E147: reduce_e78.py unchanged via reduce_e147.py (E147's items; {arm or 'primary'})\n" + body)


if __name__ == "__main__":
    main()
