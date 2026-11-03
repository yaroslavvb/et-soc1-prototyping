#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(u), post hoc checks beside fit_m7u.py:

  (a) E140's registered scorer (tools/claims-v3/e140/score_e140.py, its frozen M6/M5 predictions for pool 4), unchanged, on the
      committed reduction and on the footing's;
  (b) F4: E82 A2's dips counted in every sampler line of aifoundry2's burst sessions (E143, and E80/E83 that M7's aifoundry2
      term was fitted on), and inside the bursts' sampled windows where the run records give them;
  (c) the passes each experiment kept, committed against footing.

    python3 checks_footing.py        (writes checks-footing.json here)
"""
import glob
import gzip
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
CV = os.path.join(ROOT, "tools", "claims-v3")
sys.path.insert(0, HERE)
import reduce_footing as RF  # noqa: E402

load = lambda p: json.load(open(p))


def e140():
    out = {}
    for lab, meas in (("committed", os.path.join(DD, "2026-11-02-e140-blind4", "e140.json")),
                      ("footing", os.path.join(HERE, "reduced", "e140-footing.json"))):
        js = os.path.join(HERE, "score", f"scored-E140_{lab}_frozen.json")
        r = subprocess.run([sys.executable, os.path.join(CV, "e140", "score_e140.py"), "--e140", meas, "--json", js],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            out[lab] = {"rc": r.returncode, "err": r.stderr[-800:]}
            continue
        s = load(js)
        s = s.get("primary", s)
        out[lab] = {"leak": (s.get("leak") or {}).get("k_w_per_c"), "passes": s.get("passes"),
                    "rules": {k: {x: v.get(x) for x in ("verdict", "rms", "rms_w", "value", "bias", "bias_meas_minus_pred_w",
                                                       "inside", "n", "d_rms_w", "lo95", "hi95", "interval") if x in v}
                              for k, v in (s.get("rules") or {}).items() if isinstance(v, dict)},
                    "reported": s.get("reported")}
    return out


def a2_dips():
    out = {}
    for lab, d in (("E143", "2026-11-02-e143-blind5-aifoundry2"), ("E80", "2026-10-31-e80-kinds-speed"),
                   ("E83", "2026-10-31-e83-kinds-speed-rest")):
        files = sorted(set(glob.glob(os.path.join(DD, d, "**", "tel", "*.jsonl*"), recursive=True)))
        n = nd = 0
        worst = []
        for p in files:
            op = gzip.open if p.endswith(".gz") else open
            recs = []
            with op(p, "rt") as f:
                for ln in f:
                    if ln.startswith("{"):
                        try:
                            recs.append(json.loads(ln))
                        except ValueError:
                            pass
            _, bad = RF.drop_dips(recs)
            n += len(recs)
            nd += len(bad)
            for i in bad[:3]:
                worst.append({"file": os.path.relpath(p, ROOT), "i": i, "board_w": recs[i].get("board_w"),
                              "neighbours_w": [recs[i - 2].get("board_w"), recs[i + 2].get("board_w")]})
        out[lab] = {"tel_files": len(files), "samples": n, "a2_dips": nd, "examples": worst[:6]}
    return out


def passes():
    out = {}
    for e in RF.EXPS:
        c = load(os.path.join(DD, RF.EXPS[e][0], e.lower() + ".json"))
        f = load(os.path.join(HERE, "reduced", f"{e.lower()}-footing.json"))
        out[e] = {"card": RF.EXPS[e][1], "dips": RF.EXPS[e][3],
                  "committed": {"k": c["leak"]["k_w_per_c"], "passes": c["passes"], "kept_runs": f"{c['kept']}/{c['runs']}"},
                  "footing": {"k": f["leak"]["k_w_per_c"], "passes": f["passes"], "kept_runs": f"{f['kept']}/{f['runs']}",
                              "set_aside": f["passes_set_aside"]}}
    return out


def main():
    res = {"e140": e140(), "f4_a2_dips_aifoundry2": a2_dips(), "passes": passes()}
    json.dump(res, open(os.path.join(HERE, "checks-footing.json"), "w"), indent=1, default=float)
    for lab, v in res["e140"].items():
        print("E140", lab, v.get("leak"), v.get("passes"), json.dumps(v.get("rules"))[:1500] if v.get("rules") else v)
    for lab, v in res["f4_a2_dips_aifoundry2"].items():
        print("F4", lab, {k: v[k] for k in ("tel_files", "samples", "a2_dips")}, v["examples"][:2])
    for e, v in res["passes"].items():
        print("passes", e, v["committed"]["k"], v["committed"]["passes"], v["committed"]["kept_runs"], "->", v["footing"]["passes"],
              v["footing"]["kept_runs"], v["footing"]["set_aside"] or "")


if __name__ == "__main__":
    main()
