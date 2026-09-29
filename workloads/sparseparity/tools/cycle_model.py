#!/usr/bin/env python3
"""cycle_model.py: where each minion's time goes in the SPP_TENSOR kernel, fitted to the card's per-hart records.

Host code only; opens no card. It reads the JSON line and the per-hart records (`--records-out`: one 64 B SppRecord
per hart) of every tensor run that card_run.sh and the M3 manual runs saved on 29 September 2026, rebuilds each run's
work list exactly as the host built it (host/spp_common.h makePlan and sliceRange, host/main.cpp probePlan), checks
it against the records (hart 0's `work` = the plan's ops and hart 1's `count` = its row tiles, on every minion of
every run), and fits a cycle model of the two harts of a minion.

THE MODEL (cycles at 600 MHz; "solo" = the cost when the other hart of the minion is idle).

  Hart 0, row tile with nout column tiles, S slices, ops = nout * S:
      instr  = H_TILE[path] + nout * E_OUT * epi    instruction-bound: tile set-up, poll, release, epilogues
      tensor = nout * (S * C_OP * (1 + KAPPA_T * U) + D_OUT)  [+ S * A_RES, the resident A load]
    C_OP, D_OUT per A path (str: streamed, S > 3; res: resident in the L1 scratchpad, S <= 3). epi = 0 with
    --timing-only. U = the shire's L2 demand over 128 B per cycle (the measured own-shire rate): tensor bytes
    (2 KB per streamed op, 1 KB per resident op + the A loads) and hart 1's staged rows (S KB per row tile).
  Hart 1, one row tile (16 rows x S slices, k-1 factors, X and y bit-packed feature-major in DRAM):
      gen    = (G_TILE + S * (G_SLICE + G_K * (k-1))) * (1 + KAPPA_G * U)   [+ S * G_DRAM with DRAM staging]
  The two harts share one issue slot (et-soc1-notes.md: one RISC-V instruction per cycle for both harts): while both
  work, hart 0 runs at 1 / (1 + s0) and hart 1 at 1 / (1 + s1), with
      s0 = (SIG_I * instr + SIG_T * tensor) / (instr + tensor),   s1 = (SIG_GI * instr + SIG_GT * tensor) / (...)
  The pipeline (kernel/sparseparity.c): hart 1 starts row tile j once it finished j-1 and hart 0 released
  j - nbuf (+ SYNC to see it); hart 0 starts tile q once it finished q-1 and tile q is staged, and its wait for it
  is at least POLL (one poll of the L2 line) and ends SYNC after the rows are published; hart 0 releases a tile after
  its A load (resident) or its last op (streamed). Hart 1 starts at the kernel's entry, hart 0 after its copy-in.

THE FIT. `fit` simulates the two harts event by event for a sample of minions of every run (runs of identical row
tiles are skipped over once the pipeline is periodic) and fits the 19 constants by least squares on each sampled
minion's cycles and wait (both relative to its cycles; every run weighted alike, M3's two runs twice). Excluded:
DRAM staging (a different A path), the negative controls and --nowait-a. FITTED below is the result of
`cycle_model.py fit` on 29 September's data; `validate` prints every run's measured and modelled max, median and
wait, including the runs the fit did not use.

  cycle_model.py check                     rebuild every run's work list and check it against the records
  cycle_model.py fit [--out model.json]    refit the constants (about a minute; one thread)
  cycle_model.py validate                  every run: measured against modelled (all minions)
  cycle_model.py explain                   M3 L1 and L2: the busiest and the median minion, term by term
  cycle_model.py whatif                    M3 L1 and L2 under the proposed kernel changes, re-planned with the model
  cycle_model.py table --n N --k K --m M [--nbuf B] [--variant m1|m4] [--abuf 3] [--out F.json]
                                           the fitted pipeline's cycles per row tile by column tiles (1..nJ): the
                                           cost the M4 planners balance (spp_common.h pipeSteady prints the same)
  cycle_model.py host --n N --k K --m M [--shires S] [--per-shire P] [--slice I/N] [--variant m1|m4] [--gen ..]
                      [--epi ..] [--abuf 3] [--cost m1|fit] [--slice-cost m1|fit] [--timing-only]
                                           what sparseparity_host computes for a launch with its built-in plan
                                           (model_s: every minion simulated; --dry prints the same)
  cycle_model.py m4                        the predicted time of every card_run.sh m4 step

M4's kernel variants (variant_constants; host/spp_common.h pipeVariant is the same): incremental generation halves
G_TILE and replaces the k-1 factor term with G_K / 8 per slice; the epilogue in pieces (HIDDEN) shows only
max(0, E_OUT - (S-1) C_OP) per output tile except each row tile's last; 3 A buffers set the streamed op to 300.
These are the analysis' predictions, not measurements.

WHAT IT SAYS (29 September; `explain`, `whatif`). M3's L1 (S = 7, 2 buffers) and L2 (S = 29, 1 buffer) at 1,024
minions are 5.67x and 5.40x off 270 cycles per op, balanced = imbalance 1.52 / 1.48 x overhead 2.65 / 2.61 x op
cost 1.40. The mean minion spends per op: tensor 378; epilogue 229 / 55; issue-slot sharing with hart 1 200 / 0;
waiting for rows 128 / 534; row-tile overhead 53 / 13. Hart 1 needs 2,081 + S (2,108 + 570 (k-1)) cycles per row
tile, 4.8x the planner's 800 per slice, and the planner undercosts a one-column-tile row tile 6.3-6.7x against a
32-column one 1.1-1.3x, so the busiest minion gets 2,703 row tiles (1,940 of one column tile) where the median gets
1,176. Predicted (whatif): the fitted planner alone 1.53x / 1.48x; with incremental generation and the epilogue hidden
behind the next tile's ops 82 ms / 399 ms, and with 2 buffers at L2 301 ms, where the shire's L2 (2 KB per streamed op
at 128 B per cycle: 72 ms / 300 ms) becomes the bound.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import struct
import sys
from pathlib import Path

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data/2026-09-29-aifoundry3-card/runs"
F_HZ = 600e6
BW_SHIRE = 128.0  # B per shire-cycle, own-shire L2 / scratchpad (et-soc1-notes.md, E37)
SKIP = True  # skip over periodic stretches (False: simulate every tile; for testing)
REC = struct.Struct("<qQQQiIQQII")  # SppRecord: sum_c sum_c2 count best_rank best_c status cycles wait work copy

# The constants as `cycle_model.py fit` fitted them to 29 September's records (33 runs, 146 sampled minions, rms
# residual 1.8% of a minion's cycles; `validate` shows every run). INITIAL is the fit's starting point. Held out: fitted
# without M3 and M2's full L1, it predicts M3's busiest minion +5.0% (L1) / +7.5% (L2) and the median within 0.8%;
# that refit splits generation as G_SLICE 2,754 + G_K 351 per factor (here 2,108 + 570): the k-1 term is the least
# certain constant. The resident path (C0, C1: S <= 3) fits only to -17%..+18%; DRAM staging is not modelled.
FITTED = dict(H_TILE=3139, H_TILE_res=3097, C_OP_str=378.2, D_OUT_str=56.99, C_OP_res=256,
              D_OUT_res=1.871e-08, A_RES=2.429, E_OUT=1606, KAPPA_T=0.02297, G_TILE=2081,
              G_SLICE=2108, G_K=570.3, KAPPA_G=0.2356, SIG_I=0.8657, SIG_T=0.1291,
              SIG_GI=0.7577, SIG_GT=0.3517, SYNC=1460, POLL=17.02)
INITIAL = dict(H_TILE=3000.0, H_TILE_res=3000.0, C_OP_str=380.0, D_OUT_str=300.0, C_OP_res=300.0, D_OUT_res=300.0, A_RES=400.0,
               E_OUT=1700.0, KAPPA_T=0.12, G_TILE=6000.0, G_SLICE=2000.0, G_K=750.0, KAPPA_G=0.2, SIG_I=0.5,
               SIG_T=0.1, SIG_GI=0.3, SIG_GT=0.3, SYNC=200.0, POLL=150.0, G_DRAM=2000.0)
FIT_NAMES = ["H_TILE", "H_TILE_res", "C_OP_str", "D_OUT_str", "C_OP_res", "D_OUT_res", "A_RES", "E_OUT", "KAPPA_T", "G_TILE",
             "G_SLICE", "G_K", "KAPPA_G", "SIG_I", "SIG_T", "SIG_GI", "SIG_GT", "SYNC", "POLL"]


def constants() -> dict:
    P = dict(INITIAL)
    P.update(FITTED)
    return P


def variant_constants(gen_inc: bool = True, epi_hide: bool = True, abuf3: bool = False, P: dict | None = None) -> dict:
    """The constants of a kernel variant (host/spp_common.h pipeVariant, line for line): FITTED for M1's kernel;
    M4's changes as the analysis predicts them (not yet measured). Incremental generation: the per-tile set-up
    halves and the k-1 dependent factor loads per row become one 16-word read per slice (G_K / 8 per slice, no k
    term). The epilogue in pieces (HIDDEN): of each output tile's epilogue only max(0, E_OUT - (S-1) C_OP) shows,
    except the row tile's last, which shows whole. 3 A buffers: the streamed op 378 -> 300 cycles."""
    Q = dict(P or constants())
    if gen_inc:
        Q["G_SLICE"] = Q["G_SLICE"] + Q["G_K"] / 8.0
        Q["G_K"] = 0.0
        Q["G_TILE"] = Q["G_TILE"] * 0.5
    Q["HIDDEN"] = 1 if (epi_hide or abuf3) else 0
    if abuf3:
        Q["C_OP_str"] = 300.0
    return Q


# ---------------------------------------------------------------- geometry (host/spp_common.h Geometry)
def binom(a: int, b: int) -> int:
    return math.comb(a, b) if 0 <= b <= a else 0


class Geom:
    def __init__(self, n: int, k: int, m: int):
        self.n, self.k, self.m = n, k, m
        self.S = (m + 63) // 64
        self.nJ = (n + 15) // 16
        self.nrows = binom(n - 1, k - 1)
        self.ntiles = (self.nrows + 15) // 16
        rs = [self.ntiles] * (self.nJ + 2)
        for J in range(self.nJ + 1):
            if J == 0:
                rs[J] = 0
            elif k == 1:
                rs[J] = self.ntiles
            else:
                rs[J] = min(self.ntiles, (binom(16 * J - 1, k - 1) + 15) // 16)
        rs[self.nJ + 1] = self.ntiles
        self.runStart = rs
        self.workTiles = rs[self.nJ]

    def rle(self, t0: int, t1: int) -> list:
        """[(nout, count), ...] of the row tiles [t0, t1), in order"""
        out = []
        for J in range(self.nJ):
            a, b = max(self.runStart[J], t0), min(self.runStart[J + 1], t1)
            if b > a:
                out.append((self.nJ - J, b - a))
        return out


# ---------------------------------------------------------------- the host's plans (spp_common.h, main.cpp)
def host_tile_cycles(nJ: int, J: int, S: int) -> float:
    """spp_common.h tileCyclesWith with the default CostModel (what the M1-M3 runs were planned with)."""
    nout = float(nJ - J)
    ops = nout * S
    res = S <= 3
    hart0 = ops * (270.0 if res else 280.35) + nout * 450.0 + (S * 1024.0 / 4.0 if res else 0.0)
    by = ops * 1024.0 + (S * 1024.0 if res else ops * 1024.0) + S * 1024.0
    return max(hart0, S * 800.0, by / 4.0)


def cut_blocks(G: Geom, nblocks: int, t0: int, t1: int, cost=None) -> list:
    """cutBlocks: [t0, t1) in nblocks contiguous blocks of equal modelled cost, positional (an empty block keeps its
    place); cost(J): modelled cycles of a row tile with J0 = J (default: the host's model)."""
    cost = cost or (lambda J: host_tile_cycles(G.nJ, J, G.S))
    total = 0.0
    for J in range(G.nJ + 1):
        a, b = max(G.runStart[J], t0), min(G.runStart[J + 1], t1)
        if b > a:
            total += (b - a) * cost(J)
    blocks, cur0, acc, made = [], t0, 0.0, 0
    for J in range(G.nJ + 1):
        if made + 1 >= nblocks:
            break
        a, b = max(G.runStart[J], t0), min(G.runStart[J + 1], t1)
        if b <= a:
            continue
        c = cost(J)
        t = a
        while t < b and made + 1 < nblocks:
            target = total * (made + 1) / nblocks
            need = (target - acc) / c
            take = 0 if need <= 0 else int(math.ceil(need - 1e-9))
            if take > b - t:
                acc += (b - t) * c
                t = b
                break
            t += take
            acc += take * c
            blocks.append((cur0, t - cur0))
            cur0 = t
            made += 1
    blocks.append((cur0, t1 - cur0))
    while len(blocks) < nblocks:
        blocks.append((t1, 0))
    return blocks


def make_plan(G: Geom, shires: list, per_shire: int, rounds: int, t0: int, t1: int, cost=None) -> dict:
    """makePlan -> {slot: [(tile0, ntiles), ...]}; cost(J): modelled cycles of a row tile with J0 = J (default:
    the host's model)."""
    nblocks = len(shires) * per_shire * max(1, rounds)
    blocks = cut_blocks(G, nblocks, t0, t1, cost)
    slots = {}
    ns = len(shires)
    for bi, (tb, nt) in enumerate(blocks):
        if nt:
            slots.setdefault(shires[bi % ns] * 32 + (bi // ns) % per_shire, []).append((tb, nt))
    return slots


def slice_range(G: Geom, i: int, n: int, cost=None) -> tuple:
    """sliceRange: slice i of n is equal-cost block i, by position."""
    if n <= 1:
        return 0, G.workTiles
    tb, nt = cut_blocks(G, n, 0, G.workTiles, cost)[i]
    return tb, tb + nt


def probe_plan(G: Geom, shires: list, per_shire: int, N: int) -> dict:
    act = [s * 32 + mi for s in shires for mi in range(per_shire)]
    base = G.workTiles - N * len(act)
    return {g: [(base + i * N, N)] for i, g in enumerate(act)}


def plan_rle(G: Geom, blocks: list) -> list:
    out = []
    for tb, nt in blocks:
        for nout, c in G.rle(tb, tb + nt):
            if out and out[-1][0] == nout:
                out[-1] = (nout, out[-1][1] + c)
            else:
                out.append((nout, c))
    return out


# ---------------------------------------------------------------- runs
def shire_bytes(rle: list, S: int, res: bool) -> float:
    T = sum(c for _, c in rle)
    ops = sum(n * c for n, c in rle) * S
    return ops * 1024.0 + T * S * 2048.0 if res else ops * 2048.0 + T * S * 1024.0


class Run:
    """One launch: its parameters, its rebuilt work list and its per-minion records."""

    def __init__(self, name: str, j: dict, rec: bytes, group: str):
        self.name, self.group, self.j = name, group, j
        I, P = j["instance"], j["plan"]
        self.n, self.k, self.m = I["n"], I["k"], I["m"]
        self.G = Geom(self.n, self.k, self.m)
        self.S, self.k1 = self.G.S, self.k - 1
        self.res = self.S <= 3
        self.path = "res" if self.res else "str"
        self.epi = 0 if j["flags"]["timing_only"] else 1
        self.nowait = bool(j["flags"]["nowait_a"])
        self.stage, self.nbuf = P["stage"], int(P["nbuf"])
        self.per_shire = int(P["per_shire"])
        mask = int(P["shires"], 16)
        self.shires = [s for s in range(32) if (mask >> s) & 1]
        self.rounds = int(P["rounds"])
        self.perturb = P.get("perturb", "")
        # M4's host records its kernel and plan cost in "m4" (absent before M4: M1's kernel, M1's cost)
        m4 = j.get("m4") or {}
        self.gen_inc, self.epi_hide = m4.get("gen") == "inc", m4.get("epi") == "hide"
        self.abuf3 = int(m4.get("abuf", 2)) == 3
        self.m4kernel = self.gen_inc or self.epi_hide or self.abuf3
        self.nostore = bool(m4.get("gen_probe"))
        self.pipe_set = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in m4.get("pipe_set", "").split(",") if kv}
        src = P["source"]
        si, sn = (int(x) for x in P["slice"].split("/"))
        if src.startswith("probe narrow:"):
            self.plan = probe_plan(self.G, self.shires, self.per_shire, int(src.split(":")[1]))
        elif src == "built-in":
            fit = None
            if "fit" in (m4.get("cost"), m4.get("slice_cost")):  # the host's pipeTileCost, at the plan's U
                Q = variant_constants(self.gen_inc, self.epi_hide, self.abuf3, {**constants(), **self.pipe_set})
                fit = pipe_table(self.G, Q, self.nbuf, self.stage == "dram", 0.58 * self.per_shire / 32.0, self.epi)
            t0, t1 = slice_range(self.G, si, sn, (lambda J: fit[J]) if m4.get("slice_cost") == "fit" else None)
            assert [t0, t1] == P["tiles"], (name, t0, t1, P["tiles"])
            self.plan = make_plan(self.G, self.shires, self.per_shire, self.rounds, t0, t1,
                                  cost=(lambda J: fit[J]) if m4.get("cost") == "fit" else None)
        else:
            raise ValueError(f"{name}: plan source {src}")
        self.minions = []
        for g in sorted(self.plan):
            h0 = REC.unpack_from(rec, 64 * (2 * g))
            h1 = REC.unpack_from(rec, 64 * (2 * g + 1))
            rle = plan_rle(self.G, self.plan[g])
            T = sum(c for _, c in rle)
            O = sum(n * c for n, c in rle)
            self.minions.append(dict(slot=g, rle=rle, T=T, O=O, ops=O * self.S, cycles=h0[6], wait=h0[7],
                                     work=h0[8], copy=h0[9], gen_tiles=h1[2], gen_polls=h1[7]))
        # the shire's L2 demand over 128 B per cycle, while its minions run (measured durations)
        us = []
        for s in self.shires:
            ms = [m for m in self.minions if m["slot"] // 32 == s]
            if ms:
                by = sum(shire_bytes(m["rle"], self.S, self.res) for m in ms)
                us.append(by / (np.median([m["cycles"] for m in ms]) * BW_SHIRE))
        self.U = float(np.mean(us)) if us else 0.0

    def check(self) -> list:
        return [(self.name, mn["slot"]) for mn in self.minions if not self.perturb and
                (mn["work"] != mn["ops"] or mn["gen_tiles"] != mn["T"])]


def last_json(path: str):
    try:
        lines = [ln for ln in Path(path).read_text(errors="replace").splitlines() if ln.startswith("{")]
        return json.loads(lines[-1]) if lines else None
    except (OSError, json.JSONDecodeError):
        return None


def load_runs(data: Path = DATA, include=None) -> list:
    runs = []
    for d in sorted(glob.glob(str(data / "*"))):
        if d.endswith("-dry"):
            continue
        group = Path(d).name
        for rp in sorted(glob.glob(d + "/*.rec")):
            stem = rp[:-4]
            name = ("m3-" if "m3-manual" in group else "") + Path(stem).name
            j = None
            for cand in (stem + ".json", stem + ".log"):
                jj = last_json(cand)
                if jj and "plan" in jj:
                    j = jj
                    break
            if j is None or j.get("mode") != "tensor" or j.get("device") != "silicon":
                continue
            if include and not include(name):
                continue
            runs.append(Run(name, j, Path(rp).read_bytes(), group))
    return runs


# ---------------------------------------------------------------- the two harts of one minion
def tile_terms(nout: int, S: int, res: bool, epi: int, U: float, P: dict) -> dict:
    path = "res" if res else "str"
    cop = P["C_OP_" + path] * (1.0 + P["KAPPA_T"] * U)
    h_tile = P["H_TILE_res" if res else "H_TILE"]
    instr_full = h_tile + nout * P["E_OUT"] * epi
    instr = instr_full
    epi_shown = nout * P["E_OUT"] * epi
    if P.get("HIDDEN") and epi:  # the epilogue in pieces (variant_constants)
        epi_shown = P["E_OUT"] + (nout - 1) * max(0.0, P["E_OUT"] - (S - 1) * P["C_OP_" + path])
        instr = h_tile + epi_shown
    tens_ops = nout * S * cop
    tens_drain = nout * P["D_OUT_" + path]
    a_res = S * P["A_RES"] if res else 0.0
    tens = tens_ops + tens_drain + a_res
    tot = instr + tens
    s1 = (P["SIG_GI"] * instr + P["SIG_GT"] * tens) / tot
    if P.get("HIDDEN") and epi:  # the hidden pieces still take issue slots from hart 1
        s1 = min(P["SIG_GI"], (P["SIG_GI"] * instr_full + P["SIG_GT"] * tens) / tot)
    return dict(instr=instr, tens=tens, ops=tens_ops, drain=tens_drain, a_res=a_res, epi=epi_shown,
                p1=a_res, p2=tot - a_res, s0=(P["SIG_I"] * instr + P["SIG_T"] * tens) / tot, s1=s1)


def gen_cycles(S: int, k1: int, stage: str, U: float, P: dict) -> float:
    g = P["G_TILE"] + S * (P["G_SLICE"] + P["G_K"] * k1)
    if stage == "dram":
        g += S * P.get("G_DRAM", 0.0)
    return g * (1.0 + P["KAPPA_G"] * U)


def sim_minion(rle: list, S: int, k1: int, res: bool, nbuf: int, epi: int, stage: str, U: float, copy: float,
               P: dict, gen_override: float | None = None, tile_override=None) -> dict:
    """Event simulation of one minion's two harts over its row tiles (rle: [(nout, count), ...]). Stretches of
    identical tiles are skipped over once the pipeline repeats itself exactly. -> cycles, wait and the solo terms."""
    T = sum(c for _, c in rle)
    if T == 0:
        return dict(cycles=copy, wait=0.0, T=0, instr=0.0, tens=0.0, epi=0.0, ops=0.0, busy=0.0)
    ends = np.cumsum([c for _, c in rle]).tolist()
    nouts = [n for n, _ in rle]
    terms = {n: (tile_override(n) if tile_override else tile_terms(n, S, res, epi, U, P)) for n in set(nouts)}
    g = gen_override if gen_override is not None else gen_cycles(S, k1, stage, U, P)
    SYNC, POLL = P["SYNC"], P["POLL"]
    sig_copy = P["SIG_GI"]
    t = 0.0
    g_end, rel = {}, {}
    # hart 1
    j, ph1, rem1, wake1 = 0, "run", g, None
    s1_cur = sig_copy
    # hart 0
    q, ph0, rem0, wake0, wstart = 0, "copy", float(copy), None, 0.0
    tt = None
    wait = 0.0
    cur_stretch = 0
    sig_prev = None
    acc = dict(instr=0.0, tens=0.0, epi=0.0, ops=0.0)
    guard = 0
    while True:
        guard += 1
        if guard > 50_000_000:
            raise RuntimeError("simulation did not finish")
        run0 = ph0 in ("copy", "p1", "p2")
        run1 = ph1 == "run"
        both = run0 and run1
        if ph0 == "copy":
            r0, r1 = 1.0, (1.0 / (1.0 + sig_copy) if both else 1.0)
        else:
            r0 = 1.0 / (1.0 + tt["s0"]) if both else 1.0
            r1 = 1.0 / (1.0 + tt["s1"]) if both else 1.0
        cands = []
        f0 = t + rem0 / r0 if run0 else None  # when each run ends
        f1 = t + rem1 / r1 if run1 else None
        if run0:
            cands.append(f0)
        elif ph0 == "wait" and wake0 is not None:
            cands.append(wake0)
        if run1:
            cands.append(f1)
        elif ph1 == "wait" and wake1 is not None:
            cands.append(wake1)
        if not cands:
            break
        tn = max(min(cands), t)
        dt = tn - t
        if run0:
            rem0 -= dt * r0
        if run1:
            rem1 -= dt * r1
        t = tn
        eps = 1e-6
        # a run ends when its end time is reached, not only when rem falls under eps (past ~1e10 cycles a double's
        # step exceeds eps and the loop would stall: spp_common.h pipeSimMinion)
        end0 = run0 and (rem0 <= eps or f0 <= tn)
        end1 = run1 and (rem1 <= eps or f1 <= tn)
        # ---- hart 1
        if end1:
            g_end[j] = t
            if ph0 == "wait" and q == j:
                wake0 = max(wstart + POLL, t + SYNC)
            j += 1
            if j >= T:
                ph1, wake1 = "done", None
            elif j - nbuf < 0:
                ph1, rem1 = "run", g
            elif (j - nbuf) in rel:
                w = rel[j - nbuf] + SYNC
                if w <= t:
                    ph1, rem1 = "run", g
                else:
                    ph1, wake1 = "wait", w
            else:
                ph1, wake1 = "wait", None
        elif ph1 == "wait" and wake1 is not None and t >= wake1 - eps:
            ph1, rem1, wake1 = "run", g, None
        # ---- hart 0
        if end0:
            if ph0 == "copy" or ph0 == "p2":
                if ph0 == "p2":
                    if not res:
                        rel[q] = t
                        if ph1 == "wait" and j - nbuf == q:
                            wake1 = t + SYNC
                    q += 1
                if q >= T:
                    ph0 = "done"
                else:
                    ph0, wstart = "wait", t
                    wake0 = max(t + POLL, g_end[q] + SYNC) if q in g_end else None
            elif ph0 == "p1":
                rel[q] = t
                if ph1 == "wait" and j - nbuf == q:
                    wake1 = t + SYNC
                ph0, rem0 = "p2", tt["p2"]
        elif ph0 == "wait" and wake0 is not None and t >= wake0 - eps:
            wait += t - wstart
            while q >= ends[cur_stretch]:
                cur_stretch += 1
            tt = terms[nouts[cur_stretch]]
            for kk in acc:
                acc[kk] += tt[kk]
            wake0 = None
            if res and tt["p1"] > 0:
                ph0, rem0 = "p1", tt["p1"]
            else:
                ph0, rem0 = "p2", tt["p2"]
                if res:  # nothing before the release
                    rel[q] = t
                    if ph1 == "wait" and j - nbuf == q:
                        wake1 = t + SYNC
            # periodic skip: the state relative to t at this tile start, against the previous tile start
            left = ends[cur_stretch] - q
            sig = (ph1, round(rem1, 3) if ph1 == "run" else None, j - q,
                   None if wake1 is None else round(wake1 - t, 3),
                   tuple(round(g_end[kk] - t, 3) for kk in range(q, j)),
                   tuple(round(rel[kk] - t, 3) for kk in range(max(0, j - nbuf), q) if kk in rel))
            if SKIP and sig_prev is not None and sig_prev[0] == cur_stretch and sig_prev[1] == sig and left > nbuf + 3:
                dT, dW = t - sig_prev[2], wait - sig_prev[3]
                N = left - (nbuf + 3)
                if N > 0 and dT > 0:
                    sh = N * dT
                    t += sh
                    wait += N * dW
                    for kk in acc:
                        acc[kk] += N * tt[kk]
                    g_end = {kk + N: v + sh for kk, v in g_end.items() if kk >= q}
                    rel = {kk + N: v + sh for kk, v in rel.items() if kk >= j - nbuf - 1}
                    q += N
                    j += N
                    if wake1 is not None:
                        wake1 += sh
                    wstart += sh
                    sig_prev = None
                    continue
            sig_prev = (cur_stretch, sig, t, wait)
    if q < T:  # the model stopped early: it would understate the guarded time (spp_common.h pipeSimMinion)
        raise RuntimeError(f"sim_minion: the model stopped at row tile {q} of {T}")
    return dict(cycles=t, wait=wait, T=T, busy=t - wait - copy, **acc)


def sim_run(r: Run, P: dict, minions=None, U: float | None = None, copy: float | None = None) -> list:
    if r.m4kernel:  # M4's kernel: the fitted constants changed as variant_constants predicts
        P = variant_constants(r.gen_inc, r.epi_hide, r.abuf3, P)
    out = []
    for mn in (minions if minions is not None else r.minions):
        o = sim_minion(mn["rle"], r.S, r.k1, r.res, r.nbuf, r.epi, r.stage, r.U if U is None else U,
                       mn["copy"] if copy is None else copy, P)
        out.append(o)
    return out


# ---------------------------------------------------------------- fit
def sample_minions(r: Run, k: int = 6, seed: int = 1) -> list:
    ms = sorted(r.minions, key=lambda m: m["cycles"])
    if len(ms) <= k:
        return ms
    idx = {0, len(ms) - 1, len(ms) // 2}
    rng = np.random.default_rng(seed)
    while len(idx) < k:
        idx.add(int(rng.integers(len(ms))))
    return [ms[i] for i in sorted(idx)]


def fit_runs(runs: list) -> list:
    """The runs the constants are fitted to: M1's kernel only (an M4 run's constants are M1's changed by
    variant_constants' predictions; once the card has run them, fit the changed constants to them separately)."""
    keep, c1 = [], 0
    for r in runs:
        if r.perturb or r.nowait or r.stage == "dram" or r.name in ("m1-c0-tensor", "m1-tie") or r.m4kernel:
            continue
        if r.name.startswith("m1-c1-32-seed"):
            c1 += 1
            if c1 > 3:
                continue
        keep.append(r)
    return keep


def fit(runs: list, P0: dict | None = None, verbose: bool = True) -> dict:
    from scipy.optimize import least_squares
    P0 = dict(P0 or constants())
    fr = fit_runs(runs)
    samples = [(r, sample_minions(r), 2.0 if r.name.startswith("m3") else 1.0) for r in fr]
    x0 = np.array([P0[k] for k in FIT_NAMES])
    lo = np.zeros(len(x0))
    hi = np.full(len(x0), np.inf)
    for nm in ("C_OP_str", "C_OP_res"):  # an int8 op moves 2 x 1 KB: never under 256 cycles (et-soc1-notes.md)
        lo[FIT_NAMES.index(nm)] = 256.0
    x0 = np.clip(x0, lo, None)

    def resid(x):
        P = dict(P0)
        P.update(dict(zip(FIT_NAMES, x)))
        res = []
        for r, ms, wgt in samples:
            sims = sim_run(r, P, ms)
            w = wgt / math.sqrt(len(ms))
            for mn, o in zip(ms, sims):
                res.append(w * (o["cycles"] - mn["cycles"]) / mn["cycles"])
                res.append(w * (o["wait"] - mn["wait"]) / mn["cycles"])
        return np.array(res)

    sol = least_squares(resid, x0, bounds=(lo, hi), x_scale=np.maximum(np.abs(x0), 1e-2), diff_step=1e-3,
                        max_nfev=400, verbose=2 if verbose else 0)
    P = dict(P0)
    P.update({k: float(v) for k, v in zip(FIT_NAMES, sol.x)})
    r = resid(sol.x)
    P["_fit_rms"] = float(np.sqrt(np.mean(r ** 2)))
    P["_fit_runs"] = len(samples)
    P["_fit_minions"] = sum(len(ms) for _, ms, _ in samples)
    return P


def validate(runs: list, P: dict) -> list:
    out = []
    for r in runs:
        if r.perturb:
            continue
        sims = sim_run(r, P)
        mc = np.array([m["cycles"] for m in r.minions], float)
        mw = np.array([m["wait"] for m in r.minions], float)
        pc = np.array([o["cycles"] for o in sims])
        pw = np.array([o["wait"] for o in sims])
        out.append(dict(run=r.name, S=r.S, k=r.k, path=r.path, stage=r.stage, nbuf=r.nbuf, epi=r.epi,
                        minions=len(mc), U=r.U, fitted=r in fit_runs(runs), meas_max=mc.max(), pred_max=pc.max(),
                        meas_med=float(np.median(mc)), pred_med=float(np.median(pc)), meas_wait=float(mw.mean()),
                        pred_wait=float(pw.mean()), err_max=pc.max() / mc.max() - 1,
                        rms_rel=float(np.sqrt(np.mean(((pc - mc) / mc) ** 2))),
                        meas_imb=mc.max() / np.median(mc), pred_imb=pc.max() / np.median(pc)))
    return out


def print_validation(v: list):
    print(f"{'run':22s} {'S':>2s} k path stage/nb epi {'P':>4s}   U   | {'max meas':>9s} {'model':>9s} {'err':>6s} | "
          f"{'median':>9s} {'model':>9s} | {'wait meas':>9s} {'model':>9s} | rms   | max/med meas model")
    for x in v:
        print(f"{x['run']:22s} {x['S']:2d} {x['k']} {x['path']:4s} {x['stage']:>4s}/{x['nbuf']}  {x['epi']}  "
              f"{x['minions']:4d} {x['U']:5.2f} | {x['meas_max']/1e6:9.2f} {x['pred_max']/1e6:9.2f} "
              f"{100*x['err_max']:+5.1f}% | {x['meas_med']/1e6:9.2f} {x['pred_med']/1e6:9.2f} | "
              f"{x['meas_wait']/1e6:9.2f} {x['pred_wait']/1e6:9.2f} | {x['rms_rel']:.3f} | "
              f"{x['meas_imb']:.2f} {x['pred_imb']:.2f}{'' if x['fitted'] else '   (not fitted)'}")


# ---------------------------------------------------------------- explain and what-if
def breakdown(r: Run, mn: dict, P: dict, U: float | None = None) -> dict:
    """hart 0's cycles of one minion, term by term (the solo terms, the issue-slot sharing and the wait)."""
    U = r.U if U is None else U
    o = sim_minion(mn["rle"], r.S, r.k1, r.res, r.nbuf, r.epi, r.stage, U, mn["copy"], P)
    ops = mn["ops"]
    ideal_ops = ops * P["C_OP_" + r.path]
    solo_busy = o["instr"] + o["tens"]
    return dict(cycles=o["cycles"], meas=mn["cycles"], copy=mn["copy"], wait=o["wait"], meas_wait=mn["wait"],
                tensor_ops_solo=ideal_ops, bw_contention=o["ops"] - ideal_ops, drain=o["tens"] - o["ops"],
                epilogue=o["epi"], tile_overhead=o["instr"] - o["epi"], smt=o["busy"] - solo_busy, T=mn["T"],
                O=mn["O"], ops=ops, gen=gen_cycles(r.S, r.k1, r.stage, U, P))


def explain(runs: list, P: dict):
    """The gap to 270 cycles per op as a product: imbalance (busiest / mean minion) x overhead (mean minion / its
    ops at C_OP) x op cost (C_OP / 270); the mean minion term by term; the busiest and median minions; and the
    planner's row-tile cost against the fitted pipeline's."""
    for r in runs:
        if not r.name.startswith("m3"):
            continue
        C = np.array([m["cycles"] for m in r.minions], float)
        order = np.argsort(C)
        ops = np.array([m["ops"] for m in r.minions], float)
        cop = P["C_OP_" + r.path]
        print(f"\n{r.name}: S={r.S} nbuf={r.nbuf} U={r.U:.2f}; launch {C.max()/F_HZ*1e3:.1f} ms against "
              f"{ops.sum()*270/len(C)/F_HZ*1e3:.1f} ms at 270 cycles per op, balanced: {C.max()/(ops.mean()*270):.2f}x "
              f"= imbalance {C.max()/C.mean():.2f} (busiest / mean minion) x overhead {C.mean()/(ops.mean()*cop):.2f} "
              f"(mean minion / its ops at {cop:.0f}) x op cost {cop/270:.2f} ({cop:.0f} / 270)")
        tot = dict(ops=0.0, bw=0.0, drain=0.0, epi=0.0, tile=0.0, smt=0.0, wait=0.0, copy=0.0, cyc=0.0)
        for mn in r.minions:
            b = breakdown(r, mn, P)
            for k_, v in (("ops", b["tensor_ops_solo"]), ("bw", b["bw_contention"]), ("drain", b["drain"]),
                          ("epi", b["epilogue"]), ("tile", b["tile_overhead"]), ("smt", b["smt"]),
                          ("wait", b["wait"]), ("copy", b["copy"]), ("cyc", b["cycles"])):
                tot[k_] += v
        n_ops = ops.sum()
        print("  mean minion, cycles per op: " + ", ".join(
            f"{lab} {tot[k_]/n_ops:.0f}" for lab, k_ in (("tensor ops", "ops"), ("L2 contention", "bw"),
                                                        ("drain", "drain"), ("epilogue", "epi"),
                                                        ("row-tile overhead", "tile"), ("issue-slot sharing", "smt"),
                                                        ("wait for rows", "wait"), ("copy-in", "copy"),
                                                        ("total", "cyc"))))
        for lab, i in (("busiest", order[-1]), ("median", order[len(order) // 2])):
            b = breakdown(r, r.minions[i], P)
            mix = ", ".join(f"{n}x{c}" for n, c in r.minions[i]["rle"][:6])
            print(f"  {lab:8s} slot {r.minions[i]['slot']:4d}: {b['T']} row tiles (nout x count: {mix}), {b['O']} "
                  f"output tiles, {b['ops']} ops; measured {b['meas']/1e6:.1f} M cycles ({b['meas']/b['ops']:.0f}/op), "
                  f"wait {b['meas_wait']/1e6:.1f} M; model {b['cycles']/1e6:.1f} M, wait {b['wait']/1e6:.1f} M")
            parts = [("tensor ops", b["tensor_ops_solo"]), ("L2 contention", b["bw_contention"]),
                     ("drain", b["drain"]), ("epilogue", b["epilogue"]), ("row-tile overhead", b["tile_overhead"]),
                     ("issue-slot sharing", b["smt"]), ("wait for rows", b["wait"]), ("copy-in", b["copy"])]
            print("    " + "; ".join(f"{k} {v/b['ops']:.0f}/op ({100*v/b['cycles']:.0f}%)" for k, v in parts))
        tile_over = lambda n: tile_terms(n, r.S, r.res, r.epi, r.U, P)  # noqa: E731
        row = []
        for nout in (1, 2, 4, 8, 16, 32):
            fitted = steady_cost(nout, r.S, r.k1, r.res, r.nbuf, r.epi, r.stage, r.U, P, tile_over)
            host = host_tile_cycles(r.G.nJ, r.G.nJ - nout, r.S)
            row.append(f"{nout}: {host/1e3:.1f}k / {fitted/1e3:.1f}k ({fitted/host:.1f}x)")
        print("  row-tile cost, host planner / fitted pipeline, by column tiles: " + "; ".join(row))


def steady_cost(nout: int, S: int, k1: int, res: bool, nbuf: int, epi: int, stage: str, U: float, P: dict,
                tile_over, n: int = 64) -> float:
    """Cycles per row tile of a long run of identical row tiles (the pipeline's period): the fitted planner's cost."""
    a = sim_minion([(nout, n)], S, k1, res, nbuf, epi, stage, U, 0.0, P, tile_override=tile_over)["cycles"]
    b = sim_minion([(nout, 2 * n)], S, k1, res, nbuf, epi, stage, U, 0.0, P, tile_override=tile_over)["cycles"]
    return (b - a) / n


def predict(r: Run, P: dict, *, mods: dict | None = None, hidden_epi: bool = False, nbuf: int | None = None,
            replan: bool = False, iters: int = 5) -> dict:
    """One run under a kernel change, on all its minions: mods rescales fitted constants ({name: factor}),
    hidden_epi software-pipelines the epilogue behind the next output tile's first S-1 ops (it still takes issue
    slots from hart 1), nbuf changes the staging buffers, replan re-balances with the fitted model (the pipeline's
    period per row tile) instead of the host's model. U (the shire's L2 demand) is iterated to a fixed point, and the
    shire's L2 at 128 B per cycle is a floor under every shire's time."""
    Q = dict(P)
    for k, f in (mods or {}).items():
        Q[k] = Q[k] * f
    nb = nbuf or r.nbuf
    G = r.G
    state = dict(U=r.U)

    def tile_over(nout):
        tt = tile_terms(nout, r.S, r.res, r.epi, state["U"], Q)
        if hidden_epi and tt["epi"] > 0:
            shadow = max(r.S - 1, 0) * Q["C_OP_" + r.path]
            left = nout * max(0.0, Q["E_OUT"] - shadow)
            tt = dict(tt)
            tt["p2"] -= tt["epi"] - left
            instr_full = tt["instr"]
            tt["instr"] -= tt["epi"] - left
            tot = tt["instr"] + tt["tens"]
            tt["s0"] = (Q["SIG_I"] * tt["instr"] + Q["SIG_T"] * tt["tens"]) / tot
            # the hidden epilogue still issues on the shared slot: hart 1 is slowed as before
            tt["s1"] = min(Q["SIG_GI"], (Q["SIG_GI"] * instr_full + Q["SIG_GT"] * tt["tens"]) / tot)
            tt["epi"] = left
        return tt

    plan = r.plan
    copy = float(np.median([m["copy"] for m in r.minions]))
    for _ in range(iters):
        if replan:
            table = {nout: steady_cost(nout, r.S, r.k1, r.res, nb, r.epi, r.stage, state["U"], Q, tile_over)
                     for nout in range(1, G.nJ + 1)}
            plan = make_plan(G, r.shires, r.per_shire, r.rounds, 0, G.workTiles,
                             cost=lambda J: table.get(G.nJ - J, 1.0))
        cyc, sb = [], {}
        for slot, blocks in plan.items():
            rle = plan_rle(G, blocks)
            cyc.append(sim_minion(rle, r.S, r.k1, r.res, nb, r.epi, r.stage, state["U"], copy, Q,
                                  tile_override=tile_over)["cycles"])
            sb[slot // 32] = sb.get(slot // 32, 0.0) + shire_bytes(rle, r.S, r.res)
        cyc = np.array(cyc)
        Unew = float(np.mean(list(sb.values()))) / (float(np.median(cyc)) * BW_SHIRE)
        done = abs(Unew - state["U"]) < 0.01
        state["U"] = Unew
        if done:
            break
    floor = max(sb.values()) / BW_SHIRE
    tmax = max(float(cyc.max()), floor)
    ops = sum(m["ops"] for m in r.minions)
    return dict(cycles=tmax, ms=tmax / F_HZ * 1e3, imb=float(cyc.max() / np.median(cyc)), U=state["U"],
                floor_ms=floor / F_HZ * 1e3, per_op=tmax / (ops / len(cyc)), bound="shire L2" if floor >= cyc.max()
                else "pipeline")


def gen_mods(P: dict, S: int, k1: int, optimistic: bool = False) -> dict:
    """Incremental row generation: each row is prefix XOR x_last, the (k-2)-prefix (with y) computed once per run of
    rows that share it; X transposed sample-major (bit-plane per slice), so the 16 rows' x_last words of a slice are 2
    lines, not 16 loads through pointers; the row pointers stay in registers. Modelled: the per-factor term
    G_K * (k-1) becomes G_K / 8 (one factor, 2 lines instead of 16 words), the per-tile set-up halves (no pointer table,
    no multiplies by S), and the per-slice term (the 32 staged 32-byte stores, the expansion and y) stays. optimistic:
    the per-slice term also falls to 900 cycles (if the stores do not block)."""
    old = P["G_TILE"] + S * (P["G_SLICE"] + P["G_K"] * k1)
    gs = 900.0 if optimistic else P["G_SLICE"]
    new = 0.5 * P["G_TILE"] + S * (gs + P["G_K"] / 8.0)
    f = new / old
    return {"G_TILE": f, "G_SLICE": f, "G_K": f}


def whatif(runs: list, P: dict):
    for r in runs:
        if not r.name.startswith("m3"):
            continue
        meas = max(m["cycles"] for m in r.minions)
        base = P["G_TILE"] + r.S * (P["G_SLICE"] + P["G_K"] * r.k1)
        gB = gen_mods(P, r.S, r.k1)
        gBo = gen_mods(P, r.S, r.k1, optimistic=True)
        cop = {"C_OP_" + r.path: 300.0 / P["C_OP_" + r.path]}
        print(f"\n{r.name}: measured {meas/F_HZ*1e3:.1f} ms; generation {base:.0f} cycles per row tile solo "
              f"(B: x{gB['G_TILE']:.2f}, B optimistic: x{gBo['G_TILE']:.2f})")
        scen = [
            ("as run (model)", {}),
            ("A: planner weighted by the fitted model", dict(replan=True)),
            ("B: incremental generation", dict(mods=gB)),
            ("B + A", dict(mods=gB, replan=True)),
            ("C: epilogue hidden behind S-1 ops", dict(hidden_epi=True)),
            ("C + A", dict(hidden_epi=True, replan=True)),
            ("D: 3 A buffers, op 300 cycles", dict(mods=cop)),
            ("E: both harts generate (gen x0.88 when gen-bound)", dict(mods={"G_TILE": 0.88, "G_SLICE": 0.88,
                                                                             "G_K": 0.88})),
            ("2 buffers (L2 needs 3.0 MB of scratchpad)", dict(nbuf=2)),
            ("B + C + A", dict(mods=gB, hidden_epi=True, replan=True)),
            ("B + C + A, 2 buffers", dict(mods=gB, hidden_epi=True, replan=True, nbuf=2)),
            ("B + C + D + A, 2 buffers", dict(mods={**gB, **cop}, hidden_epi=True, replan=True, nbuf=2)),
            ("B(optimistic) + C + D + A, 2 buffers", dict(mods={**gBo, **cop}, hidden_epi=True, replan=True, nbuf=2)),
        ]
        for lab, kw in scen:
            p = predict(r, P, **kw)
            print(f"  {lab:50s} {p['ms']:7.1f} ms ({meas/F_HZ*1e3/p['ms']:4.2f}x)  max/med {p['imb']:.2f}  "
                  f"{p['per_op']:5.0f} cycles/op  U {p['U']:.2f}  shire-L2 floor {p['floor_ms']:.1f} ms ({p['bound']})")


# ---------------------------------------------------------------- the host's model of a launch (host/main.cpp)
def host_stage(G: Geom, per_shire: int, stage: str = "auto", nbuf: int = 0, scp_kb: int = 2560) -> tuple:
    """main.cpp's staging choice -> (scratchpad?, buffers): auto = the scratchpad with 2 buffers, else 1, else DRAM
    with 2."""
    off = 256 * 1024 + G.nJ * G.S * 1024
    sb = 16 * G.S * 64

    def fits(nb):
        return off + per_shire * nb * sb <= scp_kb * 1024
    if stage == "dram":
        return False, nbuf or 2
    if nbuf:
        return fits(nbuf), nbuf
    if fits(2):
        return True, 2
    if fits(1):
        return True, 1
    return False, 2


def pipe_table(G: Geom, P: dict, nbuf: int, dram: bool, U: float, epi: int = 1) -> dict:
    """spp_common.h pipeTileCost: {J: the pipeline's period for a row tile with J0 = J} (J = nJ: 1.0)."""
    res = G.S <= 3
    stage = "dram" if dram else "scp"
    tile_over = lambda n: tile_terms(n, G.S, res, epi, U, P)  # noqa: E731
    tab = {J: steady_cost(G.nJ - J, G.S, G.k - 1, res, nbuf, epi, stage, U, P, tile_over) for J in range(G.nJ)}
    tab[G.nJ] = 1.0
    return tab


def host_model(n: int, k: int, m: int, shires: list, per_shire: int, rounds: int = 4, slice_i: int = 0,
               slice_n: int = 1, gen_inc: bool = True, epi_hide: bool = True, abuf3: bool = False,
               cost_fit: bool = True, slice_fit: bool | None = None, stage: str = "auto", nbuf: int = 0,
               epi: int = 1, P: dict | None = None, pipe_set: dict | None = None, fallback: bool = False) -> dict:
    """What sparseparity_host computes for a launch with the built-in plan (--dry prints the same model_s): the
    staging, the slice and the plan cut by M1's cost or the fitted one, U iterated three times on the steady costs,
    then every minion simulated at that U. pipe_set: the host's --pipe-set (constants overridden after the
    variant's). fallback: also the same plan simulated with M1's fitted constants (the host's model_fallback_s, which
    its guard takes x1.15 while an M4 change runs on predicted constants)."""
    G = Geom(n, k, m)
    slice_fit = cost_fit if slice_fit is None else slice_fit
    scp, nb = host_stage(G, per_shire, stage, nbuf)
    dram = not scp
    Q = variant_constants(gen_inc, epi_hide, abuf3 and G.S > 3, P)
    Q.update(pipe_set or {})
    fit_tab = pipe_table(G, Q, nb, dram, 0.58 * per_shire / 32.0, epi) if (cost_fit or slice_fit) else None
    t0, t1 = slice_range(G, slice_i, slice_n, (lambda J: fit_tab[J]) if slice_fit else None)
    plan = make_plan(G, shires, per_shire, rounds, t0, t1, cost=(lambda J: fit_tab[J]) if cost_fit else None)
    copy = 5000.0 + 200.0 * ((G.nJ * G.S + per_shire - 1) // per_shire)
    res = G.S <= 3
    rles = {g: plan_rle(G, b) for g, b in plan.items()}

    def simulate(C: dict) -> tuple:
        U = 0.58 * per_shire / 32.0
        for _ in range(3):
            tab = pipe_table(G, C, nb, dram, U, epi)
            est, sb = [], {}
            for g, rle in rles.items():
                if not rle:
                    continue
                est.append(copy + sum(c * tab[G.nJ - nout] for nout, c in rle))
                sb[g // 32] = sb.get(g // 32, 0.0) + shire_bytes(rle, G.S, res)
            if not est:
                break
            est.sort()
            U = (sum(sb.values()) / len(sb)) / (est[len(est) // 2] * BW_SHIRE)
        cyc = {g: sim_minion(rle, G.S, k - 1, res, nb, epi, "dram" if dram else "scp", U, copy, C)["cycles"]
               for g, rle in rles.items() if rle}
        mx = max(cyc.values())
        return mx, mx / (sum(cyc.values()) / len(cyc)), U, len(cyc)
    mx, imb, U, nmin = simulate(Q)
    fb = simulate(variant_constants(False, False, False, P))[0] / F_HZ if fallback else 0.0
    return dict(model_s=mx / F_HZ, imbalance=imb, U=U, stage="dram" if dram else "scp",
                nbuf=nb, tiles=(t0, t1), minions=nmin, ops=sum(n_ * c for rle in rles.values() for n_, c in rle) * G.S,
                ops_max=max(sum(n_ * c for n_, c in rle) for rle in rles.values()) * G.S, fallback_s=fb)


# The m4 card steps (card_run.sh m4): name -> (instance, shires, per_shire, slice, configuration). A configuration
# is the host's options; `cfg` maps it to host_model's arguments. Every A/B at one shire passes --slice-cost m1, so
# every configuration scans the same tiles.
M4_CFG = {
    "m1": ("--variant m1", dict(gen_inc=False, epi_hide=False, abuf3=False, cost_fit=False)),
    "a": ("--variant m1 --cost fit", dict(gen_inc=False, epi_hide=False, abuf3=False, cost_fit=True)),
    "b": ("--variant m1 --cost fit --gen inc", dict(gen_inc=True, epi_hide=False, abuf3=False, cost_fit=True)),
    "c": ("--variant m1 --cost fit --epi hide", dict(gen_inc=False, epi_hide=True, abuf3=False, cost_fit=True)),
    "m4": ("--variant m4", dict(gen_inc=True, epi_hide=True, abuf3=False, cost_fit=True)),
    "m4d": ("--variant m4 --abuf 3", dict(gen_inc=True, epi_hide=True, abuf3=True, cost_fit=True)),
    # M4's kernel on the plan cut by M1's fitted constants (--pipe-set changes only the plan and the model): the
    # kernel's gain apart from the plan's balance (review of M4, finding 2)
    "m4a": ("--variant m4 --pipe-set HIDDEN=0,G_TILE=2081,G_SLICE=2108,G_K=570.3",
            dict(gen_inc=True, epi_hide=True, abuf3=False, cost_fit=True,
                 pipe_set=dict(HIDDEN=0, G_TILE=2081, G_SLICE=2108, G_K=570.3))),
}
M4_INST = {"L1": (512, 4, 448), "L2": (512, 4, 1850), "F5": (256, 5, 1925)}
M4_STEPS = (
    # one shire, 32 minions: L1's widest and narrowest thirds, L2's widest eighth and narrowest sixteenth (cut by
    # M1's cost, so the four configurations scan the same tiles; M1 fits under 4 s)
    [(f"m4-1s-l1-{w}-{c}", "L1", 1, si, sn, c) for w, si, sn in (("w", 0, 3), ("n", 2, 3))
     for c in ("m1", "a", "m4", "m4d")] +
    [(f"m4-1s-l2-{w}-{c}", "L2", 1, si, sn, c) for w, si, sn in (("w", 0, 8), ("n", 15, 16))
     for c in ("m1", "a", "m4", "m4d")] +
    # all 32 shires: L1 and L2 whole (closed forms), each change alone and together
    [(f"m4-32s-{i.lower()}-{c}", i, 32, 0, 1, c) for i in ("L1", "L2") for c in ("m1", "a", "b", "c", "m4", "m4d")] +
    [("m4-32s-l2-m4a", "L2", 32, 0, 1, "m4a")] +
    # (256, 5) on 32 shires: M1 needs two launches (4.4 s whole); M4 whole too (closed forms)
    [(f"m4-32s-f5-h{si}-{c}", "F5", 32, si, 2, c) for si in (0, 1) for c in ("m1", "m4", "m4d")] +
    [("m4-32s-f5-m4", "F5", 32, 0, 1, "m4")]
)
# Steps that card_run.sh runs with --trust-model, after their gates ran within x1.3 of the model
M4_TRUST = {"m4-32s-f5-m4"}


def m4_steps(verbose: bool = True) -> list:
    out = []
    for name, inst, nsh, si, sn, cfg in M4_STEPS:
        n, k, m = M4_INST[inst]
        opts, kw = M4_CFG[cfg]
        m1k = cfg in ("m1", "a")
        r = host_model(n, k, m, list(range(nsh)), 32, 4, si, sn, slice_fit=False,
                       fallback=not m1k and "pipe_set" not in kw, **kw)
        est = r["model_s"] * (1.15 if m1k else 1.3)
        trust = name in M4_TRUST
        guard = max(est, 0.0 if trust else 1.15 * r["fallback_s"])  # the host also takes M1's own model (smaller)
        out.append(dict(name=name, inst=inst, shires=nsh, slice=f"{si}/{sn}", cfg=cfg, opts=opts, **r,
                        est_s=est, guard_s=guard, trust=trust))
        if verbose:
            x = out[-1]
            print(f"{name:22s} {inst} {nsh:2d} shire(s) slice {x['slice']:4s} {opts:36s} model {x['model_s']*1e3:8.1f} ms "
                  f"est {x['est_s']*1e3:8.1f} ms  fallback x1.15 {1.15*x['fallback_s']*1e3:8.1f} ms  guard "
                  f"{x['guard_s']*1e3:8.1f} ms{' (trust)' if trust else ''}  max/mean {x['imbalance']:.3f}  "
                  f"U {x['U']:.2f}  {x['stage']}/{x['nbuf']}", flush=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "fit", "validate", "explain", "whatif", "table", "host", "m4"])
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--m", type=int, default=448)
    ap.add_argument("--nbuf", type=int, default=2)
    ap.add_argument("--stage", default="scp")
    ap.add_argument("--U", type=float, default=0.58, help="table: the shire's L2 demand (M3's runs: 0.58)")
    ap.add_argument("--data", default=str(DATA))
    ap.add_argument("--out", default=None, help="fit: write the constants to this JSON file")
    ap.add_argument("--model", default=None, help="constants from this JSON file instead of FITTED")
    ap.add_argument("--variant", default="m1", choices=["m1", "m4"], help="table, host: the kernel (m1: FITTED)")
    ap.add_argument("--gen", default=None, choices=["m1", "inc"])
    ap.add_argument("--epi", default=None, choices=["m1", "hide"])
    ap.add_argument("--abuf", type=int, default=2, choices=[2, 3])
    ap.add_argument("--cost", default=None, choices=["m1", "fit"], help="host: the plan's cost (default: fit for m4)")
    ap.add_argument("--slice-cost", default=None, choices=["m1", "fit"])
    ap.add_argument("--shires", type=int, default=32, help="host: shires 0..N-1")
    ap.add_argument("--per-shire", type=int, default=32)
    ap.add_argument("--slice", default="0/1")
    ap.add_argument("--timing-only", action="store_true")
    a = ap.parse_args(argv)
    P = constants()
    if a.model:
        P.update(json.loads(Path(a.model).read_text()))
    m4 = a.variant == "m4"
    gen_inc = m4 if a.gen is None else a.gen == "inc"
    epi_hide = m4 if a.epi is None else a.epi == "hide"
    if a.cmd == "m4":
        m4_steps()
        return 0
    if a.cmd == "host":
        si, sn = (int(x) for x in a.slice.split("/"))
        cost_fit = m4 if a.cost is None else a.cost == "fit"
        r = host_model(a.n, a.k, a.m, list(range(a.shires)), a.per_shire, 4, si, sn, gen_inc, epi_hide, a.abuf == 3,
                       cost_fit, None if a.slice_cost is None else a.slice_cost == "fit", epi=0 if a.timing_only else 1,
                       P=P)
        print(json.dumps(r))
        return 0
    if a.cmd == "table":
        G = Geom(a.n, a.k, a.m)
        res = G.S <= 3
        P = variant_constants(gen_inc, epi_hide, a.abuf == 3 and G.S > 3, P)
        tile_over = lambda n: tile_terms(n, G.S, res, 1, a.U, P)  # noqa: E731
        tab = {nout: round(steady_cost(nout, G.S, a.k - 1, res, a.nbuf, 1, a.stage, a.U, P, tile_over), 1)
               for nout in range(1, G.nJ + 1)}
        out = dict(n=a.n, k=a.k, m=a.m, S=G.S, nbuf=a.nbuf, stage=a.stage, U=a.U, cycles_per_row_tile=tab)
        print(json.dumps(out))
        if a.out:
            Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
        return 0
    runs = load_runs(Path(a.data))
    if a.cmd == "check":
        bad = [b for r in runs for b in r.check()]
        print(f"{len(runs)} runs, {sum(len(r.minions) for r in runs)} minions: "
              f"{len(bad)} disagree with the rebuilt work lists {bad[:5]}")
        return 1 if bad else 0
    if a.cmd == "fit":
        P = fit(runs, P)
        print(json.dumps(P, indent=1))
        if a.out:
            Path(a.out).write_text(json.dumps(P, indent=1) + "\n")
        print_validation(validate(runs, P))
    elif a.cmd == "validate":
        print_validation(validate(runs, P))
    elif a.cmd == "explain":
        explain(runs, P)
    elif a.cmd == "whatif":
        whatif(runs, P)
    return 0


if __name__ == "__main__":
    sys.exit(main())
