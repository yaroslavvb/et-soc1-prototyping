#!/usr/bin/env python3
"""E224 (Q237): THE FORECASTERS, each from its frozen code unchanged, called the same way by the point rule (desk/point_rule_e224.py) and by
the forecast freeze (forecast_e224.py). numpy through the predictors; single-threaded (the caller sets the four thread variables to 1).
E222's callers (tools/claims-v3/e222/desk/models_e222.py, reg-e222's land, frozen 13:50:25 PST Fri 20 Nov 2026 in E222's FROZEN.txt, sha256
590bcf24...) LINE FOR LINE, with four changes: E224's two cards (E220's, desk/models_e220.py: arm A aifoundry1 card 1 at 600.0 MHz, arm B
aifoundry2 card 0 at 799.0 MHz route c with 700.0 and 600.0 MHz columns), each arm's own rest law in the planning peak; THE EIGHT COMPOSITIONS
(compose_sub below: 'MM1-v3.2 + all three' restricted to any subset of the three terms, E222's SELECTION RULE's own construction); and THE
SWITCH-COUNT INPUTS of E217's operand patterns (enable_e217_counts below: decl-e217's form, its s04c_nominal_counts.py's 'v31' mode, literally:
counts-e217's rows added in memory to energy_v31's E210C31 / SWT31 and its phi in energy_v31's memo, no key colliding; MM1-v3.2 and the
candidates price energy through those tables) for family P's E217 kinds; E222's file names (its extra L3S records, its posimb features) in E224's.

THE FOUR MODELS (E220's calls, desk/models_e220.py, literally; here at E224's arms):
  MM1-v3.2   tools/matmul/mm1/v3.2/mm1_v32.py (landed 4e386f75), Model(out/mm1_v32_params.json).predict_many([{card, arm, fmt, kind, mask, f,
             kernel}]) - THE REGISTERED BASELINE;
  MM1-v3.1   tools/matmul/mm1/v3.1/mm1_v31.py (landed 2c971828), Model(out/mm1_v31_params.json).predict_many([...]);
  MM1-v3     tools/matmul/mm1/v3/mm1_v3.py (landed b1493082), Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, f, kernel, t0_c=None);
  MM1-v2     tools/matmul/mm1/v2 (landed 3ca4b717) through MM1-v3's e213_v3.v2_model(), .predict(card, arm2, fmt, kind, mask, f, V=None,
             t0_c=None), arm2 = the token with gemmLnc read as gemmL.
THE THREE MM1-v3.3 CANDIDATES (tools/matmul/mm1/v3.3-cands/, landed by land-cands, each frozen before any E220 datum; every file they run or
read pinned below by sha256), each MM1-v3.2's own predictor call (the card, the token, fmt, kind, mask, f, kernel rgm136) and its term, by the
term's own frozen code (E222's text, unchanged):
  'MM1-v3.2 + posimb'  posimb/scripts/h01_freeze.py's per-row form, line for line, with h01's own fields() and compose() imported from the file:
             MM1-v3.2's prediction times g_wall = clip(1 + a_hop Phi_hop + a_lag Phi_lag, 0.3, 3.0) (the counter's mean g_mean = clip(1 + a_hop
             Phi_hop)) at the subset points of rgm136's gemmL loop, MM1-v3.2 to the last bit elsewhere;
  'MM1-v3.2 + AF4'     gemmlnc-af4/scripts/s03_freeze.py's per-row form, line for line: F3 removed and AF4 added at MM1-v3.2's own op time;
             cooperative points MM1-v3.2;
  'MM1-v3.2 + L3S'     l3s/scripts/term_l3s.py's ModelL3S(MM1-v3.2's params, lam, cache), lam = l3s/out/fit/fit-l3s.json > lam_all (KEPT), the cache
             l3s/out/feature/l3s_cache.json plus, for a full-mask shape it does not hold, the record l3s/scripts/l3s_feature.py's a_shares() makes
             (no fitted constant: the frozen set model run on the kernel's addresses), kept apart in E224's desk/l3s-extra-e224.json.
HOW EACH CANDIDATE PRICES E224's CARDS: through MM1-v3.2's own per-card constants for the card (E220.md section 1's table: aifoundry1 card 1 kc
1.0228, Pa 1.2425 W, 0.517 V pinned, governed base 0 W, rest law 31.76 W at 55 C; aifoundry2 card 0 kc 1.0946, Pa 1.5082 W, the minion volts
0.517 / 0.568 / 0.618 V at 600 / 700 / 800 MHz, the governed base G(f), rest law 23.19 W at 51 C); posimb's two constants, AF4's two and L3S's
one are the same on every card (none of the three has a card factor). desk/xcheck_cands_e224.py re-makes each candidate's own frozen E220
forecasts at these two cards (E220's 306 rows) through these callers before any E224 forecast.
THE EIGHT COMPOSITIONS (compose_sub, by construction, no refit): E222's SELECTION RULE (E222.md section 7, registered 13:50:25 PST): "MM1-v3.3 =
MM1-v3.2 plus every candidate term whose HC test reads '<candidate> BETTER' and whose NH test reads PASS; with two or more, their composition only
as the registered combination (desk/models_e222.compose restricted to the joining terms: each term is exactly MM1-v3.2 outside its domain, so any
subset composes the same way, with no refit)". Each candidate is MM1-v3.2 exactly outside its domain (posimb: subset masks of rgm136 gemmL; L3S:
the full mask, gemmL-family loops; AF4: gemmLnc tokens), so per point at most posimb, or L3S, or AF4, or L3S with AF4 (a full-mask gemmLnc point)
acts; a subset S of the terms takes, per point, the acting terms that are in S, composed exactly as E222's compose() composes them (posimb alone;
L3S with AF4 by L3S's time and lines with F3's coefficient replaced by AF4's; L3S alone; AF4 alone; else MM1-v3.2). compose_sub(.., all three)
equals E222's compose() at every row (checked at every row by the forecast freeze), and each single term equals that candidate's own forecast.
THE PLANNING PEAK (the drop line, E220's form): PP32 = MM1-v3.2's W over idle at its own seconds at the arm's registered clock, x (1 + 2 eps_G) at
a gemmLnc point (eps_G 0.0843, MM1-v3.2's held-out gemmLnc W error), + MM1-v3.2's rest law for the arm's card at its T0 forecast, + 2 W; PP_all
(REPORTED) the largest over every model and composition of that W (MM1-v3.2's with its factor), the same rest and margin.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
MM1 = os.path.join(REPO, "tools", "matmul", "mm1")
V32, V31, V3, V2 = (os.path.join(MM1, d) for d in ("v3.2", "v3.1", "v3", "v2"))
CANDS_DIR = os.path.join(MM1, "v3.3-cands")
A3 = "aifoundry3 card 0"
C1 = "aifoundry1 card 1"
A2 = "aifoundry2 card 0"
F_REG = 600.0
STOP_W = 70.0
ARMS = {"A": {"card": C1, "f_reg": 600.0, "clocks": (600.0,), "stop_W": 72.0, "die_stop_C": 80.0},
        "B": {"card": A2, "f_reg": 799.0, "clocks": (799.0, 700.0, 600.0), "stop_W": 70.0, "die_stop_C": 70.0}}
MODELS = ("MM1-v3.2", "MM1-v3.1", "MM1-v3", "MM1-v2")
POSIMB, AF4, L3S = "MM1-v3.2 + posimb", "MM1-v3.2 + AF4", "MM1-v3.2 + L3S"
CANDS = (POSIMB, AF4, L3S)
COMBO = "MM1-v3.2 + all three"
# THE EIGHT COMPOSITIONS of MM1-v3.2 with the three terms (none, each alone, each pair, all three), named as E222's SEL prints its outcome
# ("MM1-v3.3 = MM1-v3.2" + " + <term>" for each joining term in E222's CANDS order: posimb, AF4, L3S; score_e222.py, its 'selection')
TERMS = ("posimb", "AF4", "L3S")
COMPOS = {(): "MM1-v3.2", ("posimb",): POSIMB, ("AF4",): AF4, ("L3S",): L3S, ("posimb", "AF4"): "MM1-v3.2 + posimb + AF4",
          ("posimb", "L3S"): "MM1-v3.2 + posimb + L3S", ("AF4", "L3S"): "MM1-v3.2 + AF4 + L3S", ("posimb", "AF4", "L3S"): COMBO}
COMPO_NAMES = tuple(COMPOS[k] for k in ((), ("posimb",), ("AF4",), ("L3S",), ("posimb", "AF4"), ("posimb", "L3S"), ("AF4", "L3S"),
                                       ("posimb", "AF4", "L3S")))
PAIRS = ("MM1-v3.2 + posimb + AF4", "MM1-v3.2 + posimb + L3S", "MM1-v3.2 + AF4 + L3S")
ALL = MODELS + CANDS + (COMBO,) + PAIRS


def sel_string(terms):
    """E222's SEL verdict string for a subset of the terms (score_e222.py: 'MM1-v3.3 = MM1-v3.2' + ' + ' + each joining term, CANDS order)"""
    ts = tuple(t for t in TERMS if t in terms)
    return "MM1-v3.3 = MM1-v3.2" + "".join(" + " + t for t in ts)


SEL_TO_COMPOSITION = {sel_string(k): v for k, v in COMPOS.items()}

# E217's switch-count inputs for its operand patterns (decl-e217, Q228): counts-e217 frozen by COUNTS-FROZEN.txt (4867c1d0..., 12:22:24 PST Thu
# 19 Nov 2026) before any E217 measurement; phi by kinds_v3.phi over each tile file (DECLARED-blind-e217.json > e_switch > phi)
E217_COUNTS = {
    "tools/matmul/mm1/v3.1/blind-e217/counts-e217/counts-fp32-gemm-states.json": None,
    "tools/matmul/mm1/v3.1/blind-e217/counts-e217/counts-fp16-int8-launch.json": None,
    "tools/matmul/mm1/v3.1/blind-e217/DECLARED-blind-e217.json": "633d725620d06295a144312956579fabc54462f109ea3a29e8026d992bdd4eb7",
    "tools/matmul/mm1/v3.1/blind-e217/COUNTS-FROZEN.txt": None,
    "tools/matmul/mm1/v3.1/blind-e217/SHA256SUMS": None,
}
# the zero-row tiles whose float gate decl-e217 DECLARED (gt125, gt25, gt875, h_gt25): never a family-P kind here (no gate is wrapped)
E217_GATED = ("fp32|pattern:gt125", "fp32|pattern:gt25", "fp32|pattern:gt875", "fp16|pattern:h_gt25")
SHAPE = re.compile(r"^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$")
GEMML = re.compile(r"^gemmL(\d+)x(\d+)x(\d+)$")
FULL = 0xFFFFFFFF
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
    # the three candidates' frozen code and records (land-cands; each folder's SHA256SUMS and SHA256SUMS-note1 checked too)
    "tools/matmul/mm1/v3.3-cands/posimb/scripts/h01_freeze.py": "06c9b77b787bc00e6fe2a836f533a951f687c34de43bc5d3ee104c01c921984f",
    "tools/matmul/mm1/v3.3-cands/posimb/scripts/f02_private.py": "183a354a2f691e63b792d61098cf241dbff394761d258f5bdff3efb3096602c7",
    "tools/matmul/mm1/v3.3-cands/posimb/out/fit_results.json": "816d1d51548b68062ffebf26f2c29b815a9069066c9d1f2cd71cb8fb222d3071",
    "tools/matmul/mm1/v3.3-cands/posimb/out/private_shared.json": "aa5c9cf309bc71ab6cbf6d24b75d6a38aaf321477a62dacc7fc04fdb9c459e17",
    "tools/matmul/mm1/v3.3-cands/posimb/DECLARED-posimb.md": "a7cd74a06da23523c32f5059465cfbea4c5dbbc61a24a934f43112b57b1098b9",
    "tools/matmul/mm1/v3.3-cands/posimb/SHA256SUMS": "acef395141bb0ca12f54b22d28a17e129154aa64b12b3f8c0d99ebbd95184ba8",
    "tools/matmul/mm1/v3.3-cands/posimb/SHA256SUMS-note1": "93c2575b073a456b4ffeb91140c63a7d917ca93d2c40176259d74e7ebd2a3d88",
    "tools/matmul/mm1/v3.2-terms/layout/controls-e215/v01_map.py": "b5a88d33c31f305c2c2bcf93c8bc7f5694cb8c5a8c32536d634da9b7cca66e3f",
    "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/scripts/s02_fit.py": "547415c16c777926097969ad7beb77d33b236e97cec4dc54bd7dbe41d977c3df",
    "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/scripts/s03_freeze.py": "81d96e2d841a2526823f84aec6d1df2c548c7d5c4de129314ef0cf7d18328f06",
    "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/data/fit-record.json": "d5aea26ad2adb67e1cbbfaa90eb7fa5d51db5297b651fb618f91772e01cf8acc",
    "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/term-gemmlnc-af4.json": "dfcd58a025b56d547d5b16a334f2a9db12d2d3ba008d18e3ddc423c60fc3900e",
    "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/SHA256SUMS": "ef885cb8cdf37dffb1be511b2f6ccdaa1eb37a8f7780590bc95444c9c3e2f8b9",
    "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/SHA256SUMS-note1": "d6f13cf2748c88f08bfee05c88c9e5e0efe36f754e642eed97cfa06a93430771",
    "tools/matmul/mm1/v3.3-cands/l3s/scripts/term_l3s.py": "d53a67a76a108c93865880448baa3ecde7730d7999a67c862133c0506ceae63c",
    "tools/matmul/mm1/v3.3-cands/l3s/scripts/costs.py": "d3991731a7839ede37b69a04970a2ad4788f65a10caf9c6575d9ff9b54074bf2",
    "tools/matmul/mm1/v3.3-cands/l3s/scripts/l3s_feature.py": "8a7b506a09baae1602dd208b4e2b11d34b656605e53e785e363c6d74ebb513f0",
    "tools/matmul/mm1/v3.3-cands/l3s/scripts/e220_l3s.py": "26932df86362d54eab99a94fdcc79b46e2c802a4d57baf09aae5ddb59d73be9b",
    "tools/matmul/mm1/v3.3-cands/l3s/out/fit/fit-l3s.json": "4fe923507f7fef4d9925e8d5746727a0024b0ea42465dc0d463553e9936d750b",
    "tools/matmul/mm1/v3.3-cands/l3s/out/feature/l3s_cache.json": "6171c473e57534be7ca6828f08d989887b770d1197d98044068fa9efaac0668c",
    "tools/matmul/mm1/v3.3-cands/l3s/SHA256SUMS": "c5d4f03e4364d451f988c7bd09f63f380e78a93cdb2f6e472899594bbe731091",
    "tools/matmul/mm1/v3.3-cands/l3s/SHA256SUMS-note1": "d9ec0f79db4e236ac6e51ae4a9021d41ace01db9a5264bcede8ae0ee65503b5f",
}
L3S_EXTRA = os.path.join(HERE, "l3s-extra-e224.json")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha_rel(rel):
    return sha(os.path.join(REPO, rel))


def check_pins():
    bad = {k: sha_rel(k) for k, v in PINS.items() if sha_rel(k) != v}
    if bad:
        print("models_e224: REFUSED, a pinned input changed:", bad)
        sys.exit(4)
    for d in (V32, V31, V3, V2):
        if os.system(f"cd '{d}' && sha256sum -c --quiet SHA256SUMS > /dev/null 2>&1") != 0:
            print(f"models_e224: REFUSED, SHA256SUMS check failed in {os.path.relpath(d, REPO)}")
            sys.exit(4)
    for c in ("posimb", "gemmlnc-af4", "l3s"):
        d = os.path.join(CANDS_DIR, c)
        for s in ("SHA256SUMS", "SHA256SUMS-note1"):
            if os.system(f"cd '{d}' && sha256sum -c --quiet {s} > /dev/null 2>&1") != 0:
                print(f"models_e224: REFUSED, {s} check failed in {os.path.relpath(d, REPO)}")
                sys.exit(4)
    return dict(PINS)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def shape_of(arm):
    m = SHAPE.match(arm)
    return tuple(int(x) for x in m.groups()) if m else None


def fields(p, note=""):
    """E220's models_e220.Models.fields, literally"""
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


def beyond_of(Q):
    """the gemmLnc term maker's 'beyond': 14 (1 - qA[L2]) + 12 (1 - qB[L2]), Q the line map's mean (models_e220.beyond_of)"""
    qA0 = sum(Q[0])
    qB0 = sum(row[0] for row in Q)
    return 14.0 * (1.0 - qA0) + 12.0 * (1.0 - qB0)


class Models:
    def __init__(self, cands=True, e217=True):
        self.pins = check_pins()
        sys.path.insert(0, V32)
        import mm1_v32  # noqa: E402
        self.mm1_v32 = mm1_v32
        self.P32 = json.load(open(os.path.join(V32, "out", "mm1_v32_params.json")))
        self.M32 = mm1_v32.Model(self.P32)
        self.e217 = None
        if e217:                                    # E217's switch-count inputs, before any forecast (decl-e217's form)
            self.enable_e217_counts()
        import mm1_v31  # noqa: E402
        self.P31 = json.load(open(os.path.join(V31, "out", "mm1_v31_params.json")))
        self.M31 = mm1_v31.Model(self.P31)
        sys.path.insert(0, V3)
        import mm1_v3  # noqa: E402
        import e213_v3  # noqa: E402
        import mm1_core_v3  # noqa: E402
        self.CORE = mm1_core_v3
        self.M3 = mm1_v3.Model(json.load(open(os.path.join(V3, "out", "mm1_v3_params.json"))))
        M2 = e213_v3.v2_model()
        self.M2 = M2[0] if isinstance(M2, tuple) else M2
        dec = json.load(open(os.path.join(V32, "out", "decisions_v32.json")))
        self.eps_g = dec["steps"]["step4"]["acceptance"]["5"]["LOEO W given t over gemmLnc points (no twin, >= 3 W)"]["v32"] / 100.0
        self.rest = {}
        for arm, a in ARMS.items():                  # E220's models_e220.Models.rest, literally: each arm's card's rest law at its T0 forecast
            rl = self.P32["rest_law"][a["card"]]
            T0 = rl["T0_forecast_c"]
            self.rest[arm] = {"T0_c": T0, "W": rl["a"] * T0 * T0 + rl["b"] * T0 + rl["c"], "source": rl["source"]}
        self.th = self.P32["time"]["theta"]
        self.form = self.P32["time"]["form"]
        self.cands_loaded = False
        if cands:
            self._load_cands()

    # ---------------------------------------------------------------- the three candidates' frozen code
    def _load_cands(self):
        import time_v31 as TV  # noqa: E402  (MM1-v3.1's time engine, the one MM1-v3.2 runs; imported by mm1_v32 at its pin)
        self.TV = TV
        # posimb: h01_freeze.py and f02_private.py from the landed folder, unchanged; their LAYOUT2_LANE paths resolved to a staging folder of
        # symbolic links (work/lab -> the lab's top, scripts -> the landed scripts), so h01's module code and f02's v01_map import run as landed
        self._stage = tempfile.mkdtemp(prefix="e224-posimb-stage-")
        os.makedirs(os.path.join(self._stage, "work"))
        os.symlink(REPO, os.path.join(self._stage, "work", "lab"))
        os.symlink(os.path.join(CANDS_DIR, "posimb", "scripts"), os.path.join(self._stage, "scripts"))
        os.environ["LAYOUT2_LANE"] = self._stage
        self.H01 = load("h01_freeze_landed", os.path.join(CANDS_DIR, "posimb", "scripts", "h01_freeze.py"))
        self.F02 = self.H01.F02
        fit = json.load(open(os.path.join(CANDS_DIR, "posimb", "out", "fit_results.json")))
        assert fit["declaration_sha256"] == PINS["tools/matmul/mm1/v3.3-cands/posimb/DECLARED-posimb.md"] and fit["keep_rule"]["KEPT"] is True
        self.a_hop, self.a_lag = fit["constants_all_data"]["posimb"]
        self.PS = json.load(open(os.path.join(CANDS_DIR, "posimb", "out", "private_shared.json")))
        self.PS_made = {}
        # AF4: s02_fit.py's feats() taken from the file's text exactly as s03_freeze.py takes it; the constants from the fit record
        src = open(os.path.join(CANDS_DIR, "gemmlnc-af4", "scripts", "s02_fit.py")).read()
        ns = {"np": np, "C": self.CORE, "X1": float(self.th["x1"])}
        exec(src[src.index("def feats("):src.index("FORMS = {")], ns)
        self.feats = ns["feats"]
        FIT = json.load(open(os.path.join(CANDS_DIR, "gemmlnc-af4", "data", "fit-record.json")))
        assert FIT["choice"]["form"] == "AF4" and FIT["choice"]["status"] == "KEPT", FIT["choice"]
        self.CONST_AF4 = FIT["forms"]["AF4"]["constants_all_data_pJ"]
        self.C1V, self.C2V = self.P32["energy"]["F3"]["c1_pJ"], self.P32["energy"]["F3"]["c2_pJ"]
        # L3S: term_l3s.ModelL3S at the all-data lam; the landed cache plus E224's extra records (made by the frozen l3s_feature.a_shares)
        sys.path.insert(0, os.path.join(CANDS_DIR, "l3s", "scripts"))
        import term_l3s as TL  # noqa: E402
        import l3s_feature as LF  # noqa: E402
        self.TL, self.LF = TL, LF
        fl = json.load(open(os.path.join(CANDS_DIR, "l3s", "out", "fit", "fit-l3s.json")))
        assert fl["kept"] is True
        self.lam = float(fl["lam_all"])
        self.l3s_cache = TL.load_cache()
        self.l3s_extra = json.load(open(L3S_EXTRA)) if os.path.exists(L3S_EXTRA) else {}
        for k, v in self.l3s_extra.items():
            assert k not in self.l3s_cache
            self.l3s_cache[k] = v
        self.ML3S = TL.ModelL3S(self.P32, self.lam, self.l3s_cache)
        self.cands_loaded = True

    def l3s_ensure(self, specs):
        """add, for every full-mask gemmL-family shape the L3S cache lacks, the frozen set model's record (l3s_feature.a_shares) to the extra
        records; returns the keys made"""
        made = []
        for s in specs:
            k = self.LF.domain_key({"arm": s["arm"], "mask": s["mask"], "kernel": ("rgm211" if self.TV.E.arm_parts(s["arm"])[0] == "gemmLn" else "rgm136")})
            if k is None:
                continue
            key = "%dx%dx%d:%s" % k
            if key not in self.l3s_cache:
                rec = self.LF.a_shares(*k)
                self.l3s_cache[key] = rec
                self.l3s_extra[key] = rec
                made.append(key)
        return made

    def save_l3s_extra(self):
        json.dump(self.l3s_extra, open(L3S_EXTRA, "w"), indent=1, sort_keys=True)

    # ---------------------------------------------------------------- posimb, h01_freeze.main's per-row form
    def posimb_rows(self, specs, base):
        th, form = self.th, self.form
        ths = dict(th)
        for k in self.H01.MEMK:
            ths[k] = th[k] * 1.01
        pts = []
        for s in specs:
            pre, b = self.TV.E.arm_parts(s["arm"])
            kernel = "rgm211" if pre == "gemmLn" else ("run_gemm" if pre is None else "rgm136")
            pts.append({"arm": s["arm"], "kernel": kernel, "fmt": s["fmt"], "mask": s["mask"], "f": s["f"]})
        en = self.TV.Engine31(pts)
        T0 = en.predict(th, form)
        T1 = en.predict(ths, form)
        e = np.log(T1 / T0) / np.log(1.01)
        out = []
        for j, (s, bp) in enumerate(zip(specs, base)):
            assert abs(T0[j] / bp["T_op_us"] - 1) < 1e-12, "engine and predictor differ"
            m = int(s["mask"], 16)
            in_scope = m != FULL and pts[j]["kernel"] == "rgm136" and bool(self.H01.SHAPE.match(s["arm"]))
            G1c = LAGc = 0.0
            feat = None
            if in_scope:
                key = "%s|0x%x" % (s["arm"], m)
                if key not in self.PS:
                    MB, NB, KB = (int(x) for x in self.H01.SHAPE.match(s["arm"]).groups())
                    rr = self.F02.private_shared(MB, NB, KB, m)
                    rr.update(self.F02.mesh_lat(m))
                    self.PS[key] = rr
                    self.PS_made[key] = rr
                feat = self.PS[key]
                G1c = feat["Lmean_act"] / feat["Lmean_full"] - 1.0
                Fsum = feat["Fp"] + feat["Fs"]
                LAGc = ((feat["Lmax_act"] - feat["Lmean_act"]) / feat["Lmean_full"]) * (feat["Fp"] / Fsum if Fsum > 0 else 0.0)
            ph_hop, ph_lag = float(e[j] * G1c), float(e[j] * LAGc)
            gw = float(np.clip(1.0 + self.a_hop * ph_hop + self.a_lag * ph_lag, 0.3, 3.0)) if in_scope else 1.0
            gm = float(np.clip(1.0 + self.a_hop * ph_hop, 0.3, 3.0)) if in_scope else 1.0
            bf = self.H01.fields(bp)
            cf = self.H01.compose(bf, gw, gm)
            out.append({"in_scope": bool(in_scope), "e": float(e[j]), "G1core": G1c, "LAGcore": LAGc, "Phi_hop": ph_hop, "Phi_lag": ph_lag,
                        "g_wall": gw, "g_mean": gm, "Fp": (feat or {}).get("Fp"), "Fs": (feat or {}).get("Fs"),
                        "Lmean_act": (feat or {}).get("Lmean_act"), "Lmax_act": (feat or {}).get("Lmax_act"), "h01": cf, "P_rest": bf.get("_P_rest")})
        return out

    # ---------------------------------------------------------------- AF4, s03_freeze.py's per-row form
    def af4_rows(self, specs, base):
        out = []
        for s, o in zip(specs, base):
            lnc = s["arm"].startswith("gemmLnc")
            A_, B_ = o["W_affine"]["A_W"], o["W_affine"]["B_W_us"]
            t = o["T_op_us"]
            Wv = A_ + B_ / t
            f3 = o["F3_W_at_own_t"]
            rl = o.get("rest_law") or {}
            sec = o["seconds_per_gemm"]
            r = {"lnc": lnc, "MM1-v3.2_W_over_idle": Wv, "MM1-v3.2_F3_W": f3}
            if lnc:
                assert abs(o["F3_dup"] - 26.0) < 1e-12
                S_own = f3 / (self.C1V * 26.0 + self.C2V * o["F3_first"])
                Q = 0.5 * (np.array(o["Q0"]) + np.array(o["Q1"]))
                ft = self.feats(shape_of(s["arm"]), s["fmt"], Q.sum(axis=1).tolist(), Q.sum(axis=0).tolist(), s["mask"])
                r["features"] = {k: ft[k] for k in ("dup", "beyond", "first", "qA_b", "qBF", "phi", "m", "a_f", "a3", "Lres", "R1", "R2", "R3", "R4",
                                                    "stepNB3", "footprint_MB")}
                r["S_W_per_pJ_minion_op"] = S_own
                E4 = float(np.dot(self.CONST_AF4, [ft["dup"], ft["R4"]]))
                dW = S_own * E4
            else:
                assert f3 == 0.0, (s["arm"], f3)
                S_own, dW, E4 = None, 0.0, 0.0
            Wn = Wv - f3 + dW
            Bn = B_ - f3 * t + dW * t
            r.update({"term_AF4_E_pJ_per_minion_op": E4, "term_AF4_W": dW, "W_over_idle": Wn, "A_W": A_, "B_W_us": Bn,
                      "J_over_idle_per_gemm_t_forecast": Wn * sec, "rest_law_W": rl.get("P_rest_W"),
                      "J_at_rest_per_gemm_t_forecast": ((rl["P_rest_W"] + Wn) * sec) if rl else None})
            out.append(r)
        return out

    # ---------------------------------------------------------------- one batch of points on one card at one clock
    def forecast(self, pts, f=F_REG, card=A3, models=MODELS, cands=True, which=("posimb", "af4", "l3s")):
        """pts: [{'id', 'arm' (token), 'fmt', 'kind', 'mask'}] -> {id: {model or candidate: fields}}; `which` limits the candidates made (the
        point rule asks one candidate at a time where it ranks by it); the combination only when all three are made"""
        specs = [{"card": card, "arm": p["arm"], "fmt": p["fmt"], "kind": p.get("kind", "random"), "mask": p["mask"], "f": float(f),
                  "kernel": "rgm136"} for p in pts]
        out = {p["id"]: {} for p in pts}
        r32 = self.M32.predict_many(specs)
        r31 = self.M31.predict_many(specs) if "MM1-v3.1" in models else None
        for j, (p, s) in enumerate(zip(pts, specs)):
            o = out[p["id"]]
            o["MM1-v3.2"] = fields(r32[j])
            if "MM1-v3.1" in models:
                o["MM1-v3.1"] = fields(r31[j])
            if "MM1-v3" in models:
                o["MM1-v3"] = fields(self.M3.predict(card, p["arm"], p["fmt"], s["kind"], p["mask"], float(f), kernel="rgm136", t0_c=None))
            if "MM1-v2" in models:
                arm2 = p["arm"].replace("gemmLnc", "gemmL").replace("gemmLn", "gemmL")
                o["MM1-v2"] = fields(self.M2.predict(card, arm2, p["fmt"], s["kind"], p["mask"], float(f), V=None, t0_c=None),
                                     note=("MM1-v2 has no code-path term: its rgm136 gemmL twin, literally" if arm2 != p["arm"] else ""))
        if not cands:
            return out
        assert self.cands_loaded
        # the candidates
        pr = self.posimb_rows(specs, r32) if "posimb" in which else None
        ar = self.af4_rows(specs, r32) if "af4" in which else None
        if "l3s" in which:
            self.l3s_ensure(specs)
            lr = self.ML3S.predict_many(specs)
            dom, fsa = self.TL.features([{"arm": s["arm"], "kernel": ("rgm211" if self.TV.E.arm_parts(s["arm"])[0] == "gemmLn" else "rgm136"),
                                          "mask": s["mask"], "fmt": s["fmt"], "f": s["f"]} for s in specs], self.l3s_cache)
        for j, (p, s) in enumerate(zip(pts, specs)):
            o = out[p["id"]]
            b = o["MM1-v3.2"]
            if pr is None:
                pass
            else:
                self._posimb_out(o, pr[j])
            if ar is not None:
                self._af4_out(o, b, ar[j])
            if "l3s" in which:
                self._l3s_out(o, lr[j], dom[j], fsa[j])
            if pr is not None and ar is not None and "l3s" in which:
                o[COMBO] = compose(p, o, self)
                # the pairs by compose_sub (E222's SEL: the registered combination restricted to the joining terms); compose_sub at all three
                # and at each single term re-made here and checked equal to E222's compose() and to the candidate itself (exit 5 otherwise)
                for terms in (("posimb", "AF4"), ("posimb", "L3S"), ("AF4", "L3S")):
                    o[COMPOS[terms]] = compose_sub(p, o, self, terms)
                chk = compose_sub(p, o, self, TERMS)
                if not _close(chk, o[COMBO], 0.0) or chk["acting"] != o[COMBO]["acting"]:
                    print(f"models_e224.compose_sub: REFUSED at {p['id']}: all three differs from E222's compose()")
                    sys.exit(5)
                for t, n in (("posimb", POSIMB), ("AF4", AF4), ("L3S", L3S)):
                    one = compose_sub(p, o, self, (t,))
                    ref = o[n] if one["acting"] else o["MM1-v3.2"]
                    if not _close(one, ref):
                        print(f"models_e224.compose_sub: REFUSED at {p['id']}: {t} alone differs from its own forecast")
                        sys.exit(5)
        return out

    def _posimb_out(self, o, prj):
        if True:
            # posimb (h01's compose: MM1-v3.2's affine W at the new op time)
            c = prj["h01"]
            o[POSIMB] = {"T_op_us": c["T_op_us"], "cycles_per_op_wall": c["cycles_per_op_wall"], "cycles_per_op_mean": c["cycles_per_op_mean"],
                         "seconds_per_gemm": c["seconds_per_gemm"], "W_over_idle": c.get("W_over_idle"), "A_W": c.get("A_W"), "B_W_us": c.get("B_W_us"),
                         "J_over_idle_per_gemm": c.get("J_over_idle_per_gemm"), "J_at_rest_per_gemm": c.get("J_at_rest_per_gemm"),
                         "rest_law_W": prj["P_rest"], "in_scope": prj["in_scope"],
                         "term": {k: prj[k] for k in ("e", "G1core", "LAGcore", "Phi_hop", "Phi_lag", "g_wall", "g_mean", "Fp", "Fs", "Lmean_act", "Lmax_act")}}

    def _af4_out(self, o, b, a):
        if True:
            # AF4 (time MM1-v3.2's)
            o[AF4] = {"T_op_us": b["T_op_us"], "cycles_per_op_wall": b["cycles_per_op_wall"], "cycles_per_op_mean": b["cycles_per_op_mean"],
                      "seconds_per_gemm": b["seconds_per_gemm"], "W_over_idle": a["W_over_idle"], "A_W": a["A_W"], "B_W_us": a["B_W_us"],
                      "J_over_idle_per_gemm": a["J_over_idle_per_gemm_t_forecast"], "J_at_rest_per_gemm": a["J_at_rest_per_gemm_t_forecast"],
                      "rest_law_W": a["rest_law_W"], "in_scope": a["lnc"],
                      "term": {"term_AF4_W": a["term_AF4_W"], "term_AF4_E_pJ_per_minion_op": a["term_AF4_E_pJ_per_minion_op"],
                               "MM1-v3.2_F3_W": a["MM1-v3.2_F3_W"], "features": a.get("features"), "S_W_per_pJ_minion_op": a.get("S_W_per_pJ_minion_op")}}

    def _l3s_out(self, o, q, domj, fsaj):
        if True:
            # L3S (e220_l3s.flat's fields)
            wa = q.get("W_affine") or {}
            rl = q.get("rest_law") or {}
            o[L3S] = {"T_op_us": q["T_op_us"], "cycles_per_op_wall": q["cycles_per_op_wall"], "cycles_per_op_mean": q.get("cycles_per_op_mean"),
                      "seconds_per_gemm": q.get("seconds_per_gemm"), "W_over_idle": q.get("W_over_idle"), "A_W": wa.get("A_W"), "B_W_us": wa.get("B_W_us"),
                      "J_over_idle_per_gemm": q.get("J_over_idle_per_gemm"), "J_at_rest_per_gemm": rl.get("J_at_rest_per_gemm_REPORTED"),
                      "rest_law_W": rl.get("P_rest_W"), "in_scope": bool(domj),
                      "term": {"set_model_A_fresh_share": ([None, None] if not domj else [float(fsaj[0]), float(fsaj[1])]),
                               "F3_W_at_own_t": q.get("F3_W_at_own_t"), "lines_L2_L3_F_per_shire_op": q.get("lines_L2_L3_F_per_shire_op"),
                               "Q_mean": fields(q).get("Q_mean")}}

    def planning_peak(self, arm, fc, token):
        """(PP32, PP_all, by): MM1-v3.2's planning peak on the arm (the registered drop) and the largest over every model and composition
        (REPORTED); the arm's own rest law (E220's models_e220.planning_peak, literally)"""
        lnc = token.startswith("gemmLnc")
        x = fc.get("MM1-v3.2")
        if not x or "W_over_idle" not in x:
            return None, None, "MM1-v3.2 does not price it"
        w32 = x["W_over_idle"] * ((1.0 + 2.0 * self.eps_g) if lnc else 1.0)
        ws = [(w32, "MM1-v3.2" + (" x (1 + 2 eps_G)" if lnc else ""))]
        for m in ALL[1:]:
            y = fc.get(m)
            if y and y.get("W_over_idle") is not None:
                ws.append((y["W_over_idle"], m))
        r = self.rest[arm]["W"]
        w, by = max(ws)
        return w32 + r + 2.0, w + r + 2.0, by

    # ---------------------------------------------------------------- E217's switch-count inputs (decl-e217's s04c 'v31' form, literally)
    def enable_e217_counts(self):
        """add counts-e217's rows to energy_v31's E210C31 (fp32, S1 and S2) and SWT31 (fp16, int8) and E217's phi (kinds_v3.phi over each tile
        file, as decl-e217 declared it) to energy_v31's phi memo, in memory, before any E217-kind forecast; no key collides (asserted). MM1-v3.2
        (energy_v32 reads energy_v31's tables), MM1-v3.1 and the candidates (MM1-v3.2's own predictor calls) then price E217's kinds; MM1-v3
        (energy_v3's own tables) and MM1-v2 are not given them (NOT FORECAST for those kinds). Returns the record of what was added."""
        if self.e217 is not None:
            return self.e217
        pins = {}
        for rel, want in E217_COUNTS.items():
            got = sha_rel(rel)
            if want is not None and got != want:
                print(f"models_e224: REFUSED, {rel} is {got}, pinned {want}")
                sys.exit(4)
            pins[rel] = got
        bdir = os.path.join(MM1, "v3.1", "blind-e217")
        if os.system(f"cd '{bdir}' && sha256sum -c --quiet SHA256SUMS > /dev/null 2>&1") != 0:
            print("models_e224: REFUSED, SHA256SUMS check failed in tools/matmul/mm1/v3.1/blind-e217")
            sys.exit(4)
        import energy_v31 as EV  # noqa: E402  (the module MM1-v3.2's energy_v32 imported: the same tables)
        C32n = json.load(open(os.path.join(REPO, "tools/matmul/mm1/v3.1/blind-e217/counts-e217/counts-fp32-gemm-states.json")))["shapes"]
        C16n = json.load(open(os.path.join(REPO, "tools/matmul/mm1/v3.1/blind-e217/counts-e217/counts-fp16-int8-launch.json")))["rows"]
        PHI = json.load(open(os.path.join(REPO, "tools/matmul/mm1/v3.1/blind-e217/DECLARED-blind-e217.json")))["e_switch"]["phi"]
        added = []
        for sh in ("S1", "S2"):
            for k, r in C32n[sh].items():
                assert k not in EV.E210C31[sh], (sh, k)
                EV.E210C31[sh][k] = r
                added.append(f"E210C31[{sh}][{k}]")
        for k, r in C16n.items():
            assert k not in EV.SWT31, k
            EV.SWT31[k] = r
            added.append(f"SWT31[{k}]")
        for key, v in PHI.items():
            fmt, kind = key.split("|", 1)
            for kb1 in (True, False):
                assert (fmt, kind, kb1) not in EV._PHI31
                EV._PHI31[(fmt, kind, kb1)] = (float(v["phi"]), "kinds_v3.phi over E217's registered tile file (decl-e217's declaration)")
        self.e217 = {"pins": pins, "rows_added": added, "phi_added": sorted(PHI), "gated_never_used": list(E217_GATED)}
        return self.e217


def compose(p, o, M):
    """'MM1-v3.2 + all three' by construction (no refit): see the module's text; every condition checked here, exit 5 otherwise"""
    b, ps, af, ls = o["MM1-v3.2"], o[POSIMB], o[AF4], o[L3S]
    inp, ina, inl = bool(ps["in_scope"]), bool(af["in_scope"]), bool(ls["in_scope"])
    keys = ("T_op_us", "cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
            "J_at_rest_per_gemm")

    def refuse(why):
        print(f"models_e224.compose: REFUSED at {p['id']} ({p['arm']} {p['mask']}): {why}")
        sys.exit(5)
    if inp and (ina or inl):
        refuse("posimb's scope overlaps another term's")
    acting = [n for n, v in ((POSIMB, inp), (AF4, ina), (L3S, inl)) if v]
    for n, v, x in ((POSIMB, inp, ps), (AF4, ina, af), (L3S, inl, ls)):
        if not v and not _close(x, b):
            refuse(f"{n} differs from MM1-v3.2 outside its domain (beyond 1e-12 relative)")
    if inp:
        c = {k: ps.get(k) for k in keys}
        how = "posimb alone (L3S and AF4 equal MM1-v3.2 here)"
    elif inl and ina:
        f3c_v32 = af["term"]["MM1-v3.2_F3_W"] * b["T_op_us"]
        f3c_l3s = ls["term"]["F3_W_at_own_t"] * ls["T_op_us"]
        if abs(f3c_l3s / f3c_v32 - 1.0) > 1e-9:
            refuse(f"F3's coefficient differs under L3S ({f3c_l3s} vs {f3c_v32})")
        Qv, Ql = np.array(b["Q_mean"]), np.array(ls["term"]["Q_mean"])
        if abs(Qv.sum(axis=1)[0] - Ql.sum(axis=1)[0]) > 1e-12 or np.max(np.abs(Qv.sum(axis=0) - Ql.sum(axis=0))) > 1e-12:
            refuse("L3S moved A's L2 share or B's marginal (AF4's features would change)")
        dWc = af["term"]["term_AF4_W"] * b["T_op_us"]
        t = ls["T_op_us"]
        B2 = ls["B_W_us"] - f3c_v32 + dWc
        W2 = ls["A_W"] + B2 / t
        sec = ls["seconds_per_gemm"]
        c = {"T_op_us": t, "cycles_per_op_wall": ls["cycles_per_op_wall"], "cycles_per_op_mean": ls["cycles_per_op_mean"], "seconds_per_gemm": sec,
             "W_over_idle": W2, "A_W": ls["A_W"], "B_W_us": B2, "J_over_idle_per_gemm": W2 * sec,
             "J_at_rest_per_gemm": ((ls["rest_law_W"] + W2) * sec) if ls.get("rest_law_W") is not None else None}
        how = "L3S's time and lines with F3's coefficient replaced by AF4's (F3 t and dW t are op-time independent; AF4's features unchanged by L3S)"
    elif inl:
        c = {k: ls.get(k) for k in keys}
        how = "L3S alone (posimb and AF4 equal MM1-v3.2 here)"
    elif ina:
        c = {k: af.get(k) for k in keys}
        how = "AF4 alone (posimb and L3S equal MM1-v3.2 here)"
    else:
        c = {k: b.get(k) for k in keys}
        how = "MM1-v3.2 (no term acts)"
    c["rest_law_W"] = b.get("rest_law_W")
    c["acting"] = acting
    c["how"] = how
    return c


def compose_sub(p, o, M, terms):
    """THE REGISTERED COMBINATION RESTRICTED TO THE JOINING TERMS (E222's SEL), for any subset `terms` of ('posimb', 'AF4', 'L3S'): compose()'s
    conditions checked on every term (exit 5 otherwise), then per point the terms that act AND are in the subset, composed exactly as compose()
    composes them (the same arithmetic, line for line); a term outside the subset is left out as if it did not act (MM1-v3.2 there)."""
    terms = tuple(terms)
    assert all(t in TERMS for t in terms), terms
    b, ps, af, ls = o["MM1-v3.2"], o[POSIMB], o[AF4], o[L3S]
    inp, ina, inl = bool(ps["in_scope"]), bool(af["in_scope"]), bool(ls["in_scope"])
    keys = ("T_op_us", "cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
            "J_at_rest_per_gemm")

    def refuse(why):
        print(f"models_e224.compose_sub: REFUSED at {p['id']} ({p['arm']} {p['mask']}) for {terms}: {why}")
        sys.exit(5)
    if inp and (ina or inl):
        refuse("posimb's scope overlaps another term's")
    for n, v, x in ((POSIMB, inp, ps), (AF4, ina, af), (L3S, inl, ls)):
        if not v and not _close(x, b):
            refuse(f"{n} differs from MM1-v3.2 outside its domain (beyond 1e-12 relative)")
    inp, ina, inl = inp and "posimb" in terms, ina and "AF4" in terms, inl and "L3S" in terms
    acting = [n for n, v in ((POSIMB, inp), (AF4, ina), (L3S, inl)) if v]
    if inp:
        c = {k: ps.get(k) for k in keys}
        how = "posimb alone (L3S and AF4 equal MM1-v3.2 here, or not joining)"
    elif inl and ina:
        f3c_v32 = af["term"]["MM1-v3.2_F3_W"] * b["T_op_us"]
        f3c_l3s = ls["term"]["F3_W_at_own_t"] * ls["T_op_us"]
        if abs(f3c_l3s / f3c_v32 - 1.0) > 1e-9:
            refuse(f"F3's coefficient differs under L3S ({f3c_l3s} vs {f3c_v32})")
        Qv, Ql = np.array(b["Q_mean"]), np.array(ls["term"]["Q_mean"])
        if abs(Qv.sum(axis=1)[0] - Ql.sum(axis=1)[0]) > 1e-12 or np.max(np.abs(Qv.sum(axis=0) - Ql.sum(axis=0))) > 1e-12:
            refuse("L3S moved A's L2 share or B's marginal (AF4's features would change)")
        dWc = af["term"]["term_AF4_W"] * b["T_op_us"]
        t = ls["T_op_us"]
        B2 = ls["B_W_us"] - f3c_v32 + dWc
        W2 = ls["A_W"] + B2 / t
        sec = ls["seconds_per_gemm"]
        c = {"T_op_us": t, "cycles_per_op_wall": ls["cycles_per_op_wall"], "cycles_per_op_mean": ls["cycles_per_op_mean"], "seconds_per_gemm": sec,
             "W_over_idle": W2, "A_W": ls["A_W"], "B_W_us": B2, "J_over_idle_per_gemm": W2 * sec,
             "J_at_rest_per_gemm": ((ls["rest_law_W"] + W2) * sec) if ls.get("rest_law_W") is not None else None}
        how = "L3S's time and lines with F3's coefficient replaced by AF4's (F3 t and dW t are op-time independent; AF4's features unchanged by L3S)"
    elif inl:
        c = {k: ls.get(k) for k in keys}
        how = "L3S alone (posimb and AF4 equal MM1-v3.2 here, or not joining)"
    elif ina:
        c = {k: af.get(k) for k in keys}
        how = "AF4 alone (posimb and L3S equal MM1-v3.2 here, or not joining)"
    else:
        c = {k: b.get(k) for k in keys}
        how = "MM1-v3.2 (no joining term acts)"
    c["rest_law_W"] = b.get("rest_law_W")
    c["acting"] = acting
    c["how"] = how
    c["terms"] = list(terms)
    return c


def _close(x, y, tol=1e-12):
    """a candidate outside its domain is MM1-v3.2 (its maker's words: 'to the last bit'); the recomposed affine W and J may differ from the
    predictor's own in the last digits, so equality is read to 1e-12 relative on every quantity"""
    for k in ("T_op_us", "cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
              "J_at_rest_per_gemm"):
        a, b = x.get(k), y.get(k)
        if a is None and b is None:
            continue
        if a is None or b is None or abs(a - b) > tol * max(abs(a), abs(b), 1e-300):
            return False
    return True
