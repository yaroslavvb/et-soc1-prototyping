#!/usr/bin/env python3
"""The counter against what sparse parity's kernel reports about itself, run by run.

    validate_sparseparity.py --dis sparseparity.dis --sites sites-addr2line.txt --run RUNDIR [--run RUNDIR ...]
                             [--all-sites all-addr2line.txt.gz] [--count-line sparseparity.c:324] [--out validation.json]

Each RUNDIR holds one `sparseparity_host --sysemu` run in the profiling simulator: out.json (the host's JSON line),
records.bin (`--records-out`: one 64 B SppRecord per hart, workloads/sparseparity/sparseparity_args.h) and
counts-log.json (count_kernel.py count --log, every hart of the minions that worked). --sites is the ET toolchain's
`addr2line -f -i -a` for every tensor_fma, tensor_load, amoswapl.d and amoorl.d address, run on the same kernel
built with -g (its .text is byte-identical to the run's; README.md says how): it tells each site's source line and
inline chain. The checks, per minion that worked (desk checks of code):

  T1  TensorIMA8A32 starts at sites whose inline chain has no `recompute` = hart 0's record `work` (the kernel's
      own op count, c->ops += S)
  T2  starts inside `recompute` (a tile that may hold a new best, recomputed and rescanned: M1's epilogue or the
      deferred `rescans`): ops the kernel does not count in `work`; T1 + T2 = every int8 TensorFMA the counter saw
  T3  TensorLoads into TenB = int8 TensorFMAs (every op is paired with its B load)
  T4  MACs = 16 x 64 x 16 per int8 op
  G1  hart 1's l2_write sites in the generator (run_gen_inc / run_gen, not signal_abort: one publish per row tile)
      = hart 1's record `count` (row tiles generated)
  G2  hart 1's l2_read sites inside wait_count in the generator (the polls of the buffer line) - hart 1's record
      `wait` (polls that found the buffer still busy) = the successful waits, one per row tile after the first
      `nbuf`: max(0, tiles - nbuf)

Hart 0's record `cycles` (hpmcounter3, which the simulator advances by one per emulated cycle), the counted
instructions and the log's cycle span are reported per minion, not checked.

Scalar mode, two checks: S1 the records against the host (the records' `count`, candidates scored, summed = the
host's candidate count: no counter in it), and S1c the counter against the records (with --all-sites, the addr2line
of every kernel address: each hart's executions at every address of the `++acc->count` line, sparseparity.c:324 in
the 29 Sep kernel's source, = that hart's record `count`). Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import importlib.util
import json
import os
import struct
import sys

REC = struct.Struct("<qQQQiIQQII")   # SppRecord: sum_c sum_c2 count best_rank best_c status cycles wait work copy_cycles


def load_counter():
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("ledger_count_kernel", os.path.join(here, "count_kernel.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def records(path):
    data = open(path, "rb").read()
    out = {}
    for h in range(len(data) // 64):
        f = REC.unpack_from(data, 64 * h)
        out[h] = dict(zip(("sum_c", "sum_c2", "count", "best_rank", "best_c", "status", "cycles", "wait", "work",
                           "copy_cycles"), f))
    return out


def host_json(path):
    lines = [l for l in open(path).read().splitlines() if l.strip().startswith("{")]
    return json.loads(lines[-1])


def read_sites(path):
    """addr2line -f -i -a output: an address line, then (function, file:line) pairs, innermost first."""
    import gzip
    sites, cur = {}, None
    op = gzip.open if path.endswith(".gz") else open
    lines = [l.strip() for l in op(path, "rt").read().splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        if lines[i].startswith("0x"):
            cur = int(lines[i], 16)
            sites[cur] = []
            i += 1
            continue
        if cur is not None and i + 1 < len(lines):
            sites[cur].append((lines[i], lines[i + 1].split("/")[-1]))
            i += 2
            continue
        i += 1
    return sites


def chain_fns(sites, addr):
    return [f for f, loc in sites.get(addr, [])]


def site_counts(per_pc, insns_by_addr, pred):
    n = 0
    for pc, (ex, tk) in per_pc.items():
        ins = insns_by_addr[int(pc, 16)]
        if pred(ins):
            n += ex
    return n


def check_run(ck, insns, run, sites, all_sites=None, count_line="sparseparity.c:324"):
    by_addr = {i.addr: i for i in insns}
    for a in sites:
        by_addr[a].chain = chain_fns(sites, a)
    j = host_json(os.path.join(run, "out.json"))
    rec = records(os.path.join(run, "records.bin"))
    cnt = json.load(open(os.path.join(run, "counts-log.json")))
    mode = j["mode"]
    nbuf = j["plan"].get("nbuf", 2)
    res = {"run": "/".join(os.path.normpath(run).split(os.sep)[-2:]), "mode": mode, "status": j["status"],
           "instance": j["instance"], "plan": {k: j["plan"].get(k) for k in ("shires", "per_shire", "busy_minions",
                                                                             "ops", "ops_max", "slice", "nbuf")},
           "kernel_report": j["kernel"], "variant": j.get("m4", {}).get("variant"), "minions": [], "checks": {}}
    ok = {"T1": True, "T2": True, "T3": True, "T4": True, "G1": True, "G2": True, "S1": True, "S1c": True}
    line_pcs = set()
    if all_sites:
        # the addresses whose innermost source line is the count line (the -g build's .text is the run's)
        line_pcs = set(a for a, ch in all_sites.items() if ch and ch[0][1].split(" ")[0] == count_line)
    tot = {"fma_main": 0, "fma_rescans": 0, "work": 0, "tiles": 0, "gen_publish": 0, "polls_record": 0,
           "poll_loads": 0}
    harts = cnt["harts"]
    for tid_s, h0 in sorted(harts.items(), key=lambda kv: int(kv[0])):
        tid = int(tid_s)
        if tid % 2:
            continue
        r0, r1 = rec.get(tid), rec.get(tid + 1)
        h1 = harts.get(str(tid + 1), {"per_pc": {}, "tensor": {}, "instructions": 0})
        if mode == "tensor":
            work = r0["work"]
            if work == 0 and h0["instructions"] < 100:
                continue          # a minion the plan left idle: in and out of the kernel
            pp0 = h0["per_pc"]
            fma_main = site_counts(pp0, by_addr, lambda i: i.csr == "tensor_fma" and i.csrw and "recompute" not in i.chain)
            fma_res = site_counts(pp0, by_addr, lambda i: i.csr == "tensor_fma" and i.csrw and "recompute" in i.chain)
            t_int8 = h0["tensor"].get("fma_int8", {})
            t_tenb = h0["tensor"].get("load_tenb", {})
            pp1 = h1["per_pc"]
            gen = lambda i: any(f.startswith("run_gen") for f in i.chain)
            publish = site_counts(pp1, by_addr, lambda i: gen(i) and i.chain[:1] == ["l2_write"]
                                  and "signal_abort" not in i.chain)
            polls = site_counts(pp1, by_addr, lambda i: gen(i) and i.chain[:1] == ["l2_read"] and "wait_count" in i.chain)
            tiles = r1["count"]
            m = {"shire": tid // 64, "minion": (tid % 64) // 2,
                 "record_h0": {k: r0[k] for k in ("work", "count", "cycles", "wait", "copy_cycles")},
                 "record_h1": {k: r1[k] for k in ("count", "wait")},
                 "counter": {"fma_int8_main": fma_main, "fma_int8_rescans": fma_res,
                             "fma_int8_total": t_int8.get("ops", 0), "macs": t_int8.get("macs", 0),
                             "tensor_load_tenb": t_tenb.get("ops", 0), "gen_publish": publish, "gen_poll_loads": polls,
                             "instructions_h0": h0["instructions"], "instructions_h1": h1["instructions"],
                             "cycles_span_h0": h0.get("cycles_span"), "killed_h0": h0.get("killed_and_restarted"),
                             "by_class_h0": h0["by_class"], "by_class_h1": h1["by_class"]}}
            m["T1"] = fma_main == work
            m["T2"] = fma_main + fma_res == t_int8.get("ops", 0)
            m["T3"] = t_tenb.get("ops", 0) == t_int8.get("ops", 0)
            m["T4"] = t_int8.get("macs", 0) == 16384 * t_int8.get("ops", 0)
            m["G1"] = publish == tiles
            m["G2"] = polls - r1["wait"] == max(0, tiles - nbuf)
            for k in ("T1", "T2", "T3", "T4", "G1", "G2"):
                ok[k] = ok[k] and m[k]
            tot["fma_main"] += fma_main
            tot["fma_rescans"] += fma_res
            tot["work"] += work
            tot["tiles"] += tiles
            tot["gen_publish"] += publish
            tot["polls_record"] += r1["wait"]
            tot["poll_loads"] += polls
            res["minions"].append(m)
        else:
            if r0["count"] == 0 and h0["instructions"] < 100:
                continue
            m = {"shire": tid // 64, "minion": (tid % 64) // 2,
                 "record_h0": {k: r0[k] for k in ("work", "count", "cycles")},
                 "counter": {"instructions_h0": h0["instructions"], "by_class_h0": h0["by_class"],
                             "cycles_span_h0": h0.get("cycles_span")}}
            if line_pcs:
                for t, hh, rr in ((tid, h0, r0), (tid + 1, harts.get(str(tid + 1)), r1)):
                    if hh is None or rr is None or rr["count"] == 0:
                        continue
                    ex = [hh["per_pc"].get(f"0x{a:x}", [0, 0])[0] for a in sorted(line_pcs)]
                    m.setdefault("S1c", {})[str(t)] = {"record_count": rr["count"], "executions_at_count_line": ex,
                                                       "pass": bool(ex) and all(e == rr["count"] for e in ex)}
                    ok["S1c"] = ok["S1c"] and m["S1c"][str(t)]["pass"]
            res["minions"].append(m)
    if mode == "tensor":
        res["totals"] = tot
        res["totals"]["plan_ops"] = j["plan"]["ops"]
        res["checks"] = {k: ok[k] for k in ("T1", "T2", "T3", "T4", "G1", "G2")}
        res["checks"]["T1_plan"] = tot["work"] == j["plan"]["ops"] and tot["fma_main"] == j["plan"]["ops"]
    else:
        scored = sum(rec[t]["count"] for t in rec)
        res["checks"] = {"S1": scored == j["result"]["count"]}
        res["totals"] = {"candidates_records": scored, "candidates_host": j["result"]["count"]}
        if line_pcs:
            res["checks"]["S1c"] = ok["S1c"] and any("S1c" in m for m in res["minions"])
            res["totals"]["count_line"] = count_line
            res["totals"]["count_line_addresses"] = [f"0x{a:x}" for a in sorted(line_pcs)]
    res["all_pass"] = all(res["checks"].values())
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dis", required=True)
    ap.add_argument("--sites", required=True)
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--all-sites", default="", help="addr2line of every kernel address (.gz ok), for S1c")
    ap.add_argument("--count-line", default="sparseparity.c:324", help="the source line of ++acc->count")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    ck = load_counter()
    insns = ck.parse_dis(a.dis)
    sites = read_sites(a.sites)
    all_sites = read_sites(a.all_sites) if a.all_sites else None
    out = {"tool": "tools/counter/validate_sparseparity.py", "dis_sha256": ck.sha256_file(a.dis),
           "sites_sha256": ck.sha256_file(a.sites), "runs": []}
    if a.all_sites:
        out["all_sites_sha256"] = ck.sha256_file(a.all_sites)
    for run in a.run:
        r = check_run(ck, insns, run, sites, all_sites, a.count_line)
        out["runs"].append(r)
        t = r.get("totals", {})
        print(f"{r['run']:16s} {r['mode']:6s} minions {len(r['minions']):3d} checks "
              + " ".join(f"{k}={'PASS' if v else 'FAIL'}" for k, v in r["checks"].items())
              + f"  totals {json.dumps(t)}")
    out["all_pass"] = all(r["all_pass"] for r in out["runs"])
    if a.out:
        with open(a.out, "w") as f:
            json.dump(out, f, indent=1)
            f.write("\n")
    print("VALIDATE:", "ALL PASS" if out["all_pass"] else "SOME FAIL")
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
