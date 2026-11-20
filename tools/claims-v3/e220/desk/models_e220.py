#!/usr/bin/env python3
"""E220 (Q233): THE FOUR FORECASTERS, each from its frozen code unchanged, called the same way by the point rule (desk/point_rule_e220.py) and by
the forecast freeze (forecast_e220.py). numpy through the predictors; single-threaded (the caller sets the four thread variables to 1).

  MM1-v3.2   tools/matmul/mm1/v3.2/mm1_v32.py (landed 4e386f75), Model(out/mm1_v32_params.json).predict_many([{card, arm, fmt, kind, mask, f,
             kernel}]) - THE REGISTERED MODEL;
  MM1-v3.1   tools/matmul/mm1/v3.1/mm1_v31.py (landed 2c971828), Model(out/mm1_v31_params.json).predict_many([...]) - the same inputs;
  MM1-v3     tools/matmul/mm1/v3/mm1_v3.py (landed b1493082), Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, f, kernel=kernel,
             t0_c=None) - the same inputs (its SHA256SUMS checked by its own e213_v3 import);
  MM1-v2     tools/matmul/mm1/v2 (landed 3ca4b717) through MM1-v3's e213_v3.v2_model() (its pins and SHA256SUMS checked), .predict(card, arm2, fmt,
             kind, mask, f, V=None, t0_c=None), arm2 = the token with gemmLnc read as gemmL (MM1-v2 has no code-path term: E215's and E216's call).
WHAT EACH IS GIVEN (every model the same): card 'aifoundry1 card 1' (arm A) or 'aifoundry2 card 0' (arm B), the name under which each model's
parameters hold that card's per-card terms; the point's arm token (the predictors read the loop from it and from kernel 'rgm136'); fmt; kind
'random'; the mask as MM1 spells it; f = 600.0 MHz (arm A) or 799.0, 700.0, 600.0 MHz (arm B: three frozen columns, 799.0 registered); V None
(each model's own volts at f for the card), G None (the governed base from the clock, by each model's own G_of_f), t0_c None (the energy at a 50 C
die; the J at rest REPORTED at the card's rest law at its T0 forecast); minions and ops None (32 a shire of the mask; 64 MB NB KB ops a minion).
THE PLANNING PEAK (the point rule's drop, the brief's "planning peak by MM1-v3.2"): PP32 = MM1-v3.2's W over idle at its own seconds at the arm's
registered clock, x (1 + 2 eps_G) at a gemmLnc point (eps_G = MM1-v3.2's held-out gemmLnc W error, decisions_v32.json step 4 acceptance 5: 8.43%),
+ MM1-v3.2's rest law for the card at its T0 forecast, + 2 W (E218's planning-peak form restricted to MM1-v3.2). PP_all (REPORTED) = the largest
over the four models of that W (MM1-v3.2's with its factor) + the same rest + 2 W.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
V32 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.2")
V31 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.1")
V3 = os.path.join(REPO, "tools", "matmul", "mm1", "v3")
C1 = "aifoundry1 card 1"
A2 = "aifoundry2 card 0"
ARMS = {"A": {"card": C1, "f_reg": 600.0, "clocks": (600.0,), "stop_W": 72.0},
        "B": {"card": A2, "f_reg": 799.0, "clocks": (799.0, 700.0, 600.0), "stop_W": 70.0}}
MODELS = ("MM1-v3.2", "MM1-v3.1", "MM1-v3", "MM1-v2")
SHAPE = re.compile(r"^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$")
PINS = {
    "tools/matmul/mm1/v3.2/mm1_v32.py": "e9a1ced7aa2fe50c66f9a1c389cb6c0064979be1d5f149a299f7a82e54ba2d5f",
    "tools/matmul/mm1/v3.2/energy_v32.py": "b6415d90b9218528de6efafe90902068556c8c9560fd9f4f9eb75922e3645bbf",
    "tools/matmul/mm1/v3.2/out/mm1_v32_params.json": "c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab",
    "tools/matmul/mm1/v3.2/out/decisions_v32.json": "ff1a4c014e435ac4df6e999af341fac74dbb6d4745a404b853698e7b38a3a571",
    "tools/matmul/mm1/v3.2/SHA256SUMS": "d52c9cce15db12ed66873722b9ec5c07be1fdeec3027a23833c7e3d230d1d761",
    "tools/matmul/mm1/v3.1/mm1_v31.py": "e67ea34d60e4947e6fe192d5ddd995682fe4992f7ec1595f7d5fc29843a87575",
    "tools/matmul/mm1/v3.1/time_v31.py": "4a7147eb79754d657e74d5673e26c3db67bdb89f3ef08ee64748968688402ac5",
    "tools/matmul/mm1/v3.1/energy_v31.py": "21082cbfbd14ce24f7210360203e59feca7e643a7f36042e3ece2e468d2b906b",
    "tools/matmul/mm1/v3.1/out/mm1_v31_params.json": "d01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3",
    "tools/matmul/mm1/v3.1/t7_v31.py": "893ae962174678fcd1560dfc423722361e706319a188687f8f572a4e3ca89242",
    "tools/matmul/mm1/v3.1/SHA256SUMS": "f6840d2de6617a739c30485904230e96b744b03b7c82c08b14b6de2d942528ed",
    "tools/matmul/mm1/v3/mm1_v3.py": "89c2e463e3527b379ed10557c2e595b294b289c0ba8cd2005481190c9555fe3c",
    "tools/matmul/mm1/v3/out/mm1_v3_params.json": "1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db",
    "tools/matmul/mm1/v3/e213_v3.py": "3533b4d73278381bd2a7f26891f3dded5ef154de9751733402d1d9a174d826c1",
    "tools/matmul/mm1/v3/mm1_core_v3.py": "acebc705d06be133845b78ed85a7787a6792838fcca95f75dfc03fba41ea43c2",
    "tools/matmul/mm1/v3/SHA256SUMS": "c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74",
    "tools/matmul/mm1/v2/mm1_v2.py": "5abf3a0a49757e15a776f3a1b5cdb4f7fa90943de2e016fe8b26aa4bf5324c08",
    "tools/matmul/mm1/v2/out/mm1_v2_params.json": "9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5",
    "tools/matmul/mm1/v2/SHA256SUMS": "eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2",
}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def check_pins():
    bad = {k: sha_rel(k) for k, v in PINS.items() if sha_rel(k) != v}
    if bad:
        print("models_e220: REFUSED, a pinned input changed:", bad)
        sys.exit(4)
    for d in (V32, V31, V3, os.path.join(REPO, "tools", "matmul", "mm1", "v2")):
        rc = os.system(f"cd '{d}' && sha256sum -c --quiet SHA256SUMS > /dev/null 2>&1")
        if rc != 0:
            print(f"models_e220: REFUSED, SHA256SUMS check failed in {os.path.relpath(d, REPO)}")
            sys.exit(4)
    return dict(PINS)


def shape_of(arm):
    m = SHAPE.match(arm)
    return tuple(int(x) for x in m.groups()) if m else None


class Models:
    def __init__(self):
        self.pins = check_pins()
        sys.path.insert(0, V32)
        import mm1_v32  # noqa: E402  (imports MM1-v3.1's time and energy modules at their pins)
        self.P32 = json.load(open(os.path.join(V32, "out", "mm1_v32_params.json")))
        self.M32 = mm1_v32.Model(self.P32)
        import mm1_v31  # noqa: E402
        self.P31 = json.load(open(os.path.join(V31, "out", "mm1_v31_params.json")))
        self.M31 = mm1_v31.Model(self.P31)
        sys.path.insert(0, V3)
        import mm1_v3  # noqa: E402
        import e213_v3  # noqa: E402
        self.M3 = mm1_v3.Model(json.load(open(os.path.join(V3, "out", "mm1_v3_params.json"))))
        M2 = e213_v3.v2_model()
        self.M2 = M2[0] if isinstance(M2, tuple) else M2
        dec = json.load(open(os.path.join(V32, "out", "decisions_v32.json")))
        self.eps_g = dec["steps"]["step4"]["acceptance"]["5"]["LOEO W given t over gemmLnc points (no twin, >= 3 W)"]["v32"] / 100.0
        self.rest = {}
        for arm, a in ARMS.items():
            rl = self.P32["rest_law"][a["card"]]
            T0 = rl["T0_forecast_c"]
            self.rest[arm] = {"T0_c": T0, "W": rl["a"] * T0 * T0 + rl["b"] * T0 + rl["c"], "source": rl["source"]}

    # ---------------------------------------------------------------- one batch of points on one arm at one clock
    def forecast(self, arm, pts, f, models=MODELS):
        """pts: [{'id', 'arm' (token), 'fmt', 'kind', 'mask'}] -> {id: {model: fields}}"""
        card = ARMS[arm]["card"]
        specs = [{"card": card, "arm": p["arm"], "fmt": p["fmt"], "kind": p.get("kind", "random"), "mask": p["mask"], "f": float(f),
                  "kernel": "rgm136"} for p in pts]
        out = {p["id"]: {} for p in pts}
        r32 = self.M32.predict_many(specs) if "MM1-v3.2" in models else [None] * len(pts)
        r31 = self.M31.predict_many(specs) if "MM1-v3.1" in models else [None] * len(pts)
        for j, (p, s) in enumerate(zip(pts, specs)):
            o = out[p["id"]]
            if "MM1-v3.2" in models:
                o["MM1-v3.2"] = self.fields(r32[j])
            if "MM1-v3.1" in models:
                o["MM1-v3.1"] = self.fields(r31[j])
            if "MM1-v3" in models:
                o["MM1-v3"] = self.fields(self.M3.predict(card, p["arm"], p["fmt"], s["kind"], p["mask"], float(f), kernel="rgm136", t0_c=None))
            if "MM1-v2" in models:
                arm2 = p["arm"].replace("gemmLnc", "gemmL").replace("gemmLn", "gemmL")
                o["MM1-v2"] = self.fields(self.M2.predict(card, arm2, p["fmt"], s["kind"], p["mask"], float(f), V=None, t0_c=None),
                                          note=("MM1-v2 has no code-path term: its rgm136 gemmL twin, literally" if arm2 != p["arm"] else ""))
        return out

    @staticmethod
    def fields(p, note=""):
        if p is None:
            return None
        o = {"T_op_us": p["T_op_us"], "cycles_per_op_wall": p["cycles_per_op_wall"], "cycles_per_op_mean": p.get("cycles_per_op_mean"),
             "seconds_per_gemm": p.get("seconds_per_gemm"), "ops_per_minion_per_gemm": p.get("ops_per_minion_per_gemm"), "f_mhz": p.get("f_mhz"),
             "minions": p.get("minions"), "loop": p.get("loop"), "note": note}
        if "W_over_idle" in p:
            o.update({"W_over_idle": p["W_over_idle"], "A_W": p["W_affine"]["A_W"], "B_W_us": p["W_affine"]["B_W_us"],
                      "J_over_idle_per_gemm": p.get("J_over_idle_per_gemm"), "V": p.get("V"), "s_V": p.get("s_V"), "G_W": p.get("G_W"),
                      "die_start_c": p.get("die_start_c")})
            rl = p.get("rest_law")
            if rl:
                o["rest_law_W"] = rl["P_rest_W"]
                o["rest_law_T0_c"] = rl["T0_c"]
                o["J_at_rest_per_gemm"] = rl.get("J_at_rest_per_gemm_REPORTED")
        else:
            o["energy"] = p.get("energy", "NOT FORECAST")
        for k in ("F3_dup", "F3_first", "F3_W_at_own_t", "layout_factor", "rho_wall_over_mean", "footprint_MB"):
            if k in p:
                o[k] = p[k]
        if "Q0" in p and "Q1" in p:
            Q = [[0.5 * (a + b) for a, b in zip(r0, r1)] for r0, r1 in zip(p["Q0"], p["Q1"])]
            o["Q_mean"] = Q
        return o

    def planning_peak(self, arm, fc, token):
        """(PP32, PP_all, by): MM1-v3.2's planning peak (the registered drop) and the largest over the four models (REPORTED)"""
        lnc = token.startswith("gemmLnc")
        x = fc.get("MM1-v3.2")
        if not x or "W_over_idle" not in x:
            return None, None, "MM1-v3.2 does not price it"
        w32 = x["W_over_idle"] * ((1.0 + 2.0 * self.eps_g) if lnc else 1.0)
        ws = [(w32, "MM1-v3.2" + (" x (1 + 2 eps_G)" if lnc else ""))]
        for m in ("MM1-v3.1", "MM1-v3", "MM1-v2"):
            y = fc.get(m)
            if y and "W_over_idle" in y:
                ws.append((y["W_over_idle"], m))
        r = self.rest[arm]["W"]
        w, by = max(ws)
        return w32 + r + 2.0, w + r + 2.0, by


def beyond_of(Q):
    """the gemmLnc term maker's 'beyond' (s05_freeze.feats, e218_v32's family G): 14 (1 - qA[L2]) + 12 (1 - qB[L2]), Q the line map's mean"""
    qA0 = sum(Q[0])
    qB0 = sum(row[0] for row in Q)
    return 14.0 * (1.0 - qA0) + 12.0 * (1.0 - qB0)
