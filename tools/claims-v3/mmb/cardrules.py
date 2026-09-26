#!/usr/bin/env python3
"""V3-MMB: which telemetry clock rule applies on which card (the four-card amendment; README.md "Four cards").

Imported by mmbench_power_v3.py (finish), passcheck.py and reduce.py, so the block's re-run decision and the reducer
apply one rule. No card access.

 - aifoundry2 (registered; governor free): its code paths in finish, passcheck and reduce are the registered ones and do
   not come from here: an E1 timed launch is dropped if a telemetry sample inside it (for a launch shorter than the
   sampling interval, the samples on either side) is off 600 MHz; a load-step pass is dropped if ANY sample is off 600.
 - aifoundry3 (registered; pinned at 600 MHz by a boot service): no telemetry clock rule (implied_ghz only).
 - Every other governor-free card (aifoundry1-c0, aifoundry1-c1): the "busy" rule. Only BUSY samples count: a sample
   whose time lies inside a launch's window [t_start_ms, t_end_ms] (MMBENCH / MEMPROBE lines). Idle brackets never drop
   anything: aifoundry1-c0 idles at 300 MHz in a low_power state between kernels, and a rule over idle samples would
   drop every burst there. A busy sample below 600 MHz in the first RAMP_S after a process's first launch starts is the
   clock rising from that idle state (the firmware may report it up to a management pass late): it is recorded as
   "ramp", not a drop. Any other busy sample off 600 MHz (a lift to 700/800 on a cool die, a step down later in a burst)
   drops the launch (E1) or the pass (load step). A launch with no sample inside it has no telemetry verdict (its
   implied_ghz, the registered rule for every card, still applies).
 - E1 power values (MMB-c..f) on a "busy" card: kept if every timed launch is kept, or if the only dropped launch is
   launch 0 and it was dropped only for implied_ghz BELOW 0.595 (a clock that rose from the idle state inside the
   registered 1 s settle, before the power window starts). On the registered cards: every launch kept, as registered.
"""
import glob
import json
import os

REGISTERED = ("aifoundry2", "aifoundry3")
CAMPAIGN = ("aifoundry2", "aifoundry3", "aifoundry1-c0", "aifoundry1-c1")
GHZ = (0.595, 0.605)
RAMP_S = 1.0          # = the registered E1 settle (mmbench-power.py --settle 1): the power window starts after it
IDLE_AFTER_S = 5.0    # x1_reduce's "idle after" bracket: the last 5 s of cool1


def gov_free(card, recorded=None):
    """aifoundry3 is pinned, aifoundry2 is free (registered); any other card: as the block recorded it (order.json
    gov_free, from lib.sh's GOV_FREE), else free (lib.sh: every card but aifoundry3)."""
    if card == "aifoundry3":
        return False
    if card == "aifoundry2":
        return True
    return True if recorded is None else bool(recorded)


def rule(card, recorded=None):
    """'a2' (the registered aifoundry2 rule), 'pinned' (no telemetry clock rule) or 'busy'."""
    if card == "aifoundry2":
        return "a2"
    return "busy" if gov_free(card, recorded) else "pinned"


def short(card):
    """x1_reduce's card code: a2, a3, a1c0, a1c1."""
    return {"aifoundry2": "a2", "aifoundry3": "a3"}.get(card, card.replace("aifoundry", "a").replace("-", ""))


def mhz_of(s):
    return (s.get("mhz") or {}).get("minion")


def busy_launch(q, tel_f, ramp_t0_ms):
    """The busy rule on one launch q (t_start_ms, t_end_ms); tel_f: samples with a clock reading; ramp_t0_ms: the start
    of the process's first launch (samples below 600 MHz before ramp_t0_ms + RAMP_S are ramp, not drops)."""
    inside = [s for s in tel_f if q["t_start_ms"] <= s["t_ms"] <= q["t_end_ms"]]
    off, ramp = set(), set()
    for s in inside:
        m = mhz_of(s)
        if m == 600:
            continue
        if m < 600 and s["t_ms"] < ramp_t0_ms + RAMP_S * 1000:
            ramp.add(m)
        else:
            off.add(m)
    return {"mhz": sorted({mhz_of(s) for s in inside}), "samples": len(inside), "off": sorted(off),
            "ramp": sorted(ramp), "drop": bool(off)}


def e1_power_kept(card, runs, recorded=None):
    """(kept, note) for a workload's power values; runs carry 'launch', 'implied_ghz' and their drop reasons ('drop' or
    '_drop'). Registered cards and pinned cards: every timed launch kept."""
    reasons = lambda q: q.get("drop", q.get("_drop")) or []
    dropped = [q for q in runs if reasons(q)]
    if not dropped:
        return True, None
    if rule(card, recorded) != "busy":
        return False, None
    q = dropped[0]
    if len(dropped) == 1 and q["launch"] == 0 and reasons(q) == ["implied_ghz"] and q["implied_ghz"] < GHZ[0]:
        return True, (f"launch 0 dropped (implied_ghz {q['implied_ghz']:.4f}: the clock rose from the idle state), "
                      "before the power window; power values kept")
    return False, None


def _lines(path, tag):
    out = []
    if os.path.exists(path):
        for l in open(path, errors="replace"):
            if l.startswith(tag + " "):
                try:
                    x = json.loads(l.split(" ", 1)[1])
                except ValueError:
                    continue
                if "t_start_ms" in x and "t_end_ms" in x:
                    out.append((int(x["t_start_ms"]), int(x["t_end_ms"])))
    return sorted(out)


def load_step_processes(td):
    """The load step's device processes, each a sorted list of launch windows: mm-<i>.out (MMBENCH, every launch of
    the process) and dram-<i>.out (MEMPROBE, the --loop timing launch -1 and every timed launch)."""
    procs = []
    for f in sorted(glob.glob(os.path.join(td, "mm-*.out"))):
        procs.append({"file": os.path.basename(f), "launches": _lines(f, "MMBENCH")})
    for f in sorted(glob.glob(os.path.join(td, "dram-*.out"))):
        procs.append({"file": os.path.basename(f), "launches": _lines(f, "MEMPROBE")})
    return [p for p in procs if p["launches"]]


def load_step_clock(td, tel, phases):
    """The busy rule on one load step, and the clock of every idle bracket (for every card; only a 'busy' card's pass
    validity comes from here). tel: telemetry samples; phases: thermal-phases.jsonl records."""
    procs = load_step_processes(td)
    wins = [(a, z, p["launches"][0][0]) for p in procs for a, z in p["launches"]]
    tel_f = sorted((s for s in tel if mhz_of(s) is not None), key=lambda s: s["t_ms"])
    marks = sorted((m["t_ms"], m["phase"]) for m in phases)
    t_mark = {ph: t for t, ph in marks}

    def phase_of(t):
        name = "before"
        for tm, ph in marks:
            if t >= tm:
                name = ph
        return name

    busy, off, ramp = 0, set(), set()
    by_phase = {}
    idle_after = set()
    for s in tel_f:
        t, m = s["t_ms"], mhz_of(s)
        w = [x for x in wins if x[0] <= t <= x[1]]
        kind = "busy" if w else "idle"
        ph = by_phase.setdefault(phase_of(t), {"idle": set(), "busy": set()})
        ph[kind].add(m)
        if w:
            busy += 1
            if m != 600:
                if m < 600 and t < w[0][2] + RAMP_S * 1000:
                    ramp.add(m)
                else:
                    off.add(m)
        elif "dram" in t_mark and t_mark["dram"] - IDLE_AFTER_S * 1000 <= t < t_mark["dram"]:
            idle_after.add(m)
    idle0 = sorted(by_phase.get("idle0", {}).get("idle", set()))
    idle_all = sorted(set().union(*[v["idle"] for v in by_phase.values()])) if by_phase else []
    return {"processes": len(procs), "launch_windows": len(wins), "busy_samples": busy, "busy_off_600": sorted(off),
            "busy_ramp": sorted(ramp), "valid_busy_rule": busy > 0 and not off,
            "idle_mhz": idle_all, "idle0_mhz": idle0, "idle_after_mhz": sorted(idle_after),
            "mhz_by_phase": {k: {"idle": sorted(v["idle"]), "busy": sorted(v["busy"])} for k, v in by_phase.items()}}
