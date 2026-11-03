#!/usr/bin/env python3
"""E159 (Q139): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json, protocol-stoptest-die.json and their
dry twins) from Q139(q)'s FROZEN design (docs/reports/data/2026-11-03-q139q-gemm-g3/predictions-e159.json, committed at 91def7c4); prints protocol.txt.
No card.

    /usr/bin/python3 tools/claims-v3/e159/make_protocol_e159.py > tools/claims-v3/e159/protocol.txt

Nothing of the design is chosen here: the nine holds' labels, values strings, order, registered subset, hold shape (12 processes of --seconds 8, budget
9.5, tail 6 s, a cool start at or below 57 C waiting at most 300 s) and the stops (abs_stop_c 76 C on one sample, board_cap_w 85 W on 3 samples in a row)
are read from the frozen file and written as run_hpl.py's protocol. E146's harness, unchanged (E136's binary, E119's runner through run_e159.py).

WHAT THIS FILE ADDS, none of which touches a hold:
  SMOKE          the idle card (30 s, the session's rest reading), then a 2 s launch of four zeros cells (H1, H2, H3 in fp32 and H1 in int8), each with
                 its check of C, and the cycles per op between 50% and 250% of the frozen law's (T0 at 800 MHz x 800, predictions-e159.json T0_800_us).
  STOP TESTS     E146's, after the smoke and before the session: stoptest-board (board_cap_w 30 W on three samples; one 6 s burst of H1 fp32 zeros, P0(800)
                 38.5 W over a 22 W rest) and stoptest-die (abs_stop_c 30 C; the die reads about 45 C at rest), each must fire on live samples.
  R              the session's first run: 30 s of the idle card with no launch. G3's scorer runs Q138(t)'s chain open loop on the session's measured board
                 trace from its first sample, and anchors each hold on the measured die over the 20 s before its first process; so the first hold, H1 fp32
                 random, gets 20 s of measured rest before it, as every hold of G3's fit set had a session's history before it.
  H              the registered subset, the first six holds of the frozen order.
  Z              the three zeros holds, the rest of the order.
  ADMISSION      E105's rule, unchanged, with each hold's estimate = its frozen predicted peak (P0(800) + 8.51 W, predictions-e159.json predicted_peak_w)
                 against limit_p800_w 82 W (the brief's: "no tile, shape or hold whose predicted peak board power exceeds 82 W runs as designed"; the
                 highest is H3 fp32 random's 76.63 W, so every hold runs as designed, none duty-cycled or dropped); and after any run whose board reading
                 reached peak_lock_w 82 W, no hold with an estimate at or above that run's goes on.
  CAP            the session's own cap, 30 card-minutes (run_e119.py starts a hold only if its planned time fits what is left); the smoke and the stop
                 tests apart; at most 40 card-minutes in all (the slot).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FROZEN = "docs/reports/data/2026-11-03-q139q-gemm-g3/predictions-e159.json"
P = json.load(open(os.path.join(ROOT, FROZEN)))
D = P["design"]
CELLS = P["cells"]
REL = json.load(open(os.path.join(ROOT, "tools/claims-v3/e146/predictions-e146.json")))["relation"]   # E101's relation, as E146's and E158's
B600, B800, S800 = REL["B"]["600"], REL["B"]["800"], REL["s800"]
TILES = "tools/claims-v3/kinds/tiles"
LIMIT_W = 82.0
LOCK_W = 82.0
SMOKE_CELLS = (("H1", "fp32"), ("H2", "fp32"), ("H3", "fp32"), ("H1", "int8"))


def arm(s):
    return D["shapes"][s]["arm"]


def zeros_values(s, t):
    return f"{arm(s)}:tiles:{TILES}/{t}/zeros.bin"


def t0_800(s, t):
    """the frozen T0 at 800 MHz (us an op) of a shape and format: every cell of that shape and format carries the same"""
    v = {c["T0_800_us"] for lab, c in CELLS.items() if lab.startswith(s + "-") and c["type"] == t}
    assert len(v) == 1, (s, t, v)
    return v.pop()


def hold(lab, dry):
    c = CELLS[lab]
    h = D["hold"]
    r = {"type": c["type"], "values": c["values"], "label": lab}
    if dry:
        r.update({"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5})
    else:
        r.update({"launch": {"seconds": h["seconds"], "budget": h["budget"], "processes": h["processes"]}, "tail_s": h["tail_s"]})
    r["start"] = dict(h["start"])
    return r


def rest_run(tail_s):
    return {"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": tail_s,
            "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}}


def build(dry):
    order, subset = list(D["order"]), list(D["registered_subset"])
    assert order[:len(subset)] == subset
    smoke = [rest_run(3 if dry else 30)]
    for s, t in SMOKE_CELLS:
        smoke.append({"type": t, "values": zeros_values(s, t), "label": f"{s}-{t}-zeros"})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of four cells' zeros", "default": False,
               "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3, "runs": smoke},
              {"name": "R", "title": "the session's rest reading: 30 s of the idle card, no launch (the chain's start and the first hold's anchor)", "passes": 1,
               "shuffle": False, "runs": [rest_run(3 if dry else 30)]},
              {"name": "H", "title": "the registered subset: the first six holds of Q139(q)'s frozen order", "passes": 1, "shuffle": False,
               "runs": [hold(lab, dry) for lab in subset]},
              {"name": "Z", "title": "the rest of the frozen order: the three zeros holds", "passes": 1, "shuffle": False,
               "runs": [hold(lab, dry) for lab in order[len(subset):]]}]
    adm = {"rest": {"fixed_p800_w": 30.0}}
    dry_c = {"zeros": 0.0}
    for lab, c in CELLS.items():
        c600 = round(c["P0_w"]["600"] - B600, 3)
        adm[lab] = {"c_ref_w": c600, "fixed_p800_w": c["predicted_peak_w"]}
        dry_c[c["values"]] = c600
    for s, t in SMOKE_CELLS:
        lab = f"{s}-{t}-zeros"
        if lab not in adm:            # H1 int8 zeros, the smoke's int8 check: E146's zeros relation (B800 + s800 c, c the H1 fp32 zeros cell's)
            z = CELLS[f"{s}-fp32-zeros"]
            adm[lab] = {"c_ref_w": round(z["P0_w"]["600"] - B600, 3), "fixed_p800_w": z["predicted_peak_w"]}
        dry_c[zeros_values(s, t)] = adm[lab]["c_ref_w"]
    cyc = {f"{s}-{t}-zeros": round(t0_800(s, t) * 800.0, 1) for s, t in SMOKE_CELLS}
    return {"experiment": "E159", "request": "Q139", "card": "aifoundry2", "order_seed": 159,
            "note": "three large-GEMM shapes nobody has run (H1 gemmL2x4x8, H2 gemmL4x2x4, H3 gemmL1x2x2), each held about 106 s (12 processes of 8 s) in fp32 random and int8 full, then in zeros, from a cool start at or below 57 C, under aifoundry2's own governor; Q139(q)'s G3 design and predictions frozen at 91def7c4; nothing is set on the card",
            "tools": {"heater": "build/e136/host/sparsity_host", "kernel": "build/e136/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": FROZEN,
            "sampler": {"every_ms": 100}, "safety": dict(D["stops"]), "caps": {"max_card_min": 30}, "smoke_cycles": cyc, "dry_c_w": dry_c,
            "limit_p800_w": LIMIT_W, "peak_lock_w": LOCK_W, "relation": {"B800": B800, "s800": S800}, "admission": adm, "blocks": blocks}


def stoptest(kind, dry):
    """the same runner and watcher, one block, one stop lowered so that it must fire on live samples"""
    p = build(dry)
    burst = {"launch": {"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, "tail_s": 0.5 if dry else 4}
    run = {"type": "fp32", "values": zeros_values("H1", "fp32"), "label": "H1-fp32-zeros", "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}}
    run.update(burst)
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    if kind == "board":
        p["safety"] = {"abs_stop_c": D["stops"]["abs_stop_c"], "board_cap_w": 30, "cap_consecutive": 3}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": D["stops"]["board_cap_w"], "cap_consecutive": 3}
    p["note"] = f"E159's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
    p["caps"] = {"max_card_min": 2}
    return p


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    for kind in ("board", "die"):
        json.dump(stoptest(kind, False), open(os.path.join(HERE, f"protocol-stoptest-{kind}.json"), "w"), indent=1)
        json.dump(stoptest(kind, True), open(os.path.join(HERE, f"protocol-stoptest-{kind}-dry.json"), "w"), indent=1)
    p = build(False)
    est_s, top = 0.0, 0.0
    print(f"E159 protocol from {FROZEN} (Q139(q), frozen at 91def7c4); session stops {p['safety']}; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; "
          f"session cap {p['caps']['max_card_min']} card-minutes")
    for bl in p["blocks"]:
        print(f"block {bl['name']}: {bl['title']}")
        for r in bl["runs"]:
            la = r.get("launch", bl.get("launch", {}))
            n = la.get("processes", 1)
            plan = n * (la.get("seconds", 2) + 1.2) + r.get("tail_s", bl.get("tail_s", 0)) + 25      # run_hpl.py's plan_s
            a = p["admission"].get(r["label"], {})
            if bl["name"] != "SMOKE":
                est_s += plan
                top = max(top, a.get("fixed_p800_w") or 0)
            print(f"  {r['label']:16s} {n:2d} x {la.get('seconds', 2):g} s  {r['values'][:62]:62s} estimate {a.get('fixed_p800_w')} W  plan {plan:6.1f} s  cum {est_s / 60:5.1f} min")
    sub = sum(n * (8 + 1.2) + 6 + 25 for n in [12] * 6) + 55
    print(f"the session's planned time (run_hpl plan_s, gates included as its 25 s) {est_s / 60:.1f} min; the registered subset with the rest reading {sub / 60:.1f} min; "
          f"highest estimate {top} W (limit {p['limit_p800_w']} W)")
    print(f"smoke cycles per op at 800 MHz (T0 x 800, the 50-250% check): {p['smoke_cycles']}")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']}")


if __name__ == "__main__":
    main()
