#!/usr/bin/env python3
"""E184's synthetic card sessions (the kit's self-test and its dry case; never a measurement): the raw files a box session of either arm
would leave, generated from a stated truth, in the layout the collector copies back.

    python3 -B tools/claims-v3/e184/fake_card_e184.py <raw dir> --arm S [--gain-small 1.0] [--carry-w 33.6 --carry-d 0.0328]
        [--jump-n 48 --jump-w 0.05] [--noise 1.0] [--seed 1]
    python3 -B tools/claims-v3/e184/fake_card_e184.py <raw dir> --arm B [--hmix | --normal] [--spread 0.0] [--tau-sram 0.54] [--seed 1]

Arm S: every item of plan-e184.json's passes as the patched host and the sampler write them: ENERCAT lines (seq, part, n, ref, mask_m,
orient, seg, label, t_start_ms, t_end_ms, ok, the instruction rate), 0.4 s launches 2 ms apart, a 0.5 s idle gap between processes, and
10 Hz telemetry whose board value refreshes every 160 ms one refresh late: the base (E180's idle 24.4 W plus 0.3477 W a zeros shire) plus
the switched minions at E180's 8.256 mW each (times --gain-small for steps under 0.2 W), plus a step of --carry-d W in the reading
wherever the true level exceeds --carry-w, plus --jump-w for levels from --jump-n, plus AR(1) noise (E180's 0.0696 W, lag 0.12, times
--noise), a slow drift and the 10 mW quantum; the minion rail a 1.06 s filter of 0.813 of the step. cal.json is the runner's rule on
the synthetic bases. Arm B: idle and B1's nine loads with card 1's SRAM statistic under H-MIX (min/avg 0.628, max/avg 1.589, the restart at
0.77) or a normal rail (0.978 / 1.022), each level's min/avg moved by --spread x (its rank - 0.5); the 1 s resets in pass 18441; B2's
first-order rails (SRAM tau --tau-sram, minion and NoC 1.08 s); B3's shares at September's ratio 0.718; the glitch at 0.087%.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402

PLAN = json.load(open(os.path.join(HERE, "plan-e184.json")))
INP = json.load(open(os.path.join(HERE, "inputs-e184.json")))
S_W = INP["e180_anchor"]["board_mw_per_minion"] / 1000.0
IDLE_W, Z_W = 24.4, (35.54 - 24.4) / 32.0


class Clock:
    def __init__(self, t0_ms):
        self.t = t0_ms


def gz_write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def sample(t_ms, board, rails, since=-1, mins=None, maxs=None, temp=55):
    mins = mins or {}
    maxs = maxs or {}
    sp = {"board_avg_w": round(board, 2), "minion_mv": [523, 517, 527]}
    for k in ("minion_w", "sram_w", "noc_w"):
        v = rails[k]
        sp[k] = [round(v, 3), round(mins.get(k, v * 0.97), 3), round(maxs.get(k, v * 1.03), 3)]
    return {"t_ms": int(t_ms), "since_reset_ms": since, "board_w": round(math.floor(board * 100 + 1e-9) / 100.0, 2), "sp": sp,
            "temp_c": {"pmic": temp, "minshire": [temp, temp - 2, temp + 20]}, "mhz": {"minion": 600, "noc": 400, "ddr": 933}}


def arm_s(raw, a):
    r = random.Random(a.seed)
    out = os.path.join(raw, "aifoundry3")
    clock = Clock(1795000000000)
    cal = None

    def level_w(m, n):
        return IDLE_W + Z_W * m + S_W * n

    def reading(m, n_now, ref, lab):
        """the meter's reading of the true level: E180's step, times --gain-small for a B step under 0.2 W, the carry's step, the jump"""
        w = level_w(m, n_now)
        stp = S_W * (n_now - ref) if lab == "B" else 0.0
        if lab == "B" and 0 < abs(stp) < 0.2:
            w += (a.gain_small - 1.0) * stp
        if a.carry_d and w > a.carry_w:
            w += a.carry_d
        if a.jump_w and lab == "B" and n_now >= a.jump_n:
            w += a.jump_w
        return w

    for ps in PLAN["arm_S"]["passes"]:
        p = ps["pass"]
        exp = "e184-smoke" if p == 18401 else ("e184-stoptest" if p == 18402 else "e184")
        pdir = os.path.join(out, exp, "p%d" % p)
        os.makedirs(pdir, exist_ok=True)
        items = ps["items"]
        tel, runs = [], []
        noise, rail = 0.0, 0.0
        for it in items:
            m = it["mask_m"] if isinstance(it["mask_m"], int) else cal[it["mask_m"]]
            segs = c.schedule_lines(it["orient"], "a", "b")
            t = clock.t + 500
            drift_a, drift_tau = r.uniform(-0.05, 0.05) * a.noise, r.uniform(3, 8)
            lns = []
            for k, line in enumerate(segs):
                lab, nl, _ = line.split()
                for _ in range(int(nl)):
                    lns.append({"seq": it["seq"], "part": it["part"], "n": it["n"], "ref": it["ref"], "mask_m": m, "orient": it["orient"],
                                "seg": k, "label": lab, "t_start_ms": int(t), "t_end_ms": int(t + 400), "ok": True,
                                "ops_per_cycle_per_hart": round(0.3730 + r.gauss(0, 0.0005), 4), "pattern": "fadd.ps", "pass": p})
                    t += 402
            runs.extend(lns)
            t0, t1 = lns[0]["t_start_ms"], lns[-1]["t_end_ms"]
            ts, last_refresh, held = clock.t, None, IDLE_W
            while ts < t1 + 500:
                seg = [x for x in lns if x["t_start_ms"] <= ts - 120 < x["t_end_ms"] + 2]
                if seg:
                    lab = seg[0]["label"]
                    n_now = it["n"] if lab == "B" else it["ref"]
                    rail_true = 0.62 * Z_W * m + 0.813 * S_W * n_now
                else:
                    rail_true = 0.0
                if last_refresh is None or ts - last_refresh >= 160:
                    w = reading(m, n_now, it["ref"], lab) if seg else IDLE_W
                    if seg:
                        w += drift_a * (1 - math.exp(-(ts - t0) / 1000.0 / drift_tau))
                    noise = 0.12 * noise + math.sqrt(1 - 0.12 ** 2) * r.gauss(0, 0.0696 * a.noise)
                    held, last_refresh = w + noise, ts
                rail += (rail_true - rail) * 0.1 / 1.06
                tel.append(sample(ts, held, {"minion_w": 7.4 + rail, "sram_w": 1.87, "noc_w": 2.08}))
                ts += 100
            clock.t = t1 + 500
        gz_write(os.path.join(pdir, "telemetry.jsonl.gz"), tel)
        gz_write(os.path.join(pdir, "runs.jsonl.gz"), runs)
        json.dump({"arm": "arm_S", "card": "aifoundry3", "pass": p, "items": items}, open(os.path.join(pdir, "configs.json"), "w"))
        json.dump({"status": "ok", "note": "synthetic (fake_card_e184.py)"}, open(os.path.join(pdir, "block.json"), "w"))
        if p == 18413:
            pts = [(16.0, level_w(16, 0) + 0.01), (24.0, level_w(24, 0) - 0.01), (32.0, level_w(32, 0))]
            mx, my = c.fmean(x[0] for x in pts), c.fmean(x[1] for x in pts)
            z = math.fsum((x[0] - mx) * (x[1] - my) for x in pts) / math.fsum((x[0] - mx) ** 2 for x in pts)
            a0 = my - z * mx
            cal = {"points": pts, "a_w": a0, "z_w_per_shire": z, "M_op": int(min(24, max(10, round((INP["e178_op"]["target_board_w"] - a0) / z)))),
                   "M_s": int(min(30, max(16, round((PLAN["design"]["C"]["scan_start_w"] - a0) / z)))), "synthetic": True}
            json.dump(cal, open(os.path.join(pdir, "cal.json"), "w"))
        clock.t += 10000


def arm_b(raw, a):
    r = random.Random(a.seed)
    out = os.path.join(raw, "aifoundry1-c1")
    t_pass = 1795100000000
    cat = {x["cfg"]: x for x in INP["catalogue"]["sram_set"]}
    sram_load = {"tstore/scp/random": 6.17, "fswl.ps/random/h2": 4.63, "flwl.ps/random/h2": 4.16}
    ratio_m, ratio_M = (0.628, 1.589) if a.hmix else (0.978, 1.022)
    taus = {"sram_w": a.tau_sram, "minion_w": 1.08, "noc_w": 1.08}
    idle = {"sram_w": 2.48, "minion_w": 13.3, "noc_w": 4.9}

    def u(t):
        return 1.0 - math.exp(-t) if t > 0 else 0.0

    for ps in PLAN["arm_B"]["passes"]:
        p = ps["pass"]
        exp = "e184-smoke" if p == 18431 else ("e184-stoptest" if p == 18432 else "e184")
        pdir = os.path.join(out, exp, "p%d" % p)
        os.makedirs(pdir, exist_ok=True)
        runs, marks, spans = [], [], []          # spans: (start_ms, end_ms, {rail: step}, board step)
        ranks = {}
        if p == 18441:
            for i, x in enumerate(sorted(ps["items"], key=lambda x: (x["cfg"], x["mask_m"]))):
                ranks[x["seq"]] = i / max(1, len(ps["items"]) - 1) - 0.5
        item_of = {}
        t = t_pass + 10000
        for it in ps["items"]:
            t += int(it.get("gap_s", 4.5) * 1000)
            marks.append({"event": "item_start", "seq": it["seq"], "t_ms": t})
            if it["kind"] == "burst":
                procs = [it["burst_s"]]
            elif it["cfg"] == "idle":
                procs = []
            else:
                procs = [it["proc_s"]] * int(it["hold_s"] // it["proc_s"]) + ([max(0.5, it["hold_s"] % it["proc_s"])] if it["hold_s"] % it["proc_s"] else [])
            frac = (it["mask_m"] or 0) / 32.0
            if it["kind"] == "burst" and p in (18443, 18444):
                c1 = cat[it["cfg"]]
                dl = {"sram_w": c1["c1_board_w"] * (c1["a3_sram_w"] / c1["a3_board_w"]) * 0.718, "minion_w": 1.0, "noc_w": 0.1}
                db = c1["c1_board_w"]
            else:
                ld = sram_load.get(it["cfg"], 0.0) * frac
                dl, db = {"sram_w": ld, "minion_w": 1.5 * frac, "noc_w": 0.3 * frac}, 2.0 * ld
            tt = t
            for dur in procs:
                n = int(dur / 0.4 + 1e-9)
                for k in range(n):
                    runs.append({"seq": it["seq"], "cfg": it["cfg"], "kind": it["kind"], "mask_m": it["mask_m"], "t_start_ms": tt + 402 * k,
                                 "t_end_ms": tt + 402 * k + 400, "ok": True, "pass": p})
                spans.append((tt, tt + 402 * n - 2, dl, db, it["seq"]))
                tt += 402 * n - 2 + 500
            end = tt - 500 if procs else t + int(it.get("hold_s", 20) * 1000)
            marks.append({"event": "item_end", "seq": it["seq"], "t_ms": end})
            item_of[it["seq"]] = (t, end)
            t = end + 500
        t_end = t + 8000
        tel, last_reset = [], t_pass
        for ts in range(t_pass, t_end, 100):
            rails = {}
            for rail in idle:
                v = idle[rail]
                for a0, b0, dl, db, _ in spans:
                    if a0 + 160 < ts < b0 + 160 + 10000:
                        v += dl[rail] * (u((ts - a0 - 160) / 1000.0 / taus[rail]) - u((ts - b0 - 160) / 1000.0 / taus[rail]))
                rails[rail] = v
            board = 34.4 + sum(db for a0, b0, dl, db, _ in spans if a0 <= ts <= b0) + r.gauss(0, 0.05)
            since, mins, maxs = -1, {}, {}
            if p == 18441:
                if ts - last_reset >= 1000:
                    last_reset = ts - ((ts - last_reset) % 1000)
                since = int(ts - last_reset)
                seq = [s for s, (a0, b0) in item_of.items() if a0 <= ts <= b0]
                sh = a.spread * ranks.get(seq[0], 0.0) if seq else 0.0
                k = min(1.0, 0.77 + (since - 300) / 700.0 * 0.23) if a.hmix else 1.0
                rails["sram_w"] = 0.0 if since < 300 else rails["sram_w"] * k
                mins = {"sram_w": rails["sram_w"] * (ratio_m + sh + r.gauss(0, 0.01)), "minion_w": rails["minion_w"] * 0.98,
                        "noc_w": rails["noc_w"] * 0.962}
                maxs = {"sram_w": rails["sram_w"] * (ratio_M + r.gauss(0, 0.02)), "minion_w": rails["minion_w"] * 1.022,
                        "noc_w": rails["noc_w"] * 1.036}
            elif r.random() < 0.00087:
                maxs = {"minion_w": rails["minion_w"]}
            d = sample(ts, board, rails, since, mins, maxs)
            tel.append(d)
        t_pass = t_end + 20000
        gz_write(os.path.join(pdir, "telemetry.jsonl.gz"), tel)
        gz_write(os.path.join(pdir, "runs.jsonl.gz"), runs)
        gz_write(os.path.join(pdir, "marks.jsonl.gz"), marks)
        json.dump({"arm": "arm_B", "card": "aifoundry1-c1", "pass": p, "items": ps["items"]}, open(os.path.join(pdir, "configs.json"), "w"))
        json.dump({"status": "ok", "note": "synthetic (fake_card_e184.py)"}, open(os.path.join(pdir, "block.json"), "w"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--arm", choices=["S", "B"], required=True)
    ap.add_argument("--gain-small", type=float, default=1.0)
    ap.add_argument("--carry-w", type=float, default=33.6)
    ap.add_argument("--carry-d", type=float, default=0.0)
    ap.add_argument("--jump-n", type=int, default=48)
    ap.add_argument("--jump-w", type=float, default=0.0)
    ap.add_argument("--noise", type=float, default=1.0)
    ap.add_argument("--hmix", action="store_true", default=True)
    ap.add_argument("--normal", dest="hmix", action="store_false")
    ap.add_argument("--spread", type=float, default=0.0)
    ap.add_argument("--tau-sram", type=float, default=0.54)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    (arm_s if a.arm == "S" else arm_b)(a.raw, a)


if __name__ == "__main__":
    main()
