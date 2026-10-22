#!/usr/bin/env python3
"""Validate E62's protocol.json against the die map, the power model, the drift model and the budget. Read-only.

    uv run -q --with numpy python3 validate_protocol.py            # from this directory
    uv run -q --with numpy python3 validate_protocol.py --json <path to protocol.json>

Every geometric fact is re-derived from the lab repo's own
tools/claims-v3/hp/placements.py (which reads workloads/nocbench/analyze.py MARTY), never from the
protocol file, so a transcription error in the protocol cannot hide. Version 2 also re-derives every
angle quoted in a pass rule, rebuilds every executed sign order from the block's own
lap_phase_orders and checks its moments, recomputes every predicted amplitude from the registered
formula, simulates the die temperature through the whole session rather than gating a dwell-weighted
mean, and gates three separate budgets (card time, card-held span, card session wall) at the
WORST-CASE 8.6 s launch. Exit 0 if every assertion holds, 1 otherwise. numpy is not required for the
checks; it is imported only so the run environment matches the design scripts.
"""
import argparse
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HP = os.path.join(HERE, "..", "..", "hp", "placements.py")   # tools/claims-v3/hp/placements.py

# the physical model the checks use, all from DECISIONS.md and the readers' notes
PITCH_C, PITCH_R = 3.73, 3.70     # mm per column step (W-E, long axis) / per row step (N-S, short axis)
W_PER_SHIRE = 1.3                 # DECISIONS section 2: the heater at 800 MHz, per shire at per-shire 32
IDLE_C = 51.0                     # aifoundry2 idle die, at ~23-24 W board
SLOPE_C_PER_W = 0.68              # aifoundry2 die-to-air after the 9 Oct two-fan bracket
IDLE_BOARD_W = 24.0               # measured idle board power
SWAP_W_CAP = 16.0                 # DECISIONS section 2: keep every swap's switched power at or under this
LAUNCH_NOM_S = 8.5                # one chained launch, nominal
LAUNCH_WORST_S = 8.6              # DECISIONS section 3's range is 8.3-8.6 s; the budget is gated here
BLOOM_PHASE_CAP_S = 60.0          # DECISIONS section 2: the all-32 bloom is on for <= 60 s at a time
E61_SCATTER_MK = 27.0             # E61's own measured between-pass scatter, the additive sigma floor
TAU_S = 60.0 / (-math.log(1 - 9.0 / (IDLE_C + SLOPE_C_PER_W * 41.6 - 53.0)))   # DECISIONS' 53 -> 62 C in 60 s

FAILS, WARNS = [], []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
    return bool(cond)


def warn(cond, msg):
    if not cond:
        WARNS.append(msg)
    return bool(cond)


# ------------------------------------------------------------------ the die map, from the lab repo's own code
spec = importlib.util.spec_from_file_location("placements", HP)
pl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pl)
GROUPS, GRID = pl.derive()
DIE = {}
for r, row in enumerate(GRID):
    for j, cell in enumerate(row):
        if cell.startswith("S"):
            DIE[int(cell[1:])] = (r, j + 1)
assert len(DIE) == 32, "the die map did not come out with 32 compute shires"
AT = {v: k for k, v in DIE.items()}


def bits(mask):
    m = int(mask, 16)
    return sorted(s for s in range(32) if m >> s & 1)


def mm(shires):
    rc = [DIE[s] for s in shires]
    x = sum(c for r, c in rc) / len(rc)
    y = sum(r for r, c in rc) / len(rc)
    return ((x - 3.5) * PITCH_C, (y - 2.5) * PITCH_R)


def sep(a, b):
    xa, ya = mm(a)
    xb, yb = mm(b)
    return math.hypot(xa - xb, ya - yb)


def diff(a, b):
    """the centroid difference vector, set a minus set b, in mm"""
    xa, ya = mm(a)
    xb, yb = mm(b)
    return (xa - xb, ya - yb)


def angle_between(u, v):
    d = (u[0] * v[0] + u[1] * v[1]) / (math.hypot(*u) * math.hypot(*v))
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


ap = argparse.ArgumentParser()
ap.add_argument("--json", default=os.path.join(HERE, "protocol.json"))
args = ap.parse_args()
P = json.load(open(args.json))
SETS, BLOCKS = P["sets"], P["blocks"]
CONV = P["conventions"]
MAX_STEADY = P["safety"]["max_steady_c"]
BOARD_CAP = P["safety"]["board_cap_w"]
GOVERNOR = P["safety"]["governor_c"]
BLOOM_STOP = P["safety"]["bloom_cycle_stop_c"]
BUD = P["budget"]
GATE = P["cooldown_gate"]
CARD_MIN_CAP = BUD["card_time_cap_min"]
HELD_CAP = BUD["card_held_cap_min"]
WALL_CAP = BUD["card_session_wall_cap_min"]

print("=" * 118)
print("E62 protocol validation   %s   (version %s)" % (args.json, P.get("version")))
print("die map re-derived from %s (reads workloads/nocbench/analyze.py MARTY)" % HP)
print("budget gated at the worst-case %.1f s launch; sigma floor %.0f mK; tau %.1f s from DECISIONS' 53->62 C/60 s"
      % (LAUNCH_WORST_S, E61_SCATTER_MK, TAU_S))
print("=" * 118)

# ------------------------------------------------------------------ 1. the sets
print()
print("SETS   (mask vs shire list vs harts vs die map; x is the W->E column axis, y the N->S row axis, "
      "origin the die centre)")
print("%-9s %-11s %4s %4s %6s %8s %8s %7s   %s" %
      ("set", "mask", "n", "per", "harts", "x_mm", "y_mm", "sw_W", "mask/list/harts/rc"))
SW = {}
for name, s in SETS.items():
    shires, mask, per, harts = s["shires"], s["mask"], s["per_shire"], s["harts"]
    ok = []
    ok.append(check(all(isinstance(x, int) and 0 <= x <= 31 for x in shires),
                    "%s: a shire is outside 0..31: %s" % (name, shires)))
    ok.append(check(len(set(shires)) == len(shires), "%s: a shire is listed twice" % name))
    ok.append(check(bits(mask) == sorted(shires),
                    "%s: mask %s is %s but the shire list is %s" % (name, mask, bits(mask), sorted(shires))))
    ok.append(check(harts == len(shires) * per,
                    "%s: harts %d != %d shires x per-shire %d" % (name, harts, len(shires), per)))
    rc = s.get("rc")
    if shires:
        ok.append(check(rc is not None, "%s: no rc list" % name))
        if rc is not None:
            ok.append(check(len(rc) == len(shires) and
                            all(tuple(p) == DIE[sh] for sh, p in zip(sorted(shires), rc)),
                            "%s: rc does not match the die map: %s vs %s"
                            % (name, rc, [list(DIE[sh]) for sh in sorted(shires)])))
    else:
        ok.append(check(mask == "0x00000000" and harts == 0 and per == 0,
                        "%s: an empty set must be mask 0x00000000 with 0 harts" % name))
    SW[name] = W_PER_SHIRE * len(shires) * per / 32.0
    x, y = mm(shires) if shires else (0.0, 0.0)
    print("%-9s %-11s %4d %4d %6d %8.2f %8.2f %7.1f   %s" %
          (name, mask, len(shires), per, harts, x, y, SW[name], "ok" if all(ok) else "FAIL"))

# ------------------------------------------------------------------ 2. registered identities, re-derived
print()
print("IDENTITIES re-derived from the die map")
G = GROUPS
CORE24 = sorted(set(G["W12"]["shires"]) | set(G["E12"]["shires"]))


def features(key):
    """(mem_side, ns_edge, by_io, by_ms) for a set, exactly as placements.py counts them"""
    rc = [DIE[s] for s in SETS[key]["shires"]]
    IO, MS = [(0, 5), (0, 6)], [(0, 4), (5, 4)]
    adjf = lambda p, cells: any(abs(p[0] - a) + abs(p[1] - b) == 1 for a, b in cells)
    return (sum(c in (1, 6) and 1 <= r <= 4 for r, c in rc), sum(r in (0, 5) for r, c in rc),
            sum(adjf(p, IO) for p in rc), sum(adjf(p, MS) for p in rc))


F = {k: features(k) for k in ("W12", "E12", "W8B", "E8B", "B4NW", "B4NE", "B4SE", "B4SW", "B4C",
                              "NULLP12", "NULLQ12")}
ids = [
    ("W12 | E12 = N12 | S12 = CORE24 = 0x7777f6f6 (24 shires, 4 per column)",
     CORE24 == sorted(set(G["N12"]["shires"]) | set(G["S12"]["shires"]))
     and "0x%08x" % sum(1 << s for s in CORE24) == "0x7777f6f6" and len(CORE24) == 24),
    ("W12 <-> E12 is the exact mirror c -> 7-c",
     sorted(AT[(r, 7 - c)] for r, c in (DIE[s] for s in G["W12"]["shires"])) == G["E12"]["shires"]),
    ("N12 <-> S12 is the exact mirror r -> 5-r",
     sorted(AT[(5 - r, c)] for r, c in (DIE[s] for s in G["N12"]["shires"])) == G["S12"]["shires"]),
    ("NULLQ12 is NULLP12 rotated 180 deg about the die centre, (r,c) -> (5-r, 7-c)",
     sorted(AT[(5 - DIE[s][0], 7 - DIE[s][1])] for s in SETS["NULLP12"]["shires"])
     == sorted(SETS["NULLQ12"]["shires"])),
    ("NULLP12 | NULLQ12 = CORE24, disjoint, 12 + 12",
     sorted(SETS["NULLP12"]["shires"] + SETS["NULLQ12"]["shires"]) == CORE24),
    ("NULLP12 and NULLQ12 have the same centroid to 1e-9 mm (zero dipole)",
     sep(SETS["NULLP12"]["shires"], SETS["NULLQ12"]["shires"]) < 1e-9),
    ("NULLP12 and NULLQ12 are matched on all four features placements.py records",
     F["NULLP12"] == F["NULLQ12"]),
    ("the five sweep phases are 8 shires each, mean die row exactly 2.5, mean column 1.5/2.5/3.5/4.5/5.5",
     all(len(SETS[k]["shires"]) == 8 for k in ("SCAN1", "SCAN2", "CEN8", "SCAN4", "SCAN5"))
     and [round(sum(DIE[s][0] for s in SETS[k]["shires"]) / 8, 3)
          for k in ("SCAN1", "SCAN2", "CEN8", "SCAN4", "SCAN5")] == [2.5] * 5
     and [round(sum(DIE[s][1] for s in SETS[k]["shires"]) / 8, 3)
          for k in ("SCAN1", "SCAN2", "CEN8", "SCAN4", "SCAN5")] == [1.5, 2.5, 3.5, 4.5, 5.5]),
    ("every sweep phase is an exact one-column translate of the one before",
     all(sorted((DIE[s][0], DIE[s][1] + 1) for s in SETS[a]["shires"]) == sorted(DIE[s] for s in SETS[b]["shires"])
         for a, b in zip(("SCAN1", "SCAN2", "CEN8", "SCAN4"), ("SCAN2", "CEN8", "SCAN4", "SCAN5")))),
    ("the sweep's five phases union to exactly CORE24, and phase 3 IS the registered CEN8",
     sorted(set().union(*[set(SETS[k]["shires"]) for k in ("SCAN1", "SCAN2", "CEN8", "SCAN4", "SCAN5")])) == CORE24
     and SETS["CEN8"]["shires"] == G["CEN8"]["shires"]),
    ("the five orbit arms are all 4 shires x 32 = 128 harts",
     all(SETS[k]["harts"] == 128 for k in ("B4NW", "B4NE", "B4SE", "B4SW", "B4C"))),
    ("B4C sits exactly on the die centre",
     abs(mm(SETS["B4C"]["shires"])[0]) < 1e-9 and abs(mm(SETS["B4C"]["shires"])[1]) < 1e-9),
    ("W8b/E8b are matched on n, mem_side, ns_edge, by_io and by_ms, which W12/E12 are NOT "
     "(physics.md:582 is wrong)",
     len(SETS["W8B"]["shires"]) == len(SETS["E8B"]["shires"]) and F["W8B"] == F["E8B"] and F["W12"] != F["E12"]),
]
for msg, cond in ids:
    check(cond, "identity failed: " + msg)
    print("   %-4s %s" % ("ok" if cond else "FAIL", msg))
print("      (mem_side, ns_edge, by_io, by_ms):  W12 %s  E12 %s   |   W8B %s  E8B %s" %
      (F["W12"], F["E12"], F["W8B"], F["E8B"]))
print("      orbit arms:  NW %s  NE %s  SE %s  SW %s  |  C %s  <- the CENTRE arm is the most mismatched" %
      (F["B4NW"], F["B4NE"], F["B4SE"], F["B4SW"], F["B4C"]))
check(F["W8B"] == F["E8B"], "W8b/E8b are not feature-matched, contrary to placements.py's own assert")
warn(F["W12"] == F["E12"],
     "W12/E12 differ on by_io and by_ms (declared departure: priced at ~34 mK and arbitrated by E62-W8BE8B)")
warn(len({F["B4NW"], F["B4NE"], F["B4SE"], F["B4SW"], F["B4C"]}) == 1,
     "the five orbit arms are not feature-matched, B4C least of all (declared departure: the per-phase board "
     "power band is tightened to +/-0.3 W and the C-minus-corner dipoles carry the ~34 mK correction)")

# ------------------------------------------------------------------ 3. every angle a pass rule quotes
print()
print("ANGLES re-derived from the die map (a hand-written angle in a pass rule cannot survive this)")
ANG = {
    "orbit_diagonal_pair": lambda: angle_between(diff(SETS["B4NW"]["shires"], SETS["B4SE"]["shires"]),
                                                 diff(SETS["B4NE"]["shires"], SETS["B4SW"]["shires"])),
    "orbit_nesw_from_we": lambda: angle_between(diff(SETS["B4NE"]["shires"], SETS["B4SW"]["shires"]),
                                                diff(SETS["E12"]["shires"], SETS["W12"]["shires"])),
    "orbit_nwse_from_we": lambda: angle_between(diff(SETS["B4NW"]["shires"], SETS["B4SE"]["shires"]),
                                                diff(SETS["E12"]["shires"], SETS["W12"]["shires"])),
    "ns_from_we": lambda: angle_between(diff(SETS["S12"]["shires"], SETS["N12"]["shires"]),
                                        diff(SETS["E12"]["shires"], SETS["W12"]["shires"])),
    "sweep_from_we": lambda: angle_between(diff(SETS["SCAN5"]["shires"], SETS["SCAN1"]["shires"]),
                                           diff(SETS["E12"]["shires"], SETS["W12"]["shires"])),
}
n_ang = 0
for b in BLOCKS:
    for a in b.get("angles", []):
        n_ang += 1
        got = ANG[a["derive"]]()
        ok = abs(got - a["deg"]) < 0.05
        check(ok, "%s: the registered angle %s is %.2f deg but the die map gives %.2f deg"
              % (b["id"], a["derive"], a["deg"], got))
        intxt = (("%g" % a["deg"]) in b["pass_rule"]) or (("%.1f" % a["deg"]) in b["pass_rule"])
        if a.get("in_pass_rule"):
            check(intxt, "%s: the pass rule does not quote the registered %.1f deg" % (b["id"], a["deg"]))
        print("   %-4s %-13s %-62s registered %6.1f +/- %-4.0f  die map %6.2f  in pass_rule %s" %
              ("ok" if ok else "FAIL", b["id"], a["name"][:62], a["deg"], a["tol_deg"], got,
               "yes" if intxt else ("not required" if not a.get("in_pass_rule") else "MISSING")))
# the one angle that would have passed version 1 and must now fail: anti-parallel diagonals
check(abs(ANG["orbit_diagonal_pair"]() - 180.0) > 60.0,
      "the orbit diagonals are not anti-parallel and no pass rule may ask for that")
check(not any("anti-parallel" in b["pass_rule"] for b in BLOCKS),
      "a pass rule still asks for anti-parallel diagonals: the two diagonals of a quadrilateral never are, so "
      "correct data would have to fail")
check("anti-parallel within" not in json.dumps(P).lower(),
      "version 1's criterion 'anti-parallel within <n> deg' survives somewhere in protocol.json")

# ------------------------------------------------------------------ 4. the executed sign orders
print()
print("SIGN ORDERS rebuilt from each block's own lap_phase_orders (what the runner EXECUTES, not what analysis assumes)")
SYL = {4: "ABBA", 8: "ABBABAAB", 16: "ABBABAABBAABABBA"}


def moments(signs, upto=4):
    s = [1 if a == "A" else -1 for a in signs]
    return [sum(si * t ** k for t, si in enumerate(s)) for k in range(upto)]


print("%-13s %-11s %4s %4s  %-18s %s" % ("block", "kind", "cyc", "ana", "executed sign order", "moments sum s*t^k"))
for b in BLOCKS:
    pid, ph = b["id"], b["phases"]
    laps = b.get("lap_phase_orders")
    analysed = b["cycles"] - b["warmup_cycles"]
    if not check(laps is not None, "%s: no lap_phase_orders -- a literal phases x cycles run is unbalanced" % pid):
        continue
    check(len(laps) == b["cycles"],
          "%s: lap_phase_orders has %d laps but cycles is %d" % (pid, len(laps), b["cycles"]))
    want = sorted(p["set"] for p in ph)
    check(all(sorted(l) == want for l in laps),
          "%s: a lap in lap_phase_orders is not a permutation of the block's phases" % pid)
    seq = [p for lap in laps[b["warmup_cycles"]:] for p in lap]
    if b["kind"] in ("swap", "control"):
        A = ph[0]["set"]
        signs = "".join("A" if p == A else "B" for p in seq)
        tgt = SYL.get(2 * analysed)
        check(tgt is not None, "%s: %d analysed laps has no registered Sylvester order" % (pid, analysed))
        check(signs == b["analysed_sign_order"] == tgt,
              "%s: the executed order %s is not the registered %s (Sylvester %s)"
              % (pid, signs, b["analysed_sign_order"], tgt))
        check(len(signs) == analysed * len(ph),
              "%s: sign order length %d != %d analysed laps x %d phases" % (pid, len(signs), analysed, len(ph)))
        m = moments(signs)
        check(m[0] == 0 and m[1] == 0,
              "%s: the executed order leaks a constant or a linear drift: moments %s" % (pid, m))
        if analysed >= 4:
            check(m[2] == 0, "%s: with %d analysed laps the quadratic moment must vanish, got %s"
                  % (pid, analysed, m[2]))
        else:
            warn(m[2] == 0, "%s: %d analysed laps leave a quadratic moment of %d (no 4-phase two-arm order can "
                            "do better; bounded by E62-NULLAA's matched two-lap reduction)" % (pid, analysed, m[2]))
        print("%-13s %-11s %4d %4d  %-18s %s" % (pid, b["kind"], b["cycles"], analysed, signs, m))
    elif b["kind"] == "sequence":
        ring = [p["set"] for p in ph]
        shifts = [ring[k:] + ring[:k] for k in range(len(ring))]
        used = laps[b["warmup_cycles"]:]
        check(analysed == len(ring),
              "%s: a sequence needs one analysed lap per phase for the cyclic-shift balance, %d vs %d"
              % (pid, analysed, len(ring)))
        check(all(l in shifts for l in used) and len({tuple(l) for l in used}) == analysed,
              "%s: the analysed laps are not the distinct cyclic shifts of the ring" % pid)
        slots = {p: [l.index(p) for l in used] for p in ring}
        check(all(sorted(v) == list(range(len(ring))) for v in slots.values()),
              "%s: a phase does not visit every slot exactly once: %s" % (pid, slots))
        print("%-13s %-11s %4d %4d  %-18s every phase in every slot once, mean slot %.1f" %
              (pid, b["kind"], b["cycles"], analysed, "cyclic shifts",
               sum(slots[ring[0]]) / float(len(ring))))
    else:
        print("%-13s %-11s %4d %4d  %-18s %s" %
              (pid, b["kind"], b["cycles"], analysed, "fixed", b["analysed_sign_order"][:40]))
# what a literal run would have given, printed so the reason is on the record
print("   for contrast, plain alternation ABABABAB: moments %s -- sum s*t = -4 against the registered 0"
      % moments("ABABABAB"))

# ------------------------------------------------------------------ 5. every predicted amplitude, recomputed
print()
print("PREDICTIONS recomputed from conventions.anchor and conventions.transfer_table (a hand-edited mK cannot pass)")
TT = CONV["transfer_table"]
ANCHOR = CONV["anchor"]


def transfer(d):
    xs, ys = TT["dwell_s"], TT["mk_per_w"]
    for i in range(len(xs) - 1):
        if d <= xs[i + 1] or i == len(xs) - 2:
            k = math.log(ys[i + 1] / ys[i]) / math.log(xs[i + 1] / xs[i])
            return ys[i] * (d / xs[i]) ** k


T_ANCHOR = transfer(ANCHOR["dwell_s"])


def amp(travel, w, dwell):
    return (ANCHOR["mk"] * (travel / ANCHOR["travel_mm"]) * (w / ANCHOR["switched_w"])
            * (transfer(dwell) / T_ANCHOR))


check(CONV["sigma_floor_mk"] >= E61_SCATTER_MK - 1e-9,
      "the registered sigma floor %.1f mK is below E61's own measured between-pass scatter of %.1f mK"
      % (CONV["sigma_floor_mk"], E61_SCATTER_MK))
print("   dwell factors: " + "  ".join("%.1fs %.3f" % (d, transfer(d) / T_ANCHOR) for d in (8.5, 17.0, 25.5, 42.5)))
print("%-13s %8s %7s %6s %5s %8s %8s %7s %7s" %
      ("block", "travel", "sw_W", "dwell", "laps", "pred mK", "formula", "floor", "SNR/all"))
for b in BLOCKS:
    pr = b["predicted"]
    a = pr.get("anchor")
    analysed = b["cycles"] - b["warmup_cycles"]
    if a is None:
        print("%-13s %8s %7s %6s %5d %8s %8s %7s %7s" %
              (b["id"], "-", "-", "-", analysed,
               ("%.0f" % pr["mk"]) if isinstance(pr.get("mk"), (int, float)) else "-",
               "n/a", "-", "-"))
        continue
    want = amp(a["travel_mm"], a["switched_w"], a["dwell_s"])
    got = pr["mk"]
    ok = abs(want - got) <= max(0.5, 0.01 * max(1.0, want))
    check(ok, "%s: predicted.mk %.1f does not match the registered formula's %.1f" % (b["id"], got, want))
    floor = max(CONV["sigma_floor_mk"], CONV["sigma_frac"] * want)
    snr = (want / (floor / math.sqrt(analysed))) if want else 0.0
    if want == 0.0:
        bound = 2 * CONV["sigma_floor_mk"] / math.sqrt(analysed)
        check(abs(pr["bound_2sigma_mk"] - bound) < 0.3,
              "%s: the registered 2 sigma bound %.1f mK is not 2 x %.0f / sqrt(%d) = %.1f"
              % (b["id"], pr["bound_2sigma_mk"], CONV["sigma_floor_mk"], analysed, bound))
    print("%-13s %8.3f %7.1f %6.1f %5d %8.1f %8.1f %7.1f %7s" %
          (b["id"], a["travel_mm"], a["switched_w"], a["dwell_s"], analysed, got, want, floor,
           ("%.1f" % snr) if want else ("2s %.1f" % (2 * CONV["sigma_floor_mk"] / math.sqrt(analysed)))))
# the travels the formula is fed must themselves come from the die map
for bid, pair in (("E62-WE42", ("W12", "E12")), ("E62-NS42", ("N12", "S12")), ("E62-WE17", ("W12", "E12")),
                  ("E62-W8BE8B", ("W8B", "E8B")), ("E62-ORBIT", ("B4NW", "B4SE")),
                  ("E62-SWEEP", ("SCAN1", "SCAN5")), ("E62-NULLGEO", ("NULLP12", "NULLQ12"))):
    b = next(x for x in BLOCKS if x["id"] == bid)
    d = sep(SETS[pair[0]]["shires"], SETS[pair[1]]["shires"])
    check(abs(d - b["predicted"]["anchor"]["travel_mm"]) < 0.01,
          "%s: the registered travel %.3f mm is not the die map's %s<->%s separation of %.3f mm"
          % (bid, b["predicted"]["anchor"]["travel_mm"], pair[0], pair[1], d))

# ------------------------------------------------------------------ 6. the blocks
print()
print("BLOCKS   (launch counts, not clock targets: the runner executes exactly n launches per phase)")
hdr = ("%-13s %-11s %5s %6s %6s %4s %4s %5s %7s %6s %6s %7s %7s" %
       ("block", "kind", "lap_s", "min86", "min85", "cyc", "ana", "lnch", "harts", "sw_W", "brd_W", "steady",
        "pk_inf"))
print(hdr)
print("-" * len(hdr))
total_min = total_min_nom = 0.0
n_launch = 0
for b in BLOCKS:
    pid = b["id"]
    ph = b["phases"]
    analysed = b["cycles"] - b["warmup_cycles"]

    check(all(p["set"] in SETS for p in ph), "%s: a phase names a set that is not defined" % pid)
    check(b["cycles"] >= 1 and 0 <= b["warmup_cycles"] < b["cycles"],
          "%s: cycles %s / warmup %s leaves no analysed lap" % (pid, b["cycles"], b["warmup_cycles"]))

    # launch counts: a loud phase is n launches, an idle phase is timed and launches nothing
    lap86 = lap85 = 0.0
    for p in ph:
        loud = SETS[p["set"]]["harts"] > 0
        n = p.get("launches")
        check(isinstance(n, int), "%s: phase %s has no integer launch count" % (pid, p["set"]))
        if loud:
            check(n >= 1 and abs(p["dwell_s"] - n * LAUNCH_NOM_S) < 1e-6,
                  "%s: phase %s dwell %.2f s is not %s x %.1f s launches (n = %s)"
                  % (pid, p["set"], p["dwell_s"], n, LAUNCH_NOM_S, n))
            lap86 += n * LAUNCH_WORST_S
            lap85 += n * LAUNCH_NOM_S
            n_launch += n * b["cycles"]
        else:
            check(n == 0 and p.get("timed") is True,
                  "%s: IDLE phase %s must carry launches 0 and timed true" % (pid, p["set"]))
            lap86 += p["dwell_s"]
            lap85 += p["dwell_s"]
    est, est_nom = b["est_card_min"], b["est_card_min_nominal"]
    check(abs(est - lap86 * b["cycles"] / 60.0) < 0.01,
          "%s: est_card_min %.3f != worst-case lap %.1f s x %d / 60 = %.3f"
          % (pid, est, lap86, b["cycles"], lap86 * b["cycles"] / 60.0))
    check(abs(est_nom - lap85 * b["cycles"] / 60.0) < 0.01,
          "%s: est_card_min_nominal %.3f != nominal lap %.1f s x %d / 60 = %.3f"
          % (pid, est_nom, lap85, b["cycles"], lap85 * b["cycles"] / 60.0))
    total_min += est
    total_min_nom += est_nom

    # equal harts across the arms of every swap / sequence / control block
    arms = [p["set"] for p in ph]
    loud = [p for p in ph if SETS[p["set"]]["harts"] > 0]
    hs = sorted({SETS[p["set"]]["harts"] for p in loud})
    if b["kind"] in ("swap", "sequence", "control"):
        check(len(hs) == 1,
              "%s (%s): arms do not have equal harts: %s" % (pid, b["kind"], {a: SETS[a]["harts"] for a in arms}))
        check(all(SETS[p["set"]]["harts"] > 0 for p in ph),
              "%s (%s): an IDLE phase is only allowed in a bloom or calibration block" % (pid, b["kind"]))
    elif b["kind"] == "bloom":
        check(len(hs) == 1, "%s (bloom): the loud arms do not have equal harts: %s" % (pid, hs))
    # calibration is exempt by design: its whole purpose is to walk the hart count

    # power and die temperature
    wsum = sum(SW[p["set"]] * p["dwell_s"] for p in ph)
    lap_nom = sum(p["dwell_s"] for p in ph)
    mean_w = wsum / lap_nom
    steady = IDLE_C + SLOPE_C_PER_W * mean_w
    peak_w = max(SW[p["set"]] for p in ph)
    peak_steady = IDLE_C + SLOPE_C_PER_W * peak_w
    check(steady < MAX_STEADY,
          "%s: dwell-weighted steady die %.1f C is not below max_steady_c %.1f C" % (pid, steady, MAX_STEADY))
    for p in ph:
        pw = SW[p["set"]]
        if IDLE_C + SLOPE_C_PER_W * pw >= MAX_STEADY:
            check(p["dwell_s"] <= BLOOM_PHASE_CAP_S,
                  "%s: phase %s would steady at %.1f C and runs for %.1f s, over DECISIONS' %.0f s cap"
                  % (pid, p["set"], IDLE_C + SLOPE_C_PER_W * pw, p["dwell_s"], BLOOM_PHASE_CAP_S))
        if b["kind"] in ("swap", "sequence", "control"):
            check(pw <= SWAP_W_CAP + 1e-9,
                  "%s: swap arm %s draws %.1f W switched, over DECISIONS' %.1f W" % (pid, p["set"], pw, SWAP_W_CAP))
        check(IDLE_BOARD_W + pw <= BOARD_CAP,
              "%s: phase %s would draw about %.1f W at the board, over board_cap_w %.1f"
              % (pid, p["set"], IDLE_BOARD_W + pw, BOARD_CAP))

    pr = b.get("predicted", {})
    check(set(("what", "mk", "direction", "basis", "anchor")) <= set(pr),
          "%s: predicted lacks a required key" % pid)
    check(isinstance(b.get("pass_rule"), str) and len(b["pass_rule"]) > 40, "%s: no usable pass_rule" % pid)
    print("%-13s %-11s %5.1f %6.3f %6.3f %4d %4d %5d %7s %6.1f %6.1f %7.1f %7.1f" %
          (pid, b["kind"], lap86, est, est_nom, b["cycles"], analysed,
           sum(p["launches"] for p in ph), ("%d" % hs[0]) if len(hs) == 1 else "mixed",
           mean_w, IDLE_BOARD_W + mean_w, steady, peak_steady))

# ------------------------------------------------------------------ 7. the die through the whole session
print("-" * len(hdr))
print()
print("DIE TEMPERATURE simulated phase by phase through the session (tau %.1f s), not only as a dwell-weighted mean"
      % TAU_S)
GATES = []
prev_w = None
T = IDLE_C
T = T + (1 - math.exp(-P["session"]["pre_idle_s"] / TAU_S)) * (IDLE_C - T)
worst = (T, "pre-idle")
bloom_peaks = []
for b in BLOCKS:
    lap_nom = sum(p["dwell_s"] for p in b["phases"])
    mean_w = sum(SW[p["set"]] * p["dwell_s"] for p in b["phases"]) / lap_nom
    gated, held_note = False, ""
    if prev_w is not None:
        gated = mean_w > prev_w + 1e-9
        gap = GATE["max_gap_s"] if gated else P["session"]["between_blocks_idle_s"]
        GATES.append((b["id"], gated, gap))
        # the gate's own 30 s baseline gap first, then the die decides whether the extension is used
        T30 = T + (1 - math.exp(-P["session"]["between_blocks_idle_s"] / TAU_S)) * (IDLE_C - T)
        T = T + (1 - math.exp(-gap / TAU_S)) * (IDLE_C - T)
        if gated:
            held_note = ("cool-down gate: die %.1f C after the 30 s gap, threshold %.0f C -> %s"
                         % (T30, GATE["enter_below_c"],
                            "no hold" if T30 <= GATE["enter_below_c"] else "holds up to %.0f s more"
                            % (GATE["max_gap_s"] - P["session"]["between_blocks_idle_s"])))
    prev_w = mean_w
    pk = T
    for c in range(b["cycles"]):
        for p in b["phases"]:
            d = p["launches"] * LAUNCH_WORST_S if p["launches"] else p["dwell_s"]
            tinf = IDLE_C + SLOPE_C_PER_W * SW[p["set"]]
            T = T + (1 - math.exp(-d / TAU_S)) * (tinf - T)
            pk = max(pk, T)
            if b["kind"] == "bloom" and SW[p["set"]] > 0:
                bloom_peaks.append(T)
    if pk > worst[0]:
        worst = (pk, b["id"])
    print("   %-13s mean %5.1f W  peak die %5.1f C  leaving %5.1f C   %s" %
          (b["id"], mean_w, pk, T, held_note))
print("   worst die in the session %.1f C (%s), governor %.0f C, abs stop %.0f C"
      % (worst[0], worst[1], GOVERNOR, P["safety"]["abs_stop_c"]))
check(worst[0] < GOVERNOR, "the simulated die reaches %.1f C, at or over the governor's %.0f C step"
      % (worst[0], GOVERNOR))
print("   E62-BLOOM on-phase peaks %s C against the %.0f C per-cycle gate"
      % (" / ".join("%.1f" % p for p in bloom_peaks), BLOOM_STOP))
check(all(p < BLOOM_STOP for p in bloom_peaks),
      "an E62-BLOOM on-phase peaks at %.1f C, at or over the %.0f C per-cycle gate, so the registered cycle count "
      "would be truncated at nominal power" % (max(bloom_peaks or [0]), BLOOM_STOP))
check(BLOOM_STOP < GOVERNOR, "the bloom's per-cycle gate is not below the governor")

# ------------------------------------------------------------------ 8. order, budget, session
ids_in = [b["id"] for b in BLOCKS]
check(P["order"] == ids_in, "order %s does not match the blocks' own sequence %s" % (P["order"], ids_in))
check(sorted(P["order"]) == sorted(set(ids_in)), "order does not list every block exactly once")
check(len(set(ids_in)) == len(ids_in), "two blocks share an id")
check(P["order"].index("E62-NULLAA") < P["order"].index("E62-SWEEP"),
      "E62-NULLAA must run before E62-SWEEP: it measures the sigma the sweep's detectability is quoted against")
check(P["order"].index("E62-NULLAA") < P["order"].index("E62-NULLGEO"),
      "E62-NULLAA must run before E62-NULLGEO: it is the control whose zero does not depend on the die map")

ses = P["session"]
gap_s = sum(g for _, _, g in GATES)
idles = gap_s + ses["pre_idle_s"] + ses["post_idle_s"]
held = total_min + idles / 60.0
wall = held + BUD["setup_min"] + BUD["cal_decision_min"]
check(total_min <= CARD_MIN_CAP, "total card time %.2f min is over the %.0f min cap" % (total_min, CARD_MIN_CAP))
check(held <= HELD_CAP, "the card-held span %.2f min is over the %.0f min cap" % (held, HELD_CAP))
check(wall <= WALL_CAP, "the card session wall %.2f min (held + %.0f setup + %.0f go/no-go) is over the %.0f min "
                        "cap" % (wall, BUD["setup_min"], BUD["cal_decision_min"], WALL_CAP))
check(BUD["gated_at_launch_s"] == LAUNCH_WORST_S,
      "the budget must be gated at the worst-case %.1f s launch, not %.1f" % (LAUNCH_WORST_S,
                                                                             BUD["gated_at_launch_s"]))
check(ses["pre_idle_s"] >= 180.0,
      "the pre-session idle must be at least 180 s: the FFC detection path has never been exercised on this "
      "camera and camera.md says 15 s was not enough to see one")
check(P["safety"]["abs_stop_c"] <= 90, "abs_stop_c is above the lab's 90 C rule")
check(P["heater"]["timeout_s"] <= 10, "every device process must run under timeout 10")
check(P["heater"]["budget"] < P["heater"]["timeout_s"],
      "--budget must be inside timeout 10 (the default 8.0 s would truncate an 8 s dwell silently)")
check(P["heater"]["launch_seconds"] <= P["heater"]["budget"], "--seconds must not exceed --budget")
check("--stop-file" in P["heater"]["args"], "every launch must carry --stop-file (main.cpp:980)")
R = P["runner"]
check(R["lock"]["blocking"] is False and "flock -n" in R["lock"]["line"],
      "the card lock must be non-blocking flock -n, never a wait loop")
check(R["executable_on_its_own"] is False,
      "protocol.json must declare that it is not executable without PROTOCOL.md sections 4 and 5")
for key in ("lock", "other_user_checks", "telemetry", "stop_watcher", "frames_path", "forbidden"):
    check(key in R, "runner lacks %s: a runner handed protocol.json alone would run on a shared card without it"
          % key)
check(any("reboot" in f for f in R["forbidden"]), "'never reboot aifoundry2' is not in runner.forbidden")

print()
print("total card time %6.2f min  of %.0f      (nominal 8.5 s launch: %.2f min)"
      % (total_min, CARD_MIN_CAP, total_min_nom))
print("plus idle      %6.2f min  (%d s before, %d s after, gaps %s)"
      % (idles / 60.0, int(ses["pre_idle_s"]), int(ses["post_idle_s"]),
         " ".join("%d%s" % (g, "*" if gated else "") for _, gated, g in GATES)))
print("               %6s         * = cool-down gate, gap extended to <= %d s while the die is above %d C"
      % ("", int(GATE["max_gap_s"]), int(GATE["enter_below_c"])))
print("card-held span %6.2f min  of %.0f        slack %.2f min" % (held, HELD_CAP, HELD_CAP - held))
print("card session wall %3.2f min of %.0f     (+ %.0f min setup, %.0f min E62-CAL go/no-go; reduction is OUTSIDE "
      "this and outside the lock)" % (wall, WALL_CAP, BUD["setup_min"], BUD["cal_decision_min"]))
print("heater launches %d, every one under timeout %d with --stop-file" % (n_launch, P["heater"]["timeout_s"]))
print()
print("run order, cumulative card-held minutes (the order IS the priority order):")
cum = ses["pre_idle_s"] / 60.0
gmap = {bid: g for bid, _, g in GATES}
for bid in P["order"]:
    b = next(x for x in BLOCKS if x["id"] == bid)
    cum += b["est_card_min"] + gmap.get(bid, 0.0) / 60.0
    print("   %-13s %6.2f min" % (bid, cum))
print("   %-13s %6.2f min" % ("post-idle", cum + ses["post_idle_s"] / 60.0))

print()
for w in WARNS:
    print("WARN  " + w)
if FAILS:
    print()
    for f in [x for x in FAILS if x]:
        print("FAIL  " + f)
    print()
    print("VALIDATION FAILED: %d problem(s)" % len([x for x in FAILS if x]))
    sys.exit(1)
print()
print("VALIDATION OK: %d sets, %d blocks, %d angles re-derived from the die map, every mask matches its shire list "
      "and the die map, every swap and sequence has equal harts, every executed sign order matches its registered "
      "Sylvester or cyclic-shift form with the claimed moments, every predicted amplitude reproduces from the "
      "registered formula, the simulated die peaks at %.1f C under the %.0f C governor, and %.2f min of card time "
      "/ %.2f min card-held / %.2f min card session wall are inside %.0f / %.0f / %.0f." %
      (len(SETS), len(BLOCKS), n_ang, worst[0], GOVERNOR, total_min, held, wall, CARD_MIN_CAP, HELD_CAP, WALL_CAP))
sys.exit(0)
