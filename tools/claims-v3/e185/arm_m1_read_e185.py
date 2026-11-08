#!/usr/bin/env python3
"""E185's dated note M1 (E185.md.dated-note-M1.md, section M1-4): the reader of october-forecast-model's two REPORTED arms, v3 and v4, on
E185's committed score. Written before any E185 datum. Python's standard modules only; opens no device, no box and no network.

    /usr/bin/python3 -B tools/claims-v3/e185/arm_m1_read_e185.py --data <E185's data directory> --out <prefix> [--m1 <json>]
                                                                                       # run from the lab repository's top
It writes <prefix>.json and <prefix>.txt and prints the text.

THE MEASURED SIDE is E185's own, as step 22's scorer committed it (<data>/scored-m11.json, written by score_e185.sh with M11's scorer v5):
  - the session's room, its start gate's room_c (R0's room, its last 120 s), and the H_E pattern its measured pass ran, the room mark's
    he_seconds in <data>/aifoundry3/e185/<pass>/marks.jsonl (3.2 s: the cool pattern; 2.6 s: the warm); without that mark, A6-3's rule on
    the room (cool at or under 51.5 C), said so;
  - each hold's rise R, the scorer's R_C, for every hold the scorer reads scored (E185 section > holds > <name> > scored);
  - each big hold's cool-down window rise, recovered from the scorer's two cool-down misses and the frozen board gain G_B: the scorer
    writes e_F = R_c - P_F,c and e_B = R_c - G_B P_F,c (4 decimals), so P_F,c = (e_F - e_B) / (G_B - 1) and R_c = e_F + P_F,c, to about
    +-0.004 C at 4 decimals. The same recovery is checked on each hold's plateau against the scorer's own R_C first; a hold whose plateau
    check misses by more than 0.01 C has its cool-down not read. G_B must equal the score's frozen gain and arms-e185-train.json's.
  - the measured interval: R +- 1.96 sigma_c, sigma_c = 0.0884 C (M11's REGISTRATION.md section 4, the per-hold noise E185.md section 6
    reads its tau from), for a rise and for a cool-down window alike.
THE MODEL'S SIDE is the committed json's, refused unless its sha256 is the one pinned below (exit 2): for each arm (v3, v4) each hold's rise
and each big hold's cool-down with their 1 sd at the seven plan rooms, read at the session's room by the note's rule: among the plan rooms
of the pattern the session ran (cool 49.4, 50.3, 50.8, 51.5 C; warm 52.5, 53.0, 53.9 C), linear in the room between the two that bracket it,
or from the two nearest at that end (extrapolated, and said so) when the room lies outside them; the central and the 1 sd alike.
THE WORDS, never a verdict and never an E185 rule: the model's central lies inside, above or below the measured interval; the measured R lies
inside, above or below the model's own 95% band (central +- 1.96 sd), with z = (R - central) / sd; then each arm's rms and mean miss over
the rises it read and over the cool-downs, set beside E185-BEST's rms for F, B and Rl (measured watts, as the score gives them) and beside
the same three arms' planned forecasts at the same room (design-e185.json, by the same room rule: forecasts from the plan's watts, as the
model's are). The S and S2 cool-downs are not covered. A hold the scorer does not read scored is not read.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
M1_JSON = os.path.join(HERE, "m1-october-forecast-model-e185.json")
M1_JSON_SHA256 = "d09b7c80e46254b8c98f70cc0ab1deb3bf71cc70fa06110a4cfd64f60bbf2226"
TRAIN_JSON = os.path.join(HERE, "arms-e185-train.json")
DESIGN_JSON = os.path.join(HERE, "design-e185.json")
SIGMA_C = 0.0884                      # M11's REGISTRATION.md section 4 (score_m11_v5.SIGMA_C, design_e185.SIGMA_C)
Z95 = 1.96
PLATEAU_CHECK_C = 0.01
HOLDS = ("H_E", "L1", "L2", "H_E2", "S", "S2")
BIG = ("H_E", "L1", "L2", "H_E2")
ARMS = ("v3", "v4")


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def where(m, lo, hi):
    return "inside" if lo <= m <= hi else ("above" if m > hi else "below")


def rooms_of(pattern, plan_rooms):
    return sorted([r for r in plan_rooms if (float(r) <= 51.5) == (pattern == "cool")], key=float)


def at_room(values, rooms, room):
    """values: {room string: number}; linear in the room between the two plan rooms that bracket it, else from the two nearest at that end"""
    xs = [float(r) for r in rooms]
    for r, x in zip(rooms, xs):
        if abs(x - room) < 1e-9:
            return values[r], f"at the plan room {r} C"
    if room < xs[0]:
        i, j, how = 0, 1, f"extrapolated {xs[0] - room:.3f} C below the plan room {rooms[0]} C (from {rooms[0]} and {rooms[1]})"
    elif room > xs[-1]:
        i, j, how = len(xs) - 2, len(xs) - 1, f"extrapolated {room - xs[-1]:.3f} C above the plan room {rooms[-1]} C (from {rooms[-2]} and {rooms[-1]})"
    else:
        i = max(k for k in range(len(xs) - 1) if xs[k] <= room)
        j, how = i + 1, f"interpolated between the plan rooms {rooms[i]} and {rooms[i + 1]} C"
    w = (room - xs[i]) / (xs[j] - xs[i])
    return values[rooms[i]] + w * (values[rooms[j]] - values[rooms[i]]), how


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def pattern_of(data, sess, room):
    p = os.path.join(data, "aifoundry3", "e185", sess.get("pass_dir") or "p18520", "marks.jsonl")
    if os.path.exists(p):
        for ln in open(p):
            if '"room"' not in ln:
                continue
            m = json.loads(ln)
            if m.get("kind") == "room":
                hs = m.get("he_seconds")
                if hs is not None and abs(hs - 3.2) < 1e-9:
                    return "cool", f"the room mark's H_E pattern (3.2 s every {m.get('he_period_s')} s)"
                if hs is not None and abs(hs - 2.6) < 1e-9:
                    return "warm", f"the room mark's H_E pattern (2.6 s every {m.get('he_period_s')} s)"
                break
    pat = "cool" if room <= 51.5 else "warm"
    return pat, f"no H_E pattern in the measured pass's room mark: A6-3's rule on the room ({room:.3f} C {'<=' if pat == 'cool' else '>'} 51.5 C)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--m1", default=M1_JSON)
    a = ap.parse_args()
    got = sha256(a.m1)
    if got != M1_JSON_SHA256:
        print(f"REFUSED: {os.path.basename(a.m1)} sha256 {got[:16]} is not the committed note's {M1_JSON_SHA256[:16]}")
        sys.exit(2)
    m1 = json.load(open(a.m1))
    sc = json.load(open(os.path.join(a.data, "scored-m11.json")))
    out = {"_what": "october-forecast-model's two REPORTED arms (v3, v4) read on E185's committed score by E185.md.dated-note-M1.md section "
                    "M1-4; never a verdict, never an E185 rule", "freeze_lines": m1["freeze_lines"], "m1_json_sha256": got,
           "sigma_c_C": SIGMA_C, "interval": "R +- 1.96 sigma_c", "arms": {}}
    lines = ["october-forecast-model's reported arms for E185 (E185.md.dated-note-M1.md, M1-4): v3 and v4 against E185's measured holds",
             "  " + m1["freeze_lines"]["v3"], "  " + m1["freeze_lines"]["v4"],
             "  the model: C, forecasts from the plan's watts; E185: the 34-sensor die's rises as step 22's score gives them; REPORTED, never a rule"]
    E = sc.get("E185") or {}
    if E.get("reads") != "SCORED":
        out["read"] = f"not read: E185's score reads {E.get('reads')!r}"
        lines.append("  " + out["read"])
        json.dump(out, open(a.out + ".json", "w"), indent=1, sort_keys=True)
        open(a.out + ".txt", "w").write("\n".join(lines) + "\n")
        print("\n".join(lines))
        return
    sess = sc["sessions"][E["session"]]
    room = (sess.get("start_gate") or {}).get("room_c")
    if room is None:
        room = (sess.get("start_gate_reading") or {}).get("room_c")
    pat, pat_how = pattern_of(a.data, sess, room)
    gb_score = E["gains_frozen"]["G_B"]
    gb_train = json.load(open(TRAIN_JSON))["two_pass"]["gains"]["G_B"]
    if gb_score != gb_train:
        print(f"REFUSED: the score's frozen G_B {gb_score} is not arms-e185-train.json's {gb_train}")
        sys.exit(3)
    G1 = gb_score - 1.0
    out["session"] = {"id": E["session"], "room_C": room, "pattern": pat, "pattern_from": pat_how,
                      "reading": E.get("reading"), "blind_by_the_score": E.get("blind"), "G_B": gb_score}
    lines.append(f"  the session {E['session']}: room {room:.3f} C; the {pat} pattern ({pat_how}); the score's reading: {E.get('reading')}")
    # the measured side, hold by hold
    meas = {}
    for h in HOLDS:
        x = (E.get("holds") or {}).get(h)
        if x is None:
            meas[h] = {"read": "not read: no such hold in the score"}
            continue
        if not x.get("scored"):
            meas[h] = {"read": "not read: the score reads this hold not scored"}
            continue
        if any(x.get(k) is None for k in ("R_C", "e_F_C", "e_B_C")):
            meas[h] = {"read": "not read: the score gives no finite rise for this hold"}
            continue
        d = {"R_C": x["R_C"]}
        rec = x["e_F_C"] + (x["e_F_C"] - x["e_B_C"]) / G1
        d["plateau_recovery_C"] = rec - x["R_C"]
        if h in BIG:
            c = x.get("cool")
            if not c:
                d["cool"] = {"read": "not read: the score gives no cool-down window for this hold"}
            elif c.get("e_F_C") is None or c.get("e_B_C") is None:
                d["cool"] = {"read": "not read: the score gives no finite cool-down misses for this hold"}
            elif abs(rec - x["R_C"]) > PLATEAU_CHECK_C:
                d["cool"] = {"read": f"not read: the recovery misses the plateau's R by {rec - x['R_C']:+.4f} C"}
            else:
                pf = (c["e_F_C"] - c["e_B_C"]) / G1
                d["cool"] = {"R_C": c["e_F_C"] + pf, "P_F_C_recovered": pf}
        meas[h] = d
    out["measured"] = meas
    plan_rooms = [f"{r:.1f}" for r in m1["plan_rooms_C"]]
    pr = rooms_of(pat, plan_rooms)
    # E185's own registered arms' planned forecasts at the same room (design-e185.json), beside
    D = json.load(open(DESIGN_JSON))
    plans = {r: {hh["hold"]: hh for hh in D["plans"][r]["holds"]} for r in plan_rooms}
    for v in ARMS:
        rm = m1["arms"][v]["rooms"]
        A = {"holds": {}, "summary": {}}
        lines.append(f"ARM {v} (october-forecast-model {v}), at room {room:.3f} C, the {pat} pattern:")
        miss_r, miss_c = [], []
        for h in HOLDS:
            f, how = at_room({r: rm[r]["holds"][h]["rise_C"] for r in pr}, pr, room)
            sd, _ = at_room({r: rm[r]["holds"][h]["rise_sd_C"] for r in pr}, pr, room)
            row = {"rise_model_C": f, "rise_model_sd_C": sd, "room_rule": how}
            m = meas[h]
            if "read" in m:
                row["rise"] = m["read"]
                lines.append(f"  {h} rise: model {f:.3f} +- {sd:.3f} C ({how}); {m['read']}")
            else:
                R = m["R_C"]
                lo, hi = R - Z95 * SIGMA_C, R + Z95 * SIGMA_C
                w, z = where(f, lo, hi), (R - f) / sd
                bd = where(R, f - Z95 * sd, f + Z95 * sd)
                row["rise"] = {"R_C": R, "lo": lo, "hi": hi, "model_reads": w, "z": z, "R_against_model_band": bd, "R_minus_model_C": R - f}
                miss_r.append((h, R - f))
                lines.append(f"  {h} rise: model {f:.3f} +- {sd:.3f} C ({how}) against R {R:.3f} [{lo:.3f}, {hi:.3f}] C: {w}; "
                             f"R {bd} the model's 95% band, z {z:+.2f}")
            if h in BIG:
                cf, _ = at_room({r: rm[r]["holds"][h]["cooldown_C"] for r in pr}, pr, room)
                csd, _ = at_room({r: rm[r]["holds"][h]["cooldown_sd_C"] for r in pr}, pr, room)
                row["cooldown_model_C"], row["cooldown_model_sd_C"] = cf, csd
                c = m.get("cool") if "read" not in m else {"read": m["read"]}
                if c is None or "read" in c:
                    why = (c or {}).get("read", "not read")
                    row["cooldown"] = why
                    lines.append(f"  {h} cool-down: model {cf:.3f} +- {csd:.3f} C; {why}")
                else:
                    Rc = c["R_C"]
                    lo, hi = Rc - Z95 * SIGMA_C, Rc + Z95 * SIGMA_C
                    w, z = where(cf, lo, hi), (Rc - cf) / csd
                    bd = where(Rc, cf - Z95 * csd, cf + Z95 * csd)
                    row["cooldown"] = {"R_C": Rc, "lo": lo, "hi": hi, "model_reads": w, "z": z, "R_against_model_band": bd,
                                       "R_minus_model_C": Rc - cf}
                    miss_c.append((h, Rc - cf))
                    lines.append(f"  {h} cool-down: model {cf:.3f} +- {csd:.3f} C against R {Rc:.3f} [{lo:.3f}, {hi:.3f}] C (recovered): {w}; "
                                 f"R {bd} the model's 95% band, z {z:+.2f}")
            else:
                row["cooldown"] = "not covered (the 120 s rest after this hold; E185 registers no cool-down window for it)"
                lines.append(f"  {h} cool-down: not covered")
            A["holds"][h] = row
        # the summaries, beside E185's own arms
        planned = {}
        for arm, kr, kc in (("F", "P_F_C", "cool_P_F_C"), ("B", "P_B_C", "cool_P_B_C"), ("Rl", "P_Rl_C", "cool_P_Rl_C")):
            er = [meas[h]["R_C"] - at_room({r: plans[r][h][kr] for r in pr}, pr, room)[0] for h, _ in miss_r]
            ec = [meas[h]["cool"]["R_C"] - at_room({r: plans[r][h][kc] for r in pr}, pr, room)[0] for h, _ in miss_c]
            planned[arm] = {"rise_rms_C": rms(er), "rise_mean_C": (sum(er) / len(er)) if er else None,
                            "cooldown_rms_C": rms(ec), "cooldown_mean_C": (sum(ec) / len(ec)) if ec else None}
        best = ((E.get("rules") or {}).get("E185-BEST") or {})
        A["summary"] = {"rises_read": [h for h, _ in miss_r], "rise_rms_C": rms([e for _, e in miss_r]),
                        "rise_mean_C": (sum(e for _, e in miss_r) / len(miss_r)) if miss_r else None,
                        "cooldowns_read": [h for h, _ in miss_c], "cooldown_rms_C": rms([e for _, e in miss_c]),
                        "cooldown_mean_C": (sum(e for _, e in miss_c) / len(miss_c)) if miss_c else None,
                        "beside_E185_BEST_rms_C_measured_watts": best.get("rms_C"), "beside_E185_BEST_word": best.get("verdict"),
                        "beside_registered_arms_planned_forecasts": planned}
        s = A["summary"]
        f4 = (lambda x: "n/a" if x is None else f"{x:.4f}")
        lines.append(f"  {v} over the {len(miss_r)} rises read: rms {f4(s['rise_rms_C'])} C, mean miss {f4(s['rise_mean_C'])} C; over the "
                     f"{len(miss_c)} cool-downs read: rms {f4(s['cooldown_rms_C'])} C, mean {f4(s['cooldown_mean_C'])} C")
        lines.append(f"  beside: E185-BEST's rms (measured watts) {best.get('rms_C')} ({best.get('verdict')}); the registered arms' planned "
                     "forecasts at this room, rise rms " + ", ".join(f"{k} {f4(planned[k]['rise_rms_C'])}" for k in ("F", "B", "Rl")) + " C")
        out["arms"][v] = A
    same = all(json.dumps(out["arms"]["v3"]["holds"][h], sort_keys=True) == json.dumps(out["arms"]["v4"]["holds"][h], sort_keys=True)
               for h in HOLDS)
    out["v4_reads_as_v3"] = same
    lines.append(f"v4 reads {'exactly as v3 (its forecasts equal v3 at every room)' if same else 'differently from v3'}.")
    lines.append("Labels: REPORTED, never a rule; the model's figures are modelled and frozen before any E185 datum; E185's are blind "
                 "measurements; a cool-down's R is recovered from the score's 4-decimal misses (about +-0.004 C).")
    json.dump(out, open(a.out + ".json", "w"), indent=1, sort_keys=True)
    open(a.out + ".txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
