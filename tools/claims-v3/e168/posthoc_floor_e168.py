#!/usr/bin/env python3
"""E168 (Q141(o), fix pass): a desk check of amendment A2's power at a rest floor above 46 C. Written after A2's registration
(226249e1) and the kit (a0310012), before any E168 data or claim. It is not registered: it changes no hold, gate, rule,
prediction or reading, and no frozen file. It answers one question for the records: if aifoundry2's rest floor is 47 C on the day
(E161's measured floor, Tue 3 Nov 2026), can A2's reading still separate G4's start-referenced law from a law in the absolute die?

What it runs, with no device and nothing written but its own stdout: Q140(q)'s frozen predict_e168.run_model (e39d06da), unchanged,
for the int8 zeros hold at S2 from both nominal starts, exactly as the frozen file's both_nominal_starts (the same predecessor, S2
fp32 random from cold, the same 12 x 8 s schedule), with the chain's rest anchor T_COLD set to each floor in turn. At 46.0 C it must
reproduce predictions-e168.json's both_nominal_starts byte for byte (G4 and G3 as frozen), else it exits 1.

For each floor it gives:
  - G4's mechanical difference dW_G4 = cold - warm55 window board, and A2's band h = dW_G4 / 2 (A2 section 3);
  - G3 as frozen, the same difference;
  - a law in the absolute die, two ways:
      (a) linear: k_D x (cold - warm55 window die, G4's), k_D on Q140(q)'s grid {0.44, 0.47, 0.50} W/C (the estimate the lane and
          its verifier used);
      (b) the registration's own candidate T_D run through the same frozen run_model: every level P0(f) + beta.delta + k_D (T(t) -
          T_ref), T_ref 54.3818 C (REGISTRATION.md section A2), G4's trip, zeros level and dip kept (G4's arm with T_D in place of
          G3's start-referenced k_eff), so the die and the board feed back on each other;
  - the reading A2 would give each law: SUPPORTED if dW >= +h, NO START DEPENDENCE if |dW| < h, OPPOSITE SIGN if dW <= -h, no
    reading if dW_G4 <= 0.2 W; E136's law is 0 by construction (NO START DEPENDENCE).

    /usr/bin/python3 -B tools/claims-v3/e168/posthoc_floor_e168.py > tools/claims-v3/e168/logs/posthoc-floor.txt
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
G4DIR = os.path.join(ROOT, "docs", "reports", "data", "2026-11-04-q140q-gemm-g4-stride")
sys.path.insert(0, G4DIR)
import predict_e168 as PE  # noqa: E402  (frozen at e39d06da; importing it runs no main and writes nothing)

FLOORS = (46.0, 46.5, 47.0, 47.5, 48.0)
K_D = (0.44, 0.47, 0.50)
T_REF_TD = 54.3818          # REGISTRATION.md section A2, T_D's reference (M9's mean burst start)
NO_READING_W = 0.2


def reading(dw, h, dw_g4):
    if dw_g4 <= NO_READING_W:
        return "no reading"
    if dw >= h:
        return "SUPPORTED"
    if dw <= -h:
        return "OPPOSITE SIGN"
    return "NO START DEPENDENCE"


def main():
    frozen = json.load(open(os.path.join(G4DIR, "predictions-e168.json")))["cells"]["S2-int8-zeros-warm55"]["both_nominal_starts"]
    PH = PE.phis()
    for s, b in PE.SHAPES.items():
        PE.G4.add_shape146(s, *b)            # as predict_e168.main does before any run_model
    arm4 = PE.g4_arm()
    arm3 = {"k": PE.G.K_LEAK_G3, "trip": PE.G.TRIP_G3}
    lev = PE.levels("S2", "int8", "zeros", PH)
    prev = PE.levels("S2", "fp32", "randn", PH)      # the frozen file's predecessor for every hold's warm start
    t_cold_frozen = PE.T_COLD
    print("E168 A2, a desk check at rest floors above 46 C (post hoc to A2's registration, before any E168 data; not registered)")
    print(f"frozen predictor: {os.path.relpath(PE.__file__, ROOT)}; T_COLD as frozen {t_cold_frozen:.1f} C, T_WARM {PE.T_WARM:.1f} C")
    print(f"hold: S2 int8 zeros, {PE.N_PROC} x {PE.SECONDS:g} s; warm55's predecessor S2 fp32 random from cold (both_nominal_starts' own)")
    print()
    rows = []
    ok46 = None
    for tc in FLOORS:
        PE.T_COLD = tc
        g4c, g4w = PE.run_model(lev, "int8", arm4, "cold", prev), PE.run_model(lev, "int8", arm4, "warm55", prev)
        g3c, g3w = PE.run_model(lev, "int8", arm3, "cold", prev), PE.run_model(lev, "int8", arm3, "warm55", prev)
        if tc == t_cold_frozen:
            ok46 = (g4c == frozen["cold"]["G4"] and g4w == frozen["warm55"]["G4"]
                    and g3c == frozen["cold"]["G3_as_frozen"] and g3w == frozen["warm55"]["G3_as_frozen"])
        dw4 = g4c["w"] - g4w["w"]
        h = dw4 / 2.0
        dd4 = g4c["die"] - g4w["die"]
        td = {}
        for kd in K_D:
            arm_td = dict(arm4, k=kd, T_ref=T_REF_TD)
            c, w = PE.run_model(lev, "int8", arm_td, "cold", prev), PE.run_model(lev, "int8", arm_td, "warm55", prev)
            td[kd] = {"lin": kd * dd4, "sim": c["w"] - w["w"], "sim_die": c["die"] - w["die"]}
        rows.append((tc, g4c, g4w, g3c, g3w, dw4, h, dd4, td))
    PE.T_COLD = t_cold_frozen
    print(f"self-check at {t_cold_frozen:.1f} C: G4 and G3 as frozen equal predictions-e168.json's both_nominal_starts exactly: "
          f"{'PASS' if ok46 else 'FAIL'}")
    print()
    print("floor  G4 cold W / die (start)        G4 warm55 W / die (start)      dW_G4   h      die gap  G3 dW   E136")
    for tc, g4c, g4w, g3c, g3w, dw4, h, dd4, td in rows:
        print(f"{tc:5.1f}  {g4c['w']:7.3f} / {g4c['die']:7.3f} ({g4c['die_start']:5.2f})   {g4w['w']:7.3f} / {g4w['die']:7.3f} ({g4w['die_start']:5.2f})"
              f"   {dw4:+.3f}  {h:.3f}  {dd4:+.3f}  {g3c['w'] - g3w['w']:+.3f}  0 ({reading(0.0, h, dw4)})")
    print()
    print("a law in the absolute die, cold - warm55 window board, and the reading A2 gives it")
    print("floor  k_D   (a) linear k_D x G4's die gap      (b) T_D run through run_model (its own die gap)")
    for tc, g4c, g4w, g3c, g3w, dw4, h, dd4, td in rows:
        for kd in K_D:
            t = td[kd]
            print(f"{tc:5.1f}  {kd:.2f}  {t['lin']:+.3f} W  {reading(t['lin'], h, dw4):<20}  {t['sim']:+.3f} W  {reading(t['sim'], h, dw4):<20}"
                  f" ({t['sim_die']:+.3f} C)")
    print()
    cases = [(tc, kd, way, t[way], h, dw4) for tc, _, _, _, _, dw4, h, _, td_ in rows for kd, t in td_.items() for way in ("lin", "sim")]
    opp = [c for c in cases if reading(c[3], c[4], c[5]) == "OPPOSITE SIGN"]
    margin = min(-c[4] - c[3] for c in cases)          # how far the law's dW lies past -h, at the closest case
    print(f"the absolute-die law reads OPPOSITE SIGN in {len(opp)} of {len(cases)} cases (floors {FLOORS[0]:g}-{FLOORS[-1]:g} C x k_D x both ways);"
          f" its closest case lies {margin:+.3f} W past -h")
    print("G4's own reading is SUPPORTED by construction (dW = dW_G4 >= h); E136's law reads NO START DEPENDENCE (0).")
    return 0 if ok46 else 1


if __name__ == "__main__":
    sys.exit(main())
