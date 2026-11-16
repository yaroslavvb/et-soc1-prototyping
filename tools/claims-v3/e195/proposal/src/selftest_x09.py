#!/usr/bin/env python3
"""A test of reduce_x09.py on synthetic data (it means nothing about a card).

    python3 selftest_x09.py <gen dir from make_x09.py> <scratch dir> [--sessions 100]

Part 1, the pipeline: eight synthetic passes in the runner's record format (marks.jsonl, runs.jsonl, configs.json,
telemetry.jsonl) from a known price list, with the meter's sample noise, a dip, a pass whose drift anchor moves 0.5 W
(it must be set aside) and one run off the card's clock (it must fail its gate). The reducer is run as the lab would
run it; the prices it returns must be the ones given (within 8 %; the floor and the zero lines within 25 pJ), the
sanity checks must pass, and the verdicts must be the ones the prices imply.

Part 2, reachability: the reducer's rules on synthetic sessions with a pass-to-pass scatter of every item as large as
the lab's own memory runs on this card showed (0.056 W a flat item, 0.063 W a paced one, independent within a pass:
more scatter on a four-item statistic than the lab measured), seven headline passes, under six scenarios: the
request's sizing (the write side costing what the lab measured for the read side); write inversion off; written pins
free; the wide paths and the channel free on writes; a data cost a line 1.25 times as high at the paced rate; the
write side 1.8 times the read side. Each verdict a scenario implies must come out in more than half of its sessions:
none may be out of reach. Every share is printed (request.md section 5 has the power at the sizing).

The read side's prices are the lab's public ones for this card's memory reads; the write side's are the read side's
times 0.72 in part 1 and times 1.0 (S6: 1.8) in part 2. They are test values, not a forecast.
Exit 0 on PASS.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
READ = {"one": 3.2, "pin": 1.5, "tog": 0.8, "p64": 0.7, "half": 2.4, "chan": 1.0, "floor": 95.0}
WRITE_FACTOR = 0.72
RATES = {"rd": 1.173e9, "wr": 1.19e9, "rdh": 0.6e9, "wrh": 0.6e9}
# Test values for what the lab has not priced (round numbers, not estimates): the paced loops' polling cores, W over
# rest; a zero line, pJ; a store's core side and the scratchpad array's write, pJ a line; the flat loops' waiting cores
SPIN_W = 1.5
ZL = {"rd": 4000.0, "wr": 3000.0}
STORE_ISSUE, SCP_ARRAY = 60.0, 40.0
WAIT_W = {"rd": 1.0, "wr": 1.0}
PER_POLL = {"rdh": 120.0, "wrh": 1000.0}   # polls a slot


def load_reducer():
    spec = importlib.util.spec_from_file_location("reduce_x09", os.path.join(HERE, "reduce_x09.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def prices_for(scn):
    f = WRITE_FACTOR if scn == "P1" else (1.8 if scn == "S6" else 1.0)
    w = {k: v * f for k, v in READ.items()}
    if scn == "S6":
        for k in ("p64", "half", "chan", "floor"):
            w[k] = READ[k]
    if scn == "S3":
        w["pin"] = 0.0
    if scn == "S4":
        w["p64"] = w["half"] = w["chan"] = 0.0
    return {"rd": dict(READ), "wr": w}


def line_energy(c, P, inv_off=False):
    """pJ a line over the zeros arm of the same direction, from the designed counts."""
    if c["w"] == 0:
        return 0.0
    hi = c["w"] if inv_off else c["hi"]
    tog = (c["t_raw"] + c["tx_raw"]) if inv_off else (c["t_enc"] + c["tx_enc"])
    return (P["floor"] + P["one"] * c["w"] + P["pin"] * hi + P["tog"] * tog + P["p64"] * c["p64"] +
            P["half"] * c["half"] + P["chan"] * c["k_chan"])


def item_model(it, scn="P1"):
    """Board W over the card at rest, the rails' W, the DDR die reading, the rate, and the counters of one item."""
    fam, c, role = it["family"], it["designed"], it.get("role", "")
    d = "wr" if fam.startswith("wr") else "rd"
    P = prices_for(scn)[d]
    rate = RATES[fam]
    name = it["name"]
    e = line_energy(c, P, inv_off=(scn == "S2" and d == "wr"))
    if fam in ("rdh", "wrh") and scn == "S5":
        e *= 1.25
    one_part = P["one"] * c["w"] if c["w"] else 0.0
    floor_part = P["floor"] if c["w"] else 0.0
    if fam in ("rd", "wr"):
        base = WAIT_W[fam] + ZL[d] * 1e-12 * rate
    else:
        base = SPIN_W + ZL[d] * 1e-12 * rate + (STORE_ISSUE * 1e-12 * rate if d == "wr" else 0.0)
    lines = rate
    if name.endswith("_l1") or name.endswith("_nst"):
        base, lines = SPIN_W, 0.0
    elif name.endswith("_scp"):
        base, lines = SPIN_W + (STORE_ISSUE + SCP_ARRAY) * 1e-12 * rate, 0.0
    p = base + e * 1e-12 * rate
    noc = 2.5 + 0.5 * one_part * 1e-12 * rate + 0.15 * ZL[d] * 1e-12 * lines
    sram = 2.2 + (0.05 * one_part + 0.9 * floor_part) * 1e-12 * rate + 0.1 * ZL[d] * 1e-12 * lines
    minion = 8.0 + (SPIN_W if fam in ("rdh", "wrh") else WAIT_W[fam]) * 0.8 + 0.05 * one_part * 1e-12 * rate
    paths = (P["tog"] * (c["t_enc"] + c["tx_enc"]) + P["p64"] * c["p64"]) * 1e-12 * rate if c["w"] else 0.0
    ddr = 768.0 - 0.9 * paths
    # counters a second (the denominators the host reports)
    acc = 0.0 if lines == 0 and not fam.endswith("h") else (lines if d == "rd" else lines / 8.0)
    if fam.endswith("h"):
        acc = rate / (1.0 if d == "rd" else 8.0)   # one access a slot, whatever it moves
    flat_ipa = 33.0 / 8 if d == "rd" else 43.0 / 8
    spins = acc * PER_POLL[fam] if fam.endswith("h") else 0.0
    ret = acc * flat_ipa if not fam.endswith("h") else acc * 24.0 + spins * 6.0
    l1 = acc if (d == "rd" and not name.endswith("_l1")) else 0.0
    return {"p": p, "rails": {"minion": minion, "sram": sram, "noc": noc}, "ddr": ddr, "rate": lines if lines else acc,
            "lines": lines, "acc": acc, "ret": ret, "l1": l1, "spins": spins,
            "ms_rd": lines if d == "rd" else 0.0, "ms_wr": lines if d == "wr" else 0.0}


# ---- part 1: the pipeline ----------------------------------------------------------------------------------------
def pipeline(gen, out, red):
    man = json.load(open(os.path.join(gen, "manifest.json")))
    items = man["items"]
    rng = np.random.default_rng(3)
    dirs = []
    t = 1.8e12
    for pss in range(10, 18):
        d = os.path.join(out, f"p{pss}")
        os.makedirs(d, exist_ok=True)
        tel, runs, marks = [], [], []
        order = [items[0]] + [it for it in items[1:]] + [items[0]]
        for pos, it in enumerate(order):
            idle = 25.8
            if it["kind"] == "fma":
                m = None
                p_item = 24.0 + (0.5 if (pss == 13 and pos > 0) else 0.0)   # pass 13: the anchor drifts 0.5 W
            else:
                m = item_model(it)
                p_item = m["p"]
            t0 = t + 2000
            for k in range(10):
                ts, te = t0 + 400 * k, t0 + 400 * k + 399
                rec = {"arm": it["name"][3:].replace("_", ".", 1), "mode": "x", "t_start_ms": ts, "t_end_ms": te,
                       "ok": True, "iters": 1, "participants": 1024, "ms": True, "ms_bad": 0}
                if m is not None:
                    rec.update({"ops": m["rate"] * 0.4, "lines": int(m["lines"] * 0.4),
                                "accesses": int(m["acc"] * 0.4), "ret_t0": int(m["ret"] * 0.4),
                                "l1_miss": int(m["l1"] * 0.4), "ms_rd": int(m["ms_rd"] * 0.4),
                                "ms_wr": int(m["ms_wr"] * 0.4), "late": 0, "spins": int(m["spins"] * 0.4)})
                runs.append({"card": "synthetic", "block": pss, "pos": pos, "item": it["name"], "kind": it["kind"],
                             "attempt": 1, "family": it.get("family"), "start_c": 58.0, **rec})
            marks.append({"kind": "run", "item": it["name"], "block": pss, "pos": pos, "attempt": 1,
                          "t_start_ms": t0, "t_end_ms": t0 + 4000, "start_c": 58.0, "on_protocol": True})
            off_clock = (pss == 14 and it["name"] == "x9_wr_u2")   # one run off the clock: it fails its gate
            for k in range(0, 60):
                tm = t0 - 1000 + 100 * k
                on = t0 <= tm < t0 + 4000
                temp = 58.0 + (0.3 * (tm - t0) / 4000 if on else 0.0)
                board = idle + (p_item + 0.25 * (temp - 58.0) if on else 0.0) + rng.normal(0, 0.03)
                if on and k == 25 and pos == 3:
                    board -= 9.0            # a dip, to be removed
                rails = m["rails"] if (m is not None and on) else {"minion": 8.0, "sram": 2.2, "noc": 2.5}
                tel.append({"t_ms": tm, "board_w": round(board, 2),
                            "sp": {f"{r}_w": [round(v + rng.normal(0, 0.003), 4)] for r, v in rails.items()},
                            "die_mv": {"minion": 522, "ddr": round((m["ddr"] if (m and on) else 768.0) +
                                                                   rng.normal(0, 0.05), 2)},
                            "mhz": {"minion": 500 if (off_clock and on) else 600},
                            "temp_c": {"minshire": [round(temp, 2)]}, "took_ms": 22})
            t = t0 + 4000
        for fn, rows in (("telemetry.jsonl", tel), ("runs.jsonl", runs), ("marks.jsonl", marks)):
            with open(os.path.join(d, fn), "w") as f:
                f.write("\n".join(json.dumps(x) for x in rows) + "\n")
        json.dump({"card": "synthetic", "args": {"target": 58.0}}, open(os.path.join(d, "configs.json"), "w"))
        dirs.append(d)
    res_path = os.path.join(out, "x09.json")
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "reduce_x09.py")] + dirs +
                       ["--gen", gen, "--out", res_path, "--leak", "0.25"], capture_output=True, text=True)
    print(r.stdout[-4000:])
    if r.returncode:
        print(r.stderr[-3000:])
        return ["the reducer failed"]
    res = json.load(open(res_path))
    P = res["prices_pJ"]
    Rd, Wr = prices_for("P1")["rd"], prices_for("P1")["wr"]
    want = {"rd.one_tie": Rd["one"], "rd.pin": Rd["pin"], "rd.pin_K": Rd["pin"], "rd.toggle": Rd["tog"],
            "wr.one_tie": Wr["one"], "wr.pin": Wr["pin"], "wr.pin_K": Wr["pin"], "wr.toggle": Wr["tog"], "wr.path64": Wr["p64"], "wr.path256": Wr["half"],
            "wr.path256_off": Wr["half"], "wr.channel": Wr["chan"], "rd.floor_w1": Rd["floor"],
            "wr.floor_w1": Wr["floor"], "rd.zero_line": ZL["rd"], "wr.zero_line_scp": ZL["wr"] - SCP_ARRAY,
            "wr.zero_line_nst": ZL["wr"] + STORE_ISSUE, "rd.any_line": ZL["rd"] + Rd["floor"],
            "wr.inversion_toggle_ratio": 64.0 / 512.0}
    bad = []
    for k, w in want.items():
        got = P.get(k, {}).get("mean")
        tol_abs = k.endswith(("floor_w1", "zero_line", "zero_line_scp", "zero_line_nst", "any_line"))
        if k == "wr.inversion_toggle_ratio":   # a ratio of a 0.04 W step to a 0.35 W one: its own absolute tolerance
            ok = got is not None and abs(got - w) < 0.05
        else:
            ok = got is not None and (abs(got - w) < 25.0 if tol_abs else abs(got / w - 1) < 0.08)
        print(f"  {k}: {got} (given {w}) {'ok' if ok else 'WRONG'}")
        if not ok:
            bad.append(k)
    clo = P.get("wr.rnd_less_all_terms", {}).get("mean")
    if clo is None or abs(clo) > 25.0:
        bad.append(f"write closure {clo}")
    for k in ("rd.rnd", "wr.rnd", "rd.u4", "wr.u4"):
        got = res["rate_tests"].get(k, {}).get("mean")
        if got is None or abs(got - 1) > 0.05:
            bad.append(f"rate {k} {got}")
    v = res["verdicts"]
    expect = {"R1_write_inversion": "LIVE", "R1b_write_pin": "TERMINATED", "R5_path64_write": "PAYS",
              "R6_path256_write": "BOTH DIRECTIONS", "R7_channel_write": "PAYS",
              "R8_rate_random": "rd.rnd: PER LINE, wr.rnd: PER LINE"}
    for k, e in expect.items():
        if v[k]["verdict"] != e:
            bad.append(f"{k} {v[k]['verdict']} (want {e})")
    if res["headline"] != [11, 12, 14, 15, 16, 17] or 13 not in [int(x) for x in res["set_aside"]]:
        bad.append(f"headline {res['headline']} / set aside {res['set_aside']}")
    if res["gates"]["by_reason"]["clock"] < 1:
        bad.append("the run off the clock passed its gate")
    for k, c in res["checks"].items():
        if c["verdict"] != "PASS":
            bad.append(f"check {k} {c['verdict']} {c.get('failed')}")
    if "differs_from_primary" not in res["sensitivity"]:
        bad.append("no sensitivity arms")
    return bad


# ---- part 2: reachability ----------------------------------------------------------------------------------------
def synthetic_cells(man, scn, rng, head, sd_flat=0.056, sd_paced=0.063):
    cells = {}
    for name, it in man.items():
        if not name.startswith("x9_"):
            continue
        m = item_model(it, scn)
        paced = it["family"] in ("rdh", "wrh")
        for p in head:
            x = {"p": m["p"] + rng.normal(0, sd_paced if paced else sd_flat),
                 "rails": {r: v + rng.normal(0, 0.01) for r, v in m["rails"].items()},
                 "ddr_mv": m["ddr"] + rng.normal(0, 0.15), "rate": m["rate"] * (1 + rng.normal(0, 1e-4)),
                 "lines": m["lines"], "accesses": m["acc"], "ret_t0": m["ret"], "l1_miss": m["l1"],
                 "ms_rd": m["ms_rd"], "ms_wr": m["ms_wr"], "ms_seen": True, "late": 0, "spins": m["spins"],
                 "participants": 1024}
            cells[(p, name)] = x
    return cells


SCENARIOS = {   # verdict -> the text it must contain (a leg of a two-leg rule is checked on its own)
    "S1 the request's sizing": [("R1_write_inversion", "LIVE"), ("R1b_write_pin", "TERMINATED"),
                                ("R3_one_write_over_read", "SAME"), ("R4_toggle_write_over_read", "SAME"),
                                ("R5_path64_write", "PAYS"), ("R6_path256_write", "BOTH DIRECTIONS"),
                                ("R7_channel_write", "PAYS"), ("R8_rate_random", "rd.rnd: PER LINE"),
                                ("R8_rate_random", "wr.rnd: PER LINE"), ("R2_pin_write_over_read", "SAME")],
    "S2 write inversion off": [("R1_write_inversion", "OFF"), ("R1b_write_pin", "NOT SEPARABLE"),
                               ("R2_pin_write_over_read", "NOT SEPARABLE"), ("R3_one_write_over_read", "NOT SEPARABLE")],
    "S3 written pins free": [("R1_write_inversion", "LIVE"), ("R1b_write_pin", "SMALL")],
    "S4 wide paths and channel free on writes": [("R5_path64_write", "FREE"), ("R6_path256_write", "READS ONLY"),
                                                 ("R7_channel_write", "FREE")],
    "S5 the paced data cost 1.25 times flat": [("R8_rate_random", "rd.rnd: RATE-DEPENDENT"),
                                               ("R8_rate_random", "wr.rnd: RATE-DEPENDENT")],
    "S6 the write side 1.8 times the read side": [("R3_one_write_over_read", "WRITE HIGHER"),
                                                  ("R4_toggle_write_over_read", "WRITE HIGHER"),
                                                  ("R2_pin_write_over_read", None)],
}
NEED = 0.5


def reachability(gen, red, sessions):
    man = {it["name"]: it for it in json.load(open(os.path.join(gen, "manifest.json")))["items"]}
    head = list(range(11, 18))
    bad = []
    rng = np.random.default_rng(11)
    for scn, want in SCENARIOS.items():
        key = scn.split()[0]
        got = {k: [] for k, _ in want}
        for _ in range(sessions):
            res = red.analyse(synthetic_cells(man, key, rng, head), head, man)
            for k in got:
                got[k].append(res["verdicts"][k]["verdict"])
        for k, text in want:
            vs = got[k]
            if text is None:
                tally = {}
                for x in vs:
                    tally[x] = tally.get(x, 0) + 1
                print(f"  {scn}: {k} (reported): " + ", ".join(f"{x} {n / sessions:.2f}" for x, n in
                                                              sorted(tally.items(), key=lambda y: -y[1])))
                continue
            share = sum(1 for x in vs if text in x) / sessions
            flag = "ok" if share > NEED else "OUT OF REACH"
            print(f"  {scn}: {k} -> {text}: {share:.2f} {flag}")
            if share <= NEED:
                bad.append(f"{key} {k} {text}")
    return bad


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gen")
    parser.add_argument("out")
    parser.add_argument("--sessions", type=int, default=100)
    a = parser.parse_args()
    red = load_reducer()
    print("part 1, the pipeline:")
    bad = pipeline(a.gen, a.out, red)
    print("part 2, reachability (" + str(a.sessions) + " synthetic sessions a scenario, 7 headline passes):")
    bad += reachability(a.gen, red, a.sessions)
    print("SELFTEST " + ("PASS" if not bad else "FAIL: " + "; ".join(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
