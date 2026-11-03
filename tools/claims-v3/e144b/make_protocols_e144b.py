#!/usr/bin/env python3
"""E144b (Q138): write the session protocols from E133's committed ones (tools/claims-v3/e133/protocol-*.json, which carry E111's
blocks), so that every block E144b shares with E133 is E133's in content: the same runs, gates, launch shape and tiles. Only these change:
  * the header: experiment, request, step, note, caps;
  * the hold lengths, to Q138(t)'s frozen 15 minutes (predictions-e144.json aifoundry2.G1/G2 "minutes": 15.0): H-I8 runs 107 of E133's
    190 processes (E133's W1B hold took 1596 s for 190, 8.40 s each: 107 is 899 s) and H-F32 106 (E133's took 1620 s, 8.53 s each: 904 s);
  * the safety stops, tightened to Q138(t)'s frozen aifoundry2 stops (predictions-e144.json rules.stops.aifoundry2): a die reading
    >= 72 C, or a board reading over 93 W on 3 samples. run_hpl.py's watcher applies abs_stop_c to the die mean AND to the hottest
    sensor (minshire[0] and minshire[2]) on every live sampler line, as E133 applied its 80 C.

    python3 tools/claims-v3/e144b/make_protocols_e144b.py        # from the top of the repository

Writes, beside this file (each with a -dry twin: launch blocks cut to one process, REST to 20 s, cool gates waiting 20 s, as E133's):
  protocol-smoke.json           E133's SMOKE unchanged (20 s of the idle card, then one 2 s launch each of fp32 zeros, int8 -1s, fp16 ones)
  protocol-stoptest-die.json    the die stop's path: abs_stop_c 30 C, one 2 s int8 -1s launch planned; must trip on the first live line,
                                before the launch (exit 4)
  protocol-stoptest-board.json  the board stop's path: board_cap_w 30 W on 3 samples, one 6 s int8 -1s launch (about 39 W on this card);
                                must trip inside the launch on the third live line over 30 W (exit 4)
  protocol-g1.json              G1: E133's W1B blocks (E98's REST, 120 s, then H-I8 behind E98's 57 C gate), 107 processes
  protocol-end.json             E133's END unchanged (E98's REST block, 120 s): G1's cool-down
  protocol-g2.json              G2: E133's W2 REST block, then E133's W2 HOLDF block (fp32 randn from at once, the card's own governor),
                                106 processes
  protocol-end2.json            E133's END2 unchanged: G2's cool-down
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E133 = os.path.join(ROOT, "tools/claims-v3/e133")
SAFETY = {"abs_stop_c": 72, "board_cap_w": 93, "cap_consecutive": 3,
          "note": ("Q138(t)'s frozen aifoundry2 stops (predictions-e144.json rules.stops.aifoundry2, c2f9920d): the hold ends at a die "
                   "reading >= 72 C or a board reading > 93 W on 3 samples (E133's 80 C / 93 W with the die tightened). run_hpl.py's "
                   "watcher reads every live sampler line and applies 72 C to the die mean and to the hottest sensor. E111's and E133's "
                   "H-F32 peaked at 88.04 and 88.65 W (none over 90 W) and a 67-68 C die mean; the hottest sensor's carried running "
                   "maximum read 69-70 C")}
CAPS = {"SMOKE": 4, "STOPTEST-DIE": 2, "STOPTEST-BOARD": 2, "G1": 19, "END": 5, "G2": 19, "END2": 5}
N_HOLD = {"G1": 107, "G2": 106}
NOTE = ("E133's blocks (E111's), run by run_e144b.py over E133's chain (run_kspeed.py over E64's run_hpl.py, E111's idle-login rule): "
        "REST holds no launch; nothing is set on the card; the residency read run_hpl.py makes after every run is not sent; the holds "
        "are Q138(t)'s frozen 15 minutes")


def dump(obj, name):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(p, ROOT))


def load(name):
    p = os.path.join(E133, name)
    d = json.load(open(p))
    d["_path"] = p
    return d


def header(src, step, safety=None, note=NOTE):
    out = {k: copy.deepcopy(v) for k, v in src.items() if k not in ("blocks", "_path")}
    out["experiment"] = "E144b"
    out["request"] = "Q138"
    out["step"] = step
    out["note"] = note
    out["caps"] = {"max_card_min": CAPS[step]}
    out["safety"] = copy.deepcopy(safety or SAFETY)
    out["from"] = {"protocol": f"tools/claims-v3/e133/{os.path.basename(src['_path'])}", "blocks": "unchanged"}
    return out


def dry(proto):
    """make_protocols_e133.py's dry(), copied: every launch block cut to one process, the REST to 20 s, cool gates waiting 20 s."""
    d = copy.deepcopy(proto)
    for b in d["blocks"]:
        if b["name"] in ("REST",):
            b["tail_s"] = 20
        else:
            b.setdefault("launch", {})
            b["launch"]["processes"] = 1 if b["launch"].get("processes", 1) else 0
        b.get("start", {}).update({"max_wait_s": 20}) if b.get("start", {}).get("mode") == "cool" else None
    d["caps"] = {"max_card_min": min(15, d["caps"]["max_card_min"])}
    return d


def stoptest(kind):
    sm = load("protocol-smoke.json")
    run = copy.deepcopy(next(r for r in sm["blocks"][0]["runs"] if r["label"] == "int8-neg_ones"))
    secs = 2 if kind == "die" else 6
    blk = {"name": "STOPTEST", "title": f"the {kind} stop's path on live samples (the stop lowered so that it must trip)",
           "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": secs, "budget": secs + 1.5, "processes": 1},
           "tail_s": 4, "runs": [run]}
    sf = {"abs_stop_c": 30, "board_cap_w": 93, "cap_consecutive": 3} if kind == "die" else \
         {"abs_stop_c": 72, "board_cap_w": 30, "cap_consecutive": 3}
    sf["note"] = (f"E144b's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; "
                  "the session must end with exit 4")
    out = header(sm, f"STOPTEST-{kind.upper()}", sf, note=f"E144b's {kind} stop-path test: the smoke's int8 -1s tile, E133's chain")
    out["from"] = {"protocol": "tools/claims-v3/e133/protocol-smoke.json", "blocks": "the smoke's int8 neg_ones run, one launch"}
    out["blocks"] = [blk]
    return out


def main():
    for step, src in (("SMOKE", "protocol-smoke.json"), ("END", "protocol-end.json"), ("END2", "protocol-end2.json")):
        e = load(src)
        out = header(e, step)
        out["blocks"] = copy.deepcopy(e["blocks"])
        dump(out, f"protocol-{step.lower()}.json")
        dump(dry(out), f"protocol-{step.lower()}-dry.json")
    for kind in ("die", "board"):
        out = stoptest(kind)
        dump(out, f"protocol-stoptest-{kind}.json")
        dump(dry(out), f"protocol-stoptest-{kind}-dry.json")
    # G1: E133's W1B (REST, then HOLD: int8 neg_ones behind the 57 C gate), the hold cut to 107 processes
    e = load("protocol-w1b.json")
    g1 = header(e, "G1")
    g1["blocks"] = copy.deepcopy(e["blocks"])
    assert [b["name"] for b in g1["blocks"]] == ["REST", "HOLD"]
    h = g1["blocks"][1]
    assert h["runs"][0]["label"] == "int8-neg_ones-hold" and h["launch"]["processes"] == 190
    h["launch"]["processes"] = N_HOLD["G1"]
    h["title"] = ("E144b G1 (Q138(t)'s frozen H-I8): int8 neg_ones from rest, 107 back-to-back 8 s processes (~15.0 min) behind E98's "
                  "57 C gate; the steady reading is the last 300 s")
    g1["from"]["blocks"] = "W1B's REST and HOLD, unchanged but for the hold's 107 processes (was 190) and its title"
    dump(g1, "protocol-g1.json")
    dump(dry(g1), "protocol-g1-dry.json")
    # G2: E133's W2 REST block, then its HOLDF block (fp32 randn from at once under the card's own governor), cut to 106 processes
    e = load("protocol-w2.json")
    g2 = header(e, "G2")
    rest = copy.deepcopy(next(b for b in e["blocks"] if b["name"] == "REST"))
    hf = copy.deepcopy(next(b for b in e["blocks"] if b["name"] == "HOLDF"))
    assert hf["runs"][0]["label"] == "fp32-randn-hold" and hf["launch"]["processes"] == 190
    hf["launch"]["processes"] = N_HOLD["G2"]
    hf["title"] = ("E144b G2 (Q138(t)'s frozen H-F32): fp32 randn, 106 back-to-back 8 s processes (~15.1 min) from at once after the REST, "
                   "under the card's own governor; the steady reading is the last 300 s")
    g2["blocks"] = [rest, hf]
    g2["from"]["blocks"] = "W2's REST and HOLDF, unchanged but for HOLDF's 106 processes (was 190) and its title; W2's SUS and HOLD dropped"
    dump(g2, "protocol-g2.json")
    dump(dry(g2), "protocol-g2-dry.json")


if __name__ == "__main__":
    main()
