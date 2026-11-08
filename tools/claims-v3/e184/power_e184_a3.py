#!/usr/bin/env python3
"""E184's dated amendment A3 (E184.md.dated-note-A3.md): the figures A3 states, desk only, before any E184 datum.

    /usr/bin/python3 -B tools/claims-v3/e184/power_e184_a3.py > tools/claims-v3/e184/power-e184-a3.json

It runs dated amendment A2's own definitions (power_e184_a2.py's text up to its first output line, executed as written, so the noise
models, the fast twins of both E184-C statistics and the scan's draws are A2's), and reads beside it forecast-e184.json, inputs-e184.json,
power-e184-a2.json and a2-check-e184.json (unchanged). Pure Python, seeded, the same bytes under /usr/bin/python3 3.9 and python3 3.13.

  K   A3-1: one quad's chance of a NO-GO at the smoke's 16-shire n = 19 quad under kit note 1's band (-0.15 to +0.30 W), for small steps
      read at 1.0 to 2.0 times their size (A2-7 gave 0 to 1), with A2's formula (power_e184_a2.k_section) and its two noise models; and the
      gain at which that chance reaches 0.05 and 0.5.
  C   A3-5: the 95th percentiles of both E184-C statistics' max |T| with no step, on 20,000 draws of A2's own scan model (new seeds), beside
      A2's 4,000 (its own seeds, re-drawn here and checked equal to power-e184-a2.json, which shows the definitions are A2's), and the
      null rate of each statistic at its committed critical value.
  R   A3-2: the powers of E184-L's and E184-P's two readings at a linear meter, copied from power-e184-a2.json > R (no draw here).
  B   A3-5: the refreshes a block keeps in E180's committed fadd.ps bursts, from a2-check-e184.json, against the base model's.
SPDX-License-Identifier: Apache-2.0
"""
import ast
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SRC = os.path.join(HERE, "power_e184_a2.py")


def a2_definitions():
    """power_e184_a2.py's statements up to its first output line (`res = {...}`), executed as written."""
    tree = ast.parse(open(SRC).read())
    body = []
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "res" for t in n.targets):
            break
        body.append(n)
    ns = {"__name__": "power_e184_a2_definitions", "__file__": SRC}
    saved = sys.argv
    sys.argv = [SRC]                    # A2's TEXT flag reads sys.argv; never --text here
    try:
        exec(compile(ast.Module(body=body, type_ignores=[]), "power_e184_a2.py (definitions)", "exec"), ns)
    finally:
        sys.argv = saved
    return ns, len(body)


A, NSTMT = a2_definitions()
P2 = json.load(open(os.path.join(HERE, "power-e184-a2.json")))
CHK = json.load(open(os.path.join(HERE, "a2-check-e184.json")))
FC = json.load(open(os.path.join(HERE, "forecast-e184.json")))
r6 = A["r6"]
phi = A["phi"]
BAND = (-0.15, 0.30)                    # check_e184_v2.SMOKE_BANDS_S[(16, 19)], kit note 1's band, unchanged


def k_section():
    y19 = A["S_W"] * 19
    out = {"expected_w_if_linear": r6(y19), "band_kit_note_1": list(BAND), "formula": "power_e184_a2.k_section's, one quad, Gaussian"}
    for model in ("base", "pess"):
        sq = A["QSD"][model]

        def no_go(g):
            mu = g * y19
            return phi((BAND[0] - mu) / sq) + 1.0 - phi((BAND[1] - mu) / sq)

        rows = {}
        for k in range(0, 11):
            g = 1.0 + k / 10.0
            rows["small steps read %.1f" % g] = r6(no_go(g))
        found = {}
        for target in (0.05, 0.5):
            lo, hi = 1.0, 3.0
            for _ in range(60):
                mid = (lo + hi) / 2.0
                if no_go(mid) < target:
                    lo = mid
                else:
                    hi = mid
            found["gain_at_no_go_%g" % target] = r6((lo + hi) / 2.0)
        out[model] = {"quad_sd_w": r6(sq), "no_go": rows, **found}
    out["check_against_a2"] = {"a2_no_go_at_1_base": P2["K"]["base"]["small steps read 1"]["no_go_kit_note_1_band"],
                               "a3_no_go_at_1_base": out["base"]["no_go"]["small steps read 1.0"]}
    return out


def pct95(xs):
    xs = sorted(xs)
    return xs[int(math.ceil(0.95 * (len(xs) - 1)))]


def c_section():
    out = {}
    scan, mu0 = A["scan_draw"], A["mu_offset"](0.0)
    fa2, freg = A["FAST_A2"], A["FAST_REG"]
    # A2's own 4,000 draws, its own seeds (power_e184_a2.c_section's lines), re-drawn: they must give A2's committed figures
    r = random.Random(18422)
    t_a2_4000 = r6(pct95([fa2.max_t(scan(r, "base", mu0))[0] for _ in range(4000)]))
    r = random.Random(18423)
    t_reg_4000 = r6(pct95([freg.max_t(scan(r, "base", mu0))[0] for _ in range(4000)]))
    out["a2_redrawn"] = {"t_crit_a2": t_a2_4000, "t_crit_registered_recomputed_4000": t_reg_4000,
                         "equal_to_power-e184-a2.json": t_a2_4000 == P2["C"]["t_crit_a2"]
                         and t_reg_4000 == P2["C"]["t_crit_registered_recomputed_4000"]}
    t_reg, t_a2 = FC["power"]["C"]["base"]["t_crit_family_5pct"], P2["C"]["t_crit_a2"]
    for name, fast, seed, crit in (("A2-1's statistic (the verdict)", fa2, 18461, t_a2),
                                   ("the registered statistic (reported only)", freg, 18462, t_reg)):
        r = random.Random(seed)
        ts = [fast.max_t(scan(r, "base", mu0))[0] for _ in range(20000)]
        out[name] = {"draws": 20000, "seed": seed, "t_95": r6(pct95(ts)), "committed_critical_value": crit,
                     "null_rate_at_committed_value": r6(sum(1 for t in ts if t > crit) / len(ts))}
    return out


def r_section():
    out = {}
    for rule, reg_fc in (("E184-L", FC["power"]["L"]), ("E184-P", FC["power"]["P"])):
        row = {}
        for model in ("base", "pess"):
            d = P2["R"][rule][model]["linear, no offset"]
            row[model] = {"E184.md's registered power, LINEAR if linear": reg_fc[model]["if linear"].get("LINEAR"),
                          "A2's draws, the registered R, LINEAR": d["registered_R"].get("LINEAR"),
                          "A2-2's governing reading, LINEAR": d["governing_A2_2"].get("LINEAR"),
                          "the null-corrected R alone, LINEAR": d["null_corrected_R"].get("LINEAR", 0.0)}
        out[rule] = row
    out["source"] = "forecast-e184.json > power > L|P > <model> > 'if linear'; power-e184-a2.json > R > <rule> > <model> > 'linear, no offset'"
    return out


def b_section():
    e = CHK["e180_fadd_bursts"]
    return {"block_refreshes": e["block_refreshes"], "blocks": e["blocks"], "mean_per_block": r6(e["block_refreshes"] / e["blocks"]),
            "base_model_refreshes_per_block": FC["models"]["base"]["refreshes_per_block"],
            "source": "a2-check-e184.json > e180_fadd_bursts (E180's 162 committed fadd.ps bursts, read as 324 E184 blocks; post hoc)"}


res = {"what": "E184 dated amendment A3's figures (power_e184_a3.py)",
       "a2_definitions": "power_e184_a2.py's first %d statements, executed as written" % NSTMT,
       "inputs": ["power_e184_a2.py (its definitions)", "forecast-e184.json", "inputs-e184.json", "power-e184-a2.json", "a2-check-e184.json"]}
res["K"] = k_section()
res["C"] = c_section()
res["R"] = r_section()
res["B"] = b_section()
print(json.dumps(res, indent=1, sort_keys=True))
