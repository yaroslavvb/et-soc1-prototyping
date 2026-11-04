#!/usr/bin/env python3
"""E163 (Q141): rank 14's re-run tiles, picked by the rules E163.md registers, and the earlier values each is compared with. Desk
only, from committed files of earlier runs (no E163 data exists); writes rerun-ref.json and, for E152, its committed passes re-reduced
on Q139(u)'s footing in rerun-ref/.

  pool 5 (E141, aifoundry3): of the 24 non-anchor pool-5 tiles E153's K1 did not re-run, per format in proportion (fp32 4 of 10,
      fp16 3 of 7, int8 3 of 7), those whose D on Q139(u)'s footing (docs/reports/data/2026-11-03-q139u-footing/reduced/
      e141-footing.json) has the smallest standard error, ties by name; compared with that D (the primary) and with E141's own
      session footing (e141.json, beside)
  E152 (aifoundry3): its six committed passes re-reduced on Q139(u)'s footing by E152's own reducer, unchanged
      (tools/claims-v3/e152/reduce_e152.py --leak 0.20563713796102187 --no-refit --drop-dips); of its 11 tiles the 6 with the smallest
      standard error of D on that footing, ties by name; compared with that D (primary) and with E152's committed dips-kept arm
      (leakage auto, dips kept: e152-dipskept.json, the session-own reading beside)
  E151 (aifoundry3, trains): the six bits of its registered odd-even contrast, int8.b1_0 .. int8.b1_5 (e151_common.B_TWICE); each
      tile's step over its own zero on the minion rail, board-equivalent (rail / c_rb 0.81), per kept B block, from E151's committed
      reduction (runs.csv, e151.json: its registered primary, dips removed and its rail filter on) through E151's own Book
      (score_e151 -> score_e145 -> score_e130, unchanged); mean, se and n over its eight kept B blocks

    python3 -B tools/claims-v3/e163/rerun_ref_e163.py      # numpy is needed for the E152 re-reduction (reduce_e78.py)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e163 as S  # noqa: E402

DD = "docs/reports/data"
E141F = f"{DD}/2026-11-03-q139u-footing/reduced/e141-footing.json"
E141S = f"{DD}/2026-11-02-e141-blind5-aifoundry3/e141.json"
P5 = "tools/claims-v3/kinds/blind5/blind5.json"
E152D = f"{DD}/2026-11-03-e152-gate-dose"
E152T = "tools/claims-v3/e152/e152-tiles.json"
E151D = f"{DD}/2026-11-03-e151-int8-b-aifoundry3"
K1 = ("fp32.b_exp_busy_a_const", "fp32.real_pythia_ln1_q", "fp16.sparse24_aligned", "fp16.exp_only", "int8.gray_a",
      "int8.b_line_zero_one")
POOL5_TAKE = {"fp32": 4, "fp16": 3, "int8": 3}
KF = "0.20563713796102187"
E151_TILES = tuple(f"int8.b1_{j}" for j in range(6))
E151_REPORTED = ("int8.b1_6", "int8.b1_7", "int8.b2_7", "int8.b1d_7")
CHAIN = ("tools/claims-v3/e151/score_e151.py", "tools/claims-v3/e145/score_e145.py", "tools/claims-v3/e138/score_e138.py",
         "tools/claims-v3/e130/score_e130.py", "tools/claims-v3/e151/predictions-e151.json", "tools/claims-v3/e151/e130-items.json",
         "tools/claims-v3/e145/e130-items.json", "tools/claims-v3/e138/e130-items.json")


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def J(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def dval(items, name):
    k = name if name in items else name.split(".", 1)[1]
    d = items[k]["D"]
    return {x: d[x] for x in ("mean", "se", "n", "ci95")}


def main():
    out = {"_what": "E163 (Q141): rank 14's re-run tiles, picked by E163.md's rules from committed files of earlier runs, with the "
                    "earlier D each is compared with (primary: Q139(u)'s footing; beside: the earlier session's own)", "sources": {}}
    # pool 5
    e141f, e141s = J(E141F)["items"], J(E141S)["items"]
    pool = J(P5)["tiles"]
    cand = [t for t in pool if not t.get("anchor") and t["name"] not in K1]
    assert len(cand) == 24, len(cand)
    pick5 = []
    for f in ("fp32", "fp16", "int8"):
        c = sorted((t for t in cand if t["type"] == f), key=lambda t: (dval(e141f, t["name"])["se"], t["name"]))
        pick5 += c[:POOL5_TAKE[f]]
    out["pool5"] = {"rule": "of pool 5's 24 non-anchor tiles not in E153's K1, per format 4 / 3 / 3 (fp32 / fp16 / int8, in proportion "
                            "to 10 / 7 / 7) with the smallest se of D on Q139(u)'s footing (E141 re-reduced), ties by name",
                    "candidates": {t["name"]: {"type": t["type"], "footing_se": dval(e141f, t["name"])["se"]} for t in cand},
                    "tiles": {t["name"]: {"type": t["type"], "file": f"tools/claims-v3/kinds/blind5/{t['file']}", "sha256": t["sha256"]["whole"],
                                          "sha256_a": t["sha256"]["a"], "sha256_b": t["sha256"]["b"], "source": "E141",
                                          "footing": dval(e141f, t["name"]), "session": dval(e141s, t["name"])} for t in pick5}}
    # E152: its committed passes on the footing, by its own reducer
    rr = os.path.join(HERE, "rerun-ref")
    os.makedirs(rr, exist_ok=True)
    passes = [f"{E152D}/aifoundry3/kinds/p152{n}" for n in range(10, 16)]          # relative to the top of the tree (the files record them)
    R = "tools/claims-v3/e163/rerun-ref"
    cmd = [sys.executable, "-B", "tools/claims-v3/e152/reduce_e152.py", *passes, "--leak", KF, "--no-refit",
           "--drop-dips", "--out", f"{R}/e152-footing.json", "--csv", f"{R}/runs-e152-footing.csv", "--txt", f"{R}/reduce-e152-footing.txt"]
    with open(os.path.join(rr, "reduce-e152-footing.log"), "w") as lg:
        rc = subprocess.call(cmd, cwd=ROOT, stdout=lg, stderr=subprocess.STDOUT)
    if rc != 0:
        raise SystemExit(f"reduce_e152.py exited {rc}; see rerun-ref/reduce-e152-footing.log")
    foot = json.load(open(os.path.join(rr, "e152-footing.json")))
    assert foot["passes"] == list(range(15210, 15216)) and not foot.get("passes_set_aside"), (foot["passes"], foot.get("passes_set_aside"))
    tiles152 = J(E152T)["tiles"]
    dk = J(f"{E152D}/e152-dipskept.json")["items"]
    c152 = sorted(tiles152, key=lambda t: (foot["items"][t]["D"]["se"], t))
    pick152 = c152[:6]
    out["e152"] = {"rule": "of E152's 11 tiles, the 6 with the smallest se of D on Q139(u)'s footing (E152's six committed passes "
                           "re-reduced by reduce_e152.py --leak 0.20563713796102187 --no-refit --drop-dips), ties by name",
                   "footing_reduction": {"file": "tools/claims-v3/e163/rerun-ref/e152-footing.json", "passes": foot["passes"],
                                         "set_aside": foot.get("passes_set_aside"), "leak": foot.get("leak"),
                                         "command": "reduce_e152.py <docs/reports/data/2026-11-03-e152-gate-dose/aifoundry3/kinds/p15210..p15215> "
                                                    f"--leak {KF} --no-refit --drop-dips"},
                   "candidates": {t: {"footing_se": foot["items"][t]["D"]["se"]} for t in tiles152},
                   "tiles": {t: {"type": "fp32", "file": tiles152[t]["file"], "sha256": tiles152[t]["sha256"],
                                 "sha256_a": tiles152[t]["sha256_a"], "sha256_b": tiles152[t]["sha256_b"], "source": "E152",
                                 "footing": {x: foot["items"][t]["D"][x] for x in ("mean", "se", "n", "ci95")},
                                 "session": {x: dk[t]["D"][x] for x in ("mean", "se", "n", "ci95")}} for t in pick152}}
    # E151: per-tile steps from its committed reduction, through its own Book
    chain = {rel: sha(rel) for rel in CHAIN}
    S145, reg151, tiles = S.e151_chain(chain, (16350, 16359))
    new, meta = S.e151_steps(S145, reg151, tiles, os.path.join(ROOT, E151D, "runs.csv"), os.path.join(ROOT, E151D, "e151.json"), "e151",
                             list(E151_TILES) + list(E151_REPORTED))
    assert meta["blocks"] == [15111, 15112, 15113, 15114, 15115, 15117, 15118, 15119], meta["blocks"]
    out["e151"] = {"rule": "the six bits of E151's registered odd-even contrast (e151_common.B_TWICE), their step over their own zero "
                           "(hb1) on the minion rail, board-equivalent (/ c_rb 0.81), per kept B block, E151's registered primary "
                           "reduction (dips removed, its rail filter on, leakage auto) and E130's train gate at 0.25 W",
                   "blocks_kept": meta["blocks"], "set_aside": [x["pass"] for x in meta["set_aside"]], "chain_sha256": chain,
                   "tiles": {t: dict(new[t], source="E151") for t in E151_TILES},
                   "reported": {t: new[t] for t in E151_REPORTED}}
    out["sources"] = {rel: sha(rel) for rel in (E141F, E141S, P5, E152T, f"{E152D}/e152-dipskept.json", f"{E152D}/e152.json",
                                                f"{E151D}/runs.csv", f"{E151D}/e151.json", "tools/claims-v3/e152/reduce_e152.py")}
    out["sources"]["tools/claims-v3/e163/rerun-ref/e152-footing.json"] = sha("tools/claims-v3/e163/rerun-ref/e152-footing.json")
    json.dump(out, open(os.path.join(HERE, "rerun-ref.json"), "w"), indent=1)
    for k in ("pool5", "e152", "e151"):
        for t, x in out[k]["tiles"].items():
            if k == "e151":
                print(f"{k:5s} {t:30s} {x['mean']:.4f} se {x['se']:.4f} n {x['n']}")
            else:
                print(f"{k:5s} {t:30s} footing {x['footing']['mean']:.4f} se {x['footing']['se']:.4f} n {x['footing']['n']} | "
                      f"session {x['session']['mean']:.4f} se {x['session']['se']:.4f} n {x['session']['n']}")
    print("wrote tools/claims-v3/e163/rerun-ref.json")


if __name__ == "__main__":
    main()
