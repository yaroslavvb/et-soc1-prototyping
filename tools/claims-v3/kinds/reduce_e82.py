#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E82 reduction (Q130): E78's registered reduction, reduce_e78.py, run UNCHANGED on aifoundry1 card 1's passes,
with one substitution in its card-configuration pass gate. Registration: tools/claims-v3/kinds/E82.md.

    python3 tools/claims-v3/kinds/reduce_e82.py <pass dir> ... --out e82.json [--csv] [--txt] [--leak auto|<k>]
        [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]          (every reduce_e78.py option, unchanged)

Why the substitution. reduce_e78.py sets a pass apart when an `ettelem config` read at either end of it shows a TDP
other than 0 or a threshold other than 65: aifoundry3's boot-time values. Card 1's are TDP 65 W and threshold 65 C
(every read since 25 Sep: e82_desk_checks.txt [4]), so the unchanged gate would set apart every E82 pass. This
wrapper wraps reduce_e78.runs_of_pass, which loads the two reads into the pass's meta: a read whose tdp_w and
temp_threshold_c equal the values predictions-e82.json registers for card 1 (65, 65) is handed to the gate as the
pair the gate accepts (0, 65), with the raw read kept beside it as config_start_raw / config_end_raw; a read that
differs is passed through untouched, so the gate sets the pass apart exactly as E78's would; an empty or failed read
stays unread, as in E78. Nothing else changes: every run gate, pass gate, interpolation, statistic and output key is
reduce_e78.py's, whose sha256 (and e78_common.py's) this wrapper checks against predictions-e82.json before it runs.
After reduce_e78 writes --out, its "experiment" becomes "E82" and a "reducer" block records the code, the hashes,
the substitution and every pass's raw reads; the --txt file gets one header line.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e82.json")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    reg = json.load(open(REG))
    want = reg["harness"]["reused_unchanged_sha256"]
    bad = []
    for rel in ("tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py",
                "tools/claims-v3/kinds/kinds.json"):
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code changed:\n  " + "\n  ".join(bad))
    exp = reg["card"]["config_gate"]["expected"]
    exp_tdp, exp_thr = exp["tdp_w"], exp["temp_threshold_c"]
    import reduce_e78 as r  # noqa: E402  (after the hash check)

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
            if isinstance(c, dict) and "tdp_w" in c and c.get("tdp_w") == exp_tdp \
                    and c.get("temp_threshold_c") == exp_thr:
                meta[nm] = {"tdp_w": 0, "temp_threshold_c": 65,
                            "e82_substitution": f"card-1 read equal to the registered ({exp_tdp}, {exp_thr})",
                            "raw": c}
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
        res["experiment"] = "E82"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged)",
            "reduce_e78_sha256": sha(os.path.join(HERE, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(HERE, "e78_common.py")),
            "wrapper": "tools/claims-v3/kinds/reduce_e82.py", "wrapper_sha256": sha(os.path.abspath(__file__)),
            "substitution": f"the config pass gate accepts card 1's registered (tdp_w {exp_tdp}, "
                            f"temp_threshold_c {exp_thr}) where E78's accepts aifoundry3's (0, 65)",
            "config_reads_raw": raw_reads,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write("E82: reduce_e78.py unchanged (config gate at card 1's registered 65 W / 65 C), "
                                  "via reduce_e82.py\n" + body)


if __name__ == "__main__":
    main()
