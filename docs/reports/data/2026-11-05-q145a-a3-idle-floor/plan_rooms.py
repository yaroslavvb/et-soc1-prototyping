#!/usr/bin/env python3
"""heat-q145a: M11's committed exact planner (tools/claims-v3/m11/design_power_heat_v2.plan_exact) at rooms 51.2-55.0 C (post hoc; the
plan only, no data). It prints each hold's planned plateau and in-launch peak (34-sensor mean) and the warmest room whose planned maxima stay
at or under the registered envelope (the highest at any admitted room, H_E's cool pattern at 51.5 C).

    python3 -B plan_rooms.py <lab repo top> <out.json>
"""
import json
import os
import sys

sys.dont_write_bytecode = True
TOP, OUT = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], TOP]      # the planner reads its top directory from argv[1] at import (design_power_heat_v2.py line 43)
sys.path.insert(0, os.path.join(TOP, "tools/claims-v3/m11"))
import design_power_heat_v2 as V  # noqa: E402

ROOMS = (51.2, 51.5, 52.0, 52.6, 53.0, 53.2, 53.4, 53.6, 53.8, 53.9, 54.0, 54.3, 54.5, 55.0)
out = {"rooms": {}}
for room in ROOMS:
    ex = V.plan_exact(room)
    hs = ex["holds"]
    out["rooms"][str(room)] = {"pattern": "cool" if room <= 51.5 else "warm", "plan_minutes": ex["plan_minutes"],
                               "H_E_peak_C": hs[0]["peak_C_abs"], "H_E_plateau_C": hs[0]["plateau_C_abs"], "H_E_P_C": hs[0]["P_C"],
                               "other_holds_peak_max_C": max(h["peak_C_abs"] for h in hs[1:]),
                               "holds": [{k: h[k] for k in ("hold", "item", "share", "P_C", "plateau_C_abs", "peak_C_abs", "carried_in_C")} for h in hs]}
admitted = [r for r in ROOMS if r <= 53.0]
env_peak = max(out["rooms"][str(r)]["H_E_peak_C"] for r in admitted)
env_plat = max(out["rooms"][str(r)]["H_E_plateau_C"] for r in admitted)
out["registered_envelope"] = {"peak_C": env_peak, "plateau_C": env_plat, "rooms_admitted_by_G0": admitted}
warm = [r for r in ROOMS if r > 51.5]
ok = [r for r in warm if out["rooms"][str(r)]["H_E_peak_C"] <= env_peak and out["rooms"][str(r)]["H_E_plateau_C"] <= env_plat]
# the crossing by linear interpolation between the last room inside and the first outside
last_in = max(ok)
first_out = min(r for r in warm if r > last_in)
a, b = out["rooms"][str(last_in)]["H_E_peak_C"], out["rooms"][str(first_out)]["H_E_peak_C"]
out["warmest_room_inside_envelope"] = {"grid": last_in, "interpolated_C": last_in + (env_peak - a) / (b - a) * (first_out - last_in),
                                       "binding": "H_E's in-launch peak"}
json.dump(out, open(OUT, "w"), indent=1)
for r in ROOMS:
    x = out["rooms"][str(r)]
    print(r, x["pattern"], "H_E peak", x["H_E_peak_C"], "plateau", x["H_E_plateau_C"], "P", x["H_E_P_C"], "others max", x["other_holds_peak_max_C"])
print("envelope", out["registered_envelope"], "warmest inside", out["warmest_room_inside_envelope"])
