#!/usr/bin/env python3
"""E216 (Q227): THE POINT RULE (POINT-RULE-e216.md), applied. Hashed with POINT-RULE-e216.md and models_e216.py into point-rule-e216.sha256
before it ran. Reads the never-run scan (desk/scan-e216.json) and E215's registered point list (tools/claims-v3/e215/points-e215.csv, 4cb2c2ad);
calls the six scored forecasters at 799.0 MHz on aifoundry2 card 0 (models_e216.py); no E215 datum. /usr/bin/python3 3.12.3 -I -B, numpy,
single-threaded.

    python3 -I -B tools/claims-v3/e216/desk/point_rule_e216.py --scan desk/scan-e216.json --out <dir>
        writes <dir>/candidates-e216.json, <dir>/points-e216.json, <dir>/points-e216.csv and prints the draw
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import datetime
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import neverrun_e216 as NR  # noqa: E402
import models_e216 as MD  # noqa: E402

F = 799.0
LINE = 64.0
STOP = 70.0
KBLK = {"fp32": 512, "fp16": 1024, "int8": 2048}
G_KB = (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48)
G_NB = (1, 2, 3, 5, 6)
G_QUOTA = (("NB3", 4), ("NB56", 3), ("L2", 3))
Y_MB, Y_NB, Y_KB = (1, 2, 4), (2, 4, 8), (4, 8, 12, 16, 24)
Y_MASKS = {2: ("0x3", "0x11", "0x101", "0x10001"), 4: ("0xf", "0x33", "0x1111", "0x1010101"), 8: ("0xff", "0xf0f", "0x5555", "0x11111111"),
           16: ("0xffff", "0xff00ff", "0x55555555", "0x33333333")}
Y_TOP, Y_CTRL = 6, 2
F_KB = (1, 2, 3, 4, 6, 8, 12, 16)
F_QUOTA = (("fp16", 2), ("int8", 1), ("fp32", 1))
F_TWINS = 6
FULLM = "0xffffffff"


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def tok(pre, s):
    return "%s%dx%dx%d" % (pre, s[0], s[1], s[2])


def gemm(s, fmt):
    return 1024 * s[0], 512 * s[1], KBLK[fmt] * s[2]


class Draw:
    def __init__(self, scan, M):
        self.S, self.M = scan, M
        self.shapes = set()
        self.points = []
        self.log = {"G": [], "Y": [], "Fa": [], "Fb": []}

    def never(self, token):
        return NR.ran_on_a2(self.S, token)

    def pp(self, pt):
        fc = self.M.forecast([pt], F, models=MD.SCORED)[pt["id"]]
        p, m = self.M.planning_peak(fc)
        return p, m, fc

    def add(self, **kw):
        s = MD.shape_of(kw["arm"])
        Mx, Nx, Kx = gemm(s, kw["fmt"])
        kw.update({"MB": s[0], "NB": s[1], "KB": s[2], "M": Mx, "N": Nx, "K": Kx, "ops_per_minion_per_gemm": 64 * s[0] * s[1] * s[2],
                   "shires": bin(int(kw["mask"], 16)).count("1"), "minions": 32 * bin(int(kw["mask"], 16)).count("1"),
                   "kernel": "rgm136", "loop": "rgm136 gemmLnc" if kw["arm"].startswith("gemmLnc") else "rgm136 gemmL"})
        self.points.append(kw)

    # ------------------------------------------------------------ family G and Gt
    def family_g(self):
        t0 = time.time()
        cands = []
        for fmt in ("fp32", "int8"):
            pts = []
            for MB in range(1, 9):
                for NB in G_NB:
                    for KB in G_KB:
                        s = (MB, NB, KB)
                        pts.append({"id": f"{tok('gemmLnc', s)}|{fmt}", "arm": tok("gemmLnc", s), "fmt": fmt, "kind": "random", "mask": FULLM})
            fc = self.M.forecast(pts, F, models=("MM1-v3.1", "v3.1+lnc"))
            for p in pts:
                a, b = fc[p["id"]]["MM1-v3.1"], fc[p["id"]]["v3.1+lnc"]
                if "W_over_idle" not in a or "W_over_idle" not in b:
                    continue
                beyond = b["lnc"]["beyond"]
                s = MD.shape_of(p["arm"])
                if beyond < 2.6:
                    reg = "L2"
                elif s[1] <= 3:
                    reg = "NB3"
                elif s[1] in (5, 6):
                    reg = "NB56"
                else:
                    reg = None
                if reg is None or (fmt == "int8" and reg != "L2"):
                    continue
                cands.append({"token": p["arm"], "fmt": fmt, "regime": reg, "shape": s, "g": math.log(b["W_over_idle"] / a["W_over_idle"]),
                              "W_v31": a["W_over_idle"], "W_lnc": b["W_over_idle"], "beyond": beyond, "first": b["lnc"]["first"],
                              "dW": b["lnc"]["dW"], "key": f"{p['arm']}|{fmt}|{FULLM}"})
        quota = dict(G_QUOTA)
        order = [r for r, _ in G_QUOTA]
        byreg = {r: sorted([c for c in cands if c["regime"] == r], key=lambda c: (-c["g"], c["key"])) for r in order}
        got = {r: [] for r in order}
        pos = {r: 0 for r in order}
        removed_by_line = {r: 0 for r in order}

        def try_regime(r):
            L = byreg[r]
            while pos[r] < len(L):
                c = L[pos[r]]
                pos[r] += 1
                rec = dict(c, shape=list(c["shape"]))
                if c["shape"] in self.shapes:
                    rec["verdict"] = "shape already drawn"
                    self.log["G"].append(rec)
                    continue
                twin = tok("gemmL", c["shape"])
                ev1, ev2 = self.never(c["token"]), self.never(twin)
                if ev1 or ev2:
                    rec["verdict"] = "ran on the card: " + "; ".join((ev1 + ev2)[:2])
                    self.log["G"].append(rec)
                    continue
                pg, mg, fg = self.pp({"id": "G", "arm": c["token"], "fmt": c["fmt"], "kind": "random", "mask": FULLM})
                pt_, mt, ft = self.pp({"id": "T", "arm": twin, "fmt": c["fmt"], "kind": "random", "mask": FULLM})
                rec.update({"PP_G": pg, "PP_G_by": mg, "PP_twin": pt_, "PP_twin_by": mt,
                            "twin_lnc_dW": ft["v3.1+lnc"].get("lnc_dW_at_v31_t") if ft.get("v3.1+lnc") else None})
                if pg is None or pt_ is None:
                    rec["verdict"] = "an energy not forecast"
                    self.log["G"].append(rec)
                    continue
                if pg > LINE or pt_ > LINE:
                    rec["verdict"] = f"over the {LINE} W line"
                    removed_by_line[r] += 1
                    self.log["G"].append(rec)
                    continue
                rec["verdict"] = "DRAWN"
                rec["three_W_rule"] = "kept" if pg < STOP - 3.0 else "DROPPED"
                self.log["G"].append(rec)
                return rec
            return None
        # each regime to its quota; an unfilled quota passes on in the order NB3, NB56, L2, then back to NB3
        need = 0
        for r in order:
            for _ in range(quota[r]):
                x = try_regime(r)
                if x:
                    got[r].append(x)
                    self.shapes.add(tuple(x["shape"]))
                else:
                    need += 1
        k = 0
        while need > 0 and any(pos[r] < len(byreg[r]) for r in order):
            r = order[k % len(order)]
            k += 1
            x = try_regime(r)
            if x:
                got[r].append(x)
                self.shapes.add(tuple(x["shape"]))
                need -= 1
        drawn = [x for r in order for x in got[r]]
        for n, x in enumerate(drawn, 1):
            self.add(id=f"g{n:02d}", family="G", regime=x["regime"], arm=x["token"], fmt=x["fmt"], kind="random", mask=FULLM,
                     score_g_ln=x["g"], PP_rule=x["PP_G"], twin=f"g{n:02d}t")
        for n, x in enumerate(drawn, 1):
            self.add(id=f"g{n:02d}t", family="Gt", regime=x["regime"], arm=tok("gemmL", tuple(x["shape"])), fmt=x["fmt"], kind="random", mask=FULLM,
                     PP_rule=x["PP_twin"], twin_of=f"g{n:02d}", lnc_dW_twin=x["twin_lnc_dW"])
        self.g_summary = {"candidates": len(cands), "by_regime": {r: len(byreg[r]) for r in order}, "drawn": {r: len(got[r]) for r in order},
                          "removed_by_line_while_drawing": removed_by_line, "secs": round(time.time() - t0, 1)}

    # ------------------------------------------------------------ family Y
    def family_y(self):
        t0 = time.time()
        shapes = [(a, b, c) for a in Y_MB for b in Y_NB for c in Y_KB]
        walked, skipped = [], []
        pairs = []
        for s in shapes:
            t = tok("gemmL", s)
            ev = self.never(t)
            if ev:
                skipped.append({"token": t, "ran": ev[:2]})
                continue
            if s in self.shapes:
                skipped.append({"token": t, "ran": ["shape already drawn"]})
                continue
            walked.append(t)
            pts = [{"id": m, "arm": t, "fmt": "fp32", "kind": "random", "mask": m} for n in Y_MASKS for m in Y_MASKS[n]]
            fc = self.M.forecast(pts, F, models=("MM1-v3.1", "v3.1+contention"))
            for n, ms in Y_MASKS.items():
                for i in range(len(ms)):
                    for j in range(i + 1, len(ms)):
                        A, B = ms[i], ms[j]
                        ca, cb = fc[A]["v3.1+contention"], fc[B]["v3.1+contention"]
                        va, vb = fc[A]["MM1-v3.1"], fc[B]["MM1-v3.1"]
                        pairs.append({"token": t, "shape": list(s), "n": n, "masks": [A, B],
                                      "delta": abs(math.log(ca["T_op_us"] / cb["T_op_us"])),
                                      "d31": abs(math.log(va["T_op_us"] / vb["T_op_us"])),
                                      "signed_ln_A_over_B": math.log(ca["T_op_us"] / cb["T_op_us"]),
                                      "phi": [ca["phi_fresh"], cb["phi_fresh"]], "factor": [ca["layout_factor"], cb["layout_factor"]],
                                      "key": f"{t}|fp32|{A}|{B}"})
        elig = [p for p in pairs if p["d31"] <= 0.0005]
        used = set()

        def take(ranked, k, label):
            out = []
            for p in ranked:
                if len(out) >= k:
                    break
                rec = dict(p)
                s = tuple(p["shape"])
                if s in used or s in self.shapes:
                    rec["verdict"] = "shape already drawn"
                    self.log["Y"].append(rec)
                    continue
                pps = []
                for m in p["masks"]:
                    pp_, by, _ = self.pp({"id": "Y", "arm": p["token"], "fmt": "fp32", "kind": "random", "mask": m})
                    pps.append((pp_, by))
                rec["PP"] = pps
                if any(x[0] is None for x in pps):
                    rec["verdict"] = "an energy not forecast"
                elif any(x[0] > LINE for x in pps):
                    rec["verdict"] = f"over the {LINE} W line"
                else:
                    rec["verdict"] = "DRAWN " + label
                    used.add(s)
                    out.append(rec)
                self.log["Y"].append(rec)
            return out
        top = take(sorted(elig, key=lambda p: (-p["delta"], p["key"])), Y_TOP, "(largest delta)")
        ctrl = take(sorted(elig, key=lambda p: (p["delta"], p["key"])), Y_CTRL, "(control: smallest delta)")
        for n, p in enumerate(top + ctrl, 1):
            ms = sorted(p["masks"], key=lambda m: int(m, 16))
            for lab, m in zip("ab", ms):
                self.add(id=f"y{n:02d}{lab}", family="Y", pair=f"y{n:02d}", pair_role=("largest delta" if n <= len(top) else "control"),
                         arm=p["token"], fmt="fp32", kind="random", mask=m, pair_delta_ln=p["delta"], pair_d31_ln=p["d31"])
            self.shapes.add(tuple(p["shape"]))
        self.y_summary = {"shapes_in_grid": len(shapes), "walked": walked, "not_walked": skipped, "pairs": len(pairs), "eligible_pairs": len(elig),
                          "excluded_v31_differs": len(pairs) - len(elig), "drawn_top": len(top), "drawn_controls": len(ctrl),
                          "secs": round(time.time() - t0, 1), "walk_configs_new": len(self.M.walk_new)}

    # ------------------------------------------------------------ family F
    def family_f(self):
        t0 = time.time()
        rows = [r for r in csv.DictReader(open(os.path.join(REPO, "tools/claims-v3/e215/points-e215.csv")))
                if r["arm"] == "A" and r["family"] in ("P", "C", "R") and r["loop"] == "rgm136 gemmL" and r["shire_mask"].lower() == FULLM]
        pts = [{"id": r["id"], "arm": r["arm_token"], "fmt": r["format"], "kind": r["kind"], "mask": FULLM} for r in rows]
        fc = self.M.forecast(pts, F, models=("MM1-v3.1", "MM1-v3"))
        cand = []
        for r, p in zip(rows, pts):
            a, b = fc[p["id"]]["MM1-v3.1"], fc[p["id"]]["MM1-v3"]
            cand.append({"e215_id": r["id"], "e215_family": r["family"], "token": p["arm"], "fmt": p["fmt"], "kind": p["kind"],
                         "gap_ln": abs(math.log(a["cycles_per_op_wall"] / b["cycles_per_op_wall"])), "cyc_v31": a["cycles_per_op_wall"],
                         "cyc_v3": b["cycles_per_op_wall"]})
        cand.sort(key=lambda c: (-c["gap_ln"], c["e215_id"]))
        twins = []
        for c in cand:
            if len(twins) >= F_TWINS:
                break
            rec = dict(c)
            s = MD.shape_of(c["token"])
            ev = self.never(c["token"])
            if ev:
                rec["verdict"] = "ran on the card: " + ev[0]
            elif s in self.shapes:
                rec["verdict"] = "shape already drawn"
            else:
                pp_, by, _ = self.pp({"id": "Fa", "arm": c["token"], "fmt": c["fmt"], "kind": c["kind"], "mask": FULLM})
                rec.update({"PP": pp_, "PP_by": by})
                if pp_ is None:
                    rec["verdict"] = "an energy not forecast"
                elif pp_ > LINE:
                    rec["verdict"] = f"over the {LINE} W line"
                else:
                    rec["verdict"] = "DRAWN"
                    twins.append(rec)
                    self.shapes.add(s)
            self.log["Fa"].append(rec)
        for n, c in enumerate(twins, 1):
            self.add(id=f"f{n:02d}", family="F", subfamily="card-transfer twin", e215_twin=c["e215_id"], arm=c["token"], fmt=c["fmt"],
                     kind=c["kind"], mask=FULLM, score_gap_ln=c["gap_ln"])
        # (b) new points
        newc = []
        for fmt in ("fp16", "int8", "fp32"):
            pts = []
            for MB in range(1, 9):
                for NB in range(1, 17):
                    for KB in F_KB:
                        s = (MB, NB, KB)
                        t = tok("gemmL", s)
                        if self.never(t):
                            continue
                        pts.append({"id": f"{t}|{fmt}", "arm": t, "fmt": fmt, "kind": "random", "mask": FULLM})
            fc = self.M.forecast(pts, F, models=("MM1-v3.1", "MM1-v3"))
            for p in pts:
                a, b = fc[p["id"]]["MM1-v3.1"], fc[p["id"]]["MM1-v3"]
                newc.append({"token": p["arm"], "fmt": fmt, "gap_ln": abs(math.log(a["cycles_per_op_wall"] / b["cycles_per_op_wall"])),
                             "cyc_v31": a["cycles_per_op_wall"], "cyc_v3": b["cycles_per_op_wall"], "key": f"{p['arm']}|{fmt}|{FULLM}"})
        drawn = []
        for fmt, q in F_QUOTA:
            L = sorted([c for c in newc if c["fmt"] == fmt], key=lambda c: (-c["gap_ln"], c["key"]))
            k = 0
            for c in L:
                if k >= q:
                    break
                rec = dict(c)
                s = MD.shape_of(c["token"])
                if s in self.shapes:
                    rec["verdict"] = "shape already drawn"
                    self.log["Fb"].append(rec)
                    continue
                pp_, by, _ = self.pp({"id": "Fb", "arm": c["token"], "fmt": fmt, "kind": "random", "mask": FULLM})
                rec.update({"PP": pp_, "PP_by": by})
                if pp_ is None:
                    rec["verdict"] = "an energy not forecast"
                elif pp_ > LINE:
                    rec["verdict"] = f"over the {LINE} W line"
                else:
                    rec["verdict"] = "DRAWN"
                    drawn.append(rec)
                    self.shapes.add(s)
                    k += 1
                self.log["Fb"].append(rec)
        for n, c in enumerate(drawn, len(twins) + 1):
            self.add(id=f"f{n:02d}", family="F", subfamily="new", arm=c["token"], fmt=c["fmt"], kind="random", mask=FULLM, score_gap_ln=c["gap_ln"])
        self.f_summary = {"twin_candidates": len(cand), "twins_drawn": len(twins), "new_candidates": len(newc), "new_drawn": len(drawn),
                          "secs": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = now()
    S = json.load(open(a.scan))
    M = MD.Models()
    D = Draw(S, M)
    D.family_g()
    print("G:", json.dumps(D.g_summary), flush=True)
    D.family_y()
    print("Y:", json.dumps({k: v for k, v in D.y_summary.items() if k not in ("walked", "not_walked")}), flush=True)
    D.family_f()
    print("F:", json.dumps(D.f_summary), flush=True)
    os.makedirs(a.out, exist_ok=True)
    meta = {"what": "E216's point rule applied (POINT-RULE-e216.md)", "started": t0, "ended": now(), "clock_mhz": F, "line_W": LINE, "stop_W": STOP,
            "rest_law_W_at_T0": M.rest_W, "rest_law_T0_c": M.rest_T0, "interpreter": "/usr/bin/python3 " + sys.version.split()[0],
            "summaries": {"G": D.g_summary, "Y": D.y_summary, "F": D.f_summary}, "pins": M.pins,
            "scan_sha256": NR.sha(os.path.abspath(a.scan))}
    json.dump({"meta": meta, "log": D.log, "walk_configs_new": D.M.walk_new}, open(os.path.join(a.out, "candidates-e216.json"), "w"), indent=1,
              sort_keys=True, default=float)
    json.dump({"meta": meta, "points": D.points}, open(os.path.join(a.out, "points-e216.json"), "w"), indent=1, default=float)
    cols = ["id", "family", "regime", "pair", "pair_role", "subfamily", "e215_twin", "twin", "twin_of", "loop", "kernel", "arm", "fmt", "kind",
            "mask", "shires", "minions", "MB", "NB", "KB", "M", "N", "K", "ops_per_minion_per_gemm"]
    with open(os.path.join(a.out, "points-e216.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        for p in D.points:
            w.writerow([p.get(c, "") for c in cols])
    for p in D.points:
        print(p["id"], p["family"], p.get("regime") or p.get("pair_role") or p.get("subfamily"), p["arm"], p["fmt"], p["mask"],
              "%.4f" % p.get("score_g_ln", p.get("pair_delta_ln", p.get("score_gap_ln", 0.0))), p.get("e215_twin", ""))
    print("points", len(D.points), "families", {f: sum(1 for p in D.points if p["family"] == f) for f in ("G", "Gt", "Y", "F")})


if __name__ == "__main__":
    main()
