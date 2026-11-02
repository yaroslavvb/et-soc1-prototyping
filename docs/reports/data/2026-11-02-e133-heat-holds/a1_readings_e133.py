#!/usr/bin/env python3
"""E133: amendment A1's reading and the side-by-side with E111, from the registered scorer's own output (results.json); desk only.

  * E133-R2w (amendment A1, committed f842cc39 at 10:12:24 PST, before W2 started at 10:35:14): AT THE TRIP if W2's REST idle die is under
    44.54 C (66 - (21.763 - 0.3): the governor enters its thermal state when the whole-degree die reads above 65), else AT THE FLOOR; scored
    against the registered R2's observed verdict (R2.verdict, from H-F32's plateau share at 600 MHz). The registered R2 stays E133-R2's verdict.
  * The two sessions per kind side by side (E111's committed results.json against E133's): idles, plateaus, c and its range, A1's slopes.

    python3 a1_readings_e133.py <E133 results.json> <E111 results.json>
"""
import json
import sys

KEY_R2W = 44.54
e133 = json.load(open(sys.argv[1]))
e111 = json.load(open(sys.argv[2]))
r2 = e133["R2"]
out = {"R2_registered": {k: r2.get(k) for k in ("w2_rest_idle_die", "share_at_600", "predicted", "verdict", "as_predicted")}}
if r2.get("verdict") in ("AT THE TRIP", "AT THE FLOOR"):
    pred = "AT THE TRIP" if r2["w2_rest_idle_die"] < KEY_R2W else "AT THE FLOOR"
    out["R2w_amendment_A1"] = {"key_c": KEY_R2W, "predicted": pred, "verdict": r2["verdict"], "as_predicted": pred == r2["verdict"],
                               "keys_disagree": pred != r2.get("predicted")}
rows = {}
for h in ("H-I8", "H-F32"):
    for tag, res in (("E111", e111), ("E133", e133)):
        x = (res.get("A") or {}).get(h) or {}
        p, a1, a2 = x.get("plateau") or {}, x.get("A1") or {}, x.get("A2") or {}
        rows[f"{h} {tag}"] = {"clock_mhz": x.get("clock_mhz"), "processes": f"{x.get('processes_run')}/{x.get('processes_planned')}",
                              "minutes": x.get("minutes"), "plateau_die": p.get("die"), "plateau_w": p.get("w"), "share_clock": p.get("share_clock"),
                              "rise_c": a2.get("rise_c"), "dW_w": a2.get("dW_w"), "c": a2.get("c"), "c_lo": a2.get("c_lo"), "c_hi": a2.get("c_hi"),
                              "A1": a1.get("verdict"), "A1_read_on": a1.get("read_on"), "fine_slope_c_per_min": a1.get("fine_slope_c_per_min"),
                              "fine_slope_se": a1.get("fine_slope_se"), "die_slope_c_per_min": a1.get("die_slope_c_per_min"), "die_slope_se": a1.get("die_slope_se")}
out["holds"] = rows
out["idles"] = {"E111": (e111.get("A") or {}).get("idles"), "E133": (e133.get("A") or {}).get("idles")}
for k in ("idles",):
    for tag in ("E111", "E133"):
        out[k][tag] = {s: ({"die": v.get("die"), "w": v.get("w")} if v else None) for s, v in (out[k][tag] or {}).items()}
print(json.dumps(out, indent=1))
