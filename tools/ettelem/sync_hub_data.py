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
  energy_events       a selection of the events the reports priced, each with its energy [range] and the rate at which
                      the measurement ran it, for the chart "How many identical events before the meter sees one?"
                      (the energy manual's catalogue, tensor bars and reruns, on three cards since 26 September; the
                      wires from Heat per millimetre's third run; the hot line and the flips as before; since 27
                      September E48's gathered and scattered elements and packed atomic adds, manual.json gs); its meter block
                      takes the board value's refresh and the service processor's pass per card from the
                      version-3 campaign (meter())
  claims_status       the claims check's verdicts per page, and the cards behind each claim, for §1's scoreboard: one
                      series per entry of CLAIM_SERIES (the claims after the campaign of 25-26 Sep, each tested claim
                      with its outcome on the campaign's cards, and the version-3 plan before any campaign run)
  carry               the cycle counter's late carry (§3's figure): the RTL's constants (CARRY_RTL, from rtl-sim/pmu_carry),
                      and per card the version-3 campaign's raw read pairs (MEM-R1: how many pairs 10 cycles apart read
                      128 off) and fixcyc()'s leftover per corrected launch (MEM-R3), from results/mem.json
  pcie                the host link per card (E50, docs/reports/data/2026-09-27-pcie/pcie.json), for the tokens of §1's
                      index row "Over the PCIe link"
  solve_energy        one solve's board energy split by meter, for §4.2's chart "One solve's joules, as the card's meters
                      report them": E59's energy runs (workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/energy/
                      <run>/energy.json, written by workloads/sparseparity/tools/energy_reduce.py), one entry per size
                      (SOLVE_RUNS: L1, L2, and (256,5) as its two halves summed). Per solve: the board's idle over the
                      solve's time (1 / solves_per_s) split into each rail's idle_w and the board's sp_avg_idle_w less
                      the rails' (on no meter); the leakage's rise (board.leak_rise_j_per_solve); each rail over idle
                      (rails.<rail>.j_per_solve) and the rest over idle (rails.unmetered.j_per_solve, the headline less
                      the rails). The parts must add to board.j_per_solve_total within 5 mJ, or the script stops.
                      Beside them, §4.2's fit for the runs' card (unmetered_fit.json coef, no DRAM term: every run
                      staged its operands in the shires' scratchpads, host.json plan.stage "scp", which the script
                      checks) applied to the rails' joules, and per run the same comparison in
                      watts by the catalogue's method (board.catalogue.over_idle_w less the rails' over_idle_w_plateau);
                      and the reducer's stated accuracy (SOLVE_ACC). Numbers only: the energy files also hold build
                      paths and the sampler's command line
  burst_trace         the same E59 runs as time traces through every meter, for §4.1's chart "One sparse parity burst
                      through every meter on the card": one entry per run (BURST_RUNS: L1, L2 and (256,5)'s two halves,
                      each a run of its own). From the run's telemetry.jsonl.gz, every 10 Hz sample from BURST_WINDOW[0]
                      to BURST_WINDOW[1] s after the host's first launch (host.json launch_epoch_ms[0], which must be
                      energy.json's window.lo_ms), kept only where one of BURST_COLS' readings differs from the sample
                      before it, plus the window's last sample: [t_s, board_w, sp.board_avg_w, sp.minion_w[0],
                      sp.sram_w[0], sp.noc_w[0], temp_c.minshire[0]]. Beside them, from host.json the solves' own times
                      (launch_s) and from energy.json the burst's length (window.wall_s), the board's edges against the
                      host's (window.board_edges_minus_host_s), the catalogue method's idle and busy board means and its
                      count of busy board values at idle (board.catalogue.busy_readings, busy_readings_at_idle and its
                      expected number), and each meter's step (levels: board_w from the catalogue's idle_before_w to its
                      busy_w; sp.board_avg_w from board.sp_avg_idle_w by the same step, the average having unit gain; each
                      rail from rails.<rail>.idle_w by its over_idle_w_plateau). rise is each meter's reading as sampled
                      1 s and 2 s after the board's first edge, as a share of that step (BURST_RISE_S), the last sample
                      at or before each time. Numbers only, as for solve_energy
  energy_plane        the points §2's energy-rate plane (the second view of "How many identical events before the meter
                      sees one?", "Every priced event sits on a few watts") draws beside energy_events' events, each as an
                      energy per event and the rate it ran at, so energy x rate is the power it lifted the board by:
                      .gs, every E48 configuration in manual.json gs.configs (set E: the chip-wide runs) with both
                      pj_per_element and elements_per_s, as [config less its "gs/E/", J mean, lo, hi, per second], with
                      words for its tables (gs_levels.LEVELS' labels, else the size per hart) and patterns
                      (gs_levels.PATTERNS), the ops that count updates, not elements (update_ops), and each
                      configuration measured on fewer than three cards with the cards it was (fewer_cards: E48's clock
                      rule dropped the others' bursts); .minion, one minion's word gathers from the L1 (PLANE_MINION: set R's
                      single-minion rate, both harts, measured; the chip's energy per element, borrowed: one minion's
                      lift is below the meter); .workloads, E59 as one solve, one candidate scored and one executed int8
                      multiply-add per size (SOLVE_RUNS, (256,5)'s halves summed): a solve's board joules over idle
                      (board.j_per_solve) and the solve rate (1 / the summed 1 / solves_per_s), divided by plan.candidates
                      (which must sum to C(n, k)) or by plan.ops x PLANE_MACS_PER_OP (16 x 16 x 64 per TensorIMA8A32).
                      The page computes each point's power and draws the meter's lines from energy_events.meter

Deterministic: the same inputs give the same file, byte for byte.
"""
import argparse
import glob
import gzip
import json
import math
import os
import re
import statistics
import subprocess
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
# steps and the rails in 1 mW, a new value per service-processor pass. The refresh comes from meter(), below.
LSB = {"board_lsb_w": 0.010, "rail_lsb_w": 0.001}
CLAIMS_V3 = os.path.join(D, "2026-09-25-claims-v3")
TEL_V3 = os.path.join(CLAIMS_V3, "results", "tel.json")
MEM_V3 = os.path.join(CLAIMS_V3, "results", "mem.json")
PCIE = os.path.join(D, "2026-09-27-pcie", "pcie.json")
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
    """One reading of the meter: its steps (LSB), how often a new board value arrives, and the service processor's
    pass per card, from the version-3 campaign's V3-TEL (E41, results/tel.json), three passes per card.
      - The board value's refresh (TEL-S, found by phase-folding the board-power stream): under ettelem at 10 Hz (P_H),
        as every power page sampled, and under a light one-command poller (P_L). pass_s, pass_s_a3 and pass_s_a1c1
        are P_H's means over the passes (as the power page and the energy manual state it): pass_s sets one reading's
        energy step. board_refresh_ms keeps every pass.
      - The SP stats trace's own pass interval with no sampler running (the quiet arm, Q) and while ettelem samples at
        10 Hz (the E10 arm): TEL-P1 and TEL-P3 give them for aifoundry2 (tested) and aifoundry1-c1 (reported), TEL-P5
        for aifoundry3 (tested) and again for aifoundry1-c1 (the two must agree). sp_pass_ms keeps every pass, the
        sp_pass_s_* keys the medians. The trace's pass under the sampler runs 3-5 ms longer than the refresh the
        stream shows (the two methods differ)."""
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
    ref = {c: {"sampler_10hz_ms": [p["P_H"] for p in v["passes"]], "light_poller_ms": [p["P_L"] for p in v["passes"]]}
           for c, v in it["TEL-S"]["per_card"].items() if v.get("passes")}
    ref = {c: ref[c] for c in sorted(ref, key=lambda c: (CARD_ORDER.index(c) if c in CARD_ORDER else len(CARD_ORDER), c))}
    b = lambda c: r3(statistics.fmean(ref[c]["sampler_10hz_ms"]) / 1000)  # noqa: E731
    return {**LSB, "pass_s": b("aifoundry2"), "pass_s_a3": b("aifoundry3"), "pass_s_a1c1": b("aifoundry1-c1"),
            "board_refresh_ms": ref,
            "sp_pass_s_sampled_a2": s("aifoundry2", "sampled_ms"), "sp_pass_s_sampled_a3": s("aifoundry3", "sampled_ms"),
            "sp_pass_s_sampled_a1c1": s("aifoundry1-c1", "sampled_ms"), "sp_pass_s_quiet_a2": s("aifoundry2", "quiet_ms"),
            "sp_pass_s_quiet_a3": s("aifoundry3", "quiet_ms"), "sp_pass_s_quiet_a1c1": s("aifoundry1-c1", "quiet_ms"),
            "sp_pass_ms": per,
            "source": "results/tel.json of the version-3 campaign: the board value's refresh (TEL-S, phase-folding the "
                      "board-power stream, per pass, under ettelem at 10 Hz and a light poller; pass_s* are the means over "
                      "the passes), and the SP stats trace's own pass (TEL-P1, TEL-P3, TEL-P5, per pass, quiet and under "
                      "ettelem at 10 Hz; sp_pass_s* are the medians over the passes)"}


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
    src_r = {"url": PAGES + "et-soc1-on-chip-relay#power-within-a-watt-a-thirtieth-of-the-work", "label": "Hand it to the next shire, §2"}
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
                        "the Horace model.json / report.json, and the version-3 campaign's tel.json (the meter's refresh and the SP's pass)")


# ---------------------------------------------------------------- the host link (E50), for §1's index row
def card_order(cards):
    return sorted(cards, key=lambda c: (CARD_ORDER.index(c) if c in CARD_ORDER else len(CARD_ORDER), c))


def pcie_block(p):
    """E50 on each card (docs/reports/data/2026-09-27-pcie/pcie.json, the PCIe page's data): the largest copy's rate
    (256 MB) host to card and back with the DMA alone, host to card as a program copies it (staged), an empty kernel on
    32 shires launched and waited for and each queued, and two host-to-card DMA commands in flight over one. Each value
    is the mean over the card's five runs (reduce_pcie.py). The index row "Over the PCIe link" quotes them as tokens."""
    top = lambda rows: max(rows, key=lambda r: r["bytes"])  # noqa: E731
    per = {}
    for c in card_order(p["cards"]):
        bw = p["bw"][c]
        per[c] = {"h2d_dma_gbs": r3(top(bw["h2d"]["dma"])["gbs"]["mean"]), "d2h_dma_gbs": r3(top(bw["d2h"]["dma"])["gbs"]["mean"]),
                  "h2d_staged_gbs": r3(top(bw["h2d"]["staged"])["gbs"]["mean"]),
                  "launch_wait_us": r3(p["launch"][c]["single_us"]["32"]["mean"]), "launch_queued_us": r3(p["launch"][c]["b2b_us"]["32"]["mean"]),
                  "two_h2d_over_one": r3(p["derived"][c]["h2d_two_in_flight_over_one"]["mean"])}
    return {"link_gbs": r3(p["meta"]["link_gbs"]), "bytes": top(p["bw"][p["cards"][0]]["h2d"]["dma"])["bytes"], "per_card": per,
            "source": os.path.relpath(PCIE, ROOT) + " (E50): bw.<card>.{h2d,d2h}.{dma,staged}[largest].gbs.mean, "
                      "launch.<card>.single_us['32'] and b2b_us['32'], derived.<card>.h2d_two_in_flight_over_one; means over five runs"}


# ---------------------------------------------------------------- one solve's joules, by meter (§4.2, E59)
# E59's energy session on aifoundry3 (29 September; workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/README.md):
# one run per size; (256,5) ran as two halves (slices 0/2 and 1/2) whose per-solve energies add, as energy_reduce.py
# combine adds them into aifoundry3-1136-f5.json. [id, label, runs] (the size, (n, k, eta, m), is read from each run's
# energy.json instance)
SOLVE_DIR = os.path.join(ROOT, "workloads", "sparseparity", "data", "2026-09-29-aifoundry3-m5-energy", "energy")
SOLVE_RUNS = [("l1", "L1", ["aifoundry3-1136-l1"]), ("l2", "L2", ["aifoundry3-1136-l2"]),
              ("f5", "(256,5)", ["aifoundry3-1136-f5h0", "aifoundry3-1136-f5h1"])]
SOLVE_RAILS = (("minion", "minion_w"), ("sram", "sram_w"), ("noc", "noc_w"))
# energy_reduce.py's stated accuracy (its docstring, and the TRUTH tolerances its --dry runs on two test doubles passed;
# workloads/sparseparity/README.md, "Dry tests"): the board over idle (the headline) +-3%; each rail -2% to +7% (upper
# bounds: integrated above a ramp baseline, each keeps part of its own leakage's rise); the part on no meter +-15%, in
# test doubles whose part on no meter was 24-25% of what a solve adds (workloads/sparseparity/tools/energy_stub.py
# rail_share: 1 - 0.75, 1 - 0.76).
SOLVE_ACC = {"board": 0.03, "rails": [-0.02, 0.07], "unmetered": 0.15, "stub_unmetered_share": [0.24, 0.25],
             "source": "workloads/sparseparity/tools/energy_reduce.py docstring; workloads/sparseparity/tools/energy_stub.py rail_share"}


def r4(v):
    return round(float(v), 4)


def solve_energy(fit):
    """E59's four energy runs as one solve per size, by meter (see the module docstring). Every joule is per solve;
    a size made of halves sums them (its time per solve too). Deterministic: the files are read in SOLVE_RUNS order."""
    sizes, cards, mhz = [], set(), set()
    for sid, label, runs in SOLVE_RUNS:
        j = {k: 0.0 for k in ("idle_minion", "idle_sram", "idle_noc", "idle_off", "leak", "minion", "sram", "noc", "off")}
        total = over = s_per = 0.0
        inst, rr = None, []
        for run in runs:
            e, h = load(os.path.join(SOLVE_DIR, run, "energy.json")), load(os.path.join(SOLVE_DIR, run, "host.json"))
            if not e.get("ok") or e["host"]["status"] != "PASS":
                sys.exit(f"{run}: energy.json is not ok, or its host did not PASS")
            if h["plan"]["stage"] != "scp":  # the fit's DRAM term is left out only while the operands stay on chip
                sys.exit(f"{run}: staged in {h['plan']['stage']}, not the scratchpad: the fit's DRAM term would be needed")
            b, r, sps = e["board"], e["rails"], e["solves_per_s"]
            cards.add(e["run"]["card"]); mhz.update(e["meter"]["minion_mhz_busy"])
            i = e["instance"]
            if inst and inst != i["hash"]:
                sys.exit(f"{label}: its runs are not one instance")
            inst = i["hash"]
            size = [i["n"], i["k"], i["eta"], i["m"]]
            rail_idle = sum(r[k]["idle_w"] for _, k in SOLVE_RAILS)
            parts = {**{"idle_" + n: r[k]["idle_w"] / sps for n, k in SOLVE_RAILS},
                     "idle_off": (b["sp_avg_idle_w"] - rail_idle) / sps, "leak": b["leak_rise_j_per_solve"],
                     **{n: r[k]["j_per_solve"] for n, k in SOLVE_RAILS}, "off": r["unmetered"]["j_per_solve"]}
            if abs(sum(parts.values()) - b["j_per_solve_total"]) > 0.005:
                sys.exit(f"{run}: the parts add to {sum(parts.values()):.4f} J, board.j_per_solve_total is {b['j_per_solve_total']:.4f} J")
            for k, v in parts.items():
                j[k] += v
            total += b["j_per_solve_total"]; over += b["j_per_solve"]; s_per += 1 / sps
            c = b["catalogue"]
            plat = {n: r[k]["over_idle_w_plateau"] for n, k in SOLVE_RAILS}
            rr.append({"run": run.split("-")[-1], "solves": e["solves"], "stage": h["plan"]["stage"], "solves_per_s": r4(sps), "board_idle_w": r3(b["sp_avg_idle_w"]),
                       "rails_idle_w": r3(rail_idle), "die_c": [r3(e["die_c"]["before"]), r3(e["die_c"]["busy"])],
                       "w": {"over": r3(c["over_idle_w"]), "rails": r3(sum(plat.values())), "off": r3(c["over_idle_w"] - sum(plat.values())),
                             "fit_off": None}, "_plat": plat})
        sizes.append({"id": sid, "label": label, "size": size, "s_per_solve": r4(s_per), "total": r4(total), "over": r4(over),
                      "j": {k: r4(v) for k, v in j.items()}, "runs": rr})
    if len(cards) != 1:
        sys.exit(f"E59's energy runs are on {sorted(cards)}: one card expected")
    card = cards.pop()
    coef = fit[card]["coef"]
    lin = lambda d: sum(coef[n] * d[n] for n, _ in SOLVE_RAILS)  # noqa: E731  the fit without its DRAM term
    for s in sizes:
        s["fit_off"] = r4(lin(s["j"]))
        for x in s["runs"]:
            x["w"]["fit_off"] = r3(lin(x.pop("_plat")))
    return {"experiment": "E59", "date": "2026-09-29", "card": card, "mhz": sorted(mhz), "acc": SOLVE_ACC, "sizes": sizes,
            "source": os.path.relpath(SOLVE_DIR, ROOT) + "/<run>/energy.json (" + ", ".join(r for _, _, rs in SOLVE_RUNS for r in rs) +
                      "): solves_per_s, board.{sp_avg_idle_w, leak_rise_j_per_solve, j_per_solve, j_per_solve_total}, "
                      "rails.<rail>.{idle_w, j_per_solve, over_idle_w_plateau}, rails.unmetered.j_per_solve, "
                      "board.catalogue.over_idle_w; host.json plan.stage; the fit: " + os.path.relpath(FIT, ROOT) + " <card>.coef (minion, sram, noc)"}


# ---------------------------------------------------------------- one burst through every meter (§4.1, E59)
# The same session's four runs, each on its own (the two halves of (256,5) were two bursts). [id, label, run]
BURST_RUNS = [("l1", "L1", "aifoundry3-1136-l1"), ("l2", "L2", "aifoundry3-1136-l2"),
              ("f5h0", "(256,5), first half", "aifoundry3-1136-f5h0"), ("f5h1", "(256,5), second half", "aifoundry3-1136-f5h1")]
BURST_WINDOW = (-4.0, 10.0)   # seconds from the host's first launch: the idle before, the burst, the rails' fall after
BURST_COLS = ["t_s", "board_w", "board_avg_w", "minion_w", "sram_w", "noc_w", "die_c"]
BURST_RISE_S = (1.0, 2.0)     # after the board's first edge: the rail_filter block's times, for the same comparison


def burst_trace():
    """E59's runs as time traces through every meter (see the module docstring). Deterministic: the runs in BURST_RUNS
    order, the samples in the telemetry's order."""
    runs, cards, mhz, hz = [], set(), set(), set()
    for sid, label, run in BURST_RUNS:
        d = os.path.join(SOLVE_DIR, run)
        e, h = load(os.path.join(d, "energy.json")), load(os.path.join(d, "host.json"))
        if not e.get("ok") or e["host"]["status"] != "PASS":
            sys.exit(f"{run}: energy.json is not ok, or its host did not PASS")
        lo, hi = h["launch_epoch_ms"]
        if e["window"]["lo_ms"] != lo or e["window"]["hi_ms"] != hi:
            sys.exit(f"{run}: energy.json's window is not the host's launch_epoch_ms")
        cards.add(e["run"]["card"]); mhz.update(e["meter"]["minion_mhz_busy"]); hz.add(round(1000 / e["run"]["every_ms"], 3))
        with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") as fh:
            tel = [json.loads(l) for l in fh if l.startswith("{")]
        rows, last = [], None
        for s in tel:
            if "board_w" not in s or "sp" not in s or "temp_c" not in s:
                continue
            t = (s["t_ms"] - lo) / 1000
            if not BURST_WINDOW[0] <= t <= BURST_WINDOW[1]:
                continue
            sp = s["sp"]
            row = [round(t, 3), s["board_w"], sp["board_avg_w"], sp["minion_w"][0], sp["sram_w"][0], sp["noc_w"][0], s["temp_c"]["minshire"][0]]
            if not rows or row[1:] != rows[-1][1:]:
                rows.append(row)
            last = row
        if last is not None and rows[-1] is not last:
            rows.append(last)  # the lines run to the window's end
        b, c, r = e["board"], e["board"]["catalogue"], e["rails"]
        step_b = c["busy_w"] - c["idle_before_w"]
        levels = {"board_w": [c["idle_before_w"], c["busy_w"]], "board_avg_w": [b["sp_avg_idle_w"], b["sp_avg_idle_w"] + step_b],
                  **{k: [r[k]["idle_w"], r[k]["idle_w"] + r[k]["over_idle_w_plateau"]] for k in ("minion_w", "sram_w", "noc_w")}}
        edge = e["window"]["board_edges_minus_host_s"]
        rise = {}
        for k, (i0, i1) in levels.items():
            col = BURST_COLS.index(k)
            at = [next((x[col] for x in reversed(rows) if x[0] <= edge[0] + dt), None) for dt in BURST_RISE_S]
            rise[k] = [r3((v - i0) / (i1 - i0)) for v in at]
        runs.append({"id": sid, "label": label, "size": [e["instance"][k] for k in ("n", "k", "eta", "m")], "slice": e["slice"],
                     "solves": e["solves"], "wall_s": r3(e["window"]["wall_s"]), "launch_s": [r4(x) for x in h["launch_s"]],
                     "edges_s": [r3(x) for x in edge], "die_c": [r3(e["die_c"]["before"]), r3(e["die_c"]["busy"])],
                     "levels": {k: [r3(v[0]), r3(v[1])] for k, v in levels.items()}, "rise": rise,
                     "busy_readings": c["busy_readings"], "at_idle": c["busy_readings_at_idle"],
                     "at_idle_expected": r4(c["busy_readings_at_idle_expected"]), "cat_idle_w": r3(c["idle_w"]), "cat_busy_w": r3(c["busy_w"]),
                     "busy_from_s": b["windows_s"]["busy"][0], "samples": rows})
    if len(cards) != 1 or len(hz) != 1:
        sys.exit(f"E59's energy runs: cards {sorted(cards)}, sampler rates {sorted(hz)}: one of each expected")
    return {"experiment": "E59", "date": "2026-09-29", "card": cards.pop(), "mhz": sorted(mhz), "sampler_hz": hz.pop(),
            "window_s": list(BURST_WINDOW), "rise_s": list(BURST_RISE_S), "cols": BURST_COLS, "runs": runs,
            "source": os.path.relpath(SOLVE_DIR, ROOT) + "/<run>/ (" + ", ".join(r for _, _, r in BURST_RUNS) + "): telemetry.jsonl.gz "
                      "(t_ms, board_w, sp.board_avg_w, sp.{minion,sram,noc}_w[0], temp_c.minshire[0]); host.json launch_epoch_ms, launch_s; "
                      "energy.json window.{lo_ms, hi_ms, wall_s, board_edges_minus_host_s}, board.{sp_avg_idle_w, windows_s.busy}, "
                      "board.catalogue.{idle_w, idle_before_w, busy_w, busy_readings, busy_readings_at_idle, busy_readings_at_idle_expected}, "
                      "rails.<rail>.{idle_w, over_idle_w_plateau}, instance, slice, solves, die_c"}


# ---------------------------------------------------------------- the energy-rate plane (§2's second view of the events)
# One TensorIMA8A32 multiplies 16 rows by 16 columns over 64 samples (03-experiments.md, E59 "Method";
# workloads/sparseparity/kernel/sparseparity.c ima8_word: 16 A rows x 64 int8 x 16 B columns): 16,384 int8
# multiply-adds an op, padding and masked candidates included (each output tile is ceil(m / 64) ops).
PLANE_MACS_PER_OP = 16 * 16 * 64
# E48's single-minion rate for the one-minion marker (both harts, the L1 table) and the chip's configuration whose
# energy per element it borrows: one minion's energy per element was not measured (its lift is far below the meter).
PLANE_MINION = ("gs/R/fgw.ps/dram-512B/rand/random/h2/mff/nM1", "gs/E/fgw.ps/dram-512B/rand/random/h2/mff/n1024")
# Words for E48's tables (the label of gs_levels.LEVELS where the table is one of its levels, else its size per hart),
# patterns (gs_levels.PATTERNS) and the one op that is not an instruction ("upd", gs_levels.UPDATES).
PLANE_TABLES_EXTRA = {"shire-256K": "a 256 KB table shared by the shire (at its L2)",
                      "chip-8M": "one 8 MB table for the chip (at the home L3 slices)"}


def plane_table_words(table):
    for _key, label, words, _stream, cols in GL.LEVELS:
        if any(t == table for _op, t in cols.values()):
            return f"{label}: {words}"
    if table in PLANE_TABLES_EXTRA:
        return PLANE_TABLES_EXTRA[table]
    m = re.match(r"dram-(\d+)([BKM])$", table)
    if not m:
        sys.exit(f"energy_plane: no words for E48's table {table}")
    return f"{m.group(1)} {'B' if m.group(2) == 'B' else m.group(2) + 'B'} per hart"


def energy_plane(man):
    """The points that §2's energy-rate plane draws beside energy_events (see the module docstring). Deterministic: E48's
    configurations in manual.json's key order, E59's sizes in SOLVE_RUNS order."""
    G = man["gs"]["configs"]
    rows, tables, pats, upd_ops, fewer = [], {}, dict(GL.PATTERNS), set(), {}
    for name, v in G.items():
        if not name.startswith("gs/E/") or not v.get("pj_per_element") or not v.get("elements_per_s"):
            continue
        if v["unit"] not in ("element", "update"):
            sys.exit(f"energy_plane: {name} counts {v['unit']}s")
        if v["unit"] == "update":
            upd_ops.add(v["op"])
        p, r = v["pj_per_element"], v["elements_per_s"]["mean"]
        if p["cards"] < 3:
            # E48's clock rule dropped every energy burst of it on the other cards (05-claims.md, E48 "A gap")
            fewer[name[len("gs/E/"):]] = sorted(p["per_card"])
        rows.append([name[len("gs/E/"):], r3sig(p["mean"] * 1e-12), r3sig(p["lo"] * 1e-12), r3sig(p["hi"] * 1e-12), r3sig(r)])
        tables.setdefault(v["table"], plane_table_words(v["table"]))
        if v["index"] not in pats:
            sys.exit(f"energy_plane: no words for E48's pattern {v['index']}")
    used = {n.split("/")[2] for n, *_ in rows}
    gs = {"experiment": "E48", "fields": ["config", "e_j", "lo_j", "hi_j", "per_s"], "rows": rows,
          "tables": dict(sorted(tables.items())), "patterns": {k: w for k, w in GL.PATTERNS if k in used},
          "upd": "gather + fadd.ps + scatter", "update_ops": sorted(upd_ops),
          "fewer_cards": fewer,
          "source": "manual.json gs.configs[gs/E/<config>]: pj_per_element.{mean, lo, hi} (x 1e-12) and elements_per_s.mean, "
                    "every gs/E configuration with both; pooled over three passes on each of three cards (E48), except "
                    "the configurations in fewer_cards, measured on the cards it names (pj_per_element.per_card)"}
    mr, me = G[PLANE_MINION[0]], G[PLANE_MINION[1]]
    minion = {"rate_config": PLANE_MINION[0][len("gs/"):], "e_config": PLANE_MINION[1][len("gs/"):],
              "per_s": r3sig(mr["elements_per_s"]["mean"]), "e_j": r3sig(me["pj_per_element"]["mean"] * 1e-12),
              "chip_per_s": r3sig(me["elements_per_s"]["mean"]),
              "source": f"manual.json gs.configs[{PLANE_MINION[0]}].elements_per_s.mean (one minion, both harts, measured) and "
                        f"[{PLANE_MINION[1]}].pj_per_element.mean (the chip's, assumed to hold for one minion)"}
    minion["w"] = r3sig(minion["per_s"] * minion["e_j"])
    sizes, cards = [], set()
    for sid, label, runs in SOLVE_RUNS:
        ops = cand = 0
        j = s_per = 0.0
        size = None
        for run in runs:
            e = load(os.path.join(SOLVE_DIR, run, "energy.json"))
            if not e.get("ok") or e["host"]["status"] != "PASS":
                sys.exit(f"{run}: energy.json is not ok, or its host did not PASS")
            i = e["instance"]
            size = [i["n"], i["k"], i["eta"], i["m"]]
            cards.add(e["run"]["card"])
            ops += e["plan"]["ops"]; cand += e["plan"]["candidates"]
            j += e["board"]["j_per_solve"]; s_per += 1 / e["solves_per_s"]
        if cand != math.comb(size[0], size[1]):
            sys.exit(f"{label}: its runs score {cand} candidates, not C({size[0]}, {size[1]})")
        sps, macs = 1 / s_per, ops * PLANE_MACS_PER_OP
        sizes.append({"id": sid, "label": label, "size": size, "ops": ops, "candidates": cand, "macs": macs,
                      "j_per_solve": r4(j), "solves_per_s": r4(sps), "w": r3(j * sps),
                      "per": {"solve": [r3sig(j), r3sig(sps)], "candidate": [r3sig(j / cand), r3sig(cand * sps)],
                              "mac": [r3sig(j / macs), r3sig(macs * sps)]}})
    if len(cards) != 1:
        sys.exit(f"E59's energy runs are on {sorted(cards)}: one card expected")
    work = {"experiment": "E59", "card": cards.pop(), "macs_per_op": PLANE_MACS_PER_OP, "sizes": sizes,
            "source": os.path.relpath(SOLVE_DIR, ROOT) + "/<run>/energy.json: board.j_per_solve (over idle) and 1 / solves_per_s, "
                      "summed over a size's runs ((256,5)'s two halves); plan.ops (TensorIMA8A32 ops) and plan.candidates, summed; "
                      "a solve's joules over idle divided by its candidates, or by its ops x 16,384 multiply-adds"}
    return {"gs": gs, "minion": minion, "workloads": work}


# ---------------------------------------------------------------- the cycle counter's late carry (§3's figure)
# The RTL's constants (E2: rtl-sim/pmu_carry runs core-et's neigh_pmu.v unmodified under Verilator; its README.md):
# twelve counters per neighbourhood share one adder, each a 7-bit pre-counter and a 57-bit post-counter; the adder's
# index advances one counter a cycle while any carry is pending and stops just past the counter it served, so in the
# simulation a read comes back 128 short for 12 cycles after each wrap (low bits 0-11). On aifoundry2's card on 19
# September the short window covered at least low bits 0-10 in one launch and 0-9 in the other (E1, E2);
# fixcyc() (workloads/memprobe/kernel/memprobe.c) assumes 0-10: it adds 128 to a read whose low 7 bits are below 11.
# card_short_reads_19sep is that window's length per launch, at least: [11, 10].
CARRY_RTL = {"counters": 12, "pre_bits": 7, "post_bits": 57, "sim_short_reads": 12, "card_short_reads_19sep": [11, 10], "fixcyc_below": 11,
             "source": "rtl-sim/pmu_carry (E2; README.md: 12 counters, a 7-bit pre-counter and a 57-bit post-counter each, one shared "
                       "adder whose index cnt_idx advances while any carry is pending; 12 short reads per wrap in simulation); on "
                       "aifoundry2's card at least low bits 0-10 in one launch and 0-9 in the other (E1, E2; 19 September); fixcyc() "
                       "in workloads/memprobe/kernel/memprobe.c adds 128 below 11"}


def carry_block(mem):
    """The version-3 campaign's test of the late carry on every card (E35, results/mem.json): MEM-R1's raw read pairs
    10 cycles apart (every t_raw and t_rawodd launch: how many pairs differ by 10, 138 and -118), and MEM-R3's corrected
    stamps (every t_glitch launch: the share of 10-cycle intervals that fixcyc() leaves off by 128, and the window's
    last short value e where one fits)."""
    items = mem if isinstance(mem, list) else mem["items"]
    it = {x["item"]: x for x in items} if isinstance(items, list) else items
    r1, r3_ = it["MEM-R1"], it["MEM-R3"]
    per = {}
    for c in card_order(set(r1["per_card"]) & set(r3_["per_card"])):
        v1, v3 = r1["per_card"][c], r3_["per_card"][c]
        raw = []
        for k in sorted(v1.get("diffs") or {}):
            d = {int(x): n for x, n in v1["diffs"][k].items()}
            gap = max(d, key=d.get)  # the pairs' spacing: the difference most pairs read
            raw.append({"launch": k, "pairs": sum(d.values()), "gap": gap, "plus": sum(n for x, n in d.items() if x > gap),
                        "minus": sum(n for x, n in d.items() if x < gap)})
        fixed = [{"launch": k, "e": v.get("e"), "frac": v.get("off128_frac")} for k, v in sorted((v3.get("launches") or {}).items())]
        nofit = sum(1 for x in v1.get("exceptions", []) if "no single window" in x)
        per[c] = {"raw": raw, "fixed": fixed, "raw_launches_no_window": nofit}
    return {"rtl": CARRY_RTL, "per_card": per,
            "outcome": {"MEM-R1": r1.get("all_cards", {}).get("outcome"), "MEM-R3": r3_.get("all_cards", {}).get("outcome")},
            "source": os.path.relpath(MEM_V3, ROOT) + ": [item=MEM-R1].per_card.<card>.diffs and .exceptions, "
                      "[item=MEM-R3].per_card.<card>.launches (E35); the RTL constants: CARRY_RTL in tools/ettelem/sync_hub_data.py"}


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
        if c["id"] in over:   # the claims the campaign tested, by the same rule: what each page's own note counts
            t = p.setdefault("tested", {})
            t[v] = t.get(v, 0) + 1
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
        if "tested" in p:
            p["tested"] = {k: p["tested"][k] for k in sorted(p["tested"], key=lambda k: (order.index(k) if k in order else len(order), k))}
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
BLOCKS = ("power", "energy_events", "meter", "claims_status", "carry", "pcie", "solve_energy", "burst_trace", "energy_plane")


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
    if "carry" in only:
        new["carry"] = carry_block(load(MEM_V3))
    if "pcie" in only:
        new["pcie"] = pcie_block(load(PCIE))
    if "solve_energy" in only:
        new["solve_energy"] = solve_energy(load(FIT))
    if "burst_trace" in only:
        new["burst_trace"] = burst_trace()
    if "energy_plane" in only:
        new["energy_plane"] = energy_plane(load(MAN))
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
    # Each index row's v3_note (hand-kept: the counts the page's own "Checked on three cards" note gives, by the page's
    # reading) must cover exactly the claims the campaign tested on that page, which the scoreboard counts by V3_ORDER.
    after = next((s_ for s_ in new.get("claims_status", {}).get("series", []) if s_.get("tested")), None)
    for r in new.get("reports", []):
        slug = r["url"].split("#")[0].rstrip("/").split("/")[-1]
        if r.get("v3_note") and after:
            got, want = sum(n for n, _ in r["v3_note"]), sum(after["pages"].get(slug, {}).get("tested", {}).values())
            if got != want:
                sys.exit(f"{os.path.relpath(a.hub, ROOT)}: reports[{slug}].v3_note counts {got} claims; the campaign tested {want} there")
    if a.check:
        if out == text:
            print(f"{os.path.relpath(a.hub, ROOT)}: up to date" + ("" if set(only) == set(BLOCKS) else f" ({', '.join(only)})"), flush=True)
            # the pages' "Checked on three cards" notes carry counts from this file (v3_counts.py): stale notes fail too
            rc = subprocess.run([sys.executable, os.path.join(ROOT, "tools/ettelem/v3_counts.py"), "--check",
                                 "--hub", a.hub]).returncode
            if rc:
                sys.exit("  the page notes' counts are stale: run python3 tools/ettelem/v3_counts.py, then rebuild those pages")
            return
        stale = [f"power.{k}" for k in new["power"] if new["power"].get(k) != hub.get("power", {}).get(k)]
        stale += [k for k in ("energy_events", "claims_status", "carry", "pcie", "solve_energy", "burst_trace", "energy_plane") if new.get(k) != hub.get(k)]
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
        msg.append(f"{len(new['energy_events']['events'])} energy events, board refresh {M['pass_s']}/{M['pass_s_a3']}/{M['pass_s_a1c1']} s sampled")
    if "carry" in only:
        msg.append("the late carry on " + ", ".join(new["carry"]["per_card"]))
    if "pcie" in only:
        msg.append("the host link on " + ", ".join(new["pcie"]["per_card"]))
    if "solve_energy" in only:
        SE = new["solve_energy"]
        msg.append(f"one solve's joules ({SE['experiment']}, {SE['card']}): " + ", ".join(
            f"{s['label']} {s['total']:.2f} J, off-meter over idle {s['j']['off']:.3f} J against the fit's {s['fit_off']:.3f}" for s in SE["sizes"]))
    if "burst_trace" in only:
        BT = new["burst_trace"]
        msg.append(f"one burst through every meter ({BT['experiment']}, {BT['card']}): " + ", ".join(
            f"{x['label']} {len(x['samples'])} samples, minion rail {x['rise']['minion_w'][0]:.2f}/{x['rise']['minion_w'][1]:.2f} of its step at 1/2 s" for x in BT["runs"]))
    if "energy_plane" in only:
        EP = new["energy_plane"]
        lifts = sorted(r[1] * r[4] for r in EP["gs"]["rows"])
        msg.append(f"the energy-rate plane: E48's {len(lifts)} configurations at {lifts[0]:.2f}-{lifts[-1]:.2f} W, one minion's gathers "
                   f"{1e3 * EP['minion']['w']:.1f} mW; E59 " + ", ".join(f"{s['label']} {s['w']:.2f} W ({s['per']['mac'][0] * 1e12:.3f} pJ a MAC)"
                                                                     for s in EP["workloads"]["sizes"]))
    if "claims_status" in only:
        msg.append("claims status for " + ", ".join(f"{len(s['pages'])} pages ({s['id']})" for s in new["claims_status"]["series"]))
    print(f"wrote {os.path.relpath(a.hub, ROOT)}: " + "; ".join(msg))
    print("next: python3 tools/ettelem/v3_counts.py (the page notes' counts), then the page builds")


if __name__ == "__main__":
    main()
