#!/usr/bin/env python3
"""v31-trace (Q217) THE CHECK: one traced run's summary (trace_run.py) against the walk (walk/walk_v31.py), hart by hart and event by event.
Desk (aifoundry2); standard library only; /usr/bin/python3 3.12.3.

    python3 -I -B check_v31.py --summary RUN/summary.json.gz --kernel rgm136.gemmL --shape 2x4x16 --mask 0xf [--fmt fp32] --out CHECK.json

WHAT IS COMPARED (every logged hart):
  - which harts work: a logged hart of a shire outside the mask must retire no U-mode instruction; hart 1 of an active minion no U-mode tensor
    operation; hart 0 of an active minion the walk's whole event list.
  - each working hart's tensor operations in program order (the simulator's Start lines, U-mode) as canonical tuples with pool-relative
    offsets, against walk_v31.minion_events: equal, or the first difference and the number of differing positions; the pools' bases are
    read once from the trace (one base per pool for the whole run: each A, B and C address less the walk's offset must give one value).
  - fields the canonical tuple leaves out, checked separately: TensorLoad msk 0, cmd 0, boffset 0; TenB loads start 0; TensorStore regstart 0,
    srcinc 1, coop 1; TensorFMA msk 0, bcols/arows/acols 16 (fp32), aoffset 0, tenb 1, bstart 0; the coop leader neighbourhood (the
    simulator's coop_tload_leader_neigh: A's group is its own neighbourhood, so dim1; B's (all four) by address bits 7:6 of a 1 KiB-aligned
    tile, so 0).
  - the lines each load read and each store wrote (the simulator's MEM512 / MEM128 lines): 16 per load, 64 per store (16 rows x 4), every
    one at addr + i x stride, and the physical-minus-virtual offsets.
  - the shire's requests: per active shire, the distinct A and B tiles its traced minions read at each op step, against the walk's shire stream
    (complete when the traced minions cover every neighbourhood (dim1) and every position (dim0)); the chip's sharing per step (which active
    shires read each tile) against the walk's chip steps.
  - the simulator's own interleaving: per op index, the spread of the steps at which the traced harts started it (sys_emu's lock step; the
    walk's chip model assumes lock step; neither is the card's time).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import gzip
import json
import os
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "walk"))
import walk_v31 as W  # noqa: E402

FMA_NAME = {"fp32": "TensorFMA32", "fp16": "TensorFMA16A32", "int8": "TensorIMA8A32"}
ACOLS = {"fp32": 16, "fp16": 32, "int8": 64}


def load(path):
    with gzip.open(path, "rt") as g:
        return json.load(g)


def canon(ev, base, side):
    """a trace event (trace_run.py's list) -> (canonical tuple, side-field problems)"""
    k = ev[0]
    probs = []
    if k == "LA":
        _, step, addr, start, coop, tcoop, rows, stride, idd, msk, cmd, boff, leader = ev
        if msk or cmd or boff:
            probs.append("LA msk/cmd/boffset %s/%s/%s" % (msk, cmd, boff))
        side["leaderA"][leader] += 1
        return ("LA", addr - base["A"], start, coop, tcoop, rows, stride, idd), probs
    if k == "LB":
        _, step, addr, start, coop, tcoop, rows, stride, idd, msk, cmd, boff, leader = ev
        if start or msk or cmd or boff:
            probs.append("LB start/msk/cmd/boffset %s/%s/%s/%s" % (start, msk, cmd, boff))
        side["leaderB"][leader] += 1
        return ("LB", addr - base["B"], coop, tcoop, rows, stride, idd), probs
    if k == "S":
        _, step, addr, stride, rows, cols, regstart, srcinc, coop = ev
        if regstart != 0 or srcinc != 1 or coop != 1:
            probs.append("S regstart/srcinc/coop %s/%s/%s" % (regstart, srcinc, coop))
        return ("S", addr - base["C"], rows, cols, stride), probs
    if k == "F":
        _, step, name, msk, bcols, arows, acols, aoff, tenb, bstart, astart, mul, dst = ev
        fmt = side["fmt"]
        if name != FMA_NAME[fmt] or msk or bcols != 16 or arows != 16 or acols != ACOLS[fmt] or aoff or tenb != 1 or bstart:
            probs.append("F fields %s" % ev[2:12])
        return ("F", astart, mul, dst), probs
    return (k,) + tuple(str(x) for x in ev[2:]), ["unexpected tensor op %s" % k]


def walk_offsets(kernel, MB, NB, KB, shire, minion, fmt):
    ev = list(W.minion_events(kernel, MB, NB, KB, shire, minion, fmt=fmt))
    return ev


def bases_from(summary, kernel, MB, NB, KB, fmt):
    """one base per pool: every traced address less the walk's offset at the same position (first 64 events of each working hart)"""
    cand = {"A": collections.Counter(), "B": collections.Counter(), "C": collections.Counter()}
    for hs, v in summary["harts"].items():
        h = int(hs)
        s, m, t = h // 64, (h % 64) // 2, h % 2
        if t != 0 or not v["events"]:
            continue
        wev = walk_offsets(kernel, MB, NB, KB, s, m, fmt)
        tev = [e for e in v["events"] if e[0] in ("LA", "LB", "S", "F")]
        for we, te in zip(wev[:4000], tev[:4000]):
            if we[0] != te[0]:
                continue
            if we[0] == "LA":
                cand["A"][te[2] - we[1]] += 1
            elif we[0] == "LB":
                cand["B"][te[2] - we[1]] += 1
            elif we[0] == "S":
                cand["C"][te[2] - we[1]] += 1
    base = {k: (c.most_common(1)[0][0] if c else 0) for k, c in cand.items()}
    agree = {k: (c.most_common(1)[0][1] / sum(c.values()) if c else None) for k, c in cand.items()}
    return base, agree, {k: len(c) for k, c in cand.items()}


def check(summary, kernel, shape, mask, fmt):
    MB, NB, KB = W.parse_shape(shape)
    sh = set(W.mask_shires(mask))
    base, agree, ncand = bases_from(summary, kernel, MB, NB, KB, fmt)
    side_all = {"leaderA": collections.Counter(), "leaderB": collections.Counter(), "fmt": fmt}
    per_hart = {}
    exact_harts = diff_harts = 0
    total_diff_positions = 0
    probs_all = collections.Counter()
    lines_ok = True
    starts_by_op = collections.defaultdict(list)    # op index -> steps (A load start) of traced working harts
    shire_tiles = collections.defaultdict(lambda: collections.defaultdict(lambda: (set(), set())))   # shire -> op -> (A set, B set)
    covered = collections.defaultdict(lambda: (set(), set()))   # shire -> (dim1 seen, dim0 seen)
    # the harts sys_emu was asked to log (-ls); a hart outside it can leave a stray line (sys_emu prints 'Instruction killed and will be
    # restarted' for some unlogged harts): it is not traced and is reported apart
    selected = None
    for x in summary.get("meta", {}).get("log_sel") or []:
        sh_, msk_ = x.split(",")
        selected = (selected or set()) | {64 * int(sh_) + t for t in range(64) if (int(msk_, 16) >> t) & 1}
    stray = {}
    for hs, v in sorted(summary["harts"].items(), key=lambda x: int(x[0])):
        h = int(hs)
        s, m, t = h // 64, (h % 64) // 2, h % 2
        if selected is not None and h not in selected:
            stray[hs] = {"instr_by_mode": v["instr_by_mode"], "killed_lines": v["killed"], "n_events": v["n_events"]}
            continue
        rec = {"shire": s, "minion": m, "thread": t, "instr_by_mode": v["instr_by_mode"], "outside_tensor": v["outside_tensor"]}
        if s not in sh:
            rec["expect"] = "never launched: no U-mode instruction"
            rec["ok"] = v["instr_by_mode"].get("U", 0) == 0 and v["n_events"] == 0
        elif t == 1:
            rec["expect"] = "enter and return: no U-mode tensor operation"
            rec["ok"] = v["n_events"] == 0
            rec["u_instructions"] = v["instr_by_mode"].get("U", 0)
        else:
            wev = walk_offsets(kernel, MB, NB, KB, s, m, fmt)
            side = {"leaderA": collections.Counter(), "leaderB": collections.Counter(), "fmt": fmt}
            tev, probs = [], []
            for e in v["events"]:
                c, p = canon(e, base, side)
                tev.append(c)
                probs.extend(p)
            for p in probs:
                probs_all[p.split(" ")[0] + " " + p.split(" ")[1]] += 1
            side_all["leaderA"].update(side["leaderA"])
            side_all["leaderB"].update(side["leaderB"])
            c = W.coords(s, m)
            exp_leader_a = {c["dim1"]: sum(1 for e in wev if e[0] == "LA")} if W.KERNELS[kernel]["coop"] else {None: sum(1 for e in wev if e[0] == "LA")}
            # B's group spans the four neighbourhoods: the simulator picks the leader by bits 7:6 of the address (1 KiB tiles: the pool base's)
            exp_leader_b = ({(base["B"] >> 6) & 3: sum(1 for e in wev if e[0] == "LB")} if W.KERNELS[kernel]["coop"]
                            else {None: sum(1 for e in wev if e[0] == "LB")})
            leader_ok = dict(side["leaderA"]) == exp_leader_a and dict(side["leaderB"]) == exp_leader_b
            equal = tev == [tuple(x) for x in wev]
            ndiff, first = 0, None
            if not equal:
                n = max(len(tev), len(wev))
                for i in range(n):
                    a = tev[i] if i < len(tev) else None
                    b = tuple(wev[i]) if i < len(wev) else None
                    if a != b:
                        ndiff += 1
                        if first is None:
                            first = {"index": i, "trace": a, "walk": b}
            nl = sum(1 for e in tev if e[0] in ("LA", "LB"))
            ns = sum(1 for e in tev if e[0] == "S")
            lok = (v["lines_read"] == 16 * nl and v["lines_written"] == 64 * ns and v["line_mismatch"] == 0
                   and v["exec_vs_start_mismatch"] == 0 and v["starts_never_executed"] == 0 and len(v["pa_minus_va"]) <= 1
                   and v["exec_loads"] == nl and v["exec_stores"] == ns)
            lines_ok &= lok
            rec.update({"expect": "the walk's events", "n_trace": len(tev), "n_walk": len(wev), "equal": equal, "n_diff_positions": ndiff,
                        "first_diff": first, "counts_trace": dict(collections.Counter(e[0] for e in tev)),
                        "counts_walk": dict(collections.Counter(e[0] for e in wev)), "side_field_problems": len(probs),
                        "leader_ok": leader_ok, "leaderA": {str(k): x for k, x in side["leaderA"].items()},
                        "leaderB": {str(k): x for k, x in side["leaderB"].items()},
                        "lines_read": v["lines_read"], "lines_written": v["lines_written"], "line_mismatch": v["line_mismatch"],
                        "pa_minus_va": v["pa_minus_va"], "lines_ok": lok, "walk_sha256": W.events_sha(wev),
                        "trace_sha256": W.events_sha(tev)})
            rec["ok"] = equal and not probs and lok and leader_ok
            exact_harts += equal
            diff_harts += not equal
            total_diff_positions += ndiff
            # op-indexed views for the shire and chip checks and the interleaving
            op = 0
            for e in v["events"]:
                if e[0] == "LA":
                    starts_by_op[op].append(e[1])
                    shire_tiles[s][op][0].add(e[2] - base["A"])
                elif e[0] == "LB":
                    shire_tiles[s][op][1].add(e[2] - base["B"])
                elif e[0] == "F":
                    op += 1
            covered[s][0].add(c["dim1"])
            covered[s][1].add(c["dim0"])
        per_hart[hs] = rec
    # the shire's requests against the walk's stream (where coverage is complete: every dim1 and every dim0 traced)
    shire_res = {}
    for s in sorted(shire_tiles):
        full = covered[s][0] == {0, 1, 2, 3} and covered[s][1] == set(range(8))
        stream = list(W.shire_step_requests(kernel, MB, NB, KB, s))
        bad = 0
        partial_bad = 0
        for i, (_, A, B) in enumerate(stream):
            ta, tb = shire_tiles[s][i] if i in shire_tiles[s] else (set(), set())
            wa, wb = {a for a, _ in A}, {b for b, _ in B}
            if full:
                bad += not (ta == wa and tb == wb)
            else:
                partial_bad += not (ta <= wa and tb <= wb)
        shire_res[str(s)] = {"coverage_complete": full, "dim1_traced": sorted(covered[s][0]), "dim0_traced": sorted(covered[s][1]),
                             "op_steps": len(stream), "steps_unequal": bad if full else None,
                             "steps_with_tile_outside_walk": partial_bad if not full else None}
    # the chip's sharing per step: which shires read each tile (from the traced shires), against the walk's chip steps
    chip_bad, chip_steps_n = 0, 0
    if shire_res and all(v["coverage_complete"] for v in shire_res.values()) and set(int(x) for x in shire_res) == sh:
        i = 0
        for st in W.chip_steps(kernel, MB, NB, KB, mask):
            if st[0] != "op":
                continue
            wantA = {t: set(w) for t, w in st[2]}
            wantB = {t: set(w) for t, w in st[3]}
            gotA, gotB = collections.defaultdict(set), collections.defaultdict(set)
            for s in sh:
                ta, tb = shire_tiles[s].get(i, (set(), set()))
                for a in ta:
                    gotA[a >> 10].add(s)
                for b in tb:
                    gotB[((1 << 32) + b) >> 10].add(s)
            chip_bad += not (dict(gotA) == wantA and dict(gotB) == wantB)
            chip_steps_n += 1
            i += 1
        chip = {"checked": True, "op_steps": chip_steps_n, "steps_unequal": chip_bad}
    else:
        chip = {"checked": False, "why": "not every active shire traced with complete coverage"}
    # sys_emu's interleaving
    spreads = [max(v) - min(v) for k, v in starts_by_op.items() if len(v) > 1]
    inter = {"ops": len(spreads)}
    if spreads:
        firsts = sorted((min(v), k) for k, v in starts_by_op.items())
        inter.update({"spread_steps_median": statistics.median(spreads), "spread_steps_max": max(spreads),
                      "ops_out_of_order_across_harts": sum(1 for k in starts_by_op if k > 0 and k - 1 in starts_by_op
                                                           and min(starts_by_op[k]) < max(starts_by_op[k - 1])),
                      "first_op_step": firsts[0][0], "last_op_step": firsts[-1][0]})
    # the host's own records (SPARSITY lines): ops a minion, participating minions, the walk tag (rgm211's host), the check of C
    host = {"present": False}
    sp = summary.get("meta", {}).get("sparsity") or []
    fma = [x for x in sp if x.get("test") == "fma"]
    chk = [x for x in sp if x.get("test") == "check"]
    if fma:
        x = fma[-1]
        host = {"present": True, "iters_ops_a_minion": x.get("iters"), "walk_ops_a_minion": 64 * MB * NB * KB, "minions": x.get("minions"),
                "walk_minions": 32 * len(sh), "walk_tag": x.get("walk"), "walk_tagged": x.get("walk_tagged"), "walk_ok": x.get("walk_ok"),
                "ok": x.get("ok"), "check": (chk[-1].get("result") if chk else None), "check_ok": (chk[-1].get("ok") if chk else None),
                "cycles_per_op_sim_steps": x.get("cycles_per_op")}
        want_tag = None if x.get("walk") is None else ("nm" if W.KERNELS[kernel]["walk"] == "nm" else "mn")
        host["agrees"] = (x.get("iters") == 64 * MB * NB * KB and x.get("minions") == 32 * len(sh) and x.get("ok") is True
                          and (want_tag is None or x.get("walk") == want_tag) and (not chk or chk[-1].get("ok") is True))
    working = [r for r in per_hart.values() if r.get("expect") == "the walk's events"]
    verdict = "EXACT" if (working and all(r["ok"] for r in per_hart.values()) and lines_ok
                          and all(v["coverage_complete"] is False or v["steps_unequal"] == 0 for v in shire_res.values())
                          and (not chip["checked"] or chip["steps_unequal"] == 0)
                          and (not host["present"] or host["agrees"])) else "DIFFERS"
    return {"kernel": kernel, "shape": shape, "mask": mask, "fmt": fmt, "verdict": verdict, "bases": {k: hex(v) for k, v in base.items()},
            "base_agreement": agree, "base_candidates": ncand, "working_harts_traced": len(working), "exact_harts": exact_harts,
            "diff_harts": diff_harts, "diff_positions_total": total_diff_positions, "side_field_problems": dict(probs_all),
            "lines_ok": lines_ok, "leaderA_all": {str(k): v for k, v in side_all["leaderA"].items()},
            "leaderB_all": {str(k): v for k, v in side_all["leaderB"].items()}, "shires": shire_res, "chip_sharing": chip,
            "sysemu_interleaving": inter, "host_records": host,
            "selected_harts": (len(selected) if selected is not None else None),
            "selected_harts_missing_from_log": (sorted(selected - set(int(x) for x in summary["harts"])) if selected is not None else None),
            "stray_unselected_harts": {"n": len(stray), "with_instructions": sum(1 for v in stray.values() if v["instr_by_mode"]),
                                       "with_tensor_events": sum(1 for v in stray.values() if v["n_events"]),
                                       "killed_lines": sum(v["killed_lines"] for v in stray.values())},
            "per_hart": per_hart,
            "summary_meta": {k: summary["meta"].get(k) for k in ("name", "arm", "mask", "host_rc", "host_wall_s", "reader_error",
                                                                   "peak_rss_kb_sum_of_sim_tree", "log_sel", "sim_args", "elf_sha256",
                                                                   "host_sha256", "python")},
            "log_lines": summary["log_lines"], "log_bytes": summary["log_bytes"], "warn": summary["warn"],
            "unparsed_tensor": summary["unparsed_tensor"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--summary", required=True)
    ap.add_argument("--kernel", required=True, choices=sorted(W.KERNELS))
    ap.add_argument("--shape", required=True)
    ap.add_argument("--mask", required=True)
    ap.add_argument("--fmt", default="fp32")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = check(load(a.summary), a.kernel, a.shape, a.mask, a.fmt)
    json.dump(res, open(a.out, "w"), indent=1, default=str)
    short = {k: res[k] for k in ("kernel", "shape", "mask", "verdict", "bases", "base_agreement", "working_harts_traced", "exact_harts",
                                 "diff_harts", "diff_positions_total", "side_field_problems", "lines_ok", "chip_sharing",
                                 "sysemu_interleaving", "host_records", "selected_harts", "selected_harts_missing_from_log",
                                 "stray_unselected_harts", "log_lines", "log_bytes", "warn")}
    short["shires"] = {s: {kk: vv for kk, vv in v.items() if kk in ("coverage_complete", "steps_unequal")} for s, v in res["shires"].items()}
    bad = [h for h, r in res["per_hart"].items() if not r["ok"]]
    short["harts_not_ok"] = bad[:10]
    if bad:
        short["first_bad"] = res["per_hart"][bad[0]]
        short["first_bad"].pop("instr_by_mode", None)
    print(json.dumps(short, indent=1, default=str))
    return 0 if res["verdict"] == "EXACT" else 1


if __name__ == "__main__":
    sys.exit(main())
