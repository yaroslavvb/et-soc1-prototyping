#!/usr/bin/env python3
"""E102: every number the README quotes beyond scored.json's own keys, recomputed from committed files. Standard library, and numpy for section M. Labelled POST HOC where it is: no rule depends on anything here.

    cd docs/reports/data/2026-11-01-e102-balanced-bit-prices && python3 check_e102.py > check_e102.txt
"""
import csv
import glob
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds"))
sys.path.insert(0, K)
import score_e102 as sc  # noqa: E402

reg = json.load(open(os.path.join(K, "predictions-e102.json")))
tiles = json.load(open(os.path.join(K, "e102", "e102.json")))["tiles"]
S = json.load(open(os.path.join(HERE, "scored.json")))
P = S["primary"]
RAW = os.path.join(HERE, "aifoundry1-c1", "kinds")
RATE = reg["analysis"]["rate_ops_per_s"]
POS = reg["positions"]


def f(x, nd=3):
    return "—" if x is None else f"{x:.{nd}f}"


def fi(p, nd=3):
    return "—" if p["mean"] is None else (f"{p['mean']:.{nd}f}" if p.get("lo") is None else f"{p['mean']:.{nd}f} [{p['lo']:.{nd}f}, {p['hi']:.{nd}f}]")


def sect(t):
    print("\n" + t)


# ---- [A] what ran
sect("[A] blocks, skips, and the trains' own gate")
print(open(os.path.join(HERE, "logs", "e102-queue.log")).read().count("rc=0"), "blocks rc=0; queue:", [l.strip()[:60] for l in open(os.path.join(HERE, "logs", "e102-queue.log")) if "queue" in l][-1])
for d in sorted(glob.glob(os.path.join(RAW, "p102*"))):
    M = [json.loads(l) for l in open(os.path.join(d, "marks.jsonl")) if l.startswith("{")]
    R = [m for m in M if m["kind"] == "run"]
    H = [m for m in M if m["kind"] == "heater"]
    Sk = [m for m in M if m["kind"] == "skipped"]
    dt = sorted((b["t_start_ms"] - a["t_start_ms"]) / 1000 for a, b in zip(R, R[1:]))
    print(f"  {os.path.basename(d)}: {len(R)} runs, {len(H)} heaters, median {dt[len(dt) // 2]:.2f} s a run; skipped: " +
          ("; ".join(f"{m['item']} (now {m.get('start_c')} C, hot {m.get('start_hot_c')} C, {m.get('heats')} heats, {m.get('wait_s')} s, quiet {m.get('quiet_s')} s)" for m in Sk) or "none"))
print("  the own gate:", P["passes_set_aside_by_own_gate"])
RUNS = sc.load_runs(os.path.join(HERE, "runs.csv"))
lim = reg["analysis"]["gates"]["train_zero_mid_departure_rail_w"]
deps = []
for p in sorted({r["pass"] for r in RUNS if sc.block_of(r["pass"]) in "TI"}):
    for z in {t["zero"] for t in tiles.values() if t["zero"]}:
        reads = sorted([r for r in RUNS if r["pass"] == p and r["item"] == z and r["segment"] != -1], key=lambda r: r["t0"])
        for a, b, c in zip(reads, reads[1:], reads[2:]):
            line = a["rail"] + (c["rail"] - a["rail"]) * (b["t0"] - a["t0"]) / max(c["t0"] - a["t0"], 1)
            lineb = a["p_raw"] + (c["p_raw"] - a["p_raw"]) * (b["t0"] - a["t0"]) / max(c["t0"] - a["t0"], 1)
            deps.append((p, z, b["pos"], b["rail"] - line, b["p_raw"] - lineb))
print(f"  all {len(deps)} interior own-zero reads in the trains, rail off the line through neighbours (limit {lim} W), largest five:")
for x in sorted(deps, key=lambda x: -abs(x[3]))[:5]:
    print(f"    pass {x[0]} {x[1]} pos {x[2]}: rail {x[3]:+.3f} W, board {x[4]:+.3f} W")
reads = sorted([r for r in RUNS if r["pass"] == 10223 and r["item"] == "fp32.aq" and r["segment"] != -1], key=lambda r: r["t0"])
print("  fp32.aq in pass 10223, rail at each read:", [round(r["rail"], 3) for r in reads], "positions", [r["pos"] for r in reads])

sect("[B] the noise the trains actually had: the interior own-zero reads' departure over sqrt(1.5), watts a run, against E93's registered board and rail")
print(f"  registered from E93: board {reg['analysis']['noise_from_e93_w']['p_raw']}, rail {reg['analysis']['noise_from_e93_w']['rail_raw']}")
for blk in "TI":
    dd = [x for x in deps if sc.block_of(x[0]) == blk]
    print(f"  block {blk}, {len(dd)} reads: board {math.sqrt(sum(x[4] ** 2 for x in dd) / len(dd)) / 1.5 ** 0.5:.3f}, rail {math.sqrt(sum(x[3] ** 2 for x in dd) / len(dd)) / 1.5 ** 0.5:.3f}")
g = []
for p in (10210, 10211, 10212, 10213, 10214):
    for z in ("fp32.hq", "fp32.aq", "fp16.hq", "fp16.aq"):
        rr = sorted([r for r in RUNS if r["pass"] == p and r["item"] == z], key=lambda r: r["t0"])
        if len(rr) == 2:
            g.append((rr[1]["p80"] - rr[0]["p80"], rr[1]["rail"] - rr[0]["rail"]))
print(f"  block G, last - first own zero of a pass (drift included), {len(g)} pairs: board rms {math.sqrt(sum(x[0] ** 2 for x in g) / len(g)):.3f}, rail rms {math.sqrt(sum(x[1] ** 2 for x in g) / len(g)):.3f}, over sqrt(2)")

# ---- [C] every rule's cells
sect("[C] the rules' cells (primary reduction)")
R = P["rules"]
for rid in ("E102-R1", "E102-R2"):
    print(f"  {rid}: {R[rid]['verdict']} on the rail, {R[rid]['board_arm']['verdict']} on the board")
    for j, c in R[rid]["board_arm"]["cells"].items():
        r = R[rid]["rail_arm"]["cells"][j]
        pm = POS[c["top"]]["pred_w"]["bench_map"] / POS[c["top"]]["designed_flips_per_op"] / (POS[c["bot"]]["pred_w"]["bench_map"] / POS[c["bot"]]["designed_flips_per_op"])
        print(f"    bit {j:>2s}: board {f(c['ratio'], 2)} [{f(c['lo'], 2)}, {f(c['hi'], 2)}], rail {f(r['ratio'], 2)} [{f(r['lo'], 2)}, {f(r['hi'], 2)}], bench {pm:.2f}, n {c['n']}, {'paired' if c['paired'] else 'gate/train'}")
print(f"  E102-R3: {R['E102-R3']['verdict']}")
for k, c in R["E102-R3"]["rail_arm"]["cells"].items():
    b = R["E102-R3"]["board_arm"]["cells"][k]
    d, db = c["balanced_minus_all_in_w"], b["balanced_minus_all_in_w"]
    print(f"    {k}: balanced - all-in, rail {fi(d)} (n {d['n']}), board {fi(db)}; ratio rail {f(c['ratio_all_in_over_balanced']['ratio'], 2)}, board {f(b['ratio_all_in_over_balanced']['ratio'], 2)}")
print(f"  E102-R4: {R['E102-R4']['verdict']}")
for k, c in R["E102-R4"]["rail_arm"]["cells"].items():
    b = R["E102-R4"]["board_arm"]["cells"][k]
    print(f"    {k}: rail {fi(c['difference_w'])} (n {c['difference_w']['n']}), floor {c['floor_w']} W: {c['verdict']}; board {fi(b['difference_w'])}: {b['verdict']}")
print(f"  E102-R5: {R['E102-R5']['verdict']}")
for k, c in R["E102-R5"]["cells"].items():
    print(f"    {k}: {f(c['value'], 1)} [{f(c['lo'], 1)}, {f(c['hi'], 1)}], band {c['band']}: {c['verdict']}")
print(f"  E102-R6: rail {R['E102-R6']['rail_arm']['verdict']}, board {R['E102-R6']['board_arm']['verdict']}")
for arm in ("rail", "board"):
    a = R["E102-R6"][arm + "_arm"]
    print(f"    {arm}: pooled train - gate {fi(a['pooled_train_minus_gate_w'])}, band +-{a['band_w']}; " + "; ".join(f"{k.split('.')[0]} {k.split('.')[1]} {fi(v['train_minus_gate_w'])}" for k, v in a["cells"].items()))
print(f"  E102-R7: board {R['E102-R7']['board_arm']['verdict']}, rail {R['E102-R7']['rail_arm']['verdict']}")
for j, c in R["E102-R7"]["board_arm"]["cells"].items():
    print(f"    bit {j}: excess {c['excess_w']:.3f} W, flop-bit changes an op {c['flops_per_op']:.0f}, at E92's price {c['flops_w_at_e92_price']:.3f} W, share {c['share']:.3f}, implied {c['implied_fJ_per_flop_bit']:.1f} fJ per flop bit")
for rid in ("E102-R8",):
    for arm in ("rail", "board"):
        a = R[rid][arm + "_arm"]
        print(f"  {rid} {arm}: {a['verdict']}: bk_ff {fi(a['price']['W'])} W, {fi(a['price']['fJ'], 1)} fJ per flipped bit")
for rid in ("E102-R9", "E102-R10"):
    for arm in ("rail", "board"):
        a = R[rid][arm + "_arm"]
        print(f"  {rid} {arm}: {a['verdict']}: difference {fi(a['difference_w'])} W; ratio {f(a['ratio']['ratio'], 2)} [{f(a['ratio']['lo'], 2)}, {f(a['ratio']['hi'], 2)}]")
for arm in ("rail", "board"):
    a = R["E102-R11"][arm + "_arm"]
    for k, c in a["cells"].items():
        print(f"  E102-R11 {arm}: {k}: {fi(c['difference_w'])} W; ratio {f(c['ratio']['ratio'], 2)} [{f(c['ratio']['lo'], 2)}, {f(c['ratio']['hi'], 2)}]")
    print(f"    verdict {a['verdict']}")
for arm in ("rail", "board"):
    a = R["E102-R12"][arm + "_arm"]
    print(f"  E102-R12 {arm}: {a['coefficients_of_8']} of 8 coefficients; median half-width {f(a['median_half_width_fJ'], 1)} fJ against registered {a['registered_half_width_fJ']}")
print(f"  E102-S1: {R['E102-S1']['verdict']}: " + "; ".join(f"{k} {f(v['D_w']['mean'])} vs {v['ref_w']} ({f(v['difference_w'])}, band {v['band_w']})" for k, v in R["E102-S1"]["cells"].items()))
print("  arms where S1 fails, and any rule that moves against the primary:")
for name, a in S["arms"].items():
    moved = [f"{k.split('-')[1]} {v['verdict']}" for k, v in a["rules"].items() if v["verdict"] != R[k]["verdict"]]
    print(f"    {name}: {moved or 'no verdict moves'}")

# ---- [D] post hoc: the own gate off
sect("[D] POST HOC, labelled, no verdict: pass 10223 back in (the trains' own gate opened), everything else as registered")
open_reg = json.loads(json.dumps(reg))
open_reg["analysis"]["gates"]["train_zero_mid_departure_rail_w"] = 1e9
res = json.load(open(os.path.join(HERE, "e102.json")))
book = sc.Book(RUNS, tiles, open_reg["analysis"]["gates"], set_aside={x["pass"] for x in res.get("passes_set_aside", [])})
Rx = sc.score(book, tiles, open_reg, RUNS)
print("  passes", book.passes)
print("  verdicts:", "; ".join(f"{k.split('-')[1]} {v['verdict']}" for k, v in Rx.items()))
for j, c in Rx["E102-R2"]["rail_arm"]["cells"].items():
    b = Rx["E102-R2"]["board_arm"]["cells"][j]
    print(f"    A, bit {j:>2s}: rail {f(c['ratio'], 2)} [{f(c['lo'], 2)}, {f(c['hi'], 2)}], board {f(b['ratio'], 2)} [{f(b['lo'], 2)}, {f(b['hi'], 2)}]")
for j in ("0", "6", "11"):
    c = Rx["E102-R1"]["rail_arm"]["cells"][j]
    print(f"    B, bit {j:>2s}: rail {f(c['ratio'], 2)} [{f(c['lo'], 2)}, {f(c['hi'], 2)}]")

# ---- [E] post hoc: R3 and R4's legs that a launch skip took below three passes
sect("[E] the items R3 and R4's B leg read, per pass (10213 and 10214 are amendment A1's), watts over the own zero; then the mean over bits 23, 27, 30, 31, POST HOC, labelled, no verdict")
primary_book = sc.Book(RUNS, tiles, reg["analysis"]["gates"], set_aside={x["pass"] for x in res.get("passes_set_aside", [])})
for it in ("fp32.bj_23", "fp32.bp_23", "fp32.bj_27", "fp32.bp_27", "fp32.bj_30", "fp32.bp_30", "fp32.bj_31", "fp32.bp_31"):
    print(f"  {it}: rail {[(p % 10, round(v, 3)) for p, v in sorted(primary_book.series('G', it, 'rail').items())]}; board {[(p % 10, round(v, 3)) for p, v in sorted(primary_book.series('G', it, 'board').items())]}")
ex = {}
for arm in ("rail", "board"):
    pooled = {}
    for p in (10210, 10211, 10212, 10213, 10214):
        vals = []
        for j in (23, 27, 30, 31):
            a = primary_book.series("G", f"fp32.bp_{j}", arm).get(p)
            b = primary_book.series("G", f"fp32.bj_{j}", arm).get(p)
            if a is not None and b is not None:
                vals.append(a - b)
        pooled[p] = (sum(vals) / len(vals), len(vals))
    m = sc.mean_ci([v[0] for v in pooled.values()])
    print(f"  mean over bits 23, 27, 30, 31 of balanced - all-in per pass, {arm}: {[(p % 10, round(v[0], 3), v[1]) for p, v in pooled.items()]}: {fi(m)} W, n {m['n']}")

# ---- [F] int8
sect("[F] int8's B side: the singles, on the rail and the board")
for arm in ("rail", "board"):
    ser = {j: primary_book.series("I", f"int8.bk_{j}", arm) for j in range(8)}
    keys = sorted(set.intersection(*[set(s) for s in ser.values()]))
    odd = {k: sum(ser[j][k] for j in (1, 3, 5)) / 3 for k in keys}
    even = {k: sum(ser[j][k] for j in (0, 2, 4)) / 3 for k in keys}
    r = sc.fieller(odd, even)
    d = sc.mean_ci([odd[k] - even[k] for k in keys])
    print(f"  {arm}: bits 1,3,5 over 0,2,4: {f(r['ratio'], 2)} [{f(r['lo'], 2)}, {f(r['hi'], 2)}]; difference {fi(d)} W a bit; mean of the eight {fi(sc.mean_ci([sum(ser[j][k] for j in range(8)) / 8 for k in keys]))} W, or {fi(sc.mean_ci([sum(ser[j][k] for j in range(8)) / 8 / (1024 * RATE['int8']) * 1e15 for k in keys]), 1)} fJ")
    print("     the list, fJ per flipped bit:", " ".join(f"{j}:{sc.mean_ci(primary_book.series('I', f'int8.bk_{j}', 'fj_' + arm if False else arm).values())['mean'] / (1024 * RATE['int8']) * 1e15:.0f}" for j in range(8)))
    # masks against their singles, and a digit count: radix-4 digits a mask's bits enter (a 9-bit operand: 5 digits)
    def digits(mask):
        d_ = set()
        for b in range(8):
            if mask >> b & 1:
                d_.add(b // 2)              # the bit is in digit b//2 as its low or middle bit ...
                if b % 2 == 1:
                    d_.add(b // 2 + 1)      # ... and an odd bit is also the next digit's low input
        return len(d_)
    for tag, m in (("15", 0x15), ("2a", 0x2A), ("0f", 0x0F), ("f0", 0xF0), ("ff", 0xFF)):
        bits = [b for b in range(8) if m >> b & 1]
        x = primary_book.series("I", f"int8.bk_{tag}", arm)
        y = {k: sum(ser[b][k] for b in bits) for k in x if all(k in ser[b] for b in bits)}
        r = sc.fieller({k: x[k] for k in y}, y)
        single_digits = sum(1 if b % 2 == 0 else 2 for b in bits)
        print(f"     {tag}: {fi(sc.mean_ci(x.values()))} W against its singles' sum {f(sum(y.values()) / len(y))} W: {f(r['ratio'], 2)} [{f(r['lo'], 2)}, {f(r['hi'], 2)}]; digit count {digits(m)} of {single_digits}: {digits(m) / single_digits:.2f}")
raw79 = {j: POS[f"int8.bk_{j}"]["pred_w"]["e79_measured"] for j in range(8)}


def spearman(a, b):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for i, k in enumerate(o):
            r[k] = i + 1.0
        return r
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    n = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return n / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))


for arm in ("board", "rail"):
    v = {j: sc.mean_ci(primary_book.series("I", f"int8.bk_{j}", arm).values())["mean"] for j in range(8)}
    sc_ = 1.0 if arm == "board" else reg["analysis"]["rail_over_board"]
    print(f"  against E79's list on aifoundry3 with no temperature term (over the card scale), {arm}: Spearman, bits 0-6 {spearman([raw79[j] for j in range(7)], [v[j] for j in range(7)]):.2f}, all eight {spearman([raw79[j] for j in range(8)], [v[j] for j in range(8)]):.2f}; rms {math.sqrt(sum((v[j] - sc_ * raw79[j]) ** 2 for j in range(8)) / 8):.3f} W")
print("  bk_j under E79's way, board p80 with the run's own reading in the train, fJ [95%]; 'bound' where the interval contains zero:")
for name in ("E79's way at 0.2414 (p80 in the trains)", "E79's way at 0.3803", "E79's way at 0.545"):
    a = S["arms"][name]["prices"]
    print(f"    {name}: " + " ".join(f"{j}:{a[f'int8.bk_{j}@I']['board']['fJ']['mean']:.0f}{'*' if a[f'int8.bk_{j}@I']['board']['bound'] else ''}" for j in range(8)) + f"; {sum(1 for j in range(8) if a[f'int8.bk_{j}@I']['board']['bound'])} of 8 bounds")
a = P["prices"]
print("    primary board, no temperature term: " + " ".join(f"{j}:{a[f'int8.bk_{j}@I']['board']['fJ']['mean']:.0f}{'*' if a[f'int8.bk_{j}@I']['board']['bound'] else ''}" for j in range(8)))

# ---- [G] the shape: the bench against the measured ratio over all positions
sect("[G] the frozen predictors against the measured ratio, per flipped bit, all ten positions of each fp32 side (board; the ratio of mean steps at where() blocks)")
for side, aa, bb in (("B", "bj", "bp"), ("A", "aj", "ap")):
    xs, ys, zs = [], [], []
    for j in (0, 6, 11, 16, 20, 22, 23, 27, 30, 31):
        ta, tb = f"fp32.{aa}_{j}", f"fp32.{bb}_{j}"
        m = sc.per_bit_ratio(primary_book, tiles, ta, tb, "board")
        mr = sc.per_bit_ratio(primary_book, tiles, ta, tb, "rail")
        pm = POS[ta]["pred_w"]["bench_map"] / POS[ta]["designed_flips_per_op"] / (POS[tb]["pred_w"]["bench_map"] / POS[tb]["designed_flips_per_op"])
        print(f"  {side} bit {j:2d}: all-in {P['prices'][ta + '@' + sc.where(tiles, ta)]['board']['fJ']['mean']:6.0f} fJ, balanced {P['prices'][tb + '@' + sc.where(tiles, tb)]['board']['fJ']['mean']:5.0f} fJ, ratio board {f(m['ratio'], 2)}, rail {f(mr['ratio'], 2)}, bench {pm:.2f}, n {m['n']}")
        xs.append(pm)
        ys.append(m["ratio"])
        zs.append(mr["ratio"])
    lx = [math.log(x) for x in xs]
    print(f"    Spearman(bench, measured) board {spearman(xs, ys):.2f}, rail {spearman(xs, zs):.2f}; rms of log ratio, board {math.sqrt(sum((math.log(y) - x) ** 2 for x, y in zip(lx, ys)) / len(lx)):.2f}")

sect("[H] balanced fp32 over the mantissa, board fJ per flipped bit (train), and the published all-in list over the card scale")
for side, aa, bb, pre in (("B", "bj", "bp", "E65"), ("A", "aj", "ap", "E67")):
    print(f"  {side}: " + " ".join(f"{j}:{P['prices'][f'fp32.{bb}_{j}@T']['board']['fJ']['mean']:.0f}" for j in (0, 6, 11, 16, 20, 22)) + f"; all-in here " + " ".join(f"{j}:{P['prices'][f'fp32.{aa}_{j}@' + sc.where(tiles, f'fp32.{aa}_{j}')]['board']['fJ']['mean']:.0f}" for j in (0, 6, 11, 16, 20, 22)) + f"; {pre} " + " ".join(f"{j}:{POS[f'fp32.{aa}_{j}']['pred_fJ']['all_in_list']:.0f}" for j in (0, 6, 11, 16, 20, 22)))

sect("[I] the counts on real accumulators, frozen: C-read bits and flop-bit changes an op over the own zero")
for j in (0, 6, 11, 16, 20, 22, 23, 27, 30, 31):
    a, b = POS[f"fp32.bj_{j}"], POS[f"fp32.bp_{j}"]
    z = POS[a["zero"]]
    print(f"  bit {j:2d}: all-in C read {a['exact']['cbus'] - z['exact']['cbus']:7.0f}, flops {a['flops'] - z['flops']:7.0f}; balanced C read {b['exact']['cbus'] - z['exact']['cbus']:7.0f}, flops {b['flops'] - z['flops']:7.0f}, alternations {b['alt']:5.0f}; from fl((n-1)S) all-in C read {a['stream']['cbus'] - z['stream']['cbus']:7.0f}")

sect("[J] the die reading: launch and window, by block (whole degrees; mean, min, max of a run's window mean)")
for blk in "GTI":
    rr = [r for r in RUNS if sc.block_of(r["pass"]) == blk and r["t_win"] is not None]
    v = [r["t_win"] for r in rr]
    print(f"  {blk}: mean {sum(v) / len(v):.1f}, min {min(v):.1f}, max {max(v):.1f} C, {len(v)} runs")
for p in (10220, 10221, 10222, 10223, 10230, 10231, 10232, 10233, 10234):
    v = sorted((r["t0"], r["t_win"]) for r in RUNS if r["pass"] == p and r["t_win"] is not None)
    print(f"  {p}: first run {v[0][1]:.1f} C, last run {v[-1][1]:.1f} C")

sect("[K] rail over board on the steps of 1 W or more (board arm in the same block)")
vals = []
for k, e in P["prices"].items():
    b, r = e["board"]["W"]["mean"], e["rail"]["W"]["mean"]
    if b is not None and r is not None and abs(b) >= 1.0:
        vals.append(r / b)
vals.sort()
print(f"  {len(vals)} steps: median {vals[len(vals) // 2]:.3f}, range {vals[0]:.3f}-{vals[-1]:.3f}")

# ---- [L] a crude cross-check from the raw telemetry, with none of the reduction's code: the median board and the plain mean rail in each run's window, own zero's flat pass mean
sect("[L] POST HOC cross-check: from raw telemetry, no reduction, no dip removal, no interpolation: median board_w over [t0+1, t0+3) and mean rail over [t0+2, t0+4), step = item - the mean of its own zero's reads in the pass, mean over the kept passes")
pass_vals = {}
for d in sorted(glob.glob(os.path.join(RAW, "p102*"))):
    p = int(os.path.basename(d)[1:])
    tel = [json.loads(l) for l in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") if l.startswith("{")]
    recs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl")) if l.startswith("{")]
    first = {}
    for r in recs:
        k = (r["item"], r["pos"], r.get("segment"))
        first[k] = min(first.get(k, 1e18), r["t_start_ms"])
    rows = {}
    for (item, pos, seg), t0 in first.items():
        if seg == -1 and item != "anchor_pi":
            continue
        bw = sorted(s["board_w"] for s in tel if t0 + 1000 <= s["t_ms"] < t0 + 3000)
        rw = [s["sp"]["minion_w"][0] for s in tel if t0 + 2000 <= s["t_ms"] < t0 + 4000]
        if bw and rw:
            rows.setdefault(item, []).append((bw[len(bw) // 2], sum(rw) / len(rw)))
    pass_vals[p] = {k: (sum(x[0] for x in v) / len(v), sum(x[1] for x in v) / len(v)) for k, v in rows.items()}
kept = {b: P["passes_kept"][b] for b in "GTI"}


def crude(item, blk):
    z = tiles[item]["zero"]
    ds = [(pass_vals[p][item][0] - pass_vals[p][z][0], pass_vals[p][item][1] - pass_vals[p][z][1]) for p in kept[blk] if item in pass_vals[p] and z in pass_vals[p]]
    return sc.mean_ci([x[0] for x in ds]), sc.mean_ci([x[1] for x in ds])


for item, blk in (("fp32.bj_22", "G"), ("fp32.bp_22", "T"), ("fp32.bj_0", "T"), ("fp32.bp_0", "T"), ("fp32.bj_6", "T"), ("fp32.bp_6", "T"), ("fp32.bj_11", "T"), ("fp32.bp_11", "T"), ("fp32.bp_23", "G"), ("fp32.bj_27", "G"), ("fp32.bp_27", "G"), ("fp32.ap_16", "T"), ("fp32.aj_16", "G"),
                  ("int8.bk_15", "I"), ("int8.bk_2a", "I"), ("int8.bk_ff", "I"), ("int8.bk_5", "I"), ("int8.bk_4", "I")):
    a, b = crude(item, blk)
    e = P["prices"][f"{item}@{blk}"]
    print(f"  {item:12s} {blk}: board median {fi(a)} (scored {fi(e['board']['W'])}); rail {fi(b)} (scored {fi(e['rail']['W'])})")

# ---- [M] post hoc: the float trains warm up, so fit the warm-up instead of drawing straight lines through it
sect("[M] POST HOC, labelled, no verdict: a float train warms by about 4 C over its 4.7 min (section J), so its own zeros rise along a curve and straight lines through them under-read the zero in the first quarter. Here each T pass's zero reads, settling runs included, are fitted together: one offset per zero tile + c exp(-t/tau), tau from a grid per pass; a step is an item's read minus that curve. Each pass's rms is the zeros' scatter about the curve.")
import numpy as np  # noqa: E402


def drift_steps(runs, passes, arm):
    out = {}
    rms = {}
    key = "rail" if arm == "rail" else "p_raw"
    for p in passes:
        rr = [r for r in runs if r["pass"] == p and not r["fail"] and r[key] is not None]
        t0 = min(r["t0"] for r in rr)
        zs = sorted({r["item"] for r in rr if r["item"] in tiles and tiles[r["item"]]["layout"] == "zero"})
        Z = [r for r in rr if r["item"] in zs]
        best = None
        for tau in (20, 30, 45, 60, 90, 120, 180, 240, 300, 450, 600, 900):
            X = np.zeros((len(Z), len(zs) + 1))
            y = np.array([r[key] for r in Z])
            for i, r in enumerate(Z):
                X[i, zs.index(r["item"])] = 1
                X[i, -1] = math.exp(-(r["t0"] - t0) / 1000 / tau)
            co = np.linalg.lstsq(X, y, rcond=None)[0]
            res = y - X @ co
            sse = float(res @ res)
            if best is None or sse < best[0]:
                best = (sse, tau, co, len(y) - X.shape[1])
        sse, tau, co, dof = best
        rms[p] = (round(math.sqrt(sse / max(dof, 1)), 3), tau, round(float(co[-1]), 3))
        per = {}
        for r in rr:
            t = tiles.get(r["item"])
            if not t or t["layout"] == "zero" or not t["zero"] or t["zero"] not in zs:
                continue
            base = co[zs.index(t["zero"])] + co[-1] * math.exp(-(r["t0"] - t0) / 1000 / tau)
            per.setdefault(r["item"], []).append(r[key] - float(base))
        for it, v in per.items():
            out.setdefault(it, {})[p] = sum(v) / len(v)
    return out, rms


for label, passes in (("the kept three, 10220-10222", (10220, 10221, 10222)), ("all four, 10223 back in", (10220, 10221, 10222, 10223))):
    print(f"  {label}:")
    for arm in ("rail", "board"):
        st, rms = drift_steps(RUNS, passes, arm)
        print(f"    {arm}: the zeros' scatter about the curve (W a run; tau s; amplitude W), per pass: {rms}")
        for side, aa, bb in (("B", "bj", "bp"), ("A", "aj", "ap")):
            cells = []
            for j in (0, 6, 11) if side == "B" else (0, 6, 11, 23, 27, 30, 31):
                ta, tb = f"fp32.{aa}_{j}", f"fp32.{bb}_{j}"
                r = sc.fieller(st[ta], st[tb], tiles[tb]["designed_flips_per_op"] / tiles[ta]["designed_flips_per_op"])
                cells.append(f"{j}: {f(r['ratio'], 2)} [{f(r['lo'], 2)}, {f(r['hi'], 2)}]")
            print(f"      {side}, all-in / balanced, per bit: " + "; ".join(cells))
        ls = []
        for it in ("fp32.bp_0", "fp32.bp_6", "fp32.bp_11", "fp32.bp_16", "fp32.bp_20", "fp32.bp_22", "fp32.ap_0", "fp32.ap_6", "fp32.ap_11", "fp32.ap_16", "fp32.ap_20", "fp32.ap_22"):
            m = sc.mean_ci(st[it].values())
            n_ = tiles[it]["designed_flips_per_op"]
            ty = 1e15 / (n_ * RATE["fp32"])
            ls.append(f"{it.split('.')[1]} {m['mean'] * ty:.0f} [{m['lo'] * ty:.0f}, {m['hi'] * ty:.0f}]")
        print("      balanced, fJ per flipped bit: " + "; ".join(ls))

sect("[N] fp16: all-in over balanced per flipped bit, primary reduction, and the bench's (paired inside a block; 9 in the gate; 0 gate over train)")
for side, aa, bb, js in (("B", "bj", "bp", (0, 9, 12, 15)), ("A", "aj", "ap", (9, 12))):
    for j in js:
        ta, tb = f"fp16.{aa}_{j}", f"fp16.{bb}_{j}"
        kw = {"top_block": "G", "bot_block": "G"} if j == 9 else {}
        m = sc.per_bit_ratio(primary_book, tiles, ta, tb, "board", **kw)
        r = sc.per_bit_ratio(primary_book, tiles, ta, tb, "rail", **kw)
        pm = POS[ta]["pred_w"]["bench_map"] / POS[ta]["designed_flips_per_op"] / (POS[tb]["pred_w"]["bench_map"] / POS[tb]["designed_flips_per_op"])
        print(f"  {side} bit {j:2d}: board {f(m['ratio'], 2)} [{f(m['lo'], 2)}, {f(m['hi'], 2)}], rail {f(r['ratio'], 2)} [{f(r['lo'], 2)}, {f(r['hi'], 2)}], bench {pm:.2f}, n {m['n']}")

sect("[O] the balanced mantissa's spread, fp32 B and A (train, board fJ, primary) and what a position's bench count says; the mean of the published lists' low floor")
bp = [P["prices"][f"fp32.bp_{j}@T"]["board"]["fJ"]["mean"] for j in (0, 6, 11, 16, 20, 22)]
print(f"  B balanced: min {min(bp):.0f}, max {max(bp):.0f}, ratio {max(bp) / min(bp):.2f}; all-in over the same bits: {P['prices']['fp32.bj_0@T']['board']['fJ']['mean']:.0f} to {P['prices']['fp32.bj_22@G']['board']['fJ']['mean']:.0f}")

# ---- [P] amendment A1's dense train, and what its own gate did
sect("[P] amendment A1's R blocks. The gate set aside 10241, 10242, 10243, because each block's FIRST read follows the idle gap between blocks and its rail window is not yet settled (10240 opened with five settling reads; the others had none): E102-R2a NOT SCORED")
A1 = json.load(open(os.path.join(HERE, "scored-a1.json")))
print("  kept", A1["passes_kept"], "set aside", A1["set_aside"])
for p in (10240, 10241, 10242, 10243):
    rr = sorted([r for r in RUNS if r["pass"] == p and r["item"] == "fp32.aq"], key=lambda r: r["pos"])
    print(f"  {p}, fp32.aq on the rail at each position: " + " ".join(f"{r['pos']}:{r['rail']:.3f}" for r in rr))
sect("[Q] POST HOC, labelled, no verdict: A1's R blocks with the first read after an idle gap treated as what 10240's five settling reads were. Dropped: in 10240 positions 0-4; in the others position 0 and the first pair, positions 1 and 2, which only that read brackets. Every remaining item is then between two zero reads")
series = {"board": {}, "rail": {}}
gates = []
for p in (10240, 10241, 10242, 10243):
    drop = 4 if p == 10240 else 2
    rr = sorted([r for r in RUNS if r["pass"] == p and r["pos"] > drop and not r["fail"]], key=lambda r: r["pos"])
    z = [r for r in rr if r["item"] == "fp32.aq"]
    for a, b, c in zip(z, z[1:], z[2:]):
        gates.append((p, b["pos"], round(b["rail"] - (a["rail"] + (c["rail"] - a["rail"]) * (b["t0"] - a["t0"]) / (c["t0"] - a["t0"])), 3)))
    for arm, key in (("board", "p_raw"), ("rail", "rail")):
        pts = [(q["t0"], q[key]) for q in z]
        per = {}
        for r in rr:
            if r["item"] != "fp32.aq":
                per.setdefault(r["item"], []).append(r[key] - sc.interp(pts, r["t0"]))
        for it, v in per.items():
            series[arm].setdefault(it, {})[p] = sum(v) / len(v)
print("  the same gate on what is left (limit 0.25 W), largest:", sorted(gates, key=lambda x: -abs(x[2]))[:3])
for arm in ("rail", "board"):
    for j in (0, 6):
        a, b = series[arm][f"fp32.aj_{j}"], series[arm][f"fp32.ap_{j}"]
        r = sc.fieller(a, b, 1920 / 2048)
        ma, mb = sc.mean_ci(a.values()), sc.mean_ci(b.values())
        tt = 1e15 / RATE["fp32"]
        print(f"  {arm}, bit {j}: all-in {fi(ma)} W, {ma['mean'] * tt / 2048:.0f} fJ; balanced {fi(mb)} W, {mb['mean'] * tt / 1920:.0f} fJ; ratio per bit {f(r['ratio'], 2)} [{f(r['lo'], 2)}, {f(r['hi'], 2)}], {r['n']} blocks")
    print(f"    the rule's thresholds on this arm would read: upper bounds {'below' if all(sc.fieller(series[arm][f'fp32.aj_{j}'], series[arm][f'fp32.ap_{j}'], 1920 / 2048)['hi'] is not None and sc.fieller(series[arm][f'fp32.aj_{j}'], series[arm][f'fp32.ap_{j}'], 1920 / 2048)['hi'] < 4 for j in (0, 6)) else 'not all below'} 4 at bits 0 and 6")
