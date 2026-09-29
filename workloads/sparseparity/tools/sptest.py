#!/usr/bin/env python3
"""sptest.py: tests of the sparse-parity CPU side (M0), and the comparison of card outputs with the reference.
Host code only; opens no card. Runs small sizes, with at most --threads threads (default 2), niced by the caller.

  sptest.py [--bin DIR] [--threads 2] [--spbits PATH] [groups...]   groups: gen closed ref plan planbig base (default all)
      gen     C generator and layouts (spref gen) = Python mirror (spcore) = proto/spbits gen (if --spbits)
      closed  closed-form checksums (Python) = C (spref check) = brute force in C and in Python
      ref     spref selftest (closed = brute = bits = int8 = merged plan, tie flags included; negative controls: a
              dropped range, a duplicated range, one tile's staircase mask shifted); C0's 4,960 correlations (int8
              path) = Python brute force one by one; C1: int8 path = bits path
      plan    planner -> spref plan= -> merge: every hart matches its plan, the union of the slices covers every
              row tile once, both checksums match their closed forms, the merged answer = the full scan's;
              negative controls: a tampered record, a duplicated range, a dropped range and a flagged tie must each
              be caught; every block within one row tile of its equal share of modelled cycles
      planbig the showcase plans on 32 x 32 minions (no scan): coverage, cut error, balance
      base    vexh (sums=1) = reference (answer and both checksums); two-stage survivors and stage 2 = reference;
              mitm (with and without the random halving) finds the reference's answer; batch (B1, 8 instances per
              register and one per thread) solves what the reference solves
  sptest.py card --plan WL --out CARD [--plan WL2 --out CARD2 ...] --inst n,k,eta,m,seed [--m1 M1 --tau1 T]
      runs the reference on each work list and compares the card's per-hart records with it, field by field
      (cycles excepted), then merges and checks coverage and the checksums.
Exit status 0 when every check passes.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import planner  # noqa: E402
import spcore as sc  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name}{(': ' + detail) if detail and not cond else ''}", flush=True)
    if not cond:
        FAILS.append(name)
    return cond


def run(args, ok_codes=(0,)):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if p.returncode not in ok_codes:
        raise RuntimeError(f"{' '.join(map(str, args))} -> {p.returncode}\n{p.stderr[-2000:]}")
    return p.stdout


def jrun(args, ok_codes=(0,)):
    return json.loads(run(args, ok_codes).strip().splitlines()[-1])


def kv(**d):
    return [f"{k}={v}" for k, v in d.items()]


# ---------------------------------------------------------------- groups
def t_gen(B, a):
    cases = [(32, 3, 0.1, 128, 1), (128, 4, 0.2, 192, 1), (512, 4, 0.3, 448, 1), (512, 4, 0.4, 1850, 1),
             (256, 5, 0.4, 1925, 1), (512, 5, 0.4, 2151, 1), (64, 4, 0.1, 64, 7), (33, 3, 0.3, 70, 7)]
    for n, k, eta, m, seed in cases:
        c = jrun([B / "spref", "gen", *kv(n=n, k=k, eta=eta, m=m, seed=seed)])
        I = sc.gen(n, k, eta, m, seed)
        S = sc.slices(m)
        same = (c["hash"] == sc.inst_hash(I) and tuple(c["secret"]) == I.secret
                and c["pm1_hash"] == sc.bytes_hash(sc.pm1_features(I, 64 * S).tobytes())
                and c["labels_hash"] == sc.bytes_hash(sc.pm1_labels(I, 64 * S).tobytes())
                and c["btiles_hash"] == sc.bytes_hash(sc.btiles(I, S).tobytes()))
        check(f"gen C = Python (instance, +-1, B tiles) {n,k,eta,m,seed}", same)
        if a.spbits:
            s = jrun([a.spbits, "gen", *kv(n=n, k=k, eta=eta, m=m, seed=seed)])
            check(f"gen = proto/spbits {n,k,eta,m,seed}", s.get("hash") == c["hash"], f"{s} vs {c['hash']}")
    # prefix consistency: the first m1 samples of (n,k,eta,m,seed) are (n,k,eta,m1,seed)
    I, I1 = sc.gen(512, 5, 0.4, 2151, 1), sc.gen(512, 5, 0.4, 1280, 1)
    xb, yb = I.bits()
    xb1, yb1 = I1.bits()
    check("generator is prefix-consistent (two-stage stage 1 = the first m1 samples)",
          (xb[:1280] == xb1).all() and (yb[:1280] == yb1).all() and I.secret == I1.secret)


def t_closed(B, a):
    for n, k, eta, m, seed in [(12, 3, 0.2, 20, 1), (16, 4, 0.1, 37, 2), (10, 5, 0.3, 9, 3), (32, 3, 0.1, 128, 1),
                               (24, 6, 0.2, 40, 4), (40, 2, 0.4, 300, 5), (48, 4, 0.25, 99, 6)]:
        I = sc.gen(n, k, eta, m, seed)
        s1, s2, s2m = sc.closed_forms(I)
        c = jrun([B / "spref", "check", *kv(n=n, k=k, eta=eta, m=m, seed=seed, brute=1, pm1=1)])
        d, _ = sc.brute(I)
        b1, b2 = sum(d.values()), sum(v * v for v in d.values())
        check(f"closed forms: Python = C = brute force (C) = brute force (Python) {n,k,eta,m,seed}",
              s1 == c["sum_c"] == b1 and s2m == c["sum_c2"] and s2 == b2 and c["brute"]["match"] == 1,
              f"py {s1} {s2}, C {c['sum_c']} {c['sum_c2']}, brute {b1} {b2}")
    # the large sizes: Python and C agree on the closed forms (no brute force possible)
    for inst in [(512, 4, 0.4, 1850, 1), (256, 5, 0.4, 1925, 1), (512, 5, 0.4, 2151, 1)]:
        I = sc.gen(*inst)
        s1, s2, s2m = sc.closed_forms(I)
        c = jrun([B / "spref", "check", *kv(n=inst[0], k=inst[1], eta=inst[2], m=inst[3], seed=inst[4])])
        check(f"closed forms Python = C {inst}", s1 == c["sum_c"] and s2m == c["sum_c2"] and c["sum_c2_exact"] == 1)


def t_ref(B, a):
    p = subprocess.run([B / "spref", "selftest", f"threads={a.threads}"], capture_output=True, text=True)
    lines = [json.loads(x) for x in p.stdout.splitlines() if x.startswith("{")]
    check(f"spref selftest ({len(lines) - 1} sizes: closed = brute = bits = int8 = merged plan; negative controls)",
          p.returncode == 0 and lines[-1].get("failures") == 0, p.stdout[-500:])
    with tempfile.TemporaryDirectory() as td:
        dump = Path(td) / "c0.bin"
        r = jrun([B / "spref", "scan", *kv(n=32, k=3, eta=0.1, m=128, seed=1, mode="int8", dump=dump, topm=8)])
        import numpy as np
        got = np.fromfile(dump, dtype="<i4")
        d, _ = sc.brute(sc.gen(32, 3, 0.1, 128, 1))
        want = np.array([d[i] for i in range(len(got))])
        check("C0: all 4,960 correlations of the int8 path = Python brute force",
              len(got) == 4960 and (got == want).all() and r["dump"]["missing"] == 0 and r["dump"]["duplicated"] == 0)
    c1 = [jrun([B / "spref", "scan", *kv(n=128, k=4, eta=0.2, m=192, seed=s, mode=md, threads=a.threads)])
          for s in (1, 2) for md in ("bits", "int8")]
    check("C1 seeds 1-2: int8 path = bits path (answer, top-8, checksums, ops) and = closed forms",
          all(c1[i]["result"] == c1[i + 1]["result"] and c1[i]["closed"]["match"] for i in (0, 2)))


def t_plan(B, a):
    cases = [  # (n, k, eta, m, seed), shires, mps, blocks per minion, slices, two-stage (m1, tau1)
        ((32, 3, 0.1, 128, 1), 1, 1, 1, 1, None),
        ((32, 3, 0.1, 128, 1), 1, 32, 1, 1, None),
        ((128, 4, 0.2, 192, 1), 1, 32, 1, 1, None),
        ((128, 4, 0.2, 192, 2), 32, 32, 1, 1, None),
        ((128, 4, 0.2, 192, 3), 4, 32, 2, 3, None),
        ((64, 5, 0.3, 300, 4), 3, 7, 2, 2, None),
        ((80, 4, 0.4, 700, 5), 32, 32, 1, 4, None),
        ((200, 3, 0.3, 500, 6), 2, 16, 3, 1, None),
        ((128, 4, 0.3, 400, 7), 8, 32, 1, 2, (192, 40)),
    ]
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for ci, (inst, nsh, mps, bpm, nsl, two) in enumerate(cases):
            n, k, eta, m, seed = inst
            ms = two[0] if two else m
            base = td / f"p{ci}.bin"
            args = [sys.executable, HERE / "planner.py", "plan", "--n", n, "--k", k, "--m", ms, "--shires", nsh,
                    "--mps", mps, "--blocks-per-minion", bpm, "--slices", nsl, "--out", base, "--compact"]
            if two:
                args += ["--tau1", two[1]]
            summ = json.loads(run(args))
            files = [f["file"] for f in summ["files"]]
            check(f"plan {ci} {inst}: every block within one row tile of its equal share of modelled cycles "
                  f"(error {summ['cut_error_tiles']:.3f} tiles)", summ["cut_error_tiles"] <= 1.0 + 1e-9)
            outs = []
            extra = kv(m1=two[0], tau1=two[1]) if two else []
            for f in files:
                o = f + ".out"
                r = jrun([B / "spref", "scan", *kv(n=n, k=k, eta=eta, m=m, seed=seed, plan=f, out=o,
                                                    threads=a.threads), *extra])
                check(f"plan {ci} {inst} slice {Path(f).name}: spref's per-range ops and candidates = the planner's",
                      r["plan"]["ranges_match"] == 1)
                outs.append(o)
            margs = [sys.executable, HERE / "planner.py", "merge", "--inst", ",".join(map(str, inst)), "--compact"]
            for f, o in zip(files, outs):
                margs += ["--plan", f, "--out", o]
            rep = json.loads(run(margs, ok_codes=(0, 1)))
            full = jrun([B / "spref", "scan", *kv(n=n, k=k, eta=eta, m=ms, seed=seed, threads=a.threads)])["result"]
            same = (rep.get("best", {}).get("c") == full["best_c"] and rep["best"]["j"] == full["best_j"]
                    and rep["best"]["row"] == full["best_row"] and rep["top"] == full["top"]
                    and rep["sum_c"] == full["sum_c"] and rep["sum_c2"] == full["sum_c2"])
            check(f"plan {ci} {inst} {nsh}x{mps} minions, {bpm} blocks, {nsl} slices{' two-stage' if two else ''}: "
                  f"merge ok, coverage complete, closed forms match, = full scan",
                  rep["ok"] and rep["coverage"]["complete"] and rep["closed"]["match"] and same,
                  json.dumps(rep)[:600])
            if ci in (3, 6):   # negative controls on a 1,024-minion plan
                o = Path(outs[0]).read_bytes()
                oh, recs, _ = sc.read_out(o)
                q = next(i for i in range(oh["nminions"]) if recs[2 * i]["cands"] > 0)
                if ci == 3:   # a tie: the best hart's record flags a second candidate at its best c (one launch)
                    bi = next(i for i in range(oh["nminions"])
                              if recs[2 * i]["best_c"] == rep["best"]["c"] and recs[2 * i]["best_j"] == rep["best"]["j"]
                              and recs[2 * i]["best_row"] == rep["best"]["row"])
                    offf = sc.OUT_HDR.size + 64 * (2 * bi) + 6      # the record's flags (uint16 at byte 6)
                    bad = bytearray(o)
                    fl = int.from_bytes(bad[offf:offf + 2], "little") | sc.REC_TIE
                    bad[offf:offf + 2] = fl.to_bytes(2, "little")
                    (td / "tie.out").write_bytes(bytes(bad))
                    rep5 = json.loads(run([x if x != outs[0] else str(td / "tie.out") for x in margs], ok_codes=(0, 1)))
                    check(f"negative control {ci}: a hart that flags a tie makes the answer not unique (the only "
                          f"evidence with --topm 0)", rep5["best"]["unique"] is False and rep5.get("ok_secret") is False
                          and rep5["best"]["harts_flagging_tie"] == 1)
                for off, what in ((32, "sum_c off by 2 fails the closed-form check"),
                                  (24, "best_j off by 2 fails the host's rescoring")):
                    off += sc.OUT_HDR.size + 64 * (2 * q)      # minion q's hart-0 record: sum_c at 32, best_j at 24
                    bad = bytearray(o)
                    L = 8 if what.startswith("sum_c") else 4
                    v = int.from_bytes(bad[off:off + L], "little", signed=True) + 2
                    bad[off:off + L] = v.to_bytes(L, "little", signed=True)
                    (td / "bad.out").write_bytes(bytes(bad))
                    margs2 = [x if x != outs[0] else str(td / "bad.out") for x in margs]
                    rep2 = json.loads(run(margs2, ok_codes=(0, 1)))
                    caught = (rep2["closed"]["match"] is False) if L == 8 else rep2["rescored"]["wrong"] > 0
                    check(f"negative control {ci}: a record's {what}", not rep2["ok"] and caught)
                W = sc.WorkList.from_bytes(Path(files[0]).read_bytes())
                # duplicate: minion q2's first range copied onto the minion after it (both scan it)
                q2 = next(i for i in range(len(W.minions) - 1) if W.minions[i][1] > 0 and W.minions[i + 1][1] > 0)
                r0 = dict(W.ranges[W.minions[q2][0]])
                nxt = W.minions[q2 + 1][0]
                r0["minion"] = q2 + 1
                W.ranges.insert(nxt, r0)
                W.minions = [(f + (1 if i > q2 else 0), c + (1 if i == q2 + 1 else 0), s, mm)
                             for i, (f, c, s, mm) in enumerate(W.minions)]
                W.hdr["total_ops"] += r0["ops"]
                W.hdr["total_cands"] += r0["cands"]
                (td / "dup.bin").write_bytes(W.to_bytes())
                jrun([B / "spref", "scan", *kv(n=n, k=k, eta=eta, m=ms, seed=seed, plan=td / "dup.bin",
                                               out=td / "dup.out", threads=a.threads)], ok_codes=(0, 1))
                margs3 = list(margs)
                i = margs3.index(files[0])
                margs3[i], margs3[i + 2] = str(td / "dup.bin"), str(td / "dup.out")
                rep3 = json.loads(run(margs3, ok_codes=(0, 1)))
                check(f"negative control {ci}: a duplicated range is caught (overlap and checksums)",
                      not rep3["ok"] and rep3["coverage"]["overlaps"] > 0)
                # drop: minion q2 loses its ranges (the plan says so, the scan agrees): coverage has a gap
                W = sc.WorkList.from_bytes(Path(files[0]).read_bytes())
                f0, c0, s0, m0 = W.minions[q2]
                W.minions[q2] = (f0, 0, s0, m0)
                (td / "drop.bin").write_bytes(W.to_bytes())
                jrun([B / "spref", "scan", *kv(n=n, k=k, eta=eta, m=ms, seed=seed, plan=td / "drop.bin",
                                               out=td / "drop.out", threads=a.threads)], ok_codes=(0, 1))
                margs4 = list(margs)
                margs4[i], margs4[i + 2] = str(td / "drop.bin"), str(td / "drop.out")
                rep4 = json.loads(run(margs4, ok_codes=(0, 1)))
                check(f"negative control {ci}: a dropped range leaves a coverage gap and fails",
                      not rep4["ok"] and rep4["coverage"]["gaps"] > 0)


def t_plan_big(B, a):
    """the showcase plans: balance and cut error only (no scan)"""
    P = planner.model_constants()
    for n, k, m, nsl in [(512, 4, 448, 1), (512, 4, 1850, 1), (256, 5, 1925, 1), (512, 5, 1280, 4), (512, 5, 2151, 6)]:
        plans, G, prof = planner.make_plan(n, k, m, 32, 32, 1, nsl, P)
        bal = [planner.balance(W, P) for W in plans]
        cov = sorted((r["tile_begin"], r["tile_end"]) for W in plans for r in W.ranges)
        tiles_ok = cov[0][0] == 0 and cov[-1][1] == G.NT and all(x[1] == y[0] for x, y in zip(cov, cov[1:]))
        cands_ok = sum(W.hdr["total_cands"] for W in plans) == G.Ncand
        check(f"plan (n={n}, k={k}, m={m}) on 32 x 32 minions in {nsl} launch(es): tiles covered once, all C(n,k) "
              f"candidates, cut error {prof.cut_error_tiles:.3f} tiles, minion imbalance "
              f"{max(b['minion_imbalance'] for b in bal):.4f}",
              tiles_ok and cands_ok and prof.cut_error_tiles <= 1.0 + 1e-9 and
              max(b["minion_imbalance"] for b in bal) < 1.01)


def t_base(B, a):
    for n, k, eta, m, seed in [(32, 3, 0.1, 128, 1), (128, 4, 0.2, 192, 1), (128, 4, 0.2, 192, 5),
                               (64, 5, 0.2, 300, 2), (160, 4, 0.4, 1850, 3), (96, 5, 0.4, 1925, 4),
                               (80, 5, 0.4, 2151, 5), (512, 3, 0.3, 448, 6), (120, 4, 0.3, 832, 7)]:
        v = jrun([B / "spbase", "vexh", *kv(n=n, k=k, eta=eta, m=m, seed=seed, threads=a.threads, sums=1)])
        r = jrun([B / "spref", "scan", *kv(n=n, k=k, eta=eta, m=m, seed=seed, threads=a.threads)])
        rr = r["result"]
        same = (v["found"] == rr["found"] and v["best_c"] == rr["best_c"] and v["sum_c"] == rr["sum_c"]
                and v["sum_c2"] == rr["sum_c2"] and v["closed"]["match"] == 1 and v["subsets"] == r["Ncand"]
                and (v["nbest"] == 1) == bool(rr["unique"]))
        check(f"vexh = reference (answer, ties, both checksums = closed forms) {n,k,eta,m,seed}", same,
              f"{v} vs {rr}")
        if rr["ok"]:
            for split in ((0, 1) if k >= 4 else (0,)):
                mm = jrun([B / "spbase", "mitm", *kv(n=n, k=k, eta=eta, m=m, seed=seed, threads=a.threads, maxsec=60,
                                                     split=split)])
                check(f"mitm (split={split}) finds the reference's answer {n,k,eta,m,seed}",
                      mm["found"] == rr["found"] and mm["ok"] == 1, json.dumps(mm))
    # two-stage: survivors and stage 2 agree between the reference and vexh
    for n, k, eta, m, seed, m1, tau in [(128, 4, 0.3, 448, 1, 192, 40), (64, 5, 0.4, 1000, 2, 400, 60),
                                        (160, 4, 0.4, 1850, 3, 832, 80)]:
        r = jrun([B / "spref", "scan", *kv(n=n, k=k, eta=eta, m=m, seed=seed, m1=m1, tau1=tau, threads=a.threads)])
        v = jrun([B / "spbase", "vexh", *kv(n=n, k=k, eta=eta, m=m1, seed=seed, tau=tau, m2=m, threads=a.threads)])
        check(f"two-stage: survivors, secret kept, stage-2 answer: reference = vexh {n,k,eta,m,seed,m1,tau}",
              r["survivors"] == v["survivors"] and r["secret_survived"] == v["secret_survived"]
              and r["result"]["found"] == v["stage2_found"] and r["result"]["best_c"] == v["stage2_best_c"],
              f"{r['survivors']} {v['survivors']} {r['result']['found']} {v['stage2_found']}")
    for eta, cnt in ((0.1, 24), (0.3, 21)):   # 21: a group of 8 with padding lanes; eta 0.3: some unsolved (ties)
        ref_ok = sum(jrun([B / "spref", "scan", *kv(n=64, k=4, eta=eta, m=64, seed=s, cf=0)])["result"]["ok"]
                     for s in range(1, cnt + 1))
        for lanes in (1, 0):
            b = jrun([B / "spbase", "batch", *kv(n=64, k=4, eta=eta, m=64, seed=1, count=cnt, threads=a.threads,
                                                 lanes=lanes)])
            check(f"batch lanes={lanes} (B1 shape, eta {eta}, {cnt} instances) solves exactly what the reference "
                  f"solves", b["solved"] == ref_ok, f"{b['solved']} vs {ref_ok}")


def t_card(B, a):
    inst = planner.parse_inst(a.inst)
    n, k, eta, m, seed = inst
    pairs, expect = [], []
    with tempfile.TemporaryDirectory() as td:
        for i, (p, o) in enumerate(zip(a.plan, a.out)):
            W = sc.WorkList.from_bytes(Path(p).read_bytes())
            ref = Path(td) / f"ref{i}.out"
            extra = kv(m1=a.m1, tau1=a.tau1) if a.m1 else []
            jrun([B / "spref", "scan", *kv(n=n, k=k, eta=eta, m=m, seed=seed, plan=p, out=ref, threads=a.threads),
                  *extra], ok_codes=(0, 1))
            pairs.append((W, sc.read_out(Path(o).read_bytes())))
            expect.append(sc.read_out(ref.read_bytes()))
        rep = planner.merge(pairs, inst, expect, check_hart1=not a.no_hart1, partial=a.partial)
    print(json.dumps(rep, indent=1))
    check("card output = reference, hart by hart, and the merge's checks", rep["ok"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("groups", nargs="*", default=["gen", "closed", "ref", "plan", "planbig", "base"])
    ap.add_argument("--bin", default=os.environ.get("SP_BIN", str(HERE.parent / "cpu")),
                    help="directory with spref and spbase")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--spbits", default=None, help="proto/spbits binary, to check the generator against SP3's")
    ap.add_argument("--plan", action="append", default=[])
    ap.add_argument("--out", action="append", default=[])
    ap.add_argument("--inst", default=None)
    ap.add_argument("--m1", type=int, default=0)
    ap.add_argument("--tau1", type=int, default=0)
    ap.add_argument("--no-hart1", action="store_true")
    ap.add_argument("--partial", action="store_true", help="card: the plans are a subset of the slices")
    a = ap.parse_args()
    B = Path(a.bin).resolve()
    fns = dict(gen=t_gen, closed=t_closed, ref=t_ref, plan=t_plan, planbig=t_plan_big, base=t_base, card=t_card)
    for g in a.groups:
        fns[g](B, a)
    print(f"{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED'}")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
