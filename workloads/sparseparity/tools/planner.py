#!/usr/bin/env python3
"""planner.py: the host-side planner and merge of the sparse-parity card solver (M0). Host code only; opens no card.

  plan     cut the row tiles (T2 split, colex order) into blocks of equal MODELLED CYCLES, deal the blocks
           round-robin across the shires (block b of a slice goes to shire b mod nshires, then to minion
           (b div nshires) mod mps), and write the binary work list the host passes to the kernel
           (sp.h section 6). A row tile with nJ column tiles and S sample slices costs (the critique's model, with
           the reviews' per-output-tile and hart-1 terms; host/spp_common.h tileCycles is the same function)
               cycles = max(hart 0 = cyc_op * nJ*S + CYC_EPI * nJ + (A resident ? 16*mp / BW : 0),
                            hart 1 = CYC_GEN_SLICE * S,
                            bytes / BW)
               bytes  = B loads (1 KB per op; 1 KB/32 with cooperative loads) + A reads + generated rows (16*mp)
           with cyc_op = 270 (A resident, S <= 3) or 280.35 and BW = 4 B per minion-cycle (measured, from
           docs/research/sparse-parity/design_model.py), CYC_EPI = 450 per output tile and CYC_GEN_SLICE = 800 per
           slice of a row tile (assumed). M2 calibrates them: --model FILE.json.
           --slices N cuts every minion's work into N launches of equal modelled cost (host-side slicing: no
           early exit inside the kernel in M1-M3); --slice i writes launch i (default: all, as FILE.i.bin).
  show     print a work list's header, per-minion and per-shire modelled cycles, and its balance
  merge    merge the per-hart records of one or more launches (pairs --plan WL --out OUT), check every hart
           against its work list (candidates, ops), check the coverage of the union of the plans, and when it
           covers all C(n,k) candidates check both checksums against their closed forms (--inst n,k,eta,m,seed);
           --expect REF compares every hart record with the reference's (spref scan plan= out=), field by field
  closed   the closed forms of sum c and sum c^2 for an instance

Examples:
  planner.py plan --n 512 --k 4 --m 1850 --shires 32 --out l2.bin
  planner.py plan --n 512 --k 5 --m 1280 --tau1 144 --shires 32 --slices 4 --out l5s1.bin   # two-stage stage 1
  spref scan n=512 k=4 eta=0.4 m=1850 seed=1 plan=l2.bin out=l2.ref threads=6
  planner.py merge --plan l2.bin --out l2.ref --inst 512,4,0.4,1850,1
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spcore as sc  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
DESIGN_MODEL = REPO / "docs/research/sparse-parity/design_model.py"


# ---------------------------------------------------------------- the cost model
def model_constants(path: str | None = None) -> dict:
    """Constants from design_model.py (the design's measured numbers), overridden by a JSON file if given."""
    P = dict(CYC_RESIDENT=270.0, CYC_STREAMED=280.35, BW=4.0, F=600e6, MIN_PER_SHIRE=32, TILE_FIXED=0.0,
             RANGE_FIXED=0.0, CYC_EPI=450.0, CYC_GEN_SLICE=800.0, source="built-in copy of design_model.py")
    if DESIGN_MODEL.exists():
        spec = importlib.util.spec_from_file_location("design_model", DESIGN_MODEL)
        dm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dm)
        P.update(CYC_RESIDENT=dm.CYC_RESIDENT, CYC_STREAMED=dm.CYC_STREAMED, BW=dm.BW_PRIVATE, F=dm.F,
                 MIN_PER_SHIRE=dm.MIN_PER_SHIRE, source=str(DESIGN_MODEL.relative_to(REPO)))
    if path:
        P.update(json.loads(Path(path).read_text()))
        P["source"] = f"{P['source']} + {path}"
    return P


def tile_cycles(nJ: int, S: int, P: dict, coop: bool) -> float:
    """Modelled cycles of one row tile that visits nJ column tiles with S sample slices (critique, finding 3; the
    epilogue and hart 1's generation from reviews R1-6 and R2-6). The M1 kernel loads a resident A synchronously
    once per row tile (no double buffer), which is the 16*mp/BW term."""
    mp = 64 * S
    ops = nJ * S
    resident = S <= 3
    gen = 16 * mp                                    # the generated rows, written once and read back
    b_rd = 1024.0 * ops / (P["MIN_PER_SHIRE"] if coop else 1)
    a_rd = gen if resident else 1024.0 * ops
    a_load = gen / P["BW"] if resident else 0.0
    cyc_op = P["CYC_RESIDENT"] if resident else P["CYC_STREAMED"]
    hart0 = cyc_op * ops + P["CYC_EPI"] * nJ + a_load
    hart1 = P["CYC_GEN_SLICE"] * S
    return max(hart0, hart1, (b_rd + a_rd + gen) / P["BW"]) + P["TILE_FIXED"]


class CostProfile:
    """Prefix sums of the modelled cost over the row tiles, in closed form per run of equal nJ."""

    def __init__(self, G: sc.Geom, P: dict, coop: bool):
        self.G = G
        self.runs = []                               # (t0, t1, nJ, cost per tile, cumulative cost at t0)
        acc = 0.0
        for t0, t1, nJ in G.runs():
            c = tile_cycles(nJ, G.S, P, coop)
            self.runs.append((t0, t1, nJ, c, acc))
            acc += (t1 - t0) * c
        self.total = acc

    def cost_to(self, t: int) -> float:
        """modelled cycles of row tiles [0, t)"""
        for t0, t1, _, c, acc in self.runs:
            if t <= t1:
                return acc + max(0, t - t0) * c
        return self.total

    def tile_at(self, x: float) -> int:
        """the row-tile boundary whose prefix cost is nearest x"""
        if x <= 0:
            return 0
        for t0, t1, _, c, acc in self.runs:
            if x <= acc + (t1 - t0) * c:
                return min(t1, t0 + int(round((x - acc) / c)))
        return self.G.NT


# ---------------------------------------------------------------- plan
def make_plan(n, k, m, nshires, mps, bpm, nslices, P, coop=False, topm=8, tau1=None, shire_mask=None,
              contiguous=False):
    """-> list of WorkList, one per slice. contiguous=True reproduces DESIGN.md's first layout (blocks of equal
    OPS, minion b in shire b div mps) for comparison only."""
    G = sc.Geom(n, k, m)
    if tau1 is not None and (G.NR >= 1 << 40 or m > 4095):
        raise ValueError(f"two-stage: {G.NR} rows and m1 = {m} do not fit a survivor entry (rows < 2^40, m1 <= 4095)")
    prof = CostProfile(G, P, coop)
    nmin = nshires * mps
    NB = nmin * bpm * nslices
    if contiguous:                                   # equal ops, not equal cycles
        ops_runs = [(t0, t1, nJ) for t0, t1, nJ in G.runs()]
        tot_ops = sum((t1 - t0) * nJ for t0, t1, nJ in ops_runs)

        def tile_at_ops(x):
            acc = 0
            for t0, t1, nJ in ops_runs:
                if x <= acc + (t1 - t0) * nJ:
                    return min(t1, t0 + int(round((x - acc) / nJ)))
                acc += (t1 - t0) * nJ
            return G.NT
        cuts = [0] + [tile_at_ops(b * tot_ops / NB) for b in range(1, NB)] + [G.NT]
    else:
        cuts = [0] + [prof.tile_at(b * prof.total / NB) for b in range(1, NB)] + [G.NT]
    for b in range(1, len(cuts)):                    # monotone
        cuts[b] = max(cuts[b], cuts[b - 1])
    # DESIGN.md's M0 exit criterion: every block within one row tile of its equal share
    tile_max = max((c for *_, c, _ in prof.runs), default=0.0)
    target = prof.total / NB
    cut_err = max(abs(prof.cost_to(cuts[b + 1]) - prof.cost_to(cuts[b]) - target) for b in range(NB)) / tile_max \
        if tile_max and not contiguous else None
    if shire_mask is None:
        shire_mask = (1 << nshires) - 1
    flags = (sc.WL_TWOSTAGE if tau1 is not None else 0) | (sc.WL_COOP if coop else 0)
    out = []
    for sl in range(nslices):
        per_min = [[] for _ in range(nmin)]
        for b in range(NB):
            if b % nslices != sl:
                continue
            qb = b // nslices
            if contiguous:
                shire, mis = (qb // bpm) // mps, (qb // bpm) % mps
            else:
                shire, mis = qb % nshires, (qb // nshires) % mps
            per_min[shire * mps + mis].append(b)
        ranges, minions = [], []
        for q in range(nmin):
            first = len(ranges)
            for b in per_min[q]:
                t0, t1 = cuts[b], cuts[b + 1]
                if t1 <= t0:
                    continue
                ranges.append(dict(tile_begin=t0, tile_end=t1, ops=G.range_outtiles(t0, t1) * G.S,
                                   cands=G.range_cands(t0, t1),
                                   cyc=prof.cost_to(t1) - prof.cost_to(t0) + P["RANGE_FIXED"],
                                   first_R=G.unrank(16 * t0), minion=q, block=b))
            minions.append((first, len(ranges) - first, q // mps, q % mps))
        hdr = dict(n=n, k=k, m=m, S=G.S, nshires=nshires, mps=mps, nminions=nmin, topm=topm, flags=flags,
                   tau1=tau1 if tau1 is not None else 0, slice=sl, nslices=nslices, blocks_per_minion=bpm,
                   shire_mask=shire_mask, NR=G.NR, NT=G.NT, total_ops=sum(r["ops"] for r in ranges),
                   total_cands=sum(r["cands"] for r in ranges), total_cyc=int(round(sum(r["cyc"] for r in ranges))))
        out.append(sc.WorkList(hdr, minions, ranges))
    prof.cut_error_tiles = cut_err
    return out, G, prof


def balance(W: sc.WorkList, P: dict) -> dict:
    h = W.hdr
    per_min = [0.0] * h["nminions"]
    for r in W.ranges:
        per_min[r["minion"]] += r["cyc"]
    per_shire = [sum(per_min[s * h["mps"]:(s + 1) * h["mps"]]) for s in range(h["nshires"])]
    mean = sum(per_min) / len(per_min)
    smean = sum(per_shire) / len(per_shire)
    return dict(minion_max_cyc=max(per_min), minion_mean_cyc=mean, minion_imbalance=max(per_min) / mean if mean else 0,
                shire_imbalance=max(per_shire) / smean if smean else 0,
                kernel_s_model=max(per_min) / P["F"], ops=h["total_ops"], cands=h["total_cands"],
                ranges=len(W.ranges), empty_minions=sum(1 for c in per_min if c == 0))


def cmd_plan(a):
    P = model_constants(a.model)
    nshires = a.shires if a.shire_mask is None else bin(int(a.shire_mask, 0)).count("1")
    mask = None if a.shire_mask is None else int(a.shire_mask, 0)
    plans, G, prof = make_plan(a.n, a.k, a.m, nshires, a.mps, a.blocks_per_minion, a.slices, P, coop=a.coop,
                               topm=a.topm, tau1=a.tau1, shire_mask=mask)
    outp = Path(a.out)
    written = []
    for W in plans:
        if a.slice is not None and W.hdr["slice"] != a.slice:
            continue
        path = outp if (a.slices == 1 or a.slice is not None) else outp.with_suffix(f".{W.hdr['slice']}{outp.suffix}")
        path.write_bytes(W.to_bytes())
        written.append(dict(file=str(path), slice=W.hdr["slice"], **balance(W, P)))
    # the same instance cut by DESIGN.md's first layout (equal ops, contiguous shires), for comparison
    ref, _, _ = make_plan(a.n, a.k, a.m, nshires, a.mps, 1, 1, P, coop=a.coop, topm=a.topm, tau1=a.tau1,
                          contiguous=True)
    summary = dict(n=a.n, k=a.k, m=a.m, S=G.S, NR=G.NR, NT=G.NT, Ncand=G.Ncand, nshires=nshires, mps=a.mps,
                   blocks_per_minion=a.blocks_per_minion, slices=a.slices, coop=a.coop, model=P["source"],
                   total_model_cyc=prof.total, cut_error_tiles=prof.cut_error_tiles, files=written,
                   equal_ops_contiguous=balance(ref[0], P))
    print(json.dumps(summary, indent=None if a.compact else 1, default=float))


def cmd_show(a):
    P = model_constants(a.model)
    W = sc.WorkList.from_bytes(Path(a.plan).read_bytes())
    b = balance(W, P)
    print(json.dumps(dict(header=W.hdr, **b), indent=1, default=float))
    if a.ranges:
        for r in W.ranges:
            print(json.dumps(r))


# ---------------------------------------------------------------- merge
def parse_inst(s):
    n, k, eta, m, seed = s.split(",")
    return int(n), int(k), float(eta), int(m), int(seed)


def merge(pairs, inst=None, expect=None, check_hart1=True, partial=False):
    """pairs: [(WorkList, (hdr, recs, tops))]. Returns a report dict; report['ok'] says whether every check passed.
    Unless partial=True, the union of the plans must cover every row tile exactly once."""
    errors = []
    W0 = pairs[0][0]
    n, k, m = W0.hdr["n"], W0.hdr["k"], W0.hdr["m"]
    G = sc.Geom(n, k, m)
    sum_c, sum_c2, cands, ops = 0, 0, 0, 0
    best = None
    top = []
    topm = W0.hdr["topm"]
    intervals = []
    reported = set()                                 # every hart's best and top entries, rescored below
    at_best = []                                     # (c, tie flag) of every hart's best: a tie across harts
    for pi, (W, (oh, recs, tops)) in enumerate(pairs):
        h = W.hdr
        if (h["n"], h["k"], h["m"]) != (n, k, m):
            errors.append(f"launch {pi}: plan is for a different (n, k, m)")
        if (oh["n"], oh["k"], oh["m"], oh["nminions"]) != (h["n"], h["k"], h["m"], h["nminions"]):
            errors.append(f"launch {pi}: output header does not match its plan")
            continue
        harts = oh["harts"]
        for q in range(h["nminions"]):
            first, nr, _, _ = W.minions[q]
            rg = W.ranges[first:first + nr]
            want_c = sum(r["cands"] for r in rg)
            want_o = sum(r["ops"] for r in rg)
            want_t = sum(r["tile_end"] - r["tile_begin"] for r in rg)
            intervals += [(r["tile_begin"], r["tile_end"]) for r in rg]
            r0 = recs[q * harts]
            if r0["magic"] != sc.REC_MAGIC or not (r0["flags"] & sc.REC_VALID) or r0["minion"] != q or r0["hart"] != 0:
                errors.append(f"launch {pi} minion {q}: hart-0 record missing or invalid ({r0})")
                continue
            if r0["flags"] & (sc.REC_ERROR | sc.REC_LOG_OVERFLOW):
                errors.append(f"launch {pi} minion {q}: flags {r0['flags']:#x}")
            if r0["cands"] != want_c or r0["ops"] != want_o % (1 << 32):
                errors.append(f"launch {pi} minion {q}: cands {r0['cands']} ops {r0['ops']}, plan {want_c} {want_o}")
            if check_hart1 and harts > 1:
                r1 = recs[q * harts + 1]
                if r1["magic"] != sc.REC_MAGIC or r1["hart"] != 1 or r1["ops"] != want_t % (1 << 32):
                    errors.append(f"launch {pi} minion {q}: hart-1 record {r1['ops']} row tiles, plan {want_t}")
            sum_c += r0["sum_c"]
            sum_c2 = (sum_c2 + r0["sum_c2"]) & sc.M64
            cands += r0["cands"]
            ops += r0["ops"]
            if r0["flags"] & sc.REC_HAS_BEST:
                e = (r0["best_c"], r0["best_j"], r0["best_row"])
                reported.add(e)
                at_best.append((r0["best_c"], bool(r0["flags"] & sc.REC_TIE)))
                if best is None or sc.better(e, best):
                    best = e
            top += tops[q]
            reported.update(tops[q])
            if expect is not None:
                eh, erecs, etops = expect[pi]
                for hh in range(harts):
                    a, b = recs[q * harts + hh], erecs[q * harts + hh]
                    diff = [f for f in sc.REC_FIELDS if f != "cycles" and a[f] != b[f]]
                    if diff:
                        errors.append(f"launch {pi} minion {q} hart {hh}: differs from the reference in {diff}")
                if tops[q] != etops[q]:
                    errors.append(f"launch {pi} minion {q}: top list differs from the reference")
    top = sorted(set(top), key=sc.sort_key)[:topm]
    # coverage of the union of the plans
    intervals.sort()
    pos, gaps, overlaps = 0, 0, 0
    for t0, t1 in intervals:
        if t0 > pos:
            gaps += 1
        if t0 < pos:
            overlaps += 1
        pos = max(pos, t1)
    complete = gaps == 0 and overlaps == 0 and pos == G.NT
    if overlaps:
        errors.append(f"{overlaps} overlapping ranges across the plans")
    if not complete and not partial:
        errors.append(f"coverage incomplete: {gaps} gaps, row tiles up to {pos} of {G.NT} (pass --partial for a slice)")
    rep = dict(n=n, k=k, m=m, launches=len(pairs), cands=cands, Ncand=G.Ncand, ops=ops, sum_c=sum_c, sum_c2=sum_c2,
               coverage=dict(complete=complete, gaps=gaps, overlaps=overlaps, end=pos, NT=G.NT))
    if best is not None:
        # a tie: two harts whose best is the best c, or one hart that flags a second candidate at its best c (the
        # kernel keeps no top list, so with --topm 0 the flags are the only evidence; review R2, finding 7)
        holders = [t for c, t in at_best if c == best[0]]
        unique = len(holders) == 1 and not holders[0] and (len(top) < 2 or top[1][0] < best[0])
        rep["best"] = dict(c=best[0], j=best[1], row=best[2], found=list(G.found_set(best[2], best[1])),
                           unique=unique, harts_at_best=len(holders), harts_flagging_tie=sum(holders))
        rep["top"] = [list(e) for e in top]
    if complete and cands != G.Ncand:
        errors.append(f"coverage complete but {cands} candidates scored, C(n,k) = {G.Ncand}")
    if inst is not None:
        I = sc.gen(*inst[:2], inst[2], m, inst[4])   # the scanned instance: m = the plan's m (m1 in a screen)
        rep["secret"] = list(I.secret)
        if best is not None:
            rep["ok_secret"] = tuple(rep["best"]["found"]) == I.secret and rep["best"]["unique"]
            # rescore every hart's reported best and top entries on the host: a wrong index or value is caught
            bad = [e for e in reported if e[2] >= G.NR or e[1] >= n or sc.score(I, G, e[2], e[1]) != e[0]]
            rep["rescored"] = dict(entries=len(reported), wrong=len(bad))
            if bad:
                errors.append(f"{len(bad)} reported candidates do not rescore to their c, e.g. {sorted(bad)[:3]}")
        if complete:
            s1, s2, s2m = sc.closed_forms(I)
            rep["closed"] = dict(sum_c=s1, sum_c2=s2m, sum_c2_exact=s2, match=(s1 == sum_c and s2m == sum_c2))
            if not rep["closed"]["match"]:
                errors.append("checksums differ from their closed forms: a candidate was missed, repeated or misscored")
    rep["errors"] = errors[:50]
    rep["n_errors"] = len(errors)
    rep["ok"] = not errors
    return rep


def cmd_merge(a):
    if len(a.plan) != len(a.out):
        sys.exit("give one --out per --plan")
    pairs = [(sc.WorkList.from_bytes(Path(p).read_bytes()), sc.read_out(Path(o).read_bytes()))
             for p, o in zip(a.plan, a.out)]
    expect = None
    if a.expect:
        if len(a.expect) != len(a.plan):
            sys.exit("give one --expect per --plan")
        expect = [sc.read_out(Path(e).read_bytes()) for e in a.expect]
    rep = merge(pairs, parse_inst(a.inst) if a.inst else None, expect, check_hart1=not a.no_hart1,
                partial=a.partial)
    print(json.dumps(rep, indent=None if a.compact else 1))
    sys.exit(0 if rep["ok"] else 1)


def cmd_closed(a):
    n, k, eta, m, seed = parse_inst(a.inst)
    I = sc.gen(n, k, eta, m, seed)
    s1, s2, s2m = sc.closed_forms(I)
    print(json.dumps(dict(n=n, k=k, eta=eta, m=m, seed=seed, Ncand=math.comb(n, k), sum_c=s1, sum_c2=s2m,
                          sum_c2_exact=s2)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--k", type=int, required=True)
    p.add_argument("--m", type=int, required=True, help="samples the launch scans (m1 for a two-stage screen)")
    p.add_argument("--shires", type=int, default=32)
    p.add_argument("--shire-mask", default=None, help="physical shires, e.g. 0xffffffff (overrides --shires)")
    p.add_argument("--mps", type=int, default=32, help="minions per shire")
    p.add_argument("--blocks-per-minion", type=int, default=1)
    p.add_argument("--slices", type=int, default=1, help="host-side launches the work is cut into")
    p.add_argument("--slice", type=int, default=None, help="write only this launch")
    p.add_argument("--coop", action="store_true", help="model cooperative B loads (M4)")
    p.add_argument("--topm", type=int, default=8)
    p.add_argument("--tau1", type=int, default=None, help="two-stage: log survivors with c1 >= tau1")
    p.add_argument("--model", default=None, help="JSON overrides of the cost constants (M2's calibration)")
    p.add_argument("--out", required=True)
    p.add_argument("--compact", action="store_true")
    p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("show")
    p.add_argument("plan")
    p.add_argument("--ranges", action="store_true")
    p.add_argument("--model", default=None)
    p.set_defaults(fn=cmd_show)
    p = sub.add_parser("merge")
    p.add_argument("--plan", action="append", required=True)
    p.add_argument("--out", action="append", required=True)
    p.add_argument("--expect", action="append", default=None)
    p.add_argument("--inst", default=None, help="n,k,eta,m,seed (m = the full sample count; the plan's m is scanned)")
    p.add_argument("--no-hart1", action="store_true", help="do not check the hart-1 (row generation) records")
    p.add_argument("--partial", action="store_true", help="the plans need not cover every row tile (one slice)")
    p.add_argument("--compact", action="store_true")
    p.set_defaults(fn=cmd_merge)
    p = sub.add_parser("closed")
    p.add_argument("--inst", required=True)
    p.set_defaults(fn=cmd_closed)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
