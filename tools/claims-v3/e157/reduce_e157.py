#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E157 reduction (Q139): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED on E157's passes (blind pool 6 and
K1's six pool-5 tiles on aifoundry1 card 1), with card 1's frame. A port of tools/claims-v3/e142/reduce_e142.py (E142, pool 5 on this card),
whose changes 2-5 it keeps; E157's are marked:

  1. (E157) E157's items and order installed on the shared e78_common module (e157_common.install(), as reduce_e142.py installs E142's);
  2. the card-configuration pass gate accepts card 1's (tdp_w 65, temp_threshold_c 65): a read equal to that is handed to E78's gate as the
     (0, 65) it accepts, the raw read kept beside it (E82's substitution, E131's and E142's change 2, unchanged);
  3. card 1's board-meter launch-gap dips removed from the telemetry before the reduction reads it, E82 amendment A2's definition,
     board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W, once (Q139(u)'s footing F2; E142's change 3, unchanged); --keep-dips reduces the
     raw telemetry (an arm);
  4. (E157) the leakage slope is the caller's --leak: the registered primary is Q139(u)'s frozen card-1 slope, 0.3134106532552718 W/C
     (docs/reports/data/2026-11-03-q139u-footing/footing.json > slopes.c1, reduce_footing.K_FROZEN["c1"]), with --no-refit, as
     reduce_footing.reduce runs every registered reducer; E142's footing (0.2414, E82's frozen slope) and the session's own fit (auto)
     are arms (collect_e157.sh);
  5. --relax-anchors (E131's change 5, unchanged): reduce_e78's anchor and tie pass gates raised to 99 W, every other gate E78's. A reported
     reading only.

    python3 tools/claims-v3/e157/reduce_e157.py <pass dir> ... --leak 0.3134106532552718 --no-refit --out e157.json [--keep-dips]
        [--relax-anchors] [--csv] [--txt] [--tau 0.95] [--delay 0.2] [--c-rb 0.81]          (every other argument is reduce_e78.py's)

Before it runs it checks reduce_e78.py, e78_common.py, kinds.json and e157_common.py against predictions-e157.json, and blind pool 6's and
pool 5's frozen files through e157_common's own check, and refuses on any difference. After reduce_e78 writes --out, its "experiment" becomes
"E157" and a "reducer" block records the code, the hashes, the substitutions, the gates, the dip samples removed per pass and every pass's raw
config reads; the --txt file gets one header line.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, K)
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e157.json")
DIP_W = 4.0
CARD1 = {"tdp_w": 65, "temp_threshold_c": 65}
RELAXED_GATES = {"zero_mid_departure_w": 99.0, "zero_range_w": 99.0, "random_range_w": 99.0, "tie_drift_w": 99.0}


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
    want.update(reg["harness"]["e157_card_files_sha256"])
    bad = []
    for rel in ("tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py",
                "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e157/e157_common.py"):
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e157_common as e157  # noqa: E402
    e = e157.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused code or a frozen file changed:\n  " + "\n  ".join(bad))
    keep = "--keep-dips" in sys.argv
    if keep:
        sys.argv.remove("--keep-dips")
    relax = "--relax-anchors" in sys.argv
    if relax:
        sys.argv.remove("--relax-anchors")
    e157.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install)
    if relax:                                                                     # E142 change 5
        for g, v in RELAXED_GATES.items():
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
            if isinstance(c, dict) and "tdp_w" in c and c.get("tdp_w") == CARD1["tdp_w"] \
                    and c.get("temp_threshold_c") == CARD1["temp_threshold_c"]:
                meta[nm] = {"tdp_w": 0, "temp_threshold_c": 65, "raw": c,
                            "e157_substitution": f"card-1 read equal to the registered ({CARD1['tdp_w']}, "
                                                 f"{CARD1['temp_threshold_c']})"}
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
        res["experiment"] = "E157"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e157/reduce_e157.py",
            "reduce_e78_sha256": sha(os.path.join(K, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(K, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(K, "kinds.json")),
            "e157_common_sha256": sha(os.path.join(HERE, "e157_common.py")),
            "blind6_json_sha256": sha(e157.POOL_JSON),
            "blind5_json_sha256": sha(e157.K1_JSON),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus blind pool 6's 50 tiles and K1's six pool-5 tiles (e157_common.install)",
            "config_substitution": f"accepts card 1's ({CARD1['tdp_w']}, {CARD1['temp_threshold_c']}) where E78's gate "
                                   "accepts aifoundry3's (0, 65)",
            "dips": "kept (an arm)" if keep else "removed (E82 A2's definition, once; Q139(u)'s footing F2)",
            "relaxed_anchor_gates": relax,
            "gates": dict(r.GATES),
            "dip_samples_removed": dips,
            "config_reads_raw": raw_reads,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E157: reduce_e78.py unchanged via reduce_e157.py (blind pool 6's and K1's items; config gate at card 1's 65/65; "
                                  f"dips {'kept' if keep else 'removed'}; anchor and tie gates {'relaxed to 99 W' if relax else 'E78s'})\n"
                                  + body)


if __name__ == "__main__":
    main()
