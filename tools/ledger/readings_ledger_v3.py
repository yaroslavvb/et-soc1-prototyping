#!/usr/bin/env python3
"""Ledger v3's readings: the round trip to v2 (v3 with all seven rules off against E189's, E191's and E194's frozen v2
forecasts and scorers) and the POST HOC readings on the blind days (in sample, held out across cards, one program left
out, no blind-day constant, prices from the other card, each rule alone and each left out, E191's third session as a
REPORTED repeat, E194 with and without rule 7).

    /usr/bin/python3 -I -B tools/ledger/readings_ledger_v3.py --out DIR     # DIR is required: never a default
                                                                             # (compare DIR with the committed files)

Writes DIR/roundtrip-v3.json and .txt, DIR/readings-v3.json and .txt. Every reading of E189, E191 and E194 here is POST
HOC: v3 was written after their data, two of its constants were fitted on E189's and E191's, and its rule 7 took its
form after E194's. The blind scores stand; nothing here changes a frozen number.

THE SCORES, E189's registered rules (tools/claims-v3/e189/score_e189.py), applied per pass and averaged: S1 J over idle
a launch given the measured seconds (within 10% on at least n-1, and an rms of 10% or less); S1T J with the card at rest
given the measured seconds and die (5%); S2 the seconds forecast, E189's registered test in full (score_e189.py ok_S2:
the mean t_k inside the forecast's two-sided band AND 0.85 <= mean t_k / point <= 1.15; the 15% test alone is also
counted, as S2-15, a reading only); S2T J with the card at rest at the forecast seconds and die (15%); S2I J over idle at
the forecast seconds (15%; differs from S1 only where J follows t). An error is the mean of the forecasts over the passes
/ the mean measured - 1. Sparse parity: v3 = v2 for S1, S1T and S2 (the frozen scorers' errors and band test); its S2T at
v3's die from predict_v2load(). A later scorer (E201's) registers its own rules: it does not import verdicts() unread.

Floats in the written files are rounded to 6 significant digits. Desk only. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import ledger_v3 as V3  # noqa: E402
import measured_ledger_v3 as M  # noqa: E402
import programs_ledger_v3 as PR  # noqa: E402

DATA_DIR = os.path.join(REPO, "docs/reports/data/2026-11-16-ledger-v3")
PLAIN = ("copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled")
SCALAR = ("sha256", "sort-sorted", "sort-shuffled")
COPIES = ("copy-zeros", "copy-random")
FORECAST = {"E189": "tools/claims-v3/e189/forecast-e189.json", "E191s2": "tools/claims-v3/e191/forecast-e191.json",
            "E191s3": "tools/claims-v3/e191/forecast-e191.json", "E194": "tools/claims-v3/e194/forecast-e194.json"}
SCORES = {"E189": "scores-e189.json", "E191s2": "scores-e191.json", "E191s3": "scores-e191-s3.json",
          "E194": "scores-e194.json"}
OTHER = {"E189": "E191s2", "E191s2": "E189"}
SIG = 6


def r6(x):
    if isinstance(x, dict):
        return {k: r6(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r6(v) for v in x]
    if isinstance(x, float):
        if x == 0.0 or not math.isfinite(x):
            return x
        return float(f"{x:.{SIG - 1}e}")
    return x


def rel(p):
    return os.path.join(REPO, p)


def scores_file(day):
    return json.load(open(rel(os.path.join(M.DATA, M.DAYS[day]["dir"], SCORES[day]))))


# ------------------------------------------------------------------ one configuration scored
def score(prog, F3, meas_cfg, rules=None, f_mhz=None, die_c=None, c_br=None, rdram=None, prices_from=None,
          share7=None, j_idle7=None, given_launches=True):
    """v3 (with these rules) against one configuration's passes, by E189's rules."""
    p = V3.predict(prog, F3, rules=rules, f_mhz=f_mhz, die_c=die_c, c_br=c_br, rdram=rdram, prices_from=prices_from,
                   share7=share7, j_idle7=j_idle7)
    gj, gt = [], []
    for ps in meas_cfg["passes"]:
        pr = prog
        if given_launches and prog.get("governor"):
            pr = dict(prog, governor={"launches_a_burst": ps["launches"]})
        g = V3.given(pr, F3, ps["t_k"], ps["t_w"], ps["T0"], rules=rules, f_mhz=f_mhz, c_br=c_br, rdram=rdram,
                     prices_from=prices_from, share7=share7, j_idle7=j_idle7)
        gj.append(g["j_over_idle"])
        gt.append(g["j_total"])
    m = meas_cfg["mean"]
    t = p["seconds"]["point"]
    tb = p["seconds"]["band"]
    return {"t_point": t, "t_band": tb, "j_over_forecast": p["j_over_idle"], "j_total_forecast": p["j_total"],
            "j_over_given": st.mean(gj), "j_total_given": st.mean(gt),
            "e_t": t / m["t_k"] - 1.0, "S2_ratio": m["t_k"] / t, "S2_in_band": tb[0] <= m["t_k"] <= tb[1],
            "e_S1": st.mean(gj) / m["j_over"] - 1.0, "e_S1T": st.mean(gt) / m["j_total"] - 1.0,
            "e_S2T": p["j_total"] / m["j_total"] - 1.0, "e_S2I": p["j_over_idle"] / m["j_over"] - 1.0,
            "rule7": p["rule7"], "level": p["level"], "outside_v3": p["outside_v3"],
            "terms": {k: v["j"] for k, v in p["terms"].items()}}


def ok_s2(e):
    """E189's registered S2 for one configuration (score_e189.py ok_S2): the mean t_k inside the forecast's two-sided band
    and within 15% of the point. A row without its band test reads None (not scored)."""
    if e.get("S2_ratio") is None or e.get("S2_in_band") is None:
        return None
    return bool(e["S2_in_band"]) and 0.85 <= e["S2_ratio"] <= 1.15


def verdicts(rows):
    """E189's rules over the configurations given (each a dict of errors). S2 is E189's test in full (the band and 15%);
    S2-15 counts the 15% test alone (a reading, never a verdict of record)."""
    n = len(rows)
    need = n - 1 if n >= 5 else n
    s1 = [abs(e["e_S1"]) <= 0.10 for e in rows]
    rms = math.sqrt(sum(e["e_S1"] ** 2 for e in rows) / n)
    out = {"n": n, "S1": {"pass": sum(s1), "of": n, "rms": rms}}
    out["S1"]["verdict"] = "PASS" if sum(s1) >= need and rms <= 0.10 else "FAIL"
    for k, get, test in (("S1T", lambda e: e.get("e_S1T"), lambda x: abs(x) <= 0.05),
                         ("S2", ok_s2, lambda x: x),
                         ("S2-15", lambda e: e.get("S2_ratio"), lambda x: 0.85 <= x <= 1.15),
                         ("S2T", lambda e: e.get("e_S2T"), lambda x: abs(x) <= 0.15),
                         ("S2I", lambda e: e.get("e_S2I"), lambda x: abs(x) <= 0.15)):
        ok = [test(get(e)) for e in rows if get(e) is not None]
        m = len(ok)
        out[k] = {"pass": sum(ok), "of": m, "verdict": "PASS" if m and sum(ok) >= (m - 1 if m >= 5 else m) else "FAIL"}
    out["S2"]["test"] = "E189's registered S2: the mean t_k inside the two-sided band and within 15% of the point"
    out["S2-15"]["test"] = "the 15% test alone (a reading only)"
    return out


def spp_row(day, F3, rules=None, extra=None):
    """Sparse parity (v3 = v2 but for rules 5 and 7): S1, S1T, S2 from the frozen scorer; S2T at v3's die and wall seconds."""
    sc = scores_file(day)["configs"]["sparse-parity"]
    fc = json.load(open(rel(FORECAST[day])))["configs"]["sparse-parity"] if day in FORECAST else None
    meas = M.read_day(day)["sparse-parity"]
    out = {"e_S1": sc["e_j_over"], "e_S1T": sc["e_j_total"], "S2_ratio": 1.0 / (1.0 + sc["e_t"]), "e_t": sc["e_t"],
           "S2_in_band": sc["t_inside_band"],
           "source": "the frozen scorer's errors and band test (v3 = v2 on S1, S1T and S2)"}
    if fc:
        p = V3.predict_v2load(fc["primary"]["load"], F3, rules=rules)
        out["e_S2T"] = p["j_total"] / meas["mean"]["j_total"] - 1.0
        out["e_S2I"] = p["j_over_idle"] / meas["mean"]["j_over"] - 1.0
        out["j_total_forecast"] = p["j_total"]
    return out


# ------------------------------------------------------------------ the round trip
TOL = 5e-6     # the frozen forecast files keep 6 significant digits: a value rounded there is off by at most 5e-6


def same6(a, b):
    """a (v3, full precision) against b (a frozen file's value, 6 significant digits): equal after rounding a the same way,
    or within the rounding's bound, 5e-6 relative."""
    if isinstance(b, (int, float)) and isinstance(a, (int, float)):
        d = abs(a - b) / abs(b) if b else abs(a)
        return r6(float(a)) == b or d <= TOL, d
    return False, None


def roundtrip(F3):
    out = {"label": "v3 with all seven rules off against the frozen v2 forecasts and scorers (desk check of code)",
           "days": {}}
    worst = 0.0
    fails = []
    for day, card, f_mhz, die_band in (("E189", "aifoundry3", 600.0, None), ("E191s2", "aifoundry1-c1", 600.0, None),
                                       ("E194", "aifoundry2", 800.0, [46.0, 57.0])):
        FC = json.load(open(rel(FORECAST[day])))["configs"]
        progs = PR.blind_day_programs(card, f_mhz=f_mhz)
        sc = scores_file(day)["configs"]
        meas = M.read_day(day)
        rows = {}
        for cfg in PLAIN:
            p = V3.predict(progs[cfg], F3, rules=V3.NONE, f_mhz=f_mhz)
            if die_band:
                lv, le, F2 = V3.mods()
                tb = p["seconds"]["band"]
                rest, heat = V3.rest_and_heat(card, p["seconds"]["point"], tb, p["j_over_idle"], p["j_over_idle_band"],
                                              55.0, die_band)
                p["j_total_band"] = [rest["band"][0] + heat["band"][0] + p["j_over_idle_band"][0],
                                     rest["band"][1] + heat["band"][1] + p["j_over_idle_band"][1]]
            f = FC[cfg]
            ins_key = "instructions by class"
            byt = (f["terms"]["bytes: DRAM read"]["j"] + f["terms"]["bytes: DRAM write-back"]["j"]) if cfg in COPIES \
                else f["terms"]["bytes: L2"]["j"]
            mine_b = sum(v["j"] for k, v in p["terms"].items() if k.startswith("bytes"))
            pairs = {"seconds.point": (p["seconds"]["point"], f["seconds"]["point"]),
                     "seconds.band[0]": (p["seconds"]["band"][0], f["seconds"]["band"][0]),
                     "seconds.band[1]": (p["seconds"]["band"][1], f["seconds"]["band"][1]),
                     "j_over_idle": (p["j_over_idle"], f["j_over_idle"]),
                     "j_over_idle_band[0]": (p["j_over_idle_band"][0], f["j_over_idle_band"][0]),
                     "j_over_idle_band[1]": (p["j_over_idle_band"][1], f["j_over_idle_band"][1]),
                     "j_total": (p["j_total"], f["j_total"]),
                     "j_total_band[0]": (p["j_total_band"][0], f["j_total_band"][0]),
                     "j_total_band[1]": (p["j_total_band"][1], f["j_total_band"][1]),
                     "terms.instructions": (p["terms"]["instructions"]["j"], f["terms"][ins_key]["j"]),
                     "terms.bytes": (mine_b, byt)}
            # the given-seconds function against the frozen scorer, pass by pass
            for i, ps in enumerate(meas[cfg]["passes"]):
                g = V3.given(progs[cfg], F3, ps["t_k"], ps["t_w"], ps["T0"], rules=V3.NONE, f_mhz=f_mhz)
                fp = sc[cfg]["per_pass"][i]
                pairs[f"given_j_over.p{i + 1}"] = (g["j_over_idle"], fp["given_j_over"])
                pairs[f"given_j_total.p{i + 1}"] = (g["j_total"], fp["given_j_total"])
            res = {}
            for k, (a, b) in pairs.items():
                ok, d = same6(a, b)
                if k.startswith("given"):        # the scorer computed these from the forecast file's 6-digit J over idle
                    ok = d <= TOL
                res[k] = {"v3_rules_off": a, "frozen": b, "same": ok, "rel_diff": d}
                worst = max(worst, d if d is not None else 0.0)
                if not ok:
                    fails.append(f"{day}/{cfg}/{k}")
            rows[cfg] = res
        # sparse parity: the frozen load through predict_v2load() with the rules off
        spl = FC["sparse-parity"]["primary"]["load"]
        q = V3.predict_v2load(spl, F3, rules=V3.NONE)
        res = {}
        for k, (a, b) in {"j_over_idle": (q["j_over_idle"], FC["sparse-parity"]["j_over_idle"]),
                          "j_total": (q["j_total"], FC["sparse-parity"]["j_total"])}.items():
            ok, d = same6(a, b)
            res[k] = {"v3_rules_off": a, "frozen": b, "same": ok, "rel_diff": d}
            worst = max(worst, d)
            if not ok:
                fails.append(f"{day}/sparse-parity/{k}")
        rows["sparse-parity"] = res
        out["days"][day] = {"card": card, "f_mhz": f_mhz, "forecast_file": FORECAST[day], "rows": rows}
    out["checked"] = sum(len(r) for d in out["days"].values() for r in d["rows"].values())
    out["failed"] = fails
    out["worst_rel_diff"] = worst
    out["verdict"] = "ROUND TRIP PASS" if not fails else "ROUND TRIP FAIL"
    return out


# ------------------------------------------------------------------ the post hoc readings
def day_rows(day, F3, card, f_mhz=600.0, **kw):
    progs = PR.blind_day_programs(card, f_mhz=f_mhz)
    meas = M.read_day(day)
    rows = {cfg: score(progs[cfg], F3, meas[cfg], f_mhz=f_mhz, **kw) for cfg in PLAIN}
    return rows, progs, meas


def readings(F3):
    C = F3["constants"]
    out = {"label": "POST HOC readings of ledger v3 (the blind scores stand)", "frozen_v3_sha256": V3.sha256_file(V3.FROZEN_V3),
           "readings": {}}
    R = out["readings"]
    cards = {"E189": "aifoundry3", "E191s2": "aifoundry1-c1", "E191s3": "aifoundry1-c1"}
    # (a) in sample, and held out across cards (c_br and R_dram from the other card only)
    for name, kw_of in (("in sample (the frozen constants)", lambda d: {}),
                        ("held out across cards (c_br and R_dram from the other card only)", lambda d: {
                            "c_br": C["c_br_hart_cycles"]["fit"]["per_card"][OTHER[d]],
                            "rdram": C["r_dram_b_per_s"]["value"][cards[OTHER[d]]]})):
        R[name] = {}
        for d in ("E189", "E191s2"):
            rows, _, _ = day_rows(d, F3, cards[d], **kw_of(d))
            rows["sparse-parity"] = spp_row(d, F3)
            R[name][d] = {"rows": rows, "verdicts_six": verdicts(list(rows.values())),
                          "verdicts_five_plain": verdicts([rows[c] for c in PLAIN])}
    # (b) each scalar program with c_br fitted on the other two
    R["one program left out (c_br from the other two)"] = {}
    for d in ("E189", "E191s2"):
        progs = PR.blind_day_programs(cards[d])
        meas = M.read_day(d)
        R["one program left out (c_br from the other two)"][d] = {
            cfg: dict(score(progs[cfg], F3, meas[cfg], c_br=C["c_br_hart_cycles"]["fit"]["leave_one_program_out"][cfg]),
                      c_br=C["c_br_hart_cycles"]["fit"]["leave_one_program_out"][cfg]) for cfg in SCALAR}
    # (c) each copy, R_dram from the other data column on the other card
    R["each copy, R_dram from the other copy on the other card"] = {}
    for d in ("E189", "E191s2"):
        progs = PR.blind_day_programs(cards[d])
        meas = M.read_day(d)
        mo = M.read_day(OTHER[d])
        rr = {}
        for cfg in COPIES:
            oc = "copy-random" if cfg == "copy-zeros" else "copy-zeros"
            rd = 3.0 * progs[cfg]["copy"]["bytes"] / mo[oc]["mean"]["t_k"]
            rr[cfg] = dict(score(progs[cfg], F3, meas[cfg], rdram=rd), rdram=rd)
        R["each copy, R_dram from the other copy on the other card"][d] = rr
    # (d) no blind-day constant
    R["no blind-day constant (c_br a priori, R_dram twice the store stream)"] = {}
    for d in ("E189", "E191s2"):
        rd = C["r_dram_b_per_s"]["fit"]["a_priori_fast_end"][cards[d]]
        rows, _, _ = day_rows(d, F3, cards[d], c_br=C["c_br_hart_cycles"]["a_priori"]["value"], rdram=rd)
        R["no blind-day constant (c_br a priori, R_dram twice the store stream)"][d] = {
            "rows": rows, "verdicts_five_plain": verdicts([rows[c] for c in PLAIN])}
    # (e) stress: every card-keyed price from the other card
    R["stress: every price of rules 2-4 from the other card"] = {}
    for d in ("E189", "E191s2"):
        rows, _, _ = day_rows(d, F3, cards[d], prices_from=cards[OTHER[d]])
        R["stress: every price of rules 2-4 from the other card"][d] = {
            "rows": rows, "verdicts_five_plain": verdicts([rows[c] for c in PLAIN])}
    # (f) each rule alone on v2, and v3 less each rule
    R["each rule alone and each left out"] = {}
    for d, card, f in (("E189", "aifoundry3", 600.0), ("E191s2", "aifoundry1-c1", 600.0), ("E194", "aifoundry2", 800.0)):
        progs = PR.blind_day_programs(card, f_mhz=f)
        meas = M.read_day(d)
        dd = {}
        variants = [("v2", V3.NONE), ("v3", V3.ALL)] + [(f"v2 + {r}", frozenset([r])) for r in V3.RULES] + \
                   [(f"v3 - {r}", V3.ALL - {r}) for r in V3.RULES]
        for vname, rules in variants:
            rows = {cfg: score(progs[cfg], F3, meas[cfg], rules=rules, f_mhz=f) for cfg in PLAIN}
            dd[vname] = {cfg: {k: rows[cfg][k] for k in ("e_t", "e_S1", "e_S1T", "e_S2T", "e_S2I")} for cfg in PLAIN}
            dd[vname]["rms_S1_five"] = math.sqrt(sum(rows[c]["e_S1"] ** 2 for c in PLAIN) / 5)
            dd[vname]["rms_t_five"] = math.sqrt(sum(rows[c]["e_t"] ** 2 for c in PLAIN) / 5)
        R["each rule alone and each left out"][d] = dd
    # (g) E191's third session (REPORTED repeat)
    rows, _, _ = day_rows("E191s3", F3, "aifoundry1-c1")
    rows["sparse-parity"] = spp_row("E191s3", F3)
    R["E191's third session (REPORTED repeat)"] = {"rows": rows, "verdicts_six": verdicts(list(rows.values()))}
    # (h) E194: aifoundry2 under its governor at 800 MHz
    R["E194 (aifoundry2, 800 MHz)"] = e194(F3)
    return out


def e194(F3):
    C = F3["constants"]
    FC = json.load(open(rel(FORECAST["E194"])))
    rep = FC["readings_reported"]["configs"]
    progs = PR.blind_day_programs("aifoundry2", f_mhz=800.0)
    meas = M.read_day("E194")
    v2f = V3.v2_factor("aifoundry2", 800.0)
    dB = C["governed_base_w"]["value"]["aifoundry2"]["B"]["800"] - C["governed_base_w"]["value"]["aifoundry2"]["B"]["600"]
    out = {"v2_factor_800": v2f, "delta_base_w": dB, "rows": {}}
    for cfg in PLAIN:
        p, m = progs[cfg], meas[cfg]
        no7 = score(p, F3, m, rules=V3.ALL - {"r7"}, f_mhz=800.0)
        r7 = score(p, F3, m, rules=V3.ALL, f_mhz=800.0)
        r7_55 = score(p, F3, m, rules=V3.ALL, f_mhz=800.0, die_c=55.0)
        # the design's arithmetic (Q193 fix5-design): the climb's share as E194's frozen reading gives it (computed with
        # v2's seconds), the copies' J at the idle clock taken equal to their J at 800 MHz
        share = rep[cfg]["climb"]["share_of_the_burst_work_at_600_mhz"]
        jid = no7["j_over_forecast"] if cfg in COPIES else None
        des = V3.predict(p, F3, rules=V3.ALL, f_mhz=800.0, share7=share, j_idle7=jid)
        # the form E194.md registered before its data: the base over each launch's whole forecast seconds, no climb
        reg = no7["j_over_forecast"] + dB * no7["t_point"]
        # the lines priced at (V800/V600)^2 as well (verify5's reading), with rule 7
        lines_j = no7["terms"].get("bytes: lines past the L1", 0.0)
        s7 = r7["rule7"].get("share_at_idle_clock", 0.0)
        scaled = r7["j_over_forecast"] + (1.0 - s7) * lines_j * (v2f - 1.0)
        mm = m["mean"]
        out["rows"][cfg] = {
            "measured": {k: mm[k] for k in ("t_k", "t_w", "T0", "j_over", "j_total", "launches")},
            "v2_frozen": {"t": FC["configs"][cfg]["seconds"]["point"], "j_over": FC["configs"][cfg]["j_over_idle"]},
            "v3_without_r7": {k: no7[k] for k in ("t_point", "e_t", "e_S1", "e_S1T", "e_S2T", "e_S2I")},
            "v3_with_r7": {k: r7[k] for k in ("t_point", "e_t", "e_S1", "e_S1T", "e_S2T", "e_S2I")} | {
                "share_at_600": r7["rule7"].get("share_at_idle_clock"), "e_S2T_at_55C": r7_55["e_S2T"]},
            "design_arithmetic_with_r7": {"j_over": des["j_over_idle"], "e_S2I": des["j_over_idle"] / mm["j_over"] - 1.0,
                                          "share_at_600": share},
            "registered_form_v3": {"j_over": reg, "e_S2I": reg / mm["j_over"] - 1.0},
            "registered_form_v2": {"j_over": rep[cfg]["with_e136_base"]["j_over_idle"],
                                   "e_S2I": rep[cfg]["with_e136_base"]["j_over_idle"] / mm["j_over"] - 1.0},
            "lines_scaled_with_r7": {"j_over": scaled, "e_S2I": scaled / mm["j_over"] - 1.0}}
    # sparse parity: v2's load at 800 MHz, rule 7 with E194's own load at 600 MHz (its frozen reading) at the idle clock
    spl = FC["configs"]["sparse-parity"]["primary"]["load"]
    ms = meas["sparse-parity"]["mean"]
    q7 = V3.predict_v2load(spl, F3, rules=V3.ALL, launches_a_burst=PR.K_E189["sparse-parity"],
                           j_idle7=rep["sparse-parity"]["at_600_mhz"]["j_over_idle"])
    q0 = V3.predict_v2load(spl, F3, rules=V3.ALL - {"r7"})
    out["rows"]["sparse-parity"] = {
        "measured": {k: ms[k] for k in ("t_k", "t_w", "T0", "j_over", "j_total")},
        "v3_without_r7": {"e_S2I": q0["j_over_idle"] / ms["j_over"] - 1.0, "e_t": spl["seconds"] / ms["t_k"] - 1.0},
        "v3_with_r7": {"e_S2I": q7["j_over_idle"] / ms["j_over"] - 1.0, "share_at_600": q7["rule7"].get("share_at_idle_clock"),
                       "e_S2T": q7["j_total"] / ms["j_total"] - 1.0}}
    return out


# ------------------------------------------------------------------ text
def pct(x):
    return "   n/a" if x is None else f"{100 * x:+6.1f}%"


def text_roundtrip(rt):
    L = [f"ledger v3 ROUND TRIP: v3 with all seven rules off against the frozen v2 forecasts and the frozen scorers' given "
         f"values, each equal at the files' 6 significant digits (within 5e-6 relative): {rt['verdict']}; {rt['checked']} "
         f"numbers, worst relative difference {rt['worst_rel_diff']:.2e}", ""]
    for d, v in rt["days"].items():
        n = sum(len(r) for r in v["rows"].values())
        bad = [f"{c}/{k}" for c, r in v["rows"].items() for k, x in r.items() if not x["same"]]
        L.append(f"  {d} ({v['card']}, {v['f_mhz']:.0f} MHz, {v['forecast_file']}): {n} numbers, "
                 f"{'all the same' if not bad else 'DIFFER: ' + ', '.join(bad)}")
    return "\n".join(L) + "\n"


def text_readings(rd):
    R = rd["readings"]
    L = ["ledger v3 readings (POST HOC: v3 was written after these days' data; the blind scores stand)",
         f"frozen-v3.json sha256 {rd['frozen_v3_sha256']}", ""]
    for name in ("in sample (the frozen constants)", "held out across cards (c_br and R_dram from the other card only)"):
        L.append(f"[{name}]  errors: seconds; S1 (J over idle given t); S1T (J at rest given t, T0); S2T (at v3's t "
                 f"and 50 C); S2I")
        for d, v in R[name].items():
            for cfg, e in v["rows"].items():
                L.append(f"  {d:7s} {cfg:14s} t {pct(e.get('e_t'))}  S1 {pct(e.get('e_S1'))}  S1T {pct(e.get('e_S1T'))}  "
                         f"S2T {pct(e.get('e_S2T'))}  S2I {pct(e.get('e_S2I'))}")
            vv = v["verdicts_six"]
            L.append(f"  {d:7s} six: S1 {vv['S1']['pass']}/6 rms {100 * vv['S1']['rms']:.1f}% ({vv['S1']['verdict']}); "
                     f"S1T {vv['S1T']['pass']}/{vv['S1T']['of']}; S2 (band and 15%) {vv['S2']['pass']}/{vv['S2']['of']}; "
                     f"S2T {vv['S2T']['pass']}/{vv['S2T']['of']}")
        L.append("")
    L.append("[one program left out: c_br from the other two]")
    for d, v in R["one program left out (c_br from the other two)"].items():
        for cfg, e in v.items():
            L.append(f"  {d:7s} {cfg:14s} c_br {e['c_br']:.3f}  t {pct(e['e_t'])}  S2T {pct(e['e_S2T'])}")
    L.append("")
    L.append("[each copy: R_dram from the other copy on the other card]")
    for d, v in R["each copy, R_dram from the other copy on the other card"].items():
        for cfg, e in v.items():
            L.append(f"  {d:7s} {cfg:14s} R_dram {e['rdram'] / 1e9:.3f} GB/s  t {pct(e['e_t'])}  S1 {pct(e['e_S1'])}  "
                     f"S2T {pct(e['e_S2T'])}")
    L.append("")
    for name in ("no blind-day constant (c_br a priori, R_dram twice the store stream)",
                 "stress: every price of rules 2-4 from the other card"):
        L.append(f"[{name}]")
        for d, v in R[name].items():
            for cfg, e in v["rows"].items():
                L.append(f"  {d:7s} {cfg:14s} t {pct(e['e_t'])}  S1 {pct(e['e_S1'])}  S2T {pct(e['e_S2T'])}")
            vv = v["verdicts_five_plain"]
            L.append(f"  {d:7s} five: S1 {vv['S1']['pass']}/5 (rms {100 * vv['S1']['rms']:.1f}%); S2 (band and 15%) "
                     f"{vv['S2']['pass']}/5; S2T {vv['S2T']['pass']}/5")
        L.append("")
    L.append("[each rule alone on v2, and v3 less each rule: rms over the five plain programs of S1 and of seconds]")
    for d, dd in R["each rule alone and each left out"].items():
        L.append(f"  {d}: " + "; ".join(f"{k} S1 {100 * v['rms_S1_five']:.1f}% t {100 * v['rms_t_five']:.1f}%"
                                        for k, v in dd.items()))
    L.append("")
    L.append("[E191's third session, REPORTED repeat]")
    for cfg, e in R["E191's third session (REPORTED repeat)"]["rows"].items():
        L.append(f"  {cfg:14s} t {pct(e.get('e_t'))}  S1 {pct(e.get('e_S1'))}  S1T {pct(e.get('e_S1T'))}  S2T {pct(e.get('e_S2T'))}")
    L.append("")
    E = R["E194 (aifoundry2, 800 MHz)"]
    L.append(f"[E194, aifoundry2 under its governor at 800 MHz; rule 7's base {E['delta_base_w']:.3f} W, v2(800) "
             f"{E['v2_factor_800']:.4f}]  J over idle at the forecast seconds unless named")
    for cfg, e in E["rows"].items():
        if cfg == "sparse-parity":
            L.append(f"  {cfg:14s} v3 without r7 {pct(e['v3_without_r7']['e_S2I'])}; with r7 {pct(e['v3_with_r7']['e_S2I'])} "
                     f"(share at 600 MHz {e['v3_with_r7']['share_at_600']:.3f})")
            continue
        L.append(f"  {cfg:14s} t {pct(e['v3_without_r7']['e_t'])} | S1 without r7 {pct(e['v3_without_r7']['e_S1'])}, with "
                 f"r7 {pct(e['v3_with_r7']['e_S1'])} | S2I with r7 {pct(e['v3_with_r7']['e_S2I'])}; the design's "
                 f"arithmetic {pct(e['design_arithmetic_with_r7']['e_S2I'])}; the registered form v3 "
                 f"{pct(e['registered_form_v3']['e_S2I'])}, v2 {pct(e['registered_form_v2']['e_S2I'])}; lines scaled "
                 f"{pct(e['lines_scaled_with_r7']['e_S2I'])} | S1T with r7 {pct(e['v3_with_r7']['e_S1T'])}; S2T at 50 C "
                 f"{pct(e['v3_with_r7']['e_S2T'])}, at 55 C {pct(e['v3_with_r7']['e_S2T_at_55C'])}")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True,
                    help="the directory to write the four files into (required: a run never rewrites the committed data "
                         "directory unless it is named here)")
    a = ap.parse_args(argv)
    F3 = V3.load_frozen()
    os.makedirs(a.out, exist_ok=True)
    rt = roundtrip(F3)
    rt["interpreter"] = "/usr/bin/python3 " + sys.version.split()[0]
    json.dump(r6(rt), open(os.path.join(a.out, "roundtrip-v3.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(a.out, "roundtrip-v3.txt"), "w").write(text_roundtrip(rt))
    print(text_roundtrip(rt))
    rd = readings(F3)
    rd["interpreter"] = "/usr/bin/python3 " + sys.version.split()[0]
    json.dump(r6(rd), open(os.path.join(a.out, "readings-v3.json"), "w"), indent=1, sort_keys=True)
    tx = text_readings(rd)
    open(os.path.join(a.out, "readings-v3.txt"), "w").write(tx)
    print(tx)
    return 0 if rt["verdict"] == "ROUND TRIP PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
