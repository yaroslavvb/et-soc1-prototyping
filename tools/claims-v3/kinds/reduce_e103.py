#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E103 reduction (Q132): E78's registered reduction, reduce_e78.py, run UNCHANGED on E103's passes (aifoundry1 card 1),
with three substitutions, each registered in E103.md before any E103 data (a port of reduce_e91.py):

  1. E103's items and order installed on the shared e78_common module (e103_common.install()): E78's 51 kinds and the
     tie plus E103's tiles;
  2. the card-configuration pass gate accepts card 1's (tdp_w 65, temp_threshold_c 65), as reduce_e82.py does;
  3. PRIMARY: card 1's board-meter launch-gap dips are removed from the telemetry before the reduction reads it,
     with E82 amendment A2's definition, board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W, as reduce_e88.py
     does (E88's registered primary on this card). `--keep-dips` reduces the raw telemetry instead (the arm).

`--gates-off` is one labelled arm of E103, never a verdict: E78's five PASS gates are opened (every per-run gate stays), so a
pass a gate would set aside is kept, to show how much the set-aside moved. E78's GATES dict is changed in memory only;
reduce_e78.py's bytes are unchanged and checked.

    python3 tools/claims-v3/kinds/reduce_e103.py <pass dir> ... --out e103.json [--keep-dips] [--gates-off]
        [--csv] [--txt] [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]

E103's primary is --leak 0.2414, E82's own slope on this card, as E93's (collect_e103.sh passes it; E103.md says why).

Before it runs it checks reduce_e78.py, e78_common.py and kinds.json against predictions-e103.json and e103.json against
E103's freeze, and refuses on any difference. After reduce_e78 writes --out, its "experiment" becomes "E103" and a "reducer" block records the code, the hashes, the substitutions, the dip samples
removed per pass and every pass's raw config reads; the --txt file gets one header line.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e103.json")
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
    import e103_common as e103  # noqa: E402
    e = e103.check_e103_json()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused code or e103.json changed:\n  " + "\n  ".join(bad))
    keep = "--keep-dips" in sys.argv
    if keep:
        sys.argv.remove("--keep-dips")
    gates_off = "--gates-off" in sys.argv
    if gates_off:
        sys.argv.remove("--gates-off")
    exp = reg["card"]["config_gate"]["expected"]
    e103.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install)
    if gates_off:
        r.GATES.update({"pass_max_failed_runs": 10 ** 6, "zero_mid_departure_w": 1e9, "zero_range_w": 1e9,
                        "tie_drift_w": 1e9, "random_range_w": 1e9})

    dips = {}
    orig_load = r.load_jsonl

    def load_jsonl(path):
        rows = orig_load(path)
        if not keep and os.path.basename(path).startswith("telemetry.jsonl"):
            rows2, idx = drop_dips(rows)
            dips[os.path.basename(os.path.dirname(path))] = {
                "samples_removed": len(idx),
                "t_ms": [rows[i].get("t_ms") for i in idx][:200],
            }
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
            if isinstance(c, dict) and "tdp_w" in c and c.get("tdp_w") == exp["tdp_w"] \
                    and c.get("temp_threshold_c") == exp["temp_threshold_c"]:
                meta[nm] = {"tdp_w": 0, "temp_threshold_c": 65, "raw": c,
                            "e103_substitution": f"card-1 read equal to the registered ({exp['tdp_w']}, "
                                                f"{exp['temp_threshold_c']})"}
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
        res["experiment"] = "E103"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via "
                    "tools/claims-v3/kinds/reduce_e103.py",
            "reduce_e78_sha256": sha(os.path.join(HERE, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(HERE, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(HERE, "kinds.json")),
            "e103_json_sha256": sha(e103.E103_JSON),
            "e103_common_sha256": sha(os.path.join(HERE, "e103_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus E103's tiles (e103_common.install)",
            "pass_gates": "opened (the labelled gates-off arm)" if gates_off else "E78's, unchanged",
            "config_substitution": f"accepts card 1's ({exp['tdp_w']}, {exp['temp_threshold_c']}) where E78's gate "
                                   "accepts aifoundry3's (0, 65)",
            "dips": "kept (the registered arm)" if keep else "removed (E82 A2's definition; E103's registered primary, as E88's, E91's and E93's)",
            "dip_samples_removed": dips,
            "config_reads_raw": raw_reads,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E103: reduce_e78.py unchanged via reduce_e103.py (E103's items; config gate at card "
                                  f"1's 65/65; dips {'kept' if keep else 'removed'})\n" + body)


if __name__ == "__main__":
    main()
