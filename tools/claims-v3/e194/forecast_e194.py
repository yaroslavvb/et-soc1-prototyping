#!/usr/bin/env python3
"""E194's frozen forecasts: the blind day's four programs on a third card, aifoundry2's card 0 under its own governor (E194.md).

    /usr/bin/python3 -I -B tools/claims-v3/e194/forecast_e194.py [--out DIR]   # writes forecast-e194.json and .txt
    /usr/bin/python3 -I -B tools/claims-v3/e194/forecast_e194.py --check       # recomputes and compares with the committed files

THE CARD SWITCHED AND THE CLOCK SET TO THE GOVERNOR'S (E194.md section 3). This file is E191's forecast code
(tools/claims-v3/e191/forecast_e191.py, sha256 794999c4..., in E191's registration list e458fa82...), itself E189's with
the card switched, with E191's card 'aifoundry1-c1' (key 'c1') switched to 'aifoundry2' (key 'a2') at every card-keyed
input the frozen predictor reads, and the clock moved from 600 MHz to 800 MHz, and nothing else changed:
 a. aifoundry2's idle law, leak slope and rest band (frozen-v2.json idle_laws) in given() and in the card at rest;
 b. the ledger v2's own aifoundry2 prices for sparse parity (the load's card), and in its arms (v2.1's int8 loop rate,
    v2c's vector-integer price and catalogue rows);
 c. the energy catalogue's aifoundry2 column for the plain programs (its per-card means and aifoundry2's measured issue
    rates, every one measured at 600 MHz): ledger_estimate.py's Catalogue takes the card as an argument, and its
    estimate() is handed aifoundry2's (CatCard below);
 d. the copy's DRAM-read price on random bytes, which ledger_estimate.py looks up at frozen-v2.json's 'a3' key:
    aifoundry2's key ('a2');
 e. aifoundry2's starting die, 55 C forecast in a 46-57 C band (E194.md section 5: its latest committed session, E190
    arm A, and E194's die gate).
THE CLOCK (E194.md section 3.1): the forecast is at 800 MHz, the governor's top point, the clock E190's arm A read in
every counted sample under load on this card (Fri 13 Nov 2026). What the clock changes, by the frozen ledger's own form
(tools/ledger/ledger_v2.py: v2 = (V/V600)^2, aifoundry2's volts at 600 and 800 MHz in frozen-v2.json):
 f. every price the ledger's form scales by v2 is scaled by v2(800) = (0.6174109375 / 0.5174)^2: the tensor term, the
    instruction classes (sparse parity's vector-integer class, and the catalogue rows of the plain programs and of v2c,
    all measured at 600 MHz) and the awake term; the byte paths carry no v2 in the ledger's form and stay as frozen;
 g. every seconds figure made of cycles is the same cycles at 800 MHz (x 600/800): SHA-256's and the sorts' point, fast
    end and slow end (ledger_estimate.py's seconds are at its F_HZ, 600 MHz), sparse parity's model_s and est_s; the
    awake hart-cycles from a measured t_k are N x 800 MHz x t_k (spp_eval reads the load's own clock); the literals in
    bytes or lines a second (the copy's 27 and 76 GB/s, the L2's 27.4 G lines/s) carry no minion clock and stay;
 h. the card at rest is aifoundry2's idle law, which is its 600 MHz idle (the governor's idle point); the frozen ledger
    has no term for the clock's own base at 800 MHz ("v2 has no validated 800 MHz static term", loads_ledger_v2.py), so
    none is added (its size by E136's relation is a REPORTED reading below, never used).
The cycle counts, the counts of instructions and bytes, the int8 loop's cycles an op and the probes' bytes a cycle are
counted, not timed, and stay; where a frozen rate is in ops a second at 600 MHz (the int8 zeros anchor), it is turned into
cycles at F_REF (600 MHz).
Where the frozen predictor fixes aifoundry3 where no argument reaches, the switch is made here and checked, as in E191:
ledger_estimate.py's rest_and_heat() sets its card inside, so rest_and_heat_card() is that function with its card as a
parameter (build() checks that at 'aifoundry3' it returns exactly what rest_and_heat() returns); sparse parity's load is
rebuilt at aifoundry3 and 600 MHz first and checked to reproduce ledger_estimate.py's prediction exactly, then its card
and its clock are switched.
ONE INPUT HAS NO AIFOUNDRY2 ENTRY: sparse parity's operand kind, int8.pm1 (M10 priced it on aifoundry3 only), is carried
from aifoundry3 unchanged, its band unchanged (carried() below), as E191 carried it to card 1. ONE AIFOUNDRY2 ENTRY IS A
PLACEHOLDER: frozen-v2.json's int8 zeros anchor for 'a2' is aifoundry3's E78 anchor at a 318-cycle loop's rate, labelled
there "a PLACEHOLDER ... used only where it cancels"; sparse parity's tensor term and v2.1's loop rate read it as keyed,
and it does not cancel there (E194.md section 3). What carries no card stays as frozen: ledger_estimate.py's literal
prices (the copy's write-back path, the DRAM-read bands, the L2 price for SHA-256 and the sort), the band rules' literals
below, the counts and the seconds models.

THE PREDICTOR (E189.md section 3), unchanged: the load ledger v2 as frozen (commit 06d60fa2, frozen-v2.json sha256
59ff9117...), through workloads/ledger/ledger_estimate.py as committed at 46a16bd0 (sha256 pinned in PINS below), which
prices the three plain programs at the energy catalogue's rows and sparse parity by the ledger v2 exactly as v2 prices
E59. This file never edits either; it imports them after checking every pinned input's sha256, and refuses otherwise.

WHAT THIS FILE ADDS, each stated in E189.md before any E189 datum, and kept here:
 1. the sort at 1,800 sorts a launch, a dated change from Q166's 1,500 (E189.md section 4.3): ledger_estimate.py's own
    CARD entry is given reps 1800 before its estimate() runs; the counts per sort are the simulator's, unchanged;
 2. a two-sided band on every configuration's seconds (E189.md section 5.1): the fast end is new, the point and the slow
    end are ledger_estimate.py's (the slow end plus the L1 misses' wait at the L2's line rate for SHA-256 and the sort);
 3. the J with the card at rest band carried over that two-sided band with ledger_estimate.py's own rest_and_heat()
    (sparse parity: ledger_v2.predict() at both ends of its seconds band and of the die band);
 4. every forecast split by ledger term, each term with its band; the instruction term split by class with
    ledger_estimate.py's own price_counts() on each class's counts (recorded from estimate()'s own call);
 5. the given-seconds forecast as a frozen function of the measured kernel seconds t_k, the measured wall seconds a
    launch t_w and the measured starting die T0 (given() below; score_e194.py calls it, never refits);
 6. the registered arms beside the primary: v2.1 (sparse parity's op cycles priced once, posthoc_ledger_v2.py's rule)
    and v2c (sparse parity's hart work from the counter's counts); both equal the primary on the five plain configurations;
 7. the counters arm's expectations (reported only; E189.md section 7; E189's kit dropped the arm, so E194 never runs it).
AND, NEW IN E194 (REPORTED, never scored, never used by given()): the same forecast at 600 MHz on aifoundry2 (the clock's
effect), E189's and E191's frozen forecasts beside it (comparison only), the size of the clock's base by E136's relation,
and the share of each burst the governor's climb from 600 MHz takes (E190 arm A's median climb).

Floats in the written files are rounded to 6 significant digits, so a last-digit difference in sum() between Python
versions cannot show. Standard library only. Desk only: no device, no ssh. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
F_REF = 600e6                             # the clock of every frozen rate and of ledger_estimate.py's seconds
F_HZ = 800e6                              # E194's clock: the governor's top point under load (E194.md section 3.1)
N_MIN = 1024
CARD, CK = "aifoundry2", "a2"             # the card switched (E194.md section 3); E191's: "aifoundry1-c1", "c1"
T0_FORECAST, T0_BAND = 55.0, (46.0, 57.0)  # aifoundry2's starting die (E194.md section 5)
SIG = 6                                   # significant digits in the written files
INTERPRETER = ("named: /usr/bin/python3 3.12.3 wrote the files (aifoundry2, the only python3 on that box; --check passes "
               "under it); floats rounded to 6 significant digits; no other interpreter was run")
PROGS = "docs/reports/data/2026-11-12-q166-progs"
PINS = {
    "workloads/ledger/ledger_estimate.py": "e3670e78da97107c067512450e57698680be4a1def1a0d01a232d4f360eef2f2",
    "tools/ledger/ledger_v2.py": "214cf7a49c1edae206ae34133bb6e2dc1f99a414e367b4617b2607f451cd2886",
    "tools/ledger/loads_ledger_v2.py": "6e4a9ec6724b00d90d94cf53d0fa3f3207a92321669e666f02afdcddfd28f85e",
    "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json": "59ff911705137e5486efcb15c482919e3d257f800193bcc9f1d78ee7283753ce",
    "docs/reports/data/2026-09-23-energy-manual/catalogue.json": "1186a9764838330369bc87f90f9ed4aed03d9d1373fd3185a8f107cf2eb1a7ae",
    "tools/counter/card_compare_sparseparity.py": "0de98e8e1b83badb8e18dec10273c40588f318f6173b9e766bc615470dbc51cf",
    "tools/counter/count_kernel.py": "089f354c12912026e70e0ee0c718454d1b079292e456c830d9b590c66111bff2",
    PROGS + "/SHA256SUMS": "96493d9f5e19915057ebe3112bdac568460499920e2beb0e7c1b792a9b8a54b4",
    PROGS + "/runs/p2-dry/new-dry.json": "4dc766230b27af63019e4a00ea09a682de3ed02903f6c193a6e3caca6426fafd",
    PROGS + "/digests/expect-card-b2048-r800.txt": "d6ca60ee9a1d6b06e4ad330e64a776c69214258f9acfca8265c72d912586d7d9",
    "docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel/all-addr2line.txt.gz":
        "0e2ba1e96405112211f8111dae44e4e3dcb03f5ea5206afc710b075ced54ef76",
    "docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel/sparseparity.dis":
        "7339a082c44e74ecba72205ae6593ced3b9e764bec5633ed0b04c68efbd0d0a5",
}
# read for the REPORTED readings only (E194.md sections 5 and 6); never an input to a forecast or to given()
REPORTED_PINS = {
    "tools/claims-v3/e189/forecast-e189.json": "b3b3b1325af7850d75226e16d8a2bfc022130bed10249ed315b9830fd83e9465",
    "tools/claims-v3/e191/forecast-e191.json": "4cd771746ef4c92208cf1552392ea5fc87e3cbbda539a77ad86d232c166dbba6",
    "tools/claims-v3/e136/predictions-e136.json": "542567e70e02b56db717b2a6e0b0fdafb7e011ee2bd8c9b857b88db1ac949018",
}
SPP_SLICES = [PROGS + "/runs/p2-new-s0", PROGS + "/runs/p2-new-s10000", PROGS + "/runs/p2-new-s19999"]
SORT_REPS = 1800                          # the dated change (E189.md section 4.3); Q166 proposed 1,500
L2_LINES_PER_S = 27.4e9                   # energy manual 04 (E48): L1 misses served at 27.4 G lines/s from the L2, the chip
H1_OVER_H2 = ("add", 0.581, 0.3727)       # the one row the catalogue measured both ways: add, one hart / both harts
SPP_FAST = 0.90                           # sparse parity's fast end: model_s x 0.90 (the model's held-out misses 5.0, 7.5%)
CONFIG_ORDER = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
# E189.md section 4's launches a burst, which E194 keeps (E194.md section 4); used here only for the climb's reading
K_E189 = {"copy-zeros": 8, "copy-random": 8, "sha256": 9, "sort-sorted": 8, "sort-shuffled": 7, "sparse-parity": 9}
# the governor's climb from its idle point to 800 MHz after a process's first launch on this card: E190 arm A's 84
# processes (desk/climb_e190.py over its committed telemetry): 0.014-1.325 s, median 0.852 s (REPORTED reading only)
CLIMB_MEDIAN_S = 0.852
# v2c: one catalogue row per counted class (the card's random mean, aifoundry2's column here; the row's band), E189.md 6
V2C_ROWS = {"scalar_int": "add", "load": "lw", "store": "sw", "branch_taken": "beq_taken",
            "branch_not_taken": "bne_nottaken", "jump": "jal", "mask_broadcast": "fbci.pi", "float_int_xfer": "fmv.x.w",
            "int_muldiv": "mul", "system": "csrr_fccnb", "sync": "fence", "atomic_local": "amoaddl.w"}
V2C_PRICED_ELSEWHERE = {"tensor": "the tensor term (M10's kernel term) and the scratchpad-load bytes",
                        "store_past_l1": "the staged rows' scratchpad-store bytes (fswg.ps)"}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_pins():
    bad = [p for p, h in list(PINS.items()) + list(REPORTED_PINS.items()) if sha(os.path.join(REPO, p)) != h]
    if bad:
        sys.exit("refused: pinned inputs differ: " + ", ".join(bad))
    # every file of Q166's progs data folder as committed (its own SHA256SUMS, itself pinned)
    d = os.path.join(REPO, PROGS)
    n = 0
    for ln in open(os.path.join(d, "SHA256SUMS")):
        if not ln.strip():
            continue
        h, p = ln.split(None, 1)
        if sha(os.path.join(d, p.strip())) != h:
            sys.exit(f"refused: {PROGS}/{p.strip()} differs from its SHA256SUMS")
        n += 1
    return n


def load_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def r6(x):
    """Round every float to SIG significant digits (the written files)."""
    if isinstance(x, dict):
        return {k: r6(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    if isinstance(x, float):
        if x == 0.0 or not math.isfinite(x):
            return x
        return float(f"{x:.{SIG - 1}e}")
    return x


def term(j, band, **kw):
    out = {"j": j, "band": [band[0], band[1]]}
    out.update(kw)
    return out


ZERO = {"j": 0.0, "band": [0.0, 0.0]}


# ---------------------------------------------------------------- the card switch's one carried input
def carried(F):
    """frozen-v2.json has no aifoundry2 price for sparse parity's operand kind, int8.pm1 (M10 priced it on aifoundry3
    only, from E90's signs tile). For the card switched, it is carried from aifoundry3 unchanged, its band unchanged
    (E194.md section 3, as E191 carried it to card 1). Returns F itself when nothing is missing; never edits F; every
    other input stays aifoundry2's own."""
    k = F["kinds"]["int8.pm1"]
    if CK in k:
        return F
    G = dict(F)
    G["kinds"] = dict(F["kinds"])
    G["kinds"]["int8.pm1"] = dict(k, **{CK: dict(k["a3"], carried_from=f"a3: frozen-v2.json has no {CK} entry")})
    return G


# ---------------------------------------------------------------- the frozen given-seconds function
def given(rec, t_k, t_w, T0, F, LV, arm="primary"):
    """The frozen forecast of one launch at the measured kernel seconds t_k (the last launch's slowest-minion cycles over
    800 MHz), wall seconds a launch t_w and starting die T0 (E194.md section 5.2). Plain programs: their joules over idle
    are counts times prices times v2(800) (no seconds in them; the awake rule leaves no waiting hart: E189.md 5.2);
    sparse parity: ledger_v2.predict() on the frozen load at 800 MHz with its awake hart-cycles from t_k. Both: the card
    at rest P_idle(T0) t_w and the run's own leakage rise k_leak(T0) k_rise J_over, with ledger_v2's own bands. Returns
    j_over_idle, its band, j_total, its band and the parts."""
    a = rec["primary"] if arm == "primary" else rec["arms"][arm]
    if "same_as" in a:
        a = rec["primary"]
    if a["kind"] == "plain":
        j_over, band = a["j_over_idle"], a["j_over_idle_band"]
        t = t_w
        p_over = j_over / t
        kl = LV.leak_slope(F, CARD, T0)
        kr = LV._c(F, "k_rise_c_per_w")
        kr_lo, kr_hi = LV._cb(F, "k_rise_c_per_w")
        kb = F["leak_slope_band_rel"]
        heat = kl * kr * p_over * t
        heat_band = [kl * kb[0] * kr_lo * band[0], kl * kb[1] * kr_hi * band[1]]
        p_rest, law = LV.idle_w(F, CARD, T0)
        rb = F["idle_laws"][CARD]["rest_band_w"]
        rest, rest_band = p_rest * t, [(p_rest - rb) * t, (p_rest + rb) * t]
        return {"j_over_idle": j_over, "j_over_idle_band": list(band), "rest_j": rest, "rest_band": rest_band,
                "heat_j": heat, "heat_band": heat_band, "j_total": rest + heat + j_over,
                "j_total_band": [rest_band[0] + heat_band[0] + band[0], rest_band[1] + heat_band[1] + band[1]],
                "rest_law": law}
    pr = spp_eval(a, t_k, t_w, T0, F, LV)
    return {"j_over_idle": pr["j_over_idle"], "j_over_idle_band": pr["j_over_idle_band"], "rest_j": pr["rest"]["j"],
            "rest_band": pr["rest"]["band"], "heat_j": pr["heat"]["j"], "heat_band": pr["heat"]["band"],
            "j_total": pr["j_total"], "j_total_band": pr["j_total_band"], "rest_law": pr["rest"]["law"],
            "awake_hart_cycles": pr["awake_hart_cycles_used"],
            "terms": {k: {"j": v["j"], "band": v["band"]} for k, v in pr["terms"].items()}}


def spp_eval(arm, t_k, t_w, T0, F, LV):
    """Sparse parity, one arm, at (t_k, t_w, T0): ledger_v2.predict() on the arm's frozen load, its awake hart-cycles
    from t_k at the load's own clock (each hart's cycles N f t_k beyond its busy cycles, less the arm's overlap for
    v2.1, floored at 0; f is the load's f_mhz: 800 for E194's loads, 600 for E59's); for v2c its counted instructions'
    joules (at 800 MHz, v2 already in them) added to J over idle, and the run's own rise recomputed on the new J over
    idle with predict()'s own formula (k_leak(T0) k_rise P_over t, band k_leak kb k_rise_band J_band). The frozen
    constants pass through carried() (int8.pm1 on aifoundry2; a load on any other card is untouched by it)."""
    load = copy.deepcopy(arm["load"])
    per_hart = N_MIN * load.get("f_mhz", 600.0) * 1e6 * t_k
    aw = max(0.0, per_hart - arm["hart0_busy_cycles"]) + max(0.0, per_hart - arm["hart1_busy_cycles"])
    aw = max(0.0, aw - arm.get("awake_overlap_hart_cycles", 0.0))
    load["awake_hart_cycles"] = aw
    load["seconds"] = t_w
    load["die_start_c"] = T0
    pr = LV.predict(load, carried(F))
    pr["awake_hart_cycles_used"] = aw
    j = arm.get("counted_instr_j")
    if j:
        pr["terms"]["instr:counted (v2c)"] = {"j": j[0], "band": [j[1], j[2]]}
        pr["j_over_idle"] += j[0]
        pr["j_over_idle_band"] = [pr["j_over_idle_band"][0] + j[1], pr["j_over_idle_band"][1] + j[2]]
        kl = pr["heat"]["k_leak_w_per_c"]
        kr = LV._c(F, "k_rise_c_per_w")
        kr_lo, kr_hi = LV._cb(F, "k_rise_c_per_w")
        kb = F["leak_slope_band_rel"]
        t = pr["seconds"]
        h = kl * kr * (pr["j_over_idle"] / t) * t
        hb = [kl * kb[0] * kr_lo * pr["j_over_idle_band"][0], kl * kb[1] * kr_hi * pr["j_over_idle_band"][1]]
        pr["heat"] = dict(pr["heat"], j=h, band=hb, die_rise_c=kr * pr["j_over_idle"] / t)
        pr["j_total"] = pr["rest"]["j"] + h + pr["j_over_idle"]
        pr["j_total_band"] = [pr["rest"]["band"][0] + hb[0] + pr["j_over_idle_band"][0],
                              pr["rest"]["band"][1] + hb[1] + pr["j_over_idle_band"][1]]
        pr["w_over_idle"] = pr["j_over_idle"] / t
    return pr


def rest_and_heat_card(ledger_v2, F, t, t_band, j_over, j_over_band, t0, t0_band, card=CARD):
    """ledger_estimate.py's rest_and_heat() (46a16bd0), its card a parameter: that function sets card = "aifoundry3"
    inside, and this copy differs from it only there (build() checks that at "aifoundry3" both return the same)."""
    p_rest, law = ledger_v2.idle_w(F, card, t0)
    rb = F["idle_laws"][card]["rest_band_w"]
    lo_t0 = min(ledger_v2.idle_w(F, card, x)[0] for x in t0_band)
    hi_t0 = max(ledger_v2.idle_w(F, card, x)[0] for x in t0_band)
    rest = {"w": p_rest, "law": law, "j": p_rest * t, "band": [(lo_t0 - rb) * t_band[0], (hi_t0 + rb) * t_band[1]]}
    kr = ledger_v2._c(F, "k_rise_c_per_w")
    kr_lo, kr_hi = ledger_v2._cb(F, "k_rise_c_per_w")
    kl = ledger_v2.leak_slope(F, card, t0)
    kb = F["leak_slope_band_rel"]
    p_over = j_over / t
    heat_j = kl * kr * p_over * t
    heat_band = [kl * kb[0] * kr_lo * (j_over_band[0] / t_band[1]) * t_band[0],
                 kl * kb[1] * kr_hi * (j_over_band[1] / t_band[0]) * t_band[1]]
    heat = {"k_leak_w_per_c": kl, "die_rise_c": kr * p_over, "j": heat_j, "band": heat_band}
    return rest, heat


# ---------------------------------------------------------------- building the forecasts
def class_split(le, cat, counts, orig_pc):
    """The instruction term split by the counter's classes (ledger_estimate.by_class_total's map), each class priced by
    ledger_estimate's own price_counts() on its own counts: j, band and hart-cycles a class (at the catalogue's 600 MHz
    prices; plain_record() applies the clock's v2)."""
    by = {}
    for m, n in sorted(counts.items()):
        c = next(iter(le.by_class_total({m: n})))
        by.setdefault(c, {})[m] = n
    out = {}
    for c, sub in sorted(by.items()):
        pc = orig_pc(cat, sub, "random")
        out[c] = {"j": pc["j"][0], "band": [pc["j"][1], pc["j"][2]], "count": sum(sub.values()),
                  "hart_cycles_point": pc["hart_cycles"][0], "hart_cycles_high": pc["hart_cycles"][1]}
    return out


def plain_record(key, r, counts, le, cat, orig_pc, LV, F, f_hz=F_HZ):
    """One plain program at the clock f_hz: ledger_estimate.py's record (at its 600 MHz) with the clock applied (E194.md
    3.1): the instruction term (and its split by class) times v2(f), the seconds made of cycles at f, the byte terms as
    frozen; then the card at rest and the run's own rise at the new seconds and J over idle."""
    cfg = r["config"]
    P = cfg["participants"]
    prog = cfg["prog"]
    v2 = LV.v2_factor(F, CARD, f_hz / 1e6)
    sc = F_REF / f_hz                           # seconds made of cycles: 600 MHz -> f
    cls = class_split(le, cat, counts, orig_pc)
    s = r["seconds"]
    if prog == "copy":
        fast, point, slow = s["band"][0], s["point"], s["band"][1]
        fast_how = ("progs-c's low end, kept: the stores alone at the write-back path's 27 GB/s (energy manual 4.1); "
                    "a byte rate, no minion clock in it")
        slow_how = ("progs-c's high end, kept: the stores at 27 GB/s plus the loads' bytes at 76 GB/s, unoverlapped; "
                    "byte rates, no minion clock in them")
        stall_s = 0.0
    else:
        point = s["point"] * sc
        h_tk = sum(v["hart_cycles_point"] for c, v in cls.items() if c in ("branch_taken", "jump"))
        h_rest = sum(v["hart_cycles_point"] for c, v in cls.items() if c not in ("branch_taken", "jump"))
        ratio = H1_OVER_H2[2] / H1_OVER_H2[1]
        fast = (h_tk + h_rest * ratio) / P / f_hz
        fast_how = ("every instruction but the taken branches and jumps at a lone hart's rate, by the one row the "
                    "catalogue measured both ways (add: 0.581 a hart-cycle alone, 0.3727 with both harts; x %.4f), the "
                    "taken branches and jumps at their both-harts rate (Q166 verify-progs fault 1's bound); hart-cycles "
                    "at %d MHz" % (ratio, round(f_hz / 1e6)))
        bt = [v for k, v in r["terms"].items() if k.startswith("bytes past the L1")][0]
        if prog == "sha256":
            lines_hi = bt["lines_high"]
        else:
            lines_hi = bt["bytes_point"] / 64.0
        per_minion_lines = lines_hi / (P / 2.0)
        stall_s = per_minion_lines * (N_MIN / (L2_LINES_PER_S / f_hz)) / f_hz
        slow = s["band"][1] * sc + stall_s
        slow_how = ("progs-c's high end (every one-cycle integer op at the in-place rows' rate), its hart-cycles at %d "
                    "MHz, plus every line past the L1 (the bytes term's high count) waited for at the L2's line rate, "
                    "27.4 G lines/s over the chip (energy manual 04, E48), unoverlapped: +%.4f s"
                    % (round(f_hz / 1e6), stall_s))
    t_band = [fast, slow]
    terms = {}
    ins = [v for k, v in r["terms"].items() if k.startswith("instructions")][0]
    terms["tensor ops"] = dict(ZERO, note="none in this program")
    terms["instructions by class"] = term(ins["j"] * v2, [ins["band"][0] * v2, ins["band"][1] * v2], count=ins["count"],
                                          v2=v2,
                                          by_class={c: {"j": v["j"] * v2, "band": [v["band"][0] * v2, v["band"][1] * v2],
                                                        "count": v["count"]}
                                                    for c, v in cls.items()},
                                          note=(f"catalogue rows, random column, {CARD}'s mean (measured at 600 MHz), "
                                                f"times v2 = (V{round(f_hz / 1e6)} / V600)^2; branches by outcome; "
                                                + ("the copy's vector loads and stores are inside the DRAM byte prices "
                                                   "and not priced again" if prog == "copy" else
                                                   "loads and stores at their L1-hit rows")))
    terms["awake, not issuing"] = dict(ZERO, note=("0 by the frozen awake rule: every hart issues its own work; no hart "
                                                    "waits on another (frozen-v2.json awake_rule)"))
    if prog == "copy":
        rd = [v for k, v in r["terms"].items() if k.startswith("DRAM reads")][0]
        wr = [v for k, v in r["terms"].items() if k.startswith("DRAM writes")][0]
        terms["bytes: L1"] = dict(ZERO, note="inside the DRAM paths' prices (measured end to end)")
        terms["bytes: L2"] = dict(ZERO, note="inside the DRAM paths' prices")
        terms["bytes: scratchpad"] = dict(ZERO, note="none")
        terms["bytes: DRAM read"] = term(rd["j"], rd["band"], bytes=rd["bytes"], pj_per_byte=list(rd["pj_per_byte"]),
                                         note="32 B vector loads, at the tensor-load DRAM row by analogy (04 4.1); "
                                              "bytes carry no v2 in the ledger's form")
        terms["bytes: DRAM write-back"] = term(wr["j"], wr["band"], bytes=wr["bytes"], pj_per_byte=list(wr["pj_per_byte"]),
                                               note="fsw.ps through the L1, the write-back path (04 4.1); bytes carry "
                                                    "no v2 in the ledger's form")
    else:
        bt = [v for k, v in r["terms"].items() if k.startswith("bytes past the L1")][0]
        terms["bytes: L1"] = dict(ZERO, note="inside the load and store rows (L1 hits)")
        terms["bytes: L2"] = term(bt["j"], bt["band"], note="bytes past the L1 at the L2's price (04 4.2, by analogy "
                                                             "with tensor loads), bracketed: 0 to the high count; "
                                                             "bytes carry no v2 in the ledger's form")
        terms["bytes: scratchpad"] = dict(ZERO, note="none")
        terms["bytes: DRAM read"] = dict(ZERO, note="the inputs' first reads (4 MiB or less a launch): not priced")
        terms["bytes: DRAM write-back"] = dict(ZERO, note="the outputs (64 B a hart, or the sort's work area, "
                                                          "16 MiB) are written back at the kernel's end: not priced")
    terms["mesh"] = dict(ZERO, note="not priced: the DRAM paths' prices include their mesh crossings")
    j_over = sum(v["j"] for v in terms.values())
    j_band = [sum(v["band"][0] for v in terms.values()), sum(v["band"][1] for v in terms.values())]
    # the card at rest and the run's own rise, carried over the two-sided seconds band and the die band, by
    # ledger_estimate.py's own rest_and_heat() with the card switched (rest_and_heat_card)
    rest, heat = rest_and_heat_card(LV, F, point, t_band, j_over, j_band, T0_FORECAST, T0_BAND, card=CARD)
    terms["the card at rest"] = term(rest["j"], rest["band"], w=rest["w"], law=rest["law"],
                                     note=f"{CARD}'s idle law (frozen-v2.json idle_laws; its 600 MHz idle, the governor's "
                                          f"idle point) at the forecast die {T0_FORECAST:g} C (band {T0_BAND[0]:g}-"
                                          f"{T0_BAND[1]:g} C) times the seconds (band: their two-sided band), +-0.5 W")
    terms["the run's own leakage rise"] = term(heat["j"], heat["band"], k_leak_w_per_c=heat["k_leak_w_per_c"],
                                               die_rise_c=heat["die_rise_c"],
                                               note=f"k_leak({T0_FORECAST:g} C) x k_rise x P_over_idle x t (M10's 4.5 s "
                                                    "window law)")
    j_total = rest["j"] + heat["j"] + j_over
    j_total_band = [rest["band"][0] + heat["band"][0] + j_band[0], rest["band"][1] + heat["band"][1] + j_band[1]]
    prim = {"kind": "plain", "j_over_idle": j_over, "j_over_idle_band": list(j_band)}
    return {
        "seconds": {"point": point, "band": t_band, "fast_how": fast_how, "slow_how": slow_how,
                    "point_how": s["how"] + ("" if prog == "copy" else f"; hart-cycles at {round(f_hz / 1e6)} MHz"),
                    "q166_band": list(s["band"]), "q166_point_at_600_mhz": s["point"], "l2_wait_s": stall_s},
        "j_over_idle": j_over, "j_over_idle_band": list(j_band), "w_over_idle": j_over / point,
        "j_total": j_total, "j_total_band": j_total_band, "terms": terms, "primary": prim,
        "counts": {"instructions_total": r["instructions_total"], "by_class_total": r["by_class_total"],
                   "per_participant_instructions": r["instructions_total"] / P,
                   "bytes_counted_card_total": r["bytes_counted"]["card_total"],
                   "units_per_participant": r["units_per_participant"], "unit": r["unit"],
                   "per_unit_per_participant_instructions": sum(r["per_unit_per_participant"].values())},
    }


def spp_record(r, le, LV, F, cc, ck, f_hz=F_HZ):
    """Sparse parity: the ledger v2's load as ledger_estimate.sparse_parity() builds it, made again here from the same
    pieces (checked to reproduce its prediction exactly, at aifoundry3 and 600 MHz, as it builds it), then the card and
    the clock switched, with its seconds band and its arms."""
    import loads_ledger_v2 as L  # noqa: E402  (pinned; ledger_estimate imports it the same way)
    plan = r["plan"]
    n, k, m = r["instance"]["n"], r["instance"]["k"], r["instance"]["m"]
    cy = F["cycle_model"]["FITTED"]
    cnt = L.sp_counts(n, k, m, 0, 1)
    S, U = cnt["S"], plan["model_U"]
    rows, outs, ops = cnt["row_tiles"], cnt["output_tiles"], cnt["ops"]
    gen_per_tile = (cy["G_TILE"] / 2.0 + S * (cy["G_SLICE"] + cy["G_K"] / 8.0)) * (1.0 + cy["KAPPA_G"] * U)
    store_cov = S * 1024.0 / F["probe_rates_b_per_minion_cycle"]["scp_store"]
    cyc = {"epilogue": outs * cy["E_OUT"], "row_tile_overhead": rows * cy["H_TILE"],
           "generation_hart1_beyond_its_stores": rows * max(0.0, gen_per_tile - store_cov)}
    hart0_busy = ops * cy["C_OP_str"] * (1.0 + cy["KAPPA_T"] * U) + outs * (cy["D_OUT_str"] + cy["E_OUT"]) \
        + rows * cy["H_TILE"]
    hart1_busy = rows * gen_per_tile
    x = L.DATA["pm1_int8"]
    t600 = plan["model_s"]
    load = {"card": "aifoundry3", "f_mhz": 600.0, "die_start_c": T0_FORECAST, "work_units": 1,
            "work_unit": "solve (one launch)", "seconds": t600,
            "tensor": [{"format": "int8", "kind": "int8.pm1", "ops": ops}],
            "instr": [{"class": "vec_int", "hart_cycles": cyc["epilogue"], "what": "epilogue (hart 0)"},
                      {"class": "vec_int", "hart_cycles": cyc["row_tile_overhead"], "what": "row-tile set-up (hart 0)"},
                      {"class": "vec_int", "hart_cycles": cyc["generation_hart1_beyond_its_stores"],
                       "what": "row generation beyond its stores (hart 1)"}],
            "bytes": [{"path": "scp_load", "bytes": 2048.0 * ops, "rho": x[0], "tau": x[1], "what": "A and B tiles"},
                      {"path": "scp_store", "bytes": 1024.0 * S * rows, "rho": x[0], "tau": x[1], "what": "staged rows"},
                      {"path": "dram_load", "bytes": 32.0 * n * S * 64.0, "rho": x[0], "tau": x[1], "what": "X copy-in"},
                      {"path": "l2_stream", "bytes": 192.0 * S * rows, "rho": x[0], "tau": x[1], "what": "X reads"}]}
    per_hart = N_MIN * F_REF * t600
    load["awake_hart_cycles"] = max(0.0, per_hart - hart0_busy) + max(0.0, per_hart - hart1_busy)
    pr = LV.predict(load, F)
    v = r["ledger_v2"]
    if not (pr["j_over_idle"] == v["j_over_idle"] and pr["j_total"] == v["j_total"]
            and pr["j_over_idle_band"] == v["j_over_idle_band"] and pr["j_total_band"] == v["j_total_band"]):
        sys.exit("refused: the rebuilt sparse-parity load does not reproduce ledger_estimate.py's prediction exactly")
    # the card and the clock switched, after the check (E194.md sections 3 and 3.1): the load's card, its clock (so
    # predict() applies v2 to the tensor, instruction and awake terms), its seconds (the cycle model's at f) and its awake
    # hart-cycles at f (the same count: N f t = N 600 MHz model_s)
    t = t600 * F_REF / f_hz
    load["card"] = CARD
    load["f_mhz"] = f_hz / 1e6
    load["seconds"] = t
    per_hart = N_MIN * f_hz * t
    load["awake_hart_cycles"] = max(0.0, per_hart - hart0_busy) + max(0.0, per_hart - hart1_busy)
    base = {"kind": "spp", "load": load, "hart0_busy_cycles": hart0_busy, "hart1_busy_cycles": hart1_busy}
    t_band = [SPP_FAST * t, plan["est_s"] * F_REF / f_hz]
    v2 = LV.v2_factor(F, CARD, f_hz / 1e6)

    def at(arm, tk, T0):
        return spp_eval(arm, tk, tk, T0, F, LV)

    def summarize(arm):
        p0_ = at(arm, t, T0_FORECAST)
        lo = at(arm, t_band[0], T0_BAND[0])
        hi = at(arm, t_band[1], T0_BAND[1])
        o_lo = at(arm, t_band[0], T0_FORECAST)
        o_hi = at(arm, t_band[1], T0_FORECAST)
        return p0_, {"j_over_idle": p0_["j_over_idle"],
                     "j_over_idle_band_at_point": p0_["j_over_idle_band"],
                     "j_over_idle_band": [min(o_lo["j_over_idle_band"][0], p0_["j_over_idle_band"][0]),
                                          max(o_hi["j_over_idle_band"][1], p0_["j_over_idle_band"][1])],
                     "j_total": p0_["j_total"],
                     "j_total_band": [min(lo["j_total_band"][0], p0_["j_total_band"][0]),
                                      max(hi["j_total_band"][1], p0_["j_total_band"][1])],
                     "w_over_idle": p0_["w_over_idle"],
                     "j_over_idle_at_band_ends": [o_lo["j_over_idle"], o_hi["j_over_idle"]],
                     "j_over_idle_band_at_band_ends": [o_lo["j_over_idle_band"], o_hi["j_over_idle_band"]]}

    p0, prim_sum = summarize(base)
    # ---- v2.1: the op cycles priced once (posthoc_ledger_v2.py e59_double_count's rule, applied to this instance); the
    # int8 loop's cycles an op from the anchor's rate, which is in ops a second at 600 MHz (so at F_REF)
    loop_int8 = N_MIN * F_REF / F["zeros_anchor"]["int8"][CK]["rate_ops_per_s"]
    scp_cyc = 2048.0 / F["probe_rates_b_per_minion_cycle"]["scp_load"]
    over = max(0.0, loop_int8 + scp_cyc - cy["C_OP_str"] * (1.0 + cy["KAPPA_T"] * U))
    v21 = dict(copy.deepcopy(base), awake_overlap_hart_cycles=over * ops)
    p21, sum21 = summarize(v21)
    # ---- v2c: the hart work from the counter's counts, by hart and class (ledger_estimate.spp_counter_fit's split and
    # fit, by hart), each class at one catalogue row (V2C_ROWS), the tensor class and the staging stores priced elsewhere;
    # the rows' joules (600 MHz prices) times v2(f), as the ledger's form prices an instruction class at f
    sites = cc.read_sites(os.path.join(REPO, le.SPP_SITES_REL))
    spin_pcs = set(pc for pc, ch in sites.items() if "wait_count" in ch)
    by_addr = {i.addr: i for i in ck.parse_dis(os.path.join(REPO, le.SPP_DIS_REL))}
    sl = []
    for d in SPP_SLICES:
        out = json.loads(open(os.path.join(REPO, d, "out.json")).read().strip().splitlines()[-1])
        cn = le.read_counts(os.path.join(REPO, d))
        hh = {}
        for th in ("0", "1"):
            hh[th] = cc.classes_of(cn["harts"][th]["per_pc"], by_addr, lambda x_: x_ not in spin_pcs)
        t0_, t1_ = out["plan"]["tiles"]
        sl.append({"x": (out["plan"]["ops"] / out["geometry"]["S"], t1_ - t0_), "h0": hh["0"], "h1": hh["1"]})
    xs = [s_["x"] for s_ in sl]
    classes = sorted(set(c for s_ in sl for h in ("h0", "h1") for c in s_[h]))
    per_hart = {"hart0": {}, "hart1": {}}
    for c in classes:
        ac, bc = cc.lstsq2(xs, [s_["h0"].get(c, 0) for s_ in sl])
        c1c = sum(s_["h1"].get(c, 0) for s_ in sl) / sum(s_["x"][1] for s_ in sl)
        per_hart["hart0"][c] = ac * outs + bc * rows
        per_hart["hart1"][c] = c1c * rows
    fit = r["counter_slices"]["per_solve_work_by_class"]
    for c in classes:
        tot = per_hart["hart0"][c] + per_hart["hart1"][c]
        if abs(tot - fit[c]) > 1e-6 * max(1.0, abs(fit[c])):
            sys.exit(f"refused: the per-hart fit does not add up to ledger_estimate's for class {c}")
    cat = le.Catalogue(os.path.join(REPO, le.CAT_REL), CARD)
    rows_used = {}
    jc = [0.0, 0.0, 0.0]
    busy_c = {"hart0": 0.0, "hart1": 0.0}
    by_class_v2c = {}
    for c in classes:
        if c in V2C_PRICED_ELSEWHERE:
            continue
        if c == "vector_int":
            e = F["instr_classes"]["vec_int"]["random_pj"][CK]
            elo, ehi = F["instr_classes"]["vec_int"]["band_pj"]
            rate, row = LV._c(F, "issue_rate"), "frozen-v2.json instr_classes.vec_int at issue_rate 0.37"
        else:
            row = V2C_ROWS[c]
            e, elo, ehi = cat.row(row, "random")
            rate = cat.rate(row, "random")
        rows_used[c] = {"row": row, "pj": e, "band_pj": [elo, ehi], "rate_per_hart_cycle": rate, "v2": v2}
        nt = per_hart["hart0"][c] + per_hart["hart1"][c]
        by_class_v2c[c] = {"count": nt, "j": nt * e * 1e-12 * v2, "band": [nt * elo * 1e-12 * v2, nt * ehi * 1e-12 * v2]}
        jc[0] += nt * e * 1e-12 * v2
        jc[1] += nt * elo * 1e-12 * v2
        jc[2] += nt * ehi * 1e-12 * v2
        busy_c["hart0"] += per_hart["hart0"][c] / rate
        busy_c["hart1"] += per_hart["hart1"][c] / rate
    v2c_load = copy.deepcopy(load)
    v2c_load["instr"] = []                      # v2's three cycle-model instruction terms, replaced by the counts
    v2c = {"kind": "spp", "load": v2c_load,
           "hart0_busy_cycles": ops * cy["C_OP_str"] * (1.0 + cy["KAPPA_T"] * U) + busy_c["hart0"],
           "hart1_busy_cycles": rows * store_cov + busy_c["hart1"],
           "counted_instr_j": jc, "by_class": by_class_v2c, "rows": rows_used,
           "priced_elsewhere": {c: V2C_PRICED_ELSEWHERE[c] for c in classes if c in V2C_PRICED_ELSEWHERE},
           "counted_per_hart_by_class": per_hart}

    pc_, sumc = summarize(v2c)
    # the split by ledger term (primary, at the point)
    T = p0["terms"]
    ins = [T[kk] for kk in T if kk.startswith("instr:")]
    terms = {
        "tensor ops": term(T["tensor:int8:int8.pm1:0"]["j"], T["tensor:int8:int8.pm1:0"]["band"], ops=ops,
                           note="M10's kernel term: the int8 zeros anchor (aifoundry2's entry, a placeholder holding "
                                "aifoundry3's E78 anchor) plus M10's D for int8.pm1 (carried from aifoundry3), per op, "
                                "times v2(800)"),
        "instructions by class": term(sum(x_["j"] for x_ in ins), [sum(x_["band"][0] for x_ in ins),
                                                                  sum(x_["band"][1] for x_ in ins)],
                                      by_activity={kk.split(":", 2)[2]: {"j": T[kk]["j"], "band": T[kk]["band"],
                                                                         "hart_cycles": T[kk]["hart_cycles"]}
                                                   for kk in T if kk.startswith("instr:")},
                                      note="the vector-integer class (frozen-v2.json instr_classes.vec_int) at issue "
                                           "rate 0.37, for the cycle model's busy cycles: hart 0's epilogue and row-tile "
                                           "set-up, hart 1's generation beyond its stores; times v2(800)"),
        "awake, not issuing": term(T["awake"]["j"], T["awake"]["band"], hart_cycles=T["awake"]["hart_cycles"],
                                   note="each running hart's cycles beyond its busy cycles (waits on the other hart), "
                                        "at the stalled-minion price times v2(800); this term follows t_k"),
        "bytes: L1": dict(ZERO, note="inside the scratchpad and L2 prices"),
        "bytes: L2": term(T["bytes:l2_stream:X reads"]["j"], T["bytes:l2_stream:X reads"]["band"],
                          bytes=T["bytes:l2_stream:X reads"]["bytes"], note="hart 1's reads of X (l2_stream)"),
        "bytes: scratchpad": term(T["bytes:scp_load:A and B tiles"]["j"] + T["bytes:scp_store:staged rows"]["j"],
                                  [T["bytes:scp_load:A and B tiles"]["band"][0] + T["bytes:scp_store:staged rows"]["band"][0],
                                   T["bytes:scp_load:A and B tiles"]["band"][1] + T["bytes:scp_store:staged rows"]["band"][1]],
                                  parts={"scp_load (A and B tiles, 2 KB an op)": T["bytes:scp_load:A and B tiles"],
                                         "scp_store (staged rows, S KB a row tile)": T["bytes:scp_store:staged rows"]}),
        "bytes: DRAM read": term(T["bytes:dram_load:X copy-in"]["j"], T["bytes:dram_load:X copy-in"]["band"],
                                 bytes=T["bytes:dram_load:X copy-in"]["bytes"], note="X copied into each shire, once"),
        "bytes: DRAM write-back": dict(ZERO, note="the results only (kilobytes): not priced"),
        "mesh": dict(ZERO, note="not priced (v2's sparse-parity load has no mesh row)"),
        "the card at rest": term(p0["rest"]["j"], p0["rest"]["band"], w=p0["rest"]["w"], law=p0["rest"]["law"],
                                 note=f"at the forecast seconds and {T0_FORECAST:g} C; the total's band below carries the "
                                      f"seconds' band and the {T0_BAND[0]:g}-{T0_BAND[1]:g} C die band"),
        "the run's own leakage rise": term(p0["heat"]["j"], p0["heat"]["band"], k_leak_w_per_c=p0["heat"]["k_leak_w_per_c"],
                                           die_rise_c=p0["heat"]["die_rise_c"]),
    }
    # the given-seconds formula's constants (E194.md 5.2): J over idle (t_k) = const + e_awake v2 x awake(t_k)
    e_aw = LV._c(F, "awake_pj_per_hart_cycle") * 1e-12 * v2
    formula = {"j_over_idle_without_awake": p0["j_over_idle"] - T["awake"]["j"], "awake_j_per_hart_cycle": e_aw,
               "hart_cycles_per_second": N_MIN * f_hz, "hart0_busy_cycles": hart0_busy,
               "hart1_busy_cycles": hart1_busy,
               "linear_above_t_k_s": max(hart0_busy, hart1_busy) / (N_MIN * f_hz),
               "linear_const_j": p0["j_over_idle"] - T["awake"]["j"] - e_aw * (hart0_busy + hart1_busy),
               "linear_slope_j_per_s": e_aw * 2 * N_MIN * f_hz}
    rec = {
        "seconds": {"point": t, "band": t_band,
                    "point_how": f"the host's --dry model_s (the fitted cycle model, its cycles at 600 MHz) at "
                                 f"{round(f_hz / 1e6)} MHz: model_s x 600/{round(f_hz / 1e6)}",
                    "fast_how": "model_s x 0.90 at the same clock: the cycle model's held-out misses are 5.0% and 7.5% "
                                "(workloads/sparseparity/README.md), and on E59 it never read long by more than 0.12% (L2)",
                    "slow_how": f"est_s, the host's own x1.3 margin (covers E59's worst short reading, L1's -16.6%), at "
                                f"{round(f_hz / 1e6)} MHz",
                    "model_s_at_600_mhz": t600, "est_s_at_600_mhz": plan["est_s"], "q166_band": None},
        "j_over_idle": prim_sum["j_over_idle"], "j_over_idle_band": prim_sum["j_over_idle_band"],
        "j_over_idle_band_at_point": prim_sum["j_over_idle_band_at_point"],
        "w_over_idle": prim_sum["w_over_idle"], "j_total": prim_sum["j_total"], "j_total_band": prim_sum["j_total_band"],
        "j_over_idle_band_at_band_ends": prim_sum["j_over_idle_band_at_band_ends"],
        "terms": terms, "primary": base, "given_formula": formula,
        "arms": {"v2.1": dict(v21, summary=sum21, overlap_cycles_per_op=over, loop_cycles_per_op=loop_int8,
                              scp_load_cycles_per_op=scp_cyc),
                 "v2c": dict(v2c, summary=sumc)},
        "counts": {"ops": ops, "output_tiles": outs, "row_tiles": rows, "S": S, "U_planner": U,
                   "hart0_busy_cycles": hart0_busy, "hart1_busy_cycles": hart1_busy,
                   "counted_work_instructions_per_solve": r["counter_slices"]["per_solve_work_instructions"],
                   "counted_work_hart0": r["counter_slices"]["per_solve_work_hart0"],
                   "counted_work_hart1": r["counter_slices"]["per_solve_work_hart1"],
                   "counted_by_class": r["counter_slices"]["per_solve_work_by_class"]},
        "plan": plan, "instance": r["instance"], "config_args": r["config"],
    }
    return rec


def make_configs(res, calls, le, cat, orig_pc, LV, F, cc, ck, f_hz):
    plain = [k for k in le.CARD]
    configs = {}
    for i, key in enumerate(plain):
        r = res["programs"][key]
        configs[key] = plain_record(key, r, calls[i], le, cat, orig_pc, LV, F, f_hz=f_hz)
        configs[key]["config_args"] = r["config"]["args"]
        configs[key]["arms"] = {"v2.1": {"same_as": "primary", "why": "no tensor op in this program"},
                                "v2c": {"same_as": "primary", "why": "its hart work is already the counter's "
                                                                    "counts at the catalogue's rows"}}
    configs["sparse-parity"] = spp_record(res["programs"]["sparse-parity"], le, LV, F, cc, ck, f_hz=f_hz)
    return {k: configs[k] for k in CONFIG_ORDER}


def readings(configs, at600, F, LV):
    """The REPORTED readings of E194.md sections 5 and 6, frozen here before any datum and never scored: the forecast at
    600 MHz on aifoundry2 (the clock's effect), E189's and E191's frozen forecasts (comparison only), the clock's base at
    800 MHz by E136's relation (an outside figure the frozen ledger has no term for) and the governor's climb."""
    e189 = json.load(open(os.path.join(REPO, "tools/claims-v3/e189/forecast-e189.json")))["configs"]
    e191 = json.load(open(os.path.join(REPO, "tools/claims-v3/e191/forecast-e191.json")))["configs"]
    rel = json.load(open(os.path.join(REPO, "tools/claims-v3/e136/predictions-e136.json")))["relation"]["B"]
    dB = rel["800"] - rel["600"]
    v2 = LV.v2_factor(F, CARD, F_HZ / 1e6)
    out = {"label": "REPORTED readings, frozen before any E194 datum, never scored and never used by given() "
                    "(E194.md sections 5 and 6)",
           "v2_800": v2,
           "e136_base_w": {"600": rel["600"], "800": rel["800"], "difference_800_minus_600": dB,
                           "source": "tools/claims-v3/e136/predictions-e136.json relation.B (E101's relation through "
                                     "E119, aifoundry2): the card's busy base at each clock; the frozen ledger has no "
                                     "term for it ('v2 has no validated 800 MHz static term', loads_ledger_v2.py)"},
           "configs": {}}
    for k in CONFIG_ORDER:
        c, a6 = configs[k], at600[k]
        t = c["seconds"]["point"]
        scaled = c["terms"]["tensor ops"]["j"] + c["terms"]["instructions by class"]["j"] + \
            c["terms"]["awake, not issuing"]["j"]
        if k.startswith("copy"):
            share = CLIMB_MEDIAN_S / (K_E189[k] * t)            # a byte-bound burst runs at its byte rates
            dt_w = 0.0
        else:
            share = CLIMB_MEDIAN_S * (F_REF / F_HZ) / (K_E189[k] * t)
            dt_w = CLIMB_MEDIAN_S * (1.0 - F_REF / F_HZ) / K_E189[k]
        out["configs"][k] = {
            "at_600_mhz": {"j_over_idle": a6["j_over_idle"], "j_total": a6["j_total"], "seconds": a6["seconds"]["point"],
                           "how": "this file's forecast with f = 600 MHz (v2 = 1, seconds at 600 MHz), aifoundry2's prices"},
            "e189_frozen_aifoundry3_600": {"j_over_idle": e189[k]["j_over_idle"], "j_total": e189[k]["j_total"],
                                           "seconds": e189[k]["seconds"]["point"]},
            "e191_frozen_card1_600": {"j_over_idle": e191[k]["j_over_idle"], "j_total": e191[k]["j_total"],
                                      "seconds": e191[k]["seconds"]["point"]},
            "with_e136_base": {"j_over_idle": c["j_over_idle"] + dB * t, "j_total": c["j_total"] + dB * t,
                               "how": "the forecast plus E136's base difference times the forecast seconds: what J over "
                                      "idle reads if the card draws that base at 800 MHz and no part of it is inside "
                                      "the v2-scaled prices"},
            "climb": {"share_of_the_burst_work_at_600_mhz": share,
                      "j_over_idle_change": -share * (1.0 - 1.0 / v2) * scaled / c["j_over_idle"],
                      "t_w_added_s": dt_w,
                      "how": f"the governor's median climb ({CLIMB_MEDIAN_S} s at 600 MHz, E190 arm A) at the start of a "
                             "burst of E189's K launches at the forecast seconds: the share of the burst's work done at "
                             "600 MHz, the change it makes to J over idle a launch (those instructions without v2) and "
                             "the wall seconds it adds a launch"}}
    return out


def build(args, card=None, f_hz=None):
    """card / f_hz: None for E194's own (aifoundry2, 800 MHz). The round trip of E194.md section 15 calls it with
    E191's card and 600 MHz and compares the configurations with E191's frozen file."""
    global CARD, CK
    if card is not None:
        CARD, CK = card
    f_hz = F_HZ if f_hz is None else f_hz
    nfiles = check_pins()
    sys.path.insert(0, os.path.join(REPO, "tools", "ledger"))
    le = load_module("ledger_estimate_e194", "workloads/ledger/ledger_estimate.py")
    import ledger_v2 as LV  # noqa: E402  (pinned)
    cc = load_module("ledger_card_compare_e194", "tools/counter/card_compare_sparseparity.py")
    ck = cc.load_counter()
    F = LV.load_frozen(os.path.join(REPO, "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"))
    cat = le.Catalogue(os.path.join(REPO, le.CAT_REL), CARD)
    # the dated change: the sort at 1,800 sorts a launch
    for k in ("sort-sorted", "sort-shuffled"):
        le.CARD[k]["reps"] = SORT_REPS
        le.CARD[k]["args"] = le.CARD[k]["args"].replace("--reps 1500", f"--reps {SORT_REPS}")
    calls = []
    orig_pc = le.price_counts

    def rec_pc(cat_, counts, data="random", inplace_hi=True):
        calls.append(dict(counts))
        return orig_pc(cat_, counts, data, inplace_hi)
    le.price_counts = rec_pc
    cat_cls = le.Catalogue

    class CatCard(cat_cls):                     # the card switched inside estimate(): its Catalogue(path) is aifoundry2's
        def __init__(self, path, card=CARD):
            super().__init__(path, card)
    le.Catalogue = CatCard
    ea = argparse.Namespace(runs=os.path.join(REPO, PROGS, "runs"), repo=REPO,
                            dis=os.path.join(REPO, PROGS, "kernel", "ledger.dis.gz"), t0=T0_FORECAST,
                            spp_dry=os.path.join(REPO, PROGS, "runs", "p2-dry", "new-dry.json"),
                            spp_slices=",".join(os.path.join(REPO, d) for d in SPP_SLICES), spp_sites=None, spp_dis=None,
                            out=None)
    res = le.estimate(ea)
    le.Catalogue = cat_cls
    le.price_counts = orig_pc
    plain = [k for k in le.CARD]
    if len(calls) != len(plain):
        sys.exit(f"refused: estimate() priced {len(calls)} count sets, expected {len(plain)}")
    # the card switched in the copy's one card-keyed byte price: ledger_estimate.py reads the DRAM-read price on random
    # bytes at frozen-v2.json mem_paths.dram_load.random_pj['a3']; aifoundry2's is its CK entry (its literal bands and the
    # write-back path's literal prices carry no card and stay)
    rr = res["programs"]["copy-random"]
    k_rd = [kk for kk in rr["terms"] if kk.startswith("DRAM reads")][0]
    p_a3, p_cd = F["mem_paths"]["dram_load"]["random_pj"]["a3"], F["mem_paths"]["dram_load"]["random_pj"][CK]
    if rr["terms"][k_rd]["pj_per_byte"][0] != p_a3:
        sys.exit("refused: the copy's DRAM-read price is not the 'a3' lookup this switch replaces")
    rr["terms"][k_rd]["pj_per_byte"] = (p_cd,) + tuple(rr["terms"][k_rd]["pj_per_byte"][1:])
    rr["terms"][k_rd]["j"] = rr["terms"][k_rd]["bytes"] * p_cd * 1e-12
    rr["j_over_idle"] = sum(v["j"] for v in rr["terms"].values())
    rr["j_over_idle_band"] = [sum(v["band"][0] for v in rr["terms"].values()),
                              sum(v["band"][1] for v in rr["terms"].values())]
    # rest_and_heat_card() at aifoundry3 is ledger_estimate.py's rest_and_heat(), exactly (a check of the copy)
    for k in plain:
        r = res["programs"][k]
        a_ = le.rest_and_heat(LV, F, r["seconds"]["point"], r["seconds"]["band"], r["j_over_idle"], r["j_over_idle_band"],
                              T0_FORECAST, T0_BAND)
        b_ = rest_and_heat_card(LV, F, r["seconds"]["point"], r["seconds"]["band"], r["j_over_idle"],
                                r["j_over_idle_band"], T0_FORECAST, T0_BAND, card="aifoundry3")
        if a_ != b_:
            sys.exit(f"refused: rest_and_heat_card() at aifoundry3 differs from ledger_estimate.rest_and_heat() for {k}")
    v2 = LV.v2_factor(F, CARD, f_hz / 1e6)
    out = {"schema": "e194-forecast/1", "experiment": "E194",
           "what": "the blind day on a third card, under its own governor: four programs' (six configurations') joules a "
                   "launch on aifoundry2's card 0 at the governor's 800 MHz, forecast before the card by the ledger v2 as "
                   "frozen; REGISTERED, frozen before any E194 datum; not blind to E189's measured results",
           "card": "aifoundry2 card 0 (the ledger's card 'aifoundry2'), its own governor as found, nothing set",
           "f_mhz": round(f_hz / 1e6),
           "clock": {"forecast_mhz": round(f_hz / 1e6), "v2": v2, "frozen_rates_at_mhz": round(F_REF / 1e6),
                     "what": "the governor's top point under load, as E190's arm A read it on this card (Fri 13 Nov "
                             "2026): every price the ledger's form scales by v2 = (V800/V600)^2 is scaled (tensor, "
                             "instruction classes, awake); byte paths are not; seconds made of cycles are at 800 MHz; "
                             "byte and line rates are literals with no minion clock; the card at rest is the idle law "
                             "(the governor's 600 MHz idle); no term for the clock's own base at 800 MHz (the frozen "
                             "ledger has none; E194.md 3.1)"},
           "die_start_forecast_c": T0_FORECAST, "die_start_band_c": list(T0_BAND),
           "card_switch": {"from": "aifoundry1-c1 (key c1), E191's; E191's own was E189's aifoundry3 (key a3) switched",
                           "to": f"{CARD} (key {CK})",
                           "what": "every card-keyed input the frozen predictor reads is aifoundry2's: the idle law, leak "
                                   "slope and rest band; the ledger v2's prices for sparse parity and its arms; the "
                                   "catalogue's aifoundry2 column (means and issue rates) for the plain programs; the "
                                   "copy's DRAM-read price on random bytes; nothing else changed but the clock "
                                   "(E194.md sections 3 and 3.1)",
                           "carried_from_aifoundry3": {"kinds.int8.pm1": "no aifoundry2 entry in frozen-v2.json: "
                                                                          "aifoundry3's D and band, unchanged"},
                           "placeholder_read_as_keyed": {"zeros_anchor.int8.a2": "frozen-v2.json's own aifoundry2 entry, "
                                                         "labelled 'placeholder': aifoundry3's E78 Z and band at the rate "
                                                         "of a 318-cycle loop (1,024 x 600 MHz / 318); it does not cancel "
                                                         "in sparse parity's tensor term or in v2.1's loop rate"},
                           "card_less_literals_kept": ["ledger_estimate.py's DRAM-read bands and zeros price, the "
                                                       "write-back path's prices and bands, the L2 price and band",
                                                       "the band rules' literals (H1_OVER_H2, L2_LINES_PER_S, SPP_FAST)"]},
           "predictor": {"ledger_v2": "commit 06d60fa2; frozen-v2.json sha256 " + PINS[
               "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"],
               "ledger_estimate": "workloads/ledger/ledger_estimate.py at 46a16bd0, sha256 " + PINS[
                   "workloads/ledger/ledger_estimate.py"],
               "pins": PINS, "reported_pins": REPORTED_PINS, "progs_files_checked": nfiles,
               "interpreter": INTERPRETER},
           "dated_change": {"what": f"the sort at {SORT_REPS} sorts a launch (Q166 proposed 1,500)",
                            "when": "Thu 12 Nov 2026, reg-e189, before any E189 datum",
                            "why": "so the two-sided seconds band's fast end stays at 0.5 s or more (critic-q166's "
                                   "blind-day design 1(d); verify-progs fault 1)",
                            "how": "ledger_estimate.py's own CARD entries given reps 1800 before estimate() runs; the "
                                   "counts per sort are the simulator's exact difference of two runs, scaled by "
                                   "arithmetic (the label 'scaled')"},
           "configs": make_configs(res, calls, le, cat, orig_pc, LV, F, cc, ck, f_hz)}
    # the given-seconds function reproduces each forecast's own point (a self-check of given())
    for k, rec in out["configs"].items():
        t = rec["seconds"]["point"]
        g = given(rec, t, t, T0_FORECAST, F, LV)
        for a, b in ((g["j_over_idle"], rec["j_over_idle"]), (g["j_total"], rec["j_total"])):
            if abs(a - b) > 1e-9 * abs(b):
                sys.exit(f"refused: given() at the point does not reproduce {k}'s forecast ({a} vs {b})")
    # per-unit figures (reported, not scored)
    units = {"copy-zeros": ("GiB copied", 14.0), "copy-random": ("GiB copied", 14.0),
             "sha256": ("64 B block (one compression)", 2048.0 * (800 * 32 + 1)),
             "sort-sorted": ("sort of 512 keys", 2048.0 * SORT_REPS), "sort-shuffled": ("sort of 512 keys", 2048.0 * SORT_REPS),
             "sparse-parity": ("solve", 1.0)}
    for k, (u, n) in units.items():
        rec = out["configs"][k]
        rec["per_unit"] = {"unit": u, "units_a_launch": n, "j_over_idle": rec["j_over_idle"] / n,
                           "j_total": rec["j_total"] / n}
    # the counters arm's expectations (REPORTED only; E189.md section 7; counts carry no card and no clock)
    exp = {}
    for k in CONFIG_ORDER[:-1]:
        c = out["configs"][k]["counts"]
        exp[k] = {"retired_instructions_per_participant": c["per_participant_instructions"],
                  "label": "counted (simulator, 64 participants) and scaled; the firmware's work outside the kernel "
                           "(about 1,560 instructions a hart) is not in it"}
    exp["copy-zeros"]["dram_lines_read"] = exp["copy-random"]["dram_lines_read"] = (1 << 30) * 14 / 64.0
    exp["copy-zeros"]["dram_lines_written"] = exp["copy-random"]["dram_lines_written"] = (1 << 30) * 14 / 64.0
    sp = out["configs"]["sparse-parity"]["counts"]
    exp["sparse-parity"] = {"work_instructions_hart0_per_minion": sp["counted_work_hart0"] / N_MIN,
                            "work_instructions_hart1_per_minion": sp["counted_work_hart1"] / N_MIN,
                            "label": "counted on three slices and scaled by least squares (spin loops left out, so the "
                                     "card's retired count reads higher by its spins)"}
    out["counters_arm_expectations"] = exp
    if card is None and f_hz == F_HZ:
        at600 = make_configs(res, calls, le, cat, orig_pc, LV, F, cc, ck, F_REF)
        out["readings_reported"] = readings(out["configs"], at600, F, LV)
    return r6(out)


def text(out):
    f = out["f_mhz"]
    L = [f"E194 frozen forecasts (REGISTERED; per launch on aifoundry2 card 0 at {f} MHz, its governor's top point; "
         f"forecast die {out['die_start_forecast_c']:g} C, band {out['die_start_band_c'][0]:g}-"
         f"{out['die_start_band_c'][1]:g})",
         "", f"{'configuration':15s} {'seconds point [two-sided band]':34s} {'J over idle [band]':24s} "
             f"{'J with the card at rest [band]':30s}"]
    for k, r in out["configs"].items():
        s = r["seconds"]
        L.append(f"{k:15s} {s['point']:.4f} [{s['band'][0]:.4f}, {s['band'][1]:.4f}]{'':9s} "
                 f"{r['j_over_idle']:6.3f} [{r['j_over_idle_band'][0]:.3f}, {r['j_over_idle_band'][1]:.3f}]   "
                 f"{r['j_total']:7.3f} [{r['j_total_band'][0]:.3f}, {r['j_total_band'][1]:.3f}]")
    L.append("")
    L.append("split by ledger term (J a launch, point [band])")
    for k, r in out["configs"].items():
        L.append(f"  {k}:")
        for tn, tv in r["terms"].items():
            L.append(f"    {tn:28s} {tv['j']:.4f} [{tv['band'][0]:.4f}, {tv['band'][1]:.4f}]")
    sp = out["configs"]["sparse-parity"]["arms"]
    L.append("")
    L.append("sparse parity's registered arms (reported; the day's verdict is the primary's)")
    for a in ("v2.1", "v2c"):
        s = sp[a]["summary"]
        L.append(f"  {a:5s} J over idle {s['j_over_idle']:.3f} [{s['j_over_idle_band'][0]:.3f}, "
                 f"{s['j_over_idle_band'][1]:.3f}]; J with the card at rest {s['j_total']:.3f} "
                 f"[{s['j_total_band'][0]:.3f}, {s['j_total_band'][1]:.3f}]")
    L.append("")
    L.append("per unit (reported)")
    for k, r in out["configs"].items():
        u = r["per_unit"]
        L.append(f"  {k:15s} {u['j_over_idle']:.6g} J over idle a {u['unit']}; {u['j_total']:.6g} J with the card at rest")
    rd = out.get("readings_reported")
    if rd:
        L.append("")
        L.append(f"REPORTED readings, never scored (v2(800) = {rd['v2_800']:.6g}; E136's base difference "
                 f"{rd['e136_base_w']['difference_800_minus_600']:.4f} W)")
        L.append(f"  {'configuration':15s} {'at 600 MHz: J over / at rest':30s} {'E189 a3: over / rest':22s} "
                 f"{'E191 c1: over / rest':22s} {'+ E136 base: over':18s} {'climb: share, dJ':18s}")
        for k, c in rd["configs"].items():
            a6, e9, e1, wb, cl = c["at_600_mhz"], c["e189_frozen_aifoundry3_600"], c["e191_frozen_card1_600"], \
                c["with_e136_base"], c["climb"]
            L.append(f"  {k:15s} {a6['j_over_idle']:7.3f} / {a6['j_total']:7.3f}{'':12s} {e9['j_over_idle']:6.3f} / "
                     f"{e9['j_total']:7.3f}{'':4s} {e1['j_over_idle']:6.3f} / {e1['j_total']:7.3f}{'':4s} "
                     f"{wb['j_over_idle']:7.3f}{'':11s} {cl['share_of_the_burst_work_at_600_mhz']:.3f}, "
                     f"{100 * cl['j_over_idle_change']:+.2f}%")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=HERE, help="where to write forecast-e194.json and .txt (default: this folder)")
    ap.add_argument("--check", action="store_true", help="recompute and compare with the committed files byte for byte")
    a = ap.parse_args(argv)
    out = build(a)
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    tx = text(out)
    if a.check:
        ok = True
        for name, body in (("forecast-e194.json", js), ("forecast-e194.txt", tx)):
            have = open(os.path.join(HERE, name)).read()
            same = have == body
            ok &= same
            print(f"{name}: {'identical' if same else 'DIFFERS'} (sha256 {hashlib.sha256(body.encode()).hexdigest()})")
        print("FORECAST CHECK " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    with open(os.path.join(a.out, "forecast-e194.json"), "w") as f:
        f.write(js)
    with open(os.path.join(a.out, "forecast-e194.txt"), "w") as f:
        f.write(tx)
    print(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
