#!/usr/bin/env python3
"""E96 (Q132): the registered reduction -- the burst and sustained speed, board power, die temperature and switching term of
Q132(r)'s real2 tiles, E87's six anchors and the int8 arm, on aifoundry2 under its own governor, and the decision rules of
README.md scored against this folder's frozen predictions.json (Q132(r)'s points and intervals, claims.E96 verbatim).

    python3 reduce_e96.py <RUNDIR> [--smoke <SMOKEDIR>] [--history <jsonl[.gz]>] [--pred predictions.json] [--out results.json] > reduce.txt

PER RUN: E80's, E83's and E87's reduction, imported unchanged -- reduce_hpl.run_metrics (E64's registered per-run metrics) plus
reduce_kspeed.burst_extra and reduce_kspeed.sus_limit; beside them, labelled, E80 amendment A1's idle-reset view
(posthoc_idle.flags, through reduce_e83.a1_view, unchanged).

PER KIND: the burst cell is the mean of its two BURST passes; the sustained cell is the mean of its SUS runs (two for fp32 randn and
fp16 randn, one per round for the arm's kinds); the cell's c is the mean of its burst passes' c.

THE RULES (README.md "Decision rules"). S1-S5 are claims.E96 of Q132(r)'s predictions-real2.json, frozen there, implemented here as
written. The rest are this lane's own, frozen in this folder, and move none of those.
  E96-S1   E83's relation fed (a) holds the clocks: burst cells inside burst_scoring_interval_mhz, sustained cells inside
           sus_scoring_interval_mhz; each PASS at >= 80% of the tiles run, FAIL at < 60%, else INCONCLUSIVE
  E96-S2   the gate buys burst clock: per tile, burst - same-session randn of its format; PASS if every one >= +40 MHz, FAIL if any < +15
  E96-S2b  the gate buys sustained clock: per tile, sustained - same-session randn; PASS if every one >= +50 MHz, FAIL if any < +15
  E96-S3   no-zero real tiles burst at random's speed: per format, |tiles' mean burst - randn| <= 15 MHz in both, else FAIL
  E96-S4   the sustained limit: right for >= 80% of the tiles run PASS, < 60% FAIL (a tile is right only if every run carries the label)
  E96-S5   the relation on measured c: burst rms and sustained rms each <= 15 MHz PASS, either > 25 MHz FAIL
  E96-T    the sessions tie: each anchor's burst and sustained cell within 25 MHz of the mean of the earlier sessions' cells (E80, E83, E87)
  E96-I1   the arm's clock: paired by round, mean(three real tiles) - full, 95% t interval over whole rounds, against 0 and +-15 MHz
  E96-I2   the arm's board W, same pairing, against 0
  E96-I3   the arm's die, same pairing, against 0
UNDER-RESOLVED, never PASS: a rule short of its population (predictions.json minimum_population; S2, S2b, S3 need every named tile and
randn). I1-I3 with fewer than 3 whole rounds are NOT SCORED. A FAIL that the tiles measured already force stands.
Labelled, never a verdict: the reset-free view of every clock rule; the frozen D-propagated ranges beside S1; the gate law's clocks; a no-model
baseline; the like-with-like ratios; the arm per tile, with dips left out, at fixed clock (fine W) and with a pooled two-way interval; the die line,
the line at E98's k, its trend through the session; (a-adj E96); the rest readings; the sustained differences of the no-zero tiles.
"""
import argparse
import gzip
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "hpl"))
sys.path.insert(0, os.path.join(HERE, "..", "e83"))
import reduce_hpl as R  # noqa: E402
import reduce_kspeed as RK  # noqa: E402
import predict_e83 as PE  # noqa: E402
import reduce_e83 as RE  # noqa: E402
import posthoc_idle as PI  # noqa: E402

rms, mean = RK.rms, RK.mean
RAMP_AFTER_DIP_S = 3.0         # E98's fine W: each dip and the 3 s after it are left out
FINE_MIN_SHARE = 0.7           # E98's: the fine W exists only with at least 70% of the window left
ARM_PROCS = 9


def rnd(x, n=1):
    return None if x is None else round(x, n)


def inside(x, iv):
    return x is not None and iv[0] <= x <= iv[1]


def tval(n, table):
    """t(0.975, n - 1) from the frozen table."""
    return table[str(n - 1)] if str(n - 1) in table else table.get(n - 1, 1.96)


# ---------------------------------------------------------------------------------------- the scoring: pure, so the self-test can plant data
def share_verdict(right, n, need, pass_share, fail_share):
    if n < need:
        return "UNDER-RESOLVED"
    s = right / n
    return "PASS" if s >= pass_share else ("FAIL" if s < fail_share else "INCONCLUSIVE")


def both_verdict(a, b):
    if "FAIL" in (a, b):
        return "FAIL"
    if "UNDER-RESOLVED" in (a, b):
        return "UNDER-RESOLVED"
    return "PASS" if a == b == "PASS" else "INCONCLUSIVE"


def score_s1(cells, pred):
    B, M = pred["bars"], pred["minimum_population"]
    T = pred["tiles"]
    hb = [k for k in T if cells.get(k, {}).get("burst_mhz") is not None]
    hs = [k for k in pred["sus_core"] if cells.get(k, {}).get("sus_mhz") is not None]
    inb = [k for k in hb if inside(cells[k]["burst_mhz"], T[k]["frozen"]["burst_scoring_interval_mhz"])]
    ins = [k for k in hs if inside(cells[k]["sus_mhz"], T[k]["frozen"]["sus_scoring_interval_mhz"])]
    vb = share_verdict(len(inb), len(hb), M["S1_burst"], B["S1_pass_share"], B["S1_fail_share"])
    vs = share_verdict(len(ins), len(hs), M["S1_sus"], B["S1_pass_share"], B["S1_fail_share"])
    return {"population_burst": len(hb), "population_sus": len(hs), "burst_inside": len(inb), "sus_inside": len(ins),
            "verdict_burst": vb, "verdict_sus": vs, "verdict": both_verdict(vb, vs),
            "rows": [[k, cells[k].get("burst_mhz"), T[k]["frozen"]["burst_mhz"], T[k]["frozen"]["burst_scoring_interval_mhz"],
                      inside(cells[k].get("burst_mhz"), T[k]["frozen"]["burst_scoring_interval_mhz"]),
                      cells[k].get("sus_mhz"), T[k]["frozen"]["sus_mhz"], T[k]["frozen"]["sus_scoring_interval_mhz"],
                      inside(cells[k].get("sus_mhz"), T[k]["frozen"]["sus_scoring_interval_mhz"]) if cells[k].get("sus_mhz") is not None else None]
                     for k in T if k in cells],
            "beside_frozen_D_propagated_burst_inside": sum(1 for k in hb if inside(cells[k]["burst_mhz"], T[k]["frozen"]["burst_D_propagated_range_mhz"])),
            "beside_frozen_D_propagated_sus_inside": sum(1 for k in hs if inside(cells[k]["sus_mhz"], T[k]["frozen"]["sus_D_propagated_range_mhz"])),
            "beside_a1_reset_free_burst_inside": sum(1 for k in hb if inside(cells[k].get("burst_mhz_without"), T[k]["frozen"]["burst_scoring_interval_mhz"]))}


def score_gate(cells, tiles, field, pass_mhz, fail_mhz):
    rows = []
    for k in tiles:
        ref = cells.get(k.split("/")[0] + "/randn", {}).get(field)
        x = cells.get(k, {}).get(field)
        rows.append([k, x, ref, rnd(x - ref) if (x is not None and ref is not None) else None])
    known = [r for r in rows if r[3] is not None]
    if any(r[3] < fail_mhz for r in known):
        v = "FAIL"
    elif len(known) < len(tiles):
        v = "UNDER-RESOLVED"
    elif all(r[3] >= pass_mhz for r in known):
        v = "PASS"
    else:
        v = "INCONCLUSIVE"
    return {"rows": rows, "pass_mhz": pass_mhz, "fail_mhz": fail_mhz, "population": len(known), "verdict": v,
            "min_difference_mhz": min((r[3] for r in known), default=None)}


def score_s3(cells, pred, field="burst_mhz"):
    bar = pred["bars"]["S3_mhz"]
    rows, ok, full = [], True, True
    for t, tiles in pred["claims_e96"]["S3_no_zero_runs_at_random_speed"]["tiles"].items():
        ref = cells.get(f"{t}/randn", {}).get(field)
        xs = [cells.get(k, {}).get(field) for k in tiles]
        if ref is None or any(x is None for x in xs):
            full = False
            rows.append([t, None, ref, None, xs])
            continue
        d = mean(xs) - ref
        ok = ok and abs(d) <= bar
        rows.append([t, rnd(mean(xs)), ref, rnd(d), [rnd(x - ref) for x in xs]])
    return {"rows": rows, "bar": bar, "verdict": ("PASS" if ok else "FAIL") if full else ("FAIL" if not ok else "UNDER-RESOLVED")}


def score_s4(cells, pred):
    B, M = pred["bars"], pred["minimum_population"]
    T = pred["tiles"]
    hs = [k for k in pred["sus_core"] if cells.get(k, {}).get("sus_mhz") is not None]
    ok = [k for k in hs if all(x == T[k]["frozen"]["sus_limit"] for x in cells[k]["sus_limit_runs"])]
    return {"population": len(hs), "right": len(ok), "verdict": share_verdict(len(ok), len(hs), M["S4"], B["S4_pass_share"], B["S4_fail_share"]),
            "rows": [[k, T[k]["frozen"]["sus_limit"], T[k]["frozen"]["sus_share800"], cells[k]["sus_limit_runs"],
                      [(x or {}).get("800") for x in cells[k].get("sus_last", [])]] for k in hs]}


def score_s5(cells, pred):
    B, M = pred["bars"], pred["minimum_population"]
    T = pred["tiles"]
    hb = [k for k in T if cells.get(k, {}).get("rel_on_measured_c_burst_mhz") is not None and cells[k].get("burst_mhz") is not None]
    hs = [k for k in pred["sus_core"] if cells.get(k, {}).get("rel_on_measured_c_sus_mhz") is not None and cells[k].get("sus_mhz") is not None]
    rb = rms([cells[k]["burst_mhz"] - cells[k]["rel_on_measured_c_burst_mhz"] for k in hb])
    rs = rms([cells[k]["sus_mhz"] - cells[k]["rel_on_measured_c_sus_mhz"] for k in hs])
    bok, sok = len(hb) >= M["S5_burst"], len(hs) >= M["S5_sus"]
    if (bok and rb > B["S5_fail_rms_mhz"]) or (sok and rs > B["S5_fail_rms_mhz"]):
        v = "FAIL"
    elif not (bok and sok):
        v = "UNDER-RESOLVED"
    elif rb <= B["S5_pass_rms_mhz"] and rs <= B["S5_pass_rms_mhz"]:
        v = "PASS"
    else:
        v = "INCONCLUSIVE"
    return {"population_burst": len(hb), "population_sus": len(hs), "burst_rms_mhz": rb, "sus_rms_mhz": rs, "verdict": v,
            "beside_burst_a1_reset_free_rms_mhz": rms([cells[k]["burst_mhz_without"] - cells[k]["rel_on_measured_c_burst_mhz"] for k in hb
                                                       if cells[k].get("burst_mhz_without") is not None]),
            "rows": [[k, cells[k].get("c_w"), cells[k].get("burst_mhz"), cells[k].get("rel_on_measured_c_burst_mhz"), cells[k].get("sus_mhz"),
                      cells[k].get("rel_on_measured_c_sus_mhz")] for k in T if k in cells]}


def score_tie(cells, pred):
    rows = []
    for k, A in pred["anchors"].items():
        c = cells.get(k, {})
        if c.get("burst_mhz") is not None:
            rows.append([f"burst {k}", c["burst_mhz"], A["tie_burst_mhz"], rnd(c["burst_mhz"] - A["tie_burst_mhz"]), A["e87_burst_mhz"], A["e83"].get("burst_mhz"),
                         (A["e80"] or {}).get("e80_burst_mhz")])
        if c.get("sus_mhz") is not None:
            rows.append([f"sustained {k}", c["sus_mhz"], A["tie_sus_mhz"], rnd(c["sus_mhz"] - A["tie_sus_mhz"]), A["e87_sus_mhz"], A["e83"].get("sus_mhz"),
                         (A["e80"] or {}).get("e80_sus_mhz")])
    bar = pred["bars"]["T_mhz"]
    bad = [x for x in rows if abs(x[3]) > bar]
    v = "FAIL" if bad else ("PASS" if len(rows) >= pred["minimum_population"]["T_rows"] else "UNDER-RESOLVED")
    return {"rows": rows, "bar": bar, "verdict": v, "over_bar": [x[0] for x in bad]}


def partition(lo, hi, bar):
    """E96-I1's partition of an interval against 0 and +-bar (predict_e96.partition, the same text)."""
    if lo > bar or hi < -bar:
        return "DIFFERENT_BEYOND_BAR"
    holds0 = lo <= 0 <= hi
    in_bar = -bar <= lo and hi <= bar
    if holds0:
        return "SAME_WITHIN_BAR" if in_bar else "INCONCLUSIVE"
    return "DIFFERENT_SMALL" if in_bar else "DIFFERENT"


def side(lo, hi):
    return "BELOW" if hi < 0 else ("ABOVE" if lo > 0 else "INCONCLUSIVE")


def paired(ds, table):
    n = len(ds)
    m = st.mean(ds)
    sd = st.stdev(ds) if n > 1 else None
    h = tval(n, table) * sd / math.sqrt(n) if n > 1 else None
    return {"n": n, "mean": round(m, 3), "sd": rnd(sd, 3), "halfwidth": rnd(h, 3), "lo": rnd(m - h, 3) if h is not None else None,
            "hi": rnd(m + h, 3) if h is not None else None, "rounds": [round(x, 3) for x in ds]}


def two_way(table_rt, t_table):
    """The labelled pooled arm: clock(tile, round) = mu + tile + round + e, e iid; the contrast mean(real) - full with the pooled residual
    sd on (kinds - 1)(rounds - 1) df. rows are rounds, the first column is full."""
    r, k = len(table_rt), len(table_rt[0])
    gm = st.mean([x for row in table_rt for x in row])
    rm = [st.mean(row) for row in table_rt]
    km = [st.mean([row[j] for row in table_rt]) for j in range(k)]
    sse = sum((table_rt[i][j] - rm[i] - km[j] + gm) ** 2 for i in range(r) for j in range(k))
    df = (r - 1) * (k - 1)
    s = math.sqrt(sse / df) if df else 0.0
    d = st.mean(km[1:]) - km[0]
    se = s * math.sqrt((1.0 / (k - 1) + 1.0) / r)
    h = tval(df + 1, t_table) * se
    return {"df": df, "residual_sd": round(s, 3), "mean": round(d, 3), "halfwidth": round(h, 3), "lo": round(d - h, 3), "hi": round(d + h, 3)}


def score_arm(rounds, pred):
    """rounds: {round: {kind: {"mhz", "w", "die", "limit", "mhz_without", "fine_w", "share800"}}}, whole rounds only. E96-I1, I2, I3 and the labelled views."""
    A = pred["arm"]
    table = pred["t975"]
    kinds = list(A["tiles"])
    ref = A["ref"]
    whole = sorted(r for r, d in rounds.items() if ref in d and all(k in d for k in kinds) and all(d[k].get("mhz") is not None for k in kinds + [ref]))
    out = {"whole_rounds": whole, "n": len(whole), "min_rounds": A["min_rounds"], "bar_mhz": A["bar_mhz"],
           "rows": [[r, rounds[r][ref]["mhz"]] + [rounds[r][k]["mhz"] for k in kinds] for r in whole], "columns": ["round", ref] + kinds}
    if len(whole) < A["min_rounds"]:
        for x in ("E96-I1", "E96-I2", "E96-I3"):
            out[x] = {"verdict": "NOT SCORED"}
        return out

    def diffs(field, ks=None):
        ks = ks or kinds
        vals = []
        for r in whole:
            xs = [rounds[r][k].get(field) for k in ks]
            f = rounds[r][ref].get(field)
            if f is None or any(x is None for x in xs):
                return None
            vals.append(st.mean(xs) - f)
        return vals

    i1 = paired(diffs("mhz"), table)
    i1["verdict"] = partition(i1["lo"], i1["hi"], A["bar_mhz"])
    full_none = all(rounds[r][ref].get("limit") == "none" for r in whole)
    all_none = full_none and all(rounds[r][k].get("limit") == "none" for r in whole for k in kinds)
    i1["at_the_cap"] = all_none
    i1["at_the_cap_means"] = "every run of every kind read limit none, so nothing tripped: the clock comparison did not test the trip's edge" if all_none else None
    out["E96-I1"] = i1
    i2 = paired(diffs("w"), table)
    i2["verdict"] = side(i2["lo"], i2["hi"])
    out["E96-I2"] = i2
    i3 = paired(diffs("die"), table)
    i3["verdict"] = side(i3["lo"], i3["hi"])
    out["E96-I3"] = i3
    # labelled, never a verdict
    lab = {"per_tile_clock": {k: paired(diffs("mhz", [k]), table) for k in kinds}}
    for k in kinds:
        v = lab["per_tile_clock"][k]
        v["reads"] = partition(v["lo"], v["hi"], A["bar_mhz"])
    d = diffs("mhz_without")
    if d is not None:
        lab["clock_dips_left_out"] = dict(paired(d, table))
        lab["clock_dips_left_out"]["reads"] = partition(lab["clock_dips_left_out"]["lo"], lab["clock_dips_left_out"]["hi"], A["bar_mhz"])
    d = diffs("fine_w")
    if d is not None:
        lab["fine_w_at_800"] = dict(paired(d, table))
        lab["fine_w_at_800"]["reads"] = side(lab["fine_w_at_800"]["lo"], lab["fine_w_at_800"]["hi"])
    d = diffs("share800")
    if d is not None:
        lab["share_at_800"] = paired(d, table)
    tb = [[rounds[r][ref]["mhz"]] + [rounds[r][k]["mhz"] for k in kinds] for r in whole]
    lab["clock_pooled_two_way"] = two_way(tb, table)
    lab["clock_pooled_two_way"]["reads"] = partition(lab["clock_pooled_two_way"]["lo"], lab["clock_pooled_two_way"]["hi"], A["bar_mhz"])
    lab["limits"] = {k: [rounds[r][k].get("limit") for r in whole] for k in [ref] + kinds}
    lab["run_sd_mhz"] = {k: rnd(st.stdev([rounds[r][k]["mhz"] for r in whole]), 2) for k in [ref] + kinds}
    pooled = [st.stdev([rounds[r][k]["mhz"] for r in whole]) ** 2 for k in [ref] + kinds]
    lab["run_sd_pooled_mhz"] = rnd(math.sqrt(st.mean(pooled)), 2)
    out["labelled"] = lab
    return out


# ---------------------------------------------------------------------------------------- per-run helpers
def fine_view(m, procs, last_s=40.0):
    """E98's fine reading on one sustained run: over the in-kernel samples of the last 40 s, the mean board W of the 800 MHz samples with each dip and the
    3 s after it left out (None with under 70% of the window left), the share at 800, and the mean die over the same samples."""
    work = [p for p in procs if p.get("role") == "work"]
    if not work or not m.get("trace"):
        return None
    t0 = min(p["t_start_ms"] for p in work)
    kw = [((k["t_start_ms"] - t0) / 1000.0, (k["t_end_ms"] - t0) / 1000.0) for p in work for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
    tr = m["trace"]
    lab, _ = PI.flags(m)
    t_end = m["work_s"]
    dips = []
    i = 0
    while i < len(tr):
        if lab[i] == "dip":
            j = i
            while j + 1 < len(tr) and lab[j + 1] == "dip":
                j += 1
            dips.append((tr[i][0], tr[j][0]))
            i = j + 1
        else:
            i += 1

    def dipped(t):
        return any(a <= t <= b + RAMP_AFTER_DIP_S for a, b in dips)
    last = [x for x in tr if x[0] >= t_end - last_s and any(a <= x[0] <= b for a, b in kw)]
    if not last:
        return None
    fine = [x[2] for x in last if x[3] == 800 and x[2] is not None and not dipped(x[0])]
    fdie = [x[1] for x in last if x[3] == 800 and x[1] is not None and not dipped(x[0])]
    return {"fine_w": rnd(st.mean(fine), 3) if len(fine) >= FINE_MIN_SHARE * len(last) else None, "fine_die": rnd(st.mean(fdie), 3) if fdie else None,
            "fine_share": rnd(len(fine) / len(last), 3), "share800": rnd(sum(1 for x in last if x[3] == 800) / len(last), 3), "n": len(last), "dips": len(dips)}


def round_of(label):
    i = label.rfind("-round")
    return int(label[i + 6:]) if i >= 0 and label[i + 6:].isdigit() else None


def read_jsonl(path):
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for ln in f:
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def history_rest(rows, t_end, window_min=20, skip_min=10):
    """E98's rest reading (reduce_e98.rest_reading's rule, on aifoundry2's history rows): the window_min of history before t_end, leaving out any row within skip_min
    after a busy one (a die over 55 C, a board over 26 W, the card held on two rows running) and any row with the card held. The board W is the reading; the raw
    die sits beside it (E98 derives its rest die's changes as W / 0.2315: slopes need only differences, so no absolute die is derived here)."""
    look = [r for r in rows if t_end - 40 * 60000 <= r.get("t", 0) < t_end]
    busy = []
    for i, r in enumerate(look):
        c = (r.get("cards") or [{}])[0]
        hot = (c.get("w") is not None and c["w"] > 26.0) or (c.get("die") is not None and c["die"] > 55)
        held = bool(c.get("held"))
        adj = any(0 <= j < len(look) and ((look[j].get("cards") or [{}])[0]).get("held") for j in (i - 1, i + 1))
        if hot or (held and adj):
            busy.append(r["t"])
    last_busy = max(busy) if busy else None
    skip_to = (last_busy + skip_min * 60000) if last_busy else 0
    use = [r for r in look if r["t"] >= t_end - window_min * 60000 and r["t"] >= skip_to and not ((r.get("cards") or [{}])[0]).get("held")]
    W = [(r.get("cards") or [{}])[0].get("w") for r in use]
    W = [x for x in W if x is not None]
    die = [(r.get("cards") or [{}])[0].get("die") for r in use]
    die = [x for x in die if x is not None]
    return {"rows": len(W), "w": rnd(mean(W), 3), "die_raw": rnd(mean(die), 2),
            "nic": rnd(mean([(r.get("temps") or {}).get("nic") for r in use]), 2), "nvme": rnd(mean([(r.get("temps") or {}).get("nvme") for r in use]), 2),
            "since_busy_min": round((t_end - last_busy) / 60000.0, 1) if last_busy else None, "t_end_ms": t_end}


def smoke_rest(smoke):
    """The last 60 s of the smoke's no-launch run: the 10 Hz sampler on the idle card, just before the session's first launch."""
    if not smoke:
        return None
    rr = R.jl(os.path.join(smoke, "runs.jsonl"))
    rest = next((r for r in rr if r.get("label") == "rest"), None)
    if not rest:
        return None
    s = R.tel(os.path.join(smoke, rest["tel"]))
    if not s:
        return None
    t1 = s[-1][0]
    last = [x for x in s if x[0] >= t1 - 60000]
    return {"n": len(last), "t_first_ms": last[0][0], "t_last_ms": t1, "die": rnd(mean([x[1] for x in last]), 2), "w": rnd(mean([x[3] for x in last]), 3),
            "mhz": rnd(mean([x[4] for x in last]), 1), "config": (rest.get("queries") or {}).get("config"),
            "w_first_half": rnd(mean([x[3] for x in last[:len(last) // 2]]), 3), "w_second_half": rnd(mean([x[3] for x in last[len(last) // 2:]]), 3)}


def ols(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a0 = my - k * mx
    res = [y - (a0 + k * x) for x, y in zip(xs, ys)]
    return {"k": k, "a": a0, "rms": math.sqrt(sum(q * q for q in res) / len(res)), "res": res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--smoke")
    ap.add_argument("--history")
    ap.add_argument("--rest-at", nargs="*", default=[], help="NAME=EPOCH_MS: read E98's rest rule at this moment too, from --history")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    B = {int(k): v for k, v in pred["constants"]["B_registered_w"].items()}
    rel = PE.Rel(B)
    Wb, sb = pred["relation"]["burst"]["W_star_w"], pred["relation"]["burst"]["sigma_w"]
    Ws, ss = pred["relation"]["sustained"]["W_star_w"], pred["relation"]["sustained"]["sigma_w"]
    runs, byrun_all = [], {}
    for rd in a.rundirs:
        sess, rr, launches, q0 = R.load_session(rd)
        evs = R.sp_events_by_run(rd, sess, rr, q0)
        byrun = {}
        for L in launches:
            byrun.setdefault(L["run"], []).append(L)
        byrun_all.update(byrun)
        fit = R.fit_clock(evs, launches, sess)
        for r in rr:
            procs = byrun.get(r["run"], [])
            m = R.run_metrics(rd, r, procs, evs.get(r["run"]), fit)
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["kind"] = RK.kind_of(r["values"])
            m["config_after"] = (r.get("queries") or {}).get("config")
            m["t_first_ms"], m["t_last_ms"] = r.get("t_first_ms"), r.get("t_last_ms")
            m["procs_rc"] = [x.get("rc") for x in r.get("launches", [])]
            m.update(RK.burst_extra(m, procs, B))
            if m["block"] == "SUS":
                m["limit"] = RK.sus_limit(m)
            if m["block"] in ("BURST", "SUS"):
                m["a1"] = RE.a1_view(m, [(p["t_start_ms"], p["t_end_ms"]) for p in procs if p.get("role") == "work"])
            if m["block"] == "SUS":
                m["fine"] = fine_view(m, procs)
                m["round"] = round_of(m["label"])
                m["line_k"] = rnd(m["sus_die_mean"] - pred["line"]["k_c_per_w"] * m["sus_w_mean"], 3) if m.get("sus_w_mean") is not None and m.get("sus_die_mean") is not None else None
            runs.append(m)

    cells = {}
    catalog = list(pred["tiles"].items()) + list(pred["arm"]["tiles"].items()) + list(pred["anchors"].items())
    for k, P in catalog:
        bu = [m for m in runs if m["kind"] == k and m["block"] == "BURST"]
        su = [m for m in runs if m["kind"] == k and m["block"] == "SUS"]
        c = {"kind": k, "type": P["type"], "role": P["role"], "n_burst": len(bu), "n_sus": len(su)}
        if bu:
            bm = [m["burst_mhz"] for m in bu]
            bw = [m["a1"]["burst_mhz_without"] for m in bu]
            cw = [m["c_w"] for m in bu]
            c.update({"burst_mhz": rnd(mean(bm)), "burst_mhz_runs": bm,
                      "burst_mhz_without": rnd(mean([x for x in bw if x is not None])), "burst_mhz_without_runs": bw,
                      "burst_rate": rnd(mean([m["burst_rate"] for m in bu]), 3), "burst_rate_runs": [m["burst_rate"] for m in bu],
                      "burst_p800_w": rnd(mean([m["p800_w"] for m in bu]), 2), "burst_p800_w_runs": [m["p800_w"] for m in bu],
                      "burst_w": rnd(mean([m["burst_w"] for m in bu]), 2),
                      "burst_die_start": [m["die_start"] for m in bu], "burst_die_max": [m["die_max"] for m in bu],
                      "burst_first_down": [m.get("first_down_kind") for m in bu],
                      "c_w": rnd(mean([x for x in cw if x is not None]), 3), "c_w_runs": cw,
                      "gov_own_mhz_runs": [m["gov_own_mhz"] for m in bu],
                      "idle_resets_burst": sum(m["a1"]["n_dip"] for m in bu), "late_ramps_burst": sum(m["a1"]["n_late"] for m in bu)})
            c["burst_limit"] = ("power" if any(x == "power_down" for x in c["burst_first_down"]) else
                                ("thermal" if any(x == "thermal_down" for x in c["burst_first_down"]) else "none"))
        if su:
            c.update({"sus_mhz": rnd(mean([m["sus_mhz_mean"] for m in su])), "sus_mhz_runs": [m["sus_mhz_mean"] for m in su],
                      "sus_mhz_without_runs": [m["a1"]["sus_mhz_without"] for m in su],
                      "sus_rate": rnd(mean([m["sus_rate_t"] for m in su]), 3), "sus_rate_runs": [m["sus_rate_t"] for m in su],
                      "sus_rate_wall": rnd(mean([m["sus_rate_wall_t"] for m in su]), 3),
                      "sus_w": rnd(mean([m["sus_w_mean"] for m in su]), 2), "sus_w_runs": [m["sus_w_mean"] for m in su],
                      "sus_die": rnd(mean([m["sus_die_mean"] for m in su]), 2), "sus_die_runs": [m["sus_die_mean"] for m in su],
                      "sus_die_start": [m["die_start"] for m in su], "sus_last": [m.get("sus_last") for m in su],
                      "sus_limit_runs": [m["limit"] for m in su], "idle_resets_sus": sum(m["a1"]["n_dip"] for m in su)})
            c["sus_limit"] = c["sus_limit_runs"][0] if len(set(c["sus_limit_runs"])) == 1 else "/".join(str(x) for x in c["sus_limit_runs"])
        if P["role"] == "real2":
            c["frozen"] = P["frozen"]
            c["group"], c["gated_lane_frac"] = P["group"], P["gated_lane_frac"]
        if c.get("c_w") is not None:
            c["rel_on_measured_c_burst_mhz"] = rnd(rel.f(c["c_w"], Wb, sb)[0])
            c["rel_on_measured_c_sus_mhz"] = rnd(rel.f(c["c_w"], Ws, ss)[0])
        cells[k] = c

    Cl, Ba = pred["claims_e96"], pred["bars"]
    rules = {"E96-S1": score_s1(cells, pred),
             "E96-S2": score_gate(cells, Cl["S2_gate_buys_speed"]["tiles"], "burst_mhz", Ba["S2_pass_mhz"], Ba["S2_fail_mhz"]),
             "E96-S2b": score_gate(cells, Cl["S2b_gate_buys_sustained_clock"]["tiles"], "sus_mhz", Ba["S2b_pass_mhz"], Ba["S2b_fail_mhz"]),
             "E96-S3": score_s3(cells, pred), "E96-S4": score_s4(cells, pred), "E96-S5": score_s5(cells, pred), "E96-T": score_tie(cells, pred)}

    # -- the arm, by whole rounds; a run counts only with all its processes back rc 0
    rounds = {}
    for m in runs:
        if m["block"] != "SUS" or m.get("round") is None:
            continue
        if len(m["procs_rc"]) != ARM_PROCS and not m["dry"]:
            continue
        if any(x != 0 for x in m["procs_rc"]):
            continue
        f = m.get("fine") or {}
        rounds.setdefault(m["round"], {})[m["kind"]] = {"mhz": m["sus_mhz_mean"], "w": m["sus_w_mean"], "die": m["sus_die_mean"], "limit": m["limit"],
                                                        "mhz_without": m["a1"]["sus_mhz_without"], "fine_w": f.get("fine_w"), "share800": f.get("share800"),
                                                        "run": m["run"], "die_start": m["die_start"]}
    arm = score_arm(rounds, pred)
    for x in ("E96-I1", "E96-I2", "E96-I3"):
        rules[x] = arm[x]

    # ---- labelled, never a verdict
    post = {"note": "LABELLED views and arms, frozen in README.md before the data; none changes a verdict"}
    post["arm_labelled"] = arm.get("labelled")
    post["arm_rows"] = {"columns": arm["columns"], "rows": arm["rows"], "whole_rounds": arm["whole_rounds"]}
    post["arm_rounds_detail"] = rounds
    T = pred["tiles"]
    have_b = [k for k in T if cells[k].get("burst_mhz") is not None]
    have_s = [k for k in pred["sus_core"] if cells[k].get("sus_mhz") is not None]
    # the frozen points, rms, and a baseline with no model: every tile = same-session random data of its format (E87's correction C1)
    refk = {"fp32": "fp32/randn", "fp16": "fp16/randn", "int8": "int8/full"}

    def base(k, f):
        return cells[refk[k.split("/")[0]]].get(f)
    groups = {"all": list(T), "gated float (S2)": Cl["S2_gate_buys_speed"]["tiles"] + ["fp32/resnet18_l2c1"],
              "no zero word, float": [k for k in T if T[k]["gated_lane_frac"] == 0 and T[k]["type"] != "int8"],
              "int8": [k for k in T if T[k]["type"] == "int8"]}
    post["rms_by_group"] = {}
    for name, ks in groups.items():
        kb = [k for k in ks if k in have_b]
        ks_ = [k for k in ks if k in have_s]
        post["rms_by_group"][name] = {
            "burst_vs_frozen": rms([cells[k]["burst_mhz"] - T[k]["frozen"]["burst_mhz"] for k in kb]),
            "burst_vs_relation_on_measured_c": rms([cells[k]["burst_mhz"] - cells[k]["rel_on_measured_c_burst_mhz"] for k in kb if cells[k].get("rel_on_measured_c_burst_mhz") is not None]),
            "burst_vs_no_model": rms([cells[k]["burst_mhz"] - base(k, "burst_mhz") for k in kb if base(k, "burst_mhz") is not None]),
            "sus_vs_frozen": rms([cells[k]["sus_mhz"] - T[k]["frozen"]["sus_mhz"] for k in ks_]),
            "sus_vs_relation_on_measured_c": rms([cells[k]["sus_mhz"] - cells[k]["rel_on_measured_c_sus_mhz"] for k in ks_ if cells[k].get("rel_on_measured_c_sus_mhz") is not None]),
            "sus_vs_no_model": rms([cells[k]["sus_mhz"] - base(k, "sus_mhz") for k in ks_ if base(k, "sus_mhz") is not None]),
            "n_burst": len(kb), "n_sus": len(ks_)}
    # the gate law's clock, and the measured c against the two predictions
    post["gate_law_rows"] = [[k, T[k]["gated_lane_frac"], cells[k].get("c_w"), T[k]["frozen"]["c_w"], T[k]["gate_law"]["c_w"], cells[k].get("burst_mhz"), T[k]["gate_law"]["burst_mhz"],
                              cells[k].get("sus_mhz"), T[k]["gate_law"]["sus_mhz"]] for k in T if T[k].get("gate_law") and k in have_b]
    # like with like: switching above zeros as a share of the same-session reference (E87's S3 and S4 quantity)
    ratio = {}
    for k in list(T) + list(pred["arm"]["tiles"]):
        t = k.split("/")[0]
        ref, z = cells[refk[t]], cells[f"{t}/zeros"]
        c = cells[k]
        if None in (c.get("c_w"), ref.get("c_w"), z.get("c_w")) or ref["c_w"] - z["c_w"] <= 0:
            continue
        ratio[k] = rnd((c["c_w"] - z["c_w"]) / (ref["c_w"] - z["c_w"]), 4)
    post["like_with_like_ratios"] = ratio
    post["like_with_like_rows"] = [[k, ratio.get(k), T[k]["ratio_to_ref_measured_e78"], rnd((T[k]["gate_law"]["D_w"]) / pred_ref_d(pred, T[k]), 4) if T[k].get("gate_law") else None] for k in T]
    # real against random, per tile, burst and sustained
    post["diff_from_random_rows"] = [[k, T[k]["group"], rnd(cells[k]["burst_mhz"] - base(k, "burst_mhz")) if k in have_b and base(k, "burst_mhz") is not None else None,
                                      rnd(cells[k]["sus_mhz"] - base(k, "sus_mhz")) if k in have_s and base(k, "sus_mhz") is not None else None] for k in T]
    # the reset-free view of S2 and S3
    post["s2_reset_free"] = score_gate(cells, Cl["S2_gate_buys_speed"]["tiles"], "burst_mhz_without", Ba["S2_pass_mhz"], Ba["S2_fail_mhz"])
    post["s3_reset_free"] = score_s3(cells, pred, "burst_mhz_without")
    post["s3_on_sustained_where_run"] = [[k, cells[k].get("sus_mhz"), base(k, "sus_mhz"), rnd(cells[k]["sus_mhz"] - base(k, "sus_mhz")) if base(k, "sus_mhz") is not None else None]
                                         for k in have_s if T[k]["gated_lane_frac"] == 0]
    # the die line of the session, E87's form, and the line at E98's k
    dl = pred["constants"]["e80_die_line"]
    sr = [m for m in runs if m["block"] == "SUS" and m.get("sus_w_mean") and m.get("sus_die_mean") is not None]
    if len(sr) >= 3:
        xs, ys = [m["sus_w_mean"] for m in sr], [m["sus_die_mean"] for m in sr]
        L = ols(xs, ys)
        if L:
            post["die_line_e96"] = {"k_c_per_w": round(L["k"], 4), "a_c": round(L["a"], 3), "n": len(sr), "rms_c": round(L["rms"], 3),
                                    "cap_w_at_65_5": round((65.5 - L["a"]) / L["k"], 2) if L["k"] > 0 else None,
                                    "a_c_at_e80_slope": round(st.mean(ys) - dl["k_c_per_w"] * st.mean(xs), 3),
                                    "shift_c_at_e80_slope": round(st.mean(ys) - dl["k_c_per_w"] * st.mean(xs) - dl["a_c"], 3), "e80_line": dl,
                                    "e87_line": pred["line"]["e87_die_line"]}
        kl = pred["line"]["k_c_per_w"]
        by = {}
        for m in sr:
            by.setdefault(m["kind"], []).append(m["line_k"])
        common = [st.mean(by[k]) for k in pred["line"]["kinds"] if k in by]
        t0 = min(m["t_first_ms"] for m in sr)
        tr = ols([(m["t_first_ms"] - t0) / 60000.0 for m in sr], [m["line_k"] for m in sr])
        post["line_at_e98_k"] = {"k_c_per_w": kl, "kinds_shared_with_e98": pred["line"]["kinds"], "mean_over_shared_kinds_c": rnd(st.mean(common), 3) if common else None,
                                 "e87_same_kinds_c": pred["line"]["e87_mean_c"], "difference_from_e87_c": rnd(st.mean(common) - pred["line"]["e87_mean_c"], 3) if common else None,
                                 "mean_over_all_runs_c": rnd(st.mean([m["line_k"] for m in sr]), 3),
                                 "trend_c_per_min": rnd(tr["k"], 5) if tr else None, "t0_ms": t0,
                                 "runs": [[m["run"], m["kind"], m["t_first_ms"], m["sus_w_mean"], m["sus_die_mean"], m["line_k"], m["limit"]] for m in sr]}
    anc = [m for m in sr if m["kind"] in pred["anchors"]]
    if anc:
        resid = [m["sus_die_mean"] - (dl["a_c"] + dl["k_c_per_w"] * m["sus_w_mean"]) for m in anc]
        d = st.mean(resid)
        w_adj = Ws - d / dl["k_c_per_w"]
        post["a_adj_e96"] = {"anchor_runs": [m["run"] for m in anc], "die_residual_c": [round(x, 3) for x in resid], "mean_residual_c": round(d, 3),
                             "W_star_sus_w": Ws, "W_star_adj_w": round(w_adj, 3)}
        for k in T:
            cells[k]["arm_a_adj_e96_sus_mhz"] = rnd(rel.f(T[k]["frozen"]["c_w"], w_adj, ss)[0])
            if cells[k].get("c_w") is not None:
                cells[k]["rel_on_measured_c_a_adj_e96_sus_mhz"] = rnd(rel.f(cells[k]["c_w"], w_adj, ss)[0])
        post["a_adj_e96"]["sus_rms_frozen_c_mhz"] = rms([cells[k]["sus_mhz"] - cells[k]["arm_a_adj_e96_sus_mhz"] for k in have_s])
        post["a_adj_e96"]["sus_rms_measured_c_mhz"] = rms([cells[k]["sus_mhz"] - cells[k]["rel_on_measured_c_a_adj_e96_sus_mhz"] for k in have_s
                                                           if cells[k].get("rel_on_measured_c_a_adj_e96_sus_mhz") is not None])
    # the rest readings
    rest = {"smoke_last_60s": smoke_rest(a.smoke)}
    if a.history:
        rows = read_jsonl(a.history)
        rows.sort(key=lambda r: r.get("t", 0))
        first = min((m["t_first_ms"] for m in runs), default=None)
        rest["history_before_first_session_launch"] = history_rest(rows, first) if first else None
        for x in a.rest_at:
            name, t = x.split("=")
            rest[name] = history_rest(rows, int(t))
    post["rest"] = rest
    post["burst_limit_rows"] = [[k, T[k]["frozen"]["burst_limit"], cells[k].get("burst_limit"), cells[k].get("burst_first_down")] for k in have_b]
    post["burst_limit_right"] = sum(1 for x in post["burst_limit_rows"] if x[1] == x[2])
    post["thermal_first_bursts"] = sum(1 for m in runs if m["block"] == "BURST" and m.get("first_down_kind") == "thermal_down")
    post["idle_resets"] = {"burst_runs": sum(1 for m in runs if m["block"] == "BURST" and m.get("a1", {}).get("n_dip")),
                           "sus_dips": sum(m.get("a1", {}).get("n_dip", 0) for m in runs if m["block"] == "SUS"),
                           "work_processes": sum(len(m.get("proc_spans") or []) for m in runs if m["block"] in ("BURST", "SUS"))}
    post["sus_replicates"] = [[c["kind"], c["sus_mhz_runs"], rnd(max(c["sus_mhz_runs"]) - min(c["sus_mhz_runs"]))] for c in cells.values() if c.get("n_sus", 0) >= 2]
    post["gates"] = {"burst_held_s": rnd(sum((m["gate"].get("held_s") or 0) for m in runs if m["block"] == "BURST"), 1),
                     "sus_held_s": rnd(sum((m["gate"].get("held_s") or 0) for m in runs if m["block"] == "SUS"), 1),
                     "not_reached": [m["run"] for m in runs if m.get("gate", {}).get("reached") is False]}
    post["runs_planned"] = sum(len(json.load(open(os.path.join(rd, "session.json")))["runs_planned"]) for rd in a.rundirs)
    post["runs_done"] = len(runs)
    cfg = [m["config_after"] for m in runs if m.get("config_after")]
    res = {"experiment": "E96", "bars": Ba, "rules": rules, "posthoc": post, "cells": cells,
           "config_reads": {"n": len(cfg), "tdp_w": sorted({x.get("tdp_w") for x in cfg if x}, key=str),
                            "temp_threshold_c": sorted({x.get("temp_threshold_c") for x in cfg if x}, key=str)},
           "runs": runs}
    for m in runs:
        print(f"{m['run']:38s} {m['kind'] or '-':30s} die {m.get('die_start')}->{m.get('die_max')} burst {m.get('burst_mhz')!s:>6} p800 {m.get('p800_w')!s:>6} "
              f"c {m.get('c_w')!s:>7} first={m.get('first_down_kind')} dips={m.get('a1', {}).get('n_dip')} "
              + (f"SUS {m.get('sus_mhz_mean')} MHz {m.get('sus_w_mean')} W {m.get('sus_die_mean')} C {m.get('limit')} line {m.get('line_k')} {m.get('sus_last')}" if m["block"] == "SUS" else ""))
    print()
    print("%-32s %-6s %6s %6s %16s %8s | %6s %6s %16s %6s %6s %-10s %-8s | %7s %7s" % ("kind", "role", "burst", "pred", "scoring", "rate", "sus", "pred", "scoring", "W", "die", "limit", "pred lim", "c", "c pred"))
    for k, c in cells.items():
        fz = c.get("frozen") or {}
        print("%-32s %-6s %6s %6s %16s %8s | %6s %6s %16s %6s %6s %-10s %-8s | %7s %7s" % (
            k, c["role"], c.get("burst_mhz"), fz.get("burst_mhz", ""), fz.get("burst_scoring_interval_mhz", ""), c.get("burst_rate"), c.get("sus_mhz"), fz.get("sus_mhz", ""),
            fz.get("sus_scoring_interval_mhz", ""), c.get("sus_w"), c.get("sus_die"), c.get("sus_limit"), fz.get("sus_limit", ""), c.get("c_w"), fz.get("c_w", "")))
    print()
    for k, v in rules.items():
        print(k, v.get("verdict"), {x: y for x, y in v.items() if x not in ("rows", "verdict", "at_the_cap_means")})
    print("posthoc", json.dumps({k: v for k, v in post.items() if not k.endswith("_rows") and k not in ("arm_rounds_detail", "note") and k != "line_at_e98_k"}))
    print("line_at_e98_k", json.dumps({k: v for k, v in post.get("line_at_e98_k", {}).items() if k != "runs"}))
    print("config reads", json.dumps(res["config_reads"]))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    return 0


def pred_ref_d(pred, e):
    """E78's measured D of a tile's reference kind (D_w / ratio_to_ref_measured_e78 gives it back)."""
    return e["D_w"] / e["ratio_to_ref_measured_e78"]


if __name__ == "__main__":
    sys.exit(main())
