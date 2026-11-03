"""E150, corrections after verification: prints every number the README's corrections C1-C8 quote.

    python corrections-numbers.py [--trunc <empty scratch dir>] [--fetch <the freeze's fetch dir>] > corrections-numbers.txt

It reads committed files only: this directory (score-e150.json, predictions-e150.json, reduce-L.json, reduce-H.json,
billing.json, ledger.json, apps-e150.json, logs/), E149's data directory (posthoc.txt), tools/gpu/e149/e149_app.py, and
the commit times of E150's commits from git. Two optional checks write or read outside the repo and print basenames only:
--trunc re-derives the freeze from a copy of the logs cut at the end of phase L (pass 2's last window), written into the
given directory, with the registered tools/gpu/e150/analyze_e150.py, and compares it with the committed
predictions-e150.json; --fetch lists what the freeze's fetch held (its files' times) and compares each file with the
committed log of the same name. Desk only: nothing here touches a GPU or Modal, and no committed file is changed.
"""
import datetime
import glob
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
D149 = os.path.abspath(os.path.join(HERE, "..", "2026-11-02-e149-gpu-model-check"))
RUN = os.path.join(HERE, "logs", "e150-20261102-r1")
NOTUSED = os.path.join(HERE, "logs", "e150-20261102-r1-not-used")
SMOKE = os.path.join(HERE, "logs", "e150-20261102-smoke")
PST = datetime.timezone(datetime.timedelta(hours=-8))
GPU_RATE_H = {"L4": 0.80, "A10G": 1.10}       # E150.md "Budget": modal billing rates read 21:46 PST, 2 Nov 2026


def J(p):
    with open(p) as f:
        return json.load(f)


def JG(p):
    with gzip.open(p, "rt") as f:
        return json.load(f)


def hms(t):
    return datetime.datetime.fromtimestamp(t, PST).strftime("%H:%M:%S.%f")[:-4]


def rms(v):
    v = list(v)
    return math.sqrt(sum(x * x for x in v) / len(v))


def mean(v):
    v = list(v)
    return sum(v) / len(v)


def git_time(sha):
    env = dict(os.environ, TZ="America/Los_Angeles")
    r = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%cd", "--date=format-local:%H:%M:%S", sha],
                       capture_output=True, text=True, env=env)
    return r.stdout.strip() or "?"


def ts_of(s):
    return datetime.datetime.fromisoformat(s).timestamp()


def head(t):
    print()
    print("== " + t)


sc = J(os.path.join(HERE, "score-e150.json"))
pz = J(os.path.join(HERE, "predictions-e150.json"))
redL = J(os.path.join(HERE, "reduce-L.json"))
redH = J(os.path.join(HERE, "reduce-H.json"))
print("E150 corrections after verification: the numbers C1-C8 quote (corrections-numbers.py)")

# ---------------------------------------------------------------------------------------------------------- C1
head("C1 heat: what the power path and the heat model each contribute to the blind 30 s rise error (score-e150.json heat)")
rows = sc["heat"]["rows"]
eb = {k: r["meas_rise_c"] - r["pred_blind_c"] for k, r in rows.items()}      # the registered path's error
ec = {k: r["meas_rise_c"] - r["pred_corr_c"] for k, r in rows.items()}       # the corrected arm's error
em = {k: r["meas_rise_c"] - r["pred_measP_c"] for k, r in rows.items()}      # the heat model's error, given measured power
dd = {k: r["pred_measP_c"] - r["pred_blind_c"] for k, r in rows.items()}     # = eb - em: the power path's share
n = len(rows)
print(f"kinds {n}; committed rms blind {sc['heat']['rms_blind_c']:.3f} C, corrected {sc['heat']['rms_corr_c']:.3f}, "
      f"measured power {sc['heat']['rms_measP_c']:.3f}; bias blind {sc['heat']['bias_blind_c']:+.3f}, "
      f"corrected {sc['heat']['bias_corr_c']:+.3f}, measured power {sc['heat']['bias_measP_c']:+.3f}")
print(f"recomputed: rms blind {rms(eb.values()):.3f}, corrected {rms(ec.values()):.3f}, measured power "
      f"{rms(em.values()):.3f}")
print(f"the power path's share d = predicted rise from measured power - blind predicted rise (blind error = heat model's "
      f"error + d): rms {rms(dd.values()):.3f} C, mean {mean(dd.values()):+.3f} C")
print(f"bias: blind {mean(eb.values()):+.3f} = heat model {mean(em.values()):+.3f} + power path {mean(dd.values()):+.3f}")
g1b = sc["models"]["G1"]["bias_w"]
r30p = pz["heat"]["pooled"]["rise30_per_W"]
print(f"the power path's mean, in parts: G1's bias {g1b:+.2f} W x the fit's 30 s rise per W {r30p:.3f} C/W = "
      f"{g1b * r30p:+.3f} C; the double count (corrected arm's bias minus the blind arm's) "
      f"{-(mean(ec.values()) - mean(eb.values())):+.3f} C; the rest "
      f"{mean(dd.values()) - g1b * r30p + (mean(ec.values()) - mean(eb.values())):+.3f} C")
cov = mean(em[k] * dd[k] for k in rows)
print(f"heat model's error against the power path's share: mean product {cov:+.3f} C^2, correlation "
      f"{cov / (rms(em.values()) * rms(dd.values())):+.2f} (raw moments; they partly cancel)")
ck = "bf16.checker"
r = rows[ck]
ssb = sum(v * v for v in eb.values())
print(f"checkerboard: measured {r['meas_rise_c']:.2f} C; blind {r['pred_blind_c']:.2f} (error {eb[ck]:+.2f}), corrected "
      f"{r['pred_corr_c']:.2f} (error {ec[ck]:+.2f}), from measured power {r['pred_measP_c']:.2f} (error {em[ck]:+.2f}); "
      f"d {dd[ck]:+.2f}")
print(f"checkerboard's share of the blind arm's sum of squares {100 * eb[ck] ** 2 / ssb:.0f}%; of d's "
      f"{100 * dd[ck] ** 2 / sum(v * v for v in dd.values()):.0f}%")
rest = [k for k in rows if k != ck]
print(f"without the checkerboard ({len(rest)} kinds): rms blind {rms(eb[k] for k in rest):.3f}, corrected "
      f"{rms(ec[k] for k in rest):.3f}, measured power {rms(em[k] for k in rest):.3f}, d {rms(dd[k] for k in rest):.3f}; "
      f"bias blind {mean(eb[k] for k in rest):+.3f}, measured power {mean(em[k] for k in rest):+.3f}")
g1ck = sc["per_kind"][ck]["err"]["G1"]
r30 = pz["heat"]["pooled"]["rise30_per_W"]
print(f"G1's power error on the checkerboard {g1ck:+.1f} W x the fit's 30 s rise per W {r30:.3f} C/W = "
      f"{g1ck * r30:+.2f} C")
print("largest blind errors (C): " + "; ".join(
    f"{k} {eb[k]:+.2f} (measured power {em[k]:+.2f}, d {dd[k]:+.2f})" for k in sorted(rows, key=lambda k: -abs(eb[k]))[:5]))

# ---------------------------------------------------------------------------------------------------------- C2
head("C2 cost by board: billing.json's rows per app, tied to the units by apps-e150.json's times")
bill = J(os.path.join(HERE, "billing.json"))
apps = sorted(J(os.path.join(HERE, "apps-e150.json"))["rows"], key=lambda a: a["created_at"])
units = []
for base in (SMOKE, RUN, NOTUSED):
    for d in sorted(glob.glob(os.path.join(base, "*"))):
        st, dn = J(os.path.join(d, "STARTED")), J(os.path.join(d, "DONE"))
        units.append((os.path.basename(d), st["t"], dn.get("t_end", dn.get("t")), dn.get("elapsed_s")))
for a in apps:
    c0, c1 = ts_of(a["created_at"]), ts_of(a["stopped_at"])
    mine = []
    for un, t0, t1, el in units:
        # the app created last before the unit's STARTED, and stopped after its DONE
        before = [b for b in apps if ts_of(b["created_at"]) <= t0]
        if before and max(before, key=lambda b: ts_of(b["created_at"]))["app_id"] == a["app_id"] and t1 <= c1:
            mine.append((un, el))
    cost = bill["by_app_id"].get(a["app_id"], {})
    tot = sum(cost.values())
    gpu = {g: cost[g] / GPU_RATE_H[g] * 3600 for g in GPU_RATE_H if g in cost}
    print(f"{a['app_id']}: created {a['created_at'][11:19]}, stopped {a['stopped_at'][11:19]}; units "
          f"{[u for u, _ in mine] or 'none'} (STARTED {', '.join(hms(t0) for un, t0, _, _ in units if un in [u for u, _ in mine]) or '-'}); "
          f"metered ${tot:.4f} ({', '.join(f'{k} {v:.4f}' for k, v in cost.items()) or 'no row'}); "
          f"GPU-seconds at the read rates {', '.join(f'{g} {s:.0f}' for g, s in gpu.items()) or '-'}; "
          f"the units' function-seconds {sum(el or 0 for _, el in mine):.1f}")
print(f"total metered ${bill['total_usd']:.4f}")
print("GPU resources billed per app: " + "; ".join(f"{k}: {sorted(set(v) - {'CPU', 'Memory'})}"
                                                    for k, v in bill["by_app_id"].items()))

# ---------------------------------------------------------------------------------------------------------- C3
head("C3 the ledger's priced function-seconds (ledger.json)")
led = J(os.path.join(HERE, "ledger.json"))
priced = [(c["unit"], c["fn_seconds"]) for c in led["calls"] if c["est_usd_fn"] is not None]
unpriced = [(c["unit"], c["fn_seconds"], c["gpu"]) for c in led["calls"] if c["fn_seconds"] and c["est_usd_fn"] is None]
print(f"fn_seconds_total {led['fn_seconds_total']:.1f} s; est_usd_fn_total ${led['est_usd_fn_total']:.4f}; priced "
      f"{sum(s for _, s in priced):.1f} s over {[u for u, _ in priced]}; unpriced {unpriced}")
bname = JG(os.path.join(NOTUSED, "B", "steps", "000_static.json.gz"))["static"]["name"]
print(f"board B's NVML name: {bname!r} (ledger_e150.py's gpu_of() matches 'L4' and 'A10G' only)")
rate = led["rate_per_unit_h"]["A10G"]
add = sum(s for _, s, _ in unpriced) / 3600 * rate
print(f"the unpriced seconds at the A10G unit rate ${rate:.4f}/h: ${add:.4f}; all {led['fn_seconds_total']:.1f} s: "
      f"${led['est_usd_fn_total'] + add:.4f}")

# ---------------------------------------------------------------------------------------------------------- C4
head("C4 the freeze's timing against phase H (logs/e150-20261102-r1, git)")
for un in ("A", "B4"):
    for st in ("007_pass3", "008_pass4"):
        ws = JG(os.path.join(RUN, un, "steps", st + ".json.gz"))["windows"]
        print(f"board {un} {st}: {len(ws)} windows {hms(min(w['t_a'] for w in ws))} -> {hms(max(w['t_b'] for w in ws))}")
for sha, what in (("bacc1a94", "the freeze"), ("fbd1df58", "A5"), ("bc14113b", "the note on A5"),
                  ("451812e5", "phase H scored")):
    print(f"commit {sha} ({what}): committed {git_time(sha)} PST")
for un in ("A", "B4"):
    lastp = max(r["t_a"] for ps in redL["units"][un]["passes"].values() for r in ps["rows"]) + 10.0
    p2 = JG(os.path.join(RUN, un, "steps", "006_pass2.json.gz"))["windows"]
    w0 = JG(os.path.join(RUN, un, "steps", "007_pass3.json.gz"))["windows"][0]
    print(f"board {un}: the freeze's heat series (analyze_e150.py do_freeze: the last phase-L row's start + 10 s) ends "
          f"{hms(lastp)}; pass 2's last window ends {hms(max(w['t_b'] for w in p2))}; pass 3's first window "
          f"{w0['kind']} ({w0['role']}) {hms(w0['t_a'])} -> {hms(w0['t_b'])}: the series runs {lastp - w0['t_a']:.2f} s into it")


def flat(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, p + "/" + str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from flat(v, f"{p}[{i}]")
    else:
        yield p, x


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


args = sys.argv[1:]
if "--fetch" in args:
    fd = args[args.index("--fetch") + 1]
    for un in ("A", "B4"):
        fs = sorted(glob.glob(os.path.join(fd, un, "steps", "*"))) + sorted(glob.glob(os.path.join(fd, un, "samples", "*")))
        same = all(sha(f) == sha(os.path.join(RUN, un, os.path.basename(os.path.dirname(f)), os.path.basename(f)))
                   for f in fs)
        mt = [os.path.getmtime(f) for f in fs]
        steps = [os.path.basename(f).split(".")[0] for f in fs if "/steps/" in f]
        last = max(json.loads(l)["t"] for l in gzip.open(sorted(glob.glob(os.path.join(fd, un, "samples", "*")))[-1], "rt")
                   if l.strip())
        print(f"the freeze's fetch, board {un}: {len(fs)} files written {hms(min(mt))}-{hms(max(mt))}; steps "
              f"{steps[0]} .. {steps[-1]}; last sample {hms(last)}; every file byte-identical to the committed log: {same}")
if "--trunc" in args:
    td = os.path.abspath(args[args.index("--trunc") + 1])
    cut = os.path.join(td, "e150-20261102-r1")
    if os.path.isdir(cut):
        shutil.rmtree(cut)
    for un in ("A", "B4"):
        ud, od = os.path.join(RUN, un), os.path.join(cut, un)
        os.makedirs(os.path.join(od, "steps"))
        os.makedirs(os.path.join(od, "samples"))
        for f in ("plan.json", "STARTED", "features-M.json.gz"):
            shutil.copy(os.path.join(ud, f), od)
        tend = None
        for f in sorted(glob.glob(os.path.join(ud, "steps", "*.json.gz"))):
            if int(os.path.basename(f)[:3]) <= 6:
                shutil.copy(f, os.path.join(od, "steps"))
                if "pass2" in f:
                    tend = max(w["t_b"] for w in JG(f)["windows"])
        kept = dropped = 0
        for f in sorted(glob.glob(os.path.join(ud, "samples", "*.jsonl.gz"))):
            out = []
            with gzip.open(f, "rt") as g:
                for line in g:
                    s = line.strip()
                    if s and json.loads(s).get("t", 0) <= tend:
                        out.append(s)
                        kept += 1
                    elif s:
                        dropped += 1
            if out:
                with gzip.open(os.path.join(od, "samples", os.path.basename(f)), "wt") as g:
                    g.write("\n".join(out) + "\n")
        print(f"cut copy, board {un}: steps 000-006, samples to pass 2's last window end {hms(tend)} ({kept} kept, "
              f"{dropped} dropped)")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    az = os.path.join(REPO, "tools", "gpu", "e150", "analyze_e150.py")
    rl, pr = os.path.join(td, "reduce-L.json"), os.path.join(td, "predictions-e150.json")
    for cmd in (["reduce", cut, "L", rl],
                ["freeze", rl, cut, os.path.join(D149, "model-e149.json"), os.path.join(D149, "reduce-stage1.json"), pr]):
        res = subprocess.run([sys.executable, az] + cmd, capture_output=True, text=True, env=env, timeout=900)
        print(f"analyze_e150.py {cmd[0]} on the cut copy: exit {res.returncode}")
    a, b = dict(flat(pz)), dict(flat(J(pr)))
    worst, nnum = {}, 0
    for k, x in a.items():
        y = b.get(k)
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
            nnum += 1
            rel = abs(x - y) / max(abs(x), abs(y), 1e-300) if x != y else 0.0
            top = k.split("/")[1]
            worst[top] = max(worst.get(top, 0.0), rel)
    print(f"the freeze from the cut copy against the committed predictions-e150.json, {nnum} numbers: largest relative "
          f"difference by block: " + "; ".join(f"{k} {v:.2g}" for k, v in sorted(worst.items(), key=lambda kv: -kv[1])))
    hc, ht = pz["heat"], J(pr)["heat"]
    for key in ("R_ss", "r1", "r2", "tau1", "tau2", "rise30_per_W", "F30", "rms", "sse", "n"):
        print(f"  heat pooled {key}: committed {hc['pooled'][key]:.5f}, cut {ht['pooled'][key]:.5f} "
              f"({100 * (ht['pooled'][key] / hc['pooled'][key] - 1):+.2f}%)")
    print(f"  heat pooled session-start terms (init, one per board): committed "
          f"{', '.join(f'{v:.4f}' for v in hc['pooled']['init'])}, cut {', '.join(f'{v:.4f}' for v in ht['pooled']['init'])}; "
          f"intercepts committed {', '.join(f'{v:.3f}' for v in hc['pooled']['icpt'])}, cut "
          f"{', '.join(f'{v:.3f}' for v in ht['pooled']['icpt'])}")
    for un in ("A", "B4"):
        print(f"  heat per board {un}: init {hc['per_unit'][un]['init'][0]:.4f} -> {ht['per_unit'][un]['init'][0]:.4f}; R_ss "
              f"{hc['per_unit'][un]['R_ss']:.5f} -> {ht['per_unit'][un]['R_ss']:.5f}, r1 "
              f"{hc['per_unit'][un]['r1']:.5f} -> {ht['per_unit'][un]['r1']:.5f}, n {hc['per_unit'][un]['n']} -> "
              f"{ht['per_unit'][un]['n']}, sse {hc['per_unit'][un]['sse']:.1f} -> {ht['per_unit'][un]['sse']:.1f}")
    print(f"  lambda_r1: committed {hc['lambda_r1']:.5f}, cut {ht['lambda_r1']:.5f}; sigma_cross committed "
          f"{hc['sigma_cross_c']:.4f}, cut {ht['sigma_cross_c']:.4f}")

# ---------------------------------------------------------------------------------------------------------- C5
head("C5 A2's timing: the L4's smoke container against A1 (logs/e150-20261102-smoke, apps-e150.json, git)")
st, dn = J(os.path.join(SMOKE, "S-L4", "STARTED")), J(os.path.join(SMOKE, "S-L4", "DONE"))
t_s = min(json.loads(l)["t"] for f in sorted(glob.glob(os.path.join(SMOKE, "S-L4", "samples", "*.jsonl.gz")))
          for l in gzip.open(f, "rt") if l.strip())
a1 = git_time("de658109")
a1t = datetime.datetime.strptime("2026-11-02 " + a1, "%Y-%m-%d %H:%M:%S").replace(tzinfo=PST).timestamp()
smk = [a for a in apps if a["app_id"] == "ap-2D097VePZT0r2FJq6FzIPq"][0]
print(f"the smoke's app created {smk['created_at'][11:19]}; S-A10G STARTED "
      f"{hms(J(os.path.join(SMOKE, 'S-A10G', 'STARTED'))['t'])}; S-L4 STARTED {hms(st['t'])}, its function's first line "
      f"(t_fn) {hms(dn['t_fn'])}, its first NVML sample {hms(t_s)}, its DONE {hms(dn['t_end'])}")
print(f"A1 (de658109) committed {a1} PST: the L4's function had started {a1t - dn['t_fn']:.1f} s before it; A2 "
      f"(aa706ef6) committed {git_time('aa706ef6')} PST")

# ---------------------------------------------------------------------------------------------------------- C6
head("C6 the scale and the leakage share (predictions-e150.json scales, heat; E149's posthoc.txt)")
g1 = pz["scales"]["G1"]
print(f"G1 scale per board {g1['per_board']['A']:.4f} (A), {g1['per_board']['B4']:.4f} (B4); per format "
      + "; ".join(f"{un} " + ", ".join(f"{f} {v:.3f}" for f, v in g1["per_board_fmt"][un].items()) for un in ("A", "B4")))
h = pz["heat"]
lam = {un: h["leakage"][un]["lambda_w_per_c"] for un in ("A", "B4")}
r1p = h["pooled"]["r1"]
lr1 = {un: lam[un] * r1p for un in lam}
lr1own = {un: lam[un] * h["per_unit"][un]["r1"] for un in lam}
print(f"leakage slope at the held reference: A {lam['A']:.3f}, B4 {lam['B4']:.3f} W/C (ratio "
      f"{lam['B4'] / lam['A']:.1f}); mean {h['lambda_w_per_c']:.3f}; pooled r1 {r1p:.4f} C/W")
print(f"lambda r1: committed {h['lambda_r1']:.4f} (mean slope x pooled r1); by board, each slope x pooled r1: A "
      f"{lr1['A']:.4f}, B4 {lr1['B4']:.4f}; each slope x its own board's r1: A {lr1own['A']:.4f}, B4 {lr1own['B4']:.4f}")
pt = open(os.path.join(D149, "posthoc.txt")).read()
m = re.search(r"lambda x r1 \(the share of y[^:]*: A ([0-9.]+), B ([0-9.]+), pooled ([0-9.]+)", pt)
l149 = float(m.group(3))
print(f"E149 (the A100): lambda r1 A {m.group(1)}, B {m.group(2)}, pooled {m.group(3)} (posthoc.txt); the A10G's by board "
      f"is {lr1['A'] / l149:.2f}-{lr1['B4'] / l149:.2f} of the A100's pooled")
v14 = {un: 1.4 * (1 - lr1[un]) / (1 - l149) for un in lr1}
print(f"post hoc switching-energy ratio, 1.4 x (1 - lambda r1) / (1 - {l149}): at the pooled {h['lambda_r1']:.4f} "
      f"{1.4 * (1 - h['lambda_r1']) / (1 - l149):.3f}; by board A {v14['A']:.3f}, B4 {v14['B4']:.3f}")
vown = {un: g1["per_board"][un] * (1 - lr1[un]) / (1 - l149) for un in lr1}
vpool = {un: g1["per_board"][un] * (1 - h["lambda_r1"]) / (1 - l149) for un in lr1}
print(f"the same with each board's own G1 scale: at the pooled lambda r1 A {vpool['A']:.3f}, B4 {vpool['B4']:.3f}; with "
      f"each board's own lambda r1 A {vown['A']:.3f}, B4 {vown['B4']:.3f}")

# ---------------------------------------------------------------------------------------------------------- C7
head("C7 the 75% sparse held-out kind and phase L's 75% scattered-zeros rung (tools/gpu/e149/e149_app.py; reduce files)")
src = open(os.path.join(REPO, "tools", "gpu", "e149", "e149_app.py")).read().splitlines()
want = [r'src = S\(g="randn", seed="zl-src"\)', r'for f in \(25, 50, 75, 90\):', r'"bf16", f"zs\{f\}".*zmask',
        r'def _zmask', r'z = torch\.rand\(X\.shape', r'return torch\.where\(z, torch\.zeros',
        r't == "sparse75"']
for pat in want:                                       # the first line matching each, in file order
    i = next(i for i, line in enumerate(src) if re.search(pat, line))
    print(f"  e149_app.py:{i + 1}: {src[i].strip()}")
    if "sparse75" in pat:
        for j in range(i + 1, i + 4):
            print(f"  e149_app.py:{j + 1}: {src[j].strip()}")
kh, kl = redH["kinds"]["bf16.sparse75"], redL["kinds"]["bf16.zs75"]
print(f"y: held-out bf16.sparse75 {kh['y']:.2f} +/- {kh['se']:.2f} W; phase L's bf16.zs75 {kl['y']:.2f} +/- {kl['se']:.2f} W")
pk = sc["per_kind"]
blind = sorted(pk)
for mname, where in (("G1", "err"), ("G4", "err"), ("G0", "err"), ("T0_a100_measured", "err_arms")):
    e = {k: pk[k][where].get(mname) for k in blind}
    e = {k: v for k, v in e.items() if v is not None}
    e16 = [v for k, v in e.items() if k != "bf16.sparse75"]
    print(f"{mname}: rms over {len(e)} kinds {rms(e.values()):.3f} W (bias {mean(e.values()):+.3f}); without the 75% sparse, "
          f"over {len(e16)}: {rms(e16):.3f} W (bias {mean(e16):+.3f})")

# ---------------------------------------------------------------------------------------------------------- C8
head("C8 two number slips (score-e150.json; reduce-L.json, reduce-H.json)")
print(f"G0 rms {sc['models']['G0']['rms_w']:.4f} W -> {sc['models']['G0']['rms_w']:.2f}; F4's g0_rms_w "
      f"{sc['rules']['F4']['g0_rms_w']:.4f}")
cells = [(r["p"], r["kind"], un, pn) for red in (redL, redH) for un, u in red["units"].items()
         for pn, ps in u["passes"].items() for r in ps["rows"] if r.get("valid")]
lo, hi = min(cells), max(cells)
print(f"board watts by cell (every valid pass row, both phases, both boards; {len(cells)} cells): {lo[0]:.1f} W "
      f"({lo[1]}, board {lo[2]} pass {lo[3]}) to {hi[0]:.1f} W ({hi[1]}, board {hi[2]} pass {hi[3]})")
kk = [(v["p_abs"], k) for red in (redL, redH) for k, v in red["kinds"].items() if v.get("p_abs") is not None]
print(f"board watts by kind mean (p_abs, {len(kk)} kinds): {min(kk)[0]:.1f} W ({min(kk)[1]}) to {max(kk)[0]:.1f} W "
      f"({max(kk)[1]})")
zr = [(r["p"], r["kind"]) for red in (redL, redH) for u in red["units"].values() for ps in u["passes"].values()
      for r in ps["rows"] if r.get("valid") and r["kind"].endswith(".zeros")]
print(f"the zeros anchors' cells: {min(zr)[0]:.1f} ({min(zr)[1]}) to {max(zr)[0]:.1f} W ({max(zr)[1]})")
