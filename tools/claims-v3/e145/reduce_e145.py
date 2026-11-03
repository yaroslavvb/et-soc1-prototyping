#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E145 reduction (Q138; a port of E138's reduce_e138.py with E137's card-1 configuration gate): E78's registered reduction,
tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E145's blocks (aifoundry1 card 1), with E145's items installed on the shared
e78_common module (e145_common.install(): E78's 51 kinds and the tie plus Q136(a)'s 26 tiles), so that the per-run gates (600 MHz, the voltage band, the records, cycles per op, the
window's samples and duty, the dumped tile equal to the item's registered sha256) and every per-run quantity (p_raw, p80,
rail_raw, the rate) are E78's own. E130's blocks are trains with no anchors and no tie, so E78's anchor and tie pass gates
have nothing to act on; its failed-run and configuration gates still apply. The step over each item's OWN zero and every
rule are score_e145.py's, from the per-run table this writes (--csv). E145's one change from reduce_e138.py (E137's change 2, from
reduce_e137.py): E78's card-configuration pass gate accepts card 1's reads (tdp_w 65, temp_threshold_c 65), where it accepts
aifoundry3's (0, 65); the raw reads are kept in the output. Each arm registered in README.md before any E145 data:

  --drop-dips   the board-meter dips removed from the telemetry before the reduction reads it, with E82 amendment A2's
                definition, board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W (E86's, E95's and E103's arm). E145's
                REGISTERED PRIMARY (E138's, and card 1's board meter reads launch gaps, E82 A2); without it, the dips-kept arm.
  --gates-off   E78's five pass gates opened in memory (every per-run gate stays), to show what the set-aside moved; the
                labelled gates-off arm (with score_e145.py's train gate off too).

    python3 tools/claims-v3/e145/reduce_e145.py <pass dir> ... --out e145.json [--drop-dips] [--gates-off]
        [--csv] [--txt] [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]   (every reduce_e78.py option)

Before it runs it checks reduce_e78.py, e78_common.py and kinds.json against predictions-e145.json (E78's freeze values) and
Q136(a)'s tile manifest against its frozen sha256, and refuses on any difference. After reduce_e78 writes --out, its
"experiment" becomes "E145" and a "reducer" block records the code, the hashes and the arm; the --txt file gets a header line.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e145.json")
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
    want = reg["harness"]["reused_unchanged_sha256"]
    bad = []
    for rel in ("tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py",
                "tools/claims-v3/kinds/kinds.json"):
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e145_common as e130  # noqa: E402
    e = e130.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code or Q136(a)'s tile manifest changed:\n  " + "\n  ".join(bad))
    dips_arm = "--drop-dips" in sys.argv
    if dips_arm:
        sys.argv.remove("--drop-dips")
    gates_off = "--gates-off" in sys.argv
    if gates_off:
        sys.argv.remove("--gates-off")
    e130.install()
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
    exp = reg["card"]["config_gate"]["expected"]                                    # E145: card 1's configuration
    raw_reads = {}
    orig_rop = r.runs_of_pass

    def runs_of_pass(d, by, a):
        out, meta = orig_rop(d, by, a)
        if not meta:
            return out, meta
        p = out[0]["pass"] if out else os.path.basename(d.rstrip("/"))
        raw_reads[str(p)] = {}
        for nm in ("config_start", "config_end"):
            c = meta.get(nm)
            meta[nm + "_raw"] = c
            raw_reads[str(p)][nm] = c
            if isinstance(c, dict) and "tdp_w" in c and c.get("tdp_w") == exp["tdp_w"] \
                    and c.get("temp_threshold_c") == exp["temp_threshold_c"]:
                meta[nm] = {"tdp_w": 0, "temp_threshold_c": 65, "raw": c,
                            "e145_substitution": f"card-1 read equal to the registered ({exp['tdp_w']}, {exp['temp_threshold_c']})"}
        return out, meta

    r.runs_of_pass = runs_of_pass
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
        res["experiment"] = "E145"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e145/reduce_e145.py",
            "reduce_e78_sha256": sha(os.path.join(e130.KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(e130.KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(e130.KINDS, "kinds.json")),
            "e130_items_json_sha256": sha(e130.ITEMS_JSON),
            "e145_common_sha256": sha(os.path.join(HERE, "e145_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus Q136(a)'s 26 tiles (e145_common.install)",
            "config_substitution": f"accepts card 1's ({exp['tdp_w']}, {exp['temp_threshold_c']}) where E78's gate accepts aifoundry3's (0, 65)",
            "config_reads_raw": raw_reads,
            "arm": arm or "primary (nothing changed)",
            "pass_gates": "opened (the labelled gates-off arm)" if gates_off else "E78's, unchanged",
            "dips": "removed (E82 A2's definition; the labelled dips arm)" if dips_arm else "kept (the labelled dips-kept arm)",
            "dip_samples_removed": dips,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E145: reduce_e78.py unchanged via reduce_e145.py (E145's items; config gate at card 1's 65/65; {arm or 'primary'})\n" + body)


if __name__ == "__main__":
    main()
