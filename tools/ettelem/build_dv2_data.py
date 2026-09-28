#!/usr/bin/env python3
"""DV2, the DVFS-and-heat development night on aifoundry2 (27-28 September 2026), reduced for the DVFS page.

    build_dv2_data.py --data docs/reports/data/2026-09-28-dvfs2-aifoundry2 \\
        [--out docs/reports/data/2026-09-28-dvfs2-aifoundry2/dv2.json] [--merge docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json]

Everything here is DEVELOPMENT data: the night chose the parameters and the rules of the frozen validation
(PREREG-VAL.md), and it tests nothing. The block says so in its label and the page labels every number from it.

Inputs, all under --data:
  raw/                       the development data root (a copy of build/claims-v3/aifoundry2/dv2 from the dvfs2
                             worktree; mgmt.log and host-sensors.jsonl gzipped): Z1 watch cycles p1xxx, the smoke p4001,
                             the NAT sessions p6035/p6038/p6041, their runs.jsonl (the per-run observables of
                             tools/claims-v3/dv2/dv2obs.py, computed live), tel-*.jsonl.gz (10 Hz ettelem samples) and the
                             SP trace-ring dumps (*.bin)
  queue-dv2-aifoundry2.log   the night's queue log (tools/claims-v3/queue.sh): why a Z1 slot with no pass directory
                             did not run
  incident/                  kernel-log.txt (the card's error events from dmesg), clock-anchors.txt and
                             kernel_events.py (their boot-relative stamps mapped to wall time)
  reductions/dv2-dev.json    tools/claims-v3/dv2/reduce_dv2.py --dev (the host bands, the decision log)
  reductions/dev-idle.json   tools/claims-v3/dv2v/reduce_val.py --dev (the frozen validation reducer on development data)
  plan/PREREG-VAL.md         the frozen validation plan (its SHA-256 is recomputed here and printed)

The governor's lines are read with the frozen reducer's own parser and SP-to-host mapping (reduce_val.collect,
host_of; imported, not modified), over every ring dump of the night: the Z1 cycles' and the sessions'. Times of day
are PDT (UTC-7).

What the block holds (all per card, so another card's night slots in beside aifoundry2's):
  z1          the watch cycles: time, the 34-sensor mean (the governor's input), the low and the hottest sensor
              (peak-hold marks over the 1 s sample), board W, clock, the governor state the ring implies; a slot
              that did not run is an entry with skipped, its slot time and why (its block.json, or the queue log)
  sessions    the heating sessions (kind, branch, start reading, window, status)
  lines       every thermal line (ENTER = "Thermal throttle down", EXIT = "Thermal idle state") with host time and the
              temperature it printed; crossings = clusters of those lines 30 s apart or more, each with its lines,
              the power-idle lines among them, in SP seconds from the cluster's first line
  loop        ENTER -> EXIT intervals under 60 s against k x the loop period (reduce_val.P_LOOP)
  runs        the T-runs of the NAT-4 session p6038: a telemetry excerpt (clock, mean, high, board) around each
              launch and dv2obs's markers (t_up, t_hi, t_hi2, t_m, t_down, t_end), in s from the launch
  q1, q2      the owner's two questions, summarised from the runs (G1-T/G1-H, G4's per-block L)
  bands       reduce_dv2's host bands; g3 the launch and end latencies (reduce_val)
  residency   the THERMAL_DOWN and POWER_UP residency counters at the first watch cycle, and the uptime
  incident    the Master Minion hang of 02:50:53 (p6041), from its launches, heater output and telemetry: each lift's
              kernels (a 20,000-iteration calibration kernel, then a stream of short kernels), the second lift's
              calibration kernel against the host's clock readings, and the kernel log's SP runtime errors with
              wall times from incident/kernel_events.py
  prereg      the frozen validation plan: file, SHA-256, the lock's SHA-256, the frozen G4 numbers
"""
import argparse
import datetime
import glob
import gzip
import hashlib
import json
import math
import os
import sys
import zoneinfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.dont_write_bytecode = True                      # never leave caches beside the locked DV2 tools
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "dv2v"))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "dv2"))
import reduce_val as RV  # noqa: E402  (frozen: imported for its parser and time mapping, never edited)

TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
CARD = "aifoundry2"
LABEL = ("development (DV2, aifoundry2, 27-28 September 2026): these runs chose the parameters and rules of the frozen "
         "validation plan; they test nothing")


def hm(ms, secs=True):
    return datetime.datetime.fromtimestamp(ms / 1000.0, TZ).strftime("%H:%M:%S" if secs else "%H:%M")


def jl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def jload(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return None


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def r1(v, n=1):
    return None if v is None else round(v, n)


def z1_slot(n):
    """A Z1 pass's slot (PDT) from tools/claims-v3/dv2/night.json: 1001 + k at z1_first + k x z1_period_s, 1101 + k at
    z1b_first + k x z1b_period_s."""
    nj = jload(os.path.join(ROOT, "tools", "claims-v3", "dv2", "night.json")) or {}
    first, period, base = (nj.get("z1b_first"), nj.get("z1b_period_s"), 1101) if n >= 1101 else \
        (nj.get("z1_first"), nj.get("z1_period_s"), 1001)
    if not first or not period:
        return None
    h, m = map(int, first.split(":"))
    t = h * 3600 + m * 60 + (n - base) * period
    return "%02d:%02d" % (t // 3600, t % 3600 // 60)


def z1_cycles(raw, idle):
    per = {c["cycle"]: c for c in idle.get("per_cycle", [])}
    out = []
    dirs = {os.path.basename(d): d for d in glob.glob(os.path.join(raw, "p1[0-9][0-9][0-9]"))}
    # a slot of a series (10xx, 11xx) between its first and last pass that has no directory did not run at all: the
    # queue log says why (e.g. the night stop that ended NAT-1 at 01:37:51 also stopped p1007)
    qlog = os.path.join(os.path.dirname(raw), "queue-dv2-aifoundry2.log")
    qlines = open(qlog).read().splitlines() if os.path.exists(qlog) else []
    for series in ("10", "11"):
        nums = sorted(int(k[1:]) for k in dirs if k[1:3] == series)
        for n in range(nums[0], nums[-1] + 1) if nums else []:
            if "p%d" % n not in dirs:
                dirs["p%d" % n] = None
    for name in sorted(dirs):
        d = dirs[name]
        z = jload(os.path.join(d, "z1.json")) if d else None
        if not z:
            b = (jload(os.path.join(d, "block.json")) if d else None) or {}
            why = b.get("note") or b.get("status")
            if not d:
                q = [ln for ln in qlines if " dv2 %s:" % name in ln or " dv2 %s " % name in ln]
                why = ("not run: " + q[-1].split(" dv2 %s" % name, 1)[1].lstrip(": ")) if q else "no pass directory"
            reason = "night stop" if "night stop" in (why or "") else "slot passed" if "passed" in (why or "") else None
            out.append({"pass": name, "skipped": True, "slot": z1_slot(int(name[1:])), "reason": reason, "why": why})
            continue
        tel = [s for s in jl(os.path.join(d, "tel.jsonl")) if (s.get("temp_c") or {}).get("minshire")]
        ms = [s["temp_c"]["minshire"] for s in tel]
        pc = per.get(name, {})
        out.append({"pass": name, "t_ms": z["t_ms"], "time": hm(z["t_ms"]), "mean": z["reading_c"],
                    "mean_min": min(m[0] for m in ms), "mean_max": max(m[0] for m in ms),
                    "low": min(m[1] for m in ms), "high_min": min(m[2] for m in ms), "high_max": max(m[2] for m in ms),
                    "samples": len(ms), "board_w": z["board_w"], "mhz": z["mhz"], "threshold_c": z.get("threshold_c"),
                    "state": pc.get("state"), "clean": pc.get("clean"), "class": pc.get("class"),
                    "quiet_before_s": pc.get("quiet_before_s"), "quiet_after_s": pc.get("quiet_after_s")})
    return out


def sessions(raw):
    out = []
    for d in sorted(glob.glob(os.path.join(raw, "p[4-6][0-9][0-9][0-9]"))):
        b = jload(os.path.join(d, "block.json")) or {}
        s = jload(os.path.join(d, "session.json")) or {}
        L = jl(os.path.join(d, "launches.jsonl"))
        out.append({"pass": os.path.basename(d), "kind": s.get("kind") or ("C1m" if "5001" in d else "SMOKE"),
                    "branch": s.get("branch"), "r0": s.get("r0"), "status": b.get("status"),
                    "t0_ms": b.get("t0_ms"), "t1_ms": b.get("t1_ms"),
                    "start": hm(b["t0_ms"]) if b.get("t0_ms") else None, "end": hm(b["t1_ms"]) if b.get("t1_ms") else None,
                    "note": (s.get("note") or b.get("note") or ""), "launches": len(L),
                    "launch_rc": [x.get("rc") for x in L]})
    return out


def governor_lines(raw):
    """Every governor line of the night (Z1 and session dumps), merged by kind and SP time, with the frozen reducer's
    SP-to-host offsets (fitted on the Z1 cycles' DM request lines)."""
    dirs = RV.cycles_of(raw, True)
    extra = sorted(f for f in glob.glob(os.path.join(raw, "p[4-6][0-9][0-9][0-9]", "**", "*.bin"), recursive=True))
    A = RV.analyse(dirs, extra_dumps=extra, windows=RV.session_windows(raw))
    # The frozen reducer accepts a fit made from a single DM request line (spread 0). In this night's data one such fit
    # (the p1008 dump, whose newest DM line is a session sampler's, not the previous Z1 cycle's) is 474 s off the others,
    # which agree to 0.1 s over the night (the SP clock drifts about 9 ppm). Fits more than 1 s from the median are
    # dropped here; the reducer itself is frozen and is left as it is.
    med = sorted(o[1] for o in A["offsets"])[len(A["offsets"]) // 2]
    offs = [o for o in A["offsets"] if abs(o[1] - med) <= 1.0]
    dropped = [round(o[1] - med, 1) for o in A["offsets"] if abs(o[1] - med) > 1.0]
    wins = RV.session_windows(raw)
    host = lambda ts: RV.host_of(ts, offs)
    in_session = lambda ts: any(w0 <= host(ts) <= w1 for w0, w1 in wins)
    ev = A["events"]
    thr = [e for e in ev if e["kind"] in ("thermal_down", "thermal_idle")]
    lines = [{"kind": "ENTER" if e["kind"] == "thermal_down" else "EXIT", "T": e.get("T"), "sp_s": round(e["ts"] / 1e6, 4),
              "host_ms": int(round(host(e["ts"]) * 1000)), "time": hm(host(e["ts"]) * 1000)} for e in thr]
    # crossings: clusters of thermal lines whose gaps are under 30 s
    cl = []
    for e in thr:
        if cl and e["ts"] - cl[-1][-1]["ts"] <= 30e6:
            cl[-1].append(e)
        else:
            cl.append([e])
    kinds = {"thermal_down": "ENTER", "thermal_idle": "EXIT", "power_idle": "PIDLE", "power_up": "PUP",
             "power_down": "PDOWN", "received": "RECEIVED"}
    cross = []
    for c in cl:
        a, b = c[0]["ts"], c[-1]["ts"]
        near = [e for e in ev if a - 0.5e6 <= e["ts"] <= b + 0.5e6 and e["kind"] in kinds]
        cross.append({"time": hm(host(a) * 1000), "host_ms": int(round(host(a) * 1000)), "sp_s": round(a / 1e6, 4),
                      "idle": not in_session(a),
                      "dur_s": round((b - a) / 1e6, 4),
                      "enter": sum(1 for e in c if e["kind"] == "thermal_down"),
                      "exit": sum(1 for e in c if e["kind"] == "thermal_idle"),
                      "ends": "ENTER" if c[-1]["kind"] == "thermal_down" else "EXIT",
                      "lines": [{"k": kinds[e["kind"]], "t": round((e["ts"] - a) / 1e6, 4),
                                 **({"T": e.get("T")} if e["kind"] in ("thermal_down", "thermal_idle") else {}),
                                 **({"state": e.get("state")} if e["kind"] == "received" else {})} for e in near]})
    # the loop: ENTER -> next thermal line when it is an EXIT, under 60 s, against k x P_LOOP
    P = RV.P_LOOP
    loop = []
    for i, e in enumerate(thr):
        if e["kind"] != "thermal_down" or i + 1 >= len(thr) or thr[i + 1]["kind"] != "thermal_idle":
            continue
        d = (thr[i + 1]["ts"] - e["ts"]) / 1e6
        if d >= 60:
            continue
        k = int(round(d / P))
        loop.append({"time": hm(host(e["ts"]) * 1000), "d_s": round(d, 4), "k": k, "resid_ms": round((d - k * P) * 1000, 2),
                     "idle": not in_session(e["ts"])})
    # EXIT -> the next governor line
    ex = []
    for i, e in enumerate(ev):
        if e["kind"] != "thermal_idle":
            continue
        nxt = next((x for x in ev[i + 1:] if x["kind"] in RV.GOV), None)
        if nxt is not None:
            ex.append({"next": kinds[nxt["kind"]], "dt_s": round((nxt["ts"] - e["ts"]) / 1e6, 4), "idle": not in_session(e["ts"])})
    # ENTER lines and the governor line before each (an ENTER right after the SP's own idle call: no busy test)
    en = []
    for i, e in enumerate(ev):
        if e["kind"] != "thermal_down":
            continue
        prev = [x for x in ev[:i] if x["kind"] in RV.GOV]
        if prev:
            en.append({"prev": kinds[prev[-1]["kind"]], "dt_s": round((e["ts"] - prev[-1]["ts"]) / 1e6, 4),
                       "idle": not in_session(e["ts"])})
    # the SP's heartbeat ("SP Alive..", vTaskDelay(100000) ticks plus its body, main.c:471-476 of the 0.20.0 source), for
    # the tick in SP time: 1000 ticks is the thermal loop's sleep
    alive = set()
    for f in [os.path.join(d, "sp.bin") for d in dirs] + extra:
        alive |= {e["ts"] for e in RV.ring(f) if "SP Alive" in e.get("text", "")}
    alive = sorted(alive)
    hb = sorted((b - a) / 1e6 for a, b in zip(alive, alive[1:]) if 35e6 <= b - a <= 45e6)
    hb_med = hb[len(hb) // 2] if hb else None
    return {"thermal": lines, "crossings": cross, "loop": loop, "loop_period_s": P, "exit_next": ex, "enter_prev": en,
            "heartbeat": {"n": len(hb), "median_s": r1(hb_med, 4), "min_s": r1(hb[0], 4) if hb else None,
                          "max_s": r1(hb[-1], 4) if hb else None,
                          "tick_us": r1(hb_med / 100000 * 1e6, 1) if hb_med else None},
            "new_op_lines": A["newop"], "offset_fits": len(offs), "offset_fits_dropped_s": dropped,
            "offset_spread_ms_max": round(max((o[2] for o in offs), default=0.0), 2), "dumps": len(dirs) + len(extra)}


def runs(raw, session="p6038"):
    """The T-runs (and the ADD and RST runs) of the NAT-4 session, each with a telemetry excerpt around its launch."""
    d = os.path.join(raw, session)
    out = []
    for r in jl(os.path.join(d, "runs.jsonl")):
        if r.get("kind") not in ("T", "ADD", "RST"):
            continue
        o = r.get("obs") or {}
        t0, te = o.get("t0_ms"), o.get("t_end_ms")
        if t0 is None:
            continue
        rel = lambda k: None if o.get(k) is None else round((o[k] - t0) / 1000.0, 2)
        tel = sorted((s for s in jl(os.path.join(d, "tel-%s.jsonl" % r["idx"])) if s.get("t_ms") is not None),
                     key=lambda s: s["t_ms"])
        ex = [s for s in tel if t0 - 2000 <= s["t_ms"] <= te + 3000]
        ms = lambda s: (s.get("temp_c") or {}).get("minshire") or [None, None, None]
        out.append({"session": session, "idx": r["idx"], "kind": r["kind"], "name": r["name"], "block": r.get("block"),
                    "minions": r.get("minions"), "per_shire": r.get("per_shire"), "N": r.get("N"), "S": r.get("S"),
                    "K": r.get("K"), "valid": RV.run_valid(r), "t0_ms": t0, "time": hm(t0),
                    "t_up": rel("t_up"), "t_hi": rel("t_hi"), "t_hi2": rel("t_hi2"), "t_m": rel("t_m"),
                    "t_spm": rel("t_spm"), "t_down": rel("t_down"), "t_end": rel("t_end_ms"),
                    "trip_s": o.get("trip_s"), "censored": o.get("censored"), "separating": o.get("separating"),
                    "fits_mean": o.get("fits_mean"), "fits_max": o.get("fits_max"),
                    "hold_over_thr": o.get("g1h_max_over_thr"), "W_idle": r1(o.get("W_idle"), 2),
                    "W_800": r1(o.get("W_800"), 2),
                    # the one-shot statistics reset restarts the sensors' peak-hold marks: the high is the hottest
                    # reading since then (the first sample that reports it)
                    "reset_t": next((round((s["t_ms"] - t0) / 1000.0, 2) for s in tel if (s.get("resets") or 0) >= 1), None),
                    "tel": {"t": [round((s["t_ms"] - t0) / 1000.0, 2) for s in ex],
                            "mhz": [(s.get("mhz") or {}).get("minion") for s in ex],
                            "mean": [ms(s)[0] for s in ex], "high": [ms(s)[2] for s in ex],
                            "board_w": [r1(s.get("board_w"), 1) for s in ex]}})
    return out


def q1(R, idle, z1):
    T = [r for r in R if r["kind"] == "T" and r["valid"]]
    sep = [r for r in T if r["separating"]]
    rows = [{"idx": r["idx"], "name": r["name"], "block": r["block"], "minions": r["minions"],
             "down_minus_mean": r1(r["t_down"] - r["t_m"], 2) if r["t_down"] is not None and r["t_m"] is not None else None,
             "down_minus_high": r1(r["t_down"] - r["t_hi"], 2) if r["t_down"] is not None and r["t_hi"] is not None else None,
             "fits_mean": r["fits_mean"], "fits_max": r["fits_max"]} for r in sep]
    hold = [r for r in T if (r["hold_over_thr"] or 0) >= 2]
    it = idle["items"]
    sepc = [c for c in z1 if c.get("class") == "HMAX-SEP"]
    return {"window_s": [-0.3, 0.6], "separating": rows, "T_runs": len(T),
            "blocks": sorted({r["block"] for r in sep}),
            "g1t": {k: it["G1-T"][k] for k in ("separating", "blocks", "fit_mean", "fit_max")},
            "g1h": {"holds": len(hold), "runs": len(T), "max_over_thr": max((r["hold_over_thr"] or 0) for r in T),
                    "reducer": {k: it["G1-H"][k] for k in ("holds", "blocks", "max_over_thr")}},
            "idle_separating": [{k: c[k] for k in ("pass", "time", "mean", "high_min", "high_max", "samples", "state",
                                                  "quiet_before_s", "quiet_after_s")} for c in sepc],
            "i1": {k: it["I1"][k] for k in ("verdict", "clean_cycles", "hmax_sep", "out_stretches", "hmean_viol")}}


def q2(R, idle, prereg):
    g = prereg["g4"]
    blocks = {}
    for r in R:
        if r["kind"] != "T" or not r["valid"] or r["S"] != g["g4_S"] or r["name"][:5] not in ("INT16", "PER16"):
            continue
        blocks.setdefault(r["block"], {})[r["name"][:5]] = r
    rows = []
    for b, v in sorted(blocks.items()):
        i, p = v.get("INT16"), v.get("PER16")
        if not (i and p):
            continue

        def t800(x):
            if x["trip_s"] is not None:
                return x["trip_s"], False
            return round(x["t_end"] - x["t_up"], 3), True
        ti, ci = t800(i)
        tp, cp = t800(p)
        final = i["name"].endswith("@%d" % g["g4_per"])
        rows.append({"block": b, "minions": i["minions"], "int": i["name"], "per": p["name"], "t800_int": ti,
                     "t800_per": tp, "censored_int": ci, "censored_per": cp, "final_candidate": final,
                     "L": None if (ci and cp) else round(math.log(tp / ti), 4)})
    Ls = [x["L"] for x in rows if x["final_candidate"] and x["L"] is not None]
    n = len(Ls)
    m = sum(Ls) / n if n else None
    sd = math.sqrt(sum((x - m) ** 2 for x in Ls) / (n - 1)) if n > 1 else None
    G = idle["items"]["G4"]
    return {"blocks": rows, "n": n, "L_mean": r1(m, 4), "L_sd": r1(sd, 4),
            "ratio": [r1(math.exp(min(Ls)), 3), r1(math.exp(max(Ls)), 3)] if n else None,
            "L_P_mean": r1(G["L_P_mean"], 4), "reducer_L_mean": r1(G["L_mean"], 4), "reducer_blocks": G["blocks"],
            "L_pred": g["L_pred"], "b": g["b"], "n_val": g["inputs"]["n_val"], "g4s_min_blocks": g["g4s_min_blocks"],
            "g4_min_blocks": g["g4_min_blocks"], "inputs": g["inputs"]}


def incident(raw):
    d = os.path.join(raw, "p6041")
    L = jl(os.path.join(d, "launches.jsonl"))
    lifts = [x for x in L if x.get("kind") == "lift"]
    tel = sorted((s for s in jl(os.path.join(d, "tel-1.jsonl")) if s.get("t_ms")), key=lambda s: s["t_ms"])
    out = {"alert": jload(os.path.join(raw, "ALERT-MM-HANG.json")), "lifts": []}
    for k, x in enumerate(lifts):
        w = [s for s in tel if x["t_start_ms"] <= s["t_ms"] <= x["t_end_ms"]]
        mhz = sorted({(s.get("mhz") or {}).get("minion") for s in w} - {None})
        bw = [s.get("board_w") for s in w if s.get("board_w") is not None]
        out["lifts"].append({"n": k + 1, "start": hm(x["t_start_ms"]), "t_start_ms": x["t_start_ms"], "wall_s": x["wall_s"], "rc": x["rc"],
                             "gap_s": round((x["t_start_ms"] - lifts[k - 1]["t_end_ms"]) / 1000.0, 3) if k else None,
                             "samples": len(w), "mhz": mhz, "board_w": [r1(min(bw), 1), r1(max(bw), 1)] if bw else None})
    txt = gzip.open(os.path.join(d, "heater-1-pre.out.gz"), "rt", errors="replace").read()
    # one block of heater output per lift (each process prints the device configuration first)
    blocks = [b for b in txt.split("LOGGER NOT INITIALIZED:") if b.strip()]
    for k, b in enumerate(blocks[:len(out["lifts"])]):
        rd = [ln for ln in b.splitlines() if ln.startswith("device ready in ")]
        out["lifts"][k]["ready_s"] = float(rd[0].split()[3]) if rd else None
        out["lifts"][k]["message"] = next((ln.strip() for ln in b.splitlines()
                                           if ln.startswith(("device held", "kernel did not", "FAIL:"))), None)
        # the kernels the heater completed: launch -1 is its 20,000-iteration calibration kernel, then a stream of
        # short kernels (launch 0, 1, ...) until the lift's length; a lift is not one long kernel
        ks = []
        for ln in b.splitlines():
            if ln.startswith("SPARSITY "):
                try:
                    ks.append(json.loads(ln[len("SPARSITY "):]))
                except ValueError:
                    pass
        cal = next((x for x in ks if x.get("launch") == -1), None)
        stream = [x for x in ks if (x.get("launch") or 0) >= 0]
        x0 = lifts[k]["t_start_ms"]
        out["lifts"][k]["calib"] = None if not cal else {
            "t_start_ms": cal["t_start_ms"], "t_end_ms": cal["t_end_ms"], "start": hm(cal["t_start_ms"]) + ".%03d" % (cal["t_start_ms"] % 1000),
            "from_launch_s": round((cal["t_start_ms"] - x0) / 1000.0, 3), "wall_s": r1(cal.get("wall_s"), 4),
            "ghz": cal.get("ghz"), "ok": cal.get("ok"), "iters": cal.get("iters")}
        out["lifts"][k]["stream"] = {"kernels": len(stream),
                                     "wall_s": [r1(min(x["wall_s"] for x in stream), 3), r1(max(x["wall_s"] for x in stream), 3)] if stream else None,
                                     "ghz": [min(x["ghz"] for x in stream), max(x["ghz"] for x in stream)] if stream else None,
                                     "iters": sorted({x.get("iters") for x in stream}) if stream else None}
    # the clock around the second lift: at its process start, and the idle reset the host saw after it
    if len(lifts) > 1:
        t2 = lifts[1]["t_start_ms"]
        at = [s for s in tel if s["t_ms"] <= t2]
        aft = [s for s in tel if s["t_ms"] > t2]
        first600 = next((s for s in aft if (s.get("mhz") or {}).get("minion") == 600), None)
        idle_from = next((s for s in aft if (s.get("board_w") or 99) < 27), None)
        c2 = out["lifts"][1].get("calib") or {}
        out["lift2"] = {"mhz_at_start": (at[-1].get("mhz") or {}).get("minion") if at else None,
                        "first_600_s": round((first600["t_ms"] - t2) / 1000.0, 2) if first600 else None,
                        "first_600_at": (hm(first600["t_ms"]) + ".%03d" % (first600["t_ms"] % 1000)) if first600 else None,
                        # the calibration kernel ran and returned ok after the host had already read 600 MHz; the
                        # kernel that never completed is the next one, the first of the stream
                        "calib_after_first_600_ms": (c2["t_start_ms"] - first600["t_ms"]) if (first600 and c2) else None,
                        "hung_kernel": "the first kernel of the stream, after the calibration kernel" if c2 and c2.get("ok")
                        and not out["lifts"][1]["stream"]["kernels"] else None,
                        "board_idle_from_s": round((idle_from["t_ms"] - t2) / 1000.0, 2) if idle_from else None,
                        "mhz_after_1s": sorted({(s.get("mhz") or {}).get("minion") for s in aft if s["t_ms"] >= t2 + 1000
                                                and s["t_ms"] <= lifts[1]["t_end_ms"]})}
    out["heater_messages"] = [m for m in ("device held for 7.46 s", "kernel did not finish within 6 s, aborting the stream",
                                          "Couldn't use the HPSQ. Perhaps the Master Minion is hanged?") if m in txt]
    out["hpsq_failures"] = txt.count("Couldn't use the HPSQ")
    # every heater launch of the night before the hang, and how many ran
    before = []
    for s in sorted(glob.glob(os.path.join(raw, "p[4-6][0-9][0-9][0-9]", "launches.jsonl"))):
        before += [x for x in jl(s) if x.get("t_start_ms", 0) < lifts[1]["t_start_ms"]]
    out["launches_before"] = len(before)
    out["launches_before_rc0"] = sum(1 for x in before if x.get("rc") == 0)
    # the card's error events in the host's kernel log (incident/kernel-log.txt, an excerpt of dmesg -T; its wall times
    # are approximate): the SP runtime errors, with the driver's running count
    kl = os.path.join(os.path.dirname(raw), "incident", "kernel-log.txt")
    ev, cur = [], None
    for line in (open(kl).read().split("\n\n")[0].splitlines() if os.path.exists(kl) else []):
        if "Error Event Detected" in line and line.startswith("["):
            cur = {"when": line[1:line.index("]")]}
            ev.append(cur)
        elif cur is not None and ":" in line and not line.startswith("#"):
            k, v = line.split(":", 1)
            cur[k.strip().lower()] = v.strip()
    # wall times from the boot-relative stamps (incident/kernel_events.py: interpolated between the audit records around
    # each stamp); dmesg -T's "when" is late by up to about 10 s by the 28th
    ke = os.path.join(os.path.dirname(raw), "incident", "kernel_events.py")
    cal = []
    if os.path.exists(ke):
        import subprocess
        cal = json.loads(subprocess.run([sys.executable, "-B", ke, "--json"], check=True, capture_output=True, text=True).stdout)
    sp = [e for e in ev if e.get("desc") == "SP Runtime Error"]
    cs = [c for c in cal if c.get("desc") == "SP Runtime Error"]
    if len(cs) == len(sp):
        for e, c in zip(sp, cs):
            assert c["syndrome"] == e.get("syndrome")
            e.update({"stamp_s": c["stamp_s"], "pdt": c["pdt"], "pm_s": c["pm_s"]})
    out["kernel_log"] = sp
    if sp and sp[-1].get("pdt") and len(lifts) > 1:
        t6 = datetime.datetime.strptime(sp[-1]["pdt"], "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=TZ).timestamp() * 1000
        c2 = out["lifts"][1].get("calib") or {}
        out["kernel_log_last"] = {"pdt": sp[-1]["pdt"][11:], "pm_s": sp[-1]["pm_s"],
                                  "after_lift2_launch_s": round((t6 - lifts[1]["t_start_ms"]) / 1000.0, 2),
                                  "after_lift2_calib_end_s": round((t6 - c2["t_end_ms"]) / 1000.0, 2) if c2 else None}
    after = [jload(os.path.join(raw, p, "z1.json")) for p in ("p1111", "p1112")]
    out["sp_after"] = [{"time": hm(z["t_ms"]), "mhz": z["mhz"], "board_w": z["board_w"], "mean": z["reading_c"],
                        "threshold_c": z["threshold_c"]} for z in after if z]
    return out


def host_sensors(raw):
    """The host's own temperature sensors over the night (hostlog.sh, sensors -j every 60 s): the room-side readings."""
    rows = jl(os.path.join(raw, "host-sensors.jsonl"))
    out = {"samples": len(rows)}
    if not rows:
        return out
    out["from"], out["to"] = hm(rows[0]["t_ms"]), hm(rows[-1]["t_ms"])
    pick = {"acpi_1": ("acpitz-acpi-0", "temp1", "temp1_input"), "acpi_2": ("acpitz-acpi-0", "temp2", "temp2_input"),
            "nvme": ("nvme-pci-0300", "Composite", "temp1_input"), "cpu_package": ("coretemp-isa-0000", "Package id 0", "temp1_input")}
    for k, (a, b, c) in pick.items():
        v = [((r.get("sensors") or {}).get(a) or {}).get(b, {}).get(c) for r in rows]
        v = [x for x in v if x is not None]
        if v:
            out[k] = [min(v), max(v)]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data", required=True)
    ap.add_argument("--out")
    ap.add_argument("--merge", nargs="*", default=[])
    a = ap.parse_args()
    raw = os.path.join(a.data, "raw")
    idle = json.load(open(os.path.join(a.data, "reductions", "dev-idle.json")))
    dev = json.load(open(os.path.join(a.data, "reductions", "dv2-dev.json")))
    prereg_json = os.path.join(ROOT, "tools", "claims-v3", "dv2v", "prereg-val.json")
    if not os.path.exists(prereg_json):
        prereg_json = os.path.join(a.data, "plan", "prereg-val.json")
    prereg = json.load(open(prereg_json))
    z1 = z1_cycles(raw, idle)
    R = runs(raw)
    G = governor_lines(raw)
    z = jload(os.path.join(raw, "p1001", "z1.json"))
    up = z["uptime"]
    up_days = up["day"] + up["hours"] / 24 + up["mins"] / 1440
    res = {"at": hm(z["t_ms"]), "uptime_days": round(up_days, 3),
           "thermal_down": {k: z["residency"]["4"][k] for k in ("cumulative_us", "maximum_us")},
           "power_up": {k: z["residency"]["2"][k] for k in ("cumulative_us",)},
           # the counter's change between two watch cycles less the episodes the ring recorded (reduce_val's I6 rows);
           # "busy" rows span a heating session of ours or a kernel, whose ring lines a sampler may have overwritten
           "vs_episodes": [{k: x[k] for k in ("from", "to", "n_ep", "diff_ms", "busy")} for x in idle["residency"]
                           if x["n_ep"] >= 1 or abs(x["diff_ms"]) >= 5]}
    plan = os.path.join(a.data, "plan")
    pv = os.path.join(plan, "PREREG-VAL.md")
    lock = os.path.join(plan, "LOCK.sha256")
    it = idle["items"]
    card = {"card": CARD, "threshold_c": sorted({c["threshold_c"] for c in z1 if not c.get("skipped")}),
            "z1": z1, "sessions": sessions(raw), "lines": G, "runs": R, "q1": q1(R, idle, z1), "q2": q2(R, idle, prereg),
            "bands": {k: dev["host_bands"][k] for k in ("G2-C", "G2-D", "G2-U")},
            "g3": {"launch_to_800": {k: it["G3-L"][k] for k in ("n", "median_s", "max_s")},
                   "end_to_600": {k: it["G3-I"][k] for k in ("n", "max_s")}},
            "residency": res, "incident": incident(raw), "host_sensors": host_sensors(raw)}
    pl = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "dv2", "placements.json")))
    placements = {"grid": pl["grid_rows_r0_r5_cols_c1_c6"],
                  "groups": {k: pl["groups"][k]["shires"] for k in ("B4C", "INT16", "PER16", "UNI32")},
                  "source": "tools/claims-v3/dv2/placements.json (the shire grid as inferred for the die frame)"}
    out = {"label": LABEL, "placements": placements, "source": os.path.relpath(a.data, ROOT) if os.path.isabs(a.data) else a.data,
           "tz": "PDT (UTC-7)", "cards": {CARD: card},
           "prereg": {"file": "plan/PREREG-VAL.md", "sha256": sha(pv), "lock_sha256": sha(lock),
                      "frozen": "28 Sep 2026, about 03:15 PDT", "not_before": "2026-09-28T12:00 PDT",
                      "g4": {k: prereg["g4"][k] for k in ("L_pred", "b", "g4s_min_blocks", "g4_min_blocks", "g4_registered")}},
           "decisions": [{k: x.get(k) for k in ("t_ms", "decision", "what")} for x in dev.get("dev_log", [])]}
    path = a.out or os.path.join(a.data, "dv2.json")
    json.dump(out, open(path, "w"), indent=1)
    q, c2, L = card["q1"], card["q2"], card["lines"]
    print(f"wrote {path}: {len([c for c in z1 if not c.get('skipped')])} watch cycles, {len(R)} runs, "
          f"{len(L['thermal'])} thermal lines in {len(L['crossings'])} crossings")
    print("printed: ENTER " + str(sorted({x['T'] for x in L['thermal'] if x['kind'] == 'ENTER'})) +
          " x%d, EXIT " % sum(x['kind'] == 'ENTER' for x in L['thermal']) +
          str(sorted({x['T'] for x in L['thermal'] if x['kind'] == 'EXIT'})) + " x%d" % sum(x['kind'] == 'EXIT' for x in L['thermal']))
    print(f"loop (P {L['loop_period_s']} s): " + ", ".join(f"{x['d_s']} (k {x['k']}, {x['resid_ms']:+} ms{'' if x['idle'] else ', session'})" for x in L["loop"]))
    print("EXIT -> next: " + str(sorted({x['next'] for x in L['exit_next']})) + f" x{len(L['exit_next'])}; dt " +
          ", ".join(f"{x['dt_s']}{'' if x['idle'] else ' (session)'}" for x in sorted(L["exit_next"], key=lambda x: x["dt_s"])))
    print("ENTER <- previous: " + ", ".join(f"{x['prev']}{'' if x['idle'] else ' (session)'}" for x in L['enter_prev']))
    print("crossings: " + "; ".join(f"{c['time']} {c['enter']}/{c['exit']} {c['dur_s']} s ends {c['ends']}{'' if c['idle'] else ' (session)'}" for c in L["crossings"]))
    print(f"SP heartbeat: {L['heartbeat']}")
    print(f"SP-to-host fits: {L['offset_fits']} kept (spread <= {L['offset_spread_ms_max']} ms), dropped (s from the median): {L['offset_fits_dropped_s']}")
    print("Q1 separating: " + "; ".join(f"{r['name']} b{r['block']}: down-mean {r['down_minus_mean']}, down-high {r['down_minus_high']}" for r in q["separating"]) +
          f"; holds {q['g1h']['holds']} of {q['g1h']['runs']} (max over thr {q['g1h']['max_over_thr']})")
    print("Q2 blocks: " + "; ".join(f"b{b['block']} ({b['minions']}): INT {b['t800_int']}{'+' if b['censored_int'] else ''} PER {b['t800_per']}{'+' if b['censored_per'] else ''} L {b['L']}" for b in c2["blocks"]) +
          f"; L mean {c2['L_mean']} sd {c2['L_sd']} (reducer {c2['reducer_L_mean']}), L_P {c2['L_P_mean']}, ratio {c2['ratio']}")
    print(f"PREREG-VAL sha256 {out['prereg']['sha256']}; lock {out['prereg']['lock_sha256']}")
    for p in a.merge:
        d = json.load(open(p))
        d["dv2"] = out
        json.dump(d, open(p, "w"), separators=(",", ":"))
        print("merged dv2 block into", p)


if __name__ == "__main__":
    main()
