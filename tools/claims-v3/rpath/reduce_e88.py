#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E88 reduction (Q130): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E88's
passes with e88_common in e78_common's place, and two substitutions, both registered in E88.md before any E88 data:

  1. the card-configuration pass gate accepts card 1's (tdp_w 65, temp_threshold_c 65), as reduce_e82.py does;
  2. PRIMARY: card 1's board-meter launch-gap dips are removed from the telemetry before the reduction reads it,
     with E82 amendment A2's definition, board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W (E82 README result
     6: 85 such samples in 7 passes, two passes set aside by them). `--keep-dips` reduces the raw telemetry instead
     (the registered arm).

    python3 tools/claims-v3/rpath/reduce_e88.py <pass dir> ... --out e88-reduced.json [--keep-dips]
        [--csv] [--txt] [--leak auto|<k>] [--tau] [--delay] [--c-rb] [--no-refit]   (every reduce_e78.py option)

It checks reduce_e78.py's and e78_common.py's sha256 against predictions-e88.json before it runs.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(HERE, "..", "kinds")
DIP_W = 4.0


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def drop_dips(rows):
    """E82 A2: drop sample i when board_w[i] < min(board_w[i-2], board_w[i+2]) - 4 W. Returns (kept, n_dropped)."""
    B = [r.get("board_w") for r in rows]
    bad = set()
    for i in range(2, len(rows) - 2):
        if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - DIP_W:
            bad.add(i)
    return [r for i, r in enumerate(rows) if i not in bad], len(bad)


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e88.json")))
    want = reg["harness"]["reused_unchanged_sha256"]
    bad = [f"{rel}: {sha(os.path.join(ROOT, rel))} != {w}" for rel, w in want.items()
           if rel.endswith(("reduce_e78.py", "e78_common.py")) and sha(os.path.join(ROOT, rel)) != w]
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code changed:\n  " + "\n  ".join(bad))
    keep = "--keep-dips" in sys.argv
    if keep:
        sys.argv.remove("--keep-dips")
    exp = reg["card"]["config_gate"]["expected"]
    sys.path.insert(0, HERE)
    import e88_common  # noqa: E402
    sys.modules["e78_common"] = e88_common
    sys.path.insert(0, os.path.abspath(KINDS))
    import reduce_e78 as r  # noqa: E402

    dips = {}
    orig_load = r.load_jsonl

    def load_jsonl(path):
        rows = orig_load(path)
        if not keep and os.path.basename(path).startswith("telemetry.jsonl"):
            rows, n = drop_dips(rows)
            dips[os.path.dirname(path)] = n
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
            if isinstance(c, dict) and c.get("tdp_w") == exp["tdp_w"] and c.get("temp_threshold_c") == exp["temp_threshold_c"]:
                meta[nm] = {"tdp_w": 0, "temp_threshold_c": 65, "raw": c,
                            "e88_substitution": f"card-1 read equal to the registered ({exp['tdp_w']}, {exp['temp_threshold_c']})"}
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
        res["experiment"] = "E88"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via "
                    "tools/claims-v3/rpath/reduce_e88.py",
            "reduce_e78_sha256": sha(os.path.join(KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(KINDS, "e78_common.py")),
            "e88_common_sha256": sha(os.path.join(HERE, "e88_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "config_substitution": f"accepts card 1's ({exp['tdp_w']}, {exp['temp_threshold_c']})",
            "dips": "kept (the registered arm)" if keep else "removed (E82 A2's definition; the registered primary)",
            "dip_samples_removed": {os.path.basename(k): v for k, v in dips.items()},
            "config_reads_raw": raw_reads,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E88: reduce_e78.py unchanged via reduce_e88.py (config gate at card 1's 65/65; "
                                  f"dips {'kept' if keep else 'removed'})\n" + body)


if __name__ == "__main__":
    main()
