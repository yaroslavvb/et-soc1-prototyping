#!/usr/bin/env python3
"""E111 (Q133): write the session protocols from E98's and E85's committed ones, so every block that E111 shares with them
is theirs byte for byte in content (same runs, same gates, same launch shape, same tiles).

    python3 tools/claims-v3/e111/make_protocols_e111.py        # from the top of the repository

Writes, beside this file:
  protocol-smoke.json   E98's SMOKE block (20 s idle, three 2 s launches), as its own session
  protocol-w1.json      warm probe W1 = E98's REST + SUS (nine runs, same order, same 57 C gate) + HOLD of int8 neg_ones
                        extended from E98's 39 processes to HOLD_N (E98's 5.5 min reading is its first 39; the rest is
                        the steady hold H-I8)
  protocol-w2.json      warm probe W2 = E98's REST + SUS + HOLD (39 processes, E98's exactly) + HOLDF: fp32 randn,
                        HOLD_N processes from at once (the steady hold H-F32, random fp32 at full duty under the governor)
  protocol-end.json     E98's REST block alone: the idle after H-F32
  protocol-*-dry.json   the same with every launch block cut to one process and the rest to 20 s (run_e111.py --dry)
  protocol-cam.json     one run_hlc.py session (E63's runner, as E73 used it): E85's 192-minion sets F32R (fp32 randn) and
                        F32Z (fp32 zeros), ten 10 s phases an arm, a 200 s lap, 0.005 Hz, CAM_LAPS laps of which 1 warm-up
  protocol-cam-dry.json the same shape cut to four laps of 20 s (one launch an arm), for the dry run with the real camera
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E98 = os.path.join(ROOT, "tools/claims-v3/kspeed/e98/protocol.json")
E85 = os.path.join(ROOT, "tools/claims-v3/hlk/protocol-e85.json")

HOLD_N = 190          # 8 s processes, about 8.37 s apart in E98 (326.2 s for 39): 190 x 8.37 s = 26.5 min
HOLD39 = 39
CAM_N_PER_ARM = 10    # ten 10 s phases an arm: a 200 s lap, 0.005 Hz
CAM_LAPS = 6          # protocol v2: cycles is the total, warm-up included
CAM_WARMUP = 1


def dump(obj, name):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(p, ROOT))


def base(e98, step, max_card_min):
    out = {k: copy.deepcopy(v) for k, v in e98.items() if k != "blocks"}
    out["experiment"] = "E111"
    out["request"] = "Q133"
    out["step"] = step
    out["note"] = ("E98's runner and blocks (run_e98.py's run_kspeed.py over E64's run_hpl.py, unchanged): REST holds no launch; "
                   "SUS is E98's nine runs in E98's order behind E98's 57 C gate; nothing is set on the card")
    out["caps"] = {"max_card_min": max_card_min}
    out["safety"] = {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3,
                     "note": "E98's stops, unchanged: 85 C on the die mean or the hottest sensor (the lab's 85-90 C stop for long full-load runs, "
                             "AGENT.md section 4), 97 W on three samples"}
    return out


def blk(e98, name):
    return copy.deepcopy(next(b for b in e98["blocks"] if b["name"] == name))


def dry(proto):
    d = copy.deepcopy(proto)
    for b in d["blocks"]:
        if b["name"] in ("REST",):
            b["tail_s"] = 20
        else:
            b.setdefault("launch", {})
            b["launch"]["processes"] = 1 if b["launch"].get("processes", 1) else 0
        b.get("start", {}).update({"max_wait_s": 20}) if b.get("start", {}).get("mode") == "cool" else None
    d["caps"] = {"max_card_min": 15}
    return d


def main():
    e98 = json.load(open(E98))
    # SMOKE as its own session (default true in its own file)
    sm = base(e98, "SMOKE", 4)
    b = blk(e98, "SMOKE")
    b["default"] = True
    sm["blocks"] = [b]
    dump(sm, "protocol-smoke.json")

    # W1: REST, SUS, HOLD of HOLD_N
    w1 = base(e98, "W1", 50)
    hold = blk(e98, "HOLD")
    hold["launch"]["processes"] = HOLD_N
    hold["title"] = (f"the hold: {HOLD_N} back-to-back 8 s processes (~26.5 min) of int8 neg_ones from E98's 57 C gate; E98's reading is the "
                     f"120 s ending with process {HOLD39}, the steady reading (H-I8) is the last 300 s")
    w1["blocks"] = [blk(e98, "REST"), blk(e98, "SUS"), hold]
    dump(w1, "protocol-w1.json")

    # W2: REST, SUS, HOLD (39, E98's exactly), HOLDF fp32 randn
    w2 = base(e98, "W2", 56)
    holdf = {"name": "HOLDF",
             "title": f"the fp32 hold (H-F32): {HOLD_N} back-to-back 8 s processes (~26.5 min) of fp32 randn, from at once after E98's hold, "
                      f"under the card's own governor; the steady reading is the last 300 s",
             "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5},
             "launch": {"seconds": 8, "budget": 9.5, "processes": HOLD_N}, "tail_s": 6,
             "runs": [{"type": "fp32", "values": "file:tools/claims-v3/kinds/tiles/fp32/randn.bin", "label": "fp32-randn-hold"}]}
    w2["blocks"] = [blk(e98, "REST"), blk(e98, "SUS"), blk(e98, "HOLD"), holdf]
    dump(w2, "protocol-w2.json")

    # END: the idle after H-F32
    en = base(e98, "END", 5)
    en["blocks"] = [blk(e98, "REST")]
    dump(en, "protocol-end.json")

    # amendment A2: W1B = E98's REST + the int8 neg_ones hold of HOLD_N processes from rest (no sustained series before it);
    # END2 = E98's REST block, the idle after it
    w1b = base(e98, "W1B", 34)
    holdb = blk(e98, "HOLD")
    holdb["launch"]["processes"] = HOLD_N
    holdb["title"] = (f"amendment A2: the int8 hold H-I8 from rest, {HOLD_N} back-to-back 8 s processes (~26.5 min) of int8 neg_ones behind "
                      f"E98's 57 C gate; the steady reading is the last 300 s")
    w1b["blocks"] = [blk(e98, "REST"), holdb]
    dump(w1b, "protocol-w1b.json")
    en2 = base(e98, "END2", 5)
    en2["blocks"] = [blk(e98, "REST")]
    dump(en2, "protocol-end2.json")

    for p, n in ((w1, "protocol-w1-dry.json"), (w2, "protocol-w2-dry.json"), (en, "protocol-end-dry.json"), (sm, "protocol-smoke-dry.json"),
                 (w1b, "protocol-w1b-dry.json"), (en2, "protocol-end2-dry.json")):
        dump(dry(p), n)

    # the camera session: run_hlc.py's protocol v2, E85's sets and safety, one block at 0.005 Hz
    e85 = json.load(open(E85))
    cam = {k: copy.deepcopy(e85[k]) for k in ("version", "pad_to_dwell", "pad_to_dwell_note", "heater", "safety", "camera")}
    cam.update({"experiment": "E111", "request": "Q133", "card": "aifoundry2",
                "title": "The heat path below 0.01 Hz: fp32 randn against fp32 zeros on E85's 192 minions, ten 10 s phases an arm, "
                         "a 200 s lap (0.005 Hz), filmed from the back of the board"})
    cam["sets"] = {k: copy.deepcopy(e85["sets"][k]) for k in ("F32R", "F32Z")}
    phases = [{"set": "F32R", "dwell_s": 10.0, "launches": 1}] * CAM_N_PER_ARM + [{"set": "F32Z", "dwell_s": 10.0, "launches": 1}] * CAM_N_PER_ARM
    order = ["F32R"] * CAM_N_PER_ARM + ["F32Z"] * CAM_N_PER_ARM
    blockc = {"id": "E111-F05", "name": "E111-F05", "title": "fp32 randn against fp32 zeros, 192 minions, 0.005 Hz (ten launches an arm)",
              "kind": "lockin", "role": "kind", "format": "fp32", "kind_name": "randn", "n_per_arm": CAM_N_PER_ARM,
              "lap_s": 200.0, "f_hz": 0.005, "cycles": CAM_LAPS, "warmup_cycles": CAM_WARMUP,
              "lap_phase_orders": [order] * CAM_LAPS, "phases": [dict(p) for p in phases],
              "predicted": "predictions-e111.json camera", "pass_rule": "E111.md, Part C"}
    cam["blocks"] = [blockc]
    cam["session"] = {"pre_idle_s": 30, "post_idle_s": 30, "block_gap_s": 0, "block_order": ["E111-F05"]}
    cam["caps"] = {"max_card_min": 24, "max_wall_min": 28}
    cam["planned_block_seconds"] = {"E111-F05": CAM_LAPS * 200.0}
    cam["revision"] = "E111 pre-registration"
    dump(cam, "protocol-cam.json")
    cd = copy.deepcopy(cam)
    bd = cd["blocks"][0]
    bd.update({"n_per_arm": 1, "lap_s": 20.0, "f_hz": 0.05, "cycles": 4, "warmup_cycles": 1,
               "lap_phase_orders": [["F32R", "F32Z"]] * 4, "phases": [{"set": "F32R", "dwell_s": 10.0, "launches": 1},
                                                                   {"set": "F32Z", "dwell_s": 10.0, "launches": 1}]})
    cd["session"] = {"pre_idle_s": 10, "post_idle_s": 10, "block_gap_s": 0, "block_order": ["E111-F05"]}
    cd["caps"] = {"max_card_min": 3, "max_wall_min": 5}
    cd["planned_block_seconds"] = {"E111-F05": 80.0}
    dump(cd, "protocol-cam-dry.json")


if __name__ == "__main__":
    main()
