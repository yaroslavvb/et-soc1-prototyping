#!/usr/bin/env python3
"""E114 (Q133): the numbers behind the corrections after verification (Sun 1 Nov 2026), printed from committed files.

Desk only, written after the data and after the verifier's report. No card was touched and nothing was re-run.
Everything in C2 is POST HOC (a reading, never a verdict). The definitions of a kernel's mean clock (g_eff) and of how
long a hit kernel ran at 800 MHz before a fall (x_ms) are Q132(g)'s, imported unchanged from its ir_lib.py.

    python3 corrections-check.py > corrections-check.txt        # in this directory
"""
import datetime as dt
import gzip
import hashlib
import json
import math
import os
import re
import statistics as st
import sys

sys.dont_write_bytecode = True
D = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(D)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(DATA)))
sys.path.insert(0, os.path.join(DATA, "2026-11-01-q132-governor-desk"))
import ir_lib as IL  # noqa: E402  (Q132(g)'s g_eff and x_ms)

SESS = {"E114": os.path.join(D, "s1"), "E84": os.path.join(DATA, "2026-10-31-e84-speed-aifoundry1-card0", "s1")}
RES = {"E114": os.path.join(D, "results.json"), "E84": os.path.join(DATA, "2026-10-31-e84-speed-aifoundry1-card0", "results.json")}
CAP_KINDS = ["fp16/zeros", "fp16/ones", "int8/zeros", "int8/full"]   # the four kinds at the 800 MHz cap
T975 = {2: 4.303, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def jl(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        return [json.loads(x) for x in f if x.startswith("{")]


def kind_of(v):
    p = v[5:].split("/")
    return f"{p[-2]}/{p[-1][:-4]}"


def session_runs(name):
    rd = SESS[name]
    runs = jl(os.path.join(rd, "runs.jsonl"))
    lp = os.path.join(rd, "launches.jsonl.gz")
    launches = jl(lp if os.path.exists(lp) else os.path.join(rd, "launches.jsonl"))
    out = []
    for r in runs:
        if r["block"] not in ("SUS", "SUS2"):
            continue
        k = kind_of(r["values"])
        tp = os.path.join(rd, r["tel"])
        tel = jl(tp + ".gz" if os.path.exists(tp + ".gz") else tp)
        s = sorted((int(d["t_ms"]), (d.get("mhz") or {}).get("minion")) for d in tel if "t_ms" in d)
        procs = []
        for L in sorted([L for L in launches if L["run"] == r["run"] and L.get("role") == "work"], key=lambda L: L["proc"]):
            ks = sorted([x for x in L.get("sparsity", []) if x.get("t_start_ms")], key=lambda x: x["t_start_ms"])
            procs.append({"a": min(x["t_start_ms"] for x in ks) if ks else L["t_start_ms"], "b": L["t_end_ms"], "ks": ks})
        out.append({"run": r["run"], "kind": k, "rep": r.get("rep"), "tel": s, "procs": procs, "n_tel": len(s)})
    return out


print("== 0. The registered outputs are unchanged by these corrections (sha256)")
for p in ("results.json", "reduce.txt", os.path.join("posthoc", "climb.txt"), os.path.join("posthoc", "climb.json")):
    print(f"   {p}: {sha(os.path.join(D, p))}")

# ---------------------------------------------------------------------------------------------------------------- C2
print("\n== C2 (post hoc). Every fall below 800 MHz that reaches the last 40 s while kernels run, for the four kinds at the cap.")
print("   An EPISODE is a run of consecutive samples below 800 MHz (10 Hz; no 800 MHz sample between them and no hole over 1 s).")
print("   It counts when one of its samples")
print("   lies in the window between a process's first kernel and its last kernel's end. Its ONSET is its first sample: AT A")
print("   START when that comes before, or within 0.2 s of, a process's first kernel (the fall happened in the 0.33 s gap");
print("   between processes); INSIDE a process otherwise, with the hit kernel (the first kernel there with g_eff < 0.79 GHz,")
print("   Q132(g)'s ir_lib.g_eff), the gap before it and x_ms (its time at 800 MHz before the fall).")
falls = {}
for name in SESS:
    R = {r["run"]: r for r in json.load(open(RES[name]))["runs"]}
    for run in session_runs(name):
        if run["kind"] not in CAP_KINDS:
            continue
        t1 = max(p["b"] for p in run["procs"])
        tl = t1 - 40000
        work = [(p["a"], max(k["t_end_ms"] for k in p["ks"]) if p["ks"] else p["b"]) for p in run["procs"]]
        def in_work(t):
            return any(a <= t <= kend for a, kend in work)
        eps, prev_low = [], False
        last_t = None
        for t, m in run["tel"]:
            if m is None:
                continue
            low_now = m < 800
            if low_now and prev_low and t - last_t <= 1000:
                eps[-1].append((t, m))
            elif low_now:
                eps.append([(t, m)])
            prev_low, last_t = low_now, t
        recs = []
        for ep in eps:
            inwin = [(t, m) for t, m in ep if tl <= t <= t1 and in_work(t)]
            if not inwin:
                continue
            t0 = ep[0][0]
            # the process whose first kernel follows the onset within 0.2 s, or else the one the onset falls inside
            nxt = next((i for i, (a, _) in enumerate(work) if a + 200 >= t0), None)
            if nxt is not None and work[nxt][0] - t0 <= 600:
                rec = {"at": "start", "proc": nxt, "onset_s": round((t0 - work[nxt][0]) / 1000.0, 2)}
            else:
                i = max(i for i, (a, _) in enumerate(work) if a <= t0)
                p = run["procs"][i]
                rec = {"at": "inside", "proc": i, "onset_s": round((t0 - work[i][0]) / 1000.0, 2)}
                hit = next((j for j, k in enumerate(p["ks"]) if k.get("launch", -1) >= 0 and k["t_end_ms"] >= t0 - 300
                            and (IL.g_eff(k) or 1) < 0.79), None)
                if hit is not None and hit > 0:
                    k, k0 = p["ks"][hit], p["ks"][hit - 1]
                    rec.update({"kernel": k.get("launch"), "gap_before_ms": k["t_start_ms"] - k0["t_end_ms"],
                                "x_ms": round(IL.x_ms(k), 1), "g_before": round(IL.g_eff(k0), 4)})
            rec.update({"n_low": len(ep), "n_low_in_window": len(inwin), "min_mhz": min(m for _, m in ep),
                        "starts_before_window": t0 < tl})
            recs.append(rec)
        r = R[run["run"]]
        falls.setdefault(name, {})[run["run"]] = {"kind": run["kind"], "rep": run["rep"], "eps": recs,
                                                  "rate": r["sus_rate_t"], "mhz_all": r["sus_mhz_all"]}
def nstart(f):
    return sum(1 for e in f["eps"] if e["at"] == "start")
def ninside(f):
    return sum(1 for e in f["eps"] if e["at"] == "inside")
def nlow(f):
    return sum(e["n_low_in_window"] for e in f["eps"])
for name in SESS:
    print(f"-- {name}")
    for run, f in falls[name].items():
        print(f"   {f['kind']:10s} {run:24s} rate {f['rate']:7.3f}  sampled MHz {f['mhz_all']:6.1f}  falls {len(f['eps'])} "
              f"(at a start {nstart(f)}, inside {ninside(f)}); low samples in the window {nlow(f)}")
        for e in f["eps"]:
            if e["at"] == "inside" or e["starts_before_window"]:
                print(f"        {e}")

print("\n-- int8 pass pairs: zeros against full. rho = rate ratio; clock ratio = sampled-MHz ratio; rate per clock = rho / clock ratio")
for name in SESS:
    zs = sorted([f for f in falls[name].values() if f["kind"] == "int8/zeros"], key=lambda f: f["rep"])
    fs = sorted([f for f in falls[name].values() if f["kind"] == "int8/full"], key=lambda f: f["rep"])
    for z, f in zip(zs, fs):
        rho = z["rate"] / f["rate"]
        cr = z["mhz_all"] / f["mhz_all"]
        print(f"   {name:4s} pass {z['rep']}: rho {rho:.5f}  clock ratio {cr:.5f}  rate per clock {rho / cr:.4f}  "
              f"falls zeros {len(z['eps'])} ({nstart(z)} at a start, {ninside(z)} inside), full {len(f['eps'])} ({nstart(f)}, {ninside(f)}): "
              f"zeros minus full {len(z['eps']) - len(f['eps']):+d}; low samples in the window {nlow(z)} against {nlow(f)}")
print("-- fp16 zeros against ones, the same passes (both at the cap; a check that the data do not set the rate at a given clock)")
for name in SESS:
    zs = sorted([f for f in falls[name].values() if f["kind"] == "fp16/zeros"], key=lambda f: f["rep"])
    os_ = sorted([f for f in falls[name].values() if f["kind"] == "fp16/ones"], key=lambda f: f["rep"])
    for z, o in zip(zs, os_):
        print(f"   {name:4s} pass {z['rep']}: zeros/ones rate {z['rate'] / o['rate']:.5f}  clock {z['mhz_all'] / o['mhz_all']:.5f}  "
              f"rate per clock {(z['rate'] / o['rate']) / (z['mhz_all'] / o['mhz_all']):.4f}; falls {len(z['eps'])} against {len(o['eps'])}")
ins = [(n, r, e) for n in SESS for r, f in falls[n].items() for e in f["eps"] if e["at"] == "inside"]
print(f"-- falls inside a process, in the window, all four kinds: {len(ins)}: {[(n, r, e['onset_s']) for n, r, e in ins]}")
xs = [(n, r) for n in SESS for r, f in falls[n].items() for e in f["eps"] if e["starts_before_window"]]
print(f"-- episodes that began before the window and reach into it: {len(xs)} {xs}")

# ---------------------------------------------------------------------------------------------------------------- C3
print("\n== C3. Today's die against E84's die line, with the line's own fit error")
def sus_pts(path):
    return [(r["sus_w_mean"], r["sus_die_mean"]) for r in json.load(open(path))["runs"]
            if r.get("block") in ("SUS", "SUS2") and r.get("sus_w_mean") is not None and r.get("sus_die_mean") is not None]
p84, p114 = sus_pts(RES["E84"]), sus_pts(RES["E114"])
n84 = len(p84)
mx = st.mean(w for w, _ in p84)
my = st.mean(d for _, d in p84)
sxx = sum((w - mx) ** 2 for w, _ in p84)
b = sum((w - mx) * (d - my) for w, d in p84) / sxx
a = my - b * mx
s84 = math.sqrt(sum((d - (a + b * w)) ** 2 for w, d in p84) / (n84 - 2))
dev = [d - (a + b * w) for w, d in p114]
m, sd = st.mean(dev), st.stdev(dev)
se114 = sd / math.sqrt(len(dev))
xbar = st.mean(w for w, _ in p114)
seline = s84 * math.sqrt(1 / n84 + (xbar - mx) ** 2 / sxx)
tot = math.hypot(se114, seline)
df_ws = tot ** 4 / (se114 ** 4 / (len(dev) - 1) + seline ** 4 / (n84 - 2))
t_ws = T975[min(k for k in T975 if k >= math.floor(df_ws))] if math.floor(df_ws) <= 24 else 2.064
print(f"   E84's line over its {n84} sustained runs: {a:.3f} + {b:.4f} C per W, residual sd {s84:.3f} C (df {n84 - 2})")
print(f"   E114, {len(dev)} runs: mean die minus that line {m:+.3f} C, sd {sd:.3f}; within-session se {se114:.3f}, "
      f"95% +-{T975[len(dev) - 1] * se114:.3f} (t {T975[len(dev) - 1]}, df {len(dev) - 1}): the README's +-0.33")
print(f"   the line's own se at E114's mean board W ({xbar:.2f} W, E84's mean {mx:.2f} W): {seline:.3f} C")
print(f"   combined se {tot:.3f} C; Welch-Satterthwaite df {df_ws:.1f}, t {t_ws}: 95% +-{t_ws * tot:.3f} C "
      f"(-> {m - t_ws * tot:+.2f} to {m + t_ws * tot:+.2f}); with t(13) 2.160: +-{2.160 * tot:.3f}")

# ---------------------------------------------------------------------------------------------------------------- C4
print("\n== C4. Random fp16 today against E84's single run, in matched units; the window against the run")
c114 = json.load(open(RES["E114"]))["cells"]["fp16/randn"]
e = c114["e84"]
r_now, r_then = c114["rate"]["mean"], e["rate"]
f_now, f_then = c114["mhz"]["mean"], e["mhz"]
print(f"   rate {r_now} against {r_then} TFLOPS: {100 * (r_now / r_then - 1):+.1f}%; sampled clock {f_now} against {f_then} MHz: "
      f"{100 * (f_now / f_then - 1):+.1f}% ({f_now - f_then:+.1f} MHz)")
rho = json.load(open(RES["E114"]))["rho"]["fp16"]
print(f"   rho16 today {rho['mean']} (95% {rho['lo']}-{rho['hi']}); E84's single pair {rho['e84']}")
spans = []
for run in session_runs("E114"):
    spans.append((max(p["b"] for p in run["procs"]) - run["procs"][0]["a"]) / 1000.0)
print(f"   work per run, first kernel of the first process to the end of the ninth: {min(spans):.1f}-{max(spans):.1f} s "
      f"(median {st.median(spans):.1f}); the rules read the last 40 s")

# ---------------------------------------------------------------------------------------------------------------- C1
print("\n== C1. What E114 asked of the PMIC, by count (et-platform 836a4ab; E118's CHANGE-RECORD lists the handlers)")
ident = open(os.path.join(D, "ident", "ident-141810.out")).read()
print(f"   the revisions query (DM_CMD_GET_MODULE_FIRMWARE_REVISIONS) in ident/ident-141810.out: "
      f"{ident.count('Service request succeeded')} call, 'PMIC Firmware versions' line present: {'PMIC Firmware versions' in ident}")
ntel = sum(r["n_tel"] for r in session_runs("E114"))
smoke = jl(os.path.join(D, "smoke", "runs.jsonl"))
print(f"   sampler readings in the 15 sustained runs: {ntel} (each one sends GET_ASIC_VOLTAGE and GET_MODULE_VOLTAGE, "
      f"which read PMIC voltage registers; no write); smoke runs: {len(smoke)}")
nq = sum(1 for _ in open(os.path.join(D, "s1", "runs.jsonl"))) + len(jl(os.path.join(D, "s1", "queries.jsonl")))
print(f"   ettelem config reads in the session: {nq} (after each of the 15 runs, and the start and end queries), plus the "
      f"start and closing reads in ident/; each sends GET_ASIC_VOLTAGE")

# ---------------------------------------------------------------------------------------------------------------- C8
print("\n== C8 (post hoc). Card 0's error events in the host's kernel log, from other lanes' committed reads")
q = open(os.path.join(DATA, "2026-11-01-q132-governor-desk", "host", "err-aifoundry1.txt")).read()
hdr = re.search(r"== aifoundry1 (\S+) (\S+) PDT up ([0-9.]+) s", q)
kinds = re.search(r"events by device and kind: (\{.*\})", open(os.path.join(DATA, "2026-11-01-q132-governor-desk", "host",
                                                                               "err2-aifoundry1.txt")).read())
n_q132 = sum(int(x) for x in re.findall(r"'0000:01:00\.0', '[^']+'\): (\d+)", kinds.group(1)))
cr = open(os.path.join(REPO, "tools", "claims-v3", "e118", "CHANGE-RECORD.md")).read()
m118 = re.search(r"`Error Event Detected` (\d+) \(the last at host uptime ([0-9,]+) s", cr)
print(f"   Q132(g), host/err-aifoundry1.txt: {hdr.group(1)} {hdr.group(2)} PDT, host up {hdr.group(3)} s: card 0's events "
      f"{n_q132} ({kinds.group(1)})")
print(f"   E118, tools/claims-v3/e118/CHANGE-RECORD.md (read 14:50:39 PST): card 0's 'Error Event Detected' {m118.group(1)}, "
      f"the last at host uptime {m118.group(2)} s; between the two reads {int(m118.group(1)) - n_q132}")
y, mo, d_ = (int(x) for x in hdr.group(1).split("-"))
hh, mm, ss = (int(x) for x in hdr.group(2).split(":"))
boot = dt.datetime(y, mo, d_, hh, mm, ss, tzinfo=dt.timezone(dt.timedelta(hours=-7))).timestamp() - float(hdr.group(3))
pst = dt.timezone(dt.timedelta(hours=-8))
ev = boot + 520656.762068   # the last line's own stamp, quoted in E118's gates read
print(f"   host boot from Q132(g)'s read: {dt.datetime.fromtimestamp(boot, dt.timezone(dt.timedelta(hours=-7))):%d %b %H:%M:%S.%f} PDT; "
      f"the last event (stamp 520656.762068 s) at {dt.datetime.fromtimestamp(ev, pst):%H:%M:%S.%f} PST by that boot time")
runs = jl(os.path.join(D, "s1", "runs.jsonl"))
lastq = runs[-1]["queries"]["residency"]
endq = jl(os.path.join(D, "s1", "queries.jsonl"))[-1]["residency"]
for lab, rs in (("last run's after-run read", lastq), ("session's end read", endq)):
    print(f"   E114 {lab}: residency states " + ", ".join(f"{x['state']} rc {x['rc']} at "
          f"{dt.datetime.fromtimestamp(x['t_ms'] / 1000, pst):%H:%M:%S.%f}" for x in rs))
n_res_err = sum(1 for r in runs for x in r["queries"]["residency"] if x["rc"] != 0) + \
    sum(1 for qq in jl(os.path.join(D, "s1", "queries.jsonl")) for x in qq["residency"] if x["rc"] != 0)
print(f"   E114's residency reads that returned an error (states 4-6, rc -5), every run plus start and end: {n_res_err}")
rings = sorted(os.listdir(os.path.join(D, "s1", "sp")))
cnt = {}
for fn in rings:
    b = open(os.path.join(D, "s1", "sp", fn), "rb").read()
    cnt[fn[:-4]] = (len(re.findall(rb"Unexpected power thro[a-z]*ling state", b)), b.count(b"get_throttle_time"))
print("   E114's own trace-ring dumps (s1/sp/*.bin, 8 KB each, the latest records only), counts of the service processor's")
print("   'Unexpected power throtlling state' and 'thermal pwr mgmt error: get_throttle_time()' lines (E77's amendment A1 ties")
print("   them to reads of throttle states 5 and 6):")
for k, (a1, a2) in cnt.items():
    print(f"      {k:26s} {a1} and {a2}")
