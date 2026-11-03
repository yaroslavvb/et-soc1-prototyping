#!/usr/bin/env python3
"""E144b (Q138): reduce the evening's aifoundry2 session. Registered before any E144b data; nothing here is fitted or tuned.

    /usr/bin/python3 tools/claims-v3/e144b/reduce_e144b.py <data dir> > <data dir>/reduce.txt      # writes <data dir>/results.json

1. The frozen inputs. Q138(t)'s files are hashed against their sha256 at amendment A1's commit c2f9920d (on origin before E144b's
   claim); any difference refuses (exit 2). The scorer is run as committed, never edited.
2. The registered verdicts are Q138(t)'s, applied mechanically by its own scorer:
       score_e144.py a2 <data>/G1 <data>/G2
   (a) the chain on the measured board trace, (b) the planned power (G1's plateau rise; G2's trip rule and regime), (c) G1's rise per
   board W and t63 (as frozen, and A1.8's closed reference beside it), with M6 as frozen beside every arm (A1.6). Each step dir holds one
   REST and one hold, so the scorer names the int8 -1s hold G1 and the fp32 randn hold G2 itself.
3. The sustained clock, E144b's own reading of Q138(t)'s frozen clock statements (registered here, before any data):
   * E144b-K1, G1 "800 MHz, the governor never trips": the share of the hold's samples over its last 300 s at >= 790 MHz.
     PASS >= 0.90 (E133's H-I8 read 0.960 and E111's 0.959-0.969: the samples between processes are the rest); FAIL < 0.80; else
     INCONCLUSIVE. Beside it, never a verdict: the share over the whole hold, the mean MHz, and the die's highest whole-degree reading
     (the governor's thermal step is at a reading of 66, E133 result 2).
   * G2's regime is Q138(t)'s (A1.3: "floor" when >= 98% of the last 300 s read 600 MHz, else "trip"), from the scorer. Beside it: the mean
     MHz over the last 300 s, and the first sample at or under 610 MHz after the hold's first launch (the governor's first step down), with
     the die reading then.
4. Safety, reported: the board's peak and the samples over 85 and 90 W, the die mean's and the hottest sensor's highest readings, per hold.
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
Q138T = os.path.join(ROOT, "docs/reports/data/2026-11-02-q138t-heat-model")
FROZEN = {  # sha256 at c2f9920d (Q138(t)'s amendment A1, 20:32:38 PST, on origin/main)
    "predictions-e144.json": "ae840f84bd36e80f822981913b3d44f314248669f56ff96dc2c2b61ced0a92d0",
    "amendment-a1.json": "a147f40c5225e6d213f6f907dae652961f2b7ae784fe56747dbf6d22b5726240",
    "model-q138t.json": "268b47fd580b330738eb3e1c83ea392f3784aae348a658e7335b734a1168e8fa",
    "score_e144.py": "0569c49474da4058de4ad14c13d1081fa50ba2e7dd705d4a564835d94c2e1494",
    "heat_q138t.py": "9dbb288f896b7e588fbc155d67f32b1cb7089ffe4ede465c1380d2724d1fb49b",
    "fit_q138t.py": "0f21f77cb916bb65c85708b89a89a36e7add3146e098da38dd64b4077e9eb29a",
    "predict_e144.py": "313c6840337615b2c474c39f74f095737bf7a35ecc6f9d8ac2356478f6442512",
}
K1 = {"pass_min": 0.90, "fail_below": 0.80, "mhz_at": 790.0}
FLOOR_MHZ = 610.0


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def tel_lines(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", errors="replace") as f:
        for ln in f:
            if ln.startswith("{"):
                try:
                    d = json.loads(ln)
                except ValueError:
                    continue
                ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                yield (d.get("t_ms"), d.get("board_w"), ms[0], ms[2] if len(ms) > 2 else None, (d.get("mhz") or {}).get("minion"))


def hold_rows(step_dir):
    tdir = os.path.join(step_dir, "tel")
    hf = [f for f in sorted(os.listdir(tdir)) if f.startswith("HOLD")]
    if len(hf) != 1:
        return None, hf
    rows = [r for r in tel_lines(os.path.join(tdir, hf[0])) if r[0] is not None]
    return rows, hf[0]


def frac(xs, pred):
    xs = [x for x in xs if x is not None]
    return (sum(1 for x in xs if pred(x)) / len(xs)) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def clock_and_safety(step_dir):
    rows, name = hold_rows(step_dir)
    if not rows:
        return {"error": f"no single hold file: {name}"}
    t0, t1 = rows[0][0], rows[-1][0]
    last = [r for r in rows if r[0] >= t1 - 300000]
    out = {"hold_file": name, "dur_s": round((t1 - t0) / 1000.0, 1), "samples": len(rows),
           "last300": {"n": len(last), "mean_mhz": mean([r[4] for r in last]),
                       "share_ge_790": frac([r[4] for r in last], lambda m: m >= K1["mhz_at"]),
                       "share_le_610": frac([r[4] for r in last], lambda m: m <= FLOOR_MHZ)},
           "whole": {"mean_mhz": mean([r[4] for r in rows]), "share_ge_790": frac([r[4] for r in rows], lambda m: m >= K1["mhz_at"]),
                     "share_le_610": frac([r[4] for r in rows], lambda m: m <= FLOOR_MHZ)},
           "safety": {"board_peak_W": max((r[1] for r in rows if r[1] is not None), default=None),
                      "samples_over_85W": sum(1 for r in rows if r[1] is not None and r[1] > 85),
                      "samples_over_90W": sum(1 for r in rows if r[1] is not None and r[1] > 90),
                      "die_max_C": max((r[2] for r in rows if r[2] is not None), default=None),
                      "hottest_max_C": max((r[3] for r in rows if r[3] is not None), default=None)}}
    busy = [r for r in rows if r[1] is not None and r[1] > 30]
    if busy:
        tb = busy[0][0]
        step = next((r for r in rows if r[0] >= tb and r[4] is not None and r[4] <= FLOOR_MHZ and r[1] is not None and r[1] > 30), None)
        out["first_step_down"] = None if step is None else {"after_first_launch_s": round((step[0] - tb) / 1000.0, 1), "die_C": step[2],
                                                            "board_W": step[1], "mhz": step[4]}
    return out


def k1(c):
    s = (c.get("last300") or {}).get("share_ge_790")
    if s is None:
        return {"verdict": "NOT READ", "share": None}
    v = "PASS" if s >= K1["pass_min"] else ("FAIL" if s < K1["fail_below"] else "INCONCLUSIVE")
    return {"rule": "E144b-K1: G1's share of samples over its last 300 s at >= 790 MHz: PASS >= 0.90, FAIL < 0.80", "share": s,
            "verdict": v, "die_max_C": (c.get("safety") or {}).get("die_max_C")}


def main():
    data = os.path.abspath(sys.argv[1])
    bad = [f"{f}: {sha256(os.path.join(Q138T, f))[:16]} (frozen {h[:16]})" for f, h in FROZEN.items() if sha256(os.path.join(Q138T, f)) != h]
    if bad:
        print("E144b reduce REFUSED: a frozen input differs from c2f9920d: " + "; ".join(bad))
        return 2
    steps = [s for s in ("G1", "G2") if os.path.isdir(os.path.join(data, s, "tel"))]
    res = {"experiment": "E144b", "frozen_inputs": {"commit": "c2f9920d", "sha256": FROZEN}, "steps_scored": steps}
    if steps:
        cmd = [sys.executable, os.path.join(Q138T, "score_e144.py"), "a2"] + [os.path.join(data, s) for s in steps]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            print("the frozen scorer failed:", r.stderr[-2000:])
            return 3
        res["score"] = json.loads(r.stdout)
        res["scorer_cmd"] = ["score_e144.py", "a2"] + steps
    res["clock"] = {s: clock_and_safety(os.path.join(data, s)) for s in steps}
    if "G1" in res["clock"]:
        res["K1"] = k1(res["clock"]["G1"])
    json.dump(res, open(os.path.join(data, "results.json"), "w"), indent=1, default=float)
    # the printout
    print(f"E144b reduce: frozen inputs at c2f9920d verified ({len(FROZEN)} files); steps scored {steps}")
    for h in (res.get("score") or {}).get("holds", []):
        print(f"\n== {h['step']} {h['hold']} ({h['G']}), {h['dur_s']:.0f} s, rest die {h['rest_die_C']:.2f} C")
        a, am = h["a"], h["a_M6"]
        print(f"  (a) chain on the measured board: rms {a['rms_C']:.3f} C, plateau err {a['plateau_err_C']:+.3f} C, max |err| "
              f"{a['max_abs_C']:.3f} -> {a['verdict']}   [M6 as frozen: rms {am['rms_C']:.3f}, plateau {am['plateau_err_C']:+.3f}]")
        b = h.get("b") or {}
        if h["G"] == "G1":
            print(f"  (b) plateau rise {b.get('plateau_rise_C'):.3f} vs {b.get('predicted_C'):.3f} C: err {b.get('err_C'):+.3f} -> {b.get('verdict')}"
                  f"   [M6: {(h.get('b_M6') or {}).get('err_C', float('nan')):+.3f}]")
            c, t, t2 = h.get("c_per_board_W") or {}, h.get("c_t63") or {}, h.get("c_t63_A1") or {}
            print(f"  (c) per board W {c.get('per_board_W')} -> {c.get('verdict')}; t63 {t.get('t63_s')} s, x{t.get('ratio')} of the open "
                  f"loop's -> {t.get('verdict')}; A1.8 closed reference x{t2.get('ratio')} -> {t2.get('verdict')}")
        elif h["G"] == "G2":
            print(f"  (b) plateau {b.get('plateau_C'):.3f} vs {b.get('predicted_C'):.3f} C: err {b.get('err_C'):+.3f}; regime {b.get('regime')} "
                  f"(predicted {b.get('regime_predicted')}, 600 MHz share {b.get('share_600MHz_last300s'):.3f}) -> {b.get('verdict')}; "
                  f"tests {b.get('tests')}   [M6 floor only: {(h.get('b_M6') or {}).get('err_C', float('nan')):+.3f}]")
    for s, c in res["clock"].items():
        print(f"\n== {s} clock and safety: {json.dumps(c)}")
    if "K1" in res:
        print(f"\nE144b-K1: {json.dumps(res['K1'])}")
    print(f"\nverdicts: {json.dumps((res.get('score') or {}).get('verdicts'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
