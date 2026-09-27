#!/usr/bin/env python3
"""Write the computed blocks of the observability hub's data file from the analyses that produce them.

    python3 tools/ettelem/sync_hub_data.py            # rewrite docs/reports/sources/limits-of-observability.data.json
    python3 tools/ettelem/sync_hub_data.py --check    # exit 1, and name the blocks, if that file is stale
    python3 tools/ettelem/sync_hub_data.py --only claims_status,meter   # rewrite those blocks, keep the rest
                                                      # (for when another block's inputs are being regenerated)

then build the page:

    python3 scripts/build-report.py limits-of-observability docs/reports/sources/limits-of-observability.data.json \\
        docs/reports/2026-09-20-et-soc1-limits-of-observability.html

The hub's text blocks (ladder, reports, improvements, sessions, superseded, contrast, the PVT description) are kept
by hand in the data file; this script replaces only the blocks below, so a refit or a regenerated catalogue reaches
the page without anyone copying numbers.

  power.idle_73c      dvfs.json idle_check: the 300-sample idle at 73 C after about 20.6 h with no workload
  power.fit           unmetered_fit.json, per card: coefficients, standard errors, rms (all and DRAM configurations)
                      and the refit with the line read before each store through the L1 counted (for comparison only)
  power.per_config    unmetered_fit.json <card>.per_config: each configuration's fit inputs (the V1 chart)
  power.droop         unmetered_fit.json ddr_droop, with its per_config rows (the droop chart)
  power.rail_filter   catalogue.json rail_filter: how far the rails' reading has fallen 1 s and 2 s after the board
                      steps down, and the fitted time constant, per card
  power.sampler       catalogue.json bursts: the sampler's own latency per burst (sampler_median_ms, sampler_max_ms),
                      per card, summarised for the DRAM-read bursts that slow it, and those bursts' board watts on each
                      card over aifoundry2's; and, as .ring, reruns.json dropped[]: the median latency in each rerun pass
                      dropped because the sampler was starved (the s <-> s+16 ring), per card, for the version-3
                      campaign's reruns and the 23 September ones. Per card, .dist is every distinct latency a catalogue
                      burst took (value, count, and the configuration/pass for six or fewer), and .dropped is every
                      reruns.json dropped[] entry of that card's own runs (burst, rerun pass, latency): both for the
                      chart "The meter starved by the workload"
  power.idle_unsensed catalogue.json bursts: board idle less the three rails' idle, per card, with the board's idle
                      and the die range
  power.checks        the fit's robust errors and per-pass coefficients, and the DDR-droop calibration on each card's
                      own telemetry (its V3-CATFULL blocks, fit_unmetered.catalogue_telemetry()), per pass (checks():
                      the version-3 claims check asks for them per card); each card's droop block also carries its own
                      per_config rows (fu.droop's full output), so the "Is the DDR monitor a DRAM meter?" chart can
                      draw any card
  energy_events       every event the reports priced, with its energy [range] and the rate at which the measurement
                      ran it, for the chart "How many identical events before the meter sees one?" (the energy manual's
                      catalogue, tensor bars and reruns, on three cards since 26 September; the wires from Heat per
                      millimetre's third run; the hot line and the flips as before; since 27 September E48's gathered and
                      scattered elements and packed atomic adds, manual.json gs); its meter block
                      takes the service processor's pass per card from the version-3 campaign (meter())
  claims_status       the claims check's verdicts per page, and the cards behind each claim, for §1's scoreboard: one
                      series per entry of CLAIM_SERIES (the claims after the campaign of 25-26 Sep, each tested claim
                      with its outcome on the campaign's cards, and the version-3 plan before any campaign run)

Deterministic: the same inputs give the same file, byte for byte.
"""
import argparse
import glob
import gzip
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gs_levels as GL  # noqa: E402  E48's configurations (the gathered and scattered elements, the packed atomics)

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
D = os.path.join(ROOT, "docs", "reports", "data")
HUB = os.path.join(ROOT, "docs", "reports", "sources", "limits-of-observability.data.json")
EM = os.path.join(D, "2026-09-23-energy-manual")
FIT, CAT, MAN, RERUNS = (os.path.join(EM, f) for f in ("unmetered_fit.json", "catalogue.json", "manual.json", "reruns.json"))
DVFS = os.path.join(D, "2026-09-22-dvfs-aifoundry2", "dvfs.json")
WIRE = os.path.join(D, "2026-09-24-wire-energy", "report.json")
HORACE = os.path.join(D, "2026-09-21-horace-aifoundry2")
PAGES = "https://spacesheep.dev/@yaroslavvb/"

# The meter's own constants, as the ladder rows 'Board power' and 'Rail power' quote them: the board reading in 10 mW
# steps and the rails in 1 mW, a new value per service-processor pass. The pass comes from meter(), below.
LSB = {"board_lsb_w": 0.010, "rail_lsb_w": 0.001}
CLAIMS_V3 = os.path.join(D, "2026-09-25-claims-v3")
TEL_V3 = os.path.join(CLAIMS_V3, "results", "tel.json")
RAW_V3 = os.path.join(CLAIMS_V3, "raw")    # V3-CATFULL telemetry: <card>/catfull/p<pass><part>/telemetry.jsonl.gz


def campaign_cards():
    """The version-3 campaign's cards, from tools/claims-v3/campaign.py (the reducers' default card list)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("campaign", os.path.join(ROOT, "tools", "claims-v3", "campaign.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return tuple(mod.CAMPAIGN)


# The cards of the power blocks: the campaign's (aifoundry2, aifoundry3, aifoundry1-c1), whose full catalogue
# (V3-CATFULL) catalogue.json and unmetered_fit.json hold since 26 September. CARDS[0] is the reference card
# (aifoundry2): the droop's named configurations are chosen on it and the cross-card ratios divide by it.
CARDS = campaign_cards()

# Two-sided 99% t quantiles by degrees of freedom, for intervals over passes (three passes: df 2).
T99 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032}

# The claims check, per page (§1's scoreboard). Each series is one file whose claims[] carry page, cards and a verdict
# field, optionally overlaid with the campaign's results (below); the page draws every series, in this order, one bar
# per page and series. The first is the claims after the version-3 campaign of 25-26 September (complete; its results
# are in results/), the second the version-3 plan's verdicts, committed before any card run, for comparison.
PAGEMAP_V3 = os.path.join(CLAIMS_V3, "results", "pagemap.json")
CLAIM_SERIES = [
    {"id": "post-v3", "file": os.path.join(CLAIMS_V3, "plan3.json.gz"), "verdict": "effective_verdict", "date": "2026-09-26",
     "overlay": PAGEMAP_V3, "label": "After the version-3 campaign: its results, 26 September", "short": "after v3",
     "note": "the campaign is complete: it measured aifoundry2, aifoundry3 and aifoundry1-c1 on 25\u201326 September, and its "
             "results are in docs/reports/data/2026-09-25-claims-v3/results; each claim it tested takes its outcome on those "
             "cards, the others keep their earlier verdict"},
    {"id": "pre-v3", "file": os.path.join(CLAIMS_V3, "plan3.json.gz"), "verdict": "effective_verdict", "date": "2026-09-25",
     "label": "Before the version-3 campaign: the plan of 25 September", "short": "before v3",
     "note": "its verdicts, pre-registered before any campaign run, on the evidence the pages then rested on "
             "(aifoundry2 and aifoundry3)"},
]
# The verdicts in order, strongest evidence first, with the words the page shows (PLAN3's standard, and the campaign's
# outcomes for the after-campaign series). A quoted number takes its home page's verdict (effective_verdict), so
# QUOTED does not appear. The plan's PROVEN-BOTH ("on both cards") is read as PROVEN (VERDICT_ALIAS): one class,
# "proven on the cards", for both series, since after the campaign a claim can be proven on up to three cards.
# CORRECTED exists only after the campaign. A verdict a later file adds that is not listed here is drawn after these,
# under its own name.
VERDICTS = [
    ["PROVEN", "proven on the cards", "held on every card measured, with at least three independent repeats on each (a 99% interval that "
     "excludes the null, or a deterministic value in every repeat) and the same sign: before the campaign on aifoundry2 and aifoundry3, "
     "after it on every card the campaign tested (up to three)"],
    ["CORRECTED", "a test behind it failed", "a pre-registered test covering it failed in at least one part, which may be a number "
     "the page does not quote (a claim is counted here if any of its tests failed); the page gives what was measured"],
    ["CARD-DIFFERENT", "differs by card", "measured on each card, with values or outcomes that differ between them: stated per card"],
    ["ONE-CARD", "one card only", "rests on one card's data"],
    ["UNDER-REPLICATED", "fewer than three repeats", "measured, with fewer than three independent repeats on a card: not confirmed"],
    ["WITHIN-NOISE", "within noise", "the effect is not resolved from the noise"],
    ["NOT-EMPIRICAL", "not a measurement", "arithmetic, a source reading, a specification or a simulation"],
]
VERDICT_ALIAS = {"PROVEN-BOTH": "PROVEN"}
# The campaign's outcome for a claim it tested (results/pagemap.json: every item, or part of one, that tests the claim,
# with its all_cards outcome over aifoundry2, aifoundry3 and aifoundry1-c1, amendment A4). Several items (or parts)
# give the weakest, in this order:
#   any FAIL                         -> CORRECTED         the published statement did not hold (in some part)
#   else any INSUFFICIENT            -> UNDER-REPLICATED  a card had fewer than three kept repeats: not confirmed
#   else any CARD-DIFFERENT          -> CARD-DIFFERENT    holds on some cards and not on others: stated per card
#   else any PASS                    -> PROVEN            held on every card tested (a REPORTED part beside it is a
#                                                         per-card value, not a contrary result)
#   else (REPORTED or DESCRIPTIVE)   -> the claim's earlier verdict: values given per card, nothing tested
# The cards behind a tested claim become the cards the campaign's items tested or reported it on (their all_cards
# blocks), joined with its earlier cards unless it was corrected (a corrected statement rests on the campaign's data).
V3_ORDER = [("FAIL", "CORRECTED"), ("INSUFFICIENT", "UNDER-REPLICATED"), ("CARD-DIFFERENT", "CARD-DIFFERENT"), ("PASS", "PROVEN")]
# claims[].cards as the inventories write it, mapped to card ids (the chartkit registry's): a2, a3, both, none; a1c1
# (or aifoundry1-c1) and "all" (the campaign's three cards, amendment A4) for the results. Any other token is kept as
# its own card id, so a new card needs no change here.
CARD_WORDS = {"a2": ["aifoundry2"], "a3": ["aifoundry3"], "a1c1": ["aifoundry1-c1"], "a1c0": ["aifoundry1-c0"],
              "both": ["aifoundry2", "aifoundry3"], "all": ["aifoundry2", "aifoundry3", "aifoundry1-c1"],
              "all3": ["aifoundry2", "aifoundry3", "aifoundry1-c1"], "none": [], "": []}
CARD_ORDER = ["aifoundry2", "aifoundry3", "aifoundry1-c1", "aifoundry1-c0"]


def load(p):
    with open(p) as fh:
        return json.load(fh)


def load_any(p):
    """A JSON file, gzipped or not."""
    with (gzip.open(p, "rt") if p.endswith(".gz") else open(p)) as fh:
        return json.load(fh)


def r3(v):
    return round(float(v), 3)


def rng(lo, hi):
    return [r3(lo), r3(hi)]


# ---------------------------------------------------------------- power blocks
def power_blocks(fit, cat, dvfs, reruns):
    ic = dvfs["idle_check"]
    out = {"idle_73c": {"board_w": ic["board_w"], "board_sd": ic["board_sd"], "minion_w": ic["rails"]["minion"],
                        "sram_w": ic["rails"]["sram"], "noc_w": ic["rails"]["noc"], "unsensed_w": ic["board_minus_rails"],
                        "die_c": ic["die_c"], "hours": ic["hours_idle"], "samples": ic["samples"]}}
    # The fit and its per-configuration rows go to the page for every card the fit has (the V1 chart offers each);
    # the blocks below are per card for the campaign's cards (CARDS).
    fc = sorted((c for c in fit if isinstance(fit[c], dict) and "coef" in fit[c] and "per_config" in fit[c]),
                key=lambda c: (CARD_ORDER.index(c) if c in CARD_ORDER else len(CARD_ORDER), c))
    out["fit"] = {c: {k: v for k, v in fit[c].items() if k not in ("per_config", "per_config_fields")} for c in fc}
    out["per_config"] = {"fields": fit[CARDS[0]]["per_config_fields"], **{c: fit[c]["per_config"] for c in fc}}
    out["droop"] = fit["ddr_droop"]
    out["rail_filter"] = {c: {k: cat["rail_filter"][c][k] for k in ("frac_1s", "frac_2s", "tau_s", "n")} for c in CARDS}
    out["rail_filter"]["rule"] = cat["rail_filter"][CARDS[0]]["rule"]

    # The sampler's latency: every burst records the median and the longest of its samples' took_ms.
    reads = lambda cfg: cfg.startswith(("tload/dram/", "dramrow/stride1K/"))  # noqa: E731  full-rate DRAM reads
    samp = {}
    for c in CARDS:
        bs = cat["bursts"][c]
        rd = [b for b in bs if reads(b["cfg"])]
        other = [b for b in bs if not reads(b["cfg"])]
        slow = []
        for b in sorted((b for b in bs if b["sampler_median_ms"] > 60), key=lambda b: (b["cfg"], b["pass"])):
            rest = [x["rail_noc_w"] for x in bs if x["cfg"] == b["cfg"] and x["pass"] != b["pass"]]
            slow.append({"cfg": b["cfg"], "pass": b["pass"], "median_ms": b["sampler_median_ms"], "max_ms": b["sampler_max_ms"],
                         "noc_w": r3(b["rail_noc_w"]), "noc_other_passes_w": r3(statistics.mean(rest))})
        samp[c] = {"bursts": len(bs), "over_60ms": len(slow), "slow": slow,
                   "read_median_ms": [min(b["sampler_median_ms"] for b in rd), max(b["sampler_median_ms"] for b in rd)],
                   "read_max_ms": max(b["sampler_max_ms"] for b in rd),
                   "other_median_ms": [min(b["sampler_median_ms"] for b in other), max(b["sampler_median_ms"] for b in other)]}
    # Every distinct latency a card's own bursts took (a rug for "The meter starved by the workload"): the value,
    # how many bursts took it, and, for six or fewer, which configuration and pass.
    for c in CARDS:
        by_ms = {}
        for b in cat["bursts"][c]:
            by_ms.setdefault(b["sampler_median_ms"], []).append(b)
        dist = []
        for ms in sorted(by_ms):
            grp = by_ms[ms]
            row = {"ms": r3(ms), "n": len(grp)}
            if len(grp) <= 6:
                row["cfgs"] = [{"cfg": b["cfg"], "pass": b["pass"]} for b in grp]
            dist.append(row)
        samp[c]["dist"] = dist
    # Every reruns.json dropped[] entry that is this card's own run (burst, which rerun pass, and its latency). The card
    # is the longest card name in the pass's path (so aifoundry1-c1 is not read as another card); the run is the
    # version-3 pass (raw/<card>/rl/p<K>/A: "version-3 rerun, pass K") or the 23 September directory's pass.
    def card_in(path):
        return next((c for c in sorted(CARDS, key=len, reverse=True) if c in path), None)

    def run_of(path):
        m = re.search(r"/rl/p(\d+)/", path + "/")
        if "claims-v3" in path and m:
            return f"version-3 rerun, pass {m.group(1)}"
        if "2026-09-23-reruns" in path:
            return f"23 September rerun, {os.path.basename(path)}"
        return f"{os.path.basename(os.path.dirname(path))}/{os.path.basename(path)}"
    for c in CARDS:
        samp[c]["dropped"] = [{"burst": d["burst"], "run": run_of(d["pass"]), "ms": r3(d["sampler_median_ms"])}
                              for d in reruns.get("dropped", []) if card_in(d["pass"]) == c]
    # The DRAM-read bursts' board watts over idle on each other card over the reference card's (their range), against
    # the same ratio over every catalogue entry (its 10th-90th percentiles, "the middle 80%"); and catalogue.json's
    # own cross_card block (aifoundry3 over aifoundry2).
    s2 = cat["cards"][CARDS[0]]["summary"]
    samp["reads_over_" + CARDS[0]], samp["all_over_" + CARDS[0]] = {}, {}
    for c in CARDS[1:]:
        sc = cat["cards"][c]["summary"]
        ratio = {k: sc[k]["over_idle_w"]["mean"] / s2[k]["over_idle_w"]["mean"] for k in sorted(s2) if k in sc and s2[k]["over_idle_w"]["mean"] > 0}
        rd = [v for k, v in ratio.items() if reads(k)]
        allr = sorted(ratio.values())
        samp["reads_over_" + CARDS[0]][c] = rng(min(rd), max(rd))
        samp["all_over_" + CARDS[0]][c] = {"median": r3(statistics.median(allr)), "p10_p90": [r3(v) for v in statistics.quantiles(allr, n=10, method="inclusive")[::8]],
                                           "n": len(allr)}
    cc = cat["cross_card"]
    samp["cross_card"] = {"pair": cc["pair"], "median": r3(cc["median"]), "p10": r3(cc["p10"]), "p90": r3(cc["p90"]), "n": cc["n"]}
    samp["reads"] = "tload/dram/* and dramrow/stride1K/* (full-rate DRAM reads)"
    # The ring that starves it: the rerun passes of the s <-> s+16 ring (burst "xshire16") that analyze_reruns.py
    # dropped for the sampler's latency (median > 60 ms); any other starved burst would not belong to this sentence.
    # Per card and per campaign: the version-3 reruns (V3-RL, raw/<card>/rl/) and the 23 September rerun directories.
    ring = [d for d in reruns.get("dropped", []) if d.get("burst") == "xshire16" and d.get("sampler_median_ms", 0) > 60]
    card_of = lambda d: next(c for c in sorted(CARDS, key=len, reverse=True) if c in d["pass"])  # noqa: E731
    per = {}
    for d in ring:
        per.setdefault("v3" if "claims-v3" in d["pass"] else "23sep", {}).setdefault(card_of(d), []).append(d["sampler_median_ms"])
    samp["ring"] = {"bursts": sorted({d["burst"] for d in ring}), "cards": [c for c in CARDS if any(card_of(d) == c for d in ring)],
                    "median_ms": [d["sampler_median_ms"] for d in ring], "passes": len(ring),
                    "per_card": {k: {c: per[k][c] for c in CARDS if c in per[k]} for k in sorted(per, reverse=True)},
                    "v3_passes_per_card": {c: len(v) for c, v in (reruns.get("passes_per_card", {}).get("rings") or {}).items()},
                    "fallback_23sep": reruns.get("fallback_23sep", {}).get("xshire16")}
    out["sampler"] = samp

    iu = {}
    for c in CARDS:
        bs = cat["bursts"][c]
        u = [b["p_idle_w"] - b["minion_idle_w"] - b["sram_idle_w"] - b["noc_idle_w"] for b in bs]
        T = [b["die_c_idle"] for b in bs]
        P = [b["p_idle_w"] for b in bs]
        iu[c] = {"w": rng(min(u), max(u)), "board_w": rng(min(P), max(P)), "die_c": rng(min(T), max(T)), "bursts": len(bs)}
    out["idle_unsensed"] = iu
    out["checks"] = checks(cat, fit)
    return out


# ---------------------------------------------------------------- per-card and per-pass checks (version 3)
def ci99(v):
    """Mean and two-sided 99% t interval of a few pass-level values."""
    m = statistics.mean(v)
    h = T99[len(v) - 1] * statistics.stdev(v) / len(v) ** 0.5
    return [r3(m - h), r3(m + h)]


def checks(cat, fit):
    """What the page needs to state the fit and the droop per card and per pass, computed with fit_unmetered.py's own
    functions (the same rows, windows and fits as unmetered_fit.json):

      fit[card]    se_hc3: heteroscedasticity-robust (HC3) standard errors of the published coefficients, since the
                   DRAM configurations that fix the DRAM term carry 3-4x the pooled residual; pass_coef: the same fit
                   on each catalogue pass alone, with its 99% t interval over the passes (pass_ci99)
      droop[card]  the DDR-droop calibration on each card's own catalogue telemetry (aifoundry2's reproduces
                   unmetered_fit.json ddr_droop): slope, the common term for the rest of the board, rms, n, the idle
                   reading and how it moves with the die temperature (idle_vs_temp), the minion rail's IR drop; each
                   per pass with its 99% interval; the largest excess of a
                   burst with no DRAM traffic; and, per pass, the configurations the page names (the two largest
                   non-DRAM droops outside the L3 row walks, and the largest L3 row walk, all chosen on aifoundry2)
    """
    import numpy as np
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fit_unmetered as fu
    names = ["minion", "sram", "noc", "dram_pj_per_byte"]
    out = {"fit": {}, "droop": {}}
    for c in CARDS:
        bs = cat["bursts"][c]
        rows = fu.config_means(bs)
        X, coef, res, _ = fu._fit(rows, list(rows))
        XtXi = np.linalg.inv(X.T @ X)
        h = np.einsum("ij,jk,ik->i", X, XtXi, X)
        W = X * (res / (1 - h))[:, None]
        se = np.sqrt(np.diag(XtXi @ (W.T @ W) @ XtXi))
        passes = sorted({b["pass"] for b in bs})
        pc = []
        for p in passes:
            rp = fu.config_means([b for b in bs if b["pass"] == p])
            pc.append(fu._fit(rp, list(rp))[1])
        out["fit"][c] = {"se_hc3": {k: float(v) for k, v in zip(names, se)},
                         "pass_coef": {k: [r3(x[i]) for x in pc] for i, k in enumerate(names)},
                         "pass_ci99": {k: ci99([float(x[i]) for x in pc]) for i, k in enumerate(names)}}
    # Each card's V3-CATFULL telemetry (nine blocks: three passes of three parts), the files fit_unmetered.py reads.
    tel = {c: fu.catalogue_telemetry(c, RAW_V3) for c in CARDS}
    for c in CARDS:
        if not tel[c]:
            sys.exit(f"{RAW_V3}: no catfull telemetry for {c}")
    whole = {c: fu.droop(cat["bursts"][c], fit[c], tel[c]) for c in CARDS}
    a2 = {r[0]: r for r in whole[CARDS[0]]["per_config"]}
    nd = [k for k in a2 if not fu.moves_dram(k)]
    top = sorted((k for k in nd if not k.startswith("dramrow/stride8K")), key=lambda k: -a2[k][1])[:2]
    l3 = max((k for k in nd if k.startswith("dramrow/stride8K")), key=lambda k: a2[k][1])
    for c in CARDS:
        w = whole[c]
        a, b = w["mv_per_dram_offrail_w"], w["mv_per_board_w_common"]
        ex = max(((r[1] - (a * r[2] + b * (r[3] - r[2])), r[0]) for r in w["per_config"] if not fu.moves_dram(r[0])))
        per = [fu.droop([x for x in cat["bursts"][c] if x["pass"] == p], fit[c], tel[c]) for p in sorted({x["pass"] for x in cat["bursts"][c]})]
        pcfg = [{r[0]: r[1] for r in d["per_config"]} for d in per]
        k3 = {"mv_per_dram_offrail_w": "slope", "mv_per_board_w_common": "common", "minion_ir_drop_mv_per_w": "ir"}
        out["droop"][c] = {"slope": r3(a), "common": r3(b), "rms_mv": r3(w["rms_mv"]), "n": w["n"],
                           "idle_ddr_mv": r3(w["idle_die_mv"]["ddr"]), "idle_vs_temp": idle_ddr_vs_temp(cat["bursts"][c], tel[c], fu),
                           "ir": r3(w["minion_ir_drop_mv_per_w"]),
                           "passes": {v: [round(d[k], 4) for d in per] for k, v in k3.items()},
                           "pass_ci99": {v: ci99([d[k] for d in per]) for k, v in k3.items()},
                           "max_nondram_excess_mv": [r3(ex[0]), ex[1]],
                           "named": {k: {"mean": r3({r[0]: r[1] for r in w["per_config"]}[k]), "passes": [r3(q[k]) for q in pcfg]}
                                     for k in top + [l3]},
                           "per_config_fields": w["per_config_fields"], "per_config": w["per_config"]}
    out["droop"]["named"] = {"mesh": top, "l3": l3}
    out["source"] = ("tools/ettelem/sync_hub_data.py checks(), with fit_unmetered.py's config_means, _fit and droop on catalogue.json and each "
                     "card's catalogue telemetry (catalogue_telemetry(): the V3-CATFULL blocks, raw/<card>/catfull/p*/telemetry.jsonl.gz)")
    return out


def idle_ddr_vs_temp(bursts, paths, fu):
    """The DDR monitor's idle reading against the die temperature: for every burst, the mean die_mv.ddr over
    fit_unmetered.py's idle window (2.5 s to 0.2 s before the burst starts) against the burst's die_c_idle; the
    least-squares slope, and the die temperatures' 10th-90th percentiles (what the page calls the middle 80%)."""
    import numpy as np
    T = sorted((json.loads(line) for p in paths for line in gzip.open(p, "rt") if line.startswith("{")), key=lambda r: r["t_ms"])
    ts = np.array([r["t_ms"] / 1000 for r in T])
    dd = np.array([r["die_mv"]["ddr"] for r in T], float)
    x, y = [], []
    for b in bursts:
        m = (ts >= b["t_lo"] - fu.IDLE_FROM_S) & (ts < b["t_lo"] - fu.IDLE_TO_S)
        if m.sum() >= 3:
            x.append(b["die_c_idle"])
            y.append(float(dd[m].mean()))
    slope = float(np.polyfit(x, y, 1)[0])
    return {"slope_mv_per_c": r3(slope), "die_c_p10_p90": [round(float(v), 1) for v in np.percentile(x, [10, 90])],
            "die_c": rng(min(x), max(x)), "n": len(x)}


# ---------------------------------------------------------------- the meter's refresh (version 3)
def meter(tel):
    """One reading of the meter: its steps (LSB) and the service processor's pass per card, from the version-3
    campaign's V3-TEL (E41, results/tel.json): the SP stats trace's pass interval with no sampler running (the quiet
    arm, Q) and while ettelem samples at 10 Hz (the E10 arm), three passes per card. TEL-P1 and TEL-P3 give them for
    aifoundry2 (tested) and aifoundry1-c1 (reported), TEL-P5 for aifoundry3 (tested) and again for aifoundry1-c1 (the
    two must agree). The page states the medians over the passes; pass_s (aifoundry2 under ettelem's 10 Hz, as every
    power page sampled) sets one reading's energy step, and the keys pass_s_a3 and sp_pass_s_quiet_a2 are the ones
    the page reads."""
    it = {x["item"]: x for x in tel["items"]} if isinstance(tel["items"], list) else tel["items"]
    per = {}
    for name, key, field in (("TEL-P1", "quiet_ms", "Q_ms"), ("TEL-P3", "sampled_ms", "E10_ms"),
                             ("TEL-P5", "quiet_ms", "Q_ms"), ("TEL-P5", "sampled_ms", "E10_ms")):
        for c, v in it[name]["per_card"].items():
            vals = [p[field] for p in (v.get("passes") or []) if p.get(field) is not None]
            if not vals:
                continue
            old = per.setdefault(c, {}).setdefault(key, vals)
            if old != vals:
                sys.exit(f"{TEL_V3}: {name} gives {c} {key} {vals}, another item {old}")
    for c in per:
        per[c] = {k: per[c][k] for k in ("quiet_ms", "sampled_ms") if k in per[c]}
    per = {c: per[c] for c in sorted(per, key=lambda c: (CARD_ORDER.index(c) if c in CARD_ORDER else len(CARD_ORDER), c))}
    s = lambda c, k: r3(statistics.median(per[c][k]) / 1000)  # noqa: E731
    return {**LSB, "pass_s": s("aifoundry2", "sampled_ms"), "pass_s_a3": s("aifoundry3", "sampled_ms"),
            "pass_s_a1c1": s("aifoundry1-c1", "sampled_ms"), "sp_pass_s_quiet_a2": s("aifoundry2", "quiet_ms"),
            "sp_pass_s_quiet_a3": s("aifoundry3", "quiet_ms"), "sp_pass_s_quiet_a1c1": s("aifoundry1-c1", "quiet_ms"),
            "sp_pass_ms": per,
            "source": "results/tel.json of the version-3 campaign (TEL-P1, TEL-P3, TEL-P5): the SP stats trace's pass, "
                      "per pass, quiet and under ettelem at 10 Hz; the medians over the passes"}


# ---------------------------------------------------------------- energy events
# V3-RL's ABBA labels, merged into their level (as tools/ettelem/analyze_reruns.py V3_LABEL)
V3_LABEL = {"l2-1": "l2", "l2-2": "l2", "scp-local-1": "scp-local", "scp-local-2": "scp-local"}


def v3_rl_dirs(root, half):
    """The <half> directory (A: rings, B: levels, relay) of every used V3-RL pass on every card under root
    (<card>/rl/p<K>/), relative to ROOT: the passes tools/ettelem/analyze_reruns.py v3_rl_passes() uses (block.json
    status ok, not a dry run; p<K>.attempt-* directories are never used)."""
    out = []
    for bj in sorted(glob.glob(os.path.join(ROOT, root, "*", "rl", "p[0-9]*", "block.json"))):
        pd = os.path.dirname(bj)
        if not re.fullmatch(r"p\d+", os.path.basename(pd)):
            continue
        try:
            b, p = load(bj), load(os.path.join(pd, "pass.json"))
        except (OSError, ValueError):
            continue
        if b.get("status") == "ok" and not p.get("dry"):
            out.append(os.path.relpath(os.path.join(pd, half), ROOT))
    return out


def runs_median(dirs, pattern, key):
    """Median rate per label over every launch in the rerun passes' runs.jsonl (launch -1 is the warm-up); V3-RL's
    ABBA labels count as their level."""
    by = {}
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(ROOT, d, pattern, "runs.jsonl"))):
            with open(f) as fh:
                for line in fh:
                    if not line.startswith("{"):
                        continue
                    r = json.loads(line)
                    if r.get("launch", 0) < 0 or not r.get("ok", True):
                        continue
                    v = key(r)
                    if v:
                        by.setdefault(V3_LABEL.get(r["label"], r["label"]), []).append(v)
    return {k: statistics.median(v) for k, v in by.items()}


def pooled(s, scale):
    """A pooled {mean, lo, hi, per_card} block (analyze_reruns / catalogue style) in joules."""
    pc = {c: r3sig(v["mean"] * scale) for c, v in (s.get("per_card") or {}).items() if isinstance(v, dict) and "mean" in v}
    return {"e": [r3sig(s["mean"] * scale), r3sig(s["lo"] * scale), r3sig(s["hi"] * scale)], "cards": pc}


def r3sig(v):
    return float(f"{v:.4g}")


def energy_events(man, reruns, wire, model, hrep, tel):
    ev = []
    op = man["operating_point"]["mhz"] * 1e6

    def add(family, key, label, unit, src, variants, note=None):
        e = {"id": key, "family": family, "label": label, "unit": unit, "src": src, "v": variants}
        if note:
            e["note"] = note
        ev.append(e)

    # Flips (the Horace experiment's flip model) and wires (Heat per millimetre).
    # Rates: flips per second in the random fp32 matmul, all 1,024 minions at 600 MHz and 546 cycles per op.
    tr = {r["config"]: r for r in man["tensor"]["rows"]}
    ops = 1024 * op / tr["fp32_randn"]["cycles_per_op"]
    randn = next(r for r in hrep["power_model"]["rows"] if r["values"] == "randn")
    src_h = {"url": PAGES + "et-soc1-horace-experiment#a-model-from-flips-to-temperature", "label": "The Horace experiment, §8"}
    for k, lab in (("bus", "an operand-word bit toggled outside the tensor unit"), ("ffclk", "a register bit clocked in the tensor unit"),
                   ("rest", "a net toggle in the tensor unit, outside the multiplier tree"), ("mult", "a net toggle in the multiplier tree")):
        add("flips", "flip-" + k, lab, "flip", src_h,
            {"any": {"e": [r3sig(model["power"]["e_fJ"][k] * 1e-15)] * 3, "rate": r3sig(randn[k] * 1e6 * ops)}},
            note="fitted flip energy (no pass-to-pass range); rate in the random-normal fp32 matmul")
    # Wires: Heat per millimetre's third run (report.json "wire": the version-3 check's six passes on each of three
    # cards), whose headline gives the free links ("uncontended", link-disjoint flows: wsep/) and the loaded mesh
    # ("loaded", all pairs over 1-6 hops: wu/) per meter. The 24 September runs are report.json "wire_sep24".
    hop_mm = wire["inputs"]["hop_mm"]["value"]
    cf = wire["wire"]["configs"]
    bitmm = lambda pre: max(v["gb_s"] * 8e9 * v["hop_distance"] * hop_mm for k, v in cf.items() if k.startswith(pre))  # noqa: E731
    src_w = {"url": PAGES + "et-soc1-heat-per-mm#ones", "label": "Heat per millimetre, §5"}
    h = wire["headline"]
    add("flips", "wire-free", "a random bit carried 1 mm, free links (mesh rail)", "bit·mm", src_w,
        {"any": {**pooled(h["uncontended/noc_rail"]["random_bit_total"], 1e-15), "rate": r3sig(bitmm("wsep/"))}},
        note="rate: the most bit·mm per second of the link-disjoint runs")
    add("flips", "wire-loaded", "a random bit carried 1 mm, loaded mesh (board power)", "bit·mm", src_w,
        {"any": {**pooled(h["loaded/board"]["random_bit_total"], 1e-15), "rate": r3sig(bitmm("wu/"))}},
        note="rate: the most bit·mm per second of the all-pairs configurations over one to six hops")

    # Tensor multiply-adds (energy manual §3.2), per MAC.
    src_t = {"url": PAGES + "et-soc1-energy-manual#the-tensor-unit-per-multiply-add", "label": "The energy manual, §3.2"}
    bars = man["tensor"]["bars"]
    for p, lab in (("fp32", "a TensorFMA multiply-add, fp32"), ("fp16", "a TensorFMA multiply-add, fp16"), ("int8", "a TensorFMA multiply-add, int8")):
        add("tensor", "tensor-" + p, lab, "MAC", src_t,
            {"random": {**pooled(bars[p + "_randn"], 1e-12), "rate": r3sig(tr[p + "_randn"]["per_s"])},
             "zeros": {**pooled(bars[p + "_zeros"], 1e-12), "rate": r3sig(tr[p + "_zeros"]["per_s"])}})

    # Instructions (energy manual §3.1): the catalogue pooled over both cards; rate from aifoundry2's runs.
    cb, sm = man["catalogue"]["combined"], man["catalogue"]["cards"][CARDS[0]]["summary"]
    src_i = {"url": PAGES + "et-soc1-energy-manual#every-instruction-the-core-executes", "label": "The energy manual, §3.1"}
    for n, lab in (("add", "add"), ("lw", "lw (a load hitting the L1)"), ("sw", "sw"), ("fadd.s", "fadd.s"), ("fmadd.s", "fmadd.s"),
                   ("mul", "mul"), ("fadd.ps", "fadd.ps (8 lanes)"), ("fmadd.ps", "fmadd.ps (8 lanes)"), ("flw.ps", "flw.ps (a 32-byte vector load)"),
                   ("div", "div"), ("fexp.ps", "fexp.ps (8 lanes)")):
        add("instr", "i-" + n, lab, "instruction", src_i,
            {p: {**pooled(cb[f"{n}/{p}/h2"], 1e-12), "rate": r3sig(sm[f"{n}/{p}/h2"]["ops_per_s"]["mean"])} for p in ("random", "zeros")})

    # Bytes by level: the energy manual's reruns (§4.2): since 26 September the version-3 campaign's V3-RL, six passes
    # on each of three cards (reruns.json v3_rl; before, the 23 September rerun directories, reruns.json dirs); rates
    # from the passes' own runs.
    dirs = reruns["dirs"]
    rate = lambda r: r["bytes"] / r["wall_s"] if r.get("bytes") and r.get("wall_s") else None  # noqa: E731
    v3 = reruns.get("v3_rl")
    if v3:
        rl = {**runs_median(v3_rl_dirs(v3, "A"), ".", rate), **runs_median(v3_rl_dirs(v3, "B"), ".", rate)}
        rel = runs_median(v3_rl_dirs(v3, "relay"), ".", rate)
    else:
        rl, rel = runs_median(dirs, "rl-pass*[0-9]", rate), runs_median(dirs, "relay-pass*[0-9]", rate)
    src_l = {"url": PAGES + "et-soc1-energy-manual#reads-by-level", "label": "The energy manual, §4.2"}
    lv, lbc = reruns["levels_pj_per_byte"], reruns.get("levels_by_contents_pj_per_byte") or {}
    # The L1 comes from the catalogue's unrolled 32 B vector loads (§4.1), the figure the manual says to use: memhier's
    # own loop (8 loads per iteration) issues a load every 3.2 cycles instead of 1.4 and reads about 40% higher per byte.
    add("bytes", "b-l1", "a byte read from the L1", "byte", {"url": PAGES + "et-soc1-energy-manual#reads-and-writes-measured-together", "label": "The energy manual, §4.1"},
        {p: {**pooled(cb[f"flw.ps/{p}/h2"], 1e-12 / 32), "rate": r3sig(sm[f"flw.ps/{p}/h2"]["ops_per_s"]["mean"] * 32)} for p in ("random", "zeros")},
        note=f"32-byte vector loads on both harts, the catalogue's unrolled loop; memhier's slower loop reads {lv['l1']['mean']:.2f} pJ/B")
    # The version-3 passes fill the scratchpads with zeros (odd passes) or random data (even) before reading them, so
    # their levels come per contents (levels_by_contents_pj_per_byte); the L2, L3 and DRAM buffers are never set.
    for k, lab in (("l2", "a byte read from the L2"), ("scp-local", "a byte read from the shire's own scratchpad"),
                   ("scp-remote", "a byte read from a scratchpad 16 shires away"), ("l3", "a byte read from the L3"), ("dram", "a byte read from DRAM")):
        if k.startswith("scp-") and all(k in lbc.get(p, {}) for p in ("random", "zeros")):
            add("bytes", "b-" + k, lab, "byte", src_l, {p: {**pooled(lbc[p][k], 1e-12), "rate": r3sig(rl[k])} for p in ("random", "zeros")},
                note="the scratchpad filled with zeros or random data before the reads (the version-3 passes)")
        else:
            add("bytes", "b-" + k, lab, "byte", src_l, {"any": {**pooled(lv[k], 1e-12), "rate": r3sig(rl[k])}},
                note="memory whose contents the probe never set")
    src_rw = {"url": PAGES + "et-soc1-energy-manual#reads-and-writes-measured-together", "label": "The energy manual, §4.1"}
    for n, lab in (("tload/dram", "a byte of a tensor load from DRAM"), ("st_stream/dram", "a byte stored through the L1 to DRAM (the line is read first)")):
        add("bytes", "b-" + n.replace("/", "-"), lab, "byte", src_rw,
            {p: {**pooled(cb[f"{n}/{p}"], 1e-12), "rate": r3sig(sm[f"{n}/{p}"]["bytes_per_s"]["mean"])} for p in ("random", "zeros")})

    # Gathered and scattered elements (energy manual §4.4, E48): one random 4 B element per event, both harts of all
    # 1,024 minions, pooled over every pass of the three cards (manual.json gs, build_energy_manual.py); rate: the chip's
    # element rate in that measurement. "Random" is random lines within 4 KB tiles.
    G = man.get("gs")
    GK = G["configs"] if G else {}

    def gsv(cfg):
        e = GK.get(cfg)
        return {**pooled(e["pj_per_element"], 1e-12), "rate": r3sig(e["elements_per_s"]["mean"])} if e and e.get("pj_per_element") else None
    if G:
        src_g = {"url": PAGES + "et-soc1-energy-manual#irregular-access-gathers-and-scatters-by-level", "label": "The energy manual, §4.4"}
        for k, lab, op, table in (("l1", "a random 4 B element gathered from the L1", "fgw.ps", "dram-512B"),
                                  ("l2", "a random 4 B element gathered from the L2", "fgw.ps", "dram-4K"),
                                  ("scp", "a random 4 B element gathered from the own scratchpad", "fgw.ps", "scp-16K"),
                                  ("dram", "a random 4 B element gathered from DRAM", "fgw.ps", "dram-256K"),
                                  ("s-l1", "a 4 B element scattered into the L1", "fscw.ps", "dram-512B"),
                                  ("s-l2", "a 4 B element scattered into the L2", "fscw.ps", "dram-4K")):
            v = {p: gsv(GL.cfg(op, table, data=p)) for p in ("random", "zeros")}
            v = {p: x for p, x in v.items() if x}
            if "random" in v and "zeros" not in v:
                v = {"any": v["random"]}
            if v:
                add("bytes", "gs-" + k, lab, "element", src_g, v,
                    note=f"`{op}`, eight elements an instruction on random lines within 4 KB tiles, both harts of 1,024 minions (E48, three cards)")


    src_m = {"url": PAGES + "et-soc1-energy-manual#bytes-between-cores-and-shires", "label": "The energy manual, §5"}
    rg = reruns["rings_pj_per_byte"]
    for k, lab in (("pair", "a byte messaged to the other minion of a pair"), ("neigh", "a byte messaged around a neighbourhood"),
                   ("shire", "a byte messaged around a shire"), ("xshire1", "a byte messaged to the next shire by ID")):
        add("msg", "m-" + k, lab, "byte", src_m, {"any": {**pooled(rg[k], 1e-12), "rate": r3sig(rl[k])}})
    src_r = {"url": PAGES + "et-soc1-on-chip-relay#the-same-watts-a-thirtieth-of-the-work", "label": "Hand it to the next shire, §2"}
    for k, lab in (("dram", "a byte relayed through DRAM"), ("hop", "a byte handed to the next shire's scratchpad"), ("scp", "a byte kept in the shire's own scratchpad")):
        add("msg", "r-" + k, lab, "byte", src_r, {"any": {**pooled(reruns["relay_pj_per_byte"][k], 1e-12), "rate": r3sig(rel[k])}})

    # Synchronisation: the hot line's atomics (the 23 September rerun directories; the campaign did not re-run them).
    hot = runs_median(dirs, "hotline-pass*[0-9]", lambda r: r.get("ops_per_s"))
    src_s = {"url": PAGES + "et-soc1-hot-line#what-it-costs-in-energy", "label": "One hot line stops a shire, §6"}
    for k, lab in (("spread", "a global atomic, each shire on its own line"), ("contended", "a global atomic on one contended line")):
        add("sync", "s-" + k, lab, "atomic", src_s, {"any": {**pooled(reruns["hotline_nj_per_op"][k], 1e-9), "rate": r3sig(hot[k])}})

    if G:   # packed atomic adds (energy manual §6, E48): one update per event, random words of shared tables
        src_a = {"url": PAGES + "et-soc1-energy-manual#synchronisation", "label": "The energy manual, §6"}
        for k, lab, op, table in (("famoaddl", "a packed atomic add at the shire's L2 (famoaddl.pi), per lane", "famoaddl.pi", "shire-256K"),
                                  ("famoaddg", "a packed atomic add at the home L3 (famoaddg.pi), per lane", "famoaddg.pi", "chip-8M")):
            x = gsv(GL.cfg(op, table, data="zeros"))
            if x:
                add("sync", "gs-" + k, lab, "update", src_a, {"any": x}, note="random words of a shared table, both harts of 1,024 minions (E48, three cards)")

    fam = [["flips", "Flips and wires", "var(--c7)"], ["tensor", "Tensor multiply-adds", "var(--c1)"], ["instr", "Instructions", "var(--c2)"],
           ["bytes", "Bytes by level", "var(--c3)"], ["msg", "Messages and relay", "var(--c4)"], ["sync", "Synchronisation", "var(--c5)"]]
    return {"families": fam, "events": ev,
            "meter": {**meter(tel), "idle_law_rms_w": r3(model["power"]["rms_idle"])},
            "rate_rule": "the one at which the measurement ran it on all 1,024 minions at 600 MHz: the median launch rate of the "
                         "energy manual's rerun passes (bytes by level, messages and relay: the version-3 campaign's, on three cards; "
                         "atomics: 23 September), the gathers', scatters' and packed atomics' own element rate (E48, pooled over three cards), the catalogue's aifoundry2 runs "
                         "(instructions, byte paths), the tensor rows, the Horace experiment's flip counts, and the heat runs' most "
                         "bit·mm per second (wires)",
            "source": ENERGY_EVENTS_SOURCE}


ENERGY_EVENTS_SOURCE = ("tools/ettelem/sync_hub_data.py from manual.json (its gs block: E48's gathers, scatters and packed atomics), reruns.json and its rerun passes (V3-RL and the 23 September directories), the wire report.json, "
                        "the Horace model.json / report.json, and the version-3 campaign's tel.json (the meter's pass)")


# ---------------------------------------------------------------- the claims check, per page
def card_set(cards):
    """claims[].cards (a word, or card names joined by +, commas or spaces) as a key: card ids in registry order joined
    by '+', or 'none'."""
    ids = []
    for tok in re.split(r"[+,;/\s]+", str(cards or "").strip().lower()):
        for c in CARD_WORDS.get(tok.replace("-", "") if tok.startswith("a1") else tok, [tok]):
            if c not in ids:
                ids.append(c)
    ids.sort(key=lambda c: (CARD_ORDER.index(c) if c in CARD_ORDER else len(CARD_ORDER), c))
    return "+".join(ids) or "none"


def result_items(exp, cache={}):  # noqa: B006  (a per-run cache of the results files)
    """results/<exp>.json of the campaign as {item id: item}."""
    if exp not in cache:
        r = load(os.path.join(CLAIMS_V3, "results", exp + ".json"))
        it = r["items"] if isinstance(r, dict) else r
        if isinstance(it, dict):
            it = [dict(v, item=v.get("item", k)) for k, v in it.items()]
        cache[exp] = {x["item"]: x for x in it}
    return cache[exp]


def item_cards(item, campaign):
    """The campaign's cards an item tested or reported, as its all_cards block records them: the card names that
    appear as keys or list entries anywhere in it (tested, reported, holds, status, per_card, cards, holds_on, ...),
    except under missing / no_data / cards_missing, and never in its free-text fields. An all_cards block that names no
    card falls back to the item's own per_card keys with data."""
    pat = re.compile("|".join(re.escape(c) for c in sorted(campaign, key=len, reverse=True)))
    found = set()

    def walk(o, key=None):
        if key in ("missing", "no_data", "cards_missing"):
            return
        if isinstance(o, dict):
            for k, v in o.items():
                found.update(pat.findall(str(k)))
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                if isinstance(v, str):
                    found.update(pat.findall(v))
                else:
                    walk(v, key)
    walk(item.get("all_cards"))
    if not found:
        for c, v in (item.get("per_card") or {}).items():
            if c in campaign and not (isinstance(v, dict) and v.get("n") == 0):
                found.add(c)
    return found


def v3_overlay(path, campaign):
    """{claim id: (verdict, cards or None, prior cards kept?)} for every claim the campaign tested (V3_ORDER above)."""
    out = {}
    for claims in load(path).values():
        for c in claims:
            got = {v["all_cards"] for v in c["verdicts"]}
            verdict = next((cls for o, cls in V3_ORDER if o in got), None)  # None: REPORTED / DESCRIPTIVE only
            cards = set()
            for v in c["verdicts"]:
                cards |= item_cards(result_items(v["exp"])[v["item"]], campaign)
            out[c["id"]] = (verdict, cards, verdict != "CORRECTED")
    return out


def claims_series(s):
    """One series of the scoreboard: per page, the claims by verdict and by the cards behind them."""
    src = load_any(s["file"])
    over = v3_overlay(s["overlay"], campaign_cards()) if s.get("overlay") else {}
    pages, tested = {}, 0
    for c in src["claims"]:
        p = pages.setdefault(c["page"], {"claims": 0, "verdict": {}, "cards": {}})
        p["claims"] += 1
        v, k = c[s["verdict"]], card_set(c.get("cards"))
        if c["id"] in over:
            tested += 1
            nv, cards, keep = over[c["id"]]
            v = nv or v
            if cards:
                k = card_set("+".join(sorted(cards | (set(k.split("+")) - {"none"} if keep else set()))))
        v = VERDICT_ALIAS.get(v, v)
        p["verdict"][v] = p["verdict"].get(v, 0) + 1
        p["cards"][k] = p["cards"].get(k, 0) + 1
    if over and tested != len(over):
        sys.exit(f"{s['overlay']}: {len(over) - tested} tested claims are not in {s['file']}")
    # The file's own per-page counts, where it has them, must agree with the claims it lists (the plan's own series).
    for slug, cnt in (src.get("counts", {}).get("per_page") or {}).items():
        want = {VERDICT_ALIAS.get(k, k): v for k, v in (cnt.get("effective_verdict_quoted_resolved") or {}).items() if v}
        if s["verdict"] == "effective_verdict" and not over and want and want != pages.get(slug, {}).get("verdict"):
            sys.exit(f"{s['file']}: counts.per_page[{slug}] disagrees with its claims[]")
    order = [v[0] for v in VERDICTS]
    rank = lambda k: (k.count("+") * -1 if k != "none" else 1, [CARD_ORDER.index(c) if c in CARD_ORDER else 9 for c in k.split("+")], k)  # noqa: E731
    for p in pages.values():
        p["verdict"] = {k: p["verdict"][k] for k in sorted(p["verdict"], key=lambda k: (order.index(k) if k in order else len(order), k))}
        p["cards"] = {k: p["cards"][k] for k in sorted(p["cards"], key=rank)}
    src_txt = os.path.relpath(s["file"], ROOT) + f" (claims[].page, .cards, .{s['verdict']})"
    if over:
        src_txt += (f"; {tested} claims the campaign tested take their outcome from " + os.path.relpath(s["overlay"], ROOT) +
                    " (all_cards of each item that tests them, V3_ORDER) and their cards from those items' all_cards blocks")
    return {"id": s["id"], "label": s["label"], "short": s["short"], "note": s["note"], "date": s["date"],
            "source": src_txt, **({"tested": tested} if over else {}), "pages": {k: pages[k] for k in sorted(pages)}}


def claims_status():
    series = [claims_series(s) for s in CLAIM_SERIES]
    seen = {v for s in series for p in s["pages"].values() for v in p["verdict"]}
    extra = sorted(seen - {v[0] for v in VERDICTS})
    return {"verdicts": VERDICTS + [[v, v.lower().replace("-", " "), ""] for v in extra], "series": series,
            "source": "tools/ettelem/sync_hub_data.py claims_status(), from the files in its CLAIM_SERIES"}


# ---------------------------------------------------------------- writing
def dumps(obj, ind=0):
    """json.dumps(indent=1, ensure_ascii=False), except that a list of scalars goes on one line."""
    sp, sp1 = " " * ind, " " * (ind + 1)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        return "{\n" + ",\n".join(f"{sp1}{json.dumps(k, ensure_ascii=False)}: {dumps(v, ind + 1)}" for k, v in obj.items()) + "\n" + sp + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        if all(not isinstance(v, (dict, list)) for v in obj) or all(isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v) for v in obj):
            if all(not isinstance(v, (dict, list)) for v in obj):
                return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "))
            return "[\n" + ",\n".join(sp1 + json.dumps(v, ensure_ascii=False, separators=(", ", ": ")) for v in obj) + "\n" + sp + "]"
        return "[\n" + ",\n".join(sp1 + dumps(v, ind + 1) for v in obj) + "\n" + sp + "]"
    return json.dumps(obj, ensure_ascii=False)


# "meter" is energy_events.meter alone (it reads the campaign's tel.json and the Horace model, not the energy manual):
# --only meter refreshes it while the energy manual's files are being regenerated. Every other name is a whole block.
BLOCKS = ("power", "energy_events", "meter", "claims_status")


def build(hub, only=BLOCKS):
    new = json.loads(json.dumps(hub))
    if "power" in only:
        P = new.setdefault("power", {})
        for k, v in power_blocks(load(FIT), load(CAT), load(DVFS), load(RERUNS)).items():
            P[k] = v
    if "energy_events" in only:
        new["energy_events"] = energy_events(load(MAN), load(RERUNS), load(WIRE), load(os.path.join(HORACE, "model.json")),
                                             load(os.path.join(HORACE, "report.json")), load(TEL_V3))
    elif "meter" in only:
        E = new["energy_events"]
        E["meter"] = {**meter(load(TEL_V3)), "idle_law_rms_w": r3(load(os.path.join(HORACE, "model.json"))["power"]["rms_idle"])}
        E["source"] = ENERGY_EVENTS_SOURCE
    if "claims_status" in only:
        new["claims_status"] = claims_status()
    return new


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the data file differs from what this script would write")
    ap.add_argument("--hub", default=HUB)
    ap.add_argument("--only", default=",".join(BLOCKS), help="comma-separated blocks to rewrite (default: all of " + ", ".join(BLOCKS) +
                    "); the others are kept as they are in the file")
    a = ap.parse_args()
    only = [b for b in a.only.split(",") if b]
    if set(only) - set(BLOCKS):
        sys.exit(f"--only: unknown block(s) {sorted(set(only) - set(BLOCKS))}; known: {', '.join(BLOCKS)}")
    with open(a.hub) as fh:
        text = fh.read()
    hub = json.loads(text)
    new = build(hub, only)
    out = dumps(new) + "\n"
    if a.check:
        if out == text:
            print(f"{os.path.relpath(a.hub, ROOT)}: up to date" + ("" if set(only) == set(BLOCKS) else f" ({', '.join(only)})"))
            return
        stale = [f"power.{k}" for k in new["power"] if new["power"].get(k) != hub.get("power", {}).get(k)]
        stale += [k for k in ("energy_events", "claims_status") if new.get(k) != hub.get(k)]
        sys.exit(f"{os.path.relpath(a.hub, ROOT)} is stale: " + (", ".join(stale) if stale else "formatting only") +
                 "\n  run python3 tools/ettelem/sync_hub_data.py, then rebuild the page")
    with open(a.hub, "w") as fh:
        fh.write(out)
    msg = []
    if "power" in only:
        P = new["power"]
        rms = "/".join("%.3f" % P["fit"][c]["rms_w"] for c in CARDS)
        tau = "/".join(str(P["rail_filter"][c]["tau_s"]) for c in CARDS)
        msg.append(f"fit rms {rms} W, droop {P['droop']['mv_per_dram_offrail_w']:.4f} mV/W, rail filter tau {tau} s ({', '.join(CARDS)})")
    if "energy_events" in only or "meter" in only:
        M = new["energy_events"]["meter"]
        msg.append(f"{len(new['energy_events']['events'])} energy events, SP pass {M['pass_s']}/{M['pass_s_a3']}/{M['pass_s_a1c1']} s sampled")
    if "claims_status" in only:
        msg.append("claims status for " + ", ".join(f"{len(s['pages'])} pages ({s['id']})" for s in new["claims_status"]["series"]))
    print(f"wrote {os.path.relpath(a.hub, ROOT)}: " + "; ".join(msg))


if __name__ == "__main__":
    main()
