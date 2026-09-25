#!/usr/bin/env python3
"""Write the computed blocks of the observability hub's data file from the analyses that produce them.

    python3 tools/ettelem/sync_hub_data.py            # rewrite docs/reports/sources/limits-of-observability.data.json
    python3 tools/ettelem/sync_hub_data.py --check    # exit 1, and name the blocks, if that file is stale

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
                      summarised for the DRAM-read bursts that slow it on aifoundry2; and, as .ring, reruns.json dropped[]:
                      the median latency in each rerun pass dropped because the sampler was starved (the s <-> s+16 ring)
  power.idle_unsensed catalogue.json bursts: board idle less the three rails' idle, per card, with the die range
  energy_events       every event the reports priced, with its energy [range] and the rate at which the measurement
                      ran it, for the chart "How many identical events before the meter sees one?"

Deterministic: the same inputs give the same file, byte for byte.
"""
import argparse
import glob
import json
import os
import statistics
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
D = os.path.join(ROOT, "docs", "reports", "data")
HUB = os.path.join(ROOT, "docs", "reports", "sources", "limits-of-observability.data.json")
EM = os.path.join(D, "2026-09-23-energy-manual")
FIT, CAT, MAN, RERUNS = (os.path.join(EM, f) for f in ("unmetered_fit.json", "catalogue.json", "manual.json", "reruns.json"))
DVFS = os.path.join(D, "2026-09-22-dvfs-aifoundry2", "dvfs.json")
WIRE = os.path.join(D, "2026-09-24-wire-energy", "report.json")
HORACE = os.path.join(D, "2026-09-21-horace-aifoundry2")
CARDS = ("aifoundry2", "aifoundry3")
PAGES = "https://spacesheep.dev/@yaroslavvb/"

# The meter's own constants, from the firmware as the ladder rows 'Board power' and 'Rail power' quote them: the
# board reading in 10 mW steps and the rails in 1 mW, a new value per service-processor pass (133 ms on aifoundry2).
METER = {"board_lsb_w": 0.010, "rail_lsb_w": 0.001, "pass_s": 0.133}


def load(p):
    with open(p) as fh:
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
    out["fit"] = {c: {k: v for k, v in fit[c].items() if k not in ("per_config", "per_config_fields")} for c in CARDS}
    out["per_config"] = {"fields": fit[CARDS[0]]["per_config_fields"], **{c: fit[c]["per_config"] for c in CARDS}}
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
    s2, s3 = cat["cards"][CARDS[0]]["summary"], cat["cards"][CARDS[1]]["summary"]
    ratio = [s3[k]["over_idle_w"]["mean"] / s2[k]["over_idle_w"]["mean"] for k in sorted(s2) if reads(k) and k in s3]
    cc = cat["cross_card"]
    samp["reads_a3_over_a2"] = rng(min(ratio), max(ratio))
    samp["cross_card"] = {"median": r3(cc["median"]), "p10": r3(cc["p10"]), "p90": r3(cc["p90"]), "n": cc["n"]}
    samp["reads"] = "tload/dram/* and dramrow/stride1K/* (full-rate DRAM reads)"
    # The ring that starves it: the rerun passes of the s <-> s+16 ring (burst "xshire16") that analyze_reruns.py
    # dropped for the sampler's latency (median > 60 ms); any other starved burst would not belong to this sentence.
    ring = [d for d in reruns.get("dropped", []) if d.get("burst") == "xshire16" and d.get("sampler_median_ms", 0) > 60]
    samp["ring"] = {"bursts": sorted({d["burst"] for d in ring}), "cards": sorted({c for d in ring for c in CARDS if c in d["pass"]}),
                    "median_ms": [d["sampler_median_ms"] for d in ring], "passes": len(ring)}
    out["sampler"] = samp

    iu = {}
    for c in CARDS:
        bs = cat["bursts"][c]
        u = [b["p_idle_w"] - b["minion_idle_w"] - b["sram_idle_w"] - b["noc_idle_w"] for b in bs]
        T = [b["die_c_idle"] for b in bs]
        iu[c] = {"w": rng(min(u), max(u)), "die_c": rng(min(T), max(T)), "bursts": len(bs)}
    out["idle_unsensed"] = iu
    return out


# ---------------------------------------------------------------- energy events
def runs_median(dirs, pattern, key):
    """Median rate per label over every launch in the rerun passes' runs.jsonl (launch -1 is the warm-up)."""
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
                        by.setdefault(r["label"], []).append(v)
    return {k: statistics.median(v) for k, v in by.items()}


def pooled(s, scale):
    """A pooled {mean, lo, hi, per_card} block (analyze_reruns / catalogue style) in joules."""
    pc = {c: r3sig(v["mean"] * scale) for c, v in (s.get("per_card") or {}).items() if isinstance(v, dict) and "mean" in v}
    return {"e": [r3sig(s["mean"] * scale), r3sig(s["lo"] * scale), r3sig(s["hi"] * scale)], "cards": pc}


def r3sig(v):
    return float(f"{v:.4g}")


def energy_events(man, reruns, wire, model, hrep):
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
    hop_mm = wire["inputs"]["hop_mm"]["value"]
    cf = wire["wire"]["configs"]
    bitmm = lambda pre: max(v["gb_s"] * 8e9 * v["hop_distance"] * hop_mm for k, v in cf.items() if k.startswith(pre))  # noqa: E731
    src_w = {"url": PAGES + "et-soc1-heat-per-mm#ones", "label": "Heat per millimetre, §5"}
    h = wire["headline"]
    add("flips", "wire-free", "a random bit carried 1 mm, free links (mesh rail)", "bit·mm", src_w,
        {"any": {**pooled(h["uncontended/noc_rail"]["random_bit_total"], 1e-15), "rate": r3sig(bitmm("wsep/"))}},
        note="rate: the most bit·mm per second of the link-disjoint runs")
    add("flips", "wire-loaded", "a random bit carried 1 mm, loaded mesh (board power)", "bit·mm", src_w,
        {"any": {**pooled(h["v1/board"]["random_bit_total"], 1e-15), "rate": r3sig(max(bitmm(p) for p in ("wbern/", "walt/", "wlegacy/")))}},
        note="rate: the most bit·mm per second of the first run's all-pairs configurations")

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

    # Bytes by level: the energy manual's reruns (§4.2), three passes on each card; rates from the passes' own runs.
    dirs = reruns["dirs"]
    rl = runs_median(dirs, "rl-pass*[0-9]", lambda r: r["bytes"] / r["wall_s"] if r.get("bytes") and r.get("wall_s") else None)
    src_l = {"url": PAGES + "et-soc1-energy-manual#reads-by-level", "label": "The energy manual, §4.2"}
    lv = reruns["levels_pj_per_byte"]
    # The L1 comes from the catalogue's unrolled 32 B vector loads (§4.1), the figure the manual says to use: memhier's
    # own loop (8 loads per iteration) issues a load every 3.2 cycles instead of 1.4 and reads 44% higher per byte.
    add("bytes", "b-l1", "a byte read from the L1", "byte", {"url": PAGES + "et-soc1-energy-manual#reads-and-writes-measured-together", "label": "The energy manual, §4.1"},
        {p: {**pooled(cb[f"flw.ps/{p}/h2"], 1e-12 / 32), "rate": r3sig(sm[f"flw.ps/{p}/h2"]["ops_per_s"]["mean"] * 32)} for p in ("random", "zeros")},
        note="32-byte vector loads on both harts, the catalogue's unrolled loop; memhier's slower loop reads 0.77 pJ/B")
    for k, lab in (("l2", "a byte read from the L2"), ("scp-local", "a byte read from the shire's own scratchpad"),
                   ("scp-remote", "a byte read from a scratchpad 16 shires away"), ("l3", "a byte read from the L3"), ("dram", "a byte read from DRAM")):
        add("bytes", "b-" + k, lab, "byte", src_l, {"any": {**pooled(lv[k], 1e-12), "rate": r3sig(rl[k])}},
            note="memory whose contents the probe never set")
    src_rw = {"url": PAGES + "et-soc1-energy-manual#reads-and-writes-measured-together", "label": "The energy manual, §4.1"}
    for n, lab in (("tload/dram", "a byte of a tensor load from DRAM"), ("st_stream/dram", "a byte stored through the L1 to DRAM (the line is read first)")):
        add("bytes", "b-" + n.replace("/", "-"), lab, "byte", src_rw,
            {p: {**pooled(cb[f"{n}/{p}"], 1e-12), "rate": r3sig(sm[f"{n}/{p}"]["bytes_per_s"]["mean"])} for p in ("random", "zeros")})

    # Messages (energy manual §5) and the relay (Hand it to the next shire).
    src_m = {"url": PAGES + "et-soc1-energy-manual#bytes-between-cores-and-shires", "label": "The energy manual, §5"}
    rg = reruns["rings_pj_per_byte"]
    for k, lab in (("pair", "a byte messaged to the other minion of a pair"), ("neigh", "a byte messaged around a neighbourhood"),
                   ("shire", "a byte messaged around a shire"), ("xshire1", "a byte messaged to the next shire by ID")):
        add("msg", "m-" + k, lab, "byte", src_m, {"any": {**pooled(rg[k], 1e-12), "rate": r3sig(rl[k])}})
    rel = runs_median(dirs, "relay-pass*[0-9]", lambda r: r["bytes"] / r["wall_s"] if r.get("bytes") and r.get("wall_s") else None)
    src_r = {"url": PAGES + "et-soc1-on-chip-relay#the-same-watts-a-thirtieth-of-the-work", "label": "Hand it to the next shire, §2"}
    for k, lab in (("dram", "a byte relayed through DRAM"), ("hop", "a byte handed to the next shire's scratchpad"), ("scp", "a byte kept in the shire's own scratchpad")):
        add("msg", "r-" + k, lab, "byte", src_r, {"any": {**pooled(reruns["relay_pj_per_byte"][k], 1e-12), "rate": r3sig(rel[k])}})

    # Synchronisation: the hot line's atomics.
    hot = runs_median(dirs, "hotline-pass*[0-9]", lambda r: r.get("ops_per_s"))
    src_s = {"url": PAGES + "et-soc1-hot-line#what-it-costs-in-energy", "label": "One hot line stops a shire, §6"}
    for k, lab in (("spread", "a global atomic, each shire on its own line"), ("contended", "a global atomic on one contended line")):
        add("sync", "s-" + k, lab, "atomic", src_s, {"any": {**pooled(reruns["hotline_nj_per_op"][k], 1e-9), "rate": r3sig(hot[k])}})

    fam = [["flips", "Flips and wires", "var(--c7)"], ["tensor", "Tensor multiply-adds", "var(--c1)"], ["instr", "Instructions", "var(--c2)"],
           ["bytes", "Bytes by level", "var(--c3)"], ["msg", "Messages and relay", "var(--c4)"], ["sync", "Synchronisation", "var(--c5)"]]
    return {"families": fam, "events": ev,
            "meter": {**METER, "idle_law_rms_w": r3(model["power"]["rms_idle"])},
            "rate_rule": "the one at which the measurement ran it on all 1,024 minions at 600 MHz: the median launch rate of the "
                         "energy manual's rerun passes (bytes by level, messages, relay, atomics), the catalogue's aifoundry2 runs "
                         "(instructions, byte paths), the tensor rows, the Horace experiment's flip counts, and the heat runs' most "
                         "bit·mm per second (wires)",
            "source": "tools/ettelem/sync_hub_data.py from manual.json, reruns.json and its rerun directories, the wire report.json "
                      "and the Horace model.json / report.json"}


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


def build(hub):
    fit, cat, man, reruns = load(FIT), load(CAT), load(MAN), load(RERUNS)
    new = json.loads(json.dumps(hub))
    P = new.setdefault("power", {})
    for k, v in power_blocks(fit, cat, load(DVFS), reruns).items():
        P[k] = v
    new["energy_events"] = energy_events(man, reruns, load(WIRE), load(os.path.join(HORACE, "model.json")), load(os.path.join(HORACE, "report.json")))
    return new


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the data file differs from what this script would write")
    ap.add_argument("--hub", default=HUB)
    a = ap.parse_args()
    with open(a.hub) as fh:
        text = fh.read()
    hub = json.loads(text)
    new = build(hub)
    out = dumps(new) + "\n"
    if a.check:
        if out == text:
            print(f"{os.path.relpath(a.hub, ROOT)}: up to date")
            return
        stale = [f"power.{k}" for k in new["power"] if new["power"].get(k) != hub.get("power", {}).get(k)]
        stale += ["energy_events"] if new.get("energy_events") != hub.get("energy_events") else []
        sys.exit(f"{os.path.relpath(a.hub, ROOT)} is stale: " + (", ".join(stale) if stale else "formatting only") +
                 "\n  run python3 tools/ettelem/sync_hub_data.py, then rebuild the page")
    with open(a.hub, "w") as fh:
        fh.write(out)
    P = new["power"]
    f2, f3 = P["fit"]["aifoundry2"], P["fit"]["aifoundry3"]
    print(f"wrote {os.path.relpath(a.hub, ROOT)}: fit rms {f2['rms_w']:.3f}/{f3['rms_w']:.3f} W, droop {P['droop']['mv_per_dram_offrail_w']:.4f} mV/W, "
          f"rail filter tau {P['rail_filter']['aifoundry2']['tau_s']}/{P['rail_filter']['aifoundry3']['tau_s']} s, "
          f"{len(new['energy_events']['events'])} energy events")


if __name__ == "__main__":
    main()
