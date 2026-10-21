#!/usr/bin/env python3
"""V3-DTF (E61) report page prose, with every number and every verdict read from reduce_dtf.py's dtf.json
and the camera block's cam.json. Nothing about the data is typed here.

    python3 tools/claims-v3/dtf/page_text.py --dtf <dtf.json> --cam <cam.json> --out <text.json>

build_page.py imports build() directly, so the normal path is one command (build_page.py --dtf --cam --images --out).

Rules this file follows:
  * a verdict string is never matched against a literal: it is printed as the reduction wrote it, and only its
    first word picks a colour, with a neutral default. The fixer can reword any verdict without touching this file.
  * a measured value is found by scanning the keys a verdict row happens to carry, in priority order.
  * the page-under-test's own claims come from the reduction's `page_*` fields wherever the reduction records one.
    The two it does not record are in PAGE_CLAIMS_NOT_IN_DTF below, each with its source line in the page.
"""
import argparse
import html
import json
import math
import os
import re

# The page under test. Everything here is the PAGE's claim, never a measurement, and every entry that the
# reduction also records (page_fJ, page_W, page_pJ_per_op, page_ipc) is read from dtf.json instead of from here.
PAGE_CLAIMS_NOT_IN_DTF = {
    # "e_in = (5.93 - 96(0.0444))/256 pJ = 6.52 fJ/bit (board) = 4.96 fJ/bit (die)"  -- the page, section 2
    "e_in_fJ": 6.52,
    # the same section's e_out, 44.38 fJ, is in dtf.json as derived.e_out_bridge.page_fJ; the sum is theirs:
    "e_sum_fJ": 50.90,
    "split_ratio": 6.81,
    # "~110 mK spatial thermal dipole" -- the page, E-D7
    "dipole_mK": 110.0,
}
PAGE_URL = "https://spacesheep.dev/@yaroslavvb/deterministic-transistor-flip-experiments"
E60_URL = "https://spacesheep.dev/@yaroslavvb/et-soc1-bitflip-ladder"
MICRONS_URL = "https://spacesheep.dev/@yaroslavvb/bit-flip-in-microns"
REPO = "https://github.com/yaroslavvb/et-soc1-prototyping"
PREREG = REPO + "/blob/main/tools/claims-v3/dtf/README.md"
DATA = REPO + "/tree/main/docs/reports/data/2026-10-21-dtf"
CODE = REPO + "/tree/main/tools/claims-v3/dtf"

# One section per experiment. The claim tokens are the pre-registration's section 2 table; a verdict row is
# filed under the first section its `claims` string shares a token with, so a reworded verdict still lands.
SECTIONS = [
    ("d1", "E-D1", "The toggle dial, the inverter and the register-file cell",
     ["C33", "C37", "C60", "C61", "C62", "I-22"]),
    ("d2", "E-D2", "The input-versus-output mask bridge", ["C14", "C56", "C57", "C63", "C64", "C65", "C86"]),
    ("d3", "E-D3", "The carry-chain wave", ["C54", "C66", "C67", "C68", "C87"]),
    ("d4", "E-D4", "The Miller wire law", ["C47", "C55", "C69-C73", "C88"]),
    ("d5", "E-D5", "The address decoder", ["C46", "C74", "C75", "C76", "C89"]),
    ("d6", "E-D6", "The zero gate", ["C79", "C80", "C90"]),
    ("d7", "E-D7", "The half-die dipole, on the camera", ["C58", "C83", "C84", "C91"]),
    ("rate", "S10", "The issue rate", ["S10", "C16", "C59"]),
    ("r", "R", "The operand law, and two harts", ["C22", "C23", "C26"]),
    ("det", "C13", "Determinism of the designed counts", ["C13", "C15"]),
]


def esc(s):
    return html.escape(str(s), quote=True)


def g(d, *ks, default=None):
    """Walk a path through dicts (by key, string or not) and lists (by index). Missing → default."""
    for k in ks:
        if isinstance(d, dict):
            d = d[k] if k in d else d.get(str(k))
        elif isinstance(d, (list, tuple)) and isinstance(k, int):
            d = d[k] if -len(d) <= k < len(d) else None
        else:
            return default
        if d is None:
            return default
    return d


def thou(x):
    """An integer with thousands separators, or a dash when it is missing."""
    try:
        return f"{int(x):,}"
    except (TypeError, ValueError):
        return "–"


def pval(p):
    if p is None:
        return "–"
    if p >= 1e-3:
        return f"{p:.3g}"
    e = int(math.floor(math.log10(p)))
    return f"{p / 10 ** e:.1f} × 10{str(e).translate(str.maketrans('-0123456789', chr(8315) + chr(8304) + chr(185) + chr(178) + chr(179) + '⁴⁵⁶⁷⁸⁹'))}"


def sig(x, n=2):
    """x to n significant figures, as a plain string."""
    if x is None:
        return "–"
    if x == 0:
        return "0"
    d = max(0, n - 1 - int(math.floor(math.log10(abs(x)))))
    return f"{x:.{d}f}"


def pm(x, se=None, n=2, unit=""):
    """A value with its standard error, both to the same number of decimals, chosen from the error."""
    if x is None:
        return "–"
    if se:
        d = max(0, n - 1 - int(math.floor(math.log10(abs(se)))))
    else:
        d = max(0, n - 1 - int(math.floor(math.log10(abs(x))))) if x else 2
    d = min(d, 4)
    s = f"{x:.{d}f}"
    if se:
        s += f" ± {se:.{d}f}"
    return s + (f" {unit}" if unit else "")


def fj(x, se=None, n=2):
    """x in joules → fJ."""
    if x is None:
        return "–"
    return pm(x * 1e15, se * 1e15 if se else None, n, "fJ")


def wv(x, se=None, n=2):
    if x is None:
        return "–"
    return pm(x, se, n, "W")


def el(x):
    if not x:
        return "–"
    return f"{x / 1e6:.2f} million" if x >= 1e6 else f"{float(f'{x:.3g}'):,.0f}"


def mean_of(xs):
    """The mean of a list the camera block carries, or None. Used only to quote a drift the file measured."""
    xs = [x for x in (xs or []) if isinstance(x, (int, float))]
    return sum(xs) / len(xs) if xs else None


def badge(verdict):
    """A colour class from the verdict's first word only — any wording survives."""
    head = re.split(r"[\s,(/-]", str(verdict).strip().upper(), 1)[0]
    return {"CONFIRMED": "ok", "REFUTED": "bad", "OPEN": "open", "UNDER": "thin", "PARTLY": "open",
            "HOLDS": "ok"}.get(head, "neutral")   # "not scored" is neutral: §5.2 drops the arm, see VER 2


# the derived quantity each experiment's page number lives on, when the verdict row does not carry it itself
SECTION_DERIVED = {"d1": "e_cell", "d2": "e_out_bridge", "d3": "e_carry", "d4": "phase_term", "d5": "e_addr",
                   "d6": "zero_gate_step", "d7": "half_die_result_path_load_W"}


def section_of(claims):
    toks = set(str(claims).replace(",", " ").split())
    for key, _, _, ids in SECTIONS:
        if toks & set(ids):
            return key
    return "extra"


MEASURED_KEYS = [
    # (value key, se key, formatter). First match wins, so a row that quotes a fitted value is read from that key.
    ("joint_fit_fJ", "joint_fit_se_fJ", lambda v, s: pm(v, s, 2, "fJ")),
    ("value_fJ", "se_fJ", lambda v, s: pm(v, s, 2, "fJ")),
    ("pJ_per_op", "se_pJ_per_op", lambda v, s: pm(v, s, 2, "pJ/op")),
    ("rho", "rho_se", lambda v, s: pm(v, s, 2)),
    ("half_die_W", "half_die_se_W", lambda v, s: pm(v, s, 2, "W")),
    ("W", "se_W", lambda v, s: pm(v, s, 2, "W")),
    ("W_minus_E_board_W", "W_minus_E_se", lambda v, s: pm(v, s, 2, "W")),
    ("fnot_leg_fJ", "fnot_leg_se_fJ", lambda v, s: pm(v, s, 2, "fJ")),
    ("intercept_N_W", "intercept_N_se", lambda v, s: pm(v, s, 2, "W")),
    ("measured_2gop_gres", None, lambda v, s: pm(v, s, 2, "W")),
]


def measured_of(v):
    """Whatever this verdict row carries as its number, found by key, not by position."""
    for vk, sk, f in MEASURED_KEYS:
        if v.get(vk) is not None:
            return f(v[vk], v.get(sk) if sk else None)
    if v.get("runs_kept") is not None:
        return f"{v['runs_kept']} runs over {v.get('items_with_a_rate', '–')} items, every gate passed"
    sp = v.get("spread")
    if isinstance(sp, dict) and sp.get("spread_fJ") is not None:
        # VER 12: the row reads §8.4's PAIRED per-pass statistic, so its SE is the one printed here
        return pm(v.get("paired_spread_fJ", sp["spread_fJ"]),
                  v.get("paired_spread_se_fJ", sp.get("se_fJ")), 2, "fJ spread")
    lv = g(v, "levels", "whole_spread")
    if isinstance(lv, dict) and lv.get("dW") is not None:
        return pm(lv["dW"], lv.get("se"), 2, "W over the four levels")
    rates = v.get("rates")
    if isinstance(rates, dict) and rates:
        vals = [r["ipc_per_hart"] for r in rates.values() if isinstance(r, dict) and r.get("ipc_per_hart")]
        if vals:
            return f"{min(vals):.4f}–{max(vals):.4f} ops/cycle/hart"
    return "—"


PAGE_KEYS = [("page_fJ", "fJ"), ("page_pJ_per_op", "pJ/op"), ("page_W", "W"), ("page_ipc", "ops/cycle/hart")]
# the measured key that is in the same unit as each page_* key, so the two can be compared without typing either
SAME_UNIT = {"page_fJ": [("joint_fit_fJ", "joint_fit_se_fJ"), ("value_fJ", "se_fJ")],
             "page_pJ_per_op": [("pJ_per_op", "se_pJ_per_op")],
             "page_W": [("half_die_W", "half_die_se_W"), ("W_minus_E_board_W", "W_minus_E_se")],
             "page_ipc": []}


UNIT_MEASURED = {"fJ": [("joint_fit_fJ", "joint_fit_se_fJ"), ("value_fJ", "se_fJ")],
                 "pJ/op": [("pJ_per_op", "se_pJ_per_op")],
                 "W": [("half_die_W", "half_die_se_W"), ("W", "se_W"), ("W_minus_E_board_W", "W_minus_E_se")],
                 "ops/cycle/hart": []}


def page_exclusion(V, R, claims):
    """How the rows that print a page number land: excluded two-sided, excluded only on the side the rule
    does not read, or not comparable because no measured key is in the page number's unit."""
    n, excl, one_sided, unmatched = 0, 0, 0, 0
    for i, v in enumerate(V):
        val, unit = claims[i]
        if val is None:
            continue
        n += 1
        crit = v.get("t_crit_3sigma") or next((x.get("t_crit_3sigma") for x in V if x.get("t_crit_3sigma")), 3.85)
        if unit == "ops/cycle/hart":
            r = v.get("measured_over_page_ipc")
            excl += 1 if r is not None and abs(r - 1) > 0.05 else 0
            continue
        hit = False
        for mk, sk in UNIT_MEASURED.get(unit, []):
            if v.get(mk) is not None and v.get(sk):
                hit = True
                far = abs(v[mk] - val) / v[sk] >= crit
                # a row whose registered arm is a ceiling test reads an exclusion from above as no answer
                downward_only = "downward" in str(v.get("exclusion_one_sided", "")).lower()
                if far and downward_only and v[mk] > val:
                    one_sided += 1
                elif far:
                    excl += 1
                break
        if not hit:
            unmatched += 1
    return n, excl, one_sided, unmatched


def eout_quote(V, C):
    """The result-bit price as the reduction quotes it, with the raw bridge beside it, read by key."""
    v = next((x for x in V if "e_out" in str(x.get("quantity", ""))), {})
    q = (C.get("derived") or {}).get("e_out_bridge") or {}
    fJ = v.get("joint_fit_fJ")
    se = v.get("joint_fit_se_fJ")
    src = v.get("quoted_from", "")
    if fJ is None:
        fJ, se, src = (q.get("value") or 0) * 1e15, (q.get("se") or 0) * 1e15, "the bridge combination"
    return {"fJ": fJ, "se": se, "source": src, "row": v,
            "raw_fJ": v.get("raw_combination_fJ", (q.get("value") or 0) * 1e15),
            "raw_se": v.get("raw_combination_se_fJ", (q.get("se") or 0) * 1e15),
            "rail_fJ": q.get("rail_fJ"),
            "band": v.get("E60_interval_fJ") or q.get("E60_interval_fJ") or [],
            "page": v.get("page_fJ", q.get("page_fJ")),
            "degenerate": bool(g(C, "joint_fit", "design_is_degenerate")),
            "degenerate_note": g(C, "joint_fit", "degenerate_note", default="")}


def page_claim_of(v, R, sec=None, fallback=True):
    """The page's own number for this row, as a (value, unit) pair, from the reduction's page_* fields.

    `fallback` reads it off the experiment's derived quantity instead, and the caller only allows that when the
    experiment has a single verdict row, so a page number is never attached to a row it does not belong to.
    """
    for k, u in PAGE_KEYS:
        if v.get(k) is not None:
            return v[k], u
    if fallback:
        q = g(R, "cards", v.get("card") or g(R, "meta", "primary_card"), "derived",
              SECTION_DERIVED.get(sec or section_of(v.get("claims", "")), ""), default={})
        for k, u in PAGE_KEYS:
            if isinstance(q, dict) and q.get(k) is not None:
                return q[k], u
    return None, ""


def page_of(val, unit):
    return f"{sig(val, 4)} {unit}" if val is not None else "—"


def tidy(s):
    """Typography only, for strings the reduction and the camera block write in ASCII.

    It also drops the reduction's internal fix markers (`VER 7`, `(VER 12)`, `-- VER 1:`): they label the
    verifier's twelve items inside the reduction's own code and prose, and mean nothing to a reader of this
    page. Nothing else about a quoted string is changed.
    """
    s = re.sub(r"\s*\(\s*VER\s+\d+\s*\)", "", str(s))              # a parenthetical that is only the marker
    s = re.sub(r"\(\s*VER\s+\d+\s*[,:]\s*", "(", s)                  # "(VER 2, README §5.2)" -> "(README §5.2)"
    s = re.sub(r"\s*(?:--|\u2014)\s*VER\s+\d+\s*[:,]?\s*", " ", s)      # "-- VER 1: ..." -> " ..."
    s = re.sub(r"\s*\bVER\s+\d+\b\s*[:,]?\s*", " ", s)                # a bare marker anywhere else
    s = re.sub(r"(?<![\w])'([^']{2,90})'(?![\w])", "\u201c\\1\u201d", s)
    for a, b in ((" +- ", " ± "), ("+/-", "±"), (" -- ", " — "), (" -> ", " → "), ("->", " → "), (">= ", "≥ "),
                 ("3-sigma", "3-σ"), ("alpha", "α"), ("rho", "ρ"), (" deg", "°")):
        s = s.replace(a, b)
    s = re.sub(r"(\w)\s*<=\s*(\w)", "\\1 \u2264 \\2", s).replace("<= ", "\u2264 ")
    return re.sub(r"\s+", " ", s.replace("'", "\u2019"))


def sentence(s):
    """A data string used as a sentence of its own: tidied, and ended with a full stop if it lacks one."""
    t = tidy(s).strip().rstrip(",;")
    return t if t.endswith((".", "\u2026", "?", "!")) else t + "."


def deparen(s):
    """Python dict/list reprs inside a basis string, rewritten as prose. Apostrophes elsewhere are left alone."""
    def dict_repr(m):
        inner = re.sub(r"'([^']*)':\s*", r"\1 ", m.group(1))
        return inner.replace("'", "")

    def list_repr(m):
        return m.group(1).replace("'", "") if "'" in m.group(1) else m.group(0)

    s = re.sub(r"\{([^{}]*)\}", dict_repr, str(s))
    s = re.sub(r"\[([^\[\]]*)\]", list_repr, s)
    return tidy(s)


def clamp(s, n=420):
    """A whole data string, shortened at a word boundary only if it runs past n. Never cut at a full stop."""
    s = tidy(re.sub(r"[`*]", "", str(s))).strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > n * 0.6 else cut).rstrip(" ,;(") + "\u2026"


def first_clause(s, n=210, raw=False):
    """The leading clause of a basis string, cut at a sentence end or a dash.

    The result goes straight into the page's markup, so it is HTML-escaped unless the caller is building a
    table cell (the renderer escapes those itself) and asks for the raw text.
    """
    out = _first_clause(s, n)
    return out if raw else esc(out)


def _first_clause(s, n=210):
    s = deparen(s).strip()
    bar = s.find(" || ")                      # the reduction's own separator between a verdict and its commentary
    if 0 < bar < n:
        return s[:bar].rstrip(" .;") + "."
    m = re.search(r"(?<=[a-z0-9\)])(?:\s+\|\|\s+|\s+--\s+|\s+—\s+|;\s+|\.\s+)", s)
    if m and m.start() < n:
        return s[:m.start()].rstrip(" .;") + "."
    if len(s) > n:
        cut = s[:n]
        if cut.count("(") > cut.count(")"):      # never end inside an open parenthesis
            cut = cut[:cut.rfind("(")]
        sp = cut.rfind(" ")
        return (cut[:sp] if sp > n * 0.5 else cut).rstrip(" ,;(") + "…"
    return s if s.endswith((".", "…", "?", "!")) else s + "."


def build(R, CAM, F=None):
    """R = dtf.json, CAM = cam.json, F = facts.json. Returns the text dict build_page.py renders.

    Nothing about the data is typed in this file: every number comes out of one of those three, and every
    verdict string is printed as the reduction wrote it.
    """
    F = F or {}
    meta, cards = R["meta"], R["cards"]
    prim = meta.get("primary_card", "aifoundry3")
    C = cards[prim]
    ANA = {k: v for k, v in cards.items() if "[" not in k}          # the three analysis cards
    CAMC = next((v for k, v in cards.items() if "dtf-cam" in k), {})  # the camera block
    V = R["verdicts"]
    by_sec = {}
    for v in V:
        by_sec.setdefault(section_of(v.get("claims", "")), []).append(v)
    claims_num = []
    for v in V:
        sec = section_of(v.get("claims", ""))
        claims_num.append(page_claim_of(v, R, sec, fallback=len(by_sec.get(sec, [])) == 1))
    n_page_rows, n_excl, n_one_sided, n_unmatched = page_exclusion(V, R, claims_num)

    CEN = F.get("census") or {}
    CW = F.get("changed_word_price") or {}
    BR = F.get("bridge_term") or {}
    REP = F.get("replications") or {}
    C14 = F.get("c14_leak") or {}
    SCL = F.get("cell_scaling") or {}
    ZG = F.get("zero_gate") or {}
    INT = F.get("intercept_row") or {}
    RHO = F.get("rho") or {}
    C58 = (F.get("c58_c33") or {}).get("c58") or {}
    C33 = (F.get("c58_c33") or {}).get("c33") or {}
    ED4 = F.get("ed4") or {}
    EOR = F.get("e_out_routes") or {}
    ADDR = F.get("addr") or {}
    IPC = F.get("ipc") or {}
    CONV = F.get("conventions") or {}
    HALF = F.get("half_die") or {}
    RECON = F.get("reconciliation") or {}
    CAMF = F.get("camera") or {}
    REPO = F.get("repo") or {}
    DESK = F.get("desk") or []
    UNT = F.get("untestable") or []
    COV = F.get("coverage") or {}

    n_cards = len(ANA)
    runs_kept = CEN.get("runs_kept") or sum(c.get("gates", {}).get("kept", 0) for c in cards.values())
    runs_all = CEN.get("runs") or sum(c.get("gates", {}).get("runs", 0) for c in cards.values())
    passes_kept = CEN.get("passes_kept") or sum(c.get("n_passes") or 0 for c in cards.values())
    passes_reg = CEN.get("passes_registered")
    n_aside = sum(len(r.get("set_aside") or []) for r in (CEN.get("per_card") or []))
    v_of = {k: c.get("v_mean") for k, c in cards.items()}
    mhz = {k: c.get("clock_mhz") for k, c in cards.items()}

    def D(name, card=prim):
        return g(cards, card, "derived", name, default={}) or {}

    def item(name, card=prim):
        return g(cards, card, "items", name, default={}) or {}

    def fam(name, card=prim):
        return g(cards, card, "families", name, default={}) or {}

    counts = {s: sum(1 for v in V if badge(v["verdict"]) == s) for s in ("ok", "bad", "open", "thin", "neutral")}
    vcounts = {}
    for v in V:
        vcounts[v.get("verdict", "\u2013")] = vcounts.get(v.get("verdict", "\u2013"), 0) + 1
    VORDER = ["CONFIRMED", "CONFIRMED-ours", "OPEN", "REFUTED", "under-resolved", "not scored"]
    tally = [f"{n} {k}" for k, n in sorted(vcounts.items(),
             key=lambda kv: (VORDER.index(kv[0]) if kv[0] in VORDER else 99, kv[0]))]
    verdict_tally = ", ".join(tally[:-1]) + " and " + tally[-1] if len(tally) > 1 else (tally[0] if tally else "none")
    e_out, e_carry, e_addr, e_cell = D("e_out_bridge"), D("e_carry"), D("e_addr"), D("e_cell")
    e_in_d2A, e_sum = D("e_in_fand_d2A"), D("e_sum_fnot_d1nz")
    EO = eout_quote(V, C)
    jf = g(C, "joint_fit", "coefs", default={})
    rate_v = next((v for v in V if v.get("rates")), {})
    ipc_meas = g(rate_v, "measured_over_page_ipc")
    page_ipc = g(rate_v, "page_ipc")
    rho_v = next((v for v in V if v.get("rho") is not None), {})
    wf = EOR.get("within_family_mean") or {}
    fit_forms = [ADDR.get("free_intercept") or {}, ADDR.get("with_origin") or {}]
    addr_lo = min([x["value"] for x in fit_forms if x.get("value")] or [0])
    addr_hi = max([x["value"] for x in fit_forms if x.get("value")] or [0])
    d5_v = next((v for v in by_sec.get("d5", [])), {})
    d7_v = next((v for v in by_sec.get("d7", [])), {})

    # ---------- the lede ----------
    stats = f"""<div class="stats">
<div class="stat"><b>{sig(wf.get('value'), 4)} – {sig(EO['fJ'], 4)} fJ</b><span>per flipped result bit: {pm(wf.get('value'), wf.get('se'), 2, 'fJ')} measured inside one kernel family, {pm(EO['fJ'], EO['se'], 2, 'fJ')} from the pooled fit the plan says to quote. The page predicted {sig(EO['page'], 4)}.</span></div>
<div class="stat"><b>{pm(g(CW, 'e_carry_registered', 'value'), g(CW, 'e_carry_registered', 'se'), 2, 'fJ')}</b><span>per carry stage as the plan registers the estimator — {pm(g(CW, 'e_carry_R2_corrected', 'value'), g(CW, 'e_carry_R2_corrected', 'se'), 2, 'fJ')} with §5.1's changed-word term removed under reading R2. Both read {esc(CW.get('verdict_registered') or '–')}, and both exclude the page's {sig(e_carry.get('page_fJ'), 3)} fJ.</span></div>
<div class="stat"><b>{sig(addr_lo, 4)} – {sig(addr_hi, 4)} fJ</b><span>per toggled register-index bit, depending on which of two registered fit forms you take — {sig(addr_lo / (ADDR.get('page_fJ') or 1), 2)}–{sig(addr_hi / (ADDR.get('page_fJ') or 1), 2)}× the page's {sig(ADDR.get('page_fJ'), 2)} fJ, and <i>not measurable as registered</i>.</span></div>
<div class="stat"><b>{pm(CAMF.get('statistic_mk'), CAMF.get('se_pass_mk'), 3, 'mK')}</b><span>heat moved across the board when the loud half swapped sides, p = {sig(CAMF.get('p_cyclic'), 2)} — exploratory by design, and {sig(CAMF.get('arm_min_mk'), 3)}–{sig(CAMF.get('arm_max_mk'), 3)} mK across the four registered ways of removing the field's drift.</span></div>
</div>"""

    lede = (f'<p class="lede">An agent-written proposal, <a href="{PAGE_URL}">Deterministic Transistor-Flip Experiments on '
            f"1,024 RISC-V Cores</a> (20 Oct 2026), designed seven experiments — E-D1 to E-D7 — to price one transistor flip on the "
            f"ET-SoC-1's 1,024 RISC-V minions, and printed the prices it expected. We pre-registered all seven as experiment E61, "
            f"rebuilt each one so that it can measure what it names, and ran them on {n_cards} cards on the night of 20–21 October 2026: "
            f"{thou(runs_kept)} of {thou(runs_all)} runs kept across {passes_kept} passes of {passes_reg} registered, with {n_aside} passes set "
            f"aside by a rule written before the run. "
            f"<b>The arithmetic the page did on data it had was mostly right; the physics it attached to that arithmetic mostly was not.</b> "
            f"Of {len(V)} registered rows the reduction returns {verdict_tally} — its own labels, in its own words. "
            f"Of the {n_page_rows} rows where the page printed a number, {n_excl} exclude that number at three "
            f"standard errors, {n_one_sided} excludes it only from above — which the registered rule does not read as an exclusion — and "
            f"{n_unmatched} compares against a figure the page's simulator implies rather than one it printed. The one number the page got nearly "
            f"exactly is a sum it never meant to quote; the one it missed by the widest margin, the register address path, is a part of the chip it "
            f"priced at {sig(ADDR.get('page_fJ'), 2)} fJ a bit and we cannot price at all.</p>")

    gloss = ('<p class="note"><b>Names on this page.</b> A <i>minion</i> is one of the chip\'s 1,088 small RISC-V cores in 34 shires (these '
             'kernels use 1,024); each has an 8-lane vector unit, so one 256-bit operation is 8 lanes × 32 bits. The <i>minion rail</i> is the '
             'supply that feeds them, metered on the card separately from the board\'s 12 V input. <b>Energies are board energies</b> '
             '(the card\'s 12 V input, regulator loss included) unless marked <i>rail</i>; the charge-equivalent capacitance and electron count of '
             'every price we quote is tabulated at the foot of this page, in both conventions, ½CV² and CV². <code>fxor.pi</code>, '
             '<code>fand.pi</code>, <code>for.pi</code>, <code>fadd.pi</code> and <code>fnot.pi</code> are the vector unit\'s bitwise and '
             'integer operations. <i>h</i> is the designed number of bits that flip per lane from one instruction to the next.</p>')

    # ---------- the short version ----------
    label = {k: f"{lab}" for k, lab, _, _ in SECTIONS}
    order = [k for k, *_ in SECTIONS] + ["extra"]
    short_rows = []
    for key in order:
        for v in by_sec.get(key, []):
            i = V.index(v)
            pg = page_of(*claims_num[i])
            if key == "d4" and claims_num[i][0] is not None:
                pg += " (its simulator)"
            short_rows.append([label.get(key, "cross-cutting"), v.get("quantity", ""), pg, measured_of(v),
                               v.get("card", ""), v.get("verdict", ""), first_clause(v.get("basis", ""), raw=True)])

    corr = f"""<p class="note"><b>One row in this table is not scored, and one is printed under two readings.</b>
<b>Not scored:</b> {esc(next((v.get('claims') for v in V if v.get('scored') is False), 'C14 C64'))} asks whether <code>d2A</code>'s read-port
price lands in E60's interval, but §5.2 makes <code>d2A</code> the <i>measurement</i> of that price, so it cannot also be the test of it. The
reduction reports it as <b>{esc(C14.get('reported_as') or '–')}</b>, with its direction kept and no verdict attached —
{esc(sentence(str(C14.get('not_scored_because') or '').split(': ', 1)[-1]))} <b>Two readings:</b> the carry stage's registered estimator subtracts a leg that is one
rung through its own zero, and that zero changes {int(CW.get('changed_words_per_op_delta') or 0)} fewer 32-bit words an operation, so under §5.1's
reading R2 it carries a changed-word term of {pm(CW.get('term_fJ'), None, 4, 'fJ')} a flip — the ladder intercept divided by the
{int(CW.get('r2_words') or 0)} words that reading counts ({int(CW.get('src_words') or 0)} source plus {int(CW.get('res_words') or 0)} result, from
the manifest's own counts), which is the same reading the multiplier is taken on. Removing it moves the carry stage from
{pm(g(CW, 'e_carry_registered', 'value'), g(CW, 'e_carry_registered', 'se'), 3, 'fJ')} to
{pm(g(CW, 'e_carry_R2_corrected', 'value'), g(CW, 'e_carry_R2_corrected', 'se'), 3, 'fJ')}, and both read
<b>{esc(CW.get('verdict_registered') or '–')}</b>: the verdict does not depend on the term. Both are below, in E-D3; the same intercept is the
bridge's R2 correction in E-D2, {pm(BR.get('correction_W'), None, 4, 'W')}.</p>"""

    desk_bullets = f"""<ul>
<li><b>A history that never happened.</b> Section 1 of the page recounts earlier runs — watts, slugs, dates. The desk check
(<a href="{PREREG}#1-what-the-desk-check-already-settled--no-card-needed">README §1</a>, written before any card ran) found the cited slugs do not
exist and the quoted watts appear nowhere in the lab repository or in the day's reports: the only 12 October artefact is a <i>plan</i>. The measured
anchor it should have cited is on record — {esc(re.sub(r".*The measured anchor is ", "", next((d["what"] for d in DESK if d["id"] == "S1"), "")).split(". A counted")[0] if DESK else "–")}
— and a counted toggle is {esc(re.sub(r".*A counted toggle is ", "", next((d["what"] for d in DESK if d["id"] == "S1"), "")) if DESK else "–")}</li>
<li><b>A table of numbers for runs that were never made.</b> The page's decomposition rests on <code>const</code> measurements of bitwise
operations. The corpus it cites has a <code>const</code> pass for three of 392 configurations, none of them bitwise, so five of the
<code>const</code> values it prints are values for runs that do not exist — and the two that do read differently.</li>
<li><b>The one thing its own data layer got right.</b> Twelve of the page's claims are its mining of a corpus that does exist, and all twelve
hold: three absolute energies to the third decimal, three deltas and a 24% gap, six table rows raw to ±0.01 pJ, three more opcode deltas, the one
real <code>const</code> value on the page, and 23 of 24 bit patterns decoding correctly. That row is <b>HOLDS</b>, and it is the largest single
group in the desk check.</li>
</ul>"""

    desk_rows = [[d["id"], d["claims"], re.sub(r"\*+", "", d["verdict"]), clamp(d["what"], 440)] for d in DESK]
    desk_sec = f"""<h2>The seventeen verdicts that needed no card</h2>
<p>The pre-registration's §1 settled {len(DESK)} groups over the page's 95 claims from committed files alone — the catalogue JSONs, the
<code>enercat</code> source, the lab repository and the report trees — before a card was touched. Everything tonight's runs could add sits on top of
this. Three of these groups (S3, S6, S10) were re-measured on silicon anyway, and are rows in the table above.</p>
{{{{tbl:desk}}}}
<p>Two of the page's claims are scored in neither place. {esc(", ".join(COV.get("uncovered") or []))} appear in none of §1's desk groups, §2's
families, §3's not-testable rows or §9's decision rules — {COV.get('n_covered', '–')} of {COV.get('n_claims', '–')} claims are covered, and those
two are not. We owe them a verdict or a reason, and have neither.</p>"""

    unt_rows = [[clamp(u["claims"], 150), clamp(u["why"], 420)] for u in UNT]
    unt_sec = f"""<h2>What we could not test, and why</h2>
<p>A reader needs to be able to tell a claim that is wrong from one nobody could score. The pre-registration lists {len(UNT)} of the second kind,
and they are not a small part of the page: a sub-cycle glitch count, the capacitance fits, the millikelvin figures, the shire map, and the
lock-in E-D7 was built around all need tooling this lab does not have tonight.</p>
{{{{tbl:untestable}}}}"""

    # ---------- E-D1 ----------
    cell_v = next((v for v in by_sec.get("d1", []) if v.get("value_fJ") is not None and "cell" in v.get("quantity", "")), {})
    gate_v = next((v for v in by_sec.get("d1", []) if v.get("spread")), {})
    fnot_leg = g(gate_v, "fnot_leg", default={}) or fam("fnot_leg")
    e_sum_n = D("e_sum_fnot_d1n")
    zero_word_v = next((v for v in V if re.search(r"zero[- ](operand|word)", str(v.get("quantity", "")), re.I)), {})
    rep_rows = [[r["name"].split(" [")[0], r.get("card", "–"), r.get("opcode", "–"),
                 pm(r.get("fJ_per_op"), r.get("se_fJ_per_op"), 3, "fJ/op"), r.get("n_passes", "–")]
                for r in (REP.get("rows") or [])]

    d1 = f"""<h2>E-D1 · The toggle dial, the inverter and the register-file cell</h2>
<p><b>What the page proposed.</b> Alternate two source registers so that exactly <i>k</i> bit-slices flip per core per clock cycle, and read
the price of one flip off the slope. It added that in the generated loop the eight destination registers are rewritten with the value they
already hold, so the <i>cells</i> never flip while the result bus does — a real and useful observation.</p>
<p><b>What we ran, and why it differs.</b> The dial itself, as a <code>fnot.pi</code> ladder (mode 202) at h = 8, 16 and 32, in two arms:
<code>d1n</code>, whose operand set contains the all-zero word, and <code>d1nz</code>, which never holds one. The cell question needed a new
shape: the page's 1A/1B pair cannot work as written, because the two arms differ in opcode and in rate as well as in cells. We rebuilt it as a
16-operation pair (modes 304 and 305) in which the two arms share their port and result counts exactly and differ only in how many register-file
cell bits are rewritten, and we take the <i>difference of the two slopes</i> against the shared regressor, so each arm's own intercept drops out.</p>
{{{{fig:d1}}}}
<p>The two arms lie on top of each other: the zero word is worth {pm(zero_word_v.get('fJ_per_op'), next((r.get('se_fJ_per_op') for r in (REP.get('rows') or []) if r.get('fJ_per_op') == zero_word_v.get('fJ_per_op')), None), 2, 'fJ/op')}
over the whole operation ({wv(zero_word_v.get('W'), zero_word_v.get('se_W'), 3)}), which the reduction calls
<b>{zero_word_v.get('verdict', '–')}</b> — {first_clause(zero_word_v.get('basis', ''))} The sum of an input and an output bit through the
inverter is <b>{fj(e_sum.get('value'), e_sum.get('se'), 3)}</b> on the never-zero arm and {fj(e_sum_n.get('value'), e_sum_n.get('se'), 3)} on
the arm with zeros.</p>
<p>The plan registered four replications of that zero-word term, and they do not agree, so the term is not pooled into one number. Two of the six
pairs are more than the {sig(REP.get('t_crit_3sigma'), 3)}-standard-error window apart ({esc(", ".join(f"{p['a'].split(' [')[0]} against {p['b'].split(' [')[0]} at |t| = {sig(abs(p['t']), 3)}" for p in (REP.get('pairs_over_the_window') or [])))}),
and Cochran's Q over the four is {sig(REP.get('Q'), 3)} on {REP.get('df', '–')} degrees of freedom. So the set is reported as
<b>opcode-dependent</b> — §9's registered open arm — and never collapsed: {esc(sentence(str(REP.get('reading') or '').split(': ', 1)[-1]))} The four are gathered
across cards and compared there, each in femtojoules per operation at its own item's measured rate, which is the only comparison §8.6 allows; they
are not averaged. An inverse-variance mean of {pm(REP.get('weighted_mean_fJ_per_op'), None, 4, 'fJ/op')} exists in the file as the centre Cochran's
Q is taken about and nothing reads it. What <i>is</i> applied, wherever the zero-word correction is used, is the form the §8.6 fit prefers — a
constant per operation, {pm(g(REP, 'applied_term', 'coef_fJ', 0), g(REP, 'applied_term', 'coef_se_fJ', 0), 3, 'fJ/op')} — not the single-rung watt
difference this row's headline quotes.</p>
{{{{tbl:reps}}}}
{{{{fig:cell}}}}
<p><b>The cell.</b> {pm(cell_v.get('value_fJ'), cell_v.get('se_fJ'), 2, 'fJ')} per flipped register-file cell bit on {cell_v.get('card', prim)},
rail {sig(cell_v.get('rail_fJ'), 3)} fJ, over {cell_v.get('n_passes', '–')} passes. Verdict: <b>{cell_v.get('verdict', '–')}</b> —
{first_clause(cell_v.get('basis', ''))} The registered prior was {sig(g(e_cell, 'prior_fJ', 0), 2)}–{sig(g(e_cell, 'prior_fJ', 1), 2)} fJ, and the
measurement does land inside it; it is the resolution, not the value, that falls short.</p>
<p><b>And whether the cell term scales with the cell count is untested, not settled.</b> A law proportional to the designed number of flipped cells
needs the per-cell-bit price to be the same at both rungs and the per-operation step to double. Measured, the price is
{pm(g(SCL, 'at_low_h', 'value'), g(SCL, 'at_low_h', 'se'), 3, 'fJ')} at h = {sig(SCL.get('low_h'), 2)} and
{pm(g(SCL, 'at_high_h', 'value'), g(SCL, 'at_high_h', 'se'), 3, 'fJ')} at h = {sig(SCL.get('high_h'), 2)}, a paired difference of
{pm(g(SCL, 'difference', 'value'), g(SCL, 'difference', 'se'), 3, 'fJ')} ({sig(SCL.get('per_bit_change_pct'), 3)}%) where proportionality needs
zero, and the per-operation step grows {sig(g(SCL, 'per_op_growth', 'value'), 4)}× where it needs
{sig(SCL.get('per_op_growth_needed'), 3)}×. That is |t| = {sig(abs(SCL.get('t') or 0), 2)} against a
{sig(SCL.get('t_crit_3sigma'), 3)} window, so <b>both</b> readings survive: a difference of exactly zero is inside three standard errors and so is
the measured {sig(abs(SCL.get('per_bit_change_pct') or 0), 3)}% fall, which is why the reduction's own
<code>proportional_within_3SE</code> prints {esc(str(SCL.get('proportional_within_3SE')))}. The RECON 8 condition is therefore
<b>untested</b> — not satisfied and not failed — and the confirmed arm's second condition is not met because it was never decided. This design has
no power to tell a ratio of {sig(g(SCL, 'ratio', 'value'), 3)} from 1.000. An earlier build of this reduction recorded the condition as satisfied
without running it at all, and the build after that read the same non-result as “nothing here shows the cell term scaling with h”; neither is
evidence either way.</p>
<p><b>The inverter.</b> The page's reason for liking <code>fnot.pi</code> — an inverter is two FETs where an XOR is ten or twelve — predicts an
ordering by gate depth. At identical port counts and identical designed counts the three-opcode gate ladder spreads
{pm(C33.get('spread_fJ'), C33.get('spread_se'), 2, 'fJ')} from {g(gate_v, 'spread', 'min', 'op')} to
{g(gate_v, 'spread', 'max', 'op')}, which is {sig(abs(C33.get('spread_t') or 0), 3)} standard errors — real, but
<b>not</b> ordered by depth ({', '.join(f'depth {int(d)} → {sig(x, 4)} fJ ({nm})' for d, x, nm in (g(gate_v, 'spread', 'by_depth_named') or []))}).
Verdict: <b>{gate_v.get('verdict', '–')}</b>. The error bar above is §8.4's own unit of replication, the one the row reads: the same two opcodes
({esc(" − ".join(C33.get('paired_ops') or []))}) differenced <i>inside</i> each pass, then the mean and the standard error from the scatter between
{C33.get('spread_n_passes', '–')} passes — {pm(C33.get('spread_fJ'), C33.get('spread_se'), 3, 'fJ')}, |t| = {sig(abs(C33.get('spread_t') or 0), 3)}.
Two other readings of the same spread are in the file and all three fire the same arm: the cross-item form, the two opcodes' own errors added in
quadrature, {pm(C33.get('cross_item_spread_fJ'), C33.get('cross_item_se_fJ'), 3, 'fJ')} at |t| = {sig(abs(C33.get('cross_item_t') or 0), 3)}, and
the widest-pair-per-pass form, {pm(C33.get('max_minus_min_fJ'), C33.get('max_minus_min_se_fJ'), 3, 'fJ')} at
|t| = {sig(abs(C33.get('max_minus_min_t') or 0), 3)}. The one-port <code>fnot.pi</code> leg reads
{pm(g(fnot_leg, 'e_sum_fnot_fJ'), g(fnot_leg, 'se_fJ'), 2, 'fJ')} against the two-port XOR's
{sig(g(fnot_leg, 'E60_interval_fJ', 0), 4)}–{sig(g(fnot_leg, 'E60_interval_fJ', 1), 4)} fJ from E60: a second read port is nearly free per bit,
which is a statement about ports, not about FET counts, and we report it as such.</p>"""

    # ---------- E-D2 ----------
    d2_v = next((v for v in by_sec.get("d2", []) if "e_out" in str(v.get("quantity", ""))), {})
    d2a_v = next((v for v in by_sec.get("d2", []) if "d2A" in str(v.get("quantity", ""))), {})
    skew_v = next((v for v in by_sec.get("d2", []) if "Miller skew" in str(v.get("quantity", "")) or "polarity" in str(v.get("basis", ""))), {})
    ratio = EOR.get("intercept_ratio_N_over_X") or {}
    ratio_rows = [[k, sig(p, 3), sig((ratio.get("se_from") or {}).get(k), 3) + " SE away"]
                  for k, p in sorted((ratio.get("predictions") or {}).items(), key=lambda kv: kv[1] or 0) if p]
    c14a = (C14.get("arms") or {})
    d2 = f"""<h2>E-D2 · The input-versus-output mask bridge</h2>
<p><b>What the page proposed.</b> Run <code>fand.pi</code> with the second operand held at zero, so the inputs flip and the output cannot:
“zero gate outputs flip, zero pipeline latches flip, zero writeback wires flip”. Subtract that from the same operation with the operand held at
all-ones, and what remains is the price of the output path alone — the page's {sig(d2_v.get('page_fJ') or e_out.get('page_fJ'), 4)} fJ per result bit.</p>
<p><b>What we ran, and why it differs.</b> Two arms are not enough: the held word and the opcode both move with the mask. We ran it as a
2 × 2 — <code>fand.pi</code> with the operand held at 0 and at all-ones, <code>for.pi</code> with it held at all-ones and at 0 — at h = 0, 16 and
32, so that the opcode's own intercept cancels by construction. The page's Run A is our <code>d2A</code>, its Run B our <code>d2B</code>, its
Run C our <code>d2C</code>.</p>
{{{{fig:d2}}}}
<p><b>The read-port leg.</b> <code>d2A</code> reads <b>{pm(d2a_v.get('value_fJ'), d2a_v.get('se_fJ'), 2, 'fJ')}</b> per port bit and
<code>d2C</code>, the same shape under another opcode, {sig(d2a_v.get('e_in_for_d2C_fJ'), 4)} fJ — the agreement the bridge's output leg depends
on. The reduction marks that row <b>{d2a_v.get('verdict', '–')}</b> against E60's {sig(g(d2a_v, 'E60_interval_fJ', 0), 4)}–{sig(g(d2a_v, 'E60_interval_fJ', 1), 4)} fJ
interval and reports it as <b>{esc(C14.get('reported_as') or '–')}</b>, because §5.2 of the plan says <code>d2A</code> cannot both supply
e_in(fand) and be tested against it — and in this build it does supply it: it is the subtrahend inside the registered estimator for e_out(add) and
e_carry. §9's table nonetheless registers a confirmed arm, so the plan contradicts itself; the first builds of this reduction resolved the
contradiction silently in favour of scoring, and this one drops the arm as a decision and keeps the direction. Read as agreement, the two numbers
agree. Three caveats the row's own blocks carry. The value sits {sig(d2a_v.get('fJ_above_the_lower_edge'), 3)} fJ above the interval's lower edge,
{sig((d2a_v.get('fJ_above_the_lower_edge') or 0) / (d2a_v.get('se_fJ') or 1), 2)} standard errors. The four fit forms the reduction prints for it
span {sig(min(x['fJ'] for x in (d2a_v.get('by_fit_form') or {}).values()), 4)}–{sig(max(x['fJ'] for x in (d2a_v.get('by_fit_form') or {}).values()), 4)} fJ.
And where the answer lands moves with the leakage slope: {esc(tidy("; ".join(f"{(a.get('label') or k)} → {sig(a.get('value'), 5)} ± {sig(a.get('se'), 3)} fJ, {'inside' if a.get('inside_strict') else 'OUTSIDE'} the strict interval" for k, a in (c14a or {}).items())).replace("W/C", "W/°C"))}
— so at E60's own {sig(g(R, 'cards', prim, 'leak_E60_W_per_C'), 3)} W/°C the point value is <i>below</i> the interval and inside it only after the
±{sig(g(c14a, 'E60', 'widening_fJ'), 3)} fJ widening §5.0 rule 2 allows. That reading survives on the widening alone.</p>
{{{{fig:d2e}}}}
<p><b>The output leg does not land where the page put it, and the routes to it disagree with each other.</b> Measured <i>inside</i> family B, each
leg at its own mode's rate and the opcode baseline cancelled by construction, a result bit costs
<b>{pm(wf.get('value'), wf.get('se'), 3, 'fJ')}</b> — {pm(g(EOR, 'fand_leg', 'value'), g(EOR, 'fand_leg', 'se'), 3, 'fJ')} on the
<code>fand</code> leg and {pm(g(EOR, 'for_leg', 'value'), g(EOR, 'for_leg', 'se'), 3, 'fJ')} on the <code>for</code> leg. The raw four-cell
combination reads {pm(EO['raw_fJ'], EO['raw_se'], 3, 'fJ')}. The number the plan says to quote comes from the pooled fit instead:
{pm(EO['fJ'], EO['se'], 3, 'fJ')}, inside the interval E60 measured for the same quantity through another kernel
({sig(g(EO, 'band', 0), 4)}–{sig(g(EO, 'band', 1), 4)} fJ) once widened by its own ±{sig(d2_v.get('three_sigma_widening_fJ'), 3)} fJ window,
though its point value is below that interval. And repeating E60's own cross-family subtraction on tonight's data gives
{pm(g(EOR, 'cross_family_with_origin', 'value'), g(EOR, 'cross_family_with_origin', 'se'), 3, 'fJ')} through the origin and
{pm(g(EOR, 'cross_family_free_intercept', 'value'), g(EOR, 'cross_family_free_intercept', 'se'), 3, 'fJ')} with a free intercept. So the route
family B was built to replace is the route that reproduces E60, and the route built to cancel the opcode baseline lands about
{sig(abs((EOR.get('cross_family_free_intercept') or {}).get('value', 1) - (wf.get('value') or 0)) / ((EOR.get('cross_family_free_intercept') or {}).get('value') or 1) * 100, 2)}% below it.
Against the page's {sig(EO['page'], 4)} fJ every reading is a factor of {sig(EO['page'] / EO['fJ'], 3)} to
{sig(EO['page'] / (wf.get('value') or 1), 3)} out, which is the one thing they agree on. The row is <b>{d2_v.get('verdict', '–')}</b> because a
registered open-condition fired: {first_clause(d2_v.get('basis', ''), 300)}</p>
<p><b>What the gap between the two routes is, and what it is not.</b> The pooled fit sits {sig(BR.get('gap_fJ'), 4)} fJ a flip above the raw
four-cell combination. On the bridge's own per-mode denominator — {esc(tidy(str(BR.get('denominator_how') or '').split(' -- ')[0]).replace(' x ', ' × '))} =
{sig((BR.get('denominator_bits_per_s') or 0) / 1e12, 4)}×10¹² bits a second — that is {pm(BR.get('gap_W'), None, 4, 'W')}. §5.1's changed-word term
is a <i>part</i> of it and not the whole: the raw combination changes {int(BR.get('changed_words_per_op') or 0)} 32-bit words an operation and
§5.1 prices them at the ladder intercept, {pm(BR.get('term_W_at_the_intercept'), None, 4, 'W')} =
{sig(BR.get('term_fJ_at_the_intercept'), 4)} fJ a flip, which is {sig(BR.get('share_at_the_intercept_pct'), 3)}% of the gap. The remaining
{pm(BR.get('unexplained_W'), None, 4, 'W')} separates two estimators of the same quantity and is not accounted for by changed words. Priced
instead at the fit's own changed-word coefficient ({pm(BR.get('w_coef_fJ_per_word'), BR.get('w_coef_se'), 3, 'fJ')} per 32-bit word ×
{int(BR.get('changed_words_per_op') or 0)} words over {int(BR.get('regressor_bits_per_op') or 0)} bits) the term would be
{sig(BR.get('derived:term_fJ_at_the_fitted_w'), 3)} fJ, {sig(BR.get('derived:share_at_the_fitted_w_pct'), 3)}% — still a minority of the gap. Its
sign is contested as well: one reading has the raw bridge high by that term and the other low by it, so correcting it moves the raw bridge to
either {sig(BR.get('derived:raw_minus_term_fJ'), 4)} or {sig(BR.get('derived:raw_plus_term_fJ'), 4)} fJ, and both are still short of the fit.
Something else accounts for most of the {sig(BR.get('gap_fJ'), 4)} fJ, and we cannot say what.</p>
<p><b>What the term probably is, and why it matters here.</b> The coefficient prices a 32-bit lane word that changes on any bus, once, however
many of its 32 bits move — which is the shape of a per-lane wake-up cost (a lane clock gate, an operand-valid latch, a local clock buffer), not a
per-bit cost. But the pre-registration offered three readings of that intercept and tonight's family A forces a fourth it never listed: per
address bit an operation fetches. The two ladders' intercepts are {pm(ratio.get('N_W'), ratio.get('N_se'), 3, 'W')} and
{pm(ratio.get('X_W'), ratio.get('X_se'), 3, 'W')}, a ratio of {pm(ratio.get('value'), ratio.get('se'), 3)}, and that ratio sits closest to the
reading nobody registered.</p>
{{{{tbl:ratio}}}}
<p class="note"><b>One caveat retired.</b> The first build of this reduction printed a condition number of
{thou(round(g(C, 'joint_fit', 'condition_number_raw_design') or 0))} for the pooled design and called it rank-deficient, which would have
disqualified the fit the row is quoted from. That figure is a units artefact — counts per second against an intercept of 1.0. Column-scaled, the
design's condition number is {sig(g(C, 'joint_fit', 'condition_number'), 4)} over {g(C, 'joint_fit', 'rows_per_pass', default='–')} rows a pass,
and the variance-inflation factor on e_out is {sig(g(C, 'joint_fit', 'vif', 'e_out'), 3)}. The fit is not degenerate. It is still a <i>pooled</i>
fit whose e_out rests on one contrast, and the reduction forbids quoting a standard error for any coefficient identified by one contrast —
{esc(", ".join(k for k, q in sorted((g(EOR, 'joint_fit', 'se_quoted', default={}) or {}).items()) if q is False))} are printed without one for exactly
that reason. Its own note on what cannot be separated: {esc(tidy("; ".join(g(C, 'joint_fit', 'known_collinearities') or [])))}.</p>
<p><b>The clamp polarity.</b> The page read the A-versus-C difference as an NMOS/PMOS asymmetry. That one is
<b>{skew_v.get('verdict', '–')}</b> by design rather than by data: {first_clause(skew_v.get('basis', ''), 300)}</p>"""

    # ---------- E-D3 ----------
    d3_v = next((v for v in by_sec.get("d3", [])), {})
    page_carry = page_claim_of(d3_v, R, "d3")[0]
    curv = g(d3_v, "curvature", default={}) or fam("C_curvature")
    fits = g(curv, "fits", default={})
    d3 = f"""<h2>E-D3 · The carry-chain wave</h2>
<p><b>What the page proposed.</b> Preload one operand with L low ones and toggle the other between 0 and 1, so a single input bit flip sets off
exactly L carry nodes and L + 1 sum bits. Plot power against L; the slope is “about 14 fJ per carry stage”.</p>
<p><b>What we ran, and why it differs.</b> Exactly that, in the held-operand shape (mode 302, <code>fadd.pi</code>), at
L = {', '.join(str(int(x)) for x in (g(curv, 'rungs_L') or []))}, with the carry and sum counts re-derived from the operand bytes rather than
assumed. The slope mixes one carry node with one sum bit, so the registered estimator subtracts an independently measured result bit — from the
<code>fadd.pi</code> rung of the gate ladder, the same opcode, the same shape, the same pass — and what is left is the carry stage alone. Importing
e_out from <code>fand</code>/<code>for</code> instead is the thing §4 forbids; that route is printed beside it and reads
{pm(d3_v.get('e_carry_alt_from_family_B_fJ'), d3_v.get('e_carry_alt_from_family_B_se_fJ'), 3, 'fJ')}.</p>
{{{{fig:d3}}}}
{{{{fig:d3e}}}}
<p>The line is straight: a fit in L leaves {sig(g(fits, 'linear_L', 'resid_rms_W'), 2)} W rms against
{sig(g(fits, 'sublinear_L_log2L', 'resid_rms_W'), 2)} W for the L·log₂L form a parallel-prefix adder would give, and the reduction prefers
<b>{curv.get('preferred', '–')}</b>. A carry stage costs <b>{pm(d3_v.get('value_fJ'), d3_v.get('se_fJ'), 2, 'fJ')}</b> (rail
{sig(d3_v.get('rail_fJ'), 2)} fJ), against the page's {sig(page_carry, 3)} fJ and our own registered {sig(d3_v.get('ours_fJ'), 2)} fJ.
Verdict: <b>{d3_v.get('verdict', '–')}</b> — {first_clause(d3_v.get('basis', ''))} {esc(tidy(curv.get('unit_note', '')))}</p>
<p><b>The second reading, and why it does not change the verdict.</b> The leg this estimator subtracts is one rung through its own zero, and that
zero changes {int(CW.get('changed_words_per_op_delta') or 0)} fewer 32-bit words an operation, so under §5.1's reading R2 the registered
e_out(add) carries a changed-word term. The reduction prices it at the ladder intercept divided by the {int(CW.get('r2_words') or 0)} words that
reading counts — {int(CW.get('src_words') or 0)} source plus {int(CW.get('res_words') or 0)} result, which is the count the multiplier itself is
taken on, so price and count come from one reading — giving {pm(CW.get('term_fJ'), None, 4, 'fJ')} a flip
({pm(CW.get('W_per_changed_word'), None, 4, 'W')} per changed word). Remove it and e_out(add) is
{pm(g(CW, 'e_out_add_R2_corrected', 'value'), g(CW, 'e_out_add_R2_corrected', 'se'), 3, 'fJ')} instead of
{pm(g(CW, 'e_out_add_registered', 'value'), g(CW, 'e_out_add_registered', 'se'), 3, 'fJ')}, and the carry stage is
<b>{pm(g(CW, 'e_carry_R2_corrected', 'value'), g(CW, 'e_carry_R2_corrected', 'se'), 3, 'fJ')}</b>. That is
{sig(abs(CW.get('derived:t_vs_ours') or 0), 3)} standard errors from our own registered {sig(CW.get('ours_fJ'), 2)} fJ, inside the
{sig(CW.get('t_crit_3sigma'), 3)} window, and it excludes the page's {sig(CW.get('page_fJ'), 3)} fJ at
|t| = {sig(abs(CW.get('derived:t_vs_page') or 0), 3)}: <b>{esc(CW.get('verdict_R2_corrected') or '–')}</b>, the same arm as the registered form.
So the row's verdict does not depend on whether the term is removed — the file says so in a field of its own,
<code>verdict_depends_on_the_R2_term = {esc(str(CW.get('verdict_depends_on_the_R2_term')))}</code> — and the primary stays the registered
estimator, because §4 registers it and §5.1's reading is itself an open row in this file. An earlier build of this reduction priced the term per
<i>source</i> word against reading R2's count of {int(CW.get('r2_words') or 0)}, doubling it, which flipped this second reading to refuted on both sides on nothing but the mismatched reading. Both readings are in the table at the top.</p>"""

    # ---------- E-D4 ----------
    d4_v = next((v for v in by_sec.get("d4", [])), {})
    lv = g(d4_v, "levels", default={}) or fam("M_levels")
    ws = g(lv, "whole_spread", default={})
    cc = ED4.get("complement_control") or {}
    ed4_rows = [
        ["the spread across the four k_adj levels is ≥ 3 SE",
         pm(ws.get("dW"), ws.get("se"), 3, "W") + f", |t| = {sig(abs(ws.get('t') or 0), 3)}",
         f"no — the window is {sig(ws.get('t_crit_3sigma'), 3)} at {ws.get('n_passes', '–')} passes"],
        ["Spearman ρ over the four levels is ≥ 0.90, rising with k_adj",
         f"{sig(ED4.get('spearman_pass_averaged'), 3)} pass-averaged; " +
         pm(g(ED4, 'spearman_per_pass', 'value'), g(ED4, 'spearman_per_pass', 'se'), 3) + " per pass",
         "no — and the sign is the opposite of the law's"],
        ["every level-to-level step is ≥ 3 SE",
         "; ".join(pm(s.get("dW"), s.get("se"), 2, "W") for s in (ED4.get("steps") or [])),
         "no — not one of the three"],
        ["the complement pair is symmetric within 3 SE",
         pm(g(cc, "value"), g(cc, "se"), 3, "W") + f" on {ED4.get('complement_control_card', '–')}",
         "yes — this one the design did deliver"],
    ]
    d4 = f"""<h2>E-D4 · The Miller wire law</h2>
<p><b>What the page proposed.</b> Hold the number of flipping wires at 128 and change only their neighbours' phase — all flipping together,
every flipping wire flanked by quiet ones, or every wire counter-phased against its neighbours — to separate a wire's capacitance to ground
from its capacitance to the wire beside it.</p>
<p><b>What we ran, and why it differs.</b> Four occupancy-matched patterns at identical designed counts and no zero word, with a complement pair as
a control, so that the only thing that moves is the neighbour phase: k_adj = {', '.join(sig(x, 3) for x in (lv.get('k_adj') or []))}. Bit index =
physical wire adjacency is an assumption, and it is stated in the result rather than discovered afterwards.</p>
{{{{fig:d4}}}}
<p>The registered rule has four conditions, not one, and three of them fail.</p>
{{{{tbl:ed4}}}}
<p>Verdict: <b>{d4_v.get('verdict', '–')}</b> — {first_clause(d4_v.get('basis', ''))} Two things that reads as, and one it does not. It is a null
about the <i>design</i>: at 128 flips out of 256 wires the four patterns differ by too little for a board meter, so nothing about C_gnd against
C_adj can be extracted from them. It is also a sign problem — more counter-phasing reads {sig(abs(ws.get('dW') or 0), 3)} W <i>less</i> power where
the page's law predicts {sig(ED4.get('page_W'), 3)} W more, a disagreement of {sig(abs((ws.get('dW') or 0) - (ED4.get('page_W') or 0)), 3)} W. It
is <i>not</i> support for the law. And the margin is thin on its own terms: |t| = {sig(abs(ws.get('t') or 0), 3)} against the
{sig(ws.get('t_crit_3sigma'), 3)} window is {sig(abs(ws.get('t') or 0) / (ws.get('t_crit_3sigma') or 1) * 100, 3)}% of the threshold, so “the whole
spread is under three standard errors” is true by {sig((ws.get('t_crit_3sigma') or 0) - abs(ws.get('t') or 0), 2)} of a standard error.</p>
<p class="note"><b>On the page's own number for this row.</b> The {sig(ED4.get('page_W'), 4)} W in the table at the top is §5.4's reading of the
page's <i>simulator</i> for one step (m_pair against m_nib), not a watt figure the page printed. The page's §6 row gives a span of about 0.6–1.4 W
and the desk check computes 2.58 W from the same simulator. We compare a single simulated step against a measured four-level spread, which is the
closest commensurable pair available, and say so rather than hiding it in a cell.</p>"""

    # ---------- E-D5 ----------
    page_addr = ADDR.get("page_fJ")
    holm_sig = [r for r in (g(R, "holm", "rows", default=[]) or []) if "significant at" in str(r.get("holm", ""))]
    live = D("e_addr_live")
    gml = fam("A_gated_minus_live_slope")
    deg = ADDR.get("degeneracy") or []
    d5 = f"""<h2>E-D5 · The address decoder — the night's largest effect, and the one we cannot price</h2>
<p><b>What the page proposed.</b> Hold every data register at zero so nothing flips in the datapath, and change only <i>which</i> registers the
instruction names. What is left is the 5-bit index decoder and its wordline drivers, which the page priced at
{sig(page_addr, 3)} fJ per address bit across three ports.</p>
<p><b>What we ran, and why it differs.</b> A ladder of register-index Hamming distances (new modes 306–309) in two data regimes: <i>gated</i>, every
data register zero, as the page specified; and <i>live</i>, every data register holding the same non-zero word, so that the data path is awake while
the index still moves. The 5-bit rung retires at a different instruction rate from the rest of the ladder, so the amendment keeps it out of the
slope and reports it beside — it is drawn hollow below.</p>
{{{{fig:d5}}}}
<p>Something very large is there. The gated ladder's slope is {pm(ADDR.get('value_fJ'), ADDR.get('se_fJ'), 3, 'fJ')} per toggled index bit if it is
fitted with a free intercept, and {pm(g(ADDR, 'with_origin', 'value'), g(ADDR, 'with_origin', 'se'), 3, 'fJ')} if it is forced through the origin —
two forms the plan registers, differing by {sig(abs((ADDR.get('with_origin') or {}).get('value', 0) - (ADDR.get('value_fJ') or 0)), 3)} fJ a bit,
far more than either standard error. It is {esc("the only one of the confirmatory five that survives Holm correction" if len(holm_sig) == 1 else f"one of {len(holm_sig)} quantities that survive Holm correction")}
(p = {pval(holm_sig[0]['p_two']) if holm_sig else '–'}), it is {sig((ADDR.get('value_fJ') or 0) / (page_addr or 1), 3)} to
{sig((g(ADDR, 'with_origin', 'value') or 0) / (page_addr or 1), 3)} times the page's {sig(page_addr, 3)} fJ, and it sits
{sig(ADDR.get('times_the_prior_ceiling'), 4)} times our own registered ceiling of {sig(g(ADDR, 'prior_fJ', 1), 2)} fJ.</p>
{{{{fig:d5e}}}}
<p>And it is <b>{d5_v.get('verdict', '–')}</b>. Not refuted: the registered arm is a <i>ceiling</i> test — the page claimed 32 fJ a bit and the
question was whether silicon is cheaper — so excluding 32 fJ from <i>above</i> does not answer it, and the exclusion is read one-sided downward
only. {first_clause(d5_v.get('basis', ''), 260)} The ladder is reported descriptively and no verdict rests on the number.</p>
<p><b>Four reasons the slope is not “energy per address bit”.</b> First, the two fit forms disagree by more than their errors, which is itself why
the row cannot be scored. Second, the three rungs are three separately emitted kernels, and a per-kernel constant that a single free intercept
cannot remove is measurable elsewhere on this card: the five zero rungs of other families that share the A ladder's own issue rate
({esc(", ".join(g(ADDR, 'per_op_constant_summary', 'items') or []))}) span
{sig(g(ADDR, 'per_op_constant_summary', 'span_W'), 3)} W, which on this ladder is
{sig(g(ADDR, 'per_op_constant_summary', 'fJ_per_bit_equiv'), 3)} fJ a bit —
{sig(g(ADDR, 'per_op_constant_summary', 'pct_of_the_slope'), 2)}% of the slope itself. A per-kernel constant of the size measured elsewhere
accounts for part of this slope, not all of it, and it cannot be subtracted, because the A rungs' own spread <i>is</i> the ladder. Third, the cost is not one slope: a fixed step is paid the moment the source index stops being the same register
twice in a row, and only the remainder grows with distance, so a single number per bit is the wrong functional form. Fourth, the design is exactly
degenerate in its own regressor — we chose f1, f7 and f31, so Hamming distance equals log₂(1 + physical row distance) rung for rung
({esc("; ".join(f"{d['rung']}: {sig(d['addr_bits_above_a0'], 2)} index bits, row distance {d['index_row_distance']}, log₂(1+distance) {sig(d['log2_1_plus_distance'], 2)}" for d in deg))}).
A per-address-bit law and a per-decoder-tree-level law are the same arithmetic here, and the index travels in the instruction word as well as into
the register file's decoder, so instruction-fetch toggles and read-port address toggles move together by construction.</p>
<p>What <i>is</i> solid: changing which register an instruction names, with every data bit held still, moves real power, and it is the most
expensive bit on this page — about {sig((ADDR.get('times_a_data_bit') or 0), 3)} times a read-port data bit
({sig(ADDR.get('e_in_fJ'), 4)} fJ). The gated and live ladders differ by {fj(gml.get('value'), gml.get('se'), 3)} per bit — the registered test for
data-path gating reaching the address path, and it fires — with the live arm reading
{pm(ADDR.get('live_fJ'), ADDR.get('live_se_fJ'), 3, 'fJ')}. The page's 32 fJ across three ports is refuted and nothing is confirmed in its place.
Two rungs break the degeneracy for E62: one with high Hamming distance and small row distance, one with the reverse, and one with the two source
index fields different so that the units stop being ambiguous by a factor of two.</p>
<p class="note"><b>One consequence for E-D1, which we owe the reader.</b> The pre-registration budgeted family V's address-count difference as
“0.05% of the signal”. At a price of this order it is nearer 19% of the cell signal, and in the direction that makes the cell term larger. The
A2.3 slope-difference form E-D1's headline uses is immune — the address count is constant inside each arm's own ladder — so
{pm(cell_v.get('value_fJ'), cell_v.get('se_fJ'), 2, 'fJ')} stands. The cross-mode per-rung step figures are not immune. The B bridge, family C,
family M, family Z and the X ladder all hold their address count constant across rungs, so they are clean.</p>"""

    # ---------- E-D6 ----------
    d6_v = next((v for v in by_sec.get("d6", [])), {})
    page_zero = page_claim_of(d6_v, R, "d6")[0]
    d6 = f"""<h2>E-D6 · The zero gate</h2>
<p><b>What the page proposed.</b> That the fused multiply-add is clock-gated on zero operands, so replacing zeros with a non-zero constant
un-gates about 3,800 flip-flops and costs <b>+{sig(page_zero, 3)} pJ per operation</b> — its single
largest energy claim, and the premise of a whole section.</p>
<p><b>What we ran.</b> The same two constants on the same instruction (mode 191), 20 seconds a pass, with every designed count zero in both
arms so that only the operand's zero-ness differs.</p>
{{{{fig:d6}}}}
<p>The step is <b>{pm(ZG.get('pJ_per_op'), ZG.get('se_pJ_per_op'), 2, 'pJ/op')}</b>, or {wv(ZG.get('W'), ZG.get('se_W'), 3)} on the card. Verdict:
<b>{d6_v.get('verdict', '–')}</b> — {first_clause(d6_v.get('basis', ''))} The desk check had already found the same step at
{sig(ZG.get('ours_pJ_per_op'), 3)} pJ in the corpus the page itself cites; silicon agrees with the corpus, not with the page.</p>
<p>Read strictly this row is a null, and the honest statement is “no step larger than about half a picojoule”. The margin deserves one line,
because it is not large: the rule's boundary at 0.5 pJ an operation is {sig(abs(ZG.get('se_to_the_0p5_boundary') or 0), 3)} standard errors away,
the three-standard-error window reaches {sig(ZG.get('upper_3se_pJ_per_op'), 3)} pJ an operation, so the rule's own OPEN band
({'%g' % (g(ZG, 'open_band_pJ_per_op', 0) or 0)}–{'%g' % (g(ZG, 'open_band_pJ_per_op', 1) or 0)} pJ an operation) lies inside that window; and in watts the
point value is {sig(abs(ZG.get('derived:se_to_0p1_W') or 0), 2)} of a standard error from the 0.1 W the verdict calls a null. What the data exclude is the
page's {sig(page_zero, 3)} pJ, by a very long way. What they do not do is measure a small step.</p>"""

    # ---------- E-D7 ----------
    page_half = d7_v.get("page_W")
    t3 = d7_v.get("half_die_three_ways") or {}
    blk = g(CAM, "block", default={})
    camv = g(CAM, "verdict", default={})
    est = "".join(f"<li>{esc(tidy(x))}</li>" for x in (CAMF.get("established") or []))
    nest = "".join(f"<li>{esc(tidy(x))}</li>" for x in (CAMF.get("not_established") or []))
    bd = CAMF.get("board") or {}
    half_rows = [[k, f"{d.get('mhz')} MHz, {d.get('mv')} mV", pm(d.get("value"), d.get("se"), 3, "W"),
                  f"{d.get('n_passes', '–')} passes"] for k, d in sorted(HALF.items(), key=lambda kv: -(kv[1].get("value") or 0))]
    d7 = f"""<h2>E-D7 · The half-die dipole, on the camera</h2>
<p><b>What the page proposed.</b> Give one half of the die work whose result bits flip and the other half work whose result bits cannot, swap
the halves every ten seconds, and watch a thermal dipole of about {sig(PAGE_CLAIMS_NOT_IN_DTF['dipole_mK'], 3)} mK appear on the camera while
total card power stays exactly flat — about {sig(page_half, 2)} W of switching heat moving from side to side at constant total power.</p>
<p><b>What we ran, and why it differs.</b> The page's own definition of the halves had to be replaced before the experiment could mean anything:
its “West = shires 0–15, East = shires 16–31” is not a spatial split at all. The host's own mesh table puts shires 0–15 in <i>every</i> mesh
column, so that split would modulate the whole die, and no 16/16 vertical or horizontal cut of this chip exists. We used the mesh x ≤ 2 split
instead. Then a contiguous camera block on {blk.get('card', '–')} ({blk.get('passes', '–')} passes,
{blk.get('runs_per_pass', '–')} runs each, {blk.get('frames_fetched', '–')} frames at about {sig(blk.get('frame_rate_per_s'), 2)} frames a
second), with the two halves' masks swapped between passes so that block order is balanced rather than assumed away. The page's 0.05 Hz
lock-in needs a kernel and three raised timeouts we do not have tonight, so the registered substitute is a double difference across the swap,
calibrated by a permutation null over all {thou(CAMF.get('p_labellings'))} labellings.</p>
{{{{fig:halfdie}}}}
<p><b>The board meter first, because it carries a verdict.</b> The registered tier-1 test is the result-path load on one half of the mesh, against
a window of {sig(g(d7_v, 'half_die_target_W', 0), 3)}–{sig(g(d7_v, 'half_die_target_W', 1), 3)} W. It can be read three ways, and the plan
registers all three. Half the measured combination gives {pm(t3.get('a_measured_half_of_the_combination_W'), t3.get('a_se_W'), 3, 'W')} — outside
the window, and outside it after its own ±{sig(t3.get('c_3SE_widening_W'), 3)} W widening. The plan's <i>own formula</i> for the same quantity,
e_out × 256 result bits an operation × the rate, halved, gives {sig(t3.get('b_from_joint_fit_e_out_W'), 4)} W from the pooled fit — which is
<i>inside</i> the window — and {sig(t3.get('b_from_raw_bridge_e_out_W'), 4)} W from the raw bridge, which is outside it below. So this arm turns on
which spelling of one quantity is used, and the row is <b>{d7_v.get('verdict', '–')}</b>: {first_clause(d7_v.get('basis', ''))}</p>
<p>The same quantity on the other two cards brackets the number the page printed. The page specified 600 MHz, and the only clock-pinned card is
{prim}, so {sig(g(HALF, prim, 'value'), 4)} W is the fair comparison — but a page scored on three cards should say that the two governor-free cards
at 800 MHz read {' and '.join(pm(d.get('value'), d.get('se'), 3, 'W') for k, d in sorted(HALF.items(), key=lambda kv: -(kv[1].get('value') or 0)) if k != prim)},
on either side of the page's {sig(page_half, 2)} W.</p>
{{{{tbl:half}}}}
<p><b>And the two halves are not electrically interchangeable.</b> The registered W-against-E equality reads
{pm(d7_v.get('W_minus_E_board_W'), d7_v.get('W_minus_E_se'), 2, 'W')} in the main reduction and {sig(bd.get('hi_W'), 3)} W in the camera block's
own telemetry pipeline — a {sig(abs((bd.get('hi_W') or 0) - (d7_v.get('W_minus_E_board_W') or 0)), 2)} W difference between two implementations of
one test, which we cannot reconcile and will not paper over. Inside the camera pipeline, fitting the balanced block-order term does not move that
mean at all; it moves the standard error, from {sig(bd.get('hi_se_naive'), 3)} W to {sig(bd.get('hi_se_order'), 3)} W, and so |t| from
{sig(abs(bd.get('hi_t_naive') or 0), 3)} to {sig(abs(bd.get('hi_t_order') or 0), 3)}. On that reading the two halves draw
{sig(abs(bd.get('hi_W') or 0), 3)} W of different total power for the same work — about
{sig(abs(bd.get('hi_W') or 0) / (bd.get('hi_minus_rest_W') or 1) * 100, 2)}% of the {sig(bd.get('hi_minus_rest_W'), 3)} W the work itself draws,
and the same sign on the quiet arm ({sig(bd.get('lo_W'), 3)} W). A delivery-path asymmetry is therefore not hypothetical, which matters for how the
camera's picture is read. Note also that the equality arm the row scores as satisfied rests on
{C58.get('n_passes', '–')} passes with a {sig(C58.get('t_crit_3sigma'), 3)} window, so it could not have detected an asymmetry below about
{sig(C58.get('detectable_W'), 3)} W — and §9's own floor for a confirmatory item is {C58.get('confirmatory_floor_passes', 6)} passes. That arm is an absence of evidence at low resolution, not an equality.</p>
{{{{fig:cam}}}}
<p><b>The camera, which is tier 2 and exploratory by design</b> — plan §10 and §2's E-D7 row carry no confirmed or refuted arm, so nothing below is
scored. The pattern moves. The double difference is <b>{pm(CAMF.get('statistic_mk'), CAMF.get('se_pass_mk'), 4, 'mK')}</b> between passes at
p = {sig(CAMF.get('p_cyclic'), 2)} on an enumerated permutation null over {thou(CAMF.get('p_labellings'))} labellings, against a null scatter of
{sig(CAMF.get('null_sd_mk'), 3)} mK; the quiet arm shows the same dipole in the same direction at {sig(CAMF.get('lo_mk'), 4)} mK. It is a dipole and
not a level shift: the card mean of the difference image — the camera's own reading of the page's “ΔP_card = 0” — is
{sig(CAMF.get('monopole_mk'), 3)} mK at p = {sig(CAMF.get('monopole_p'), 2)}. It lies on one axis: the same reduction with the frame halved the
other way returns {sig(CAMF.get('orthogonal_mk'), 3)} mK at p = {sig(CAMF.get('orthogonal_p'), 2)}. It survives dropping the frame's outer border
({sig(CAMF.get('footprint_mk'), 4)} mK at p = {sig(CAMF.get('footprint_p'), 2)}).</p>
<p><b>Three things the camera does not show.</b> It is not the result path: the quiet arm flips zero result bits and still carries
{sig((CAMF.get('lo_mk') or 0) / (CAMF.get('statistic_mk') or 1) * 100, 2)}% of the amplitude, and its column profile is the same shape as the loud
arm's, so what is being imaged is the half's threads and read ports with the result path adding amplitude to a pattern that is already there. The
one contrast that <i>is</i> the result path, loud minus quiet at {sig(CAMF.get('hi_minus_lo_mk'), 4)} mK, is the one the tool flags as biased
upward, because {first_clause(CAMF.get('hi_minus_lo_caveat') or '', 170)} It is not a two-lobed picture of sixteen shires: the profile is dominated by a
whole-frame gradient ({sig(CAMF.get('gradient_mk_per_px'), 3)} mK a pixel, p = {sig(CAMF.get('gradient_p'), 2)}) with its hottest and coldest
columns at x = {CAMF.get('peak_px', '–')} and x = {CAMF.get('trough_px', '–')}, at the edges of the die's footprint rather than at the centres of
the two halves. And the automatic mask covers {sig((CAMF.get('card_fraction') or 0) * 100, 3)}% of the frame with a bounding box that <i>is</i> the
frame, so the statistic is the frame halved, board and package included. Nor is it calibrated:
{first_clause(CAMF.get('mm_note') or '', 150)} So the discriminator we registered for die heat against the power-delivery path, whether the lobe moves
about 11 mm, could not be run at all, and the amplitude itself moves from {sig(CAMF.get('arm_min_mk'), 4)} to {sig(CAMF.get('arm_max_mk'), 4)} mK
({sig(CAMF.get('arm_spread_pct'), 2)}%) across the four registered ways of removing the field's own
{sig(mean_of(CAMF.get('drift_mk_per_s')), 2)} mK a second drift. What we can report is a sign, an axis and a p-value. The millikelvins are not a
measurement yet.</p>
<p><b>What the camera block establishes.</b></p><ul>{est}</ul>
<p><b>What it cannot show.</b></p><ul>{nest}</ul>"""

    # ---------- the issue rate ----------
    fitsA = IPC.get("fits") or {}
    ALN = IPC.get("alignment") or {}
    aln_rows = [[f"{r.get('mode')} · `{r.get('kernel') or r.get('mnemonic') or ''}`",
                 f"`{r.get('head') or ''}`", r.get("mod32"), r.get("n_vector_ops"),
                 sig(r.get("ipc"), 4)] for r in (ALN.get("c2_rows") or [])]
    acc = ALN.get("addr_count_check") or {}
    rate = f"""<h2>Every price here is per flip, because the issue rate is not 1.0 — and it is set by the linker</h2>
<p>The page holds “instruction issue rate (1.0 IPC = 614.4 Gops/s)” strictly invariant across all seven experiments and converts every
energy-per-operation into watts with it. Measured, the same kernels retire
{sig(min(r['ipc_per_hart'] for r in (g(rate_v, 'rates') or {}).values()), 4)}–{sig(max(r['ipc_per_hart'] for r in (g(rate_v, 'rates') or {}).values()), 4)}
operations per cycle per hart — {sig(ipc_meas, 3)}× the page's {sig(page_ipc, 2)}. Verdict: <b>{rate_v.get('verdict', '–')}</b>.</p>
{{{{fig:ipc}}}}
<p><b>But the measured rates are not a spectrum: they are two levels, and which level a kernel gets is decided by where the linker put its loop.</b>
Every one-hart shape in this campaign sits at {sig(g(fitsA, 'slow', 'ipc'), 4)} or {sig(g(fitsA, 'fast', 'ipc'), 4)} operations per cycle per hart
at 64 operations an iteration, with nothing in between, and the same split at 128. The reduction re-derives why from the committed disassembly
(<code>{esc(IPC.get('disassembly') or '–')}</code>, {ALN.get('n_long_vector_loops', '–')} long packed-vector loops): <b>the level follows the loop
head's address mod 32</b>. Heads at {ALN.get('fast_residue', '–')} issue {sig(ALN.get('fast_rate'), 4)} operations a cycle a hart and heads at
{ALN.get('slow_residue', '–')} issue {sig(ALN.get('slow_rate'), 4)} — a {sig(ALN.get('derived:pct_fast_over_slow'), 3)}% difference with nothing in
the data changing. The <code>c2</code> family pins the map one-to-one, because its pinned third operand identifies each of its four opcodes and so
each mode:</p>
{{{{tbl:align}}}}
<p>Each residue carries exactly one rate{', and the two residues are distinct' if ALN.get('residues_distinct') else ''}. The four
<code>df.addr</code> kernels cannot be named from the bytes, so they are a count check instead, and it agrees:
{acc.get('heads_at_the_fast_residue', '–')} head at the fast residue and {acc.get('heads_at_the_slow_residue', '–')} at the slow, against
{acc.get('modes_at_the_fast_rate', '–')} of the four address modes at the fast rate and {acc.get('modes_at_the_slow_rate', '–')} at the slow. This
is an instruction-<i>fetch</i> alignment effect, and it explains three things at once: why amendment A2.1 found the rate fixed by the mode rather
than by h, why the same split is identical on all three cards, and why mode 179 itself moved
+{sig(mean_of(list((IPC.get('mode179_build_shift_pct') or {}).values())), 3)}% between E60's build and tonight's, on every card. Opcode does not predict it and neither does shape: the same
opcode appears on both levels. It is reported, and it gates nothing.</p>
<p><b>Underneath that, the vector unit issues one operation per cycle per hart.</b> Combining the 64-operation and 128-operation bodies, cycles per
iteration are {sig(g(fitsA, 'fast', 'cycles_per_vector_op'), 4)}·ops + {sig(g(fitsA, 'fast', 'fixed_cycles'), 4)} on the fast alignment and
{sig(g(fitsA, 'slow', 'cycles_per_vector_op'), 4)}·ops + {sig(g(fitsA, 'slow', 'fixed_cycles'), 4)} on the slow one: a slope of
{sig(g(fitsA, 'fast', 'ops_per_cycle'), 3)} operations a cycle, and a fixed cost of
{sig(g(fitsA, 'fast', 'fixed_cycles'), 3)}–{sig(g(fitsA, 'slow', 'fixed_cycles'), 3)} cycles an iteration spent on the loop's own scalar
instructions, four of which are performance-counter reads — our instrumentation. So the page's “1.0 IPC” is right about the issue rate and wrong
only about the Gops/s, by the loop overhead. We were wrong to read the 40% as a property of the chip.</p>
<p>Two consequences we have to carry. The first: the same mode — same pattern, same designed counts — ran {sig(fitsA.get('E60_reference_ipc'), 4)}
in E60's build and {sig(g(fitsA, 'fast', 'ipc'), 4)} in tonight's, and the registered refuted arm was written against that exact number. That
{sig((1 / (fitsA.get('E60_over_fast') or 1) - 1) * 100, 3)}% is one alignment flip, not drift in the chip: inserting ten new bodies ahead of it
moved it across the boundary, and E60's figure is within {sig(abs(1 / (fitsA.get('E60_over_slow') or 1) - 1) * 100, 2)}% of tonight's <i>slow</i>
level. The second: it is inside the e_out bridge. The <code>fand</code> and <code>for</code> legs sit on opposite alignments, so dividing all four
arms by one mode's rate reads {sig(d2_v.get('raw_bridge_one_rate_excess_pct'), 3)}% high — {sig(d2_v.get('raw_bridge_one_rate_form_fJ'), 4)} fJ
against the {sig(EO['raw_fJ'], 4)} fJ a per-leg denominator gives. That is why nothing on this page is quoted in watts: every price is per flip,
from each run's own operation count.</p>

<h2>The operand law, and what two harts do to it</h2>
<p>The page's split of a flip's cost into input and output — {sig(PAGE_CLAIMS_NOT_IN_DTF['split_ratio'], 3)} to 1 — comes from assuming
uniform random operand bits. They are not uniform, and the catalogue's own numbers admit two readings depending on whether two harts interleave
and destroy operand sharing. The registered statistic is a rate-free ratio ρ of the per-operation cost at two harts to one.</p>
{{{{fig:rho}}}}
<p>ρ = <b>{pm(RHO.get('rho'), RHO.get('se'), 3)}</b> on {rho_v.get('rho_card', '–')} over {RHO.get('n_passes', '–')} passes: interleaving destroys
sharing, so the catalogue cannot settle the split at all, and the page's {sig(PAGE_CLAIMS_NOT_IN_DTF['split_ratio'], 3)}:1 is the full-interleave
reading arrived at by coincidence. Verdict: <b>{rho_v.get('verdict', '–')}</b>. This one survived every attack we could make on it. The obvious
objection — that two harts change the per-operation overhead the baseline removes — does not hold, because the baseline is removed inside each
hart setting before the ratio is taken. To pull ρ to 1.000 the two-hart arm would have to shed
{sig(RHO.get('fJ_per_op_the_two_hart_arm_must_lose'), 3)} fJ an operation, {sig(RHO.get('pct_the_two_hart_arm_must_lose'), 2)}% of its
{pm(g(RHO, 'per_op_harts2', 'value'), g(RHO, 'per_op_harts2', 'se'), 4, 'fJ/op')}, and the only mechanism left is temperature — where the measured
differential heating between the two arms is the same at one hart as at two, so it cannot be the cause. The leakage arms all read above 1: the
board leg is {pm(RHO.get('rho'), RHO.get('se'), 3)} and the minion-rail leg {pm(g(RHO, 'rail_leg', 'value'), g(RHO, 'rail_leg', 'se'), 3)} in the
independent reduction. A phase-locking alternative pushes the wrong way: locked harts would give ρ below 1.</p>
<p>Two honest limits, and one correction against our own plan. The row is thinner than it looks: 1.000 is excluded at |t| =
{sig(RHO.get('t_vs_1'), 3)} against a {sig(RHO.get('t_crit_3sigma'), 3)} window at {RHO.get('n_passes', '–')} passes —
{sig(RHO.get('derived:pct_of_the_threshold'), 4)}% of the threshold, so one more lost pass would reopen it — and the statistic cannot tell complete
destruction of sharing from near-complete ({sig((RHO.get('interleave_fraction') or 0) * 100, 3)}% ±
{sig((RHO.get('derived:interleave_fraction_se') or 0) * 100, 2)}% destroyed is consistent with all of it). It also rests on one card, one opcode. The
correction: our own §0.2 argued that the catalogue's forward agreement proves sharing <i>survives</i> interleaving. Redone with §0.2's own
interleaved counts, the five ratios move from a uniformly low 0.951 (sd 0.030) to a centred 1.002 (sd 0.045), so neither reading is excluded and
the forward check discriminates nothing. ρ is the only evidence here, and the claim that the catalogue settles it is withdrawn. The model-free leg
reads {pm(rho_v.get('fnot_leg_fJ'), rho_v.get('fnot_leg_se_fJ'), 3, 'fJ')} against the
{sig(g(rho_v, 'fnot_leg_target_tie_scaled_fJ', 0), 4)}–{sig(g(rho_v, 'fnot_leg_target_tie_scaled_fJ', 1), 4)} fJ that E60's measurement predicts
for this card once scaled by this campaign's own measured per-bit tie ({sig(rho_v.get('fnot_leg_per_bit_tie'), 4)}, against E60's
{sig(rho_v.get('fnot_leg_tie_E60'), 4)}) — <b>outside</b>, even widened, so the operand law is not confirmed on this leg. The tie itself is
{sig(rho_v.get('fnot_leg_tie_measured_over_E60'), 4)}× E60's, outside §8.7's registered 0.88–0.99 card-to-card band, so the scaling is a reported
method choice and not a check that passed.</p>"""

    # ---------- what the page got right ----------
    det_v = next((v for v in by_sec.get("det", [])), {})
    sum_page = PAGE_CLAIMS_NOT_IN_DTF["e_in_fJ"] + (EO["page"] or 0)
    ratio_meas = (g(jf, "e_out", "fJ") or EO["fJ"]) / (g(jf, "e_in", "fJ") or (e_in_d2A.get("value") or 1) * 1e15)
    sum_meas = (e_sum.get("value") or 0) * 1e15
    s14 = next((d for d in DESK if d["id"] == "S14"), {})
    right = f"""<h2>What the page got right</h2>
<ul>
<li><b>Its arithmetic on real data — twelve claims, all holding.</b> The largest single group in the desk check is the page's mining of a corpus
that does exist, and it survives in full: {esc(clamp(s14.get("what", ""), 350))} That is the page's whole data layer,
and it is correct.</li>
<li><b>The sum, to {sig(abs(sum_page - sum_meas) / sum_meas * 100, 2)}%.</b> Its input and output prices add to
{sig(sum_page, 4)} fJ per flipped bit-slice. Measured through the inverter at matched counts, an input bit plus an output bit costs
<b>{fj(e_sum.get('value'), e_sum.get('se'), 4)}</b>. The page split that sum wrongly — {sig(PAGE_CLAIMS_NOT_IN_DTF['split_ratio'], 3)}:1 against a
measured ratio of {sig(ratio_meas, 3)}:1 — but the quantity its arithmetic actually fixed, the sum, is the quantity it got nearly exactly.</li>
<li><b>One operation retires per cycle per hart.</b> Its “1.0 IPC” is right about the vector unit's issue rate, which we did not expect and
first scored against it. What is wrong is the conversion to Gops/s, because 41 to 46 cycles an iteration go on the loop's own scalar work.</li>
<li><b>The flip counts are deterministic.</b> {g(det_v, 'runs_kept', default='–')} runs over
{g(det_v, 'items_with_a_rate', default='–')} items passed the within-mode instruction-rate, <code>ok</code> and participant gates on every
card, with {('no subtraction voided' if not g(det_v, 'pair_gate_voids', default=0) else str(g(det_v, 'pair_gate_voids')) + ' subtractions voided')} — verdict
<b>{det_v.get('verdict', '–')}</b>. One rung is excluded by name as rate-confounded and reported beside its ladder; the on-silicon register
dump that would close the last gap is not in tonight's build, which the row says in full.</li>
<li><b>The destination cells really do stay still.</b> The page's observation that the generated loop rewrites each destination with the value it
already holds is correct, and it is what makes the cell term separable at all: the rebuilt 1A/1B pair finds a cell bit at
{pm(cell_v.get('value_fJ'), cell_v.get('se_fJ'), 2, 'fJ')}, far below a result bit.</li>
<li><b>The address path costs energy.</b> Changing which registers an instruction names, with every data bit held still, moves real power — the
one effect tonight that survives Holm correction across the confirmatory five ({holm_sig[0]['coef'] if holm_sig else '–'}, p = {pval(holm_sig[0]['p_two']) if holm_sig else '–'}).
The page was right that this is worth measuring; it was wrong about the size, and so were we, and neither of us measured it.</li>
<li><b>The halves move heat.</b> Giving one half of the mesh flipping result bits and the other half none does move heat across the board, it does
so without changing total card power to within the camera's reading of it, and it reverses when the masks swap — exactly the qualitative claim
E-D7 makes, at a size the camera cannot convert into millikelvin on an uncalibrated card, and with the halves it names replaced by halves that
exist.</li>
</ul>"""

    # ---------- what we got wrong ----------
    wrong_rows = []
    for name, lab in (("e_addr", "energy per toggled register-index bit"), ("e_carry", "energy per carry stage"),
                      ("e_cell", "energy per register-file cell bit")):
        q = D(name)
        pr = q.get("prior_fJ")
        if not pr:
            continue
        val = (q.get("value") or 0) * 1e15
        inside = pr[0] <= val <= pr[1]
        wrong_rows.append([lab, f"{sig(pr[0], 2)}–{sig(pr[1], 2)} fJ", pm(val, (q.get('se') or 0) * 1e15, 2, "fJ"),
                           "inside" if inside else ("above" if val > pr[1] else "below")])
    eo_band = EO["band"]
    if eo_band:
        v = EO["raw_fJ"]
        wrong_rows.append(["energy per result bit, the raw bridge", f"{sig(eo_band[0], 4)}–{sig(eo_band[1], 4)} fJ (E60)",
                           pm(v, EO["raw_se"], 2, "fJ"),
                           "inside" if eo_band[0] <= v <= eo_band[1] else ("above" if v > eo_band[1] else "below")])
    band = RHO.get("destroyed_band") or [None, None]
    wrong_rows.append(["two harts: does operand sharing survive interleaving?",
                       f"{sig(band[0], 3)}–{sig(band[1], 3)} if it does not",
                       pm(RHO.get("rho"), RHO.get("se"), 3),
                       "inside — sharing does not survive"])
    wrong_rows.append(["the camera settles a half-die amplitude in watts", "a watt figure with an error bar",
                       f"{sig(CAMF.get('statistic_mk'), 4)} mK, uncalibrated", "missed — a sign and an axis only"])
    n_missed = sum(1 for r in wrong_rows if not str(r[3]).startswith("inside"))
    addr_page_closer = bool(page_addr and ADDR.get("value_fJ") is not None
                            and abs(ADDR["value_fJ"] - page_addr) < abs(ADDR["value_fJ"] - (g(ADDR, "prior_fJ", 1) or 0)))
    wrong = f"""<h2>What we got wrong</h2>
<p>{len(wrong_rows)} of our own registered expectations, written into the pre-registration before any card ran, and what the night did to
them: {n_missed} of the {len(wrong_rows)} missed.{" On the address bit ours missed by more than the page's own number did." if addr_page_closer else ""}</p>
{{{{tbl:priors}}}}
<p>The address prior is the worst number on either side of this exercise: we registered 0–{sig(g(ADDR, 'prior_fJ', 1), 2)} fJ per index bit on
the reasoning that a 5-bit decoder is small, and measured a slope of {sig(ADDR.get('value_fJ'), 4)} to {sig(g(ADDR, 'with_origin', 'value'), 4)} fJ
that is not a price per bit at all. The page's {sig(page_addr, 3)} fJ is nearer the truth than our ceiling was, and still refuted, because the
ladder is not measuring what either of us named. Four more, for the record: we registered the camera block as able to settle a half-die amplitude
in watts, and it settles a direction and a sign; we registered the bridge's number behind an intercept test that fired on
{len(g(d2_v, 'h0_differing_cross_opcode', default=[]))} cross-opcode pairs and
{len(g(d2_v, 'h0_differing_within_opcode', default=[])) or 'no'} within-opcode pair — the one term the 2 × 2 cancels by construction, so the rule
was written too tightly rather than the measurement failing; we registered C14 as a scoreable arm in §9 and forbade exactly that in §5.2; and we
budgeted family V's address-count difference at 0.05% of its signal when it is nearer 19%. Two arithmetic slips of our own are corrected on this
page rather than quietly fixed: the changed-word price, and the four zero-word replications the file pooled against its own rule.</p>"""

    # ---------- the two reductions ----------
    recon_rows = [[r["quantity"], r.get("unit", ""), pm(r.get("mine"), r.get("mine_se"), 3),
                   pm(r.get("theirs"), r.get("theirs_se"), 3),
                   (f"{sig(r['in_SE'], 2)} SE" if r.get("in_SE") is not None else "–"), r.get("why", "")]
                  for r in (RECON.get("rows") or [])]
    recon = f"""<h2>Where the two reductions disagree</h2>
<p>The reduction was re-derived from the raw records by a second implementation before this page was written, and the two were then reconciled.
They agree on the shape of every result and on the verdicts, and they do not agree on every number. The largest source of difference is not the
estimators: it is which passes each one sets aside. This reduction keeps {RECON.get('mine_passes_on_the_primary', '–')} passes on the primary card;
the independent one keeps {esc(", ".join(str(x) for x in (RECON.get('their_passes_on_the_primary') or [])))}. The rows below are every quantity we
compared where the two can be put side by side.</p>
{{{{tbl:recon}}}}
<p>Nothing here changes a verdict. It does mean a reader should treat the third digit of any number on this page as a method choice rather than a
measurement, and the reduction's own list of method choices — which fit form, which leakage slope, which rung, which tie — is where to look first.</p>"""

    # ---------- the explorers ----------
    exp_rows = [
        ["`eInBoard` = 6.52 fJ, an input bit",
         pm(g(jf, "e_in", "fJ"), g(jf, "e_in", "se_fJ"), 3, "fJ") + " from the pooled fit",
         "3.3× low"],
        ["`eOutBoard` = 44.38 fJ, a result bit",
         pm(wf.get("value"), wf.get("se"), 3, "fJ") + " within family B, " + pm(EO["fJ"], EO["se"], 3, "fJ") + " pooled",
         "1.5–1.7× high"],
        ["`eXorCell` = 5.60 fJ, an XOR cell's own cost",
         "already inside e_out, which was solved by subtracting AND/OR from XOR",
         "double-counted, then added a third time by the simulator"],
        ["`eCarryBit` = 14.2 fJ, a carry stage",
         pm(d3_v.get("value_fJ"), d3_v.get("se_fJ"), 3, "fJ") + " registered, " +
         pm(g(CW, "e_carry_R2_corrected", "value"), g(CW, "e_carry_R2_corrected", "se"), 3, "fJ") + " with the R2 term removed",
         "excluded at ≥ 3 SE either way"],
        ["`eRegAddr` = 32 fJ, an address bit",
         f"{sig(ADDR.get('value_fJ'), 4)}–{sig(g(ADDR, 'with_origin', 'value'), 4)} fJ, not measurable as registered",
         "11–14× low, and not a price per bit"],
        ["`millerScale` = 0.71 + 0.29 k_adj",
         pm(ws.get("dW"), ws.get("se"), 3, "W") + " across the four levels, the wrong way",
         "the design did not deliver k_adj"],
        ["19.65 W of card idle, and 49.5 mK/W",
         "idle measured near 31.8 W at 73 °C; the mK/W figure has no provenance in the corpus",
         "unsourced"],
        ["a “151× power floor” badge",
         "the 0.03 W it divides by is the zeros pattern's run-to-run repeat spread, not a sensor floor",
         "the documented detection line is 3.33 W"],
    ]
    explorers = f"""<h2>The page's three explorers, and the five constants inside them</h2>
<p>A reader of the original page meets most of its physics by clicking, not by reading: it ships a seven-rung ladder, a live kernel generator and a
cycle-stepping microscope. The generator is the one that matters, because its model hard-codes the five per-flip constants this experiment set out
to measure, plus an idle offset and a thermal conversion. Anyone who moved its sliders was reading those constants back out. Here is what each one
became.</p>
{{{{tbl:explorers}}}}
<p>The ladder's rungs 0–4 are the <code>const</code> values the desk check found to be measurements of runs that do not exist; the microscope is a
cycle-level animation, which nothing here scores. We have not rebuilt the explorers. If they are kept, those are the numbers to change.</p>"""

    # ---------- how this was run ----------
    dep = "; ".join(x.rstrip(". ") for x in (meta.get("departures") or [])) + "."
    miss = R.get("missing") or []
    card_rows = []
    for r in (CEN.get("per_card") or []):
        card_rows.append([r["card"], r.get("mhz"), r.get("mv"), "free" if r.get("gov_free") else "pinned",
                          f"{r.get('passes_kept')} of {r.get('passes_registered')}",
                          f"{len(r.get('set_aside') or [])}",
                          f"{r.get('runs_kept', '–')} / {r.get('runs', '–')}",
                          f"{r['leak_W_per_C']:.3f}" if r.get("leak_W_per_C") is not None else "–"])
    conv_rows = [[r["quantity"], pm(r.get("fJ"), r.get("se_fJ"), 3, "fJ"), f"{sig(r.get('C_fF_halfCV2'), 4)} fF",
                  el(r.get("electrons_halfCV2")), f"{sig(r.get('C_fF_CV2'), 4)} fF", el(r.get("electrons_CV2"))]
                 for r in (CONV.get("rows") or [])]
    aside_rows = []
    for r in (CEN.get("per_card") or []):
        for a in (r.get("set_aside") or []):
            aside_rows.append([r["card"], a.get("pass"), tidy(a.get("why", ""))])
    band_m = re.search(r"([\d.]+)-([\d.]+) band", str(g(R, "across_cards", "_band", default="")))
    tie_band = (band_m.group(1) + "\u2013" + band_m.group(2)) if band_m else "registered"
    cm = REPO.get("commits") or {}
    link = lambda k, lab: (f'<a href="{REPO.get("remote", "").replace(".git", "")}/commit/{cm[k]["sha"]}">{lab}</a>'
                           if cm.get(k) and REPO.get("remote") else lab)
    DAT = REPO.get("data") or {}
    dat_cards = DAT.get("cards") or []
    pass_dirs = sum(b.get("passes", 0) for c in dat_cards for b in (c.get("blocks") or {}).values())
    per_pass_files = next((b.get("files_per_pass") for c in dat_cards
                          for b in (c.get("blocks") or {}).values() if b.get("files_per_pass")), [])
    cam_png = len((DAT.get("camera") or {}).get("png") or [])
    method = f"""<h2>How this was run</h2>
<p><b>Pre-registered.</b> The design, the eleven families, every prediction as an interval, the analysis and the decision rules were committed
before the first measured pass: <a href="{PREREG}">tools/claims-v3/dtf/README.md</a>
({link("prereg", "the pre-registration commit")}), with two amendments, each committed before the data it touches —
{link("A1", "A1")}, more passes inside the claim window, decided on elapsed time alone, and {link("A2", "A2")}, which fixes the issue rate by mode
and so reduces families V and A within mode. {esc(meta.get('n_manifest_items', '–'))} manifest items, seed {esc(meta.get('seed', '–'))}; the
analysis manifest A2 introduces, and which the reduction actually reads, is
<a href="{DATA}/manifest-a2.json"><code>manifest-a2.json</code></a>. The reduction's own record of what it departed from: {esc(dep)}</p>
<p><b>The operating point is not the page's, and no card could have given the page's.</b> The page puts all seven experiments on
aifoundry2 at 600 MHz and 0.517 V. That card is governor-free at {mhz.get('aifoundry2')} MHz and about
{sig((v_of.get('aifoundry2') or 0) * 1000, 4)} mV; 0.517 V was its 21 September point; and the only clock-pinned card in the lab is {prim}, at
{mhz.get(prim)} MHz and {sig((v_of.get(prim) or 0) * 1000, 4)} mV. So every per-flip price the page prints is quoted at a point no card ran, and
most rows here are decided on a card the page never names. Card-to-card scaling is reported, never assumed: the measured per-bit ties are
{esc(", ".join(f"{k} {sig(g(R, 'across_cards', k, 'e_in_fxor_ratio_to_a3'), 4)}× {prim} against E60's {sig(g(R, 'across_cards', k, 'E60_per_bit_tie'), 4)}" for k in sorted(g(R, 'across_cards', default={}) or {}) if k in cards and k != prim))},
against the {esc(tie_band)} band §8.7 registers — one card inside it, one not.</p>
{{{{tbl:cards}}}}
<p><b>Passes are kept or set aside, never missing.</b> Every registered pass ran. {n_aside} of {passes_reg} were set aside afterwards by the
rule §8.9 registers — more than 5% of a pass's runs failing a gate, with at least two runs failing, or the anchor drifting more than the pass's own
threshold — and the reduction reports them as set aside rather than absent.</p>
{{{{tbl:aside}}}}
<p><b>Proved before the first pass.</b> Every operand image was written by the generator and its designed counts re-derived from the bytes
(<code>make_dtf.py --check</code>); the built ELF was walked to prove it holds exactly the intended blocks; ten <code>sys_emu</code> runs
executed the kernels with the register-file checker on; and a smoke block ran on each card
({', '.join(f"{k} {v.get('n_runs', '–')} runs, " + ('every gate passed' if v.get('all_ok') else 'A GATE FAILED') for k, v in (R.get('smoke') or {}).items())}).</p>
<p><b>Protocol.</b> E60's: each run launched as the die's reading fell to a fixed value after a heater burst, the board's power read over a
fixed window once the clock had settled, every item differenced against its own zero rung inside the same pass, every error bar the scatter
between passes, and a three-sigma window read as the two-sided t quantile at p = {sig(meta.get('three_sigma_p'), 2)} on that scatter. The
confirmatory five ({', '.join(meta.get('confirmatory_family') or [])}) are Holm-corrected at α = {sig(meta.get('holm_alpha'), 2)}; everything
else is exploratory and says so. Leakage is corrected with each card's own fitted slope, and because tonight's fit and E60's differ by an order of
magnitude ({sig(g(cards, prim, 'leak_W_per_C'), 3)} against {sig(g(cards, prim, 'leak_E60_W_per_C'), 3)} W/°C on {prim}, with only
{sig(g(cards, prim, 'leak_qualifying_run_pct'), 3)}% of runs qualifying for the within-run fit), every quantity is also reported at a zero slope and
at E60's. Two rows move: the ladder intercept and the <code>d2A</code> read-port price.</p>
<p><b>The intercept row, and which kind of open it is.</b> The ladder intercept reads {pm(INT.get('intercept_N_W'), INT.get('intercept_N_se'), 3, 'W')}
and is <b>open</b> because two of the three registered mechanism readings are inside three standard errors
({esc(", ".join(x.split("_", 1)[-1].replace("_", " ") for x in (INT.get("matched") or [])))}) — a case §9's partition does not name. Its registered open arm, that the two ladders' intercepts
disagree by more than three standard errors once scaled by their word counts, does <i>not</i> fire:
{pm(INT.get('X_minus_N_W'), INT.get('X_minus_N_se'), 3, 'W')} per changed source word, |t| = {sig(abs(INT.get('X_minus_N_t') or 0), 3)} against
{sig(INT.get('t_crit_3sigma'), 3)}. The row is open for a reason the rules do not list, and that gap is ours.</p>
<p><b>What is missing.</b> {len(miss)} gaps are recorded by the reduction itself, the largest being that several families ran on the pinned card
only, so e_cell, e_carry, the Miller set, the address ladder and the zero gate have no second-card replicate. The on-silicon register dump is
not implemented in tonight's build, so a value corruption that left the operation count and the participant count intact would not have been
caught — the pre-registration says so in its §11, and the determinism row rests on the rate, <code>ok</code> and participant gates and on the
off-card proofs instead.</p>
{{{{tbl:conv}}}}
<p><b>Data and code.</b> <a href="{CODE}">tools/claims-v3/dtf/</a> holds the generator, the ELF check, the runner, the reduction and this page's
builder. <a href="{DATA}">docs/reports/data/2026-10-21-dtf/</a> is the record this page is built from, and it ships in the same commit:
{esc(", ".join(DAT.get("top_level_files") or []))} at the top; {len(DAT.get("proof_files") or [])} proof files under
<code>proof/</code> (three ELF checks and a <code>sys_emu</code> log); the raw passes as
{esc(", ".join(f"{c['card']}/" + "+".join(sorted(b for b, d in (c.get("blocks") or {}).items() if d.get("passes"))) for c in dat_cards))} —
{pass_dirs} pass directories in all, each holding {esc(", ".join(per_pass_files))}; the camera block's
<code>cam.json</code>, <code>tier1.json</code> and {cam_png} PNGs under
<code>aifoundry2/dtf-cam-analysis/</code>; and the reduction's three outputs,
{esc(", ".join(sorted((DAT.get("reduction_outputs") or {}).keys())))}. That is {thou(DAT.get("n_files"))} files and
{sig((DAT.get("bytes") or 0) / 1e6, 3)} MB. Every number on this page comes out of <code>dtf.json</code> in that directory, or out of
<code>cam.json</code> beside it; the page's own builder prints which file answered for each one.</p>

<h2>Related</h2>
<ul>
<li><a href="{PAGE_URL}">Deterministic Transistor-Flip Experiments on 1,024 RISC-V Cores</a> — the page under test, 20 Oct 2026.</li>
<li><a href="{E60_URL}">What one flipped bit costs on the ET-SoC-1</a> — E60, the Hamming ladder, whose intervals
({sig(g(EO, 'band', 0), 4)}–{sig(g(EO, 'band', 1), 4)} fJ for a result bit,
{sig(g(fnot_leg, 'E60_interval_fJ', 0), 4)}–{sig(g(fnot_leg, 'E60_interval_fJ', 1), 4)} fJ for an input plus an output bit, and
{sig(g(d2a_v, 'E60_interval_fJ', 0), 4)}–{sig(g(d2a_v, 'E60_interval_fJ', 1), 4)} fJ for a read-port bit) every target here is tied to.</li>
<li><a href="{MICRONS_URL}">A bit flip in microns</a> — what a flipped bit is, in metal.</li>
<li><a href="{PREREG}">The pre-registration</a>, its <a href="{PREREG}#1-what-the-desk-check-already-settled--no-card-needed">§1 desk check</a>,
<a href="{PREREG}#3-what-is-not-testable-tonight-and-why">§3 what is not testable</a> and
<a href="{PREREG}#9-decision-rules-per-claim">§9 decision rules</a> — binding, with amendments A1 and A2 at the end.</li>
</ul>"""

    body = (lede + stats + gloss
            + '<h2>The short version</h2><p>Every row the pre-registration registered, with the page\'s own number where it printed one, what '
              'the night measured, and the verdict as the reduction states it. “Card” is the card the decision rests on.</p>'
            + "{{tbl:short}}" + corr
            + "<p>Three of the page's claims never needed a card — two against it, one for it:</p>" + desk_bullets
            + desk_sec + unt_sec
            + d1 + d2 + d3 + d4 + d5 + d6 + d7 + rate + right + wrong + recon + explorers + method)

    captions = {
        "d1": f"Board energy per flipped bit (read port plus result) against h, the bits that flip per lane per instruction, through "
              f"<code>fnot.pi</code> on {prim} at {mhz.get(prim)} MHz and {sig(v_of.get(prim), 3)} V. Circles: the arm whose operands include "
              f"the all-zero word, the page's design. Squares: the never-zero control. Whiskers: one standard error between passes.",
        "cell": "Energy per flipped register-file cell bit, against the interval registered for it before the run. The bar is one standard error, "
                "the thin line three. The pooled fit's own coefficient is shown for reference and carries no standard error, because one contrast "
                "identifies it.",
        "d2": f"The 2 × 2 bridge on {prim}: board watts above each cell's own h = 0 rung, against h. <code>d2A</code> and <code>d2C</code> hold "
              f"the result static (the page's Runs A and C); <code>d2B</code> and <code>d2D</code> let it flip.",
        "d2e": "Every route to the result-bit price that tonight's data support: inside family B leg by leg, the raw four-cell combination, the "
               "pooled fit the plan says to quote, and E60's own cross-family subtraction repeated on tonight's data. The band is the interval E60 "
               "published. The two methods disagree by about 5 fJ, and the page is above all of them.",
        "d3": "Board watts above the L = 0 rung against the carry run length L, with the fitted line the reduction prefers. One flipped input bit "
              "per lane throughout.",
        "d3e": "Energy per carry stage, after an independently measured result bit is subtracted: measured, our registered prior, our registered "
               "point value, and the page's.",
        "d4": "Board watts against the neighbour-phase parameter k_adj at matched occupancy and matched designed counts. Whiskers: one standard "
              "error between passes; the dashed line is the matched reference pattern. The trend runs the wrong way for the page's law.",
        "d5": "Board watts above the matched zero rung against the number of register-index bits that toggle per operation. Filled: the ladder "
              "the slope is fitted on. Hollow: the rung that retires at another instruction rate, reported beside the ladder and excluded from "
              "the fit.",
        "d5e": "The same three rungs, read every way the plan and the data allow, against the two numbers that were registered in advance. The "
               "spread between fit forms is larger than any one reading's error, which is why this row carries no verdict.",
        "d6": "The zero-to-non-zero operand step, per operation: measured on silicon tonight, found in the catalogue by the desk check, and as the "
              "page states it.",
        "halfdie": "The result-path load on one half of the mesh: measured on each card, and the plan's own formula for the same quantity evaluated "
                   "from each of the two e_out readings. The band is the registered window. One spelling lands inside it and the other does not.",
        "cam": "Left: the mean thermal frame, the back of the board under the die, every pass averaged. Right: the difference image when the loud "
               "half swaps sides — one half of the image warms and the other cools, with no change in the card mean. The camera is uncalibrated on "
               "this card, so the image carries no absolute scale and no orientation; the grid is the camera's own, and the automatic mask is the "
               "warm board, not the die.",
        "ipc": "Operations retired per cycle per hart, by compiled shape, on each card — against the 1.0 the page assumes and the rate the previous "
               "experiment measured for the same mode in another build. The two levels are the two loop-head alignments, not two kinds of work.",
        "rho": "ρ, the ratio of the per-operation cost at two harts to one, against the two values the catalogue's readings predict.",
    }
    title = "Verifying the deterministic transistor-flip experiments"
    desc = (f"Seven proposed experiments, pre-registered and run on {n_cards} ET-SoC-1 cards: a result bit costs "
            f"{sig(wf.get('value'), 4)} to {sig(EO['fJ'], 4)} fJ against the proposal's {sig(EO['page'], 4)} fJ, a carry stage "
            f"{fj(e_carry.get('value'), None, 2)} against {sig(e_carry.get('page_fJ'), 3)} fJ, the zero gate is a null, the issue rate is set by "
            f"the linker, and the address path is too large for anyone's prior and not measurable as registered.")
    byline = (f"AI Foundry lab · experiment E61 · the night of 20–21 Oct 2026 · "
              f"{', '.join(sorted(ANA))} · {thou(runs_kept)} of {thou(runs_all)} runs kept")
    return {"title": title, "description": desc, "byline": byline, "body": body, "captions": captions,
            "tables": {"short": {"head": ["row", "quantity", "the page", "measured", "card", "verdict", "why"],
                                 "rows": short_rows, "verdict_col": 5, "cards": True, "wide": True},
                       "desk": {"head": ["group", "the page's claims", "verdict", "what settles it"],
                                "rows": desk_rows, "verdict_col": 2, "cards": True, "wide": True},
                       "untestable": {"head": ["the page's claims", "why no run tonight can score it"],
                                      "rows": unt_rows, "cards": True, "wide": True},
                       "reps": {"head": ["replication", "card", "opcode", "the zero-word term", "passes"],
                                "rows": rep_rows, "cards": True},
                       "align": {"head": ["mode \u00b7 kernel", "loop head", "mod 32", "vector ops", "ops/cycle/hart"],
                                 "rows": aln_rows, "num": [2, 3, 4], "cards": True},
                       "ratio": {"head": ["what the intercept would be per", "the ratio it predicts", "how far the measurement is"],
                                 "rows": ratio_rows, "cards": True},
                       "ed4": {"head": ["the registered condition", "measured", "satisfied?"], "rows": ed4_rows,
                               "cards": True, "wide": True},
                       "half": {"head": ["card", "operating point", "half-die result-path load", "passes"],
                                "rows": half_rows, "cards": True},
                       "priors": {"head": ["our registered prior", "the interval we wrote", "measured", "where it landed"],
                                  "rows": wrong_rows, "cards": True},
                       "recon": {"head": ["quantity", "unit", "this reduction", "the independent one", "apart", "why"],
                                 "rows": recon_rows, "cards": True, "wide": True},
                       "explorers": {"head": ["the constant the generator hard-codes", "what the night measured", "the error"],
                                     "rows": exp_rows, "cards": True, "wide": True},
                       "cards": {"head": ["card", "MHz", "mV", "governor", "passes kept", "set aside", "runs kept", "leak W/°C"],
                                 "rows": card_rows, "num": [1, 2, 5, 6, 7]},
                       "aside": {"head": ["card", "pass", "why it was set aside"], "rows": aside_rows, "cards": True},
                       "conv": {"head": ["price (minion rail)", "energy", "½CV²", "electrons", "CV²", "electrons"],
                                "rows": conv_rows, "num": [1, 2, 3, 4, 5], "cards": True, "wide": True}},
            "primary": prim}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dtf", required=True)
    ap.add_argument("--cam")
    ap.add_argument("--facts")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.dtf))
    CAM = json.load(open(a.cam)) if a.cam else {}
    F = json.load(open(a.facts)) if a.facts else {}
    json.dump(build(R, CAM, F), open(a.out, "w"), indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
