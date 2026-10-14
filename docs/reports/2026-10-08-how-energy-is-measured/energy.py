#!/usr/bin/env python3
"""energy.py OUT_DIR: the energy of the workload that measure.sh ran, from the card's power meter.

  idle power    = mean board power over the idle stretches before and after the work
                  (their mean removes most of idle power's drift with die temperature)
  energy        = sum over samples of (board power - idle power) x sample interval,
                  over the work plus a short margin either side (the meter lags by up to one
                  service-processor pass, about 0.13-0.27 s)
  per operation = energy / operations completed (the workload's own count, from the device)

The published tables add one refinement, also computed here: the die runs a little warmer during
the work than in the idle stretches, and the warmer die leaks more, so that extra leakage (the idle
law's slope times the temperature difference) is taken out (energy manual §9; the constants are
workloads/enercat/analyze_catalogue.py's).

Prints a summary and writes OUT_DIR/summary.json and OUT_DIR/trace.csv (time from the start of the work).
"""
import json
import math
import os
import re
import statistics
import sys


def load_samples(path):
    rows = []
    with open(path) as f:
        for line in f:
            if not line.startswith("{"):
                continue
            d = json.loads(line)
            if "board_w" not in d:
                continue
            t = d["t_ms"] / 1000.0 if "t_ms" in d else d["t"]          # ettelem / etpower.py
            sp = d.get("sp", {})
            rail = lambda k: sp[k][0] if k in sp else d.get(k)           # the PMIC's running average
            die = d.get("temp_c", {}).get("minshire", [d.get("die_c")])[0]
            mhz = d.get("mhz", {}).get("minion", d.get("minion_mhz"))
            rows.append({"t": t, "board_w": d["board_w"], "minion_w": rail("minion_w"), "sram_w": rail("sram_w"),
                         "noc_w": rail("noc_w"), "die_c": die, "mhz": mhz, "took_ms": d.get("took_ms")})
    return rows


def load_launches(path):
    """The workload's own records: sparsity_host prints one 'SPARSITY {json}' line per launch."""
    out = []
    if os.path.exists(path):
        for line in open(path):
            m = re.match(r"SPARSITY (\{.*\})", line)
            if m:
                r = json.loads(m.group(1))
                if r.get("launch", 0) >= 0:      # launch -1 is a calibration run
                    out.append(r)
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else None


A_LEAK_80, T_L = 23.257, 36.0  # idle law's leakage: 23.3 W x e^((T-80)/36)


def leak_slope(t_c):
    """Watts of extra leakage per degree C of die temperature, at t_c."""
    return A_LEAK_80 / T_L * math.exp((t_c - 80.0) / T_L)


def main():
    out = sys.argv[1]
    idle_before = float(os.environ.get("IDLE_BEFORE", 6))
    idle_after = float(os.environ.get("IDLE_AFTER", 8))
    s = load_samples(os.path.join(out, "power.jsonl"))
    t_start = float(open(os.path.join(out, "t_start")).read())
    t_end = float(open(os.path.join(out, "t_end")).read())
    launches = load_launches(os.path.join(out, "workload.out"))

    # The work itself: from the first launch to the end of the last (device-side records), else the process.
    w0 = min(r["t_start_ms"] for r in launches) / 1000.0 if launches else t_start
    w1 = max(r["t_end_ms"] for r in launches) / 1000.0 if launches else t_end
    busy_s = w1 - w0

    before = [x for x in s if t_start - idle_before + 1.0 <= x["t"] <= t_start - 0.1]
    after = [x for x in s if t_end + 3.0 <= x["t"] <= t_end + idle_after - 0.3]
    idle_b, idle_a = mean(x["board_w"] for x in before), mean(x["board_w"] for x in after)
    idle_w = (idle_b + idle_a) / 2

    # Energy above idle, integrated over the work plus a margin (sample interval from the timestamps).
    win = [x for x in s if w0 - 0.5 <= x["t"] <= w1 + 1.0]
    energy_j = 0.0
    for a, b in zip(win, win[1:]):
        energy_j += (a["board_w"] - idle_w) * (b["t"] - a["t"])
    inside = [x for x in s if w0 + 0.3 <= x["t"] <= w1]
    t_idle = mean([x["die_c"] for x in before + after])
    t_busy = mean([x["die_c"] for x in inside])
    leak_w = leak_slope((t_busy + t_idle) / 2) * (t_busy - t_idle) if None not in (t_idle, t_busy) else 0.0
    energy_corr_j = energy_j - leak_w * busy_s
    res = {
        "idle_before_w": round(idle_b, 3), "idle_after_w": round(idle_a, 3), "idle_w": round(idle_w, 3),
        "busy_s": round(busy_s, 3), "energy_above_idle_j": round(energy_j, 3),
        "mean_above_idle_w": round(energy_j / busy_s, 3) if busy_s > 0 else None,
        "leakage_correction_w": round(leak_w, 3), "energy_corrected_j": round(energy_corr_j, 3),
        "busy_mean_board_w": round(mean(x["board_w"] for x in inside), 3) if inside else None,
        "die_c_before": mean(x["die_c"] for x in before), "die_c_busy": mean(x["die_c"] for x in inside),
        "die_c_after": mean(x["die_c"] for x in after),
        "minion_mhz_seen": sorted({x["mhz"] for x in s if x["mhz"] is not None and w0 <= x["t"] <= w1}),
        "samples": len(s), "sample_period_ms": round(1000 * (s[-1]["t"] - s[0]["t"]) / (len(s) - 1), 1),
        "distinct_board_values_per_s": round(sum(1 for a, b in zip(s, s[1:]) if a["board_w"] != b["board_w"])
                                             / (s[-1]["t"] - s[0]["t"]), 2),
        "launches": len(launches),
    }
    if launches and launches[0].get("test") == "fma":
        ops = sum(r["iters"] * r["minions"] for r in launches)          # TensorFMA instructions completed
        macs = ops * 16 * launches[0]["a_elems"]                         # 16 x 16 x 16 = 4,096 per fp32 op
        res.update({"values": launches[0]["values"], "type": launches[0]["type"], "tensorfma_ops": ops,
                    "multiply_adds": macs, "pj_per_multiply_add": round(energy_j / macs * 1e12, 3),
                    "pj_per_multiply_add_corrected": round(energy_corr_j / macs * 1e12, 3),
                    "ghz_device": launches[0].get("ghz"),
                    "all_checked_ok": all(r.get("ok") for r in launches)})
    json.dump(res, open(os.path.join(out, "summary.json"), "w"), indent=1)

    with open(os.path.join(out, "trace.csv"), "w") as f:
        f.write("t_s,board_w,minion_w,sram_w,noc_w,die_c,mhz\n")
        for x in s:
            f.write("%.3f,%s,%s,%s,%s,%s,%s\n" % (x["t"] - w0, x["board_w"], x["minion_w"], x["sram_w"],
                                                 x["noc_w"], x["die_c"], x["mhz"]))

    print("idle: %.2f W before, %.2f W after, baseline %.2f W" % (idle_b, idle_a, idle_w))
    print("work: %.2f s, %.2f W above idle on average, %.1f J above idle" % (busy_s, res["mean_above_idle_w"], energy_j))
    print("      leakage correction %.2f W (die %.1f C busy vs %.1f C idle) -> %.1f J"
          % (leak_w, t_busy or 0, t_idle or 0, energy_corr_j))
    if "pj_per_multiply_add" in res:
        print("      %s data, %d TensorFMA ops = %.3g multiply-adds -> %.3f pJ per multiply-add (%.3f corrected)"
              % (res["values"], res["tensorfma_ops"], res["multiply_adds"], res["pj_per_multiply_add"],
                 res["pj_per_multiply_add_corrected"]))
    print("die: %s C before, %s C during, %s C after; minion clock %s MHz"
          % tuple([None if v is None else round(v, 1) for v in (res["die_c_before"], res["die_c_busy"],
                                                                 res["die_c_after"])] + [res["minion_mhz_seen"]]))


if __name__ == "__main__":
    main()
