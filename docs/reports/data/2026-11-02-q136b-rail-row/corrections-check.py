#!/usr/bin/env python3
"""Q136(b), corrections after verification (Mon 2 Nov 2026): every new number in README.md's corrections F1-F8.

    python3 docs/reports/data/2026-11-02-q136b-rail-row/corrections-check.py            # from the lab repo's root
        -> docs/reports/data/2026-11-02-q136b-rail-row/corrections-check.txt

Needs numpy (pip3 install --user numpy). Desk only and post hoc: nothing here was registered, no card was touched, no
device command was sent. It reads committed files only, through recut.py's own functions (imported, not re-run) and
tools/claims-v3/e77/reduce_e77.py's registered fit:
  F1  E77's REGISTERED form (reduce_e77.py fit/verdict_for: offrail = a_m dm + a_s dSRAM + a_n dNoC + R dq, the total
      current, no offset, per pass over both arms' rung means, t(0.995) over passes, the pooled rms test) on the
      re-cut's footings for both blocks, checked first against E77's registered fit and E120's registered secondary in
      that form; then both forms (E77's, and E120's offset form) with each block's board drift moved by -2..+2 s.e.,
      and R's 99% interval with the drift's s.e. added (approx.).
  F3  the band's edges: the models with a conduction term at the row's own operating point (recut.json); arm A through
      the origin (the published fit's no-intercept form) and the row it gives; each arm-A pass's intercept against
      the intercept the block's post hoc conduction term predicts over that pass's own rungs; the two free-heating
      catalogue fits against the measured slopes; the fit's residual against the ledger's three footings.
  F5  how the registered 0.81 W/C was split: E38's own drift at about 81 C against the blocks' at 52-55 C.
  F7  the in-step coefficients with t on the pass part instead of 1.96, and the row they give.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recut as rc  # noqa: E402  (recut.py's functions; its main() is not run)

sys.path.insert(0, os.path.join(rc.ROOT, "tools", "claims-v3", "e77"))
import reduce_e77 as r77  # noqa: E402  (E77's registered reduction; its main() is not run)

T995_NORMAL = 2.5758
T975_NORMAL = 1.96


def e77_form(means):
    """E77's registered verdict form (reduce_e77.verdict_for, model 'total', SRAM and NoC free, no offset)."""
    v = r77.verdict_for(means, model="total", fixed_small=False)
    lo, hi = v["R_ci99_ohm"]
    return {"R_mohm": v["R_mean_ohm"] * 1e3, "lo": lo * 1e3, "hi": hi * 1e3, "sd": v["R_sd_ohm"] * 1e3, "n": v["n_pass"],
            "rms_gain": v["rms_improvement"], "verdict": v["verdict"],
            "per_pass": [round(p["R_eff_ohm"] * 1e3, 3) for _, p in sorted(v["per_pass"].items())]}


def e120_form(means):
    """E120's registered offset form (recut.registered_form 'offset': a_m dm + c_B [B] + R dq), its own rules."""
    o = rc.registered_form(means, "offset")
    r = o["R_mohm"]
    return {"R_mohm": r["mean"], "lo": r["lo"], "hi": r["hi"], "sd": r["sd"], "n": r["n"], "rms_gain": o["rms_improvement"],
            "verdict": o["reading_by_the_registered_rules"]}


def fmt(f):
    return (f"R {f['R_mohm']:.3f} [{f['lo']:.3f}, {f['hi']:.3f}] mOhm 99% over {f['n']} passes, rms gain {f['rms_gain']:.1%}: "
            f"{f['verdict']}")


def verdict_of(lo, hi, gain):
    excl = lo > 0 or hi < 0
    return "PASS" if excl and gain >= 0.30 else ("FAIL" if not excl else "NEITHER (resolved, not material)")


def main():
    txt = []
    P = txt.append
    J = rc.load(os.path.join(HERE, "recut.json"))
    ledger = rc.load(rc.LEDGER)
    res = {"E77": rc.load(rc.E77), "E120": rc.load(rc.E120)}
    B = {"E77": rc.block(rc.E77, "E77"), "E120": rc.block(rc.E120, "E120")}

    # ------------------------------------------------------------------------------------------------ checks
    P("== Checks: the imported code is the committed re-cut, and E77's registered fit is reproduced")
    for n in ("E77", "E120"):
        a = e120_form(rc.rung_means(B[n], "measured_split"))
        b = J["blocks"][n]["footings"]["measured_split"]["offset_form"]["R_mohm"]["mean"]
        P(f"   {n} measured_split, E120's offset form: R {a['R_mohm']:.6f} mOhm here, {b:.6f} in recut.json (diff {abs(a['R_mohm'] - b):.1e})")
    f = e77_form(rc.rung_means(B["E77"], "registered_drift_split"))
    g = res["E77"]["footings"]["drift_split"]["fit"]
    P(f"   E77 registered (drift_split, E77's form): {fmt(f)}")
    P(f"      E77 results.json footings.drift_split.fit: R {g['R_mean_ohm'] * 1e3:.3f} [{g['R_ci99_ohm'][0] * 1e3:.3f}, "
      f"{g['R_ci99_ohm'][1] * 1e3:.3f}], rms gain {g['rms_improvement']:.1%}: {g['verdict']} (diff {abs(f['R_mohm'] - g['R_mean_ohm'] * 1e3):.1e} mOhm)")
    f = e77_form(rc.rung_means(B["E120"], "registered_drift_split"))
    g = res["E120"]["secondary"]["e77_registered_form"]
    P(f"   E120's registered secondary in E77's form (drift_split): {fmt(f)}")
    P(f"      E120 results.json secondary.e77_registered_form: R {g['R_mean_ohm'] * 1e3:.3f} [{g['R_ci99_ohm'][0] * 1e3:.3f}, "
      f"{g['R_ci99_ohm'][1] * 1e3:.3f}], rms gain {g['rms_improvement']:.1%}: {g['verdict']} (diff {abs(f['R_mohm'] - g['R_mean_ohm'] * 1e3):.1e} mOhm)")
    g = res["E120"]["footings"]["drift_split"]["fit"]
    P(f"   E120's registered verdict (V, its offset form, drift_split): R {g['R_mean_ohm'] * 1e3:.3f} [{g['R_ci99_ohm'][0] * 1e3:.3f}, "
      f"{g['R_ci99_ohm'][1] * 1e3:.3f}], rms gain {g['rms_improvement']:.1%}: {g['verdict']}")

    # ------------------------------------------------------------------------------------------------ F1
    P("")
    P("== F1. The conduction term in each registered form, post hoc, on the re-cut's footings")
    P("   (E77 registered offrail = a_m dm + a_s dSRAM + a_n dNoC + R dq with no offset; E120 registered a_m dm + c_B [B] + R dq;")
    P("    both read by the same rules: PASS if the 99% interval excludes 0 and the pooled rms falls by >= 30%, FAIL if it holds 0)")
    for n in ("E77", "E120"):
        for v in ("uncorrected", "registered_drift_split", "measured_split"):
            m = rc.rung_means(B[n], v)
            P(f"   {n:4s} {v:24s} E77's form: {fmt(e77_form(m))}")
            P(f"   {n:4s} {v:24s} E120's form: {fmt(e120_form(m))}")
    P("")
    P("   the measured_split footing with each block's board drift moved (the rails at the block's own slopes, so the off-rail")
    P("   drift moves with it); then R's 99% interval with the drift's s.e. added in quadrature (normal on the drift part; approx.)")
    for n in ("E77", "E120"):
        se, b0 = B[n]["drift"]["board"]["se"], B[n]["dr"]["board"]
        rows = {}
        for z in (-2, -1, 0, 1, 2):
            m = rc.rung_means(B[n], "measured_split", s_board=b0 + z * se)
            a = rc.arm_slopes(m)["A"]["slope_ci99"]["mean"]
            rows[z] = {"e77": e77_form(m), "e120": e120_form(m), "slope": a}
            P(f"   {n:4s} board drift {b0 + z * se:.3f} W/C ({z:+d} s.e.): arm A slope {a:.4f}; E120's form {fmt(rows[z]['e120'])}")
            P(f"   {'':4s} {'':32s}  E77's form  {fmt(rows[z]['e77'])}")
        for form in ("e120", "e77"):
            c = rows[0][form]
            dR = (rows[1][form]["R_mohm"] - rows[-1][form]["R_mohm"]) / 2.0          # mOhm per s.e. of board drift
            hw_pass = c["hi"] - c["R_mohm"]
            hw = math.sqrt(hw_pass ** 2 + (T995_NORMAL * dR) ** 2)
            lo, hi = c["R_mohm"] - hw, c["R_mohm"] + hw
            P(f"   {n:4s} {'E120' if form == 'e120' else 'E77'}'s form, the drift's s.e. added: R moves {dR:+.3f} mOhm per s.e.; "
              f"99% [{lo:.3f}, {hi:.3f}] mOhm (passes alone [{c['lo']:.3f}, {c['hi']:.3f}]); with its rms gain "
              f"{c['rms_gain']:.1%}: {verdict_of(lo, hi, c['rms_gain'])}")

    # ------------------------------------------------------------------------------------------------ F3
    P("")
    P("== F3. The band's edges")
    rows3 = J["at_the_rows_operating_point"]
    for k in ("E120 on its measured drift, offset form, mean", "E77 on its measured drift, offset form, mean",
              "the catalogue, published, with its curvature's R", "the catalogue, measured_split_filtered, with its curvature's R",
              "the catalogue, measured_split_filtered_rails_scaled, with its curvature's R"):
        P(f"   with a conduction term, at the row's own operating point (recut.json at_the_rows_operating_point): {k:66s} row {rows3[k]['row_pJ']:.3f} pJ")
    pub = J["row"]["published"]["coef"]["aifoundry2"]
    row0 = J["row"]["published"]["row_pJ"]
    ppr = J["row"]["pJ_per_unit_ratio"]

    def recut_row(a):
        return row0 + ppr * (a / pub - 1.0)

    P("")
    P("   arm A through the origin (the published fit's no-intercept form), measured_split, per pass:")
    prop = J["measured_split_uncertainty"]
    to = {}
    for n in ("E77", "E120"):
        m = rc.rung_means(B[n], "measured_split")
        per = []
        for p in sorted({k[1] for k in m if k[0] == "A"}):
            pts = [v for k, v in m.items() if k[0] == "A" and k[1] == p]
            x = np.array([v["minion"] for v in pts])
            y = np.array([v["offrail"] for v in pts])
            per.append(float(x @ y / (x @ x)))
        to[n] = float(np.mean(per))
        P(f"   {n:4s} {to[n]:.4f} W/W (per pass {[round(v, 4) for v in per]}) -> row {recut_row(to[n]):.3f} pJ; "
          f"with an intercept {prop[n]['A']['slope']:.4f} -> {recut_row(prop[n]['A']['slope']):.3f} pJ")
    w = {n: 1.0 / prop[n]["A"]["total_se"] ** 2 for n in ("E77", "E120")}
    comb_to = sum(to[n] * w[n] for n in w) / sum(w.values())
    P(f"   combined with the re-cut's own block weights: {comb_to:.4f} W/W -> row {recut_row(comb_to):.3f} pJ "
      f"(with an intercept {J['instep_coefficient']['value']:.4f} -> {recut_row(J['instep_coefficient']['value']):.3f} pJ)")
    P("")
    P("   each arm-A pass's intercept (measured_split), against the intercept the block's own post hoc conduction term")
    P("   (E120's offset form, R at its mean) puts on a line fitted over that pass's rungs:")
    for n in ("E77", "E120"):
        m = rc.rung_means(B[n], "measured_split")
        R = J["blocks"][n]["footings"]["measured_split"]["offset_form"]["R_mohm"]["mean"] * 1e-3
        ints = J["blocks"][n]["footings"]["measured_split"]["arms"]["A"]["per_pass"]
        pred = []
        for p in sorted({k[1] for k in m if k[0] == "A"}):
            pts = [v for k, v in m.items() if k[0] == "A" and k[1] == p]
            x = [v["minion"] for v in pts]
            q = [((v["m0"] + v["minion"]) / v["V"]) ** 2 - (v["m0"] / v["V0"]) ** 2 for v in pts]
            pred.append(rc.ls(x, [R * qq for qq in q])[1])
        meas = [ints[str(p)]["intercept"] for p in sorted(int(s) for s in ints)]
        P(f"   {n:4s} measured {[round(v, 3) for v in meas]} W (mean {np.mean(meas):+.3f}); predicted by R {R * 1e3:.3f} mOhm "
          f"{[round(v, 3) for v in pred]} W (mean {np.mean(pred):+.3f})")
    P("")
    P("   the two free-heating catalogue fits (recut.json catalogue.<card>.free_kappa, free_kappa2), against the measured slopes")
    for card in ("aifoundry2", "aifoundry3"):
        c = J["catalogue"][card]
        bc = c["board_correction"]
        cd = ledger["cards"][card]["card_drift_w_per_c"]
        P(f"   {card}: published minion s.e. {c['published']['se']['minion']:.4f}; the idle law's slope at the median busy die "
          f"{bc['die_c_busy_median']:.1f} C {bc['idle_law_slope_at_median']:.3f} W/C; E38's within-run board drift {cd['board']['mean']:.3f}, "
          f"its rails' {cd['rails']['mean']:.3f} W/C")
        for v in ("free_kappa", "free_kappa2"):
            f = c[v]
            line = (f"      {v:11s} minion {f['coef']['minion']:.4f} +- {f['se']['minion']:.4f}, board kappa "
                    f"{f['coef']['kappa_board_rise_w_per_c']:+.3f} +- {f['se']['kappa_board_rise_w_per_c']:.3f} W/C")
            if v == "free_kappa2":
                line += f", rails kappa {f['coef']['kappa_rails_rise_w_per_c']:+.3f} +- {f['se']['kappa_rails_rise_w_per_c']:.3f} W/C"
            line += f", corr(minion, the board's rise) {f['corr_minion_rise']:.2f}"
            P(line)
    for case in J["row"]["cases"]:
        if case["case"].startswith("the catalogue refitted, free"):
            P(f"   {case['case']:44s} row {case['row_pJ']:.3f} pJ")
    P("")
    on = {k: ledger["footings"]["two_card_mean"]["launch"][k]["on_q128_board_pJ"] for k in ("uncorrected", "drift_split", "board_only")}
    off = on["drift_split"]["offrail"]
    P(f"   the fit's residual: the ledger's off-rail on E38 {off:.4f} pJ (central footing); the ledger's residual over its three footings "
      f"{on['board_only']['unattributed']:+.3f} (board_only) / {on['drift_split']['unattributed']:+.3f} (central) / "
      f"{on['uncorrected']['unattributed']:+.3f} (uncorrected) pJ")
    cases = {c["case"]: c["row_pJ"] for c in J["row"]["cases"]}
    for lab, key in (("the linear band's top, the catalogue refit (filtered)", "the catalogue refitted, measured_split_filtered"),
                     ("its bottom, E120 alone", "E120 arm A, measured drift"),
                     ("the combined coefficient", "E77 and E120 combined, arm A, measured drift"),
                     ("the combined coefficient's approx. 95% low", "its approx 95% low")):
        P(f"   {lab:54s} row {cases[key]:.3f} pJ -> residual {off - cases[key]:+.3f} pJ")

    # ------------------------------------------------------------------------------------------------ F5
    P("")
    P("== F5. How drift_split split the registered 0.81 W/C")
    cd = ledger["cards"]["aifoundry2"]["card_drift_w_per_c"]
    P(f"   E38 on aifoundry2, near 81-84 C (rail-ledger.json cards.aifoundry2.card_drift_w_per_c): board {cd['board']['mean']:.3f} +- "
      f"{cd['board']['se']:.3f}, the metered rails {cd['rails']['mean']:.3f} +- {cd['rails']['se']:.3f}, off-rail {cd['offrail']['mean']:.3f} +- "
      f"{cd['offrail']['se']:.3f} W/C (off-rail share {cd['offrail_share_of_board_drift']:.2f})")
    for n in ("E77", "E120"):
        dr = B[n]["dr"]
        share = 1.0 - sum(dr[k] for k in rc.RAILS) / dr["board"]
        take = rc.REG_LEAK * share
        own = B[n]["drift"]["offrail"]
        T = float(np.mean([r["T_launch"] for r in B[n]["rows"]]))
        P(f"   {n:4s} launched at {T:.1f} C: own board drift {dr['board']:.3f}, rails {sum(dr[k] for k in rc.RAILS):+.3f}, off-rail share "
          f"{share:.2f}; drift_split takes {rc.REG_LEAK} x {share:.2f} = {take:.3f} W/C off the off-rail, against its own off-rail drift "
          f"{own['mean']:.3f} +- {own['se']:.3f} (per launch): {take / own['mean']:.1f}x, {take - own['mean']:.3f} W/C too much; split as "
          f"E38's was, it would take {rc.REG_LEAK * cd['offrail_share_of_board_drift']:.3f}; the idle law at {T:.1f} C {rc.idle_law_slope(T):.3f} W/C")

    # ------------------------------------------------------------------------------------------------ F7
    P("")
    P("== F7. The in-step coefficients with t on the pass part (t(0.975, n-1)) instead of 1.96; the drift part normal")
    se_eff = {}
    for n in ("E77", "E120"):
        u = prop[n]["A"]
        s = J["blocks"][n]["footings"]["measured_split"]["arms"]["A"]["slope_ci95"]
        t = rc.T975[s["n"] - 1]
        hw = math.sqrt((t * u["pass_se"]) ** 2 + (T975_NORMAL * u["drift_se_term"]) ** 2)
        se_eff[n] = hw / T975_NORMAL
        P(f"   {n:4s} arm A {u['slope']:.4f} W/W: passes {s['n']}, t {t:.3f} x s.e. {u['pass_se']:.4f}, drift 1.96 x {u['drift_se_term']:.4f} "
          f"-> [{u['slope'] - hw:.3f}, {u['slope'] + hw:.3f}] (with 1.96 throughout [{u['approx95'][0]:.3f}, {u['approx95'][1]:.3f}]); "
          f"rows [{recut_row(u['slope'] - hw):.3f}, {recut_row(u['slope'] + hw):.3f}] pJ")
    wt = {n: 1.0 / se_eff[n] ** 2 for n in se_eff}
    comb = sum(prop[n]["A"]["slope"] * wt[n] for n in wt) / sum(wt.values())
    cse = 1.0 / math.sqrt(sum(wt.values()))
    ic = J["instep_coefficient"]
    P(f"   combined: {comb:.4f} +- {cse:.4f} -> [{comb - T975_NORMAL * cse:.3f}, {comb + T975_NORMAL * cse:.3f}] W/W, rows "
      f"{recut_row(comb):.3f} [{recut_row(comb - T975_NORMAL * cse):.3f}, {recut_row(comb + T975_NORMAL * cse):.3f}] pJ "
      f"(with 1.96 throughout {ic['value']:.4f} [{ic['approx95'][0]:.3f}, {ic['approx95'][1]:.3f}], rows "
      f"{recut_row(ic['value']):.3f} [{recut_row(ic['approx95'][0]):.3f}, {recut_row(ic['approx95'][1]):.3f}] pJ)")

    with open(os.path.join(HERE, "corrections-check.txt"), "w") as fh:
        fh.write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
