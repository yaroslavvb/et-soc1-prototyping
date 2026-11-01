#!/usr/bin/env python3
"""E97 (Q132): the self-test, at the desk, touching no card. Nothing it prints is data.

Part A: two synthetic passes in the runner's and the sampler's exact formats (E89's selftest generator on E97's blocks and order), from a heat chain driven by E78's and E86's
powers, with 34 sensors as raw codes; then reduce_e97.py (E89's reducer byte for byte) and score_e97.py. World 1: every kind heats the same per W: the reducer must return r near 1,
H near the chain's, and R0-R6 PASS or INCONCLUSIVE, no FAIL. World 2: int8 kinds get 0.70 of the heat per watt: R2 and R5 must FAIL or be INCONCLUSIVE for them, never PASS at the true value.

Part B: run_e97b.run_plan itself, on a simulated card (a virtual clock, a die on a chain with the law of leakage, the launches' timing, the sampler's format), with different times left:
the plan's branches, the stop at 78 C and the reduced phase, the rests' criteria; then reduce_e97b.py must return what the simulated card was given.

    /usr/bin/python3 tools/claims-v3/e97/selftest_e97.py <scratch dir> [--part a|b]
"""
import argparse
import gzip
import json
import math
import os
import subprocess
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e97_common as c  # noqa: E402
import reduce_e97b as rb  # noqa: E402
import run_e97b as rn  # noqa: E402

PRED = json.load(open(os.path.join(HERE, "predictions-e97.json")))
TAU = np.array(PRED["heat_paths"]["e89_fit"]["tau"])
R = np.array(PRED["heat_paths"]["e89_fit"]["R"])
A_LEAK = PRED["leak_law"]["A_W"]
L_LEAK = PRED["leak_law"]["L_C"]
DT = 0.1
S_OF = {}
for b, v in PRED["blocks"].items():
    S_OF[v["kind"]] = v["S"]
S_OF["int8.zeros"] = 2.605
S_OF["int8.full"] = 9.648
S_OF["fp32.ones"] = 10.288


def typ(item):
    return item.split(".")[0]


def build_a(d, pass_no, t_start, gain_int8=1.0, seed=0):
    """E89's selftest generator, on E97's blocks"""
    rng = np.random.default_rng(seed)
    os.makedirs(d, exist_ok=True)
    order = c.pass_order("aifoundry3", pass_no)
    marks, runs = [], []
    seg = []
    t = t_start
    marks.append({"kind": "gate", "t_start_ms": int(t * 1000), "t_end_ms": int(t * 1000), "die_c": 55, "reached": True, "gate_c": 62})
    marks.append({"kind": "idle", "t_start_ms": int(t * 1000), "t_end_ms": int((t + 15) * 1000), "die_c": 55})
    seg.append((t, t + 15, None))
    t += 15
    for bi, b in enumerate(order):
        k, z = c.BLOCKS[b]
        tb = t + 0.3
        marks.append({"kind": "block", "block": b, "pos": bi, "item": k, "ref": z, "t_start_ms": int(tb * 1000),
                      "t_end_ms": int((tb + 140) * 1000), "half_s": 30.0, "cycles": 2, "lead_s": 20.0, "die_c": 55})
        halves = [(z, 20.0, "lead")] + [(k, 30.0, "K"), (z, 30.0, "Z")] * 2
        th = tb
        for hi, (item, L, role) in enumerate(halves):
            marks.append({"kind": "half", "block": b, "half": hi, "role": role, "item": item,
                          "t_start_ms": int(th * 1000), "t_end_ms": int((th + L) * 1000)})
            if item == "idle":
                seg.append((th, th + L, None))
            else:
                tl = th
                while th + L - tl - 0.75 >= 1.0:
                    secs = min(6.8, th + L - tl - 0.75)
                    seg.append((tl, tl + 0.3, None))
                    c0 = tl + 0.3
                    seg.append((c0, c0 + secs, item))
                    marks.append({"kind": "launch", "block": b, "half": hi, "role": role, "item": item, "secs": secs,
                                  "t_start_ms": int(tl * 1000), "t_end_ms": int((c0 + secs + 0.02) * 1000), "rc": 0, "records": 2})
                    for li, (a0, a1) in enumerate([(c0, c0 + 0.02), (c0 + 0.02, c0 + secs)]):
                        runs.append({"card": "aifoundry3", "pass": pass_no, "block": b, "half": hi, "role": role, "item": item,
                                     "type": typ(item), "launch": li - 1, "cycles_per_op": 546.0 if typ(item) != "int8" else 318.0,
                                     "t_start_ms": int(a0 * 1000), "t_end_ms": int(a1 * 1000), "ok": True})
                    tl = c0 + secs + 0.02
                seg.append((tl, th + L, None))
            th += L
        t = th
    seg.append((t, t + 5, None))
    t_end = t + 5
    n = int((t_end - t_start) / DT)
    tt = t_start + np.arange(n) * DT
    P = np.zeros(n)
    is8 = np.zeros(n, bool)
    for a0, a1, item in seg:
        if item is None:
            continue
        m = (tt >= a0) & (tt < a1)
        P[m] = S_OF.get(item, S_OF.get(item, 2.0))
        if item.startswith("int8"):
            is8[m] = True
    x = np.zeros(len(TAU))
    T = np.empty(n)
    aa = np.exp(-DT / TAU)
    for i in range(n):
        tn = 52.0 + x.sum()
        dP = P[i] + A_LEAK * (math.exp((tn - 80.0) / L_LEAK) - math.exp((52.0 - 80.0) / L_LEAK))
        heat = P[i] * (gain_int8 if is8[i] else 1.0) + (dP - P[i])
        x = aa * x + (1 - aa) * R * heat
        T[i] = tn
    offs = rng.uniform(0, 3, 34)
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt", compresslevel=1) as f:
        for i in range(n):
            ts = T[i] + offs + rng.normal(0, 0.03, 34)
            cd = np.round((ts * 1000 - 57400 + 124700) * 4096 / 249400).astype(int).tolist()
            fw = int(sum(int((57400 + (int(249400 * q / 4096) - 124700)) / 1000) for q in cd) / 34)
            dP = P[i] + A_LEAK * (math.exp((T[i] - 80.0) / L_LEAK) - math.exp((52.0 - 80.0) / L_LEAK))
            bw = 23.7 + dP + rng.normal(0, 0.05)
            f.write(json.dumps({"t_ms": int(tt[i] * 1000), "board_w": round(bw, 2),
                                "sp": {"minion_w": [round(13.0 + 0.85 * dP, 3), 0, 0], "sram_w": [round(2.0 + 0.02 * dP, 3), 0, 0], "noc_w": [round(1.0 + 0.01 * dP, 3), 0, 0], "minion_mv": [522, 522, 522]},
                                "temp_c": {"pmic": fw, "ioshire": [fw, 0, 0], "minshire": [fw, 40, 90]},
                                "die_mv": {"minion": 522}, "mhz": {"minion": 600, "noc": 400, "ddr": 933},
                                "pvt": {"st": 0, "f": 0, "c": cd}}) + "\n")
    with open(os.path.join(d, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    with open(os.path.join(d, "runs.jsonl"), "w") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")
    json.dump({"args": {"pass_no": pass_no}, "order": order}, open(os.path.join(d, "configs.json"), "w"))
    json.dump({"status": "ok"}, open(os.path.join(d, "block.json"), "w"))
    json.dump({"sampler": "pvt"}, open(os.path.join(d, "sampler.json"), "w"))
    return t_end


def case_a(scratch, name, gain):
    base = os.path.join(scratch, name)
    p1, p2 = os.path.join(base, "p9710"), os.path.join(base, "p9711")
    t1 = build_a(p1, 9710, 1.79e9, gain, seed=1)
    build_a(p2, 9711, t1 + 20, gain, seed=2)
    out = os.path.join(base, "red")
    for script, args in (("reduce_e97.py", [p1, p2, "--out", out]), ("score_e97.py", [p1, p2, "--out", out])):
        r = subprocess.run([sys.executable, os.path.join(HERE, script)] + args, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-1500:], r.stderr[-3000:])
            raise SystemExit(f"{name}: {script} failed")
    return json.load(open(os.path.join(out, "e97.json")))


def part_a(scratch):
    ok = True
    e = case_a(scratch, "world1", 1.0)
    print("== Part A, world 1: heat follows power, one coefficient")
    rr = [e["blocks"][b]["r_board_pass"]["r"] for b in c.LOW_BLOCKS]
    print(f"   r board, pass mean over 28 blocks: {min(rr):.3f}-{max(rr):.3f}; H_ref {e['blocks'][c.REF_BLOCK]['H']['mean']:.4f}")
    print("   tally", json.dumps(e["tally"]["by_rule_primary"]))
    bad = [v for v in e["verdicts"] if v["verdict"] == "FAIL" and v["rule"] in ("E97-R0", "E97-R1", "E97-R2", "E97-R5")]
    for v in bad:
        print("   FAIL", v["rule"], v["cell"], v["unit"], v["measured"])
    if bad or not (0.93 <= min(rr) and max(rr) <= 1.07):
        ok = False
    ce = e["cells_over_idle"]
    ra = [v["ratio_to_extrapolation"] for k, v in ce.items()]
    print(f"   cells {len(ce)}; the 2 s rise over idle / (S x 0.118): {min(ra):.3f}-{max(ra):.3f} (the chain's own 2 s is about 0.93-1.0 of 0.118 per W)")
    e2 = case_a(scratch, "world2", 0.70)
    print("== Part A, world 2: int8 heats 0.70 per W")
    for v in e2["verdicts"]:
        if v["rule"] in ("E97-R2", "E97-R5") and v["unit"] == "pass" and c.BLOCKS.get(v["cell"], ("", ""))[0].startswith("int8."):
            print("  ", v["rule"], v["cell"], v["verdict"], {k: round(x, 3) for k, x in v["measured"].items() if isinstance(x, float) and k in ("r", "lo", "hi")})
            if v["verdict"] == "PASS":
                ok = False
    return ok


class SimCard:
    """A card for run_plan: a virtual clock, a die on a heat chain with leakage feedback, launches with E89's timing, the sampler's lines at 10 Hz"""

    def __init__(self, out, t0, tau=TAU, R_=R, Ti=51.4, drift_c_per_h=-0.1, gain=1.0, seed=3, start_excess=8.0, others_at=None, off_clock_at=None):
        self.t = t0
        self.t0 = t0
        self.tau, self.R, self.Ti, self.drift, self.gain = np.array(tau, float), np.array(R_, float), Ti, drift_c_per_h, gain
        self.a = np.exp(-DT / self.tau)
        self.x = self.R / self.R.sum() * start_excess
        self.rng = np.random.default_rng(seed)
        self.offs = self.rng.uniform(0, 3, 34)
        self.lines = []
        self.f = gzip.open(os.path.join(out, "telemetry.jsonl.gz"), "wt", compresslevel=1)
        self.on = 0.0
        self.item_of = {}
        self.others_at = others_at
        self.off_clock_at = off_clock_at
        self.next_line = t0
        self.leak0 = self._leak(Ti)
        self._step(0.3)

    def _leak(self, T):
        return min(A_LEAK * math.exp((T - 80.0) / L_LEAK), 300.0)

    def _step(self, dur):
        n = max(1, int(round(dur / DT)))
        for _ in range(n):
            tn = self.Ti + self.x.sum() + self.drift * (self.t - self.t0) / 3600.0
            dP = self.on + self._leak(tn) - self.leak0
            self.x = self.a * self.x + (1 - self.a) * self.R * (self.on * self.gain + self._leak(tn) - self.leak0)
            ts = tn + self.offs + self.rng.normal(0, 0.03, 34)
            cd = np.round((ts * 1000 - 57400 + 124700) * 4096 / 249400).astype(int).tolist()
            fw = int(sum(int((57400 + (int(249400 * q / 4096) - 124700)) / 1000) for q in cd) / 34)
            mhz = 600 if (self.off_clock_at is None or self.t < self.off_clock_at) else 300
            rec = {"t_ms": int(self.t * 1000), "board_w": round(23.5 + dP + self.rng.normal(0, 0.05), 2),
                   "sp": {"minion_w": [round(13.0 + 0.85 * dP, 3), 0, 0], "sram_w": [round(2.0 + 0.02 * dP, 3), 0, 0], "noc_w": [round(1.0 + 0.01 * dP, 3), 0, 0], "minion_mv": [522, 522, 522]},
                   "temp_c": {"pmic": fw, "ioshire": [fw, 0, 0], "minshire": [fw, 40, 90]}, "die_mv": {"minion": 522}, "mhz": {"minion": mhz, "noc": 400, "ddr": 933},
                   "pvt": {"st": 0, "f": 0, "c": cd}}
            self.lines.append(rec)
            self.f.write(json.dumps(rec) + "\n")
            self.t += DT
        if len(self.lines) > 8000:
            self.lines = self.lines[-6000:]

    def now(self):
        return self.t

    def sleep(self, s):
        self._step(s)

    def latest(self):
        return self.lines[-1]

    def tail(self, seconds):
        return self.lines[-int(seconds * 10 + 40):]

    def launch(self, cmd):
        tile = cmd[cmd.index("--values") + 1]
        secs = float(cmd[cmd.index("--seconds") + 1])
        ty = cmd[cmd.index("--type") + 1]
        item = ty + "." + os.path.basename(tile).replace(".bin", "")
        self._step(0.26)
        self.on = S_OF[item]
        recs = []
        t_k = self.t
        recs.append({"launch": -1, "cycles_per_op": 546.0 if ty != "int8" else 318.0, "t_start_ms": int(t_k * 1000), "t_end_ms": int((t_k + 0.02) * 1000), "ok": True})
        n = int(math.ceil((secs - 0.02) / 0.491))
        tk = t_k + 0.02
        for i in range(n):
            recs.append({"launch": i, "cycles_per_op": 546.0 if ty != "int8" else 318.0, "t_start_ms": int(tk * 1000), "t_end_ms": int((tk + 0.49) * 1000), "ok": True})
            tk += 0.491
        self._step(n * 0.491 + 0.02)
        self.on = 0.0
        self._step(0.06)
        return 0, recs, ""

    def others(self):
        return ["sim:other"] if self.others_at and self.t >= self.others_at else []

    def close(self):
        self.f.close()


def run_b(scratch, name, left_min, **kw):
    d = os.path.join(scratch, name)
    os.makedirs(d, exist_ok=True)
    for f in ("marks.jsonl", "runs.jsonl", "run.log"):
        p = os.path.join(d, f)
        if os.path.exists(p):
            os.remove(p)
    t0 = 1.79e9
    a = rn.parse_args([d, "--root", c.ROOT, "--deadline-epoch", str(t0 + left_min * 60.0)])
    a.dry = False
    card = SimCard(d, t0, **kw)
    code = 0
    import e86_common
    e86_common.install()
    import e78_common as ec
    items = {it["name"]: it for it in ec.load_items()}
    save = sys.stdout
    sys.stdout = open(os.path.join(d, "stdout.txt"), "w")
    try:
        rn.run_plan(a, card, d, items)
    except rn.Finished as e:
        code = e.code
    finally:
        sys.stdout.close()
        sys.stdout = save
        card.close()
    json.dump({"status": "ok"}, open(os.path.join(d, "block.json"), "w"))
    res = rb.reduce_pass(d, PRED)
    res["verdicts"] = rb.score(res, PRED)
    res["exit_code"] = code
    res["t_end_over_deadline_s"] = card.t - a.deadline_epoch
    return res


def show_b(res):
    for x in res["decisions"]:
        print(f"   decision: {x['choice']} ({x['left_s'] / 60:.1f} min left)")
    for r in res["rests"]:
        print(f"   rest {r['name']}: {r['why_end']}, {(r['t_end_ms'] - r['t_start_ms']) / 1000:.0f} s, idle {r.get('idle_c')}")
    for h, x in res["holds"].items():
        st = x.get("steady") or {}
        lk = x.get("leak") or {}
        print(f"   hold {h} {x['item']}: {x['dur_s']:.0f} s, {x['why_end']}, {x['launches']} launches, stop {x.get('stop', {}).get('t_s')}, gates {x['gates']['ok']}; "
              f"dT {st.get('dT', float('nan')):.2f}+-{st.get('eT', float('nan')):.2f}, dP {st.get('dP', float('nan')):.2f}, R_ol {st.get('R_ol', float('nan')):.3f} [{st.get('R_ol_lo', float('nan')):.3f}, {st.get('R_ol_hi', float('nan')):.3f}], "
              f"slope {x.get('slope_C_per_min')}, share {st.get('compute_share')}, leak {lk.get('share_of_dP')}, loop {lk.get('loop_gain')}, closure {lk.get('closure')}, shares60/300 {(x.get('shares') or {}).get('60')}/{(x.get('shares') or {}).get('300')}")
    t = {}
    for v in res["verdicts"]:
        t.setdefault(v["rule"], {}).setdefault(v["verdict"], 0)
        t[v["rule"]][v["verdict"]] += 1
    print("   verdicts", json.dumps(t))
    print(f"   exit {res['exit_code']}, ended {res['t_end_over_deadline_s']:.0f} s against the deadline")


def part_b(scratch):
    ok = True
    print("== Part B, 143 min left, the E89 chain: the on-time plan (chain)")
    r = run_b(scratch, "b143", 143)
    show_b(r)
    if not ({"H1", "H2", "H3"} <= set(r["holds"])) or r["exit_code"] or r["t_end_over_deadline_s"] > 1:
        ok = False
    x = r["holds"]["H1"]["steady"]
    if not 0.80 <= x["R_ol"] <= 0.92:
        print("   H1's R_ol off the truth 0.861")
        ok = False
    if not r["holds"]["H3"].get("stop"):
        print("   H3 should have reached the stop")
        ok = False
    if not 0.80 <= r["holds"]["H3"]["steady"]["R_ol"] <= 0.92:
        print("   H3's R_ol off the truth 0.861")
        ok = False
    bad = [v for v in r["verdicts"] if v["verdict"] != v["pred"] and v["verdict"] != "INCONCLUSIVE"]
    for v in bad:
        print("   against its prediction:", v["rule"], v["cell"], v["verdict"], v["measured"], v["band"])
    print("== Part B, 210 min left: the full plan")
    r = run_b(scratch, "b210", 210)
    show_b(r)
    if "H2" not in r["holds"] or r["holds"]["H2"]["chained"] or r["t_end_over_deadline_s"] > 1:
        ok = False
    print("== Part B, 75 min left: no time for H2's rest; the chain or none")
    r = run_b(scratch, "b75", 75)
    show_b(r)
    if r["t_end_over_deadline_s"] > 1:
        ok = False
    print("== Part B, 50 min left: H1 and a last rest")
    r = run_b(scratch, "b50", 50)
    show_b(r)
    if "H3" in r["holds"] or r["t_end_over_deadline_s"] > 1:
        ok = False
    print("== Part B, 20 min left: no hold fits")
    r = run_b(scratch, "b20", 20)
    show_b(r)
    if r["holds"]:
        ok = False
    print("== Part B, 143 min left, the lab model's chain (the die runs hotter; the stop in H1 too)")
    r = run_b(scratch, "b143lab", 143, tau=PRED["heat_paths"]["lab_model"]["tau"], R_=PRED["heat_paths"]["lab_model"]["R"])
    show_b(r)
    print("== Part B, the clock leaves 600 MHz 40 minutes in: the holds end, a last rest runs")
    r = run_b(scratch, "bclock", 143, off_clock_at=1.79e9 + 2400.0)
    show_b(r)
    if not any(x["why_end"] == "clock" for x in r["holds"].values()):
        ok = False
    print("== Part B, another user 40 minutes in: exit 3")
    r = run_b(scratch, "bothers", 143, others_at=1.79e9 + 2400.0)
    print("   exit", r["exit_code"])
    if r["exit_code"] != 3:
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--part", default="ab")
    a = ap.parse_args()
    ok = True
    if "b" in a.part:
        ok = part_b(a.scratch) and ok
    if "a" in a.part:
        ok = part_a(a.scratch) and ok
    print("SELFTEST", "OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
