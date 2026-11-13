#!/usr/bin/env python3
"""E191's frozen scorer: the blind day's six configurations scored against the frozen forecasts (E191.md section 8).

    python3 -I -B tools/claims-v3/e191/score_e191.py DATA [--out FILE]   # score a day's data folder
    python3 -I -B tools/claims-v3/e191/score_e191.py --selftest-e59        # reproduce scores-v2.json's E59 rows
    /usr/bin/python3 -I -B tools/claims-v3/e191/score_e191.py --selftest-stub OUT   # a stub card (needs numpy)

It refuses unless every file of SHA256SUMS-e191-registration matches (the forecasts, this file, given()'s module). It
never refits: each pass's given-seconds forecast is forecast_e191.given() evaluated at that pass's measured kernel
seconds t_k, wall seconds a launch t_w and starting die T0; the seconds forecast is the frozen point and band.

DATA's form (E191.md section 8.1; the kit's runner writes it): DATA/passes/<config>/p<k>/ with
  energy.json     workloads/sparseparity/tools/energy_reduce.py's output for that pass (the reducer unchanged);
  host.json       what the reducer read (sparse parity: its host's own line; the ledger programs: the runner's adapter
                  of the ledger host's line into the reducer's fields: reps_done, reps_requested, launch_s,
                  launch_epoch_ms [first start, last end], status, problems);
  host-raw.json   the ledger programs only: the ledger host's own JSON line;
  pass.json       the runner's marks: config, pass (1-4), order_index, launches_requested, set_aside (null or why).
Measured, per pass: J over idle a launch = energy.json board.j_per_solve (the SP's board average over the long window
above the before bracket, less the leakage law on the measured die); J with the card at rest a launch =
board.j_per_solve_total; t_w = 1 / solves_per_s; T0 = die_c.before; t_k = the slowest minion's hpmcounter3 cycles /
600 MHz (ledger host: hart0_cycles.max; sparse parity's host: kernel.cycles_max), the burst's last launch.

Standard library only for scoring and the E59 self-test; the stub self-test imports the reducer (numpy).
SPDX-License-Identifier: Apache-2.0
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
SUMS = os.path.join(HERE, "SHA256SUMS-e191-registration")
ORDER = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
# the registered rules (E191.md section 8.3): words and thresholds as frozen
RULES = {
    "E191-S1": {"words": "score 1, given the measured seconds: J over idle a launch within 10% on at least 5 of the 6 "
                         "configurations, and the rms of the six errors at most 10%", "tol": 0.10, "need": 5, "rms": 0.10},
    "E191-S1T": {"words": "score 1, given the measured seconds: J with the card at rest a launch within 5% on at least "
                          "5 of 6", "tol": 0.05, "need": 5},
    "E191-S2": {"words": "score 2, with the seconds forecast: the measured kernel seconds inside the frozen two-sided "
                         "band and within 15% of the point, on at least 5 of 6", "tol": 0.15, "need": 5},
    "E191-S2T": {"words": "score 2, with the seconds forecast: J with the card at rest a launch, at the forecast "
                          "seconds and die, within 15% on at least 5 of 6", "tol": 0.15, "need": 5},
}
MIN_PASSES = 2          # a configuration with fewer good passes reads NO DATA (never a failed prediction)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    if not os.path.exists(SUMS):
        sys.exit("refused: no SHA256SUMS-e191-registration beside this file")
    bad, n = [], 0
    for ln in open(SUMS):
        if not ln.strip():
            continue
        h, p = ln.split(None, 1)
        p = p.strip()                   # a path from the repository's top, as the lab's other lists
        if os.path.basename(p).startswith("selftest-"):
            continue                    # the self-tests' own outputs, which a self-test rewrites (step 2 pins them)
        n += 1
        if sha(os.path.join(REPO, p)) != h:
            bad.append(p)
    if bad:
        sys.exit("refused: frozen files differ from SHA256SUMS-e191-registration: " + ", ".join(bad))
    return n


def modules():
    sys.path.insert(0, os.path.join(REPO, "tools", "ledger"))
    import ledger_v2 as LV  # noqa: E402
    spec = importlib.util.spec_from_file_location("forecast_e191", os.path.join(HERE, "forecast_e191.py"))
    FC = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(FC)
    F = LV.load_frozen(os.path.join(REPO, "docs", "reports", "data", "2026-11-12-q166-ledger-v2", "frozen-v2.json"))
    return LV, FC, F


def last_json(path):
    try:
        lines = [l for l in open(path).read().splitlines() if l.startswith("{")]
        return json.loads(lines[-1]) if lines else {}
    except (OSError, ValueError):
        return {}


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def sd(xs):
    if len(xs) < 2:
        return None
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


# ---------------------------------------------------------------- one pass
def read_pass(d, cfg):
    """A pass's measured values and its validity (E191.md section 8.2). Returns (record, why_not) ."""
    try:
        en = json.load(open(os.path.join(d, "energy.json")))
    except (OSError, ValueError):
        return None, "no energy.json"
    mk = {}
    try:
        mk = json.load(open(os.path.join(d, "pass.json")))
    except (OSError, ValueError):
        return None, "no pass.json"
    if mk.get("set_aside"):
        return None, f"set aside by the runner: {mk['set_aside']}"
    if not en.get("board") or not en.get("ok"):
        return None, "the reducer's hard checks: " + "; ".join(en.get("hard", []) or ["no board result"])
    flags = list(en.get("flags", []))
    short = False
    if cfg == "sparse-parity":
        h = last_json(os.path.join(d, "host.json"))
        cyc = (h.get("kernel") or {}).get("cycles_max")
        if h.get("status") != "PASS":
            pr = h.get("problems") or []
            if pr and all(p.startswith("reps:") for p in pr) and (h.get("reps_done") or 0) > 0:
                short = True
            else:
                return None, f"sparse parity's host: status {h.get('status')} ({'; '.join(pr)})"
        if (h.get("result") or {}).get("solved") is False:
            return None, "sparse parity's host: not solved"
    else:
        h = last_json(os.path.join(d, "host-raw.json"))
        cyc = (h.get("hart0_cycles") or {}).get("max")
        good = (h.get("records_bad") == 0 and h.get("records_ok") == h.get("participants") and h.get("mismatches") == 0
                and h.get("expect_mismatches", 0) == 0 and h.get("units") == h.get("units_expected")
                and (h.get("checked") or 0) > 0)
        if cfg == "sha256" and (h.get("expect_checked") or 0) != h.get("participants"):
            return None, "SHA-256 ran without --expect over every participant"
        if h.get("status") != "PASS":
            if good and 0 < (h.get("launches") or 0) < (mk.get("launches_requested") or 0):
                short = True             # the budget cut the burst short: scored on the launches it ran
            else:
                return None, f"the ledger host's checks: status {h.get('status')}, first mismatch {h.get('first_mismatch')}"
    if not cyc:
        return None, "no kernel cycle count"
    if short:
        flags.append("SHORT: the host's budget cut the burst short; scored on the launches it ran")
    b = en["board"]
    return {"dir": d, "pass": mk.get("pass"), "order_index": mk.get("order_index"),
            "j_over": b["j_per_solve"], "j_total": b["j_per_solve_total"], "j_raw": b.get("j_per_solve_raw"),
            "t_k": cyc / F_HZ,
            "t_w": 1.0 / en["solves_per_s"], "T0": en["die_c"]["before"], "launches": en["solves"],
            "launch_s_mean": en.get("launch_s_mean"), "rails": {k: (en.get("rails") or {}).get(k, {}).get("j_per_solve")
                                                                for k in ("minion_w", "sram_w", "noc_w", "unmetered")},
            "flags": flags}, None


# ---------------------------------------------------------------- one configuration
def score_config(key, rec, passes, LV, FC, F, arm="primary"):
    if len(passes) < MIN_PASSES:
        return {"config": key, "verdict": "NO DATA", "passes": len(passes),
                "note": f"fewer than {MIN_PASSES} good passes: no data, never a failed prediction"}
    rows = []
    for p in passes:
        g = FC.given(rec, p["t_k"], p["t_w"], p["T0"], F, LV, arm=arm)
        rows.append({"pass": p["pass"], "t_k": p["t_k"], "t_w": p["t_w"], "T0": p["T0"],
                     "measured_j_over": p["j_over"], "given_j_over": g["j_over_idle"],
                     "given_j_over_band": g["j_over_idle_band"], "measured_j_total": p["j_total"],
                     "given_j_total": g["j_total"], "given_j_total_band": g["j_total_band"],
                     "err_j_over": g["j_over_idle"] / p["j_over"] - 1.0, "err_j_total": g["j_total"] / p["j_total"] - 1.0,
                     "flags": p["flags"]})
    m_over = mean([r["measured_j_over"] for r in rows])
    f_over = mean([r["given_j_over"] for r in rows])
    m_tot = mean([r["measured_j_total"] for r in rows])
    f_tot = mean([r["given_j_total"] for r in rows])
    tk = mean([r["t_k"] for r in rows])
    s = rec["seconds"]
    a = rec["primary"] if arm == "primary" or "same_as" in rec["arms"][arm] else rec["arms"][arm]
    summ = a.get("summary") if arm != "primary" and "summary" in a else rec
    f_tot_fc = summ["j_total"]
    f_over_fc = summ["j_over_idle"]
    out = {"config": key, "arm": arm, "passes": len(rows), "per_pass": rows,
           "measured_j_over_mean": m_over, "given_j_over_mean": f_over, "e_j_over": f_over / m_over - 1.0,
           "e_j_over_pass_sd": sd([r["err_j_over"] for r in rows]),
           "measured_j_total_mean": m_tot, "given_j_total_mean": f_tot, "e_j_total": f_tot / m_tot - 1.0,
           "t_k_mean": tk, "t_point": s["point"], "t_band": s["band"], "e_t": s["point"] / tk - 1.0,
           "t_inside_band": s["band"][0] <= tk <= s["band"][1],
           "forecast_j_total_at_forecast": f_tot_fc, "e_j_total_forecast": f_tot_fc / m_tot - 1.0,
           "forecast_j_over_at_forecast": f_over_fc, "e_j_over_forecast": f_over_fc / m_over - 1.0,
           "j_over_inside_frozen_band": rec["j_over_idle_band"][0] <= m_over <= rec["j_over_idle_band"][1],
           "j_total_inside_frozen_band": rec["j_total_band"][0] <= m_tot <= rec["j_total_band"][1],
           "rails_mean": {k: mean([p["rails"][k] for p in passes if p["rails"].get(k) is not None])
                          for k in ("minion_w", "sram_w", "noc_w", "unmetered")},
           "reported_heat_crosscheck": {
               "what": "the reducer's uncorrected J a launch (all of the leakage's rise in it) beside the given-seconds "
                       "J over idle plus the ledger's own rise term (REPORTED, not scored: the headline's leakage "
                       "correction reads whole degrees, so a low-power burst can keep part of its rise; E191.md 12)",
               "measured_raw_mean": mean([p["j_raw"] for p in passes if p.get("j_raw") is not None]),
               "given_j_over_plus_heat_mean": mean([FC.given(rec, p["t_k"], p["t_w"], p["T0"], F, LV, arm=arm)["j_over_idle"]
                                                    + FC.given(rec, p["t_k"], p["t_w"], p["T0"], F, LV, arm=arm)["heat_j"]
                                                    for p in passes])},
           "flags": sorted(set(f for r in rows for f in r["flags"]))}
    out["ok_S1"] = abs(out["e_j_over"]) <= RULES["E191-S1"]["tol"]
    out["ok_S1T"] = abs(out["e_j_total"]) <= RULES["E191-S1T"]["tol"]
    out["ok_S2"] = out["t_inside_band"] and abs(tk / s["point"] - 1.0) <= RULES["E191-S2"]["tol"]
    out["ok_S2T"] = abs(out["e_j_total_forecast"]) <= RULES["E191-S2T"]["tol"]
    if key == "sparse-parity":
        sc = rec["terms"]["bytes: scratchpad"]
        out["rail_crosscheck"] = {"what": "the scratchpad term beside the SRAM rail over idle (E59's cross-check; "
                                          "reported, not scored)", "scratchpad_term_j": sc["j"],
                                  "sram_rail_j": out["rails_mean"]["sram_w"]}
    return out


def count_rule(name, cs, key_ok):
    """At least `need` of 6 within: PASS if `need` or more configurations pass; FAIL if 2 or more fail (so fewer than
    `need` can pass); otherwise NOT DECIDED (configurations without data count neither way)."""
    r = RULES[name]
    sc = [c for c in cs if c.get("verdict") != "NO DATA"]
    npass = sum(1 for c in sc if c[key_ok])
    nfail = len(sc) - npass
    if npass >= r["need"]:
        v = "PASS"
    elif nfail >= 6 - r["need"] + 1:
        v = "FAIL"
    else:
        v = "NOT DECIDED"
    out = {"rule": name, "words": r["words"], "scored": len(sc), "within": npass, "outside": nfail, "verdict": v}
    if name == "E191-S1" and sc:
        rr = rms([c["e_j_over"] for c in sc])
        out["rms_e_j_over"] = rr
        if v == "PASS" and rr > r["rms"]:
            v = "FAIL" if len(sc) >= r["need"] else "NOT DECIDED"
        elif v == "NOT DECIDED" and len(sc) >= r["need"] and rr > r["rms"]:
            v = "FAIL"
        out["verdict"] = v
    return out


def score_day(data, LV, FC, F, fc):
    res = {"what": "E191 scored by the frozen scorer (score_e191.py); every number labelled as E191.md section 8 says",
           "configs": {}, "rules": {}, "arms": {}, "not_used": []}
    by = {}
    for key in ORDER:
        d = os.path.join(data, "passes", key)
        ps = []
        if os.path.isdir(d):
            for p in sorted(os.listdir(d)):
                rp, why = read_pass(os.path.join(d, p), key)
                if rp:
                    ps.append(rp)
                else:
                    res["not_used"].append(f"{key}/{p}: {why}")
        by[key] = ps
    for arm in ("primary", "v2.1", "v2c"):
        cs = [score_config(k, fc["configs"][k], by[k], LV, FC, F, arm=arm) for k in ORDER]
        rules = {n: count_rule(n, cs, f"ok_{n.split('-')[1]}") for n in RULES}
        if arm == "primary":
            res["configs"] = {c["config"]: c for c in cs}
            res["rules"] = rules
        else:
            res["arms"][arm] = {"label": "a registered arm, REPORTED (the day's verdict is the primary's)",
                                "rules": rules, "configs": {c["config"]: {k: c.get(k) for k in (
                                    "verdict", "e_j_over", "e_j_total", "e_j_total_forecast", "passes")} for c in cs}}
    res["verdict_of_the_day"] = {n: res["rules"][n]["verdict"] for n in RULES}
    return res


# ---------------------------------------------------------------- self-test 1: E59 (scores-v2.json's rows)
def selftest_e59(LV, FC, F):
    """Reproduce scores-v2.json's 20 E59 rows from predictions-v2.json and E59's committed energy.json records, with the
    row form of tools/ledger/score_ledger_v2.py; then evaluate forecast_e191's sparse-parity evaluator (spp_eval, which
    given() calls) on each E59 load at E59's own measured seconds and die and compare it with predictions-v2.json's
    frozen given-seconds prediction."""
    D = os.path.join(REPO, "docs", "reports", "data", "2026-11-12-q166-ledger-v2")
    SP = "workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/energy"
    names = {"L1 (512,4,0.3,448)": "aifoundry3-1136-l1", "L2 (512,4,0.4,1850)": "aifoundry3-1136-l2",
             "(256,5,0.4,1925) first half": "aifoundry3-1136-f5h0",
             "(256,5,0.4,1925) second half": "aifoundry3-1136-f5h1"}
    P = json.load(open(os.path.join(D, "predictions-v2.json")))
    S = json.load(open(os.path.join(D, "scores-v2.json")))
    v1 = {r["size"]: r for r in json.load(open(os.path.join(REPO, "docs/reports/data/2026-10-26-load-model/scores.json")))[
        "loads"]["E59_sparse_parity"]["rows"]}
    want = [r for r in S["rows"] if r["load"] == "E59"]

    def row(load, name, quantity, unit, measured, msrc, forecast, band, label, v1f=None, seconds="given"):
        err = forecast - measured
        r = {"load": load, "name": name, "quantity": quantity, "unit": unit, "seconds": seconds,
             "measured": measured, "measured_source": msrc, "forecast": forecast, "forecast_band": band,
             "error": err, "error_pct": 100.0 * err / measured if measured else None,
             "inside_band": (band[0] <= measured <= band[1]) if band else None, "label": label}
        if v1f is not None:
            r["v1_forecast"] = v1f
            r["v1_error"] = v1f - measured
            r["v1_error_pct"] = 100.0 * (v1f - measured) / measured if measured else None
        return r
    got, evals = [], []
    for ld in [x for x in P["loads"] if x["load"] == "E59"]:
        en = json.load(open(os.path.join(REPO, SP, names[ld["name"]], "energy.json")))
        mw, mj, mjt = en["board"]["catalogue"]["over_idle_w"], en["board"]["j_per_solve"], en["board"]["j_per_solve_total"]
        src = f"{SP}/{names[ld['name']]}/energy.json board"
        g, f = ld["predicted"]["given_seconds"], ld["predicted"]["forecast_seconds"]
        got.append(row("E59", ld["name"], "W over idle, leak-corrected", "W", mw, src + ".catalogue.over_idle_w",
                       g["w_over_idle"], g["w_over_idle_band"], "held out, not blind",
                       v1f=v1[ld["name"]]["predicted_over_idle_w"]))
        for which, pr in (("given", g), ("forecast", f)):
            pu = pr["per_unit"]
            got.append(row("E59", ld["name"], "J a solve over idle", "J", mj, src + ".j_per_solve", pu["j_over_idle"],
                           pu["j_over_idle_band"], "held out, not blind", seconds=which,
                           v1f=v1[ld["name"]]["predicted_j_per_solve_over_idle"] if which == "given" else None))
            got.append(row("E59", ld["name"], "J a solve with the card at rest", "J", mjt, src + ".j_per_solve_total",
                           pu["j_total"], pu["j_total_band"], "held out, not blind", seconds=which))
        # the evaluator against v2's own frozen given-seconds prediction
        v = ld["variants"]["given_seconds"]
        arm = {"kind": "spp", "load": {k: x for k, x in v.items() if k != "_note"},
               "hart0_busy_cycles": ld["inputs"]["hart0_busy_cycles"], "hart1_busy_cycles": ld["inputs"]["hart1_busy_cycles"]}
        e = FC.spp_eval(arm, v["_note"]["t_kernel_s"], v["seconds"], v["die_start_c"], F, LV)
        rel = max([abs(e[k] - g[k]) / abs(g[k]) for k in ("j_over_idle", "j_total")] +
                  [abs(a - b) / abs(b) for k in ("j_over_idle_band", "j_total_band") for a, b in zip(e[k], g[k])])
        same = rel <= 1e-12        # exact under /usr/bin/python3 3.9.6, which wrote predictions-v2.json; the last
        #                            digit under 3.12+ (sum()'s rounding), so values below are shown to 12 digits
        evals.append({"run": ld["name"], "t_k": v["_note"]["t_kernel_s"], "t_w": v["seconds"], "T0": v["die_start_c"],
                      "evaluator_j_over_idle": float(f"{e['j_over_idle']:.11e}"),
                      "frozen_j_over_idle": float(f"{g['j_over_idle']:.11e}"),
                      "evaluator_j_total": float(f"{e['j_total']:.11e}"), "frozen_j_total": float(f"{g['j_total']:.11e}"),
                      "max_relative_difference_below_1e-12": same})
    rows_same = got == want
    diffs = [] if rows_same else [i for i, (a, b) in enumerate(zip(got, want)) if a != b]
    ok = rows_same and len(got) == len(want) == 20 and all(x["max_relative_difference_below_1e-12"] for x in evals)
    return {"selftest": "E59", "rows_reproduced": len(got), "rows_in_scores_v2": len(want), "rows_identical": rows_same,
            "rows_differing": diffs, "evaluator_checks": evals,
            "scores_v2_sha256": sha(os.path.join(D, "scores-v2.json")),
            "predictions_v2_sha256": sha(os.path.join(D, "predictions-v2.json")),
            "verdict": "PASS" if ok else "FAIL"}


# ---------------------------------------------------------------- self-test 2: a stub card
def selftest_stub(out_dir, LV, FC, F, fc):
    """Stub passes made by stub_e191.py (a simulated card in simulated time with energy_stub.py's 'alt' laws, which break
    the reducer's own), reduced by the unchanged reducer, then scored. Each scenario's verdicts are stated first."""
    spec = importlib.util.spec_from_file_location("stub_e191", os.path.join(HERE, "stub_e191.py"))
    ST = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ST)
    scenarios = ST.SCENARIOS
    results = []
    for sc in scenarios:
        d = os.path.join(out_dir, sc["name"])
        if os.path.isdir(d):
            shutil.rmtree(d)
        ST.make_day(d, sc, fc, F, LV, FC)
        res = score_day(d, LV, FC, F, fc)
        got = {"verdicts": res["verdict_of_the_day"],
               "no_data": sorted(k for k, c in res["configs"].items() if c.get("verdict") == "NO DATA"),
               "short_flagged": sorted(k for k, c in res["configs"].items()
                                       if any(f.startswith("SHORT") for f in c.get("flags", [])))}
        ok = (got["verdicts"] == sc["expect"]["verdicts"] and got["no_data"] == sc["expect"].get("no_data", [])
              and got["short_flagged"] == sc["expect"].get("short_flagged", []))
        errs = {k: {"e_j_over": round(c.get("e_j_over", float("nan")), 4) if c.get("e_j_over") is not None else None,
                    "e_j_total": round(c.get("e_j_total", float("nan")), 4) if c.get("e_j_total") is not None else None,
                    "e_t": round(c.get("e_t", float("nan")), 4) if c.get("e_t") is not None else None}
                for k, c in res["configs"].items()}
        results.append({"scenario": sc["name"], "what": sc["what"], "expected": sc["expect"], "got": got,
                        "errors": errs, "verdict": "PASS" if ok else "FAIL"})
    return {"selftest": "stub card", "card": "energy_stub.py CARDS['alt'] laws, simulated time (stub_e191.py)",
            "scenarios": results, "verdict": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL"}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("data", nargs="?")
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest-e59", action="store_true")
    ap.add_argument("--selftest-stub", default=None, metavar="OUT")
    a = ap.parse_args(argv)
    n = check_frozen()
    LV, FC, F = modules()
    fc = json.load(open(os.path.join(HERE, "forecast-e191.json")))
    if a.selftest_e59:
        r = selftest_e59(LV, FC, F)
        r["frozen_files_checked"] = n
    elif a.selftest_stub:
        r = selftest_stub(a.selftest_stub, LV, FC, F, fc)
        r["frozen_files_checked"] = n
    else:
        if not a.data:
            ap.error("give DATA, --selftest-e59 or --selftest-stub OUT")
        r = score_day(a.data, LV, FC, F, fc)
        r["frozen_files_checked"] = n
    js = json.dumps(r, indent=1, sort_keys=True, default=str) + "\n"
    if a.out:
        open(a.out, "w").write(js)
    print(js if (a.selftest_e59 or a.selftest_stub) else json.dumps(r["verdict_of_the_day"], indent=1))
    v = r.get("verdict")
    return 0 if v in (None, "PASS") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
