#!/usr/bin/env python3
"""E184's forecast inputs, read from the lab's committed files and the public firmware (registration, desk only).

    /usr/bin/python3 -B tools/claims-v3/e184/inputs_e184.py <repository top> > tools/claims-v3/e184/inputs-e184.json

Every number E184's forecasts and power use comes from here, with the sha256 of each committed file it reads:
  1. the energy catalogue (docs/reports/data/2026-09-23-energy-manual/catalogue.json, 25-26 Sep 2026): fadd.ps zeros, const and
     random on aifoundry3 and aifoundry1's card 1 (board and minion rail over idle, the instruction rate); E46's SRAM-dominated set
     (SRAM rail at least 2 W and at least half of the three rails on aifoundry3) with card 1's rows beside them;
  2. E180 (docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/, 6 Nov 2026, aifoundry3 at 600 MHz): fadd.ps random less zeros on
     the board and the minion rail, per pass; and, from its raw telemetry, the board's noise per SP refresh inside fadd.ps bursts, the
     refreshes' lag-1 correlation, the launch-gap dips, and the absolute board level of fadd.ps zeros on 32 shires and of the idle card;
  3. E178 (docs/reports/data/2026-11-06-e178-one-number-aifoundry3/e178.json): the board level of the int8 pair (4s, 5s), the operating
     point E184's part P reproduces;
  4. Q150's committed checks (docs/reports/data/2026-11-06-q150-meter-checks/, 707cd2c5; its dated note 1, baa7c01b): card 1's SRAM
     rail in the version-3 TEL block's reset windows, and its average's restart after a reset;
  5. E58 (docs/reports/data/2026-09-29-tau-aifoundry1-c1/ and -aifoundry3/report.json): the rails' filters;
  6. E172's raw telemetry (docs/reports/data/2026-11-05-e172-blind8-card1/): card 1's minion-average glitch rate;
  7. the public PMIC firmware's board-meter conversion (aifoundry-org/et-boards e5e0cf2, runtime 1.7.0), as literals with their files,
     lines and git blob ids (the files are not in this repository).
Pure Python, deterministic (math.fsum), the same output under python3 3.9 and 3.13.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import hashlib
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e184_common as c  # noqa: E402

TOP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
D = "docs/reports/data/"
CAT = D + "2026-09-23-energy-manual/catalogue.json"
E180R = D + "2026-11-06-e180-vector-add-aifoundry3/reduced-e180-v3.json"
E180RAW = D + "2026-11-06-e180-vector-add-aifoundry3/raw/e180"
E178J = D + "2026-11-06-e178-one-number-aifoundry3/e178.json"
Q150 = D + "2026-11-06-q150-meter-checks/"
TAU1 = D + "2026-09-29-tau-aifoundry1-c1/report.json"
TAU3 = D + "2026-09-29-tau-aifoundry3/report.json"
E172RAW = D + "2026-11-05-e172-blind8-card1/aifoundry1-c1/e172"
used = {}


def rd(rel, mode="json"):
    p = os.path.join(TOP, rel)
    b = open(p, "rb").read()
    used[rel] = hashlib.sha256(b).hexdigest()
    return json.loads(b) if mode == "json" else b


def r6(x):
    return None if x is None or x != x else float("%.6g" % x)


def jl_gz(rel):
    b = rd(rel, "bytes")
    out = []
    for line in gzip.decompress(b).decode().splitlines():
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


out = {"what": "E184's forecast inputs (inputs_e184.py), every one from a committed file or the public firmware", "repo_files": used}

# ---- 1. the catalogue ----------------------------------------------------------------------------------------------------------
cat = rd(CAT)
rows = {}
for card in ("aifoundry3", "aifoundry1-c1"):
    s = cat["cards"][card]["summary"]
    for k in ("fadd.ps/zeros/h2", "fadd.ps/const/h2", "fadd.ps/random/h2"):
        r = s[k]
        rows["%s %s" % (card, k)] = {"board_over_idle_w": r6(r["over_idle_w"]["mean"]), "board_se_w": r6(r["over_idle_w"]["se"]),
                                      "minion_over_idle_w": r6(r["rails_over_w"]["minion_w"]["mean"]),
                                      "ops_per_s": r6(r["ops_per_s"]["mean"]), "passes": r["passes"]}
cat_step = {}
for card in ("aifoundry3", "aifoundry1-c1"):
    z, rr = rows["%s fadd.ps/zeros/h2" % card], rows["%s fadd.ps/random/h2" % card]
    cat_step[card] = {"board_random_less_zeros_w": r6(rr["board_over_idle_w"] - z["board_over_idle_w"]),
                      "board_mw_per_minion": r6((rr["board_over_idle_w"] - z["board_over_idle_w"]) / 1024 * 1000),
                      "rail_random_less_zeros_w": r6(rr["minion_over_idle_w"] - z["minion_over_idle_w"]),
                      "rail_mw_per_minion": r6((rr["minion_over_idle_w"] - z["minion_over_idle_w"]) / 1024 * 1000),
                      "board_zeros_per_shire_w": r6(z["board_over_idle_w"] / 32)}
s3, s1 = cat["cards"]["aifoundry3"]["summary"], cat["cards"]["aifoundry1-c1"]["summary"]
sram_set = []
for k in sorted(s3):
    ro = s3[k].get("rails_over_w") or {}
    try:
        sr, mn, nc = ro["sram_w"]["mean"], ro["minion_w"]["mean"], ro["noc_w"]["mean"]
    except (KeyError, TypeError):
        continue
    if sr >= 2.0 and sr / (sr + mn + nc) >= 0.5 and k in s1:
        b3, b1 = s3[k]["over_idle_w"]["mean"], s1[k]["over_idle_w"]["mean"]
        sr1 = s1[k]["rails_over_w"]["sram_w"]["mean"]
        sram_set.append({"cfg": k, "pattern": s3[k]["pattern"], "operands": s3[k]["operands"], "scp": s3[k]["scp"],
                         "harts": s3[k]["harts"], "a3_sram_w": r6(sr), "a3_board_w": r6(b3), "c1_sram_w": r6(sr1),
                         "c1_board_w": r6(b1), "share_ratio_c1_over_a3": r6((sr1 / b1) / (sr / b3))})
ratios = sorted(x["share_ratio_c1_over_a3"] for x in sram_set)
out["catalogue"] = {"file": CAT, "rows": rows, "fadd_ps_step": cat_step, "sram_set": sram_set,
                    "sram_set_n": len(sram_set), "sram_share_ratio_median": r6(c.median(ratios)),
                    "sram_share_ratio_p10_p90": [r6(ratios[int(0.1 * (len(ratios) - 1))]), r6(ratios[int(math.ceil(0.9 * (len(ratios) - 1)))])],
                    "card1_idle_w": r6(cat["cards"]["aifoundry1-c1"]["idle_clock"]["idle_w_by_mhz"]["600"]),
                    "a3_idle_w": r6(cat["cards"]["aifoundry3"]["idle_clock"]["idle_w_by_mhz"]["600"])}

# ---- 2. E180 ---------------------------------------------------------------------------------------------------------------------
e180 = rd(E180R)
P = e180["passes"]
bz = [P[p]["D"]["fadd.ps/random"] - P[p]["D"]["fadd.ps/zeros"] for p in sorted(P)]
rz = [P[p]["R"]["fadd.ps/random"] - P[p]["R"]["fadd.ps/zeros"] for p in sorted(P)]
m_b, m_r = c.fmean(bz), c.fmean(rz)
se_b, se_r = c.fsd(bz) / math.sqrt(len(bz)), c.fsd(rz) / math.sqrt(len(rz))
out["e180_anchor"] = {"file": E180R, "passes": sorted(P), "board_random_less_zeros_w": [r6(x) for x in bz],
                      "rail_random_less_zeros_w": [r6(x) for x in rz],
                      "board_mean_w": r6(m_b), "board_se_w": r6(se_b), "rail_mean_w": r6(m_r), "rail_se_w": r6(se_r),
                      "board_mw_per_minion": r6(m_b / 1024 * 1000), "board_mw_per_minion_se": r6(se_b / 1024 * 1000),
                      "rail_mw_per_minion": r6(m_r / 1024 * 1000), "rail_over_board": r6(m_r / m_b),
                      "zeros_d_w": r6(c.fmean(P[p]["D"]["fadd.ps/zeros"] for p in sorted(P))),
                      "note": "D is the catalogue's leakage-corrected over-idle power (analyze_catalogue.bursts_of), R the rail's"}

# the raw telemetry: per-refresh noise inside fadd.ps bursts (from 0.5 s after a burst's first launch), detrended per burst
noise = {"zeros": [], "onenum": [], "random": [], "const": []}
lag1, dips, nref, zeros_lvl, idle_lvl = [], 0, 0, [], []
for pdir in sorted(glob.glob(os.path.join(TOP, E180RAW, "p180*"))):
    rel = os.path.relpath(pdir, TOP)
    tel = jl_gz(rel + "/telemetry.jsonl.gz")
    runs = jl_gz(rel + "/runs.jsonl.gz")
    bursts = {}
    for r in runs:
        b = bursts.setdefault(r["cfg"], [r["t_start_ms"], r["t_end_ms"], r["kind"]])
        b[0], b[1] = min(b[0], r["t_start_ms"]), max(b[1], r["t_end_ms"])
    tt = [d["t_ms"] for d in tel]
    for cfg, (t0, t1, kind) in sorted(bursts.items()):
        if not kind.startswith("fadd.ps/"):
            continue
        ref = c.refreshes([d for d in tel if t0 + 500 <= d["t_ms"] <= t1])
        xs = [d["board_w"] for d in ref]
        keep = c.dip_keep(xs)
        dips += len(xs) - len(keep)
        nref += len(xs)
        ys = [xs[i] for i in keep]
        ts = [(ref[i]["t_ms"] - t0) / 1000.0 for i in keep]
        if len(ys) < 8:
            continue
        mt, my = c.fmean(ts), c.fmean(ys)
        b = math.fsum((t - mt) * (y - my) for t, y in zip(ts, ys)) / math.fsum((t - mt) ** 2 for t in ts)
        res = [y - my - b * (t - mt) for t, y in zip(ts, ys)]
        kk = kind.split("/")[1]
        noise[kk if kk in ("zeros", "random", "const") else "onenum"].append(c.fsd(res))
        lag1.append(math.fsum(res[i] * res[i + 1] for i in range(len(res) - 1)) / math.fsum(x * x for x in res))
        if kk == "zeros":
            zeros_lvl.append(my)
        # the idle card just before the burst: the last sample at least 1 s before the first launch
        pre = [d["board_w"] for d in tel if t0 - 1500 <= d["t_ms"] <= t0 - 200]
        if pre:
            idle_lvl.append(c.median(pre))
out["e180_noise"] = {"dir": E180RAW, "refreshes": nref, "dips_removed": dips,
                     "refresh_sd_w_median": {k: r6(c.median(v)) for k, v in noise.items()},
                     "bursts": {k: len(v) for k, v in noise.items()},
                     "lag1_median": r6(c.median(lag1)), "lag1_mean": r6(c.fmean(lag1)),
                     "zeros32_board_w_median": r6(c.median(zeros_lvl)), "idle_before_burst_w_median": r6(c.median(idle_lvl)),
                     "rule": "each fadd.ps burst's distinct refreshes from 0.5 s after its first launch to its last launch's end, the dip "
                             "rule applied, detrended by a line in time; sd of the residuals; lag-1 correlation of the residuals"}

# ---- 3. E178's int8 pair ---------------------------------------------------------------------------------------------------------
e178 = rd(E178J)
it = e178["items"]
op = [it["int8.e178_v4"]["p80"]["mean"], it["int8.e178_v5"]["p80"]["mean"]]
out["e178_op"] = {"file": E178J, "int8_4s_p80_w": r6(op[0]), "int8_5s_p80_w": r6(op[1]), "target_board_w": r6(c.fmean(op)),
                  "idle80_w": r6(it["int8.e178_v4"]["idle80"]["mean"]),
                  "pair_d_w": r6(it["int8.e178_v5"]["D"]["mean"] - it["int8.e178_v4"]["D"]["mean"]),
                  "note": "p80 is E178's board level over each run's last 80% (reduce_e178's window), the level the pair was read at"}

# ---- 4. Q150's card-1 SRAM checks ----------------------------------------------------------------------------------------------------
bl = rd(Q150 + "reset_minmax_bylevel.json")
st = rd(Q150 + "reset_minmax_steady.json")
rc = rd(Q150 + "reset_recovery.json")
c1 = bl["aifoundry1-c1"]
f_of = {}
for lvl in ("idle", "busy"):
    m, M = c1[lvl]["min_over_avg"], c1[lvl]["max_over_avg"]
    f_of[lvl] = r6((m / M + 1) / 2)
out["q150_sram"] = {"files": [Q150 + "reset_minmax_bylevel.json", Q150 + "reset_minmax_steady.json", Q150 + "reset_recovery.json"],
                    "card1_sram": c1, "a3_sram": bl["aifoundry3"], "a2_sram": bl["aifoundry2"],
                    "f_reading_fraction": f_of,
                    "card1_minion_noc": {k: v for k, v in st.get("aifoundry1-c1", {}).items() if k in ("minion_w", "noc_w")},
                    "card1_sram_restart_by_100ms": rc["aifoundry1-c1"]["sram_w"],
                    "card1_minion_restart_by_100ms": rc["aifoundry1-c1"]["minion_w"]}

# ---- 5. E58's filters ----------------------------------------------------------------------------------------------------------------
taus = {}
for nm, rel in (("aifoundry1-c1", TAU1), ("aifoundry3", TAU3)):
    rep = rd(rel)
    tv = {}
    for rail in ("minion_w", "sram_w", "noc_w"):
        try:
            tv[rail] = r6(rep[rail]["100"]["one_pass"]["tau_s"])
        except (KeyError, TypeError):
            tv[rail] = None
    try:
        tv["board_avg_w_fixed_delay"] = r6(rep["board_avg_w"]["100"]["fixed_delay"]["tau_s"])
    except (KeyError, TypeError):
        tv["board_avg_w_fixed_delay"] = None
    taus[nm] = tv
out["e58_tau_s"] = taus

# ---- 6. card 1's minion-average glitch (E172) ------------------------------------------------------------------------------------------
g, n = 0, 0
for f in sorted(glob.glob(os.path.join(TOP, E172RAW, "p172*", "telemetry.jsonl.gz"))):
    for d in jl_gz(os.path.relpath(f, TOP)):
        try:
            mw = d["sp"]["minion_w"]
        except (KeyError, TypeError):
            continue
        n += 1
        g += 1 if mw[0] == mw[2] else 0
out["e172_glitch"] = {"dir": E172RAW, "samples": n, "avg_equals_running_max": g, "rate": r6(g / n if n else float("nan")),
                      "rule": "sp.minion_w[0] == sp.minion_w[2] (Q150's q150_crosscheck.py line 188)"}

# ---- 6b. the heat and leakage laws on aifoundry3, for the leakage a quad's B blocks let through ------------------------------------------
xc = rd(D + "2026-11-06-q150-sensor-crosscheck/crosscheck.json")
hs = xc["H_heat_sessions"]["sessions"]
heat = {k: r6(v["per_board_W_origin"]["slope"]) for k, v in sorted(hs.items()) if v.get("card") == "aifoundry3"}
fl = rd(D + "2026-11-06-e181-m11-session2-aifoundry3/scored-m11.json")["sessions"]["S2:p18120"]["FL5c"]["primary"]
leak = fl["beside_34_codes"]["slope_rests_w_per_c"]
hmax = max(heat.values())
out["thermal"] = {"heat_c_per_board_w_by_session": heat, "heat_c_per_board_w_max": hmax,
                  "leak_w_per_c_e181_fl5c": r6(leak), "leak_gain_allowance": r6(hmax * leak),
                  "files": [D + "2026-11-06-q150-sensor-crosscheck/crosscheck.json > H_heat_sessions (b5ab9d46, post hoc)",
                            D + "2026-11-06-e181-m11-session2-aifoundry3/scored-m11.json > FL5c primary (E181, blind)"],
                  "note": "the die's 4.5 s rise per board watt times the leakage law's watts per degree: the most of a step's own leakage "
                          "a block can carry; a 1.6 s block carries less"}

# ---- 7. the public PMIC firmware's board meter (et-boards e5e0cf2) -----------------------------------------------------------------------
def f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]


den = f32(f32(f32(f32(f32(1.0787) * f32(0.001)) * f32(0.00667)) * 12400.0) * 4096.0)
den512 = int(f32(den * 512.0))
ma_per_code = 512000.0 / den512
carry_ma = (1024 * 512000 + den512 // 2) // den512
out["pmic_meter"] = {
    "source": "aifoundry-org/et-boards e5e0cf23c3ee6197b6af10a295065a06acf58f17 (runtime 1.7.0, committed 2026-06-17); the cards run "
              "PMIC 1.5.0 (aifoundry3) and 1.3.0 (card 1), whose sources are not public",
    "files": {
        "firmware/et-soc1-pmic/common/HardwarePlatform/Drivers/inc/adc.h": "blob b755d66db242f5a6c325e3c974d033747620ecf9, lines 19-35: "
            "ADC_FULL_SCALE_MV 1000, ADC_FULL_SCALE_COUNT 4096, HOTSWAP_SENSE_RESISTOR 0.001, LTC4218_TRANSCONDUCTANCE 0.00667, "
            "LTC4218_OUTPUT_LOAD_RESISTOR 12400, CUR_ADJ_FACTOR 1.0787, SHIFT_FOR_INCREASED_PRECISION 9, IMON_DENOMINATOR",
        "firmware/et-soc1-pmic/runtime/PowerManager/src/power_manager_event.c": "blob 85b0163c6f4f85db48d3d3b1ada5040db684d7a2, lines "
            "199-210: imon12vMA = ((result << 9) * 1000 + den / 2) / den; instmW = (imon12vMA * vmon12vMV + 500) / 1000; POWER_IN = "
            "instmW / 10 (the 10 mW units the service processor returns as board_w); lines 216-224: AVERAGE_POWER, a 1 s dt-weighted "
            "average; line 156: the ADC interrupts come every 6 to 10 ms",
        "firmware/et-soc1-pmic/runtime/Startup/src/system_init.c": "blob 0fb96a8a2b12cd0a3eb51dc81ad2ecf4488ee342, lines 251-259: the "
            "internal 1.0 V reference, the 16-bit averaging result, 64 conversions accumulated with ADJRES 4 (so each IMON result is a "
            "64-conversion average on the 12-bit scale the driver's 4096 assumes)",
        "firmware/et-soc1-pmic/common/HardwarePlatform/Drivers/src/TPS53681.c": "blob e4aff5e70bf4110fafa6745a46b0a244ca99d66c, lines "
            "22-33: TPS53681_init writes CLEAR_FAULT, ON_OFF_CONFIG, PHASE 0x80 (all phases selected for the next commands), "
            "OT_FAULT_RESPONSE, OPERATION and the boot VIDs; nothing reads or sets phase shedding"},
    "imon_denominator_x512": den512, "ma_per_code": r6(ma_per_code), "mw_per_code_at_12v": r6(ma_per_code * 12.0),
    "carry_1024_ma": carry_ma, "carry_1024_board_w_at_11p7_12p0_12p3_v": [r6(carry_ma * v / 1000.0) for v in (11.7, 12.0, 12.3)]}

print(json.dumps(out, indent=1, sort_keys=True))
