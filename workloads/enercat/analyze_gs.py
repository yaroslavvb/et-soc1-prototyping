#!/usr/bin/env python3
"""V3-GS (E48) analysis: gather/scatter/atomic rates and energy per element, per card and pooled, pass by pass.

    python3 workloads/enercat/analyze_gs.py --data <dir> --out gs.json [--root <tree>] [--cards a,b,c]

<dir>/<card>/gs/p<KS>/ are the blocks of tools/claims-v3/gs/block.sh (K = pass, S = 0 check, 1 energy, 2 rate), as
the queue's DATA_ROOT/gs collected per card. Nothing here touches a card.

Energy blocks (E): bursts are cut by workloads/enercat/analyze_catalogue.py's bursts_of() through catfull's
cflib.pass_bursts() (both imported unchanged: busy board power over the mean of the bracketing idle, less the leakage
of a warmer burst, times the burst's wall time, over its operations; governor-free cards drop bursts with busy samples
off 600 MHz or a launch whose implied clock is outside 0.595-0.605 GHz). A gs launch counts its operations as active
elements (gathered, scattered or loaded elements; updates for the scatter-adds), so pj_per_op is pJ per element and
pj_per_byte pJ per useful byte. Each E block is one pass: one value per configuration per pass.
Rate blocks (R): the launches kept by gslib's R rule (implied clock and busy samples at 600 MHz on governor-free
cards); a pass's value is the mean over its kept launches.
Check blocks (C): gslib's check.json (verify outcome per configuration, lane-conflict winners, the probe).

Per configuration and card: mean, sd, se, n over passes and the 99% two-sided t interval (catfull's t_crit) for
elements/s (chip), pJ/element, pJ/useful byte, cycles per instruction per hart (median over harts) and per minion,
line bytes/s. Pooled over cards ("combined"): every pass value of every card, E and R alike (mean, per-card means and
se beside, the within-card sd); "combined_catalogue" is the same pool over aifoundry2 and aifoundry3 only, the card set
of the energy manual's catalogue tables, so gs rows set beside catalogue rows compare like with like (aifoundry1-c1,
firmware 1.2.0, then stands beside as a third card). Cross-card: each card's median ratio to aifoundry2 over
configurations. Derived: pJ per line, an overhead-corrected pJ/element (the loop's integer instructions at the
catalogue's addi cost), and measured/predicted against the design's section 1.5 model. Launch checks per card: every
launch of every used E and R block (kept or dropped burst alike) counted for gsc_progress != 0 at exit and for ok false.
"""
import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))

REFERENCE = "aifoundry2"
CATALOGUE_CARDS = ("aifoundry2", "aifoundry3")   # the energy manual's catalogue pools these two
USED_ER = {"ok", "offclock", "partial"}
USED_C = {"ok", "checkfail"}
ADDI_PJ = 8.6                     # the catalogue's addi (random) energy, pJ per instruction (design 2.7)
LOOP_INT_PER_VISIT = 4 + 7.5 / 8  # the walk (4) + the deadline check once per 8 visits: ++iters, 4 csrr, the branch,
                                  # and 0-3 alignment nops (.p2align 4 of cycles()), 1.5 on average
F_FREQ = 0.6e9

# The design's section 1.5 model (stated before any data): elements/s per chip at 1,024 minions, both harts.
MODEL = {
    "gs/E/fgw.ps/dram-512B/rand/random/h2/mff/n1024": {"elements_per_s": 614e9, "why": "8 cycles per instruction per minion (issue)"},
    "gs/E/fgw.ps/dram-4K/rand/random/h2/mff/n1024": {"elements_per_s": 23.9e9, "why": "2 miss handlers, one line per 51.5 cycles"},
    "gs/E/fgw.ps/scp-16K/rand/random/h2/mff/n1024": {"elements_per_s": 23.9e9, "why": "2 miss handlers, one line per 51.5 cycles"},
    "gs/E/fgwl.ps/dram-4K/rand/random/h2/mff/n1024": {"elements_per_s": 26.7e9, "why": "8 x 46 cycles per instruction per hart"},
    "gs/E/fgwg.ps/dram-4K/rand/random/h2/mff/n1024": {"elements_per_s": 7.7e9, "why": "8 x ~160 cycles per hart"},
    "gs/E/fgw.ps/rscp-16K/rand/random/h2/mff/n1024": {"elements_per_s": 7.2e9, "why": "2 miss handlers per ~170 cycles"},
    "gs/E/fgw.ps/dram-256K/rand/random/h2/mff/n1024": {"elements_per_s": 1.19e9, "why": "DRAM line rate 76 GB/s"},
    "gs/E/fscw.ps/dram-256K/rand/random/h2/mff/n1024": {"elements_per_s": 0.6e9, "why": "two line transfers per element"},
    "gs/E/famoaddl.pi/shire-256K/rand/zeros/h2/mff/n1024": {"elements_per_s": 13.4e9, "why": "8 x 92 cycles per hart"},
    "gs/E/famoaddg.pi/chip-8M/rand/zeros/h2/mff/n1024": {"elements_per_s": 2.95e9, "why": "8 x 417 cycles per hart"},
}


def _import(path, name):
    sys.path.insert(0, path)
    try:
        return __import__(name)
    finally:
        sys.path.pop(0)


def libs(root):
    cf = _import(os.path.join(root, "tools", "claims-v3", "catfull"), "cflib")
    gl = _import(os.path.join(root, "tools", "claims-v3", "gs"), "gslib")
    return cf, gl


def stat(v, cf):
    v = np.array([x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))], float)
    if not len(v):
        return None
    out = {"mean": float(v.mean()), "n": int(len(v)), "min": float(v.min()), "max": float(v.max())}
    if len(v) > 1:
        sd = float(v.std(ddof=1))
        h = cf.t_crit(len(v) - 1, 0.99) * sd / math.sqrt(len(v))
        out.update({"sd": sd, "se": sd / math.sqrt(len(v)), "ci99": [out["mean"] - h, out["mean"] + h]})
    else:
        out.update({"sd": 0.0, "se": 0.0, "ci99": None})
    return out


def launch_fields(runs):
    """Per configuration: the gs fields of its launches (mean over launches for the numbers)."""
    by = defaultdict(list)
    for r in runs:
        by[r["cfg"]].append(r)
    out = {}
    for cfg, rs in by.items():
        g = [r.get("gs") or {} for r in rs]
        g0 = g[0]
        out[cfg] = {"op": g0.get("op"), "family": g0.get("family"), "form": g0.get("form"), "index": g0.get("index"),
                    "target": g0.get("target"), "ws": g0.get("ws"), "share": g0.get("share"), "mask": g0.get("mask"),
                    "lanes": g0.get("lanes"), "elem_bytes": g0.get("elem_bytes"), "per_instr": g0.get("per_instr"),
                    "lines_per_instr": g0.get("lines_per_instr"), "harts": rs[0].get("harts"),
                    "participants": rs[0].get("participants"), "shires": rs[0].get("shires"),
                    "minion_mask": rs[0].get("minion_mask"), "unit": rs[0].get("unit"), "operands": rs[0].get("operands"),
                    "cpi_med": float(np.mean([x.get("cpi_med", 0) for x in g])),
                    "cpi_p10": float(np.mean([x.get("cpi_p10", 0) for x in g])),
                    "cpi_p90": float(np.mean([x.get("cpi_p90", 0) for x in g])),
                    "iters_spread": float(np.mean([(x.get("iters_max", 0) - x.get("iters_min", 0)) / max(1, x.get("iters_max", 1)) for x in g])),
                    "gsc_nonzero": int(sum(x.get("gsc_nonzero", 0) for x in g)), "launches": len(rs)}
    return out


def derived_values(lf, elements_per_s, pj):
    """Line bytes/s, per-minion cycles per instruction, pJ per line, overhead-corrected pJ per element."""
    per_instr = lf.get("per_instr") or 8
    lpi = lf.get("lines_per_instr") or 0
    harts = lf.get("harts") or 2
    fam = lf.get("family")
    out = {"line_bytes_per_s": elements_per_s / per_instr * lpi * 64 if elements_per_s and per_instr else None,
           "cpi_minion": lf["cpi_med"] / harts if lf.get("cpi_med") else None}
    if pj is not None:
        lines_per_elem = lpi / per_instr if per_instr else 0
        out["pj_per_line"] = pj / lines_per_elem if lines_per_elem else None
        instr_per_visit = 64 if fam in (7, 8, 9) else 8
        elem_per_visit = instr_per_visit * per_instr
        # the restricted forms' 7 block steps; the packed atomics' 8 fbci.pi addend refreshes (priced at the addi
        # cost as a proxy: they are part of what a famo loop must issue, not of the famo itself)
        extra = 7 if fam in (3, 4) else 8 if fam == 6 else 0
        out["pj_overhead_corrected"] = pj - (LOOP_INT_PER_VISIT + extra) * ADDI_PJ / elem_per_visit
    return out


def load_blocks(card_dir, gl):
    base = os.path.join(card_dir, "gs")
    blocks = []
    if not os.path.isdir(base):
        return blocks
    for name in sorted(os.listdir(base)):
        m = re.fullmatch(r"p(\d)(\d)", name)
        if not m:
            continue   # .attempt-* directories are never used
        d = os.path.join(base, name)
        bj = gl.load_block_json(os.path.join(d, "block.json")) or {}
        pj = gl.jload(os.path.join(d, "pass.json"), {}) or {}
        k, s = int(m.group(1)), int(m.group(2))
        kind = {0: "C", 1: "E", 2: "R"}.get(s)
        st = bj.get("status")
        used = (st in USED_C) if kind == "C" else (st in USED_ER)
        blocks.append({"block": name[1:], "dir": d, "pass": k, "kind": kind, "status": st, "note": bj.get("note"),
                       "gov_free": pj.get("gov_free"), "used": bool(used and not pj.get("smoke")),
                       "idle_mhz_start": pj.get("idle_mhz_start"), "heat_reached": pj.get("heat_reached"),
                       "excluded": pj.get("excluded", [])})
    return blocks


def analyze(root, data, cards=None):
    cf, gl = libs(root)
    out = {"rules": {"energy": "catfull cflib.pass_bursts (analyze_catalogue.bursts_of) per E block; one pass value per "
                               "configuration per block", "rate": "gslib R rule: launches at 600 MHz; pass value = mean",
                     "interval": "99% two-sided t over pass values", "pooled": "every pass value of every card",
                     "overhead": f"{LOOP_INT_PER_VISIT} integer instructions per visit at {ADDI_PJ} pJ (+7 block steps for fg32/fsc32, "
                                 "+8 fbci.pi addend refreshes for the packed atomics)"},
           "model": MODEL, "cards": {}, "bursts": {}, "combined": {}, "cross_card": {}, "checks": {}}
    card_names = cards or sorted(n for n in os.listdir(data) if os.path.isdir(os.path.join(data, n, "gs")))
    for card in card_names:
        blocks = load_blocks(os.path.join(data, card), gl)
        gov = card != "aifoundry3"
        E, R = defaultdict(lambda: defaultdict(list)), defaultdict(lambda: defaultdict(list))
        lfs, bursts, dropped = {}, [], []
        lchk = {"launches": 0, "gsc_nonzero_launches": 0, "gsc_nonzero_harts": 0, "not_ok_launches": 0, "blocks": []}
        for blk in blocks:
            if not blk["used"]:
                continue
            g = blk["gov_free"] if blk["gov_free"] is not None else gov
            runs = gl.jl(os.path.join(blk["dir"], "runs.jsonl"))
            if blk["kind"] in ("E", "R"):
                cnt = gl.gs_counts(runs)
                for k in ("launches", "gsc_nonzero_launches", "gsc_nonzero_harts", "not_ok_launches"):
                    lchk[k] += cnt[k]
                lchk["blocks"].append(blk["block"])
            lf = launch_fields(runs)
            for k, v in lf.items():
                lfs.setdefault(k, v)
            if blk["kind"] == "E":
                kept, drop, _, info, _ = cf.pass_bursts(blk["dir"], g, root)
                dropped += [{"block": blk["block"], **x} for x in drop]
                for b in kept:
                    f = lf.get(b["cfg"], {})
                    dv = derived_values(f, b["ops_per_s"], b["pj_per_op"])
                    rec = {"cfg": b["cfg"], "block": blk["block"], "pass": blk["pass"], "elements_per_s": b["ops_per_s"],
                           "pj_per_element": b["pj_per_op"], "pj_per_byte": b["pj_per_byte"], "over_idle_w": b["over_idle_w"],
                           "die_c_busy": b["die_c_busy"], "cpi_med": f.get("cpi_med"), "cpi_p10": f.get("cpi_p10"),
                           "cpi_p90": f.get("cpi_p90"), "sampler_median_ms": b.get("sampler_median_ms"),
                           "idle_mhz": b.get("idle_mhz"), "gsc_nonzero": f.get("gsc_nonzero"), **dv}
                    bursts.append(rec)
                    for key in ("elements_per_s", "pj_per_element", "pj_per_byte", "cpi_med", "cpi_minion", "line_bytes_per_s",
                                "pj_per_line", "pj_overhead_corrected"):
                        E[b["cfg"]][key].append(rec.get(key))
            elif blk["kind"] == "R":
                tel = gl.jl(os.path.join(blk["dir"], "telemetry.jsonl"))
                tt = [s["t_ms"] / 1000.0 for s in tel]
                mz = [s["mhz"]["minion"] for s in tel]
                per = defaultdict(list)
                for r in runs:
                    ok, _ = gl.launch_clock_ok(r, tt, mz, g)
                    if ok and r.get("ok"):
                        per[r["cfg"]].append(r)
                for cfg, rs in per.items():
                    eps = float(np.mean([r["ops_per_s"] for r in rs]))
                    cpi = float(np.mean([(r.get("gs") or {}).get("cpi_med", 0) for r in rs]))
                    f = lf.get(cfg, {})
                    R[cfg]["elements_per_s"].append(eps)
                    R[cfg]["cpi_med"].append(cpi)
                    R[cfg]["cpi_minion"].append(cpi / (f.get("harts") or 2))
                    R[cfg]["elements_per_s_per_minion"].append(eps / max(1, (f.get("participants") or 1) / (f.get("harts") or 1)))
            elif blk["kind"] == "C":
                out["checks"].setdefault(card, []).append({"block": blk["block"], "status": blk["status"],
                                                           **(gl.jload(os.path.join(blk["dir"], "check.json"), {}) or {})})
        cfgs = {}
        for cfg in sorted(set(E) | set(R)):
            src = E if cfg in E else R
            cfgs[cfg] = {"set": "E" if cfg in E else "R", "fields": lfs.get(cfg, {}),
                         **{k: stat(v, cf) for k, v in src[cfg].items()}}
            if cfg in MODEL and cfgs[cfg].get("elements_per_s"):
                cfgs[cfg]["model_ratio"] = cfgs[cfg]["elements_per_s"]["mean"] / MODEL[cfg]["elements_per_s"]
        out["cards"][card] = {"blocks": [{k: v for k, v in b.items() if k != "dir"} for b in blocks], "configs": cfgs,
                              "dropped": dropped, "launch_checks": lchk,
                              "pass_values": {c: {k: [x for x in v if x is not None] for k, v in (E[c] if c in E else R[c]).items()}
                                              for c in cfgs},
                              "passes_E": sorted({b["pass"] for b in blocks if b["kind"] == "E" and b["used"]}),
                              "passes_R": sorted({b["pass"] for b in blocks if b["kind"] == "R" and b["used"]})}
        out["bursts"][card] = bursts
    # pooled over cards: every pass value (E: one burst per pass; R: one mean per pass) of every card
    allc = sorted({c for card in out["cards"].values() for c in card["configs"]})
    out["combined_catalogue"] = {}
    for cfg in allc:
        for key_out, card_set in (("combined", None), ("combined_catalogue", CATALOGUE_CARDS)):
            per_card, pooled = {}, defaultdict(list)
            for card, cd in out["cards"].items():
                if card_set is not None and card not in card_set:
                    continue
                c = cd["configs"].get(cfg)
                if not c:
                    continue
                per_card[card] = {k: c[k] for k in ("elements_per_s", "pj_per_element", "cpi_med") if c.get(k)}
                for k, vals in cd["pass_values"].get(cfg, {}).items():
                    if k in ("elements_per_s", "pj_per_element", "pj_per_byte", "cpi_med"):
                        pooled[k] += [(card, v) for v in vals]
            if not per_card:
                continue
            comb = {"cards": sorted(per_card), "per_card": per_card}
            for k, pv in pooled.items():
                vals = np.array([v for _, v in pv], float)
                within = []
                for card in {c for c, _ in pv}:
                    cv = np.array([v for c, v in pv if c == card], float)
                    within += list(cv - cv.mean())
                dfree = len(vals) - len({c for c, _ in pv})
                comb[k] = {"mean": float(vals.mean()), "min": float(vals.min()), "max": float(vals.max()), "n": int(len(vals)),
                           "sd_within": float(math.sqrt(sum(x * x for x in within) / dfree)) if dfree > 0 else None}
            out[key_out][cfg] = comb
    # cross-card: each card against aifoundry2
    ref = out["cards"].get(REFERENCE, {}).get("configs", {})
    for card, cd in out["cards"].items():
        if card == REFERENCE or not ref:
            continue
        rr = {}
        for key in ("pj_per_element", "elements_per_s"):
            ratios = [cd["configs"][c][key]["mean"] / ref[c][key]["mean"] for c in cd["configs"]
                      if c in ref and cd["configs"][c].get(key) and ref[c].get(key) and ref[c][key]["mean"]]
            if ratios:
                rv = np.array(ratios)
                rr[key] = {"median": float(np.median(rv)), "p10": float(np.percentile(rv, 10)),
                           "p90": float(np.percentile(rv, 90)), "n": int(len(rv))}
        out["cross_card"][f"{card}/{REFERENCE}"] = rr
    return out


def rnd(x, nd=5):
    if isinstance(x, dict):
        return {k: rnd(v, nd) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v, nd) for v in x]
    if isinstance(x, (float, np.floating)):
        if math.isnan(x) or math.isinf(x):
            return None
        return float(f"{x:.{nd}g}")
    if isinstance(x, np.integer):
        return int(x)
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    ap.add_argument("--cards", default="")
    a = ap.parse_args()
    res = analyze(a.root, a.data, [c for c in a.cards.split(",") if c] or None)
    json.dump(rnd(res), open(a.out, "w"), indent=1)
    for card, cd in res["cards"].items():
        print(f"{card}: E passes {cd['passes_E']}, R passes {cd['passes_R']}, {len(cd['configs'])} configurations, "
              f"{len(cd['dropped'])} bursts dropped")
        for cfg in list(MODEL)[:4]:
            c = cd["configs"].get(cfg)
            if c and c.get("elements_per_s"):
                e = c["elements_per_s"]["mean"]
                pj = c.get("pj_per_element", {}) or {}
                print(f"  {cfg}: {e / 1e9:.2f} G/s, {pj.get('mean', float('nan')):.1f} pJ/element (model {MODEL[cfg]['elements_per_s'] / 1e9:.1f} G/s)")


if __name__ == "__main__":
    main()
