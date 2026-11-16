#!/usr/bin/env python3
"""E202's frozen scorer: one pass over MNIST in int8, scored against the frozen forecasts (E202.md section 7).

    python3 -I -B tools/claims-v3/e202/score_e202.py DATA [--out FILE]        # score a day's data folder
    python3 -I -B tools/claims-v3/e202/score_e202.py --selftest OUT          # the stand-in self-test (must PASS)

It refuses unless every file of SHA256SUMS-e202-registration matches (the self-test outputs aside) and the forecasts
recomputed by forecast_e202.py equal the committed forecast-e202.json, whose sha256 must be FORECAST_SHA256. It never
refits: each burst's given-seconds forecast is forecast_e202.Model.given() at that burst's measured kernel seconds t_k,
wall seconds t_w and starting die T0; the seconds forecast is the frozen point and band at the burst's R.

DATA's form (E202.md 7.1; the kit's runner writes it):
  DATA/smoke/<arm>/host-raw.json    the mnistmlp host's own --out file for each smoke process (arm T-scp, Z-scp, T-dram,
                                    Z-dram, ACC);
  DATA/bursts/<config>/b<k>/        config trained-scp, random-scp, trained-dram or random-dram; k = 1, 2, ...:
      energy.json                   the reducer's output for the burst (one launch): ok, hard, flags, solves (1),
                                    solves_per_s, board.j_per_solve, board.j_per_solve_total, die_c.before;
      host-raw.json                 the mnistmlp host's own --out file for the burst's launch;
      burst.json                    the runner's marks: config, burst (k), order_index, R, set_aside (null or why).
Measured, per burst: J over idle a launch = energy.json board.j_per_solve; J with the card at rest a launch =
board.j_per_solve_total; t_w = 1 / solves_per_s; T0 = die_c.before; t_k = host-raw.json hart0_cycles.max / 600 MHz (the
slowest minion's cycle counter, entry to exit). Per pass = per launch / R.

Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
F_HZ = 600e6
SUMS = os.path.join(HERE, "SHA256SUMS-e202-registration")
FORECAST_SHA256 = "d1dc7679de1386f2f01ec8b9f9bbc035c0af28f4c6768b6279d7e64ce44d3656"
CONFIGS = ("trained", "random")
MIN_BURSTS = 2           # a configuration with fewer good bursts reads NO DATA (never a failed prediction)
RULES = {
    "E202-S1": {"words": "score 1, given the measured seconds: J over idle a pass within 10% (forecast / measured - 1), "
                         "each scored configuration", "tol": 0.10},
    "E202-S1T": {"words": "score 1, given the measured seconds: J with the card at rest a pass within 10%, each scored "
                          "configuration", "tol": 0.10},
    "E202-S2": {"words": "score 2, with the seconds forecast too: J over idle a pass at the frozen point within 15%, each "
                         "scored configuration", "tol": 0.15},
    "E202-S2T": {"words": "score 2, with the seconds forecast too: J with the card at rest a pass at the frozen point "
                          "(the forecast seconds and die) within 15%, each scored configuration", "tol": 0.15},
    "E202-S3": {"words": "the seconds as their own score: the mean measured kernel seconds a pass inside the frozen "
                         "two-sided band and within 15% of the point (0.85 <= mean / point <= 1.15), each scored "
                         "configuration", "tol": 0.15},
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    if not os.path.exists(SUMS):
        sys.exit("refused: no SHA256SUMS-e202-registration beside this file")
    bad, n = [], 0
    for ln in open(SUMS):
        if not ln.strip():
            continue
        h, p = ln.split(None, 1)
        p = p.strip()
        if os.path.basename(p).startswith("selftest-"):
            continue
        n += 1
        if sha(os.path.join(REPO, p)) != h:
            bad.append(p)
    if bad:
        sys.exit("refused: frozen files differ from SHA256SUMS-e202-registration: " + ", ".join(bad))
    return n


def model(frozen_check=True):
    spec = importlib.util.spec_from_file_location("forecast_e202", os.path.join(HERE, "forecast_e202.py"))
    FC = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(FC)
    M, out = FC.build()
    fj = os.path.join(HERE, "forecast-e202.json")
    if frozen_check:
        if sha(fj) != FORECAST_SHA256:
            sys.exit("refused: forecast-e202.json is not the registered file")
        if open(fj).read() != json.dumps(out, indent=1, sort_keys=True) + "\n":
            sys.exit("refused: forecast_e202.py no longer recomputes the committed forecasts")
    return FC, M, out


def load_json(p):
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return None


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def sd(xs):
    if len(xs) < 2:
        return None
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


# ---------------------------------------------------------------- the smoke gate (E202-R0)
def smoke_gate(data):
    arms = {}
    for arm in ("T-scp", "Z-scp", "T-dram", "Z-dram", "ACC"):
        h = load_json(os.path.join(data, "smoke", arm, "host-raw.json"))
        if h is None:
            arms[arm] = {"core": "NO FILE"}
            continue
        arms[arm] = {"core": h.get("core_status"), "logits": h.get("logits_status"), "status": h.get("status"),
                     "tensor_error_or": h.get("tensor_error_or"), "accuracy": h.get("accuracy")}
        if h.get("core_status") == "PASS" and h.get("logits_status") == "FAIL":
            arms[arm]["note"] = "a logits-only failure: a debug-path defect, recorded; the core checks passed"
    ok = lambda a: arms[a]["core"] == "PASS"  # noqa: E731
    if ok("T-scp") and ok("Z-scp"):
        stage, why = "scp", "the scp pair's smokes passed: the scp pair is scored"
    elif ok("T-dram") and ok("Z-dram"):
        stage, why = "dram", "the scp pair's smoke failed and the dram pair's passed: the registered fallback is scored"
    else:
        stage, why = None, "no pair passed its smoke: no burst counts (no data, never a failed forecast)"
    return {"arms": arms, "scored_stage": stage, "why": why}


# ---------------------------------------------------------------- one burst
def read_burst(d, cfg_key):
    en = load_json(os.path.join(d, "energy.json"))
    mk = load_json(os.path.join(d, "burst.json"))
    h = load_json(os.path.join(d, "host-raw.json"))
    if en is None:
        return None, "no energy.json"
    if mk is None:
        return None, "no burst.json"
    if h is None:
        return None, "no host-raw.json"
    if mk.get("set_aside"):
        return None, "set aside by the runner: %s" % mk["set_aside"]
    if not en.get("ok") or not en.get("board"):
        return None, "the reducer's hard checks: " + "; ".join(en.get("hard") or ["no board result"])
    R = mk.get("R")
    if R not in (16, 32, 48, 64, 80, 96):
        return None, "R %s is not an allowed R" % R
    if h.get("status") != "PASS" or h.get("core_status") != "PASS":
        return None, "the host's checks: status %s, core %s (%s)" % (h.get("status"), h.get("core_status"),
                                                                     h.get("first_mismatch"))
    if h.get("groups_done") != 3750 * R or h.get("pad_groups") != 0 or h.get("ops") != 3750 * R * 10892:
        return None, "the launch is not R = %d passes (groups %s, padding %s, ops %s)" % (
            R, h.get("groups_done"), h.get("pad_groups"), h.get("ops"))
    cyc = (h.get("hart0_cycles") or {}).get("max")
    if not cyc:
        return None, "no kernel cycle count"
    b = en["board"]
    return {"dir": d, "burst": mk.get("burst"), "order_index": mk.get("order_index"), "R": R,
            "j_over": b["j_per_solve"], "j_total": b["j_per_solve_total"], "t_k": cyc / F_HZ,
            "t_w": 1.0 / en["solves_per_s"], "T0": en["die_c"]["before"], "flags": list(en.get("flags") or [])}, None


# ---------------------------------------------------------------- one configuration
def score_config(M, fc, cfg, stage, bursts):
    key = f"{cfg}-{stage}"
    if len(bursts) < MIN_BURSTS:
        return {"config": key, "verdict": "NO DATA", "bursts": len(bursts),
                "note": "fewer than %d good bursts: no data, never a failed prediction" % MIN_BURSTS}
    rows = []
    for b in bursts:
        R = b["R"]
        g = M.given(cfg, stage, R, b["t_k"], b["t_w"], b["T0"])["per_pass"]
        tp = {e: M.FCmod.t_kernel(M.SM, R, e, stage) / R for e in ("point", "fast", "slow")}
        f0 = M.given(cfg, stage, R, tp["point"] * R, tp["point"] * R, M.FCmod.T0_FORECAST)["per_pass"]
        rows.append({"burst": b["burst"], "R": R, "t_k_pass": b["t_k"] / R, "t_w_pass": b["t_w"] / R, "T0": b["T0"],
                     "measured_j_over": b["j_over"] / R, "measured_j_total": b["j_total"] / R,
                     "given_j_over": g["j_over_idle"], "given_j_over_band": g["j_over_idle_band"],
                     "given_j_total": g["j_total"], "given_j_total_band": g["j_total_band"],
                     "forecast_j_over": f0["j_over_idle"], "forecast_j_total": f0["j_total"],
                     "t_point_pass": tp["point"], "t_band_pass": [tp["fast"], tp["slow"]],
                     "err_j_over": g["j_over_idle"] / (b["j_over"] / R) - 1.0,
                     "err_j_total": g["j_total"] / (b["j_total"] / R) - 1.0, "flags": b["flags"]})
    m_over, m_tot = mean([r["measured_j_over"] for r in rows]), mean([r["measured_j_total"] for r in rows])
    g_over, g_tot = mean([r["given_j_over"] for r in rows]), mean([r["given_j_total"] for r in rows])
    f_over, f_tot = mean([r["forecast_j_over"] for r in rows]), mean([r["forecast_j_total"] for r in rows])
    tk, tpnt = mean([r["t_k_pass"] for r in rows]), mean([r["t_point_pass"] for r in rows])
    tb = [mean([r["t_band_pass"][0] for r in rows]), mean([r["t_band_pass"][1] for r in rows])]
    rec = fc["configs"][key]
    out = {"config": key, "bursts": len(rows), "per_burst": rows,
           "measured_j_over_mean": m_over, "given_j_over_mean": g_over, "e_j_over": g_over / m_over - 1.0,
           "e_j_over_burst_sd": sd([r["err_j_over"] for r in rows]),
           "measured_j_total_mean": m_tot, "given_j_total_mean": g_tot, "e_j_total": g_tot / m_tot - 1.0,
           "forecast_j_over_mean": f_over, "e_j_over_forecast": f_over / m_over - 1.0,
           "forecast_j_total_mean": f_tot, "e_j_total_forecast": f_tot / m_tot - 1.0,
           "t_k_pass_mean": tk, "t_point_pass": tpnt, "t_band_pass": tb, "t_ratio": tk / tpnt,
           "t_inside_band": tb[0] <= tk <= tb[1],
           "j_over_inside_frozen_band": rec["j_over_idle_band"][0] <= m_over <= rec["j_over_idle_band"][1],
           "j_total_inside_frozen_band": rec["j_total_band"][0] <= m_tot <= rec["j_total_band"][1],
           "reported_s1t_within_5pct": abs(g_tot / m_tot - 1.0) <= 0.05,
           "per_image": {"measured_j_over": m_over / 60000.0, "measured_j_total": m_tot / 60000.0,
                         "measured_seconds": tk / 60000.0},
           "per_mac_issued_pj": {"measured_j_over": m_over / fc["per_pass_units"]["macs_issued"] * 1e12,
                                 "measured_j_total": m_tot / fc["per_pass_units"]["macs_issued"] * 1e12},
           "arms_reported": {arm: {"e_j_over": mean([M.given(cfg, stage, r["R"], r["t_k_pass"] * r["R"],
                                                             r["t_w_pass"] * r["R"], r["T0"], arm=arm)["per_pass"]["j_over_idle"]
                                                     for r in rows]) / m_over - 1.0} for arm in ("v2.1", "epi-only")},
           "flags": sorted(set(f for r in rows for f in r["flags"]))}
    out["ok_S1"] = abs(out["e_j_over"]) <= RULES["E202-S1"]["tol"]
    out["ok_S1T"] = abs(out["e_j_total"]) <= RULES["E202-S1T"]["tol"]
    out["ok_S2"] = abs(out["e_j_over_forecast"]) <= RULES["E202-S2"]["tol"]
    out["ok_S2T"] = abs(out["e_j_total_forecast"]) <= RULES["E202-S2T"]["tol"]
    out["ok_S3"] = out["t_inside_band"] and abs(out["t_ratio"] - 1.0) <= RULES["E202-S3"]["tol"]
    return out


def rule_verdict(name, cs):
    sc = [c for c in cs if c.get("verdict") != "NO DATA"]
    k = "ok_" + name.split("-")[1]
    if not sc:
        v = "NO DATA"
    elif all(c[k] for c in sc):
        v = "PASS"
    else:
        v = "FAIL"
    return {"rule": name, "words": RULES[name]["words"], "scored": len(sc), "within": sum(1 for c in sc if c[k]),
            "verdict": v, "note": None if len(sc) == len(cs) else "scored on %d of %d configurations" % (len(sc), len(cs))}


def score_day(data, M, fc):
    res = {"what": "E202 scored by the frozen scorer (score_e202.py); every number labelled as E202.md section 7 says",
           "gate": smoke_gate(data), "configs": {}, "rules": {}, "reported": {}, "not_used": []}
    by = {}
    for cfg in CONFIGS:
        for stage in ("scp", "dram"):
            key = f"{cfg}-{stage}"
            d = os.path.join(data, "bursts", key)
            ps = []
            if os.path.isdir(d):
                for b in sorted(os.listdir(d)):
                    rb, why = read_burst(os.path.join(d, b), key)
                    if rb:
                        ps.append(rb)
                    else:
                        res["not_used"].append(f"{key}/{b}: {why}")
            by[key] = ps
    st = res["gate"]["scored_stage"]
    if st is None:
        res["rules"] = {n: {"rule": n, "words": RULES[n]["words"], "verdict": "NO DATA", "scored": 0}
                        for n in RULES}
    else:
        cs = [score_config(M, fc, c, st, by[f"{c}-{st}"]) for c in CONFIGS]
        res["configs"] = {c["config"]: c for c in cs}
        res["rules"] = {n: rule_verdict(n, cs) for n in RULES}
        other = "dram" if st == "scp" else None
        if other:
            for c in CONFIGS:
                if len(by[f"{c}-{other}"]) >= MIN_BURSTS:
                    x = score_config(M, fc, c, other, by[f"{c}-{other}"])
                    res["reported"][x["config"]] = {"label": "REPORTED, never a verdict",
                                                    **{k: x[k] for k in ("e_j_over", "e_j_total", "e_j_over_forecast",
                                                                         "e_j_total_forecast", "t_ratio", "bursts")}}
    res["verdict_of_the_day"] = {n: res["rules"][n]["verdict"] for n in RULES}
    return res


# ---------------------------------------------------------------- the stand-in self-test (desk check of code)
def write_stub(day, M, fc, scen):
    """One stand-in day: smokes and bursts made from the frozen forecasts, as each scenario states."""
    if os.path.exists(day):
        shutil.rmtree(day)
    sm = scen["smoke"]
    for arm in ("T-scp", "Z-scp", "T-dram", "Z-dram", "ACC"):
        core = sm.get(arm, "PASS")
        if core == "MISSING":
            continue
        os.makedirs(os.path.join(day, "smoke", arm))
        logits = sm.get(arm + ":logits", "PASS" if arm != "ACC" else "NOT CHECKED")
        status = "PASS" if core == "PASS" and logits != "FAIL" else "FAIL"
        json.dump({"status": status, "core_status": core, "logits_status": logits, "tensor_error_or": 0},
                  open(os.path.join(day, "smoke", arm, "host-raw.json"), "w"))
    for key, spec in scen["bursts"].items():
        cfg, stage = key.split("-")
        R = spec.get("R", 96)
        tpt = M.FCmod.t_kernel(M.SM, R, "point", stage)
        for k in range(1, spec.get("n", 4) + 1):
            t = tpt * spec.get("t_factor", 1.0)
            T0 = spec.get("T0", 55.0)
            g = M.given(cfg, stage, R, t, t, T0)
            jo = g["j_over_idle"] * spec.get("e_factor", 1.0)
            jt = g["j_total"] + (jo - g["j_over_idle"])
            d = os.path.join(day, "bursts", key, "b%d" % k)
            os.makedirs(d)
            aside = "stand-in: set aside" if k <= spec.get("aside", 0) else None
            bad = k <= spec.get("host_fail", 0)
            json.dump({"ok": True, "hard": [], "flags": [], "solves": 1, "solves_per_s": 1.0 / t,
                       "board": {"j_per_solve": jo, "j_per_solve_total": jt}, "die_c": {"before": T0}},
                      open(os.path.join(d, "energy.json"), "w"))
            json.dump({"status": "FAIL" if bad else "PASS", "core_status": "FAIL" if bad else "PASS",
                       "logits_status": "NOT CHECKED", "groups_done": 3750 * R, "pad_groups": 0,
                       "ops": 3750 * R * 10892, "hart0_cycles": {"max": int(round(t * F_HZ))},
                       "first_mismatch": "stand-in" if bad else ""},
                      open(os.path.join(d, "host-raw.json"), "w"))
            json.dump({"config": key, "burst": k, "order_index": k, "R": R, "set_aside": aside},
                      open(os.path.join(d, "burst.json"), "w"))


SCENARIOS = [
    {"name": "A as forecast", "smoke": {}, "bursts": {"trained-scp": {}, "random-scp": {}, "trained-dram": {"n": 2},
                                                      "random-dram": {"n": 2}},
     "expect": {"E202-S1": "PASS", "E202-S1T": "PASS", "E202-S2": "PASS", "E202-S2T": "PASS", "E202-S3": "PASS"},
     "expect_stage": "scp"},
    {"name": "B J over idle 25% above the forecast", "smoke": {},
     "bursts": {"trained-scp": {"e_factor": 1.25}, "random-scp": {"e_factor": 1.25}},
     "expect": {"E202-S1": "FAIL", "E202-S1T": "PASS", "E202-S2": "FAIL", "E202-S2T": "PASS", "E202-S3": "PASS"},
     "expect_stage": "scp"},
    {"name": "C 30% slow, the joules following the given-seconds formula", "smoke": {},
     "bursts": {"trained-scp": {"t_factor": 1.3}, "random-scp": {"t_factor": 1.3}},
     "expect": {"E202-S1": "PASS", "E202-S1T": "PASS", "E202-S2": "PASS", "E202-S2T": "FAIL", "E202-S3": "FAIL"},
     "expect_stage": "scp"},
    {"name": "D the scp smoke fails: the dram fallback scored", "smoke": {"Z-scp": "FAIL"},
     "bursts": {"trained-dram": {}, "random-dram": {}},
     "expect": {"E202-S1": "PASS", "E202-S1T": "PASS", "E202-S2": "PASS", "E202-S2T": "PASS", "E202-S3": "PASS"},
     "expect_stage": "dram"},
    {"name": "E every smoke fails: no data", "smoke": {"T-scp": "FAIL", "T-dram": "FAIL", "Z-dram": "MISSING"},
     "bursts": {"trained-scp": {}, "random-scp": {}},
     "expect": {"E202-S1": "NO DATA", "E202-S1T": "NO DATA", "E202-S2": "NO DATA", "E202-S2T": "NO DATA",
                "E202-S3": "NO DATA"}, "expect_stage": None},
    {"name": "F a logits-only smoke failure: the gate passes", "smoke": {"T-scp:logits": "FAIL", "Z-scp:logits": "FAIL"},
     "bursts": {"trained-scp": {}, "random-scp": {}},
     "expect": {"E202-S1": "PASS", "E202-S1T": "PASS", "E202-S2": "PASS", "E202-S2T": "PASS", "E202-S3": "PASS"},
     "expect_stage": "scp"},
    {"name": "G trained short of data (3 set aside, R 64), random 10% fast and its J over idle 10% high", "smoke": {},
     "bursts": {"trained-scp": {"aside": 3}, "random-scp": {"R": 64, "t_factor": 0.9, "e_factor": 1.1}},
     "expect": {"E202-S1": "PASS", "E202-S1T": "PASS", "E202-S2": "PASS", "E202-S2T": "PASS", "E202-S3": "PASS"},
     "expect_stage": "scp"},
    {"name": "H failed host checks drop two bursts; random 25% fast", "smoke": {},
     "bursts": {"trained-scp": {"host_fail": 2}, "random-scp": {"t_factor": 0.75}},
     "expect": {"E202-S1": "PASS", "E202-S1T": "PASS", "E202-S2": "PASS", "E202-S2T": "FAIL", "E202-S3": "FAIL"},
     "expect_stage": "scp"},
]


def selftest(outdir, M, fc):
    rows, ok = [], True
    for i, sc in enumerate(SCENARIOS):
        day = os.path.join(outdir, "stub-%d" % i)
        write_stub(day, M, fc, sc)
        r = score_day(day, M, fc)
        got = r["verdict_of_the_day"]
        good = got == sc["expect"] and r["gate"]["scored_stage"] == sc["expect_stage"]
        ok &= good
        rows.append({"scenario": sc["name"], "expected": sc["expect"], "observed": got,
                     "expected_stage": sc["expect_stage"], "observed_stage": r["gate"]["scored_stage"],
                     "not_used": r["not_used"], "result": "AS EXPECTED" if good else "DIFFERS",
                     "errors": {k: {e: round(c.get(e), 6) if isinstance(c.get(e), float) else c.get(e)
                                    for e in ("e_j_over", "e_j_total", "e_j_over_forecast", "e_j_total_forecast", "t_ratio",
                                              "bursts")} for k, c in r["configs"].items()}})
        shutil.rmtree(day)
    return {"selftest": "PASS" if ok else "FAIL", "label": "desk check of code: stand-in days made from the frozen "
                                                           "forecasts, each with its verdicts stated before the run; not a measurement",
            "scenarios": rows}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--selftest")
    a = ap.parse_args(argv)
    n = check_frozen()
    FC, M, fc = model()
    M.FCmod = FC
    if a.selftest:
        os.makedirs(a.selftest, exist_ok=True)
        r = selftest(a.selftest, M, fc)
        r["frozen_files_checked"] = n
        js = json.dumps(r, indent=1, sort_keys=True) + "\n"
        open(os.path.join(HERE, "selftest-stub-e202.json"), "w").write(js)
        print(json.dumps({"selftest": r["selftest"], "scenarios": [(s["scenario"], s["result"]) for s in r["scenarios"]]}))
        return 0 if r["selftest"] == "PASS" else 1
    if not a.data:
        ap.error("DATA or --selftest")
    r = score_day(a.data, M, fc)
    r["frozen_files_checked"] = n
    js = json.dumps(r, indent=1, sort_keys=True) + "\n"
    if a.out:
        open(a.out, "w").write(js)
    print(json.dumps(r["verdict_of_the_day"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
