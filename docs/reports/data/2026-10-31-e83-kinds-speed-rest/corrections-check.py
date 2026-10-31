#!/usr/bin/env python3
"""E83: the desk check behind the corrections after verification (Sat 31 Oct 2026). Desk only: it reads the committed
session and the committed reductions, and prints every number the README's "Corrections after verification" section
quotes. Nothing registered is recomputed differently: the per-sample conventions are reduce_hpl.py's (E64's), and the
registered numbers it starts from are read from results.json, which reduce_e83.py reproduces byte for byte.

    cd docs/reports/data/2026-10-31-e83-kinds-speed-rest
    python3 corrections-check.py > corrections-check.txt

Inputs: results.json, s1/runs.jsonl, s1/marks.jsonl, smoke/marks.jsonl, s1/launches.jsonl.gz, s1/tel/*.jsonl.gz,
s1/e83.json, s1/kspeed.json, s1/session.json, the frozen predictions.json, E80's results.json and posthoc-idle.json, and
the code files whose sha256 C1 checks. Python 3, no third-party modules.
"""
import datetime
import gzip
import hashlib
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E80D = os.path.join(HERE, "..", "2026-10-31-e80-kinds-speed")
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "hpl"))
import surface_hpl as SH  # noqa: E402  (frozen; only its constants S, V, T_REF, LEAK_W_PER_C are read)

R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(REPO, "tools", "claims-v3", "kspeed", "e83", "predictions.json")))
E80 = json.load(open(os.path.join(E80D, "results.json")))
E80PH = json.load(open(os.path.join(E80D, "posthoc-idle.json")))
C = R["cells"]
RUNS = {m["run"]: m for m in R["runs"]}
ROWS = [json.loads(ln) for ln in open(os.path.join(HERE, "s1", "runs.jsonl"))]
NEW = [k for k, c in C.items() if c["role"] == "e83"]
SQ2 = math.sqrt(2.0)


def pdt(ms):
    t = datetime.datetime.fromtimestamp(ms / 1000.0, datetime.timezone.utc) - datetime.timedelta(hours=7)
    return t.strftime("%H:%M:%S.%f")[:-3]


def ms_of(hms):
    """14:06:39 PDT on Sat 31 Oct 2026 -> epoch ms."""
    h, m, s = (int(x) for x in hms.split(":"))
    return int(datetime.datetime(2026, 10, 31, h + 7, m, s, tzinfo=datetime.timezone.utc).timestamp() * 1000)


def jl_gz(path):
    out = []
    with gzip.open(path, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def tel(run):
    """reduce_hpl.tel's tuple: (t_ms, die = minion-shire mean, hottest minion-shire sensor, board W, minion MHz)."""
    s = []
    for d in jl_gz(os.path.join(HERE, "s1", "tel", run + ".jsonl.gz")):
        try:
            ms = d.get("temp_c", {}).get("minshire") or [None, None, None]
            s.append((int(d["t_ms"]), ms[0], ms[2], d.get("board_w"), d.get("mhz", {}).get("minion")))
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    return sorted(s)


LAUNCH = {}
for L in jl_gz(os.path.join(HERE, "s1", "launches.jsonl.gz")):
    LAUNCH.setdefault(L["run"], []).append(L)


def windows(run):
    """reduce_hpl.run_metrics' spans: the work processes, the kernel launches inside them, t0 and t1."""
    work = [p for p in LAUNCH.get(run, []) if p.get("role") == "work"]
    kw = [(k["t_start_ms"], k["t_end_ms"]) for p in work for k in p.get("sparsity", [])
          if k.get("t_start_ms") and k.get("t_end_ms")]
    starts = [p["t_start_ms"] for p in work]
    t0 = min(p["t_start_ms"] for p in work)
    t1 = max(p["t_end_ms"] for p in work)
    return starts, kw, t0, t1


def rms(xs):
    xs = [x for x in xs if x is not None]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def sha(path):
    return hashlib.sha256(open(os.path.join(REPO, path), "rb").read()).hexdigest()


def hdr(s):
    print("\n" + "=" * 8 + " " + s)


def t2_two_sided_p(t):
    """Student's t with 2 degrees of freedom: two-sided p = 1 - |t| / sqrt(t^2 + 2)."""
    return 1.0 - abs(t) / math.sqrt(t * t + 2.0)


print("E83 corrections-check: every number quoted in the README's 'Corrections after verification', from the committed")
print("files. Times are PDT, Sat 31 Oct 2026.")

# ------------------------------------------------------------------------------------------------------------------
hdr("C1. The two interim looks: which runs were done, which run was running, and what the copy overlapped")
# The two pulls are the lane's own record (its command log; not a committed file): each command copied the box's
# s1/ directory with rsync over ssh and ran reduce_e83.py on the copy in the lane's scratch on the Intel.
PULLS = [("first look", "14:06:39"), ("second look", "14:26:17")]
MK = [json.loads(ln) for ln in open(os.path.join(HERE, "s1", "marks.jsonl"))]
SPAN = list(zip([m["t_ms"] for m in MK if m["kind"] == "sampler_start"],
                [m["t_ms"] for m in MK if m["kind"] == "sampler_stop"]))   # one recording span per run, in run order
for name, hms in PULLS:
    t = ms_of(hms)
    done = [r for r in ROWS if (r.get("queries") or {}).get("t_ms", r["t_last_ms"]) < t]
    nb = sum(1 for r in done if r["block"] == "BURST")
    ns = sum(1 for r in done if r["block"] == "SUS")
    cur = [r for r, (a, b) in zip(ROWS, SPAN) if a <= t <= b]
    nxt = next(((r, a) for r, (a, b) in zip(ROWS, SPAN) if a > t), None)
    print(f"{name}: copy issued {hms}; runs finished before it: {len(done)} ({nb} BURST, {ns} SUS); the next run's "
          f"sampler started {pdt(nxt[1]) if nxt else '-'} ({nxt[0]['run'] if nxt else '-'})")
    for r in cur:
        starts, kw, t0, t1 = windows(r["run"])
        tl = t1 - 40000
        inside = tl <= t <= t1
        print(f"  running: {r['run']} work {pdt(t0)}-{pdt(t1)}; its last-40-s window {pdt(tl)}-{pdt(t1)}; "
              f"copy issued {'INSIDE' if inside else 'outside'} it")
        s = tel(r["run"])
        win = [x for x in s if x[0] >= tl and any(a <= x[0] <= b for a, b in kw)]
        near = [x for x in win if t <= x[0] <= t + 10000]
        rest = [x for x in win if not (t <= x[0] <= t + 10000)]
        mhz = lambda xs: st.mean([x[4] for x in xs]) if xs else float("nan")  # noqa: E731
        w = lambda xs: st.mean([x[3] for x in xs]) if xs else float("nan")  # noqa: E731
        die = lambda xs: st.mean([x[1] for x in xs]) if xs else float("nan")  # noqa: E731
        print(f"    in-kernel readings in the window: {len(win)}; in the 10 s from the copy: {len(near)}")
        print(f"    the 10 s from the copy: {mhz(near):.1f} MHz, {w(near):.2f} W, die {die(near):.2f} C | the rest of "
              f"the window: {mhz(rest):.1f} MHz, {w(rest):.2f} W, die {die(rest):.2f} C")
        c = C[RUNS[r["run"]]["kind"]]
        print(f"    registered sustained cell: {c.get('sus_mhz')} MHz, {c.get('sus_w')} W, {c.get('sus_die')} C, limit "
              f"{c.get('sus_limit')}; without those 10 s (labelled, not a re-score): {mhz(rest):.1f} MHz")
        print(f"    the 10 s from the copy, readings (s after the copy, MHz, W, die): "
              + ", ".join(f"({(x[0] - t) / 1000:.1f}, {x[4]}, {x[3]:.1f}, {x[1]})" for x in near[::5]))
print("Code that ran = code registered (sha256 of the file now, against the hash the session recorded or the hash at "
      "the pre-registration c253bd1c):")
E83J = json.load(open(os.path.join(HERE, "s1", "e83.json")))
KSJ = json.load(open(os.path.join(HERE, "s1", "kspeed.json")))
SESS = json.load(open(os.path.join(HERE, "s1", "session.json")))
AT_C253 = {  # git show c253bd1c:<path> | sha256sum
    "tools/claims-v3/kspeed/e83/reduce_e83.py": "b1bfb65bae3fe557b7d866a55b7597fae6eab92313994c1c84664fc6b2db2349",
    "tools/claims-v3/kspeed/reduce_kspeed.py": "10fee8c153a2af4550e0ae40cda521683ab8245413a7af6f9649f381af71eca2",
    "tools/claims-v3/kspeed/posthoc_idle.py": "f25e2f717acd4dbf647edd6d249bfc45ae3ea7486ada064f88fc31188a27ec8a",
    "tools/claims-v3/hpl/reduce_hpl.py": "e49b6c1b39d742043a73447f7b4f67c677bd9b73c9902664261113c5c241ed00",
}
checks = [("tools/claims-v3/kspeed/e83/run_e83.py", E83J["wrapper_sha256"], "s1/e83.json wrapper_sha256"),
          ("tools/claims-v3/kspeed/e83/predictions.json", E83J["predictions_sha256"], "s1/e83.json predictions_sha256"),
          ("tools/claims-v3/kspeed/run_kspeed.py", E83J["run_kspeed_sha256"], "s1/e83.json run_kspeed_sha256"),
          ("tools/claims-v3/kspeed/e83/protocol.json", KSJ["protocol_sha256"], "s1/kspeed.json protocol_sha256"),
          ("tools/claims-v3/hpl/run_hpl.py", SESS["sha256"]["runner"], "s1/session.json sha256.runner")]
checks += [(p, h, "c253bd1c") for p, h in AT_C253.items()]
for p, h, src in checks:
    print(f"  {p}: {'same' if sha(p) == h else 'DIFFERENT'} as {src} ({h[:12]})")
print(f"  session git_head {SESS['git_head'][:8]}, runs planned {len(SESS['runs_planned'])}, runs done {len(ROWS)}, "
      f"in the planned order: {[r['run'] for r in ROWS] == SESS['runs_planned']}")

# ------------------------------------------------------------------------------------------------------------------
hdr("C2. What the switching term c is")
B = {int(k): v for k, v in P["constants"]["B_registered_w"].items()}
print(f"c is fitted per burst run as P_f = B_f + c s_f over the burst's 600/700/800 MHz board powers, each referred to a "
      f"{SH.T_REF:g} C die with {SH.LEAK_W_PER_C} W/C (reduce_kspeed.burst_extra; E64's method).")
print(f"  B_f (E64's registered baseline, not idle): " + ", ".join(f"{f} MHz {B[f]:.2f} W" for f in sorted(B)))
print(f"  s_f = (V_f / 0.517)^2 f / 600: " + ", ".join(f"{f} MHz {SH.S[f]:.3f} (V {SH.V[f]} V)" for f in sorted(SH.S)))
for k in ("fp32/zeros", "fp16/zeros", "int8/zeros"):
    print(f"  {k}: c {C[k]['c_w']} W on that baseline")
for k in ("fp32/randn", "fp32/ones", "fp32/a_zeros_b_randn"):
    c = C[k]["c_w"]
    print(f"  {k}: c {c} W; the same data's switching term at 700 / 800 MHz: {c * SH.S[700]:.2f} / {c * SH.S[800]:.2f} W")

# ------------------------------------------------------------------------------------------------------------------
hdr("C3. The uncertainty of one run, and of a burst cell")
pairs = []
for src, cells in (("E80", E80["cells"]), ("E83", C)):
    for k, c in cells.items():
        r = c.get("sus_mhz_runs") or []
        if len(r) == 2:
            pairs.append((src, k, r, c.get("sus_w_runs"), c.get("sus_die_runs"), c.get("sus_limit_runs")))
print("sustained replicate pairs (E80's three and E83's four): kind, runs, half-spread |x1 - x2| / 2, class")
slope, clamp = [], []
for src, k, r, wr, dr, lr in pairs:
    m = (r[0] + r[1]) / 2
    h = abs(r[0] - r[1]) / 2
    cls = "clamp" if (m <= 615 or m >= 790) else "slope"
    (clamp if cls == "clamp" else slope).append(h)
    print(f"  {src} {k:16s} {r[0]:6.1f} / {r[1]:6.1f}  mean {m:6.1f}  half-spread {h:5.2f}  {cls}  (limits {lr})")
hs, hc = rms(slope), rms(clamp)
print(f"class rule (the README's): at or near a clamp if the pair's mean is <= 615 or >= 790 MHz, else on the slope")
print(f"  slope: n {len(slope)}, rms half-spread {hs:.2f} MHz -> one run's sigma = sqrt(2) x {hs:.2f} = {SQ2 * hs:.1f} MHz")
print(f"  clamp: n {len(clamp)}, rms half-spread {hc:.2f} MHz -> one run's sigma = sqrt(2) x {hc:.2f} = {SQ2 * hc:.1f} MHz")
print("  (a pair's half-spread is the deviation of each run from the pair's mean: E[(x1 - x2)^2 / 4] = sigma^2 / 2)")
dw = [abs(p[3][0] - p[3][1]) for p in pairs]
dd = [abs(p[4][0] - p[4][1]) for p in pairs]
sw = math.sqrt(sum(x * x for x in dw) / (2 * len(dw)))
sd_ = math.sqrt(sum(x * x for x in dd) / (2 * len(dd)))
print(f"  board W over all {len(dw)} pairs: one run's sigma {sw:.2f} W; die C: {sd_:.2f} C (sqrt(sum d^2 / 2n))")
# the S1 residual on the slope cells, as a cross-check (out of sample)
sl = [k for k in NEW if len(C[k]["sus_mhz_runs"]) == 1 and C[k]["sus_limit"] == "thermal" and C[k]["sus_mhz"] > 615]
res = [C[k]["sus_mhz"] - C[k]["rel_on_measured_c_sus_mhz"] for k in sl]
print(f"cross-check: the relation on measured c (S1) over the {len(sl)} single-run slope cells "
      f"({', '.join(sl)}): residual rms {rms(res):.1f} MHz (noise and model error together)")
# burst passes
lim = [k for k in C if C[k].get("burst_limit") == "power"]
rf = [k for k in lim if not C[k].get("idle_resets_burst")]
d = [C[k]["burst_mhz_runs"][1] - C[k]["burst_mhz_runs"][0] for k in rf]
md, sdd = st.mean(d), st.stdev(d)
spass = sdd / SQ2
print(f"burst: the {len(lim)} power-limited kinds; {len(rf)} without an idle reset in either pass "
      f"({len(lim) - len(rf)} with: {[k for k in lim if k not in rf]})")
print(f"  pass 2 - pass 1 over those {len(rf)}: mean {md:+.1f} MHz, sd {sdd:.1f} MHz, t {md / (sdd / math.sqrt(len(d))):+.2f} "
      f"({len(d) - 1} df); one pass's random part sigma = sd / sqrt(2) = {spass:.1f} MHz; a two-pass cell mean "
      f"{spass / SQ2:.1f} MHz; a difference of two cell means {spass:.1f} MHz (the pass-order offset cancels: every cell "
      f"has one pass in each round)")
g = C["fp32/fp16grid"]
a = C["fp32/randn"]
db = g["burst_mhz"] - a["burst_mhz"]
ds = g["sus_mhz"] - a["sus_mhz"]
sig_s = math.sqrt((SQ2 * hs) ** 2 + (SQ2 * hc) ** 2)
print(f"fp32 fp16grid against E83's fp32 randn anchor: burst {g['burst_mhz']} - {a['burst_mhz']} = {db:+.1f} MHz "
      f"(1 sigma {spass:.1f}); sustained {g['sus_mhz']} - {a['sus_mhz']} = {ds:+.1f} MHz (one run on the slope against "
      f"one at the 600 MHz clamp: 1 sigma sqrt({SQ2 * hs:.1f}^2 + {SQ2 * hc:.1f}^2) = {sig_s:.1f})")

# ------------------------------------------------------------------------------------------------------------------
hdr("C4. The rms figures with and without the cells pinned at 800 MHz")
bk = [k for k in NEW if C[k]["pred_a"]["burst_mhz"] < 799]
sk = [k for k in NEW if C[k]["pred_a"]["sus_mhz"] < 799]
print(f"kinds (a) puts below 799 MHz: burst {len(bk)} of {len(NEW)} ({len(NEW) - len(bk)} at the 800 MHz clamp), "
      f"sustained {len(sk)} of {len(NEW)} ({len(NEW) - len(sk)} at the clamp)")


def r_b(keys, f):
    return rms([C[k]["burst_mhz"] - f(C[k]) for k in keys])


def r_s(keys, f):
    return rms([C[k]["sus_mhz"] - f(C[k]) for k in keys])


fa_b = lambda c: c["pred_a"]["burst_mhz"]  # noqa: E731
fb_b = lambda c: c["pred_b"]["burst_mhz_4_12s"]  # noqa: E731
fr_b = lambda c: c["rel_on_measured_c_burst_mhz"]  # noqa: E731
fa_s = lambda c: c["pred_a"]["sus_mhz"]  # noqa: E731
fb_s = lambda c: c["pred_b"]["sus_mhz_40_80s"]  # noqa: E731
fr_s = lambda c: c["rel_on_measured_c_sus_mhz"]  # noqa: E731
print(f"{'':34s} {'all 33':>8s} {'below 799':>10s} {'at 800':>8s}   (registered value in results.json)")
for name, f, keys, reg in (("burst (a) [E83-R1]", fa_b, bk, R["rules"]["E83-R1"].get("rms_mhz")),
                           ("burst (b) Q130(c) 4-12 s", fb_b, bk, None),
                           ("burst, relation on measured c [S1]", fr_b, bk, None)):
    at = [k for k in NEW if k not in keys]
    print(f"  {name:32s} {r_b(NEW, f):8.2f} {r_b(keys, f):10.2f} {r_b(at, f):8.2f}   {reg}")
for name, f, keys, reg in (("sustained (a) [E83-R3]", fa_s, sk, R["rules"]["E83-R3"].get("rms_mhz")),
                           ("sustained (b) Q130(c) [E83-R4]", fb_s, sk, None),
                           ("sustained, relation on c [S1]", fr_s, sk, None)):
    at = [k for k in NEW if k not in keys]
    print(f"  {name:32s} {r_s(NEW, f):8.2f} {r_s(keys, f):10.2f} {r_s(at, f):8.2f}   {reg}")
print("  registered S1:", {k: v for k, v in R["rules"]["E83-S1"].items() if k != "rows"})
print("  registered R1 / R3 beside-values:",
      {k: v for k, v in R["rules"]["E83-R1"].items() if "beside" in k},
      {k: v for k, v in R["rules"]["E83-R3"].items() if "beside" in k})

# ------------------------------------------------------------------------------------------------------------------
hdr("C5. Which side's zero: A (the broadcast side) zero against B zero")
for t, az, bz in (("fp32", "a_zeros_b_randn", "a_randn_b_zeros"), ("fp16", "a_zeros_b_randn", "a_randn_b_zeros"),
                  ("int8", "a_zeros_b_full", "a_full_b_zeros")):
    xa, xb = C[f"{t}/{az}"]["c_w_runs"], C[f"{t}/{bz}"]["c_w_runs"]
    dm = st.mean(xa) - st.mean(xb)
    sp = math.sqrt((st.variance(xa) + st.variance(xb)) / 2)
    tt = dm / (sp * math.sqrt(1 / len(xa) + 1 / len(xb))) if sp > 0 else float("inf")
    overlap = not (min(xa) > max(xb) or min(xb) > max(xa))
    print(f"  {t}: A zero {xa} (mean {st.mean(xa):.3f}), B zero {xb} (mean {st.mean(xb):.3f}); difference {dm:+.3f} W; "
          f"largest pass spread {max(abs(xa[0] - xa[1]), abs(xb[0] - xb[1])):.3f} W; passes overlap: {overlap}; "
          f"pooled t {tt:.2f} (2 df), two-sided p {t2_two_sided_p(tt):.2f}")
print("  all three differences have the same sign; three of three by chance alone: p = 2 x 0.5^3 = 0.25 (two-sided)")

# ------------------------------------------------------------------------------------------------------------------
hdr("C6. The two burst passes are two rounds, not exchangeable replicates")
b1 = [m for m in R["runs"] if m["block"] == "BURST" and m["rep"] == 1]
b2 = [m for m in R["runs"] if m["block"] == "BURST" and m["rep"] == 2]
order = [m["run"] for m in R["runs"] if m["block"] == "BURST"]
first2 = min(i for i, r in enumerate(order) if r.endswith("-r2"))
print(f"run order: all {len(b1)} pass-1 bursts first (positions 1-{first2}), then all {len(b2)} pass-2 bursts")
g1 = [m["gate"]["reading"][0] for m in b1]
g2 = [m["gate"]["reading"][0] for m in b2]
print(f"  launch die reading (gate): pass 1 mean {st.mean(g1):.2f} C (range {min(g1):g}-{max(g1):g}), pass 2 mean "
      f"{st.mean(g2):.2f} C (range {min(g2):g}-{max(g2):g}); difference {st.mean(g2) - st.mean(g1):+.2f} C")
print(f"  the {len(rf)} power-limited kinds without an idle reset (kind: die at the first work reading, p1 -> p2; MHz p1 -> p2):")
dd2, dm2 = [], []
for k in rf:
    c = C[k]
    ds1, ds2 = c["burst_die_start"]
    m1, m2 = c["burst_mhz_runs"]
    dd2.append(ds2 - ds1)
    dm2.append(m2 - m1)
    print(f"    {k:18s} die {ds1} -> {ds2}  MHz {m1:6.1f} -> {m2:6.1f}  ({m2 - m1:+.1f})")
mx, my = st.mean(dd2), st.mean(dm2)
sxx = sum((x - mx) ** 2 for x in dd2)
slope_ = sum((x - mx) * (y - my) for x, y in zip(dd2, dm2)) / sxx if sxx else float("nan")
print(f"  mean die difference {mx:+.2f} C; mean clock difference {my:+.1f} MHz; least-squares slope of the clock "
      f"difference on the die difference {slope_:+.1f} MHz per C (n {len(dd2)}, descriptive)")
print(f"  a check of scale: at 700 MHz, 1 C more of die costs {SH.LEAK_W_PER_C} W of leakage under the 65 W cap, and the "
      f"burst power of random fp32 rises about {C['fp32/randn']['c_w'] * (SH.S[800] - SH.S[700]):.1f} W per 100 MHz "
      f"(c x (s_800 - s_700)): about {100 * SH.LEAK_W_PER_C / (C['fp32/randn']['c_w'] * (SH.S[800] - SH.S[700])):.1f} "
      f"MHz per C")

# ------------------------------------------------------------------------------------------------------------------
hdr("C7. table_cells / cells.json: what goes in `interval`")
print(f"  burst cells: the two passes. Single-run sustained cells: one run's sigma from C3 (slope {SQ2 * hs:.1f} MHz, "
      f"clamp {SQ2 * hc:.1f} MHz; board W {sw:.1f} W; die {sd_:.1f} C). Two-run cells: both runs. Limits: no interval.")
nsingle = sum(1 for k in NEW if len(C[k]["sus_mhz_runs"]) == 1)
ns_slope = sum(1 for k in NEW if len(C[k]["sus_mhz_runs"]) == 1 and C[k]["sus_limit"] == "thermal"
               and C[k]["sus_mhz"] > 615)
print(f"  of the 33: {nsingle} single-run sustained cells ({ns_slope} thermal-held above 615 MHz take the slope sigma, "
      f"{nsingle - ns_slope} the clamp sigma: limit none, or at most 615 MHz), {len(NEW) - nsingle} with two runs")

# ------------------------------------------------------------------------------------------------------------------
hdr("C8. The sampler: outside timeout 10 by E64's design, stopped by the runner's SIGTERM")
for s in ("smoke", "s1"):
    M = [json.loads(ln) for ln in open(os.path.join(HERE, s, "marks.jsonl"))]
    starts = [m for m in M if m["kind"] == "sampler_start"]
    stops = [m for m in M if m["kind"] == "sampler_stop"]
    other = sorted({m["kind"] for m in M} - {"sampler_start", "sampler_stop", "use_count_baseline"})
    att = sorted({m["detail"].split(",")[0] for m in starts})
    rcs = sorted({m["detail"].split("rc ")[-1] for m in stops})
    dur = [b["t_ms"] - a["t_ms"] for a, b in zip(starts, stops)]
    print(f"  {s}: {len(starts)} sampler_start ({att}), {len(stops)} sampler_stop (rc {rcs}); other marks: "
          f"{other or 'none'}; stop - start {min(dur) / 1000:.1f}-{max(dur) / 1000:.1f} s")
print("  run_hpl.py run_one starts the sampler as `ettelem sample --seconds <plan + 900>` and calls stop_sampler at the")
print("  end of every run: a sampler still running gets SIGTERM (stop_sampler), and SIGKILL plus one queue drain only if it")
print("  is still alive 30 s later. ettelem's sample() catches SIGTERM, finishes the reading in flight and returns 0")
print("  (tools/ettelem/ettelem.cpp, the comment above sample()). Every stop came minutes before the --seconds bound, so")
print("  all of them were SIGTERM stops, and every one exited with rc 0 inside the 30 s grace: no `error` mark, no SIGKILL,")
print("  no drain.")

# ------------------------------------------------------------------------------------------------------------------
hdr("C9. Wording: the idle reset in bursts, int8's 796 MHz passes, and the launch-ramp count's window")
print("  idle resets (results.json posthoc.idle_resets):", json.dumps(R["posthoc"]["idle_resets"]))
for m in R["runs"]:
    if m["block"] == "BURST" and m["a1"]["n_dip"]:
        ep = m["a1"]["episodes"][0]
        print(f"    {m['run']}: burst {m['burst_mhz']} MHz (without the dip {m['a1']['burst_mhz_without']}), dip at "
              f"{ep['t_s']} s on a {ep['die']} C die; first throttle-down line {m['first_down_kind']}")
print("  int8 burst passes, E80 and E83 (all 16 int8 kinds; E83's anchors int8 zeros and full are E80 kinds):")
i8 = []
e80dip = {(r["kind"], int(name.rsplit("-r", 1)[1])) for name, r in E80PH["runs"].items()
          if r["block"] == "BURST" and r["n_dip_samples"]}
for src, cells in (("E80", E80["cells"]), ("E83", {k: c for k, c in C.items() if c["role"] == "e83"})):
    for k, c in cells.items():
        if not k.startswith("int8/"):
            continue
        for i, v in enumerate(c["burst_mhz_runs"]):
            dip = (src == "E83" and any(m["kind"] == k and m["rep"] == i + 1 and m["a1"]["n_dip"]
                                        for m in R["runs"] if m["block"] == "BURST")) or \
                  (src == "E80" and (k, i + 1) in e80dip)
            i8.append((src, k, i + 1, v, dip))
n800 = sum(1 for x in i8 if x[3] == 800)
print(f"    {len(i8)} passes over {len({(x[0], x[1]) for x in i8})} kinds: {n800} at 800 MHz; below 800 without an idle "
      f"reset: {[(x[0], x[1], 'pass %d' % x[2], x[3]) for x in i8 if x[3] != 800 and not x[4]]}; with one: "
      f"{[(x[0], x[1], 'pass %d' % x[2], x[3]) for x in i8 if x[3] != 800 and x[4]]}")
tot = {"whole": [0, 0], "in-kernel": [0, 0]}
nrun = 0
for m in R["runs"]:
    if m["block"] != "SUS" or P["kinds"][m["kind"]]["a"]["sus_mhz"] < 799:
        continue
    nrun += 1
    starts, kw, t0, t1 = windows(m["run"])
    s = [x for x in tel(m["run"]) if t1 - 40000 <= x[0] <= t1]
    for lab, xs in (("whole", s), ("in-kernel", [x for x in s if any(a <= x[0] <= b for a, b in kw)])):
        below = [x for x in xs if x[4] is not None and x[4] != 800]
        tot[lab][0] += len(below)
        tot[lab][1] += sum(1 for x in below if any(0 <= x[0] - a <= 1500 for a in starts))
print(f"  launch ramps, over the {nrun} sustained runs of kinds (a) puts at 800 MHz: readings below 800 in the last 40 s "
      f"that sit within 1.5 s after one of the nine process starts:")
print(f"    every reading in the last 40 s (the gaps between processes included): {tot['whole'][1]} of {tot['whole'][0]} "
      f"({tot['whole'][1] / tot['whole'][0]:.0%})")
print(f"    the registered window (readings inside a kernel launch, as reduce_hpl.run_metrics keeps them): "
      f"{tot['in-kernel'][1]} of {tot['in-kernel'][0]} ({tot['in-kernel'][1] / tot['in-kernel'][0]:.0%})")
