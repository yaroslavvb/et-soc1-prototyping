#!/usr/bin/env python3
"""E96: post-hoc checks, written after the data and LABELLED -- none is a registered rule or changes a verdict. Every number is read from
results.json (reduce_e96.py's output), this experiment's predictions.json, the queue's records, E98's desk table and E80's, E83's and E87's results.json.
Standard library only.

    python3 checks.py > checks.txt

K1  the session's timing: card-minutes, per-run rates against the plan's, the gates, the safety peaks.
K2  the bursts: every gated float and int8 pass, the power-limited passes' spread, the like-with-like shares pass by pass, and int8's shares from the
    800 MHz power alone, because E64's c lets one or two ramp samples at 700 MHz into the fit of a tile that holds 800 MHz.
K3  the idle resets and the late ramps; why S1's one sustained miss read 795.4 MHz.
K4  the gate and the clock: how far the relation, the frozen points and a no-model baseline sit from the gated tiles; (a) against the gate law on c.
K5  no zero word: the shares and the clocks against randn, by model, with their standard errors; fp16's difference in E87 and E96.
K6  the int8 arm: the rounds, the relation at this session's heat path, the trips, the fine W, what E87's single runs read, the arm with each round's
    first run left out, and where a run's samples below 800 MHz fall: at a process's start, or later.
K7  the heat path: the line on the kinds shared across sessions, against the rest readings; a heat carryover from the previous run.
K8  the rest readings, and P2's early end, which made the pre-launch reading a true rest.
K9  the other things nobody scored here: -0.0, the bf16 grid, the calibrations, the fp16 forward pass (c only; E95 holds the energy claims).
"""
import gzip
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kspeed/e83"))
sys.dont_write_bytecode = True
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/kspeed/e96/predictions.json")))
R87 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e87-real-tensors-speed/results.json")))
R83 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json")))
R80 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e80-kinds-speed/results.json")))
Q = [json.loads(x) for x in open(os.path.join(HERE, "queue.jsonl"))]
C, T, runs, post = R["cells"], P["tiles"], R["runs"], R["posthoc"]
import predict_e83 as PE  # noqa: E402

B_ = {int(k): v for k, v in P["constants"]["B_registered_w"].items()}
rel = PE.Rel(B_)
Wb, sb, Ws, ss = P["relation"]["burst"]["W_star_w"], P["relation"]["burst"]["sigma_w"], P["relation"]["sustained"]["W_star_w"], P["relation"]["sustained"]["sigma_w"]
T975 = P["t975"]


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def by_pass(kind, field="c_w"):
    return {m["rep"]: m[field] for m in runs if m["block"] == "BURST" and m["kind"] == kind}


print("K1  the session's timing")
ev = {x["kind"]: x for x in Q if x["kind"] in ("card_free", "s1_end", "queue_end")}
ss_ = next(x for x in Q if x["kind"] == "session_end" and x["name"] == "s1")
sm = next(x for x in Q if x["kind"] == "session_end" and x["name"] == "smoke")
print(f"    card free at the slot's start, {ev['card_free']['late_s']} s late, waits {ev['card_free']['waits']}")
print(f"    smoke {sm['end']['card_min']} card-min, session {ss_['end']['card_min']} card-min, in all {sm['end']['card_min'] + ss_['end']['card_min']:.1f}; session reason {ss_['end']['reason']!r}, exit {ss_['end']['exit']}")
print(f"    card free {ev['queue_end']['before_slot_end_s']} s before the slot's end; slot stop or SIGTERM used: {ss_['slot_stopped']}")
qs = [json.loads(x) for x in open(os.path.join(HERE, "s1", "queries.jsonl"))]
rr = [json.loads(x) for x in open(os.path.join(HERE, "s1", "runs.jsonl"))]
prev = qs[0]["t_ms"]
du = {"BURST": [], "SUS": []}
for r in rr:
    t = r["queries"]["t_ms"]
    du[r["block"]].append((t - prev) / 1000.0)
    prev = t
print(f"    BURST {len(du['BURST'])} runs, {st.mean(du['BURST']):.1f} s a run, {sum(du['BURST']) / 60:.1f} min (plan 14.5 s, 15.0 min); SUS {len(du['SUS'])} runs, {st.mean(du['SUS']):.1f} s a run, {sum(du['SUS']) / 60:.1f} min (plan 99.7 s)")
g = post["gates"]
print(f"    the gates held {g['burst_held_s']} s before bursts and {g['sus_held_s']} s before sustained runs; not reached: {g['not_reached']}")
print(f"    peaks: die {max(m['die_max'] for m in runs)} C, board {max(max(x[2] for x in m['trace'] if x[2] is not None) for m in runs)} W; launches rc {sorted(set(x for m in runs for x in m['procs_rc']))}; cycles per op {sorted({(m['type'], m['cycles_per_op']) for m in runs})}")
print(f"    config reads {R['config_reads']}")
rr_b = [r for r in rr if r["block"] == "BURST"]
rr_s = [r for r in rr if r["block"] == "SUS"]
print(f"    epoch ms: first burst launch {rr_b[0]['t_first_ms']}, last burst's last launch {rr_b[-1]['t_last_ms']}, first sustained launch {rr_s[0]['t_first_ms']}, last sustained launch {rr_s[-1]['t_last_ms']}; session end {ss_['end']['t_end_ms']}")
print()

print("K2  the bursts")
gated = P["claims_e96"]["S2_gate_buys_speed"]["tiles"]
print("    S2's six gated float tiles, passes:", {k: C[k]["burst_mhz_runs"] for k in gated})
i8 = [k for k in T if T[k]["type"] == "int8"]
print(f"    int8, {len(i8)} tiles: passes at 800.0: {sum(1 for k in i8 for x in C[k]['burst_mhz_runs'] if x == 800)} of {2 * len(i8)}")
pl = [k for k in list(T) + ["fp32/randn", "fp16/randn"] if C[k].get("burst_limit") == "power"]
hs = [(C[k]["burst_mhz_runs"][0] - C[k]["burst_mhz_runs"][1]) / 2 for k in pl]
print(f"    power-limited tiles, {len(pl)}: pass half-spread rms {rms(hs):.1f} MHz, so one pass's 1 sigma {rms(hs) * math.sqrt(2):.1f} (E83 C6's 7.5), a cell's {rms(hs):.1f} (E83's 5.3); largest {max(abs(x) for x in hs) * 2:.1f} MHz between passes, {pl[max(range(len(hs)), key=lambda i: abs(hs[i]))]}")
ds = [m["die_start"] for m in runs if m["block"] == "BURST"]
print(f"    launch die readings {min(ds)}-{max(ds)} C; pass 1 mean {st.mean(m['die_start'] for m in runs if m['block'] == 'BURST' and m['rep'] == 1):.2f}, pass 2 mean {st.mean(m['die_start'] for m in runs if m['block'] == 'BURST' and m['rep'] == 2):.2f}")
print("    like-with-like shares from each pass alone, (c - c_zeros) / (c_ref - c_zeros):")
refk = {"fp32": "fp32/randn", "fp16": "fp16/randn", "int8": "int8/full"}
for k in T:
    t = k.split("/")[0]
    tp, rp, zp = by_pass(k), by_pass(refk[t]), by_pass(f"{t}/zeros")
    a = {p: (tp[p] - zp[p]) / (rp[p] - zp[p]) for p in (1, 2)}
    print(f"      {k:32s} {a[1]:.4f} {a[2]:.4f}  round difference {abs(a[1] - a[2]):.4f}  cell {post['like_with_like_ratios'][k]}")


def p800(kind):
    return {m["rep"]: (m.get("p_ref58_w") or {}).get("800") for m in runs if m["block"] == "BURST" and m["kind"] == kind}


s8 = P["constants"]["s_f"]["800"]
b8 = float(P["constants"]["B_registered_w"]["800"])
print("    int8, from the 800 MHz power alone (each pass referred to 58 C, E64's method); c800 = (P800 - B_800) / s_800; the share (P800 - zeros) / (full - zeros):")
print("    why: c fits all three clocks a burst touched, and a tile that holds 800 MHz has one or two ramp samples at 700, whose reading can sit at 600's: int8/vgg16_fc2's P700 read 36.96 and then 31.65 W, and its c 5.856 and then 4.756, while its P800 read 44.30 and 44.36 W")
zr, fu = p800("int8/zeros"), p800("int8/full")
z8, f8 = st.mean(zr.values()), st.mean(fu.values())
print(f"      int8/zeros P800 {list(zr.values())} c800 {(z8 - b8) / s8:.2f}; int8/full P800 {list(fu.values())} c800 {(f8 - b8) / s8:.2f}")
SHARE8 = {}
for k in i8:
    q = p800(k)
    m8 = st.mean(q.values())
    SHARE8[k] = (m8 - z8) / (f8 - z8)
    g = T[k]["gate_law"]
    law = (g["D_w"] / (T[k]["D_w"] / T[k]["ratio_to_ref_measured_e78"])) if g else None
    print(f"      {k:32s} P800 {list(q.values())} c800 {(m8 - b8) / s8:.2f} (registered c {C[k]['c_w']}, (a) {T[k]['frozen']['c_w']}, law {g['c_w'] if g else None}); share {SHARE8[k]:.3f} ((a) {T[k]['ratio_to_ref_measured_e78']:.3f}, law {f'{law:.3f}' if law else None})")
print()

print("K3  idle resets and late ramps")
print(f"    {post['idle_resets']}")
print("    dips:", [(m["run"], m["a1"]["n_dip"], m["sus_mhz_mean"] if m["block"] == "SUS" else m["burst_mhz"], m["a1"].get("sus_mhz_without")) for m in runs if m["a1"]["n_dip"]])
nl = sum(m["a1"]["n_late"] for m in runs)
print(f"    late ramps (a process's first 800 MHz sample later than 1.2 s with no limit able to hold it): {nl} in {post['idle_resets']['work_processes']} work processes, in {sum(1 for m in runs if m['a1']['n_late'])} runs")
for k in ("fp32/t5small_l0_down", "fp16/t5small_l0_down", "int8/zeros"):
    m = next(x for x in runs if x["block"] == "SUS" and x["kind"] == k)
    t_end, spans = m["work_s"], m.get("proc_spans") or []
    since = [round(x[0] - next((a for a, b in spans if a <= x[0] <= b), x[0]), 1) for x in m["trace"] if t_end - 40.0 <= x[0] <= t_end and x[3] in (600, 700) and any(a <= x[0] <= b for a, b in spans)]
    print(f"    {k}: sustained {m['sus_mhz_mean']} MHz, share at 800 {m['sus_last']['800']}, die {m['sus_die_mean']}, die max {m['die_max']}; {m['a1']['n_late']} late ramps, {m['a1']['n_dip']} dips; reset-free {m['a1']['sus_mhz_without']}; its samples below 800 lie this many s after a process's start: {since}")
print()

print("K4  the gate and the clock")
print(f"    rms by group {json.dumps(post['rms_by_group'])}")
print("    seven gated float tiles: sustained, relation on measured c, difference; one run's 1 sigma on the slope is 15.6 MHz (E83 C3)")
Z = gated + ["fp32/resnet18_l2c1"]
for k in Z:
    c = C[k]
    print(f"      {k:24s} c {c['c_w']:6.2f} burst {c['burst_mhz']:6.1f} rel {c['rel_on_measured_c_burst_mhz']:6.1f} | sus {c['sus_mhz']:6.1f} rel {c['rel_on_measured_c_sus_mhz']:6.1f} diff {c['sus_mhz'] - c['rel_on_measured_c_sus_mhz']:+6.1f} frozen {T[k]['frozen']['sus_mhz']:6.1f} limit {c['sus_limit']} share at 800 {c['sus_last'][0]['800']}")
print("    (a) against the gate law on the measured c, the gated float tiles (int8's c is not fit for this: K2's 800 MHz shares):")
for t in ("float",):
    ks = [k for k in T if T[k].get("gate_law") and (T[k]["type"] == "int8") == (t == "int8")]
    near = sum(1 for k in ks if abs(C[k]["c_w"] - T[k]["gate_law"]["c_w"]) < abs(C[k]["c_w"] - T[k]["frozen"]["c_w"]))
    ma = st.mean(C[k]["c_w"] - T[k]["frozen"]["c_w"] for k in ks)
    mg = st.mean(C[k]["c_w"] - T[k]["gate_law"]["c_w"] for k in ks)
    print(f"      {t}: {len(ks)} tiles, nearer the gate law on {near}; mean miss (a) {ma:+.2f} W, gate law {mg:+.2f} W; rms (a) {rms([C[k]['c_w'] - T[k]['frozen']['c_w'] for k in ks]):.2f}, gate law {rms([C[k]['c_w'] - T[k]['gate_law']['c_w'] for k in ks]):.2f}")
    for k in ks:
        print(f"        {k:24s} measured {C[k]['c_w']:6.2f} (a) {T[k]['frozen']['c_w']:6.2f} law {T[k]['gate_law']['c_w']:6.2f}")
print()

print("K5  no zero word, against same-session randn")
for t, ks in (("fp32", ["fp32/gpt2_l3_mlp_down", "fp32/gpt2_l9_attn_qk", "fp32/bert_l6_up", "fp32/vit_l5_down"]), ("fp16", ["fp16/gpt2_l9_attn_qk", "fp16/bert_l6_up", "fp16/vit_l5_down"])):
    sh = [post["like_with_like_ratios"][k] for k in ks]
    m, s = st.mean(sh), st.stdev(sh)
    d = st.mean(C[k]["burst_mhz"] for k in ks) - C[f"{t}/randn"]["burst_mhz"]
    sig = 5.3 * math.sqrt(1.0 / len(ks) + 1)
    print(f"    {t}: share mean {m:.4f}, between-tile sd {s:.4f}, t against 1.000 {(1 - m) / (s / math.sqrt(len(ks))):.2f} on {len(ks) - 1} df; burst difference {d:+.1f} MHz, 1 sigma {sig:.1f} (E83 C6's 5.3 MHz a cell), so {d / sig:+.1f} sigma")
    print(f"       per tile, burst minus randn: {[round(C[k]['burst_mhz'] - C[f'{t}/randn']['burst_mhz'], 1) for k in ks]}; randn's passes {C[f'{t}/randn']['burst_mhz_runs']}; tiles' passes { {k: C[k]['burst_mhz_runs'] for k in ks} }")
a, b = 7.8, st.mean(C[k]["burst_mhz"] for k in ("fp16/gpt2_l9_attn_qk", "fp16/bert_l6_up", "fp16/vit_l5_down")) - C["fp16/randn"]["burst_mhz"]
sg = 5.3 * math.sqrt(1.0 / 3 + 1)
print(f"    fp16's burst difference in two sessions: E87 {a:+.1f}, E96 {b:+.1f}; their mean {(a + b) / 2:+.1f}, 1 sigma {sg / math.sqrt(2):.1f}; the relation on the measured c's mean gives {rel.f(st.mean(C[k]['c_w'] for k in ('fp16/gpt2_l9_attn_qk', 'fp16/bert_l6_up', 'fp16/vit_l5_down')), Wb, sb)[0] - rel.f(C['fp16/randn']['c_w'], Wb, sb)[0]:+.1f} MHz")
print(f"    the no-model baseline beside S5, over the no-zero-word float tiles: {post['rms_by_group']['no zero word, float']}")
print()

print("K6  the int8 arm")
D = post["arm_rounds_detail"]
ks = ["int8/full", "int8/l0_mlp_up", "int8/l6_mlp_down", "int8/l6_attn_qk"]
for r in sorted(D, key=int):
    print(f"    round {r}: " + "; ".join(f"{k.split('/')[1]} {D[r][k]['mhz']} MHz {D[r][k]['w']} W {D[r][k]['die']} C {D[r][k]['limit']} share {D[r][k]['share800']} start {D[r][k]['die_start']}" for k in ks))
i1 = R["rules"]["E96-I1"]
print(f"    I1 {i1['verdict']}: mean {i1['mean']} MHz, sd {i1['sd']}, half-width {i1['halfwidth']}, [{i1['lo']}, {i1['hi']}]; rounds {i1['rounds']}")
print(f"    I2 {R['rules']['E96-I2']['verdict']}: {R['rules']['E96-I2']['mean']} W [{R['rules']['E96-I2']['lo']}, {R['rules']['E96-I2']['hi']}]; I3 {R['rules']['E96-I3']['verdict']}: {R['rules']['E96-I3']['mean']} C [{R['rules']['E96-I3']['lo']}, {R['rules']['E96-I3']['hi']}]")
print(f"    expected, frozen: {json.dumps({k: v for k, v in P['arm']['expected'].items() if k != 'how'})}")
wadj = post["a_adj_e96"]["W_star_adj_w"]
cs = {k: P["arm"]["tiles"][k]["e87"]["c_w"] for k in P["arm"]["tiles"]}
cs_full = P["arm"]["e87_full"]["c_w"]
for name, W in (("E80's W*", Ws), ("this session's a-adj W*", wadj)):
    a = st.mean(rel.f(c, W, ss)[0] for c in cs.values())
    f = rel.f(cs_full, W, ss)[0]
    print(f"    the relation on E87's c at {name} {W}: real {a:.1f}, full {f:.1f}, difference {a - f:+.1f} MHz; measured real {st.mean(C[k]['sus_mhz'] for k in cs):.1f}, full {C['int8/full']['sus_mhz']}")
print(f"    trips (limit thermal): full {sum(1 for x in C['int8/full']['sus_limit_runs'] if x == 'thermal')} of {len(C['int8/full']['sus_limit_runs'])}; real {sum(1 for k in cs for x in C[k]['sus_limit_runs'] if x == 'thermal')} of {sum(len(C[k]['sus_limit_runs']) for k in cs)}; Fisher's exact one-sided p = {4 / 16:.2f} (the one trip landing on a full run by chance, 4 of 16 runs are full)")
print(f"    pooled one-run sd {post['arm_labelled']['run_sd_pooled_mhz']} MHz, per kind {post['arm_labelled']['run_sd_mhz']}: planning sigma was 5.6-15.6, and 9.2 across sessions")
print(f"    E87's single runs: real {[P['arm']['tiles'][k]['e87']['sus_mhz'] for k in cs]} against full {P['arm']['e87_full']['sus_mhz']}, a difference of {st.mean(P['arm']['tiles'][k]['e87']['sus_mhz'] for k in cs) - P['arm']['e87_full']['sus_mhz']:+.1f} MHz")
print(f"    labelled: {json.dumps({k: {x: v[k].get(x) for x in ('mean', 'lo', 'hi', 'reads') if x in v[k]} for v in [post['arm_labelled']] for k in ('clock_dips_left_out', 'fine_w_at_800', 'clock_pooled_two_way')})}")
print(f"    labelled per tile: {json.dumps({k: {x: v[x] for x in ('mean', 'lo', 'hi', 'reads')} for k, v in post['arm_labelled']['per_tile_clock'].items()})}")
sus_in_order = sorted((m for m in runs if m["block"] == "SUS"), key=lambda m: m["t_first_ms"])
first_in_round = {}
for m in sus_in_order:
    if m.get("round") is not None and m["round"] not in first_in_round:
        first_in_round[m["round"]] = m["kind"]
print(f"    the first run of each round: {first_in_round}; int8 full was never first (the seeded shuffle's chance)")
reals = ["int8/l0_mlp_up", "int8/l6_mlp_down", "int8/l6_attn_qk"]


def tci(ds):
    n = len(ds)
    m, sd = st.mean(ds), st.stdev(ds)
    h = T975[str(n - 1)] * sd / math.sqrt(n)
    return m, m - h, m + h


for field, unit in (("mhz", "MHz"), ("w", "W"), ("die", "C")):
    ds = []
    for r in sorted(D, key=int):
        xs = [D[r][k][field] for k in reals if k != first_in_round[int(r)]]
        ds.append(st.mean(xs) - D[r]["int8/full"][field])
    print(f"    with each round's first run left out, {field}: mean {tci(ds)[0]:+.3f} {unit}, 95% [{tci(ds)[1]:+.3f}, {tci(ds)[2]:+.3f}]; rounds {[round(x, 2) for x in ds]}")


def below_800(m):
    """The last-40-s samples below 800 MHz: within 1.5 s of a process's start (the launch ramp), and later."""
    t_end = m["work_s"]
    spans = m.get("proc_spans") or []
    ramp = later = n = 0
    for x in m["trace"]:
        if not (t_end - 40.0 <= x[0] <= t_end) or x[3] not in (600, 700, 800):
            continue
        sp = next((a for a, b in spans if a <= x[0] <= b), None)
        if sp is None:
            continue
        n += 1
        if x[3] < 800:
            if x[0] - sp <= 1.5:
                ramp += 1
            else:
                later += 1
    return n, ramp, later


print("    where each arm run's samples below 800 MHz fall in the last 40 s (in a process, within 1.5 s of its start, or later):")
for r in sorted(D, key=int):
    row = []
    for k in ["int8/full"] + reals:
        m = next(x for x in runs if x["run"] == D[r][k]["run"])
        n, a_, b_ = below_800(m)
        row.append(f"{k.split('/')[1]} ramp {a_} later {b_} of {n}")
    print(f"      round {r}: " + "; ".join(row))
totals = {}
for k in ["int8/full"] + reals:
    A_ = [below_800(next(x for x in runs if x["run"] == D[r][k]["run"])) for r in D]
    totals[k] = (sum(x[1] for x in A_), sum(x[2] for x in A_), sum(x[0] for x in A_))
print(f"      in all, (ramp, later, samples): {totals}")
print("      a run has launch-ramp samples in the window or next to none: bimodal in the data, not by kind; post hoc, it fits Q132(g)'s heartbeat in the gap between kernels")
later_pct = []
for r in sorted(D, key=int):
    f_ = below_800(next(x for x in runs if x["run"] == D[r]["int8/full"]["run"]))
    rs_ = []
    for k in reals:
        m = next(x for x in runs if x["run"] == D[r][k]["run"])
        n, _, b_ = below_800(m)
        if m["a1"]["n_dip"]:
            b_ = 0 if b_ <= sum(e["samples"] for e in m["a1"]["episodes"] if e["kind"] == "dip") else b_
        rs_.append(100.0 * b_ / n)
    later_pct.append(100.0 * f_[2] / f_[0] - st.mean(rs_))
m_, lo_, hi_ = tci(later_pct)
print(f"    POST HOC, the share of the last 40 s below 800 MHz after the launch ramp (the idle-reset dip left out), full minus the mean of the real tiles: rounds {[round(x, 2) for x in later_pct]} points of share; mean {m_:+.2f}, 95% [{lo_:+.2f}, {hi_:+.2f}]; at 100 MHz a step that is {m_:+.1f} MHz, the arm's whole +{i1['mean']:.1f}")
print()

print("K7  the heat path")
print(f"    die line {json.dumps({k: v for k, v in post['die_line_e96'].items() if not k.endswith('_line')})}")
kinds = P["line"]["kinds"]
kl = P["line"]["k_c_per_w"]


def line_of(res, name):
    out = {}
    for k in kinds:
        xs = [m["sus_die_mean"] - kl * m["sus_w_mean"] for m in res["runs"] if m["block"] == "SUS" and m.get("kind") == k]
        if xs:
            out[k] = st.mean(xs)
    return out


L = {"E80": line_of(R80, "E80"), "E83": line_of(R83, "E83"), "E87": line_of(R87, "E87"), "E96": line_of(R, "E96")}
# rest W and die: the desk lane's table (docs/reports/data/2026-11-01-q132-governor-desk/README.md, "The die lines against the room at rest"), E96's from K8
rest_desk = {"E80": (21.76, 45.58), "E83": (22.03, 46.42), "E87": (22.17, 47.15)}
r96 = post["rest"]["first_launch"]
rest_desk["E96"] = (r96["w"], r96["die_raw"])
base = st.mean(L["E80"].values())
print(f"    the line die - {kl} W over the kinds shared by all four sessions, {kinds}:")
for s in ("E80", "E83", "E87", "E96"):
    m = st.mean(L[s].values())
    print(f"      {s}: {m:.3f} C (per kind { {k: round(v, 2) for k, v in L[s].items()} }), shift from E80 {m - base:+.3f}; rest W {rest_desk[s][0]}, rest die {rest_desk[s][1]}, rest die from E80 {rest_desk[s][1] - rest_desk['E80'][1]:+.2f}")
d96 = st.mean(L["E96"].values()) - base
print(f"    E96 over E80: {d96:+.3f} C of line for {rest_desk['E96'][1] - rest_desk['E80'][1]:+.2f} C of rest die, {d96 / (rest_desk['E96'][1] - rest_desk['E80'][1]):+.2f} C per C; the desk's fit was 0.25-0.35, 95% roughly 0-0.6; a point in E98's night, not a test of it")
sr = [m for m in runs if m["block"] == "SUS"]
sr.sort(key=lambda m: m["t_first_ms"])
x, y = [], []
for a, b in zip(sr, sr[1:]):
    x.append(a["sus_w_mean"])
    y.append(b["line_k"])
mx, my = st.mean(x), st.mean(y)
sxx = sum((u - mx) ** 2 for u in x)
k = sum((u - mx) * (v - my) for u, v in zip(x, y)) / sxx
res = [v - (my + k * (u - mx)) for u, v in zip(x, y)]
se = math.sqrt(sum(q * q for q in res) / (len(x) - 2) / sxx)
print(f"    carryover: a run's line against the previous run's board W, {len(x)} pairs: slope {k:+.4f} C per W, s.e. {se:.4f}; so a run after a zeros run (about 36 W) rather than a full-power one (about 53 W) reads {k * (36 - 53):+.2f} C of line")
sr2 = [m for m in sr if m.get("round") is not None]
print(f"    the first run of each round, die, W, line: {[(m['round'], m['kind'].split('/')[1], m['sus_die_mean'], m['sus_w_mean'], m['line_k']) for m in sr2 if m is next(q for q in sr2 if q['round'] == m['round'])]}")
print(f"    the runs before each round: {[(m['round'], sr[sr.index(next(q for q in sr2 if q['round'] == m['round'])) - 1]['kind'] if sr.index(next(q for q in sr2 if q['round'] == m['round'])) else 'the bursts') for m in sr2 if m is next(q for q in sr2 if q['round'] == m['round'])]}")
print(f"    the line's trend through the session {post['line_at_e98_k']['trend_c_per_min']} C/min; range over runs {min(m['line_k'] for m in sr)} to {max(m['line_k'] for m in sr)}")
print()

print("K8  the rest readings")
for name, v in post["rest"].items():
    print(f"    {name}: {json.dumps(v)}")
E98_P2_END_MS = 1793525874516   # E98's queue on the box, the end of P2 (exit 3: another user logged in; E98's lane reports it, with no login)
print(f"    E98's P2 ended early, at {E98_P2_END_MS} (09:37:54 UTC), so the card was idle {(1793527500058 - E98_P2_END_MS) / 60000.0:.1f} min when this queue took its first snapshot: the 60 s reading is a true rest")
s0 = json.load(open(os.path.join(HERE, "sensors-start.json")))
s1 = json.load(open(os.path.join(HERE, "sensors-end.json")))


def temps(s):
    out = {}
    for chip, d in s.items():
        if isinstance(d, dict):
            for lab, v in d.items():
                if isinstance(v, dict):
                    for kk, x in v.items():
                        if kk.endswith("_input") and "temp" in kk:
                            out[f"{chip.split('-')[0]}:{lab}"] = x
    return out


print(f"    sensors at the start {json.dumps(temps(s0))}")
print(f"    sensors at the end   {json.dumps(temps(s1))}")
rows = [json.loads(x) for x in gzip.open(os.path.join(HERE, "history.jsonl.gz"), "rt")]
print(f"    history rows committed {len(rows)}, from {rows[0]['t']} to {rows[-1]['t']}")
print()

print("K9  the other tiles, c only (E95 holds the energy claims)")
c = C["fp32/vit_l11_down"]
print(f"    -0.0: fp32/vit_l11_down c {c['c_w']}, (a) {T['fp32/vit_l11_down']['frozen']['c_w']}, if the gate took -0.0 {P['constants']['c_zeros_w_real2']['fp32'] + 9.34 / P['constants']['xfer_real2']:.2f} W; share {post['like_with_like_ratios']['fp32/vit_l11_down']}; burst {c['burst_mhz']} sustained {c['sus_mhz']}")
c = C["fp32/t5small_l0_up"]
print(f"    the bf16 grid: fp32/t5small_l0_up c {c['c_w']}, (a) {T['fp32/t5small_l0_up']['frozen']['c_w']}, share {post['like_with_like_ratios']['fp32/t5small_l0_up']}; burst {c['burst_mhz']} sustained {c['sus_mhz']}")
print("    int8 calibration, shares from the 800 MHz power (K2): " + json.dumps({k: round(SHARE8[k], 3) for k in T if T[k]["group"] == "C"}))
L11 = st.mean(p800("int8/gpt2_l11_down_p999").values()) - st.mean(p800("int8/gpt2_l11_down_maxabs").values())
VG = st.mean(p800("int8/vgg16_fc2_asym").values()) - st.mean(p800("int8/vgg16_fc2").values())
print(f"      the lever on GPT-2 layer 11: p99.9 - max-abs {L11:+.2f} W at 800 MHz, {L11 / s8:+.2f} W on c's scale (predicted {T['int8/gpt2_l11_down_p999']['frozen']['c_w'] - T['int8/gpt2_l11_down_maxabs']['frozen']['c_w']:+.2f}); VGG asym - symmetric {VG:+.2f} W at 800 MHz, {VG / s8:+.2f} on c's scale (predicted {T['int8/vgg16_fc2_asym']['frozen']['c_w'] - T['int8/vgg16_fc2']['frozen']['c_w']:+.2f}); every one bursts at 800.0, so none of it moves the burst clock")
c = C["fp16/gpt2_l6_mlp_down_fp16fwd"]
e = R87["cells"]["fp16/l6_mlp_down"]
print(f"    the fp16 forward pass: c {c['c_w']}, share {post['like_with_like_ratios']['fp16/gpt2_l6_mlp_down_fp16fwd']}, burst {c['burst_mhz']} (passes {c['burst_mhz_runs']}); the rounded tile in E87's session c {e['c_w']}, share {R87['posthoc']['like_with_like_ratios']['fp16/l6_mlp_down']}, burst {e['burst_mhz']}")
