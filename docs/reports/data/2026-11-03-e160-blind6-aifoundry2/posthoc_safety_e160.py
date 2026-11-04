#!/usr/bin/env python3
"""E160 (Q139): POST HOC, never a verdict. Written at the desk on Tue 3 Nov 2026, about 16:00 PST, after the data was collected (about 15:56 PST),
by the lane that collected it. It re-reads the raw records with its own code (it imports nothing of the harness or the reducer) to check three things
the queue's own records claim:

  (S1) the session's peaks over EVERY sampler line of every session (board W, the minion shires' mean die reading, the hottest-sensor field, the PMIC's
       own temperature), how many lines reached 80, 82 and 85 W, and the service processor's own running maxima (board_max_w and the minion
       temperature's max) at the queue's first and last line: E160 sent no statistics reset, so a running maximum that does not move means no reading
       of the SP's exceeded it during the queue;
  (S2) the two stop-path tests, from the raw sampler lines: the board stop (30 W on three lines in a row) tripped while the launch ran, within 1.5 s of the
       third live line over 30 W, and the launch ended within 3 s of the trip; the die stop (30 C) tripped within 1.5 s of the first live line, before
       any launch (E160.md, "The stop-path tests");
  (S3) the service processor's trace ring over the whole queue: every entry new since the smoke's start dump, by kind; the governor's power-status
       records by throttle state (3 = POWER_SAFE); any thermal throttle; every other text line, grouped with its digits masked;
  (S4) the admission rule's records (every run admitted or refused, the 82 W lock), every session's end, and E111's idle-login decisions
       (counts only: how many counted another user, session, blocking user, ignored idle user or young process).

    python3 posthoc_safety_e160.py [<the aifoundry2 dir>] > posthoc-safety.txt      (writes posthoc-safety.json beside this file)

SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A2 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "aifoundry2")
SESSIONS = ("smoke", "stoptest-board", "stoptest-die", "s1")
out = {}


def jl(p):
    if not os.path.exists(p) and os.path.exists(p + ".gz"):
        p = p + ".gz"
    if not os.path.exists(p):
        return []
    op = gzip.open if p.endswith(".gz") else open
    rows = []
    with op(p, "rt") as f:
        for ln in f:
            if ln.startswith("{"):
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    pass
    return rows


def tel_files(sess):
    fs = glob.glob(os.path.join(A2, sess, "tel", "*.jsonl")) + glob.glob(os.path.join(A2, sess, "tel", "*.jsonl.gz"))
    return sorted(fs)


# ---------------------------------------------------------------- (S1)
print("(S1) peaks over every sampler line of every session")
lines = []
for s in SESSIONS:
    for p in tel_files(s):
        for d in jl(p.replace(".gz", "") if p.endswith(".gz") else p):
            d["_sess"], d["_file"] = s, os.path.basename(p).replace(".jsonl.gz", "").replace(".jsonl", "")
            lines.append(d)
lines.sort(key=lambda d: d.get("t_ms", 0))
bw = [(d["board_w"], d["_sess"], d["_file"], d["t_ms"]) for d in lines if d.get("board_w") is not None]
dm = [((d.get("temp_c") or {}).get("minshire") or [None])[0] for d in lines]
dh = [(((d.get("temp_c") or {}).get("minshire") or [None, None, None]) + [None, None, None])[2] for d in lines]
pm = [(d.get("temp_c") or {}).get("pmic") for d in lines]
top = max(bw)
S1 = {"lines": len(lines), "board_max_w": top[0], "board_max_at": f"{top[1]}/{top[2]}", "board_max_t_ms": top[3],
      "lines_ge_80w": sum(1 for x in bw if x[0] >= 80.0), "lines_ge_82w": sum(1 for x in bw if x[0] >= 82.0), "lines_ge_85w": sum(1 for x in bw if x[0] >= 85.0),
      "die_mean_max_c": max(x for x in dm if x is not None), "die_hottest_field_max_c": max(x for x in dh if x is not None),
      "die_hottest_field_min_c": min(x for x in dh if x is not None), "pmic_temp_max_c": max(x for x in pm if x is not None)}
sp0 = (lines[0].get("sp") or {})
sp1 = (lines[-1].get("sp") or {})
S1["sp_running_max_first_line"] = {"board_max_w": sp0.get("board_max_w"), "minion_c_max": (sp0.get("minion_c") or [None] * 3)[2],
                                   "minion_w_max": (sp0.get("minion_w") or [None] * 3)[2], "since_reset_ms": lines[0].get("since_reset_ms")}
S1["sp_running_max_last_line"] = {"board_max_w": sp1.get("board_max_w"), "minion_c_max": (sp1.get("minion_c") or [None] * 3)[2],
                                  "minion_w_max": (sp1.get("minion_w") or [None] * 3)[2], "since_reset_ms": lines[-1].get("since_reset_ms")}
S1["sp_board_max_w_values_seen"] = sorted({(d.get("sp") or {}).get("board_max_w") for d in lines if (d.get("sp") or {}).get("board_max_w") is not None})
S1["since_reset_ms_values_seen"] = sorted({d.get("since_reset_ms") for d in lines})
per_sess = {}
for s in SESSIONS:
    xs = [x[0] for x in bw if x[1] == s]
    if xs:
        per_sess[s] = {"lines": len(xs), "board_max_w": max(xs)}
S1["per_session"] = per_sess
top10 = sorted(bw, reverse=True)
seen, t10 = set(), []
for w, s, f, t in top10:
    if f in seen:
        continue
    seen.add(f)
    t10.append({"run": f"{s}/{f}", "board_max_w": w})
    if len(t10) == 10:
        break
S1["highest_runs"] = t10
out["S1_peaks"] = S1
for k, v in S1.items():
    print(f"  {k}: {json.dumps(v)}")

# ---------------------------------------------------------------- (S2)
print("\n(S2) the stop-path tests from the raw sampler lines")
q = jl(os.path.join(A2, "queue.jsonl"))
det = {x["name"]: x for x in q if x.get("kind") == "stoptest_detail"}
ends = {x["name"]: x for x in q if x.get("kind") == "session_end"}
S2 = {}
# board
tb = jl(os.path.join(A2, "stoptest-board", "tel", "STOPTEST-00-b6-fp32.anchor6_zeros-r1.jsonl"))
tb.sort(key=lambda d: d["t_ms"])
run3, third = 0, None
for d in tb:
    if d.get("board_w") is not None and d["board_w"] > 30.0:
        run3 += 1
        if run3 == 3:
            third = d
            break
    else:
        run3 = 0
L = jl(os.path.join(A2, "stoptest-board", "launches.jsonl"))
work = [x for x in L if x.get("role") == "work"]
lw = (work[0]["t_start_ms"], work[0]["t_end_ms"]) if work else (None, None)
sp_lines = [s for x in work for s in (x.get("sparsity") or [])]
db = det.get("stoptest-board", {})
trip = db.get("t_trip_ms")
S2["board"] = {"exit": ends.get("stoptest-board", {}).get("rc"), "reason": ends.get("stoptest-board", {}).get("end", {}).get("reason"),
               "third_line_over_30w_t_ms": third["t_ms"] if third else None, "third_line_w": third["board_w"] if third else None,
               "queue_t_third_line_ms": db.get("t_third_line_ms"), "t_trip_ms": trip,
               "trip_after_third_line_ms": (trip - third["t_ms"]) if (trip and third) else None,
               "launch_process": lw, "trip_inside_launch_process": bool(trip and lw[0] and lw[0] <= trip <= lw[1]),
               "kernel_launches_before_trip": sum(1 for s in sp_lines if s.get("t_end_ms", 0) <= (trip or 0)),
               "kernel_launch_running_at_trip": any(s.get("t_start_ms", 0) <= (trip or 0) <= s.get("t_end_ms", 0) for s in sp_lines),
               "process_end_after_trip_ms": (lw[1] - trip) if (trip and lw[1]) else None,
               "lines": len(tb)}
S2["board"]["registered_test_passes"] = bool(S2["board"]["exit"] == 4 and "board" in (S2["board"]["reason"] or "") and S2["board"]["trip_inside_launch_process"]
                                            and S2["board"]["trip_after_third_line_ms"] is not None and 0 <= S2["board"]["trip_after_third_line_ms"] <= 1500
                                            and S2["board"]["process_end_after_trip_ms"] is not None and S2["board"]["process_end_after_trip_ms"] <= 3000)
# die
td = jl(os.path.join(A2, "stoptest-die", "tel", "STOPTEST-00-b6-fp32.anchor6_zeros-r1.jsonl"))
td.sort(key=lambda d: d["t_ms"])
dd = det.get("stoptest-die", {})
first = td[0] if td else None
Ld = jl(os.path.join(A2, "stoptest-die", "launches.jsonl"))
S2["die"] = {"exit": ends.get("stoptest-die", {}).get("rc"), "reason": ends.get("stoptest-die", {}).get("end", {}).get("reason"),
             "first_line_t_ms": first["t_ms"] if first else None, "first_line_minshire": (first.get("temp_c") or {}).get("minshire") if first else None,
             "queue_t_first_line_ms": dd.get("t_first_line_ms"), "t_trip_ms": dd.get("t_trip_ms"),
             "trip_after_first_line_ms": (dd["t_trip_ms"] - first["t_ms"]) if (first and dd.get("t_trip_ms")) else None,
             "launch_records": len(Ld), "lines": len(td)}
S2["die"]["registered_test_passes"] = bool(S2["die"]["exit"] == 4 and "die" in (S2["die"]["reason"] or "") and S2["die"]["launch_records"] == 0
                                          and S2["die"]["trip_after_first_line_ms"] is not None and 0 <= S2["die"]["trip_after_first_line_ms"] <= 1500)
out["S2_stoptests"] = S2
for k, v in S2.items():
    print(f"  {k}: {json.dumps(v)}")

# ---------------------------------------------------------------- (S3)
print("\n(S3) the service processor's trace ring over the queue (every entry new since the smoke's start dump)")


def ring_entries(buf):
    """every entry of a trace dump, read here without the harness's code: 8-byte timestamp, u32 length, then a string or a 16-byte type-14 record"""
    if len(buf) < 64:
        return []
    size = struct.unpack_from("<I", buf, 16)[0] or len(buf)
    size = min(size, len(buf))
    ents, off = [], 64
    while off + 16 <= size:
        ts, n = struct.unpack_from("<QI", buf, off)
        if not (0 < n <= 512 and n % 8 == 0) or ts == 0 or off + 16 + n > size + 16:
            off += 8
            continue
        if n == 16 and off + 32 <= size and struct.unpack_from("<H", buf, off + 14)[0] == 14:
            pw, ths, pws, temp, mhz = struct.unpack_from("<HBBIH", buf, off + 16)
            if 0 <= pw < 400 and 0 <= temp < 200 and 0 <= mhz <= 2000 and ths < 16:
                ents.append((ts, off, "pstat", {"power_w": pw, "throttle_state": ths, "power_state": pws, "temp_c": temp, "mhz": mhz}))
                off += 32
                continue
        if off + 16 + n > size:
            off += 8
            continue
        body = buf[off + 16:off + 16 + n]
        text = body.split(b"\0")[0]
        if b"\0" not in body or len(text) < 4 or not all(32 <= c < 127 or c in (9, 10, 13) for c in text):
            off += 8
            continue
        ents.append((ts, off, "text", text.decode("latin-1").rstrip()))
        off += 16 + n
    return ents


dumps = []
for s in SESSIONS:
    sd = os.path.join(A2, s, "sp")
    if not os.path.isdir(sd):
        continue
    fs = sorted(glob.glob(os.path.join(sd, "*.bin")), key=lambda p: os.path.getmtime(p))
    st = os.path.join(sd, "start.bin")
    if st in fs:
        fs.remove(st)
        fs.insert(0, st)
    dumps += [(s, p) for p in fs]
seen_k, allents = set(), []
first_start = None
for s, p in dumps:
    for ts, off, kind, val in ring_entries(open(p, "rb").read()):
        if (ts, off, kind) in seen_k:
            continue
        seen_k.add((ts, off, kind))
        allents.append((ts, s, kind, val))
    if first_start is None:
        first_start = max((ts for ts, _, _, _ in allents), default=None)
allents.sort(key=lambda e: e[0])
new = [e for e in allents if first_start is not None and e[0] > first_start]
kinds = {}
masked = {}
gov = re.compile(r"Power throttle (up|down) event|Power idle state event|Thermal throttle down event|Thermal idle state event|New OP: Freq")
ths = {}
for ts, s, kind, val in new:
    if kind == "pstat":
        kinds["pstat"] = kinds.get("pstat", 0) + 1
        ths[val["throttle_state"]] = ths.get(val["throttle_state"], 0) + 1
        continue
    m = gov.search(val)
    k = ("governor: " + m.group(0)) if m else "other"
    kinds[k] = kinds.get(k, 0) + 1
    if not m:
        mk = re.sub(r"\d+", "#", val)[:140]
        masked[mk] = masked.get(mk, 0) + 1
S3 = {"dumps": len(dumps), "entries_new_since_smoke_start": len(new), "by_kind": dict(sorted(kinds.items())),
      "pstat_by_throttle_state": {str(k): v for k, v in sorted(ths.items())},
      "thermal_down_events": kinds.get("governor: Thermal throttle down event", 0),
      "other_text_lines_masked": dict(sorted(masked.items(), key=lambda kv: -kv[1]))}
grep_bad = {w: sum(v for k, v in masked.items() if w.lower() in k.lower()) for w in ("error", "fail", "alarm", "pmic", "over", "reset", "fault", "critical")}
S3["other_lines_matching"] = grep_bad
out["S3_sp_trace"] = S3
for k, v in S3.items():
    print(f"  {k}: {json.dumps(v)[:2500]}")

# ---------------------------------------------------------------- (S4)
print("\n(S4) the admission rule and every session's end")
adm = json.load(open(os.path.join(A2, "admission.json")))
logs = {}
for s in SESSIONS:
    p = os.path.join(A2, s, "run.log")
    if os.path.exists(p):
        t = open(p).read()
        logs[s] = {"admitted": len(re.findall(r"e105: admitted", t)), "not_admitted": len(re.findall(r"NOT ADMITTED|not admitted|refused", t)),
                   "lock_lines": len(re.findall(r"e105_peak_lock|lock engaged|lock:", t))}
S4 = {"lock_est": adm.get("lock_est"), "runs_seen": len(adm.get("seen", {})),
      "seen_peak_max_w": max((v.get("peak_w") or 0) for v in adm.get("seen", {}).values()),
      "run_logs": logs, "session_ends": {x["name"]: {"rc": x.get("rc"), "reason": (x.get("end") or {}).get("reason"), "card_min": (x.get("end") or {}).get("card_min")}
                                         for x in q if x.get("kind") == "session_end"},
      "queue_end": next(({"card_free_ms": x.get("card_free_ms"), "before_slot_end_s": x.get("before_slot_end_s"), "config": (x.get("snapshot") or {}).get("config")}
                         for x in q if x.get("kind") == "queue_end"), None),
      "queue_start_config": next(((x.get("snapshot") or {}).get("config") for x in q if x.get("kind") == "before_first_launch"), None)}
il = jl(os.path.join(A2, "idle_logins.jsonl"))
S4["idle_login_decisions"] = {"n": len(il), **{f"with_{k}": sum(1 for x in il if x.get(k)) for k in
                                                ("other_users", "other_sessions", "blocking_users", "ignored_idle_users", "young_process_users")}}
out["S4_admission_and_ends"] = S4
for k, v in S4.items():
    print(f"  {k}: {json.dumps(v)[:1500]}")

json.dump(out, open(os.path.join(HERE, "posthoc-safety.json"), "w"), indent=1)
