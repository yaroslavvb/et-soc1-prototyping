#!/usr/bin/env python3
"""V3-MMB reducer: PLAN3's pre-registered prediction items MMB-a, -b, -c, -d, -e, -f, -X1 and -T, decided as registered.

    python3 tools/claims-v3/mmb/reduce.py --data DIR --out verdicts.json [--quiet]

DIR holds aifoundry2/ and aifoundry3/, each laid out like the block's DATA_ROOT: <card>/mmb/p<k>/ (one directory per
pass: e1/<workload>/, x1/, thermal/, smoke/, block.json) and, for MMB-b's smoke-test clause only, <card>/mmb-smoke/p<k>/.
Directories named p<k>.attempt-* (earlier attempts the queue set aside) are ignored. It runs on partial data (one card,
fewer passes): an item without enough kept repeats on a card says INSUFFICIENT.

This file holds the plan's N8 reducers mmb_pool (E1 pass-level values, Welch, per W) and ridge_x1 (cycles per op of the
private and shared pools); the load step (MMB-T) is reduced per pass by x1_reduce.py (the plan's
validate3/inv/pt-spatial-work/x1_reduce.py, copied here: see README.md).

Registered rules applied (PLAN3 section 2, common rules and V3-MMB):
 - unit: one pass (a separately started block); >= 3 kept passes on a card or the item is INSUFFICIENT on that card;
 - drop any launch whose implied_ghz is outside 0.595-0.605; on aifoundry2 drop any E1 launch with a telemetry sample
   inside it off 600 MHz, and any load-step pass with any mhz.minion != 600 (x1_reduce's "valid");
 - E1 power values (MMB-c..f) of a workload in a pass are kept only if none of its timed launches was dropped;
 - 99% t intervals on pass-level values (two-sided, t_0.995,df); one-sided 99% where registered (MMB-e);
 - holds on both cards -> PASS; on neither -> FAIL; on one -> CARD-DIFFERENT; missing repeats -> INSUFFICIENT.
Every choice the plan's text leaves open is listed in README.md ("Reduction: readings of the registered text").

Four cards (README.md "Four cards"; the amendment written before any aifoundry1 data): DIR may hold any card directory
(aifoundry1-c0/, aifoundry1-c1/, ...); all are read, and aifoundry2, aifoundry3, aifoundry1-c0 and aifoundry1-c1 are
always expected. Each item's "outcome" is the REGISTERED one, computed exactly as before from aifoundry2 and aifoundry3
only. Each item adds "all_cards": PASS if it holds on every card on which it is tested, CARD-DIFFERENT if on some, FAIL
if on none, INSUFFICIENT if any such card lacks kept repeats (a missing card lacks them), REPORTED if the item (its
band) is registered for aifoundry2 or aifoundry3 only, so aifoundry1's cards are reported, not tested. per_card holds
every card. aifoundry1's cards take cardrules.py's busy-sample clock rule; items over an idle bracket carry each card's
idle clock (aifoundry1-c0 idles at 300 MHz), and doc["idle_clock"] has the full table.
"""
import argparse
import glob
import gzip
import json
import math
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import cardrules  # noqa: E402  (the per-card clock rules, shared with finish and passcheck)
CARDS = ("aifoundry2", "aifoundry3")   # the registered cards: every "outcome" comes from these two only
SHORT = {"aifoundry2": "a2", "aifoundry3": "a3"}
REPORTED = "reported"                  # all_cards: the item (or this part) is not tested on that card, only reported
IDLE = {}                              # each card's idle clock (idle_clock(); filled by main before the items)
NEED = 3                       # kept repeats per card (common rules)
GHZ = (0.595, 0.605)           # drop band for implied_ghz
L2 = ("fp32-tensor-L2", "fp16-tensor-L2", "int8-tensor-L2")
DRAM = "fp32-tensor-DRAM"
WORKLOADS = L2 + (DRAM,)
MODE = {"fp32-tensor-L2": "fp32", "fp16-tensor-L2": "fp16", "int8-tensor-L2": "int8", DRAM: "fp32"}
A100_INT8_PER_W = 1560.0       # 624 TOP/s / 400 W (SXM4), as registered
SETTLE_S = 1.0                 # mmbench-power.py --settle (default; the blocks use it)
IDLE_BEFORE_S = (3.5, 1.8)

CLAIMS = {
    "MMB-a": ["matmul-sparse-testdrive-29", "matmul-sparse-testdrive-30", "matmul-sparse-testdrive-31",
              "matmul-sparse-testdrive-24", "ridge-11", "ridge-12", "ridge-13", "ridge-28", "ridge-64", "ridge-75",
              "matmul-sparse-testdrive-V09"],
    "MMB-b": ["matmul-sparse-testdrive-01", "matmul-sparse-testdrive-03", "matmul-sparse-testdrive-V03",
              "matmul-sparse-testdrive-43", "hub-018"],
    "MMB-c": ["matmul-sparse-testdrive-04", "matmul-sparse-testdrive-21", "matmul-sparse-testdrive-23",
              "matmul-sparse-testdrive-25"],
    "MMB-d": ["matmul-sparse-testdrive-22", "matmul-sparse-testdrive-05", "matmul-sparse-testdrive-07"],
    "MMB-e": ["matmul-sparse-testdrive-07"],
    "MMB-f": ["matmul-sparse-testdrive-34"],
    "MMB-X1": ["ridge-07", "ridge-18", "ridge-33", "ridge-55", "ridge-65", "ridge-70"],
    "MMB-T": ["pt-spatial-02", "pt-spatial-04", "pt-spatial-08", "pt-spatial-20", "pt-spatial-21", "pt-spatial-22",
              "pt-spatial-23", "pt-spatial-24", "pt-spatial-25", "pt-spatial-26", "pt-spatial-27", "pt-spatial-29",
              "pt-spatial-31", "pt-spatial-32", "pt-spatial-38", "pt-spatial-39", "pt-spatial-V02",
              "horace-lowpower-030", "horace-lowpower-090"],
}
PREDICTION = {  # the registered text, verbatim (PLAN3 V3-MMB table)
    "MMB-a": "cycles/op every launch, both cards: fp32 529.0+-0.5, fp16 529.0+-0.5, int8 280.4+-1.0; DRAM 15,000-16,200 on a2 and within +-6% of a2 on a3. | deterministic: every launch of every pass inside the band on both cards.",
    "MMB-b": "9.511+-0.01 / 19.02+-0.02 / 71.78+-0.08 T(FL)OP/s at 600 MHz, every launch exact with 0 bad minions; smoke tests (mmbench-check, it_test_code_loading) pass on aifoundry3. | deterministic.",
    "MMB-c": "above idle (mean_w - idle_before_w): a2 fp32 26+-3 W, fp16 27+-3, int8 28+-3, DRAM 8+-2; a3 = 0.92 x a2 +-3 W. | per card 99% t over 4 pass values excludes 0; a3/a2 ratio of pass means in 0.85-1.0. Board watts are stated per card with die temperature.",
    "MMB-d": "board G(FL)OP/s per W higher on a3 than a2 by >= 8% in each L2 mode. | Welch per mode, alpha 0.01/3 (Bonferroni over three modes); a significant difference is labelled \"card at its operating temperature\", never a card property.",
    "MMB-e": "A100 int8 lead (1560 / ET GOP/s per W): a2 1.25-1.45x, a3 1.00-1.25x. | one-sided 99% t vs 1560 per card; if aifoundry3's interval includes 1560 the page drops \"the A100 wins int8 efficiency\" as a general statement.",
    "MMB-f": "rise from the first to the last 1 s of a 6 s L2 workload: +0.5 to +2 W on a2, ~0 on the DRAM workload. | pass values, 99% t, each card.",
    "MMB-X1": "(a) shared controls 529.0+-0.5 (fp32, fp16), 280.4+-1 (int8); (b) private tiles fp32/fp16 529-545 cycles/op; (c) private int8 480-560 cycles/op (3.7-4.3 B/minion-cycle: the shared pool explains 7.3). | deterministic per launch; (b) any card above 560 -> drop \"can just keep fp32 and fp16 busy\"; (c) <= 330 on both cards refutes the shared-pool cause; 330-480 -> report, cause open.",
    "MMB-T": "load step (4 passes): P1 busy slope from 5 s after launch a2 0.80+-0.10 W/C at ~75-88 C, a3 0.45+-0.15; P2 minion-rail share a2 0.45-0.55, a3 0.40-0.60; P3 idle after - idle before a2 +3 to +7 W, a3 +1 to +4 W, a2 within +-0.7 W of the idle law; P4 DRAM phase remainder +3 to +7 W, minion rail < +1.0 W; P5 die_mv.ddr in the DRAM phase 2-5 mV below the idle trend, within 1 mV under the matmul; P6 droop per W of minion-rail rise: 99% interval excludes 0 (band a2 0.03-0.08, a3 0.03-0.15 reported); P7 at tau = 0 the remainder overshoots >= 10 W at the start and dips >= 2 W at the stop, filtered with the card's tau (1.15 / 1.22 s) within +-1 W; P8 |PMIC board average - board| <= 0.5 W steady; P9 600 MHz throughout; P10 a2 cools 4-8 C in the 40 s after the matmul. | 99% t over passes (df 3): P1, P3, P4 remainder, P5, P6 exclude 0 on each card with the mean in band; P4 minion rail and P8 upper bounds; P7, P9 every pass; sign disagreement -> CARD-DIFFERENT; magnitude only -> per card. The busy-minus-idle clause (pt-spatial-22) is not decided by 4 passes (needs ~8 per card): it stays dropped.",
}


# ------------------------------------------------------------------ statistics (no scipy on the lab hosts)
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        dl = d * c
        h *= dl
        if abs(dl - 1.0) < 3e-15:
            break
    return h


def _betai(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * _betai(df / 2.0, 0.5, x)
    return 1.0 - p if t > 0 else p


def t_ppf(q, df):
    lo, hi = 0.0, 1e4
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def summ(xs, one_sided_upper=False):
    """n, mean, sd, the two-sided 99% t interval (t_0.995,n-1) and, if asked, the one-sided 99% upper bound."""
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    n = len(xs)
    o = {"n": n, "values": [round(x, 5) for x in xs]}
    if n == 0:
        return o
    o["mean"] = round(st.fmean(xs), 5)
    if n >= 2:
        sd = st.stdev(xs); se = sd / math.sqrt(n); t = t_ppf(0.995, n - 1)
        o.update(sd=round(sd, 5), ci99=[round(o["mean"] - t * se, 5), round(o["mean"] + t * se, 5)], t_crit=round(t, 3))
        o["excludes_0"] = o["ci99"][0] > 0 or o["ci99"][1] < 0
        if one_sided_upper:
            t1 = t_ppf(0.99, n - 1)
            o["upper99_one_sided"] = round(o["mean"] + t1 * se, 5); o["t1_crit"] = round(t1, 3)
    return o


def welch(a, b):
    """Two-sided Welch t test of mean(b) - mean(a)."""
    na, nb = len(a), len(b)
    ma, mb = st.fmean(a), st.fmean(b)
    va, vb = st.variance(a) / na, st.variance(b) / nb
    if va + vb == 0:
        return {"t": math.inf if mb != ma else 0.0, "df": na + nb - 2, "p": 0.0 if mb != ma else 1.0}
    t = (mb - ma) / math.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (na - 1) + vb ** 2 / (nb - 1))
    return {"t": round(t, 4), "df": round(df, 3), "p": 2 * (1 - t_cdf(abs(t), df))}


def decide(h2, h3):
    if h2 is None or h3 is None:
        return "INSUFFICIENT"
    if h2 and h3:
        return "PASS"
    if not h2 and not h3:
        return "FAIL"
    return "CARD-DIFFERENT"


def extra_cards(D):
    """The cards beyond the registered two (aifoundry1-c0, aifoundry1-c1 and any other directory present)."""
    return [c for c in D if c not in CARDS]


def all_cards(holds, sign=None, idle=None, note=""):
    """The all-cards outcome. holds: {card: True | False | None (lacks kept repeats) | REPORTED} over every card, the
    registered cards with their registered per-card holds. sign: {card: +1/-1/0} of the tested cards' 99% intervals
    (a sign disagreement is CARD-DIFFERENT, as registered). idle: {card: idle-clock summary} for items over an idle
    bracket."""
    tested = {c: h for c, h in holds.items() if h != REPORTED}
    rep = [c for c, h in holds.items() if h == REPORTED]
    lacking = [c for c, h in tested.items() if h is None]
    have = {c: h for c, h in tested.items() if h is not None}

    def over(hs):
        if not hs:
            return None
        if all(hs.values()):
            return "PASS"
        if not any(hs.values()):
            return "FAIL"
        return "CARD-DIFFERENT"
    part = over(have)
    sg = {c: v for c, v in (sign or {}).items() if c in have}
    if part and len({v for v in sg.values() if v}) == 2:
        part = "CARD-DIFFERENT"  # registered: sign disagreement
    if not any(c not in CARDS for c in tested):
        oc = "REPORTED"          # registered for aifoundry2/aifoundry3 only: aifoundry1's cards are reported
    elif lacking:
        oc = "INSUFFICIENT"
    else:
        oc = part
    o = {"outcome": oc, "holds": holds, "tested": sorted(tested), "reported_only": rep, "lacking_repeats": lacking,
         "outcome_over_cards_with_repeats": part}
    if sign:
        o["sign"] = sign
    txt = {"PASS": "holds on every card tested", "FAIL": "holds on none of the cards tested",
           "CARD-DIFFERENT": "holds on some cards only: per-card values",
           "INSUFFICIENT": f"cards without {NEED} kept repeats: {lacking}",
           "REPORTED": "registered for aifoundry2/aifoundry3 only: the other cards are reported (per_card), not tested"}[oc]
    if rep and oc != "REPORTED":
        txt += f"; reported only on {rep}"
    if idle:
        o["idle_clock"] = idle
        diff = {c: v["idle_mhz"] for c, v in idle.items() if v.get("differs")}
        if diff:
            txt += (f"; idle brackets not at 600 MHz on {diff}: the value there includes the step from that idle "
                    "state (low_power) to the 600 MHz burst")
    o["reading"] = txt + (f"; {note}" if note else "")
    return o


def comb_all(subs):
    """A summary item's all-cards outcome from its sub-items' all-cards outcomes (REPORTED ones left out)."""
    v = [x for x in subs if x != "REPORTED"]
    if not v:
        return "REPORTED"
    return ("INSUFFICIENT" if "INSUFFICIENT" in v else "PASS" if all(x == "PASS" for x in v)
            else "FAIL" if "FAIL" in v else "CARD-DIFFERENT")


def inb(x, band):
    return x is not None and band[0] <= x <= band[1]


def r(x, n=4):
    return None if x is None else round(x, n)


# ------------------------------------------------------------------ loading
def load_jsonl(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rt") as f:
                return [json.loads(l) for l in f if l.startswith("{")]
    return []


def mmbench_lines(path):
    out = []
    if os.path.exists(path):
        for l in open(path, errors="replace"):
            if l.startswith("MMBENCH "):
                try:
                    out.append(json.loads(l.split(" ", 1)[1]))
                except ValueError:
                    pass
    return out


def pass_dirs(root, exp):
    out = []
    for d in glob.glob(os.path.join(root, exp, "p*")):
        m = re.fullmatch(r"p(\d+)", os.path.basename(d))
        if m and os.path.isdir(d):
            out.append((int(m.group(1)), d))
    return sorted(out)


def load_e1(wd, card, rule=None):
    """One E1 workload invocation: launches with drop flags recomputed from the telemetry, and the pass-level values.
    rule: cardrules.rule() of the card; the registered cards' paths below are unchanged."""
    rule = rule or cardrules.rule(card)
    res_p = os.path.join(wd, "results.json")
    if not os.path.exists(res_p):
        return None
    res = json.load(open(res_p))
    runs = [json.loads(l) for l in open(os.path.join(wd, "runs.jsonl"))] if os.path.exists(os.path.join(wd, "runs.jsonl")) else []
    if not runs or not res.get("results"):
        return None
    x = res["results"][0]
    tel = sorted(load_jsonl(os.path.join(wd, "telemetry.jsonl")), key=lambda s: s["t_ms"])
    samples = []
    if os.path.exists(os.path.join(wd, "power.csv")):
        for line in open(os.path.join(wd, "power.csv")):
            t, _, w = line.strip().partition(",")
            if t.isdigit():
                samples.append((int(t), float(w)))
    tel = [s for s in tel if "mhz" in s]  # a sample whose clock query failed is not a clock reading (ettelem omits it)
    t_proc0 = min(q["t_start_ms"] for q in runs)  # the timed process's first launch (the busy rule's ramp second)
    for q in runs:
        if rule == "busy":  # aifoundry1's cards (four-card amendment): busy samples only, cardrules.py
            b = cardrules.busy_launch(q, tel, t_proc0)
            q["_mhz"], q["_ramp"] = b["mhz"], b["ramp"]
            q["_drop"] = [] if GHZ[0] <= q["implied_ghz"] <= GHZ[1] else ["implied_ghz"]
            if b["drop"]:
                q["_drop"].append("mhz_minion")
            q["_cyc_mean"] = q["cycles_mean"] / q["ops_per_minion"]
            q["_cyc_max"] = q["cycles_max"] / q["ops_per_minion"]
            continue
        inside = [s for s in tel if q["t_start_ms"] <= s["t_ms"] <= q["t_end_ms"]]
        if not inside:
            b = [s for s in tel if s["t_ms"] <= q["t_start_ms"]][-1:]
            a = [s for s in tel if s["t_ms"] >= q["t_end_ms"]][:1]
            inside = b + a
        q["_mhz"] = sorted({s["mhz"]["minion"] for s in inside})
        q["_drop"] = []
        if not GHZ[0] <= q["implied_ghz"] <= GHZ[1]:
            q["_drop"].append("implied_ghz")
        if card == "aifoundry2" and q["_mhz"] != [600]:
            q["_drop"].append("mhz_minion")
        q["_cyc_mean"] = q["cycles_mean"] / q["ops_per_minion"]
        q["_cyc_max"] = q["cycles_max"] / q["ops_per_minion"]
    kept = [q for q in runs if not q["_drop"]]
    idle_b = x.get("idle_before_w")
    if idle_b is None:  # results.json from an older mmbench-power.py: recompute (mmbench-report-data.py does the same)
        lo, hi = runs[0]["t_start_ms"] - IDLE_BEFORE_S[0] * 1000, runs[0]["t_start_ms"] - IDLE_BEFORE_S[1] * 1000
        w = [v for t, v in samples if lo <= t <= hi]
        idle_b = st.fmean(w) if w else None
    # MMB-f: the power window of mean_w (after the settle second, samples inside a launch); first and last 1 s of it
    w0, w1 = runs[0]["t_start_ms"] + SETTLE_S * 1000, runs[-1]["t_end_ms"]
    win = [(t, v) for t, v in samples if t >= w0 and any(q["t_start_ms"] <= t <= q["t_end_ms"] for q in runs)]
    first = [v for t, v in win if t <= w0 + 1000]
    last = [v for t, v in win if t >= w1 - 1000]
    rise = st.fmean(last) - st.fmean(first) if first and last else None
    power_ok = (len(kept) == len(runs) and x.get("power_samples", 0) > 0 and idle_b is not None
                and not math.isnan(x["mean_w"]))
    tflops, per_w, power_note = x["tflops"], x["gflops_per_w"], None
    if rule == "busy":  # the ramp exemption (cardrules.e1_power_kept); per W over the kept launches when one is out
        pk, power_note = cardrules.e1_power_kept(card, runs)
        power_ok = (pk and bool(kept) and x.get("power_samples", 0) > 0 and idle_b is not None
                    and not math.isnan(x["mean_w"]))
        if kept and len(kept) < len(runs):
            tflops = sum(q["total_flop"] for q in kept) / sum(q["wall_s"] for q in kept) / 1e12
            per_w = tflops * 1000 / x["mean_w"]
    # the idle clock of the workload's brackets (four cards): recorded by finish, else read from the telemetry
    meta_p = os.path.join(wd, "meta.json")
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    clk = lambda lo, hi: sorted({s["mhz"]["minion"] for s in tel if lo <= s["t_ms"] <= hi})
    idle_mhz = res.get("idle_mhz_minion")
    if idle_mhz is None and "t_idle0_ms" in meta:
        idle_mhz = clk(meta["t_idle0_ms"] + 1000, meta["t_idle1_ms"])
    ib_mhz = x.get("idle_before_mhz_minion")
    if ib_mhz is None and x.get("idle_before_window_ms"):
        ib_mhz = clk(*x["idle_before_window_ms"])
    return {"runs": runs, "kept": kept, "dropped": [q["launch"] for q in runs if q["_drop"]],
            "idle_mhz": idle_mhz, "idle_before_mhz": ib_mhz, "power_note": power_note,
            "ramp_mhz": sorted({m for q in runs for m in q.get("_ramp", [])}),
            "mean_w": x["mean_w"], "idle_before_w": idle_b, "tflops": tflops, "gflops_per_w": per_w,
            "above_idle_w": x["mean_w"] - idle_b if idle_b is not None else None, "rise_w": rise,
            "rise_samples": [len(first), len(last)], "power_ok": bool(power_ok),
            "die_c_start": x.get("die_c_start"), "die_c_mean": x.get("die_c_mean_power_window"),
            "kept_tflops": (sum(q["total_flop"] for q in kept) / sum(q["wall_s"] for q in kept) / 1e12) if kept else None,
            "cal": [json.loads(l) for l in open(os.path.join(wd, "cal.jsonl"))] if os.path.exists(os.path.join(wd, "cal.jsonl")) else []}


def load_smoke(sd):
    recs = load_jsonl(os.path.join(sd, "smoke.jsonl"))
    launches = []
    for f in glob.glob(os.path.join(sd, "check-*.out")):
        launches += mmbench_lines(f)
    return {"records": recs, "check_launches": launches}


def load_card(root, card):
    passes = []
    for k, d in pass_dirs(root, "mmb"):
        bj = os.path.join(d, "block.json")
        oj = os.path.join(d, "order.json")
        order = json.load(open(oj)) if os.path.exists(oj) else {}
        rule = cardrules.rule(card, order.get("gov_free"))
        P = {"pass": k, "dir": d, "status": json.load(open(bj)).get("status") if os.path.exists(bj) else None,
             "e1": {}, "x1": {}, "smoke": load_smoke(os.path.join(d, "smoke")), "thermal": None, "rule": rule,
             "idle_state": load_jsonl(os.path.join(d, "idle-state.jsonl")),
             "x1_clock": load_jsonl(os.path.join(d, "x1", "clock.jsonl"))}
        for w in WORKLOADS:
            wd = os.path.join(d, "e1", w)
            if os.path.isdir(wd):
                e = load_e1(wd, card, rule)
                if e:
                    P["e1"][w] = e
        for kind in ("private", "shared"):
            for m in ("fp32", "fp16", "int8"):
                L = mmbench_lines(os.path.join(d, "x1", f"{kind}-{m}.out"))
                for q in L:
                    q["_cyc_max"] = q["cycles_max"] / q["ops_per_minion"]
                    q["_keep"] = GHZ[0] <= q["implied_ghz"] <= GHZ[1]
                if L:
                    P["x1"][(kind, m)] = L
        td = os.path.join(d, "thermal")
        if os.path.exists(os.path.join(td, "thermal-phases.jsonl")) and (
                os.path.exists(os.path.join(td, "thermal-telemetry.jsonl")) or
                os.path.exists(os.path.join(td, "thermal-telemetry.jsonl.gz"))):
            P["thermal"] = td
        passes.append(P)
    smoke_blocks = [load_smoke(os.path.join(d, "smoke")) for _, d in pass_dirs(root, "mmb-smoke")]
    return {"passes": passes, "smoke_blocks": smoke_blocks}


# ------------------------------------------------------------------ items
def item(name, per_card, test, outcome, reading, extra=None, claims=None):
    o = {"item": name, "claims": claims if claims is not None else CLAIMS.get(name.split("/")[0], []),
         "prediction_registered": PREDICTION.get(name.split("/")[0]), "per_card": per_card, "test": test,
         "outcome": outcome, "reading": reading}
    if extra:
        o.update(extra)
    return o


def mmb_a(D):
    band = {"fp32-tensor-L2": (528.5, 529.5), "fp16-tensor-L2": (528.5, 529.5), "int8-tensor-L2": (279.4, 281.4)}
    pc, holds = {}, {}
    a2dram = [q["_cyc_mean"] for P in D["aifoundry2"]["passes"] for q in (P["e1"].get(DRAM) or {}).get("kept", [])]
    n2dram = sum(1 for P in D["aifoundry2"]["passes"] if (P["e1"].get(DRAM) or {}).get("kept"))
    a2ref = st.fmean(a2dram) if a2dram and n2dram >= NEED else None
    def a_row(card, w, b):
        E = [P["e1"][w] for P in D[card]["passes"] if w in P["e1"] and P["e1"][w]["kept"]]
        ks = [q for e in E for q in e["kept"]]
        cm = [q["_cyc_mean"] for q in ks]
        out = [round(v, 3) for v in cm if b and not b[0] <= v <= b[1]]
        tf = [q["tflops"] for e in E for q in e["kept"]]
        spread = [100 * (max(x) - min(x)) / st.fmean(x) for x in ([q["tflops"] for q in e["kept"]] for e in E) if len(x) > 1]
        ovh = [(q["wall_s"] - q["cycles_max"] / 600e6) * 1e3 for q in ks]
        return len(E), cm, out, {
            "passes": len(E), "launches": len(ks), "band": [r(b[0], 2), r(b[1], 2)] if b else None,
            "cycles_per_op_mean_based": [r(min(cm), 3), r(max(cm), 3)] if cm else None,
            "out_of_band": out,
            "cycles_per_op_max_based": [r(min(q["_cyc_max"] for q in ks), 3), r(max(q["_cyc_max"] for q in ks), 3)] if ks else None,
            "dropped_launches": sum(len(e["dropped"]) for e in E),
            "info_implied_ghz": [r(min(q["implied_ghz"] for q in ks)), r(max(q["implied_ghz"] for q in ks))] if ks else None,
            "info_launch_spread_pct_max": r(max(spread), 4) if spread else None,
            "info_launch_overhead_ms": {"median": r(st.median(ovh), 3), "range": [r(min(ovh), 3), r(max(ovh), 3)]} if ovh else None,
            "info_tflops_range": [r(min(tf)), r(max(tf))] if tf else None}

    for card in CARDS:
        c, ok, enough = {}, True, True
        for w in WORKLOADS:
            if w == DRAM:
                b = (15000.0, 16200.0) if card == "aifoundry2" else ((a2ref * 0.94, a2ref * 1.06) if a2ref else None)
            else:
                b = band[w]
            nE, cm, out, c[w] = a_row(card, w, b)
            if nE < NEED or b is None:
                enough = False
            elif out:
                ok = False
        holds[card] = ok if enough else None  # fewer than 3 kept passes on a card: the claim stays as it is
        pc[card] = c
    oc = decide(holds["aifoundry2"], holds["aifoundry3"])
    # four cards: the L2 bands are registered for both cards, so they are tested on every card; the DRAM band is
    # registered for aifoundry2 (and relative to it for aifoundry3), so on the other cards DRAM is reported
    hall = dict(holds)
    for card in extra_cards(D):
        c, ok, enough = {}, True, True
        for w in WORKLOADS:
            nE, cm, out, c[w] = a_row(card, w, band.get(w))
            if w == DRAM:
                a3b = (a2ref * 0.94, a2ref * 1.06) if a2ref else None
                c[w]["reported_only"] = True
                c[w]["in_a2_band_15000_16200"] = all(15000 <= v <= 16200 for v in cm) if cm else None
                c[w]["a3_rule_band_from_a2"] = [r(a3b[0], 2), r(a3b[1], 2)] if a3b else None
                c[w]["in_a3_rule_band"] = all(a3b[0] <= v <= a3b[1] for v in cm) if (cm and a3b) else None
                continue
            if nE < NEED:
                enough = False
            elif out:
                ok = False
        hall[card] = ok if enough else None
        pc[card] = c
    ac = all_cards(hall, note="DRAM cycles/op reported on aifoundry1's cards (its band is aifoundry2's)")
    bad = {card: {w: len(pc[card][w]["out_of_band"]) for w in WORKLOADS if pc[card][w]["out_of_band"]} for card in CARDS}
    reading = {"PASS": "every kept launch of every pass inside its cycles/op band on both cards",
               "FAIL": f"launches outside the band on both cards {bad}: the page takes the measured cycles/op per card",
               "CARD-DIFFERENT": f"inside the band on one card only {bad}: the page gives per-card cycles/op",
               "INSUFFICIENT": f"fewer than {NEED} kept passes for some workload on a card; out-of-band so far {bad}"}[oc]
    return item("MMB-a", pc, "every kept E1 timed launch: cycles_mean/ops_per_minion inside the band (fp32/fp16 528.5-529.5, "
                "int8 279.4-281.4, DRAM a2 15000-16200, a3 within +-6% of a2's mean DRAM value); >= 3 kept passes per workload",
                oc, reading, {"all_cards": ac})


def mmb_b(D):
    band = {"fp32-tensor-L2": (9.501, 9.521), "fp16-tensor-L2": (19.00, 19.04), "int8-tensor-L2": (71.70, 71.86)}
    pc, holds = {}, {}
    hall = {}
    for card in list(CARDS) + extra_cards(D):  # the registered two decide "outcome"; every card enters all_cards
        c, ok, enough = {}, True, True
        for w in L2:
            E = [P["e1"][w] for P in D[card]["passes"] if w in P["e1"] and P["e1"][w]["kept"]]
            tf = [q["tflops"] for e in E for q in e["kept"]]
            out = [round(v, 4) for v in tf if not band[w][0] <= v <= band[w][1]]
            c[w] = {"passes": len(E), "launches": len(tf), "band": band[w], "tflops_launch_range": [r(min(tf)), r(max(tf))] if tf else None,
                    "tflops_pass_values": [r(e["kept_tflops"]) for e in E], "out_of_band": out}
            if len(E) < NEED:
                enough = False
            elif out:
                ok = False
        runs = [q for P in D[card]["passes"] for e in P["e1"].values() for q in e["kept"]]
        inexact = [(q.get("workload"), q["launch"], q["check"], q["bad_minions"], q["launch_errors"]) for q in runs
                   if q["check"] != "exact" or q["bad_minions"] or q["launch_errors"]]
        c["exactness"] = {"kept_timed_launches": len(runs), "not_exact_or_bad": inexact}
        if inexact:
            ok = False
        cal = [q for P in D[card]["passes"] for e in P["e1"].values() for q in e["cal"]]
        c["info_calibration_launches"] = {"n": len(cal), "not_exact": sum(1 for q in cal if q["check"] != "exact" or q["bad_minions"])}
        sm = [s for P in D[card]["passes"] for s in P["smoke"]["records"]] + [s for B in D[card]["smoke_blocks"] for s in B["records"]]
        not_run = [s["test"] for s in sm if s["rc"] == 127]  # binary not found: the test did not run (not a failure)
        sm = [s for s in sm if s["rc"] != 127]
        sl = [q for P in D[card]["passes"] for q in P["smoke"]["check_launches"]] + [q for B in D[card]["smoke_blocks"] for q in B["check_launches"]]
        sm_ok = bool(sm) and all(s["rc"] == 0 for s in sm if s["test"] in ("mmbench-check", "it_test_code_loading")) \
            and {"mmbench-check", "it_test_code_loading"} <= {s["test"] for s in sm} \
            and all(q["check"] == "exact" and not q["bad_minions"] and not q["launch_errors"] for q in sl)
        c["smoke"] = {"records": len(sm), "not_run_binary_missing": not_run,
                      "failed": [s["test"] + " " + s.get("args", "") for s in sm if s["rc"] != 0],
                      "check_launches": len(sl), "check_launches_not_exact": sum(1 for q in sl if q["check"] != "exact" or q["bad_minions"]),
                      "pass": sm_ok if sm else None, "decides": card == "aifoundry3"}
        if card == "aifoundry3":
            if not sm or not {"mmbench-check", "it_test_code_loading"} <= {x["test"] for x in sm}:
                enough = False  # a smoke test that never ran on aifoundry3 leaves the clause undecided
            elif not sm_ok:
                ok = False
        if card in CARDS:
            holds[card] = ok if enough else None
        hall[card] = ok if enough else None  # other cards: throughput and exactness tested, the smoke clause reported
        pc[card] = c
    oc = decide(holds["aifoundry2"], holds["aifoundry3"])
    ac = all_cards(hall, note="the smoke-test clause is registered for aifoundry3: reported on the other cards")
    reading = {"PASS": "throughput inside the bands, every kept launch exact with 0 bad minions, and the smoke tests pass on aifoundry3",
               "FAIL": "throughput, exactness or the aifoundry3 smoke tests failed on both cards: the page takes the measured values",
               "CARD-DIFFERENT": "holds on one card only: the page gives per-card throughput",
               "INSUFFICIENT": f"fewer than {NEED} kept passes per L2 mode on a card (or no aifoundry3 smoke-test record)"}[oc]
    return item("MMB-b", pc, "every kept L2 timed launch's tflops inside 9.501-9.521 / 19.00-19.04 / 71.70-71.86; every kept timed "
                "launch check=exact, bad_minions=0, launch_errors=0; aifoundry3: every mmbench-check (4 launches) and "
                "it_test_code_loading record rc 0 and exact; >= 3 kept passes per mode", oc, reading, {"all_cards": ac})


def e1_values(D, card, w, key):
    return [P["e1"][w][key] for P in D[card]["passes"] if w in P["e1"] and P["e1"][w]["power_ok"] and P["e1"][w][key] is not None]


def mmb_c(D):
    """Registered: above idle a2 fp32 26+-3, fp16 27+-3, int8 28+-3, DRAM 8+-2 W; a3 = 0.92 x a2 +-3 W; decided by
    'per card 99% t over 4 pass values excludes 0; a3/a2 ratio of pass means in 0.85-1.0'. A card holds if, for every
    workload, its interval excludes 0 and its pass mean is inside its registered band (a3: 0.92 x the a2 mean +-3 W, and
    the a3/a2 ratio in 0.85-1.0, both a3's prediction); a3 needs a2's >= 3 passes for its band."""
    band2 = {"fp32-tensor-L2": (23, 29), "fp16-tensor-L2": (24, 30), "int8-tensor-L2": (25, 31), DRAM: (6, 10)}
    pc, ratio = {c: {} for c in CARDS}, {}
    for card in CARDS:
        for w in WORKLOADS:
            s = summ(e1_values(D, card, w, "above_idle_w"))
            s["board_w"] = summ(e1_values(D, card, w, "mean_w")).get("mean")
            s["idle_before_w"] = summ(e1_values(D, card, w, "idle_before_w")).get("mean")
            s["die_c_mean"] = summ(e1_values(D, card, w, "die_c_mean")).get("mean")
            s["die_c_start"] = summ(e1_values(D, card, w, "die_c_start")).get("mean")
            pc[card][w] = s
    enough2 = all(pc["aifoundry2"][w]["n"] >= NEED for w in WORKLOADS)
    for w in WORKLOADS:
        c2, c3 = pc["aifoundry2"][w], pc["aifoundry3"][w]
        c2["band"] = band2[w]; c2["in_band"] = inb(c2.get("mean"), band2[w])
        m2, m3 = c2.get("mean") if c2["n"] >= NEED else None, c3.get("mean")
        ratio[w] = r(m3 / m2) if m2 and m3 is not None else None
        c3["ratio_a3_over_a2"] = ratio[w]; c3["ratio_in_0.85_1.0"] = ratio[w] is not None and 0.85 <= ratio[w] <= 1.0
        if m2 is not None:
            b3 = (0.92 * m2 - 3, 0.92 * m2 + 3)
            c3["band"] = [r(b3[0], 2), r(b3[1], 2)]; c3["in_band"] = inb(m3, b3)
        else:
            c3["band"] = None; c3["in_band"] = None
    holds = {}
    for card in CARDS:
        rows = pc[card].values()
        if any(x["n"] < NEED for x in rows) or (card == "aifoundry3" and not enough2):
            holds[card] = None
            continue
        ok = all(x["excludes_0"] and x["in_band"] for x in rows)
        if card == "aifoundry3":
            ok = ok and all(x["ratio_in_0.85_1.0"] for x in rows)
        holds[card] = ok
    for card in CARDS:
        for w in WORKLOADS:
            x = pc[card][w]
            if x["n"] >= NEED and holds[card] is not None:
                x["holds"] = bool(x["excludes_0"] and x["in_band"] and (card == "aifoundry2" or x["ratio_in_0.85_1.0"]))
    oc = decide(holds["aifoundry2"], holds["aifoundry3"])
    miss = {card: [w for w in WORKLOADS if pc[card][w].get("holds") is False] for card in CARDS}
    reading = {"PASS": f"above-idle power real (99% t excludes 0) and inside the registered bands on both cards; a3/a2 ratios {ratio} inside 0.85-1.0",
               "FAIL": f"not as registered on either card (failing workloads {miss}; a3/a2 ratios {ratio}): the page states the measured per-card watts with die temperature",
               "CARD-DIFFERENT": f"as registered on one card only (failing workloads {miss}; a3/a2 ratios {ratio}): the page gives per-card watts with die temperature",
               "INSUFFICIENT": f"fewer than {NEED} kept passes for some workload on a card (aifoundry3's band needs aifoundry2's)"}[oc]
    hall = dict(holds)
    for card in extra_cards(D):  # reported: the value, where it would fall in each registered band, the idle clock
        pc[card] = {}
        for w in WORKLOADS:
            x = summ(e1_values(D, card, w, "above_idle_w"))
            x["board_w"] = summ(e1_values(D, card, w, "mean_w")).get("mean")
            x["idle_before_w"] = summ(e1_values(D, card, w, "idle_before_w")).get("mean")
            x["die_c_mean"] = summ(e1_values(D, card, w, "die_c_mean")).get("mean")
            x["die_c_start"] = summ(e1_values(D, card, w, "die_c_start")).get("mean")
            x["idle_before_mhz"] = sorted({m for P in D[card]["passes"] if w in P["e1"] and P["e1"][w]["power_ok"]
                                           for m in (P["e1"][w].get("idle_before_mhz") or [])})
            m2 = pc["aifoundry2"][w].get("mean") if pc["aifoundry2"][w]["n"] >= NEED else None
            x["reported_only"] = True
            x["in_a2_band"] = inb(x.get("mean"), band2[w]) if x.get("mean") is not None else None
            x["ratio_to_a2"] = r(x["mean"] / m2) if (m2 and x.get("mean") is not None) else None
            x["a3_rule_band_from_a2"] = [r(0.92 * m2 - 3, 2), r(0.92 * m2 + 3, 2)] if m2 else None
            pc[card][w] = x
        hall[card] = REPORTED
    idl = {c: {k: v for k, v in IDLE[c].items() if k in ("idle_mhz", "differs", "e1_idle_before_mhz", "block_state")} for c in pc}
    return item("MMB-c", pc, "per card and workload, pass values of mean_w - idle_before_w: the 99% t interval excludes 0 and the "
                "pass mean is inside the band (a2: 23-29 / 24-30 / 25-31 / 6-10 W; a3: 0.92 x the a2 mean +-3 W and the a3/a2 "
                "ratio of pass means in 0.85-1.0); a card holds if every workload does",
                oc, reading, {"cross": {"ratio_a3_over_a2": ratio,
                                        "ratio_in_0.85_1.0": all(v is not None and 0.85 <= v <= 1.0 for v in ratio.values())},
                              "all_cards": all_cards(hall, idle=idl, note="the watt bands are aifoundry2's (aifoundry3's relative "
                                                     "to it): aifoundry1's above-idle watts are reported with their idle clock")})


def mmb_d(D):
    pc, cross, ok, enough = {c: {} for c in D}, {}, True, True
    alpha = 0.01 / 3
    for w in L2:
        a2, a3 = e1_values(D, "aifoundry2", w, "gflops_per_w"), e1_values(D, "aifoundry3", w, "gflops_per_w")
        for card, v in (("aifoundry2", a2), ("aifoundry3", a3)):
            pc[card][w] = summ(v); pc[card][w]["die_c_mean"] = summ(e1_values(D, card, w, "die_c_mean")).get("mean")
        if len(a2) < NEED or len(a3) < NEED:
            enough = False; cross[w] = None; continue
        W = welch(a2, a3); ratio = st.fmean(a3) / st.fmean(a2)
        sig = W["p"] < alpha
        cross[w] = {**W, "alpha": round(alpha, 5), "significant": sig, "ratio_a3_over_a2": round(ratio, 4),
                    "holds": sig and ratio >= 1.08}
        if not cross[w]["holds"]:
            ok = False
    oc = "INSUFFICIENT" if not enough else ("PASS" if ok else "FAIL")
    hall = {"aifoundry2": REPORTED, "aifoundry3": REPORTED}
    for card in extra_cards(D):  # reported: per W per mode, its ratio to aifoundry2 and a Welch test against it (info)
        for w in L2:
            v, a2v = e1_values(D, card, w, "gflops_per_w"), e1_values(D, "aifoundry2", w, "gflops_per_w")
            pc[card][w] = summ(v); pc[card][w]["die_c_mean"] = summ(e1_values(D, card, w, "die_c_mean")).get("mean")
            pc[card][w]["reported_only"] = True
            if len(v) >= NEED and len(a2v) >= NEED:
                pc[card][w]["ratio_to_a2"] = round(st.fmean(v) / st.fmean(a2v), 4)
                pc[card][w]["welch_vs_a2_info"] = welch(a2v, v)
        hall[card] = REPORTED
    ac = all_cards(hall, note="a comparison of aifoundry3 with aifoundry2: aifoundry1's per-W values and their ratio to "
                   "aifoundry2 are reported")
    reading = {"PASS": "board per W higher on a3 by >= 8% in every L2 mode (Welch, alpha 0.01/3): stated as the card at its operating temperature, not a card property",
               "FAIL": "a3's board per W is not significantly >= 8% above a2's in every L2 mode: the page states per-card efficiency with die temperature",
               "INSUFFICIENT": f"fewer than {NEED} kept passes per L2 mode on a card"}[oc]
    return item("MMB-d", pc, "per L2 mode, Welch t on pass values of board GFLOP/s per W (gflops_per_w), two-sided, alpha 0.01/3; "
                "holds if significant with mean(a3)/mean(a2) >= 1.08, in all three modes", oc, reading,
                {"cross": cross, "all_cards": ac})


def mmb_e(D):
    """Registered: A100 int8 lead (1560 / ET GOP/s per W) a2 1.25-1.45x, a3 1.00-1.25x; decided by 'one-sided 99% t vs
    1560 per card; if aifoundry3's interval includes 1560 the page drops "the A100 wins int8 efficiency" as a general
    statement'. A card holds if the A100 wins there (one-sided 99% upper bound of the pass values < 1560) and the lead
    1560 / pass mean is inside the card's band."""
    pc, holds = {}, {}
    band = {"aifoundry2": (1.25, 1.45), "aifoundry3": (1.00, 1.25)}
    for card in CARDS:
        s = summ(e1_values(D, card, "int8-tensor-L2", "gflops_per_w"), one_sided_upper=True)
        s["lead_band"] = band[card]
        if s["n"]:
            s["a100_lead"] = r(A100_INT8_PER_W / s["mean"])
            s["lead_in_band"] = inb(s["a100_lead"], band[card])
        if s["n"] < NEED:
            holds[card] = None
        else:
            s["a100_wins"] = s["upper99_one_sided"] < A100_INT8_PER_W
            holds[card] = bool(s["a100_wins"] and s["lead_in_band"])
            s["holds"] = holds[card]
        pc[card] = s
    oc = decide(holds["aifoundry2"], holds["aifoundry3"])
    a3 = pc["aifoundry3"]
    if a3["n"] >= NEED and not a3["a100_wins"]:
        cons = "aifoundry3's one-sided interval includes 1560: the page drops 'the A100 wins int8 efficiency' as a general statement"
    elif all(pc[c]["n"] >= NEED and pc[c]["a100_wins"] for c in CARDS):
        cons = "the A100 wins int8 efficiency on both cards"
    else:
        cons = "the A100 wins on aifoundry3; see per_card for aifoundry2" if a3["n"] >= NEED else "not decided yet"
    leads = {c: pc[c].get("a100_lead") for c in CARDS}
    hall = dict(holds)
    for card in extra_cards(D):
        x = summ(e1_values(D, card, "int8-tensor-L2", "gflops_per_w"), one_sided_upper=True)
        x["lead_band"] = None; x["reported_only"] = True
        if x["n"]:
            x["a100_lead"] = r(A100_INT8_PER_W / x["mean"])
            x["in_a2_lead_band"] = inb(x["a100_lead"], band["aifoundry2"])
            x["in_a3_lead_band"] = inb(x["a100_lead"], band["aifoundry3"])
        if x["n"] >= NEED:
            x["a100_wins"] = x["upper99_one_sided"] < A100_INT8_PER_W
        pc[card] = x
        hall[card] = REPORTED
    enough_all = [c for c in pc if pc[c]["n"] >= NEED]
    lose = [c for c in enough_all if not pc[c]["a100_wins"]]
    cons_all = ("not decided yet" if not enough_all else
                f"on {lose} the one-sided interval includes 1560: 'the A100 wins int8 efficiency' is not general across the cards"
                if lose else f"the A100 wins int8 efficiency on every card with {NEED} kept passes {enough_all}")
    ac = all_cards(hall, note=f"the lead bands are per registered card; consequence over all cards: {cons_all}")
    ac["consequence"] = cons_all
    reading = {"PASS": f"the A100 wins on both cards with the lead inside the registered bands {leads}",
               "FAIL": f"on neither card is the lead as registered {leads}: the page takes the measured lead per card; {cons}",
               "CARD-DIFFERENT": f"as registered on one card only {leads}: per-card lead; {cons}",
               "INSUFFICIENT": f"fewer than {NEED} kept int8 passes on a card"}[oc]
    return item("MMB-e", pc, "per card, one-sided 99% t (t_0.99,n-1) on pass values of int8 board GOP/s per W: the A100 wins if "
                "the upper bound < 1560; a card holds if the A100 wins and 1560/mean is inside its band (a2 1.25-1.45, "
                "a3 1.00-1.25)", oc, reading, {"consequence": cons, "all_cards": ac})


def mmb_f(D):
    pc, holds = {c: {} for c in D}, {}
    for card in list(CARDS) + extra_cards(D):
        ok, enough = True, True
        for w in WORKLOADS:
            s = summ(e1_values(D, card, w, "rise_w"))
            if w == DRAM:
                # "~0": equivalence, the 99% interval inside +-0.5 W (the lower edge of the registered L2 band)
                s["claim"] = "~0: the 99% interval inside +-0.5 W"
                s["holds"] = (-0.5 < s["ci99"][0] and s["ci99"][1] < 0.5) if s["n"] >= NEED else None
            else:
                s["claim"] = ("+0.5 to +2 W, 99% interval above 0" if card == "aifoundry2" else
                              "rise > 0 (no band registered for a3)" if card == "aifoundry3" else
                              "rise > 0 (no band registered for this card: aifoundry3's rule)")
                if s["n"] >= NEED:
                    s["holds"] = s["ci99"][0] > 0 and (card != "aifoundry2" or inb(s["mean"], (0.5, 2.0)))
                else:
                    s["holds"] = None
            pc[card][w] = s
            if s["holds"] is None:
                enough = False
            elif not s["holds"]:
                ok = False
        holds[card] = ok if enough else None
    oc = decide(holds["aifoundry2"], holds["aifoundry3"])
    ac = all_cards(holds, note="aifoundry1's cards: the L2 rise's sign (no band registered for them, as aifoundry3) and "
                   "the DRAM ~0 clause")
    reading = {"PASS": "power rises within each 6 s L2 workload on both cards (a2 by 0.5-2 W) and not on the DRAM workload",
               "FAIL": "the within-run rise did not hold on either card as registered: the page takes the measured rise per card",
               "CARD-DIFFERENT": "the within-run rise holds on one card only: per-card statement",
               "INSUFFICIENT": f"fewer than {NEED} kept passes per workload on a card"}[oc]
    return item("MMB-f", pc, "per card and workload, pass values of mean(last 1 s) - mean(first 1 s) of the mean_w window (after the "
                "1 s settle, samples inside launches); L2: 99% interval above 0 and, on a2, mean in 0.5-2.0 W; DRAM: 99% "
                "interval inside +-0.5 W", oc, reading, {"all_cards": ac})


def mmb_x1(D):
    parts = {"a": [("shared", "fp32", (528.5, 529.5)), ("shared", "fp16", (528.5, 529.5)), ("shared", "int8", (279.4, 281.4))],
             "b": [("private", "fp32", (529.0, 545.0)), ("private", "fp16", (529.0, 545.0))],
             "c": [("private", "int8", (480.0, 560.0))]}
    per = {c: {} for c in D}
    for card in D:  # every card (the computation is per card; the registered two decide "outcome")
        for kind in ("shared", "private"):
            for m in ("fp32", "fp16", "int8"):
                ps = [P["x1"][(kind, m)] for P in D[card]["passes"] if (kind, m) in P["x1"] and any(q["_keep"] for q in P["x1"][(kind, m)])]
                ks = [q for L in ps for q in L if q["_keep"]]
                cyc = [q["_cyc_max"] for q in ks]
                per[card][f"{kind}-{m}"] = {"passes": len(ps), "launches": len(ks),
                                             "dropped_launches": sum(1 for L in ps for q in L if not q["_keep"]),
                                             "cycles_per_op": [r(min(cyc), 3), r(max(cyc), 3)] if cyc else None,
                                             "cycles_per_op_mean": r(st.fmean(cyc), 3) if cyc else None,
                                             "B_per_minion_cycle": [r(2048 / max(cyc), 3), r(2048 / min(cyc), 3)] if cyc else None,
                                             "checks": sorted({q["check"] for q in ks}),
                                             "_cyc": cyc}
    out = []
    sub_oc, sub_all = {}, {}
    for p, rows in parts.items():
        pc, holds = {}, {}
        for card in list(CARDS) + extra_cards(D):  # registered for every card: tested on aifoundry1's cards unchanged
            ok, enough, c = True, True, {}
            for kind, m, b in rows:
                v = dict(per[card][f"{kind}-{m}"]); cyc = v.pop("_cyc")
                v["band"] = b; v["out_of_band"] = [round(x, 2) for x in cyc if not b[0] <= x <= b[1]]
                c[f"{kind}-{m}"] = v
                if v["passes"] < NEED:
                    enough = False
                elif v["out_of_band"]:
                    ok = False
            holds[card] = ok if enough else None
            pc[card] = c
        oc = decide(holds["aifoundry2"], holds["aifoundry3"])
        extra = {"all_cards": all_cards(holds)}
        if p == "b":
            above = {card: any(x > 560 for kind, m, _ in rows for x in per[card][f"{kind}-{m}"]["_cyc"]) for card in CARDS}
            extra["consequence"] = ("drop \"can just keep fp32 and fp16 busy\" and give the measured %" if any(above.values())
                                    else "no card above 560 cycles/op")
            extra["above_560"] = above
            above_all = {card: any(x > 560 for kind, m, _ in rows for x in per[card][f"{kind}-{m}"]["_cyc"]) for card in D}
            extra["all_cards"]["above_560"] = above_all
            extra["all_cards"]["consequence"] = (f"above 560 cycles/op on {[c for c, v in above_all.items() if v]}: drop \"can "
                                                 "just keep fp32 and fp16 busy\" there" if any(above_all.values())
                                                 else "no card above 560 cycles/op")
        if p == "c":
            cyc = {card: per[card]["private-int8"]["_cyc"] for card in CARDS}
            if all(cyc.values()) and all(max(v) <= 330 for v in cyc.values()):
                cons = "refutes the shared-pool cause: private tiles reach the measured rate (own-shire 4.0 B/cycle is a probe limit)"
            elif all(cyc.values()) and all(330 < min(v) and max(v) < 480 for v in cyc.values()):
                cons = "330-480 cycles/op: report the measured rate, cause open"
            elif oc == "PASS":
                cons = "480-560 cycles/op on both cards: the own-shire streaming rate binds and the shared pool explains 7.3 B/cycle"
            else:
                cons = "report the measured per-card rates (see per_card)"
            extra["consequence"] = cons
            ca = {card: per[card]["private-int8"]["_cyc"] for card in D}
            if all(ca.values()) and all(max(v) <= 330 for v in ca.values()):
                cons_all = "<= 330 cycles/op on every card: refutes the shared-pool cause on all cards"
            elif all(ca.values()) and all(330 < min(v) and max(v) < 480 for v in ca.values()):
                cons_all = "330-480 cycles/op on every card: report the measured rate, cause open"
            elif extra["all_cards"]["outcome"] == "PASS":
                cons_all = "480-560 cycles/op on every card: the own-shire streaming rate binds on all cards"
            else:
                cons_all = "report the measured per-card rates (see per_card)"
            extra["all_cards"]["consequence"] = cons_all
        reading = {"PASS": f"X1({p}) every kept launch inside the band on both cards",
                   "FAIL": f"X1({p}) outside the band on both cards",
                   "CARD-DIFFERENT": f"X1({p}) inside the band on one card only",
                   "INSUFFICIENT": f"X1({p}) fewer than {NEED} passes with kept launches on a card"}[oc]
        if "consequence" in extra:
            reading += "; " + extra["consequence"]
        sub_oc[p] = oc
        sub_all[p] = extra["all_cards"]["outcome"]
        out.append(item(f"MMB-X1/{p}", pc, "deterministic per launch: cycles_max/ops_per_minion of every kept launch (implied_ghz "
                        "0.595-0.605) inside the band; >= 3 passes per card", oc, reading, extra))
    vals = list(sub_oc.values())
    comb = ("INSUFFICIENT" if "INSUFFICIENT" in vals else "PASS" if all(v == "PASS" for v in vals)
            else "FAIL" if "FAIL" in vals else "CARD-DIFFERENT")
    for card in D:
        for v in per[card].values():
            v.pop("_cyc", None)
    ca = comb_all(list(sub_all.values()))
    out.insert(0, item("MMB-X1", per, "summary of MMB-X1/a, /b, /c (each decided on its own)", comb,
                       f"a {sub_oc['a']}, b {sub_oc['b']}, c {sub_oc['c']}",
                       {"all_cards": {"outcome": ca, "sub_items": sub_all,
                                      "reading": f"a {sub_all['a']}, b {sub_all['b']}, c {sub_all['c']} (all cards)"}}))
    return out


def load_step(D):
    import x1_reduce  # the plan's reducer (copy): imports tools/ettelem/summarize_power_session.py read-only
    per = {}
    for card in D:  # every card; the registered two exactly as before
        rows = []
        for P in D[card]["passes"]:
            if not P["thermal"]:
                continue
            try:
                o = x1_reduce.reduce_pass(P["thermal"], SHORT.get(card) or cardrules.short(card))
            except Exception as e:  # a broken pass: reported, never used
                rows.append({"pass": P["pass"], "error": f"{type(e).__name__}: {e}", "valid": False})
                continue
            o["pass"] = P["pass"]
            try:  # the clock of every phase's idle and busy samples (four cards); the busy rule's validity
                o["clock"] = cardrules.load_step_clock(P["thermal"], load_jsonl(os.path.join(P["thermal"], "thermal-telemetry.jsonl")),
                                                       load_jsonl(os.path.join(P["thermal"], "thermal-phases.jsonl")))
            except Exception as e:
                o["clock"] = {"error": f"{type(e).__name__}: {e}", "valid_busy_rule": False}
            if P["rule"] == "busy":  # aifoundry1's cards: busy samples only (x1_reduce's "valid" is the a2 rule)
                o["valid"] = bool(o["clock"].get("valid_busy_rule"))
            rows.append(o)
        per[card] = rows
    return per


def idle_clock(D, per=None):
    """Each card's idle clock: E1's 8 s idle and idle-before windows, the load step's idle samples (idle0, the idle-after
    bracket, every phase), the block's start/end records (ettelem config's power_state) and ridge-X1's before/after
    reading. differs: any idle reading off 600 MHz (aifoundry1-c0's low_power state is 300 MHz)."""
    out = {}
    for card in D:
        e1i, e1b, st_names, st_mhz, x1c = set(), set(), set(), set(), set()
        for P in D[card]["passes"]:
            for e in P["e1"].values():
                e1i.update(e.get("idle_mhz") or []); e1b.update(e.get("idle_before_mhz") or [])
            for r in P["idle_state"]:
                cfg = r.get("config") or {}
                if cfg.get("power_state_name"):
                    st_names.add(f"{r.get('at')}:{cfg['power_state_name']}")
                for m in (cfg.get("minion_mhz"), r.get("mhz_minion")):
                    if m:
                        st_mhz.add(m)
            for r in P["x1_clock"]:
                if r.get("mhz_minion"):
                    x1c.add(r["mhz_minion"])
        ls, l0, la = set(), set(), set()
        for o in (per or {}).get(card, []):
            ck = o.get("clock") or {}
            ls.update(ck.get("idle_mhz") or []); l0.update(ck.get("idle0_mhz") or []); la.update(ck.get("idle_after_mhz") or [])
        allm = e1i | e1b | ls | st_mhz | x1c
        out[card] = {"idle_mhz": sorted(allm), "differs": any(m != 600 for m in allm),
                     "e1_idle_mhz": sorted(e1i), "e1_idle_before_mhz": sorted(e1b), "load_step_idle_mhz": sorted(ls),
                     "load_step_idle0_mhz": sorted(l0), "load_step_idle_after_mhz": sorted(la),
                     "block_state": sorted(st_names), "block_state_mhz": sorted(st_mhz), "x1_before_after_mhz": sorted(x1c)}
    return out


def mmb_t(D, per=None):
    per = per if per is not None else load_step(D)
    kept = {c: [o for o in per[c] if o.get("valid")] for c in D}
    dropped = {c: [o["pass"] for o in per[c] if not o.get("valid")] for c in D}
    items = []
    EX = extra_cards(D)
    idl = {c: {k: IDLE.get(c, {}).get(k) for k in ("idle_mhz", "differs", "load_step_idle0_mhz", "load_step_idle_after_mhz",
                                                     "block_state")} for c in D}

    def sgn(x):
        return (1 if x["ci99"][0] > 0 else -1 if x["ci99"][1] < 0 else 0) if x.get("n", 0) >= NEED and "ci99" in x else None

    def ext(pc, key=None, getter=None, band=None, need_excl=True, reported=False, idle=False, note="", sign=True):
        """Four cards: add aifoundry1's cards to a ci_item-style sub-item and return its all_cards. reported: the band
        is per registered card, so the other cards are reported; else tested with the band registered for each card."""
        hall, sg = {c: pc[c]["holds"] for c in CARDS}, {c: sgn(pc[c]) for c in CARDS}
        for c in EX:
            x = summ([getter(o) if getter else o[key] for o in kept[c]])
            x["band"] = None if reported else band
            if reported:
                x["reported_only"] = True; x["holds"] = None; hall[c] = REPORTED
            elif x["n"] >= NEED:
                h = True
                if need_excl:
                    h = h and x["excludes_0"]
                if band:
                    h = h and inb(x["mean"], band)
                x["holds"] = h; hall[c] = h; sg[c] = sgn(x)
            else:
                x["holds"] = None; hall[c] = None
            pc[c] = x
        return all_cards(hall, sign={c: v for c, v in sg.items() if v is not None} if (sign and need_excl) else None,
                         idle=idl if idle else None, note=note)

    def ci_item(name, key, bands, need_excl=True, band_test=True, getter=None, note=""):
        pc, holds = {}, {}
        sig = {}
        for card in CARDS:
            xs = [getter(o) if getter else o[key] for o in kept[card]]
            s = summ(xs)
            b = bands.get(card) if bands else None
            s["band"] = b
            if s["n"] >= NEED:
                h = True
                if need_excl:
                    h = h and s["excludes_0"]
                if band_test and b:
                    h = h and inb(s["mean"], b)
                s["holds"] = h
                sig[card] = (1 if s["ci99"][0] > 0 else -1 if s["ci99"][1] < 0 else 0)
            else:
                s["holds"] = None
            pc[card] = s
            holds[card] = s["holds"]
        oc = decide(holds["aifoundry2"], holds["aifoundry3"])
        if len(sig) == 2 and sig["aifoundry2"] * sig["aifoundry3"] == -1:
            oc = "CARD-DIFFERENT"  # registered: sign disagreement
        return pc, oc

    def add(name, pc, oc, test, reading, hint, extra=None, ac=None):
        e = {"claims_hint_unregistered": hint}
        if extra:
            e.update(extra)
        if ac is not None:
            e["all_cards"] = ac
        items.append(item(f"MMB-T/{name}", pc, test, oc, reading, e, claims=CLAIMS["MMB-T"]))

    pc, oc = ci_item("P1", "busy_slope_board", {"aifoundry2": (0.70, 0.90), "aifoundry3": (0.30, 0.60)})
    ac = ext(pc, key="busy_slope_board", reported=True, note="the busy-slope bands are per registered card")
    for c in D:
        pc[c]["busy_T_range"] = [o["busy_T_range"] for o in kept[c]]
    add("P1", pc, oc, "busy slope board W/C (fit from 5 s after launch): 99% t excludes 0 and pass mean in band (a2 0.70-0.90, a3 0.30-0.60)",
        f"busy slope {oc}", ["pt-spatial-02", "pt-spatial-08", "pt-spatial-20", "pt-spatial-23", "pt-spatial-24", "horace-lowpower-030", "horace-lowpower-090"],
        ac=ac)
    pc, oc = ci_item("P2", None, {"aifoundry2": (0.45, 0.55), "aifoundry3": (0.40, 0.60)}, need_excl=False,
                     getter=lambda o: o["busy_slope_minion"] / o["busy_slope_board"] if o["busy_slope_board"] else None)
    ac = ext(pc, getter=lambda o: o["busy_slope_minion"] / o["busy_slope_board"] if o["busy_slope_board"] else None,
             reported=True, need_excl=False, note="the share bands are per registered card")
    add("P2", pc, oc, "minion-rail share of the busy slope (busy_slope_minion / busy_slope_board): pass mean in band (a2 0.45-0.55, "
        "a3 0.40-0.60); the decision column names no interval test for P2", f"minion share {oc}", ["pt-spatial-08", "pt-spatial-20"],
        ac=ac)
    pc, oc = ci_item("P3", "idle_after_minus_before_w", {"aifoundry2": (3.0, 7.0), "aifoundry3": (1.0, 4.0)})
    law = summ([o["idle_after_minus_before_w"] - o["idle_after_minus_before_law_w"] for o in kept["aifoundry2"]])
    pc["aifoundry2"]["minus_idle_law"] = law
    if pc["aifoundry2"]["holds"] is not None:
        pc["aifoundry2"]["holds"] = pc["aifoundry2"]["holds"] and abs(law["mean"]) <= 0.7
        oc = decide(pc["aifoundry2"]["holds"], pc["aifoundry3"]["holds"])
    ac = ext(pc, key="idle_after_minus_before_w", reported=True, idle=True,
             note="the bands (and the idle-law clause) are per registered card")
    for c in D:
        pc[c]["idle_before"] = [o["idle_before"] for o in kept[c]]; pc[c]["idle_after"] = [o["idle_after"] for o in kept[c]]
    add("P3", pc, oc, "idle after - idle before (W): 99% t excludes 0 and pass mean in band (a2 3-7, a3 1-4); a2 also mean of "
        "(measured - idle-law) within +-0.7 W", f"idle after the load {oc}", ["pt-spatial-04", "pt-spatial-25", "pt-spatial-27"],
        ac=ac)
    pc, oc = ci_item("P4-remainder", "dram_rest_rise_w", {"aifoundry2": (3.0, 7.0), "aifoundry3": (3.0, 7.0)})
    ac = ext(pc, key="dram_rest_rise_w", band=(3.0, 7.0), idle=True, note="registered for each card (3-7 W): tested on every card")
    add("P4-remainder", pc, oc, "DRAM-phase remainder rise over the cool1 baseline (W): 99% t excludes 0 and mean in 3-7",
        f"DRAM remainder {oc}", ["pt-spatial-26", "pt-spatial-29", "pt-spatial-31"], ac=ac)
    pc, holds = {}, {}
    for c in list(CARDS) + EX:
        s = summ([o["dram_minion_rise_w"] for o in kept[c]]); s["bound"] = 1.0
        s["holds"] = (s["ci99"][1] < 1.0) if s["n"] >= NEED else None
        pc[c] = s; holds[c] = s["holds"]
    add("P4-minion", pc, decide(holds["aifoundry2"], holds["aifoundry3"]), "DRAM-phase minion-rail rise: upper end of the 99% t "
        "interval < 1.0 W", "minion rail under DRAM load", ["pt-spatial-31"],
        ac=all_cards(holds, idle=idl, note="registered for each card: tested on every card"))
    pc, oc = ci_item("P5-dram", None, {"aifoundry2": (2.0, 5.0), "aifoundry3": (2.0, 5.0)}, getter=lambda o: o["ddr"]["dram_below_trend"])
    ac = ext(pc, getter=lambda o: o["ddr"]["dram_below_trend"], band=(2.0, 5.0), idle=True,
             note="registered for each card (2-5 mV): tested on every card")
    add("P5-dram", pc, oc, "die_mv.ddr below the idle trend in the DRAM phase (mV): 99% t excludes 0 and mean in 2-5",
        f"DDR droop under DRAM load {oc}", ["pt-spatial-38", "pt-spatial-39"], ac=ac)
    pc, holds = {}, {}
    for c in list(CARDS) + EX:
        s = summ([o["ddr"]["mm_below_trend"] for o in kept[c]]); s["band"] = [-1.0, 1.0]
        s["holds"] = inb(s["mean"], (-1.0, 1.0)) if s["n"] >= NEED else None
        pc[c] = s; holds[c] = s["holds"]
    add("P5-matmul", pc, decide(holds["aifoundry2"], holds["aifoundry3"]), "die_mv.ddr below the idle trend under the matmul: pass "
        "mean within +-1 mV", "DDR under the matmul", ["pt-spatial-39"],
        ac=all_cards(holds, idle=idl, note="registered for each card: tested on every card"))
    pc, oc = ci_item("P6", "die_minion_droop_mv_per_w", {"aifoundry2": (0.03, 0.08), "aifoundry3": (0.03, 0.15)}, band_test=False)
    for c in CARDS:
        if pc[c].get("mean") is not None:
            pc[c]["in_reported_band"] = inb(pc[c]["mean"], pc[c]["band"])
    ac = ext(pc, key="die_minion_droop_mv_per_w", idle=True,
             note="the interval test is registered for each card (the bands are reported only): tested on every card")
    add("P6", pc, oc, "minion on-die droop per W of minion-rail rise (mV/W): 99% t excludes 0 (band only reported)",
        f"minion droop {oc}", ["pt-spatial-V02"], ac=ac)
    pc, holds = {}, {}
    for c in CARDS:
        rows = []
        for o in kept[c]:
            idle_lvl = min(o["rest_idle0"], o["rest_cool"]); mm_hi = o["rest_matmul_range"][1]
            rw = {"pass": o["pass"], "start_overshoot_w": round(o["edge_tau0"]["start_max"] - mm_hi, 2),
                  "stop_dip_w": round(idle_lvl - o["edge_tau0"]["min_stop_window"], 2),
                  "filtered": o["edge_tau_card"], "envelope": [round(idle_lvl - 1, 2), round(mm_hi + 1, 2)]}
            rw["holds"] = (rw["start_overshoot_w"] >= 10 and rw["stop_dip_w"] >= 2 and
                           o["edge_tau_card"][0] >= idle_lvl - 1 and o["edge_tau_card"][1] <= mm_hi + 1)
            rows.append(rw)
        h = all(x["holds"] for x in rows) if len(rows) >= NEED else None
        pc[c] = {"n": len(rows), "passes": rows, "holds": h}; holds[c] = h
    hall = dict(holds)
    for c in EX:  # the tau = 0 clauses are registered for each card; the filter clause names each card's own tau
        rows = []
        for o in kept[c]:
            idle_lvl = min(o["rest_idle0"], o["rest_cool"]); mm_hi = o["rest_matmul_range"][1]
            rw = {"pass": o["pass"], "start_overshoot_w": round(o["edge_tau0"]["start_max"] - mm_hi, 2),
                  "stop_dip_w": round(idle_lvl - o["edge_tau0"]["min_stop_window"], 2),
                  "filtered_reported": o["edge_tau_card"], "tau_used_reported": o.get("edge_tau_used"),
                  "envelope": [round(idle_lvl - 1, 2), round(mm_hi + 1, 2)]}
            rw["filtered_within_envelope_reported"] = (o["edge_tau_card"][0] >= idle_lvl - 1 and o["edge_tau_card"][1] <= mm_hi + 1)
            rw["holds"] = rw["start_overshoot_w"] >= 10 and rw["stop_dip_w"] >= 2
            rows.append(rw)
        h = all(x["holds"] for x in rows) if len(rows) >= NEED else None
        pc[c] = {"n": len(rows), "passes": rows, "holds": h,
                 "note": "tau = 0 clauses tested; the filtered clause uses aifoundry2's tau (this card's is not measured): reported"}
        hall[c] = h
    add("P7", pc, decide(holds["aifoundry2"], holds["aifoundry3"]), "every pass: tau=0 remainder start max - matmul steady "
        "level (top of rest_matmul_range) >= 10 W; idle level (lower of idle0 and cool1 remainders) - tau=0 stop-window min >= 2 W; "
        "filtered with the card's tau, min >= idle level - 1 W and max <= matmul steady top + 1 W", "edges", ["pt-spatial-32"],
        ac=all_cards(hall, idle=idl, note="aifoundry1's cards: the tau = 0 overshoot and dip tested; the filtered clause "
                     "(the card's own tau, registered for aifoundry2 and aifoundry3) reported with aifoundry2's tau"))
    pc, holds = {}, {}
    for c in list(CARDS) + EX:
        s = summ([o["board_avg_minus_board_steady_median"] for o in kept[c]]); s["bound"] = 0.5
        s["holds"] = (max(abs(s["ci99"][0]), abs(s["ci99"][1])) < 0.5) if s["n"] >= NEED else None
        pc[c] = s; holds[c] = s["holds"]
    add("P8", pc, decide(holds["aifoundry2"], holds["aifoundry3"]), "|PMIC board average - board| in steady state: the 99% t "
        "interval of the per-pass medians lies inside +-0.5 W", "PMIC average vs board", ["pt-spatial-32"],
        ac=all_cards(holds, note="registered for each card: tested on every card"))
    pc, holds = {}, {}
    for c in list(CARDS) + EX:
        rows = [{"pass": o["pass"], "mhz": o.get("mhz")} for o in kept[c]]
        h = all(x["mhz"] == [600] for x in rows) if len(rows) >= NEED else None
        pc[c] = {"n": len(rows), "passes": rows, "dropped_passes_off_600": dropped[c], "holds": h}; holds[c] = h
        if c not in CARDS:  # the busy rule kept these passes; say what the busy and the idle samples read
            for rw, o in zip(rows, kept[c]):
                ck = o.get("clock") or {}
                rw["busy_off_600"] = ck.get("busy_off_600"); rw["busy_ramp"] = ck.get("busy_ramp"); rw["idle_mhz"] = ck.get("idle_mhz")
            pc[c]["dropped_passes_note"] = "dropped by the busy rule (a busy sample off 600 MHz); idle samples never drop"
    add("P9", pc, decide(holds["aifoundry2"], holds["aifoundry3"]), "every kept pass: mhz.minion 600 in every sample (aifoundry2 "
        "passes off 600 are dropped by rule and listed)", "clock", ["pt-spatial-21"],
        ac=all_cards(holds, idle=idl, note="'600 MHz throughout' is registered for each card: every sample of every kept pass, "
                     "idle ones included, so a card that idles below 600 MHz does not hold it"))
    pc = {}
    s = summ([o["cool_drop_40s_c"] for o in kept["aifoundry2"]]); s["band"] = [4, 8]
    s["holds"] = inb(s.get("mean"), (4, 8)) if s["n"] >= NEED else None
    pc["aifoundry2"] = s
    pc["aifoundry3"] = summ([o["cool_drop_40s_c"] for o in kept["aifoundry3"]]); pc["aifoundry3"]["note"] = "reported without a prior"
    oc10 = "INSUFFICIENT" if s["holds"] is None else ("PASS" if s["holds"] else "FAIL")
    hall = {"aifoundry2": s["holds"], "aifoundry3": REPORTED}
    for c in EX:
        pc[c] = summ([o["cool_drop_40s_c"] for o in kept[c]]); pc[c]["note"] = "reported without a prior"; hall[c] = REPORTED
    add("P10", pc, oc10, "aifoundry2 only: pass mean of the die's drop in the 40 s after the matmul in 4-8 C (aifoundry3 reported)",
        "cooling after the matmul (a2)", ["pt-spatial-27"], ac=all_cards(hall, note="registered for aifoundry2 only"))
    # busy-minus-idle clause (pt-spatial-22): not decided by 4 passes, reported only
    bmi = summ([o["busy_slope_board"] - o["law_slope_same_bins"] for o in kept["aifoundry2"]])
    vals = [i["outcome"] for i in items]
    comb = ("INSUFFICIENT" if "INSUFFICIENT" in vals else "PASS" if all(v == "PASS" for v in vals)
            else "FAIL" if "FAIL" in vals else "CARD-DIFFERENT")
    subs = {i["item"].split("/")[1]: i["all_cards"]["outcome"] for i in items}
    summary = item("MMB-T", {c: {"passes_reduced": len(per[c]), "kept": len(kept[c]), "dropped": dropped[c],
                                 "clock_rule": (D[c]["passes"][0]["rule"] if D[c]["passes"] else cardrules.rule(c)),
                                 "errors": [o for o in per[c] if "error" in o]} for c in D},
                   "summary of P1-P10 (each decided on its own); pt-spatial-22's busy-minus-idle clause is reported, not decided",
                   comb, ", ".join(f"{i['item'].split('/')[1]} {i['outcome']}" for i in items),
                   {"busy_minus_idle_slope_a2_not_decided": bmi, "per_pass": {c: per[c] for c in D},
                    "all_cards": {"outcome": comb_all(list(subs.values())), "sub_items": subs,
                                  "reading": ", ".join(f"{k} {v}" for k, v in subs.items()) + " (all cards)"}})
    return [summary] + items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    # every card directory present (one holding mmb/ or mmb-smoke/), and the four campaign cards whether present or not
    present = [c for c in sorted(os.listdir(a.data)) if os.path.isdir(os.path.join(a.data, c, "mmb"))
               or os.path.isdir(os.path.join(a.data, c, "mmb-smoke"))]
    cards = list(cardrules.CAMPAIGN) + [c for c in present if c not in cardrules.CAMPAIGN]
    D = {c: load_card(os.path.join(a.data, c), c) for c in cards}
    per = load_step(D)
    IDLE.clear(); IDLE.update(idle_clock(D, per))
    items = [mmb_a(D), mmb_b(D), mmb_c(D), mmb_d(D), mmb_e(D), mmb_f(D)] + mmb_x1(D) + mmb_t(D, per)
    doc = {"exp": "V3-MMB", "data": os.path.abspath(a.data), "need_kept_repeats": NEED,
           "cards": {"registered": list(CARDS), "all": cards, "present": present,
                     "missing": [c for c in cards if c not in present],
                     "clock_rule": {c: sorted({P["rule"] for P in D[c]["passes"]}) or [cardrules.rule(c)] for c in cards}},
           "passes": {c: [{"pass": P["pass"], "status": P["status"], "e1": sorted(P["e1"]), "x1": len(P["x1"]),
                           "thermal": bool(P["thermal"])} for P in D[c]["passes"]] for c in cards},
           "idle_clock": IDLE,
           "items": items}
    with open(a.out, "w") as f:
        json.dump(doc, f, indent=1, default=str)
    if not a.quiet:
        print(f"{'item':16s} {'registered':15s} {'all cards':15s} reading (registered)")
        for i in items:
            print(f"{i['item']:16s} {i['outcome']:15s} {i.get('all_cards', {}).get('outcome', '-'):15s} {i['reading']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
