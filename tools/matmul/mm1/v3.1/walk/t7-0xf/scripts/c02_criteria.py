#!/usr/bin/env python3
"""t7-0xf (Q221) c02: MM1-v3.1's registered T7 trace check (DECLARED-v31.md section 4, d58601fa..., landed 7375bc9c), criteria (a), (b) and
(c), judged at both masks over every traced run, against the walk's predictions AS FROZEN at 05:11:43 PST (walk_predictions.json,
10f2f3da...). This lane's own code: it imports nothing of check_v31.py, trace_run.py or verify-v31trace's scripts; it imports walk_v31.py
(87736da2..., read only) only to get each traced minion's walk sequence for (b), and it first proves that sequence is the frozen one (its
sha256 in the frozen file's form equals the frozen per-hart sha256).

THE RULE'S WORDS (section 4):
  (a) over the logged harts, with a minimum log set. At each mask the traces log at least (i) every hart (all 64) of every shire the mask
      enables and (ii) every hart (all 64) of at least one shire it does not enable. (a) holds when, at both masks, every logged hart 0 of an
      enabled shire issues tensor loads, no logged hart 1 issues one, and no logged hart of a shire outside the mask retires a U-mode
      instruction. A log set below the minimum leaves (a) undecided.
  (b) for every traced minion (hart 0 logged), the ordered sequence of its tensor-load requests (operand, tile index relative to the
      operand's base) over the traced window equals the walk's sequence for that minion: zero mismatches.
  (c) for every traced minion, the request counts by operand equal the walk's.
How it is read here: a 'logged' hart is one the run's sys_emu selection (-ls, meta.log_sel) names; the minimum log set is judged per mask
over every run at that mask (and reported per run too); "issues tensor loads" = at least one U-mode TensorLoad Start line (A or B) in the
summarizer's event list; a hart 1 "issues one" if it has any; "retires a U-mode instruction" = any I(U) line counted by the summarizer
(and, for runs that kept them, by the runner's own independent counters, mine.json.gz). Each pool's base is the minimum address the run's
traced working harts used for it (no walk involved).

    /usr/bin/python3 -I -B c02_criteria.py <runs.json> <frozen walk_predictions.json> <walk dir> > out.json
runs.json: [{"name", "summary", "mine" (or null), "kernel", "shape", "mask", "frozen_key"}, ...]. Desk; standard library.
"""
import collections
import gzip
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
FROZEN_SHA = "10f2f3da0dd543a088830edb67584713e5b66b986faae1d1c0327d041bc2bf57"


def sha_lines(evs):
    h = hashlib.sha256()
    for e in evs:
        h.update((",".join(str(x) for x in e) + "\n").encode())
    return h.hexdigest()


def canon(events, base):
    out = []
    for e in events:
        k = e[0]
        if k == "LA":
            out.append(("LA", e[2] - base["A"], e[3], e[4], e[5], e[6], e[7], e[8]))
        elif k == "LB":
            out.append(("LB", e[2] - base["B"], e[4], e[5], e[6], e[7], e[8]))
        elif k == "S":
            out.append(("S", e[2] - base["C"], e[4], e[5], e[3]))
        elif k == "F":
            out.append(("F", e[10], e[11], e[12]))
        else:
            out.append((k,) + tuple(str(x) for x in e[2:]))
    return out


def loads(seq):
    """(operand, tile index relative to the operand's base) of every tensor-load request, in order"""
    return [("A" if t[0] == "LA" else "B", t[1] // 1024, t[1] % 1024) for t in seq if t[0] in ("LA", "LB")]


def main():
    runs = json.load(open(sys.argv[1]))
    fz_path = sys.argv[2]
    fz_sha = hashlib.sha256(open(fz_path, "rb").read()).hexdigest()
    frozen = json.load(open(fz_path))
    sys.path.insert(0, sys.argv[3])
    import walk_v31 as W  # noqa: E402
    walk_sha = hashlib.sha256(open(os.path.join(sys.argv[3], "walk_v31.py"), "rb").read()).hexdigest()
    res = {"frozen_predictions": {"path_name": os.path.basename(fz_path), "sha256": fz_sha, "equals_registered_10f2f3da": fz_sha == FROZEN_SHA,
                                  "made_pst": frozen.get("made_pst"), "frozen_walk_sha256": frozen.get("walk_sha256")},
           "walk_v31_sha256_used_for_b": walk_sha, "python": sys.version.split()[0], "runs": {}, "masks": {}}
    per_mask = collections.defaultdict(lambda: {"runs": [], "logged": set(), "h0_enabled_logged": 0, "h0_with_loads": 0,
                                                "h1_logged": 0, "h1_with_loads": 0, "h1_with_any_tensor_op": 0, "off_logged": 0,
                                                "off_present_in_log": 0, "off_with_U": 0, "off_with_U_mine": None, "traced_minions": 0,
                                                "b_equal": 0, "c_equal_walk": 0, "c_equal_frozen_counts": 0, "seq_sha_eq_frozen": 0,
                                                "walk_sha_eq_frozen": 0, "b_mismatch_positions": 0})
    for r in runs:
        s = json.load(gzip.open(r["summary"], "rt"))
        meta = s["meta"]
        mask = int(r["mask"], 16)
        assert int(meta["mask"], 16) == mask, (r["name"], meta["mask"])
        act = [x for x in range(32) if (mask >> x) & 1]
        MB, NB, KB = (int(x) for x in r["shape"].split("x"))
        fr = frozen["runs"][r["frozen_key"]]
        assert fr["kernel"] == r["kernel"] and fr["shape"] == r["shape"] and int(fr["mask"], 16) == mask, r["name"]
        fz_h = fr["harts"]
        fz_counts = fr["walk_summary"]["per_minion"]
        logged = set()
        for x in meta["log_sel"]:
            shs, mk = x.split(",")
            logged |= {64 * int(shs) + t for t in range(64) if (int(mk, 16) >> t) & 1}
        harts = {int(h): v for h, v in s["harts"].items()}
        mine = None
        if r.get("mine"):
            mine = json.load(gzip.open(r["mine"], "rt"))
        per_shire = collections.Counter(h // 64 for h in logged)
        h0 = sorted(h for h in logged if (h // 64) in act and h % 2 == 0)
        h1 = sorted(h for h in logged if (h // 64) in act and h % 2 == 1)
        off = sorted(h for h in logged if (h // 64) not in act)
        # (a) statements
        h0_loads = [h for h in h0 if any(e[0] in ("LA", "LB") for e in harts.get(h, {}).get("events", []))]
        h1_loads = [h for h in h1 if any(e[0] in ("LA", "LB") for e in harts.get(h, {}).get("events", []))]
        h1_any = [h for h in h1 if harts.get(h, {}).get("n_events", 0)]
        off_present = [h for h in off if h in harts]
        off_u = [h for h in off if harts.get(h, {}).get("instr_by_mode", {}).get("U", 0)]
        off_u_mine = None
        h1_tensor_mine = h0_loads_mine = None
        if mine is not None:
            off_u_mine = [h for h in off if mine["instr"].get(str(h), {}).get("U", 0)]
            h1_tensor_mine = [h for h in h1 if any(k.startswith("TensorLoad@U") for k in mine["start"].get(str(h), {}))]
            h0_loads_mine = [h for h in h0 if mine["start"].get(str(h), {}).get("TensorLoad@U", 0) > 0]
        # bases: the minimum address per pool over the traced working harts
        base = {"A": None, "B": None, "C": None}
        for h in h0:
            for e in harts.get(h, {}).get("events", []):
                p = {"LA": "A", "LB": "B", "S": "C"}.get(e[0])
                if p and (base[p] is None or e[2] < base[p]):
                    base[p] = e[2]
        # (b), (c) per traced minion
        nb = nc_w = nc_f = n_seq_fz = n_walk_fz = 0
        mism = 0
        first_bad = []
        for h in h0:
            v = harts.get(h)
            if v is None:
                first_bad.append({"hart": h, "why": "traced minion absent from the log"})
                continue
            sh, m = h // 64, (h % 64) // 2
            tseq = canon(v["events"], base)
            wseq = [tuple(x) for x in W.minion_events(r["kernel"], MB, NB, KB, sh, m)]
            fsha = fz_h.get(str(h), {}).get("sha256")
            n_walk_fz += sha_lines(wseq) == fsha
            n_seq_fz += sha_lines(tseq) == fsha
            lt, lw = loads(tseq), loads(wseq)
            ok_b = lt == lw
            nb += ok_b
            if not ok_b:
                mism += sum(1 for a, b in zip(lt, lw) if a != b) + abs(len(lt) - len(lw))
                if len(first_bad) < 5:
                    i = next((i for i, (a, b) in enumerate(zip(lt, lw)) if a != b), min(len(lt), len(lw)))
                    first_bad.append({"hart": h, "index": i, "trace": lt[i] if i < len(lt) else None, "walk": lw[i] if i < len(lw) else None})
            ct = collections.Counter(x[0] for x in lt)
            cw = collections.Counter(x[0] for x in lw)
            nc_w += ct == cw
            nc_f += ct["A"] == fz_counts["load_a"] and ct["B"] == fz_counts["load_b"]
        killed = collections.Counter(harts.get(h, {}).get("killed", 0) for h in logged)
        rr = {"kernel": r["kernel"], "shape": r["shape"], "mask": r["mask"], "frozen_key": r["frozen_key"],
              "summary_sha256": hashlib.sha256(open(r["summary"], "rb").read()).hexdigest(),
              "logged_harts": len(logged), "logged_harts_present_in_log": sum(1 for h in logged if h in harts),
              "logged_per_shire": {str(k): v for k, v in sorted(per_shire.items())},
              "min_log_set_i_all_enabled_shires_full": all(per_shire.get(x, 0) == 64 for x in act),
              "min_log_set_ii_offmask_shires_full": [k for k, v in sorted(per_shire.items()) if k not in act and v == 64],
              "a_hart0_enabled_logged": len(h0), "a_hart0_with_tensor_loads": len(h0_loads),
              "a_hart1_logged": len(h1), "a_hart1_with_tensor_loads": len(h1_loads), "a_hart1_with_any_tensor_op": len(h1_any),
              "a_offmask_logged": len(off), "a_offmask_present_in_log": len(off_present), "a_offmask_with_U_instruction": len(off_u),
              "a_offmask_with_U_instruction_runner_counters": (None if off_u_mine is None else len(off_u_mine)),
              "a_hart1_with_U_TensorLoad_runner_counters": (None if h1_tensor_mine is None else len(h1_tensor_mine)),
              "a_hart0_with_U_TensorLoad_runner_counters": (None if h0_loads_mine is None else len(h0_loads_mine)),
              "bases_min_addr": {k: (hex(v) if v is not None else None) for k, v in base.items()},
              "traced_minions": len(h0), "b_load_sequence_equal_walk": nb, "b_mismatch_positions": mism,
              "c_counts_equal_walk": nc_w, "c_counts_equal_frozen_per_minion": nc_f,
              "full_sequence_sha256_equal_frozen": n_seq_fz, "walk_sequence_sha256_equal_frozen": n_walk_fz,
              "first_problems": first_bad, "killed_lines_per_logged_hart": {str(k): v for k, v in sorted(killed.items())},
              "offmask_instr_M_range": ([min(harts[h]["instr_by_mode"].get("M", 0) for h in off_present),
                                         max(harts[h]["instr_by_mode"].get("M", 0) for h in off_present)] if off_present else None),
              "offmask_instr_S_range": ([min(harts[h]["instr_by_mode"].get("S", 0) for h in off_present),
                                         max(harts[h]["instr_by_mode"].get("S", 0) for h in off_present)] if off_present else None),
              "hart1_U_instr_values": sorted({harts.get(h, {}).get("instr_by_mode", {}).get("U", 0) for h in h1})}
        res["runs"][r["name"]] = rr
        pm = per_mask[r["mask"]]
        pm["runs"].append(r["name"])
        pm["logged"] |= logged
        pm["h0_enabled_logged"] += len(h0)
        pm["h0_with_loads"] += len(h0_loads)
        pm["h1_logged"] += len(h1)
        pm["h1_with_loads"] += len(h1_loads)
        pm["h1_with_any_tensor_op"] += len(h1_any)
        pm["off_logged"] += len(off)
        pm["off_present_in_log"] += len(off_present)
        pm["off_with_U"] += len(off_u)
        if off_u_mine is not None:
            pm["off_with_U_mine"] = (pm["off_with_U_mine"] or 0) + len(off_u_mine)
        pm["traced_minions"] += len(h0)
        pm["b_equal"] += nb
        pm["b_mismatch_positions"] += mism
        pm["c_equal_walk"] += nc_w
        pm["c_equal_frozen_counts"] += nc_f
        pm["seq_sha_eq_frozen"] += n_seq_fz
        pm["walk_sha_eq_frozen"] += n_walk_fz
        pm["act"] = act
        del s, harts, mine
    allok = True
    for mk, pm in sorted(per_mask.items()):
        act = pm["act"]
        ps = collections.Counter(h // 64 for h in pm["logged"])
        mi = all(ps.get(x, 0) == 64 for x in act)
        mii = [k for k, v in sorted(ps.items()) if k not in act and v == 64]
        minimum = mi and len(mii) >= 1
        stmts = (pm["h0_with_loads"] == pm["h0_enabled_logged"] and pm["h1_with_loads"] == 0 and pm["off_with_U"] == 0
                 and (pm["off_with_U_mine"] in (None, 0)))
        a = "HOLDS" if (minimum and stmts) else ("FAILS" if not stmts else "UNDECIDED (log set below the minimum)")
        b = "HOLDS" if pm["b_equal"] == pm["traced_minions"] and pm["b_mismatch_positions"] == 0 else "FAILS"
        c = "HOLDS" if pm["c_equal_walk"] == pm["traced_minions"] == pm["c_equal_frozen_counts"] else "FAILS"
        res["masks"][mk] = {"runs": pm["runs"], "enabled_shires": act, "logged_union": len(pm["logged"]),
                            "min_log_set_i": mi, "min_log_set_ii_offmask_shires_full": mii, "minimum_met": minimum,
                            "hart0_enabled_logged": pm["h0_enabled_logged"], "hart0_with_tensor_loads": pm["h0_with_loads"],
                            "hart1_logged": pm["h1_logged"], "hart1_with_tensor_loads": pm["h1_with_loads"],
                            "hart1_with_any_tensor_op": pm["h1_with_any_tensor_op"],
                            "offmask_logged": pm["off_logged"], "offmask_present_in_log": pm["off_present_in_log"],
                            "offmask_with_U_instruction": pm["off_with_U"], "offmask_with_U_runner_counters": pm["off_with_U_mine"],
                            "traced_minions": pm["traced_minions"], "b_equal": pm["b_equal"], "b_mismatch_positions": pm["b_mismatch_positions"],
                            "c_equal_walk": pm["c_equal_walk"], "c_equal_frozen_counts": pm["c_equal_frozen_counts"],
                            "full_sequence_sha256_equal_frozen": pm["seq_sha_eq_frozen"],
                            "walk_sequence_sha256_equal_frozen": pm["walk_sha_eq_frozen"],
                            "criterion_a": a, "criterion_b": b, "criterion_c": c}
        allok &= a == "HOLDS" and b == "HOLDS" and c == "HOLDS"
    fails = [mk for mk, v in res["masks"].items() if "FAILS" in (v["criterion_a"], v["criterion_b"], v["criterion_c"])]
    undecided = [mk for mk, v in res["masks"].items() if v["criterion_a"].startswith("UNDECIDED")]
    res["criteria_at_both_masks"] = ("FAIL (a mismatch at %s)" % fails if fails else
                                     ("UNDECIDED at %s" % undecided if undecided else
                                      ("ALL HOLD" if allok and len(res["masks"]) == 2 else "INCOMPLETE")))
    json.dump(res, sys.stdout, indent=1, default=str)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
