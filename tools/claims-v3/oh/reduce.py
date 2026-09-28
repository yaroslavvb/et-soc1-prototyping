#!/usr/bin/env python3
"""OH (the effect of overheating, E53): the reducer. Standard library only. Decision rules as frozen in
prereg/PREREG.md (the registered predictions OH1-a..c, OH2-a..e, OH3-a..b); descriptive numbers are labelled so.

  reduce.py --check-pass BLOCKDIR                one block: launches by status, voids, bad results, the refresh period
  reduce.py --oh1 --data D [D ...] --out F       OH-1: hottest-minus-mean per 1 s window, the three verdicts
  reduce.py --oh2 --data D [D ...] --out F       OH-2: checked launches by band, work per cycle, clock, gap, refresh
  reduce.py --oh3 --data D [D ...] --out F       OH-3: idle board power against the die mean, against E44's laws
  reduce.py --all --data ROOT --out DIR          all three from ROOT/<card>/oh/p*/ (and verdicts.json)
  reduce.py --self-test                          the rules on synthetic windows and launches

A block directory holds: launches.jsonl (every device process: kind heat / cond-<C> / check, its host times, rc, the
status ohlib.py kcheck gave it), marks.jsonl, tel-<run>.jsonl.gz (10 Hz, --reset-ms 1000), k.tar.gz (every process's
output), mp/ (the memprobe refresh programs' results), block.json.
"""
import collections
import glob
import gzip
import io
import json
import math
import os
import statistics as st
import struct
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import ohlib  # noqa: E402

# E44's idle laws (docs/findings/16-dvfs-and-leakage.md; the r4 script idle_vs_temp.py): P = P_fix + A e^((T-80)/T_L)
E44 = {"aifoundry3": (15.45, 21.89, 30.0), "aifoundry1-c1": (18.45, 30.50, 30.0), "aifoundry2": (12.24, 23.71, 36.0)}
GRID = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 45, 50, 60, 80, 120]
REFRESH_CYCLES = 2325.4
METRIC = {"fma": "cycles_per_op", "gemv": "cycles_per_layer_max", "MMB": "cycles_max", "relay": "cycles_max"}


def med(v):
    return st.median(v) if v else None


def card_of(d):
    for c in ("aifoundry1-c1", "aifoundry3", "aifoundry1-c0", "aifoundry2"):
        if "/%s/" % c in d + "/" or d.rstrip("/").endswith(c):
            return c
    bj = ohlib.load_json(os.path.join(d, "block.json"), {})
    return bj.get("card")


def block_dirs(paths):
    out = []
    for p in paths:
        if os.path.exists(os.path.join(p, "block.json")) or os.path.exists(os.path.join(p, "launches.jsonl")):
            out.append(p)
        else:
            out += sorted(d for d in glob.glob(os.path.join(p, "**", "p[0-9]*"), recursive=True)
                          if os.path.isdir(d) and os.path.exists(os.path.join(d, "launches.jsonl"))
                          and ".attempt-" not in d)
    return out


class Block:
    def __init__(self, d):
        self.d = d
        self.card = card_of(d)
        self.info = ohlib.load_json(os.path.join(d, "block.json"), {})
        self.pass_no = int(os.path.basename(d.rstrip("/"))[1:].split(".")[0])
        self.kind = ohlib.KINDS.get(self.pass_no // 100)
        self.launches = ohlib.load_jsonl(os.path.join(d, "launches.jsonl"))
        self.marks = ohlib.load_jsonl(os.path.join(d, "marks.jsonl"))
        self._k = None
        self._tel = {}

    def kfiles(self):
        if self._k is None:
            self._k = {}
            tp = os.path.join(self.d, "k.tar.gz")
            if os.path.exists(tp):
                with tarfile.open(tp, "r:gz") as tf:
                    for m in tf.getmembers():
                        if m.isfile():
                            self._k[m.name] = tf.extractfile(m).read().decode("utf-8", "replace")
            for f in glob.glob(os.path.join(self.d, "k", "*.out")):
                self._k["k/" + os.path.basename(f)] = open(f, errors="replace").read()
        return self._k

    def kout(self, launch):
        return self.kfiles().get(launch.get("file"), "")

    def records(self, launch):
        pre = ohlib.PREFIX[launch["tool"]]
        out = []
        for line in self.kout(launch).splitlines():
            i = line.find(pre)
            if i >= 0:
                try:
                    out.append(json.loads(line[i + len(pre) - 1:]))
                except ValueError:
                    pass
        return out

    def status(self, launch):
        """(status, n_checked, bad reasons) recomputed from the kernel's own output (never the block's record)."""
        recs = self.records(launch)
        if not recs:
            return "NORESULT", 0, []
        bads, n, unchk = [], 0, 0
        for r in recs:
            c, b = ohlib.check_record(r, launch["tool"])
            n += c
            unchk += (not c) and launch["tool"] != "MEMPROBE"
            if b:
                bads.append(b)
        if bads:
            return "BAD", n, bads
        if launch["tool"] != "MEMPROBE" and n == 0:
            return "UNCHECKED", 0, []
        return ("PARTIAL" if unchk else "OK"), n, []

    def runs(self):
        return sorted(os.path.basename(p)[4:].split(".jsonl")[0] for p in glob.glob(os.path.join(self.d, "tel-*.jsonl*")))

    def tel(self, run):
        if run not in self._tel:
            s = ohlib.load_jsonl(os.path.join(self.d, "tel-%s.jsonl" % run))
            self._tel[run] = sorted((x for x in s if x.get("t_ms")), key=lambda x: x["t_ms"])
        return self._tel[run]

    def all_tel(self):
        out = []
        for r in self.runs():
            out += self.tel(r)
        return sorted(out, key=lambda x: x["t_ms"])


def around(samples, t0, t1, pad=300):
    return [s for s in samples if t0 - pad <= s["t_ms"] <= t1 + pad]


def hottest_mean(samples, t0, t1):
    xs = [ohlib.sample_fields(s) for s in around(samples, t0, t1)]
    m = [x[1] for x in xs if x[1] is not None]
    return max(m) if m else None


def bin5(T):
    if T is None:
        return "no-tel"
    lo = int(T // 5 * 5)
    return "%d-%d" % (lo, lo + 5)


# ------------------------------------------------------------------------------------------------ check-pass
def load_u32(d, name):
    meta = None
    for p in (os.path.join(d, name + ".json"), os.path.join(d, name + ".json.gz")):
        if os.path.exists(p):
            meta = json.load(ohlib.open_any(p))
            break
    raw = None
    for p in (os.path.join(d, name + ".u32"), os.path.join(d, name + ".u32.gz")):
        if os.path.exists(p):
            raw = (gzip.open(p) if p.endswith(".gz") else open(p, "rb")).read()
            break
    if meta is None or raw is None or len(raw) < 4 * len(meta["labels"]):
        return None
    return struct.unpack("<%dI" % len(meta["labels"]), raw[:4 * len(meta["labels"])])


def refresh_period(d):
    """The refresh period from the jittered series, exactly as tools/claims-v3/mem/prereg/recompute_latency.py
    (P5_refresh_period): the period in 0.2-cycle steps from 2200 to 2449.8 whose 50-bin fold of the slow loads
    (>= 260 cycles) peaks highest. The constant timer overhead cancels (stamps are taken relative to the first)."""
    r = load_u32(d, "refresh_jit")
    if r is None:
        return None
    OVH = 5
    r = [(v if v < 2 ** 31 else v - 2 ** 32) - OVH for v in r]
    ts = [v + OVH for v in r[0::2]]
    lat = r[1::2]
    ts = [(t - ts[0]) % 2 ** 32 for t in ts]
    slow = [t for t, l_ in zip(ts, lat) if l_ >= 260]
    if len(slow) < 10:
        return {"n": len(lat), "slow": len(slow), "best_period": None}
    scores = []
    for P in range(22000, 24500, 2):
        Pp = P / 10
        scores.append((max(collections.Counter(int((t % Pp) / Pp * 50) for t in slow).values()), Pp))
    scores.sort(reverse=True)
    out = {"n": len(lat), "slow": len(slow), "best_period": scores[0][1], "top5": scores[:5],
           "max_latency": max(lat), "in_refresh_ge240": sum(1 for v in lat if v >= 240) / len(lat)}
    r0 = load_u32(d, "refresh")
    if r0 is not None:
        r0 = [(v if v < 2 ** 31 else v - 2 ** 32) - OVH for v in r0]
        ts0, lat0 = [v + OVH for v in r0[0::2]], r0[1::2]
        per = [(ts0[i + 1] - ts0[i]) % 2 ** 32 for i in range(len(ts0) - 1)]
        out["locked"] = {"n": len(lat0), "period_med": st.median(per) if per else None, "max": max(lat0) if lat0 else None,
                         "frac_ge_220": sum(1 for v in lat0 if v >= 220) / len(lat0) if lat0 else None}
    return out


def check_pass(d):
    B = Block(d)
    res = {"dir": d, "card": B.card, "pass": B.pass_no, "kind": B.kind, "block": B.info, "runs": B.runs()}
    by = collections.Counter()
    kinds = collections.Counter()
    bad, voids = [], []
    per_kernel = collections.defaultdict(collections.Counter)
    for L in B.launches:
        kinds[L["kind"]] += 1
        if L["kind"] != "check":
            continue
        s, n, why = B.status(L)
        by[s] += 1
        per_kernel[L["name"]][s] += 1
        if s == "BAD":
            bad.append({"seq": L["seq"], "name": L["name"], "band": L.get("band"), "role": L.get("role"), "why": why})
        if s == "NORESULT" and L.get("rc"):
            voids.append({"seq": L["seq"], "name": L["name"], "rc": L["rc"], "role": L.get("role")})
    res.update({"launch_kinds": dict(kinds), "check_status": dict(by), "per_kernel": {k: dict(v) for k, v in per_kernel.items()},
                "bad": bad, "voids": voids,
                "aborts": [m for m in B.marks if m.get("ev") in ("abort", "session_stop")],
                "chain_gaps": sum(1 for m in B.marks if m.get("ev") == "chain_gap")})
    rp = refresh_period(os.path.join(d, "mp"))
    if rp:
        res["refresh"] = {k: rp[k] for k in ("n", "slow", "best_period", "locked") if k in rp}
    tel = B.all_tel()
    if tel:
        xs = [ohlib.sample_fields(s) for s in tel]
        res["telemetry"] = {"samples": len(tel), "mean_max": max(x[1] for x in xs if x[1] is not None),
                            "high_max": max((x[3] for x in xs if x[3] is not None), default=None),
                            "board_max": max((x[4] for x in xs if x[4] is not None), default=None),
                            "mhz": sorted({x[5] for x in xs if x[5] is not None})}
    # launch spans: the longest chain of back-to-back launches (gaps < 15 s), a rule check
    spans, cur = [], None
    for L in sorted(B.launches, key=lambda x: x["t_start_ms"]):
        if cur and L["t_start_ms"] - cur[1] < 15000:
            cur[1] = max(cur[1], L["t_end_ms"])
        else:
            if cur:
                spans.append(cur)
            cur = [L["t_start_ms"], L["t_end_ms"]]
    if cur:
        spans.append(cur)
    res["longest_chain_s"] = round(max((b - a for a, b in spans), default=0) / 1000.0, 1)
    res["longest_process_s"] = round(max((L["t_end_ms"] - L["t_start_ms"] for L in B.launches), default=0) / 1000.0, 2)
    if B.kind == "SMOKE":
        names = sorted({L["name"] for L in B.launches if L["kind"] == "check" and L.get("tool") != "MEMPROBE"})
        res["smoke_kernels"] = {n: dict(per_kernel[n]) for n in names}
        res["smoke_ok"] = all(per_kernel[n].get("OK", 0) >= 1 for n in names) and not bad and bool(rp and rp.get("best_period"))
    return res


# ------------------------------------------------------------------------------------------------ OH-1
def oh1_block(B):
    P = ohlib.params()["oh1"]
    skip = P["analysis_skip_s"] * 1000
    out = []
    begins = {m["run"]: m for m in B.marks if m.get("ev") == "cond_begin"}
    ends = {m["run"]: m for m in B.marks if m.get("ev") == "cond_end"}
    for run in B.runs():
        if run not in begins or run not in ends:
            continue
        cond = begins[run]["cond"]
        tc, te = ends[run]["t_begin_ms"], ends[run]["t_ms"]
        spans = []
        for L in B.launches:
            if L.get("run") == run and L["kind"] == "cond-%s" % cond:
                recs = B.records(L)
                if recs:
                    spans.append((min(r["t_start_ms"] for r in recs), max(r["t_end_ms"] for r in recs)))
        W = [w for w in ohlib.windows(B.tel(run), ohlib.params()["reset_ms"]) if w["ok"]]
        for w in W:
            if w["t_start"] < tc + skip or w["t_end"] > te:
                continue
            if cond != "IDLE" and not any(a <= w["t_start"] and w["t_end"] <= b for a, b in spans):
                continue
            if w["max_high"] is None or w["max_mean"] is None:
                continue
            out.append({"card": B.card, "pass": B.pass_no, "run": run, "cond": cond, "t_rel_s": round((w["t_start"] - tc) / 1000.0, 1),
                        "mean": w["max_mean"], "high": w["max_high"], "io": w["max_io"], "dhot": w["max_high"] - w["max_mean"],
                        "board_w": w["board_w"]})
    # descriptive: every window of the block (preheat, condition, tail) whose mean read 64-66 C (the governor's point)
    near = []
    for run in B.runs():
        for w in ohlib.windows(B.tel(run), ohlib.params()["reset_ms"]):
            if w["ok"] and w["max_mean"] is not None and 64 <= w["max_mean"] <= 66 and w["max_high"] is not None:
                near.append({"run": run, "mean": w["max_mean"], "high": w["max_high"], "dhot": w["max_high"] - w["max_mean"]})
    return out, near


def dist(v):
    c = collections.Counter(v)
    return {str(k): c[k] for k in sorted(c)}


def oh1(dirs):
    blocks = [Block(d) for d in block_dirs(dirs)]
    blocks = [b for b in blocks if b.kind == "OH1" and b.info.get("status") == "ok"]
    rows, near = [], collections.defaultdict(list)
    per_block = {}
    for B in blocks:
        r, nr = oh1_block(B)
        rows += r
        near[B.card] += nr
        per_block[(B.card, B.pass_no)] = r
    res = {"blocks": sorted("%s p%d" % k for k in per_block), "n_windows": len(rows), "by_card_cond": {}}
    by = collections.defaultdict(list)
    for x in rows:
        by[(x["card"], x["cond"])].append(x)
    for (c, cond), xs in sorted(by.items()):
        d = [x["dhot"] for x in xs]
        res["by_card_cond"]["%s %s" % (c, cond)] = {"n": len(xs), "dhot_median": med(d), "dhot_max": max(d), "dhot_dist": dist(d),
                                                     "mean_range": [min(x["mean"] for x in xs), max(x["mean"] for x in xs)],
                                                     "io_minus_mean_median": med([x["io"] - x["mean"] for x in xs if x["io"] is not None]),
                                                     "board_w_median": med([x["board_w"] for x in xs if x["board_w"] is not None])}
    # OH1-a: every analysed window <= +4
    mx = max((x["dhot"] for x in rows), default=None)
    res["OH1-a"] = {"rule": "every 1 s analysis window, every condition, both cards: dhot <= +4 C (FAIL if any >= +5)",
                    "max_dhot": mx, "n": len(rows),
                    "verdict": None if mx is None else ("PASS" if mx <= 4 else "FAIL")}
    # OH1-b: per block, median dhot ONE-C <= B4C; aifoundry3 >= 2 of 3, card 1 2 of 2
    b_res, by_card = {}, collections.defaultdict(list)
    for (c, p), r in sorted(per_block.items()):
        one = med([x["dhot"] for x in r if x["cond"] == "ONE-C"])
        b4 = med([x["dhot"] for x in r if x["cond"] == "B4C"])
        ok = None if one is None or b4 is None else one <= b4
        b_res["%s p%d" % (c, p)] = {"ONE-C": one, "B4C": b4, "holds": ok}
        by_card[c].append(ok)
    need = {"aifoundry3": 2, "aifoundry1-c1": 2}
    res["OH1-b"] = {"rule": "per block median dhot(ONE-C) <= median dhot(B4C); PASS in >= 2 of 3 blocks on aifoundry3 and 2 of 2 on card 1",
                    "blocks": b_res,
                    "verdict_by_card": {c: ("PASS" if sum(1 for v in vs if v) >= need.get(c, 2) else
                                            "INSUFFICIENT" if any(v is None for v in vs) or len(vs) < need.get(c, 2) else "FAIL")
                                        for c, vs in by_card.items()}}
    # OH1-c: per card, pooled, |median(cond) - median(IDLE)| <= 1 C
    c_res = {}
    for c in sorted({x["card"] for x in rows}):
        idle = med([x["dhot"] for x in rows if x["card"] == c and x["cond"] == "IDLE"])
        for cond in ("ONE-C", "ONE-NE", "B4C"):
            m = med([x["dhot"] for x in rows if x["card"] == c and x["cond"] == cond])
            dlt = None if m is None or idle is None else m - idle
            c_res["%s %s" % (c, cond)] = {"median": m, "idle_median": idle, "diff": dlt,
                                          "verdict": None if dlt is None else ("PASS" if abs(dlt) <= 1 else "FAIL")}
    res["OH1-c"] = {"rule": "per card, pooled over blocks: |median dhot(condition) - median dhot(IDLE)| <= 1 C for ONE-C, ONE-NE, B4C",
                    "items": c_res}
    res["near_65"] = {c: {"n": len(v), "high_dist": dist([x["high"] for x in v]), "dhot_dist": dist([x["dhot"] for x in v])}
                      for c, v in near.items()}
    res["near_65_note"] = "descriptive: every ok 1 s window of the OH-1 blocks whose mean read 64-66 C (the governor's decision point), any phase"
    res["windows"] = rows
    return res


# ------------------------------------------------------------------------------------------------ OH-2
def oh2(dirs):
    blocks = [Block(d) for d in block_dirs(dirs)]
    blocks = [b for b in blocks if b.kind in ("OH2", "SMOKE")]
    L2 = []          # checked launches
    heat_lines = []  # heater SPARSITY lines (launch >= 0)
    win = []         # windows inside heater spans
    allwin = []
    droop = collections.defaultdict(lambda: collections.defaultdict(list))
    refresh = {}
    for B in blocks:
        if B.info.get("status") not in ("ok", None) and B.kind == "OH2":
            pass     # a failed OH-2 block is still reported (its launches happened); marked by status below
        tel = B.all_tel()
        for L in B.launches:
            if L["kind"] == "check":
                s, n, why = B.status(L)
                T = hottest_mean(tel, L["t_start_ms"], L["t_end_ms"])
                hs = [ohlib.sample_fields(x)[3] for x in around(tel, L["t_start_ms"], L["t_end_ms"])]
                hs = [h for h in hs if h is not None]
                recs = B.records(L)
                L2.append({"card": B.card, "pass": B.pass_no, "block_status": B.info.get("status"), "seq": L["seq"],
                           "name": L["name"], "tool": L["tool"], "band": L.get("band"), "role": L.get("role"),
                           "attempt": L.get("attempt"), "status": s, "n_checked": n, "why": why, "rc": L.get("rc"),
                           "mean": T, "high": max(hs) if hs else None, "recs": recs, "t_start_ms": L["t_start_ms"]})
            elif L["kind"] == "heat" or L["kind"].startswith("cond-"):
                recs = B.records(L)
                spans = [(r["t_start_ms"], r["t_end_ms"]) for r in recs]
                for r in recs:
                    if r.get("launch", -1) >= 0 and r.get("iters", 0) >= 100000:
                        heat_lines.append({"card": B.card, "pass": B.pass_no, "ghz": r.get("ghz"), "cpo": r.get("cycles_per_op"),
                                           "mean": hottest_mean(tel, r["t_start_ms"], r["t_end_ms"]),
                                           "per_shire": L.get("per_shire")})
                if L["kind"] == "heat" and B.kind == "OH2" and spans:
                    a, b = min(x[0] for x in spans), max(x[1] for x in spans)
                    for run in B.runs():
                        for w in ohlib.windows(B.tel(run), ohlib.params()["reset_ms"]):
                            if w["ok"] and a <= w["t_start"] and w["t_end"] <= b and w["max_high"] is not None:
                                win.append({"card": B.card, "mean": w["max_mean"], "dhot": w["max_high"] - w["max_mean"],
                                            "per_shire": L.get("per_shire")})
        if B.kind == "OH2":
            for run in B.runs():
                for w in ohlib.windows(B.tel(run), ohlib.params()["reset_ms"]):
                    if w["ok"] and w["max_high"] is not None:
                        allwin.append({"card": B.card, "mean": w["max_mean"], "dhot": w["max_high"] - w["max_mean"]})
            for s in tel:
                dm = s.get("die_mv") or {}
                m = (s.get("temp_c") or {}).get("minshire", [None])[0]
                if m is not None and dm:
                    for k in ("minion", "sram", "noc", "ddr"):
                        if dm.get(k):
                            droop[B.card][(k, bin5(m))].append(dm[k])
        rp = refresh_period(os.path.join(B.d, "mp"))
        if rp:
            rl = [L for L in B.launches if L["kind"] == "check" and L["name"] == "refresh_jit"]
            T = hottest_mean(tel, rl[-1]["t_start_ms"], rl[-1]["t_end_ms"]) if rl else None
            refresh["%s p%d" % (B.card, B.pass_no)] = dict(rp, die_mean=T, band=rl[-1].get("band") if rl else None)

    res = {"blocks": sorted({"%s p%d (%s)" % (x["card"], x["pass"], x["block_status"]) for x in L2})}
    # the table: card x measured 5 C bin (and the target band)
    tab = collections.defaultdict(collections.Counter)
    bands = collections.defaultdict(collections.Counter)
    for x in L2:
        if x["tool"] == "MEMPROBE":
            continue
        for key, t in (((x["card"], bin5(x["mean"])), tab), ((x["card"], x["band"]), bands)):
            c = t[key]
            c["launches"] += 1
            c["checked"] += x["status"] in ("OK", "PARTIAL", "BAD") and x["n_checked"] > 0
            c["bad"] += x["status"] == "BAD"
            c["void"] += x["status"] == "NORESULT"
            c["unchecked"] += x["status"] == "UNCHECKED"
    res["by_bin"] = {"%s %s" % k: dict(v, upper95_per_launch=(round(3.0 / v["checked"], 4) if v["checked"] and not v["bad"] else None))
                     for k, v in sorted(tab.items())}
    res["by_band"] = {"%s %s" % k: dict(v) for k, v in sorted(bands.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))}
    chk = [x for x in L2 if x["tool"] != "MEMPROBE" and x["status"] in ("OK", "PARTIAL", "BAD")]
    nbad = sum(1 for x in chk if x["status"] == "BAD")
    res["hottest_checked"] = {c: max(((x["mean"], x["high"], x["name"]) for x in chk if x["card"] == c and x["mean"] is not None), default=None)
                              for c in sorted({x["card"] for x in chk})}
    res["OH2-a"] = {"rule": "0 wrong results, 0 tensor-error CSRs, 0 not-ok among all checked launches, every band, both cards",
                    "checked": len(chk), "bad": nbad, "voids": sum(1 for x in L2 if x["status"] == "NORESULT"),
                    "bad_list": [{k: x[k] for k in ("card", "name", "band", "role", "mean", "high", "why")} for x in chk if x["status"] == "BAD"],
                    "verdict": "PASS" if chk and nbad == 0 else ("FAIL" if nbad else None)}
    # OH2-b: work per cycle, hot (measured mean 80-85) against rest (band B0)
    def metric_keys(x):
        out = []
        for r in x["recs"]:
            if x["tool"] == "SPARSITY" and r.get("test") == "fma" and r.get("cycles_per_op"):
                out.append(("%s sp=%.4f" % (x["name"], r.get("sparsity", 0)), r["cycles_per_op"]))
            elif x["tool"] == "SPARSITY" and r.get("test") == "gemv" and r.get("cycles_per_layer_max"):
                out.append(("%s sp=%.4f" % (x["name"], r.get("sparsity", 0)), r["cycles_per_layer_max"]))
            elif x["tool"] == "MMB" and r.get("cycles_max"):
                out.append((x["name"], r["cycles_max"]))
            elif x["tool"] == "ONCHIP" and r.get("test") == "relay" and r.get("cycles_max"):
                out.append((x["name"], r["cycles_max"]))
        return out
    hot, rest = collections.defaultdict(list), collections.defaultdict(list)
    for x in chk:
        if x["status"] == "BAD":
            continue
        for k, v in metric_keys(x):
            if x["band"] == "B0" and x["role"] == "battery":
                rest[(x["card"], k)].append(v)
            if x["mean"] is not None and 80 <= x["mean"] <= 85:
                hot[(x["card"], k)].append(v)
    b = {}
    for key in sorted(set(hot) | set(rest)):
        h, r = hot.get(key, []), rest.get(key, [])
        if not h or not r:
            b["%s %s" % key] = {"n_hot": len(h), "n_rest": len(r), "verdict": "INSUFFICIENT"}
            continue
        mh, mr = med(h), med(r)
        d = (mh / mr - 1) * 100
        v = "PASS" if abs(d) <= 0.1 else ("PASS (within noise)" if min(r) <= mh <= max(r) else "FAIL")
        b["%s %s" % key] = {"n_hot": len(h), "n_rest": len(r), "median_hot": mh, "median_rest": mr, "diff_pct": round(d, 4),
                            "rest_range": [min(r), max(r)], "hot_range": [min(h), max(h)],
                            "rest_spread_pct": round((max(r) - min(r)) / mr * 100, 4), "verdict": v}
    res["OH2-b"] = {"rule": "per kernel metric: |median(hot 80-85 C) / median(rest B0) - 1| <= 0.1 % PASS; else hot median "
                            "inside the rest band's range PASS (within noise); else FAIL", "items": b}
    # OH2-c: the heater's implied clock by band
    cband = collections.defaultdict(list)
    cpo = collections.defaultdict(list)
    for x in heat_lines:
        if x["ghz"] is not None:
            cband[(x["card"], bin5(x["mean"]))].append(x["ghz"])
            cpo[(x["card"], bin5(x["mean"]))].append(x["cpo"])
    c = {}
    for k in sorted(cband):
        g = cband[k]
        c["%s %s" % k] = {"n": len(g), "ghz_median": med(g), "ghz_range": [min(g), max(g)],
                          "cycles_per_op_range": [min(cpo[k]), max(cpo[k])],
                          "verdict": "PASS" if 0.5994 <= med(g) <= 0.5995 else "FAIL"}
    res["OH2-c"] = {"rule": "the heater's implied clock (cycles / host wall time of each 0.5 s launch), median per 5 C band of the die mean, in 0.5994-0.5995 GHz",
                    "items": c}
    # OH2-d: dhot under the heater's whole-chip load by band
    def band_d(m):
        return "60-70" if 60 <= m < 70 else "70-80" if 70 <= m < 80 else "80-85" if 80 <= m <= 85 else None
    d = {}
    for card in sorted({x["card"] for x in win}):
        g = collections.defaultdict(list)
        for x in win:
            if x["card"] == card and band_d(x["mean"]):
                g[band_d(x["mean"])].append(x["dhot"])
        items = {k: {"n": len(v), "median": med(v), "max": max(v), "dist": dist(v)} for k, v in sorted(g.items())}
        mx = max((v["max"] for v in items.values()), default=None)
        grow = (items["80-85"]["median"] - items["60-70"]["median"]) if "80-85" in items and "60-70" in items else None
        d[card] = {"bands": items, "max": mx, "growth_80_85_minus_60_70": grow,
                   "verdict_max": None if mx is None else ("PASS" if mx <= 4 else "FAIL"),
                   "verdict_growth": None if grow is None else ("PASS" if 0 <= grow <= 1 else "FAIL")}
    res["OH2-d"] = {"rule": "windows inside a heater (ALL32/ALL24) launch: max dhot <= +4 in every band; median(80-85) - median(60-70) in [0, +1]",
                    "cards": d}
    ga = collections.defaultdict(list)
    for x in allwin:
        ga[(x["card"], bin5(x["mean"]))].append(x["dhot"])
    res["dhot_all_windows"] = {"%s %s" % k: {"n": len(v), "median": med(v), "max": max(v), "dist": dist(v)} for k, v in sorted(ga.items())}
    res["dhot_all_windows_note"] = "descriptive: every ok 1 s window of the OH-2 blocks (heating, batteries, holds, tail), by the window's mean"
    # OH2-e: the refresh period
    e = {}
    for k, v in refresh.items():
        bp = v.get("best_period")
        e[k] = {"best_period": bp, "die_mean": v.get("die_mean"), "band": v.get("band"), "slow_loads": v.get("slow"), "n": v.get("n"),
                "locked": v.get("locked"), "verdict": None if bp is None else ("PASS" if abs(bp - REFRESH_CYCLES) <= 0.1 + 1e-9 else "FAIL")}
    res["OH2-e"] = {"rule": "memprobe's refresh period (jittered series, as MEM-P5) at the hot band = 2,325.4 +- 0.1 minion cycles", "items": e}
    # descriptive: die voltages by band (the supply at the die against temperature)
    res["die_mv_by_band"] = {card: {"%s %s" % k: {"n": len(v), "median": med(v), "min": min(v), "max": max(v)}
                                    for k, v in sorted(g.items())} for card, g in droop.items()}
    res["launches"] = [{k: x[k] for k in ("card", "pass", "seq", "name", "band", "role", "attempt", "status", "n_checked", "mean", "high", "rc")}
                       for x in L2]
    return res


# ------------------------------------------------------------------------------------------------ OH-3
def fit_law(T, P, N):
    fits = []
    for TL in GRID:
        # weighted least squares for (a, b) in P = a + b e^((T-80)/TL), a, b >= 0
        X = [math.exp((t - 80.0) / TL) for t in T]
        sw = sum(N)
        sx = sum(n * x for n, x in zip(N, X))
        sxx = sum(n * x * x for n, x in zip(N, X))
        sy = sum(n * p for n, p in zip(N, P))
        sxy = sum(n * x * p for n, x, p in zip(N, X, P))
        det = sw * sxx - sx * sx
        if det <= 0:
            continue
        b = (sw * sxy - sx * sy) / det
        a = (sy - b * sx) / sw
        if a < 0 or b < 0:
            continue
        rms = math.sqrt(sum(n * (a + b * x - p) ** 2 for n, x, p in zip(N, X, P)) / sw)
        fits.append((rms, TL, a, b))
    fits.sort()
    return fits


def oh3(dirs):
    blocks = [Block(d) for d in block_dirs(dirs)]
    blocks = [b for b in blocks if b.kind in ("OH1", "OH2")]
    bins = collections.defaultdict(lambda: collections.defaultdict(list))
    src = collections.defaultdict(collections.Counter)
    for B in blocks:
        ends = sorted((L["t_start_ms"], L["t_end_ms"]) for L in B.launches)
        for s in B.all_tel():
            t = s["t_ms"]
            if (s.get("mhz") or {}).get("minion") not in (600, None):
                continue
            prev = [e for a, e in ends if a <= t + 300]
            if not prev or t < max(prev) + 5000:
                continue          # inside or within 5 s of a launch (or before the block's first launch)
            if any(a - 300 <= t <= e for a, e in ends):
                continue
            m = (s.get("temp_c") or {}).get("minshire", [None])[0]
            if m is None or s.get("board_w") is None:
                continue
            bins[B.card][m].append(s["board_w"])
            src[B.card][B.kind] += 1
    res = {}
    for card, g in sorted(bins.items()):
        T = sorted(t for t in g if len(g[t]) >= 20)
        rows = []
        law = E44.get(card)
        for t in T:
            p = med(g[t])
            ref = law[0] + law[1] * math.exp((t - 80.0) / law[2]) if law else None
            rows.append({"T": t, "n": len(g[t]), "board_w": round(p, 3), "e44": round(ref, 3) if ref else None,
                         "diff": round(p - ref, 3) if ref else None})
        a_rows = [r for r in rows if 60 <= r["T"] <= 84]
        a_ok = None if not a_rows else all(abs(r["diff"]) <= 1.5 for r in a_rows)
        fits = fit_law(T, [med(g[t]) for t in T], [len(g[t]) for t in T]) if len(T) >= 4 else []
        fb = None
        if fits:
            rms, TL, a, b = fits[0]
            okr = sorted(f[1] for f in fits if f[0] <= 1.10 * rms)
            fb = {"best": {"P_fix": round(a, 2), "A": round(b, 2), "T_L": TL, "rms": round(rms, 3), "doubling_C": round(TL * math.log(2), 1)},
                  "T_L_within_10pct": [okr[0], okr[-1]], "doubling_range_C": [round(okr[0] * math.log(2), 1), round(okr[-1] * math.log(2), 1)],
                  "verdict": "PASS" if 17 <= TL * math.log(2) <= 25 else "FAIL"}
        res[card] = {"samples": sum(len(v) for v in g.values()), "by_kind": dict(src[card]), "bins": rows,
                     "OH3-a": {"rule": "median board power per whole degree (>= 20 samples) between 60 and 84 C within +-1.5 W of the card's E44 law",
                               "n_bins": len(a_rows), "max_abs_diff": max((abs(r["diff"]) for r in a_rows), default=None),
                               "verdict": None if a_ok is None else ("PASS" if a_ok else "FAIL")},
                     "OH3-b": fb if fb else {"verdict": "INSUFFICIENT", "why": "fewer than 4 whole-degree bins with >= 20 samples"}}
    return res


# ------------------------------------------------------------------------------------------------ self-test
def self_test():
    ok = True

    def expect(c, what):
        nonlocal ok
        print(("ok   " if c else "FAIL ") + what)
        ok = ok and c
    # windows and dhot
    S = []
    t = 1000
    for i in range(30):
        S.append({"t_ms": t, "since_reset_ms": (i % 10 + 1) * 100, "board_w": 40, "temp_c": {"minshire": [70, 66, 72 + (i // 10)], "ioshire": [69, 68, 69]},
                  "mhz": {"minion": 600}})
        t += 100
    W = ohlib.windows(S)
    expect(len(W) == 3 and all(w["ok"] for w in W), "three 1 s windows")
    expect([w["max_high"] - w["max_mean"] for w in W] == [2, 3, 4], "dhot per window 2, 3, 4")
    # refresh period on a synthetic series with a 2325.4-cycle period
    import random
    rng = random.Random(1)
    import tempfile
    d = tempfile.mkdtemp()
    labels, vals, tc = [], [], 0
    for i in range(19000):
        tc += 300 + rng.randrange(3000)
        lat = 300 if (tc % 2325.4) < 250 else 215
        labels += [["t", i], ["lat", i]]
        vals += [tc % 2 ** 32, lat + 5]
        tc += lat
    json.dump({"labels": labels}, open(os.path.join(d, "refresh_jit.json"), "w"))
    open(os.path.join(d, "refresh_jit.u32"), "wb").write(struct.pack("<%dI" % len(vals), *vals))
    rp = refresh_period(d)
    expect(rp and abs(rp["best_period"] - 2325.4) <= 0.1 + 1e-9, "synthetic refresh period found: %s" % (rp or {}).get("best_period"))
    # the idle-law fit recovers a planted law
    T = list(range(60, 85))
    P = [15.45 + 21.89 * math.exp((x - 80) / 30.0) for x in T]
    f = fit_law(T, P, [30] * len(T))
    expect(f and f[0][1] == 30, "the planted T_L 30 is the best fit")
    print("self-test: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-pass")
    ap.add_argument("--oh1", action="store_true")
    ap.add_argument("--oh2", action="store_true")
    ap.add_argument("--oh3", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--data", nargs="*", default=[])
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.check_pass:
        print(json.dumps(check_pass(a.check_pass), indent=1, default=str))
        return 0
    if a.all:
        out = a.out or "."
        os.makedirs(out, exist_ok=True)
        dirs = []
        for root in a.data:
            dirs += sorted(glob.glob(os.path.join(root, "*", "oh", "p[0-9]*")))
        dirs = [x for x in dirs if ".attempt-" not in x]
        # amendment 1: a block stopped by hand (block.json status "aborted") enters no verdict; its checked launches are
        # reported beside them (oh2-aborted.json), since each was a real, checked launch at a measured temperature
        aborted = [x for x in dirs if (ohlib.load_json(os.path.join(x, "block.json"), {}) or {}).get("status") == "aborted"]
        dirs = [x for x in dirs if x not in aborted]
        if aborted:
            ra = oh2(aborted)
            json.dump({k: ra[k] for k in ("blocks", "by_bin", "by_band", "hottest_checked", "OH2-a", "launches")},
                      open(os.path.join(out, "oh2-aborted.json"), "w"), indent=1, default=str)
        r1, r2, r3 = oh1(dirs), oh2(dirs), oh3(dirs)
        for n, r in (("oh1.json", r1), ("oh2.json", r2), ("oh3.json", r3)):
            json.dump(r, open(os.path.join(out, n), "w"), indent=1, default=str)
        checks = {os.path.relpath(x, a.data[0]) if a.data else x: check_pass(x) for x in dirs}
        json.dump(checks, open(os.path.join(out, "checks.json"), "w"), indent=1, default=str)
        v = {"OH1-a": r1["OH1-a"]["verdict"], "OH1-b": r1["OH1-b"]["verdict_by_card"],
             "OH1-c": {k: x["verdict"] for k, x in r1["OH1-c"]["items"].items()},
             "OH2-a": r2["OH2-a"]["verdict"], "OH2-b": {k: x["verdict"] for k, x in r2["OH2-b"]["items"].items()},
             "OH2-c": {k: x["verdict"] for k, x in r2["OH2-c"]["items"].items()},
             "OH2-d": {k: {"max": x["verdict_max"], "growth": x["verdict_growth"]} for k, x in r2["OH2-d"]["cards"].items()},
             "OH2-e": {k: x["verdict"] for k, x in r2["OH2-e"]["items"].items()},
             "OH3-a": {c: x["OH3-a"]["verdict"] for c, x in r3.items()},
             "OH3-b": {c: x["OH3-b"]["verdict"] for c, x in r3.items()}}
        json.dump(v, open(os.path.join(out, "verdicts.json"), "w"), indent=1)
        print(json.dumps(v, indent=1))
        return 0
    for flag, fn in (("oh1", oh1), ("oh2", oh2), ("oh3", oh3)):
        if getattr(a, flag):
            r = fn(a.data)
            s = json.dumps(r, indent=1, default=str)
            if a.out:
                open(a.out, "w").write(s)
            else:
                print(s)
            return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
