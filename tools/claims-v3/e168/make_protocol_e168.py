#!/usr/bin/env python3
"""E168 (Q141(o)): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json,
protocol-stoptest-die.json and their dry twins) from Q140(q)'s FROZEN design (docs/reports/data/2026-11-04-q140q-gemm-g4-stride/
predictions-e168.json, e39d06da) and amendment A2 (predictions-e168-a2.json, 226249e1); prints protocol.txt. No card. It is E159's
make_protocol_e159.py ported to E168's ten holds. Run on the Intel (it imports Q140(q)'s g4_model for E146's T0 and zeros levels):

    /usr/bin/python3 -B tools/claims-v3/e168/make_protocol_e168.py > tools/claims-v3/e168/protocol.txt

Nothing of a hold is chosen here: the nine holds' labels, values strings, order and registered subset (the six fp32 random holds),
the hold shape (12 processes of --seconds 8, budget 9.5, tail 6 s) and the stops (abs_stop_c 76 C on one sample, board_cap_w 85 W on
3 samples in a row) are read from the frozen file; the tenth hold and the gates' bounds from A2 (REGISTRATION-A2-cold-int8-zeros.md
sections 1 and 2): cold = a die mean at or below 46 C, waiting at most 360 s; warm55 = at or below 55 C, at most 300 s. E146's
harness, unchanged (E136's binary, E119's runner through run_e168.py).

WHAT THIS FILE ADDS, none of which touches a hold (E159's additions, ported):
  SMOKE        the idle card (30 s), then a 2 s launch of four zeros cells (S1, S2, S3 in fp32 and S2 in int8), each with rgm136's
               check of C against the host's own reference, and the cycles per op between 50% and 250% of E146's law (T0 at 800 MHz x
               800, make_predictions_e146.T0 on the desk's 32 MB split, the function predict_e168.py's levels come from).
  STOP TESTS   after the smoke and before the session: stoptest-board (board_cap_w 30 W on three samples; one 6 s burst of S2 fp32
               zeros, P0(800) about 38 W over a 22 W rest) and stoptest-die (abs_stop_c 30 C; the die reads about 45-47 C at rest),
               each must fire on live samples (the queue's step 5b).
  R            the session's first run: 30 s of the idle card with no launch (the chain's start, and the first hold's 20 s anchor).
  H            the registered subset: the six fp32 random holds of the frozen order.
  I            the rest of the frozen order: the three int8 holds at S2, warm.
  A            amendment A2's hold: S2 int8 zeros from cold, the tenth and last.
  ADMISSION    E105's rule, unchanged: each hold's estimate is its frozen predicted peak (P0(800) + 8.51 W) against limit_p800_w 82 W
               (the highest, S2 fp32 random's 76.63 W: every hold runs as designed); after any run whose board reading reached
               peak_lock_w 82 W, no hold with an estimate at or above that run's goes on. The smoke's and the stop test's zeros cells
               carry E146's zeros level at 800 MHz + 8.51 W.
  CAP          the session's own cap, 58 card-minutes (run_e119.py starts a run only if its planned time fits what is left); the
               smoke and the stop tests apart; the slot 66 minutes, so at most 63 card-minutes in all (the queue ends the session
               3 min before the slot's end): A2's 55 + 8.
  DRY TWINS    protocol-dry.json: 2 processes of 2.5 s, and every gate's wait cut to 6 s (the toy card rests near 51 C, so a 46 C gate
               would wait its whole bound): the code path only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
G4D_REL = "docs/reports/data/2026-11-04-q140q-gemm-g4-stride"
FROZEN = f"{G4D_REL}/predictions-e168.json"
FROZEN_SHA256 = "430f4afa266a30c35f3e4da44ebef9fbf1d1186c00ceb5e2e8ae312c8c168583"      # frozen-sha256-e168.json (e39d06da)
A2_REL = "tools/claims-v3/e168/predictions-e168-a2.json"
A2_SHA256 = "2afb290f62f7cc722c1f58837c18ab545f914863107a162653c38459c35fafe6"         # as committed in 226249e1
A2_LABEL = "S2-int8-zeros-cold"
TILES = "tools/claims-v3/kinds/tiles"
LIMIT_W = 82.0
LOCK_W = 82.0
PEAK_MARGIN_W = 8.51                      # G3's frozen peak rule (A8), as predict_e168.py
SESSION_CAP_MIN = 58.0
SLOT_MIN = 66.0
CAP_MARGIN_MIN = 3.0
GATES = {"cold": {"mode": "cool", "max_c": 46, "max_wait_s": 360}, "warm55": {"mode": "cool", "max_c": 55, "max_wait_s": 300}}
DRY_WAIT_S = 6
SHAPES = {"S1": (1, 3, 3), "S2": (3, 3, 2), "S3": (3, 5, 3)}
SMOKE_CELLS = (("S1", "fp32"), ("S2", "fp32"), ("S3", "fp32"), ("S2", "int8"))
STOPTEST_CELL = ("S2", "fp32")
# planned gate waits beyond run_hpl's own 25 s a run (logs/rest-chain.txt): a cold start after a hold about 4 min, the first one
# (after the smoke, the stop tests and R) about 0.5 min; a warm55 gate about 10 s; the worst case every cold gate at its 360 s
PLAN_COLD_AFTER_HOLD_S, PLAN_COLD_FIRST_S, PLAN_WARM_S = 240.0, 30.0, 10.0


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load():
    for rel, want in ((FROZEN, FROZEN_SHA256), (A2_REL, A2_SHA256)):
        got = sha256(os.path.join(ROOT, rel))
        if got != want:
            raise SystemExit(f"refused: {rel} sha256 {got}, registered {want}")
    return json.load(open(os.path.join(ROOT, FROZEN))), json.load(open(os.path.join(ROOT, A2_REL)))


P, A2 = load()
D = P["design"]
CELLS = dict(P["cells"])
CELLS[A2_LABEL] = A2["cells"][A2_LABEL]
ORDER = list(D["order"]) + [A2_LABEL]
SUBSET = [c for c in D["order"] if CELLS[c]["type"] == "fp32" and CELLS[c]["kind"] == "randn"]     # "registered subset the six fp32 random holds"
REL = json.load(open(os.path.join(ROOT, "tools/claims-v3/e146/predictions-e146.json")))["relation"]   # E101's relation, as E146's, E158's and E159's
B600, B800, S800 = REL["B"]["600"], REL["B"]["800"], REL["s800"]


def e146_law():
    """E146's T0 at 800 MHz and zeros levels for E168's shapes, through Q140(q)'s g4_model (add_shape146 on the desk's 32 MB split)"""
    sys.path.insert(0, os.path.join(ROOT, G4D_REL))
    import g4_model as G4  # noqa: E402
    M146, _ = G4._m146()
    for s, b in SHAPES.items():
        G4.add_shape146(s, *b)
    t0 = {(s, t): M146.T0(s, t, 800) for s in SHAPES for t in ("fp32", "int8")}
    z = {(s, t): M146.levels0(s, t, "zeros") for s in SHAPES for t in ("fp32", "int8")}
    # the int8 zeros level at S2 is the frozen cell's: check the law reproduces it (to the frozen file's 3 decimals)
    fz = CELLS["S2-int8-zeros-warm55"]["P0_w"]
    assert all(abs(z[("S2", "int8")][f] - fz[str(f)]) < 0.0006 for f in (600, 700, 800)), (z[("S2", "int8")], fz)
    return t0, z


T0_800, ZEROS = e146_law()


def zeros_values(s, t):
    MB, NB, KB = SHAPES[s]
    return f"gemmL{MB}x{NB}x{KB}:tiles:{TILES}/{t}/zeros.bin"


def hold(lab, dry):
    c = CELLS[lab]
    h = D["hold"]
    r = {"type": c["type"], "values": c["values"], "label": lab}
    if dry:
        r.update({"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5})
        r["start"] = dict(GATES[c["start"]], max_wait_s=DRY_WAIT_S)
    else:
        r.update({"launch": {"seconds": h["seconds"], "budget": h["budget"], "processes": h["processes"]}, "tail_s": h["tail_s"]})
        r["start"] = dict(GATES[c["start"]])
    return r


def rest_run(tail_s):
    return {"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": tail_s,
            "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}}


def build(dry):
    assert ORDER[:len(SUBSET)] == SUBSET and len(SUBSET) == 6
    smoke = [rest_run(3 if dry else 30)]
    for s, t in SMOKE_CELLS:
        smoke.append({"type": t, "values": zeros_values(s, t), "label": f"{s}-{t}-zeros"})
    ints = [c for c in D["order"] if c not in SUBSET]
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (30 s), then a 2 s launch of four cells' zeros, each with its check of C", "default": False,
               "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3, "runs": smoke},
              {"name": "R", "title": "the session's rest reading: 30 s of the idle card, no launch (the chain's start and the first hold's anchor)", "passes": 1,
               "shuffle": False, "runs": [rest_run(3 if dry else 30)]},
              {"name": "H", "title": "the registered subset: the six fp32 random holds of Q140(q)'s frozen order (cold, then warm55, per shape)", "passes": 1,
               "shuffle": False, "runs": [hold(lab, dry) for lab in SUBSET]},
              {"name": "I", "title": "the rest of the frozen order: the three int8 holds at S2, warm55", "passes": 1, "shuffle": False,
               "runs": [hold(lab, dry) for lab in ints]},
              {"name": "A", "title": "amendment A2 (226249e1): S2 int8 zeros from cold, the tenth and last hold", "passes": 1, "shuffle": False,
               "runs": [hold(A2_LABEL, dry)]}]
    adm = {"rest": {"fixed_p800_w": 30.0}}
    dry_c = {"zeros": 0.0}
    for lab in ORDER:
        c = CELLS[lab]
        c600 = round(c["P0_w"]["600"] - B600, 3)
        adm[lab] = {"c_ref_w": c600, "fixed_p800_w": c["predicted_peak_w"]}
        dry_c[c["values"]] = c600
    for s, t in SMOKE_CELLS + (STOPTEST_CELL,):
        lab = f"{s}-{t}-zeros"
        z = ZEROS[(s, t)]
        adm[lab] = {"c_ref_w": round(z[600] - B600, 3), "fixed_p800_w": round(z[800] + PEAK_MARGIN_W, 2)}
        dry_c[zeros_values(s, t)] = adm[lab]["c_ref_w"]
    cyc = {f"{s}-{t}-zeros": round(T0_800[(s, t)] * 800.0, 1) for s, t in SMOKE_CELLS}
    return {"experiment": "E168", "request": "Q141", "card": "aifoundry2", "order_seed": 168,
            "note": ("G4's blind test (Q140(q), frozen at e39d06da): three large-GEMM shapes nobody has run (S1 gemmL1x3x3, S2 gemmL3x3x2, S3 gemmL3x5x3), each "
                     "held about 106 s (12 processes of 8 s) in fp32 random from a cold (46 C) and a warm (55 C) start, then int8 zeros, W8A8 real and sparse50 "
                     "at S2 warm, then amendment A2's int8 zeros at S2 from cold (226249e1); under aifoundry2's own governor; nothing is set on the card"),
            "tools": {"heater": "build/e136/host/sparsity_host", "kernel": "build/e136/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": FROZEN, "predictions_sha256": FROZEN_SHA256, "amendment": A2_REL, "amendment_sha256": A2_SHA256,
            "sampler": {"every_ms": 100}, "safety": dict(D["stops"]), "caps": {"max_card_min": SESSION_CAP_MIN}, "smoke_cycles": cyc, "dry_c_w": dry_c,
            "limit_p800_w": LIMIT_W, "peak_lock_w": LOCK_W, "relation": {"B800": B800, "s800": S800}, "admission": adm, "blocks": blocks}


def stoptest(kind, dry):
    """the same runner and watcher, one block, one stop lowered so that it must fire on live samples"""
    p = build(dry)
    s, t = STOPTEST_CELL
    burst = {"launch": {"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, "tail_s": 0.5 if dry else 4}
    run = {"type": t, "values": zeros_values(s, t), "label": f"{s}-{t}-zeros", "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}}
    run.update(burst)
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    if kind == "board":
        p["safety"] = {"abs_stop_c": D["stops"]["abs_stop_c"], "board_cap_w": 30, "cap_consecutive": 3}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": D["stops"]["board_cap_w"], "cap_consecutive": 3}
    p["note"] = f"E168's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
    p["caps"] = {"max_card_min": 2}
    return p


def plan_s(r, bl):
    la = r.get("launch", bl.get("launch", {}))
    n = la.get("processes", 1)
    return n * (la.get("seconds", 2) + 1.2) + r.get("tail_s", bl.get("tail_s", 0)) + 25      # run_hpl.py's plan_s


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    for kind in ("board", "die"):
        json.dump(stoptest(kind, False), open(os.path.join(HERE, f"protocol-stoptest-{kind}.json"), "w"), indent=1)
        json.dump(stoptest(kind, True), open(os.path.join(HERE, f"protocol-stoptest-{kind}-dry.json"), "w"), indent=1)
    p = build(False)
    print(f"E168 protocol from {FROZEN} (Q140(q), frozen at e39d06da, sha256 {FROZEN_SHA256[:12]}...) and {A2_REL} (A2, 226249e1, sha256 {A2_SHA256[:12]}...); "
          f"session stops {p['safety']}; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session cap {p['caps']['max_card_min']:g} card-minutes; "
          f"gates {GATES}")
    est, worst, top, first_cold = 0.0, 0.0, 0.0, True
    nine_est = nine_worst = None
    for bl in p["blocks"]:
        print(f"block {bl['name']}: {bl['title']}")
        for r in bl["runs"]:
            la = r.get("launch", bl.get("launch", {}))
            n = la.get("processes", 1)
            pl = plan_s(r, bl)
            a = p["admission"].get(r["label"], {})
            gate_plan = gate_worst = 0.0
            st = r.get("start", bl.get("start", {}))
            if r["label"] in CELLS:
                if CELLS[r["label"]]["start"] == "cold":
                    gate_plan = PLAN_COLD_FIRST_S if first_cold else PLAN_COLD_AFTER_HOLD_S
                    gate_worst = float(st["max_wait_s"])          # a rest floor above 46 C: the gate waits its whole bound
                    first_cold = False
                else:
                    gate_plan = gate_worst = PLAN_WARM_S          # 65 to 55 C takes about 30 s, most of it inside run_hpl's 25 s
                top = max(top, a.get("fixed_p800_w") or 0)
            if bl["name"] != "SMOKE":
                est += pl + gate_plan
                worst += pl + gate_worst
            print(f"  {r['label']:36s} {n:2d} x {la.get('seconds', 2):g} s  {r['values'][:74]:74s} start {st.get('max_c')}/{st.get('max_wait_s')} s  "
                  f"estimate {a.get('fixed_p800_w')} W  plan {pl:6.1f} s + gate {gate_plan:5.1f} s (at most {gate_worst:5.1f})  cum {est / 60:5.1f} min")
            if r["label"] == D["order"][-1]:
                nine_est, nine_worst = est, worst
    smoke_s = sum(plan_s(r, p["blocks"][0]) for r in p["blocks"][0]["runs"])
    stop_s = 36.2 + 10.0
    print(f"the session (R, the nine holds, A2's hold; run_hpl plan_s with its 25 s a run, plus the planned gate waits): {est / 60:.1f} min planned, "
          f"{worst / 60:.1f} min if every cold gate waits its 360 s (a rest floor above 46 C; the session cap {SESSION_CAP_MIN:g}); the nine alone {nine_est / 60:.1f} / "
          f"{nine_worst / 60:.1f} min")
    print(f"with the smoke ({smoke_s / 60:.1f} min) and the two stop tests (about {stop_s / 60:.1f} min): about {(est + smoke_s + stop_s) / 60:.0f} card-minutes planned, "
          f"{(worst + smoke_s + stop_s) / 60:.0f} with every cold gate at its bound; the nine without A2 about {(nine_est + smoke_s + stop_s) / 60:.0f} / "
          f"{(nine_worst + smoke_s + stop_s) / 60:.0f} "
          f"(Q140(q)'s design: about 45, cap 55); the slot {SLOT_MIN:g} min, the session ended {CAP_MARGIN_MIN:g} min before it: at most {SLOT_MIN - CAP_MARGIN_MIN:g} in all")
    print(f"highest estimate {top} W (limit {p['limit_p800_w']} W): every hold runs as designed")
    print(f"smoke cycles per op at 800 MHz (E146's T0 x 800, the 50-250% check): {p['smoke_cycles']}")
    print(f"smoke / stop-test admission estimates (E146's zeros level at 800 MHz + {PEAK_MARGIN_W} W): "
          f"{ {f'{s}-{t}-zeros': p['admission'][f'{s}-{t}-zeros']['fixed_p800_w'] for s, t in SMOKE_CELLS} }")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']} "
              f"({q['blocks'][0]['runs'][0]['launch']['seconds']:g} s)")
    for f in ("protocol.json", "protocol-dry.json", "protocol-stoptest-board.json", "protocol-stoptest-die.json", "protocol-stoptest-board-dry.json",
              "protocol-stoptest-die-dry.json"):
        print(f"  {f} sha256 {sha256(os.path.join(HERE, f))}")


if __name__ == "__main__":
    main()
