#!/usr/bin/env python3
"""The load ledger, version 3 (Q193: the ledger's repair after the blind days, step 5 of the owner's private checkpoint of
Wed 11 Nov 2026).

v3 is ledger v2 (tools/ledger/ledger_v2.py with workloads/ledger/ledger_estimate.py, both unchanged and pinned) with
seven rules, each of which can be switched off on its own; with all seven off it is v2, number for number
(tools/ledger/readings_ledger_v3.py checks it against E189's, E191's and E194's frozen v2 forecasts). It reads nothing at
run time but the frozen constants (tools/ledger/frozen-v3.json, written by freeze_ledger_v3.py; its sha256 is the
freeze line), frozen-v2.json, the energy catalogue and the two pinned v2 modules.

THE SEVEN RULES (V2-TO-V3.md has them term by term against v2):
 r1  SECONDS OF SCALAR CODE. Per participant (hart), T_hart = a (N - B - n_o) + c_br B + sum over the other mnemonics
     n (1/r - delta) hart-cycles: N instructions, B taken branches and jumps; a = 2.0 (the catalogue's one-cycle rows less
     their own loop: a priori) for the a-set, the fitted programs' mnemonics whose own row is a one-cycle row (within half
     a hart-cycle of a after delta), and for untaken branches; c_br fitted on the blind days' cycle counters (post hoc);
     every other mnemonic (n_o of them: mul and csrr in the blind day's programs, and div, float arithmetic or any class a
     later program brings) at its own catalogue row's 1/rate less the loop's delta. v2: the sum of 1/rate over the rows.
 r2  SECONDS OF MEMORY CODE. t = max(T_hart / f, T_L2 / 600 MHz, D / R_dram): T_L2 = a minion's two harts' line fills
     and allocations at E48's line cycles (a priori; no minion clock in them, as assumed), D = the DRAM traffic (a byte
     copied through the L1 moves 3: read, allocate, write back), R_dram fitted on the blind days' copies (post hoc).
     v2: a copy at the midpoint of [the stores at 27 GB/s, the stores plus the loads at 76 GB/s].
 r3  BYTES BY LEVEL. Lines past the L1 from an L1 model of the documented 512 B a hart (tools/counter/l1_model.py),
     a fill at e_r and a dirty eviction at e_w - e_r, E48's L2 rows less its L1 rows (a priori); the level a load
     lives at by the working set (below). v2: the L2 tensor-load row's 2.83 pJ a byte on its own byte counts.
 r4  THE DRAM COPY. Bytes at the card's own tensor-load and store-stream DRAM rows, plus P_stall for its time past the
     store probe's own (E23's 1.19 W, the band down to E193's stall price; a priori). At another clock the byte rows stay
     unscaled and their bands' high ends take x (V/V600)^2, as rule 3's do. v2: literal prices, no awake time.
 r5  THE FORECAST DIE. 50 C, and the wall seconds a launch = its seconds + 1.5 ms (both read on the blind days: post
     hoc, input conditions, not prices). v2: 55 C and the seconds alone.
 r6  CARD INPUTS. Rules 2-4 read the card's own column (E48 line prices, catalogue DRAM rows, R_dram); off, they read
     aifoundry3's, the v2 habit that cost card 1's copies -0.6 J (E191). A v2 term that has no per-card value keeps
     its literal either way.
 r7  A GOVERNED CARD ABOVE ITS IDLE CLOCK. + (B(f_busy) - B(f_idle)) for the time at f_busy, the burst's work less
     the governor's climb at its start done at f_idle (E136's relation, E190's median climb: a priori numbers; the FORM
     was chosen after E194's data: POST HOC, its blind test is a later aifoundry2 day). Zero on a pinned card.
Unchanged from v2: every instruction price (the catalogue's rows, random column, the card's own mean; branches by
outcome), the card at rest (the footing law per card) and the leakage rise (k_rise), the tensor, scratchpad, L2-stream
and mesh terms, sparse parity's whole load, the clock scaling of prices (v2 = (V / V600)^2 on instruction and awake
terms; byte paths and line prices unscaled), and the multiply-add (no refit).

THE LEVEL RULE (r3): a load lives in the L1 if the L1 model leaves no steady-state fill; in the L2 if its working set is
at most the L2 a shire (512 KiB; 384 KiB a shire is the largest validated: the 512-key sorts); through DRAM if it
exceeds the L2 a shire and the L3 (32 MiB) in all; anything else is outside v3 (priced at the L2's prices and flagged).

A PLAIN PROGRAM (program() builds one): its card, clock, participants and units; its instruction counts a participant
by mnemonic (the counter's form: branches and jumps as @taken, @not_taken, @jump); its lines past the L1 a participant
(fills, read fills, write fills, dirty evictions: l1_model.py); its working set a hart; for a copy its bytes copied and
data; v2's own byte description (for the rules-off path); for rule 7 the launches a burst.
Sparse parity and any other v2 load: predict_v2load() (ledger_v2.predict(), rules 5 and 7 on top).

Desk only: no card, no device. Standard library only; run with /usr/bin/python3 -I -B (3.12.3 wrote the outputs).
SPDX-License-Identifier: Apache-2.0
"""
import copy as _copy
import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FROZEN_V3 = os.path.join(HERE, "frozen-v3.json")
FROZEN_V2_REL = "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"
CAT_REL = "docs/reports/data/2026-09-23-energy-manual/catalogue.json"
F_REF = 600e6
P_MINION = 2                       # participants (harts) a minion
RULES = ("r1", "r2", "r3", "r4", "r5", "r6", "r7")
ALL = frozenset(RULES)
NONE = frozenset()
MOVES = ("flw.ps", "fsw.ps", "ld", "sd")     # a DRAM copy's moves: inside its byte prices (v2's rule, kept)
CARD_KEY = {"aifoundry2": "a2", "aifoundry3": "a3", "aifoundry1-c1": "c1"}
# the v2 modules v3 imports, pinned (they are never edited; a different file is refused)
PINS = {
    "tools/ledger/ledger_v2.py": "214cf7a49c1edae206ae34133bb6e2dc1f99a414e367b4617b2607f451cd2886",
    "workloads/ledger/ledger_estimate.py": "e3670e78da97107c067512450e57698680be4a1def1a0d01a232d4f360eef2f2",
    FROZEN_V2_REL: "59ff911705137e5486efcb15c482919e3d257f800193bcc9f1d78ee7283753ce",
    CAT_REL: "1186a9764838330369bc87f90f9ed4aed03d9d1373fd3185a8f107cf2eb1a7ae",
}


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_pins(repo=REPO):
    bad = [p for p, h in PINS.items() if sha256_file(os.path.join(repo, p)) != h]
    if bad:
        raise SystemExit("ledger_v3: refused, pinned v2 inputs differ: " + ", ".join(bad))


_MODS = {}


def mods(repo=REPO):
    """ledger_v2 and ledger_estimate, after their pins are checked (loaded once)."""
    if "lv" not in _MODS:
        check_pins(repo)
        for name, rel in (("lv", "tools/ledger/ledger_v2.py"), ("le", "workloads/ledger/ledger_estimate.py")):
            spec = importlib.util.spec_from_file_location("ledger_v3_" + name, os.path.join(repo, rel))
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            _MODS[name] = m
        _MODS["F2"] = json.load(open(os.path.join(repo, FROZEN_V2_REL)))
        _MODS["cat"] = {}
    return _MODS["lv"], _MODS["le"], _MODS["F2"]


def catalogue(card, repo=REPO):
    lv, le, F2 = mods(repo)
    if card not in _MODS["cat"]:
        _MODS["cat"][card] = le.Catalogue(os.path.join(repo, CAT_REL), card)
    return _MODS["cat"][card]


def load_frozen(path=None):
    return json.load(open(path or FROZEN_V3))


def rules_of(rules):
    if rules is None:
        return ALL
    if isinstance(rules, str):
        rules = [r for r in rules.split(",") if r]
    r = frozenset(rules)
    bad = r - ALL
    if bad:
        raise ValueError(f"unknown rules {sorted(bad)}")
    return r


def _c(F3, name):
    return F3["constants"][name]["value"]


def _band(F3, name):
    c = F3["constants"][name]
    return c.get("band") or [c["value"], c["value"]]


# ------------------------------------------------------------------ the pieces
def v2_factor(card, f_mhz):
    lv, le, F2 = mods()
    return lv.v2_factor(F2, card, f_mhz)


def price_card(F3, card, rules):
    """The card whose column rules 2-4 read: the card's own with r6, aifoundry3's without (v2's habit)."""
    return card if "r6" in rules else "aifoundry3"


def line_prices(F3, card):
    """(e_r, e_w) in joules: E48's L2 rows less its L1 rows on that card."""
    prices = _c(F3, "line_prices_pj")[card]
    return prices["e_r"] * 1e-12, prices["e_w"] * 1e-12


def dram_rows(F3, card, data):
    return _c(F3, "dram_copy_rows")[card][data]


def r_dram(F3, card):
    v = _c(F3, "r_dram_b_per_s")
    return v.get(card, v["default"])


def instr_term(prog, counts, f_mhz):
    """v2's instruction term, unchanged: every instruction at its catalogue row (random column, the card's own mean;
    branches by outcome), times v2 = (V/V600)^2 at another clock. Returns j, band and v2's hart-cycles (point, high)."""
    lv, le, F2 = mods()
    cat = catalogue(prog["card"])
    P = prog["participants"]
    total = {k: v * P for k, v in sorted(counts.items()) if v}
    pc = le.price_counts(cat, total, "random")
    v2f = v2_factor(prog["card"], f_mhz)
    return {"j": pc["j"][0] * v2f, "band": [pc["j"][1] * v2f, pc["j"][2] * v2f],
            "hart_cycles_v2": [pc["hart_cycles"][0] / P, pc["hart_cycles"][1] / P], "v2_factor": v2f,
            "split": pc["split"], "count": sum(total.values())}


def t_hart_v3(F3, prog, counts, c_br=None):
    """Rule 1: hart-cycles a participant (both harts issuing)."""
    a = _c(F3, "a_hart_cycles")
    cbr = _c(F3, "c_br_hart_cycles") if c_br is None else c_br
    delta = _c(F3, "loop_delta_hart_cycles")
    aset = set(_c(F3, "a_set_mnemonics"))
    cat = catalogue(prog["card"])
    lv, le, F2 = mods()
    T = 0.0
    other = {}
    for m, n in sorted(counts.items()):
        if not n:
            continue
        if m in ("@taken", "@jump"):
            T += cbr * n
        elif m == "@not_taken" or m in aset:
            T += a * n
        else:
            pat = le.ALIAS.get(m, m)
            if not cat.has(pat, "random"):
                raise SystemExit(f"ledger_v3: no catalogue row for {m} (as {pat})")
            x = 1.0 / cat.rate(pat, "random") - delta
            T += n * x
            other[m] = x
    return T, other


def level_of(F3, prog):
    """The level rule (r3): 'L1', 'L2', 'DRAM' or 'outside'."""
    lv_ = _c(F3, "levels")
    ws_h = prog.get("working_set_b_per_hart")
    lines = prog.get("lines") or {}
    if ws_h is None:
        return "outside", "no working set given"
    ws_shire = ws_h * lv_["harts_per_shire"]
    ws_chip = ws_h * prog["participants"]
    if "fills" in lines and lines["fills"] == 0.0:
        return "L1", "the L1 model leaves no steady-state fill"
    if ws_shire <= lv_["l2_bytes_per_shire"]:
        why = "working set %d B a shire, at most the L2's %d" % (ws_shire, lv_["l2_bytes_per_shire"])
        if ws_shire > lv_["l2_validated_bytes_per_shire"]:
            why += " (above the largest validated, %d B a shire)" % lv_["l2_validated_bytes_per_shire"]
        return "L2", why
    if ws_shire > lv_["l2_bytes_per_shire"] and ws_chip > lv_["l3_bytes_chip"]:
        return "DRAM", "working set %d B a shire past the L2, %d B in all past the L3" % (ws_shire, ws_chip)
    return "outside", "working set %d B a shire past the L2 but %d B in all inside the L3" % (ws_shire, ws_chip)


def idle_w(card, T):
    lv, le, F2 = mods()
    return lv.idle_w(F2, card, T)[0]


def rest_and_heat(card, t, t_band, j_over, j_over_band, t0, t0_band):
    """ledger_estimate.rest_and_heat() with the card as a parameter (E191's and E194's rest_and_heat_card, the same
    arithmetic): the card at rest P_idle(T0) t and the run's own rise k_leak(T0) k_rise P_over t, with their bands."""
    lv, le, F2 = mods()
    p_rest, law = lv.idle_w(F2, card, t0)
    rb = F2["idle_laws"][card]["rest_band_w"]
    lo_t0 = min(lv.idle_w(F2, card, x)[0] for x in t0_band)
    hi_t0 = max(lv.idle_w(F2, card, x)[0] for x in t0_band)
    rest = {"w": p_rest, "law": law, "j": p_rest * t, "band": [(lo_t0 - rb) * t_band[0], (hi_t0 + rb) * t_band[1]]}
    kr = lv._c(F2, "k_rise_c_per_w")
    kr_lo, kr_hi = lv._cb(F2, "k_rise_c_per_w")
    kl = lv.leak_slope(F2, card, t0)
    kb = F2["leak_slope_band_rel"]
    p_over = j_over / t
    heat_j = kl * kr * p_over * t
    heat_band = [kl * kb[0] * kr_lo * (j_over_band[0] / t_band[1]) * t_band[0],
                 kl * kb[1] * kr_hi * (j_over_band[1] / t_band[0]) * t_band[1]]
    return rest, {"k_leak_w_per_c": kl, "die_rise_c": kr * p_over, "j": heat_j, "band": heat_band}


def j_rest_given(card, j_over, j_over_band, t_w, T0):
    """The card at rest given the measured wall seconds a launch and starting die (E189's given(), any card)."""
    lv, le, F2 = mods()
    kl = lv.leak_slope(F2, card, T0)
    kr = lv._c(F2, "k_rise_c_per_w")
    kr_lo, kr_hi = lv._cb(F2, "k_rise_c_per_w")
    kb = F2["leak_slope_band_rel"]
    heat = kl * kr * (j_over / t_w) * t_w
    heat_band = [kl * kb[0] * kr_lo * j_over_band[0], kl * kb[1] * kr_hi * j_over_band[1]]
    p_rest, law = lv.idle_w(F2, card, T0)
    rb = F2["idle_laws"][card]["rest_band_w"]
    rest, rest_band = p_rest * t_w, [(p_rest - rb) * t_w, (p_rest + rb) * t_w]
    return {"j_total": rest + heat + j_over,
            "j_total_band": [rest_band[0] + heat_band[0] + j_over_band[0], rest_band[1] + heat_band[1] + j_over_band[1]],
            "rest_j": rest, "heat_j": heat, "rest_law": law}


# ------------------------------------------------------------------ v2's own band rules (the rules-off path)
def _v2_scalar_seconds_band(F3, prog, ins, f_mhz):
    """E189's registered two-sided band for scalar code at its clock (forecast_e189.py, plain_record): the fast end every
    instruction but the taken branches and jumps at a lone hart's rate (add, 0.3727 / 0.581), the slow end v2's high
    issue (in-place rates) plus every v2 line past the L1 waited for at the L2's 27.4 G lines/s, unoverlapped."""
    lit = _c(F3, "v2_literals")
    P = prog["participants"]
    f = f_mhz * 1e6
    sp = ins["split"]
    cat = catalogue(prog["card"])
    h_tk = sum(v["count"] / cat.rate(v["row"], "random") for m, v in sp.items() if m in ("@taken", "@jump"))
    h_rest = sum(v["count"] / cat.rate(v["row"], "random") for m, v in sp.items() if m not in ("@taken", "@jump"))
    ratio = lit["h1_over_h2_add"][1] / lit["h1_over_h2_add"][0]
    fast = (h_tk + h_rest * ratio) / P / f
    lines_hi = prog["v2_bytes"]["lines_high"]
    per_minion = lines_hi / (P / 2.0)
    stall = per_minion * (1024 / (lit["l2_lines_per_s"] / f)) / f
    slow = ins["hart_cycles_v2"][1] / f + stall
    return [fast, slow], stall


# ------------------------------------------------------------------ rule 7
def governed(F3, card, f_mhz):
    """(B(f_busy) - B(f_idle), f_idle in Hz) when the card has a registered busy-base relation and f_busy > f_idle."""
    g = _c(F3, "governed_base_w").get(card)
    if not g:
        return None
    f_idle = g["f_idle_mhz"]
    if f_mhz <= f_idle + 1e-9:
        return None
    B = g["B"]
    key = str(int(round(f_mhz)))
    if key not in B:
        raise SystemExit(f"ledger_v3: no busy base for {card} at {f_mhz} MHz")
    return B[key] - B[str(int(f_idle))], f_idle * 1e6


# ------------------------------------------------------------------ the whole ledger, a plain program
def predict(prog, F3, rules=None, f_mhz=None, die_c=None, c_br=None, rdram=None, prices_from=None, t_given=None,
            share7=None, j_idle7=None):
    """One plain program in, v3's forecast out (seconds, J over idle, J with the card at rest, each term with a band).
    rules: the rules on (default all seven; [] is v2). f_mhz: the clock (default the program's). die_c: a forecast die
    other than the rule's. c_br, rdram: constants other than the frozen (the hold-out readings). prices_from: read every
    card-keyed price of rules 2-4 from that card (the stress reading). t_given: the copy's awake term at these seconds
    (the given-seconds reading). share7, j_idle7: rule 7's share of the burst's work at the idle clock and the J over
    idle a launch there, given instead of computed (to reproduce another reading's arithmetic)."""
    R = rules_of(rules)
    card = prog["card"]
    f_mhz = prog.get("f_mhz", 600.0) if f_mhz is None else f_mhz
    f = f_mhz * 1e6
    P = prog["participants"]
    pcard = prices_from or price_card(F3, card, R)
    lit = _c(F3, "v2_literals")
    counts = prog["counts"]
    kind = prog["kind"]
    level, level_why = level_of(F3, prog) if "r3" in R else ("v2", "v2 has no level rule")
    copy_dram = kind == "copy" and level in ("DRAM", "v2")
    outside = level == "outside" or (level == "DRAM" and kind != "copy")
    out = {"program": prog.get("name"), "card": card, "f_mhz": f_mhz, "rules": sorted(R), "level": level,
           "level_why": level_why + ("; scalar code past the L2 has no rule in v3" if level == "DRAM" and kind != "copy"
                                     else ""), "outside_v3": outside, "prices_from": pcard, "terms": {}}
    T = out["terms"]
    # -- instructions (v2's term, unchanged); a DRAM copy's moves are inside its byte prices
    icounts = {k: v for k, v in counts.items() if not (copy_dram and k in MOVES)}
    ins = instr_term(prog, icounts, f_mhz)
    T["instructions"] = {"j": ins["j"], "band": ins["band"], "count": ins["count"],
                         "note": "v2's: catalogue rows, random column, the card's own mean; branches by outcome"
                                 + ("; the copy's moves inside its byte prices" if copy_dram else "")}
    # -- seconds
    secs = {}
    if "r1" in R:
        Th, other = t_hart_v3(F3, prog, counts, c_br=c_br)
        Th_lo, _ = t_hart_v3(F3, prog, counts, c_br=_band(F3, "c_br_hart_cycles")[0])
        Th_hi, _ = t_hart_v3(F3, prog, counts, c_br=_band(F3, "c_br_hart_cycles")[1])
        secs["issue"] = {"t": Th / f, "band": [Th_lo / f, Th_hi / f], "hart_cycles": Th, "how": "r1",
                         "other_classes": other}
    else:
        hc = instr_term(prog, counts, f_mhz)["hart_cycles_v2"]
        secs["issue"] = {"t": hc[0] / f, "band": [hc[0] / f, hc[1] / f], "hart_cycles": hc[0], "how": "v2"}
    lines = prog.get("lines") or {}
    cfill, calloc = (_c(F3, "l2_line_cycles_minion")["fill"], _c(F3, "l2_line_cycles_minion")["alloc"])
    T_l2 = P_MINION * (lines.get("read_fills", 0.0) * cfill + lines.get("write_fills", 0.0) * calloc)
    T_l2_ov = P_MINION * max(lines.get("read_fills", 0.0) * cfill, lines.get("write_fills", 0.0) * calloc)
    nbytes = prog.get("copy", {}).get("bytes", 0.0)
    D = _c(F3, "dram_traffic_bytes_per_byte_copied") * nbytes if copy_dram else 0.0
    Rd = rdram if rdram is not None else r_dram(F3, pcard)
    rows = dram_rows(F3, pcard, prog["copy"]["data"]) if kind == "copy" else None
    if "r2" in R:
        t_issue = secs["issue"]["t"]
        t_l2 = T_l2 / F_REF if not copy_dram else 0.0
        t_dram = D / Rd if D else 0.0
        t = max(t_issue, t_l2, t_dram)
        which = "issue" if t == t_issue else ("L2 lines" if t == t_l2 else "DRAM traffic")
        if copy_dram:
            fast = max(secs["issue"]["band"][0], D / (2.0 * rows["b_wb_b_per_s"]))
            slow = max(secs["issue"]["band"][1], t_dram * _c(F3, "r_dram_b_per_s_slow_factor"))
        elif kind == "copy":          # an L2 copy: E48's two line streams overlapped, to serialized plus issue
            fast = max(secs["issue"]["band"][0], T_l2_ov / F_REF)
            slow = max(secs["issue"]["band"][1], t_l2 + t_issue)
        else:                         # scalar code: the lines waited for unoverlapped at the slow end
            fast = max(secs["issue"]["band"][0], T_l2_ov / F_REF)
            slow = secs["issue"]["band"][1] + T_l2 / F_REF
        secs.update({"l2_lines": {"t": t_l2, "minion_cycles": T_l2}, "dram": {"t": t_dram, "bytes": D, "rate": Rd}})
        out["seconds"] = {"point": t, "band": [min(fast, t), max(slow, t)], "bound_by": which, "parts": secs}
    else:
        if kind == "copy":
            t_lo = nbytes / (lit["store_stream_gb_s"] * 1e9)
            t_hi = t_lo + nbytes / (mods()[2]["constants"]["dram_bandwidth_gb_s"]["value"] * 1e9)
            out["seconds"] = {"point": 0.5 * (t_lo + t_hi), "band": [t_lo, t_hi], "bound_by": "v2's DRAM bracket",
                              "parts": secs}
        else:
            if "r1" in R:
                out["seconds"] = {"point": secs["issue"]["t"], "band": secs["issue"]["band"], "bound_by": "issue",
                                  "parts": secs}
            else:
                band, stall = _v2_scalar_seconds_band(F3, prog, ins, f_mhz)
                out["seconds"] = {"point": secs["issue"]["t"], "band": band, "bound_by": "issue (v2)",
                                  "parts": secs, "v2_l2_wait_s": stall}
    t = out["seconds"]["point"]
    t_aw = t if t_given is None else t_given
    # -- bytes
    if kind == "copy" and copy_dram:
        data = prog["copy"]["data"]
        if "r4" in R:
            v2f = v2_factor(card, f_mhz)
            pst = _c(F3, "p_stall_w") * (f / F_REF) * v2f
            pst_lo, pst_hi = [x * (f / F_REF) * v2f for x in _band(F3, "p_stall_w")]
            bwb = rows["b_wb_b_per_s"]
            aw_t = max(0.0, t_aw - nbytes / bwb)
            # the byte rows unscaled at another clock; their bands' high ends x (V/V600)^2, as rule 3's (1.0 at 600 MHz)
            T["bytes: DRAM read"] = {"j": nbytes * rows["p_tload_pj_b"] * 1e-12,
                                     "band": [nbytes * rows["p_tload_band"][0] * 1e-12,
                                              nbytes * rows["p_tload_band"][1] * 1e-12 * v2f],
                                     "pj_per_byte": rows["p_tload_pj_b"], "note": f"r4: {pcard}'s tload/dram/{data} row"}
            T["bytes: DRAM write-back"] = {"j": nbytes * rows["p_wb_pj_b"] * 1e-12,
                                           "band": [nbytes * rows["p_wb_band"][0] * 1e-12,
                                                    nbytes * rows["p_wb_band"][1] * 1e-12 * v2f],
                                           "pj_per_byte": rows["p_wb_pj_b"], "note": f"r4: {pcard}'s st_stream/dram/{data} row"}
            T["awake, waiting on DRAM"] = {"j": pst * aw_t, "band": [pst_lo * aw_t, pst_hi * aw_t], "w": pst,
                                           "seconds": aw_t, "note": "r4: P_stall for the time past the store probe's own"}
        else:
            F2 = mods()[2]
            mp = F2["mem_paths"]
            ck = CARD_KEY[card]
            if data == "zeros":
                rd = (mp["dram_load"]["zeros_pj"],) + tuple(lit["rd_zeros_band"])
                wr = tuple(lit["wb_zeros"])
            else:
                rd = (mp["dram_load"]["random_pj"][ck],) + tuple(lit["rd_random_band"])
                wr = tuple(lit["wb_random"])
            T["bytes: DRAM read"] = {"j": nbytes * rd[0] * 1e-12, "band": [nbytes * rd[1] * 1e-12, nbytes * rd[2] * 1e-12],
                                     "pj_per_byte": list(rd), "note": "v2: the tensor-load DRAM row by analogy"}
            T["bytes: DRAM write-back"] = {"j": nbytes * wr[0] * 1e-12, "band": [nbytes * wr[1] * 1e-12, nbytes * wr[2] * 1e-12],
                                           "pj_per_byte": list(wr), "note": "v2: the fsw.ps write-back path's literal"}
    elif "r3" in R:
        e_r, e_w = line_prices(F3, pcard)
        lb = F3["constants"]["line_prices_pj"]["band"]
        er_lo, er_hi = [x * 1e-12 for x in lb["e_r"]]
        ew_lo, ew_hi = [x * 1e-12 for x in lb["e_w"]]
        Fl, WB = lines.get("fills", 0.0) * P, lines.get("dirty_evictions", 0.0) * P
        v2f = v2_factor(card, f_mhz)
        T["bytes: lines past the L1"] = {
            "j": Fl * e_r + WB * (e_w - e_r),
            "band": [Fl * er_lo + WB * max(0.0, ew_lo - er_lo), (Fl * er_hi + WB * max(0.0, ew_hi - er_hi)) * v2f],
            "fills": Fl, "dirty_evictions": WB, "e_r_pj": e_r * 1e12, "e_w_pj": e_w * 1e12,
            "note": f"r3: {pcard}'s E48 line prices; level {level}"}
    else:
        vb = prog["v2_bytes"]
        l2 = lit["l2_row_pj_b"]
        T["bytes: L2 (v2)"] = {"j": vb["bytes_point"] * l2[0] * 1e-12, "band": [0.0, vb["bytes_high"] * l2[2] * 1e-12],
                               "note": "v2: bytes past the L1 at the L2 tensor-load row (aifoundry3's literal)"}
    j_over = sum(v["j"] for v in T.values())
    j_band = [sum(v["band"][0] for v in T.values()), sum(v["band"][1] for v in T.values())]
    # -- rule 7: a governed card above its idle clock
    dt_w = 0.0
    out["rule7"] = {"applies": False}
    if "r7" in R:
        g = governed(F3, card, f_mhz)
        if g:
            dB, f_idle = g
            K = (prog.get("governor") or {}).get("launches_a_burst")
            climb = _c(F3, "governor_climb_s")
            bytes_bound = copy_dram
            if share7 is not None:
                s = share7
            elif not K:
                s = 0.0
            elif bytes_bound:
                s = min(1.0, climb / (K * t_aw))
            else:
                s = min(1.0, climb * (f_idle / f) / (K * t_aw))
            idle = predict(prog, F3, rules=R - {"r7"}, f_mhz=f_idle / 1e6, die_c=die_c, c_br=c_br, rdram=rdram,
                           prices_from=prices_from, t_given=t_given)
            j_idle = idle["j_over_idle"] if j_idle7 is None else j_idle7
            jb_idle = idle["j_over_idle_band"] if j_idle7 is None else [j_idle7, j_idle7]
            j7 = (1.0 - s) * (j_over + dB * t_aw) + s * j_idle
            band7 = [(1.0 - s) * (j_band[0] + dB * t_aw) + s * jb_idle[0],
                     (1.0 - s) * (j_band[1] + dB * t_aw) + s * jb_idle[1]]
            if not bytes_bound and K:
                dt_w = climb * (1.0 - f_idle / f) / K
            out["rule7"] = {"applies": True, "delta_base_w": dB, "share_at_idle_clock": s, "launches_a_burst": K,
                            "climb_s": climb, "j_over_idle_before": j_over, "j_at_idle_clock": j_idle,
                            "wall_added_a_launch_s": dt_w,
                            "note": "POST HOC form (chosen after E194); zero on a pinned card"}
            T["governed clock-state base (r7)"] = {"j": j7 - j_over, "band": [band7[0] - j_band[0], band7[1] - j_band[1]]}
            j_over, j_band = j7, band7
    out["j_over_idle"] = j_over
    out["j_over_idle_band"] = j_band
    out["w_over_idle"] = j_over / t
    # -- the card at rest at the forecast die
    if die_c is not None:
        T0 = die_c
    else:
        T0 = _c(F3, "forecast_die_c") if "r5" in R else lit["forecast_die_c"]
    t0_band = _band(F3, "forecast_die_c") if "r5" in R else lit["die_band_c"]
    over = _c(F3, "launch_overhead_s") if "r5" in R else 0.0
    t_w = t + over + dt_w
    tb = out["seconds"]["band"]
    rest, heat = rest_and_heat(card, t_w, [tb[0] + over + dt_w, tb[1] + over + dt_w], j_over, j_band, T0, t0_band)
    out["die_start_c"] = T0
    out["wall_s"] = t_w
    out["rest"] = rest
    out["heat"] = heat
    out["j_total"] = rest["j"] + heat["j"] + j_over
    out["j_total_band"] = [rest["band"][0] + heat["band"][0] + j_band[0], rest["band"][1] + heat["band"][1] + j_band[1]]
    n = prog.get("units")
    if n:
        u = n * P
        out["per_unit"] = {"unit": prog.get("unit", "unit"), "units_a_launch": u, "j_over_idle": j_over / u,
                           "j_total": out["j_total"] / u}
    return out


def given(prog, F3, t_k, t_w, T0, rules=None, f_mhz=None, c_br=None, rdram=None, prices_from=None, share7=None,
          j_idle7=None):
    """The frozen given-seconds forecast (E189's score 1 and 1T): J over idle at the measured kernel seconds t_k (the
    DRAM copy's awake term and rule 7 follow t_k; nothing else does) and J with the card at rest at the measured wall
    seconds a launch t_w and starting die T0."""
    p = predict(prog, F3, rules=rules, f_mhz=f_mhz, c_br=c_br, rdram=rdram, prices_from=prices_from, t_given=t_k,
                share7=share7, j_idle7=j_idle7)
    jr = j_rest_given(prog["card"], p["j_over_idle"], p["j_over_idle_band"], t_w, T0)
    return {"j_over_idle": p["j_over_idle"], "j_over_idle_band": p["j_over_idle_band"], "j_total": jr["j_total"],
            "j_total_band": jr["j_total_band"], "terms": {k: v["j"] for k, v in p["terms"].items()},
            "rule7": p["rule7"], "level": p["level"]}


# ------------------------------------------------------------------ v2 loads (sparse parity and the rest)
def carried(F2, card):
    """frozen-v2.json prices some tensor operand kinds on aifoundry3 only (int8.pm1, sparse parity's: M10 priced it from
    E90's signs tile). On another card such a kind is carried from aifoundry3 unchanged, band unchanged, as E191 and E194
    registered it (their carried()); never edits F2; every other input stays the card's own. Rule 6 cannot change this:
    no other card's entry exists."""
    ck = CARD_KEY[card]
    miss = [k for k, v in F2["kinds"].items() if isinstance(v, dict) and "a3" in v and ck not in v]
    if not miss:
        return F2
    G = dict(F2)
    G["kinds"] = dict(F2["kinds"])
    for k in miss:
        G["kinds"][k] = dict(F2["kinds"][k], **{ck: dict(F2["kinds"][k]["a3"], carried_from="a3")})
    return G


def predict_v2load(load, F3, rules=None, die_c=None, launches_a_burst=None, j_idle7=None):
    """A ledger v2 load (tensor / instr / awake / bytes / mesh: ledger_v2.predict()'s form) at its own seconds: v2's own
    prices, unchanged; r5 moves the forecast die to 50 C and adds the 1.5 ms a launch to the card at rest; r7 adds a
    governed card's base (j_idle7: the same load's J over idle at the idle clock, when it was built there; else the load
    is re-priced at the idle clock). Rules 1-4 and 6 have nothing to change in a v2 load."""
    R = rules_of(rules)
    lv, le, F2 = mods()
    card = load["card"]
    ld = _copy.deepcopy(load)
    lit = _c(F3, "v2_literals")
    if die_c is not None:
        ld["die_start_c"] = die_c
    elif "r5" in R:
        ld["die_start_c"] = _c(F3, "forecast_die_c")
    t = ld["seconds"]
    F2 = carried(F2, card)
    pr = lv.predict(ld, F2)
    j_over, j_band = pr["j_over_idle"], list(pr["j_over_idle_band"])
    out = {"card": card, "rules": sorted(R), "seconds": t, "v2_prediction": pr, "rule7": {"applies": False}}
    dt_w = 0.0
    if "r7" in R:
        g = governed(F3, card, ld.get("f_mhz", 600.0))
        if g:
            dB, f_idle = g
            f = ld.get("f_mhz", 600.0) * 1e6
            climb = _c(F3, "governor_climb_s")
            K = launches_a_burst
            s = min(1.0, climb * (f_idle / f) / (K * t)) if K else 0.0
            if j_idle7 is None:
                idle = _copy.deepcopy(ld)
                idle["f_mhz"] = f_idle / 1e6
                pi = lv.predict(idle, F2)
                ji, jib = pi["j_over_idle"], pi["j_over_idle_band"]
            else:
                ji, jib = j_idle7, [j_idle7, j_idle7]
            j7 = (1.0 - s) * (j_over + dB * t) + s * ji
            j_band = [(1.0 - s) * (j_band[0] + dB * t) + s * jib[0],
                      (1.0 - s) * (j_band[1] + dB * t) + s * jib[1]]
            if K:
                dt_w = climb * (1.0 - f_idle / f) / K
            out["rule7"] = {"applies": True, "delta_base_w": dB, "share_at_idle_clock": s, "launches_a_burst": K,
                            "j_over_idle_before": j_over, "j_at_idle_clock": ji,
                            "wall_added_a_launch_s": dt_w, "note": "POST HOC form (chosen after E194)"}
            j_over = j7
    over = _c(F3, "launch_overhead_s") if "r5" in R else 0.0
    T0 = ld["die_start_c"]
    t_w = t + over + dt_w
    jr = j_rest_given(card, j_over, j_band, t_w, T0)
    out.update({"j_over_idle": j_over, "j_over_idle_band": j_band, "j_total": jr["j_total"],
                "j_total_band": jr["j_total_band"], "die_start_c": T0, "wall_s": t_w,
                "v2_die_c": lit["forecast_die_c"]})
    return out


# ------------------------------------------------------------------ building a program
def program(name, kind, card, counts, participants, units=None, unit=None, f_mhz=600.0, lines=None,
            working_set_b_per_hart=None, copy=None, v2_bytes=None, launches_a_burst=None):
    """A plain program's description (see the module's text). counts: a participant's whole launch, the counter's form."""
    p = {"name": name, "kind": kind, "card": card, "f_mhz": f_mhz, "participants": participants,
         "counts": dict(counts), "units": units, "unit": unit, "lines": dict(lines or {}),
         "working_set_b_per_hart": working_set_b_per_hart}
    if copy:
        p["copy"] = dict(copy)
    if v2_bytes:
        p["v2_bytes"] = dict(v2_bytes)
    if launches_a_burst:
        p["governor"] = {"launches_a_burst": launches_a_burst}
    return p


def widen_s2(band, point, floor=0.15):
    """The design's registration rule for a seconds band: never narrower than S2's own 15% (reg-e201 adopts it or not)."""
    return [min(band[0], (1.0 - floor) * point), max(band[1], (1.0 + floor) * point)]


def both_can_pass(a, b, th):
    """verify5's exclusivity test: two forecasts a <= b can both lie within th of one measurement iff b/a <= (1+th)/(1-th)."""
    lo, hi = min(a, b), max(a, b)
    return hi / lo <= (1.0 + th) / (1.0 - th)


if __name__ == "__main__":
    F3 = load_frozen()
    print(json.dumps({k: F3[k] for k in ("model", "frozen_pst")}, indent=1))
    print("frozen-v3.json sha256", sha256_file(FROZEN_V3))
