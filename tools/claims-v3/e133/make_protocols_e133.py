#!/usr/bin/env python3
"""E133 (Q136): write the session protocols from E111's committed ones, so every block E133 shares with E111 is E111's byte for
byte in content (the same runs, gates, launch shape and tiles), and only the header changes: experiment, request, step, note,
caps, and the safety stops, tightened to E126's (80 C on the die mean or the hottest sensor; 93 W on three samples).

    python3 tools/claims-v3/e133/make_protocols_e133.py        # from the top of the repository

Writes, beside this file:
  protocol-smoke.json  E111's SMOKE (E98's: 20 s of the idle card, three 2 s launches), its own session
  protocol-w2.json     E111's W2: E98's probe (REST, SUS: nine 76 s runs behind the 57 C gate, HOLD of 39) and then H-F32
                       (190 processes of fp32 randn from at once, under the card's own governor)
  protocol-end.json    E111's END: E98's REST block, the idle after H-F32
  protocol-w1b.json    E111's W1B (its amendment A2): E98's REST block, then H-I8 from rest (190 processes of int8 neg_ones
                       behind the 57 C gate)
  protocol-end2.json   E111's END2: E98's REST block, the idle after H-I8
  protocol-w3.json     the optional afternoon probe: W2's first three blocks (REST, SUS, HOLD of 39), E98's probe exactly
  protocol-*-dry.json  the same with every launch block cut to one process and the rest to 20 s (run_e133.py --dry),
                       as make_protocols_e111.py cut E111's
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E111 = os.path.join(ROOT, "tools/claims-v3/e111")
SAFETY = {"abs_stop_c": 80, "board_cap_w": 93, "cap_consecutive": 3,
          "note": ("E126's tightened stops (the owner's rules of 2 November 2026: nothing that risks a power cycle): 80 C on the die mean "
                   "or the hottest sensor, 93 W on three samples. E111's own W2 peaked at 88.04 W (fp32 randn's first seconds at "
                   "800 MHz) and 68 C die mean; its hottest sensor's running maximum read 70 C")}
CAPS = {"SMOKE": 4, "W2": 56, "END": 5, "W1B": 34, "END2": 5, "W3": 30}


def dump(obj, name):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(p, ROOT))


def header(src, step):
    out = {k: copy.deepcopy(v) for k, v in src.items() if k != "blocks"}
    out["experiment"] = "E133"
    out["request"] = "Q136"
    out["step"] = step
    out["note"] = ("E111's blocks, unchanged (E98's runner: run_kspeed.py over E64's run_hpl.py, run by run_e133.py): REST holds no "
                   "launch; SUS is E98's nine runs in E98's order behind E98's 57 C gate; nothing is set on the card; the residency "
                   "read run_hpl.py makes after every run is not sent (run_e133.py)")
    out["caps"] = {"max_card_min": CAPS[step]}
    out["safety"] = copy.deepcopy(SAFETY)
    out["from"] = {"protocol": f"tools/claims-v3/e111/{os.path.basename(src['_path'])}", "blocks": "unchanged"}
    out.pop("_path", None)
    return out


def dry(proto):
    """make_protocols_e111.py's dry(), copied: every launch block cut to one process, the REST to 20 s, cool gates waiting 20 s."""
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


def load(name):
    p = os.path.join(E111, name)
    d = json.load(open(p))
    d["_path"] = p
    return d


def main():
    for step, src in (("SMOKE", "protocol-smoke.json"), ("W2", "protocol-w2.json"), ("END", "protocol-end.json"),
                      ("W1B", "protocol-w1b.json"), ("END2", "protocol-end2.json")):
        e = load(src)
        out = header(e, step)
        out["blocks"] = copy.deepcopy(e["blocks"])
        dump(out, f"protocol-{step.lower()}.json")
        dump(dry(out), f"protocol-{step.lower()}-dry.json")
    e = load("protocol-w2.json")
    w3 = header(e, "W3")
    w3["from"]["blocks"] = "W2's first three blocks (REST, SUS, HOLD of 39), unchanged: E98's probe; no H-F32"
    w3["blocks"] = [copy.deepcopy(b) for b in e["blocks"] if b["name"] in ("REST", "SUS", "HOLD")]
    assert [b["name"] for b in w3["blocks"]] == ["REST", "SUS", "HOLD"]
    dump(w3, "protocol-w3.json")
    dump(dry(w3), "protocol-w3-dry.json")


if __name__ == "__main__":
    main()
