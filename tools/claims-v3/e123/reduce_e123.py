#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E123 reduction (Q134): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E123's passes
(aifoundry3 card 0), with two substitutions, each registered in E123.md before any E123 data (a port of
tools/claims-v3/kinds/reduce_e94.py; on aifoundry3 the card reads 0/65, which E78's configuration gate accepts as it
stands, so E94's card-1 substitution is dropped and the raw reads are only recorded):

  1. E123's items and order installed on the shared e78_common module (e123_common.install()): E78's 51 kinds and the
     tie plus E123's forty-two draws;
  2. PRIMARY: board-meter launch-gap dips are removed from the telemetry before the reduction reads it, with E82
     amendment A2's definition, board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W (E93's, E94's and E121's
     primary). `--keep-dips` reduces the raw telemetry instead (the arm).

`--gates-off` is one labelled arm of E123, never a verdict: E78's five PASS gates are opened (every per-run gate stays), so a
pass a gate would set aside is kept, to show how much the set-aside moved. E78's GATES dict is changed in memory only;
reduce_e78.py's bytes are unchanged and checked.

    python3 tools/claims-v3/e123/reduce_e123.py <pass dir> ... --out e123.json [--keep-dips] [--gates-off]
        [--csv] [--txt] [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]

E123's primary is --leak 0.1994, E78's own fit on this card, as E121's (collect_e123.sh passes it; E123.md says why).

Before it runs it checks reduce_e78.py, e78_common.py and kinds.json against predictions-e123.json and e123.json against
E123's freeze, and refuses on any difference. After reduce_e78 writes --out, its "experiment" becomes "E123" and a
"reducer" block records the code, the hashes, the substitution, the dip samples removed per pass and every pass's raw
config reads; the --txt file gets one header line.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KDIR = os.path.abspath(os.path.join(HERE, "..", "kinds"))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e123.json")
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
    import e123_common as e123  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)
    e = e123.check_e123_json()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused code or e123.json changed:\n  " + "\n  ".join(bad))
    keep = "--keep-dips" in sys.argv
    if keep:
        sys.argv.remove("--keep-dips")
    gates_off = "--gates-off" in sys.argv
    if gates_off:
        sys.argv.remove("--gates-off")
    e123.install()
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
        res["experiment"] = "E123"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via "
                    "tools/claims-v3/e123/reduce_e123.py",
            "reduce_e78_sha256": sha(os.path.join(KDIR, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(KDIR, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(KDIR, "kinds.json")),
            "e123_json_sha256": sha(e123.E123_JSON),
            "e123_common_sha256": sha(os.path.join(HERE, "e123_common.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus E123's forty-two draws (e123_common.install)",
            "pass_gates": "opened (the labelled gates-off arm)" if gates_off else "E78's, unchanged",
            "config_substitution": "none: aifoundry3 reads (0, 65), which E78's gate accepts as it stands",
            "dips": "kept (the registered arm)" if keep else "removed (E82 A2's definition; E123's registered primary, as E93's, E94's and E121's)",
            "dip_samples_removed": dips,
            "config_reads_raw": raw_reads,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E123: reduce_e78.py unchanged via reduce_e123.py (E123's items; aifoundry3's own "
                                  f"config gate; dips {'kept' if keep else 'removed'})\n" + body)


if __name__ == "__main__":
    main()
