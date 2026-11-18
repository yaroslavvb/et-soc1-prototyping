#!/usr/bin/env python3
"""verify-v31trace (Q217) v04: an INDEPENDENT re-derivation of the traced minions' accesses from v31-trace's trace summaries.

Nothing here imports or copies v31-trace's walk_v31.py, check_v31.py or trace_run.py. Two sides, both written by this lane:
  MODEL  my own transcription of the kernels' C loops (LAB tools/claims-v3/e136/rgm136/kernel/sparsity.c run_gemm_large, and
         tools/claims-v3/e211/rgm211/kernel/sparsity.c run_gemm_large_nm; entry_point's hart -> shire, minion, thread), giving each working
         minion's tensor operations in program order with pool-relative offsets;
  TRACE  my own reading of each summary.json.gz's per-hart event lists (the summarizer's output: U-mode Start lines), with each pool's base
         taken as the MINIMUM address the run's traced harts used for that pool (no walk involved; shire 0 minion 0, which starts every pool
         at offset 0 in the model, is traced in every run).
Per traced working hart it checks: the full event sequence (model == trace, tuple for tuple, in the walk's canonical tuple form so the sha256
can also be compared with v31-trace's FROZEN per-hart sha256 in walk/walk_predictions.json); the registered criteria (b) the ordered load
requests (operand, tile index relative to the operand's base) and (c) request counts by operand; and access counts derived from the trace
alone (decomposing each address into (mb, kb, row, k), (kb, nb, col, k) and (mb, nb, row, col)): loads, stores, FMAs, distinct tiles,
reads per distinct tile, rows and columns touched, the lines the summarizer saw. Also the hart 1s, the off-mask harts and the selection.
Desk; /usr/bin/python3 3.12.3; standard library only. Writes JSON to stdout.
    python3 -I -B v04_independent.py <runs dir> <frozen walk_predictions.json> [run name ...]
"""
import collections
import gzip
import hashlib
import json
import os
import sys

TILE = 1024
ABLK, BBLK, CBLK = 2048 * TILE, 1024 * TILE, 2048 * TILE   # SP_GEMM_MT 64 x KT 32, KT 32 x NT 32, MT 64 x NT 32 tiles of 1 KiB
KT, NT = 32, 32

# run name -> (walk, coop, MB, NB, KB, mask) from the RUN.txt arguments (checked below against the summary's meta)
RUNS = {
    "t1-gemmL-2x4x16-0xf": ("mn", 1, 2, 4, 16, 0xf),
    "t2-gemmL-2x4x16-0x1111": ("mn", 1, 2, 4, 16, 0x1111),
    "t3-gemmLn-2x4x16-0xf": ("nm", 1, 2, 4, 16, 0xf),
    "t4-gemmLn-2x4x16-0x1111": ("nm", 1, 2, 4, 16, 0x1111),
    "t5-gemmLnc-2x4x16-0xf": ("mn", 0, 2, 4, 16, 0xf),
    "t6-gemmLnc-2x4x16-0x1111": ("mn", 0, 2, 4, 16, 0x1111),
    "t7-gemmL-1x1x16-0xf-all": ("mn", 1, 1, 1, 16, 0xf),
    "t8-gemmL-1x1x16-0x1111-all": ("mn", 1, 1, 1, 16, 0x1111),
    "u1": ("mn", 1, 1, 1, 16, 0x1111),   # verify-v31trace's own run (t8's point, every hart of every compute shire logged)
}
FROZEN_KEY = {"u1": "t8-gemmL-1x1x16-0x1111-all"}   # the frozen walk predictions for t8's harts serve u1's (same kernel, shape, mask)
SHOW = {  # minions whose access counts are printed in full (shire, minion), at least two a run
    "t1-gemmL-2x4x16-0xf": [(0, 0), (3, 31), (1, 13)],
    "t2-gemmL-2x4x16-0x1111": [(0, 0), (12, 22), (8, 9)],
    "t3-gemmLn-2x4x16-0xf": [(0, 0), (2, 27)],
    "t4-gemmLn-2x4x16-0x1111": [(4, 4), (12, 31)],
    "t5-gemmLnc-2x4x16-0xf": [(0, 0), (1, 18)],
    "t6-gemmLnc-2x4x16-0x1111": [(8, 13), (12, 31)],
    "t7-gemmL-1x1x16-0xf-all": [(0, 0), (1, 5), (3, 30)],
    "t8-gemmL-1x1x16-0x1111-all": [(4, 1), (12, 26), (8, 15)],
    "u1": [(0, 0), (12, 31), (4, 17), (8, 2)],
}


def model(walk, coop, MB, NB, KB, s, m):
    """my transcription of run_gemm_large (walk mn) / run_gemm_large_nm (walk nm), iters 1, fp32 (no int8 last bit)"""
    dim0, dim1, s0, s1 = m & 7, (m >> 3) & 3, s & 3, (s >> 2) & 7
    row0, col = s1 * 8 + dim1 * 2, s0 * 8 + dim0
    coop_a = (0xFF << 8) | ((1 << dim1) << 16)
    coop_b = (dim0 + 1) | ((1 << dim0) << 8) | (0xF << 16)
    if walk == "mn":
        blocks = [(mb, nb) for mb in range(MB) for nb in range(NB)]
    else:
        blocks = [(mb, nb) for nb in range(NB) for mb in range(MB)]
    ev, op, pending = [], 0, None
    for mb, nb in blocks:
        cb = (mb * NB + nb) * CBLK
        for r in (0, 1):
            row = row0 + r
            for kb in range(KB):
                ab, bb = (mb * KB + kb) * ABLK, (kb * NB + nb) * BBLK
                for k in range(KT):
                    aline = (op & 1) * 16
                    ev.append(("LA", ab + (row * KT + k) * TILE, aline, coop, coop_a if coop else 0, 16, 64, 0))
                    ev.append(("LB", bb + (col * KT + k) * TILE, coop, coop_b if coop else 0, 16, 64, 1))
                    if pending is not None:
                        ev.append(("S", pending, 16, 4, 64))
                        pending = None
                    ev.append(("F", aline, 1 if (kb == 0 and k == 0) else 0, 0))
                    op += 1
            pending = cb + (row * NT + col) * TILE
    ev.append(("S", pending, 16, 4, 64))
    return ev, {"row0": row0, "col": col, "dim0": dim0, "dim1": dim1}


def sha(evs):
    h = hashlib.sha256()
    for e in evs:
        h.update((",".join(str(x) for x in e) + "\n").encode())
    return h.hexdigest()


def trace_tuples(events, base):
    """the trace's events in the same tuple form, from the summary's raw lists, with my bases; plus field problems"""
    out, probs = [], collections.Counter()
    for e in events:
        k = e[0]
        if k in ("LA", "LB"):
            _, step, addr, start, coop, tcoop, rows, stride, idd, msk, cmd, boff, leader = e
            if msk or cmd or boff:
                probs[k + " msk/cmd/boffset"] += 1
            if k == "LA":
                out.append(("LA", addr - base["A"], start, coop, tcoop, rows, stride, idd))
            else:
                if start:
                    probs["LB start"] += 1
                out.append(("LB", addr - base["B"], coop, tcoop, rows, stride, idd))
        elif k == "S":
            _, step, addr, stride, rows, cols, regstart, srcinc, coop = e
            if regstart != 0 or srcinc != 1 or coop != 1:
                probs["S regstart/srcinc/coop"] += 1
            out.append(("S", addr - base["C"], rows, cols, stride))
        elif k == "F":
            _, step, name, msk, bcols, arows, acols, aoff, tenb, bstart, astart, mul, dst = e
            if name != "TensorFMA32" or msk or bcols != 16 or arows != 16 or acols != 16 or aoff or tenb != 1 or bstart:
                probs["F fields"] += 1
            out.append(("F", astart, mul, dst))
        else:
            probs["other tensor op " + str(k)] += 1
            out.append((k,))
    return out, probs


def access_counts(tt, MB, NB, KB, info):
    """counts derived from the trace tuples alone: each address decomposed into the kernel's indices"""
    A, B, C = collections.Counter(), collections.Counter(), collections.Counter()
    rows, cols, bad = set(), set(), collections.Counter()
    seqA, seqB = [], []
    for t in tt:
        if t[0] == "LA":
            off = t[1]
            if off % TILE:
                bad["A not tile aligned"] += 1
            ti = off // TILE
            blk, w = divmod(ti, ABLK // TILE)
            mb, kb = divmod(blk, KB)
            row, k = divmod(w, KT)
            if not (0 <= mb < MB):
                bad["A mb out of range"] += 1
            rows.add(row)
            A[ti] += 1
            seqA.append(ti)
        elif t[0] == "LB":
            off = t[1]
            if off % TILE:
                bad["B not tile aligned"] += 1
            ti = off // TILE
            blk, w = divmod(ti, BBLK // TILE)
            kb, nb = divmod(blk, NB)
            col, k = divmod(w, KT)
            if not (0 <= kb < KB):
                bad["B kb out of range"] += 1
            cols.add(col)
            B[ti] += 1
            seqB.append(ti)
        elif t[0] == "S":
            ti = t[1] // TILE
            blk, w = divmod(ti, CBLK // TILE)
            row, col = divmod(w, NT)
            C[ti] += 1
    nA, nB = sum(A.values()), sum(B.values())
    return {"loads_A": nA, "loads_B": nB, "stores": sum(C.values()), "fmas": sum(1 for t in tt if t[0] == "F"),
            "distinct_A": len(A), "distinct_B": len(B), "distinct_C": len(C),
            "reads_per_A_tile": sorted(collections.Counter(A.values()).items()),
            "reads_per_B_tile": sorted(collections.Counter(B.values()).items()),
            "rows_touched": sorted(rows), "model_rows": [info["row0"], info["row0"] + 1],
            "cols_touched": sorted(cols), "model_col": [info["col"]],
            "closed_form": {"loads_A": 64 * MB * NB * KB, "loads_B": 64 * MB * NB * KB, "fmas": 64 * MB * NB * KB, "stores": 2 * MB * NB,
                            "distinct_A": 64 * MB * KB, "distinct_B": 32 * NB * KB, "distinct_C": 2 * MB * NB,
                            "reads_per_A_tile": NB, "reads_per_B_tile": 2 * MB},
            "decomposition_problems": dict(bad)}, seqA, seqB


def main():
    runs_dir, frozen_path = sys.argv[1], sys.argv[2]
    names = sys.argv[3:] or sorted(RUNS)
    frozen = json.load(open(frozen_path))
    allres = {"frozen_sha256": hashlib.sha256(open(frozen_path, "rb").read()).hexdigest(), "runs": {}}
    for name in names:
        walk, coop, MB, NB, KB, mask = RUNS[name]
        d = os.path.join(runs_dir, name)
        s = json.load(gzip.open(os.path.join(d, "summary.json.gz"), "rt"))
        meta = s["meta"]
        act = [x for x in range(32) if (mask >> x) & 1]
        assert int(meta["mask"], 16) == mask, name
        sel = set()
        for x in meta["log_sel"]:
            sh, mk = x.split(",")
            sel |= {64 * int(sh) + t for t in range(64) if (int(mk, 16) >> t) & 1}
        harts = {int(h): v for h, v in s["harts"].items()}
        work = sorted(h for h in sel if (h // 64) in act and h % 2 == 0)
        # my bases: the minimum address per pool over the traced working harts
        mins = {"A": None, "B": None, "C": None}
        for h in work:
            for e in harts.get(h, {}).get("events", []):
                p = {"LA": "A", "LB": "B", "S": "C"}.get(e[0])
                if p:
                    a = e[2]
                    mins[p] = a if mins[p] is None or a < mins[p] else mins[p]
        fz = frozen["runs"][FROZEN_KEY.get(name, name)]["harts"]
        res = {"bases_min_addr": {k: hex(v) for k, v in mins.items()}, "selected": len(sel), "working_selected": len(work),
               "missing_selected": sorted(h for h in sel if h not in harts)}
        n_eq = n_sha_frozen = n_sha_trace_frozen = n_b = n_c = 0
        tot_ev = tot_lines_r = tot_lines_w = 0
        firstdiff = {}
        probs_all = collections.Counter()
        shows = {}
        for h in work:
            sh_, m = h // 64, (h % 64) // 2
            mev, info = model(walk, coop, MB, NB, KB, sh_, m)
            v = harts.get(h)
            if v is None:
                firstdiff[str(h)] = "selected working hart absent from the log"
                continue
            tt, probs = trace_tuples(v["events"], mins)
            probs_all.update(probs)
            eq = tt == mev
            n_eq += eq
            if not eq and len(firstdiff) < 5:
                i = next((i for i, (a, b) in enumerate(zip(tt, mev)) if a != b), min(len(tt), len(mev)))
                firstdiff[str(h)] = {"index": i, "trace": tt[i] if i < len(tt) else None, "model": mev[i] if i < len(mev) else None,
                                     "n_trace": len(tt), "n_model": len(mev)}
            ms, ts, fsha = sha(mev), sha(tt), fz.get(str(h), {}).get("sha256")
            n_sha_frozen += ms == fsha
            n_sha_trace_frozen += ts == fsha
            # (b) ordered load requests (operand, tile index rel. to the operand base) and (c) counts by operand
            reqT = [("A" if t[0] == "LA" else "B", t[1] // TILE) for t in tt if t[0] in ("LA", "LB")]
            reqM = [("A" if t[0] == "LA" else "B", t[1] // TILE) for t in mev if t[0] in ("LA", "LB")]
            n_b += reqT == reqM
            n_c += collections.Counter(x[0] for x in reqT) == collections.Counter(x[0] for x in reqM)
            tot_ev += len(tt)
            tot_lines_r += v["lines_read"]
            tot_lines_w += v["lines_written"]
            if (sh_, m) in SHOW[name]:
                ac, seqA, seqB = access_counts(tt, MB, NB, KB, info)
                ac.update({"hart": h, "shire": sh_, "minion": m, "events_trace": len(tt), "events_model": len(mev), "sequence_equal": eq,
                           "sha_model": ms[:16], "sha_trace": ts[:16], "sha_frozen": (fsha or "")[:16],
                           "lines_read_summarizer": v["lines_read"], "lines_written_summarizer": v["lines_written"],
                           "lines_read_expected": 16 * (ac["loads_A"] + ac["loads_B"]), "lines_written_expected": 64 * ac["stores"],
                           "line_mismatch": v["line_mismatch"], "pa_minus_va": v["pa_minus_va"], "killed_lines": v["killed"],
                           "outside_tensor_ops": v["outside_tensor"], "outside_lines": v["outside_lines"],
                           "instr_by_mode": v["instr_by_mode"], "first_A_tiles": seqA[:6], "first_B_tiles": seqB[:6]})
                shows["%d/%d" % (sh_, m)] = ac
        # the hart 1s and the off-mask harts
        h1 = [h for h in sel if (h // 64) in act and h % 2 == 1]
        h1_tensor = sum(1 for h in h1 if harts.get(h, {}).get("n_events", 0))
        h1_u = sorted({harts.get(h, {}).get("instr_by_mode", {}).get("U", 0) for h in h1})
        off = [h for h in sel if (h // 64) not in act]
        off_u = {str(h): harts.get(h, {}).get("instr_by_mode") for h in off}
        per_shire_sel = collections.Counter(h // 64 for h in sel)
        res.update({"working_traced_equal_model": n_eq, "model_sha_eq_frozen": n_sha_frozen, "trace_sha_eq_frozen": n_sha_trace_frozen,
                    "criterion_b_equal": n_b, "criterion_c_equal": n_c, "events_compared": tot_ev,
                    "lines_read_summarizer": tot_lines_r, "lines_written_summarizer": tot_lines_w,
                    "first_differences": firstdiff, "field_problems": dict(probs_all),
                    "hart1_selected": len(h1), "hart1_with_tensor_events": h1_tensor, "hart1_U_instr_values": h1_u,
                    "offmask_selected": len(off), "offmask_instr": off_u,
                    "harts_selected_per_shire": {str(k): v for k, v in sorted(per_shire_sel.items())},
                    "minimum_log_set_i": all(per_shire_sel.get(x, 0) == 64 for x in act),
                    "minimum_log_set_ii_inactive_shires_full": [k for k, v in per_shire_sel.items() if k not in act and v == 64],
                    "shown_minions": shows})
        allres["runs"][name] = res
        del s, harts
    json.dump(allres, sys.stdout, indent=1, default=str)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
