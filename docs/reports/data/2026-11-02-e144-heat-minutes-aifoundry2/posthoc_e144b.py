#!/usr/bin/env python3
"""E144b post hoc readings (written after the data; NO verdict, nothing registered changes). Run from the top of the repository:

    /usr/bin/python3 docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/posthoc_e144b.py > docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/posthoc.txt

1. G1's measured rise at Q138(t)'s checkpoints (60 s, 2, 5, 10 min after the hold's first sample; 10-s means over the REST's last-120-s
   anchor) beside the frozen planned-power curve (predictions-e144.json aifoundry2.G1.rise_C_by_s). The registered (b) for G1 reads the
   plateau only.
2. The board: each hold's rise over its REST (median) over the last 300 s, beside the planned trace's (G1 17.836 W; G2's floor rule uses
   E111's 32.42 W), and the idle board and die before each hold.
3. G2's clock timeline: the first sample at >= 790 MHz, the first step down to <= 610 MHz after it, the die's first reading of 66, and the
   last sample above 610 MHz (after it the clock stayed at the floor).
4. The idle before and after: each REST's die and board (G1, END, G2, END2).
"""
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PRED = json.load(open(os.path.join(HERE, "..", "2026-11-02-q138t-heat-model", "predictions-e144.json")))["aifoundry2"]


def rows(path):
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt", errors="replace") as f:
        for ln in f:
            if ln.startswith("{"):
                d = json.loads(ln)
                ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                out.append((d["t_ms"] / 1000.0, d.get("board_w"), ms[0], (d.get("mhz") or {}).get("minion")))
    return out


def files(step):
    t = os.path.join(HERE, step, "tel")
    fs = sorted(os.listdir(t))
    return {("REST" if f.startswith("REST") else "HOLD"): os.path.join(t, f) for f in fs}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    return xs[len(xs) // 2] if xs else None


def rest_reading(rr):
    t1 = rr[-1][0]
    last = [r for r in rr if r[0] >= t1 - 120]
    return {"die_C": mean([r[2] for r in last]), "board_W_median": median([r[1] for r in rr]), "die_first": rr[0][2], "die_last": rr[-1][2]}


def main():
    print("E144b post hoc readings (not registered; no verdict)\n")
    for step in ("G1", "END", "G2", "END2"):
        fs = files(step)
        print(f"{step} REST: {json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rest_reading(rows(fs['REST'])).items()})}")
    print()
    for step in ("G1", "G2"):
        fs = files(step)
        rr, hh = rows(fs["REST"]), rows(fs["HOLD"])
        a = rest_reading(rr)
        t0, t1 = hh[0][0], hh[-1][0]
        last = [r for r in hh if r[0] >= t1 - 300]
        rise_w = mean([r[1] for r in last]) - a["board_W_median"]
        rise_c = mean([r[2] for r in last]) - a["die_C"]
        print(f"== {step}: hold {t1 - t0:.0f} s; last 300 s: die {mean([r[2] for r in last]):.3f} C (rise {rise_c:.3f} over the REST anchor "
              f"{a['die_C']:.3f}), board {mean([r[1] for r in last]):.2f} W (rise {rise_w:.2f} over the REST median {a['board_W_median']:.2f})")
        if step == "G1":
            pr = PRED["G1"]
            print(f"   planned board rise {pr['plateau_board_rise_W']} W; measured {rise_w:.2f} W ({rise_w - pr['plateau_board_rise_W']:+.2f}); "
                  f"the chain's R 0.663 x the measured rise = {0.663 * rise_w:.2f} C against the planned {pr['plateau_rise_C']} C")
            print("   checkpoint   measured rise   frozen (b)   measured - frozen")
            for sec in (60, 120, 300, 600):
                k = [r[2] for r in hh if t0 + sec - 5 <= r[0] < t0 + sec + 5]
                m = mean(k) - a["die_C"]
                f = pr["rise_C_by_s"][str(sec)]
                print(f"   {sec:5d} s      {m:8.3f}       {f:8.3f}      {m - f:+.3f}")
        else:
            print(f"   the floor rule's board rise (E111's) 32.42 W; measured {rise_w:.2f} W ({rise_w - 32.42:+.2f}); 0.663 x the measured rise = "
                  f"{0.663 * rise_w:.2f} C against the frozen 21.49 C")
            fast = next((r for r in hh if r[3] is not None and r[3] >= 790), None)
            down = next((r for r in hh if fast and r[0] > fast[0] and r[3] is not None and r[3] <= 610), None)
            d66 = next((r for r in hh if r[2] is not None and r[2] >= 66), None)
            above = [r for r in hh if r[3] is not None and r[3] > 610]
            at800 = sum(1 for r in hh if r[3] is not None and r[3] >= 790)
            print(f"   first sample >= 790 MHz: {None if not fast else round(fast[0] - t0, 1)} s (die {fast and fast[2]}, board {fast and fast[1]} W)")
            print(f"   first step down to <= 610 MHz after it: {None if not down else round(down[0] - t0, 1)} s (die {down and down[2]}, board {down and down[1]} W)")
            print(f"   the die's first reading of 66: {None if not d66 else round(d66[0] - t0, 1)} s")
            print(f"   last sample above 610 MHz: {None if not above else round(above[-1][0] - t0, 1)} s ({above and above[-1][3]} MHz); "
                  f"samples at >= 790 MHz: {at800} of {len(hh)} ({at800 / 10.0:.1f} s at 10 Hz)")
            pk = max(hh, key=lambda r: r[1] or 0)
            print(f"   board peak {pk[1]} W at {pk[0] - t0:.1f} s ({pk[3]} MHz); samples over 85 W: {sum(1 for r in hh if (r[1] or 0) > 85)}, over 90 W: "
                  f"{sum(1 for r in hh if (r[1] or 0) > 90)}")


if __name__ == "__main__":
    main()


def counts():
    """5. What was sent, counted from the records: sampler lines (each one ettelem sample: 6 READ commands), the per-run and end queries
    (queries.jsonl: an sptrace, the residency read answered unsent, an ettelem config), the queue's config reads (snapshot-start/end), and
    the residency reads answered unsent (e144b-not-sent.jsonl)."""
    tot = {"sampler_lines": 0, "queries_records": 0, "queue_config_reads": 0, "residency_not_sent": 0}
    print("\n5. Commands, counted from the records (every one a READ; the residency read never sent)")
    for step in ("SMOKE", "STOPTEST-DIE", "STOPTEST-BOARD", "G1", "END", "G2", "END2"):
        d = os.path.join(HERE, step)
        n_tel = sum(1 for f in os.listdir(os.path.join(d, "tel")) for _ in rows(os.path.join(d, "tel", f)))
        n_q = sum(1 for _ in open(os.path.join(d, "queries.jsonl"))) if os.path.exists(os.path.join(d, "queries.jsonl")) else 0
        n_c = sum(1 for t in ("start", "end") if os.path.exists(os.path.join(d, f"config-{t}.txt")))
        n_ns = sum(1 for _ in open(os.path.join(d, "e144b-not-sent.jsonl"))) if os.path.exists(os.path.join(d, "e144b-not-sent.jsonl")) else 0
        for k, v in (("sampler_lines", n_tel), ("queries_records", n_q), ("queue_config_reads", n_c), ("residency_not_sent", n_ns)):
            tot[k] += v
        print(f"   {step:15s} sampler lines {n_tel:6d}  queries {n_q:3d}  queue config reads {n_c}  residency answered unsent {n_ns}")
    print(f"   total: {json.dumps(tot)}")


if __name__ == "__main__":
    counts()
