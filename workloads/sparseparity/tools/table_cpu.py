#!/usr/bin/env python3
"""table_cpu.py: the CPU baseline tables from bench_cpu.py's bench.jsonl (markdown on stdout).

  table_cpu.py DATA_DIR [DATA_DIR2 ...] [--json]     (a later directory's runs of a label replace an earlier one's)

Times are per full solve: the median of the repetitions, with the range (min-max). A 1/64 slice (L5) is scaled by
C(n,k) / subsets scanned. Two-stage rows add stage 2 (the rescoring of the survivors on all m samples) to stage 1.
16 threads (8 cores x 2 SMT threads on the i7-11700K) are extrapolated, not measured, as a range: the fast end is
t6 * 6/8 / max(U, 1), linear from 6 to 8 cores times the SMT uplift U measured on one core (2 threads on core 0's
two hyperthreads against 1 thread); the slow end adds the 7th and 8th cores at the measured 4 -> 6 step efficiency,
with no SMT gain.

CPU energy is not measured and not bounded: the RAPL counter is root-only on the lab hosts and the board lifts both
package power limits to 4,095 W (powercap.txt in the data directory). It is ESTIMATED as P * t at an ASSUMED package
power of 125-251 W (the i7-11700K's rated PL1 and PL2), and labelled as such.

The summary pairs every card method (DESIGN.md's predictions, recomputed by design_model.py: P) with the CPU's best
measured method at that size, and states each side's chance of returning the secret.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

P_ASSUMED = (125.0, 251.0)   # W, assumed package power (the part's PL1 and PL2); not measured, not a bound
REPO = Path(__file__).resolve().parents[3]
SIZES = {"C0": (32, 3, 0.1, 128), "C1": (128, 4, 0.2, 192), "L1": (512, 4, 0.3, 448), "L2": (512, 4, 0.4, 1850),
         "F5": (256, 5, 0.4, 1925), "L5": (512, 5, 0.4, 2151)}
TWO = [("L2", 832, 80), ("L2", 1024, 104), ("F5", 1024, 104), ("F5", 1280, 144), ("L5", 1024, 104), ("L5", 1280, 144)]
CARD_M1 = {"L2": 832, "F5": 1024, "L5": 1280}   # the card's two-stage m1: DESIGN.md's, and F5's from design_model.py


def design_model():
    spec = importlib.util.spec_from_file_location("design_model", REPO / "docs/research/sparse-parity/design_model.py")
    dm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dm)
    return dm


def fmt(t):
    if t is None:
        return "-"
    for lim, div, unit in ((1e-3, 1e-6, "us"), (1, 1e-3, "ms"), (120, 1, "s"), (7200, 60, "min")):
        if t < lim:
            return f"{t / div:.3g} {unit}"
    return f"{t / 3600:.3g} h"


def f2(x, spec):
    return "-" if x is None or x == "" else format(x, spec)


def load(d: Path):
    return [json.loads(x) for x in (d / "bench.jsonl").read_text().splitlines() if x.strip()]


def times(r):
    """(median, min, max) seconds per full solve of one run (a slice scaled up by its candidate fraction)"""
    if r["cmd"] == "vexh":
        f = r["fraction"]
        return (r.get("wall_med_s", r["wall_s"]) / f, r["wall_s"] / f, r.get("wall_max_s", r["wall_s"]) / f)
    if r["cmd"] == "batch":
        return (r.get("wall_med_s", r["wall_s"]), r["wall_s"], r.get("wall_max_s", r["wall_s"]))
    w = r.get("wall_s")
    return (w, w, w)


def stage2(r):
    return (r["stage2_s"] / r["fraction"]) if "stage2_s" in r else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="+", help="bench directories; a later one's runs of a label replace an earlier one's")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows = []
    for d in a.data:
        new = load(Path(d))
        labels = {r["label"] for r in new}
        rows = [r for r in rows if r["label"] not in labels] + new
    bad = [r for r in rows if r.get("rc") not in (0, None) or "parse_error" in r]
    by = defaultdict(list)
    for r in rows:
        by[(r["label"], r.get("threads"), r["place"])].append(r)
    dm = design_model()
    out = {}

    # ---- vexh thread scaling
    print("## vexh (AVX-512, 8 candidates per register) and batch: per full solve, median of the repetitions\n")
    print("| size | (n, k, eta, m) | Wm | reps | 1 thread | 2 | 4 | 6 (range) | smt2 (1 core) | speedup 6T | "
          "4->6 step eff. | SMT uplift U | 16T extrapolated | ns/subset (1T) | clock 1T / 6T (MHz) | result |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    labels = [("C0", "vexh C0"), ("C1", "vexh C1"), ("L1", "vexh L1"), ("L2", "vexh L2"), ("F5", "vexh F5"),
              ("L5 (1/64 slice)", "vexh L5/64")]
    labels += [(f"{n} two-stage m1={m1}", f"vexh {n}{'/64' if n == 'L5' else ''} two-stage m1={m1}") for n, m1, _ in TWO]
    labels += [("B1 (1,024 instances, 8 per register)", "batch B1"),
               ("B1, one instance per thread (old)", "batch B1 vexh-per-instance")]
    for name, lab in labels:
        t, rr = {}, {}
        for th in (1, 2, 4, 6):
            if by.get((lab, th, "cores")):
                r = by[(lab, th, "cores")][-1]
                med, lo, hi = times(r)
                s2 = stage2(r)
                t[th], rr[th] = (med + s2, lo + s2, hi + s2), r
        sm = by.get((lab, 2, "smt2"))
        tsm = (times(sm[-1])[0] + stage2(sm[-1])) if sm else None
        if not t:
            continue
        tb = min(t, key=lambda x: t[x][0])
        t1 = t.get(1, (None,))[0]
        t6 = t.get(6, (None,))[0]
        r1 = rr.get(1) or rr[tb]
        U = t1 / tsm if (tsm and t1) else None
        sp6 = t1 / t6 if (t1 and t6) else None
        eff46 = ((t[4][0] / t[6][0]) / 1.5) if (4 in t and 6 in t) else None
        t16 = t6 * 6 / 8 / max(U or 1.0, 1.0) if t6 else None
        t16c = t6 / (1 + (8 / 6 - 1) * min(eff46, 1.0)) if (t6 and eff46) else None
        key = name.split()[0]
        inst = SIZES.get(key)
        instr = f"({','.join(map(str, inst))})" if inst else ("(64,4,0.1,64) x 1,024" if "B1" in name else "")
        if "two-stage" in name and inst:
            instr = f"({inst[0]},{inst[1]},{inst[2]},{r1['m']}), tau1 {r1.get('tau')}, rescored at {r1.get('m2')}"
        if r1["cmd"] == "vexh":
            res = "ok" if all(x.get("ok", 1) == 1 for x in rr.values()) else "not solved"
        else:
            res = f"{r1['solved']}/{r1['count']} solved"
        sliced = r1.get("slice", 1) > 1
        if sliced:
            res = "n/a (a slice need not hold the secret)"
        if "two-stage" in name:
            sv = r1.get("survivors")
            res = (f"survivors {sv}" + (f" in the slice (x{1 / r1['fraction']:.0f} = {sv / r1['fraction']:.3g})" if sliced
                                        else f", secret kept {r1.get('secret_survived')}, stage 2 ok {r1.get('stage2_ok')}"))
        rng = f"{fmt(t[6][0])} ({fmt(t[6][1])}-{fmt(t[6][2])})" if 6 in t else "-"
        print(f"| {name} | {instr} | {r1.get('Wm', 1)} | {r1.get('reps', 1)} | {fmt(t1)} | {fmt(t.get(2, (None,))[0])} | "
              f"{fmt(t.get(4, (None,))[0])} | {rng} | {fmt(tsm)} | {f2(sp6, '.2f')}x | {f2(eff46, '.2f')} | "
              f"{f2(U, '.2f')} | {fmt(t16)} - {fmt(t16c)} | {f2(r1.get('ns_per_subset', ''), '.3f')} | "
              f"{r1.get('mhz_mean') or '-'} / {(rr[6].get('mhz_mean') if 6 in rr else None) or '-'} | {res} |")
        out[name] = dict(t1=t1, t6=t6, t6_min=t[6][1] if 6 in t else None, t6_max=t[6][2] if 6 in t else None,
                         tsmt2=tsm, U=U, t16_fast=t16, t16_slow=t16c, best=t[tb][0], best_threads=tb,
                         stage2_6T=stage2(rr[6]) if 6 in rr else None, survivors=r1.get("survivors"),
                         fraction=r1.get("fraction", 1.0))

    # ---- two-stage screens: tau1, P(kept), survivors
    print("\n## Two-stage screens (stage 1 on the first m1 samples, stage 2 rescoring on all m): the CPU's side\n")
    print("| size | m1 | tau1 | P(secret kept) (binomial) | survivors: predicted / measured | stage 1, 6T (median) | "
          "stage 2, 6T | total 6T | total 16T extrapolated | one stage 6T |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name, m1, tau in TWO:
        o = out.get(f"{name} two-stage m1={m1}")
        n, k, eta, m = SIZES[name]
        pk, surv = dm.screen_at(n, k, eta, m1, tau)
        one = out.get("L5 (1/64 slice)" if name == "L5" else name)
        if not o:
            continue
        meas = o["survivors"] / o["fraction"] if o.get("survivors") is not None else None
        print(f"| {name} | {m1} | {tau} | {pk:.4f} | {surv:.3g} / {f2(meas, '.3g')} | "
              f"{fmt(o['t6'] - (o['stage2_6T'] or 0))} | {fmt(o['stage2_6T'])} | {fmt(o['t6'])} | "
              f"{fmt(o['t16_fast'])} - {fmt(o['t16_slow'])} | {fmt(one['t6']) if one else '-'} |")
        o["p_kept"] = pk

    # ---- mitm
    print("\n## mitm: bucketed meet in the middle with the random halving (per solve; random repetitions)\n")
    print("| size | threads | seeds | r | split | ok | wall s: median / mean (range) | expected (this seed's 1/q, "
          "or the cap when the secret cannot clear the threshold): median / mean | seeds that cannot clear it |")
    print("|---|---|---|---|---|---|---|---|---|")
    mitm = {}
    for name in ("C0", "C1", "L1", "L2", "F5"):
        for th in (1, 6):
            rs = by.get((f"mitm {name}", th, "cores"), [])
            if not rs:
                continue
            walls = [r["wall_s"] for r in rs]
            exps = [r.get("expected_s_full", r.get("expected_s_actual")) for r in rs]
            nocl = sum(1 for r in rs if r.get("can_accept", 1) == 0)
            print(f"| {name} | {th} | {len(rs)} | {rs[0]['r']} | {rs[0].get('split', 0)} | "
                  f"{sum(r['ok'] for r in rs)}/{len(rs)} | {st.median(walls):.3g} / {st.mean(walls):.3g} "
                  f"({min(walls):.3g}-{max(walls):.3g}) | {fmt(st.median(exps))} / {fmt(st.mean(exps))} | {nocl} |")
            mitm[(name, th)] = dict(median_s=st.median(walls), mean_s=st.mean(walls), ok=sum(r["ok"] for r in rs),
                                    n=len(rs), exp_median=st.median(exps), exp_mean=st.mean(exps), cannot_clear=nocl)
    for lab, name in (("mitm F5 reps", "F5"), ("mitm L5 reps", "L5")):
        for th in (1, 6):
            for r in by.get((lab, th, "cores"), []):
                e = r["wall_s"] / r["reps"] / r["q_actual"] if r.get("q_actual") else None
                print(f"| {name} (per-repetition sample: {r['reps']} reps) | {th} | 1 | {r['r']} | {r.get('split', 0)} | - | "
                      f"{r['wall_s']:.3g} | {fmt(e)} (1/q x wall per repetition, extrapolated) | - |")
                mitm[(name + " reps", th)] = dict(expected=e)
    for name in ("L1", "L2"):
        rs = [r for r in rows if r["label"] == f"mitm {name} r-sweep"]
        rn = [r for r in rows if r["label"] == f"mitm {name} r-sweep no-split"]
        if not rs:
            continue
        auto = sorted({r["r"] for r in rows if r["label"] == f"mitm {name}"})
        print(f"\nr sweep on {name}, seed 1 (6 threads, a fixed number of repetitions, no early stop; the automatic r "
              f"chose {auto}): expected solve time = wall per repetition x 1/q\n")
        print("| r | split | wall per repetition (6T) | 1/q (this seed) | verifications per repetition | "
              "expected solve, 6T |\n|---|---|---|---|---|---|")
        for r in sorted(rs, key=lambda x: x["r"]) + rn:
            wpr = r["wall_s"] / r["reps"]
            print(f"| {r['r']} | {r.get('split', 0)} | {wpr:.3g} s | {r['expected_reps_actual']:.3g} | "
                  f"{r['verifies'] / r['reps']:.3g} | {fmt(wpr * r['expected_reps_actual'])} |")

    # ---- correctness at scale and the other scans
    print("\n## Correctness at scale, and SP3's scan (spbits exh) for continuity\n")
    print("| run | threads | wall | answer ok | checksums = closed forms |\n|---|---|---|---|---|")
    for r in rows:
        if r["label"].startswith(("vexh sums", "spref", "spbits")):
            if r["cmd"] == "vexh":
                ok, cf = r["ok"], r["closed"]["match"]
            elif r["cmd"] == "scan":
                res = r.get("result", {})
                ok = res.get("ok")
                cf = r.get("closed", {}).get("match") if r.get("closed", {}).get("applies") else "n/a (a slice)"
                if "survivors" in r:
                    ok = f"{ok} (survivors {r['survivors']}, secret kept {r['secret_survived']})"
            else:
                ok, cf = r.get("ok"), "-"
            print(f"| {r['label']} | {r.get('threads')} | {fmt(r.get('wall_s'))} | {ok} | {cf} |")
    for f in sorted(p for d in a.data for p in Path(d).glob("*.merge.json")):
        try:
            m = json.loads(f.read_text())
            print(f"| planner merge of {f.name.split('.merge')[0]} (1,024 minions) | - | - | "
                  f"{m.get('ok_secret')} | {m.get('closed', {}).get('match', 'n/a (a slice)')}; merge ok {m['ok']} |")
        except (json.JSONDecodeError, KeyError):
            pass
    if bad:
        print(f"\n{len(bad)} runs failed: " + "; ".join(f"{r['label']} rc={r.get('rc')}" for r in bad))

    # ---- the summary: every card method against the CPU's best method at its size
    print("\n## The card's methods against the CPU's best method at each size\n")
    print("CPU: measured at 1-6 threads (median of the repetitions), 16 threads extrapolated. P(ok) is the chance of "
          "returning the secret: m is SP3's 99% sample count, and a two-stage screen also needs the secret to "
          "survive stage 1. CPU energy is an ESTIMATE at an ASSUMED 125-251 W package power, not a measurement and "
          "not a bound (the limits are lifted: powercap.txt). Card: DESIGN.md's model (design_model.py), M3 private "
          "loads / M4 cooperative loads, 32 shires at 600 MHz: predictions (P), nothing measured. A card two-stage "
          "row adds the host's stage 2 as the CPU measured it at 6 threads for the same m1 (M) and the survivors' "
          "readback at 8 GB/s (D).\n")
    print("| size | card method | card time, M3 / M4 (P) | card P(ok) | CPU's best method | CPU P(ok) | CPU 1T | "
          "CPU 6T (range) | CPU 16T extrapolated | CPU energy at 16T, assumed 125-251 W | CPU 16T / card M3 - M4 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")

    def cpu_best(size):
        """the fastest measured CPU method at 6 threads, full solve (stage 2 included)"""
        cands = []
        one = out.get("L5 (1/64 slice)" if size == "L5" else size)
        if one and one.get("t6"):
            cands.append(("vexh one stage", one, 0.99))
        for name, m1, tau in TWO:
            o = out.get(f"{name} two-stage m1={m1}")
            if name == size and o and o.get("t6"):
                cands.append((f"vexh two-stage m1 = {m1}, tau1 = {tau}", o, 0.99 - (1 - o.get("p_kept", 1.0))))
        mm = mitm.get((size, 6))
        if mm and one and mm["exp_mean"] < one["t6"]:
            # the mean over seeds of each seed's expected time; 16 threads: linear to 8 cores, +3% at the slow end
            m1t = mitm.get((size, 1))
            cands.append((f"mitm, expected over {mm['n']} seeds", dict(
                t1=m1t["exp_mean"] if m1t else None, t6=mm["exp_mean"], t6_min=None, t6_max=None,
                t16_fast=mm["exp_mean"] * 6 / 8, t16_slow=mm["exp_mean"] * 6 / 8 * 1.03), 0.99))
        return min(cands, key=lambda c: c[1]["t6"]) if cands else None

    summary = []
    for size in ("L1", "L2", "F5", "L5"):
        n, k, eta, m = SIZES[size]
        methods = [("one stage", m, None)]
        if size in CARD_M1:
            m1 = CARD_M1[size]
            tau = next(t for s, mm1, t in TWO if s == size and mm1 == m1)
            methods.append((f"two-stage m1 = {m1}, tau1 = {tau}", m1, tau))
        best = cpu_best(size)
        for label, ms, tau in methods:
            cp, cc = dict(dm.plan(n, k, ms, "private")), dict(dm.plan(n, k, ms, "coop"))
            pk, surv = dm.screen_at(n, k, eta, ms, tau) if tau else (1.0, 0.0)
            if tau:   # the host's stage 2 (measured on the CPU for this m1) and the survivors' readback
                o2 = out.get(f"{size} two-stage m1={ms}")
                s2 = (o2.get("stage2_6T") or 0.0) if o2 else 0.0
                extra = s2 + surv * 8 / dm.PCIE_BPS
                cp["t"] += extra
                cc["t"] += extra
            card_ok = 0.99 - (1 - pk)
            if not best:
                continue
            bl, bo, bp = best
            t16 = bo.get("t16_slow") or bo.get("t16_fast")
            ratio = f"{t16 / cp['t']:.2f} - {t16 / cc['t']:.2f}" if t16 else "-"
            rng = (f"{fmt(bo['t6'])} ({fmt(bo['t6_min'])}-{fmt(bo['t6_max'])})" if bo.get("t6_min") else fmt(bo["t6"]))
            en = f"{P_ASSUMED[0] * t16:.3g}-{P_ASSUMED[1] * t16:.3g} J" if t16 else "-"
            print(f"| {size} ({n},{k},{eta},{m}) | {label} | {fmt(cp['t'])} / {fmt(cc['t'])} | {card_ok:.3f} | {bl} | "
                  f"{bp:.3f} | {fmt(bo.get('t1'))} | {rng} | {fmt(bo.get('t16_fast'))} - {fmt(bo.get('t16_slow'))} | "
                  f"{en} | {ratio} |")
            summary.append(dict(size=size, card=label, card_p=cp["t"], card_c=cc["t"], cpu=bl, cpu_t16=t16))
    b1 = out.get("B1 (1,024 instances, 8 per register)")
    if b1:
        t16 = b1.get("t16_slow") or b1.get("t16_fast")
        print(f"| B1 1,024 x (64,4,0.1,64) | vector path, one instance per minion | 6-12 ms (DESIGN.md) | ~0.99 | "
              f"batch, 8 instances per register | ~0.99 | {fmt(b1['t1'])} | {fmt(b1['t6'])} "
              f"({fmt(b1['t6_min'])}-{fmt(b1['t6_max'])}) | {fmt(b1['t16_fast'])} - {fmt(b1['t16_slow'])} | "
              f"{P_ASSUMED[0] * t16:.3g}-{P_ASSUMED[1] * t16:.3g} J | {t16 / 12e-3:.2f} - {t16 / 6e-3:.2f} |")
    if a.json:
        print("\n```json\n" + json.dumps(dict(vexh=out, mitm={f"{k[0]}|{k[1]}": v for k, v in mitm.items()},
                                              summary=summary), indent=1, default=float) + "\n```")


if __name__ == "__main__":
    main()
