#!/usr/bin/env python3
"""E216 (Q227): THE SEVEN FORECASTERS, each from its frozen code unchanged, called the same way by the point rule (point_rule_e216.py) and by the
forecast freeze (forecast_e216.py). numpy through the predictors; single-threaded (the caller sets the four thread variables to 1).

  MM1-v3.1   tools/matmul/mm1/v3.1/mm1_v31.py (landed 2c971828), Model(out/mm1_v31_params.json).predict_many([{card, arm, fmt, kind, mask, f,
             kernel}]): card 'aifoundry2 card 0'; f the clock (799.0, 700 or 600 MHz); V None (mm1_core volts at f: this card's 0.517 / 0.568 /
             0.618 V at 600 / 700 / 800 MHz, interpolated), G None (G_of_f: this card's governed base), t0_c None (the energy at a 50 C die; the J
             at rest REPORTED at the card's rest law's T0, 51 C); minions and ops None (32 a shire of the mask; 64 MB NB KB an op a minion).
  MM1-v3     tools/matmul/mm1/v3/mm1_v3.py (landed b1493082), Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, f, kernel=kernel,
             t0_c=None): the same inputs.
  MM1-v2     tools/matmul/mm1/v2 (landed 3ca4b717) through MM1-v3's e213_v3.v2_model() (its pins and SHA256SUMS checked), .predict(card, arm2, fmt,
             kind, mask, f, V=None, t0_c=None), arm2 = the token with gemmLnc read as gemmL (MM1-v2 has no code-path term), E215's call.
  v3.1 with T7   MM1-v3.1's predictor with the same fit's declared T7 time form (out/fits/time_T5r+G0+T7.json > theta_all and form), E215's
             call; REPORTED, never scored by a registered rule.
  'v3.1 + gemmLnc term'   MM1-v3.1's output plus term F3 (terms/gemmlnc/term-gemmlnc.json, sha256 2ee478f8..., Q225 track B, frozen 09:30:36
             PST Thu 19 Nov 2026), computed by the term's own maker's functions - feats() and term_W(), with its FORMS and LAM - taken from
             terms/gemmlnc/s05_freeze.py (byte-equal to Q225's land) by its syntax tree and run unchanged, with the term file's two constants:
             dW = D sL (minions / t_op) 1e-12 (c1 dup + c2 first), D = 1 + 0.0048 (die - 50), sL = 1 + xi (s_V - 1), t_op MM1-v3.1's op time;
             W over idle at a measured op time t = A + (B + dW t_op) / t (the term adds dW t_op to B, the maker's own words); time MM1-v3.1's.
  'v3.1 + contention'   MM1-v3.1's op time x (1 + a Phi_fresh) (form F1, Q225 track C, frozen 09:31:34 PST: a = -0.08316593007433395 read from
             terms/layout/forecast-e215-v31-layout.json's meta, never refitted), the factor clipped to [0.3, 3.0] as freeze_layout.py clips it;
             Phi_fresh by eval_layout.phi_of over the masked walk's features (features_layout.walk_feats and mesh_feats at the walk's pin, for a
             configuration not in the frozen feature cache; the cache's own entries as frozen); 0 at the full mask, so the factor is exactly 1
             there. Its energy is MM1-v3.1's affine form at its own op time (given t: MM1-v3.1's exactly).
  'v3.1 + both terms' (the candidate MM1-v3.2; THE COMPOSITION, declared before any forecast was computed): time = MM1-v3.1's op time x the
             contention factor; W over idle at a measured op time t = A + (B + dW t_op,v3.1) / t (the gemmLnc term's energy an op added to B, the
             same as in 'v3.1 + gemmLnc term'); at its own seconds, t = its own op time. No E216 point carries both terms (every gemmLnc point is
             on the full chip, every subset point is cooperative), so it equals 'v3.1 + gemmLnc term' on G, 'v3.1 + contention' on Y and MM1-v3.1
             elsewhere: the composition is stated so that it is fixed, not because it is tested where the terms meet.
SPDX-License-Identifier: Apache-2.0
"""
import ast
import copy
import hashlib
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
E216 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
V31 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.1")
V3 = os.path.join(REPO, "tools", "matmul", "mm1", "v3")
TERMS = os.path.join(E216, "terms")
CARD = "aifoundry2 card 0"
FULL = 0xFFFFFFFF
SHAPE = re.compile(r"^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$")
A_FRESH_POSTED = -0.08316593007433395
TERM_SHA_POSTED = "2ee478f80aa1182aeb5d00e07fc302cffa668e66964ca7ebc2e61362128f3ee4"
MODELS = ("MM1-v3.1", "MM1-v3", "MM1-v2", "v3.1+lnc", "v3.1+contention", "v3.1+both", "v3.1 with T7")
SCORED = ("MM1-v3.1", "MM1-v3", "MM1-v2", "v3.1+lnc", "v3.1+contention", "v3.1+both")
PINS = {
    "tools/matmul/mm1/v3.1/mm1_v31.py": "e67ea34d60e4947e6fe192d5ddd995682fe4992f7ec1595f7d5fc29843a87575",
    "tools/matmul/mm1/v3.1/time_v31.py": "4a7147eb79754d657e74d5673e26c3db67bdb89f3ef08ee64748968688402ac5",
    "tools/matmul/mm1/v3.1/energy_v31.py": "21082cbfbd14ce24f7210360203e59feca7e643a7f36042e3ece2e468d2b906b",
    "tools/matmul/mm1/v3.1/out/mm1_v31_params.json": "d01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3",
    "tools/matmul/mm1/v3.1/out/fits/time_T5r+G0+T7.json": "fe98b06f9a32412556137576422ca237aaa74c80542143d7f9fda0c6f308fcfd",
    "tools/matmul/mm1/v3.1/t7_v31.py": "893ae962174678fcd1560dfc423722361e706319a188687f8f572a4e3ca89242",
    "tools/matmul/mm1/v3.1/SHA256SUMS": "f6840d2de6617a739c30485904230e96b744b03b7c82c08b14b6de2d942528ed",
    "tools/matmul/mm1/v3/mm1_v3.py": "89c2e463e3527b379ed10557c2e595b294b289c0ba8cd2005481190c9555fe3c",
    "tools/matmul/mm1/v3/out/mm1_v3_params.json": "1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db",
    "tools/matmul/mm1/v3/SHA256SUMS": "c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74",
    "tools/matmul/mm1/v2/mm1_v2.py": "5abf3a0a49757e15a776f3a1b5cdb4f7fa90943de2e016fe8b26aa4bf5324c08",
    "tools/matmul/mm1/v2/out/mm1_v2_params.json": "9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5",
    "tools/matmul/mm1/v2/SHA256SUMS": "eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2",
    "tools/claims-v3/e216/terms/gemmlnc/term-gemmlnc.json": TERM_SHA_POSTED,
    "tools/claims-v3/e216/terms/gemmlnc/s05_freeze.py": "42c38901450a022cb59a689ecaf12325cf9b48c534da4fb4c7c3612ef7a37257",
    "tools/claims-v3/e216/terms/layout/freeze_layout.py": "ca04faa37bb4f22cb8b8b293fcefbdc99b153a2e0f15b46857ace034f926b58c",
    "tools/claims-v3/e216/terms/layout/eval_layout.py": "f076fa919ab4c28d438e5f4fcad9bd9ea8824a99afad63811d2f394cd4d97ae1",
    "tools/claims-v3/e216/terms/layout/features_layout.py": "b1f16c83d7967df7483de3bc20c64f96f9a899dd1efcd722869d942a895e26b3",
    "tools/claims-v3/e216/terms/layout/out/features_layout.json": "1de94e5611c0912eb4bfb4294df9fabeb07078f4c31344e29e15c5200f1b0183",
    "tools/claims-v3/e216/terms/layout/forecast-e215-v31-layout.json": "f09f9e1abe8acdb4995e9945b75628637e6cf61487cf561818091ee673814259",
}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def check_pins():
    bad = {k: sha_rel(k) for k, v in PINS.items() if sha_rel(k) != v}
    if bad:
        print("models_e216: REFUSED, a pinned input changed:", bad)
        sys.exit(4)
    return dict(PINS)


def shape_of(arm):
    m = SHAPE.match(arm)
    return tuple(int(x) for x in m.groups()) if m else None


def lnc_maker():
    """the gemmLnc term maker's own functions, run unchanged: FORMS, LAM, shape(), feats(), term_W() from s05_freeze.py's syntax tree"""
    src = open(os.path.join(TERMS, "gemmlnc", "s05_freeze.py")).read()
    tree = ast.parse(src)
    keep = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in ("shape", "feats", "term_W"):
            keep.append(n)
        elif isinstance(n, ast.Assign) and any(getattr(t, "id", None) in ("FORMS", "LAM") for t in n.targets):
            keep.append(n)
    ns = {"np": np}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "s05_freeze.py", "exec"), ns)
    assert set(("FORMS", "LAM", "feats", "term_W")) <= set(ns), sorted(ns)
    return ns


class Models:
    def __init__(self):
        self.pins = check_pins()
        sys.path.insert(0, V31)
        import mm1_v31  # noqa: E402
        self.P31 = json.load(open(os.path.join(V31, "out", "mm1_v31_params.json")))
        self.M31 = mm1_v31.Model(self.P31)
        T7 = json.load(open(os.path.join(V31, "out", "fits", "time_T5r+G0+T7.json")))
        P7 = copy.deepcopy(self.P31)
        P7["time"]["theta"] = dict(T7["theta_all"])
        P7["time"]["form"] = dict(T7["form"])
        self.M7 = mm1_v31.Model(P7)
        sys.path.insert(0, V3)
        import mm1_v3  # noqa: E402
        import e213_v3  # noqa: E402
        self.M3 = mm1_v3.Model(json.load(open(os.path.join(V3, "out", "mm1_v3_params.json"))))
        M2 = e213_v3.v2_model()
        self.M2 = M2[0] if isinstance(M2, tuple) else M2
        self.L = lnc_maker()
        self.TERM = json.load(open(os.path.join(TERMS, "gemmlnc", "term-gemmlnc.json")))
        assert self.TERM["form"] == "F3" and list(self.TERM["x"]) == ["dup", "first"]
        self.c_lnc = list(self.TERM["constants_pJ_per_line"])
        self.XI = self.P31["energy"]["theta"]["xi"]
        sys.path.insert(0, os.path.join(TERMS, "layout"))
        import eval_layout as S  # noqa: E402
        import features_layout as FL  # noqa: E402
        self.S, self.FL = S, FL
        meta = json.load(open(os.path.join(TERMS, "layout", "forecast-e215-v31-layout.json")))["meta"]
        self.a_fresh = float(meta["a_fresh"])
        assert self.a_fresh == A_FRESH_POSTED, self.a_fresh
        self.walk_new = {}
        rl = self.P31["rest_law"][CARD]
        self.rest_T0 = rl["T0_forecast_c"]
        self.rest_W = rl["a"] * self.rest_T0 ** 2 + rl["b"] * self.rest_T0 + rl["c"]

    # ---------------------------------------------------------------- the layout feature (walk) for one configuration
    def ensure_feats(self, loop, arm, mask):
        m = int(mask, 16)
        if m == FULL or loop not in self.S.WALK_OF_LOOP:
            return
        MB, NB, KB = shape_of(arm)
        wk = self.S.WALK_OF_LOOP[loop]
        for mm in (m, FULL):
            key = "%s|%dx%dx%d|0x%x" % (wk, MB, NB, KB, mm)
            if key in self.S.FEATS:
                continue
            f = self.FL.walk_feats(wk, (MB, NB, KB), mm)
            f.update({"mesh_" + k: v for k, v in self.FL.mesh_feats(mm).items() if k != "n"})
            self.S.FEATS[key] = f
            self.walk_new[key] = f

    def layout_factor(self, loop, arm, mask):
        self.ensure_feats(loop, arm, mask)
        ph, key = self.S.phi_of(loop, arm, mask)
        g = float(np.clip(1.0 + self.a_fresh * ph[0], 0.3, 3.0))
        return g, float(ph[0]), key

    # ---------------------------------------------------------------- one batch of points at one clock
    def forecast(self, pts, f, models=MODELS, card=CARD):
        """pts: [{'id', 'arm' (token), 'kernel' ('rgm136'), 'fmt', 'kind', 'mask'}] -> {id: {model: fields}} (card: aifoundry2 card 0; another
        card only for the makers' reproduction checks)"""
        specs = [{"card": card, "arm": p["arm"], "fmt": p["fmt"], "kind": p["kind"], "mask": p["mask"], "f": float(f),
                  "kernel": p.get("kernel", "rgm136")} for p in pts]
        out = {p["id"]: {} for p in pts}
        r31 = self.M31.predict_many(specs) if any(m.startswith("v3.1") or m == "MM1-v3.1" for m in models) else [None] * len(pts)
        r7 = self.M7.predict_many(specs) if "v3.1 with T7" in models else [None] * len(pts)
        for j, (p, s) in enumerate(zip(pts, specs)):
            o = out[p["id"]]
            if "MM1-v3.1" in models:
                o["MM1-v3.1"] = self.fields(r31[j])
            if "v3.1 with T7" in models:
                o["v3.1 with T7"] = self.fields(r7[j])
            if "MM1-v3" in models:
                o["MM1-v3"] = self.fields(self.M3.predict(card, p["arm"], p["fmt"], p["kind"], p["mask"], float(f), kernel=s["kernel"], t0_c=None))
            if "MM1-v2" in models:
                arm2 = p["arm"].replace("gemmLnc", "gemmL").replace("gemmLn", "gemmL")
                o["MM1-v2"] = self.fields(self.M2.predict(card, arm2, p["fmt"], p["kind"], p["mask"], float(f), V=None, t0_c=None),
                                          note=("MM1-v2 has no code-path term: its rgm136 gemmL twin, literally" if arm2 != p["arm"] else ""))
            if any(m in models for m in ("v3.1+lnc", "v3.1+contention", "v3.1+both")):
                base = r31[j]
                loop = base.get("loop") or ("rgm136 gemmLnc" if p["arm"].startswith("gemmLnc") else "rgm136 gemmL")
                lnc = self.lnc_term(base, p["arm"])
                g, phi, key = self.layout_factor(loop, p["arm"], p["mask"])
                o["v3.1+lnc"] = self.composed(base, lnc, 1.0, phi, key, "v3.1+lnc")
                o["v3.1+contention"] = self.composed(base, None, g, phi, key, "v3.1+contention")
                o["v3.1+both"] = self.composed(base, lnc, g, phi, key, "v3.1+both")
        return out

    def lnc_term(self, p, arm):
        t = p["T_op_us"]
        Q = 0.5 * (np.array(p["Q0"]) + np.array(p["Q1"]))
        fe = self.L["feats"](arm, Q)
        D = 1.0 + self.L["LAM"] * (p["die_start_c"] - 50.0)
        sL = 1.0 + self.XI * (p["s_V"] - 1.0)
        rate = p["minions"] / (t * 1e-6)
        dW, E = self.L["term_W"]("F3", self.c_lnc, fe, rate, D, sL)
        return {"dW": float(dW), "E_pJ_per_minion_op": float(E), "dup": fe["dup"], "beyond": fe["beyond"], "first": fe["first"], "NB": fe["NB"],
                "qA_L2_L3_F": fe["qA"], "qB_L2_L3_F": fe["qB"], "D": D, "sL": sL, "dB_W_us": float(dW) * t}

    @staticmethod
    def fields(p, note=""):
        if p is None:
            return None
        o = {"T_op_us": p["T_op_us"], "cycles_per_op_wall": p["cycles_per_op_wall"], "cycles_per_op_mean": p.get("cycles_per_op_mean"),
             "seconds_per_gemm": p.get("seconds_per_gemm"), "ops_per_minion_per_gemm": p.get("ops_per_minion_per_gemm"), "f_mhz": p.get("f_mhz"),
             "minions": p.get("minions"), "note": note}
        if "W_over_idle" in p:
            o.update({"W_over_idle": p["W_over_idle"], "A_W": p["W_affine"]["A_W"], "B_W_us": p["W_affine"]["B_W_us"],
                      "J_over_idle_per_gemm": p.get("J_over_idle_per_gemm"), "V": p.get("V"), "s_V": p.get("s_V"), "G_W": p.get("G_W"),
                      "die_start_c": p.get("die_start_c")})
            rl = p.get("rest_law")
            if rl:
                o["rest_law_W"] = rl["P_rest_W"]
                o["rest_law_T0_c"] = rl["T0_c"]
        else:
            o["energy"] = p.get("energy", "NOT FORECAST")
        for k in ("t7_mapped", "rho_wall_over_mean"):
            if k in p:
                o[k] = p[k]
        return o

    def composed(self, base, lnc, g, phi, key, name):
        t = base["T_op_us"] * g
        o = {"T_op_us": t, "cycles_per_op_wall": base["cycles_per_op_wall"] * g, "cycles_per_op_mean": base["cycles_per_op_mean"] * g,
             "seconds_per_gemm": base["seconds_per_gemm"] * g, "ops_per_minion_per_gemm": base["ops_per_minion_per_gemm"], "f_mhz": base["f_mhz"],
             "minions": base["minions"], "layout_factor": g, "phi_fresh": phi, "walk_key": key, "note": name}
        if "W_over_idle" not in base:
            o["energy"] = "NOT FORECAST"
            return o
        A = base["W_affine"]["A_W"]
        B = base["W_affine"]["B_W_us"] + (lnc["dB_W_us"] if lnc else 0.0)
        W = A + B / t
        o.update({"W_over_idle": W, "A_W": A, "B_W_us": B, "J_over_idle_per_gemm": W * o["seconds_per_gemm"], "lnc_dW_at_v31_t": (lnc["dW"] if lnc else 0.0),
                  "lnc": lnc, "V": base.get("V"), "s_V": base.get("s_V"), "die_start_c": base.get("die_start_c")})
        rl = base.get("rest_law")
        if rl:
            o["rest_law_W"] = rl["P_rest_W"]
            o["rest_law_T0_c"] = rl["T0_c"]
        return o

    def planning_peak(self, fc):
        """the largest W over idle at its own seconds over the six scored forecasters + the card's rest law at T0 + 2 W (None if any is not forecast)"""
        ws = []
        for m in SCORED:
            x = fc.get(m)
            if not x or "W_over_idle" not in x:
                return None, None
            ws.append((x["W_over_idle"], m))
        w, m = max(ws)
        return w + self.rest_W + 2.0, m


def ln(a, b):
    return math.log(a / b)
