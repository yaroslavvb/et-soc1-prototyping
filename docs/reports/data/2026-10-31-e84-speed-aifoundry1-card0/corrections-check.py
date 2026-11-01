#!/usr/bin/env python3
"""E84: the desk check behind the corrections after verification (Sat 31 Oct 2026). Desk only: it reads the committed
E84 session and reduction, the committed same-day aifoundry2 reductions (E80, E83), E64's committed results, E60's
committed card-0 telemetry and the committed trace-ring dumps, and prints every number the README's "Corrections after
verification" section quotes. Nothing registered is recomputed differently: results.json is read as reduce_e84.py
wrote it (it reproduces byte for byte), and the die lines use the per-run fields and the least-squares form of
reduce_kspeed.py's and reduce_e83.py's posthoc die line. Post hoc throughout, labelled, never a verdict.

    cd docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0
    python3 corrections-check.py > corrections-check.txt

Python 3, no third-party modules.
"""
import collections
import datetime
import glob
import gzip
import hashlib
import json
import math
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E80D = os.path.join(DATA, "2026-10-31-e80-kinds-speed")
E83D = os.path.join(DATA, "2026-10-31-e83-kinds-speed-rest")
E64D = os.path.join(DATA, "2026-10-23-e64-horace-power-limit")
E60D = os.path.join(DATA, "2026-10-20-bitflip-ladder", "aifoundry1-c0")

R = json.load(open(os.path.join(HERE, "results.json")))
C = R["cells"]
RUNS = R["runs"]
E80 = json.load(open(os.path.join(E80D, "results.json")))
E83 = json.load(open(os.path.join(E83D, "results.json")))
E64 = json.load(open(os.path.join(E64D, "results.json")))
A80, A83 = E80["cells"], E83["cells"]
PMIC = json.load(open(os.path.join(HERE, "posthoc", "pmic.json")))
HEAVY = {"fp32": "randn", "fp16": "randn", "int8": "full"}


def hdr(s):
    print()
    print("======== " + s)


def pdt(ms):
    t = datetime.datetime.fromtimestamp(ms / 1000.0, datetime.timezone.utc) - datetime.timedelta(hours=7)
    return t.strftime("%H:%M:%S")


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


def r3(x):
    return "%.3f" % x


def fit(points):
    """Least squares die = a + k * W over (W, die) points, as reduce_kspeed.py / reduce_e83.py fit their die lines."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - k * mx
    res = [y - (a + k * x) for x, y in zip(xs, ys)]
    rms = math.sqrt(sum(r * r for r in res) / len(res))
    se_k = math.sqrt(sum(r * r for r in res) / (len(res) - 2) / sxx)
    return {"k": k, "a": a, "n": len(points), "rms": rms, "se_k": se_k, "mx": mx, "my": my, "res": res}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]


print("E84 corrections-check: every number quoted in the README's 'Corrections after verification', from the committed")
print("files. Post hoc, labelled, never a verdict. Times are PDT, Sat 31 Oct 2026. Card 0 = aifoundry1 card 0 (E84);")
print("aifoundry2 = its card under its own governor (E80, E83: the same day; E64: 23 Oct).")
print("results.json sha256 %s, reduce.txt sha256 %s (the registered reduction, not changed by the corrections)"
      % (sha(os.path.join(HERE, "results.json")), sha(os.path.join(HERE, "reduce.txt"))))

# ------------------------------------------------------------------------------------------------------------------
hdr("C1. All-ones data against same-day aifoundry2, and the heat path per board watt")
for k, src, A in (("fp32/ones", "E83", A83), ("fp16/ones", "E80", A80)):
    c, a = C[k], A[k]
    gap = c["sus_mhz"] - a["sus_mhz"]
    spread = max(a["sus_mhz_runs"]) - min(a["sus_mhz_runs"])
    print("%s sustained: card 0 %.1f MHz (n=%d, limit %s), %.2f W, die %.2f C (max %s) | aifoundry2 %s %.1f MHz (runs %s, limits %s), "
          "%.2f W (runs %s), die %.2f C (runs %s)" % (
              k, c["sus_mhz"], len(c["sus_mhz_runs"]), "/".join(c["sus_limit_runs"]), c["sus_w"], c["sus_die"], c["sus_die_max"],
              src, a["sus_mhz"], ", ".join(str(x) for x in a["sus_mhz_runs"]), "/".join(a["sus_limit_runs"]),
              a["sus_w"], ", ".join(str(x) for x in a["sus_w_runs"]), a["sus_die"], ", ".join(str(x) for x in a["sus_die_runs"])))
    print("   card 0 minus aifoundry2's mean: %+.1f MHz (%.1f%%); aifoundry2's own two runs differ by %.1f MHz; "
          "board W: aifoundry2 %+.2f W at a die %+.2f C apart" % (
              gap, 100.0 * gap / a["sus_mhz"], spread, a["sus_w"] - c["sus_w"], a["sus_die"] - c["sus_die"]))
for lab in ("fp32-ones-1024", "fp16-ones-1024"):
    m = [r for r in E64["runs"] if r.get("label") == lab and r.get("block") == "SUS"]
    for r in m:
        print("E64 (23 Oct, aifoundry2) %s SUS: %s MHz, %s W, die %s C (the stale comparison)" % (
            lab, r.get("sus_mhz_mean"), r.get("sus_w_mean"), r.get("sus_die_mean")))
dl80 = E80["posthoc"]["die_line_e80"]
dl83 = E83["posthoc"]["die_line_e83"]
print("aifoundry2's heat path moved between 23 Oct and 31 Oct: E80's die line sits %.3f C off E64's at E64's slope "
      "(E80 results.json posthoc.die_line_e80.shift_c_at_e64_slope)" % dl80["shift_c_at_e64_slope"])
sus = [m for m in RUNS if m["block"] in ("SUS", "SUS2") and m.get("sus_w_mean") and m.get("sus_die_mean") is not None]
f0 = fit([(m["sus_w_mean"], m["sus_die_mean"]) for m in sus])
f1 = fit([(m["sus_w_mean"], m["sus_die_mean"]) for m in sus if m["kind"] != "fp32/randn"])
print("card 0 die line over its %d sustained runs (per-run sus_w_mean, sus_die_mean): die = %.2f + %.4f C per W "
      "(slope s.e. %.4f), rms %.2f C, 65.5 C at %.1f W" % (f0["n"], f0["a"], f0["k"], f0["se_k"], f0["rms"], (65.5 - f0["a"]) / f0["k"]))
print("   without the two PMIC-cycle runs (fp32 randn): die = %.2f + %.4f C per W (s.e. %.4f), rms %.2f C, n %d, "
      "65.5 C at %.1f W" % (f1["a"], f1["k"], f1["se_k"], f1["rms"], f1["n"], (65.5 - f1["a"]) / f1["k"]))
print("   the fp32 randn runs sit %s C off the line (cooler than their board W says)" % (
    ", ".join("%+.2f" % r for m, r in zip(sus, f0["res"]) if m["kind"] == "fp32/randn")))
for nm, dl in (("E83 (aifoundry2, 13:47-15:08)", dl83), ("E80 (aifoundry2, 12:22-13:02)", dl80)):
    k, a = dl["k_c_per_w"], dl["a_c"]
    off = f0["my"] - k * f0["mx"] - a
    print("%s die line: die = %.2f + %.4f C per W (n %d, rms %.2f C), 65.5 C at %.1f W; card 0 sits %+.2f C off it at "
          "its slope; at 47.09 W: card 0's line %.2f C, this line %.2f C" % (
              nm, a, k, dl["n"], dl["rms_c"], (65.5 - a) / k, off, f0["a"] + f0["k"] * 47.09, a + k * 47.09))

# ------------------------------------------------------------------------------------------------------------------
hdr("C2. aifoundry2's fp32 zeros from the same day (E83), and the zeros-over-random speed ratios")
z83, r80, r83 = A83["fp32/zeros"], A80["fp32/randn"], A83["fp32/randn"]
print("E83 fp32/zeros: burst %s MHz (passes), rate %s TFLOPS (passes %s), p800 %.2f W (passes %s); sustained %.1f MHz "
      "(n=%d), %.3f TFLOPS, limit %s" % (
          ", ".join(str(x) for x in z83["burst_mhz_runs"]), z83["burst_rate"], ", ".join(str(x) for x in z83["burst_rate_runs"]),
          z83["burst_p800_w"], ", ".join(str(x) for x in z83["burst_p800_w_runs"]), z83["sus_mhz"], len(z83["sus_mhz_runs"]),
          z83["sus_rate"], "/".join(z83["sus_limit_runs"])))
print("E83 fp32/ones: burst %s MHz (passes); sustained %.1f MHz (runs %s)" % (
    ", ".join(str(x) for x in A83["fp32/ones"]["burst_mhz_runs"]), A83["fp32/ones"]["sus_mhz"],
    ", ".join(str(x) for x in A83["fp32/ones"]["sus_mhz_runs"])))
print("random fp32 rates: E80 burst %.3f (passes %s), sustained %.3f (runs %s); E83 anchor burst %.3f (passes %s), "
      "sustained %.3f (n=1)" % (r80["burst_rate"], ", ".join(str(x) for x in r80["burst_rate_runs"]), r80["sus_rate"],
                                ", ".join(str(x) for x in r80["sus_rate_runs"]), r83["burst_rate"],
                                ", ".join(str(x) for x in r83["burst_rate_runs"]), r83["sus_rate"]))


def ratio_range(zr, rr, paired):
    if paired and len(zr) == len(rr):
        v = [z / r for z, r in zip(zr, rr)]
    else:
        v = [z / r for z in zr for r in rr]
    return min(v), max(v)


for nm, rr in (("E83 zeros / E80 randn", r80), ("E83 zeros / E83 randn", r83)):
    b = z83["burst_rate"] / rr["burst_rate"]
    s = z83["sus_rate"] / rr["sus_rate"]
    bl, bh = ratio_range(z83["burst_rate_runs"], rr["burst_rate_runs"], True)
    if len(z83["sus_rate_runs"]) * len(rr["sus_rate_runs"]) > 1:
        sl, sh = ratio_range(z83["sus_rate_runs"], rr["sus_rate_runs"], False)
        siv = "runs %s-%s" % (r3(sl), r3(sh))
    else:
        siv = "n=1 / n=1, no interval"
    print("aifoundry2 fp32 %s: burst %s (pass-paired %s-%s), sustained %s (%s)" % (nm, r3(b), r3(bl), r3(bh), r3(s), siv))
print("the stale aifoundry2 figures (E64 zeros 12.115 / 12.278 TFLOPS over E80 randn): burst %s, sustained %s" % (
    r3(12.115 / r80["burst_rate"]), r3(12.278 / r80["sus_rate"])))
print("README cells-table column, aifoundry2 burst / sustained MHz: fp32 zeros %s / %.1f (E83); fp32 ones %s / %.1f (E83)" % (
    ", ".join(str(x) for x in z83["burst_mhz_runs"]), z83["sus_mhz"],
    ", ".join(str(x) for x in A83["fp32/ones"]["burst_mhz_runs"]), A83["fp32/ones"]["sus_mhz"]))

# ------------------------------------------------------------------------------------------------------------------
hdr("C3. Card 0's own idle level")
iw = [(m["idle_w"], m["run"]) for m in RUNS]
print("runs[].idle_w: %.2f-%.2f W over %d runs (max %s); idle_mhz %s; idle_die %s-%s C; die at the cooling gates "
      "(gate.reading[0]) %s-%s C; burst runs alone %.2f-%.2f W" % (
          min(iw)[0], max(iw)[0], len(iw), max(iw)[1], sorted(set(m["idle_mhz"] for m in RUNS)),
          min(m["idle_die"] for m in RUNS), max(m["idle_die"] for m in RUNS),
          min(m["gate"]["reading"][0] for m in RUNS), max(m["gate"]["reading"][0] for m in RUNS),
          min(m["idle_w"] for m in RUNS if m["block"] == "BURST"), max(m["idle_w"] for m in RUNS if m["block"] == "BURST")))

# ------------------------------------------------------------------------------------------------------------------
hdr("C4. Intervals: the speed ratios and switching over zeros")
for f, h in HEAVY.items():
    z, r = C[f + "/zeros"], C[f + "/" + h]
    b = z["burst_rate"] / r["burst_rate"]
    bl, bh = ratio_range(z["burst_rate_runs"], r["burst_rate_runs"], True)
    s = z["sus_rate"] / r["sus_rate"]
    nz, nr = len(z["sus_rate_runs"]), len(r["sus_rate_runs"])
    if nz > 1 and nr > 1:
        sl, sh = ratio_range(z["sus_rate_runs"], r["sus_rate_runs"], False)
        sus_iv = "every pairing of the two replicates: %s-%s" % (r3(sl), r3(sh))
    else:
        sus_iv = "n=%d / n=%d, no interval" % (nz, nr)
    print("card 0 %s zeros over %s: burst %s (pass-paired %s-%s), sustained %s (%s)" % (f, h, r3(b), r3(bl), r3(bh), r3(s), sus_iv))
for f, h in HEAVY.items():
    zsrc = A83 if f == "fp32" else A80
    z, r = zsrc[f + "/zeros"], A80[f + "/" + h]
    b = z["burst_rate"] / r["burst_rate"]
    bl, bh = ratio_range(z["burst_rate_runs"], r["burst_rate_runs"], True)
    s = z["sus_rate"] / r["sus_rate"]
    nz, nr = len(z["sus_rate_runs"]), len(r["sus_rate_runs"])
    if nz > 1 or nr > 1:
        sl, sh = ratio_range(z["sus_rate_runs"], r["sus_rate_runs"], False)
        sus_iv = "runs %s-%s" % (r3(sl), r3(sh))
    else:
        sus_iv = "n=1 / n=1, no interval"
    print("aifoundry2 %s zeros (%s) over %s (E80): burst %s (pass-paired %s-%s), sustained %s (%s)" % (
        f, "E83" if f == "fp32" else "E80", h, r3(b), r3(bl), r3(bh), r3(s), sus_iv))
fr = A80["int8/full"]["sus_rate_runs"]
print("E80's two int8 full sustained runs: %s TOPS, %.1f%% apart (the size of the int8 effect itself)" % (
    ", ".join(str(x) for x in fr), 100.0 * (max(fr) - min(fr)) / min(fr)))
print("switching over zeros at 800 MHz, pass-paired (pass i of the kind minus pass i of the same format's zeros; the passes "
      "ran as two rounds, all pass 1 then all pass 2):")
for k, c in C.items():
    f, kind = k.split("/")
    if kind == "zeros":
        continue
    zr = C[f + "/zeros"]["p800_w_runs"]
    d = [a - b for a, b in zip(c["p800_w_runs"], zr)]
    print("   %-15s p800_sw_w %6.2f W; pass-paired %s" % (k, c["p800_sw_w"], ", ".join("%.2f" % x for x in d)))

# ------------------------------------------------------------------------------------------------------------------
hdr("C5. Device holds: which processes ran under timeout 10, and which did not")
L = jl_gz(os.path.join(HERE, "s1", "launches.jsonl.gz"))
t10 = sum(1 for x in L if x["cmd"][:2] == ["timeout", "10"])
stopf = sum(1 for x in L if "--stop-file" in x["cmd"])
rc0 = sum(1 for x in L if x.get("rc") == 0)
print("kernel launch processes: %d records; %d start 'timeout 10', %d carry --stop-file, %d exited rc 0" % (len(L), t10, stopf, rc0))
M = [json.loads(ln) for ln in open(os.path.join(HERE, "s1", "marks.jsonl"))]
kinds = collections.Counter(m["kind"] for m in M)
starts = [m["t_ms"] for m in M if m["kind"] == "sampler_start"]
stops = [m for m in M if m["kind"] == "sampler_stop"]
life = [(b["t_ms"] - a) / 1000.0 for a, b in zip(starts, stops)]
print("sampler (ettelem sample, run_hpl.py start_sampler, --seconds = plan + 900 s, no timeout wrapper): %d starts, %d stops, "
      "%d of them 'rc 0', alive %.1f-%.1f s; marks: %s" % (
          len(starts), len(stops), sum(1 for s in stops if s["detail"].endswith("rc 0")), min(life), max(life), dict(kinds)))
print("   error / drain / SIGKILL marks: %d" % sum(kinds.get(x, 0) for x in ("error", "drain", "drain_deferred")))
sh_txt = open(os.path.join(REPO, "tools", "claims-v3", "kspeed", "e84", "run_e84.sh")).read().splitlines()
for i, ln in enumerate(sh_txt, 1):
    if re.search(r"timeout (10|20) ", ln) and ("dev_mngt_service" in ln or '"$ETT"' in ln):
        print("run_e84.sh:%d: %s" % (i, ln.strip()))
idt = open(os.path.join(HERE, "ident", "ident-154200.out")).read()
ts = re.findall(r"2026-10-31 (\d\d:\d\d:\d\d) PDT", idt)
print("ident/ident-154200.out: first time stamp %s, last %s; %s; %s" % (
    ts[0], ts[-1], re.search(r"dev_mngt_service rc=\d+", idt).group(0),
    "; ".join(re.findall(r"(Firmware release revision: .*|BL2 Firmware versions: .*|PMIC Firmware versions: .*)", idt))))

# ------------------------------------------------------------------------------------------------------------------
hdr("C6. The 300 MHz point: E84, and E60's committed card-0 telemetry of 20 Oct")
n300 = collections.Counter()
for p in sorted(glob.glob(os.path.join(HERE, "s1", "tel", "*.jsonl.gz"))):
    for r in jl_gz(p):
        if (r.get("mhz") or {}).get("minion") == 300:
            n300[os.path.basename(p).replace(".jsonl.gz", "")] += 1
print("E84: readings at 300 MHz by run: %s (no other run); every run's idle_mhz is %s; alarm runs (posthoc/pmic.json): %s" % (
    dict(n300), sorted(set(m["idle_mhz"] for m in RUNS)), PMIC["summary"]["runs_with_alarm"]))
probe = os.path.join(E60D, "hl-probe", "p1", "telemetry.jsonl.gz")
rows = jl_gz(probe)
t0 = rows[0]["t_ms"]
S = [((r["t_ms"] - t0) / 1000.0, r.get("board_w"), r["mhz"]["minion"], r["die_mv"]["minion"]) for r in rows]
eps, i = [], 0
while i < len(S):
    if S[i][2] == 300:
        j = i
        while j + 1 < len(S) and S[j + 1][2] == 300:
            j += 1
        eps.append((i, j))
        i = j + 1
    else:
        i += 1
cls = collections.Counter()
odd = []
for (i, j) in eps:
    t = S[i][0]
    pw = [s[1] for s in S[:i] if t - 0.4 <= s[0] < t and s[1] is not None]
    path = []
    for s in S[:i]:
        if t - 2.0 <= s[0] < t and (not path or path[-1] != s[2]):
            path.append(s[2])
    last = S[i - 1]
    if pw and max(pw) >= 70:
        c = "a board reading >= 70 W in the prior 0.4 s"
    elif last[2] == 800 and last[1] is not None and last[1] < 30:
        c = "an idle-level reading at 800 MHz just before"
        odd.append("%.1f s (%.2f W, %d mV)" % (t, last[1], last[3]))
    elif 800 in path and (600 in path or 700 in path):
        c = "the 600-700-800 climb, then a lagged reading under 70 W"
    else:
        c = "other"
    cls[c] += 1
lag = [S[i - 1] for (i, j) in eps if S[i - 1][1] is not None and 30 <= S[i - 1][1] < 70]
print("E60 heater probe (hl-probe/p1): %d readings, %d episodes at 300 MHz (%d readings), each right after an 800 MHz "
      "reading in %d of them" % (len(S), len(eps), sum(j - i + 1 for i, j in eps), sum(1 for (i, j) in eps if S[i - 1][2] == 800)))
for c, n in cls.most_common():
    print("   %2d after %s" % (n, c))
print("   the lagged readings before a 300 MHz episode: %.1f-%.1f W at %d-%d mV; the idle-level ones: %s" % (
    min(s[1] for s in lag), max(s[1] for s in lag), min(s[3] for s in lag), max(s[3] for s in lag), "; ".join(odd)))
idle = collections.Counter()
allc = collections.Counter()
nf = 0
for p in sorted(glob.glob(os.path.join(E60D, "**", "telemetry*.jsonl.gz"), recursive=True)):
    nf += 1
    for r in jl_gz(p):
        m = r["mhz"]["minion"]
        allc[m] += 1
        if r.get("board_w") is not None and r["board_w"] < 25:
            idle[m] += 1
print("E60 card 0, all %d committed telemetry files: readings under 25 W (idle) by clock %s of %d; all readings by clock %s" % (
    nf, dict(sorted(idle.items())), sum(idle.values()), dict(sorted(allc.items()))))
print("E60's trace rings are not in the repository (the .bin files there are tiles), so the alarm cannot be confirmed for 20 Oct")

# ------------------------------------------------------------------------------------------------------------------
hdr("C7. fp32 random data on card 0 at 800 MHz, and what 1.67x means")
r = C["fp32/randn"]
mx8 = []
for p in sorted(glob.glob(os.path.join(HERE, "s1", "tel", "*fp32-randn*.jsonl.gz"))):
    w = [x["board_w"] for x in jl_gz(p) if (x.get("mhz") or {}).get("minion") == 800 and x.get("board_w") is not None]
    mx8.append((max(w), os.path.basename(p).replace(".jsonl.gz", "")))
print("p800 (median board W, first second at 800 MHz): %s W (passes); highest board reading at 800 MHz per fp32 randn run: %s" % (
    ", ".join(str(x) for x in r["p800_w_runs"]), ", ".join("%.2f (%s)" % x for x in mx8)))
print("PMIC's own readings at the alarm: %s mW; set point %s mW (posthoc/pmic.json summary)" % (
    PMIC["summary"]["alarm_powers_mw"], PMIC["summary"]["set_points_mw"]))
z = C["fp32/zeros"]
print("sustained rates: zeros %.3f TFLOPS, random %.3f TFLOPS: zeros %.3fx faster, i.e. random data takes %.3fx as long" % (
    z["sus_rate"], r["sus_rate"], z["sus_rate"] / r["sus_rate"], z["sus_rate"] / r["sus_rate"]))

# ------------------------------------------------------------------------------------------------------------------
hdr("C8. Board power at 800 MHz, card 0 against aifoundry2: absolute, and split into zeros and switching over zeros")
ref = {}
for k in C:
    f, kind = k.split("/")
    if kind in ("zeros", "ones") and f == "fp32":
        ref[k] = ("E83", A83[k])
    elif k in A80:
        ref[k] = ("E80", A80[k])
gaps, sw = [], []
for k, c in C.items():
    f, kind = k.split("/")
    src, a = ref[k]
    za_src, za = ref[f + "/zeros"]
    sw_a = a["burst_p800_w"] - za["burst_p800_w"]
    gaps.append((a["burst_p800_w"] - c["p800_w"], k))
    line = "   %-15s card 0 %6.2f W | aifoundry2 %6.2f W (%s) | absolute gap %5.2f W" % (
        k, c["p800_w"], a["burst_p800_w"], src, a["burst_p800_w"] - c["p800_w"])
    if kind != "zeros":
        sw.append((sw_a - c["p800_sw_w"], k))
        line += " | over own zeros: card 0 %5.2f, aifoundry2 %5.2f (zeros %s), gap %4.2f W" % (c["p800_sw_w"], sw_a, za_src, sw_a - c["p800_sw_w"])
    print(line)
print("absolute gap over the 11 kinds %.2f-%.2f W; the zeros themselves %s W; over own zeros, the 8 other kinds %.2f-%.2f W "
      "(fp32 randn / fp16 randn / int8 full: %s W)" % (
          min(gaps)[0], max(gaps)[0], ", ".join("%.2f" % g for g, k in gaps if k.endswith("/zeros")), min(sw)[0], max(sw)[0],
          " / ".join("%.2f" % g for g, k in sw if k in ("fp32/randn", "fp16/randn", "int8/full"))))
print("E83's fp32 randn anchor p800 %.2f W (E80 %.2f W)" % (A83["fp32/randn"]["burst_p800_w"], A80["fp32/randn"]["burst_p800_w"]))

# ------------------------------------------------------------------------------------------------------------------
hdr("C10. E84-P3 split by what was predicted")
rows3 = R["rules"]["E84-P3"]
for blk, pk, mk in (("burst", "pred_burst_limit", "burst_limit_runs"), ("sustained", "pred_sus_limit", "sus_limit_runs")):
    lst = [(k, c[pk], c[mk], all(x == c[pk] for x in c[mk])) for k, c in C.items()]
    lim = [x for x in lst if x[1] != "none"]
    non = [x for x in lst if x[1] == "none"]
    print("%s: %d of %d right (results.json rules.E84-P3.%s.right = %d); predicted limited: %d of %d right (%s); "
          "predicted none: %d of %d right" % (
              blk, sum(1 for x in lst if x[3]), len(lst), blk, rows3[blk]["right"], sum(1 for x in lim if x[3]), len(lim),
              "; ".join("%s %s -> %s" % (x[0], x[1], "/".join(x[2])) for x in lim), sum(1 for x in non if x[3]), len(non)))

# ------------------------------------------------------------------------------------------------------------------
hdr("C11. The voltage behind p800 and switching over zeros")
mv = []
for p in sorted(glob.glob(os.path.join(HERE, "s1", "tel", "BURST-*.jsonl.gz"))):
    v = [x["die_mv"]["minion"] for x in jl_gz(p) if (x.get("mhz") or {}).get("minion") == 800
         and x.get("board_w") is not None and x["board_w"] > 25 and (x.get("die_mv") or {}).get("minion")]
    if v:
        mv.append(st.median(v))
print("minion rail at 800 MHz under load, median per burst run: %.0f-%.0f mV over %d runs (E78/E82's switching_W is at 600 MHz, "
      "~500-520 mV)" % (min(mv), max(mv), len(mv)))

# ------------------------------------------------------------------------------------------------------------------
hdr("C12. aifoundry2's committed trace rings and telemetry: no PMIC alarm, no 300 MHz")
ALARM = re.compile(rb"alarm set point = (\d+) mW")
F300 = re.compile(rb"New OP: Freq 300")
for nm, d in (("E80", E80D), ("E64", E64D), ("E83", E83D), ("E84", HERE)):
    files = sorted(glob.glob(os.path.join(d, "**", "sp", "*.bin"), recursive=True))
    na = nf3 = 0
    for p in files:
        b = open(p, "rb").read()
        na += len(ALARM.findall(b))
        nf3 += len(F300.findall(b))
    tel = sorted(glob.glob(os.path.join(d, "**", "tel*", "*.jsonl*"), recursive=True)) + \
        sorted(glob.glob(os.path.join(d, "**", "telemetry*.jsonl*"), recursive=True))
    cnt = collections.Counter()
    for p in tel:
        op = gzip.open if p.endswith(".gz") else open
        try:
            with op(p, "rt") as fh:
                for ln in fh:
                    if ln.startswith("{"):
                        try:
                            cnt[(json.loads(ln).get("mhz") or {}).get("minion")] += 1
                        except ValueError:
                            pass
        except (OSError, EOFError):
            pass
    print("%s: %d ring dumps (%d in s1/), %d alarm lines, %d 'New OP: Freq 300' lines; telemetry %d readings, %d at 300 MHz" % (
        nm, len(files), len(glob.glob(os.path.join(d, "s1", "**", "sp", "*.bin"), recursive=True)), na, nf3,
        sum(v for k2, v in cnt.items() if k2 is not None), cnt.get(300, 0)))
