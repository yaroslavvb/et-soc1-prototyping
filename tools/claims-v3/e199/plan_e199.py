#!/usr/bin/env python3
"""E199 (Q190, lane reg-e199): the plan registered with E199.md, written before any card-1 X01 datum: the card and its identity gate,
the run order on a host named aifoundry1 (E192's registered draw), the passes and the smoke, THE PREDICTED PEAK on card 1 (E192's
measured peaks on aifoundry3 plus card 1's idle difference by the frozen ledger v2's idle laws), the stops, the card time and the cap,
the rests and the window form. Standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e199/plan_e199.py           # from the top of the tree: writes plan-e199.json and plan-e199.txt
    /usr/bin/python3 -I -B tools/claims-v3/e199/plan_e199.py --check   # PLAN CHECK PASS: both re-made byte for byte, and the order equal
                                                                       # to order-e199-aifoundry1.txt (E192's own order_e192.py's output)

SPDX-License-Identifier: Apache-2.0
"""
import datetime
import gzip
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E192D = "docs/reports/data/2026-11-14-e192-intbits-aifoundry3"
ARMS = "tools/claims-v3/e192/proposal/src/arms.txt"
FROZEN = "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"
PINS = {
    ARMS: "826936fcac376d3664182e3230d7766cf8522bb6fd97f5c5366acab96cd128c5",
    FROZEN: "59ff911705137e5486efcb15c482919e3d257f800193bcc9f1d78ee7283753ce",
    E192D + "/run/telemetry.jsonl.gz": "d9cd0cf2dc9cff92440d0d8c6aee9b26663b3cd880f4117db1da8999667d129b",
    E192D + "/run/marks.jsonl": "c139a18bb5c64d11a76e7dd2588b00486f419d5ac66b76640385ab260f748dda",
    "tools/claims-v3/e192/desk/order_e192.py": "58e91673e275bf07ffb0f16245f23d68c5e56385edc24833ca82f32ddeacdfef",
}
HOST = "aifoundry1"
PASSES = 9
STOP_BOARD_W, STOP_DIE_C = 65.0, 70.0          # card 1's live stop lines: E191's kit (e191_common.py STOP_BOARD_W, STOP_DIE_C)
E37_C1_OVER_A3 = 8.865 / 8.355                 # E37's DRAM-streamed fp32 matmul at 600 MHz, W over idle (E190.md 4.3's sources)
CAP_MIN, ABOUT_MIN, E192_EST_MIN = 65, 60, 52  # E192.md section 10's cap and its estimate before its run; about 60 since fix-e199
                                               # (verify-e199 F4: E192 measured 59.52), before any datum; the cap unchanged
REST_MIN = 40


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def idle_w(F, card, T):
    """ledger_v2.idle_w() as frozen (tools/ledger/ledger_v2.py at 214cf7a4...): the footing law inside its band, else the exponential."""
    law = F["idle_laws"][card]
    q = law["quad"]
    lo, hi = law["quad_band_c"]
    if lo <= T <= hi:
        return q["a"] * T * T + q["b"] * T + q["c"]
    e = law["exp"]
    return e["B"] + e["A80"] * math.exp((T - 80.0) / e["T_L"])


def r4(x):
    return float("%.4f" % x)


def order(host, passes):
    lines = [l.split() for l in open(os.path.join(TOP, ARMS)) if l.strip() and not l.startswith("#")]
    anchor = [x[1] for x in lines if x[0] == "anchor"][0]
    base = [x[0] for x in lines if x[0] != "anchor"]
    out = []
    for p in range(passes):
        arms = list(base)
        random.Random("%s|%d" % (host, p)).shuffle(arms)
        out.append({"pass": p, "warm_up": p == 0,
                    "runs": ["burnin:" + anchor, "burnin:" + anchor, "anchor_first:" + anchor] + arms + ["anchor_last:" + anchor]})
    return anchor, base, out


def order_text(host, passes):
    """E192's desk/order_e192.py's printed form, for the same host and passes."""
    anchor, base, out = order(host, passes)
    L = ["host %r; anchor %s; %d arms shuffled a pass (the anchor's arm among them: %s); %d runs a pass with the two burn-ins and the "
         "two anchors" % (host, anchor, len(base), anchor in base, len(base) + 4),
         "smoke block (pass -1): nop, add.a.f2, add.cr.l31 (run_block.py SMOKE_ARMS; 2 s each; no burn-in, no anchor)"]
    for o in out:
        L.append("pass %d%s: %s" % (o["pass"], " (the registered warm-up)" if o["warm_up"] else "", " ".join(o["runs"])))
    return "\n".join(L) + "\n"


def peaks():
    F = json.load(open(os.path.join(TOP, FROZEN)))
    tel = []
    with gzip.open(os.path.join(TOP, E192D, "run/telemetry.jsonl.gz"), "rt") as f:
        for line in f:
            if line.startswith("{"):
                tel.append(json.loads(line))
    marks = [json.loads(l) for l in open(os.path.join(TOP, E192D, "run/marks.jsonl")) if l.startswith("{")]
    k = max(range(len(tel)), key=lambda i: tel[i]["board_w"])
    s = tel[k]
    T = s["temp_c"]["minshire"][0]
    kind = [m.get("kind") for m in marks if "t0_ms" in m and m["t0_ms"] <= s["t_ms"] <= m["t1_ms"]]
    lvl = [m for m in marks if m.get("kind") == "heater_level"][0]
    die_max = max(x["temp_c"]["minshire"][0] for x in tel)
    p_c1, p_a3 = idle_w(F, "aifoundry1-c1", T), idle_w(F, "aifoundry3", T)
    pred = s["board_w"] + (p_c1 - p_a3)
    over = s["board_w"] - p_a3
    return {
        "e192_peak_board_w": s["board_w"], "e192_peak_t_ms": s["t_ms"], "e192_peak_die_c": T, "e192_peak_during": kind,
        "e192_heater_check_board_max_w": lvl["board_max_w"], "e192_die_max_c": die_max, "e192_samples": len(tel),
        "idle_aifoundry3_at_peak_die_w": r4(p_a3), "idle_card1_at_peak_die_w": r4(p_c1), "idle_difference_w": r4(p_c1 - p_a3),
        "PREDICTED_PEAK_W": r4(pred),
        "how": "E192's highest board reading on aifoundry3 (a heater launch of the approach) plus card 1's idle law minus aifoundry3's "
               "at that sample's die reading, both laws as frozen in the ledger v2 (frozen-v2.json idle_laws)",
        "reported_sensitivity": {
            "dynamic part x s_hi of the allowance": r4(p_c1 + over * 1.03707),
            "dynamic part x E37's card-1-over-aifoundry3 fp32 ratio %.4f" % E37_C1_OVER_A3: r4(p_c1 + over * E37_C1_OVER_A3),
            "card 1's highest committed board reading (E142, docs/findings/14-card-behaviour.md)": 62.09},
        "margin_to_card1_board_stop_w": r4(STOP_BOARD_W - pred),
        "the die": "E192's die peaked at %g C on aifoundry3 (the approach heats to 59 C and launches at 58 C); the die stop is 70 C" % die_max,
    }


def window(g):
    """THE WINDOW FORM (E199.md section 10) for a booking at g (a naive Pacific datetime): last start = G + 1:30 and last end = G + 3:30,
    each rounded up to the whole minute; both inside G's Pacific day (the last end at most 23:59, the last start at most the last end
    less 70 minutes, the cap of 65 card-minutes and 5); None when no start fits."""
    def up(t):
        return t if (t.second == 0 and t.microsecond == 0) else (t.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1))
    day_end = g.replace(hour=23, minute=59, second=0, microsecond=0)
    le = min(up(g + datetime.timedelta(hours=3, minutes=30)), day_end)
    ls = min(up(g + datetime.timedelta(hours=1, minutes=30)), le - datetime.timedelta(minutes=CAP_MIN + 5))
    if ls < g:
        return None
    return ls.strftime("%H:%M"), le.strftime("%H:%M")


def build():
    bad = [rel for rel, want in PINS.items() if sha(os.path.join(TOP, rel)) != want]
    if bad:
        raise SystemExit("REFUSED: not at their pins: " + ", ".join(bad))
    anchor, base, out = order(HOST, PASSES)
    ex = {}
    for label in ("2026-11-16 09:00:00", "2026-11-16 13:00:00", "2026-11-16 10:05:42", "2026-11-16 21:13:20", "2026-11-16 22:50:00"):
        w = window(datetime.datetime.strptime(label, "%Y-%m-%d %H:%M:%S"))
        ex[label + " PST"] = {"last_start": w[0], "last_end": w[1]} if w else "no start fits that day"
    return {
        "experiment": "E199",
        "label": "REGISTERED before any card-1 X01 datum (the plan); THE PREDICTED PEAK is desk arithmetic of E192's measured telemetry "
                 "and the frozen ledger v2's idle laws",
        "card": {"box": "aifoundry1", "card": 1, "clock": "600 MHz as found (nothing set)", "ET_DEVICES": "1 in the environment of "
                 "every process that may open a device", "lock": "/run/lock/etsoc-shire1.lock (run_session.sh's LOCK default with "
                 "ET_DEVICES=1), never etsoc-shire0.lock", "nothing_on_card_0": True,
                 "identity_gate": "E191 dated note 1 (8c8f825f) section 1 item 3, before the first launch: (a) the start config read's "
                 "stderr names PCIe target /dev/et1_mgmt and Physical device ID 1, its JSON reads TDP 65 W, threshold 65 C, 600 MHz and "
                 "minion_mv below 510; (b) with the sampler running and before the smoke's first launch, every et-who holder line of "
                 "ours is on a /dev/et1_ node or lock:etsoc-shire1.lock, at least one on /dev/et1_mgmt, none on /dev/et0_ or "
                 "lock:etsoc-shire0.lock; either failing ends the session before any launch: a gate, no data",
                 "one_session_of_ours_on_aifoundry1": True},
        "runner": "E192's proposal/src as committed (run_session.sh, run_block.py, stopwatch.py, the host and kernel built on aifoundry1), "
                  "unchanged: the arms, values, order rule, windows, passes and smoke are E192's",
        "order": {"host": HOST, "rule": "random.Random('<hostname>|<pass>').shuffle over arms.txt's 32 arms (E192.md section 5)",
                  "anchor": anchor, "arms": base, "passes": out,
                  "the kit's check": "Python's socket.gethostname() on the box returns exactly 'aifoundry1' (else no session)"},
        "passes": {"count": PASSES, "warm_up": 0, "measured": PASSES - 1, "runs_a_pass": len(base) + 4, "device_calls": 3 + PASSES * (len(base) + 4)},
        "peak": peaks(),
        "stops": {"card1_live_lines": "board at or above %g W on any live sample, or minshire[0] at or above %g C: E191's kit's lines "
                                      "(e191_common.Stops), carried by E199's kit beside E192's own" % (STOP_BOARD_W, STOP_DIE_C),
                  "e192_registered_unchanged": "stopwatch.py: board above 80 W on three distinct readings in a row, minshire[0] at or "
                                               "above 70 C, the sampler quiet 10 s (or no sample in its first 60 s); run_block.py: 70 C "
                                               "or telemetry older than 5 s before a device process; the smoke's heater check above 70 W",
                  "never": "a device process killed; a reset; a power cycle; any set"},
        "card_time": {"about_card_minutes": ABOUT_MIN, "cap_card_minutes": CAP_MIN,
                      "e192_measured_card_minutes": 59.52, "e192_estimate_card_minutes": E192_EST_MIN,
                      "plan_words": "plan the booking and the rests on about 60-65 card-minutes; the cap may cut the last pass",
                      "cap_rule": "no pass starts that could end after the cap, counted from the "
                      "session's first card command (E192.md section 10; the kit's means, never a killed device process)"},
        "rests": "E199's first card command at least %d minutes after the end of the previous session of ours on aifoundry1 (card 0 is "
                 "never ours, so in practice card 1's), and the next session of ours on aifoundry1 at least %d minutes after E199's end"
                 % (REST_MIN, REST_MIN),
        "window": {"G": "the moment the card lane holds the round's booking of aifoundry1 (bash W/book.sh take aifoundry1 <lane>)",
                   "rule": window.__doc__.strip().replace("\n   ", "").replace("    ", " "), "examples": ex},
        "post": "waived: the owner's standing words, Sun 15 Nov 2026 10:22:36 PST ('don't worry about discord post, just use the "
                "machines, nobody is using them'); 17:21:16 PST ('I don't need to reserve them')",
        "package_counter": "not read",
    }


def text(p):
    k = p["peak"]
    L = ["E199's plan (REGISTERED; the peak is desk arithmetic of E192's measured telemetry and the frozen idle laws)",
         "card: aifoundry1 card 1, 600 MHz as found, ET_DEVICES=1, /run/lock/etsoc-shire1.lock, identity gate (a) and (b), nothing on card 0",
         "passes: %d (pass 0 the warm-up), %d runs a pass, %d device calls with the smoke's 3" % (
             p["passes"]["count"], p["passes"]["runs_a_pass"], p["passes"]["device_calls"]),
         "PREDICTED PEAK on card 1: %.2f W = E192's %.2f W (a heater launch, die %g C) + card 1's idle difference %.2f W (%.2f - %.2f W)" % (
             k["PREDICTED_PEAK_W"], k["e192_peak_board_w"], k["e192_peak_die_c"], k["idle_difference_w"], k["idle_card1_at_peak_die_w"],
             k["idle_aifoundry3_at_peak_die_w"]),
         "  margin to card 1's board stop (65 W): %.2f W; reported: %s" % (k["margin_to_card1_board_stop_w"], json.dumps(k["reported_sensitivity"])),
         "stops: " + p["stops"]["card1_live_lines"] + "; " + p["stops"]["e192_registered_unchanged"],
         "card time: about %d card-minutes, cap %d (E192 measured %.2f; its estimate before its run, %d): %s" % (
             p["card_time"]["about_card_minutes"], p["card_time"]["cap_card_minutes"], p["card_time"]["e192_measured_card_minutes"],
             p["card_time"]["e192_estimate_card_minutes"], p["card_time"]["plan_words"]),
         "rests: " + p["rests"],
         "window examples: " + json.dumps(p["window"]["examples"]),
         "order for host %r:" % p["order"]["host"]]
    for o in p["order"]["passes"]:
        L.append("  pass %d%s: %s" % (o["pass"], " (warm-up)" if o["warm_up"] else "", " ".join(o["runs"])))
    L.append("PLAN-E199 MADE")
    return "\n".join(L) + "\n"


def main():
    p = build()
    js = json.dumps(p, indent=1) + "\n"
    tx = text(p)
    pj, pt = os.path.join(HERE, "plan-e199.json"), os.path.join(HERE, "plan-e199.txt")
    po = os.path.join(HERE, "order-e199-aifoundry1.txt")
    if "--check" in sys.argv[1:]:
        ok1 = os.path.exists(pj) and open(pj).read() == js and os.path.exists(pt) and open(pt).read() == tx
        ok2 = os.path.exists(po) and open(po).read() == order_text(HOST, PASSES)
        print("plan-e199.json and .txt re-made byte for byte: %s; the order equals order-e199-aifoundry1.txt (E192's order_e192.py's "
              "output for aifoundry1): %s; interpreter %s" % (ok1, ok2, sys.version.split()[0]))
        print("PLAN CHECK " + ("PASS" if ok1 and ok2 else "FAIL"))
        sys.exit(0 if ok1 and ok2 else 1)
    with open(pj, "w") as f:
        f.write(js)
    with open(pt, "w") as f:
        f.write(tx)
    print("wrote plan-e199.json and plan-e199.txt; predicted peak %.2f W" % p["peak"]["PREDICTED_PEAK_W"])


if __name__ == "__main__":
    main()
