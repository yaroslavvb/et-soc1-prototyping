#!/usr/bin/env python3
"""E80 amendment A1 (POST HOC, labelled; it changes no registered verdict): the governor's idle reset inside a
launch, found from the sampler alone, and the burst and sustained views with those samples set aside.

    python3 posthoc_idle.py <results.json> <RUNDIR> [<RUNDIR> ...] [--out posthoc-idle.json] > posthoc-idle.txt

The behaviour is documented in docs/findings/14-card-behaviour.md, "A one-second idle reset inside a launch
(aifoundry2, 23 October 2026, E63)": the clock falls from 800 MHz straight to the boot point, 600 MHz, for 0.6-1.5 s
while the work runs on at the lower clock, then climbs back through 700. It is neither of the governor's limits and
neither E64's governor model nor E64-T1 has it. Its sampler signature, used here and nothing else:

  DIP        a work sample at 600 MHz whose previous sample read 800 MHz (no 700 between: a power step and a thermal
             step both go one point at a time), more than 1.5 s after its process started and more than 0.3 s before
             that process ended; the dip runs from that sample until the clock next reads 800 or the process ends.
  LATE RAMP  a process whose first 800 MHz sample comes more than 1.2 s after its start (E63's measured launch-to-800
             maximum, the same findings section); the late-ramp samples run from 1.2 s after the start to that first
             800 MHz sample, and are flagged only when every one of them reads a die under 65 C and a board under 65 W
             (so that no limit can be what holds the clock).
  (A DIP also needs its first sample's die reading under 65 C.)

Views (each beside, never instead of, the registered number):
  * burst: the mean clock over the registered window (1.5 s to the end of the work) without DIP and LATE-RAMP
    samples, per run and per kind, and the R1 / R7 / S2 numbers on those means;
  * sustained: the registered limit labels recomputed with DIP and LATE-RAMP samples left out of every share
    (`none` at >= 90% at 800 of what is left, then thermal / power at >= 50% of what is below 800), and R2 on them.
"""
import argparse
import json
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hpl"))
import reduce_hpl as RH  # noqa: E402

RAMP_MAX_S = 1.2
DIP_FROM_START_S = 1.5
DIP_BEFORE_END_S = 0.3


def rms(xs):
    xs = [x for x in xs if x is not None]
    return round(math.sqrt(sum(x * x for x in xs) / len(xs)), 2) if xs else None


def flags(m):
    """per trace index: 'dip' / 'late' / None, over the work samples; and the episode list."""
    tr = m["trace"]
    starts = m.get("proc_spans") or []
    lab = [None] * len(tr)
    eps = []
    for (a, b) in starts:
        idx = [i for i, x in enumerate(tr) if a <= x[0] <= b]
        if not idx:
            continue
        first800 = next((tr[i][0] for i in idx if tr[i][3] == 800), None)
        late = [i for i in idx if first800 is not None and a + RAMP_MAX_S < tr[i][0] < first800]
        # only a ramp that nothing could be holding back: the process does reach 800, and while it waits the die
        # reads under 65 C and the board under 65 W (otherwise a limit may be what holds it, and it is not flagged)
        if late and all((tr[i][1] is None or tr[i][1] < 65) and (tr[i][2] is None or tr[i][2] < 65) for i in late):
            for i in late:
                lab[i] = "late"
            eps.append({"kind": "late_ramp", "t_s": round(a, 2), "first800_s": first800, "samples": len(late)})
        i_prev = None
        k = 0
        while k < len(idx):
            i = idx[k]
            x = tr[i]
            if (i_prev is not None and x[3] == 600 and tr[i_prev][3] == 800 and x[0] - a > DIP_FROM_START_S
                    and b - x[0] > DIP_BEFORE_END_S and (x[1] is None or x[1] < 65)):
                j = k
                n = 0
                while j < len(idx) and tr[idx[j]][3] != 800:
                    lab[idx[j]] = "dip"
                    n += 1
                    j += 1
                eps.append({"kind": "dip", "t_s": round(x[0], 2), "samples": n,
                            "w_before": tr[i_prev][2], "w_in": x[2], "die": x[1]})
                i_prev = idx[j - 1]
                k = j
                continue
            i_prev = i
            k += 1
    return lab, eps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args()
    R = json.load(open(a.results))
    spans = {}
    for rd in a.rundirs:
        for L in RH.jl(os.path.join(rd, "launches.jsonl")):
            if L.get("role") == "work":
                spans.setdefault(L["run"], []).append((L["t_start_ms"], L["t_end_ms"]))
    for m in R["runs"]:
        sp = sorted(spans.get(m["run"], []))
        t0 = sp[0][0] if sp else None
        m["proc_spans"] = [((x - t0) / 1000.0, (y - t0) / 1000.0) for x, y in sp] if sp else []
    out = {"amendment": "A1", "note": "POST HOC, labelled; no registered verdict changes", "runs": {}, "kinds": {}}
    for m in R["runs"]:
        if m.get("kind") is None:
            continue
        lab, eps = flags(m)
        tr = m["trace"]
        r = {"block": m["block"], "kind": m["kind"], "episodes": eps,
             "n_dip_samples": lab.count("dip"), "n_late_samples": lab.count("late")}
        if m["block"] == "BURST":
            keep = [x[3] for x, l in zip(tr, lab) if 1.5 <= x[0] <= m["work_s"] and x[3] in (600, 700, 800)
                    and l is None]
            r["burst_mhz_registered"] = m.get("burst_mhz")
            r["burst_mhz_without"] = round(st.mean(keep), 1) if keep else None
        if m["block"] == "SUS":
            t_end = m["work_s"]
            last = [(x, l) for x, l in zip(tr, lab) if t_end - 40.0 <= x[0] <= t_end and x[3] in (600, 700, 800)]
            # the registered per-sample labels are not stored per sample; recompute the sampler-only parts the same
            # way reduce_hpl does (a reading >= 66 C in the 2 s before = thermal), the governor-line part is not
            # available per sample, so this view is the sampler-only one (A3's second column)
            ws = [x for x in tr if 0 <= x[0] <= t_end]
            kept = [x for x, l in last if l is None]
            n800 = sum(1 for x in kept if x[3] == 800)
            below = [x for x in kept if x[3] != 800]
            hot = [x for x in below if any(y[1] is not None and y[1] >= 66 for y in ws if x[0] - 2.0 <= y[0] <= x[0])]
            share800 = n800 / len(kept) if kept else None
            if share800 is None:
                lim = None
            elif share800 >= 0.9:
                lim = "none"
            elif below and len(hot) / len(below) >= 0.5:
                lim = "thermal"
            else:
                lim = "power_or_other"
            r.update({"sus_share800_without": round(share800, 3) if share800 is not None else None,
                      "sus_hot_share_of_below_without": round(len(hot) / len(below), 3) if below else None,
                      "sus_limit_without_sampler_only": lim, "sus_limit_registered": m.get("limit"),
                      "sus_mhz_registered": m.get("sus_mhz_mean"),
                      "sus_mhz_without": round(st.mean([x[3] for x in kept]), 1) if kept else None})
        out["runs"][m["run"]] = r
    C = R["cells"]
    for k, c in C.items():
        rr = [v for v in out["runs"].values() if v["kind"] == k]
        b = [v["burst_mhz_without"] for v in rr if v["block"] == "BURST" and v.get("burst_mhz_without") is not None]
        s = [v for v in rr if v["block"] == "SUS"]
        out["kinds"][k] = {"burst_mhz_without": round(st.mean(b), 1) if b else None,
                           "pred_burst_reg": c.get("pred_burst_reg"), "pred_burst_q130c": c.get("pred_burst_q130c"),
                           "dips": sum(len([e for e in v["episodes"] if e["kind"] == "dip"]) for v in rr),
                           "late_ramps": sum(len([e for e in v["episodes"] if e["kind"] == "late_ramp"]) for v in rr),
                           "sus_limits_without": [v.get("sus_limit_without_sampler_only") for v in s],
                           "pred_limit": c.get("pred_limit")}
    K = out["kinds"]
    have = [v for v in K.values() if v["burst_mhz_without"] is not None]
    out["views"] = {
        "R1_rms_without_mhz": rms([v["burst_mhz_without"] - v["pred_burst_reg"] for v in have]),
        "R7_predicted_800_below_790_without": [k for k, v in K.items() if v["burst_mhz_without"] is not None
                                               and v["pred_burst_q130c"] >= 800 and v["burst_mhz_without"] < 790],
        "R2_right_without": sum(1 for v in K.values() if v["sus_limits_without"] and all(
            (x if x != "power_or_other" else "power") == v["pred_limit"] for x in v["sus_limits_without"])),
        "R2_population": sum(1 for v in K.values() if v["sus_limits_without"]),
        "dip_episodes": sum(v["dips"] for v in K.values()),
        "late_ramp_episodes": sum(v["late_ramps"] for v in K.values()),
        "processes": sum(len(m.get("proc_spans") or []) for m in R["runs"] if m.get("kind")),
    }
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
    print("A1 post hoc (no verdict changes):", json.dumps(out["views"]))
    for k, v in K.items():
        print(f"  {k:15s} burst without {v['burst_mhz_without']!s:>6} (pred {v['pred_burst_reg']}) dips {v['dips']} "
              f"late {v['late_ramps']} sus limits without {v['sus_limits_without']} (pred {v['pred_limit']})")
    return 0


if __name__ == "__main__":
    main()
