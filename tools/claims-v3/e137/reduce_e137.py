#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E137 reduction (Q137): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E137's passes (aifoundry1 card 1).
A port of tools/claims-v3/e128/reduce_e128.py, with E131's set-aside reading added; each change from reduce_e128.py marked E137:

  1. E137's items and order installed on the shared e78_common module (e137_common.install()): E78's 51 kinds and the tie plus E128's seven
     fp16 sign tiles (E137);
  2. the card-configuration pass gate accepts card 1's (tdp_w 65, temp_threshold_c 65), as reduce_e128.py does;
  3. PRIMARY: card 1's board-meter launch-gap dips removed (E82 A2's definition, board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W), as
     reduce_e128.py; `--keep-dips` reduces the raw telemetry instead (an arm);
  4. E137: --relax-anchors, the reduction E137's set-aside rule reads (E137.md, "The set-aside rule"; predictions-e137.json > set_aside_rule):
     reduce_e78's anchor and tie pass gates raised to 99 W, every other gate E78's, as reduce_e131.py. It never carries a verdict by itself.
`--gates-off` is reduce_e128.py's labelled arm, kept.

    python3 tools/claims-v3/e137/reduce_e137.py <pass dir> ... --leak 0.2414 --out e137.json [--keep-dips] [--gates-off] [--relax-anchors]
        [--csv] [--txt] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]          (every other argument is reduce_e78.py's)

Before it runs it checks reduce_e78.py, e78_common.py and kinds.json against predictions-e137.json and E128's e128.json against E128's freeze, and
refuses on any difference.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
KINDS = os.path.abspath(os.path.join(HERE, "..", "kinds"))
REG = os.path.join(HERE, "predictions-e137.json")
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
    import e137_common as e137  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)
    e = e137.check_e128_json()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused code or E128's e128.json changed:\n  " + "\n  ".join(bad))
    keep = "--keep-dips" in sys.argv
    if keep:
        sys.argv.remove("--keep-dips")
    gates_off = "--gates-off" in sys.argv
    if gates_off:
        sys.argv.remove("--gates-off")
    relax = "--relax-anchors" in sys.argv                                           # E137 change 4
    if relax:
        sys.argv.remove("--relax-anchors")
    exp = reg["card"]["config_gate"]["expected"]
    e137.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install)
    if gates_off:
        r.GATES.update({"pass_max_failed_runs": 10 ** 6, "zero_mid_departure_w": 1e9, "zero_range_w": 1e9,
                        "tie_drift_w": 1e9, "random_range_w": 1e9})
    if relax:                                                                       # E137 change 4
        for g, v in reg["set_aside_rule"]["relaxed_reduction_gates"].items():
            r.GATES[g] = v

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
                            "e137_substitution": f"card-1 read equal to the registered ({exp['tdp_w']}, "
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
        res["experiment"] = "E137"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via "
                    "tools/claims-v3/e137/reduce_e137.py",
            "reduce_e78_sha256": sha(os.path.join(KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(KINDS, "kinds.json")),
            "e128_json_sha256": sha(e137.E128_JSON),
            "e137_common_sha256": sha(os.path.join(HERE, "e137_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus E128's seven fp16 sign tiles (e137_common.install)",
            "pass_gates": "opened (the labelled gates-off arm)" if gates_off else ("anchor and tie gates relaxed to 99 W (the set-aside rule's reading)" if relax else "E78's, unchanged"),
            "relaxed_anchor_gates": relax,
            "config_substitution": f"accepts card 1's ({exp['tdp_w']}, {exp['temp_threshold_c']}) where E78's gate "
                                   "accepts aifoundry3's (0, 65)",
            "dips": "kept (the registered arm)" if keep else "removed (E82 A2's definition; E137's registered primary, as E128's)",
            "dip_samples_removed": dips,
            "config_reads_raw": raw_reads,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E137: reduce_e78.py unchanged via reduce_e137.py (E137's items; config gate at card "
                                  f"1's 65/65; dips {'kept' if keep else 'removed'}; anchor and tie gates {'relaxed to 99 W' if relax else 'E78s'})\n" + body)


if __name__ == "__main__":
    main()
