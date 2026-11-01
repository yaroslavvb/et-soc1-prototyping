#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E91 reduction (Q130): E78's registered reduction, reduce_e78.py, run UNCHANGED on E91's passes (aifoundry1 card 1),
with three substitutions, each registered in E91.md before any E91 data:

  1. E86's items and order installed on the shared e78_common module (e86_common.install(), exactly as
     reduce_e86.py does): E78's 51 kinds and the tie plus Q130(n)'s nine real tiles;
  2. the card-configuration pass gate accepts card 1's (tdp_w 65, temp_threshold_c 65), as reduce_e82.py does;
  3. PRIMARY: card 1's board-meter launch-gap dips are removed from the telemetry before the reduction reads it,
     with E82 amendment A2's definition, board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W, as reduce_e88.py
     does (E88's registered primary on this card). `--keep-dips` reduces the raw telemetry instead (the arm).

    python3 tools/claims-v3/kinds/reduce_e91.py <pass dir> ... --out e91.json [--keep-dips]
        [--csv] [--txt] [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]

Before it runs it checks reduce_e78.py, e78_common.py, kinds.json and e86_common.py against predictions-e91.json
and real.json against Q130(n)'s sha256, and refuses on any difference. After reduce_e78 writes --out, its
"experiment" becomes "E91" and a "reducer" block records the code, the hashes, the substitutions, the dip samples
removed per pass and every pass's raw config reads; the --txt file gets one header line.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e91.json")
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
                "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/kinds/e86_common.py"):
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e86_common as e86  # noqa: E402
    e = e86.check_real_json()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused code or real.json changed:\n  " + "\n  ".join(bad))
    keep = "--keep-dips" in sys.argv
    if keep:
        sys.argv.remove("--keep-dips")
    exp = reg["card"]["config_gate"]["expected"]
    e86.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install)

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
                            "e91_substitution": f"card-1 read equal to the registered ({exp['tdp_w']}, "
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
        res["experiment"] = "E91"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via "
                    "tools/claims-v3/kinds/reduce_e91.py",
            "reduce_e78_sha256": sha(os.path.join(HERE, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(HERE, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(HERE, "kinds.json")),
            "real_json_sha256": sha(e86.REAL_JSON),
            "e86_common_sha256": sha(os.path.join(HERE, "e86_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus the nine real tiles (e86_common.install)",
            "config_substitution": f"accepts card 1's ({exp['tdp_w']}, {exp['temp_threshold_c']}) where E78's gate "
                                   "accepts aifoundry3's (0, 65)",
            "dips": "kept (the registered arm)" if keep else "removed (E82 A2's definition; E91's registered primary)",
            "dip_samples_removed": dips,
            "config_reads_raw": raw_reads,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E91: reduce_e78.py unchanged via reduce_e91.py (E86's items; config gate at card "
                                  f"1's 65/65; dips {'kept' if keep else 'removed'})\n" + body)


if __name__ == "__main__":
    main()
