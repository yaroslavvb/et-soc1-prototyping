#!/usr/bin/env python3
"""E167 (Q141(h)): write the session protocols from E161's committed ones (tools/claims-v3/e161/protocol-*.json, E144b's blocks), so that
every block E167 shares with E161 is E161's in content: the same tiles, launch shape, process counts, gates, stops and REST readings.
Only these change (E167.md, registered in 7ba987b3; its departure D1):
  * the header: experiment, request, note, "from";
  * G1Q's start gate G1: its REST block starts with E98's cool gate at 49 C, waiting at most 240 s with no launch (E161's REST: 99 C, 5 s,
    a gate that never waits), and the protocol carries "e167_gate" for run_e167.py: before the HOLD block's first work process the REST's
    anchor (the mean of minshire[0] over the REST file's last 120 s, as reduce_e161.rest_reading reads it) must read 49.0 C or less from at
    least 600 lines, else the session ends with exit 6 and no work process;
  * G1Q's cap: 21 card-minutes (E161: 17), for that wait.
The tools (Q139(k)'s C-logging wrapper, E80's kernel and sampler), the safety stops (72 C, over 80 W on 3 samples; the stop tests lower one),
the smoke's DMA rule and every other block are E161's, byte for byte in content.

    python3 tools/claims-v3/e167/make_protocols_e167.py        # from the top of the repository

Writes, beside this file (each with a -dry twin, made by E161's dry(): launch blocks cut to one process, the REST to 20 s, cool gates waiting
20 s): protocol-smoke.json, protocol-stoptest-die.json, protocol-stoptest-board.json, protocol-g1q.json, protocol-end.json, protocol-g2q.json,
protocol-end2.json
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E161 = os.path.join(ROOT, "tools/claims-v3/e161")
STEPS = ("smoke", "stoptest-die", "stoptest-board", "g1q", "end", "g2q", "end2")
G1Q_REST_START = {"mode": "cool", "max_c": 49, "max_wait_s": 240}
G1Q_CAP = 21
GATE = {"block": "HOLD", "rest_anchor_max_c": 49.0, "window_s": 120.0, "min_lines": 600,
        "note": ("E167.md G1: the HOLD block's work starts only if the REST's anchor (the mean of minshire[0] over the REST file's last 120 s, "
                 "reduce_e161.rest_reading's reading) is 49.0 C or less from at least 600 lines; else the session ends with exit 6 and no "
                 "work process (RK3-b: not scored, the start gate)")}
NOTE = ("E161's blocks (E144b's, E133's), run by run_e167.py over E144b's chain (run_kspeed.py over E64's run_hpl.py, E111's idle-login rule), "
        "with Q139(k)'s C log on every launch (E160's wrapper and host): REST holds no launch; nothing is set on the card; the residency read "
        "run_hpl.py makes after every run is not sent; the holds are Q139(e)'s frozen 13 minutes of its frozen pool-6 tiles, scored by Q140(e)'s "
        "frozen predictions (E167.md)")


def dump(obj, name):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(p, ROOT))


def dry(proto):
    """make_protocols_e161.py's dry(), copied: every launch block cut to one process, the REST to 20 s, cool gates waiting 20 s."""
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


def main():
    for step in STEPS:
        src = os.path.join(E161, f"protocol-{step}.json")
        e = json.load(open(src))
        assert e["experiment"] == "E161", src
        out = copy.deepcopy(e)
        out["experiment"] = "E167"
        out["request"] = "Q141(h)"
        out["note"] = NOTE if not step.startswith("stoptest") else e["note"].replace("E161's", "E167's (E161's, unchanged)")
        out["from"] = {"protocol": f"tools/claims-v3/e161/protocol-{step}.json", "blocks": "unchanged" if step != "g1q" else
                       "E161's REST and HOLD unchanged but for the REST's start gate (cool, 49 C, 240 s: E167.md G1)",
                       "E161_from": e.get("from")}
        if step == "g1q":
            names = [b["name"] for b in out["blocks"]]
            assert names == ["REST", "HOLD"], names
            assert out["blocks"][0]["start"] == {"mode": "cool", "max_c": 99, "max_wait_s": 5}, out["blocks"][0]["start"]
            assert out["blocks"][1]["launch"]["processes"] == 93 and out["blocks"][1]["start"]["max_c"] == 57
            out["blocks"][0]["start"] = dict(G1Q_REST_START)
            out["blocks"][0]["title"] = ("the rest reading: no launch, the 10 Hz sampler on the idle card; it starts once the die reads 49 C or less "
                                         "(at most 240 s of waiting, E167.md G1); the last 120 s are G1Q's anchor")
            out["caps"] = {"max_card_min": G1Q_CAP}
            out["e167_gate"] = dict(GATE)
        if step == "g2q":
            assert [b["name"] for b in out["blocks"]] == ["REST", "HOLD"] and out["blocks"][1]["launch"]["processes"] == 91
        assert out["safety"]["abs_stop_c"] <= 72 and out["safety"]["board_cap_w"] <= 80 and out["safety"]["cap_consecutive"] <= 3
        dump(out, f"protocol-{step}.json")
        dd = dry(out)
        if step == "g1q":
            # the dry twin's REST tail is 20 s (dry()), so the registered "half of the expected lines" (600 of 1,200) is 100 of its 200
            dd["e167_gate"]["min_lines"] = 100
            dd["e167_gate"]["note"] += " (the dry twin: its REST tail is 20 s, so half of its lines is 100)"
        dump(dd, f"protocol-{step}-dry.json")


if __name__ == "__main__":
    main()
