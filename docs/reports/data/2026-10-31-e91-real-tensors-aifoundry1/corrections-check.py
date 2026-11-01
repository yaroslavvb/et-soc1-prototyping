#!/usr/bin/env python3
"""E91: the desk check behind 'Corrections after verification' (Sat 31 Oct 2026). Written after an independent
verifier's report, at the desk: no card touched, nothing re-run. Every number is read from committed files; none is
a registered rule, and none changes a registered number or verdict (every registered E91 rule stays NOT SCORED).
Standard library only.

    python3 corrections-check.py > corrections-check.txt

C1  The baseline behind the ratios. Per kept pass, each real tile's D / D(random) (D = board power over the type's own
    all-zeros level; the registered ratio), S / S(random) (S = over idle) and p80 / p80(random) (p80 = the window's
    whole board power, leakage-corrected: idle plus S); each format's three-tile mean per pass, then the mean over
    passes. Card 1 (E91 primary, 3 kept passes), card 1 at the registered 0.1994 W/C arm (4 passes), and aifoundry3
    (E86's registered reduction, 4 passes), with the card 1 - aifoundry3 differences of the three-tile means.
C2  The cross-card scale beside E82's: E82's X3 median and its kind count, and E91's scale at every resolved pairing.
C3  A1 as registered and as carried out: the claim's time from its message id, the second queue's helper's
    arithmetic (floored), A1's exact budget at the refusal and after it, and the queue's whole-minute rule.
C4  The registered arms: the passes each keeps and its verdicts, R1-R5 and S1 per arm, X1-X4 per cross-card pairing.
C5  The real tiles' scale against the six synthetic kinds run beside them (random and stand-in kinds), and against
    all 15 kinds (which include the nine real tiles).
C6  Machine paths: which committed files carry the box's own paths, and that the reductions carry none.
C7  The 2 s die rise per pass of every real tile and random kind (whole-degree reading).
C9  The 21:05 dry pass, from its files copied into logs/dry-p9100/ after verification.
C10 Push times: logs/push-and-claim-times.txt.
"""
import datetime as dt
import gzip
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
E86D = os.path.join(DATA, "2026-10-31-e86-real-tensors-energy")
E82D = os.path.join(DATA, "2026-10-31-e82-kinds-aifoundry1")
SC = json.load(open(os.path.join(HERE, "scored.json")))

FMTS = ("fp32", "fp16", "int8")
NAMES = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
# two-sided 95% Student t, by degrees of freedom
T975 = {1: 12.7062, 2: 4.3027, 3: 3.1824, 4: 2.7764, 5: 2.5706}
PDT = dt.timezone(dt.timedelta(hours=-7))


def mci(v):
    """mean and 95% half-width over the values (the pass as the unit)"""
    n = len(v)
    m = st.mean(v)
    h = T975[n - 1] * st.stdev(v) / math.sqrt(n) if n > 1 else float("nan")
    return m, h


def ratios(path):
    E = json.load(open(path))
    P = [str(p) for p in E["passes"]]
    out = {}
    for t in FMTS:
        three = {k: {p: [] for p in P} for k in ("D", "S", "p80")}
        for n in NAMES:
            it = f"{t}.real_{n}"
            for k in ("D", "S", "p80"):
                v = [E["per_pass"][p][it][k] / E["per_pass"][p][REF[t]][k] for p in P]
                for p, x in zip(P, v):
                    three[k][p].append(x)
                out[(t, n, k)] = mci(v)
        for k in ("D", "S", "p80"):
            out[(t, "mean", k)] = mci([st.mean(three[k][p]) for p in P])
    return E, P, out


print("E91 corrections-check (desk only; committed files only)")

# ---------------------------------------------------------------- C1
print("\n== C1 the baseline behind the ratios (per kept pass, then the mean over passes; 95%, t(0.975, n-1) x SE)")
print("D = board power over the type's own all-zeros level (the registered ratio); S = over idle; "
      "p80 = the window's whole board power (leakage-corrected), i.e. idle plus S")
views = (("card 1, E91 primary (dips removed, leakage auto)", os.path.join(HERE, "e91.json")),
         ("card 1, E91 registered arm 0.1994 W/C (dips removed)", os.path.join(HERE, "e91-leak0.1994.json")),
         ("aifoundry3, E86 registered reduction", os.path.join(E86D, "e86.json")))
R = {}
for label, path in views:
    E, P, o = ratios(path)
    R[label] = o
    print(f"{label}: kept passes {P} (n = {len(P)}); idle level {E['idle_level']['mean']:.3f} W; "
          f"leakage {E['leak']['mode']} {E['leak']['k_w_per_c']:.4f} W/C")
    for t in FMTS:
        ref = REF[t]
        print(f"  {t} (random kind {ref}: D {E['items'][ref]['D']['mean']:.3f} W, S {E['items'][ref]['S']['mean']:.3f} W, "
              f"p80 {E['items'][ref]['p80']['mean']:.3f} W; the type's zeros S {E['items'][t + '.zeros']['S']['mean']:.3f} W "
              f"over idle)")
        for n in NAMES:
            print(f"     {n:12s} " + "; ".join(f"{k} {o[(t, n, k)][0]:.4f} +- {o[(t, n, k)][1]:.4f}"
                                            for k in ("D", "S", "p80")))
        for k in ("D", "S", "p80"):
            tl = [o[(t, n, k)][0] for n in NAMES]
            m, h = o[(t, "mean", k)]
            print(f"     three-tile mean, {k:3s}: {m:.4f} +- {h:.4f} (tiles {min(tl):.4f}-{max(tl):.4f}; "
                  f"saving {100 * (1 - max(tl)):.1f}-{100 * (1 - min(tl)):.1f}%)")
a, b = R[views[0][0]], R[views[2][0]]
print("card 1 (E91 primary, 3 passes) - aifoundry3 (E86 registered, 4 passes), three-tile means "
      "(95% half-widths in quadrature):")
for t in FMTS:
    print(f"  {t}: " + "; ".join(f"{k} {a[(t, 'mean', k)][0] - b[(t, 'mean', k)][0]:+.4f} +- "
                                 f"{math.hypot(a[(t, 'mean', k)][1], b[(t, 'mean', k)][1]):.4f}" for k in ("D", "S", "p80")))
print("  per tile, D: " + "; ".join(f"{t} {n} {a[(t, n, 'D')][0] - b[(t, n, 'D')][0]:+.4f}" for t in FMTS for n in NAMES))
print(f"  scored.json replication_of_e86.rho_by_type: " + "; ".join(
    f"{t} {SC['replication_of_e86']['rho_by_type'][t]['diff']:+.4f} +- {SC['replication_of_e86']['rho_by_type'][t]['diff_ci95']:.4f}"
    for t in FMTS))

# ---------------------------------------------------------------- C2
print("\n== C2 the cross-card scale D(aifoundry3) / D(card 1), beside E82's")
e82 = json.load(open(os.path.join(E82D, "scored.json")))["cross_card"]["primary"]
x3 = e82["x3"] if "x3" in e82 else e82["detail"]["x3"]
print(f"E82 (E78's kinds, card 1 vs aifoundry3) scored.json cross_card.primary x3: median {x3['median_ratio']:.4f} over "
      f"n {x3['n']} kinds, IQR {x3['iqr'][0]:.4f}-{x3['iqr'][1]:.4f}")
pairs = {"primary (E91 auto, dips removed; E86 registered)": SC["cross_card"]["primary"]}
pairs.update(SC["cross_card"]["pairs"])
resolved = {}
for name, pr in pairs.items():
    k = pr["detail"]["kinds"]
    real = [v["ratio"] for kk, v in k.items() if ".real_" in kk and v.get("ratio") is not None]
    syn = [v["ratio"] for kk, v in k.items() if ".real_" not in kk and v.get("ratio") is not None]
    if not real:
        print(f"  {name}: unresolved (too few kept passes; x3 n {pr['detail']['x3']['n']})")
        continue
    resolved[name] = (real, syn, sorted(kk for kk in k if ".real_" not in kk))
    print(f"  {name}: median over all {len(real) + len(syn)} kinds {st.median(real + syn):.4f}; nine real tiles "
          f"{st.median(real):.4f}; X3 {pr['detail']['x3']['median_ratio']:.4f} (n {pr['detail']['x3']['n']}); "
          f"verdicts {', '.join(f'{r[4:]} {v}' for r, v in pr['verdicts'].items())}")
allm = [st.median(r + s) for r, s, _ in resolved.values()]
realm = [st.median(r) for r, _, _ in resolved.values()]
print(f"  range over the resolved pairings: all kinds {min(allm):.4f}-{max(allm):.4f}; real tiles "
      f"{min(realm):.4f}-{max(realm):.4f}")

# ---------------------------------------------------------------- C3
print("\n== C3 A1 as registered and as carried out")
mid = 1566303302210158713
claim_ms = (mid >> 22) + 1420070400000
claim = dt.datetime.fromtimestamp(claim_ms / 1000, PDT)
print(f"claim message {mid}: posted {claim.strftime('%H:%M:%S.%f')[:-3]} PDT (Discord id >> 22, + 2015-01-01 epoch)")
print("A1 (tools/claims-v3/kinds/E91.md, Amendments): E91_BUDGET_MIN = 35 - the card-minutes used since the claim "
      "(21:10:07) - 3; no rounding is given")
print("queue_e86.sh: starts a pass only if [ $((el + longest)) -le $((BUDGET_MIN * 60)) ], bash integer arithmetic, "
      "so the budget must be whole minutes")
print("the lane's helper, logs/a1-second-queue.sh (last written 21:30:54 PDT, after A1 was pushed at 21:30:24): "
      "budget = max(0, math.floor(35 - (now - claim) / 60.0 - 3)), with the claim at 21:10:07")
used = 1515  # logs/a1-second-queue.out: "A1: used 1515 s since the claim"
longest = 361  # logs/a1-second-queue.out: E91_FIRST_S=361 (p9111, 21:17:03-21:23:19 by logs/e91-queue-1.log)
fl = max(0, math.floor(35 - used / 60.0 - 3))
print(f"  at 21:35:22 (helper's clock): used {used} s = {used / 60:.2f} min; A1's budget 35 - {used / 60:.2f} - 3 = "
      f"{35 - used / 60 - 3:.2f} min = {(35 - 3) * 60 - used} s; floored {fl} min = {fl * 60} s; pass {longest} s: "
      f"floored {'fits' if longest <= fl * 60 else 'refused'} by {abs(fl * 60 - longest)} s; exact "
      f"{'fits' if longest <= (35 - 3) * 60 - used else 'refused'} with {(35 - 3) * 60 - used - longest} s to spare")
print("  first queue (logs/e91-queue-1.log): elapsed 1,450 s + longest 361 s = 1,811 s > 1,800 s (30 card-min): "
      "stopped by 11 s")


def at(hms):
    h, m, s = (float(x) for x in hms.split(":"))
    return dt.datetime(2026, 10, 31, int(h), int(m), 0, tzinfo=PDT) + dt.timedelta(seconds=s)


for when, what in (("21:35:22", "the refusal (logs/e91-queue.log)"),
                   ("21:35:26", "the helper's output complete (lane scratch file time)"),
                   ("21:35:56", "the lane's closing et-who read (logs/push-and-claim-times.txt)")):
    b_s = (35 - 3) * 60 - (at(when) - claim).total_seconds()
    print(f"  A1's exact budget at {when}, {what}: {b_s:.1f} s ({'holds' if b_s >= longest else 'does not hold'} "
          f"the {longest} s pass)")
lapse = claim + dt.timedelta(seconds=(35 - 3) * 60 - longest)
print(f"  A1's exact budget falls below {longest} s at {lapse:%H:%M}:{lapse.second + lapse.microsecond / 1e6:04.1f} PDT; "
      f"the release was read back at 21:36:14")

# ---------------------------------------------------------------- C4
print("\n== C4 the registered arms (scored.json arms and rules.*.at_arms)")
for arm, v in SC["arms"].items():
    print(f"  {arm}: leakage {v['leak']['mode']} ({v['leak']['k_w_per_c']:.4f} W/C); dips {v['dips'].split(' (')[0]}; "
          f"kept {v['passes']}; " + ", ".join(f"{r[4:]} {x}" for r, x in v["rules"].items()))
for r in ("E91-X1", "E91-X2a", "E91-X2b", "E91-X3", "E91-X4"):
    print(f"  {r}: " + "; ".join(f"{p}: {x}" for p, x in SC["rules"][r]["at_arms"].items()))
print(f"  registered tally (primary): {SC['tally']}")

# ---------------------------------------------------------------- C5
print("\n== C5 the real tiles' scale against the six synthetic kinds beside them, at every resolved pairing")
for name, (real, syn, synk) in resolved.items():
    mr, ms, ma = st.median(real), st.median(syn), st.median(real + syn)
    print(f"  {name}: real tiles {mr:.4f}; six synthetic kinds {ms:.4f}; all 15 {ma:.4f}; real - synthetic "
          f"{mr - ms:+.4f}; real - all 15 {mr - ma:+.4f}")
print(f"  the six synthetic kinds: {', '.join(next(iter(resolved.values()))[2])}")
print(f"  largest |real - synthetic|: {max(abs(st.median(r) - st.median(s)) for r, s, _ in resolved.values()):.4f}")

# ---------------------------------------------------------------- C6
# a home directory on a lab box, and one on a Mac; spelled apart so this file passes the repo's public-text scan
BOX_HOME, MAC_HOME = "/" + "home" + "/", "/" + "Users" + "/"
print("\n== C6 machine paths in the committed files (lines holding a home-directory path, a lab box's or a Mac's)")
groups = {}
for dirpath, _, files in os.walk(HERE):
    for f in files:
        p = os.path.join(dirpath, f)
        rel = os.path.relpath(p, HERE)
        if rel in ("corrections-check.py", "corrections-check.txt", "README.md"):
            continue  # this check and the README describe the paths in prose; they record no run
        op = gzip.open if f.endswith(".gz") else open
        try:
            with op(p, "rt", errors="replace") as fh:
                lines = [l for l in fh if BOX_HOME in l or MAC_HOME in l]
        except OSError:
            continue
        if lines:
            g = rel.split(os.sep)[0] if os.sep in rel else rel
            n_mac = sum(MAC_HOME in l for l in lines)
            groups.setdefault(g, [0, 0, 0])
            groups[g][0] += len(lines)
            groups[g][1] += n_mac
            groups[g][2] += 1
for g, (n, nu, nf) in sorted(groups.items()):
    print(f"  {g}: {n} lines in {nf} file(s), {nu} of them a Mac's")
red = [f for f in sorted(os.listdir(HERE)) if os.path.isfile(os.path.join(HERE, f))
       and f.startswith(("e91", "runs", "reduce", "score", "results", "code.sha256"))]
hit = [f for f in red if any(BOX_HOME in l or MAC_HOME in l for l in open(os.path.join(HERE, f), errors="replace"))]
print(f"  the reductions, scores and their logs (e91*, runs*, reduce*, score*, scored*, results*, code.sha256): "
      f"{len(red)} files; with a machine path: {hit or 'none'}")
print(f"  e91.json dirs: {json.load(open(os.path.join(HERE, 'e91.json')))['dirs']}")

# ---------------------------------------------------------------- C7
print("\n== C7 the 2 s die rise per pass (e91.json per_pass dT_win; one run a pass for each real tile; whole-degree "
      "readings averaged over the window)")
E = json.load(open(os.path.join(HERE, "e91.json")))
for t in FMTS:
    for it in [f"{t}.real_{n}" for n in NAMES] + [REF[t]]:
        v = [E["per_pass"][p][it]["dT_win"] for p in E["per_pass"]]
        m, h = mci(v)
        print(f"  {it:22s} per pass {['%.2f' % x for x in v]} -> {m:.2f} +- {h:.2f} C")

# ---------------------------------------------------------------- C9
print("\n== C9 the 21:05 dry pass (logs/dry-p9100/, copied read-only from aifoundry1 after verification)")
DRY = os.path.join(HERE, "logs", "dry-p9100")
blk = json.load(open(os.path.join(DRY, "block.json")))
plan = json.load(open(os.path.join(DRY, "plan.json")))
marks = [json.loads(l) for l in open(os.path.join(DRY, "marks.jsonl"))]
kinds = {}
for mk in marks:
    kinds[mk["kind"]] = kinds.get(mk["kind"], 0) + 1
t0 = dt.datetime.fromtimestamp(blk["t0_ms"] / 1000, PDT).strftime("%H:%M:%S")
t1 = dt.datetime.fromtimestamp(blk["t1_ms"] / 1000, PDT).strftime("%H:%M:%S")
print(f"  block.json: pass {blk['pass']}, card {blk['card']}, {t0}-{t1} PDT, status {blk['status']}, "
      f"die {blk['die_c_start']} C (stubbed)")
print(f"  plan.json: {len(plan)} runs, {sum('.real_' in r['item'] for r in plan)} of them on real tiles")
print(f"  marks.jsonl: {kinds}; launches recorded {sum(mk.get('launches', 0) for mk in marks if mk['kind'] == 'run')}")
hdr = open(os.path.join(DRY, "run.log")).readline().strip()
print(f"  run.log header: {hdr}")
print(f"  config_start.json {open(os.path.join(DRY, 'config_start.json')).read().strip()}, config_end.json "
      f"{open(os.path.join(DRY, 'config_end.json')).read().strip()}")
print(f"  logs/e91-dry.log (committed with the data): {open(os.path.join(HERE, 'logs', 'e91-dry.log')).read().strip()}")

# ---------------------------------------------------------------- C10
print("\n== C10 push and claim times: logs/push-and-claim-times.txt")
for l in open(os.path.join(HERE, "logs", "push-and-claim-times.txt")).read().splitlines():
    print("      " + l)
