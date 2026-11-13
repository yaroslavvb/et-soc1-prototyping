#!/usr/bin/env python3
"""The ledger programs' counts and first, UNFROZEN ledger estimates (Q166, the November checkpoint's plan, step 3).

  ledger_estimate.py --runs DIR [--repo TREE] [--out FILE] [--t0 C] [--spp-dry FILE] [--spp-slices DIR,...]

Reads, for each case the README names, DIR/<case>/counts-log.json (tools/counter/count_kernel.py's ledger-counts/1, from
one simulator run) and DIR/<case>/out.json (the host's line; the case must PASS), and:

1. COUNTS. Per unit of work by differencing two runs that differ only in the repeat count (copy: passes 2 - 1; SHA-256:
   repeat 2 - 1, i.e. the block's compressions; sort: sorts 2 - 1), and the fixed rest (the 1-repeat run less one unit).
   Exact per participant: the simulator's log, every instruction of every participant (64, shire 0). Then scaled to the
   card configuration (CARD below): fixed x participants + unit x units. The scaling is arithmetic, not a run.
2. SECONDS at 600 MHz, a bracket. SHA-256 and the sort: hart-cycles = sum over instructions of 1 / (the catalogue's issue
   per hart per cycle for that row, both harts issuing), from the main rows (point) and with every one-cycle integer op
   at the in-place rows' rate (c.add, add_norvc: about 0.21) (high); the simulator's own cycles are one an instruction
   (no pipeline sharing, no cache model) and are reported beside, not used. The copy: DRAM-bound, the write-back
   path's 27 GB/s (energy manual 4.1) for the stores, plus the 76 GB/s of the DRAM loads at the high end.
3. JOULES over idle, a bracket, by the energy manual's prices: every instruction at its catalogue row
   (docs/reports/data/2026-09-23-energy-manual/catalogue.json, combined/<row>/<data>/h2, aifoundry3's own mean; band:
   the row's lo across passes and cards to its hi, the hi times 2.06 for one-cycle integer ops: the in-place row
   add_norvc's hi over add's aifoundry3 mean);
   branches by outcome (taken: beq_taken, not taken: bne_nottaken; the *_data rows agree with a 50/50 mix of the two);
   the copy's bytes at the DRAM paths (energy manual 4.1: loads at the tensor-load DRAM row, stores at the fsw.ps
   write-back path, both inclusive of their instructions, which are not priced again); bytes past the L1 for SHA-256
   and the sort bracketed (the simulator has no cache model): 0 to every line once a level at the L2 (4.2, memhier's
   tensor-load row, by analogy).
   The card at rest, its leakage rise and the footing law: the ledger v2 of Q166's step 1 (tools/ledger/ledger_v2.py; frozen-v2.json
   idle_laws, k_rise_c_per_w, leak_slope_band_rel), at a starting die of --t0 (default 55 C, band 52-60 C).
4. SPARSE PARITY's never-run instance: the ledger v2 exactly as it prices E59 (tools/ledger/loads_ledger_v2.py's
   construction for a new (n, k, m)) at the host's own --dry plan (model_s, model_U) - a FORECAST of seconds - and,
   beside it, the counter's instructions per op from three 1/20000 slices scaled to the plan's ops.

Nothing here is frozen or registered: these are first estimates for the blind day's design. Desk only: no device.
Standard library only; run with python3 -I -B. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAT_REL = "docs/reports/data/2026-09-23-energy-manual/catalogue.json"
FROZEN_REL = "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"
F_HZ = 600e6
GiB = 1 << 30

# The card configurations these estimates are for (proposed for the blind day; nothing registered).
CARD = {
    "copy-zeros": {"prog": "copy", "args": "--prog copy --bytes 1G --passes 14 --data zeros --width 32", "participants": 2048,
                   "bytes": GiB, "passes": 14, "data": "zeros"},
    "copy-random": {"prog": "copy", "args": "--prog copy --bytes 1G --passes 14 --data random --width 32",
                    "participants": 2048, "bytes": GiB, "passes": 14, "data": "random"},
    "sha256": {"prog": "sha256", "args": "--prog sha256 --block 2048 --repeat 800", "participants": 2048, "block": 2048,
               "repeat": 800},
    "sort-sorted": {"prog": "sort", "args": "--prog sort --keys 512 --reps 1500 --order sorted", "participants": 2048,
                    "keys": 512, "reps": 1500, "order": "sorted"},
    "sort-shuffled": {"prog": "sort", "args": "--prog sort --keys 512 --reps 1500 --order shuffled",
                      "participants": 2048, "keys": 512, "reps": 1500, "order": "shuffled"},
}
# The simulator cases each estimate rests on (64 participants on shire 0; the README's table).
CASES = {
    "copy-zeros": ("c-v32-zero-p1", "c-v32-zero-p2"),
    "copy-random": ("c-v32-rand-p1", "c-v32-rand-p2"),
    "sha256": ("sha-b256-r1", "s-b256-r2"),
    "sort-sorted": ("o-sorted-r1", "o-sorted-r2"),
    "sort-shuffled": ("o-shuf-r1", "o-shuf-r2"),
}

# objdump's pseudo-instructions and forms without a catalogue row of their own -> the row that prices them.
ALIAS = {"mv": "addi", "li": "addi", "not": "xori", "neg": "sub", "negw": "subw", "sext.w": "addiw", "seqz": "sltiu",
         "snez": "sltu", "sltz": "slt", "sgtz": "slt", "slliw": "sllw", "srliw": "srlw", "sraiw": "sraw",
         "zext.b": "andi", "csrr": "csrr_fccnb", "csrw": "csrr_fccnb", "csrs": "csrr_fccnb", "csrc": "csrr_fccnb",
         "mov.m.x": "fbci.pi", "ecall": "fence"}
BRANCHES = {"beq", "bne", "blt", "bge", "bltu", "bgeu", "beqz", "bnez", "blez", "bgez", "bltz", "bgtz", "bgt", "ble",
            "bgtu", "bleu"}
JUMPS = {"jal", "jalr", "j", "jr", "ret", "call", "tail"}
ONE_CYCLE_INT = {"add", "sub", "and", "or", "xor", "sll", "srl", "sra", "slt", "sltu", "addw", "subw", "sllw", "srlw",
                 "sraw", "addi", "andi", "ori", "xori", "slli", "srli", "srai", "slti", "sltiu", "addiw", "lui", "auipc"}
INPLACE = ("add_norvc", "add")          # the in-place full-width form against the main row: price and rate ratios


class Catalogue:
    def __init__(self, path, card="aifoundry3"):
        self.J = json.load(open(path))
        self.card = card
        self.rates = {}
        for b in self.J["bursts"][card]:
            self.rates.setdefault(b["cfg"], []).append(b["ops_per_cycle_per_hart"])

    def row(self, pat, data):
        c = self.J["combined"][f"{pat}/{data}/h2"]
        mean = c["per_card"].get(self.card, {}).get("mean", c["mean"])
        return mean, c["lo"], c["hi"]

    def rate(self, pat, data="random"):
        return statistics.mean(self.rates[f"{pat}/{data}/h2"])

    def has(self, pat, data="random"):
        return f"{pat}/{data}/h2" in self.J["combined"]


def read_counts(d):
    """counts-log.json, or its gzip'd copy as the data folder keeps it."""
    p = os.path.join(d, "counts-log.json")
    if os.path.exists(p):
        return json.load(open(p))
    with gzip.open(p + ".gz", "rt") as f:
        return json.load(f)


def load_case(runs, name):
    d = os.path.join(runs, name)
    out = json.loads(open(os.path.join(d, "out.json")).read().strip().splitlines()[-1])
    if out.get("status") != "PASS":
        raise SystemExit(f"{name}: the host's status is {out.get('status')}, not PASS")
    cnt = read_counts(d)
    ck = cnt["checks"]
    if ck["unknown_mnemonics"] or ck["traps_executed"] or ck["unresolved_runs"]:
        raise SystemExit(f"{name}: counter checks {ck}")
    if cnt["total"]["harts"] != out["participants"]:
        raise SystemExit(f"{name}: {cnt['total']['harts']} harts logged, {out['participants']} participants")
    t = cnt["total"]
    bc = t["by_class"]
    mn = dict(t["by_mnemonic"])
    pcs = {}
    for h in cnt["harts"].values():
        for pc, (ex, tk) in h["per_pc"].items():
            e = pcs.setdefault(int(pc, 16), [0, 0])
            e[0] += ex
            e[1] += tk
    return {"name": name, "out": out, "instructions": t["instructions"], "by_class": bc, "by_mnemonic": mn, "pcs": pcs,
            "taken": bc["branch_taken"], "not_taken": bc["branch_not_taken"], "jumps": bc["jump"],
            "memory": t["memory"], "participants": out["participants"],
            "cycles_span_mean": statistics.mean(h["cycles_span"] for h in cnt["harts"].values()),
            "killed": sum(h["killed_and_restarted"] for h in cnt["harts"].values())}


def read_dis(path):
    """PC -> (mnemonic, operands) and symbol -> [start, end) from objdump -d -w output (plain or gzip'd)."""
    ins, syms, last = {}, {}, None
    fh = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    for line in fh:
        line = line.rstrip("\n")
        if line.endswith(">:") and " <" in line:
            a, name = line.split(" <", 1)
            last = name[:-2]
            syms[last] = [int(a, 16), None]
            continue
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].strip().endswith(":"):
            pc = int(parts[0].strip()[:-1], 16)
            ins[pc] = (parts[2].strip(), parts[3].strip() if len(parts) > 3 else "")
            if last:
                syms[last][1] = pc + 1
    return ins, syms


def loop_body(c, dis, func):
    """The executions of a function's innermost loop body (the last backward branch's span), as counts by mnemonic,
    its back edge's executions as taken, summed over every logged hart."""
    ins, syms = dis
    lo, hi = syms[func]
    back = None
    for pc in sorted(p for p in ins if lo <= p < hi):
        mn, ops = ins[pc]
        if mn in BRANCHES:
            tgt = int(ops.split(",")[-1].split()[0], 16)
            if tgt < pc:
                back = (tgt, pc)
    if back is None:
        raise SystemExit(f"{func}: no backward branch")
    out = {}
    for pc in range(back[0], back[1] + 1):
        if pc not in ins or pc not in c["pcs"]:
            continue
        mn = ins[pc][0]
        ex, tk = c["pcs"][pc]
        if mn in BRANCHES:
            # every execution of the back edge counts per byte as taken: the one exit a call makes is not taken, and
            # the caller's own back edge (one a pass) is taken, so per pass the two cancel (checked: the counts
            # reproduce the difference of the two runs exactly)
            out["@taken"] = out.get("@taken", 0) + ex
        elif mn in JUMPS:
            out["@jump"] = out.get("@jump", 0) + ex
        else:
            out[mn] = out.get(mn, 0) + ex
    return out, back


def mem_bytes(c):
    """Bytes read and written by the logged harts, every class and address region (no cache model: not levels)."""
    rd = wr = 0
    for cls in c["memory"].values():
        for reg in cls.values():
            rd += reg.get("read_bytes", 0)
            wr += reg.get("write_bytes", 0)
    return {"read_bytes": rd, "write_bytes": wr}


def vec(c):
    """A case's counts as one flat dict: mnemonics (branches and jumps out) plus taken / not taken / jumps."""
    v = {m: n for m, n in c["by_mnemonic"].items() if m not in BRANCHES and m not in JUMPS}
    v["@taken"], v["@not_taken"], v["@jump"] = c["taken"], c["not_taken"], c["jumps"]
    return v


def lin(a, b, fa=1.0, fb=1.0):
    keys = sorted(set(a) | set(b))     # sorted: the same sums in the same order on every run
    return {k: fa * a.get(k, 0) + fb * b.get(k, 0) for k in keys}


def per_participant_units(c1, c2, units1, units2):
    """unit = (c2 - c1) / (units2 - units1) per participant; fixed = c1 / participants - units1 * unit."""
    P = c1["participants"]
    du = units2 - units1
    unit = {k: v / (du * P) for k, v in lin(vec(c2), vec(c1), 1.0, -1.0).items()}
    fixed = {k: vec(c1).get(k, 0) / P - units1 * unit.get(k, 0) for k in sorted(set(vec(c1)) | set(unit))}
    return unit, fixed


def price_counts(cat, counts, data="random", inplace_hi=True):
    """Joules and hart-cycles for a dict of counts. Returns point, lo, hi for both, and the split by row."""
    j = [0.0, 0.0, 0.0]
    cyc = [0.0, 0.0]          # point (main rows' rates), high (one-cycle integer ops at the in-place rate)
    split = {}
    pr_in = cat.row(INPLACE[0], data)[2] / cat.row(INPLACE[1], data)[0]      # hi of the in-place row / main row
    rate_in = cat.rate(INPLACE[0], data)
    for m, n in sorted(counts.items()):
        if not n:
            continue
        if m == "@taken":
            pat = "beq_taken"
        elif m == "@not_taken":
            pat = "bne_nottaken"
        elif m == "@jump":
            pat = "jal"
        else:
            pat = ALIAS.get(m, m)
        if not cat.has(pat, data):
            raise SystemExit(f"no catalogue row for {m} (as {pat})")
        mean, lo, hi = cat.row(pat, data)
        r = cat.rate(pat, data)
        hi_m = hi * pr_in if (inplace_hi and pat in ONE_CYCLE_INT) else hi
        j[0] += n * mean * 1e-12
        j[1] += n * lo * 1e-12
        j[2] += n * hi_m * 1e-12
        cyc[0] += n / r
        cyc[1] += n / (min(r, rate_in) if pat in ONE_CYCLE_INT else r)
        split[m] = {"count": n, "row": pat, "pj": mean, "j": n * mean * 1e-12}
    return {"j": j, "hart_cycles": cyc, "split": split}


def rest_and_heat(ledger_v2, F, t, t_band, j_over, j_over_band, t0, t0_band):
    """The card at rest and the run's own leakage rise, by the ledger v2, with bands over t, T0 and the rest band."""
    card = "aifoundry3"
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


def estimate(args):
    repo = os.path.abspath(args.repo)
    sys.path.insert(0, os.path.join(repo, "tools", "ledger"))
    import ledger_v2  # noqa: E402  (the ledger v2, tools/ledger/ledger_v2.py)
    F = ledger_v2.load_frozen(os.path.join(repo, FROZEN_REL))
    cat = Catalogue(os.path.join(repo, CAT_REL))
    t0, t0_band = args.t0, (52.0, 60.0)
    res = {"schema": "ledger-progs-estimate/1", "label": "estimate, UNFROZEN (nothing registered); counts: simulator, "
           "exact for 64 participants, scaled to the card configuration by arithmetic",
           "catalogue": CAT_REL, "frozen_v2": FROZEN_REL, "frozen_v2_model": F.get("model"),
           "card": "aifoundry3", "f_mhz": 600, "die_start_c": t0, "die_start_band_c": list(t0_band), "programs": {}}
    mp = F["mem_paths"]
    for key, cfg in CARD.items():
        c1n, c2n = CASES[key]
        c1, c2 = load_case(args.runs, c1n), load_case(args.runs, c2n)
        prog = cfg["prog"]
        data = cfg.get("data", "random")
        P = cfg["participants"]
        if prog == "copy":
            u1, u2 = c1["out"]["passes"] * c1["out"]["part_bytes"], c2["out"]["passes"] * c2["out"]["part_bytes"]
            dis = read_dis(args.dis or os.path.join(args.runs, "ledger.dis"))
            func = "copy_v32" if c1["out"]["width"] == 32 else "copy_x8"
            b1, span = loop_body(c1, dis, func)
            b2, _ = loop_body(c2, dis, func)
            Pp = c1["participants"]
            unit = {k: (b2.get(k, 0) - b1.get(k, 0)) / ((u2 - u1) * Pp) for k in sorted(set(b1) | set(b2))}  # per byte
            # the taken back edges of the body are per byte; its one not-taken exit is per pass (below)
            unit.pop("@not_taken", None)
            part1 = c1["out"]["part_bytes"]
            dpass = c2["out"]["passes"] - c1["out"]["passes"]
            per_pass = {k: v / (dpass * Pp) - part1 * unit.get(k, 0)
                        for k, v in lin(vec(c2), vec(c1), 1.0, -1.0).items()}
            fixed = {k: vec(c1).get(k, 0) / Pp - c1["out"]["passes"] * per_pass.get(k, 0) - u1 * unit.get(k, 0)
                     for k in sorted(set(vec(c1)) | set(unit) | set(per_pass))}
            units_card = cfg["bytes"] / P * cfg["passes"]
            for k, v in per_pass.items():     # carried into the fixed part at the card's passes
                fixed[k] = fixed.get(k, 0) + cfg["passes"] * v
            unit_name = "byte copied"
        elif prog == "sha256":
            nb1 = c1["out"]["repeat"] * (c1["out"]["block"] // 64)
            nb2 = c2["out"]["repeat"] * (c2["out"]["block"] // 64)
            unit, fixed = per_participant_units(c1, c2, nb1, nb2)             # per message block (one compression)
            units_card = cfg["repeat"] * (cfg["block"] // 64)
            unit_name = "message block (one compression)"
        else:
            unit, fixed = per_participant_units(c1, c2, c1["out"]["reps"], c2["out"]["reps"])   # per sort
            units_card = cfg["reps"]
            unit_name = "sort of 512 keys"
        per_part = {k: fixed.get(k, 0) + units_card * unit.get(k, 0) for k in sorted(set(unit) | set(fixed))}
        m1, m2 = mem_bytes(c1), mem_bytes(c2)
        du = (u2 - u1) if prog == "copy" else ((nb2 - nb1) if prog == "sha256" else (c2["out"]["reps"] - c1["out"]["reps"]))
        u1n = u1 if prog == "copy" else (nb1 if prog == "sha256" else c1["out"]["reps"])
        mem_unit = {kk: (m2[kk] - m1[kk]) / (du * c1["participants"]) for kk in m1}
        mem_fixed = {kk: m1[kk] / c1["participants"] - u1n * mem_unit[kk] for kk in m1}
        mem_card = {kk: P * (mem_fixed[kk] + units_card * mem_unit[kk]) for kk in m1}
        total = {k: v * P for k, v in per_part.items()}
        instr_total = sum(total.values())
        rec = {"config": cfg, "cases": [c1n, c2n], "unit": unit_name, "units_per_participant": units_card,
               "per_unit_per_participant": {k: v for k, v in sorted(unit.items()) if abs(v) > 1e-12},
               "per_pass_per_participant": ({k: v for k, v in sorted(per_pass.items()) if abs(v) > 1e-9}
                                            if prog == "copy" else None),
               "loop_body": ({"function": func, "pcs": [hex(span[0]), hex(span[1])]} if prog == "copy" else None),
               "fixed_per_participant": {k: v for k, v in sorted(fixed.items()) if abs(v) > 1e-9},
               "instructions_total": instr_total,
               "by_class_total": by_class_total(total),
               "bytes_counted": {"per_unit_per_participant": mem_unit, "fixed_per_participant": mem_fixed,
                                 "card_total": mem_card,
                                 "label": "counted (simulator log: every load and store's bytes, any address region); "
                                          "which level served them is not counted (no cache model) and is bracketed "
                                          "in the byte terms"},
               "sim": {c["name"]: {"instructions": c["instructions"], "cycles_span_mean": c["cycles_span_mean"],
                                   "hart0_cycles_mean": c["out"]["hart0_cycles"]["mean"], "killed": c["killed"],
                                   "taken": c["taken"], "not_taken": c["not_taken"]} for c in (c1, c2)}}
        terms = {}
        if prog == "copy":
            nbytes = cfg["bytes"] * cfg["passes"]
            move = {"flw.ps", "fsw.ps", "ld", "sd"}
            over = {k: v for k, v in total.items() if k not in move}
            pc = price_counts(cat, over, "random")
            terms["instructions (loop and set-up; the moves are inside the byte prices)"] = {
                "j": pc["j"][0], "band": [pc["j"][1], pc["j"][2]], "count": sum(over.values())}
            if data == "zeros":
                rd = (mp["dram_load"]["zeros_pj"], 86.2, 114.6)
                wr = (247.4, 202.4, 288.9)
            else:
                rd = (mp["dram_load"]["random_pj"]["a3"], 105.6, 145.4)
                wr = (325.8, 317.4, 373.3)
            terms["DRAM reads, 32 B vector loads (tensor-load DRAM row by analogy; 4.2 memhier DRAM inside the band)"] = {
                "j": nbytes * rd[0] * 1e-12, "band": [nbytes * rd[1] * 1e-12, nbytes * rd[2] * 1e-12],
                "bytes": nbytes, "pj_per_byte": rd}
            terms["DRAM writes, fsw.ps through the L1 (the write-back path, 4.1)"] = {
                "j": nbytes * wr[0] * 1e-12, "band": [nbytes * wr[1] * 1e-12, nbytes * wr[2] * 1e-12],
                "bytes": nbytes, "pj_per_byte": wr}
            bw_st = 27e9
            bw_ld = ledger_v2._c(F, "dram_bandwidth_gb_s") * 1e9
            t_lo = nbytes / bw_st
            t_hi = nbytes / bw_st + nbytes / bw_ld
            t = 0.5 * (t_lo + t_hi)
            secs = {"point": t, "band": [t_lo, t_hi], "how": "stores at the write-back path's 27 GB/s (energy manual 4.1) "
                    "and, at the high end, the loads' bytes at 76 GB/s on top (frozen-v2 dram_bandwidth_gb_s)",
                    "instruction_bound_s": pc["hart_cycles"][0] / P / F_HZ}
        else:
            pc = price_counts(cat, total, "random")
            terms["instructions (catalogue rows, random column; branches by outcome)"] = {
                "j": pc["j"][0], "band": [pc["j"][1], pc["j"][2]], "count": instr_total}
            hc_point = pc["hart_cycles"][0] / P
            hc_hi = pc["hart_cycles"][1] / P
            secs = {"point": hc_point / F_HZ, "band": [hc_point / F_HZ, hc_hi / F_HZ],
                    "how": "hart-cycles = sum of 1 / issue rate (catalogue, both harts issuing), per participant; high: "
                           "one-cycle integer ops at the in-place rows' rate; L2 stalls not modelled (no cache model)"}
            l2_pj = (2.83, 1.42, 4.99)            # energy manual 4.2, L2 (memhier's tensor loads, by analogy): a3 mean, the row's range
            if prog == "sha256":
                lines = units_card * P            # the message block's line, once a compression
                thrash = 8 * units_card * P       # W[64] and K[64]: 8 lines a compression if the 512 B L1 loses them
                terms["bytes past the L1 (bracketed: the message line a compression; up to 8 more lines of W and K)"] = {
                    "j": lines * 64 * l2_pj[0] * 1e-12, "band": [0.0, (lines + thrash) * 64 * l2_pj[2] * 1e-12],
                    "lines_point": lines, "lines_high": lines + thrash}
            else:
                n = cfg["keys"]
                levels = int(math.log2(n))
                b_sort = (2 * n * 4) * levels + 2 * n * 4    # each level reads and writes every key; the copy-in
                nb = b_sort * cfg["reps"] * P
                terms["bytes past the L1 (bracketed: every key read and written once a level at the L2)"] = {
                    "j": nb * l2_pj[0] * 1e-12, "band": [0.0, nb * l2_pj[2] * 1.5 * 1e-12], "bytes_point": nb}
            t = secs["point"]
        j_over = sum(v["j"] for v in terms.values())
        j_band = [sum(v["band"][0] for v in terms.values()), sum(v["band"][1] for v in terms.values())]
        rest, heat = rest_and_heat(ledger_v2, F, t, secs["band"], j_over, j_band, t0, t0_band)
        rec.update({"seconds": secs, "terms": terms, "j_over_idle": j_over, "j_over_idle_band": j_band,
                    "w_over_idle": j_over / t, "rest": rest, "heat": heat,
                    "j_total": rest["j"] + heat["j"] + j_over,
                    "j_total_band": [rest["band"][0] + heat["band"][0] + j_band[0],
                                     rest["band"][1] + heat["band"][1] + j_band[1]]})
        res["programs"][key] = rec
    if args.spp_dry:
        res["programs"]["sparse-parity"] = sparse_parity(args, repo, F, ledger_v2, t0, t0_band)
    return res


def sparse_parity(args, repo, F, ledger_v2, t0, t0_band):
    import loads_ledger_v2 as L  # noqa: E402  (tools/ledger/loads_ledger_v2.py)
    dry = json.loads(open(args.spp_dry).read().strip().splitlines()[-1])
    if dry.get("status") != "DRY":
        raise SystemExit(f"{args.spp_dry}: not a --dry line (status {dry.get('status')})")
    inst = dry.get("instance", {})
    n, k, m = int(inst.get("n", dry.get("n"))), int(inst.get("k", dry.get("k"))), int(inst.get("m", dry.get("m")))
    plan = dry.get("plan", dry)          # the host's --dry line is flat: ops, dump_tiles, model_U, model_s at the top
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
    t = plan["model_s"]
    per_hart = 1024 * F_HZ * t
    load = {"card": "aifoundry3", "f_mhz": 600.0, "die_start_c": t0, "work_units": 1, "work_unit": "solve (one launch)",
            "seconds": t,
            "tensor": [{"format": "int8", "kind": "int8.pm1", "ops": ops}],
            "instr": [{"class": "vec_int", "hart_cycles": cyc["epilogue"], "what": "epilogue (hart 0)"},
                      {"class": "vec_int", "hart_cycles": cyc["row_tile_overhead"], "what": "row-tile set-up (hart 0)"},
                      {"class": "vec_int", "hart_cycles": cyc["generation_hart1_beyond_its_stores"],
                       "what": "row generation beyond its stores (hart 1)"}],
            "awake_hart_cycles": max(0.0, per_hart - hart0_busy) + max(0.0, per_hart - hart1_busy),
            "bytes": [{"path": "scp_load", "bytes": 2048.0 * ops, "rho": x[0], "tau": x[1], "what": "A and B tiles"},
                      {"path": "scp_store", "bytes": 1024.0 * S * rows, "rho": x[0], "tau": x[1], "what": "staged rows"},
                      {"path": "dram_load", "bytes": 32.0 * n * S * 64.0, "rho": x[0], "tau": x[1], "what": "X copy-in"},
                      {"path": "l2_stream", "bytes": 192.0 * S * rows, "rho": x[0], "tau": x[1], "what": "X reads"}]}
    out = ledger_v2.predict(load, F)
    rec = {"instance": {"n": n, "k": k, "eta": inst.get("eta", dry.get("eta")), "m": m,
                        "seed": inst.get("seed", dry.get("seed"))},
           "config": "--mode tensor --shires 0xffffffff --per-shire 32 --variant m1 --cost fit --gen inc (variant b, "
                     "energy.sh's ALL and CB)",
           "plan": {kk: plan.get(kk) for kk in ("ops", "dump_tiles", "model_U", "model_s", "est_s", "guard_s", "S",
                                                "stage", "nbuf", "scp_layout_kb", "candidates", "work_tiles")},
           "port_matches_plan": cnt["ops"] == plan.get("ops") and cnt["output_tiles"] == plan.get("dump_tiles"),
           "counts": {"ops": ops, "output_tiles": outs, "row_tiles": rows, "S": S},
           "seconds": {"point": t, "how": "the host's --dry model_s (the fitted cycle model; held out +5.0% and +7.5% "
                                          "on the 29 Sep runs, README)"},
           "ledger_v2": {"j_over_idle": out["j_over_idle"], "j_over_idle_band": out["j_over_idle_band"],
                         "w_over_idle": out["w_over_idle"], "j_total": out["j_total"],
                         "j_total_band": out["j_total_band"], "rest_w": out["rest"]["w"],
                         "heat_j": out["heat"]["j"],
                         "terms": {kk: {"j": v["j"], "band": v["band"]} for kk, v in out["terms"].items()}},
           "label": "estimate, UNFROZEN: the ledger v2 (frozen 59ff9117...) on a load built as its E59 loads are, at the "
                    "--dry plan's forecast seconds; a new instance, so neither held out nor blind yet"}
    if args.spp_slices:
        rec["counter_slices"] = spp_counter_fit(repo, args, [d for d in args.spp_slices.split(",") if d],
                                                rec["counts"]["output_tiles"], rec["counts"]["row_tiles"],
                                                rec["counts"]["ops"])
    return rec


SPP_SITES_REL = "docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel/all-addr2line.txt.gz"
SPP_DIS_REL = "docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel/sparseparity.dis"


def spp_counter_fit(repo, args, dirs, outs_total, rows_total, ops_total):
    """The counter's own split and fit (tools/counter/card_compare_sparseparity.py's, by its functions): every
    instruction inside wait_count is a spin (its count follows the simulator's timing, not the card's) and the rest is
    work; hart 0's work = a x output tiles + b x row tiles, hart 1's = c x row tiles, by least squares over the slices,
    class by class; then scaled to the never-run instance's whole plan (its output and row tiles)."""
    import importlib.util  # noqa: E402
    spec = importlib.util.spec_from_file_location(
        "ledger_card_compare", os.path.join(repo, "tools", "counter", "card_compare_sparseparity.py"))
    cc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cc)
    sites = cc.read_sites(args.spp_sites or os.path.join(repo, SPP_SITES_REL))
    spin_pcs = set(pc for pc, ch in sites.items() if "wait_count" in ch)
    ck = cc.load_counter()
    by_addr = {i.addr: i for i in ck.parse_dis(args.spp_dis or os.path.join(repo, SPP_DIS_REL))}
    slices = []
    for d in dirs:
        out = json.loads(open(os.path.join(d, "out.json")).read().strip().splitlines()[-1])
        if out.get("status") != "PASS":
            raise SystemExit(f"{d}: status {out.get('status')}")
        cnt = read_counts(d)
        S = out["geometry"]["S"]
        ops = out["plan"]["ops"]
        t0, t1 = out["plan"]["tiles"]
        h = {}
        for t in ("0", "1"):
            pp = cnt["harts"][t]["per_pc"]
            spin = sum(n for pc, (n, tk) in pp.items() if int(pc, 16) in spin_pcs)
            h[t] = {"instructions": cnt["harts"][t]["instructions"], "spin": spin,
                    "work": cnt["harts"][t]["instructions"] - spin,
                    "work_by_class": cc.classes_of(pp, by_addr, lambda x: x not in spin_pcs),
                    "tensor": cnt["harts"][t]["tensor"]}
        slices.append({"run": os.path.basename(d.rstrip("/")), "ops": ops, "row_tiles": t1 - t0,
                       "output_tiles": ops / S, "S": S, "hart0": h["0"], "hart1": h["1"],
                       "oracle": out.get("checks", {}).get("oracle"), "status": out.get("status")})
    xs = [(sl["output_tiles"], sl["row_tiles"]) for sl in slices]
    a0, b0 = cc.lstsq2(xs, [sl["hart0"]["work"] for sl in slices])
    c1 = sum(sl["hart1"]["work"] for sl in slices) / sum(sl["row_tiles"] for sl in slices)
    cls = sorted(set(k for sl in slices for t in ("hart0", "hart1") for k in sl[t]["work_by_class"]))
    by_class, resid = {}, {}
    for c in cls:
        ac, bc = cc.lstsq2(xs, [sl["hart0"]["work_by_class"].get(c, 0) for sl in slices])
        c1c = sum(sl["hart1"]["work_by_class"].get(c, 0) for sl in slices) / sum(sl["row_tiles"] for sl in slices)
        by_class[c] = ac * outs_total + bc * rows_total + c1c * rows_total
        tot = [sl["hart0"]["work_by_class"].get(c, 0) + sl["hart1"]["work_by_class"].get(c, 0) for sl in slices]
        fit = [ac * sl["output_tiles"] + bc * sl["row_tiles"] + c1c * sl["row_tiles"] for sl in slices]
        resid[c] = max((abs(t - f) / t) if t else 0.0 for t, f in zip(tot, fit))
    work0 = a0 * outs_total + b0 * rows_total
    work1 = c1 * rows_total
    int8 = [sl["hart0"]["tensor"].get("fma_int8", {}).get("ops", 0) for sl in slices]
    return {"slices": [{kk: sl[kk] for kk in ("run", "ops", "row_tiles", "output_tiles", "status", "oracle")} |
                       {"hart0_instructions": sl["hart0"]["instructions"], "hart0_spin": sl["hart0"]["spin"],
                        "hart1_instructions": sl["hart1"]["instructions"], "hart1_spin": sl["hart1"]["spin"]}
                       for sl in slices],
            "rates": {"hart0_work_per_output_tile": a0, "hart0_work_per_row_tile": b0,
                      "hart1_work_per_row_tile": c1},
            "int8_ops_counted_over_planned": sum(int8) / sum(sl["ops"] for sl in slices),
            "per_solve_work_instructions": work0 + work1,
            "per_solve_work_hart0": work0, "per_solve_work_hart1": work1,
            "per_solve_work_by_class": by_class, "fit_residual_max_fraction": resid,
            "per_op_work_instructions": (work0 + work1) / ops_total,
            "label": "counted (simulator log of harts 0 and 1 of one minion, three 1/20000 slices; spin loops inside "
                     "wait_count left out, as tools/counter/card_compare_sparseparity.py does) and scaled by least "
                     "squares to the plan's output and row tiles: an estimate of the whole solve's work instructions"}


def by_class_total(total):
    """The card configuration's counts in the counter's classes (branches and jumps by outcome)."""
    cls = {}
    for m, n in sorted(total.items()):
        if m == "@taken":
            k = "branch_taken"
        elif m == "@not_taken":
            k = "branch_not_taken"
        elif m == "@jump":
            k = "jump"
        elif m in ("flw.ps", "lw", "ld", "lwu", "lbu", "lb", "lh", "lhu", "flw"):
            k = "load"
        elif m in ("fsw.ps", "sw", "sd", "sb", "sh", "fsw"):
            k = "store"
        elif m in ("mul", "mulw", "mulh", "mulhu", "div", "divu", "rem", "remu", "divw", "divuw", "remw", "remuw"):
            k = "int_muldiv"
        elif m in ("csrr", "csrw", "ecall", "fence"):
            k = "system"
        elif m == "mov.m.x":
            k = "mask_broadcast"
        else:
            k = "scalar_int"
        cls[k] = cls.get(k, 0) + n
    return cls


def table(res):
    lines = ["program          seconds [band]            J over idle [band]        W over idle   J with the card at rest [band]"]
    for k, r in res["programs"].items():
        if k == "sparse-parity":
            v = r["ledger_v2"]
            lines.append(f"{k:16s} {r['seconds']['point']:.3f} (model)              {v['j_over_idle']:7.2f} "
                         f"[{v['j_over_idle_band'][0]:.2f}, {v['j_over_idle_band'][1]:.2f}]   {v['w_over_idle']:6.2f}"
                         f"       {v['j_total']:7.2f} [{v['j_total_band'][0]:.2f}, {v['j_total_band'][1]:.2f}]")
            continue
        s = r["seconds"]
        lines.append(f"{k:16s} {s['point']:.3f} [{s['band'][0]:.3f}, {s['band'][1]:.3f}]   {r['j_over_idle']:7.2f} "
                     f"[{r['j_over_idle_band'][0]:.2f}, {r['j_over_idle_band'][1]:.2f}]   {r['w_over_idle']:6.2f}"
                     f"       {r['j_total']:7.2f} [{r['j_total_band'][0]:.2f}, {r['j_total_band'][1]:.2f}]")
    return "\n".join(lines)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--runs", required=True, help="the folder holding one subfolder per simulator case")
    ap.add_argument("--repo", default=os.path.normpath(os.path.join(HERE, "..", "..")), help="the lab tree (default: this file's)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--dis", default=None, help="the kernel's objdump -d -w (plain or .gz); default RUNS/ledger.dis")
    ap.add_argument("--t0", type=float, default=55.0, help="the card's die at the start, C (default 55)")
    ap.add_argument("--spp-dry", default=None, help="sparseparity_host --dry's JSON for the new instance")
    ap.add_argument("--spp-slices", default=None, help="comma-separated counted slice folders")
    ap.add_argument("--spp-sites", default=None, help="sparse parity's addr2line of every kernel address (.gz)")
    ap.add_argument("--spp-dis", default=None, help="sparse parity's kernel disassembly")
    a = ap.parse_args(argv)
    res = estimate(a)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1, sort_keys=True)
    print(table(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
