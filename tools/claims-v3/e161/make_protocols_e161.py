#!/usr/bin/env python3
"""E161 (Q139): write the session protocols from E144b's committed ones (tools/claims-v3/e144b/protocol-*.json, E133's blocks), so that
every block E161 shares with E144b is E144b's in content: the same gates, launch shape and REST readings. Only these change:
  * the header: experiment, request, step, note, caps;
  * the tools: the heater is Q139(k)'s C-logging wrapper tools/claims-v3/ccheck/sparsity_ccheck.sh (E160's), the kernel and the sampler
    stay E80's (build/sparsity_t2/kernel/sparsity.elf, build/ettelem-hpl/ettelem);
  * the two holds' tiles: Q139(e)'s frozen hold candidates from blind pool 6 (predictions-q139e.json aifoundry2.holds):
      G1Q  int8.b_line_zero_ff             (tools/claims-v3/kinds/blind6/tiles/int8/int8.b_line_zero_ff.bin), label b6-int8.b_line_zero_ff
      G2Q  fp32.real_smol_softmax_v_causal (tools/claims-v3/kinds/blind6/tiles/fp32/fp32.real_smol_softmax_v_causal.bin), label b6-...
  * the hold lengths, to Q139(e)'s frozen 13 minutes, as process counts (E144b's D3): G1Q 93 of E144b G1's 8.37 s processes (8.41 s with
    the C log's 24 x 1.5 ms: 782 s) and G2Q 91 of E144b G2's 8.54 s (8.58 s: 781 s);
  * the safety stops, Q139(e)'s for E161 (predictions-q139e.json rules: "a hold ends at a die reading >= 72 C or board >= 80 W on 3
    consecutive live samples (at most 85 W, tested in the smoke)"): abs_stop_c 72, board_cap_w 80, cap_consecutive 3. run_hpl.py's watcher
    applies abs_stop_c to the die mean and to the hottest sensor (minshire[0] and minshire[2]) on every live sampler line;
  * the smoke carries the DMA rule's numbers (E160's rule on E144b's committed launches): E144b's smoke launch gap median (1 ms), its holds'
    longest device-held time (8.70 s) and most launches in a process (24), the limit 9.2 s of the 9.5 s budget.

    python3 tools/claims-v3/e161/make_protocols_e161.py        # from the top of the repository

Writes, beside this file (each with a -dry twin: launch blocks cut to one process, REST to 20 s, cool gates waiting 20 s, as E144b's):
  protocol-smoke.json, protocol-stoptest-die.json, protocol-stoptest-board.json, protocol-g1q.json, protocol-end.json, protocol-g2q.json,
  protocol-end2.json
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E144B = os.path.join(ROOT, "tools/claims-v3/e144b")
TOOLS = {"heater": "tools/claims-v3/ccheck/sparsity_ccheck.sh", "kernel": "build/sparsity_t2/kernel/sparsity.elf",
         "ettelem": "build/ettelem-hpl/ettelem"}
SAFETY = {"abs_stop_c": 72, "board_cap_w": 80, "cap_consecutive": 3,
          "note": ("Q139(e)'s frozen E161 stops (predictions-q139e.json rules, 455c46c1): the hold ends at a die reading >= 72 C or a board "
                   "reading > 80 W on 3 consecutive live samples (section 22: at most 85 W on live samples, tested in the smoke). run_hpl.py's "
                   "watcher reads every live sampler line and applies 72 C to the die mean and to the hottest sensor. M8's 95% peaks: "
                   "G1Q 53.3 W, G2Q 68.2 W")}
CAPS = {"SMOKE": 4, "STOPTEST-DIE": 2, "STOPTEST-BOARD": 2, "G1Q": 17, "END": 5, "G2Q": 17, "END2": 5}
N_HOLD = {"G1Q": 93, "G2Q": 91}
HOLD_RUN = {"G1Q": {"type": "int8", "values": "file:tools/claims-v3/kinds/blind6/tiles/int8/int8.b_line_zero_ff.bin",
                    "label": "b6-int8.b_line_zero_ff"},
            "G2Q": {"type": "fp32", "values": "file:tools/claims-v3/kinds/blind6/tiles/fp32/fp32.real_smol_softmax_v_causal.bin",
                    "label": "b6-fp32.real_smol_softmax_v_causal"}}
DMA = {"e144b_smoke_gap_ms_median": 1.0, "e144b_hold_held_s_max": 8.70, "launches": 24, "projected_held_max_s": 9.2, "budget_s": 9.5,
       "source": ("E144b's committed launches (docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/{SMOKE,G1,G2}/launches.jsonl.gz): "
                  "the smoke's launch gaps median 1 ms; G1/G2 'device held for' max 8.63 / 8.70 s; at most 24 launches a process")}
NOTE = ("E144b's blocks (E133's), run by run_e161.py over E144b's chain (run_kspeed.py over E64's run_hpl.py, E111's idle-login rule), with "
        "Q139(k)'s C log on every launch (E160's wrapper and host): REST holds no launch; nothing is set on the card; the residency read "
        "run_hpl.py makes after every run is not sent; the holds are Q139(e)'s frozen 13 minutes of its frozen pool-6 tiles")


def dump(obj, name):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(p, ROOT))


def load(name):
    p = os.path.join(E144B, name)
    d = json.load(open(p))
    d["_path"] = p
    return d


def header(src, step, safety=None, note=NOTE):
    out = {k: copy.deepcopy(v) for k, v in src.items() if k not in ("blocks", "_path")}
    out["experiment"] = "E161"
    out["request"] = "Q139"
    out["step"] = step
    out["note"] = note
    out["tools"] = dict(TOOLS)
    out["caps"] = {"max_card_min": CAPS[step]}
    out["safety"] = copy.deepcopy(safety or SAFETY)
    out["from"] = {"protocol": f"tools/claims-v3/e144b/{os.path.basename(src['_path'])}", "blocks": "unchanged"}
    return out


def dry(proto):
    """make_protocols_e144b.py's dry(), copied: every launch block cut to one process, the REST to 20 s, cool gates waiting 20 s."""
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
    for step, src in (("SMOKE", "protocol-smoke.json"), ("END", "protocol-end.json"), ("END2", "protocol-end2.json")):
        e = load(src)
        out = header(e, step)
        out["blocks"] = copy.deepcopy(e["blocks"])
        if step == "SMOKE":
            out["dma"] = dict(DMA)
        dump(out, f"protocol-{step.lower()}.json")
        dump(dry(out), f"protocol-{step.lower()}-dry.json")
    for kind in ("die", "board"):
        e = load(f"protocol-stoptest-{kind}.json")
        sf = {"abs_stop_c": 30, "board_cap_w": 80, "cap_consecutive": 3} if kind == "die" else \
             {"abs_stop_c": 72, "board_cap_w": 30, "cap_consecutive": 3}
        sf["note"] = (f"E161's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; "
                      "the session must end with exit 4")
        out = header(e, f"STOPTEST-{kind.upper()}", sf, note=f"E161's {kind} stop-path test: E144b's, the smoke's int8 -1s tile, E161's chain")
        out["from"] = {"protocol": f"tools/claims-v3/e144b/protocol-stoptest-{kind}.json", "blocks": "unchanged"}
        out["blocks"] = copy.deepcopy(e["blocks"])
        dump(out, f"protocol-stoptest-{kind}.json")
        dump(dry(out), f"protocol-stoptest-{kind}-dry.json")
    # G1Q: E144b G1's blocks (E98's REST, 120 s, then the hold behind E98's 57 C gate), the hold's tile and length Q139(e)'s
    e = load("protocol-g1.json")
    g1 = header(e, "G1Q")
    g1["blocks"] = copy.deepcopy(e["blocks"])
    assert [b["name"] for b in g1["blocks"]] == ["REST", "HOLD"]
    h = g1["blocks"][1]
    assert h["runs"][0]["label"] == "int8-neg_ones-hold" and h["launch"]["processes"] == 107 and h["start"]["max_c"] == 57
    h["runs"] = [dict(HOLD_RUN["G1Q"])]
    h["launch"]["processes"] = N_HOLD["G1Q"]
    h["title"] = ("E161 G1Q (Q139(e)'s frozen hold): int8.b_line_zero_ff from rest, 93 back-to-back 8 s processes (~13.0 min) behind E98's "
                  "57 C gate, every launch's C logged; the steady reading is the last 300 s")
    g1["from"]["blocks"] = "G1's REST and HOLD, unchanged but for the hold's tile (Q139(e)'s G1q), its 93 processes (was 107) and its title"
    dump(g1, "protocol-g1q.json")
    dump(dry(g1), "protocol-g1q-dry.json")
    # G2Q: E144b G2's blocks (E98's REST, 120 s, then the hold from at once under the card's own governor)
    e = load("protocol-g2.json")
    g2 = header(e, "G2Q")
    g2["blocks"] = copy.deepcopy(e["blocks"])
    assert [b["name"] for b in g2["blocks"]] == ["REST", "HOLDF"]
    h = g2["blocks"][1]
    assert h["runs"][0]["label"] == "fp32-randn-hold" and h["launch"]["processes"] == 106 and h["start"]["max_c"] == 99
    h["name"] = "HOLD"
    h["runs"] = [dict(HOLD_RUN["G2Q"])]
    h["launch"]["processes"] = N_HOLD["G2Q"]
    h["title"] = ("E161 G2Q (Q139(e)'s frozen hold): fp32.real_smol_softmax_v_causal, 91 back-to-back 8 s processes (~13.0 min) from at once "
                  "after the REST, under the card's own governor, every launch's C logged; the steady reading is the last 300 s")
    g2["from"]["blocks"] = ("G2's REST and HOLDF, unchanged but for HOLDF's name (HOLD), its tile (Q139(e)'s G2q), its 91 processes "
                            "(was 106) and its title")
    dump(g2, "protocol-g2q.json")
    dump(dry(g2), "protocol-g2q-dry.json")


if __name__ == "__main__":
    main()
