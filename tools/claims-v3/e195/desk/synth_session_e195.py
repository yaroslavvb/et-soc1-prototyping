#!/usr/bin/env python3
"""A small synthetic E195 session for the registered reducer (a desk check of code; it says nothing about a card).

    python3 -I -B synth_session_e195.py <gen dir (make_x09.py's manifest.json)> <out dir>

Writes, in the block library's record format (runitems.py's runs.jsonl and marks.jsonl, the sampler's telemetry.jsonl,
configs.json, block.json), the smoke pass p901 and the passes p910-p917 of request.md section 8, every pass with its two
burn-in runs, the anchor first and last and the 31 arms shuffled by runitems.py's own rule, and writes injected.json:
the test values put in. The values are ARBITRARY TEST VALUES, chosen by this lane and unlike any lab measurement: not a
forecast and not a measurement. Every arm's board power over rest is its family's base plus its line energy at its rate,
from the manifest's designed counts:

    E_line = floor + one*w + pin*hi + toggle*(t_enc + tx_enc) + path64*p64 + path256*half + channel*k_chan   (pJ)

(the read side has its own prices, the paths included; inversion is live on both sides: the encoded counts), with the
zero lines and the two paced write controls priced apart. The rails carry fixed shares (the NoC rail half of the ones
part, the SRAM rail the floor), the DDR die reading falls 1 mV a watt of the toggle part. Exact: no noise,
full-precision readings, the die steady at the launch reading (so no leakage correction at any slope), launches tiling
the run (so the rate is exact). Three
faults are injected, each of which the registered reducer must handle as registered: pass 913's anchor ends 0.5 W above
its start (the pass must be set aside); x9_wr_u2 in pass 912 runs off the 600 MHz clock (its run must fail the clock
gate); one board sample of x9_rd_u4 in pass 915 dips 9 W (removed in the primary arm, kept in the unfiltered arm). The
smoke p901 is written so that a reader can see what passing it to the reducer would do; the registered reduction is
given p910-p917 only, with --warmup 910.
"""
import json
import os
import random
import sys

gen, out = sys.argv[1], sys.argv[2]
man = json.load(open(os.path.join(gen, "manifest.json")))
items = man["items"]
X9 = [it for it in items if it["name"].startswith("x9_")]
ANCHOR = items[0]

PRICES = {   # pJ per event; arbitrary test values
    "rd": {"floor": 80.0, "one": 2.5, "pin": 1.2, "toggle": 0.6, "path64": 0.3, "path256": 1.0, "channel": 0.5},
    "wr": {"floor": 60.0, "one": 3.5, "pin": 0.9, "toggle": 0.7, "path64": 0.45, "path256": 1.6, "channel": 0.8},
}
ZERO_LINE = {"rd": 3500.0, "wr": 2800.0}      # pJ a line, over the paced controls
SCP_STORE = 150.0                            # pJ a line of the scratchpad store over storing nothing
RATE = {"rd": 1.1e9, "wr": 1.2e9, "rdh": 0.6e9, "wrh": 0.6e9}   # lines a second
BASE = {"rd": 6.0, "wr": 7.0, "rdh": 2.0, "wrh": 2.5}           # W over rest of each family's zeros arm, less its lines
REST = 23.0                                   # board at rest
ANCHOR_W = 24.0                               # anchor_pi over rest
RAIL_REST = {"minion": 8.0, "sram": 2.2, "noc": 2.5}
RAIL_MV = {"minion": 523, "sram": 700, "noc": 490}   # the telemetry's rail volts, set off the reducer's fixed RAIL_V on purpose
NOC_ONE_SHARE, SRAM_FLOOR_SHARE = 0.5, 1.0
RET_PER_ACCESS = {"rd": 33.0 / 8, "wr": 43.0 / 8}
POLLS_PER_SLOT = {"rdh": 120, "wrh": 1000}


def fam_dir(it):
    f = it["family"]
    return f, ("wr" if f.startswith("wr") else "rd")


def line_energy(it):
    f, d = fam_dir(it)
    c, P = it["designed"], PRICES[d]
    if c.get("no_dram") or c["w"] == 0:
        return 0.0, 0.0, 0.0, 0.0
    tog = P["toggle"] * (c["t_enc"] + c["tx_enc"])
    e = (P["floor"] + P["one"] * c["w"] + P["pin"] * c["hi"] + tog + P["path64"] * c["p64"] + P["path256"] * c["half"] +
         P["channel"] * c["k_chan"])
    return e, P["one"] * c["w"], P["floor"], tog


def model(it):
    """W over rest on the board, the three rails (true W), the DDR die reading, and the run's counters a second."""
    f, d = fam_dir(it)
    name = it["name"]
    rate = RATE[f]
    e, ones, floor, tog = line_energy(it)
    base = BASE[f]
    lines = rate
    if name.endswith(("_l1", "_nst")):
        lines = 0.0
    elif name.endswith("_scp"):
        base, lines = BASE[f] + SCP_STORE * 1e-12 * rate, 0.0
    if f in ("rdh", "wrh") and lines:
        base += ZERO_LINE[d] * 1e-12 * rate
    elif f in ("rd", "wr"):
        base += ZERO_LINE[d] * 1e-12 * rate   # the flat zeros arm pays its zero lines too (it cancels in every contrast)
    p = base + e * 1e-12 * rate
    rails = {"minion": RAIL_REST["minion"] + 1.0, "sram": RAIL_REST["sram"] + SRAM_FLOOR_SHARE * floor * 1e-12 * rate,
             "noc": RAIL_REST["noc"] + NOC_ONE_SHARE * ones * 1e-12 * rate}
    ddr = 760.0 - 1.0 * tog * 1e-12 * rate
    if d == "rd":
        acc = rate                                   # one access a line (rdh.l1: one a slot)
    else:
        acc = rate / 8.0                             # one 512 B store a slot of 8 lines
    cnt = {"lines": lines, "accesses": acc,
           "ret_t0": acc * RET_PER_ACCESS[d] if f in ("rd", "wr") else acc * 24.0,
           "l1_miss": acc if (d == "rd" and not name.endswith("_l1")) else 0.0,
           "ms_rd": lines if d == "rd" else 0.0, "ms_wr": lines if d == "wr" else 0.0,
           "spins": acc * POLLS_PER_SLOT[f] if f in ("rdh", "wrh") else 0.0}
    ops = lines if lines else acc
    return {"p": p, "rails": rails, "ddr": ddr, "ops": ops, "cnt": cnt, "e_line": e}


def write_pass(d, pss, order, t, faults):
    os.makedirs(d, exist_ok=True)
    tel, runs, marks = [], [], []
    t0_block = t

    def telemetry(ts, te, on, m, off_clock=False, dip_at=None, extra=0.0):
        for k in range(int((te - ts) / 100)):
            tm = ts + 100 * k
            busy = on[0] <= tm < on[1]
            board = REST + ((m["p"] + extra) if busy else 0.0)
            if dip_at is not None and tm == dip_at:
                board -= 9.0
            rails = m["rails"] if busy and m.get("rails") else {r: RAIL_REST[r] for r in RAIL_REST}
            tel.append({"t_ms": tm, "board_w": board,
                        "sp": {**{f"{r}_w": [0.94 * v + 0.06 * RAIL_REST[r]] for r, v in rails.items()},
                               **{f"{r}_mv": [RAIL_MV[r]] for r in RAIL_MV}},
                        "die_mv": {"minion": 523, "ddr": m["ddr"] if busy and "ddr" in m else 760.0},
                        "mhz": {"minion": 500 if (busy and off_clock) else 600},
                        "temp_c": {"minshire": [58], "pmic": 58}, "took_ms": 22})

    # two burn-in runs of the anchor (marks only, as runitems.py writes them; the reducer ignores them)
    for i in range(2):
        marks.append({"kind": "burnin", "item": "anchor_pi", "block": -1, "t_start_ms": t, "t_end_ms": t + 4100,
                      "rc": 0, "start_c": 58.0, "start_hot_c": 59.0, "heats": 1, "wait_s": 3.0})
        telemetry(t, t + 8000, (t + 2000, t + 6000), {"p": ANCHOR_W, "rails": None})
        t += 8000
    for pos, it in enumerate(order):
        t0 = t + 2000
        if it["kind"] == "fma":
            m = {"p": ANCHOR_W + (0.5 if (pss == faults["drift_pass"] and pos > 0) else 0.0), "rails": None}
        else:
            m = model(it)
        off_clock = (pss, it["name"]) == faults["off_clock"]
        dip_at = t0 + 1500 if (pss, it["name"]) == faults["dip"] else None
        telemetry(t, t + 8000, (t0, t0 + 4000), m, off_clock=off_clock, dip_at=dip_at)
        for k in range(10):
            rec = {"card": "synthetic", "block": pss, "pos": pos, "item": it["name"], "kind": it["kind"], "attempt": 1,
                   "start_c": 58.0, "start_hot_c": 59.0, "heats": 1, "wait_s": 3.0,
                   "t_start_ms": t0 + 400 * k, "t_end_ms": t0 + 400 * (k + 1), "ok": True}
            if it["kind"] != "fma":
                rec.update({"family": it["family"], "designed": it["designed"],
                            "arm": it["name"][3:].replace("_", ".", 1), "participants": 1024,
                            "ops": round(m["ops"] * 0.4), "ms": True, "ms_bad": 0, "late": 0,
                            **{k2: round(v * 0.4) for k2, v in m["cnt"].items()}})
            runs.append(rec)
        marks.append({"kind": "run", "item": it["name"], "block": pss, "t_start_ms": t0 - 50, "t_end_ms": t0 + 4100,
                      "pos": pos, "attempt": 1, "rc": 0, "launches": 10, "start_c": 58.0, "start_hot_c": 59.0,
                      "heats": 1, "wait_s": 3.0, "on_protocol": True})
        t += 8000
    for fn, rows in (("telemetry.jsonl", tel), ("runs.jsonl", runs), ("marks.jsonl", marks)):
        with open(os.path.join(d, fn), "w") as fh:
            fh.write("".join(json.dumps(x) + "\n" for x in rows))
    json.dump({"card": "synthetic", "args": {"target": 58.0, "max_c": 70.0}, "items": order}, open(os.path.join(d, "configs.json"), "w"))
    json.dump({"exp": "x09", "pass": pss, "card": "synthetic", "t0_ms": t0_block, "t1_ms": t, "status": "ok"},
              open(os.path.join(d, "block.json"), "w"))
    return t


faults = {"drift_pass": 913, "off_clock": (912, "x9_wr_u2"), "dip": (915, "x9_rd_u4")}
t = 1_800_000_000_000
os.makedirs(out, exist_ok=True)
smoke = [ANCHOR] + [it for it in X9 if it["name"] in ("x9_rd_rnd", "x9_wr_u4", "x9_wrh_rnd", "x9_wrh_nst")] + [ANCHOR]
t = write_pass(os.path.join(out, "p901"), 901, smoke, t, faults)
for pss in range(910, 918):
    rest = list(X9)
    random.Random(f"synthetic|{pss}|{pss}").shuffle(rest)     # runitems.py's rule: card|seed|block (seed = pass)
    t = write_pass(os.path.join(out, f"p{pss}"), pss, [ANCHOR] + rest + [ANCHOR], t + 15000, faults)
inj = {"prices": PRICES, "zero_line": ZERO_LINE, "scp_store": SCP_STORE, "rate": RATE, "base": BASE,
       "noc_one_share": NOC_ONE_SHARE, "sram_floor_share": SRAM_FLOOR_SHARE, "ddr_mv_per_toggle_w": -1.0,
       "faults": {"drift_pass": faults["drift_pass"], "off_clock": list(faults["off_clock"]), "dip": list(faults["dip"])},
       "passes": [901] + list(range(910, 918)),
       "note": "arbitrary test values, not a forecast and not a measurement"}
json.dump(inj, open(os.path.join(out, "injected.json"), "w"), indent=1)
print(f"wrote p901 and p910-p917 under {os.path.basename(out)}; injected.json")
