#!/usr/bin/env python3
"""Attribute the catalogue's unmetered power, and calibrate the DDR-rail droop against it.

    python3 tools/ettelem/fit_unmetered.py                    # fit, and compare with the committed unmetered_fit.json
    python3 tools/ettelem/fit_unmetered.py --out FIT.json     # also write the fit (same shape as unmetered_fit.json)

Board power minus the three metered rails (minion, SRAM, NoC) is power no sensor on the card reports. For each
card, each catalogue configuration's mean unmetered watts over idle is fitted, with no intercept, as

    unmetered = a_minion * rail_minion_w + a_sram * rail_sram_w + a_noc * rail_noc_w + e_dram * DRAM bytes/s

where the rail terms are each rail's watts over idle (a delivery loss, plus whatever unmetered logic works in step
with the rail) and the DRAM term counts the bytes per second of the configurations that move DRAM: those with
'dram' in the name, except dramrow*/stride8K. The rows are configuration means over the three passes (392 on
aifoundry2, 386 on aifoundry3), not bursts. Standard errors are rms * sqrt(diag((X^T X)^-1)).

The second fit is the DDR-rail droop: the Moortec monitors' ddr reading (die_mv.ddr, averaged over the eight memory
shires) during each burst, below its reading in the idle gap before it, regressed with no intercept on the
fitted off-rail DRAM watts (the unmetered watts less the fitted rail losses, DRAM configurations only) and on the
rest of the board's power over idle. It uses the aifoundry2 catalogue telemetry only, which does not cover the six
dramrow2 configurations run separately, hence n = 386.

Reproducibility against docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json, which was first computed
inline: the attribution (coefficients, standard errors, rms and n on both cards) is reproduced exactly. The droop
coefficient is reproduced to within 3% (0.865 against 0.841 mV per off-rail DRAM watt), its rms to 6% (0.375 against
0.355 mV), the minion IR drop to 3% (0.070 against 0.068 mV/W) and the idle monitor levels to 0.2 mV; the small
common term is 0.029 against 0.025 mV per board watt. The inline computation's busy and idle windows were not
recorded, and the ones used here (busy: from 0.5 s after a burst starts to its end; idle: from 2.5 s to 0.2 s before
it starts) are this script's choice. The committed file keeps the inline numbers; this script does not overwrite it
unless asked to with --out on that path and --overwrite.
"""
import argparse
import collections
import gzip
import json
import os
import sys

import numpy as np

D = "docs/reports/data"
CAT = f"{D}/2026-09-23-energy-manual/catalogue.json"
TEL = f"{D}/2026-09-23-catalogue-aifoundry2/telemetry.jsonl.gz"
COMMITTED = f"{D}/2026-09-23-energy-manual/unmetered_fit.json"
MONITORS = ["ddr", "sram", "maxion", "minion", "pshire", "noc", "ioshire"]
EXAMPLES = ["add/zeros/h2", "fmadd.ps/random/h2", "st_stream/dram/random", "tload/dram/random", "tload/dram/zeros",
            "tload/scp/random", "tstore/dram/random", "wire/hop6/random"]
BUSY_SKIP_S, IDLE_FROM_S, IDLE_TO_S = 0.5, 2.5, 0.2


def moves_dram(cfg):
    return "dram" in cfg and "stride8K" not in cfg


def config_means(bursts):
    """One row per configuration: the mean of each field over its passes."""
    by = collections.defaultdict(list)
    for b in bursts:
        by[b["cfg"]].append(b)
    rows = {}
    for cfg, bs in by.items():
        m = {k: float(np.mean([x[k] for x in bs])) for k in ("rail_minion_w", "rail_sram_w", "rail_noc_w", "over_idle_w", "bytes_per_s")}
        m["unmetered_w"] = m["over_idle_w"] - m["rail_minion_w"] - m["rail_sram_w"] - m["rail_noc_w"]
        m["dram_bytes_per_s"] = m["bytes_per_s"] if moves_dram(cfg) else 0.0
        rows[cfg] = m
    return rows


def attribute(rows):
    cfgs = list(rows)
    X = np.array([[rows[c]["rail_minion_w"], rows[c]["rail_sram_w"], rows[c]["rail_noc_w"], rows[c]["dram_bytes_per_s"] * 1e-12] for c in cfgs])
    y = np.array([rows[c]["unmetered_w"] for c in cfgs])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    rms = float(np.sqrt(np.mean(res ** 2)))
    se = rms * np.sqrt(np.diag(np.linalg.inv(X.T @ X)))
    names = ["minion", "sram", "noc", "dram_pj_per_byte"]
    return {"coef": dict(zip(names, map(float, coef))), "se": dict(zip(names, map(float, se))), "rms_w": rms, "n": len(cfgs)}


def droop(bursts, fit, tel_path):
    T = [json.loads(line) for line in gzip.open(tel_path, "rt")]
    ts = np.array([r["t_ms"] / 1000 for r in T])
    mv = {k: np.array([r["die_mv"][k] for r in T], float) for k in MONITORS}
    c = fit["coef"]
    per = collections.defaultdict(list)
    idle_levels = {k: [] for k in MONITORS}
    for b in sorted(bursts, key=lambda r: r["t_lo"]):
        busy = (ts >= b["t_lo"] + BUSY_SKIP_S) & (ts <= b["t_hi"])
        idle = (ts >= b["t_lo"] - IDLE_FROM_S) & (ts < b["t_lo"] - IDLE_TO_S)
        if busy.sum() < 5 or idle.sum() < 3:
            continue  # outside this telemetry file (the dramrow2 run) or too short
        for k in MONITORS:
            idle_levels[k].append(mv[k][idle].mean())
        per[b["cfg"]].append((mv["ddr"][idle].mean() - mv["ddr"][busy].mean(),
                              mv["minion"][idle].mean() - mv["minion"][busy].mean(), b))
    out = {}
    for cfg, v in per.items():
        m = lambda k: float(np.mean([x[2][k] for x in v]))  # noqa: E731
        un = m("over_idle_w") - m("rail_minion_w") - m("rail_sram_w") - m("rail_noc_w")
        off = un - (c["minion"] * m("rail_minion_w") + c["sram"] * m("rail_sram_w") + c["noc"] * m("rail_noc_w")) if moves_dram(cfg) else 0.0
        out[cfg] = {"cfg": cfg, "over_idle_w": m("over_idle_w"), "dram_offrail_w": off, "rail_minion_w": m("rail_minion_w"),
                    "droop_ddr_mv": float(np.mean([x[0] for x in v])), "droop_minion_mv": float(np.mean([x[1] for x in v]))}
    cfgs = list(out)
    X = np.array([[out[k]["dram_offrail_w"], out[k]["over_idle_w"] - out[k]["dram_offrail_w"]] for k in cfgs])
    y = np.array([out[k]["droop_ddr_mv"] for k in cfgs])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    rms = float(np.sqrt(np.mean((y - X @ coef) ** 2)))
    xm = np.array([out[k]["rail_minion_w"] for k in cfgs])
    ym = np.array([out[k]["droop_minion_mv"] for k in cfgs])
    return {
        "mv_per_dram_offrail_w": float(coef[0]), "mv_per_board_w_common": float(coef[1]), "rms_mv": rms, "n": len(cfgs),
        "idle_die_mv": {k: float(np.mean(v)) for k, v in idle_levels.items()},
        "minion_ir_drop_mv_per_w": float(xm @ ym / (xm @ xm)),
        "examples": [{k: out[e][k] for k in ("cfg", "over_idle_w", "dram_offrail_w", "droop_ddr_mv", "droop_minion_mv")} for e in EXAMPLES if e in out],
        "source": f"{TEL} (die_mv from DM_CMD_GET_ASIC_VOLTAGE: the Moortec voltage monitors averaged over the 8 memory shires "
                  "for ddr, the 34 minion shires for minion/sram/noc); computed by tools/ettelem/fit_unmetered.py",
    }


def compare(new, old, path=""):
    """Print every number that differs from the committed file by more than 1e-9 relative."""
    worst = 0.0
    if isinstance(new, dict):
        for k, v in new.items():
            if k in old and k not in ("examples", "source"):
                worst = max(worst, compare(v, old[k], f"{path}.{k}" if path else k))
    elif isinstance(new, (int, float)):
        rel = abs(new - old) / max(abs(old), 1e-12)
        print(f"  {path:45s} {new:12.6g}  committed {old:12.6g}  {'same' if rel < 1e-9 else f'{100 * rel:.1f}% off'}")
        worst = rel
    return worst


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--catalogue", default=CAT)
    ap.add_argument("--telemetry", default=TEL, help="aifoundry2 catalogue telemetry, for the droop fit")
    ap.add_argument("--out", help="write the fit here")
    ap.add_argument("--overwrite", action="store_true", help=f"allow --out to replace {COMMITTED}")
    a = ap.parse_args()
    cat = json.load(open(a.catalogue))
    fit = {card: attribute(config_means(cat["bursts"][card])) for card in ("aifoundry2", "aifoundry3")}
    fit["ddr_droop"] = droop(cat["bursts"]["aifoundry2"], fit["aifoundry2"], a.telemetry)
    for card in ("aifoundry2", "aifoundry3"):
        f = fit[card]
        print(f"{card}: unmetered = {f['coef']['minion']:.4f} minion + {f['coef']['sram']:.4f} sram + {f['coef']['noc']:.4f} noc "
              f"+ {f['coef']['dram_pj_per_byte']:.3f} pJ/B DRAM; rms {f['rms_w']:.4f} W over {f['n']} configuration means")
    dr = fit["ddr_droop"]
    print(f"ddr droop (aifoundry2): {dr['mv_per_dram_offrail_w']:.3f} mV per off-rail DRAM W + {dr['mv_per_board_w_common']:.4f} mV per other board W; "
          f"rms {dr['rms_mv']:.3f} mV over {dr['n']} configurations")
    if os.path.exists(COMMITTED):
        print(f"against {COMMITTED}:")
        old = json.load(open(COMMITTED))
        attr = max(compare(fit[c], old[c], c) for c in ("aifoundry2", "aifoundry3"))
        drp = compare(dr, old["ddr_droop"], "ddr_droop")
        print(f"attribution: {'reproduced exactly' if attr < 1e-9 else f'differs by up to {100 * attr:.2g}%'}; "
              f"droop block: {'reproduced exactly' if drp < 1e-9 else f'differs by up to {100 * drp:.2g}%'}")
    if a.out:
        if os.path.abspath(a.out) == os.path.abspath(COMMITTED) and not a.overwrite:
            sys.exit(f"refusing to replace {COMMITTED}: its droop block came from an inline computation this script "
                     "reproduces only to within 3% (droop coefficient); pass --overwrite to replace it anyway")
        with open(a.out, "w") as fh:
            json.dump(fit, fh, indent=1)
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
