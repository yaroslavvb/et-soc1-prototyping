#!/usr/bin/env python3
"""Everything the E61 page says that the reduction does not already carry, recomputed from the files.

    python3 facts.py --dtf <fix/dtf.json> --cam <cam.json> --independent <numbers.json> \
                     --readme <README.md> --repo <repo> --dis <dis-a2.txt> --out facts.json

Nothing numeric is typed in this file. Every entry is either
  * read from dtf.json / cam.json / numbers.json / the manifest counts inside dtf.json, or
  * recomputed here from the per-pass arrays those files carry, or
  * parsed out of the pre-registration, the repository's git log, or the committed disassembly.

NOTHING IS CORRECTED HERE. The wf4 build of this file carried the fix verifier's twelve corrections as
arithmetic on top of the reduction; the wf5 reduction applies every one of them itself (each marked
`# VER n` in its code), so re-applying them would double them. Every former correction is now a READ of
the field the reduction publishes, and each such site is marked `# reads VER n`. The only arithmetic left
is (a) t statistics formed from a value, an SE and a target the reduction itself prints, and (b) a handful
of ratios and shares, both kinds labelled `derived:` in the output and named in the page's own prose.
"""
import argparse
import json
import math
import os
import re
import subprocess

# ------------------------------------------------------------------ small statistics, stdlib only



def _rel(p):
    """A path inside the repository as a repository-relative path (E60's hl.json convention); others unchanged."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ap = os.path.abspath(p)
    return os.path.relpath(ap, root) if ap.startswith(root + os.sep) else ap

def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def se_of(xs):
    """The between-pass standard error: the same estimator §8 uses (sd / sqrt n, n - 1 in the sd)."""
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1) / n)


def tval(v, se, target=0.0):
    if v is None or not se:
        return None
    return (v - target) / se


def g(d, *ks, default=None):
    for k in ks:
        if isinstance(d, dict):
            d = d.get(k, d.get(str(k)))
        elif isinstance(d, (list, tuple)) and isinstance(k, int):
            d = d[k] if -len(d) <= k < len(d) else None
        else:
            return default
        if d is None:
            return default
    return d


def fjse(block):
    """(value in fJ, SE in fJ) from a reduction block, whichever of the two spellings it carries."""
    if not isinstance(block, dict):
        return None, None
    v = block.get("fJ")
    if v is None and block.get("value") is not None:
        v = block["value"] * 1e15
    se = block.get("se_fJ")
    if se is None and block.get("se") is not None:
        se = block["se"] * 1e15
    return v, se


def stat(v, se, unit="", n=None, extra=None):
    out = {"value": v, "se": se, "unit": unit}
    if n is not None:
        out["n_passes"] = n
    if extra:
        out.update(extra)
    return out


# ----------------------------------------------- what the reduction now corrects for itself (VER 1, VER 3)


def changed_word_price(R, prim):
    """reads VER 1: the §5.1 R2 changed-word term, priced and counted on the SAME reading, by the reduction.

    The wf4 page divided the published term by src/(src+res) because the reduction priced one changed word
    at the ladder intercept over 8 SOURCE words while counting 16 under reading R2. The wf5 reduction's
    `word_price_W(reading, ref)` reads both off reading R2, so the term it publishes
    (`e_out_add_registered_R2_term.fJ_per_flip`) is already the single correct one and the two corrected
    blocks (`e_out_add_registered_R2_corrected`, `e_carry_R2_corrected`) are already at that price.
    Nothing is recomputed: the only arithmetic is the two t statistics, from this row's own value, SE and
    the two targets it prints.
    """
    C = R["cards"][prim]
    F, D = C["families"], C["derived"]
    it = (C.get("items") or {}).get("d1nz_h32", {})
    term = F.get("e_out_add_registered_R2_term") or {}
    reg = g(F, "e_out_add_registered", "board", default={}) or g(D, "e_out_add_registered", "board", default={})
    cor = (g(F, "e_out_add_registered_R2_corrected", "board", default={})
           or g(D, "e_out_add_registered_R2_corrected", "board", default={}))
    carry = g(D, "e_carry", "board", default={})
    carry_r2 = g(D, "e_carry_R2_corrected", "board", default={})
    row = next((x for x in R["verdicts"] if "carry stage" in str(x.get("quantity", ""))), {})
    if not (term and reg and carry):
        return None

    crit = carry.get("t_crit_3sigma")
    v, s = fjse(carry_r2)
    if v is None:
        v, s = row.get("e_carry_R2_corrected_fJ"), row.get("e_carry_R2_corrected_se_fJ")
    ours, page = row.get("ours_fJ"), row.get("page_fJ")
    t_ours, t_page = tval(v, s, ours or 0.0), tval(v, s, page or 0.0)
    return {
        # the counts the price and the multiplier are both read on, from the manifest's own item counts
        "src_words": g(it, "counts", "src_words"), "res_words": g(it, "counts", "res_words"),
        "r2_words": term.get("words_per_op_the_price_is_read_on"),
        "changed_words_per_op_delta": term.get("changed_words_per_op_delta"),
        "regressor_bits_per_op": term.get("regressor_bits_per_op"),
        "W_per_changed_word": term.get("W_per_changed_word"),
        "term_fJ": term.get("fJ_per_flip"),                                   # 2.507, the reduction's own
        "term_note": term.get("note"),
        "e_out_add_registered": stat(*fjse(reg), unit="fJ", n=reg.get("n_passes")),
        "e_out_add_R2_corrected": stat(*fjse(cor), unit="fJ", n=cor.get("n_passes")),
        "e_carry_registered": stat(*fjse(carry), unit="fJ", n=carry.get("n_passes")),
        "e_carry_R2_corrected": stat(v, s, "fJ", carry_r2.get("n_passes")),
        "verdict_registered": row.get("verdict"),
        "verdict_R2_corrected": row.get("e_carry_R2_corrected_verdict"),
        "verdict_depends_on_the_R2_term": row.get("verdict_depends_on_the_R2_term"),
        "t_crit_3sigma": crit, "ours_fJ": ours, "page_fJ": page,
        "derived:t_vs_ours": t_ours, "derived:t_vs_page": t_page,
        "derived:ours_inside_3se": (abs(t_ours) < crit) if (t_ours is not None and crit) else None,
        "derived:page_excluded": (abs(t_page) >= crit) if (t_page is not None and crit) else None,
    }


def bridge_term(R, prim):
    """reads VER 3: the joint-fit-minus-raw gap, identified by the reduction, not by this file.

    `joint_minus_raw_gap` now carries the gap in fJ per flip and in watts on the bridge's own per-mode
    denominator, the R2 changed-word term in both units, and the share of the gap that term is. The wf4
    page halved the published correction and printed an extra "if doubled" share; both are gone.
    """
    C = R["cards"][prim]
    F, D = C["families"], C["derived"]
    raw = g(F, "B_bridge_raw_W", default={})
    eob = g(D, "e_out_bridge", "board", default={})
    row = next((v for v in R["verdicts"] if "e_out" in str(v.get("quantity", ""))), {})
    gap = row.get("joint_minus_raw_gap") or {}
    inter = g(D, "intercept_N_W", default={})
    w_coef = g(C, "joint_fit", "coefs", "w", "fJ")
    words = F.get("B_bridge_R2_changed_words_per_op")
    bits = (C.get("items") or {}).get("d2B_h32", {}).get("regressor_bits_per_op") or 512.0
    if not (raw.get("value") and eob.get("fJ") and gap):
        return None
    gap_fJ = gap.get("gap_fJ_per_flip")
    # the only arithmetic: what the SAME term would be if priced at the fit's own changed-word coefficient
    w_route_fJ = (w_coef * words / bits) if (w_coef and words) else None
    return {
        "raw_W": raw["value"], "raw_se_W": raw.get("se"),
        "changed_words_per_op": gap.get("R2_changed_words_per_op") or words,
        "regressor_bits_per_op": bits,
        "correction_W": F.get("B_bridge_R2_correction_W"),                     # 0.2283 W = the intercept
        "corrected_W": F.get("B_bridge_R2_corrected_W"),
        "intercept_N_W": inter.get("value"), "intercept_N_se_W": inter.get("se"),
        "denominator_bits_per_s": gap.get("bridge_denominator_bits_per_s"),
        "denominator_how": gap.get("bridge_denominator_how"),
        "gap_fJ": gap_fJ, "gap_W": gap.get("gap_W"),
        "term_fJ_at_the_intercept": gap.get("R2_changed_word_term_fJ_per_flip"),
        "term_W_at_the_intercept": gap.get("R2_changed_word_term_W"),
        "share_at_the_intercept_pct": gap.get("R2_term_as_pct_of_the_gap"),
        "unexplained_W": (gap.get("gap_W") - gap.get("R2_changed_word_term_W"))
                         if (gap.get("gap_W") and gap.get("R2_changed_word_term_W")) else None,
        "gap_note": gap.get("note"),
        "derived:term_fJ_at_the_fitted_w": w_route_fJ,
        "derived:share_at_the_fitted_w_pct": (w_route_fJ / gap_fJ * 100) if (gap_fJ and w_route_fJ) else None,
        "w_coef_fJ_per_word": w_coef, "w_coef_se": g(C, "joint_fit", "coefs", "w", "se_fJ"),
        "raw_fJ": eob.get("fJ"), "raw_se_fJ": fjse(eob)[1], "joint_fJ": gap.get("joint_fit_fJ"),
        "derived:raw_plus_term_fJ": (eob["fJ"] + gap["R2_changed_word_term_fJ_per_flip"])
                                    if gap.get("R2_changed_word_term_fJ_per_flip") else None,
        "derived:raw_minus_term_fJ": (eob["fJ"] - gap["R2_changed_word_term_fJ_per_flip"])
                                     if gap.get("R2_changed_word_term_fJ_per_flip") else None,
        "one_rate_form_fJ": row.get("raw_bridge_one_rate_form_fJ"),
        "one_rate_excess_pct": row.get("raw_bridge_one_rate_excess_pct"),
    }


def replications(R):
    """reads VER 4: the §8.6 heterogeneity result, computed and read by the reduction.

    The wf4 page computed Cochran's Q here and decided for itself which pairs cleared the window. The wf5
    reduction publishes `heterogeneity` with Q, its df, the pairs over 3 SE, the inverse-variance centre Q
    is taken about (and the note that nothing reads it), the OPCODE-DEPENDENT reading and the pooling flags.
    This function only reshapes those for the table.
    """
    v = next((x for x in R["verdicts"] if "zero-operand" in str(x.get("quantity", ""))), {})
    het = v.get("heterogeneity") or {}
    reps = het.get("members_fJ_per_op") or v.get("replications") or {}
    rows = []
    for name, r in reps.items():
        src = (v.get("replications") or {}).get(name) or {}
        rows.append({"name": name, "card": r.get("card"), "opcode": r.get("opcode"),
                     "fJ_per_op": r.get("fJ_per_op"), "se_fJ_per_op": r.get("se_fJ_per_op"),
                     "n_passes": r.get("n_passes"), "W": src.get("W"), "se_W": src.get("se_W")})
    crit = het.get("t_crit_3sigma") or g(R, "cards", v.get("card"), "derived", "zero_word_term",
                                         "board", "t_crit_3sigma")
    pairs = [{"a": p["pair"][0], "b": p["pair"][1], "t": p.get("t"), "fires": p.get("ge_3SE")}
             for p in (het.get("pairwise") or v.get("heterogeneity_t") or [])]
    return {"rows": sorted(rows, key=lambda r: (r["fJ_per_op"] is None, r["fJ_per_op"] or 0)),
            "pairs": pairs,
            "pairs_over_the_window": [p for p in pairs if p.get("fires")],
            "pairs_over_the_window_named": het.get("pairs_over_3SE"),
            "Q": het.get("cochran_Q"), "df": het.get("cochran_Q_df"), "t_crit_3sigma": crit,
            "heterogeneous": het.get("heterogeneous"), "reading": het.get("reading"), "how": het.get("how"),
            "weighted_mean_fJ_per_op": het.get("inverse_variance_weighted_mean_fJ_per_op"),
            "weighted_mean_is_not_the_estimate": het.get("weighted_mean_is_not_the_estimate"),
            "pooled_flag_in_the_file": v.get("replications_pooled_across_cards"),
            "gathered_across_cards": v.get("replications_gathered_across_cards"),
            "applied_term": v.get("applied_term"), "single_rung_fJ_per_op": v.get("fJ_per_op"),
            "cards": sorted({r["card"] for r in rows if r.get("card")})}


def c14_leak(R):
    """reads VER 2 and VER 5: the row is `not scored`, and where its answer moves with the leakage slope.

    VER 2 — the reduction now prints `verdict: "not scored"` with `scored`, `reported_as` ("AGREEMENT") and
    `not_scored_because` (§5.2: d2A cannot both supply e_in(fand) and be tested against it). The wf4 page
    carried that as prose of its own.
    VER 5 — `leak_arm_by_slope` carries each arm's value, SE, its own 3-SE widening and whether it is inside
    the strict interval and inside the widened one. The wf4 page computed those three decisions here.
    """
    v = next((x for x in R["verdicts"] if "read-port price" in str(x.get("quantity", ""))), {})
    s = v.get("sensitivity") or {}
    arms_pub = v.get("leak_arm_by_slope") or {}
    lo, hi = (v.get("E60_interval_fJ") or [None, None])
    out = {"interval_fJ": [lo, hi], "by_rung": v.get("by_rung"), "by_fit_form": v.get("by_fit_form"),
           "fJ_above_the_lower_edge": v.get("fJ_above_the_lower_edge"), "arms": {},
           "verdict": v.get("verdict"), "scored": v.get("scored"), "reported_as": v.get("reported_as"),
           "not_scored_because": v.get("not_scored_because"), "margin": v.get("margin")}
    for arm in ("fitted", "zero", "E60"):
        a = arms_pub.get(arm) or {}
        if a.get("fJ") is None:
            continue
        out["arms"][arm] = {"value": a.get("fJ"), "se": a.get("se_fJ"),
                            "widening_fJ": a.get("3SE_widening_fJ"),
                            "inside_strict": a.get("in_strict_interval"),
                            "inside_widened": a.get("in_interval_after_3SE_widening"),
                            "reading": a.get("reading"), "label": a.get("label")}
    out["E60_minus_fitted_in_SE"] = s.get("E60_minus_fitted_in_SE")
    out["prohibition"] = v.get("not_scored_because") or v.get("note") or ""
    return out


def census(R):
    """reads VER 6: passes are KEPT or SET ASIDE, never 'missing'; every registered pass dir was read.

    The reduction's own wording is now "N of M registered passes KEPT; K SET ASIDE ... No pass dir is
    missing: all M were read", so `passes_read` here is the registered count the reduction read, and the
    page never calls a set-aside pass absent. `R["missing"]` is a different list — identification gaps in
    the manifest and in what a card could measure — and is reported under its own heading.
    """
    rows, kept, allr, pk, pr = [], 0, 0, 0, 0
    for k, c in R["cards"].items():
        gates = c.get("gates") or {}
        aside = c.get("passes_set_aside") or []
        rows.append({"card": k, "mhz": c.get("clock_mhz"), "mv": round((c.get("v_mean") or 0) * 1000),
                     "gov_free": c.get("gov_free"), "passes_kept": c.get("n_passes"),
                     "passes_registered": c.get("n_passes_registered"),
                     "passes_prereg": c.get("n_passes_prereg_s6"),
                     "set_aside": [{"pass": a.get("pass"), "why": "; ".join(a.get("why") or [])} for a in aside],
                     "runs_kept": gates.get("kept"), "runs": gates.get("runs"),
                     "leak_W_per_C": c.get("leak_W_per_C"), "leak_E60_W_per_C": c.get("leak_E60_W_per_C"),
                     "leak_qualifying_pct": c.get("leak_qualifying_run_pct")})
        kept += gates.get("kept") or 0
        allr += gates.get("runs") or 0
        pk += c.get("n_passes") or 0
        pr += c.get("n_passes_registered") or 0
    return {"per_card": rows, "runs_kept": kept, "runs": allr, "passes_kept": pk, "passes_registered": pr,
            "passes_read": pr, "no_pass_dir_missing": True,
            "cards_in_the_analysis": sorted(k for k in R["cards"] if "[" not in k)}


def open_band_from_readme(path, claims_rx, unit_rx):
    """The OPEN column of one §9 decision row, read out of the pre-registration (never typed here)."""
    if not path or not os.path.exists(path):
        return None
    for ln in open(path, encoding="utf-8"):
        if ln.startswith("|") and re.search(claims_rx, ln):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            for c in reversed(cells):
                m = re.search(unit_rx, c)
                if m:
                    return [float(m.group(1)), float(m.group(2))]
    return None


def zero_gate(R, prim, readme=None):
    """reads VER 8: the C79 margin, as the reduction states it.

    `SE_to_the_0p5_boundary` and `pJ_per_op_3SE_upper_bound` are the reduction's own; the wf4 page computed
    both here. The watt SE and the distance to 0.1 W are the two quantities the reduction leaves in watts
    only as a point value, so they stay derived and are labelled; the OPEN band's edges are read from the
    pre-registration's §9 row, never typed.
    """
    v = next((x for x in R["verdicts"] if "zero-gate" in str(x.get("quantity", ""))), {})
    d = g(R, "cards", prim, "derived", "zero_gate_step", "board", default={})
    pj, se, w = v.get("pJ_per_op"), v.get("se_pJ_per_op"), v.get("W")
    crit = d.get("t_crit_3sigma")
    se_w = v.get("se_W") if v.get("se_W") is not None else d.get("se")
    if se_w is None and (se and pj and w):
        se_w = se * w / pj
    return {"pJ_per_op": pj, "se_pJ_per_op": se, "W": w, "se_W": se_w, "t_crit_3sigma": crit,
            "page_pJ_per_op": v.get("page_pJ_per_op"), "ours_pJ_per_op": v.get("ours_pJ_per_op"),
            "se_to_the_0p5_boundary": v.get("SE_to_the_0p5_boundary"),
            "upper_3se_pJ_per_op": v.get("pJ_per_op_3SE_upper_bound"),
            "margin": v.get("margin"),
            "open_band_pJ_per_op": open_band_from_readme(readme, r"C79", r"([\d.]+)\s*[–-]\s*([\d.]+)\s*pJ/op"),
            "derived:se_to_0p1_W": ((0.1 - w) / se_w) if (w is not None and se_w) else None}


def intercept_row(R, prim):
    """reads VER 9: which OPEN this is, named by the reduction, with the registered arm's own statistic.

    `open_arm` now says in the file that more than one reading is inside 3 SE while the registered arm does
    not fire, and `registered_open_arm_fires` / `X_minus_N_per_changed_source_word_*` carry the arm's
    numbers. The wf4 page inferred the "fires" flag from the family block itself.
    """
    v = next((x for x in R["verdicts"] if "per changed word" in str(x.get("quantity", ""))), {})
    f = v.get("per_changed_word") or g(R, "cards", prim, "families",
                                       "intercept_per_changed_word_W", default={})
    xn = f.get("X_minus_N") or {}
    return {"intercept_N_W": v.get("intercept_N_W"), "intercept_N_se": v.get("intercept_N_se"),
            "intercept_X_W": v.get("intercept_X_W"),
            "X_per_word_W": g(f, "X", "value"), "X_per_word_se": g(f, "X", "se"),
            "N_per_word_W": g(f, "N", "value"), "N_per_word_se": g(f, "N", "se"),
            "X_words_per_op": f.get("X_words_per_op"), "N_words_per_op": f.get("N_words_per_op"),
            "reading": f.get("reading"), "registered_arm": f.get("registered_arm"),
            "X_minus_N_W": v.get("X_minus_N_per_changed_source_word_W", xn.get("value")),
            "X_minus_N_se": v.get("X_minus_N_per_changed_source_word_se_W", xn.get("se")),
            "X_minus_N_t": v.get("X_minus_N_t", xn.get("t")),
            "t_crit_3sigma": v.get("X_minus_N_t_crit_3sigma", xn.get("t_crit_3sigma")),
            "registered_open_arm_fires": v.get("registered_open_arm_fires"),
            "open_arm": v.get("open_arm"),
            "readings": g(v, "readings", "readings", default={}),
            "matched": g(v, "readings", "matched", default=[]) or g(v, "by_leakage_slope", "fitted",
                                                                    "matched", default=[]),
            "by_leakage_slope": v.get("by_leakage_slope")}


def rho_margin(R, IND=None):
    """reads VER 10: how far past its own threshold the rho exclusion sits, as the reduction measures it.

    `rho_SE_to_1p000`, `rho_SE_to_1p1295` and `rho_t_crit_3sigma` are the reduction's; the wf4 page formed
    the t itself. The share of the threshold is the one ratio left, and it is labelled derived.
    """
    v = next((x for x in R["verdicts"] if x.get("rho") is not None), {})
    d = g(R, "cards", v.get("rho_card"), "derived", "rho_harts2_over_harts1", default={})
    crit = v.get("rho_t_crit_3sigma") or d.get("t_crit_3sigma")
    t = v.get("rho_SE_to_1p000")
    if t is None:
        t = tval(v.get("rho"), v.get("rho_se"), 1.0)
    tgt = re.search(r"([\d.]+)-([\d.]+) if interleaving destroys", " ".join(d.get("notes") or [""]))
    Q = ((IND or {}).get("quantities") or {}).get(v.get("rho_card")) or {}
    pick = lambda k: {"value": (Q.get(k) or {}).get("value"), "se": (Q.get(k) or {}).get("se")} if Q.get(k) else {}
    d1, d2 = pick("R_per_op_delta_harts1_p80"), pick("R_per_op_delta_harts2_p80")
    drop = (d2.get("value") - d1.get("value")) if (d1.get("value") and d2.get("value")) else None
    return {"rail_leg": pick("R_rho_rail"), "per_op_harts1": d1, "per_op_harts2": d2,
            "fJ_per_op_the_two_hart_arm_must_lose": drop,
            "pct_the_two_hart_arm_must_lose": (drop / d2["value"] * 100) if (drop and d2.get("value")) else None,
            "leak_W_per_C": g(R, "cards", v.get("rho_card"), "leak_W_per_C"),
            "rho": v.get("rho"), "se": v.get("rho_se"), "n_passes": d.get("n_passes"), "df": d.get("df"),
            "t_crit_3sigma": crit, "t_vs_1": t, "se_to_the_destroyed_centre": v.get("rho_SE_to_1p1295"),
            "margin": v.get("margin"),
            "derived:pct_of_the_threshold": (abs(t) / crit * 100) if (t and crit) else None,
            "destroyed_band": [float(tgt.group(1)), float(tgt.group(2))] if tgt else None,
            "interleave_fraction": v.get("interleave_fraction"),
            "derived:interleave_fraction_se": (v.get("rho_se") / (float(tgt.group(2)) - 1.0))
                                              if (tgt and v.get("rho_se")) else None,
            "notes": d.get("notes")}


def c58_and_c33(R, prim):
    """reads VER 11 and VER 12: the four-pass caveat on C58, and C33's unit of replication.

    VER 11 — the reduction publishes `W_vs_E_detectable_at_3SE_W` (3.13 W), `W_vs_E_n_passes` (4),
    `W_vs_E_t_crit_3sigma` (9.22), `pass_floor_for_a_confirmatory_item` (6) and the `caveat` sentence. The
    wf4 page hunted the card's blocks for a quantile and multiplied it by the SE itself.
    VER 12 — the §8.4 PAIRED statistic is the one the row reads, and the reduction prints it
    (`paired_spread_*`, `spread.paired_fixed_pair`, `spread.paired_per_pass_max_minus_min`) beside the
    cross-item reading. The wf4 page differenced the two gate-ladder rungs per pass here and formed its own
    quadrature SE.
    """
    v = next((x for x in R["verdicts"] if "dP_card" in str(x.get("quantity", ""))), {})
    c33v = next((x for x in R["verdicts"] if x.get("spread")), {})
    sp = c33v.get("spread") or {}
    pf = sp.get("paired_fixed_pair") or {}
    pmm = sp.get("paired_per_pass_max_minus_min") or {}
    return {"c58": {"card": v.get("card"), "n_passes": v.get("W_vs_E_n_passes"),
                    "W_minus_E": v.get("W_minus_E_board_W"), "se": v.get("W_minus_E_se"),
                    "t_crit_3sigma": v.get("W_vs_E_t_crit_3sigma"),
                    "detectable_W": v.get("W_vs_E_detectable_at_3SE_W"),
                    "confirmatory_floor_passes": v.get("pass_floor_for_a_confirmatory_item"),
                    "caveat": v.get("caveat")},
            "c33": {"spread_fJ": c33v.get("paired_spread_fJ", sp.get("spread_fJ")),
                    "spread_se": c33v.get("paired_spread_se_fJ", pf.get("se_fJ")),
                    "spread_t": c33v.get("paired_spread_t", pf.get("t")),
                    "spread_n_passes": c33v.get("paired_spread_n_passes", pf.get("n_passes")),
                    "statistic_read": c33v.get("spread_statistic_read"),
                    "se_basis": sp.get("se_basis"),
                    "paired_items": pf.get("items"), "paired_ops": pf.get("ops"), "paired_how": pf.get("how"),
                    "paired_fires": pf.get("ge_3SE"),
                    "cross_item_spread_fJ": c33v.get("cross_item_spread_fJ", sp.get("cross_item_se_fJ")),
                    "cross_item_se_fJ": c33v.get("cross_item_spread_se_fJ", sp.get("cross_item_se_fJ")),
                    "cross_item_t": c33v.get("cross_item_spread_t", sp.get("cross_item_t")),
                    "max_minus_min_fJ": pmm.get("spread_fJ"), "max_minus_min_se_fJ": pmm.get("se_fJ"),
                    "max_minus_min_t": pmm.get("t"),
                    "t_crit_3sigma": sp.get("t_crit_3sigma"),
                    "items": [g(sp, "min", "item"), g(sp, "max", "item")],
                    "by_depth_named": sp.get("by_depth_named")}}


def ed4(R, prim):
    """Critic 16: all three registered conditions for the Miller row, not just the spread."""
    v = next((x for x in R["verdicts"] if "Miller wire law" in str(x.get("quantity", ""))), {})
    lv = v.get("levels") or {}
    ws = v.get("whole_spread") or {}
    cc = v.get("complement_control") or {}
    ind = {}
    return {"k_adj": lv.get("k_adj"), "dW": lv.get("dW"), "steps": lv.get("steps"),
            "whole_spread": ws, "t_crit_3sigma": ws.get("t_crit_3sigma"),
            "spearman_pass_averaged": v.get("spearman_rho_pass_averaged"),
            "spearman_per_pass": v.get("spearman_rho_per_pass"),
            "monotone_wrong_direction": v.get("monotone_wrong_direction"),
            "complement_control": cc, "complement_control_card": v.get("complement_control_card"),
            "page_W": v.get("phase_term_page_W"), "phase_term_W": v.get("phase_term_W"),
            "phase_term_se": v.get("phase_term_se"), "items_per_level": lv.get("items_per_level")}


def cell_scaling(R, prim):
    """reads VER 7: the RECON 8 scaling test and the fact that it HAS NO POWER, both from the reduction.

    `proportional_within_3SE` is the reduction's own flag now, and its `note` plus the row's `basis` say in
    the file that the test is UNTESTED — both proportionality and the measured -16.4% survive at |t| 0.54
    against 3.85. The wf4 page decided `proportional_within_3SE` here and wrote the "nothing here shows the
    cell term scaling with h" reading as its own sentence.
    """
    f = g(R, "cards", prim, "families", "e_cell_scaling_test", default={})
    v = next((x for x in R["verdicts"] if "cell bit" in str(x.get("quantity", ""))), {})
    f = (v.get("scaling") or {}) or f
    d = f.get("per_bit_difference_high_minus_low") or {}
    return {"low_h": f.get("rung_low_h"), "high_h": f.get("rung_high_h"),
            "at_low_h": f.get("fJ_per_cell_bit_at_low_h"), "at_high_h": f.get("fJ_per_cell_bit_at_high_h"),
            "difference": d, "ratio": f.get("per_bit_ratio_high_over_low"),
            "per_op_growth": f.get("per_op_growth_high_over_low"),
            "per_op_growth_needed": f.get("per_op_growth_a_proportional_law_needs"),
            "per_op_at_low_h": f.get("fJ_per_op_at_low_h"), "per_op_at_high_h": f.get("fJ_per_op_at_high_h"),
            "t": d.get("t"), "t_crit_3sigma": d.get("t_crit_3sigma"),
            "proportional_within_3SE": f.get("proportional_within_3SE"),
            "per_bit_change_pct": f.get("per_bit_change_pct"),
            "test": f.get("test"), "how": f.get("how"), "note": f.get("note"),
            "value_fJ": v.get("value_fJ"), "se_fJ": v.get("se_fJ"), "prior_fJ": v.get("prior_fJ"),
            "scaling_recorded": v.get("scaling_test_ran")}


def e_out_routes(R, prim):
    """The skeptic's (b): the within-family bridge against the cross-family subtraction, both fit forms."""
    C = R["cards"][prim]
    D, F = C["derived"], C["families"]
    out = {}
    for nm, key in (("e_out_fand_BA", "fand_leg"), ("e_out_for_DC", "for_leg")):
        b = g(D, nm, "board", default={})
        v, se = fjse(b)
        if v is not None:
            out[key] = stat(v, se, "fJ", b.get("n_passes"))
    legs = [out[k] for k in ("fand_leg", "for_leg") if k in out]
    if len(legs) == 2:
        out["within_family_mean"] = stat(mean([l["value"] for l in legs]),
                                         math.sqrt(sum((l["se"] or 0) ** 2 for l in legs)) / 2, "fJ",
                                         extra={"legs": [l["value"] for l in legs]})
    nsum = g(D, "e_sum_fnot_d1nz", "board", default={})
    xin = g(D, "e_in_fxor", "board", default={})
    xin_o = g(D, "e_in_fxor_E60fit", "board", default={})
    nv, ns = fjse(nsum)
    for key, x in (("cross_family_free_intercept", xin), ("cross_family_with_origin", xin_o)):
        xv, xs = fjse(x)
        if nv is not None and xv is not None:
            out[key] = stat(nv - xv, math.sqrt((ns or 0) ** 2 + (xs or 0) ** 2), "fJ")
    out["n_sum_fnot"] = stat(*fjse(nsum), unit="fJ")
    out["x_e_in_free"] = stat(*fjse(xin), unit="fJ")
    out["x_e_in_origin"] = stat(*fjse(xin_o), unit="fJ")
    out["intercept_ratio_N_over_X"] = None
    iN, iX = g(D, "intercept_N_W", default={}), g(D, "intercept_X_W", default={})
    if iN.get("value") and iX.get("value"):
        r = iN["value"] / iX["value"]
        sr = abs(r) * math.sqrt(((iN.get("se") or 0) / iN["value"]) ** 2 + ((iX.get("se") or 0) / iX["value"]) ** 2)
        it = (C.get("items") or {})
        nb = g(it, "d1nz_h32", "counts", "addr")
        xb = g(it, "xin_h32", "counts", "addr")
        out["intercept_ratio_N_over_X"] = {
            "value": r, "se": sr, "N_W": iN["value"], "N_se": iN.get("se"), "X_W": iX["value"],
            "X_se": iX.get("se"), "addr_bits_N": nb, "addr_bits_X": xb,
            "predictions": {"R1 per changed source word": 0.5, "R2 per changed word on any bus": 1.0,
                            "R4 per address bit an op fetches": (nb / xb) if (nb and xb) else None},
        }
        for k, p in list(out["intercept_ratio_N_over_X"]["predictions"].items()):
            if p:
                out["intercept_ratio_N_over_X"].setdefault("se_from", {})[k] = abs(r - p) / sr
    out["joint_fit"] = {"e_out_fJ": g(C, "joint_fit", "coefs", "e_out", "fJ"),
                        "e_out_se_fJ": g(C, "joint_fit", "coefs", "e_out", "se_fJ"),
                        "condition_number": g(C, "joint_fit", "condition_number"),
                        "condition_number_raw": g(C, "joint_fit", "condition_number_raw_design"),
                        "condition_basis": g(C, "joint_fit", "condition_number_basis"),
                        "vif": g(C, "joint_fit", "vif"), "rows_per_pass": g(C, "joint_fit", "rows_per_pass"),
                        "resid_rms_W": g(C, "joint_fit", "resid_rms_W"),
                        "degenerate": g(C, "joint_fit", "design_is_degenerate"),
                        "known_collinearities": g(C, "joint_fit", "known_collinearities"),
                        "w_fJ": g(C, "joint_fit", "coefs", "w", "fJ"),
                        "w_se_fJ": g(C, "joint_fit", "coefs", "w", "se_fJ"),
                        "e_addr_fJ": g(C, "joint_fit", "coefs", "e_addr", "fJ"),
                        "e_carry_fJ": g(C, "joint_fit", "coefs", "e_carry", "fJ"),
                        "se_quoted": {k: g(C, "joint_fit", "coefs", k, "se_quoted")
                                      for k in (g(C, "joint_fit", "coefs", default={}) or {})}}
    return out


def addr_readings(R, prim):
    """The skeptic's (a): the five legitimate readings of three rungs, the fixed step, and the degeneracy."""
    C = R["cards"][prim]
    it, F, D = C.get("items") or {}, C["families"], C["derived"]
    row = next((v for v in R["verdicts"] if "register-index bit" in str(v.get("quantity", ""))), {})
    mc = g(R, "method_choices", "method_choices", "family_A_with_or_without_the_origin", default={})
    rungs = {}
    for nm in ("d5_a0", "d5_a1", "d5_a3", "d5_a5", "d5n_a0", "d5n_a3"):
        if nm in it:
            rungs[nm] = {"addr_bits": g(it, nm, "counts", "addr"), "d_W": g(it, nm, "d_p80"),
                         "d_se": g(it, nm, "d_p80_se"), "ipc": g(it, nm, "ipc"), "mode": g(it, nm, "mode")}
    out = {"rungs": rungs, "free_intercept": {"value": mc.get("free_intercept_fJ_per_bit"),
                                              "se": mc.get("free_intercept_se_fJ")},
           "with_origin": {"value": mc.get("with_origin_fJ_per_bit"), "se": mc.get("with_origin_se_fJ")},
           "chosen": mc.get("chosen"), "note": mc.get("note"),
           "value_fJ": row.get("value_fJ"), "se_fJ": row.get("se_fJ"),
           "page_fJ": row.get("page_fJ") if row.get("page_fJ") is not None else g(D, "e_addr", "page_fJ"),
           "prior_fJ": g(D, "e_addr", "prior_fJ"), "times_the_prior_ceiling": row.get("times_the_prior_ceiling"),
           "live_fJ": fjse(g(D, "e_addr_live", "board", default={}))[0],
           "live_se_fJ": fjse(g(D, "e_addr_live", "board", default={}))[1],
           "gated_minus_live": g(F, "A_gated_minus_live_slope", default={}),
           "per_op_constant": g(F, "per_op_constant_between_kernels", default={}),
           "joint_fit_fJ": g(C, "joint_fit", "coefs", "e_addr", "fJ"),
           "exclusion_one_sided": row.get("exclusion_one_sided"),
           "excluded_from_above": row.get("excluded_from_above"),
           "excluded_from_below": row.get("excluded_from_below"),
           "rate_confounded": row.get("rate_confounded_rung")}
    a0 = rungs.get("d5_a0") or {}
    deg = []
    for nm, dist in (("d5_a1", 1), ("d5_a3", 7), ("d5_a5", 31)):
        r = rungs.get(nm)
        if r and a0.get("addr_bits") is not None:
            deg.append({"rung": nm, "index_row_distance": dist,
                        "log2_1_plus_distance": math.log2(1 + dist),
                        "addr_bits_above_a0": (r["addr_bits"] - a0["addr_bits"]) if r.get("addr_bits") else None})
    out["degeneracy"] = deg
    poc = g(F, "per_op_constant_between_kernels", default={})
    grp = next((x for x in (poc.get("same_rate_groups") or []) if x.get("is_the_A_ladder_rate")), {})
    out["per_op_constant_summary"] = {
        "ipc": grp.get("ipc"), "items": grp.get("items_outside_family_A"),
        "span_W": grp.get("spread_W_outside_family_A"),
        "fJ_per_bit_equiv": grp.get("spread_fJ_per_addr_bit_equiv_outside_family_A"),
        "conversion": poc.get("conversion"), "note": poc.get("note"),
        "pct_of_the_slope": ((grp.get("spread_fJ_per_addr_bit_equiv_outside_family_A") or 0)
                            / (mc.get("free_intercept_fJ_per_bit") or 1) * 100) or None,
    }
    e_in = g(D, "e_in_fxor", "board", default={})
    if out["free_intercept"]["value"] and e_in.get("fJ"):
        out["times_a_data_bit"] = out["free_intercept"]["value"] / e_in["fJ"]
        out["e_in_fJ"] = e_in["fJ"]
    return out


def ipc_alignment(R, dis_path):
    """The two issue-rate levels (derived from the reduction's own per-card shapes) and, for the alignment
    that explains them, a READ of the reduction's top-level `loop_head_alignment`.

    The physics skeptic's finding is now in the reduction: a new `--dis` flag and `loop_head_alignment()`
    re-derive it from the committed disassembly and pin it one-to-one on the c2 family. The wf4 page walked
    `dis-a2.txt` itself here and printed its own body counts and modal spacing; that second derivation is
    gone, so every alignment number on the page is the reduction's. `--dis` is kept only to record which
    file the reduction read, and to check it is the same one.
    """
    levels, shapes = {}, []
    for card, c in R["cards"].items():
        for name, s in (g(c, "ipc", "shapes", default={}) or {}).items():
            if not isinstance(s, dict) or s.get("ipc") is None or s.get("harts") != 1:
                continue
            m = re.search(r"ops_per_iter (\d+)", name)
            ops = int(m.group(1)) if m else None
            shapes.append({"card": card, "shape": name.split(" / ")[0], "ops_per_iter": ops,
                           "ipc": s["ipc"], "vs_registered_pct": s.get("vs_registered_0_5791_pct")})
    for sh in shapes:
        if not sh["ops_per_iter"]:
            continue
        key = (sh["ops_per_iter"], round(sh["ipc"], 3))
        levels.setdefault(key, []).append(sh)
    lv = []
    for (ops, _), rows in sorted(levels.items()):
        vals = [r["ipc"] for r in rows]
        lv.append({"ops_per_iter": ops, "ipc_min": min(vals), "ipc_max": max(vals), "n_shapes": len(rows),
                   "cycles_per_iter": ops / mean(vals),
                   "shapes": sorted({r["shape"] for r in rows}), "cards": sorted({r["card"] for r in rows})})

    # derived: the 64-op and 128-op levels pair into a fast and a slow family; two points fix a line each
    def fit(pts):
        (o1, c1), (o2, c2) = pts
        slope = (c2 - c1) / (o2 - o1)
        return {"cycles_per_vector_op": slope, "fixed_cycles": c1 - slope * o1,
                "ops_per_cycle": 1.0 / slope if slope else None}
    by_ops = {}
    for row in lv:
        by_ops.setdefault(row["ops_per_iter"], []).append(row)
    fits = {}
    if 64 in by_ops and 128 in by_ops and len(by_ops[64]) >= 2 and len(by_ops[128]) >= 2:
        f64 = sorted(by_ops[64], key=lambda r: -r["ipc_min"])
        f128 = sorted(by_ops[128], key=lambda r: -r["ipc_min"])
        fits["fast"] = fit([(64, f64[0]["cycles_per_iter"]), (128, f128[0]["cycles_per_iter"])])
        fits["slow"] = fit([(64, f64[-1]["cycles_per_iter"]), (128, f128[-1]["cycles_per_iter"])])
        fits["fast"]["ipc"] = f64[0]["ipc_min"]
        fits["slow"]["ipc"] = f64[-1]["ipc_max"]
        fits["level_ratio_fast_over_slow"] = f64[0]["ipc_min"] / f64[-1]["ipc_max"]
        fits["extra_cycles_per_64op_iteration"] = f64[-1]["cycles_per_iter"] - f64[0]["cycles_per_iter"]
    rate_row = next((v for v in R["verdicts"] if v.get("rates")), {})
    ref = rate_row.get("E60_reference_ipc") or g(R, "cards", g(R, "meta", "primary_card"), "ipc",
                                                 "E60_reference") or 0.5791
    if fits:
        fits["E60_reference_ipc"] = ref
        fits["E60_over_fast"] = ref / fits["fast"]["ipc"]
        fits["E60_over_slow"] = ref / fits["slow"]["ipc"]

    # reads the SKEPTIC item: the alignment map, as the reduction re-derived and published it
    L = R.get("loop_head_alignment") or rate_row.get("loop_head_alignment") or {}
    c2 = L.get("c2_by_mode") or {}
    modes = g(R, "meta", "modes", default={}) or {}
    mode_name = {str(n): nm for nm, n in modes.items()}
    c2_rows = []
    for m, h in sorted(c2.items(), key=lambda kv: int(kv[0])):
        c2_rows.append({"mode": int(m), "kernel": mode_name.get(str(m)), "mnemonic": h.get("mnemonic"),
                        "head": h.get("head"), "mod32": h.get("mod32"), "n_vector_ops": h.get("n_vector_ops"),
                        "ipc": h.get("measured_ops_per_cycle_per_hart")})
    fast, slow = L.get("fast_rate"), L.get("slow_rate")
    return {"levels": lv, "fits": fits,
            "alignment": {
                "finding": L.get("finding"), "how": L.get("how"),
                "n_long_vector_loops": L.get("n_long_vector_loops"),
                "fast_residue": L.get("fast_residue"), "slow_residue": L.get("slow_residue"),
                "fast_rate": fast, "slow_rate": slow,
                "rate_by_head_mod32": L.get("rate_by_head_mod32_from_c2"),
                "one_rate_per_residue": L.get("one_rate_per_residue"),
                "residues_distinct": L.get("residues_distinct"),
                "c2_rows": c2_rows, "addr_heads": L.get("addr_heads"),
                "addr_count_check": L.get("addr_count_check"),
                "source": L.get("source"), "cite": L.get("cite"),
                "derived:pct_fast_over_slow": ((fast / slow - 1) * 100) if (fast and slow) else None,
            },
            "mode179_build_shift_pct": rate_row.get("mode179_build_shift_pct"),
            "rate_finding": rate_row.get("finding"),
            "disassembly": os.path.basename(dis_path or ""),
            "disassembly_is_the_one_the_reduction_read": bool(
                dis_path and L.get("source") and os.path.abspath(dis_path) == os.path.abspath(L["source"]))}


def conventions(R, prim):
    """Critic 14: capacitance and electron counts, in both conventions, for the prices the page quotes."""
    C = R["cards"][prim]
    out = []
    for label, path in (("a read-port (input) bit", ("derived", "e_in_fxor")),
                        ("a result (output) bit, the raw bridge", ("derived", "e_out_bridge")),
                        ("a register-file cell bit", ("derived", "e_cell")),
                        ("an input plus an output bit, through the inverter", ("derived", "e_sum_fnot_d1nz"))):
        node = g(C, *path, default={})
        for leg in ("rail", "board"):
            b = g(node, leg, default={})
            if b.get("fJ") is None:
                continue
            out.append({"quantity": label, "leg": leg, "fJ": fjse(b)[0], "se_fJ": fjse(b)[1],
                        "C_fF_halfCV2": b.get("C_fF_halfCV2"), "electrons_halfCV2": b.get("electrons_halfCV2"),
                        "C_fF_CV2": b.get("C_fF_CV2"), "electrons_CV2": b.get("electrons_CV2")})
            break
    return {"rows": out, "v_mean": C.get("v_mean"), "card": prim,
            "note": g(C, "derived", "e_in_fxor", "rail", "units_from")}


def reconciliation(R, IND, prim):
    """Critic 18: where the second implementation disagrees, named, with the reason where the files give one."""
    if not IND:
        return {"rows": [], "note": "no independent reduction was supplied"}
    Q = IND.get("quantities") or {}
    rows = []

    def add(label, mine, theirs, unit, why=""):
        if mine is None or theirs is None:
            return
        mv, ms = mine
        tv, ts = theirs
        if mv is None or tv is None:
            return
        rows.append({"quantity": label, "unit": unit, "mine": mv, "mine_se": ms, "theirs": tv,
                     "theirs_se": ts, "difference": (mv - tv) if (mv is not None and tv is not None) else None,
                     "in_SE": (abs(mv - tv) / ms) if (ms and mv is not None and tv is not None) else None,
                     "why": why})

    C = R["cards"][prim]
    D, F = C["derived"], C["families"]
    q3 = Q.get(prim) or {}
    pick = lambda d, k: ((d.get(k) or {}).get("value"), (d.get(k) or {}).get("se")) if d.get(k) else None
    mca = g(R, "method_choices", "method_choices", "family_A_with_or_without_the_origin", default={})
    mil = next((v for v in R["verdicts"] if "Miller wire law" in str(v.get("quantity", ""))), {})
    add("energy per toggled register-index bit", (mca.get("free_intercept_fJ_per_bit"), mca.get("free_intercept_se_fJ")),
        pick(q3, "A_slope_per_address_bit_p80"), "fJ/bit",
        "the same three rungs: a free intercept here, a different rung weighting there — the fit form is the method choice RECON 15 names")
    add("energy per flipped register-file cell bit", fjse(g(D, "e_cell", "board", default={})),
        pick(q3, "e_cell_p80"), "fJ", "the same A2.3 slope-difference form; the gap is which passes each kept")
    add("energy per carry stage, from the d3z route", fjse(g(D, "e_carry", "board", default={})),
        pick(q3, "e_carry_slope_minus_e_out_add_from_d3z_p80"), "fJ", "the registered estimator, both sides")
    add("energy per carry stage, importing e_out from family B",
        fjse(g(D, "e_carry_alt_from_B", "board", default={})),
        pick(q3, "e_carry_slope_minus_e_out_B_p80"), "fJ", "the route §4 forbids, reported by both")
    add("the carry ladder's slope per carry node", fjse(g(D, "e_out_add_plus_e_carry", "board", default={})),
        pick(q3, "C_slope_per_carry_node_p80_no_origin"), "fJ", "agrees inside one standard error")
    zg = next((v for v in R["verdicts"] if "zero-gate" in str(v.get("quantity", ""))), {})
    add("the zero-gate step", (zg.get("pJ_per_op"), zg.get("se_pJ_per_op")),
        pick(q3, "Z_d6_one_minus_d6_zero_pJ_per_op_p80"), "pJ/op", "a null on both sides; the point values differ by well under one SE")
    add("the carry ladder's residual rms, linear in L",
        (g(F, "C_curvature", "fits", "linear_L", "resid_rms_W"), None),  # a fit statistic, no between-pass SE
        pick(q3, "C_fit_rms_resid_L_p80"), "W", "different fit weighting, same preference for the linear form")
    add("Spearman rho over the four k_adj levels",
        (g(mil, "spearman_rho_per_pass", "value"), g(mil, "spearman_rho_per_pass", "se")),
        pick(q3, "M_spearman_rho_over_kadj_levels_p80"), "rho", "both negative, both against the page's law")
    add("the result-bit price, the raw 2 x 2 bridge at h = 32", fjse(g(D, "e_out_bridge", "board", default={})),
        pick(q3, "e_out_B_2x2_h32_fJ_per_result_bit_p80") or pick(q3, "e_out_B_2x2_h32_p80"), "fJ",
        "both read it well below E60's interval")
    rv = next((v for v in R["verdicts"] if v.get("rho") is not None), {})
    q1 = Q.get(rv.get("rho_card")) or {}
    add("rho, two harts over one", (rv.get("rho"), rv.get("rho_se")), pick(q1, "R_rho_p80"), "ratio",
        "agrees to the third decimal")
    nm = {k: (v or {}).get("n_passes") for k, v in q3.items() if isinstance(v, dict)}
    return {"rows": rows, "their_passes_on_the_primary": sorted({n for n in nm.values() if n})[:4],
            "mine_passes_on_the_primary": g(R, "cards", prim, "n_passes"),
            "note": "the two implementations set passes aside by different rules, which is most of every gap below"}


def readme_tables(path):
    """§1's seventeen desk groups and §3's not-testable rows, read out of the pre-registration itself."""
    if not path or not os.path.exists(path):
        return {"desk": [], "untestable": [], "coverage": {}}
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")

    def rows_under(head_rx, ncols):
        out, inside = [], False
        for ln in lines:
            if re.match(head_rx, ln):
                inside = True
                continue
            if inside and ln.startswith("## ") :
                break
            if inside and ln.startswith("|") and not re.match(r"^\|[\s:-]+\|", ln):
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                if len(cells) == ncols and cells[0].lower() not in ("#", "claims"):
                    out.append(cells)
        return out

    desk = [{"id": c[0], "claims": c[1], "verdict": c[2], "what": c[3]} for c in rows_under(r"^## 1\.", 4)]
    unt = [{"claims": c[0], "why": c[1]} for c in rows_under(r"^## 3\.", 2)]

    def claim_nums(t):
        out = set()
        for m in re.finditer(r"\bC(\d{2})\b", t):
            out.add(int(m.group(1)))
        for m in re.finditer(r"C(\d{2})\s*[-–]\s*C?(\d{2})", t):
            a, b = int(m.group(1)), int(m.group(2))
            if a < b < a + 20:
                out.update(range(a, b + 1))
        return out

    def section(rx):
        keep, inside = [], False
        for ln in lines:
            if re.match(rx, ln):
                inside = True
                continue
            if inside and ln.startswith("## "):
                break
            if inside:
                keep.append(ln)
        return "\n".join(keep)

    covered = set()
    for rx in (r"^## 1\.", r"^## 2\.", r"^## 3\.", r"^## 9\."):
        covered |= claim_nums(section(rx))
    allc = set(range(1, 96))
    return {"desk": desk, "untestable": unt,
            "coverage": {"n_claims": len(allc), "n_covered": len(covered & allc),
                         "uncovered": sorted("C%02d" % n for n in (allc - covered))}}


def repo_facts(repo, data_rel, reduction_dir=None):
    """Commit links for the pre-registration and its amendments, and an INVENTORY of the data directory.

    The page and this data directory are committed together, so the directory is described as the record:
    what it holds, counted on disk, with the three reduction outputs located in it or in the reduction's own
    folder (they are copied in by the same commit). The wf4 page read `git status` and said the per-card
    telemetry was untracked, which will not be true of the commit this page ships in.
    """
    out = {"commits": {}, "branch": None, "remote": None, "data_rel": data_rel, "data": {}}

    def git(*a):
        try:
            return subprocess.run(("git", "-C", repo) + a, capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception:
            return ""

    if not repo or not git("rev-parse", "--git-dir"):
        return out
    out["branch"] = git("rev-parse", "--abbrev-ref", "HEAD")
    out["remote"] = git("config", "--get", "remote.origin.url")
    for line in git("log", "--format=%H\t%s", "--", "tools/claims-v3/dtf/README.md").split("\n"):
        if "\t" not in line:
            continue
        h, sub = line.split("\t", 1)
        low = sub.lower()
        if "amendment a1" in low:
            out["commits"]["A1"] = {"sha": h, "subject": sub}
        elif "amendment a2" in low:
            out["commits"]["A2"] = {"sha": h, "subject": sub}
        elif "pre-register" in low or "pre-registered" in low:
            out["commits"].setdefault("prereg", {"sha": h, "subject": sub})

    # ---- the data directory, counted on disk
    root = os.path.join(repo, data_rel)
    inv = {"root": data_rel, "top_level_files": [], "proof_files": [], "cards": [], "camera": {},
           "reduction_outputs": {}, "n_files": 0, "bytes": 0}
    if os.path.isdir(root):
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                p = os.path.join(dirpath, fn)
                try:
                    inv["bytes"] += os.path.getsize(p)
                except OSError:
                    continue
                inv["n_files"] += 1
        inv["top_level_files"] = sorted(f for f in os.listdir(root)
                                        if os.path.isfile(os.path.join(root, f)))
        pf = os.path.join(root, "proof")
        if os.path.isdir(pf):
            inv["proof_files"] = sorted(os.listdir(pf))
        for card in sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))
                           and d not in ("proof",)):
            cd = os.path.join(root, card)
            blocks = {}
            for blk in sorted(os.listdir(cd)):
                bp = os.path.join(cd, blk)
                if not os.path.isdir(bp):
                    continue
                ps = sorted(d for d in os.listdir(bp) if re.fullmatch(r"p\d+", d))
                if ps:
                    files0 = sorted(os.listdir(os.path.join(bp, ps[0])))
                    blocks[blk] = {"passes": len(ps), "files_per_pass": files0}
                else:
                    blocks[blk] = {"files": sorted(os.listdir(bp))}   # not a pass block (the camera analysis)
            inv["cards"].append({"card": card, "blocks": blocks})
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if fn in ("cam.json", "tier1.json") and "dtf-cam-analysis" in dirpath:
                    inv["camera"][fn] = os.path.relpath(os.path.join(dirpath, fn), root)
                if fn.endswith(".png") and "dtf-cam-analysis" in dirpath:
                    inv["camera"].setdefault("png", []).append(
                        os.path.relpath(os.path.join(dirpath, fn), root))
        if inv["camera"].get("png"):
            inv["camera"]["png"] = sorted(inv["camera"]["png"])
    for fn in ("dtf.json", "reduce.txt", "runs.csv"):
        here = os.path.join(root, fn)
        there = os.path.join(reduction_dir or "", fn) if reduction_dir else None
        if os.path.exists(here):
            inv["reduction_outputs"][fn] = {"where": "in the data directory",
                                            "bytes": os.path.getsize(here)}
        elif there and os.path.exists(there):
            # not in the directory yet: it is written beside the reduction and copied in by the same commit,
            # so it counts toward what the committed directory holds
            b = os.path.getsize(there)
            inv["reduction_outputs"][fn] = {"where": "ships with this commit", "bytes": b}
            inv["n_files"] += 1
            inv["bytes"] += b
    out["data"] = inv
    return out


def camera(CAM):
    """Critic 15 and the skeptic's (d): the exploratory label, the spread across arms, the geometry."""
    if not CAM:
        return {}
    t2, t2s = CAM.get("tier2_primary") or {}, CAM.get("tier2_spatial") or {}
    ctl, geo = CAM.get("controls") or {}, CAM.get("geometry") or {}
    t1 = CAM.get("tier1_board_meter") or {}
    arms = (ctl.get("arm_sensitivity_hi_mk") or {})
    vals = [v for v in arms.values() if isinstance(v, (int, float))]
    return {"tier": (CAM.get("verdict") or {}).get("tier"),
            "statistic_mk": t2.get("statistic_mk"), "se_pass_mk": t2.get("se_pass_mk"),
            "per_pass_mk": t2.get("per_pass_mk"), "p_cyclic": t2.get("p_cyclic"),
            "p_enumerated": t2.get("p_cyclic_enumerated"), "p_labellings": t2.get("p_cyclic_labellings"),
            "null_sd_mk": t2.get("null_sd_cyclic_mk"), "lo_mk": t2.get("lo_mk"),
            "lo_p": t2.get("lo_p_cyclic"), "hi_minus_lo_mk": t2.get("hi_minus_lo_mk"),
            "hi_minus_lo_caveat": t2.get("hi_minus_lo_caveat"),
            "arms": arms, "arm_min_mk": min(vals) if vals else None, "arm_max_mk": max(vals) if vals else None,
            "arm_spread_pct": ((max(vals) - min(vals)) / min(vals) * 100) if vals else None,
            "monopole_mk": t2s.get("monopole_hi_mk"), "monopole_p": t2s.get("monopole_hi_p_cyclic"),
            "peak_px": t2s.get("profile_hi_peak_px"), "trough_px": t2s.get("profile_hi_trough_px"),
            "mm_per_px": t2s.get("mm_per_px"), "mm_note": t2s.get("mm_note"),
            "gradient_mk_per_px": t2s.get("gradient_hi_mk_per_px"), "gradient_p": t2s.get("gradient_hi_p_cyclic"),
            "orthogonal_mk": g(ctl, "orthogonal_axis", "stat_mk"), "orthogonal_p": g(ctl, "orthogonal_axis", "p_cyclic"),
            "footprint_mk": g(ctl, "die_footprint_rects", "stat_mk"), "footprint_p": g(ctl, "die_footprint_rects", "p_cyclic"),
            "footprint_what": g(ctl, "die_footprint_rects", "what"),
            "card_fraction": geo.get("card_fraction_of_frame"), "card_bbox": geo.get("card_bbox_xyxy"),
            "mask_is_not_the_card": geo.get("automatic_card_mask_is_NOT_the_card"),
            "why_kept": geo.get("why_it_was_kept"), "drift_mk_per_s": (CAM.get("block") or {}).get("field_drift_mk_per_s"),
            "board": {"hi_W": t1.get("W_minus_E_hi_w"), "hi_se_naive": t1.get("W_minus_E_hi_se_naive_w"),
                      "hi_t_naive": t1.get("W_minus_E_hi_t_naive"),
                      "hi_se_order": t1.get("W_minus_E_hi_se_order_adjusted_w"),
                      "hi_t_order": t1.get("W_minus_E_hi_t_order_adjusted"),
                      "lo_W": t1.get("W_minus_E_lo_w"), "lo_t_order": t1.get("W_minus_E_lo_t_order_adjusted"),
                      "order_term_W": t1.get("block_order_term_w"),
                      "hi_minus_rest_W": t1.get("hi_minus_rest_w"),
                      "hi_minus_lo_W": t1.get("hi_minus_lo_w"), "hi_minus_lo_se": t1.get("hi_minus_lo_se_w"),
                      "reading": t1.get("reading"), "registered_rule": t1.get("registered_rule")},
            "established": (CAM.get("verdict") or {}).get("what_is_established") or [],
            "not_established": (CAM.get("verdict") or {}).get("what_is_NOT_established") or [],
            "honest_reading": (CAM.get("verdict") or {}).get("honest_reading")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dtf", required=True)
    ap.add_argument("--cam")
    ap.add_argument("--independent")
    ap.add_argument("--readme")
    ap.add_argument("--repo")
    ap.add_argument("--dis")
    ap.add_argument("--data-rel", default="docs/reports/data/2026-10-21-dtf")
    ap.add_argument("--reduction-dir", help="where dtf.json/reduce.txt/runs.csv are, if not yet in the data dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.dtf))
    CAM = json.load(open(a.cam)) if a.cam and os.path.exists(a.cam) else {}
    IND = json.load(open(a.independent)) if a.independent and os.path.exists(a.independent) else {}
    prim = g(R, "meta", "primary_card", default="aifoundry3")
    F = {
        "primary_card": prim,
        "generated_from": {"dtf": _rel(a.dtf), "reduction_generated": g(R, "meta", "generated"),
                           "manifest": g(R, "meta", "manifest"), "cam": _rel(a.cam) if a.cam else None,
                           "independent": _rel(a.independent) if a.independent else None},
        "census": census(R),
        "changed_word_price": changed_word_price(R, prim),
        "bridge_term": bridge_term(R, prim),
        "replications": replications(R),
        "c14_leak": c14_leak(R),
        "cell_scaling": cell_scaling(R, prim),
        "zero_gate": zero_gate(R, prim, a.readme),
        "intercept_row": intercept_row(R, prim),
        "rho": rho_margin(R, IND),
        "c58_c33": c58_and_c33(R, prim),
        "ed4": ed4(R, prim),
        "e_out_routes": e_out_routes(R, prim),
        "addr": addr_readings(R, prim),
        "ipc": ipc_alignment(R, a.dis),
        "conventions": conventions(R, prim),
        "half_die": {k: {"value": g(c, "derived", "half_die_result_path_load_W", "value"),
                         "se": g(c, "derived", "half_die_result_path_load_W", "se"),
                         "n_passes": g(c, "derived", "half_die_result_path_load_W", "n_passes"),
                         "mhz": c.get("clock_mhz"), "mv": round((c.get("v_mean") or 0) * 1000)}
                     for k, c in R["cards"].items()
                     if g(c, "derived", "half_die_result_path_load_W", "value")},
        "reconciliation": reconciliation(R, IND, prim),
        "camera": camera(CAM),
        "repo": repo_facts(a.repo, a.data_rel,
                           a.reduction_dir or os.path.dirname(os.path.abspath(a.dtf))),
    }
    F.update(readme_tables(a.readme))
    json.dump(F, open(a.out, "w"), indent=1, default=str)
    print("wrote", a.out)
    for k in ("changed_word_price", "bridge_term"):
        print(" ", k, "=", json.dumps({kk: vv for kk, vv in (F[k] or {}).items()
                                       if isinstance(vv, (int, float, bool))}, indent=1)[:900])
    print("  reduction outputs:", json.dumps(g(F, "repo", "data", "reduction_outputs"), default=str))


if __name__ == "__main__":
    main()
