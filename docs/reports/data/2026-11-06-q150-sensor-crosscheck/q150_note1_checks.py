#!/usr/bin/env python3
"""Q150's fix lane, post hoc desk checks on committed lab data (the two dated notes beside Q150's READMEs read them).

Read-only. Standard library only. From the top of the repository:

    python3 -I docs/reports/data/2026-11-06-q150-sensor-crosscheck/q150_note1_checks.py . \
        > docs/reports/data/2026-11-06-q150-sensor-crosscheck/q150_note1_checks.json

A  E178's footing: his pair (int8 5s - 4s) per couple on the registered footing (runs.csv) and on the leak-0 footing
   (runs-leak0.csv), the couples' order term, and every adjacent same-format couple whose two kinds read within
   0.15 W of each other on the leak-0 footing (the leak term's mean in two orientations, the pooled couple scatter).
B  die_mv - reg_mv by load on November's kept passes: E171 and E178 on aifoundry3, E172 on aifoundry1's card 1.
   Idle: board_w under the file's 5th percentile + 2 W; busy: over it + 8 W.
C  the minion rail's and the board's mean change interval by date (samples with no statistics reset, consecutive
   samples at most 300 ms apart), and how often the board value changes on the same sample as the minion rail.
D  card 1's SRAM reading fraction f = (m + M) / (2 M) from the committed reset-window medians of the sibling
   directory 2026-11-06-q150-meter-checks (under a statistic updated with P0 and then with P0 + P1, the settled
   average is (P0 + S) / 2, its minimum P0 and its maximum S, so f = settled average / S).
E  E65's 600 MHz hart ladder on aifoundry3: the minion rail's level and the board's switched watts against harts,
   a straight line with an intercept.
F  arithmetic: E178's per-pass sd as its couples predict it, half-widths at 4, 8 and 16 passes; the launch-level
   ABBA forecast's half-width in 30 card-minutes.

Every input's sha256 is recorded in the output (`inputs_sha256`).
"""
import csv, glob, gzip, hashlib, json, math, os, statistics as st, sys, collections

TOP = sys.argv[1] if len(sys.argv) > 1 else "."
DATA = os.path.join(TOP, "docs", "reports", "data")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 20: 2.086, 30: 2.042, 40: 2.021, 60: 2.000,
        120: 1.980}
INPUTS = {}


def rel(path):
    return os.path.relpath(path, TOP)


def note(path):
    if rel(path) not in INPUTS:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for blk in iter(lambda: fh.read(1 << 20), b""):
                h.update(blk)
        INPUTS[rel(path)] = h.hexdigest()


def t975(df):
    for k in sorted(T975):
        if k >= df:
            return T975[k]
    return 1.96


def r4(x):
    return None if x is None else round(x, 4)


out = {}

# ---------------------------------------------------------------- A: E178's footing
E178 = os.path.join(DATA, "2026-11-06-e178-one-number-aifoundry3")


def load_runs(fn):
    path = os.path.join(E178, fn)
    note(path)
    rows = {}
    for r in csv.DictReader(open(path)):
        try:
            d = float(r["D"])
        except (ValueError, TypeError):
            continue
        rows[(int(r["pass"]), int(r["pos"]))] = {"item": r["item"], "seg": int(r["segment"]), "D": d}
    return rows


sc, l0 = load_runs("runs.csv"), load_runs("runs-leak0.csv")
A = {}
PASSES = sorted({p for p, _ in sc})
A5, A4 = "int8.e178_v5", "int8.e178_v4"
cp = []
for p in PASSES:
    for s in (0, 1, 2):
        k5 = [k for k, v in sc.items() if k[0] == p and v["seg"] == s and v["item"] == A5]
        k4 = [k for k, v in sc.items() if k[0] == p and v["seg"] == s and v["item"] == A4]
        if not k5 or not k4:
            continue
        first = min(min(k[1] for k in k5), min(k[1] for k in k4))
        prev = sc.get((p, first - 1))
        cp.append({"pass": p, "seg": s, "five_first": min(k[1] for k in k5) < min(k[1] for k in k4),
                   "prev_item": prev["item"] if prev else None,
                   "prev_minus_first_D": (prev["D"] - sc[(p, first)]["D"]) if prev else None,
                   "adjacent": abs(min(k[1] for k in k5) - min(k[1] for k in k4)) == 1,
                   "scored": st.mean(sc[k]["D"] for k in k5) - st.mean(sc[k]["D"] for k in k4),
                   "leak0": st.mean(l0[k]["D"] for k in k5) - st.mean(l0[k]["D"] for k in k4)})


def pair_stats(key):
    per_pass = collections.defaultdict(list)
    for c in cp:
        per_pass[c["pass"]].append(c[key])
    pm = [st.mean(v) for _, v in sorted(per_pass.items())]
    m, sd = st.mean(pm), st.stdev(pm)
    hw = t975(len(pm) - 1) * sd / math.sqrt(len(pm))
    a = [c[key] for c in cp if c["five_first"]]
    b = [c[key] for c in cp if not c["five_first"]]
    return {"pass_means": [r4(x) for x in pm], "mean": r4(m), "lo": r4(m - hw), "hi": r4(m + hw), "hw": r4(hw),
            "pass_sd": r4(sd), "couples": len(cp), "couple_sd": r4(st.stdev([c[key] for c in cp])),
            "five_first_n": len(a), "five_first_mean": r4(st.mean(a)), "four_first_n": len(b),
            "four_first_mean": r4(st.mean(b)),
            "order_term_first_minus_second_W": r4((st.mean(a) - st.mean(b)) / 2),
            "order_adjusted_pair_W": r4((st.mean(a) + st.mean(b)) / 2)}


pv = [c["prev_minus_first_D"] for c in cp if c["prev_minus_first_D"] is not None]
A["his_pair"] = {"scored": pair_stats("scored"), "leak0": pair_stats("leak0"),
                 "every_couple_adjacent": all(c["adjacent"] for c in cp),
                 "run_before_each_couple": {"items": sorted({c["prev_item"] for c in cp if c["prev_item"]}),
                                            "n": len(pv), "mean_D_above_the_first_run_W": r4(st.mean(pv))}}
lt = [c["scored"] - c["leak0"] for c in cp]
A["his_pair"]["leak_term_per_couple_W"] = {"n": len(lt), "mean": r4(st.mean(lt)), "sd": r4(st.stdev(lt))}
A["his_pair"]["couple_variance_ratio_scored_over_leak0"] = r4(
    (st.stdev([c["scored"] for c in cp]) / st.stdev([c["leak0"] for c in cp])) ** 2)

groups = collections.defaultdict(list)
for (p, pos), v in sc.items():
    nx = (p, pos + 1)
    if nx not in sc or (p, pos) not in l0 or nx not in l0:
        continue
    w = sc[nx]
    if v["item"] == w["item"] or v["item"].split(".")[0] != w["item"].split(".")[0]:
        continue
    a, b = sorted([v["item"], w["item"]])
    sgn = 1 if v["item"] == a else -1
    groups[(a, b)].append({
        "alpha_scored": sgn * (v["D"] - w["D"]), "alpha_leak0": sgn * (l0[(p, pos)]["D"] - l0[nx]["D"]),
        "order_scored": v["D"] - w["D"], "order_leak0": l0[(p, pos)]["D"] - l0[nx]["D"]})


def pooled(lo, hi, skip=()):
    res_s, res_0, lt_a, lt_o, raw_o, names = [], [], [], [], [], []
    for k, v in sorted(groups.items()):
        if len(v) < 2 or k in skip:
            continue
        m0 = st.mean(x["alpha_leak0"] for x in v)
        if not (lo <= abs(m0) < hi):
            continue
        names.append("%s - %s (%d)" % (k[0], k[1], len(v)))
        ms = st.mean(x["alpha_scored"] for x in v)
        res_s += [x["alpha_scored"] - ms for x in v]
        res_0 += [x["alpha_leak0"] - m0 for x in v]
        lt_a += [x["alpha_scored"] - x["alpha_leak0"] for x in v]
        lt_o += [x["order_scored"] - x["order_leak0"] for x in v]
        raw_o += [x["order_leak0"] for x in v]
    rms = lambda xs: math.sqrt(sum(x * x for x in xs) / len(xs))
    se = lambda xs: st.stdev(xs) / math.sqrt(len(xs))
    return {"pairs": len(names), "pair_names": names, "couples": len(res_s),
            "couple_rms_scored_W": r4(rms(res_s)), "couple_rms_leak0_W": r4(rms(res_0)),
            "scatter_added_by_leak_term_pct": round(100 * (rms(res_s) / rms(res_0) - 1), 1),
            "leak_term_in_name_order_W": {"mean": r4(st.mean(lt_a)), "sd": r4(st.stdev(lt_a)), "se": r4(se(lt_a))},
            "leak_term_first_minus_second_W": {"mean": r4(st.mean(lt_o)), "sd": r4(st.stdev(lt_o)), "se": r4(se(lt_o))},
            "leak0_first_minus_second_W": {"mean": r4(st.mean(raw_o)), "se": r4(se(raw_o))}}


A["adjacent_near_equal_lt_0.15W"] = pooled(0, 0.15)
A["adjacent_near_equal_lt_0.15W_without_his_pair"] = pooled(0, 0.15, skip=((A4, A5),))

# every same-format pair of items run in one (pass, segment), adjacent or not: a couple per (pass, segment)
seg = {"scored": collections.defaultdict(lambda: collections.defaultdict(list)),
       "leak0": collections.defaultdict(lambda: collections.defaultdict(list))}
for nm, rows in (("scored", sc), ("leak0", l0)):
    for (p, pos), v in rows.items():
        if v["seg"] >= 0:
            seg[nm][(p, v["seg"])][v["item"]].append(v["D"])


def seg_couples(nm):
    pairs = collections.defaultdict(dict)
    for key, items in seg[nm].items():
        its = sorted(items)
        for i in range(len(its)):
            for j in range(i + 1, len(its)):
                a, b = its[i], its[j]
                if a.split(".")[0] == b.split(".")[0]:
                    pairs[(a, b)][key] = st.mean(items[a]) - st.mean(items[b])
    return pairs


cs_, c0_ = seg_couples("scored"), seg_couples("leak0")
rs, r0, npairs, lower, higher = [], [], 0, 0, 0
for k in cs_:
    keys = sorted(set(cs_[k]) & set(c0_.get(k, {})))
    if len(keys) < 4:
        continue
    m0 = st.mean(c0_[k][x] for x in keys)
    if abs(m0) >= 0.15:
        continue
    ms = st.mean(cs_[k][x] for x in keys)
    rs += [cs_[k][x] - ms for x in keys]
    r0 += [c0_[k][x] - m0 for x in keys]
    npairs += 1
    s_sc, s_l0 = st.pstdev([cs_[k][x] for x in keys]), st.pstdev([c0_[k][x] for x in keys])
    lower += s_sc < s_l0 - 1e-12
    higher += s_sc > s_l0 + 1e-12
A["same_segment_near_equal_lt_0.15W_any_distance"] = {
    "pairs": npairs, "couples": len(rs),
    "couple_rms_scored_W": r4(math.sqrt(sum(x * x for x in rs) / len(rs))),
    "couple_rms_leak0_W": r4(math.sqrt(sum(x * x for x in r0) / len(r0))),
    "share_of_pairs_where_the_correction_lowers_the_scatter": round(lower / npairs, 3),
    "share_of_pairs_where_the_correction_raises_the_scatter": round(higher / npairs, 3),
    "share_of_pairs_unchanged": round((npairs - lower - higher) / npairs, 3)}
out["A_e178_footing"] = A

# ---------------------------------------------------------------- B: die_mv - reg_mv by load, November
SESS = {
    "E171_aifoundry3": "2026-11-05-e171-blind8-aifoundry3/aifoundry3/e171/p171*/telemetry.jsonl.gz",
    "E178_aifoundry3": "2026-11-06-e178-one-number-aifoundry3/aifoundry3/e178/p178*/telemetry.jsonl.gz",
    "E172_card1": "2026-11-05-e172-blind8-card1/aifoundry1-c1/e172/p172*/telemetry.jsonl.gz",
}


def read_tel(path):
    note(path)
    op = gzip.open if path.endswith(".gz") else open
    rows = []
    with op(path, "rt") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    rows = [r for r in rows if "t_ms" in r]
    rows.sort(key=lambda r: r["t_ms"])
    return rows


B = {}
RAILS = ("minion", "sram", "noc", "ddr", "maxion")
for name, pat in SESS.items():
    files = sorted(glob.glob(os.path.join(DATA, pat)))
    cnt = {lv: {rail: collections.Counter() for rail in RAILS} for lv in ("idle", "busy", "all")}
    spd = collections.Counter()
    setp = collections.Counter()
    nsamp = 0
    for fn in files:
        tel = [r for r in read_tel(fn) if r.get("board_w") is not None and "die_mv" in r and "reg_mv" in r]
        if not tel:
            continue
        bw = sorted(r["board_w"] for r in tel)
        p5 = bw[int(0.05 * (len(bw) - 1))]
        for r in tel:
            nsamp += 1
            setp[r["reg_mv"].get("minion")] += 1
            lv = "idle" if r["board_w"] < p5 + 2.0 else ("busy" if r["board_w"] > p5 + 8.0 else None)
            for rail in RAILS:
                if rail in r["die_mv"] and rail in r["reg_mv"]:
                    d = r["die_mv"][rail] - r["reg_mv"][rail]
                    cnt["all"][rail][d] += 1
                    if lv:
                        cnt[lv][rail][d] += 1
            smv = r.get("sp", {}).get("minion_mv")
            if smv and "minion" in r["die_mv"]:
                spd[smv[0] - r["die_mv"]["minion"]] += 1
    res = {"files": [rel(f) for f in files], "samples": nsamp,
           "minion_set_point_mv": {str(k): v for k, v in sorted(setp.items())}}
    for lv in ("idle", "busy", "all"):
        res[lv] = {}
        for rail, c in cnt[lv].items():
            n = sum(c.values())
            if n:
                res[lv][rail] = {"n": n, "counts_mV": {str(k): v for k, v in sorted(c.items())},
                                 "mean_mV": round(sum(k * v for k, v in c.items()) / n, 3)}
    n = sum(spd.values())
    res["sp_minion_mv_minus_die_mv"] = {"counts_mV": {str(k): v for k, v in sorted(spd.items())},
                                        "share_equal": round(spd[0] / n, 4),
                                        "share_within_1": round(sum(v for k, v in spd.items() if abs(k) <= 1) / n, 4)}
    B[name] = res
out["B_die_minus_set_point_by_load"] = B

# ---------------------------------------------------------------- C: refresh by date
SETS = [
    ("2026-09-29 E58 aifoundry3", "2026-09-29-tau-aifoundry3/p10[1-3]/tel-*.jsonl"),
    ("2026-10-20 bitflip ladder aifoundry3", "2026-10-20-bitflip-ladder/aifoundry3/hl/p*/telemetry.jsonl.gz"),
    ("2026-10-21 dtf aifoundry3", "2026-10-21-dtf/aifoundry3/dtf/p*/telemetry.jsonl.gz"),
    ("2026-10-26 E65 aifoundry3", "2026-10-26-e65-bit-prices-hart-ladder/aifoundry3/hl/p*/telemetry.jsonl.gz"),
    ("2026-10-27 E70 aifoundry3", "2026-10-27-e70-saturation-ladder/aifoundry3/hl/p*/telemetry.jsonl.gz"),
    ("2026-10-31 E78 aifoundry3", "2026-10-31-e78-kinds-energy-matrix/aifoundry3/kinds/p781*/telemetry.jsonl.gz"),
    ("2026-11-05 E171 aifoundry3", SESS["E171_aifoundry3"]),
    ("2026-11-06 E178 aifoundry3", SESS["E178_aifoundry3"]),
    ("2026-09-29 E58 card 1", "2026-09-29-tau-aifoundry1-c1/p[1-3]/tel-*.jsonl"),
    ("2026-11-05 E172 card 1", SESS["E172_card1"]),
]
C = {}
for label, pat in SETS:
    files = sorted(glob.glob(os.path.join(DATA, pat)))
    pairs = n_m = n_b = b_and_m = b_not_m = m_n = notm_n = b_m_or_next = 0
    span, dts = 0.0, []
    for fn in files:
        tel = [r for r in read_tel(fn) if r.get("since_reset_ms", -1) == -1 and r.get("board_w") is not None
               and r.get("sp", {}).get("minion_w")]
        for i in range(1, len(tel)):
            dt = tel[i]["t_ms"] - tel[i - 1]["t_ms"]
            if dt <= 0 or dt > 300:
                continue
            dts.append(dt)
            pairs += 1
            span += dt
            cm = tel[i]["sp"]["minion_w"][0] != tel[i - 1]["sp"]["minion_w"][0]
            cb = tel[i]["board_w"] != tel[i - 1]["board_w"]
            n_m += cm
            n_b += cb
            if cm:
                m_n += 1
                b_and_m += cb
                nxt = i + 1 < len(tel) and tel[i + 1]["board_w"] != tel[i]["board_w"]
                b_m_or_next += (cb or nxt)
            else:
                notm_n += 1
                b_not_m += cb
    C[label] = {"files": len(files), "sample_pairs": pairs, "median_sample_ms": st.median(dts) if dts else None,
                "minion_change_interval_ms": round(span / n_m, 1) if n_m else None,
                "board_change_interval_ms": round(span / n_b, 1) if n_b else None,
                "P_board_changes_given_minion_changes": round(b_and_m / m_n, 4) if m_n else None,
                "P_board_changes_same_or_next_sample_given_minion_changes": round(b_m_or_next / m_n, 4)
                if m_n else None,
                "P_board_changes_given_minion_unchanged": round(b_not_m / notm_n, 4) if notm_n else None}
out["C_refresh_by_date"] = C

# ---------------------------------------------------------------- D: card 1's SRAM reading fraction
QM = os.path.join(DATA, "2026-11-06-q150-meter-checks")
for fn in ("reset_minmax_bylevel.json", "reset_minmax_steady.json"):
    note(os.path.join(QM, fn))
byl = json.load(open(os.path.join(QM, "reset_minmax_bylevel.json")))
std = json.load(open(os.path.join(QM, "reset_minmax_steady.json")))
D = {}
for card, v in byl.items():
    for lv, row in v.items():
        if row:
            m, M = row["min_over_avg"], row["max_over_avg"]
            D["%s sram %s (bylevel)" % (card, lv)] = {"n": row["n"], "m": m, "M": M, "m_over_M": r4(m / M),
                                                      "f": r4((m + M) / (2 * M)), "one_over_f": r4(2 * M / (m + M))}
for card, v in std.items():
    for rail in ("minion_w", "sram_w", "noc_w"):
        row = v.get(rail)
        if row:
            m, M = row["min_over_avg"], row["max_over_avg"]
            D["%s %s (steady)" % (card, rail)] = {"n": row["n"], "f": r4((m + M) / (2 * M))}
out["D_card1_sram_fraction"] = D

# ---------------------------------------------------------------- E: E65's rail and board against harts
LAD = os.path.join(DATA, "2026-10-26-e65-bit-prices-hart-ladder", "ladder.json")
note(LAD)
lad = json.load(open(LAD))
E = {}
for sess, v in lad["sessions"].items():
    pts = sorted((int(h), r["minion_w"], r["d_board_w"]) for h, r in v["per_rung_mean"].items())
    xs = [p[0] for p in pts]
    for idx, nm in ((1, "minion_w level"), (2, "board switched W (d_board_w)")):
        ys = [p[idx] for p in pts]
        mx, my = st.mean(xs), st.mean(ys)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        a = my - b * mx
        res = [y - (a + b * x) for x, y in zip(xs, ys)]
        E["%s, %s" % (sess, nm)] = {"intercept_W": r4(a), "slope_mW_per_hart": round(1000 * b, 2),
                                    "max_abs_residual_W": r4(max(abs(r) for r in res)),
                                    "max_residual_pct_of_span": round(
                                        100 * max(abs(r) for r in res) / (b * (max(xs) - min(xs))), 2),
                                    "harts": xs}
out["E_e65_against_harts"] = E

# ---------------------------------------------------------------- F: arithmetic
F = {}
hp = A["his_pair"]["scored"]
cpp = hp["couples"] / len(hp["pass_means"])
F["couples_per_pass"] = round(cpp, 2)
F["observed_pass_sd_W"] = hp["pass_sd"]
for nm, s in (("his_pair_couple_sd", hp["couple_sd"]), ("registered_couple_noise", 0.125)):
    ps = s / math.sqrt(cpp)
    F["per_pass_sd_predicted_from_" + nm] = r4(ps)
    F["half_widths_W_from_" + nm] = {str(n): r4(t975(n - 1) * ps / math.sqrt(n)) for n in (4, 8, 16)}
quad_s = 4 * 0.49 + 0.01
abba = {}
for duty in (0.49, 0.65):
    nq = 30 * 60 * duty / quad_s
    for lab_, sd in (("window_from_170ms", 0.0339), ("window_from_250ms", 0.0406),
                     ("window_from_100ms_no_dip_rule", 0.0772)):
        hw = 1.96 * sd / math.sqrt(nq)
        abba["duty %.2f, %s" % (duty, lab_)] = {"quad_sd_W": sd, "quads_in_30_min": round(nq), "hw_W": r4(hw),
                                               "hw_doubled_W": r4(2 * hw)}
F["abba_30_card_minutes"] = abba
F["abba_note"] = ("quad sd: four 0.49 s launches inside one E178 run read as A B B A, board_w averaged from the "
                  "window start to the launch's end, int8 one-number kinds (67 quads); post hoc")
out["F_arithmetic"] = F

out["inputs_sha256"] = dict(sorted(INPUTS.items()))
json.dump(out, sys.stdout, indent=1)
print()
