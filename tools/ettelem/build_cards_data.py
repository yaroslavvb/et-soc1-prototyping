#!/usr/bin/env python3
"""Assemble the three-machine block and merge it into the report data files.

    build_cards_data.py --cards cards.json --transfer transfer.json --leak leakage_crosscard.json \
        --config config.json --driver driver_config.json --sptrace sptrace-aifoundry3.bin \
        --out cards-report.json --merge dvfs.json report.json

Nothing is fitted here. The per-pattern switching powers come from each card's own strict session; the model
coefficients come from the aifoundry2 fit and are used unchanged; the single scale factor is the least-squares
ratio between the two, reported alongside the leave-one-out check that calibrates it on one run.
"""
import argparse
import json
import re

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    for k in ("cards", "transfer", "leak", "config", "driver", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--sptrace")
    ap.add_argument("--merge", nargs="*", default=[])
    a = ap.parse_args()
    cards = json.load(open(a.cards))
    tr = json.load(open(a.transfer))
    leak = json.load(open(a.leak))
    cfg = json.load(open(a.config))
    drv = json.load(open(a.driver))

    rows = cards["rows"]
    m = np.array([r["model_switching"] for r in rows])
    a3 = np.array([r["aifoundry3"]["switching"] for r in rows])
    scale = float(m @ a3 / (m @ m))
    out = {
        "patterns": [{"values": r["values"], "model": r["model_switching"],
                      "a2": r["aifoundry2"]["switching"], "a3": r["aifoundry3"]["switching"],
                      "a2_sd": r["aifoundry2"]["p80_sd"], "a3_sd": r["aifoundry3"]["p80_sd"]} for r in rows],
        "launch": {k: {"T": v["launch_temp"], "T_sd": v["launch_temp_sd"]} for k, v in cards["cards"].items()},
        "idle": {"aifoundry2": rows[0]["aifoundry2"]["p80"] - rows[0]["aifoundry2"]["switching"],
                 "aifoundry3": rows[0]["aifoundry3"]["p80"] - rows[0]["aifoundry3"]["switching"]},
        "scale": scale,
        "rms_raw": cards["model_error"]["aifoundry3"]["rms"],
        "max_raw": cards["model_error"]["aifoundry3"]["max"],
        "rms_scaled": float(np.sqrt(np.mean((a3 - scale * m) ** 2))),
        "loo": {"median_rms": tr["median_rms"], "worst": tr["worst"],
                "per_pattern": dict(zip(tr["names"], tr["loo_scale_rms"]))},
        "leakage": leak,
        "config": cfg,
        "driver_tdp": {h: v[0]["tdp_w"] for h, v in drv.items()},
        "driver_cards": {h: len(v) for h, v in drv.items()},
    }
    # voltage: the operating point cannot explain the scale, it points the other way
    mv2, mv3 = cfg["aifoundry2"]["minion_mv"], cfg["aifoundry3"]["minion_mv"]
    out["voltage"] = {"a2_mv": mv2, "a3_mv": mv3, "cv2f_ratio": (mv3 / mv2) ** 2}
    if a.sptrace:
        s = open(a.sptrace, "rb").read().decode("latin-1")
        ev = re.findall(r"Power throttle down event, current pwr (\d+)\s+tdp level: (\d+)", s)
        out["sptrace_aifoundry3"] = {"down_events": len(ev), "tdp_levels": sorted({int(t) for _, t in ev}),
                                     "pwr_mw": [int(p) for p, _ in ev][:8],
                                     "up_events": len(re.findall(r"Power throttle up event", s))}
    json.dump(out, open(a.out, "w"), indent=1)
    for path in a.merge:
        d = json.load(open(path))
        d["cards"] = out
        json.dump(d, open(path, "w"), separators=(",", ":"))
        print("merged cards block into", path)
    print(f"scale {scale:.4f}, rms raw {out['rms_raw']:.2f} W -> scaled {out['rms_scaled']:.2f} W; "
          f"leave-one-out median {out['loo']['median_rms']:.2f} W; "
          f"sp trace: {out.get('sptrace_aifoundry3',{}).get('down_events','-')} throttle-down events at tdp "
          f"{out.get('sptrace_aifoundry3',{}).get('tdp_levels','-')}")


if __name__ == "__main__":
    main()
