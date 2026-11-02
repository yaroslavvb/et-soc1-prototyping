#!/usr/bin/env python3
"""Q134(a): aifoundry2's over-power alarm (kinds page section 11 item 14) from the POWER_SAFE residency counter.

Reads only committed files: every throttle-residency read (DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES) in the lab's
data dirs since aifoundry2's service processor started on 26 Oct 2026, the same dirs' telemetry, and the two read-only
host reads in host/ (driver event counters and kernel-log ET events, 1 Nov 2026 19:14-19:15 PST).

Run from the top of the repository:  python3 docs/reports/data/2026-11-01-q134a-alarm-residency/q134a_residency.py
Writes reads.csv, sessions.json, runs-80w.txt, replay-card0.json, replay-card0.txt, counters.txt, continuity.txt and
results.json next to this file. Post hoc desk analysis: nothing here was pre-registered.

Corrected 1 Nov 2026 (PST), after verification: the telemetry tally counts each sample once, keyed on (t_ms, board_w)
(E111's CAM-RED/ and CAM/tel.jsonl.raw repeat CAM/'s samples), and leaves out the per-launch summary lines, which carry
a board_w but no t_ms. It now covers every aifoundry2 card session since the 26 Oct start with committed data: E68 and
E72 have 10 Hz telemetry and were missing, and E66 (an idle run) has none. The residency de-duplication is a guard
only: no residency list appears in two files, and results.json records how many rows it dropped (0).
"""
import csv, glob, gzip, itertools, json, os, re, sys
from collections import Counter, defaultdict

RID = itertools.count()
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
PDT, PST = timezone(timedelta(hours=-7)), timezone(timedelta(hours=-8))
DST_END = datetime(2026, 11, 1, 9, 0, tzinfo=timezone.utc)  # 02:00 PDT


def local(ms):
    t = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    z, n = (PDT, "PDT") if t < DST_END else (PST, "PST")
    return t.astimezone(z).strftime("%a %d %b %H:%M:%S ") + n


# Residency-reading sessions (host from each dir's own manifest) and the sessions with telemetry only.
RES_DIRS = [
    ("E69", "2026-10-27-e69-governor-knob", "aifoundry2"),
    ("E80", "2026-10-31-e80-kinds-speed", "aifoundry2"),
    ("E83", "2026-10-31-e83-kinds-speed-rest", "aifoundry2"),
    ("E87", "2026-10-31-e87-real-tensors-speed", "aifoundry2"),
    ("E96", "2026-11-01-e96-real-tensors-speed", "aifoundry2"),
    ("E98", "2026-11-01-e98-heat-path-drift", "aifoundry2"),
    ("E100", "2026-11-01-e100-idle-reset", "aifoundry2"),
    ("E101", "2026-11-01-e101-real-matmul/aifoundry2", "aifoundry2"),
    ("E105", "2026-11-01-e105-gemm-layout/aifoundry2", "aifoundry2"),
    ("E111", "2026-11-01-e111-heat-steady", "aifoundry2"),
    ("E77", "2026-11-01-e77-rail-one-temperature/raw", "aifoundry2"),
    ("E84", "2026-10-31-e84-speed-aifoundry1-card0", "aifoundry1 card 0"),
    ("E114", "2026-11-01-e114-card0-replicates", "aifoundry1 card 0"),
]
TEL_DIRS = [  # every aifoundry2 card session since the 26 Oct SP start with committed data, in time order
    # (E68, E66, E72, E73 and E85 read no residency; E66 is an idle run with no board_w telemetry)
    ("E68", "2026-10-27-e68-stage-map"), ("E66", "2026-10-27-e66-idle-long"),
    ("E69", "2026-10-27-e69-governor-knob"), ("E72", "2026-10-27-e72-600mhz"), ("E73", "2026-10-27-e73-camera-frequencies"),
    ("E80", "2026-10-31-e80-kinds-speed"), ("E83", "2026-10-31-e83-kinds-speed-rest"),
    ("E85", "2026-10-31-e85-camera-kinds"), ("E87", "2026-10-31-e87-real-tensors-speed"),
    ("E96", "2026-11-01-e96-real-tensors-speed"), ("E98", "2026-11-01-e98-heat-path-drift"),
    ("E100", "2026-11-01-e100-idle-reset"), ("E101", "2026-11-01-e101-real-matmul"),
    ("E105", "2026-11-01-e105-gemm-layout"), ("E111", "2026-11-01-e111-heat-steady"),
    ("E77", "2026-11-01-e77-rail-one-temperature"),
]
CARD0_75_ON_A2 = 2.46 + 1.117 * 75  # Q132(g)'s cross-card line a2 = 2.46 + 1.117 c0 (q132-governor-desk README :16, :87)


def walk(o, ctx, out, path):
    if isinstance(o, dict):
        t = o.get("t_ms", ctx.get("t_ms"))
        tag = o.get("tag") or o.get("run") or o.get("label") or ctx.get("tag")
        c2 = {"t_ms": t, "tag": tag}
        if isinstance(o.get("residency"), list):
            rid = next(RID)  # one residency list = one read
            for r in o["residency"]:
                if isinstance(r, dict) and "state" in r:
                    out.append(dict(t_ms=r.get("t_ms", t), rid=rid, tag=tag, file=path, state=r["state"], rc=r.get("rc"),
                                    cumulative_us=r.get("cumulative_us"), average_us=r.get("average_us"),
                                    maximum_us=r.get("maximum_us"), minimum_us=r.get("minimum_us")))
        for k, v in o.items():
            if k != "residency":
                walk(v, c2, out, path)
    elif isinstance(o, list):
        for v in o:
            walk(v, ctx, out, path)


def load_json_any(fp):
    with open(fp) as f:
        txt = f.read()
    try:
        return [json.loads(txt)]
    except ValueError:
        return [json.loads(l) for l in txt.splitlines() if l.strip().startswith("{")]


DROPPED_RES_ROWS = [0]  # residency rows the guard below dropped (0: every residency list is distinct across files)


def collect_reads():
    rows, seen = [], set()
    for exp, sub, host in RES_DIRS:
        for fp in sorted(glob.glob(os.path.join(DATA, sub, "**", "*.json*"), recursive=True)):
            if fp.endswith(".gz"):
                continue
            got = []
            for doc in load_json_any(fp):
                walk(doc, {}, got, os.path.relpath(fp, DATA))
            for g in got:
                key = (host, g["t_ms"], g["state"], g["cumulative_us"], g["rc"])
                if key in seen:  # a guard against a read copied into a second file; it drops nothing in these dirs
                    DROPPED_RES_ROWS[0] += 1
                    continue
                seen.add(key)
                g.update(exp=exp, host=host)
                rows.append(g)
    # one row per read: the states asked in one residency list
    reads = defaultdict(dict)
    for g in rows:
        reads[(g["host"], g["exp"], g["tag"], g["rid"])][g["state"]] = g
    out = []
    for (host, exp, tag, _), st in reads.items():
        t = min(v["t_ms"] for v in st.values())
        f = sorted(set(v["file"] for v in st.values()))[0]
        r = dict(host=host, exp=exp, tag=tag, file=f, t_ms=t, local=local(t))
        for s in (2, 3):
            v = st.get(s)
            r[f"raw{s}_rc"] = v["rc"] if v else None
            for k in ("cumulative_us", "average_us", "maximum_us", "minimum_us"):
                r[f"raw{s}_{k}"] = v[k] if v else None
        for s in (4, 5, 6):
            r[f"raw{s}_rc"] = st[s]["rc"] if s in st else None
        out.append(r)
    out.sort(key=lambda r: (r["host"], r["t_ms"]))
    return out


def tel_tally():
    sessions, runs = {}, []
    seen = set()  # (t_ms, board_w): one sample, counted once wherever it is repeated
    for exp, sub in TEL_DIRS:
        files = [f for f in glob.glob(os.path.join(DATA, sub, "**", "*.jsonl*"), recursive=True)
                 if "aifoundry3" not in f and "aifoundry1" not in f]
        S = dict(files=0, n=0, max_board_w=None, max_avg_w=None, ge75=0, ge80=0, ge84=0, ge85=0, ge_card0_75=0, ge100=0,
                 avg_ge70=0, avg_ge75=0, mhz300=0, t_first=None, t_last=None, duplicate_lines=0,
                 launch_lines_no_t_ms=0, launch_lines_max_w=None, duplicates_by_file={})
        # primaries first, so a repeat is charged to the copy: E111's CAM-RED/tel.jsonl.gz is a byte-for-byte copy of
        # CAM/tel.jsonl.gz (reduce_hm.py's output dir), and CAM/tel.jsonl.raw an earlier partial dump of the same stream
        for f in sorted(files, key=lambda p: (("-RED" + os.sep) in p or p.endswith(".raw"), p)):
            op = gzip.open if f.endswith(".gz") else open
            R = dict(n=0, max_board_w=None, max_avg_w=None)
            with op(f, "rt") as fh:
                for line in fh:
                    if '"board_w"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except ValueError:
                        continue
                    b = d.get("board_w")
                    if not isinstance(b, (int, float)):
                        continue
                    t = d.get("t_ms")
                    if t is None:  # a per-launch summary line (board_w with no time of its own), not a sample
                        S["launch_lines_no_t_ms"] += 1
                        S["launch_lines_max_w"] = b if S["launch_lines_max_w"] is None else max(S["launch_lines_max_w"], b)
                        continue
                    if (t, b) in seen:  # the same sample already counted from another file
                        S["duplicate_lines"] += 1
                        k = os.path.relpath(f, DATA)
                        S["duplicates_by_file"][k] = S["duplicates_by_file"].get(k, 0) + 1
                        continue
                    seen.add((t, b))
                    S["n"] += 1; R["n"] += 1
                    S["t_first"] = t if S["t_first"] is None else min(S["t_first"], t)
                    S["t_last"] = t if S["t_last"] is None else max(S["t_last"], t)
                    for X in (S, R):
                        if X["max_board_w"] is None or b > X["max_board_w"]:
                            X["max_board_w"] = b
                    a = (d.get("sp") or {}).get("board_avg_w")
                    if isinstance(a, (int, float)):
                        for X in (S, R):
                            if X["max_avg_w"] is None or a > X["max_avg_w"]:
                                X["max_avg_w"] = a
                        S["avg_ge70"] += a >= 70; S["avg_ge75"] += a >= 75
                    S["ge75"] += b >= 75; S["ge80"] += b >= 80; S["ge84"] += b >= 84; S["ge85"] += b >= 85
                    S["ge_card0_75"] += b >= CARD0_75_ON_A2; S["ge100"] += b >= 100
                    S["mhz300"] += (d.get("mhz") or {}).get("minion") == 300
            if R["n"]:
                S["files"] += 1
                runs.append(dict(exp=exp, file=os.path.relpath(f, DATA), **R))
        S["first"] = local(S["t_first"]) if S["t_first"] else None
        S["last"] = local(S["t_last"]) if S["t_last"] else None
        sessions[exp] = S
    return sessions, runs


def parse_host(fp):
    txt = open(fp).read()
    H = {"counters": {}, "events": [], "kinds": {}}
    m = re.search(r"== host (\S+) (.+?) epoch (\d+)", txt); H["host"], H["date"], H["epoch"] = m.group(1), m.group(2), int(m.group(3))
    m = re.search(r"uptime: ([0-9.]+) \S+\s+btime: (\d+)", txt); H["uptime_s"], H["btime"] = float(m.group(1)), int(m.group(2))
    for blk in re.finditer(r"== /sys/bus/pci/devices/(\S+)/err_stats/ce_count\n((?:\w+:\s+\d+\n)+)", txt):
        H["counters"][blk.group(1)] = {k: int(v) for k, v in re.findall(r"(\w+):\s+(\d+)", blk.group(2))}
    for n, dev, kind in re.findall(r"^\s+(\d+) (\S+): \| (.+)$", txt, re.M):
        H["kinds"][dev + " | " + kind] = int(n)
    for line in txt.splitlines():
        m = re.match(r"^([0-9.]+) \| (\S+): \| (.*?) \| (.*)$", line.strip())
        if m:
            H["events"].append((float(m.group(1)), m.group(2), m.group(3), m.group(4)))
    m = re.search(r"Runtime Error Count Beyond Threshold: (\d+)", txt)
    H["last_sp_runtime_error_count"] = int(m.group(1)) if m else None
    m = re.search(r"^events: (\d+)$", txt, re.M)
    H["events_in_log"] = int(m.group(1)) if m else None
    m = re.search(r"^first: \[ *([0-9.]+)\]", txt, re.M)
    H["log_first_mono_s"] = float(m.group(1)) if m else None
    return H


def replay_card0(H, reads):
    T = [(ts, int(re.search(r"(\d+) msec", s).group(1))) for ts, d, k, s in H["events"]
         if d == "0000:01:00.0" and k.startswith("Thermal Throttling")]
    P = [(ts, float(re.search(r"current = ([0-9.]+) W", s).group(1))) for ts, d, k, s in H["events"]
         if d == "0000:01:00.0" and k.startswith("Power Management")]
    T.sort(); P.sort()
    # thermal_pwr_mgmt.c @836a4ab :351-393 update_residency: cumulative += t; average = (average + t) / 2 (integer;
    # first episode sets it); maximum; minimum (0 = unset)
    cum = avg = mx = mn = 0
    states = {0: dict(n=0, cumulative_us=0, average_us=0, maximum_us=0, minimum_us=0)}
    for k, (ts, t) in enumerate(T):
        cum += t; avg = (avg + t) // 2 if avg else t; mx = max(mx, t); mn = t if mn == 0 else min(mn, t)
        states[cum] = dict(n=k + 1, cumulative_us=cum, average_us=avg, maximum_us=mx, minimum_us=mn)
    rows, exact, steps = [], 0, []
    for r in [r for r in reads if r["host"] == "aifoundry1 card 0"]:
        s = states.get(r["raw3_cumulative_us"])
        ok = s is not None and all(s[k] == r["raw3_" + k] for k in ("cumulative_us", "average_us", "maximum_us", "minimum_us"))
        exact += ok
        rows.append(dict(exp=r["exp"], tag=r["tag"], local=r["local"], raw3_cumulative_us=r["raw3_cumulative_us"],
                         episodes=s["n"] if s else None, exact=ok))
        if not steps or steps[-1]["raw3_cumulative_us"] != r["raw3_cumulative_us"]:
            steps.append(rows[-1])
    per, j, prev = [], 0, -1.0
    lags, lags_if_ms = [], []
    for ts, t in T:
        inside = [p for p in P if prev < p[0] <= ts]
        per.append(len(inside))
        if inside:
            lags.append((ts - inside[0][0]) * 1e6 - t)  # the logged duration read as microseconds
            lags_if_ms.append((ts - inside[0][0]) - t / 1e3)  # the same, read as the "msec" the syndrome prints (s)
        prev = ts
    lags.sort()
    return dict(throttle_time_events=len(T), pmic_events=len(P), sum_us=cum, mean_us=round(cum / len(T)),
                min_us=mn, max_us=mx, reads=len(rows), exact_reads=exact, steps=steps,
                pmic_per_episode=dict(sorted(Counter(per).items())), episodes_without_pmic=per.count(0),
                pmic_after_last_episode=len([p for p in P if p[0] > T[-1][0]]),
                lag_us_median=round(lags[len(lags) // 2]), lag_us_range=[round(lags[0]), round(lags[-1])],
                lag_if_msec_s_first3=[round(x, 1) for x in lags_if_ms[:3]],
                lag_if_msec_s_range=[round(min(lags_if_ms), 1), round(max(lags_if_ms), 1)],
                pmic_watts=dict(sorted(Counter(w for _, w in P).items())), rows=rows)


def main():
    reads = collect_reads()
    with open(os.path.join(HERE, "reads.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(reads[0].keys()))
        w.writeheader(); w.writerows(reads)
    a2 = [r for r in reads if r["host"] == "aifoundry2"]
    c0 = [r for r in reads if r["host"] == "aifoundry1 card 0"]

    def series(lst, s):
        return [r[f"raw{s}_cumulative_us"] for r in lst if r[f"raw{s}_rc"] == 0]
    mono = lambda v: all(b >= a for a, b in zip(v, v[1:]))
    a2_2, a2_3, c0_2, c0_3 = series(a2, 2), series(a2, 3), series(c0, 2), series(c0, 3)
    invalid = {s: sum(1 for r in a2 if r[f"raw{s}_rc"] not in (None, 0)) for s in (4, 5, 6)}
    invalid_c0 = {s: sum(1 for r in c0 if r[f"raw{s}_rc"] not in (None, 0)) for s in (4, 5, 6)}
    q132_t = 1793517211000  # 1 Nov 2026 00:13:31 PDT, Q132(g)'s host snapshot (q132-governor-desk/host/err-*.txt)
    invalid_a2_before_q132 = sum(1 for r in a2 if r["t_ms"] < q132_t for s in (4, 5, 6) if r[f"raw{s}_rc"] not in (None, 0))
    invalid_c0_before_q132 = sum(1 for r in c0 if r["t_ms"] < q132_t for s in (4, 5, 6) if r[f"raw{s}_rc"] not in (None, 0))
    per_exp = {}
    for r in a2:
        e = per_exp.setdefault(r["exp"], dict(reads=0, first=r["local"], last=None, raw2_first=r["raw2_cumulative_us"],
                                              raw2_last=None, raw3_values=set()))
        e["reads"] += 1; e["last"] = r["local"]; e["raw2_last"] = r["raw2_cumulative_us"]; e["raw3_values"].add(r["raw3_cumulative_us"])
    for e in per_exp.values():
        e["raw3_values"] = sorted(e["raw3_values"])

    sessions, runs = tel_tally()
    for exp, S in sessions.items():
        S["residency"] = per_exp.get(exp)
    json.dump(sessions, open(os.path.join(HERE, "sessions.json"), "w"), indent=1)
    hot = sorted([r for r in runs if r["max_board_w"] is not None and r["max_board_w"] >= 80], key=lambda r: -r["max_board_w"])
    with open(os.path.join(HERE, "runs-80w.txt"), "w") as f:
        f.write(f"aifoundry2 runs (telemetry files) whose board_w reached 80 W or more, since the 26 Oct SP start: {len(hot)} "
                f"(readings = samples, each counted once)\n")
        f.write("max_board_w  max_avg_w  readings  file\n")
        for r in hot:
            f.write(f"{r['max_board_w']:10.2f}  {r['max_avg_w'] if r['max_avg_w'] is not None else float('nan'):9.2f}  {r['n']:8d}  {r['file']}\n")

    H2 = parse_host(os.path.join(HERE, "host", "aifoundry2-20261101-1914.txt"))
    H1 = parse_host(os.path.join(HERE, "host", "aifoundry1-20261101-1915.txt"))
    rep = replay_card0(H1, reads)
    json.dump(rep, open(os.path.join(HERE, "replay-card0.json"), "w"), indent=1)
    with open(os.path.join(HERE, "replay-card0.txt"), "w") as f:
        f.write("Card 0 (aifoundry1 0000:01:00.0): kernel-log THROTTLE_TIME events replayed through update_residency "
                "(thermal_pwr_mgmt.c:351-393 in et-platform 836a4ab, a public tree that declares BL2 0.22.0) against every "
                "committed raw-3 read\n")
        f.write(f"THROTTLE_TIME events {rep['throttle_time_events']}, PMIC over-power events {rep['pmic_events']}\n")
        f.write(f"reads reproduced exactly on cumulative, average, maximum and minimum: {rep['exact_reads']} of {rep['reads']}\n")
        for s in rep["steps"]:
            f.write(f"  {s['exp']:5s} {s['tag']:30s} {s['local']}  raw3 {s['raw3_cumulative_us']:>10d} us = first {s['episodes']} episodes, exact={s['exact']}\n")
        f.write(f"sum {rep['sum_us']} us, mean {rep['mean_us']} us, min {rep['min_us']}, max {rep['max_us']}\n")
        f.write(f"PMIC events per episode {rep['pmic_per_episode']}; episodes without one {rep['episodes_without_pmic']}; "
                f"PMIC events after the last episode {rep['pmic_after_last_episode']}\n")
        f.write(f"episode end (host arrival) minus first PMIC event minus duration: median {rep['lag_us_median']} us, "
                f"range {rep['lag_us_range']} us\n")
        f.write(f"  the same with the duration read as the syndrome's 'msec': {rep['lag_if_msec_s_range'][0]} to "
                f"{rep['lag_if_msec_s_range'][1]} s (first three {rep['lag_if_msec_s_first3']} s), every episode ending minutes "
                f"before its own first interrupt; so the unit is microseconds\n")
        f.write(f"alarm values (W, count): {rep['pmic_watts']}\n")

    a2c = H2["counters"].get("0000:02:00.0", {}); c0c = H1["counters"].get("0000:01:00.0", {}); c1c = H1["counters"].get("0000:02:00.0", {})
    with open(os.path.join(HERE, "counters.txt"), "w") as f:
        f.write("Driver event counters (sysfs err_stats/ce_count), read-only host reads, 1 Nov 2026\n")
        f.write(f"aifoundry2 0000:02:00.0 at {H2['date']} (host up {H2['uptime_s']:.0f} s): {a2c}\n")
        f.write(f"aifoundry1 0000:01:00.0 (card 0) at {H1['date']}: {c0c}\n")
        f.write(f"aifoundry1 0000:02:00.0 (card 1) at {H1['date']}: {c1c}\n")
        f.write("Q132(g)'s snapshot at 00:13:31 PDT 1 Nov (q132-governor-desk/host/err-aifoundry*.txt): aifoundry2 PmicCeEvent 0, "
                "SpCeEvent 1692, ThermThrottleCeEvent 0; card 0 PmicCeEvent 177, SpCeEvent 252, ThermThrottleCeEvent 146\n")
        f.write("SP Runtime Error events against committed residency reads of invalid states 4-6 (two events per invalid-state read, E77 F1):\n")
        f.write(f"  card 0: {sum(invalid_c0.values())} invalid-state reads x 2 = {2 * sum(invalid_c0.values())} vs SpCeEvent {c0c.get('SpCeEvent')}; "
                f"before 00:13:31 PDT {invalid_c0_before_q132} x 2 = {2 * invalid_c0_before_q132} vs 252\n")
        f.write(f"  aifoundry2: {sum(invalid.values())} invalid-state reads x 2 = {2 * sum(invalid.values())} vs SpCeEvent {a2c.get('SpCeEvent')}; "
                f"before 00:13:31 PDT {invalid_a2_before_q132} x 2 = {2 * invalid_a2_before_q132} vs 1692\n")
        first = datetime.fromtimestamp(H2["btime"] + H2["log_first_mono_s"], tz=PST).strftime("%a %d %b %H:%M PST")
        f.write(f"  aifoundry2's kernel log (it has wrapped; oldest line {first}) holds {H2['events_in_log']} ET events, kinds "
                f"{H2['kinds']}, none a PMIC or throttling event; the last syndrome count is {H2['last_sp_runtime_error_count']} "
                f"(= SpCeEvent)\n")
        f.write(f"  aifoundry1's kernel log (unwrapped since its boot) holds {H1['events_in_log']} ET events, kinds {H1['kinds']}\n")
    up = []
    for line in open(os.path.join(DATA, "2026-11-01-e77-rail-one-temperature", "raw", "gov.jsonl")):
        d = json.loads(line)
        u = d.get("uptime")
        if isinstance(u, dict) and u.get("rc") == 0:
            t = datetime.fromtimestamp(u["t_ms"] / 1000, tz=timezone.utc)
            start = t - timedelta(days=u["day"], hours=u["hours"], minutes=u["mins"])
            up.append((local(u["t_ms"]), f"{u['day']} d {u['hours']} h {u['mins']} m",
                       (start - timedelta(minutes=1)).astimezone(PDT).strftime("%d %b %H:%M:%S"),
                       start.astimezone(PDT).strftime("%d %b %H:%M:%S PDT")))
    bt2 = datetime.fromtimestamp(H2["btime"], tz=PDT).strftime("%a %d %b %H:%M:%S PDT")
    bt1 = datetime.fromtimestamp(H1["btime"], tz=PDT).strftime("%a %d %b %H:%M:%S PDT")
    with open(os.path.join(HERE, "continuity.txt"), "w") as f:
        f.write("aifoundry2: one service-processor lifetime covers every read\n")
        for u in up:
            f.write(f"  module uptime {u[1]} read at {u[0]} (E77 raw/gov.jsonl) -> SP started between {u[2]} and {u[3]}\n")
        f.write("  E77 raw/gates.json uptime_min 8833 at 17:26:28 PST -> SP started 26 Oct 15:12:28-15:13:28 PDT\n")
        f.write(f"  host btime {bt2}; host up {H2['uptime_s']:.0f} s at {H2['date']} (no host reboot since)\n")
        f.write(f"  raw 2 (POWER_DOWN) over {len(a2_2)} reads: {a2_2[0]} -> {a2_2[-1]} us, monotonic {mono(a2_2)}\n")
        f.write(f"  raw 3 (POWER_SAFE) over {len(a2_3)} reads: values {sorted(set(a2_3))}\n")
        f.write(f"aifoundry1 card 0: host btime {bt1}; raw 2 {c0_2[0]} -> {c0_2[-1]} us monotonic {mono(c0_2)}; "
                f"raw 3 {c0_3[0]} -> {c0_3[-1]} us monotonic {mono(c0_3)}\n")

    allS = {k: sum(S[k] for S in sessions.values()) for k in ("n", "ge75", "ge80", "ge84", "ge85", "ge_card0_75", "ge100", "avg_ge70",
                                                             "avg_ge75", "mhz300", "duplicate_lines", "launch_lines_no_t_ms")}
    allS["max_board_w"] = max(S["max_board_w"] for S in sessions.values() if S["max_board_w"] is not None)
    allS["max_avg_w"] = max(S["max_avg_w"] for S in sessions.values() if S["max_avg_w"] is not None)
    allS["launch_lines_max_w"] = max(S["launch_lines_max_w"] for S in sessions.values() if S["launch_lines_max_w"] is not None)
    allS["sessions_checked"] = list(sessions)
    allS["sessions_with_samples"] = [e for e, S in sessions.items() if S["n"]]
    res = dict(
        aifoundry2=dict(reads=len(a2), raw3_reads_rc0=len(a2_3), raw3_values=sorted(set(a2_3)), first=a2[0]["local"], last=a2[-1]["local"],
                        sessions_with_reads=sorted(per_exp, key=lambda e: int(e[1:])), raw2_first_us=a2_2[0], raw2_last_us=a2_2[-1],
                        raw2_monotonic=mono(a2_2), invalid_state_reads=invalid, residency_duplicate_rows_dropped=DROPPED_RES_ROWS[0],
                        telemetry=allS, runs_ge80=len(hot),
                        card0_75w_on_a2_scale=round(CARD0_75_ON_A2, 2), host_counters_1914=a2c, host_btime=bt2, module_uptime=up),
        card0=dict(reads=len(c0), raw3_first_us=c0_3[0], raw3_last_us=c0_3[-1], raw3_monotonic=mono(c0_3), invalid_state_reads=invalid_c0,
                   replay={k: v for k, v in rep.items() if k not in ("rows",)}, host_counters_1915=c0c),
    )
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
    print(json.dumps({k: (v if k != "card0" else {kk: vv for kk, vv in v.items() if kk != "replay"}) for k, v in res.items()}, indent=1, default=str)[:4000])
    print(open(os.path.join(HERE, "replay-card0.txt")).read())
    print(open(os.path.join(HERE, "counters.txt")).read())
    print(open(os.path.join(HERE, "continuity.txt")).read())


if __name__ == "__main__":
    main()
