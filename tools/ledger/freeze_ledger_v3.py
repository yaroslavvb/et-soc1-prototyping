#!/usr/bin/env python3
"""Freeze ledger v3: write tools/ledger/frozen-v3.json (every constant with its committed source, label and band) and
tools/ledger/frozen-v3.json.sha256 (the freeze line).

    /usr/bin/python3 -I -B tools/ledger/freeze_ledger_v3.py --frozen-pst "Mon 16 Nov 2026 HH:MM PST"   # write
    /usr/bin/python3 -I -B tools/ledger/freeze_ledger_v3.py --check     # recompute; compare byte for byte with the files

Sources, all committed and read here (none is typed in, except the v2 literals, which are checked against the pinned
v2 source text they come from):
  * the energy catalogue (docs/reports/data/2026-09-23-energy-manual/catalogue.json): the loop's delta (add's issue
    rate), the a priori taken-branch cost (beq_taken's), the DRAM copy's rows per card (tload/dram, st_stream/dram);
  * E48 in the energy manual (manual.json > gs, 26 Sep): the line prices e_r, e_w per card and the L2 line cycles;
  * frozen-v2.json: E23's stall power (v2's own awake constant, per hart-cycle, x 1,024 x 600 MHz);
  * E193's committed reduction (docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3/x04-e193-A.json):
    the stall price tr_tk_stall2 and the spin price spin2 (the awake band's ends and a reading beside it);
  * the blind days' passes (tools/ledger/measured_ledger_v3.py: E189, E191's second session) and the counts v2 priced
    (tools/ledger/programs_ledger_v3.py): c_br and R_dram, FITTED (post hoc); the measured starting dice and launch
    overheads (post hoc);
  * E136's busy-base relation (tools/claims-v3/e136/predictions-e136.json relation.B) and E190's climb
    (tools/claims-v3/e194/desk/climb-e190.txt), for rule 7;
  * the level sizes (docs/reports/data/2026-09-28-memory-levels/research/facts-l1.json, facts-l2.json).
It also pins, by sha256, what a new configuration's counts and lines are computed from at forecast time (the kernel's
committed disassembly, workloads/ledger/ledger_desk.py's mirror of the host's inputs) and every measured day it reads.

Re-frozen before the land (Q193 fix-ledger3) for the adversarial verify's findings (Q193 verify-ledger3): rule 1's a-set
is now the fitted programs' one-cycle mnemonics (finding 1: the first freeze put mul and csrr in it, at a = 2.0), c_br is
fitted with those two at their own rows, and the parents list gains the four inputs finding 5 names. The first freeze
(sha256 bd6e71ca..., Mon 16 Nov 2026 03:40 PST) was never landed; `supersedes` in the written file records it.
Desk only. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import ledger_v3 as V3  # noqa: E402
import measured_ledger_v3 as M  # noqa: E402
import programs_ledger_v3 as PR  # noqa: E402

OUT_JSON = os.path.join(HERE, "frozen-v3.json")
OUT_SHA = os.path.join(HERE, "frozen-v3.json.sha256")
CAT_REL = V3.CAT_REL
MAN_REL = "docs/reports/data/2026-09-23-energy-manual/manual.json"
E193_REL = "docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3/x04-e193-A.json"
E136_REL = "tools/claims-v3/e136/predictions-e136.json"
CLIMB_REL = "tools/claims-v3/e194/desk/climb-e190.txt"
FACTS_L1 = "docs/reports/data/2026-09-28-memory-levels/research/facts-l1.json"
FACTS_L2 = "docs/reports/data/2026-09-28-memory-levels/research/facts-l2.json"
EST_REL = "workloads/ledger/ledger_estimate.py"
F189_REL = "tools/claims-v3/e189/forecast_e189.py"
DIS_REL = "docs/reports/data/2026-11-12-q166-progs/kernel/ledger.dis.gz"     # ledger_interp.py's and l1_model.py's kernel
DESK_REL = "workloads/ledger/ledger_desk.py"                                 # ledger_interp.py's host inputs
A_SLOT = 2.0                        # rule 1's a, hart-cycles an instruction with both harts issuing (a priori)
ONE_CYCLE_TOL = 0.5                 # a one-cycle row: its 1/rate less delta within half a hart-cycle of a
FIRST_FREEZE = {"sha256": "bd6e71cae962972437d5b2c7827f4dd9a43b613a89669e48afeba60c30ef2304",
                "frozen_pst": "Mon 16 Nov 2026 03:40 PST",
                "why": "re-frozen before the land, before any E201 datum, for the adversarial verify's findings (Q193 "
                       "verify-ledger3): 1, rule 1's a-set held mul and csrr (now at their own rows, c_br refitted); 4, "
                       "ledger_v3.py's citation; 5, the parents list; 7, the DRAM copy's byte-row bands at another clock "
                       "(ledger_v3.py); the first freeze was never landed"}
CARDS = ("aifoundry3", "aifoundry1-c1", "aifoundry2")
SCALAR = ("sha256", "sort-sorted", "sort-shuffled")
COPIES = ("copy-zeros", "copy-random")
FIT_DAYS = ("E189", "E191s2")
E48 = {"flw4k": "gs/E/flw/dram-4K/rand/random/h2/mff/n1024", "flw512": "gs/E/flw/dram-512B/rand/random/h2/mff/n1024",
       "fsw4k": "gs/E/fsw/dram-4K/rand/random/h2/mff/n1024", "fsw512": "gs/E/fsw/dram-512B/rand/random/h2/mff/n1024",
       "flw256k": "gs/E/flw/dram-256K/rand/random/h2/mff/n1024"}
# the v2 literals the rules-off path needs, each with the exact text it is checked against in the pinned v2 source
V2_LITERALS = {
    "l2_row_pj_b": ([2.83, 1.42, 4.99], EST_REL, "l2_pj = (2.83, 1.42, 4.99)"),
    "wb_zeros": ([247.4, 202.4, 288.9], EST_REL, "wr = (247.4, 202.4, 288.9)"),
    "wb_random": ([325.8, 317.4, 373.3], EST_REL, "wr = (325.8, 317.4, 373.3)"),
    "rd_zeros_band": ([86.2, 114.6], EST_REL, 'rd = (mp["dram_load"]["zeros_pj"], 86.2, 114.6)'),
    "rd_random_band": ([105.6, 145.4], EST_REL, 'rd = (mp["dram_load"]["random_pj"]["a3"], 105.6, 145.4)'),
    "store_stream_gb_s": (27.0, EST_REL, "bw_st = 27e9"),
    "sha256_thrash_lines_a_compression": (8, EST_REL, "thrash = 8 * units_card * P"),
    "sort_high_factor": (1.5, EST_REL, 'nb * l2_pj[2] * 1.5'),
    "h1_over_h2_add": ([0.581, 0.3727], F189_REL, 'H1_OVER_H2 = ("add", 0.581, 0.3727)'),
    "l2_lines_per_s": (27.4e9, F189_REL, "L2_LINES_PER_S = 27.4e9"),
    "forecast_die_c": (55.0, F189_REL, "T0_FORECAST, T0_BAND = 55.0, (52.0, 60.0)"),
    "die_band_c": ([52.0, 60.0], F189_REL, "T0_FORECAST, T0_BAND = 55.0, (52.0, 60.0)"),
}


def rel(p):
    return os.path.join(REPO, p)


def cat_mean(CAT, card, cfg, key):
    return st.mean(b[key] for b in CAT["bursts"][card] if b["cfg"] == cfg)


def e48(MAN, card, k, key="pj_per_element"):
    return MAN["gs"]["configs"][E48[k]][key]["per_card"][card]["mean"]


def fit_cbr(rows, a=A_SLOT, weight="relative"):
    """c_br by least squares over rows (N, B, T, n_o, O): T - a (N - B - n_o) - O = c_br B, where n_o counts the
    instructions outside the a-set and O is their hart-cycles at their own catalogue rows less delta."""
    num = math.fsum((1.0 / T ** 2 if weight == "relative" else 1.0) * (T - a * (N - B - n_o) - O) * B
                    for N, B, T, n_o, O in rows)
    den = math.fsum((1.0 / T ** 2 if weight == "relative" else 1.0) * B * B for N, B, T, n_o, O in rows)
    return num / den


def fit_free(rows):
    """a and c by relative least squares (the two-parameter reading; not used)."""
    w = [1.0 / T ** 2 for N, B, T, n_o, O in rows]
    x1 = [N - B - n_o for N, B, T, n_o, O in rows]
    x2 = [B for N, B, T, n_o, O in rows]
    y = [T - O for N, B, T, n_o, O in rows]
    s11 = math.fsum(wi * a * a for wi, a in zip(w, x1))
    s12 = math.fsum(wi * a * b for wi, a, b in zip(w, x1, x2))
    s22 = math.fsum(wi * b * b for wi, b in zip(w, x2))
    t1 = math.fsum(wi * a * yi for wi, a, yi in zip(w, x1, y))
    t2 = math.fsum(wi * b * yi for wi, b, yi in zip(w, x2, y))
    det = s11 * s22 - s12 * s12
    return (t1 * s22 - t2 * s12) / det, (s11 * t2 - s12 * t1) / det


def build(frozen_pst):
    V3.check_pins()
    CAT = json.load(open(rel(CAT_REL)))
    MAN = json.load(open(rel(MAN_REL)))
    F2 = json.load(open(rel(V3.FROZEN_V2_REL)))
    meas = M.read_all()
    progs = PR.blind_day_programs("aifoundry3")
    # ---- the v2 literals, checked against the pinned source text
    lit = {}
    for k, (v, path, text) in V2_LITERALS.items():
        if text not in open(rel(path)).read():
            raise SystemExit(f"freeze_ledger_v3: the literal {k} ({text!r}) is not in {path}")
        lit[k] = v
    # ---- rule 1: a, delta, the a-set, c_br
    r_add = cat_mean(CAT, "aifoundry3", "add/random/h2", "ops_per_cycle_per_hart")
    r_add_h1 = cat_mean(CAT, "aifoundry3", "add/random/h1", "ops_per_cycle_per_hart")
    r_beq = cat_mean(CAT, "aifoundry3", "beq_taken/random/h2", "ops_per_cycle_per_hart")
    delta = 1.0 / r_add - A_SLOT
    c_prior = 1.0 / r_beq - delta
    # the a-set: the programs' mnemonics whose own catalogue row (aifoundry3's, the card delta is read on) is a one-cycle
    # row, i.e. its 1/rate less delta within ONE_CYCLE_TOL of a; every other mnemonic issues at its own row (mul, csrr)
    lv_, le_, F2_ = V3.mods()
    mnem = sorted(set(m for p in progs.values() for m in p["counts"] if not m.startswith("@")))
    row_x = {}
    for m in mnem:
        pat = le_.ALIAS.get(m, m)
        if not any(b["cfg"] == f"{pat}/random/h2" for b in CAT["bursts"]["aifoundry3"]):
            raise SystemExit(f"freeze_ledger_v3: no catalogue row for {m} (as {pat})")
        row_x[m] = {"row": pat,
                    "hart_cycles": 1.0 / cat_mean(CAT, "aifoundry3", f"{pat}/random/h2", "ops_per_cycle_per_hart") - delta}
    aset = [m for m in mnem if abs(row_x[m]["hart_cycles"] - A_SLOT) < ONE_CYCLE_TOL]
    others = [m for m in mnem if m not in aset]

    def other_hart_cycles(card, counts):
        """(n_o, O): the instructions outside the a-set and their hart-cycles at the card's own rows less delta,
        exactly as ledger_v3.t_hart_v3() prices them."""
        cat = V3.catalogue(card)
        n_o = math.fsum(counts.get(m, 0.0) for m in others)
        O = math.fsum(counts.get(m, 0.0) * (1.0 / cat.rate(le_.ALIAS.get(m, m), "random") - delta) for m in others)
        return n_o, O
    rows = {}
    for d in FIT_DAYS:
        card = meas[d]["info"]["card"]
        for cfg in SCALAR:
            c = progs[cfg]["counts"]
            N = math.fsum(c.values())
            B = c.get("@taken", 0.0) + c.get("@jump", 0.0)
            n_o, O = other_hart_cycles(card, c)
            rows[(d, cfg)] = (N, B, meas[d]["configs"][cfg]["mean"]["cycles_max"], n_o, O)
    allrows = list(rows.values())
    c_br = fit_cbr(allrows)
    per_card = {d: fit_cbr([rows[(d, c)] for c in SCALAR]) for d in FIT_DAYS}
    loo = {cfg: fit_cbr([rows[(d, c)] for d in FIT_DAYS for c in SCALAR if c != cfg]) for cfg in SCALAR}
    c_abs = fit_cbr(allrows, weight="absolute")
    a_free, c_free = fit_free(allrows)
    # ---- rule 2: R_dram, the L2 line cycles
    NB = progs["copy-zeros"]["copy"]["bytes"]
    rd = {}
    for d in FIT_DAYS:
        card = meas[d]["info"]["card"]
        rd[card] = st.mean(3.0 * NB / meas[d]["configs"][c]["mean"]["t_k"] for c in COPIES)
    rd_default = st.mean(rd.values())
    cyc = {}
    for card in CARDS:
        cyc[card] = (e48(MAN, card, "flw4k", "cpi_minion"), e48(MAN, card, "fsw4k", "cpi_minion"))
    if len(set(cyc.values())) != 1:
        raise SystemExit(f"freeze_ledger_v3: E48's line cycles differ between cards: {cyc}")
    fill, alloc = cyc["aifoundry3"]
    # ---- rule 3: line prices
    prices = {}
    for card in CARDS:
        e_r = e48(MAN, card, "flw4k") - e48(MAN, card, "flw512")
        e_w = e48(MAN, card, "fsw4k") - e48(MAN, card, "fsw512")
        prices[card] = {"e_r": e_r, "e_w": e_w, "dram_line_pj_b": e48(MAN, card, "flw256k") / 64.0}
    prices_band = {"e_r": [min(v["e_r"] for v in prices.values()), max(v["e_r"] for v in prices.values())],
               "e_w": [min(v["e_w"] for v in prices.values()), max(v["e_w"] for v in prices.values())]}
    # ---- rule 4: the DRAM copy's rows, P_stall and its band
    rows4 = {}
    for card in CARDS:
        rows4[card] = {}
        for data in ("zeros", "random"):
            ct, cw = CAT["combined"][f"tload/dram/{data}"], CAT["combined"][f"st_stream/dram/{data}"]
            rows4[card][data] = {
                "p_tload_pj_b": cat_mean(CAT, card, f"tload/dram/{data}", "pj_per_byte"),
                "p_tload_band": [ct["lo"], ct["hi"]],
                "p_wb_pj_b": cat_mean(CAT, card, f"st_stream/dram/{data}", "pj_per_byte"),
                "p_wb_band": [cw["lo"], cw["hi"]],
                "b_wb_b_per_s": cat_mean(CAT, card, f"st_stream/dram/{data}", "bytes_per_s")}
    p_stall = F2["constants"]["awake_pj_per_hart_cycle"]["value"] * 1e-12 * 1024 * 600e6
    X4 = json.load(open(rel(E193_REL)))
    workers = X4["arms"]["spin2"]["workers"]
    stall2 = X4["trains"]["tr_tk_stall2"]["contrast_board_w"] * 1024.0 / workers
    spin2 = X4["arms"]["spin2"]["board_w"] * 1024.0 / workers
    # ---- rule 5: the dice and the launch overhead
    t0 = {d: [p["T0"] for c in meas[d]["configs"].values() for p in c["passes"]] for d in meas}
    ovh = {d: [p["t_w"] - p["t_k"] for cfg, c in meas[d]["configs"].items() if cfg != "sparse-parity" for p in c["passes"]]
           for d in FIT_DAYS}
    # ---- rule 7
    rel136 = json.load(open(rel(E136_REL)))["relation"]["B"]
    m = re.search(r"climb over (\d+) processes: min ([0-9.]+) s, median ([0-9.]+) s, max ([0-9.]+) s",
                  open(rel(CLIMB_REL)).read())
    if not m:
        raise SystemExit("freeze_ledger_v3: no climb line in " + CLIMB_REL)
    climb_n, climb_min, climb_med, climb_max = int(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    # ---- the levels
    fl1 = {f["id"]: f for f in json.load(open(rel(FACTS_L1)))}
    fl2 = {f["id"]: f for f in json.load(open(rel(FACTS_L2)))}
    l1b = fl1["l1.firmware-mode"]["value"]
    if l1b != 512 or "0.5 MB L2, 1 MB L3 per shire" not in fl2["l2.partition.default"]["statement"]:
        raise SystemExit("freeze_ledger_v3: the level facts are not as expected")
    parents = {p: V3.sha256_file(rel(p)) for p in sorted(set(
        list(V3.PINS) + [MAN_REL, E193_REL, E136_REL, CLIMB_REL, FACTS_L1, FACTS_L2,
                         "docs/reports/data/2026-11-12-q166-progs/SHA256SUMS", DIS_REL, DESK_REL,
                         "tools/counter/l1_model.py", "tools/counter/ledger_interp.py",
                         "tools/ledger/ledger_v3.py", "tools/ledger/measured_ledger_v3.py",
                         "tools/ledger/programs_ledger_v3.py", "tools/ledger/freeze_ledger_v3.py"] +
        [os.path.join(M.DATA, M.DAYS[d]["dir"], "SHA256SUMS") for d in M.DAYS]))}
    C = {}
    C["a_hart_cycles"] = {
        "value": A_SLOT, "unit": "hart-cycles an instruction, both harts of a minion issuing", "rule": "r1",
        "label": "a priori", "band": [2.0, 2.0],
        "source": "the catalogue's one-cycle rows (1/rate 2.66-2.70 hart-cycles with both harts) less their own "
                  "measuring loop (workloads/enercat/kernel/enercat.c: 64 ops, then an increment, counter reads and a taken "
                  "back edge): add's 1/rate %.4f less its loop's delta %.4f; a lone hart's add row reads 1/rate %.4f" % (
                      1.0 / r_add, delta, 1.0 / r_add_h1)}
    C["loop_delta_hart_cycles"] = {
        "value": delta, "unit": "hart-cycles an op", "rule": "r1", "label": "a priori",
        "source": f"{CAT_REL}: 1 / (add/random/h2's issue rate on aifoundry3, the mean of its bursts) - 2.0"}
    C["a_set_mnemonics"] = {
        "value": aset, "rule": "r1", "label": "a priori (the catalogue's one-cycle rows)",
        "source": "the mnemonics in the counts v2 priced for the blind day's five programs (programs_ledger_v3.py) whose "
                  f"own catalogue row ({CAT_REL}: random column, both harts, aifoundry3's mean, through "
                  "ledger_estimate.ALIAS) less the loop's delta is within %.1f hart-cycles of a = %.1f, i.e. one minion "
                  "cycle an instruction; these issue at a, taken branches and jumps at c_br, untaken branches at a, every "
                  "other mnemonic (here %s) at its own catalogue row's 1/rate less delta, as the step-5 design prices a "
                  "class outside the one-cycle rows" % (ONE_CYCLE_TOL, A_SLOT, " and ".join(others)),
        "widest_inside": max(([abs(row_x[m]["hart_cycles"] - A_SLOT), m] for m in aset)),
        "outside": {m: dict(row_x[m]) for m in others},
        "fixed_before_the_land": "Q193 verify-ledger3 finding 1: the first freeze took every mnemonic of the five "
                                 "programs, mul and csrr included, at a"}
    C["c_br_hart_cycles"] = {
        "value": c_br, "unit": "hart-cycles a taken branch or jump, both harts issuing", "rule": "r1",
        "label": "FITTED, POST HOC (E189 and E191's second session)", "band": [12.0, c_prior],
        "band_how": "the fast end 12.0: the leave-one-program-out low end less a margin (the design's); the slow end the "
                    "a priori value",
        "fit": {"how": "relative least squares of T - a (N - B - n_o) - O = c_br B over SHA-256 and both sorts on both "
                       "cards: T the slowest minion's cycles (the mean over a configuration's passes), N and B a "
                       "participant from the counts v2 priced, n_o the instructions outside the a-set and O their "
                       "hart-cycles at the day's card's own catalogue rows less delta (as ledger_v3.t_hart_v3 prices them)",
                "rows": {f"{d}/{c}": {"N": v[0], "B": v[1], "T": v[2], "n_o": v[3], "O": v[4]}
                         for (d, c), v in rows.items()},
                "per_card": per_card, "absolute_least_squares": c_abs, "leave_one_program_out": loo,
                "free_two_parameter_fit": {"a": a_free, "c_br": c_free, "note": "not used: it fails when SHA-256 is held out"}},
        "a_priori": {"value": c_prior, "how": "1 / (beq_taken/random/h2's issue rate on aifoundry3) less delta"}}
    C["r_dram_b_per_s"] = {
        "value": dict(rd, default=rd_default), "unit": "B/s of DRAM traffic at the slowest minion", "rule": "r2",
        "label": "FITTED, POST HOC (the blind days' copies; the default, for a card without its own, is their mean)",
        "fit": {"how": "the mean over the two copies of 3 B a byte copied x 1 GiB x 14 / the mean t_k (the slowest "
                       "minion's cycles / 600 MHz)",
                "a_priori_fast_end": {c: 2.0 * rows4[c]["random"]["b_wb_b_per_s"] for c in CARDS}},
        "note": "no minion clock in it (E194, post hoc, read the same rate at 800 MHz)"}
    C["r_dram_b_per_s_slow_factor"] = {
        "value": 1.10, "rule": "r2", "label": "a hand choice (the design's)", "source": "the DRAM copy's seconds band's "
        "slow end: +10%; its fast end the copy's traffic at twice the store stream's rate, no skew"}
    C["dram_traffic_bytes_per_byte_copied"] = {
        "value": 3, "rule": "r2", "label": "a priori (the L1's write-allocate)",
        "source": "a store through the L1 that misses fetches its line (facts-l1.json l1.write-policy): read + allocate + "
                  "write back"}
    C["l2_line_cycles_minion"] = {
        "value": {"fill": fill, "alloc": alloc}, "unit": "minion-cycles a line at the L2 (both harts of a minion)",
        "rule": "r2", "label": "a priori (E48, 26 Sep; the same on three cards)",
        "source": f"{MAN_REL} gs.configs[{E48['flw4k']}].cpi_minion and [{E48['fsw4k']}].cpi_minion",
        "note": "assumed clock-free (E48 measured them at 600 MHz only)"}
    C["line_prices_pj"] = {
        "value": prices, "band": prices_band, "unit": "pJ a line past the L1", "rule": "r3", "label": "a priori (E48, 26 Sep)",
        "source": f"{MAN_REL} gs.configs: e_r = flw dram-4K less flw dram-512B, e_w = fsw dram-4K less fsw dram-512B, each "
                  "card's own mean (pj_per_element; one line an element); band the three cards' range; dram_line_pj_b = flw "
                  "dram-256K / 64 B, the loads' L1-fill path from DRAM (the other candidate for the copy's read path)"}
    C["dram_copy_rows"] = {
        "value": rows4, "unit": "pJ a byte; B/s", "rule": "r4", "label": "a priori (the catalogue, 26 Sep)",
        "source": f"{CAT_REL}: bursts of tload/dram/<data> and st_stream/dram/<data> on each card (their mean); bands "
                  "the combined rows' lo and hi (every card)"}
    C["p_stall_w"] = {
        "value": p_stall, "band": [stall2, p_stall], "unit": "W over idle, 1,024 minions waiting, at 600 MHz",
        "rule": "r4", "label": "a priori",
        "source": f"E23 (1,024 minions stalled on a contended atomic, 1.19 W): {V3.FROZEN_V2_REL} "
                  "constants.awake_pj_per_hart_cycle x 1,024 x 600 MHz, v2's own awake price",
        "band_low_source": f"E193's stall price, {E193_REL} trains.tr_tk_stall2.contrast_board_w (%.4f W on %d workers) "
                           "x 1,024 / %d" % (X4["trains"]["tr_tk_stall2"]["contrast_board_w"], workers, workers),
        "why_e23_is_the_point": "it is the ledger v2's own awake price (no new number chosen after the blind days), and "
                                "it measures a stall on the memory side, as a copy's harts wait on DRAM; E193's stall2 "
                                "is a stalled pipeline with both harts idle (0.007 issue slots a cycle) and is the band's "
                                "low end; post hoc the blind days' copies read -5.2/-3.2% (aifoundry3) and +4.2/-3.1% "
                                "(card 1) at E23, -10.9/-7.4% and -1.1/-6.9% at E193's stall2",
        "beside_it": {"e193_spin2_w_per_1024": spin2, "note": "a spinning pair issues instructions: not a stall; "
                                                              "REPORTED only, outside the band"}}
    C["forecast_die_c"] = {
        "value": 50.0, "band": [48.0, 60.0], "unit": "C", "rule": "r5", "label": "POST HOC (an input condition, not a price)",
        "source": "the blind days' measured starting dice (energy.json die_c.before over every pass)",
        "measured": {d: {"mean": st.mean(v), "range": [min(v), max(v)]} for d, v in t0.items()}}
    C["launch_overhead_s"] = {
        "value": 0.0015, "unit": "s a launch (t_w - t_k)", "rule": "r5", "label": "POST HOC (measured)",
        "source": "the blind days' passes: t_w = 1 / solves_per_s less t_k",
        "measured": {d: {"mean": st.mean(v), "range": [min(v), max(v)]} for d, v in ovh.items()}}
    C["governed_base_w"] = {
        "value": {"aifoundry2": {"f_idle_mhz": 600, "B": {k: float(v) for k, v in rel136.items()}}},
        "unit": "W, the card's busy base at each clock", "rule": "r7",
        "label": "a priori numbers (E136's relation, registered before E194); rule 7's FORM is POST HOC",
        "source": f"{E136_REL} relation.B (E101's relation through E119, aifoundry2)",
        "note": "no relation for aifoundry3 or card 1: both run pinned at 600 MHz, where rule 7 is zero"}
    C["governor_climb_s"] = {
        "value": climb_med, "band": [climb_min, climb_max], "unit": "s at the idle clock at each burst's start",
        "rule": "r7", "label": "a priori (E190 arm A, %d processes)" % climb_n, "source": CLIMB_REL}
    C["levels"] = {
        "value": {"l1_bytes_per_hart": l1b, "l2_bytes_per_shire": 512 * 1024, "l2_validated_bytes_per_shire": 384 * 1024,
                  "l3_bytes_chip": 32 * 1024 * 1024, "harts_per_shire": 64},
        "rule": "r3", "label": "a priori (the documented geometry)",
        "source": f"{FACTS_L1} l1.firmware-mode; {FACTS_L2} l2.partition.default (0.5 MB L2, 1 MB L3 a shire, 32 MB in "
                  "all); validated: the 512-key sorts' 6 KiB a hart (384 KiB a shire), E189, E191 and E194"}
    C["v2_literals"] = {
        "value": lit, "rule": "none (the rules-off path)", "label": "v2's own literals, kept",
        "source": {k: f"{v[1]}: {v[2]}" for k, v in V2_LITERALS.items()}}
    out = {
        "model": "ledger v3 (Q193): ledger v2 with seven rules, each switchable; all seven off is v2",
        "schema": "ledger-v3-frozen/1", "frozen_pst": frozen_pst,
        "frozen_by": "tools/ledger/freeze_ledger_v3.py under /usr/bin/python3 %s" % sys.version.split()[0],
        "supersedes": FIRST_FREEZE,
        "parents_sha256": parents,
        "rules": {
            "r1": "seconds of scalar code: a (N - B) + c_br B (+ other classes at 1/rate - delta) hart-cycles",
            "r2": "seconds of memory code: max(issue, L2 line time, DRAM traffic / R_dram)",
            "r3": "bytes by level: lines past the L1 (L1 model) at the card's own E48 line prices; the level rule",
            "r4": "the DRAM copy: the card's own catalogue DRAM rows + P_stall for its time past the store probe's own",
            "r5": "the forecast die 50 C; wall seconds = seconds + 1.5 ms",
            "r6": "card inputs: rules 2-4 read the card's own column (off: aifoundry3's)",
            "r7": "a governed card above its idle clock: + (B(f) - B(f_idle)) for the time at f, the climb's share at "
                  "f_idle (POST HOC form)"},
        "fitted_on_the_blind_days": ["c_br_hart_cycles", "r_dram_b_per_s"],
        "post_hoc_choices": [
            "the forecast die 50 C and the 1.5 ms a launch (input conditions read on the blind days)",
            "the max() of rule 2 (not a sum): carried by the sorts, whose line time is hidden",
            "the awake analog of rule 4 (E23's stall power as the point, E193's stall2 the band's low end)",
            "rule 7's form: the climb's share of the burst's work done at the idle clock, without the base (chosen "
            "after E194's data; E194.md registered the base over each launch's whole seconds)",
            "the structure of rules 1-4, chosen after the blind days named seconds and bytes by level"],
        "constants": C,
    }
    return out


def dump(obj):
    return json.dumps(obj, indent=1, sort_keys=True) + "\n"


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frozen-pst", help="the freeze time, Pacific (written into the file)")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        have = json.load(open(OUT_JSON))
        body = dump(build(have["frozen_pst"]))
        same = body == open(OUT_JSON).read()
        h = V3.sha256_file(OUT_JSON)
        line = open(OUT_SHA).read().split()[0]
        print(f"frozen-v3.json: {'identical' if same else 'DIFFERS'}; sha256 {h}; the .sha256 file says {line}")
        ok = same and h == line
        print("FREEZE CHECK " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    if not a.frozen_pst:
        ap.error("--frozen-pst or --check")
    body = dump(build(a.frozen_pst))
    with open(OUT_JSON, "w") as f:
        f.write(body)
    h = V3.sha256_file(OUT_JSON)
    with open(OUT_SHA, "w") as f:
        f.write(f"{h}  frozen-v3.json\n")
    C = json.loads(body)["constants"]
    print(f"frozen-v3.json written, sha256 {h}")
    print(f"c_br {C['c_br_hart_cycles']['value']:.4f} (per card {C['c_br_hart_cycles']['fit']['per_card']}, LOO "
          f"{C['c_br_hart_cycles']['fit']['leave_one_program_out']}, a priori {C['c_br_hart_cycles']['a_priori']['value']:.3f}); "
          f"R_dram {C['r_dram_b_per_s']['value']}; P_stall {C['p_stall_w']['value']:.4f} W band {C['p_stall_w']['band']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
