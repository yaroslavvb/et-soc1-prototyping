#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E148 reduction (Q138): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED (sha256 checked against
predictions-e148.json), on E148's passes (aifoundry1 card 1), with E148's items and card 1's frame as E124 registered it. A port of
tools/claims-v3/e124/reduce_e124.py, each change marked E148:

  1. E148's items installed (e148_common.install_for_reduce: an arm's item is typed "<arm>:<format>", so its D is over the format's zeros and it has no
     cycle gate) - E148 change;
  2. the card-configuration pass gate accepts card 1's (tdp_w 65, temp_threshold_c 65): a read equal to that is handed to E78's gate as the (0, 65) it
     accepts, the raw read kept beside it (E82's substitution, as E124's);
  3. PRIMARY: card 1's board-meter launch-gap dips removed from the telemetry before the reduction reads it, E82 amendment A2's definition,
     board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W (E124's primary); --keep-dips reduces the raw telemetry (a reported arm);
  4. --relax-tie: E148's registered set-aside rule (E148.md; predictions-e148.json › set_aside_rule): GATES["tie_drift_w"] 0.60 -> 99 W, every other
     gate E78's (pi enters no E148 statistic but its own tie cell). Used for the verdicts only as the set-aside rule says; always reported - E148 change.

    uv run tools/claims-v3/e148/reduce_e148.py <pass dir> [...] --leak 0.2414 --out e148.json [--csv runs.csv] [--txt reduce.txt]
        [--keep-dips] [--relax-tie] [--no-refit]           (every other argument is reduce_e78.py's)

E148's primary is --leak 0.2414 (E82's own slope on this card, E93's and E124's choice); pipeline_e148.sh passes it. After reduce_e78 writes --out, its
"experiment" becomes "E148" and a "reducer" block records the code, the hashes, the substitutions, the dip samples removed per pass and every pass's raw
config reads; the --txt file gets one header line.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kinds"))
REG = os.path.join(HERE, "predictions-e148.json")
DIP_W = 4.0


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def drop_dips(rows):
    """E82 A2 (as reduce_e93.drop_dips and reduce_e124.drop_dips): drop sample i when board_w[i] < min(board_w[i-2], board_w[i+2]) - 4 W."""
    B = [r.get("board_w") for r in rows]
    bad = set()
    for i in range(2, len(rows) - 2):
        if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - DIP_W:
            bad.add(i)
    return [r for i, r in enumerate(rows) if i not in bad], sorted(bad)


def main():
    reg = json.load(open(REG))
    bad = []
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: sha256 {have} != registered {want}")
    if bad:
        raise SystemExit("refusing to reduce - a reused file changed:\n  " + "\n  ".join(bad))
    keep = "--keep-dips" in sys.argv
    if keep:
        sys.argv.remove("--keep-dips")
    relax = "--relax-tie" in sys.argv
    if relax:
        sys.argv.remove("--relax-tie")
    exp = reg["card"]["config_gate"]["expected"]
    import e148_common as e148  # noqa: E402
    e148.install_for_reduce()
    import reduce_e78 as r  # noqa: E402  (after the check and the install)
    if relax:
        r.GATES["tie_drift_w"] = reg["set_aside_rule"]["relaxed_gate"]["tie_drift_w"]

    dips = {}
    orig_load = r.load_jsonl

    def load_jsonl(path):
        rows = orig_load(path)
        if not keep and os.path.basename(path).startswith("telemetry.jsonl"):
            rows2, idx = drop_dips(rows)
            dips[os.path.basename(os.path.dirname(path))] = {"samples_removed": len(idx), "t_ms": [rows[i].get("t_ms") for i in idx][:200]}
            rows = rows2
        return rows

    r.load_jsonl = load_jsonl
    raw_reads = {}
    orig = r.runs_of_pass

    def runs_of_pass(d, by, a):
        out, meta = orig(d, by, a)
        if not meta:
            return out, meta
        p = out[0]["pass"] if out else os.path.basename(d.rstrip("/"))
        raw_reads[str(p)] = {}
        for nm in ("config_start", "config_end"):
            c = meta.get(nm)
            meta[nm + "_raw"] = c
            raw_reads[str(p)][nm] = c
            if isinstance(c, dict) and "tdp_w" in c and c.get("tdp_w") == exp["tdp_w"] and c.get("temp_threshold_c") == exp["temp_threshold_c"]:
                meta[nm] = {"tdp_w": 0, "temp_threshold_c": 65, "raw": c,
                            "e148_substitution": f"card-1 read equal to the registered ({exp['tdp_w']}, {exp['temp_threshold_c']})"}
        return out, meta

    r.runs_of_pass = runs_of_pass
    out_path = txt_path = None
    for i, x in enumerate(sys.argv):
        if x == "--out" and i + 1 < len(sys.argv):
            out_path = sys.argv[i + 1]
        if x == "--txt" and i + 1 < len(sys.argv):
            txt_path = sys.argv[i + 1]
    r.main()
    if out_path and os.path.exists(out_path):
        res = json.load(open(out_path))
        res["experiment"] = "E148"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e148/reduce_e148.py",
            "reduce_e78_sha256": sha(os.path.join(ROOT, "tools/claims-v3/kinds/reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(ROOT, "tools/claims-v3/kinds/e78_common.py")),
            "e148_common_sha256": sha(os.path.join(HERE, "e148_common.py")),
            "kinds_json_sha256": sha(os.path.join(ROOT, "tools/claims-v3/kinds/kinds.json")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "E148's (e148_common.install_for_reduce)",
            "config_substitution": f"accepts card 1's ({exp['tdp_w']}, {exp['temp_threshold_c']}) where E78's gate accepts aifoundry3's (0, 65)",
            "dips": "kept (an arm)" if keep else "removed (E82 A2's definition; E124's primary on this card)",
            "tie_drift_w": r.GATES["tie_drift_w"],
            "set_aside_rule_applied": relax,
            "dip_samples_removed": dips,
            "config_reads_raw": raw_reads,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E148: reduce_e78.py unchanged via reduce_e148.py (E148's items; config gate at card 1's 65/65; dips "
                                  f"{'kept' if keep else 'removed'}; tie_drift_w {r.GATES['tie_drift_w']})\n" + body)


if __name__ == "__main__":
    main()
