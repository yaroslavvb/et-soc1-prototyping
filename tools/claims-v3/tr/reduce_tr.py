#!/usr/bin/env python3
"""E76 (V3-TR) probe reduction: the count P1 registered, plus P2, P3 and P4.

    python3 tools/claims-v3/tr/reduce_tr.py <pass dir> [<pass dir> ...] --gen <make_tr.py dir>
        --pred tools/claims-v3/tr/predictions.json --out tr.json [--csv runs.csv]

Written on the day of the run (departure D-T1, 28 Oct 2026): the registration named the rules and left the
reducer to the running agent. The probe needs no power at all — predictions.json says so itself ("the board meter
is 3-4 orders of magnitude short") — so this reads `runs.jsonl` and `marks.jsonl` only:

  P1  per item, the modal `ok` over passes; a non-unanimous item is reported unstable with its per-pass values.
      A trapping mode must record ok:false with zero ops; every control must record ok:true with 64 ops.
  P2  the catalogue's own hand-written `trx_fdiv_ps` / `trx_fsqrt_ps` must behave as their `tr.` counterparts.
  P3  the trap's wall-clock excess: the median difference between a trapping item's `wall_s` and the controls'
      median `wall_s` in the same block, in milliseconds. The host clock, not the board meter.
  P4  no lasting harm: every control that ran AFTER a trapping launch in the same block still records ok:true,
      and every pass ends "ok".
"""
import argparse
import csv
import json
import os
import statistics

TRAP_MODES = ["tr_fdiv_s", "tr_fsqrt_s", "tr_fdiv_ps", "tr_fsqrt_ps", "tr_frsq_ps", "tr_fsin_ps",
              "tr_fdiv_pi", "tr_fdivu_pi", "tr_frem_pi", "tr_fremu_pi", "tr_fcvt_l_s", "tr_fcvt_s_l",
              "tr_csrr_cycle"]


def jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path):
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    a = ap.parse_args()

    pred = json.load(open(a.pred))
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}

    rows, blocks, card = [], {}, None
    for d in a.dirs:
        cfg = json.load(open(os.path.join(d, "configs.json")))
        card = card or cfg.get("card")
        blk = json.load(open(os.path.join(d, "block.json"))) if os.path.exists(os.path.join(d, "block.json")) else {}
        blocks[os.path.basename(d)] = blk.get("status")
        marks = {(m["block"], m["item"], m.get("pos", 0), m.get("attempt", 1)): m
                 for m in jsonl(os.path.join(d, "marks.jsonl")) if m.get("kind") == "run"}
        seen = {}
        for r in jsonl(os.path.join(d, "runs.jsonl")):
            key = (r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))
            m = marks.get(key, {})
            it = man.get(r["item"], {})
            rows.append({"dir": os.path.basename(d), "pass": r["block"], "pos": r.get("pos", 0),
                         "item": r["item"], "kind": r.get("kind"), "attempt": r.get("attempt", 1),
                         "pattern": r.get("pattern") or it.get("args", [None, None])[1:2],
                         "designed_trap": it.get("expected_to_trap"), "ok": r.get("ok"),
                         "ops": r.get("ops", r.get("iters")), "wall_s": r.get("wall_s"),
                         "rc": m.get("rc"), "launches": m.get("launches"), "start_c": r.get("start_c")})
            seen[r["item"]] = True
        # items launched but recording no line at all (the host printed nothing taggable)
        for key, m in marks.items():
            if m["item"] not in seen and m["item"] in man:
                it = man[m["item"]]
                rows.append({"dir": os.path.basename(d), "pass": key[0], "pos": m.get("pos", 0),
                             "item": m["item"], "kind": it.get("kind"), "attempt": m.get("attempt", 1),
                             "pattern": None, "designed_trap": it.get("expected_to_trap"), "ok": None, "ops": None,
                             "wall_s": None, "rc": m.get("rc"), "launches": m.get("launches"),
                             "start_c": m.get("start_c")})

    items = sorted({r["item"] for r in rows})
    per_item = {}
    for name in items:
        rr = [r for r in rows if r["item"] == name]
        oks = [r["ok"] for r in rr]
        modal = max(set(oks), key=oks.count) if oks else None
        per_item[name] = {
            "designed_trap": man.get(name, {}).get("expected_to_trap"),
            "n_runs": len(rr), "ok_values": oks, "modal_ok": modal,
            "unanimous": len(set(oks)) <= 1,
            "ops": [r["ops"] for r in rr],
            "wall_s_median": statistics.median([r["wall_s"] for r in rr if r["wall_s"] is not None])
            if any(r["wall_s"] is not None for r in rr) else None,
            "rc": sorted({r["rc"] for r in rr}),
            "launches": sorted({r["launches"] for r in rr}),
        }

    # ---- P1 ---------------------------------------------------------------------------------------------------
    traps = ["trp_" + m for m in TRAP_MODES]
    controls = [n for n in items if n.startswith("trp_tr_ctl_")]
    trx = [n for n in items if n.startswith("trx_")]
    trap_ok = {n: per_item[n]["modal_ok"] for n in traps if n in per_item}
    ctl_ok = {n: per_item[n]["modal_ok"] for n in controls}
    trap_ops = {n: per_item[n]["ops"] for n in traps if n in per_item}
    ctl_ops = {n: per_item[n]["ops"] for n in controls}
    p1 = {"registered": pred["predictions"]["P1_all_thirteen_trap"],
          "trapping_items_found": len(trap_ok), "controls_found": len(ctl_ok),
          "trapping_that_trapped": sorted(n for n, v in trap_ok.items() if v is not True),
          "trapping_that_did_NOT_trap": sorted(n for n, v in trap_ok.items() if v is True),
          "controls_ok": sorted(n for n, v in ctl_ok.items() if v is True),
          "controls_not_ok": sorted(n for n, v in ctl_ok.items() if v is not True),
          "unstable": sorted(n for n in items if not per_item[n]["unanimous"]),
          "trap_ops_all_zero": all(all((o in (0, None)) for o in v) for v in trap_ops.values()),
          "control_ops": {n: sorted(set(v)) for n, v in ctl_ops.items()}}
    p1["pass"] = bool(len(trap_ok) == 13 and not p1["trapping_that_did_NOT_trap"]
                      and not p1["controls_not_ok"] and p1["trap_ops_all_zero"] and not p1["unstable"])

    # ---- P2 ---------------------------------------------------------------------------------------------------
    pairs = {"trx_fdiv_ps": "trp_tr_fdiv_ps", "trx_fsqrt_ps": "trp_tr_fsqrt_ps"}
    p2 = {"pairs": {}, "pass": True}
    for x, y in pairs.items():
        if x in per_item and y in per_item:
            same = per_item[x]["modal_ok"] == per_item[y]["modal_ok"]
            p2["pairs"][x] = {"trx_modal_ok": per_item[x]["modal_ok"], "tr_modal_ok": per_item[y]["modal_ok"],
                              "agree": same}
            p2["pass"] = p2["pass"] and same
        else:
            p2["pairs"][x] = {"missing": True}
            p2["pass"] = False

    # ---- P3: the trap's wall-clock excess over the controls in the same block -------------------------------
    excess = []
    for (dirn, blk) in {(r["dir"], r["pass"]) for r in rows}:
        ctl = [r["wall_s"] for r in rows if r["dir"] == dirn and r["pass"] == blk
               and r["item"] in controls and r["wall_s"] is not None]
        if not ctl:
            continue
        base = statistics.median(ctl)
        for r in rows:
            if r["dir"] == dirn and r["pass"] == blk and r["item"] in traps and r["wall_s"] is not None:
                excess.append({"pass": blk, "item": r["item"], "excess_ms": 1000.0 * (r["wall_s"] - base)})
    vals = [e["excess_ms"] for e in excess]
    p3 = {"registered_ms": pred["predictions"]["P3_wall_s_excess_ms"],
          "median_ms": statistics.median(vals) if vals else None,
          "min_ms": min(vals) if vals else None, "max_ms": max(vals) if vals else None,
          "n": len(vals), "per_item": excess}
    p3["pass"] = (None if p3["median_ms"] is None else
                  bool(pred["predictions"]["P3_wall_s_excess_ms"][0] <= p3["median_ms"]
                       <= pred["predictions"]["P3_wall_s_excess_ms"][1]))

    # ---- P4: nothing lasting ---------------------------------------------------------------------------------
    after = []
    for (dirn, blk) in sorted({(r["dir"], r["pass"]) for r in rows}):
        tr_pos = [r["pos"] for r in rows if r["dir"] == dirn and r["pass"] == blk and r["item"] in traps]
        first = min(tr_pos) if tr_pos else None
        if first is None:
            continue
        for r in rows:
            if (r["dir"] == dirn and r["pass"] == blk and r["pos"] > first
                    and (r["item"] in controls or r["kind"] == "fma")):
                after.append({"pass": blk, "pos": r["pos"], "item": r["item"], "ok": r["ok"],
                              "ops": r["ops"]})
    p4 = {"runs_after_a_trap": len(after), "any_not_ok": [x for x in after if x["ok"] is not True],
          "pass_status": blocks, "pass": bool(after and not [x for x in after if x["ok"] is not True]
                                              and all(v == "ok" for v in blocks.values()))}

    res = {"exp": "E76", "stage": "probe", "card": card, "dirs": a.dirs, "block_status": blocks,
           "structural_finding": pred["structural_finding"],
           "counted_registration": pred["counted_27_oct_2026_aifoundry1"],
           "per_item": per_item,
           "scored": {"P1_all_thirteen_trap": p1, "P2_build_independence": p2, "P3_wall_s_excess_ms": p3,
                      "P4_no_lasting_harm": p4,
                      "P5_no_energy_figure": {"registered": pred["predictions"]["P5_no_energy_figure"],
                                              "measured": None,
                                              "note": "not measurable with the board meter and not attempted: "
                                                      "the probe's deliverable is the count, not an energy"},
                      "P6_substitute_price": {"registered": pred["predictions"]["P6_substitute_price"],
                                              "note": "static, from the firmware and library ELFs; no card "
                                                      "stage in this run"}}}
    json.dump(res, open(a.out, "w"), indent=1, default=float)

    if a.csv:
        cols = ["dir", "pass", "pos", "item", "designed_trap", "ok", "ops", "wall_s", "rc", "launches", "start_c"]
        with open(a.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for r in sorted(rows, key=lambda r: (r["dir"], r["pos"])):
                w.writerow([r.get(c) for c in cols])

    print("E76 %s probe: %d runs over %s, block status %s" % (card, len(rows), a.dirs, blocks))
    print("  P1 %s: %d/13 trapping modes ended the kernel, %d/%d controls ok, ops zero on every trap: %s" %
          (p1["pass"], len(p1["trapping_that_trapped"]), len(p1["controls_ok"]), len(ctl_ok),
           p1["trap_ops_all_zero"]))
    if p1["trapping_that_did_NOT_trap"]:
        print("     DID NOT TRAP: %s" % p1["trapping_that_did_NOT_trap"])
    print("  P2 %s  P3 median %s ms [%s, %s] %s  P4 %s (%d runs after a trap, %d not ok)" %
          (p2["pass"], "%.2f" % p3["median_ms"] if p3["median_ms"] is not None else "-",
           "%.2f" % p3["min_ms"] if p3["min_ms"] is not None else "-",
           "%.2f" % p3["max_ms"] if p3["max_ms"] is not None else "-", p3["pass"],
           p4["pass"], p4["runs_after_a_trap"], len(p4["any_not_ok"])))


if __name__ == "__main__":
    main()
