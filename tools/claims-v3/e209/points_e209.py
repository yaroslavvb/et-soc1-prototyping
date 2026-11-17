#!/usr/bin/env python3
"""E209 (Q202): the points, the time cases, the tiles, the order and the session schedule of THE BLIND MATMUL DAY ON aifoundry2's CARD UNDER
ITS GOVERNOR, read from MM1-v2's frozen list (tools/matmul/mm1/v2/out/e209_points.csv and its forecast files, sha256 checked) and never
re-chosen here. Standard library only. Desk: nothing is measured.

    python3 -I -B tools/claims-v3/e209/points_e209.py            writes points-e209.json, points-e209.csv and sched-e209.json beside this file
    python3 -I -B tools/claims-v3/e209/points_e209.py --check    re-makes them in memory and compares byte for byte (PASS / FAIL)

THE POINTS: MM1-v2's 45 (ids e01-e45), each a distinct shape, format, data kind and shire mask (MM1-v2's `case` column), 55 runs (10 points run
  twice), each in MM1-v2's planned form (`burst`: one 6 s process; `sus3`: three, for the two points v2 puts under 8 W over idle).
THE TIME CASES: a distinct (shape, format, shire mask). MM1-v2's, MM1-v1's and F1's time forecasts do not depend on the data kind, so the four
  points that share a shape, format and mask with a random point share its time case (E207's form): 41 time cases; energy is per point (45).
THE MASK is written in the host's own spelling (hex, no leading zeros: the host prints '0x%llx') in the schedule; MM1-v2's spelling is kept
  beside it; a record is compared with its point as a number.
THE TILES: every file a point's --values names, by its sha256 (E208's kit tiles, copies of tools/claims-v3/kinds/tiles/, and E206's real
  tiles under tools/claims-v3/kinds/real2/tiles/); the kit may place them under its own root (E208's src/tiles/ form): the bytes are what
  registers, and the scorer reads a record's --values by its arm, generator and files' <format>/<name> (values_key()).
THE ORDER (registered here): E208's three smoke arms; then A1 (E208's anchor 4x8x8-int8-rnd, a burst), N1 (a null run); pass 1 = the 45 points
  in the order of Python's random.Random("E209|pass1") shuffle of their sorted ids, with an anchor after the 12th, 24th and 36th; pass 2 = the
  second runs of the ten doubled points in the reverse of their pass-1 order; then A5 and N2. 62 runs: 55 point runs, 5 anchors, 2 nulls.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import io
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V2 = "tools/matmul/mm1/v2"
PINS = {
    f"{V2}/out/e209_points.csv": "5e425b771f84e0af53068a6293d46a8fdec40f17dd0381f6a909a9eae2298e8a",
    f"{V2}/out/mm1_v2_e209.csv": "fdd018ca9ceb420285746acdc94b2e0fc62a68141d9b0d3990c3cf9777ec3a63",
    f"{V2}/out/mm1_v1_e209.csv": "f51336af951447678763f0b483c06668d3b462c3c4c30891dc14286112d3a7d3",
    f"{V2}/out/f1f2_e209.csv": "65a98e01868743b4daf4b06be1b1ba4edbd77c47f3d4824353ffdb0bf4ceefce",
}
E208_SRC = "tools/claims-v3/e208/proposal/src"
E208_SCHED = f"{E208_SRC}/sched/a2c0-S1.json"
ANCHOR = {"arm": "4x8x8-int8-rnd", "type": "int8", "shires": "0xffffffff", "values": "gemmL4x8x8:randn:src/tiles/int8/full.bin", "est_peak_w": 50.0}
EST_S = {"burst": 23.0, "sus3": 70.0, "null": 50.0}   # card seconds a run, gates included (MM1-v2's planning, E208 a2c0-S1 averaged; a null ~50 s)
LINE_W = 80.0          # E208's planning line on this card (no point planned above it)
RULE_MIN, CAP_MIN = 45.0, 55.0


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_pins():
    bad = [p for p, h in PINS.items() if sha(os.path.join(REPO, p)) != h]
    if bad:
        sys.exit(f"refused: a frozen MM1-v2 file changed: {bad}")


def mask_int(x):
    return int(str(x), 16)


def mask_host(x):
    return format(mask_int(x), "#x")


def values_files(values):
    parts = values.split(":", 2)
    return [f for f in parts[2].split(",") if f] if len(parts) > 2 else []


def values_key(values):
    """(arm, generator, (format/name, ...)): a --values string read independently of the folder its tiles sit in"""
    parts = str(values).split(":", 2)
    files = tuple("/".join(f.replace("\\", "/").split("/")[-2:]) for f in (parts[2].split(",") if len(parts) > 2 else []) if f)
    return [parts[0], parts[1] if len(parts) > 1 else "", list(files)]


def tile_path(f):
    """the lab path of a tile a --values names: E208's kit tiles (src/tiles/...) sit in E208's committed kit"""
    if f.startswith("src/tiles/"):
        return f"{E208_SRC}/{f[len('src/'):]}"
    return f


def build():
    check_pins()
    P = list(csv.DictReader(open(os.path.join(REPO, V2, "out", "e209_points.csv"))))
    F2 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "out", "mm1_v2_e209.csv")))}
    if [p["id"] for p in P] != [f"e{i:02d}" for i in range(1, 46)] or set(F2) != {p["id"] for p in P}:
        sys.exit("refused: MM1-v2's point list is not e01-e45")
    pts, tiles = [], {}
    for p in P:
        arm = p["arm"]
        MB, NB, KB = (int(x) for x in arm[5:].split("x"))
        files = values_files(p["values"])
        for f in files:
            tiles[f] = sha(os.path.join(REPO, tile_path(f)))
        tc = f"{arm}|{p['fmt']}|{mask_host(p['mask'])}"
        pts.append({"id": p["id"], "family": p["family"], "arm": arm, "blocks": [MB, NB, KB], "fmt": p["fmt"], "kind": p["kind"],
                    "mask_mm1v2": p["mask"], "mask_host": mask_host(p["mask"]), "mask_int": mask_int(p["mask"]), "shires": int(p["shires"]),
                    "minions": int(p["minions"]), "M": int(p["M"]), "N": int(p["N"]), "K": int(p["K"]),
                    "ops_per_minion_per_gemm": int(p["ops"]), "runs_planned": int(p["runs_planned"]), "form": p["form_planned"],
                    "case_mm1v2": p["case"], "time_case": tc, "values": p["values"], "values_key": values_key(p["values"]),
                    "values_files_sha256": {f: tiles[f] for f in files}, "footprint_MB": float(p["footprint_MB"]),
                    "planning_peak_w_mm1v2": round(float(p["pred_board_peak_planning_W"]), 2),
                    "forecast_capped_mm1v2": p["pred_capped"] == "True", "host_args": ["--test", "fma", "--type", p["fmt"], "--pattern", "none",
                                                                                     "--values", p["values"], "--shires", mask_host(p["mask"]),
                                                                                     "--per-shire", "32", "--seconds", "6", "--budget", "7.5",
                                                                                     "--seed", "1"]})
    tcs = {}
    for x in pts:
        tcs.setdefault(x["time_case"], []).append(x["id"])
    ids = sorted(x["id"] for x in pts)
    pass1 = ids[:]
    random.Random("E209|pass1").shuffle(pass1)
    byid = {x["id"]: x for x in pts}
    pass2 = [i for i in reversed(pass1) if byid[i]["runs_planned"] == 2]
    order = [("A1", "anchor", "start"), ("N1", "null", "start")]
    for k, i in enumerate(pass1):
        order.append((i, "arm", "pass1"))
        if k + 1 in (12, 24, 36):
            order.append((f"A{(k + 1) // 12 + 1}", "anchor", "pass1"))
    order += [(i, "arm", "pass2") for i in pass2] + [("A5", "anchor", "end"), ("N2", "null", "end")]
    S = json.load(open(os.path.join(REPO, E208_SCHED)))
    runs = []
    for n, (rid, role, block) in enumerate(order, 1):
        if role == "anchor":
            runs.append({"arm": ANCHOR["arm"], "block": block, "est_peak_w": ANCHOR["est_peak_w"], "est_s": EST_S["burst"], "form": "burst",
                         "i": n, "role": "anchor", "shires": ANCHOR["shires"], "test": "fma", "type": ANCHOR["type"], "unit": rid,
                         "values": ANCHOR["values"]})
        elif role == "null":
            runs.append({"arm": f"null-{rid[1:]}", "block": block, "est_peak_w": 22.5, "est_s": EST_S["null"], "form": "null", "i": n,
                         "role": "null", "test": "null", "unit": rid})
        else:
            x = byid[rid]
            runs.append({"arm": rid, "block": block, "est_peak_w": x["planning_peak_w_mm1v2"], "est_s": EST_S[x["form"]], "form": x["form"], "i": n,
                         "role": "arm", "shires": x["mask_host"], "test": "fma", "type": x["fmt"], "unit": x["time_case"], "values": x["values"]})
    planned_s = sum(r["est_s"] for r in runs)
    sched = {"card": "a2c0", "kit": "E209 (E208's kit form)", "session": "E209", "seed": "E209|pass1", "forms": S["forms"], "process": S["process"],
             "timing": {"cap_min": CAP_MIN, "gate_wait_s": S["timing"]["gate_wait_s"], "open_rest_s": S["timing"]["open_rest_s"], "rule_min": RULE_MIN},
             "line_w": LINE_W, "cap_est_w": max(r["est_peak_w"] for r in runs), "planned_min": round(planned_s / 60.0, 1), "smoke": S["smoke"],
             "runs": runs, "note": "E209's registered order in E208's schedule form (proposal/src/sched/*.json), for the kit; est_peak_w is MM1-v2's "
                                   "planning peak (its board power at the top point + 2 W) at the points, E208's at its anchor and nulls"}
    out = {"experiment": "E209", "what": "MM1-v2's frozen E209 points (never re-chosen), their time cases, tiles, order and schedule",
           "inputs_sha256": dict(PINS), "e208_schedule_form_sha256": {E208_SCHED: sha(os.path.join(REPO, E208_SCHED))},
           "n_points": len(pts), "n_point_runs": sum(x["runs_planned"] for x in pts), "n_time_cases": len(tcs),
           "points": pts, "time_cases": {k: v for k, v in sorted(tcs.items())},
           "shared_time_cases": {k: v for k, v in sorted(tcs.items()) if len(v) > 1}, "tiles_sha256": dict(sorted(tiles.items())),
           "anchor": ANCHOR, "smoke": S["smoke"], "order": [{"n": n, "id": rid, "role": role, "block": block} for n, (rid, role, block) in enumerate(order, 1)],
           "pass1": pass1, "pass2": pass2, "n_runs": len(order), "planned_card_seconds_runs": planned_s,
           "registered_subset_if_cut": "the smoke, A1, N1 and pass 1 with its anchors (every point once)"}
    buf = io.StringIO()
    keys = ["id", "family", "arm", "fmt", "kind", "mask_mm1v2", "mask_host", "shires", "minions", "M", "N", "K", "ops_per_minion_per_gemm",
            "runs_planned", "form", "time_case", "case_mm1v2", "footprint_MB", "planning_peak_w_mm1v2", "forecast_capped_mm1v2", "values"]
    w = csv.DictWriter(buf, fieldnames=keys, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for x in pts:
        w.writerow(x)
    return (json.dumps(out, indent=1, sort_keys=True) + "\n", buf.getvalue(), json.dumps(sched, indent=1, sort_keys=True) + "\n")


def main():
    files = ("points-e209.json", "points-e209.csv", "sched-e209.json")
    made = build()
    if "--check" in sys.argv[1:]:
        bad = [f for f, txt in zip(files, made) if open(os.path.join(HERE, f), encoding="utf-8").read() != txt]
        print("POINTS CHECK " + ("PASS" if not bad else f"FAIL {bad}"))
        sys.exit(0 if not bad else 1)
    for f, txt in zip(files, made):
        with open(os.path.join(HERE, f), "w", encoding="utf-8") as fh:
            fh.write(txt)
    o = json.loads(made[0])
    print(f"points {o['n_points']}, point runs {o['n_point_runs']}, time cases {o['n_time_cases']}, runs {o['n_runs']}, "
          f"planned {round(o['planned_card_seconds_runs'] / 60.0, 1)} card-minutes of runs; shared time cases {o['shared_time_cases']}")


if __name__ == "__main__":
    main()
