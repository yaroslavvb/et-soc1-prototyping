#!/usr/bin/env python3
"""Q140(e): the heat replicates' frozen predictions for E166 (aifoundry3 card 0) and E167 (aifoundry2 card 0). Desk only.

Registered first in REGISTRATION.md (commit 11174d20, 02:23:53 PST Wed 4 Nov 2026); this file was written after that commit and computes
what the registration's R7 names. Nothing is fitted: every number comes from frozen code imported unchanged after a sha256 check.

  * the duty convention (R1): a hold's kernel duty = the time in every kernel-launch record of its work processes (the calibration
    launch included) over the span from its first process's start to its last process's end, from the launch records alone;
  * aifoundry3 (R5): Q138(t)'s chain closed through E97's law from R0's room, on dispatch records (score_e144's s_on_grid and
    closed_on_grid, E154's registered arm E machinery), each record on at M8's frozen S; the plan's records are E154's for the same item;
  * aifoundry2 (R1, R2): Q139(e)'s composition (M8's burst board moved to the die by 0.442 W/C from 56.0 C, the chain, the governor's
    trip and M8's 65.2 W cap) with the switching part scaled by the kernel duty d, and M8's level replaced by M9's (Q140(l)'s T2 shift
    through its refit relation, option (a)) in the primary;
  * the windows (R3): the plateau is the 300 s ending at the hold's last process; checkpoints from the first process's start.

    /usr/bin/python3 docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py > .../predictions-q140e.txt
writes predictions-q140e.json beside itself (about 1-2 minutes). `--selftest` runs the reproduction checks only. numpy 1.26.4, Python 3.9.
As a module (for E166's and E167's scorers): a3_records, a2_records, kernel_duty, a3_arm_e_on_records, a3_read, a2_hold,
a2_closed_dl, a2_fixed_800, a2_trip_clock_dl, level_offsets.
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")
Q139E = os.path.join(DATA, "2026-11-03-q139e-heat-end-to-end")
Q138T = os.path.join(DATA, "2026-11-02-q138t-heat-model")
Q140L = os.path.join(DATA, "2026-11-04-q140l-a2-session-terms")
E154D = os.path.join(DATA, "2026-11-03-e154-heat-e2e-aifoundry3")
E154P = os.path.join(E154D, "aifoundry3", "e154", "p15420")
E161D = os.path.join(DATA, "2026-11-03-e161-heat-e2e-aifoundry2")

FROZEN = {
    "docs/reports/data/2026-11-03-q139e-heat-end-to-end/predict_q139e.py": "0dad4370b5274f6bd85ab86c4065ac9bab8c414f68542d6552255b7891526314",
    "docs/reports/data/2026-11-03-q139e-heat-end-to-end/predictions-q139e.json": "60424edb5ade86bc50986b9a8eb3368a4fdf28c10780f662361a518e225ed703",
    "docs/reports/data/2026-11-03-q139e-heat-end-to-end/amendment-a1.json": "1e2b7abf99e126a229a6102aa68af211c792a114578f786f281281b7b1ebeb8a",
    "docs/reports/data/2026-11-02-q138t-heat-model/model-q138t.json": "268b47fd580b330738eb3e1c83ea392f3784aae348a658e7335b734a1168e8fa",
    "docs/reports/data/2026-11-02-q138t-heat-model/heat_q138t.py": "9dbb288f896b7e588fbc155d67f32b1cb7089ffe4ede465c1380d2724d1fb49b",
    "docs/reports/data/2026-11-02-q138t-heat-model/score_e144.py": "0569c49474da4058de4ad14c13d1081fa50ba2e7dd705d4a564835d94c2e1494",
    "docs/reports/data/2026-11-02-q138t-heat-model/fit_q138t.py": "0f21f77cb916bb65c85708b89a89a36e7add3146e098da38dd64b4077e9eb29a",
    "docs/reports/data/2026-11-02-q138t-heat-model/predictions-e144.json": "ae840f84bd36e80f822981913b3d44f314248669f56ff96dc2c2b61ced0a92d0",
    "docs/reports/data/2026-11-02-q137m-model/m6.json": "87c17e086ee36699d7bb96609c02c471b5ba6b7bcdc20ead576d26f89e136e82",
    "docs/reports/data/2026-11-03-q139m-model/m8.json": "8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd",
    "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json": "b7463b6c2c159eb70bd59418f729c4c9144f6eec778126ef660fe781cc724da5",
    "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json": "972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f",
    "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json": "6b9a5e6ee5f3c4761855d8cedc486c546fecc2d855d0e706919c2a21302e3125",
    "docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json": "cc6fbccc4b63fa80575e91abb02c6296a24ac97984fd52a232dbea04a6c6fec8",
    "docs/reports/data/2026-11-04-q140l-a2-session-terms/predict_m9_a2.py": "420b887ea57cfdfec7da6a1f4f3f2017a92da9c9cf86d71cefe8c17ec1fcf284",
    "docs/reports/data/2026-11-04-q140l-a2-session-terms/corrections.json": "4494f2e5125a5941fc7e5a568114742dddaa6172880e8cfde5cb2229d32febdc",
    "tools/claims-v3/e119/make_predictions_e119.py": "8f9b7fe440a632bddbab411a2b054aa87880b64c12b685efd612e211ca8e96e0",
    "docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420/runs.jsonl": "c834afb01305ff5065d60259fc5c6f3e48dfbd50bdcb5f949529d0ae8de1a24e",
    "docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420/marks.jsonl": "066c0fd1f8069b9d902982eb21391b506742340670105867a1af80e11f3919f3",
    "docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420/telemetry.jsonl.gz": "4f1e10cb0b1260cedb27f2a5926f6430c8fe67895c32f4b93f766aea8560f32b",
    "docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/scored.json": "9dc62828bd10d8469a1420ae547f40bbab16d2391bfb8234d206267925b560a8",
    "docs/reports/data/2026-11-03-e153-blind6-aifoundry3/e153.json": "afff8cb2eca522ebdc9e22138850aef9d92bf482d8ebb4a0aae2faa4ef14be38",
    "docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/G1Q/launches.jsonl.gz": "f9737067cb20d5e321472a16d247785efc889d695753b54e816c1c062a002dcc",
    "docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/G2Q/launches.jsonl.gz": "9c9a8dd623c3e534e5d6e58dbd5e86eb5e4bc6f8b9e3bd3dd0c737c7f333b440",
    "docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/results.json": "18184bd3d5ed02b1cdeda017c12ea9a6fa72e50a72b5b46b88cf5a7a97dfb5fe",
    "docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/corrections.txt": "74c650ef35af5ae01f4c22757401d5845c0dff22bc1d412ab1af61bb33a5f24b",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    bad = [p for p, h in FROZEN.items() if sha(os.path.join(REPO, p)) != h]
    if bad:
        sys.exit("Q140(e) REFUSED: frozen inputs changed: " + ", ".join(bad))
    return {p: h[:16] for p, h in FROZEN.items()}


check_frozen()
sys.path.insert(0, Q139E)
sys.path.insert(0, Q138T)
sys.path.insert(0, Q140L)
import predict_q139e as PQ  # noqa: E402  frozen, unchanged (importing it runs no main; it imports heat_q138t)
import score_e144 as SE  # noqa: E402  frozen, unchanged
import fit_q138t as FT  # noqa: E402  frozen, unchanged
import predict_m9_a2 as M9A2  # noqa: E402  frozen, unchanged (Q140(l)'s aifoundry2 part)

hm = PQ.hm
DT = hm.DT
QE = json.load(open(os.path.join(Q139E, "predictions-q139e.json")))
A1 = json.load(open(os.path.join(Q139E, "amendment-a1.json")))
A3F = QE["aifoundry3"]
FZ = {h["hold"]: h for h in A3F["session"]["holds"]}            # Q139(e)'s frozen per-hold bands and critic scales
S_TABLE = dict(A3F["S_table_W"])
ARMS = A3F["power_arms"]
E153S = {it: float(v["S"]["mean"]) for it, v in json.load(open(os.path.join(DATA, "2026-11-03-e153-blind6-aifoundry3", "e153.json")))["items"].items()
         if it in PQ.CANDIDATES}
POOL6 = {"K_S": "fp32.real_smol_softmax_v_causal", "K_Q": "int8.real_qwen_w8a8_v", "K_L": "int8.b_line_zero_ff", "K_O": "fp32.a_onebit_b5_third"}
A2_HOLDS = {"G1Q": "int8.b_line_zero_ff", "G2Q": "fp32.real_smol_softmax_v_causal"}
PEAK_LINE_C = PQ.PEAK_LINE_C      # 67.5 C, H_H's line
ROOMS = (49.5, 50.6, 51.2, 51.5, 52.5, 53.0)
ROOM_NOMINAL = PQ.A3_REST_NOMINAL  # 51.2 C
REST_DIES_A2 = (44.0, 45.0, 46.0, 47.0, 48.0)
CHECK_A3 = (60, 120, 180, 300, 450, 600)
CHECK_LONG = (60, 120, 180, 300, 450, 600, 900, 1200, 1500)
CHECK_A2 = (60, 120, 180, 300, 450, 600, 750)
RK3B_C = 1.0
RK3C_FRAC = 0.015
LARGE_RISE_C = 10.0
SLOW = {"seen": 0.15, "not_seen_hi": 0.05, "overshoot": -0.15}
TAU_S_SCENARIOS = (600.0, 1200.0, 2400.0)


def r3(x, n=3):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), n)


def rms(xs):
    xs = [float(x) for x in xs if x is not None and math.isfinite(x)]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


# ================================================================ R1: the duty convention
def kernel_duty(procs, recs):
    """d = time in every kernel-launch record over the span from the first process's start to the last process's end"""
    span = procs[-1][1] - procs[0][0]
    return sum(b - a for a, b in recs) / span


def a3_records(pass_dir):
    """aifoundry3 (E154's harness): per hold, its process launches (marks.jsonl 'launch' marks of the block), its dispatch records
    (runs.jsonl of the block, the launch = -1 calibration record included), the hold's marks and the kernel duty"""
    marks = [json.loads(x) for x in open(os.path.join(pass_dir, "marks.jsonl")) if x.strip()]
    runs = [json.loads(x) for x in open(os.path.join(pass_dir, "runs.jsonl")) if x.strip()]
    holds = {}
    for m in marks:
        if m.get("kind") == "hold":
            holds[m["name"]] = {"name": m["name"], "item": m["item"], "t0_mark": m["t_start_ms"] / 1e3, "t1_mark": m["t_end_ms"] / 1e3}
    for nm, h in holds.items():
        h["procs"] = sorted((m["t_start_ms"] / 1e3, m["t_end_ms"] / 1e3) for m in marks if m.get("kind") == "launch" and m.get("block") == nm)
        h["recs"] = sorted((r["t_start_ms"] / 1e3, r["t_end_ms"] / 1e3) for r in runs if r.get("block") == nm)
        h["kernel_duty"] = kernel_duty(h["procs"], h["recs"])
        h["b"] = h["procs"][-1][1]
    return marks, holds


def a2_records(step_dir):
    """aifoundry2 (E144b's harness): the HOLD's work processes and their kernel-launch records (launches.jsonl's sparsity entries, the
    launch = -1 calibration entry included), and the kernel duty"""
    p = os.path.join(step_dir, "launches.jsonl.gz")
    op = gzip.open if os.path.exists(p) else open
    p = p if os.path.exists(p) else os.path.join(step_dir, "launches.jsonl")
    L = [json.loads(x) for x in op(p, "rt") if x.strip()]
    work = [x for x in L if x.get("role") == "work" and str(x.get("run", "")).startswith("HOLD")]
    procs = [(x["t_start_ms"] / 1e3, x["t_end_ms"] / 1e3) for x in work]
    recs = [(z["t_start_ms"] / 1e3, z["t_end_ms"] / 1e3) for x in work for z in (x.get("sparsity") or [])]
    return procs, recs, kernel_duty(procs, recs)


# ================================================================ aifoundry2: the composition with the level and the duty (R1, R2)
ZERO_OFF = {600: 0.0, 700: 0.0, 800: 0.0}
M9 = M9A2.M9
REL9 = M9["relation"]
B9 = {int(k): float(v) for k, v in REL9["B_w"].items()}
S9 = {int(k): float(v) for k, v in REL9["s_f"].items()}
CZ9, G9 = REL9["c_zeros_w"], float(REL9["g"])
BETA = float(M9["params"]["beta"])
FALLBACK = dict(M9["fallback_delta_w"])


def level_offsets(item, level, delta=None, D=None):
    """the in-work level offset at 600/700/800 MHz (W) on Q139(e)'s board: 0 for M8; for 'M9a' (Q140(l)'s option (a)):
    [B9(f) + c9 s9(f)] - [B8(f) + c8 s8(f)] + beta x delta_t, c8 = Q139(e)'s c, c9 = M9's c_zeros[t] + g x D, D the same M8 D600 from
    the bits unless given; delta_t the session's zeros offset for the format (M9's fallback when none was read)"""
    if level == "M8":
        return dict(ZERO_OFF)
    t = PQ.P2["tiles"][item]
    typ = t["type"]
    D = float(t["M8"]["D600_a3_footing_w"]) if D is None else float(D)
    c8 = PQ.CZ[typ] + PQ.GSC[typ] * D
    c9 = float(CZ9[typ]) + G9 * D
    dl = float((delta or FALLBACK)[typ])
    return {f: (B9[f] + c9 * S9[f]) - (PQ.B_F[f] + c8 * PQ.S_F[f]) + BETA * dl for f in (600, 700, 800)}


def off_at(f, off):
    if f >= 800:
        return off[800]
    if f >= 700:
        return off[700] + (off[800] - off[700]) * (f - 700) / 100.0
    return off[600] + (off[700] - off[600]) * (f - 600) / 100.0


def board_lv(f, c, T, off):
    """Q139(e)'s board(f, c, T) (M8's burst board moved to die T by 0.442 W/C from 56.0 C) plus the level offset"""
    return PQ.board(f, c, T) + off_at(f, off)


def a2_closed_dl(c, T_rest, P_ref, dur_s, d=1.0, off=None, dt=DT, period_s=1.0):
    """predict_q139e.a2_closed with the level offset and the kernel duty: the chain is driven by L(T) + d (board - L(T)) - P_ref,
    L(T) = P_ref + 0.442 (T - T_rest); the governor (one level a second down while the whole-degree reading is above 65 or the in-work
    board is over W0, up while under 65 and the next level's in-work board stays under W0) sees the in-work board. At d = 1 and no offset
    it is a2_closed. Returns g, T, the duty-averaged board, the in-work board, the clock."""
    off = ZERO_OFF if off is None else off
    n = int(round(dur_s / dt))
    tau, R = np.asarray(PQ.TAU, float), np.asarray(PQ.R2, float)
    a = np.exp(-dt / tau)
    x = np.zeros(len(tau))
    levels = [600, 700, 800]
    ci = 2
    Tk = T_rest
    T, Pa, Pw, F = np.empty(n), np.empty(n), np.empty(n), np.empty(n)
    nxt = 0.0
    for k in range(n):
        if k * dt >= nxt:
            nxt = k * dt + period_s
            rd = math.floor(Tk)
            pb = board_lv(levels[ci], c, Tk, off)
            if rd > 65 or pb > PQ.W0:
                ci = max(0, ci - 1)
            elif rd < 65 and ci < 2 and board_lv(levels[ci + 1], c, Tk, off) <= PQ.W0:
                ci += 1
        pb = board_lv(levels[ci], c, Tk, off)
        if d == 1.0:
            pin = pb - P_ref
        else:
            Lk = PQ.K_A2 * (Tk - T_rest)
            pin = Lk + d * (pb - P_ref - Lk)
        x = a * x + (1 - a) * pin
        Tk = T_rest + float((R * x).sum())
        T[k], Pa[k], Pw[k], F[k] = Tk, P_ref + pin, pb, levels[ci]
    return np.arange(n) * dt, T, Pa, Pw, F


def a2_fixed_800(c, T_rest, P_ref, d=1.0, off=None):
    """the 800 MHz fixed point at duty d (E161 C1's fixed_point_share with the level offset)"""
    off = ZERO_OFF if off is None else off
    Rt = float(np.asarray(PQ.R2).sum())
    T = T_rest
    for _ in range(500):
        L = P_ref + PQ.K_A2 * (T - T_rest)
        T = T_rest + Rt * (L + d * (board_lv(800, c, T, off) - L) - P_ref)
    return T


def a2_trip_clock_dl(c, T_rest, P_ref, d=1.0, off=None, T_trip=None):
    """the trip clock at duty d (E161 C1's trip_clock_share with the level offset): the held board P_t = P_ref + (T_trip - T_rest)/R,
    the in-work board P_w = L_t + (P_t - L_t)/d, the clock where the in-work board meets P_w; at d = 1, no offset, it is a2_trip_clock"""
    off = ZERO_OFF if off is None else off
    T_trip = PQ.TRIP_C if T_trip is None else T_trip
    Rt = float(np.asarray(PQ.R2).sum())
    Pt = P_ref + (T_trip - T_rest) / Rt
    Lt = P_ref + PQ.K_A2 * (T_trip - T_rest)
    Pw = Lt + (Pt - Lt) / d
    if board_lv(600, c, T_trip, off) >= Pw:
        return 600.0, Pt, Pw
    lo, hi = 600.0, 800.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if board_lv(mid, c, T_trip, off) < Pw:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), Pt, Pw


def a2_hold(item, T_rest, P_ref, span_s, d, level, delta=None, D=None):
    """one aifoundry2 hold's frozen prediction from its REST anchor, on R3's windows: the regime, the plateau (the trajectory's mean over
    the 300 s ending at the last process, or the trip rule's 65.9 C), the checkpoints from the first process's start and 'end', the
    clock (the share at >= 790 MHz on the 800 MHz regime, the trip clock at d on the trip regime), the boards, the first step down"""
    c = PQ.c_of(item)
    off = level_offsets(item, level, delta, D)
    T800 = a2_fixed_800(c, T_rest, P_ref, d, off)
    regime = "trip" if T800 > PQ.TRIP_C else "800 MHz"
    g, T, Pa, Pw, F = a2_closed_dl(c, T_rest, P_ref, span_s, d, off)
    m = g >= span_s - 300.0
    plat_sim = float(T[m].mean())
    cps = {}
    for s in CHECK_A2:
        if s + 2.5 <= span_s:
            cps[str(s)] = r3(PQ.at(g, T, s, 5.0) - T_rest)
    ke = (g >= span_s - 5.5) & (g < span_s - 0.5)
    cps["end"] = r3(float(T[ke].mean()) - T_rest)
    out = {"item": item, "level": level, "d": r3(d, 4), "T_rest_C": r3(T_rest), "P_ref_W": r3(P_ref), "span_s": r3(span_s, 2),
           "level_offset_W": {str(f): r3(v, 4) for f, v in off.items()}, "c_W": r3(c, 4), "T800_fixed_point_C": r3(T800),
           "regime": regime, "plateau_C_trajectory_window": r3(plat_sim),
           "plateau_C_predicted": r3(plat_sim if regime == "800 MHz" else PQ.TRIP_C),
           "plateau_rise_C_predicted": r3((plat_sim if regime == "800 MHz" else PQ.TRIP_C) - T_rest),
           "checkpoint_rise_C": cps, "share_ge790MHz_window_sim": r3(float(np.mean(F[m] >= 790.0)), 4),
           "clock_MHz_window_sim": r3(float(F[m].mean()), 1), "board_avg_W_window_sim": r3(float(Pa[m].mean()), 2),
           "board_in_work_W_window_sim": r3(float(Pw[m].mean()), 2), "board_in_work_W_max_sim": r3(float(Pw.max()), 2)}
    kt = np.where(F < 800)[0]
    out["first_step_down_s_sim"] = r3(float(g[kt[0]]), 1) if len(kt) else None
    if regime == "trip":
        f, Pt, Pwk = a2_trip_clock_dl(c, T_rest, P_ref, d, off)
        out.update(clock_MHz_trip_rule=r3(f, 1), board_held_W_trip_rule=r3(Pt, 2), board_in_work_W_trip_rule=r3(Pwk, 2))
    # the closed loop's gain at 800 MHz: d(fixed point)/d(in-work board), +-0.5 W
    gp = a2_fixed_800(c, T_rest, P_ref, d, {f: v + 0.5 for f, v in off.items()})
    gm = a2_fixed_800(c, T_rest, P_ref, d, {f: v - 0.5 for f, v in off.items()})
    out["dT800_dP_in_work_C_per_W"] = r3((gp - gm) / 1.0, 4)
    return out


# ================================================================ aifoundry3: records, the chain, the readings (R1, R3, R5)
def s_table(model):
    """the S each record is on, as score_e154.s_table: E78's (score_e144's S78) for every E78 item, the model's S for the pool-6 items"""
    t = dict(SE.S78)
    for it in POOL6.values():
        t[it] = float(S_TABLE[it]) if model == "M8" else (E153S[it] if model == "E153" else float(ARMS[it][f"{model}_S_W"]))
    return t


def a3_arm_e_on_records(g, recs_items, room, S_of, tau=None, R=None):
    """the frozen closed chain on dispatch records [(t0, t1, item)] from the room (score_e144's s_on_grid + closed_on_grid, unchanged);
    returns T and the board rise over P_ref"""
    S_t = SE.s_on_grid(g, [(a, b, S_of[it]) for (a, b, it) in recs_items])
    T, Pr = SE.closed_on_grid(S_t, PQ.TAU if tau is None else tau, PQ.R3 if R is None else R, room, hm.law_a3)
    return T, Pr, S_t


def a3_read(g, y, t0, b, anchor_end, w, checks):
    """R3's readings on one series: the base over the anchor's last 120 s, the checkpoints (w-s means centred at t0 + s, each ending before
    b) and 'end' (the w s ending 0.5 s before b), the plateau over [b - 300, b), all as rises over the base (score_e144.traj's form)"""
    base = SE.wmean(g, y, anchor_end - hm.ANCHOR_S, anchor_end)
    tr = {}
    for s in checks:
        if t0 + s + w / 2 <= b and s >= w:
            tr[str(s)] = SE.wmean(g, y, t0 + s - w / 2, t0 + s + w / 2) - base
    tr["end"] = SE.wmean(g, y, b - w - 0.5, b - 0.5) - base
    return {"base_C": base, "rise_C_by_s": tr, "plateau_rise_C": SE.wmean(g, y, b - 300.0, b) - base}


def e154_templates():
    """E154's records per item, as offsets from E154's hold start: the processes, the dispatch records, the hold's length, its kernel duty"""
    _, holds = a3_records(E154P)
    tpl = {}
    for nm, h in holds.items():
        t0 = h["t0_mark"]
        procs = [(a - t0, b - t0) for a, b in h["procs"]]
        recs = [(a - t0, b - t0) for a, b in h["recs"]]
        tpl[h["item"]] = {"hold_in_E154": nm, "procs": procs, "recs": recs, "length_s": h["t1_mark"] - t0,
                          "kernel_duty": h["kernel_duty"], "median_launch_period_s": float(np.median(np.diff([p[0] for p in procs])))}
    return tpl


def relay(tp, period_old, period_new, length_s):
    """K_S at another period: launch k (and its records) moved by k x (new - old); launches that end by length_s"""
    procs, recs = [], []
    for k, (a, b) in enumerate(tp["procs"]):
        sh = k * (period_new - period_old)
        if b + sh > length_s:
            break
        procs.append((a + sh, b + sh))
        recs += [(ra + sh, rb + sh) for ra, rb in tp["recs"] if a - 1e-6 <= ra and rb <= b + 1e-6]
    return procs, recs


def tile(tp, block_s, length_s):
    """a long hold: E154's block of launches repeated every block_s; launches that end by length_s"""
    procs, recs = [], []
    j = 0
    while j * block_s < length_s:
        for (a, b) in tp["procs"]:
            a2, b2 = a + j * block_s, b + j * block_s
            if b2 <= length_s:
                procs.append((a2, b2))
                recs += [(ra + j * block_s, rb + j * block_s) for ra, rb in tp["recs"] if a - 1e-6 <= ra and rb <= b + 1e-6]
        j += 1
    return procs, recs


def e166_plan(tpl, ks_period):
    """E166's design as records at exact times from R0's start. ks_period None: K_S is a rest (a room above 53.0 C)"""
    steps = [("rest", "R0", None, 300.0), ("hold", "K_S", POOL6["K_S"], 600.0), ("rest", "R2", None, 210.0),
             ("hold", "K_Q", POOL6["K_Q"], 600.0), ("rest", "R3", None, 210.0), ("hold", "K_L", POOL6["K_L"], 600.0),
             ("rest", "R4", None, 210.0), ("hold", "K_OL", POOL6["K_O"], 1500.0), ("rest", "R5", None, 150.0)]
    t, recs, holds = 0.0, [], []
    for kind, nm, item, length in steps:
        if kind == "rest" or (nm == "K_S" and ks_period is None):
            t += length
            continue
        tp = tpl[item]
        if nm == "K_S":
            procs, rr = relay(tp, 4.37, ks_period, length) if abs(ks_period - 4.37) > 1e-9 else (tp["procs"], tp["recs"])
        elif nm == "K_OL":
            procs, rr = tile(tp, 600.0, length)
        else:
            procs, rr = tp["procs"], tp["recs"]
        procs = [(a + t, b + t) for a, b in procs]
        rr = [(a + t, b + t) for a, b in rr]
        recs += [(a, b, item) for a, b in rr]
        holds.append({"name": nm, "item": item, "t0": procs[0][0], "b": procs[-1][1], "anchor_end": t, "t_end": t + length,
                      "procs": procs, "kernel_duty": kernel_duty(procs, rr), "period": ks_period if nm == "K_S" else None})
        t += length
    return recs, holds, t


def e154_plan(tpl):
    """E154's design (H_M included) as records at exact times from R0's start, from E154's own records (amendment A2's aifoundry3 part)"""
    steps = [("rest", 300.0), ("H_M", 660.0), ("rest", 210.0), ("K_S", 600.0), ("rest", 210.0), ("K_Q", 600.0), ("rest", 210.0),
             ("K_L", 600.0), ("rest", 210.0), ("K_O", 600.0), ("rest", 150.0)]
    item_of = {"H_M": "int8.full", **POOL6}
    t, recs, holds = 0.0, [], []
    for nm, length in steps:
        if nm == "rest":
            t += length
            continue
        tp = tpl[item_of[nm]]
        procs = [(a + t, b + t) for a, b in tp["procs"]]
        rr = [(a + t, b + t) for a, b in tp["recs"]]
        recs += [(a, b, item_of[nm]) for a, b in rr]
        holds.append({"name": nm, "item": item_of[nm], "t0": procs[0][0], "b": procs[-1][1], "anchor_end": t, "t_end": t + length,
                      "procs": procs, "kernel_duty": kernel_duty(procs, rr), "period": 4.37 if nm == "K_S" else None})
        t += length
    return recs, holds, t


def window_10min(h):
    """K_O's replicate window inside K_OL: b = the end of the last process ending at or before 600 s after the first process's start"""
    return max(b for a, b in h["procs"] if b <= h["t0"] + 600.0 + 1e-9)


def read_plan(g, T, h, w, long=False):
    out = {}
    rd = a3_read(g, T, h["t0"], h["b"], h["anchor_end"], w, CHECK_LONG if long else CHECK_A3)
    k = (g >= h["t0"]) & (g < h["b"])
    out["main"] = {"window": [r3(h["b"] - 300.0, 2), r3(h["b"], 2)], "carried_in_C": None, "plateau_rise_C": r3(rd["plateau_rise_C"]),
                   "plateau_C_abs": r3(SE.wmean(g, T, h["b"] - 300.0, h["b"]), 2), "peak_C_abs": r3(float(T[k].max()), 2),
                   "rise_C_by_s": {kk: r3(v) for kk, v in rd["rise_C_by_s"].items()}, "base_C": r3(rd["base_C"])}
    if long:
        b10 = window_10min(h)
        r10 = a3_read(g, T, h["t0"], b10, h["anchor_end"], w, CHECK_A3)
        out["K_O_window"] = {"window": [r3(b10 - 300.0, 2), r3(b10, 2)], "plateau_rise_C": r3(r10["plateau_rise_C"]),
                             "plateau_C_abs": r3(SE.wmean(g, T, b10 - 300.0, b10), 2),
                             "peak_C_abs": r3(float(T[(g >= h["t0"]) & (g < b10)].max()), 2),
                             "rise_C_by_s": {kk: r3(v) for kk, v in r10["rise_C_by_s"].items()}}
    return out


def run_plan(recs, holds, total, room, S_of, tau=None, R=None):
    g = np.arange(int(round(total / DT))) * DT
    T, Pr, S_t = a3_arm_e_on_records(g, recs, room, S_of, tau, R)
    res = {}
    for h in holds:
        w = h["period"] if h["period"] else 5.0
        rr = read_plan(g, T, h, w, long=(h["name"] == "K_OL"))
        rr["main"]["carried_in_C"] = r3(rr["main"]["base_C"] - room)
        rr["kernel_duty_plan"] = r3(h["kernel_duty"], 4)
        rr["period_s"] = h["period"]
        rr["span_s"] = r3(h["b"] - h["t0"], 2)
        res[h["name"]] = rr
    return res, g, T, Pr


def a3_band(recs_fn, room, name, item, sigma, long=False):
    """Q139(e)'s band form on the plan: G = d(plateau)/dS from the session re-run with the hold's S moved by +-0.25 W"""
    vals = []
    for sg in (+1, -1):
        S2 = s_table("M8")
        S2[item] = S2[item] + sg * 0.25
        recs, holds, total = recs_fn()
        res, *_ = run_plan(recs, holds, total, room, S2)
        vals.append(res[name]["main"]["plateau_rise_C"])
    G = (vals[0] - vals[1]) / 0.5
    b1 = math.sqrt(PQ.SIG_CHAIN_A3 ** 2 + (G * sigma) ** 2)
    return {"G_C_per_W": r3(G, 4), "sigma_S_W": sigma, "band_95_C": r3(1.96 * b1), "fail_beyond_C": r3(max(2 * 1.96 * b1, 1.30)),
            "critic_scale_C": r3(math.sqrt(PQ.SIG_CHAIN_A3 ** 2 + (float(np.asarray(PQ.R3).sum()) * sigma) ** 2))}


def kol_crossings(tpl):
    """the long hold's room rule above 53.0 C (K_S a rest there): K_OL's in-launch peak by room, the first planned crossing of the 67.5 C
    line, and the end of the last whole launch before it (where the rule ends K_OL); the room where K_OL stops fitting 25 minutes"""
    out = {}
    for room in (53.1, 53.2, 53.3, 53.4, 53.5, 54.0):
        recs, holds, total = e166_plan(tpl, None)
        g = np.arange(int(round(total / DT))) * DT
        T, Pr, _ = a3_arm_e_on_records(g, recs, room, s_table("M8"))
        h = [x for x in holds if x["name"] == "K_OL"][0]
        k = (g >= h["t0"]) & (g < h["b"])
        pk = float(T[k].max())
        row = {"peak_C_abs": r3(pk, 2), "runs_25_min": bool(pk <= PEAK_LINE_C)}
        if pk > PEAK_LINE_C:
            tc = float(g[k][np.argmax(T[k] > PEAK_LINE_C)])
            ends = [b for a, b in h["procs"] if b <= tc]
            row.update(first_crossing_s_into_K_OL=r3(tc - h["t0"], 1),
                       ends_at_s_into_K_OL=r3((max(ends) - h["t0"]) if ends else 0.0, 1))
        out[f"{room:.1f}"] = row
    return out


# ================================================================ the slow-stage scenarios (R6, reported only)
def arm_a_errors(g, T, Pr, h, w, long=True):
    """what arm A would read if T (with its board rise Pr) were measured: the frozen chain open loop on Pr, anchored over the hold's
    anchor window, read on the hold's windows (score_e144 / fit_q138t's arm (a) form)"""
    pred = hm.states(Pr, PQ.TAU) @ np.asarray(PQ.R3, float)
    a = hm.anchor_value(g, T, pred, h["anchor_end"])
    e = T - (pred + a)
    out = {"window_long": SE.wmean(g, e, h["b"] - 300.0, h["b"])}
    b10 = window_10min(h)
    out["window_K_O"] = SE.wmean(g, e, b10 - 300.0, b10)
    out["G_A"] = out["window_long"] - out["window_K_O"]
    base = SE.wmean(g, T, h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"])
    out["rise_long"] = SE.wmean(g, T, h["b"] - 300.0, h["b"]) - base
    out["rise_K_O"] = SE.wmean(g, T, b10 - 300.0, b10) - base
    out["by_s"] = {str(s): SE.wmean(g, e, h["t0"] + s - w / 2, h["t0"] + s + w / 2) for s in CHECK_LONG if h["t0"] + s + w / 2 <= h["b"]}
    return out


def scenarios(tpl, f_target):
    recs, holds, total = e166_plan(tpl, 4.37)
    hl = [h for h in holds if h["name"] == "K_OL"][0]
    tau0, R0 = list(PQ.TAU), list(np.asarray(PQ.R3, float))
    out = {"f_target": r3(f_target, 4)}
    # R_s = 0: the chain against itself must read zero (a check of the reading)
    res0, g, T0, P0 = run_plan(recs, holds, total, ROOM_NOMINAL, s_table("M8"))
    z = arm_a_errors(g, T0, P0, hl, 5.0)
    out["check_Rs0_G_A_C"] = r3(z["G_A"], 6)
    for ts in TAU_S_SCENARIOS:
        tau_s = tau0 + [ts]

        def frac(Rs):
            gg = np.arange(int(round(total / DT))) * DT
            T, Pr, _ = a3_arm_e_on_records(gg, recs, ROOM_NOMINAL, s_table("M8"), tau_s, R0 + [Rs])
            e = arm_a_errors(gg, T, Pr, hl, 5.0)
            return e["window_K_O"] / e["rise_K_O"], e
        lo, hi = 0.0, 1.5
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if frac(mid)[0] < f_target:
                lo = mid
            else:
                hi = mid
        Rs = 0.5 * (lo + hi)
        fr, e = frac(Rs)
        out[f"tau_s_{int(ts)}"] = {"R_s_C_per_W": r3(Rs, 4), "arm_A_err_K_O_window_C": r3(e["window_K_O"]), "frac_K_O": r3(fr, 4),
                                   "arm_A_err_long_window_C": r3(e["window_long"]), "G_A_C": r3(e["G_A"]),
                                   "arm_A_err_by_s_C": {k: r3(v) for k, v in e["by_s"].items()}}
    # D6 (dated after the registration, before any E166 data; reported only): the same deficit as a gain error, every stage's R
    # scaled by (1 + gamma), no new stage - what G_A a chain that is merely low by E154's fraction would give

    def frac_g(gm):
        gg = np.arange(int(round(total / DT))) * DT
        T, Pr, _ = a3_arm_e_on_records(gg, recs, ROOM_NOMINAL, s_table("M8"), tau0, [x * (1.0 + gm) for x in R0])
        e = arm_a_errors(gg, T, Pr, hl, 5.0)
        return e["window_K_O"] / e["rise_K_O"], e
    lo, hi = 0.0, 0.5
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if frac_g(mid)[0] < f_target:
            lo = mid
        else:
            hi = mid
    gm = 0.5 * (lo + hi)
    fr, e = frac_g(gm)
    out["gain_D6"] = {"gamma": r3(gm, 4), "arm_A_err_K_O_window_C": r3(e["window_K_O"]), "frac_K_O": r3(fr, 4),
                      "arm_A_err_long_window_C": r3(e["window_long"]), "G_A_C": r3(e["G_A"]),
                      "arm_A_err_by_s_C": {k: r3(v) for k, v in e["by_s"].items()}}
    return out


# ================================================================ reproduction checks (R7.1): nothing else runs if one fails
def checks():
    out, ok = {}, True
    # (1) at d = 1 and no offset, a2_closed_dl is Q139(e)'s a2_closed, sample for sample; the fixed point and trip clock likewise
    worst = 0.0
    for item in A2_HOLDS.values():
        c = PQ.c_of(item)
        P_ref, _ = PQ.p_ref_a2(46.0)
        g1, T1, P1, F1 = PQ.a2_closed(c, 46.0, P_ref, 780.0)
        g2, T2, Pa2, Pw2, F2 = a2_closed_dl(c, 46.0, P_ref, 780.0, 1.0, None)
        worst = max(worst, float(np.abs(T1 - T2).max()), float(np.abs(P1 - Pw2).max()), float(np.abs(F1 - F2).max()))
        worst = max(worst, abs(PQ.a2_plateau_800(c, 46.0, P_ref) - a2_fixed_800(c, 46.0, P_ref)),
                    abs(PQ.a2_trip_clock(c, 46.0, P_ref)[0] - a2_trip_clock_dl(c, 46.0, P_ref)[0]))
    out["a2_duty1_equals_a2_closed_worst_abs"] = worst
    ok &= worst < 1e-9
    # (2) Q139(e)'s frozen aifoundry2 table at 46.0 C
    fz = {h["item"]: h for h in QE["aifoundry2"]["holds"]}
    P_ref, _ = PQ.p_ref_a2(46.0)
    d2 = {}
    for nm, item in A2_HOLDS.items():
        c = PQ.c_of(item)
        T800 = a2_fixed_800(c, 46.0, P_ref)
        d2[nm] = {"T800": [r3(T800), fz[item]["T800_fixed_point_C"]]}
        ok &= abs(r3(T800) - fz[item]["T800_fixed_point_C"]) < 6e-4
        if fz[item]["regime"] == "trip":
            f = a2_trip_clock_dl(c, 46.0, P_ref)[0]
            d2[nm]["trip_clock"] = [r3(f, 1), fz[item]["clock_MHz_at_plateau_rule"]]
            ok &= abs(r3(f, 1) - fz[item]["clock_MHz_at_plateau_rule"]) < 0.06
    out["q139e_a2_table_46C"] = d2
    # (3) E161's kernel duty and corrections C1's fixed point and trip clock at it, from E161's own records and anchors
    s = open(os.path.join(E161D, "corrections.txt")).read()
    c1 = json.loads(s[s.find("{"):])["C1"]
    res = json.load(open(os.path.join(E161D, "results.json")))
    KD = "launches.jsonl alone: kernel-launch time over the hold's span (the hold's kernel duty)"
    e161 = {}
    for nm, item in A2_HOLDS.items():
        procs, recs, d = a2_records(os.path.join(E161D, nm))
        E = res["holds"][nm]["E_end_to_end"]
        T_rest, P_ref = E["T_rest_C"], E["P_ref_W"]
        row = {"d_here": r3(d, 6), "d_E161_C1_rounded": c1[nm]["work_share_by_definition"][KD]}
        ok &= abs(d - c1[nm]["work_share_by_definition"][KD]) < 6e-5
        c = PQ.c_of(item)
        if nm == "G1Q":
            fp = a2_fixed_800(c, T_rest, P_ref, d)
            ref = c1[nm]["G1Q_plateau_at_each_share"][KD]["fixed_point_C"]
            row["fixed_point_at_d"] = [r3(fp), ref]
            ok &= abs(fp - ref) < 1e-3
        else:
            f = a2_trip_clock_dl(c, T_rest, P_ref, d)[0]
            ref = c1[nm]["G2Q_clock_at_each_share"][KD]["trip_clock_MHz"]
            row["trip_clock_at_d"] = [r3(f, 3), ref]
            ok &= abs(f - ref) < 0.01
        e161[nm] = row
    out["e161_c1"] = e161
    # (4) Q140(l) C1's level shift (option (a)) for E161 G1Q's tile, at the D Q140(l) used (E153's measured D)
    q = json.load(open(os.path.join(Q140L, "corrections.json")))["C1"]["E161_G1Q"]
    off = level_offsets("int8.b_line_zero_ff", "M9a", None, q["D_w"])
    want = q["relation_M9_minus_M8_at_800_w"] + q["M9_shift_w"]
    out["q140l_c1_level_800"] = [r3(off[800], 6), r3(want, 6)]
    ok &= abs(off[800] - want) < 1e-9
    # (5) E154's registered arm E predictions, on E154's own session through score_e144 (the scorer's path), and on this lane's plan grid
    sess = SE.a3_load([E154P])
    g, T = sess["g"], sess["T"]
    r0 = sess["rests"][0]
    T_rest = SE.wmean(g, T, r0["t1"] - hm.ANCHOR_S, r0["t1"])
    k0 = g >= r0["t0"]
    Sm8 = s_table("M8")
    S_t = SE.s_on_grid(g, [(a, b, Sm8[it]) for (a, b, it) in sess["recs"]])
    pb = np.full(len(g), np.nan)
    pb[k0], _ = SE.closed_on_grid(S_t[k0], PQ.TAU, PQ.R3, T_rest, hm.law_a3)
    sc = json.load(open(os.path.join(E154D, "scored.json")))
    tpl = e154_templates()
    recs, holds, total = e154_plan(tpl)
    rp, gp, Tp, Pp = run_plan(recs, holds, total, T_rest, Sm8)
    rep = {}
    for h in sess["holds"]:
        w = (h["launch_period_s"] or 7.0) if h["share"] < 0.9 else 5.0
        pr = SE.traj(g, pb, h, w)
        want = sc["holds"][h["name"]]["E_predicted_M8"]["plateau_rise_C"]
        # this lane's plan grid, read on the registered window (t1 = the hold's end mark) for the comparison
        hp = [x for x in holds if x["name"] == h["name"]][0]
        rpl = a3_read(gp, Tp, hp["t0"], hp["t_end"], hp["anchor_end"], w, CHECK_A3)
        rep[h["name"]] = {"scorer_path": r3(pr["plateau_rise_C"]), "scored_json": want, "plan_grid_registered_window": r3(rpl["plateau_rise_C"])}
        ok &= abs(pr["plateau_rise_C"] - want) < 6e-4
        ok &= abs(rpl["plateau_rise_C"] - want) < 0.01
    out["e154_arm_e"] = {"room_R0_C": r3(T_rest, 4), "holds": rep}
    out["ok"] = bool(ok)
    return out, (sess, tpl)


# ================================================================ main
def main(selftest=False):
    frozen = check_frozen()
    chk, (sess154, tpl) = checks()
    if selftest or not chk["ok"]:
        print(json.dumps(chk, indent=1))
        if not chk["ok"]:
            sys.exit("Q140(e): a reproduction check failed; nothing else is computed")
        return
    res = {"_note": "Q140(e): the heat replicates' frozen predictions (E166 aifoundry3, E167 aifoundry2); desk only, nothing refitted; "
                    "registered in REGISTRATION.md (11174d20) before this file was written",
           "registration_commit": "11174d20", "frozen_inputs_sha256_16": frozen, "checks": chk}
    # ---------------- R1: the convention's planned duties, from the records
    _, h154 = a3_records(E154P)
    duties = {"E154": {nm: {"item": h["item"], "kernel_duty": r3(h["kernel_duty"], 4), "processes": len(h["procs"]), "records": len(h["recs"]),
                            "t_end_mark_minus_last_process_end_s": r3(h["t1_mark"] - h["b"], 3),
                            "share_E154_scorer": r3(sum(max(0.0, min(b, h["t1_mark"]) - max(a, h["t0_mark"])) for a, b in h["recs"])
                                                    / (h["t1_mark"] - h["t0_mark"]), 4)} for nm, h in h154.items()},
              "E161": {}}
    for nm in A2_HOLDS:
        procs, recs, d = a2_records(os.path.join(E161D, nm))
        duties["E161"][nm] = {"item": A2_HOLDS[nm], "kernel_duty": r3(d, 4), "processes": len(procs), "records": len(recs),
                              "span_s": r3(procs[-1][1] - procs[0][0], 2)}
    res["duty_convention"] = duties
    D161 = {nm: a2_records(os.path.join(E161D, nm))[2] for nm in A2_HOLDS}
    SPAN161 = {nm: (lambda p: p[-1][1] - p[0][0])(a2_records(os.path.join(E161D, nm))[0]) for nm in A2_HOLDS}
    E161RES = json.load(open(os.path.join(E161D, "results.json")))
    # ---------------- R7.2: amendment A2 to Q139(e) - the duty convention alone (M8's level)
    a2a = {"aifoundry3_E154_design": {}, "aifoundry2_E161_holds": {}}
    recs, holds, total = e154_plan(tpl)
    for room in ROOMS:
        rp, *_ = run_plan(recs, holds, total, room, s_table("M8"))
        a2a["aifoundry3_E154_design"][f"{room:.1f}"] = rp
    nom = a2a["aifoundry3_E154_design"][f"{ROOM_NOMINAL:.1f}"]
    a1t = A1.get("C1_E154_plan_on_the_registered_machinery", {}).get("frozen_vs_armE_at_51.2C", {})
    a2a["aifoundry3_against_frozen_at_51.2C"] = {
        nm: {"Q139e_frozen_table_plateau_rise_C": FZ[nm]["plateau_rise_C"], "Q139e_frozen_share": FZ[nm]["share"],
             "A1_armE_on_plan_plateau_rise_C": (a1t.get(nm) or {}).get("armE_plateau_rise_C"),
             "A2_kernel_duty_plateau_rise_C": nom[nm]["main"]["plateau_rise_C"], "A2_kernel_duty": nom[nm]["kernel_duty_plan"],
             "A2_carried_in_C": nom[nm]["main"]["carried_in_C"], "A2_peak_C_abs": nom[nm]["main"]["peak_C_abs"]} for nm in nom}
    for nm, item in A2_HOLDS.items():
        rows = {}
        for Tr in REST_DIES_A2:
            Pr_, _ = PQ.p_ref_a2(Tr)
            rows[f"{Tr:.1f}"] = a2_hold(item, Tr, Pr_, SPAN161[nm], D161[nm], "M8")
        E = E161RES["holds"][nm]["E_end_to_end"]
        rows["E161_anchor"] = a2_hold(item, E["T_rest_C"], E["P_ref_W"], SPAN161[nm], D161[nm], "M8")
        rows["E161_anchor_continuous_Q139e"] = a2_hold(item, E["T_rest_C"], E["P_ref_W"], SPAN161[nm], 1.0, "M8")
        a2a["aifoundry2_E161_holds"][nm] = rows
    res["amendment_A2_duty_convention_alone"] = a2a
    # ---------------- R7.3: E166 (aifoundry3)
    e166 = {"design": "R0 5.0, K_S 10.0, R2 3.5, K_Q 10.0, R3 3.5, K_L 10.0, R4 3.5, K_OL 25.0 (its first 600 s = K_O's window), R5 2.5 min",
            "plan_minutes": None, "by_room": {}, "arms_at_nominal_room": {}, "bands": {}, "room_rules": {}}
    for room in ROOMS + (53.5,):
        per = 4.37 if room <= 51.5 else (4.97 if room <= 53.0 else None)
        recs, holds, total = e166_plan(tpl, per)
        e166["plan_minutes"] = r3(total / 60.0, 2)
        rp, g, T, Pr = run_plan(recs, holds, total, room, s_table("M8"))
        rp["_K_S_period_s"] = per
        e166["by_room"][f"{room:.1f}"] = rp
    recs, holds, total = e166_plan(tpl, 4.37)
    for model in ("M8", "M7", "M6", "E153"):
        rp, *_ = run_plan(recs, holds, total, ROOM_NOMINAL, s_table(model))
        e166["arms_at_nominal_room"][model] = {nm: {"plateau_rise_C": v["main"]["plateau_rise_C"], **({"K_O_window_plateau_rise_C": v["K_O_window"]["plateau_rise_C"]}
                                                                                                      if "K_O_window" in v else {})}
                                               for nm, v in rp.items() if not nm.startswith("_")}
    # bands: the four replicate holds keep Q139(e)'s frozen ones (R4); the long window's by the same form on the plan (R6)
    for nm in ("K_S", "K_Q", "K_L", "K_O"):
        e166["bands"][nm] = {"band_95_C": FZ[nm]["band_95_C"], "fail_beyond_C": FZ[nm]["fail_beyond_C"], "critic_scale_C": FZ[nm]["critic_scale_C"],
                             "source": "predictions-q139e.json aifoundry3.session.holds (frozen, carried)"}
    e166["bands"]["K_OL_long_window"] = a3_band(lambda: e166_plan(tpl, 4.37), ROOM_NOMINAL, "K_OL", POOL6["K_O"], FZ["K_O"]["sigma_S_W"], long=True)
    # the room rules: K_S's period and K_OL's in-launch peak by room
    e166["room_rules"]["K_S"] = {f"{room:.1f}": {"period_s": e166["by_room"][f"{room:.1f}"]["_K_S_period_s"],
                                                 "peak_C_abs": (e166["by_room"][f"{room:.1f}"].get("K_S") or {}).get("main", {}).get("peak_C_abs")}
                                 for room in ROOMS + (53.5,)}
    e166["room_rules"]["K_OL"] = {}
    for room in ROOMS + (53.5,):
        rr = e166["by_room"][f"{room:.1f}"]["K_OL"]["main"]
        e166["room_rules"]["K_OL"][f"{room:.1f}"] = {"peak_C_abs": rr["peak_C_abs"], "runs_25_min": bool(rr["peak_C_abs"] <= PEAK_LINE_C)}
    e166["room_rules"]["K_OL_above_53C"] = kol_crossings(tpl)
    res["E166"] = e166
    # ---------------- R6: the slow-stage scenarios (reported only)
    sc = json.load(open(os.path.join(E154D, "scored.json")))
    fr = {nm: sc["holds"][nm]["A_given_watts"]["plateau_err_C"] / sc["holds"][nm]["measured"]["plateau_rise_C"] for nm in ("H_M", "K_S", "K_O")}
    sce = scenarios(tpl, float(np.mean(list(fr.values()))))
    sce["E154_arm_A_fractions"] = {k: r3(v, 4) for k, v in fr.items()}
    res["E166_slow_stage_scenarios_reported"] = sce
    # ---------------- R7.4: E167 (aifoundry2)
    e167 = {"design": "E161's: SMOKE, stop tests, 15 min rest, G1Q (REST 2 + 13 min), END 2, 15 min rest, G2Q (REST 2 + 13 min), END2 2",
            "plan_d": {nm: r3(D161[nm], 4) for nm in A2_HOLDS}, "plan_span_s": {nm: r3(SPAN161[nm], 2) for nm in A2_HOLDS},
            "fallback_delta_w": FALLBACK, "beta": BETA, "by_rest_die": {}, "at_E161_anchor": {},
            "peak_rule_M8_unchanged_hi95_W": {nm: [h["peak_board_W_hi95"] for h in QE["aifoundry2"]["holds"] if h["item"] == it][0]
                                              for nm, it in A2_HOLDS.items()}}
    for nm, item in A2_HOLDS.items():
        e167["by_rest_die"][nm] = {}
        for Tr in REST_DIES_A2:
            Pr_, _ = PQ.p_ref_a2(Tr)
            e167["by_rest_die"][nm][f"{Tr:.1f}"] = {"primary_M9a_at_d": a2_hold(item, Tr, Pr_, SPAN161[nm], D161[nm], "M9a"),
                                                    "M8_at_d": a2_hold(item, Tr, Pr_, SPAN161[nm], D161[nm], "M8"),
                                                    "M8_continuous": a2_hold(item, Tr, Pr_, SPAN161[nm], 1.0, "M8")}
        E = E161RES["holds"][nm]["E_end_to_end"]
        e167["at_E161_anchor"][nm] = {"primary_M9a_at_d": a2_hold(item, E["T_rest_C"], E["P_ref_W"], SPAN161[nm], D161[nm], "M9a"),
                                      "M8_at_d": a2_hold(item, E["T_rest_C"], E["P_ref_W"], SPAN161[nm], D161[nm], "M8"),
                                      "M8_continuous": a2_hold(item, E["T_rest_C"], E["P_ref_W"], SPAN161[nm], 1.0, "M8"),
                                      "anchor_pm0p5": {f"{dT:+.1f}": a2_hold(item, E["T_rest_C"] + dT, E["P_ref_W"], SPAN161[nm], D161[nm], "M9a")
                                                       ["plateau_rise_C_predicted"] for dT in (-0.5, 0.5)}}
    # the trip boundary: the rest die above which G1Q's primary would trip (bisection on the 800 MHz fixed point)
    lo, hi = 44.0, 56.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        Pr_, _ = PQ.p_ref_a2(mid)
        if a2_fixed_800(PQ.c_of(A2_HOLDS["G1Q"]), mid, Pr_, D161["G1Q"], level_offsets(A2_HOLDS["G1Q"], "M9a")) > PQ.TRIP_C:
            hi = mid
        else:
            lo = mid
    e167["G1Q_trips_above_rest_die_C"] = r3(0.5 * (lo + hi), 2)
    res["E167"] = e167
    res["rules"] = json.load(open(os.path.join(HERE, "registration.json")))["R4_rules"]
    json.dump(res, open(os.path.join(HERE, "predictions-q140e.json"), "w"), indent=1, sort_keys=False)
    summary(res)


def summary(res):
    P = print
    P("Q140(e): the heat replicates' frozen predictions (registered 11174d20; desk only, nothing refitted)")
    P(f"frozen inputs checked: {len(res['frozen_inputs_sha256_16'])}; reproduction checks: {'OK' if res['checks']['ok'] else 'FAIL'}")
    c = res["checks"]
    P(f"  a2_closed at d = 1 equals Q139(e)'s: worst |diff| {c['a2_duty1_equals_a2_closed_worst_abs']:.1e}")
    P(f"  Q139(e)'s 46.0 C table: {json.dumps(c['q139e_a2_table_46C'])}")
    P(f"  E161 C1 at the kernel duty: {json.dumps(c['e161_c1'])}")
    P(f"  Q140(l) C1 level at 800 MHz (here, Q140(l)): {c['q140l_c1_level_800']}")
    P(f"  E154 arm E (scorer path, scored.json, this lane's plan grid at R0's room): {json.dumps(c['e154_arm_e'])}")
    P("")
    P("R1 the duty convention (kernel duty from the launch records):")
    for s_, rows in res["duty_convention"].items():
        for nm, r in rows.items():
            P(f"  {s_} {nm:4s} {r['item']:34s} d {r['kernel_duty']:.4f}" + (f"  (E154 scorer's share {r['share_E154_scorer']:.4f}; window end - last process {r['t_end_mark_minus_last_process_end_s']:.3f} s)" if s_ == "E154" else f"  span {r['span_s']} s"))
    P("")
    P("Amendment A2 to Q139(e): the duty convention alone (M8's level)")
    for nm, r in res["amendment_A2_duty_convention_alone"]["aifoundry3_against_frozen_at_51.2C"].items():
        P(f"  aifoundry3 {nm:4s} plateau rise at 51.2 C: Q139(e) frozen {r['Q139e_frozen_table_plateau_rise_C']} (share {r['Q139e_frozen_share']}), "
          f"A1 on plan {r['A1_armE_on_plan_plateau_rise_C']}, A2 at the kernel duty {r['A2_kernel_duty_plateau_rise_C']} (d {r['A2_kernel_duty']}, tail {r['A2_carried_in_C']}, peak {r['A2_peak_C_abs']})")
    for nm, rows in res["amendment_A2_duty_convention_alone"]["aifoundry2_E161_holds"].items():
        a, b = rows["E161_anchor"], rows["E161_anchor_continuous_Q139e"]
        P(f"  aifoundry2 {nm} at E161's anchor ({a['T_rest_C']} C, {a['P_ref_W']} W): regime {a['regime']}; plateau {b['plateau_C_predicted']} (continuous, window mean; fixed point {b['T800_fixed_point_C']}) "
          f"-> {a['plateau_C_predicted']} C at d {a['d']} (fixed point {a['T800_fixed_point_C']})" + (f"; trip clock {b.get('clock_MHz_trip_rule')} -> {a.get('clock_MHz_trip_rule')} MHz" if a["regime"] == "trip" else ""))
    P("")
    e = res["E166"]
    P(f"E166 (aifoundry3): {e['design']}; {e['plan_minutes']} min of plan")
    for room, rp in e["by_room"].items():
        line = f"  room {room} C (K_S period {rp['_K_S_period_s']}):"
        for nm in ("K_S", "K_Q", "K_L", "K_OL"):
            if nm in rp:
                m = rp[nm]["main"]
                line += f" {nm} rise {m['plateau_rise_C']} (tail {m['carried_in_C']}, peak {m['peak_C_abs']})"
                if nm == "K_OL":
                    line += f" [K_O window {rp[nm]['K_O_window']['plateau_rise_C']}, peak {rp[nm]['K_O_window']['peak_C_abs']}]"
        P(line)
    for room in ("51.2", "53.0"):
        k = e["by_room"][room]["K_OL"]
        P(f"  K_OL's frozen trajectory at {room} C (rise over its anchor, C): {json.dumps(k['main']['rise_C_by_s'])}; plateau {k['main']['plateau_rise_C']} "
          f"over {k['main']['window']} s; K_O window {json.dumps(k['K_O_window']['rise_C_by_s'])}, plateau {k['K_O_window']['plateau_rise_C']}")
    P(f"  K_OL above 53.0 C (K_S a rest): {json.dumps(e['room_rules']['K_OL_above_53C'])}")
    P(f"  arms at 51.2 C: {json.dumps(e['arms_at_nominal_room'])}")
    P(f"  bands: {json.dumps(e['bands'])}")
    P(f"  room rules: {json.dumps(e['room_rules'])}")
    s = res["E166_slow_stage_scenarios_reported"]
    P(f"  slow-stage scenarios (reported only): {json.dumps(s)}")
    P("")
    e = res["E167"]
    P(f"E167 (aifoundry2): {e['design']}; plan d {e['plan_d']}, spans {e['plan_span_s']} s; M8 peak rule hi95 {e['peak_rule_M8_unchanged_hi95_W']} W")
    for nm, arms in e["at_E161_anchor"].items():
        for arm in ("primary_M9a_at_d", "M8_at_d", "M8_continuous"):
            a = arms[arm]
            P(f"  {nm} {arm:17s} at E161's anchor: regime {a['regime']}, plateau {a['plateau_C_predicted']} C (rise {a['plateau_rise_C_predicted']}), "
              f"T800 {a['T800_fixed_point_C']}, checkpoints {a['checkpoint_rise_C']}, clock {a.get('clock_MHz_trip_rule', a['clock_MHz_window_sim'])} MHz, "
              f"board avg {a['board_avg_W_window_sim']} / in work {a['board_in_work_W_window_sim']} W, offset {a['level_offset_W']['800']} W")
        P(f"  {nm} primary over the anchor's +-0.5 C: rises {arms['anchor_pm0p5']}")
    P(f"  G1Q's primary trips above a rest die of {e['G1Q_trips_above_rest_die_C']} C")
    for nm, rows in e["by_rest_die"].items():
        P(f"  {nm} primary by rest die: " + "; ".join(f"{k} C: {v['primary_M9a_at_d']['plateau_C_predicted']} C"
                                                     + (f" @ {v['primary_M9a_at_d'].get('clock_MHz_trip_rule')} MHz" if v['primary_M9a_at_d']['regime'] == 'trip' else "")
                                                     for k, v in rows.items()))


if __name__ == "__main__":
    main(selftest="--selftest" in sys.argv[1:])
