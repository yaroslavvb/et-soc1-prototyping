#!/usr/bin/env python3
"""Q136(c): corrections after verification (Mon 2 Nov 2026). Desk only and POST HOC: it decides nothing and registers nothing.

Every number the README's corrections F1-F9 cite that no earlier file prints, computed from committed files only: this directory's counts.json
and priced.json; E124's e124.json and extras.json; E109's e109-3pass.json, e109.json and posthoc.json; Q132(b)'s constants. It imports
rtl-sim/tima_bench/price.py and uses its functions and line groups unchanged (candidates, terms, constants, group, TIMA_CTRL, TIMA_PIPE,
TENTMP_CTRL), on price.py's own selection of streams, so every count is the one priced.json prices. No bench is built or run, no reduction is
re-run, and nothing touches a card.

    python3 docs/reports/data/2026-11-02-q136c-tima-bench/corrections-check.py     # from the repo root; writes corrections-check.txt and .json beside it

Three prices for a register bit, each read from a card's own watts (E109 and E124 measured the watts; posthoc_check_e109.py and extras_e124.py
printed the prices):
  A  the card's price for int8's enabled bits on zeros: U = -D(m0.int8.zeros), what issuing int8's micro-ops on all-zero tiles costs, over the
     enabled (clocked) register bits a second that issuing adds in the bench, 12,144 an op (E124 extras.json > reported.U_per_clocked_int8_fj;
     E109 posthoc.json > *.U_per_clocked_int8_fj);
  B  the same U per register-bit clock edge that issuing adds (*.U_per_edge_int8_fj), the reading E109 found fits both formats better;
  C  fp32's no-issue floor at one price: the most a clocked register bit could cost if all of fp32's no-issue S were clocked bits.
Every per-pass quantity uses that pass's own measured op rates and its own N; then the mean and a 95% t interval over passes (n = 4: t 3.182;
n = 3: 4.303; n = 2: 12.706). The pass is the unit of replication. A clocked term is priced at A, B or C alone; the nets and buses are shown
at the bench's constants beside it. The RTL is core-et's (the Erbium branch), a later revision of the ET-SoC-1's lineage, not its own.
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "rtl-sim", "tima_bench"))
import price as P  # noqa: E402  price.py's own functions, unchanged

DD = os.path.join(ROOT, "docs", "reports", "data")
T95 = {1: 12.706, 2: 4.303, 3: 3.182}
CANDS = ("tenb", "tenc", "tima_ctrl", "scp")
CNAME = {"tenb": "TenB arrays", "tenc": "TenC read port", "tima_ctrl": "TIMA controls", "scp": "scratchpad, TenA, TenTMP"}


def load(*p):
    return json.load(open(os.path.join(*p)))


def ci(v):
    n = len(v)
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "half": None, "n": n, "per_pass": v}
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T95[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "half": h, "lo": m - h, "hi": m + h, "n": n, "per_pass": v}


def pm(c, k=3, unit=""):
    return f"{c['mean']:.{k}f}" + ("" if c["half"] is None else f" ± {c['half']:.{k}f}") + unit


C = load(HERE, "counts.json")
PR = load(HERE, "priced.json")
S = {s["name"]: s for s in C["streams"] if s["set"] in ("design", "context", "arms", "context_arms")}  # price.py's own selection
CHK = {s["name"]: s["per_op"] for s in C["streams"] if s["set"] == "check"}  # E109's bench-arms.json, reproduced 360 of 360
PO = {n: s["per_op"] for n, s in S.items()}
CAND = {n: P.candidates(po) for n, po in PO.items()}
TERMS = {n: P.terms(c) for n, c in CAND.items()}
K = P.constants()

E124D = os.path.join(DD, "2026-11-01-e124-int8-zeros-replicate")
E109D = os.path.join(DD, "2026-11-01-e109-int8-zeros")
EXPS = [("E124, aifoundry1 card 1 (registered, four passes)", load(E124D, "e124.json"), load(E124D, "extras.json"), "reported", True),
        ("E109, aifoundry3 card 0 (three passes, post hoc)", load(E109D, "e109-3pass.json"), load(E109D, "posthoc.json"), "three_passes_gate_lifted", False),
        ("E109, aifoundry3 card 0 (two kept passes)", load(E109D, "e109.json"), load(E109D, "posthoc.json"), "registered_reduction", False)]
CONTRASTS = [("N, from reset", "m0.int8.zeros", "m0.fp32.zeros"),
             ("N, fp32 after an int8 run (the card's order)", "m0.int8.zeros", "pre.m0.fp32.zeros"),
             ("desk-only arm: one A row, fp32 after an int8 run", "m0r1.int8.zeros", "pre.m0r1.fp32.zeros"),
             ("desk-only arm: one A row, from reset", "m0r1.int8.zeros", "m0r1.fp32.zeros")]
PRICED_NAME = {"N, from reset": "N, from reset (the bench's own runs)",
               "N, fp32 after an int8 run (the card's order)": "N, fp32 after an int8 run (the card's order)",
               "desk-only arm: one A row, fp32 after an int8 run": "desk-only arm: N with one A row, fp32 after an int8 run",
               "desk-only arm: one A row, from reset": "desk-only arm: N with one A row (TenC read at one address), from reset"}
BE_EVENTS = [("a TenC read, from reset", "m0.fp32.zeros", lambda c: c["tenc"]["reads"]),
             ("a TenC read at a new address (the card's order)", "pre.m0.fp32.zeros", lambda c: c["tenc"]["reads_newaddr"]),
             ("a TIMA control bit clocked", "m0.fp32.zeros", lambda c: c["tima_ctrl"]["clocked"]),
             ("a TenB write (one 32-bit entry)", "m0.fp32.zeros", lambda c: c["tenb"]["writes"]),
             ("a scratchpad read (any size)", "m0.fp32.zeros", lambda c: c["scp"]["reads"]),
             ("a scratchpad bit requested", "m0.fp32.zeros", lambda c: c["scp"]["bits_requested"]),
             ("a 64-bit A read into TenTMP (int8 only)", "m0.fp32.zeros", lambda c: c["scp"]["rd64"]),
             ("a working cycle of one minion's FSM in int8", "m0.fp32.zeros", lambda c: c["tima_clk_en_cycles"])]
ALL_GROUPS = {}
for spec in (P.TIMA_CTRL, P.TIMA_PIPE, P.TENTMP_CTRL):
    for f_, ls in spec.items():
        ALL_GROUPS.setdefault(f_, set()).update(ls)
TIMA_GROUP = {}
for spec in (P.TIMA_CTRL, P.TIMA_PIPE):
    for f_, ls in spec.items():
        TIMA_GROUP.setdefault(f_, set()).update(ls)


def in_spec(key, spec):
    f_, ln = key.rsplit(":", 1)
    return int(ln) in spec.get(f_, ())


def rate_fn(rates_of_items, duty):
    def rate(n):
        item = n[4:] if n.startswith("pre.") else n
        if item in rates_of_items:
            return rates_of_items[item]
        return P.MINIONS * P.CLOCK * duty / S[n]["period"]
    return rate


def duty_of(rates_of_items):
    return sum(rates_of_items[i] / (P.MINIONS * P.CLOCK / c) for i, c in (("fp32.zeros", 546.001), ("int8.zeros", 318.001), ("m0.int8.zeros", 318.001))) / 3


def per_pass_rates(e, p):
    r = {item: v["rate"] for item, v in e["per_pass"][p].items()}
    return rate_fn(r, duty_of(r))


def mean_rates(e):
    acc = {}
    for p, pp in e["per_pass"].items():
        for item, v in pp.items():
            acc.setdefault(item, []).append(v["rate"])
    r = {k: sum(v) / len(v) for k, v in acc.items()}
    return rate_fn(r, duty_of(r))


def dterms(x, y, rate):
    return {c: {k: TERMS[x][c][k] * rate(x) - TERMS[y][c][k] * rate(y) for k in ("clocked", "nets", "bus")} for c in CANDS}


def main():
    out = {"what": __doc__.split("\n")[0], "experiments": {}}
    L = ["Q136(c) CORRECTIONS AFTER VERIFICATION (corrections-check.py): post hoc, desk only, deciding nothing; per pass, then mean ± 95% t over passes",
         "The RTL is core-et's (Erbium), a later revision of the ET-SoC-1's lineage. Every count is the bench's (counts.json, price.py's selection).", ""]
    checks = []
    for ename, e, src, key, card1 in EXPS:
        rep = src[key]
        passes = list(e["per_pass"].keys())
        rp = list(src["passes"]) if key == "reported" else list(rep["passes"])
        assert rp == passes, (ename, rp, passes)
        R = {"passes": passes}
        rows = {}

        def put(k, v):
            rows.setdefault(k, []).append(v)

        for i, p in enumerate(passes):
            pp = e["per_pass"][p]
            rate = per_pass_rates(e, p)
            N = pp["m0.int8.zeros"]["S"] - pp["m0.fp32.zeros"]["S"]
            put("N_w", N)
            # the three prices of a register bit
            pA = rep["U_per_clocked_int8_fj"]["per_pass"][i]
            pB = rep["U_per_edge_int8_fj"]["per_pass"][i]
            U = -pp["m0.int8.zeros"]["D"]
            add_clk = CHK["base.int8.zeros"]["ff_clocked_bits"] - CHK["m0.int8.zeros"]["ff_clocked_bits"]
            add_edge = CHK["base.int8.zeros"]["ff_present_bits"] - CHK["m0.int8.zeros"]["ff_present_bits"]
            pA_re = U / (add_clk * pp["int8.zeros"]["rate"]) * 1e15
            pB_re = U / (add_edge * pp["int8.zeros"]["rate"]) * 1e15
            checks.append((ename, p, "price A recomputed from counts.json's check streams", pA_re - pA))
            checks.append((ename, p, "price B recomputed from counts.json's check streams", pB_re - pB))
            pC = pp["m0.fp32.zeros"]["S"] / (PO["m0.fp32.zeros"]["ff_clocked_bits"] * rate("m0.fp32.zeros")) * 1e15
            put("price_A_fj", pA); put("price_B_fj", pB); put("price_C_ceiling_fj", pC)
            put("price_A_fp32_fj", rep["U_per_clocked_fp32_fj"]["per_pass"][i])
            put("U_int8_w", U)
            tima_issue = CAND["int8.zeros"]["tima_ctrl"]["clocked"] - CAND["m0.int8.zeros"]["tima_ctrl"]["clocked"]
            # what price A implies if it were one price for every bit
            all_m0_int8_A = pA * 1e-15 * PO["m0.int8.zeros"]["ff_clocked_bits"] * rate("m0.int8.zeros")
            put("A_on_all_of_int8_no_issue_enabled_bits_w", all_m0_int8_A)
            put("S_m0_int8_w", pp["m0.int8.zeros"]["S"])
            put("A_share_of_int8_no_issue_bits_it_could_price", pp["m0.int8.zeros"]["S"] / all_m0_int8_A)
            # fp32's own no-issue level as a bound, at one price per event, on every event fp32 does too (posthoc_check_e109.reading's
            # read ceiling, applied event by event): the most one event could cost if all of fp32's no-issue S were that event, and what
            # int8's extra events a second would then buy
            Sf, xi, xf = pp["m0.fp32.zeros"]["S"], "m0.int8.zeros", "m0.fp32.zeros"
            ev = {"a TenB write": lambda c: c["tenb"]["writes"], "a TenB latch or data-latch bit": lambda c: c["tenb"]["latch_bits"] + c["tenb"]["dl_bits"],
                  "a TenA write": lambda c: c["scp"]["tena_writes"], "a TenA bit": lambda c: c["scp"]["tena_bits"],
                  "a scratchpad read": lambda c: c["scp"]["reads"], "a scratchpad bit requested": lambda c: c["scp"]["bits_requested"]}
            worst = 0.0
            for lab, fn in ev.items():
                nf, ni = fn(CAND[xf]) * rate(xf), fn(CAND[xi]) * rate(xi)
                put(f"fp32 floor|{lab}|at most, fJ each", Sf / nf * 1e15)
                put(f"fp32 floor|{lab}|int8's extra at most, W", (ni - nf) * Sf / nf)
                worst = max(worst, (ni - nf) / nf)
            put("fp32 floor|every event fp32 does too, together|int8's extra at most, W", worst * Sf)
            put("fp32 floor|a TenC read at one address (the card's order)|at most, fJ each",
                Sf / (CAND["pre.m0.fp32.zeros"]["tenc"]["reads"] * rate("pre.m0.fp32.zeros")) * 1e15)
            # price A against fp32's own no-issue level: what A would make fp32's own TenB (and TenA) bits cost
            fb = TERMS[xf]["tenb"]["clocked"] * rate(xf)
            fa = CAND[xf]["scp"]["tena_bits"] * rate(xf)
            put("A on fp32's own TenB bits, W", pA * 1e-15 * fb)
            put("A on fp32's own TenB and TenA bits, W", pA * 1e-15 * (fb + fa))
            put("S_m0_fp32_w", Sf)
            for cname, x, y in CONTRASTS:
                dt = dterms(x, y, rate)
                de = CAND[x]["tima_ctrl"]["edges"] * rate(x) - CAND[y]["tima_ctrl"]["edges"] * rate(y)
                wA = {c: pA * 1e-15 * dt[c]["clocked"] for c in CANDS}
                wC = {c: pC * 1e-15 * dt[c]["clocked"] for c in CANDS}
                for c in CANDS:
                    put(f"{cname}|A|{c}", wA[c]); put(f"{cname}|C|{c}", wC[c])
                    put(f"{cname}|A share of N|{c}", wA[c] / N)
                    put(f"{cname}|d_clocked_per_s|{c}", dt[c]["clocked"])
                put(f"{cname}|A share of N|sum", sum(wA.values()) / N)
                put(f"{cname}|A|sum", sum(wA.values()))
                # what int8 alone clocks, at A: the TIMA controls, TenTMP's latch bits and control (in the scratchpad row), TenTMP's zero mask
                # (vpu_ctrl.v:738, in no candidate row)
                tlat = CAND[x]["scp"]["tentmp_bits"] * rate(x) - CAND[y]["scp"]["tentmp_bits"] * rate(y)
                tctl = CAND[x]["scp"]["tentmp_ctrl_clocked"] * rate(x) - CAND[y]["scp"]["tentmp_ctrl_clocked"] * rate(y)
                ttmp = tlat + tctl
                zm = PO[x]["lines"].get("shire/minion/vpu/vpu_ctrl.v:738", [0, 0.0])[1] * rate(x) - PO[y]["lines"].get("shire/minion/vpu/vpu_ctrl.v:738", [0, 0.0])[1] * rate(y)
                put(f"{cname}|A|int8 only: TenTMP's bits and control", pA * 1e-15 * ttmp)
                put(f"{cname}|A|int8 only: TenTMP's latch bits (the latch module TenA and TenB use)", pA * 1e-15 * tlat)
                put(f"{cname}|A|int8 only: TenTMP's control (vpu_tensorfma.v:940-946)", pA * 1e-15 * tctl)
                put(f"{cname}|A|int8 only: TenTMP's zero mask (vpu_ctrl.v:738)", pA * 1e-15 * zm)
                put(f"{cname}|A|int8 only: TIMA controls, TenTMP and its zero mask together", pA * 1e-15 * (ttmp + zm) + wA["tima_ctrl"])
                put(f"{cname}|A share of N|int8 only together", (pA * 1e-15 * (ttmp + zm) + wA["tima_ctrl"]) / N)
                put(f"{cname}|A|int8-only registers (flip-flops): TIMA controls, TenTMP's control, its zero mask", pA * 1e-15 * (tctl + zm) + wA["tima_ctrl"])
                put(f"{cname}|A share of N|int8-only registers", (pA * 1e-15 * (tctl + zm) + wA["tima_ctrl"]) / N)
                put(f"{cname}|A|sum without TenC", sum(wA[c] for c in CANDS if c != "tenc"))
                put(f"{cname}|B|tima_ctrl", pB * 1e-15 * de)
                put(f"{cname}|d_edges_per_s|tima_ctrl", de)
                for kn, kv in K.items():
                    f_ = kv["card1"] if card1 else 1.0
                    nb = {c: f_ * 1e-15 * (dt[c]["nets"] * kv["nets"] + dt[c]["bus"] * kv["bus"]) for c in CANDS}
                    put(f"{cname}|nets and buses at {kn}|sum", sum(nb.values()))
                    put(f"{cname}|nets and buses at {kn}|tenc", nb["tenc"])
            # break-even with N's spread: N of this pass over the events of this pass
            for lab, y, fn in BE_EVENTS:
                d = fn(CAND["m0.int8.zeros"]) * rate("m0.int8.zeros") - fn(CAND[y]) * rate(y)
                put(f"break-even|{lab}", N / d * 1e15 if d > 0 else float("nan"))
            put("issue_adds_tima_bits_per_op", tima_issue)
        R["per_pass"] = {k: ci(v) for k, v in rows.items()}
        # bench prices of TenC's 32 output-register bits, for the ratios
        R["bench_32bit_output_fj"] = {kn: 32 * kv["clocked"] * (kv["card1"] if card1 else 1.0) for kn, kv in K.items()}
        # consistency with priced.json, at the mean rates as price.py computes
        mr = mean_rates(e)
        pe = PR["experiments"][ename]
        md = 0.0
        for cname, x, y in CONTRASTS:
            dt = dterms(x, y, mr)
            for kn, kv in K.items():
                f_ = kv["card1"] if card1 else 1.0
                for c in CANDS:
                    w = f_ * 1e-15 * (dt[c]["clocked"] * kv["clocked"] + dt[c]["nets"] * kv["nets"] + dt[c]["bus"] * kv["bus"])
                    md = max(md, abs(w - pe["contrasts"][PRICED_NAME[cname]]["priced_w"][kn][c]))
        checks.append((ename, "-", "max |this script's bench-constant prices - priced.json| over 4 contrasts x 4 sets x 4 candidates, W", md))
        # the register split at the mean rates (F6): every macro register by line, plus the registers outside the macros' lines
        x, y = "m0.int8.zeros", "m0.fp32.zeros"
        lx, ly = PO[x]["lines"], PO[y]["lines"]
        split = {"TIMA group (TIMA_CTRL and TIMA_PIPE)": 0.0, "int8 only, in TENTMP_CTRL (priced in the scratchpad row)": 0.0,
                 "int8 only, outside every candidate group": 0.0, "fp32 only": 0.0, "clocked in both formats, outside the TIMA group": 0.0}
        top = {"int8 only, outside every candidate group": [], "fp32 only": []}
        tog_rest = 0.0
        for k_ in sorted(set(lx) | set(ly)):
            cx = lx.get(k_, [0, 0.0, 0.0, 0.0]); cy = ly.get(k_, [0, 0.0, 0.0, 0.0])
            d = cx[1] * mr(x) - cy[1] * mr(y)
            if in_spec(k_, TIMA_GROUP):
                split["TIMA group (TIMA_CTRL and TIMA_PIPE)"] += d
            elif cx[1] > 0 and cy[1] == 0:
                if in_spec(k_, ALL_GROUPS):
                    split["int8 only, in TENTMP_CTRL (priced in the scratchpad row)"] += d
                else:
                    split["int8 only, outside every candidate group"] += d
                    tog_rest += cx[2] * mr(x) - cy[2] * mr(y)
                    top["int8 only, outside every candidate group"].append((d, k_, cx[0]))
            elif cy[1] > 0 and cx[1] == 0:
                split["fp32 only"] += d
                top["fp32 only"].append((d, k_, cy[0]))
            elif cx[1] > 0 and cy[1] > 0:
                split["clocked in both formats, outside the TIMA group"] += d
        outside = (PO[x]["ff_clocked_bits"] - sum(v[1] for v in lx.values())) * mr(x) - (PO[y]["ff_clocked_bits"] - sum(v[1] for v in ly.values())) * mr(y)
        split["registers outside the macros' lines (not by line)"] = outside
        split["total: every register bit clocked"] = PO[x]["ff_clocked_bits"] * mr(x) - PO[y]["ff_clocked_bits"] * mr(y)
        split["check: the parts sum to the total"] = sum(v for k_, v in split.items() if not k_.startswith("total") and not k_.startswith("check")) - split["total: every register bit clocked"]
        rest_w = {}
        for kn, kv in K.items():
            f_ = kv["card1"] if card1 else 1.0
            rest_w[kn] = f_ * 1e-15 * (split["int8 only, outside every candidate group"] * kv["clocked"] + tog_rest * kv["nets"])
        R["register_split_per_s_at_mean_rates"] = split
        R["int8_only_outside_groups_priced_w"] = rest_w
        R["top_lines"] = {g: [{"line": k_, "width": w_, "d_clocked_per_s": d} for d, k_, w_ in sorted(v, key=lambda t: -abs(t[0]))[:6]] for g, v in top.items()}
        out["experiments"][ename] = R

    # F4 and F7: the per-row work one A row removes, and the read enable's first pass
    F4 = {}
    for n in ("m0.int8.zeros", "m0r1.int8.zeros", "m0.fp32.zeros", "m0r1.fp32.zeros", "pre.m0r1.fp32.zeros"):
        po, c = PO[n], CAND[n]
        F4[n] = {"period": S[n]["period"], "cycles": po["cycles"], "rd32": c["scp"]["rd32"], "rd64": c["scp"]["rd64"], "rd256": c["scp"]["rd256"],
                 "A reads (32- and 64-bit)": c["scp"]["rd32"] + c["scp"]["rd64"], "TenA writes": c["scp"]["tena_writes"], "TenTMP writes": c["scp"]["tentmp_writes"],
                 "TenTMP zero mask bits clocked (vpu_ctrl.v:738)": po["lines"].get("shire/minion/vpu/vpu_ctrl.v:738", [0, 0.0])[1],
                 "TenC reads": c["tenc"]["reads"], "TenC reads at a new address": c["tenc"]["reads_newaddr"],
                 "TIMA control bits clocked": c["tima_ctrl"]["int8_enabled_clocked"]}
    F7 = {n: {"cycles": PO[n]["cycles"], "f2_tima_ren3 high (cycles)": PO[n]["x"]["tima_ren3"], "tima_clk_en high (cycles)": PO[n]["x"]["tima_clk_en"],
              "micro-ops": PO[n]["uops"], "TenC reads": CAND[n]["tenc"]["reads"]}
          for n in ("f1.m0k1.int8.zeros", "m0k1.int8.zeros", "f1.m0.int8.zeros", "m0.int8.zeros", "pre.m0.fp32.zeros")}
    out["F4_per_row_work"] = F4
    out["F7_read_enable"] = F7
    out["checks"] = [{"experiment": a, "pass": b, "what": c, "difference": d} for a, b, c, d in checks]

    # ---- the printout
    L.append("## Checks")
    L.append("")
    worst = {}
    for a, b, c, d in checks:
        worst[(a, c)] = max(worst.get((a, c), 0.0), abs(d))
    for (a, c), d in worst.items():
        L.append(f"- {a}: {c}: max difference {d:.2e}")
    L.append("")
    L.append("## F1: the TIMA controls and TenB at three prices of a register bit, each from a card's own watts")
    L.append("")
    for ename, R in out["experiments"].items():
        q = R["per_pass"]
        L.append(f"### {ename}")
        L.append("")
        L.append(f"N = {pm(q['N_w'], 3, ' W')}. Price A (the card's, int8's enabled bits on zeros): {pm(q['price_A_fj'], 2, ' fJ')}"
                 f" (fp32's the same way: {pm(q['price_A_fp32_fj'], 2, ' fJ')}); price B (per clock edge): {pm(q['price_B_fj'], 3, ' fJ')};"
                 f" price C (fp32's no-issue floor, a ceiling): {pm(q['price_C_ceiling_fj'], 3, ' fJ')}. Issuing adds"
                 f" {q['issue_adds_tima_bits_per_op']['mean']:,.0f} TIMA-control bits an op of the 12,144 enabled bits it adds.")
        L.append("")
        L.append(f"Price A as one price for every bit: int8's no-issue loop's enabled bits alone would cost {pm(q['A_on_all_of_int8_no_issue_enabled_bits_w'], 2, ' W')}"
                 f" against its measured S of {pm(q['S_m0_int8_w'], 3, ' W')}; it can hold for at most {pm(q['A_share_of_int8_no_issue_bits_it_could_price'], 3)} of them."
                 f" At A, fp32's own TenB bits would cost {pm(q[chr(65) + ' on fp32' + chr(39) + 's own TenB bits, W'], 3, ' W')}, and its TenB and TenA bits"
                 f" {pm(q[chr(65) + ' on fp32' + chr(39) + 's own TenB and TenA bits, W'], 3, ' W')}, against fp32's whole no-issue S of {pm(q['S_m0_fp32_w'], 3, ' W')}.")
        L.append("")
        L.append("fp32's own no-issue level as a bound at one price per event, on the events fp32 does too (the most one could cost; what int8's extra"
                 " events a second would then buy):")
        L.append("")
        for k_ in sorted(k for k in q if k.startswith("fp32 floor|")):
            L.append(f"- {k_[len('fp32 floor|'):]}: {pm(q[k_], 3)}")
        L.append("")
        for cname, x, y in CONTRASTS:
            L.append(f"**{cname}** (`{x}` − `{y}`), W, clocked terms only:")
            L.append("")
            L.append("| price | TenB arrays | TenC read port | TIMA controls | scratchpad, TenA, TenTMP | sum |")
            L.append("|---|---:|---:|---:|---:|---:|")
            L.append("| A (the card's) | " + " | ".join(pm(q[f"{cname}|A|{c}"], 3) for c in CANDS) + f" | {pm(q[f'{cname}|A|sum'], 3)} |")
            L.append("| A, share of N | " + " | ".join(pm(q[f"{cname}|A share of N|{c}"], 2) for c in CANDS) + f" | {pm(q[f'{cname}|A share of N|sum'], 2)} |")
            L.append("| B (per edge) | | | " + pm(q[f"{cname}|B|tima_ctrl"], 4) + " | | |")
            L.append("| C (fp32's floor, at most) | " + " | ".join(pm(q[f"{cname}|C|{c}"], 4) for c in CANDS) + " | |")
            nb = [q[f"{cname}|nets and buses at {kn}|sum"]["mean"] for kn in K]
            nbc = [q[f"{cname}|nets and buses at {kn}|tenc"]["mean"] for kn in K]
            L.append("")
            L.append(f"Beside it, the nets and buses at the bench's constants: {min(nb):.3f}–{max(nb):.3f} W, of which TenC's {min(nbc):.3f}–{max(nbc):.3f} W."
                     f" The TIMA controls' clocked bits a second {q[f'{cname}|d_clocked_per_s|tima_ctrl']['mean']:.4g}; their clock edges a second"
                     f" {q[f'{cname}|d_edges_per_s|tima_ctrl']['mean']:+.3g}. Every candidate without TenC at A: {pm(q[f'{cname}|A|sum without TenC'], 3, ' W')}.")
            L.append("")
            L.append(f"What int8 alone clocks, at A: TenTMP's bits and control {pm(q[f'{cname}|A|int8 only: TenTMP' + chr(39) + 's bits and control'], 3, ' W')};"
                     f" TenTMP's zero mask {pm(q[f'{cname}|A|int8 only: TenTMP' + chr(39) + 's zero mask (vpu_ctrl.v:738)'], 3, ' W')}; with the TIMA controls"
                     f" {pm(q[f'{cname}|A|int8 only: TIMA controls, TenTMP and its zero mask together'], 3, ' W')}, {pm(q[f'{cname}|A share of N|int8 only together'], 2)} of N."
                     f" Of TenTMP's, its latch bits {pm(q[f'{cname}|A|int8 only: TenTMP' + chr(39) + 's latch bits (the latch module TenA and TenB use)'], 3, ' W')} and its control"
                     f" {pm(q[f'{cname}|A|int8 only: TenTMP' + chr(39) + 's control (vpu_tensorfma.v:940-946)'], 3, ' W')}. The int8-only registers alone (the TIMA controls,"
                     f" TenTMP's control, its zero mask): {pm(q[f'{cname}|A|int8-only registers (flip-flops): TIMA controls, TenTMP' + chr(39) + 's control, its zero mask'], 3, ' W')},"
                     f" {pm(q[f'{cname}|A share of N|int8-only registers'], 2)} of N.")
            L.append("")
    L.append("## F8: break-even prices with N's spread (per pass N over that pass's events)")
    L.append("")
    L.append("| event | " + " | ".join(out["experiments"]) + " |")
    L.append("|---|" + "---:|" * len(out["experiments"]))
    for lab, _, _ in BE_EVENTS:
        L.append(f"| {lab} | " + " | ".join(pm(R["per_pass"][f"break-even|{lab}"], 1, " fJ") for R in out["experiments"].values()) + " |")
    L.append("")
    ratios = {}
    for ename, R in out["experiments"].items():
        b32 = R["bench_32bit_output_fj"]
        lo_b, hi_b = min(b32.values()), max(b32.values())
        for lab in ("a TenC read, from reset", "a TenC read at a new address (the card's order)"):
            c = R["per_pass"][f"break-even|{lab}"]
            ratios[(ename, lab)] = {"at_means": (c["mean"] / hi_b, c["mean"] / lo_b), "with_N_spread": (c["lo"] / hi_b, c["hi"] / lo_b)}
        L.append(f"- {ename}: the bench's price for TenC's 32 output-register bits {lo_b:.1f}–{hi_b:.1f} fJ" + (" (card 1's scale)" if "card 1" in ename else ""))
    L.append("")
    for (ename, lab), r in ratios.items():
        L.append(f"- {ename}, {lab}: {r['at_means'][0]:.2f}–{r['at_means'][1]:.2f} times the bench's price at N's mean; {r['with_N_spread'][0]:.2f}–{r['with_N_spread'][1]:.2f} with N's 95% interval")
    use = [r for (en, lab), r in ratios.items() if "two kept" not in en]
    allr = (min(r["with_N_spread"][0] for r in use), max(r["with_N_spread"][1] for r in use))
    allm = (min(r["at_means"][0] for r in use), max(r["at_means"][1] for r in use))
    out["F8_tenc_ratio_to_bench_32bit"] = {"at_means": allm, "with_N_spread": allr,
                                           "per_row": {f"{en} | {lab}": r for (en, lab), r in ratios.items()}}
    L.append(f"- across card 1 and aifoundry3 (three passes): {allm[0]:.1f}–{allm[1]:.1f} times at N's means, {allr[0]:.1f}–{allr[1]:.1f} with N's spread")
    L.append("")
    L.append("## F6: int8's register bits clocked a second, beyond fp32's, by kind of register (m0.int8.zeros − m0.fp32.zeros, mean rates)")
    L.append("")
    for ename, R in out["experiments"].items():
        L.append(f"### {ename}")
        L.append("")
        for k_, v in R["register_split_per_s_at_mean_rates"].items():
            L.append(f"- {k_}: {v:+.4g}")
        rw = R["int8_only_outside_groups_priced_w"]
        L.append(f"- int8 only, outside every candidate group, priced at the bench's constants: {min(rw.values()):.3f}–{max(rw.values()):.3f} W")
        for g, v in R["top_lines"].items():
            L.append(f"- largest lines, {g}: " + "; ".join(f"`{t['line']}` ({t['width']} bits) {t['d_clocked_per_s']:+.3g}" for t in v))
        L.append("")
    L.append("## F4: the per-row work one A row removes (per op on one minion)")
    L.append("")
    keys = list(next(iter(F4.values())).keys())
    L.append("| | " + " | ".join(f"`{n}`" for n in F4) + " |")
    L.append("|---|" + "---:|" * len(F4))
    for k_ in keys:
        L.append(f"| {k_} | " + " | ".join(f"{F4[n][k_]:,.2f}" for n in F4) + " |")
    L.append("")
    L.append("## F7: TenC's read enable in an op with first_pass set (per op on one minion)")
    L.append("")
    keys = list(next(iter(F7.values())).keys())
    L.append("| | " + " | ".join(f"`{n}`" for n in F7) + " |")
    L.append("|---|" + "---:|" * len(F7))
    for k_ in keys:
        L.append(f"| {k_} | " + " | ".join(f"{F7[n][k_]:,.2f}" for n in F7) + " |")
    L.append("")
    json.dump(out, open(os.path.join(HERE, "corrections-check.json"), "w"), indent=1)
    open(os.path.join(HERE, "corrections-check.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
