#!/usr/bin/env python3
"""heat-q145a, Part 2: aifoundry3's idle floor, split into a room part and the card's own part, and the start gates on its history
(post hoc, descriptive; reads floors.json, written by floor_scan.py from committed files, and committed files).

  floor        the session's first sample (34-sensor mean by E97's code_to_c where the sampler carried the raw codes; else the firmware's
               whole degree, with the mean offset of the raw-code sessions added and labelled "est");
  the split    a die at rest sits at T = T_room + R x P_idle(T), R = Q138(t)'s 0.8695 C per board W (model-q138t.json a3). With the
               measured first-sample board power: the room part T_room,eff = T - R x P (relative values are what matter), the card's own
               part R x P_idle (the board's idle draw, of which the temperature-dependent part is leakage, E97's law); a change of room
               dT_room moves the floor by dT_room / (1 - g), g = R x k(T) (the loop gain), so the card's own share of a floor change is g;
  the tail     the card's own part left from the previous run: M6's slowest pole (1,500 s, weight 0.010 of a plateau) after the rest,
               bounded with a 25 C plateau;
  the gates    G0 as registered (R0's room <= 53.0 C) and the dated amendment's (FL-G0: R0's room <= 53.9 C, R0's room - F0 <= 0.5 C), with
               R0's room modelled as the floor + the largest committed smoke residue (0.43 C) where no R0 ran.

    python3 -B floor_analysis.py <floors.json> <lab repo top> <out.json>
"""
import gzip
import json
import math
import os
import sys

import numpy as np

R = 0.8695
A97, B97, C97 = 0.006175439291277969, -0.3665903970069978, 25.998917638611008


def law(T):
    return A97 * T * T + B97 * T + C97


def k(T):
    return 2 * A97 * T + B97


def main():
    fl, top, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    S = json.load(open(fl))["sessions"]
    D = os.path.join(top, "docs/reports/data")
    raw = [s for s in S if s["floor_m34_c"] is not None]
    offs = [s["floor_m34_c"] - s["floor_fw_c"] for s in raw]
    off = float(np.mean(offs))
    rows = []
    for s in S:
        est = s["floor_m34_c"] is None
        T = s["floor_m34_c"] if not est else s["floor_fw_c"] + off
        P = s["floor_board_w"]
        rest = s["rest_h"]
        tail = None if rest is None else 0.010 * 25.0 * math.exp(-rest * 3600.0 / 1500.0)
        g = R * k(T)
        rows.append({"start_pst": s["start_pst"], "hour": round(s["hour_pst"], 2), "rest_h": None if rest is None else round(rest, 2),
                     "first_dir": s["first_dir"], "floor_c": round(T, 3), "floor_kind": "est (firmware + offset)" if est else "34-sensor mean",
                     "fw_c": s["floor_fw_c"], "board_w": P, "law_board_w_at_floor": round(law(T), 3),
                     "board_minus_law_w": round(P - law(T), 3), "room_eff_c": round(T - R * P, 3), "card_own_c": round(R * P, 3),
                     "loop_gain": round(g, 4), "slow_tail_bound_c": None if tail is None else round(tail, 4),
                     "settled": rest is not None and rest >= 1.0})
    # the split across the raw-code sessions (34-sensor floors, settled)
    rc = [r for r in rows if r["floor_kind"] == "34-sensor mean"]
    base = min(rc, key=lambda r: r["floor_c"])
    split = []
    for r in rc:
        dT = r["floor_c"] - base["floor_c"]
        droom = r["room_eff_c"] - base["room_eff_c"]
        split.append({"session": r["start_pst"], "dfloor_c": round(dT, 3), "room_part_c": round(droom, 3), "card_own_part_c": round(dT - droom, 3),
                      "card_own_share": None if abs(dT) < 1e-9 else round((dT - droom) / dT, 3),
                      "predicted_card_own_share_g": round(R * k((r["floor_c"] + base["floor_c"]) / 2.0), 3)})
    # E97's settled R0 (slope rule) and the room proxies
    e97 = json.load(open(os.path.join(D, "2026-11-01-e97-heat-low-power-steady/e97.json")))["holds"]["holds"]["H1"]["idle"]["before"]
    proxies = {"E97_R0": {"floor_c": e97["T"], "board_w": e97["P"], "room_eff_c": e97["T"] - R * e97["P"],
                          "host_nvme_c_R0": 36.71, "host_cpu_c_R0": 32.36, "source": "e97.json holds.H1.idle.before; room.txt R0 (aifoundry3)"},
               "E176": {"floor_c": 53.20226332720588, "board_w": 23.97, "room_eff_c": 53.20226332720588 - R * 23.97,
                        "host_nvme_c": 38.85, "host_acpitz1_c": 27.8, "source": "the smoke's first sample; room-rule/hostwin-base.out (17:31:50)"}}
    d_floor = proxies["E176"]["floor_c"] - proxies["E97_R0"]["floor_c"]
    d_nvme = 38.85 - 36.71
    proxies["ratio_dfloor_over_dnvme"] = d_floor / d_nvme
    proxies["predicted_1_over_1_minus_g"] = 1.0 / (1.0 - R * k((proxies["E176"]["floor_c"] + proxies["E97_R0"]["floor_c"]) / 2))
    # the cool-hour pattern (settled floors, rest >= 1 h, November)
    nov = [r for r in rows if r["settled"] and (" Nov " in r["start_pst"])]
    hours = {"before 12:00": [r for r in nov if r["hour"] < 12.0], "12:00-17:00": [r for r in nov if 12.0 <= r["hour"] < 17.0],
             "17:00 and after": [r for r in nov if r["hour"] >= 17.0]}
    pattern = {k_: {"n": len(v), "floor_min_c": min(r["floor_c"] for r in v) if v else None, "floor_max_c": max(r["floor_c"] for r in v) if v else None,
                    "fw_max": max(r["fw_c"] for r in v) if v else None, "sessions": [(r["start_pst"], r["floor_c"], r["floor_kind"][:3]) for r in v]}
               for k_, v in hours.items()}
    # the gates on the history
    resid = {"E154": 51.409838125191484 - 50.98161764705882, "E166": 51.924207119810816 - 51.8376407398897, "E176": 53.58212805175781 - 53.20226332720588}
    rmax = max(resid.values())
    gates = []
    for r in rows:
        if not r["settled"]:
            continue
        room = r["floor_c"] + rmax
        gates.append({"session": r["start_pst"], "floor_c": r["floor_c"], "kind": r["floor_kind"][:3], "R0_room_model_c": round(room, 3),
                      "G0_registered": "PASS" if room <= 53.0 else "REFUSE", "FL_G0": "PASS" if room <= 53.9 else "REFUSE",
                      "pattern": "cool" if room <= 51.5 else "warm"})
    res = {"offset_m34_minus_fw": {"mean": off, "values": offs}, "rows": rows, "split_raw_code_sessions": split, "base": base["start_pst"],
           "room_proxies": proxies, "cool_hours_november": pattern, "smoke_residues_c": resid, "gates_on_history": gates,
           "gate_counts": {"settled_sessions": len(gates), "G0_registered_pass": sum(g["G0_registered"] == "PASS" for g in gates),
                           "FL_G0_pass": sum(g["FL_G0"] == "PASS" for g in gates),
                           "november_G0_registered_pass": sum(g["G0_registered"] == "PASS" for g in gates if " Nov " in g["session"]),
                           "november_FL_G0_pass": sum(g["FL_G0"] == "PASS" for g in gates if " Nov " in g["session"]),
                           "november_settled": sum(1 for g in gates if " Nov " in g["session"])}}
    json.dump(res, open(outp, "w"), indent=1)
    print("offset m34 - fw:", round(off, 3), [round(x, 3) for x in offs])
    for r in rows:
        print(f"{r['start_pst']} h{r['hour']:5.2f} rest {r['rest_h']} floor {r['floor_c']:.3f} ({r['floor_kind'][:3]}) P {r['board_w']:.2f} "
              f"law {r['law_board_w_at_floor']:.2f} room_eff {r['room_eff_c']:.2f} g {r['loop_gain']:.3f} tail<= {r['slow_tail_bound_c']}")
    print("split vs", base["start_pst"])
    for x in split:
        print("  ", x)
    print("proxies", {k_: (v if not isinstance(v, dict) else {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()}) for k_, v in proxies.items()})
    print("cool hours", json.dumps(pattern)[:1500])
    print("residues", {k_: round(v, 3) for k_, v in resid.items()})
    print("gates", res["gate_counts"])
    for gg in gates:
        if " Nov " in gg["session"] or " Oct " in gg["session"]:
            print("  ", gg)


if __name__ == "__main__":
    main()
