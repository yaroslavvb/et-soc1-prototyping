#!/usr/bin/env python3
"""The joined load model: one place that turns a description of a load into board watts, a clock, a die
temperature, a speed and an energy per unit of work.

Q126, 26 Oct 2026. Before this the four pieces lived apart -- the flip model (predict_heat.py, fp32 tiles only),
the instruction-and-byte catalogue (docs/energy-manual/), E60/E61's measured per-flip prices, and E64's governor
-- and a prediction for a new load needed a person to pick the model and apply three corrections by hand.

    P_board(load) = idle(T, card)                     P_fix + leakage(T), re-anchored on E64's 600 MHz floor
                  + B_clk(f)                          the clock-dependent static part (E64's floor by clock)
                  + c0 * s(f)                         a per-kernel offset: paid once while any hart runs
                  + p_sm * (active/1024) * s(f)       the tensor state machines
                  + P_flip(load) * s(f) * k_T * k_card    the four fitted flip prices, zero-gated
                  + P_cat(load) * s(f) * k_card       catalogue rows: instructions, bytes, hops

    s(f, V) = (f / 600) * (V / 0.517)^2               the f*V^2 referral, an ARGUMENT, not a constant
    k_T     = 1 + temp_coeff * (T - T_fit)            switching drifts with die temperature (E45 CAT-a)
    k_card  = the card scale (E38)

Every coefficient is read from a committed file and carries the experiment it came from in COEFF_SOURCES.

E37, E39, E43 and E59 are the held-out loads of docs/reports/data/2026-10-26-load-model/. The first version of
this file said "nothing here is fitted on" them; that was wrong, and the exact list of what does come from them
is HELD_OUT_LEAKS below. None of the three is fitted -- each is a single constant read from the other
experiment's record -- but a held-out test has to name them.

Import it, or run it for the fitted constants:
    /usr/local/bin/python3.12 load_model.py            # print the fit and its residuals
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")

D21 = os.path.join(DATA, "2026-09-21-horace-aifoundry2")
D60 = os.path.join(DATA, "2026-10-20-bitflip-ladder")
D62 = os.path.join(DATA, "2026-10-21-e62-heat-movies")
D64 = os.path.join(DATA, "2026-10-23-e64-horace-power-limit")
DEM = os.path.join(DATA, "2026-09-23-energy-manual")
DV3 = os.path.join(DATA, "2026-09-25-claims-v3", "results")

load = lambda *p: json.load(open(os.path.join(*p)))

# ---------------------------------------------------------------------------- operating points
V_REF = 0.517                       # the volts the 21 Sep fit was taken at (aifoundry2, 600 MHz)
F_OP = 600e6 / 546.0                # TensorFMA32 ops per second per minion at 600 MHz (546 cycles an op)
MAC_OP = 4096                       # multiply-adds in one 16x16x16 op
T_FIT = 80.96                       # the die reading the 21 Sep switching prices were fitted at
T_REF = 58.0                        # the die reading E60 and E64 refer their powers to

# Cards: volts by clock, the card scale, the leakage slope, and what share of the board the minion rail carries.
# volts  : aifoundry2 from surface_hpl.py:31 (E64); aifoundry3 and aifoundry1-c0 from hl.json cards.*.v_mean (E60);
#          aifoundry1-c1 from ablb.runs.json idle_by_card (E39's busy_mv, the only committed figure for that
#          card) -- a HELD_OUT_LEAK, see above: it is E39's own number and it makes E39's prediction worse.
# scale  : E38's switching ratio at a matched die temperature; 1.0 on the card the prices were fitted on.
# leak   : E60 reduce.txt per card; aifoundry3 and aifoundry1 fall back to aifoundry2's.
# idle_offset_w: how far the card idles above aifoundry2's law in the version-3 idle cycles
#                (energy manual §7.1: +1.0 W on aifoundry3, +10.1 W on aifoundry1's card 1).
CARDS = {
    "aifoundry2":    {"volts": {600: 0.5174, 700: 0.568, 800: 0.6174109375}, "scale": 1.000, "leak_w_per_c": 0.442,
                      "rail_share": 0.70, "idle_offset_w": 0.0},
    "aifoundry3":    {"volts": {600: 0.521775},                              "scale": 0.963, "leak_w_per_c": 0.442,
                      "rail_share": 0.75, "idle_offset_w": 1.0},
    "aifoundry1-c0": {"volts": {600: 0.6038674672},                          "scale": 1.000, "leak_w_per_c": 0.442,
                      "rail_share": 0.89, "idle_offset_w": 10.1},
    "aifoundry1-c1": {"volts": {600: 0.4979},                                "scale": 1.000, "leak_w_per_c": 0.442,
                      "rail_share": 0.89, "idle_offset_w": 10.1},
}

MULT_BLOCKS = ("csa", "compressor", "wallace", "booth")
CLASSES = ("ffclk", "mult", "rest", "bus")

COEFF_SOURCES = {
    "e_fJ, P_fix, A_leak, T_L, p_sm": "2026-09-21-horace-aifoundry2/model.json (E17 fit, 14 fp32 patterns)",
    "B(f) floor by clock":            "2026-10-23-e64-horace-power-limit/figures.json fit.B (E64, 103 points)",
    "s(f) referral":                  "E64 figures.json fit.s; same form as tools/claims-v3/hpl/surface_hpl.py:31",
    "c0 per-kernel offset":           "fitted here on E64's B and E62's de-leaked 0-hart intercept",
    "leakage shape":                  "2026-09-25-claims-v3/results/idle.json (E44) aifoundry3 residual bins 55-84 C",
    "bus bit, all-in":                "2026-10-20-bitflip-ladder (E60) reduce.txt lq/lb per bus",
    "read-port bit":                  "E60/E61: 20.83 fJ, used when --pin-bus is given",
    "hart line":                      "2026-10-21-e62-heat-movies/posthoc/cal_ladder.json rungs 1-6",
    "memory levels, relay, rings":    "2026-09-23-energy-manual/reruns.json",
    "instructions":                   "2026-09-23-energy-manual/catalogue.json combined",
    "governor tau, pass":             "E64 figures.json governor",
    "heat path":                      "E64 figures.json thermal (T = a_c + k_c_per_w * P)",
    "card scale":                     "E38 (05-claims.md): aifoundry3 switches 0.958-0.969 of aifoundry2",
}

# What this model takes from the four loads it is scored on. Named here because a held-out test that does not
# name its leaks is not one (found by a check of the first version's blanket "nothing here is fitted on them").
HELD_OUT_LEAKS = {
    "hop_pj_per_byte = 1.753": {
        "from": "E43 RL-a, the pooled mesh slope per hop (finding 20)",
        "reaches": "hop_w() and predict_load.py --hops. NOT any frozen E43 prediction: the relay rows are "
                   "priced from the energy manual's level prices, not from the hop slope.",
        "effect_on_the_score": "none -- no scored number reads it",
    },
    "CARDS['aifoundry1-c1']['volts'] = 0.4979": {
        "from": "E39 ablb.runs.json idle_by_card busy_mv -- the only committed rail voltage for that card",
        "reaches": "every prediction on aifoundry1-c1: E39's own line, E43's third card, E37's third card",
        "effect_on_the_score": "it made E39 WORSE, not better. At this voltage the predicted aifoundry1-c1 "
                               "slope is 14.425 W, -8.60% against the measured 15.782 and the worst number in "
                               "the E39 row; at a neutral 0.517 V it would be 15.553 W, -1.45%.",
    },
    "E59_CYCLES_IDEAL = 280.35": {
        "from": "E37 MMB-a, the measured int8 shared-tile cycles an op",
        "reaches": "freeze_load_predictions.py: it sets E59's tensor duty, and so its tensor term",
        "effect_on_the_score": "the tensor term is 9-14% of each E59 prediction, and E59 misses low by "
                               "13-39%, so the leak cannot be what carries that load.",
    },
}


# ---------------------------------------------------------------------------- the pieces, read from disk
class Constants:
    """Every coefficient, read once from the committed files."""

    def __init__(self):
        m = load(D21, "model.json")["power"]
        self.e_fJ = dict(m["e_fJ"])                 # ffclk 3.1786, mult 0.02504, rest 0.80081, bus 15.539 fJ
        self.P_fix_21 = m["P_fix"]                  # 12.635 W
        self.A_leak_21 = m["A_leak_at_80"]          # 23.257 W at 80 C
        self.T_L_21 = m["T_L"]                      # 36 C e-folding
        self.p_sm = m["p_sm_full_chip"]             # 1.8546 W of tensor state machines at 1,024 minions
        self.rms_21 = m.get("rms")

        f64 = load(D64, "figures.json")
        self.B64 = {int(k): v for k, v in f64["fit"]["B"].items()}
        self.s64 = {int(k): v for k, v in f64["fit"]["s"].items()}
        self.c64 = dict(f64["fit"]["c"])
        self.rms64_own = f64["fit"]["rms_w"]
        self.n64 = f64["fit"]["n"]
        self.gov = dict(f64["governor"])            # tau_s 1.3, pass_s 0.24, rms_mhz 3.3
        self.thermal = dict(f64["thermal"])         # k_c_per_w 0.4696, a_c 41.88
        self.runs64 = f64["runs"]
        self.cap_table = f64["cap_table"]

        # E60: the directly measured all-in price of one flipped operand-bus bit (the whole cascade it sets off).
        self.e_bus_allin_quiet = 74.658e-15         # J, quiet partner A = 1.0
        self.e_bus_allin_busy = 85.578e-15          # J, busy partner A = pi
        self.e_readport = 20.83e-15                 # J, E60/E61's measured register-file read-port bit

        # E62's hart ladder, de-leaked per rung with the card's own leakage slope.
        cal = load(D62, "posthoc", "cal_ladder.json")
        self.e62_idle_board = cal["idle_board_w"]
        self.e62_rungs = [r for r in cal["ladder"] if r["n"] <= 6]
        self.e62_T0 = 49.0                          # the pre-session idle die the ladder's baseline was taken at

        # The catalogue.
        rr = load(DEM, "reruns.json")
        self.levels_pj_per_byte = {k: v["mean"] for k, v in rr["levels_pj_per_byte"].items()}
        self.levels_per_card = {k: {c: x["mean"] for c, x in v.get("per_card", {}).items()}
                                for k, v in rr["levels_pj_per_byte"].items()}
        self.rings_pj_per_byte = {k: v["mean"] for k, v in rr["rings_pj_per_byte"].items()} \
            if "rings_pj_per_byte" in rr else {}
        self.levels_by_contents = rr.get("levels_by_contents_pj_per_byte", {})
        self.catalogue = load(DEM, "catalogue.json")["combined"]

        # E44's idle residuals: aifoundry3's measured idle above the 21 Sep law, by 1 C bin, 55-84 C.
        self.idle_resid_a3 = self._idle_resid()

        self.hop_pj_per_byte = 1.753                # E43 RL-a, pooled mesh slope per hop (finding 20)

    def _idle_resid(self):
        try:
            idl = load(DV3, "idle.json")
        except Exception:
            return {}
        for it in idl["items"]:
            pc = it.get("per_card", {}).get("aifoundry3", {})
            for cyc in pc.get("cycles", []) or []:
                if "resid_by_bin" in cyc:
                    acc = {}
                    for item in idl["items"]:
                        p = item.get("per_card", {}).get("aifoundry3", {})
                        for c in p.get("cycles", []) or []:
                            for b, r in (c.get("resid_by_bin") or {}).items():
                                acc.setdefault(int(b), []).append(r)
                    return {b: sum(v) / len(v) for b, v in sorted(acc.items())}
        return {}


K = Constants()


# ---------------------------------------------------------------------------- the static part
def sfv(f_mhz, volts, v_ref=V_REF):
    """The f*V^2 referral. An argument of the model, not a constant hidden inside it."""
    return (f_mhz / 600.0) * (volts / v_ref) ** 2


def volts_of(card, f_mhz):
    """The card's measured volts at this clock; between measured points, interpolate; outside, hold the end."""
    tbl = CARDS[card]["volts"]
    if f_mhz in tbl:
        return tbl[f_mhz]
    ks = sorted(tbl)
    if len(ks) == 1 or f_mhz <= ks[0]:
        return tbl[ks[0]]
    if f_mhz >= ks[-1]:
        return tbl[ks[-1]]
    for a, b in zip(ks, ks[1:]):
        if a <= f_mhz <= b:
            w = (f_mhz - a) / (b - a)
            return tbl[a] + w * (tbl[b] - tbl[a])
    return tbl[ks[-1]]


def leak_w(T, A=None, T_L=None):
    A = K.A_leak_21 if A is None else A
    T_L = K.T_L_21 if T_L is None else T_L
    return A * math.exp((min(T, 110.0) - 80.0) / T_L)


def fit_leakage(lo=51.0, hi=67.0):
    """Refit the leakage law's A and T_L over a cool band, on aifoundry3's measured idle (E44's residual bins
    above the 21 Sep law). Returns (A, T_L, n_bins, band, rms) or None where no committed bin falls in the band.

    The 21 Sep law was fitted on 64-67 and 81-88 C bins and is read at 58 C under every week-43 number
    (recap item 13). E44's aifoundry3 cycles carry 1 C bins from 55 C up, so the band can be re-fitted from 55 C."""
    pts = [(T, K.P_fix_21 + leak_w(T) + r) for T, r in K.idle_resid_a3.items() if lo <= T <= hi]
    if len(pts) < 4:
        return None
    best = None
    for T_L in [x * 0.5 for x in range(24, 161)]:          # 12 to 80 C e-folding
        # P(T) = P_fix + A*exp((T-80)/T_L): linear in (P_fix, A) at fixed T_L
        xs = [math.exp((T - 80.0) / T_L) for T, _ in pts]
        ys = [p for _, p in pts]
        n = len(xs)
        sx, sy = sum(xs), sum(ys)
        sxx = sum(x * x for x in xs)
        sxy = sum(x * y for x, y in zip(xs, ys))
        den = n * sxx - sx * sx
        if abs(den) < 1e-18:
            continue
        A = (n * sxy - sx * sy) / den
        P0 = (sy - A * sx) / n
        rms = math.sqrt(sum((P0 + A * x - y) ** 2 for x, y in zip(xs, ys)) / n)
        if best is None or rms < best[-1]:
            best = (P0, A, T_L, n, (min(T for T, _ in pts), max(T for T, _ in pts)), rms)
    return best


def fit_static():
    """Fit the static part: the idle anchor at 58 C, the per-kernel offset c0 and the clock-dependent term B_clk.

    Four committed observations, three parameters (so B(700) is one degree of freedom, not a free fit):
      B64(600), B64(700), B64(800)   -- E64's data-independent floor at 1,024 active minions, a 58 C die, a2;
      I62                            -- E62's de-leaked 0-hart intercept at 800 MHz on the same card.
    Model:
      B64(f) = idle58 + k_clk*(s(f)-1) + (c0 + p_sm)*s(f)
      I62    = k_clk*(s(800)-1) + c0*s(800)
    (I62 is measured over the card's own idle, so the idle anchor drops out of it.)

    🛑 I62 IS A FIT TARGET, NOT A PREDICTION. k_clk is solved from the E62 row in closed form at every trial c0
    (the line below), so the fitted model reproduces E62's de-leaked 0-hart intercept to 1e-15 W BY
    CONSTRUCTION. Nothing about E62's intercept is evidence for this model; what is evidence is that the same
    three parameters then reproduce E64's three floors to 0.42 W rms (STATIC['resid_w']), one degree of freedom
    over four observations. scores.json records the identity as e62_rescore['intercept_is_a_fit_target'].
    """
    i62, slope62, _ = fit_hart_line()
    s = {f: K.s64[f] for f in (600, 700, 800)}
    rows = [(s[f], 1.0, K.B64[f], "B64@%d" % f) for f in (600, 700, 800)]
    best = None
    # grid then polish on (idle58, c0); k_clk closed-form from the E62 row at each (c0)
    for c0_m in range(-400, 401):
        c0 = c0_m / 100.0
        k_clk = (i62 - c0 * s[800]) / (s[800] - 1.0)
        res = [(sf, B - (k_clk * (sf - 1.0) + (c0 + K.p_sm) * sf)) for sf, _, B, _ in rows]
        # idle58 is the mean of the residuals (least squares with a free constant)
        idle58 = sum(r for _, r in res) / len(res)
        rms = math.sqrt(sum((r - idle58) ** 2 for _, r in res) / len(res))
        if best is None or rms < best[0]:
            best = (rms, idle58, c0, k_clk)
    rms, idle58, c0, k_clk = best
    resid = {f: K.B64[f] - (idle58 + k_clk * (s[f] - 1.0) + (c0 + K.p_sm) * s[f]) for f in (600, 700, 800)}
    return {"idle58_w": idle58, "c0_w": c0, "k_clk_w": k_clk, "rms_w": rms, "resid_w": resid,
            "e62_intercept_w": i62, "e62_slope_mw_per_hart": slope62 * 1000.0}


def fit_hart_line(leak_k=None, T0=None):
    """E62's calibration ladder, de-leaked per rung: switched_w - k*(die - T0) against harts, rungs 1-6.
    Returns (intercept W, slope W/hart, n). The skeptic's correction: cal_ladder.py:61 does NOT leakage-correct
    switched_w, and the rungs ran 52-61 C against a 49 C idle baseline, so the raw line's offset is inflated."""
    k = CARDS["aifoundry2"]["leak_w_per_c"] if leak_k is None else leak_k
    T0 = K.e62_T0 if T0 is None else T0
    xs = [r["harts"] for r in K.e62_rungs]
    ys = [r["switched_w"] - k * (r["die_c_med"] - T0) for r in K.e62_rungs]
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    return (sy - slope * sx) / n, slope, n


STATIC = fit_static()
LEAK_COOL = fit_leakage(51.0, 67.0)


def idle_w(T, card="aifoundry2", law="e64"):
    """Board watts with nothing running, at a die reading of T.

    law='e64'  : the 21 Sep leakage shape re-anchored so it passes through the fitted idle58 (the default;
                 the 21 Sep law read at 58 C is ~0.6 W above E64's own floor, recap item 13).
    law='21sep': the 21 Sep law as predict_heat.py has always read it.
    law='cool' : the leakage refitted on E44's 51-67 C bins, where committed data allow. The refit is on
                 aifoundry3's OWN measured idle, so it is that card's absolute curve; another card is reached
                 by the difference of the two idle offsets, exactly as the 'e64' branch does. (Until this fix
                 the branch returned aifoundry3's curve for every card: 25.97 W for aifoundry1-c0 at 58 C,
                 where that card idles 8.6 W higher.)

    No published number in docs/reports/data/2026-10-26-load-model/ uses law='cool': the freeze, the scoring
    and predict() all run on 'e64'. It is exposed by predict_load.py --law cool and reported in the README as
    a refit, nothing more.
    """
    off = CARDS.get(card, {}).get("idle_offset_w", 0.0)
    if law == "21sep":
        return K.P_fix_21 + leak_w(T) + off
    if law == "cool" and LEAK_COOL:
        P0, A, T_L = LEAK_COOL[0], LEAK_COOL[1], LEAK_COOL[2]
        off_a3 = CARDS["aifoundry3"]["idle_offset_w"]
        return P0 + A * math.exp((min(T, 110.0) - 80.0) / T_L) + (off - off_a3)
    return STATIC["idle58_w"] + (leak_w(T) - leak_w(T_REF)) + off


def static_w(f_mhz, T, card="aifoundry2", active=1024, volts=None, kernel_offset=None, law="e64"):
    """Everything the card draws at this clock and die temperature with the load's own switching taken out:
    the idle law, the clock-dependent static term, the per-kernel offset and the tensor state machines."""
    v = volts_of(card, f_mhz) if volts is None else volts
    s = sfv(f_mhz, v)
    c0 = STATIC["c0_w"] if kernel_offset is None else kernel_offset
    return (idle_w(T, card, law)
            + STATIC["k_clk_w"] * (s - 1.0)
            + c0 * s
            + K.p_sm * (active / 1024.0) * s)


# ---------------------------------------------------------------------------- the flip part
def flips_from_toggles(tog, pattern):
    """The four counted classes per op, exactly as predict_heat.py reads them."""
    m = tog[pattern]["mean"]
    mult = sum(v for k, v in m["by_block"].items() if any(b in k for b in MULT_BLOCKS))
    return {"ffclk": m["ff_clocked"], "mult": mult, "rest": m["nets"] - mult,
            "bus": m["bus"], "valid": m.get("lane_valid", MAC_OP), "nets": m["nets"]}


def flip_w(flips, active=1024, f_mhz=600.0, volts=None, card="aifoundry2", die_c=T_FIT,
           temp_coeff=0.0, card_scale=None, pin_bus=False, gate="counted", zero_word_frac=0.0,
           e_fJ=None):
    """Switching watts from counted flips.

    flips       : per op and per minion, {'ffclk','mult','rest','bus'} (+ 'valid' lanes of MAC_OP)
    temp_coeff  : the switching drift with die temperature, per C. 0.0 reproduces predict_heat.py; E45 CAT-a
                  puts it at 0.003-0.005 and nobody knows the cause, so it is an argument with a zero default.
    card_scale  : E38's per-card switching scale; defaults to the card's own entry.
    pin_bus     : price the operand-bus class at E60/E61's MEASURED read-port bit (20.83 fJ) instead of the
                  fitted 15.539 fJ (recap item 10: the fitted bus term refits over 2.4x across six fits).
    gate        : 'counted' trusts the bench's own lane_valid; 'hard' zeroes every per-lane class for the
                  zero_word_frac of lanes whose operand word is zero (a zero word gates the lane's clocks).
    """
    v = volts_of(card, f_mhz) if volts is None else volts
    k_T = 1.0 + temp_coeff * (die_c - T_FIT)
    k_c = CARDS[card]["scale"] if card_scale is None else card_scale
    e = dict(K.e_fJ if e_fJ is None else e_fJ)
    if pin_bus:
        e["bus"] = K.e_readport * 1e15
    g = (1.0 - zero_word_frac) if gate == "hard" else 1.0
    # s(f, V) = (f/600) * (V/0.517)^2 enters once: the f/600 as a faster op rate, the V^2 as a dearer event.
    rate = F_OP * (f_mhz / 600.0) * active
    k_v = (v / V_REF) ** 2
    parts = {c: e[c] * flips.get(c, 0.0) * g * rate / 1e15 * k_v * k_T * k_c for c in CLASSES}
    return sum(parts.values()), parts


# ---------------------------------------------------------------------------- the hook for job (b)'s recount
RECOUNT_DIR = os.path.join(DATA, "2026-10-26-toggle-recount")


def recount_counts(path=None):
    """Read job (b)'s recount of the bench's toggles, if it is on main yet; None while the file does not exist,
    so everything here keeps working without it.

    Every per-toggle price in this project is a measured watt divided by one of these counts, and the counters
    disagree. 🛑 THE NUMBERS BELOW ARE THE SETTLED ONES (corrected 26 Oct 2026, Q128(e); this docstring first
    said "the two counters disagree 2.9x ... against the recount's 7,160-7,470", which was the dispute as it
    stood before job (b) finished and before job (e)'s netlist existed):

      * the bench's 21,331 is a count of NAMES under one Verilator, not of wires, and 2.94x of it is a
        counter defect measured inside a single traced run -- 21,297 from the coverage counter against 7,233
        in that same run's own VCD, the whole gap in txfma_csa and txfma_4_2_compressor (8.45x; every other
        module 0.98x). The same bench on the same tiles reads 7,014 under Verilator 5.052;
      * counting each PHYSICAL net once gives 1,301 per random multiply-add (1,325 at a 512-cycle window) --
        job (b)'s figure to quote, and a floor;
      * the open netlist, an independent count on real wires, gives 3,299 unique nets for the whole unit
        (3,623 with the hierarchy kept) -- so two physical counts still disagree 2.5x, which is the live
        dispute, not the 2.9x one;
      * clocked register bits: 595.2 a multiply-add in stream, 71% of this RTL's 838 a lane, against the
        netlist's 1,586 of 1,851, 86%.

    docs/findings/05-claims.md carries each of these with its file and field (Q126(b), Q126(c), Q126(e)).
    A refit on whichever count survives moves the four prices but not the watts, so it is a SECOND,
    separately reported pass, not a change to this one -- scores.json's `toggle_recount_refit` and
    refit_on_recount.json are that pass, and on the 14 measured board powers the deduplicated counts fit
    WORSE than the bench's own.

    EXPECTED SHAPE -- the loosest thing that can be read without guessing:
        {"per_pattern": {"<pattern>": {"ffclk": <per op>, "mult": ..., "rest": ..., "bus": ...}, ...}}
    or a scale per class, applied to the bench's own counts:
        {"scale": {"ffclk": 2.63, "mult": 2.94, "rest": 1.0, "bus": 1.0}}
    Anything else is returned as {"unreadable": why}, and the caller says so rather than guessing.

    WHAT JOB (b) ACTUALLY SHIPPED (26 Oct 2026, commits dc3a5820 and b2e180b9): not counts.json but
    recount.json, 14 patterns x {nets, nets_settled, nets_ids, nets_hier, nets_distinct, ff_clocked, bus,
    by_block_* for each}, plus hier-factors.json. It publishes no four-class split of its own, so
    recount_reading() builds one the same way flips_from_toggles does, and the caller must say which rung of
    job (b)'s ladder it read; the rungs are RUNG_HOW, and RUNG_RETIRED says why 'settled_over_hf' is gone.
    The second pass itself, every rung scored and E60's ladder re-scored under each, is
    docs/reports/data/2026-10-26-load-model/refit_on_recount.json (tools/ettelem/refit_on_recount.py).
    """
    p = path or os.path.join(RECOUNT_DIR, "counts.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    if "per_pattern" in d or "scale" in d:
        return d
    return {"unreadable": f"{p} has neither 'per_pattern' nor 'scale'; see load_model.recount_counts"}


RUNG_HOW = {
 "settled": "recount.json nets_settled, split by by_block_settled: one count per RTL NAME, after the "
            "settling window drops the transient values Verilator's coverage counter keeps",
 "ids": "recount.json nets_ids: once per VCD identifier, names that share a waveform object merged",
 "hier": "per pattern, nets_hier as the total with the SHARES taken from by_block_settled -- job (b)'s "
         "corrected recipe, applied pattern by pattern",
 "hier_one_factor": "by_block_settled scaled by ONE factor for the whole unit, hier-factors.json _total "
                    "(5.327 settled names per merged net on randn) -- job (b)'s corrected recipe read "
                    "literally, 'scale the whole unit by one factor'",
 "distinct": "per pattern, nets_distinct as the total, shares from by_block_settled: once per distinct "
             "waveform, job (b)'s LOWER BOUND on the physical count",
 "distinct_one_factor": "by_block_settled scaled by ONE factor, randn's nets_settled / nets_distinct",
 "hier_by_block": "by_block_hier straight. KEPT ONLY FOR THE RECORD: this is what the first pass read, "
                  "and hier-factors.json now says a net is credited to the OUTERMOST module that names "
                  "it, so by_block_hier is not a per-block net count. It is what made the multiplier "
                  "price come out negative",
}
RUNG_RETIRED = {
 "settled_over_hf": "retired. hier-factors.json's own _how_to_use now says: 'Do NOT divide "
                    "by_block_settled by the per-module factors below' -- 12 of the 40 switching modules "
                    "hold no merged net at all and carry a null factor, and 7 more are attribution "
                    "artefacts. Use 'hier_one_factor', which is the recipe that file gives instead.",
}


def recount_reading(rung="hier_one_factor", directory=None):
    """Job (b)'s recount.json read into the four classes, at one rung of its ladder. None if it is not here.

    Returns {"per_pattern": {...}, "rung": ..., "how": ...} so refit_prices() can take it directly. The split
    is this file's, not job (b)'s: job (b) measured counts, it did not price them.

    🛑 THE SHARES COME FROM by_block_settled, ALWAYS. Job (b)'s d1059a8e measured what by_block_hier is: a
    net is credited to the OUTERMOST module that names it, so the multiplier's share reads 54.8% of
    by_block_settled but 22.8% of by_block_hier on randn and 0.0% on pow2 and signs. A least-squares fit over
    patterns whose multiplier column collapses to zero for an attribution reason has nothing left to fit,
    which is where the first pass's negative multiplier price (-1.769 fJ) came from. The rung chooses the
    TOTAL only; 'hier_by_block' reproduces the old reading and is kept to show the difference."""
    d = directory or RECOUNT_DIR
    rc_p = os.path.join(d, "recount.json")
    if not os.path.exists(rc_p):
        return None
    if rung in RUNG_RETIRED:
        return {"unreadable": f"rung {rung!r} is {RUNG_RETIRED[rung]}"}
    if rung not in RUNG_HOW:
        return {"unreadable": f"unknown rung {rung!r}; use one of {', '.join(RUNG_HOW)}"}
    rc = json.load(open(rc_p))
    hf_p = os.path.join(d, "hier-factors.json")
    hf_total = None
    if os.path.exists(hf_p):
        hf_total = json.load(open(hf_p)).get("_total")
    if rung == "hier_one_factor" and not hf_total:
        return {"unreadable": f"{hf_p} has no _total, so the hier_one_factor rung cannot be built"}
    d2d = None
    if rung == "distinct_one_factor":
        rm = (rc.get("randn") or {}).get("mean") or {}
        if not rm.get("nets_distinct"):
            return {"unreadable": "recount.json has no randn.mean.nets_distinct for the single factor"}
        d2d = rm["nets_settled"] / rm["nets_distinct"]
    out = {}
    for pat, v in rc.items():
        m = v.get("mean") or {}
        if rung == "hier_by_block":
            bb, tot = m.get("by_block_hier"), m.get("nets_hier")
            if bb is None or tot is None:
                return {"unreadable": f"recount.json[{pat!r}].mean has no by_block_hier/nets_hier"}
            mult = sum(x for k, x in bb.items() if any(b in k for b in MULT_BLOCKS))
        else:
            bbs = m.get("by_block_settled")
            if bbs is None:
                return {"unreadable": f"recount.json[{pat!r}].mean has no by_block_settled"}
            names = sum(bbs.values())
            share = (sum(x for k, x in bbs.items() if any(b in k for b in MULT_BLOCKS)) / names
                     if names else 0.0)
            settled = m.get("nets_settled")
            if rung == "settled":
                tot = settled
            elif rung == "ids":
                tot = m.get("nets_ids")
            elif rung == "hier":
                tot = m.get("nets_hier")
            elif rung == "distinct":
                tot = m.get("nets_distinct")
            elif rung == "hier_one_factor":
                tot = None if settled is None else settled / hf_total
            else:                                           # distinct_one_factor
                tot = None if settled is None else settled / d2d
            if tot is None:
                return {"unreadable": f"recount.json[{pat!r}].mean has no total for rung {rung!r}"}
            mult = share * tot
        out[pat] = {"ffclk": m["ff_clocked"], "mult": mult, "rest": tot - mult, "bus": m["bus"]}
    return {"per_pattern": out, "rung": rung, "how": RUNG_HOW[rung],
            "source": os.path.relpath(rc_p, REPO),
            "caveat": "the four-class split is load_model's, not job (b)'s: job (b) counts toggles and "
                      "publishes no price classes."}


def _lsq(A, b):
    """Normal equations, Gauss-Jordan. Small and well conditioned here."""
    n = len(A[0])
    M = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(n)]
         + [sum(A[k][i] * b[k] for k in range(len(A)))] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        d = M[i][i]
        M[i] = [x / d for x in M[i]]
        for r in range(n):
            if r != i and M[r][i]:
                f = M[r][i]
                M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return [M[i][n] for i in range(n)]


def refit_prices(measured_board_w, idle_w, counts=None, active=1024, f_mhz=600.0, volts=V_REF,
                 kernel_offset=None):
    """Refit the four per-event prices on measured board powers; the hook job (b)'s recount plugs into.

    measured_board_w : {pattern: W}.  idle_w : the measured idle those launches sat on.
    counts           : None for the bench's own counts, or recount_counts()/recount_reading()'s dict.
    kernel_offset    : the per-kernel offset subtracted into the base. 🛑 THIS MATTERS A LOT. The design
                       matrix is four flip-rate columns and NO constant column, so a constant put into `base`
                       is NOT absorbed harmlessly -- the four prices have to take it up through regressors
                       that cannot represent a constant. On the 14 fp32 patterns, c0 = 0 gives a leave-one-out
                       of 0.458 W and a bus price of 16.09 fJ (reproducing the published 21 Sep fit), while
                       c0 = -1.18 W gives 0.739 W and 25.34 fJ. Pass 0.0 to fit on the base the published
                       prices were fitted on; pass STATIC['c0_w'] (the default) to ask what the joined model's
                       offset does to them. Both are reported in scores.json.
    Returns {prices_fJ, in_sample_rms_w, leave_one_out_rms_w, counts_used, base_w, kernel_offset_w}.
    """
    tog = load(D21, "toggles.json")
    pats = list(measured_board_w)

    def row(pat):
        if counts and "per_pattern" in counts and pat in counts["per_pattern"]:
            fl = counts["per_pattern"][pat]
        else:
            fl = flips_from_toggles(tog, pat)
            if counts and "scale" in counts:
                fl = {c: fl[c] * counts["scale"].get(c, 1.0) for c in CLASSES}
        r = F_OP * (f_mhz / 600.0) * active * (volts / V_REF) ** 2 / 1e15
        return [fl[c] * r for c in CLASSES]

    c0 = STATIC["c0_w"] if kernel_offset is None else kernel_offset
    base = c0 + K.p_sm + idle_w
    A = [row(p) for p in pats]
    b = [measured_board_w[p] - base for p in pats]
    e = _lsq(A, b)
    ins = [sum(a * x for a, x in zip(A[i], e)) + base - measured_board_w[pats[i]] for i in range(len(pats))]
    loo = []
    for i in range(len(pats)):
        ei = _lsq([A[j] for j in range(len(pats)) if j != i], [b[j] for j in range(len(pats)) if j != i])
        loo.append(sum(a * x for a, x in zip(A[i], ei)) + base - measured_board_w[pats[i]])
    n = len(pats)
    return {"prices_fJ": dict(zip(CLASSES, e)),
            "in_sample_rms_w": math.sqrt(sum(x * x for x in ins) / n),
            "leave_one_out_rms_w": math.sqrt(sum(x * x for x in loo) / n),
            "kernel_offset_w": c0, "base_w": base,
            "counts_used": (counts.get("rung", "job (b)'s recount") if counts else "the bench's own counts")}


# ---------------------------------------------------------------------------- the catalogue part
def mem_w(bytes_per_s, level, card="aifoundry2", f_mhz=600.0, volts=None, card_scale=None):
    """Watts to move bytes through one level of the hierarchy, from the energy manual's measured pJ per byte.
    Levels: l1, l2, l3, dram, scp-local, scp-remote. Per card where the manual gives a per-card figure.

    Returns (watts, pJ per byte, per_card). `per_card` is True when the price is this card's OWN measurement,
    in which case the caller must NOT also apply the card's switching scale -- the card is already in the
    number. predict() used to multiply both, so a catalogue row on aifoundry3 came out 3.7% low."""
    own = K.levels_per_card.get(level, {}).get(card)
    pj = own or K.levels_pj_per_byte[level]
    return bytes_per_s * pj * 1e-12, pj, bool(own)


def hop_w(bytes_per_s, hops, card="aifoundry2"):
    """Watts to carry bytes `hops` mesh hops (E43's pooled per-hop slope, 1.753 pJ/B per hop).
    Pooled over the three cards, so the caller DOES apply the card scale. See HELD_OUT_LEAKS."""
    return bytes_per_s * hops * K.hop_pj_per_byte * 1e-12


def instr_pj(name, values="random", harts="h2", card=None):
    """One instruction's measured pJ per op from the catalogue (392 rows: op/values/harts)."""
    row = K.catalogue.get(f"{name}/{values}/{harts}")
    if row is None:
        return None
    if card and card in row.get("per_card", {}):
        return row["per_card"][card]["mean"]
    return row["mean"]


def instr_w(ops_per_s, name, values="random", harts="h2", card=None):
    """Returns (watts, pJ per op, per_card). As in mem_w, a per-card price already carries the card, so the
    caller must not apply the card's switching scale on top of it."""
    row = K.catalogue.get(f"{name}/{values}/{harts}")
    own = bool(card and row and card in row.get("per_card", {}))
    pj = instr_pj(name, values, harts, card)
    return (None if pj is None else ops_per_s * pj * 1e-12), pj, own


# ---------------------------------------------------------------------------- the governor and the heat path
PTS = (600, 700, 800)


def governor(p_by_clock, tdp_w=65.0, tau_s=None, pass_s=None, t_end=6.5, t_from=1.5, start_avg=24.0,
             ramp_at=0.4):
    """E64's governor, as its trace shows it: once a pass it compares a running average of board power with the
    TDP and steps one point down if over, one up if under. Returns the mean clock in MHz from t_from to t_end.
    Same arithmetic as tools/claims-v3/hpl/surface_hpl.py:simulate (that script's fit: tau 1.3 s, pass 0.24 s,
    3.3 MHz rms over 26 runs)."""
    tau = K.gov["tau_s"] if tau_s is None else tau_s
    dt = K.gov["pass_s"] if pass_s is None else pass_s
    k = PTS.index(600)
    avg, t, acc, n, climbing = start_avg, 0.0, 0.0, 0.0, True
    while t < t_end:
        if t >= ramp_at:
            if climbing:
                if avg > tdp_w or k >= 2:
                    climbing = False
                else:
                    k += 1
            else:
                if avg > tdp_w and k > 0:
                    k -= 1
                elif avg < tdp_w and k < 2:
                    k += 1
        f = PTS[k]
        avg += (p_by_clock[f] - avg) * (1 - math.exp(-dt / tau))
        if t >= t_from:
            acc += f
            n += 1
        t += dt
    return acc / n if n else None


def die_steady_c(p_board_w):
    """The die reading a sustained board power settles at (E64's thermal line on aifoundry2's cooling)."""
    return K.thermal["a_c"] + K.thermal["k_c_per_w"] * p_board_w


def solve_die_c(p_of_T, T0=58.0, iters=60):
    """Close the loop between power and temperature: leakage raises power, power raises the die."""
    T = T0
    for _ in range(iters):
        T_new = die_steady_c(p_of_T(T))
        if abs(T_new - T) < 1e-4:
            return T_new
        T += 0.5 * (T_new - T)
    return T


# ---------------------------------------------------------------------------- the rate model
OPS_PER_TENSOR_OP = {"fp32": 8192, "fp16": 16384, "int8": 32768}     # FLOP or OP in one 16x16x16 op
CYCLES_PER_TENSOR_OP = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}  # as issued; mmbench's int8 runs 280.35


def tensor_rate(kind, f_mhz, active=1024, cycles_per_op=None, duty=1.0):
    """Tera-(FL)OP per second from the clock, the active minions and the cycles an op actually takes."""
    cyc = CYCLES_PER_TENSOR_OP[kind] if cycles_per_op is None else cycles_per_op
    return active * OPS_PER_TENSOR_OP[kind] / cyc * f_mhz * 1e6 / 1e12 * duty


# ---------------------------------------------------------------------------- the whole thing
def predict(load):
    """One load in, watts / clock / die / speed / energy per unit of work out.

    `load` is a dict:
      card, f_mhz (or 'governor': tdp_w), volts, die_c (or 'cooling': True to solve the heat path),
      active, kernel ('tensor'|'other'), kind ('fp32'|'fp16'|'int8'),
      flips {...} or c_w (a measured switching coefficient at 600 MHz / 0.517 V),
      duty (the share of the time the tensor unit is issuing),
      harts, zero_word_frac, temp_coeff, card_scale, pin_bus, kernel_offset,
      bytes_per_s {level: B/s}, hops [(B/s, hops)], instrs [(ops/s, name, values, harts)],
      work_per_s (units of work a second) and work_unit (what a unit is).
    """
    card = load.get("card", "aifoundry2")
    active = load.get("active", 1024)
    temp_coeff = load.get("temp_coeff", 0.0)
    scale = load.get("card_scale")
    law = load.get("law", "e64")
    k_off = load.get("kernel_offset")

    def board_at(f_mhz, T):
        v = load.get("volts") or volts_of(card, f_mhz)
        s = sfv(f_mhz, v)
        k_c = CARDS[card]["scale"] if scale is None else scale
        p = static_w(f_mhz, T, card, active, v, k_off, law)
        sw = 0.0
        if load.get("flips"):
            w, _ = flip_w(load["flips"], active, f_mhz, v, card, T, temp_coeff, scale,
                          load.get("pin_bus", False), load.get("gate", "counted"),
                          load.get("zero_word_frac", 0.0))
            sw += w * load.get("duty", 1.0)
        if load.get("c_w") is not None:
            sw += load["c_w"] * s * (1.0 + temp_coeff * (T - T_REF)) * k_c * load.get("duty", 1.0)
        # A catalogue price that is the card's OWN measurement already carries the card: scaling it again by
        # k_c double-counts. Only a pooled price takes the scale.
        for level, bps in (load.get("bytes_per_s") or {}).items():
            w, _, own = mem_w(bps, level, card)
            k = 1.0 if own else k_c
            sw += w * k * (s / sfv(600.0, V_REF) if load.get("scale_cat_with_clock") else 1.0)
        for bps, hops in (load.get("hops") or []):
            sw += hop_w(bps, hops, card) * k_c        # E43's hop slope is pooled over the cards
        for ops, name, values, h in (load.get("instrs") or []):
            w, _, own = instr_w(ops, name, values, h, card if load.get("per_card_instr") else None)
            if w:
                sw += w * (1.0 if own else k_c)
        return p + sw

    tdp = load.get("tdp_w")
    f_set = load.get("f_mhz", 600.0)
    T = load.get("die_c", T_REF)

    if load.get("cooling"):
        T = solve_die_c(lambda t: board_at(f_set, t), T)

    mhz = f_set
    if tdp:
        pbc = {f: board_at(f, T) for f in PTS}
        mhz = governor(pbc, tdp)
    p = board_at(mhz, T)

    out = {"board_w": p, "clock_mhz": mhz, "die_c": T,
           "static_w": static_w(mhz, T, card, active, load.get("volts"), k_off, law),
           "idle_w": idle_w(T, card, law)}
    out["switching_w"] = p - out["static_w"]
    if load.get("kind"):
        out["rate_t"] = tensor_rate(load["kind"], mhz, active, load.get("cycles_per_op"), load.get("duty", 1.0))
    wps = load.get("work_per_s")
    if wps:
        out["work_unit"] = load.get("work_unit", "unit")
        out["energy_per_work_j"] = p / wps
        out["energy_per_work_over_idle_j"] = (p - out["idle_w"]) / wps
    return out


# ---------------------------------------------------------------------------- self-report
def main():
    print("=" * 100)
    print("THE JOINED LOAD MODEL -- fitted constants, all from committed files")
    print("=" * 100)
    i62, s62, n62 = fit_hart_line()
    raw_i, raw_s, _ = fit_hart_line(leak_k=0.0)
    print(f"E62 hart line, raw            : {raw_i:6.3f} W + {raw_s*1000:5.2f} mW/hart   (published 5.80 + 55.8)")
    print(f"E62 hart line, de-leaked k=.442: {i62:6.3f} W + {s62*1000:5.2f} mW/hart   over {n62} rungs")
    s800 = K.s64[800]
    ident = STATIC["k_clk_w"] * (s800 - 1.0) + STATIC["c0_w"] * s800
    print(f"  ^ this intercept is a FIT TARGET: k_clk*(s800-1) + c0*s800 = {ident:.6f} W against "
          f"{i62:.6f} W, residual {ident - i62:.1e} W. It is matched by construction and is not evidence.")
    print()
    print(f"idle anchor at {T_REF:.0f} C        : {STATIC['idle58_w']:.3f} W   "
          f"(the 21 Sep law reads {K.P_fix_21 + leak_w(T_REF):.3f} W there, "
          f"{K.P_fix_21 + leak_w(T_REF) - STATIC['idle58_w']:+.3f} W)")
    print(f"per-kernel offset c0          : {STATIC['c0_w']:+.3f} W at 600 MHz / 0.517 V")
    print(f"clock-dependent static k_clk  : {STATIC['k_clk_w']:.3f} W per unit of (s(f) - 1)")
    print(f"static fit rms over 4 points  : {STATIC['rms_w']:.3f} W; residuals " +
          ", ".join(f"{f} MHz {r:+.3f} W" for f, r in STATIC["resid_w"].items()))
    print("  (4 observations, 3 parameters, 1 degree of freedom. The E62 row is matched exactly; the "
          "evidence is the 3 E64 floors above.)")
    print()
    for f in PTS:
        print(f"  B({f}) model {static_w(f, T_REF, 'aifoundry2', 1024):7.3f} W   "
              f"E64 measured {K.B64[f]:7.3f} W   err {static_w(f, T_REF, 'aifoundry2', 1024) - K.B64[f]:+.3f} W")
    print()
    if LEAK_COOL:
        P0, A, T_L, n, band, rms = LEAK_COOL
        print(f"leakage refitted on E44's aifoundry3 bins {band[0]:.0f}-{band[1]:.0f} C ({n} bins): "
              f"P_fix {P0:.3f} W, A(80 C) {A:.3f} W, e-fold {T_L:.1f} C, rms {rms:.4f} W")
        print(f"  against the 21 Sep law P_fix {K.P_fix_21:.3f}, A {K.A_leak_21:.3f}, e-fold {K.T_L_21:.1f} C")
        print(f"  local slope at 58 C: refit {A/T_L*math.exp((58-80)/T_L):.4f} W/C, "
              f"21 Sep {K.A_leak_21/K.T_L_21*math.exp((58-80)/K.T_L_21):.4f} W/C, "
              f"E60 measured on aifoundry2 at 800 MHz 0.442 W/C")
    else:
        print("leakage: no committed idle bin in 51-67 C")
    print()
    print("flip prices (fJ): " + ", ".join(f"{c} {K.e_fJ[c]:.4f}" for c in CLASSES) +
          f"; pinned bus {K.e_readport*1e15:.2f} (E60/E61 read-port bit)")
    print(f"governor: tau {K.gov['tau_s']} s, pass {K.gov['pass_s']} s, {K.gov['rms_mhz']} MHz rms over "
          f"{K.gov['n']} runs")
    print(f"heat path: die = {K.thermal['a_c']:.2f} + {K.thermal['k_c_per_w']:.4f} * board W")
    print(f"levels pJ/B: " + ", ".join(f"{k} {v:.3f}" for k, v in sorted(K.levels_pj_per_byte.items())))
    print(f"catalogue rows: {len(K.catalogue)}")
    print()
    print("what this model takes from the four held-out loads (HELD_OUT_LEAKS):")
    for k, v in HELD_OUT_LEAKS.items():
        print(f"  {k}: from {v['from']}")
        print(f"    reaches {v['reaches']}")
        print(f"    effect on the score: {v['effect_on_the_score']}")


if __name__ == "__main__":
    main()
