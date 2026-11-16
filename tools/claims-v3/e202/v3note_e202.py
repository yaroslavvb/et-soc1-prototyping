#!/usr/bin/env python3
"""E202's ledger v3 note (Q193, lane fix-e202, Mon 16 Nov 2026, before any E202 datum; E202.md 4.4 and verify-e202's finding 3): ledger
v3's forecast of E202's load, frozen before any E202 datum and REPORTED beside the registered v2 forecasts. The verdicts stay v2's.

    /usr/bin/python3 -I -B tools/claims-v3/e202/v3note_e202.py              write v3note-e202.json and v3note-e202.txt
    /usr/bin/python3 -I -B tools/claims-v3/e202/v3note_e202.py --check      recompute; V3NOTE CHECK PASS when equal to the committed files
    /usr/bin/python3 -I -B tools/claims-v3/e202/v3note_e202.py --score DATA [--out FILE]
                                                                            after the data commit only: the v3 readings, REPORTED

THE ROUTE: ledger v3 (tools/ledger/ledger_v3.py, frozen-v3.json; both pinned below) forecasts a ledger v2 load with its own function for
one, ledger_v3.predict_v2load(): v2's prices unchanged; rule 5 moves the forecast die to 50 C (its band 48-60 C) and adds 1.5 ms a launch
to the card at rest; rule 7 adds a governed card's base, zero on aifoundry3 (pinned at 600 MHz, no governed-base entry); in v3's own words
"Rules 1-4 and 6 have nothing to change in a v2 load". E202's load is such a load: forecast_e202.py builds it for ledger_v2.predict() from
E202's counted events, with E202's kinds rule (the tensor-data price) and the catalogue's class rows added in memory to the frozen v2
constants (forecast_e202.build_F2). This file runs predict_v2load, all seven rules on, on exactly that load and those constants (v3's
module is given E202's constants in place of the plain frozen-v2.json it would read; nothing is edited on disk), at E202's own seconds
(its cycle model, which v3 does not touch): the point at the point seconds and v3's 50 C; the J over idle band over the fast and slow
seconds; the J-with-rest band over the fast seconds at 48 C and the slow seconds at 60 C (E202's own band construction, forecast_e202.
build(), with v3's die and its band in place of v2's 55 C [52, 60]); the dram stage's band top from its dram-top arm, as E202's given().

WHAT IT SHOWS (checked here, printed): J over idle and the seconds are v2's to the last digit (v3's rules change nothing in them for a v2
load); the given-seconds readings (S1, S1T) are v2's to the last digit too (at measured seconds and die, rule 5's forecast die and launch
overhead do not enter), so v3's S1, S1T and S2 are v2's verdicts; only J with the card at rest at the frozen point differs (the 50 C die
and the 1.5 ms a launch): S2T-v3, REPORTED, is the one v3 reading that can differ from v2's.

Desk only: no card, no device, no simulator. Python's own modules; /usr/bin/python3 3.12.3 wrote the files. SPDX-License-Identifier:
Apache-2.0
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V3_PY = "tools/ledger/ledger_v3.py"
V3_FROZEN = "tools/ledger/frozen-v3.json"
PINS = {V3_PY: "339aa642f5c68af519005406661747bf5b7c4473035bca5708b738caf27ac629",     # ledger v3 as landed (50795847)
        V3_FROZEN: "4b43f510fdf2f1df1f940303247a523b0b6fb409eb853161c7621b458635014b",  # v3's freeze line
        "tools/claims-v3/e202/forecast_e202.py": "89a7616d8edbce319ed55029bb3ba073a35de35782e0731ae6851daed7bdd5a7",
        "tools/claims-v3/e202/forecast-e202.json": "d1dc7679de1386f2f01ec8b9f9bbc035c0af28f4c6768b6279d7e64ce44d3656",
        "tools/claims-v3/e202/score_e202.py": "31ac8e9029aec1c76d26d3c098a9d49e97abcd6543c0c8e6774df4a20fe92d24"}
OUT_JSON = os.path.join(HERE, "v3note-e202.json")
OUT_TXT = os.path.join(HERE, "v3note-e202.txt")
S2T_TOL = 0.15
INTERPRETER = "/usr/bin/python3 %s wrote the files (named)" % platform.python_version()


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_pins():
    bad = [p for p, h in PINS.items() if sha(os.path.join(REPO, p)) != h]
    if bad:
        sys.exit("refused: pinned files differ: " + ", ".join(bad))


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class V3:
    """E202's model (forecast_e202.Model, unchanged) and ledger v3's module, the latter reading E202's constants."""

    def __init__(self):
        check_pins()
        self.FC = load("forecast_e202", "tools/claims-v3/e202/forecast_e202.py")
        self.M = self.FC.Model()
        self.L3 = load("ledger_v3", V3_PY)
        self.L3.mods()                                       # v3's own pins on the v2 modules, checked once
        self.L3._MODS["F2"] = self.M.F2                      # E202's constants (frozen v2 + E202's kinds and class rows, in memory)
        self.F3 = self.L3.load_frozen(os.path.join(REPO, V3_FROZEN))
        c = self.F3["constants"]
        self.die, self.die_band = c["forecast_die_c"]["value"], list(c["forecast_die_c"]["band"])
        self.over = c["launch_overhead_s"]["value"]

    def launch(self, cfg, stage, R, t, T0, rules=None):
        """predict_v2load on E202's load of one launch of R passes at kernel seconds t and die T0 (the dram stage's band top from its
        dram-top arm, as forecast_e202.Model.given())."""
        M, FC = self.M, self.FC
        ld, aw = FC.make_load(M.F2, M.T, M.LS, M.KR, M.hops, cfg, stage, R, t, t, T0, M.busy, "primary")
        if aw > 0:
            ld["awake_hart_cycles"] = aw
        pr = self.L3.predict_v2load(ld, self.F3, rules=rules, die_c=T0)
        if stage == "dram":
            lt, at = FC.make_load(M.F2, M.T, M.LS, M.KR, M.hops, cfg, stage, R, t, t, T0, M.busy, "dram-top")
            if at > 0:
                lt["awake_hart_cycles"] = at
            top = self.L3.predict_v2load(lt, self.F3, rules=rules, die_c=T0)
            pr["j_over_idle_band"] = [pr["j_over_idle_band"][0], top["j_over_idle_band"][1]]
            pr["j_total_band"] = [pr["j_total_band"][0], top["j_total_band"][1]]
        return pr

    def given(self, cfg, stage, R, t_k, t_w, T0):
        """v3's given-seconds reading of one burst: predict_v2load at the measured die, with rule 5 off (its forecast die and its 1.5 ms
        a launch are forecast conditions: the measured t_w already holds the launch's overhead); awake from the measured t_k."""
        M, FC = self.M, self.FC
        ld, aw = FC.make_load(M.F2, M.T, M.LS, M.KR, M.hops, cfg, stage, R, t_k, t_w, T0, M.busy, "primary")
        if aw > 0:
            ld["awake_hart_cycles"] = aw
        rules = sorted(set(self.L3.RULES) - {"r5"})
        pr = self.L3.predict_v2load(ld, self.F3, rules=rules, die_c=T0)
        return {"j_over_idle": pr["j_over_idle"] / R, "j_total": pr["j_total"] / R}

    def forecast(self, cfg, stage, R):
        """v3's forecast of a launch of R passes, per pass: E202's build() construction with v3's die."""
        tk = {e: self.FC.t_kernel(self.M.SM, R, e, stage) for e in ("point", "fast", "slow")}
        p0 = self.launch(cfg, stage, R, tk["point"], self.die)
        f_lo = self.launch(cfg, stage, R, tk["fast"], self.die)
        f_hi = self.launch(cfg, stage, R, tk["slow"], self.die)
        T_lo = self.launch(cfg, stage, R, tk["fast"], self.die_band[0])
        T_hi = self.launch(cfg, stage, R, tk["slow"], self.die_band[1])
        return {"R": R, "seconds": {"point": tk["point"] / R, "band": [tk["fast"] / R, tk["slow"] / R]},
                "wall_s_a_launch": p0["wall_s"], "die_c": self.die, "die_band_c": self.die_band,
                "j_over_idle": p0["j_over_idle"] / R,
                "j_over_idle_band": [min(f_lo["j_over_idle_band"][0], p0["j_over_idle_band"][0]) / R,
                                     max(f_hi["j_over_idle_band"][1], p0["j_over_idle_band"][1]) / R],
                "j_total": p0["j_total"] / R,
                "j_total_band": [min(T_lo["j_total_band"][0], p0["j_total_band"][0]) / R,
                                 max(T_hi["j_total_band"][1], p0["j_total_band"][1]) / R],
                "rule7": p0["rule7"], "rules": p0["rules"]}


def r6(x):
    if isinstance(x, float):
        return float("%.6g" % x)
    if isinstance(x, dict):
        return {k: r6(v) for k, v in x.items()}
    if isinstance(x, list):
        return [r6(v) for v in x]
    return x


def build():
    V = V3()
    fc = json.load(open(os.path.join(HERE, "forecast-e202.json")))
    out = {"_what": "E202's ledger v3 note (v3note_e202.py): ledger v3's forecast of E202's load (predict_v2load, all seven rules on), per "
                    "pass of the 60,000-image training split on aifoundry3 card 0 at 600 MHz; frozen before any E202 datum; REPORTED beside "
                    "the registered v2 forecasts (forecast-e202.json), whose verdicts stand",
           "label": "forecast of code, frozen before any E202 datum, REPORTED (never a verdict); desk check of code",
           "interpreter": INTERPRETER, "pins_sha256": dict(PINS), "die_c": V.die, "die_band_c": V.die_band,
           "launch_overhead_s": V.over, "R_registered": 96, "configs": {}, "by_R": {}, "checks": {}}
    worst_over = worst_rel = worst_given = 0.0
    for key, rec in fc["configs"].items():
        cfg, stage = key.split("-")
        f = V.forecast(cfg, stage, 96)
        tp = V.FC.t_kernel(V.M.SM, 96, "point", stage)
        g2p = V.M.given(cfg, stage, 96, tp, tp, V.FC.T0_FORECAST)["per_pass"]   # v2's own point, unrounded (the registered model)
        f["v2"] = {"j_over_idle": rec["j_over_idle"], "j_over_idle_band": rec["j_over_idle_band"], "j_total": rec["j_total"],
                   "j_total_band": rec["j_total_band"], "seconds": rec["seconds"]["point"], "die_c": fc["T0_forecast_c"],
                   "die_band_c": fc["T0_band_c"]}
        f["v3_over_v2_j_total"] = f["j_total"] / rec["j_total"] - 1.0
        f["role"] = rec["role"]
        u = fc["per_pass_units"]
        f["per_image_uj"] = {"j_over_idle": f["j_over_idle"] / u["images"] * 1e6, "j_total": f["j_total"] / u["images"] * 1e6}
        f["per_mac_issued_pj"] = {"j_over_idle": f["j_over_idle"] / u["macs_issued"] * 1e12, "j_total": f["j_total"] / u["macs_issued"] * 1e12}
        out["configs"][key] = f
        worst_over = max(worst_over, abs(f["j_over_idle"] - g2p["j_over_idle"]))
        for a, b in ((f["j_over_idle"], rec["j_over_idle"]), (f["j_over_idle_band"][0], rec["j_over_idle_band"][0]),
                     (f["j_over_idle_band"][1], rec["j_over_idle_band"][1]), (f["seconds"]["point"], rec["seconds"]["point"]),
                     (f["seconds"]["band"][0], rec["seconds"]["band"][0]), (f["seconds"]["band"][1], rec["seconds"]["band"][1])):
            worst_rel = max(worst_rel, abs(a / b - 1.0))
        byr = {}
        for R in (16, 32, 48, 64, 80, 96):
            fr = f if R == 96 else V.forecast(cfg, stage, R)
            byr[str(R)] = {"j_over_idle": fr["j_over_idle"], "j_total": fr["j_total"]}
        out["by_R"][key] = byr
        # v3's given-seconds readings against v2's (forecast_e202.Model.given), at the point and at four off-point bursts
        tk = V.FC.t_kernel(V.M.SM, 96, "point", stage)
        for t_k, t_w, T0 in ((tk, tk, 55.0), (tk * 1.3, tk * 1.3 + 0.002, 58.0), (tk * 0.8, tk * 0.8 + 0.001, 51.0),
                             (tk, tk + 0.0015, 49.5), (tk * 1.1, tk * 1.12, 56.25)):
            g3 = V.given(cfg, stage, 96, t_k, t_w, T0)
            g2 = V.M.given(cfg, stage, 96, t_k, t_w, T0)["per_pass"]
            worst_given = max(worst_given, abs(g3["j_over_idle"] - g2["j_over_idle"]), abs(g3["j_total"] - g2["j_total"]))
    out["checks"] = {"j_over_idle_v3_minus_v2_point_worst": worst_over,
                     "v3_over_committed_v2_rel_worst": worst_rel,
                     "given_v3_minus_v2_worst": worst_given,
                     "how": "J over idle at the point against v2's own model (unrounded); J over idle's band and the seconds against "
                            "forecast-e202.json's six significant digits (relative); the given-seconds readings against v2's given() "
                            "at five bursts per configuration (absolute, J a pass)",
                     "reading": "J over idle, the seconds and the given-seconds readings are v2's (differences at rounding); only J with "
                                "the card at rest at the frozen point moves (v3's 50 C die and 1.5 ms a launch)"}
    return V, r6(out)


def text(o):
    L = ["E202's ledger v3 note (v3note_e202.py): ledger v3's forecast of E202's load, per pass, aifoundry3 card 0, 600 MHz; "
         "die %g C [%g, %g] (v3's rule 5), 1.5 ms a launch; REPORTED beside v2, the verdicts stay v2's; %s" % (
             o["die_c"], o["die_band_c"][0], o["die_band_c"][1], o["interpreter"]), ""]
    L.append("%-14s %-26s %-26s %-26s %9s" % ("config", "J over idle [band]", "J with rest, v3 [band]", "J with rest, v2 [band]",
                                              "v3/v2-1"))
    for k, r in o["configs"].items():
        L.append("%-14s %.4f [%.4f, %.4f] %.4f [%.4f, %.4f] %.4f [%.4f, %.4f] %+8.4f" % (
            k, r["j_over_idle"], *r["j_over_idle_band"], r["j_total"], *r["j_total_band"], r["v2"]["j_total"],
            *r["v2"]["j_total_band"], r["v3_over_v2_j_total"]))
    L += ["", "per image (uJ) and per multiply-add issued (pJ), over idle / with the card at rest (v3):"]
    for k, r in o["configs"].items():
        L.append("  %-14s %.4f / %.4f uJ   %.4f / %.4f pJ" % (k, r["per_image_uj"]["j_over_idle"], r["per_image_uj"]["j_total"],
                                                          r["per_mac_issued_pj"]["j_over_idle"], r["per_mac_issued_pj"]["j_total"]))
    c = o["checks"]
    L += ["", "checks: J over idle at the point v3 - v2 worst %.3g J; J over idle's band and the seconds v3 / v2 (six digits) - 1 worst %.3g; "
              "given-seconds readings v3 - v2 worst %.3g J a pass" % (
        c["j_over_idle_v3_minus_v2_point_worst"], c["v3_over_committed_v2_rel_worst"], c["given_v3_minus_v2_worst"]),
          "rule 7 on aifoundry3: %s" % ("applies" if any(r["rule7"].get("applies") for r in o["configs"].values()) else "zero (a pinned card)")]
    return "\n".join(L) + "\n"


def score(data, outp):
    """After the data commit: S2T-v3 (|e| <= 15% at v3's point at each counted burst's R), REPORTED, beside v2's S1, S1T, S2 and S2T, and
    v3's S1 / S1T / S2 recomputed through v3's route (equal to v2's by construction: shown). Bursts counted by the frozen scorer's own
    read_burst() and smoke_gate(), imported unchanged."""
    V, o = build()
    committed = json.load(open(OUT_JSON))
    if committed != json.loads(json.dumps(o)):
        sys.exit("refused: v3note_e202.py no longer recomputes the committed v3note-e202.json")
    SC = load("score_e202", "tools/claims-v3/e202/score_e202.py")
    gate = SC.smoke_gate(data)
    st = gate["scored_stage"]
    res = {"what": "E202's ledger v3 readings (v3note_e202.py --score), REPORTED, never a verdict; the verdicts are score_e202.py's (v2)",
           "label": "REPORTED", "gate": gate, "configs": {}, "interpreter": INTERPRETER}
    for cfg in ("trained", "random"):
        for stage in ("scp", "dram"):
            key = f"{cfg}-{stage}"
            d = os.path.join(data, "bursts", key)
            rows = []
            for b in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                rb, why = SC.read_burst(os.path.join(d, b), key)
                if rb:
                    rows.append(rb)
            if len(rows) < SC.MIN_BURSTS:
                res["configs"][key] = {"verdict": "NO DATA", "bursts": len(rows)}
                continue
            m_tot = sum(r["j_total"] / r["R"] for r in rows) / len(rows)
            m_over = sum(r["j_over"] / r["R"] for r in rows) / len(rows)
            f3_tot = sum(o["by_R"][key][str(r["R"])]["j_total"] for r in rows) / len(rows)
            f3_over = sum(o["by_R"][key][str(r["R"])]["j_over_idle"] for r in rows) / len(rows)
            g3 = [V.given(cfg, stage, r["R"], r["t_k"], r["t_w"], r["T0"]) for r in rows]
            e = {"S1-v3 (= v2's S1)": sum(g["j_over_idle"] for g in g3) / len(g3) / m_over - 1.0,
                 "S1T-v3 (= v2's S1T)": sum(g["j_total"] for g in g3) / len(g3) / m_tot - 1.0,
                 "S2-v3 (= v2's S2)": f3_over / m_over - 1.0, "S2T-v3": f3_tot / m_tot - 1.0}
            res["configs"][key] = {"bursts": len(rows), "scored_stage": stage == st, "errors": e,
                                   "S2T-v3 within 15%": abs(e["S2T-v3"]) <= S2T_TOL, "label": "REPORTED"}
    js = json.dumps(r6(res), indent=1, sort_keys=True) + "\n"
    if outp:
        open(outp, "w").write(js)
    print(js)
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--score")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.score:
        return score(a.score, a.out)
    V, out = build()
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    tx = text(out)
    if a.check:
        ok = os.path.exists(OUT_JSON) and open(OUT_JSON).read() == js and open(OUT_TXT).read() == tx
        c = out["checks"]
        good = ok and c["j_over_idle_v3_minus_v2_point_worst"] <= 1e-12 and c["v3_over_committed_v2_rel_worst"] <= 5e-6 \
            and c["given_v3_minus_v2_worst"] <= 1e-12
        print("V3NOTE CHECK " + ("PASS" if good else "FAIL") + ": recomputed equals committed %s; J over idle at the point v3-v2 %.3g J; "
              "band and seconds against six digits %.3g; given %.3g J" % (ok, c["j_over_idle_v3_minus_v2_point_worst"],
                                                                          c["v3_over_committed_v2_rel_worst"], c["given_v3_minus_v2_worst"]))
        return 0 if good else 1
    open(OUT_JSON, "w").write(js)
    open(OUT_TXT, "w").write(tx)
    print(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
