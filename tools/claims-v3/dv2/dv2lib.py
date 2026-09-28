#!/usr/bin/env python3
"""DV2 (the DVFS-heat experiments, DESIGN.md revision 2 and PREREG-DEV.md, 27 Sep 2026): parameters, the branch table,
run plans, the live watcher (safety caps, the falling edge, the one-shot statistics reset, the stop 2 s after the first
700 MHz sample, the C1m target), the post-run clock check (ABORT-LATCH), the dump scan for the governor's error lines,
the Z1 summary, the night rules (NAT and C1m start conditions), DEV-1's move rule, the SP log level's state (a copy of
hp/hplib.py's), and the V3_DRY=1 simulator of the 0.20.0 governor (0.40 s thermal loop, one-call climb, exit to 600 MHz,
1.05 s master-minion heartbeat, a configurable threshold, and a latch hook). Standard library only.

Subcommands (block.sh and dv2lib.sh call them; each prints plain text a shell can read):
  params                                       the fixed parameters as SET P_k=v lines
  branch --r0 R                                "BRANCH S K" (NAT-4/3/2/1, LOOP, WARM; D1 is never returned: not approved)
  plan-c1m                                     C1m's 12 runs: "RUN <block> <slot> <name>" lines (DESIGN §5.4)
  plan-t --block B --branch BR --n N           one T-block's 4 runs: "RUN <slot> <name>" (DESIGN §5.5; NAT-1's own rows)
  rundef NAME                                  "mask per_shire minions"
  watch --tel RAW --state F --ctl F --stop-file F --reset-file F --session-stop F [--caps k=v,...]
  postcheck --tel F --t-end MS [--within-s 3] [--tail-s 10]
                                               exit 0 if the clock read 600 MHz within 3 s of the kernel end and stayed
                                               there to the tail's end; 1 LATCH (not back at 600); 2 UNVERIFIED (no data)
  resets --tel F --t0 MS                       exit 0 ("ONE ...") if since_reset_ms shows exactly one reset before t0
  dumpcheck --dump F [--prev F]                exit 1 if the dump holds a "failed to set operating point" or "failed to
                                               get soc power" line newer than --prev (any line if no --prev)
  z1sum --dir D --pass P                       the Z1 cycle's summary (z1.json); prints "READING R THR T COOL|-"
  natok --data D --now MS                      exit 0 if a NAT session may start now (PREREG-DEV §4 row 6)
  c1mok --data D --now MS --r0 R               exit 0 if C1m may start now (row 5)
  dev1 --data D                                DEV-1's candidate for the next block from the session's runs so far
  nightval HH:MM                               epoch ms of HH:MM on night.json's day
  level-begin|level-mark|level-show --state F  the SP log level's per-card state (copied from hp/hplib.py)
  envcheck                                     exit 1 if a dry-only override is set without V3_DRY
  binhash role=path ...                        {role: {path, sha256}}
  vnow                                         the (virtual, under V3_DRY) clock in ms
  dry-sampler|dry-heater|dry-die|dry-sptrace|dry-config|dry-loglevel|dry-residency|dry-uptime   the simulator
  selftest                                     the offline checks of this file
"""
import glob
import gzip
import hashlib
import json
import math
import os
import random
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _find_root(d):
    x = d
    for _ in range(6):
        if os.path.exists(os.path.join(x, "tools", "claims-v3", "lib.sh")):
            return x
        x = os.path.dirname(x)
    return os.path.abspath(os.path.join(d, "..", "..", ".."))


ROOT = _find_root(HERE)

# ------------------------------------------------------------------------------------------ fixed parameters
# DESIGN §4-§5 and PREREG-DEV §1 (fixed now). The development decisions DEV-1..DEV-12 change only the keys named
# there, by their rules (block.sh logs each in dev-log.jsonl).
DEFAULTS = {
    "thr": 65, "K": 66,                              # the native software threshold and the trip reading (thr + 1)
    "abs_stop_c": 90, "cap_mean_c": 80, "cap_high_c": 85, "cap_board_w": 73, "cap_consecutive": 2,
    "sampler_stale_s": 3, "sampler_every_ms": 100,
    "edge_cap_s": 300,                               # an edge not reached within 300 s: the run is void
    "lift_max": 4, "lift_s": 7, "lift_mask": "0xffffffff", "lift_per": 4,      # T-run lifts: 7 s UNI32@4, <= 4
    "launch_s": 7,                                   # DEV-2: 7 -> 8
    "tail_s": 10,
    "stop_after_700_s": 2.0,                         # DEV-3: 2.0 -> 3.0
    "reset_confirm_s": 1.5,                          # the one-shot reset must show in the sampler before the launch
    "post_within_s": 3.0,                            # R6: 600 MHz within 3 s of the kernel end
    "smoke_launch_s": 2,
    "c1m_launch_s": 7, "c1m_max_launches": 3, "c1m_rise": 4, "c1m_edge_over": 2,   # E = R0 + 2; target E + 4
    # C1m's preheat: 2 s UNI32@16 bursts (512 minions, the C1m load's own power: about 45 W at 600 MHz and 64 W even at
    # 800 MHz if the card has left its loop; ALL24 would draw about 76 W at 800, over the 73 W cap)
    "c1m_preheat_mask": "0xffffffff", "c1m_preheat_per": 16, "c1m_preheat_s": 2, "c1m_preheat_max": 30,
    "c1m_cap_s": 3900,                               # 65 min of card time
    "c1m_no_cool_s": 3600,                           # C1m only if no Z1 reading <= 64 in the previous 60 min
    "nat_cap_s": 3600,                               # a NAT session: <= 60 min of card time
    "block_rest_s": 300,                             # DEV-10: 5 -> 10 min
    "edge_timeouts_end": 2,                          # two consecutive edge time-outs end the session
    "cool_max": 64,                                  # a Z1 reading <= 64 raises COOL
    "z1_fresh_s": 900,                               # the NAT start needs a Z1 reading <= 64 within the last 15 min
    "gap_between_launches_s": 0.3,
}
# DEV-1's candidates (N minions of INT/PER, K - S), in order (PREREG-DEV §2)
DEV1_CANDIDATES = [(128, 4), (192, 4), (192, 3)]
# the branch table (DESIGN §4.1): R0 -> (branch, S). D1 is not here: it needs the owner's yes (DESIGN §4.3)
BRANCHES = [("NAT-4", 60, 62), ("NAT-3", 61, 63), ("NAT-2", 62, 64), ("NAT-1", 64, 65)]
# the T-block cycle (DESIGN §5.5), block mod 4 -> order; INT/PER are INT16@N and PER16@N
T_CYCLE = {1: ["B4C@32", "INT", "PER", "UNI32@4"], 2: ["UNI32@4", "PER", "INT", "B4C@32"],
           3: ["PER", "INT", "UNI32@4", "B4C@32"], 4: ["INT", "PER", "B4C@32", "UNI32@4"]}
NAT1_ROW = ["B4C@32", "UNI32@4", "B4C@32", "UNI32@4"]
C1M_ROWS = [["INT16@32", "PER16@32", "UNI32@16"], ["UNI32@16", "PER16@32", "INT16@32"],
            ["PER16@32", "INT16@32", "UNI32@16"], ["UNI32@16", "INT16@32", "PER16@32"]]
FAIL_STRINGS = (b"failed to set operating point", b"failed to get soc power")
FORBIDDEN_CARDS = {"aifoundry1-c0": "aifoundry1 card 0 is never used (owner decision)"}


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def dry():
    return bool(os.environ.get("V3_DRY"))


def placements():
    return load_json(os.path.join(HERE, "placements.json"))


def run_def(name):
    """(mask, per_shire, minions) of a named run (placements.json 'runs', plus DV2's own entries)."""
    r = placements()["runs"].get(name)
    if r is None:
        raise KeyError("no run %s in dv2/placements.json" % name)
    return r["mask"], r["per_shire"], r["minions"]


def branch(r0):
    """(name, S) for the session's first reading R0 (DESIGN §4.1; D1 not approved: never returned)."""
    if r0 is None:
        return "WARM", None
    for name, rmax, S in BRANCHES:
        if r0 <= rmax:
            return name, S
    if r0 >= 66:
        return "LOOP", None
    return "WARM", None             # 65: neither a native edge nor the loop


def t_block(block, br, n):
    """The 4 runs of T-block `block` (1-based) under branch br with N minions for INT/PER."""
    if br == "NAT-1":
        return list(NAT1_ROW)
    per = {128: 8, 192: 12}[n]
    row = T_CYCLE[(block - 1) % 4 + 1]
    return [("INT16@%d" % per if x == "INT" else "PER16@%d" % per if x == "PER" else x) for x in row]


# ----------------------------------------------------------------------------------------------- telemetry
def open_any(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", errors="replace")
    return open(path, errors="replace")


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    out = []
    if not os.path.exists(path):
        return out
    with open_any(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def sample_fields(s):
    """(t_ms, mean, low, high, board_w, mhz, since_reset, resets) of one sampler line (None where absent)."""
    tc = s.get("temp_c") or {}
    ms = tc.get("minshire") or [None, None, None]
    return (s.get("t_ms"), ms[0], ms[1], ms[2], s.get("board_w"), (s.get("mhz") or {}).get("minion"),
            s.get("since_reset_ms"), s.get("resets"))


def heater_lines(path):
    out = []
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return out
    with open_any(path) as f:
        for line in f:
            if line.startswith("SPARSITY {"):
                try:
                    out.append(json.loads(line[9:]))
                except Exception:
                    pass
    return out


def median(v):
    v = sorted(x for x in v if x is not None)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])


# ----------------------------------------------------------------------------------------------- virtual time
def vnow_ms():
    r = time.time() * 1000.0
    if dry():
        vt0 = float(os.environ.get("HP_VT0", "0") or 0)
        sp = float(os.environ.get("HP_DRY_SPEED", "1") or 1)
        if vt0:
            return vt0 + (r - vt0) * sp
    return r


def vsleep(s):
    sp = float(os.environ.get("HP_DRY_SPEED", "1") or 1) if dry() else 1.0
    time.sleep(max(0.0, s / sp))


# ----------------------------------------------------------------------------------------------- the watcher
def watch(a):
    """One run's live watcher (hp/hplib.py's, extended). Reads the sampler's raw output as it grows; writes one state
    line (atomically):
      t_ms mean high board_w mhz n stop edge_ms tau_s s1_ms age_ms resets t700_ms planstop_ms target_ms reset_touch_ms wall_ms
    Safety stops (sticky; they create the heater's stop file): ABS90 (mean or high >= 90; also the session stop file),
    CAP_MEAN/CAP_HIGH/CAP_W (2 samples in a row at mean >= 80, high >= 85 or board >= 73 W).
    Control lines (the ctl file): 'edge S since_ms' (the falling S+1 -> S edge; the one-shot reset file is touched at
    the first S+1 reading at or after since_ms, or at the edge if no S+1 was seen after it), 'resetnow', 'stop700
    delay_ms since_ms' (the heater's stop file delay_ms after the first one-point 800 -> 700 step at or after since_ms:
    the trip; a 700 sample inside a 600 -> 800 climb, which 35 of 85 committed climbs showed, does not count),
    'target T since_ms' (the stop file at the first mean >= T at or after since_ms), 'quit'."""
    caps = dict(DEFAULTS)
    for kv in (a.get("caps") or "").split(","):
        if "=" in kv:
            k, v = kv.split("=", 1)
            caps[k] = float(v)
    tel, state, ctl = a["tel"], a["state"], a["ctl"]
    stop_file, session_stop = a.get("stop_file") or "", a.get("session_stop") or ""
    reset_file = a.get("reset_file") or ""
    pos, buf = 0, ""
    last = None
    n = 0
    consec = 0
    stop = None
    edge = {"S": None, "since": None, "armed": False, "s1": None, "t": None, "tau": None}
    s700 = {"delay": None, "since": None, "t700": None, "done": None}
    tgt = {"T": None, "since": None, "t": None}
    prev_mhz = None
    reset_touch = None
    resets = None
    ctl_sig = None
    hist = []
    parent = os.getppid()

    def touch(f):
        if f:
            try:
                open(f, "a").close()
            except Exception:
                pass

    def do_reset(t):
        nonlocal reset_touch
        if reset_touch is None and reset_file:
            touch(reset_file)
            reset_touch = t

    def edge_step(t, m, live):
        if edge["S"] is None or edge["t"] is not None:
            return
        S = edge["S"]
        if m >= S + 2:
            edge.update(armed=True, s1=None)
        elif m == S + 1:
            if edge["s1"] is None:
                edge["s1"] = t
            if live and t >= edge["since"]:
                do_reset(t)
        elif t >= edge["since"] and edge["s1"] is not None:
            edge["t"] = t
            edge["tau"] = (t - edge["s1"]) / 1000.0 if edge["armed"] else None
            if live:
                do_reset(t)          # no S+1 reading after the wait began: the reset comes at the edge
        else:
            edge.update(armed=False, s1=None)

    def set_stop(why, session=False):
        nonlocal stop
        if stop is None:
            stop = why
            touch(stop_file)
            if session:
                touch(session_stop)

    def write_state():
        now = vnow_ms()
        f = lambda v: "-" if v is None else (("%.3f" % v) if isinstance(v, float) else str(v))
        age = (now - last[0]) if last else None
        vals = [last[0] if last else None, last[1] if last else None, last[3] if last else None,
                last[4] if last else None, last[5] if last else None, n, stop, edge["t"], edge["tau"], edge["s1"],
                int(age) if age is not None else None, resets, s700["t700"], s700["done"], tgt["t"], reset_touch,
                int(time.time() * 1000)]
        line = " ".join(f(v) for v in vals)
        tmp = state + ".tmp"
        with open(tmp, "w") as fh:
            fh.write(line + "\n")
        os.replace(tmp, state)

    while True:
        try:
            st = os.stat(ctl)
            sig = (st.st_mtime_ns, st.st_size)
            if sig != ctl_sig:
                ctl_sig = sig
                for line in open(ctl):
                    p = line.split()
                    if not p:
                        continue
                    if p[0] == "quit":
                        write_state()
                        return 0
                    if p[0] == "edge" and len(p) >= 3 and (edge["S"] != int(p[1]) or edge["since"] != float(p[2])):
                        edge.update(S=int(p[1]), since=float(p[2]), armed=False, s1=None, t=None, tau=None)
                        for ht, hm in hist:          # replay: a fall that began before the wait counts (no reset)
                            edge_step(ht, hm, False)
                        if edge["t"] is None and edge["s1"] is not None and last and last[1] == edge["S"] + 1:
                            do_reset(last[0])        # already at S+1 when the wait began
                    if p[0] == "resetnow":
                        do_reset(last[0] if last else vnow_ms())
                    if p[0] == "stop700" and len(p) >= 3 and s700["delay"] is None:
                        s700.update(delay=float(p[1]), since=float(p[2]))
                    if p[0] == "target" and len(p) >= 3 and tgt["T"] is None:
                        tgt.update(T=int(p[1]), since=float(p[2]))
        except FileNotFoundError:
            pass
        try:
            with open(tel, errors="replace") as fh:
                fh.seek(pos)
                chunk = fh.read()
                pos = fh.tell()
        except FileNotFoundError:
            chunk = ""
        buf += chunk
        lines = buf.split("\n")
        buf = lines.pop()
        for line in lines:
            if not line.startswith("{"):
                continue
            try:
                s = json.loads(line)
            except Exception:
                continue
            x = sample_fields(s)
            if x[0] is None or x[1] is None:
                continue
            last = x
            n += 1
            t, m, hi, w, mhz = x[0], x[1], x[3], x[4], x[5]
            if x[7] is not None:
                resets = x[7]
            if (hi is not None and hi >= caps["abs_stop_c"]) or m >= caps["abs_stop_c"]:
                set_stop("ABS90", session=True)
            bad = None
            if m >= caps["cap_mean_c"]:
                bad = "CAP_MEAN"
            elif hi is not None and hi >= caps["cap_high_c"]:
                bad = "CAP_HIGH"
            elif w is not None and w >= caps["cap_board_w"]:
                bad = "CAP_W"
            consec = consec + 1 if bad else 0
            if bad and consec >= caps["cap_consecutive"]:
                set_stop(bad)
            hist.append((t, m))
            edge_step(t, m, True)
            if s700["delay"] is not None and s700["t700"] is None and t >= s700["since"] and mhz == 700 and prev_mhz == 800:
                s700["t700"] = t
            if mhz is not None:
                prev_mhz = mhz
            if tgt["T"] is not None and tgt["t"] is None and t >= tgt["since"] and m >= tgt["T"]:
                tgt["t"] = t
                touch(stop_file)             # the C1m chain ends at the target (a planned stop, not a safety stop)
        if s700["t700"] is not None and s700["done"] is None and vnow_ms() >= s700["t700"] + s700["delay"]:
            s700["done"] = int(vnow_ms())
            touch(stop_file)                 # the planned stop 2 s after the first 700 sample
        write_state()
        try:
            os.kill(parent, 0)
        except OSError:
            return 0
        time.sleep(0.05)


# ----------------------------------------------------------------------------------------------- post-run checks
def postcheck(tel_path, t_end, within_s=3.0, tail_s=10.0, excursion_s=2.0):
    """R6 (DESIGN §4.4): after the kernel end the clock must read 600 MHz within `within_s` and stay there to the tail's
    end. Departure (README, D-4): a transient re-climb after the first 600 sample that returns to 600 within
    `excursion_s` is recorded, not a latch: the SP learns that a kernel ended only at the next master-minion heartbeat
    (about 1.05 s), so a thermal loop that exits just after the kernel end sees a stale busy flag, climbs (PUP), and
    idles (PIDLE) at the heartbeat (the dry simulator of the 0.20.0 governor produced exactly this). A latch
    (TPM:2323-2341) holds the clock off 600 for good.
    (0 OK, why) | (1 LATCH, why) | (2 UNVERIFIED, why)."""
    F = sorted((sample_fields(s) for s in load_jsonl(tel_path) if s.get("t_ms") is not None), key=lambda x: x[0])
    win = [x for x in F if t_end < x[0] <= t_end + tail_s * 1000.0 and x[5] is not None]
    if not win:
        return 2, "no sample with a clock in the %.0f s after the kernel end" % tail_s
    first600 = next((x for x in win if x[5] == 600), None)
    if first600 is None:
        return 1, "no 600 MHz sample in the %.1f s after the kernel end (clocks %s)" % (
            (win[-1][0] - t_end) / 1000.0, sorted({x[5] for x in win}))
    if first600[0] > t_end + within_s * 1000.0:
        return 1, "600 MHz only %.2f s after the kernel end (> %.1f s)" % ((first600[0] - t_end) / 1000.0, within_s)
    exc, cur = [], None
    for x in win:
        if x[0] < first600[0]:
            continue
        if x[5] != 600 and cur is None:
            cur = [x[0], None, x[5]]
        elif x[5] == 600 and cur is not None:
            cur[1] = x[0]
            exc.append(cur)
            cur = None
    if cur is not None:
        return 1, "off 600 MHz (%s) from %.2f s after the kernel end to the tail's end" % (cur[2], (cur[0] - t_end) / 1000.0)
    long_ = [e for e in exc if e[1] - e[0] > excursion_s * 1000.0]
    if long_:
        e = long_[0]
        return 1, "off 600 MHz (%s) for %.2f s after the kernel end (> %.1f s)" % (e[2], (e[1] - e[0]) / 1000.0, excursion_s)
    if win[-1][0] < t_end + (tail_s - 2.0) * 1000.0:
        return 2, "the samples end %.1f s after the kernel end (tail %.0f s)" % ((win[-1][0] - t_end) / 1000.0, tail_s)
    note = "600 MHz %.2f s after the kernel end, at 600 at the tail's end (%.1f s)" % (
        (first600[0] - t_end) / 1000.0, (win[-1][0] - t_end) / 1000.0)
    if exc:
        note += "; %d transient re-climb(s) back to 600 within %.1f s (longest %.2f s)" % (
            len(exc), excursion_s, max(e[1] - e[0] for e in exc) / 1000.0)
    return 0, note


def reset_check(tel_path, t0):
    """Exactly one statistics reset before t0 (PREREG-DEV §1.1 void rule): since_reset_ms -1 before it, then growing
    with no drop (no second reset) and never back to -1."""
    F = sorted((sample_fields(s) for s in load_jsonl(tel_path) if s.get("t_ms") is not None), key=lambda x: x[0])
    if not F:
        return False, "no telemetry"
    drops, first_pos, prev = 0, None, None
    for x in F:
        sr = x[6]
        if sr is None:
            continue
        if sr >= 0 and first_pos is None:
            first_pos = x[0]
        if prev is not None and prev >= 0 and (sr < prev or sr < 0):
            drops += 1
        prev = sr
    if first_pos is None:
        return False, "no reset seen (since_reset_ms never >= 0)"
    if first_pos > t0:
        return False, "the reset came after t0 (%d ms)" % (first_pos - t0)
    if drops:
        return False, "%d further reset(s) or a window restart" % drops
    return True, "one reset, %.2f s before t0" % ((t0 - first_pos) / 1000.0)


def dumpcheck(dump, prev=None):
    """(bad lines, note): the governor's error lines (TPM:2327, 2338 and the others) in `dump`, only those newer than
    `prev`'s newest entry when prev is given; with no prev, any such line in the ring (conservative)."""
    import sptrace_events as SE
    try:
        buf = open(dump, "rb").read()
    except Exception as e:
        return None, "unreadable dump: %s" % e
    raw_hits = sum(buf.count(s) for s in FAIL_STRINGS)
    evs = SE.events(buf)
    scope = "whole ring"
    cand = evs
    if prev and os.path.exists(prev):
        try:
            cand = SE.since(SE.events(open(prev, "rb").read()), evs)
            scope = "new since %s" % os.path.basename(prev)
        except Exception:
            scope = "whole ring (prev unreadable)"
    bad = [e for e in cand if any(s.decode() in e["text"] for s in FAIL_STRINGS)]
    if not bad and raw_hits and scope.startswith("whole ring"):
        bad = [{"text": "raw byte match (%d) outside the parsed entries" % raw_hits, "ts": None}]
    return bad, "%s; %d raw byte matches in the ring" % (scope, raw_hits)


# ----------------------------------------------------------------------------------------------- Z1
def z1sum(d, pass_no):
    """The Z1 cycle's summary from its files: the sample, config, residency, uptime and the dump's governor lines."""
    import sptrace_events as SE
    out = {"pass": pass_no, "dir": os.path.relpath(d, ROOT)}
    tel = [sample_fields(s) for s in load_jsonl(os.path.join(d, "tel.jsonl"))]
    tel = [x for x in tel if x[1] is not None]
    out["n_samples"] = len(tel)
    out["reading_c"] = tel[-1][1] if tel else None
    out["reading_min_c"] = min(x[1] for x in tel) if tel else None
    out["high_c"] = max((x[3] for x in tel if x[3] is not None), default=None)
    out["mhz"] = sorted({x[5] for x in tel if x[5] is not None})
    out["board_w"] = median([x[4] for x in tel])
    out["t_ms"] = tel[-1][0] if tel else None
    cfg = load_json(os.path.join(d, "config.json"), {}) or {}
    out["config"] = cfg
    out["threshold_c"] = cfg.get("temp_threshold_c")
    out["residency"] = {str(r.get("state")): r for r in load_jsonl(os.path.join(d, "z2-residency.jsonl"))}
    out["uptime"] = (load_jsonl(os.path.join(d, "z2-uptime.jsonl")) or [None])[0]
    try:
        evs = SE.events(open(os.path.join(d, "sp.bin"), "rb").read())
        kinds = {}
        for e in evs:
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        out["sp_kinds"] = kinds
        out["sp_level_ring"] = SE.level(evs)
        out["sp_governor"] = [{"kind": e["kind"], "ts": e["ts"], "T": e.get("T"), "threshold": e.get("threshold")}
                              for e in evs if e["kind"] in ("thermal_down", "thermal_idle", "power_up", "power_down",
                                                            "power_idle")]
        out["sp_new_op"] = sum(1 for e in evs if "new OP" in e["text"])
    except Exception as e:
        out["sp_error"] = str(e)
    r = out["reading_c"]
    out["cool"] = r is not None and r <= DEFAULTS["cool_max"]
    json.dump(out, open(os.path.join(d, "z1.json"), "w"), indent=1)
    return out


def val_mode():
    """DV2_VAL=1: PREREG-VAL's frozen replication on aifoundry2 (dv2v/block.sh sets it after its lock check): the data
    root is dv2v/, the watch cycles are the VZ passes (p9101-p9499), and night() is val.json's "nat" section (no clock
    windows: dv2v/block.sh applies val.json's)."""
    return bool(os.environ.get("DV2_VAL"))


def z1_history(data):
    """Every Z1 summary of this data root, oldest first (in validation mode, the VZ cycles)."""
    zs = []
    pat = "p9[1-4][0-9][0-9]" if val_mode() else "p1[0-9][0-9][0-9]"
    for f in glob.glob(os.path.join(data, pat, "z1.json")):
        z = load_json(f)
        if z and z.get("t_ms"):
            zs.append(z)
    return sorted(zs, key=lambda z: z["t_ms"])


def night():
    if val_mode():
        return dict((load_json(os.path.join(HERE, "..", "dv2v", "val.json"), {}) or {}).get("nat") or {})
    return load_json(os.environ.get("DV2_NIGHT_FILE") or os.path.join(HERE, "night.json"), {}) or {}


def local_ms(day, hhmm):
    """Epoch ms of HH:MM local time on `day` (YYYY-MM-DD)."""
    return int(time.mktime(time.strptime("%s %s" % (day, hhmm), "%Y-%m-%d %H:%M")) * 1000)


def sessions(data, kinds):
    out = []
    for f in glob.glob(os.path.join(data, "p[0-9]*", "session.json")):
        s = load_json(f)
        if s and s.get("kind") in kinds:
            out.append(s)
    return out


def any_time():
    """DV2_ANY_TIME=1 (V3_DRY only): the night's clock windows are not applied (the dry clock is virtual)."""
    return dry() and bool(os.environ.get("DV2_ANY_TIME"))


def natok(data, now):
    """PREREG-DEV §4 row 6: the auto-start flag on; the newest Z1 reading <= 64 and fresh; at most one NAT session
    tonight (one that launched); start between nat_start_after and nat_start_by (07:00)."""
    N = {} if any_time() else night()
    if not os.path.exists(os.path.join(data, "NAT-AUTOSTART")):
        return False, "the NAT auto-start flag (NAT-AUTOSTART) is off"
    if N.get("day") and now > local_ms(N["day"], N.get("nat_start_by", "07:00")):
        return False, "after %s: no NAT start" % N.get("nat_start_by", "07:00")
    if N.get("day") and now < local_ms(N["day"], N.get("nat_start_after", "00:00")):
        return False, "before %s" % N.get("nat_start_after")
    done = [s for s in sessions(data, ("NAT",)) if s.get("launched")]
    if N.get("nat1_off"):
        # orchestrator DEVIATION-N4 (28 Sep 01:40): a NAT-1 session (S = 65) cannot climb, so it does not use up the
        # night's one NAT session; NAT-1 itself is off (the branch command reads WARM at 63-64)
        done = [s for s in done if s.get("branch") != "NAT-1"]
    mx = int(N.get("nat_sessions_max", 1))    # DEVIATION-N5: a continuation session when night.json allows it
    if len(done) >= mx:
        return False, "%d NAT session(s) already ran tonight (pass %s)" % (len(done), done[-1].get("pass"))
    zs = z1_history(data)
    if not zs:
        return False, "no Z1 reading yet"
    z = zs[-1]
    if now - z["t_ms"] > DEFAULTS["z1_fresh_s"] * 1000:
        return False, "the newest Z1 reading is %.0f min old" % ((now - z["t_ms"]) / 60000.0)
    if not z.get("cool"):
        return False, "the newest Z1 reading is %s (> %d)" % (z.get("reading_c"), DEFAULTS["cool_max"])
    cmax = N.get("nat_cool_max")
    if cmax is not None and (z.get("reading_c") is None or z["reading_c"] > int(cmax)):
        return False, "the newest Z1 reading is %s (> %s: NAT-2 or better only, DEVIATION-N4)" % (z.get("reading_c"), cmax)
    return True, "Z1 p%s read %s C" % (z.get("pass"), z.get("reading_c"))


def c1mok(data, now, r0):
    """PREREG-DEV §4 row 5: LOOP (R0 >= 66); no Z1 reading <= 64 in the previous 60 min; once tonight; inside the
    C1m start window."""
    N = {} if any_time() else night()
    if r0 is None or r0 < 66:
        return False, "R0 %s: not LOOP" % r0
    if N.get("day"):
        if now < local_ms(N["day"], N.get("c1m_after", "02:30")):
            return False, "before %s" % N.get("c1m_after", "02:30")
        if now > local_ms(N["day"], N.get("c1m_start_by", "05:00")):
            return False, "after %s: no C1m start" % N.get("c1m_start_by", "05:00")
    if [s for s in sessions(data, ("C1M",)) if s.get("launched")]:
        return False, "C1m already ran tonight"
    smokes = [load_json(f) or {} for f in glob.glob(os.path.join(data, "p40[0-9][0-9]", "block.json"))]
    if not any(b.get("status") == "ok" for b in smokes):
        return False, "no smoke (40xx) passed tonight"
    cool = [z for z in z1_history(data) if z.get("cool") and now - z["t_ms"] <= DEFAULTS["c1m_no_cool_s"] * 1000]
    if cool:
        return False, "a Z1 reading <= 64 in the previous 60 min (%s in p%s)" % (cool[-1].get("reading_c"), cool[-1].get("pass"))
    return True, "LOOP at R0 %d" % r0


# ----------------------------------------------------------------------------------------------- DEV-1
def dev1(out_dir):
    """DEV-1 (PREREG-DEV §2): the (N, K - S) candidate for the next block, from the session's finished T-blocks
    (runs.jsonl of the session directory). A run qualifies if its host trip (the first 800 -> 700 step) falls in
    [t_up + 1.5 s, kernel end - 0.5 s]. Interpretation (logged): all 4 T-runs of a block count ('3 of 4' after block 1,
    '6 of 8' after block 2), since K - S applies to all of them. At most two moves; final after block 3."""
    fx = (night() if not any_time() else {}).get("dev1_fixed")
    if fx:
        # orchestrator DEVIATION-N5 (28 Sep): a continuation session keeps the first session's final candidate
        n, ks = int(fx[0]), int(fx[1])
        cand = DEV1_CANDIDATES.index((n, ks)) if (n, ks) in DEV1_CANDIDATES else -1
        return {"cand": cand, "N": n, "KS": ks, "moves": [], "flagged": False,
                "fixed": "night.json dev1_fixed (DEVIATION-N5)"}
    runs = [r for r in load_jsonl(os.path.join(out_dir, "runs.jsonl")) if r.get("kind") == "T" and r.get("block")]
    blocks = sorted({r["block"] for r in runs})
    cand, moves, flagged, since_block = 0, [], False, 1
    for b in blocks:
        if b > 3 or len(moves) >= 2 or flagged:
            break
        pooled = [r for r in runs if since_block <= r["block"] <= b and r.get("cand") == cand]
        nblk = b - since_block + 1
        if nblk > 2:
            break
        need = 3 if nblk == 1 else 6
        ok = sum(1 for r in pooled if r.get("qualifies") is True)
        if ok >= need or not pooled:
            continue
        fails = [r for r in pooled if r.get("qualifies") is not True]
        cens = [r for r in fails if r.get("trip_s") is None]
        early = [r for r in fails if r.get("trip_s") is not None and r["trip_s"] < 1.5]
        if early and len(early) >= len(cens):
            flagged = True
            moves.append({"after_block": b, "to": list(DEV1_CANDIDATES[cand]), "why": "early trips (%d): stay, flagged" % len(early)})
        elif cand < len(DEV1_CANDIDATES) - 1:
            cand += 1
            since_block = b + 1
            moves.append({"after_block": b, "to": list(DEV1_CANDIDATES[cand]), "why": "censored or late (%d of %d fail)" % (len(fails), len(pooled))})
    n, ks = DEV1_CANDIDATES[cand]
    return {"cand": cand, "N": n, "KS": ks, "moves": moves, "flagged": flagged}


# ----------------------------------------------------------------------------------------------- SP log level
LEVELS_RESTORABLE = ("INFO", "DEBUG")


def level_state(path):
    return load_json(path, None) or {"original": None, "pending": False, "log": []}


def level_save(path, st, **ev):
    st.setdefault("log", []).append(dict(ev, t_ms=int(vnow_ms())))
    st["log"] = st["log"][-50:]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, path)


def level_begin(path, found, block):
    st = level_state(path)
    if st.get("pending"):
        if st.get("original") in LEVELS_RESTORABLE:
            act, orig, why = "set", st["original"], "an earlier set was not restored (pending): restore target %s" % st["original"]
        else:
            act, orig, why = "skip", None, "pending set with no known original level: nothing is set"
    elif found in LEVELS_RESTORABLE:
        act, orig, why = "set", found, "found %s: WARNING for the session, %s restored at its end" % (found, found)
        st["original"] = found
    elif found == "WARNING_OR_LOWER":
        act, orig, why = "none", found, "found at WARNING or lower: nothing set, nothing to restore"
    else:
        act, orig, why = "skip", None, "level %s: WARNING is never set on an unknown level" % found
    level_save(path, st, ev="begin", block=block, found=found, action=act, original=orig)
    return act, orig, why


def level_mark(path, block, pending=None, checked=None):
    st = level_state(path)
    ev = {"ev": "mark", "block": block}
    if pending is not None:
        st["pending"] = bool(int(pending))
        ev["pending"] = st["pending"]
    if checked is not None:
        ev["checked"] = checked
        ev["ok"] = checked == st.get("original")
        if ev["ok"]:
            st["pending"] = False
    level_save(path, st, **ev)
    return st


# ----------------------------------------------------------------------------------------------- misc
# honoured only under V3_DRY=1 (dry tests); on a card they are refused
DRY_ONLY = ["DV2_DRY_LATCH", "DV2_DRY_LATCH_SILENT", "DV2_DRY_THR", "HP_DRY_REST", "DV2_NIGHT_FILE", "DV2_ANY_TIME", "V3_FORCE",
            "DV2_ETTELEM", "DV2_HEATER"]


def envcheck():
    bad = sorted(k for k in DRY_ONLY if os.environ.get(k))
    return (dry() or not bad), bad


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def binhash(pairs):
    out = {}
    for p in pairs:
        role, path = p.split("=", 1)
        full = path if os.path.isabs(path) else os.path.join(ROOT, path)
        out[role] = {"path": path, "sha256": sha256(full) if os.path.exists(full) else None}
    return out


# ----------------------------------------------------------------------------------------------- dry simulator
# V3_DRY=1: a small thermal model on an accelerated clock (HP_DRY_SPEED, default 40) with the 0.20.0 governor as
# DESIGN §2.1 reads it: the integer mean compared '> thr' each 133 ms pass; ENTER (CRITICAL line, state 4) with no busy
# test; a thermal loop that reduces one point, waits 0.40 s and re-reads (a reduce at 600 is a no-op) and exits to
# 600 MHz with an EXIT line; the power branch gated out while the loop runs; PUP climbs 600 -> 800 in one call (two OP
# lines 5 ms apart); PIDLE at idle. The SP learns busy/idle at the master minion's heartbeat (1.05 s). Test hooks:
# HP_DRY_REST (the rest reading), DV2_DRY_LATCH=1 (the loop's first reduce from 800 fails: 'failed to set operating
# point', the clock stays at 800, state 4 for good), DV2_DRY_THR (the threshold the simulated SP holds).
# Its numbers mean nothing about the cards.
DRY_CARDS = {
    "aifoundry2": {"P_idle": 32.0, "R": [0.6, 1.1], "tau": [5.0, 150.0], "rest": 67.0, "dvfs": True, "tdp": 65},
    "aifoundry3": {"P_idle": 25.7, "R": [0.55, 1.0], "tau": [6.0, 150.0], "rest": 53.0, "dvfs": False, "tdp": 0},
}
DRY_CONC = {"INT16": 1.0, "PER16": 0.8, "UNI32": 0.4, "B4C": 1.6}
DRY_KAPPA = {"INT16": 1.05, "PER16": 0.9, "UNI32": 1.0, "B4C": 1.1}


def _dry_dir():
    d = os.environ.get("HP_DRY_DIR") or os.path.join(ROOT, "build", "claims-v3-dry", "dv2-sim")
    os.makedirs(d, exist_ok=True)
    return d


def _dry_card():
    return os.environ.get("HP_DRY_CARD") or os.environ.get("CARD") or "aifoundry2"


def _dry_state_path(card):
    return os.path.join(_dry_dir(), "sim-%s.json" % card)


def _dry_load(card):
    if card in FORBIDDEN_CARDS:
        raise SystemExit("dry: %s refused" % card)
    st = load_json(_dry_state_path(card))
    cfg = dict(DRY_CARDS.get(card, DRY_CARDS["aifoundry2"]))
    rest = os.environ.get("HP_DRY_REST")
    if rest:
        cfg["rest"] = float(rest)
    if not st:
        T_amb = cfg["rest"] + 0.3 - sum(cfg["R"]) * cfg["P_idle"]
        st = {"t": vnow_ms(), "x": [cfg["P_idle"]] * 2, "T_amb": T_amb, "T": cfg["rest"] + 0.3, "mhz": 600, "gov": 0,
              "level": "INFO", "cfg": cfg, "last_pass": 0, "loop_next": None, "busy_sp": False, "last_hb": 0,
              "thr": 65, "boot_ms": vnow_ms() - 9 * 86400e3, "res": {str(k): 0 for k in range(2, 7)}, "gov_t0": None,
              "latched": False}
        # a card resting in the loop (rest >= thr + 1) starts in state 4, as aifoundry2 does at 66-67
        if cfg["dvfs"] and int(math.floor(cfg["rest"] + 0.3)) > 65:
            st["gov"], st["gov_t0"], st["loop_next"] = 4, vnow_ms(), vnow_ms()
    st["thr"] = int(os.environ.get("DV2_DRY_THR") or st.get("thr", 65))
    return st


def _dry_save(card, st):
    p = _dry_state_path(card)
    tmp = p + ".tmp"
    json.dump(st, open(tmp, "w"))
    os.replace(tmp, p)


def _dry_launches(card):
    d = {}
    for l in load_jsonl(os.path.join(_dry_dir(), "launches-%s.jsonl" % card)):
        d[l["id"]] = l
    return list(d.values())


def _dry_event(card, kind, t_ms, lvl, **kw):
    with open(os.path.join(_dry_dir(), "events-%s.jsonl" % card), "a") as f:
        f.write(json.dumps(dict(kind=kind, t=t_ms, lvl=lvl, **kw)) + "\n")


def _dry_host_request(card, st, what):
    if st.get("level", "INFO") in ("INFO", "DEBUG"):
        _dry_event(card, "host", vnow_ms(), st.get("level", "INFO"), what=what)


def _dry_power(card, st, t, launches):
    cfg = st["cfg"]
    busy = [l for l in launches if l["t0"] <= t < l.get("t1", 0)]
    P, Pk, conc = cfg["P_idle"], 0.0, 0.0
    mhz = st.get("mhz", 600)
    f = 1.9 if mhz >= 800 else (1.4 if mhz >= 700 else 1.0)
    if mhz > 600:
        add = 6.9 * (mhz - 600) / 200.0
        P += add
        Pk += add
    for l in busy:
        g = l.get("group", "UNI32")
        w = 0.026 * l["minions"] * f
        P += w
        Pk += w * DRY_KAPPA.get(g, 1.0)
        conc += w * DRY_CONC.get(g, 0.6) / max(1.0, l["minions"] / 128.0)
    return P, Pk, conc, bool(busy)


def _dry_op(card, st, t, new, lvl):
    if new != st["mhz"]:
        st["mhz"] = new
        _dry_event(card, "new_op", t, lvl, mhz=new)


def _dry_governor(card, st, t, busy_now):
    """One SP pass of the 0.20.0 governor (DESIGN §2.1)."""
    lvl = st.get("level", "INFO")
    if t - st.get("last_hb", 0) >= 1050:          # the master minion's heartbeat: the SP's view of busy
        st["last_hb"] = t
        st["busy_sp"] = busy_now
    mean_i = int(math.floor(st["T"]))
    thr = st["thr"]
    if st.get("latched"):
        return
    if mean_i > thr and st["gov"] < 4:            # entry: no busy test
        _dry_event(card, "thermal_down", t, lvl, T=mean_i, thr=thr)
        st["gov"], st["gov_t0"], st["loop_next"] = 4, t, t
        st["climb_800_at"] = None
    if st["gov"] == 4:
        if t >= (st.get("loop_next") or t):
            if mean_i > thr:
                if st["mhz"] > 600:
                    if (os.environ.get("DV2_DRY_LATCH") or os.environ.get("DV2_DRY_LATCH_SILENT")) and st["mhz"] == 800:
                        if not os.environ.get("DV2_DRY_LATCH_SILENT"):     # silent: the line lost from the ring
                            _dry_event(card, "err_setop", t, lvl)
                        st["latched"] = True
                        return
                    _dry_op(card, st, t, st["mhz"] - 100, lvl)
                st["loop_next"] = t + 400
            else:
                _dry_event(card, "thermal_idle", t, lvl, T=mean_i, thr=thr)
                st["res"]["4"] = st["res"].get("4", 0) + int((t - (st.get("gov_t0") or t)) * 1000)
                st["gov"] = 1
                _dry_op(card, st, t, 600, lvl)
        return
    busy = st["busy_sp"]
    if not busy and st["gov"] != 0:
        _dry_event(card, "power_idle", t, lvl)
        if st["gov"] == 2:
            st["res"]["2"] = st["res"].get("2", 0) + int((t - (st.get("gov_t0") or t)) * 1000)
        st["gov"] = 0
        _dry_op(card, st, t, 600, lvl)
    elif busy and st["gov"] < 2:
        _dry_event(card, "power_up", t, lvl)
        st["gov"], st["gov_t0"] = 2, t
        _dry_op(card, st, t, 700, lvl)
        st["climb_800_at"] = t + 110                # the one-call climb's second OP; at 10 Hz a 700 sample may show
    if st.get("climb_800_at") and t >= st["climb_800_at"]:
        if st["gov"] == 2 and st["mhz"] == 700:
            _dry_op(card, st, t, 800, lvl)
        st["climb_800_at"] = None


def _dry_advance(card, st, t_to, launches, emit=None):
    cfg = st["cfg"]
    t = st["t"]
    rng = random.Random(int(t) % 100000)
    while t + 100 <= t_to:
        t += 100
        P, Pk, conc, busy = _dry_power(card, st, t, launches)
        x = st["x"]
        a0 = 1 - math.exp(-0.1 / cfg["tau"][0])
        a1 = 1 - math.exp(-0.1 / cfg["tau"][1])
        x[0] += a0 * ((cfg["P_idle"] + Pk) - x[0])
        x[1] += a1 * (P - x[1])
        st["T"] = st["T_amb"] + cfg["R"][0] * x[0] + cfg["R"][1] * x[1]
        st["hot"] = st.get("hot", 0.0) + (1 - math.exp(-0.1 / 2.0)) * (conc * 0.5 - st.get("hot", 0.0))
        if cfg["dvfs"] and t - st.get("last_pass", 0) >= 133:
            st["last_pass"] = t
            _dry_governor(card, st, t, busy)
        if emit:
            nz = rng.gauss(0, 0.12)
            T = st["T"]
            emit(t, int(math.floor(T + nz)), int(math.floor(T - 3.0 + nz)), int(math.floor(T + 1.4 + st["hot"] + nz)),
                 P + rng.gauss(0, 0.15), st.get("mhz", 600))
    st["t"] = t
    return st


def dry_sampler(a):
    card = a.get("card") or _dry_card()
    secs = float(a.get("seconds", 10))
    every = int(a.get("every_ms", 100))
    reset = int(a.get("reset_ms", 0) or 0)
    once = a.get("reset_once_file") or ""
    out = a["out"]
    stop = {"now": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(now=True))
    signal.signal(signal.SIGINT, lambda *_: stop.update(now=True))
    st = _dry_load(card)
    t_begin = vnow_ms()
    if st["t"] < t_begin - 3.6e6:
        st["t"] = t_begin
    st = _dry_advance(card, st, t_begin, _dry_launches(card))
    win = {"t0": t_begin, "lo": None, "hi": None, "last_emit": 0, "resets": 0, "reset_t": None}
    fh = open(out, "a")

    def emit(t, m, lo, hi, w, mhz):
        if t - win["last_emit"] < every:
            return
        win["last_emit"] = t
        if reset:
            sr = int(t - win["t0"])
        elif once:
            sr = int(t - win["reset_t"]) if win["reset_t"] is not None else -1
        else:
            sr = -1
        win["lo"] = lo if win["lo"] is None else min(win["lo"], lo)
        win["hi"] = hi if win["hi"] is None else max(win["hi"], hi)
        d = {"t_ms": int(t), "took_ms": 20, "since_reset_ms": sr}
        if once:
            d["resets"] = win["resets"]
        d.update({"board_w": round(w, 2),
                  "temp_c": {"pmic": m, "ioshire": [m + 1, m, m + 2], "minshire": [m, win["lo"], win["hi"]]},
                  "sp": {"minion_c": [m, win["lo"], win["hi"]]}, "mhz": {"minion": mhz, "noc": 400, "ddr": 933}})
        if once and win["resets"] == 0 and os.path.exists(once):
            win.update(resets=1, reset_t=t, lo=None, hi=None)
            d["reset_rc"] = 0
        fh.write(json.dumps(d, separators=(",", ":")) + "\n")
        fh.flush()
        if reset and sr >= reset:
            win.update(t0=t, lo=None, hi=None)
    while not stop["now"] and vnow_ms() - t_begin < secs * 1000.0:
        st = _dry_advance(card, st, vnow_ms(), _dry_launches(card), emit)
        _dry_save(card, st)
        time.sleep(0.02)
    fh.close()
    return 0


def dry_die(a):
    card = a.get("card") or _dry_card()
    st = _dry_load(card)
    if st["t"] < vnow_ms() - 3.6e6:
        st["t"] = vnow_ms()
    st = _dry_advance(card, st, vnow_ms(), _dry_launches(card))
    _dry_save(card, st)
    print(int(math.floor(st.get("T", st["cfg"]["rest"]))))
    return 0


def dry_heater(a):
    card = a.get("card") or _dry_card()
    args = a["argv"]

    def opt(name, default):
        return args[args.index(name) + 1] if name in args else default
    mask = int(opt("--shires", "0xffffffff"), 0)
    per = int(opt("--per-shire", "32"))
    secs = float(opt("--seconds", "0"))
    stopf = opt("--stop-file", "")
    minions = bin(mask).count("1") * per
    PL = placements()["groups"]
    group = next((g for g, v in PL.items() if int(v["mask"], 0) == mask and g not in ("W12", "E12", "N12", "S12")), "UNI32")
    lf = os.path.join(_dry_dir(), "launches-%s.jsonl" % card)
    t0 = vnow_ms() + 200
    lid = "%d-%d" % (int(t0), os.getpid())
    with open(lf, "a") as f:
        f.write(json.dumps({"id": lid, "t0": t0, "t1": t0 + 30 + secs * 1000 + 20, "minions": minions, "group": group}) + "\n")
    lines = []

    def line(n, ts, te, it):
        return ("SPARSITY " + json.dumps({"test": "fma", "type": "fp32", "values": "randn", "minions": minions,
                                          "shire_mask": hex(mask), "iters": it, "launch": n, "wall_s": (te - ts) / 1000.0,
                                          "t_start_ms": int(ts), "t_end_ms": int(te), "ghz": 0.6, "ok": True},
                                         separators=(",", ":")))
    t = t0
    vsleep(0.2)
    lines.append(line(-1, t, t + 30, 20000))
    t += 30
    stopped = False
    k = 0
    while t < t0 + 30 + secs * 1000 - 1:
        if stopf and os.path.exists(stopf):
            stopped = True
            break
        vsleep(0.5)
        lines.append(line(k, t, t + 500, 549000))
        t += 500
        k += 1
    with open(lf, "a") as f:
        f.write(json.dumps({"id": lid, "t0": t0, "t1": t, "minions": minions, "group": group}) + "\n")
    print("device ready in 0.20 s (dry), kernel %s" % opt("--kernel", "?"), file=sys.stderr)
    for l in lines:
        print(l)
    if stopped:
        print("stopping: %s exists" % stopf, file=sys.stderr)
    vsleep(0.3)
    return 0


def _dry_catchup(card, st):
    """Advance the model to now (the governor runs between samplers too, e.g. during the probe's launch)."""
    if st["t"] < vnow_ms() - 3.6e6:
        st["t"] = vnow_ms()
    st = _dry_advance(card, st, vnow_ms(), _dry_launches(card))
    _dry_save(card, st)
    return st


def dry_sptrace(a):
    from sptrace_events import build_ring
    card = a.get("card") or _dry_card()
    st = _dry_catchup(card, _dry_load(card))
    _dry_host_request(card, st, "sptrace")
    ev = load_jsonl(os.path.join(_dry_dir(), "events-%s.jsonl" % card))
    ents = []
    for e in ev:
        ts = int((e["t"] - 1.7e12) * 1000)
        lv = e.get("lvl", "INFO")
        k = e["kind"]
        info = lv in ("INFO", "DEBUG")
        if k == "host":
            if info:
                ents.append((ts, "Host_Iface: Received DM request from host.\n"))
                ents.append((ts + 1, "pc_vq_process_pending_command TagID: 0 MsgID:1\r\n"))
            continue
        crit, inf, err = [], [], []
        if k == "power_up":
            crit.append("Power throttle up event, current pwr 42000  tdp level: 65000\n")
            inf.append("Power Throttle event received. throttle_state: 2\n")
        elif k == "power_idle":
            crit.append("Power idle state event, current pwr 30000  tdp level 65000\n")
            inf.append("Power Throttle event received. throttle_state: 0\n")
        elif k == "thermal_down":
            crit.append("Thermal throttle down event, current temperature: %d, threshold: %d\n" % (e["T"], e.get("thr", 65)))
            inf.append("Power Throttle event received. throttle_state: 4\n")
        elif k == "thermal_idle":
            crit.append("Thermal idle state event, current temperature %d, threshold %d\n" % (e["T"], e.get("thr", 65)))
        elif k == "new_op":
            crit.append("new OP: Freq %d MNN voltage %d SRM voltage 750 \n" % (e["mhz"], {600: 525, 700: 560, 800: 600}.get(e["mhz"], 525)))
        elif k == "err_setop":
            err.append("thermal pwr mgmt svc error: -1 failed to set operating point\r\n")
        for i, s in enumerate(crit + err):
            ents.append((ts + i, s))
        if info:
            for i, s in enumerate(inf):
                ents.append((ts + 10 + i, s))
    ents.sort()
    open(a["out"], "wb").write(build_ring(ents))
    print("sptrace: rc 0, 8192 bytes (dry, level %s)" % st.get("level"))
    return 0


def dry_config(a):
    card = a.get("card") or _dry_card()
    st = _dry_catchup(card, _dry_load(card))
    _dry_host_request(card, st, "config")
    tdp = st["cfg"]["tdp"]
    print(json.dumps({"tdp_w": tdp, "temp_threshold_c": st.get("thr", 65), "power_state": 1 if tdp else 0,
                      "power_state_name": "managed_power" if tdp else "max_power", "minion_mhz": st.get("mhz", 600),
                      "minion_mv": 525, "dry": True}))
    return 0


def dry_loglevel(a):
    card = a.get("card") or _dry_card()
    st = _dry_load(card)
    _dry_host_request(card, st, "loglevel")
    lv = a["level"].upper()
    st["level"] = {"CRITICAL": "WARNING", "ERROR": "WARNING", "WARNING": "WARNING", "INFO": "INFO", "DEBUG": "DEBUG"}.get(lv, "?")
    _dry_save(card, st)
    print("loglevel %s: rc 0 status 0 (dry)" % a["level"])
    return 0


def dry_residency(a):
    card = a.get("card") or _dry_card()
    st = _dry_catchup(card, _dry_load(card))
    for s in a["states"]:
        if not 2 <= s <= 6:
            print("residency: raw states 2-6 only", file=sys.stderr)
            return 2
    _dry_host_request(card, st, "residency")
    for s in a["states"]:
        c = st["res"].get(str(s), 0) if st["cfg"]["dvfs"] else 0
        print(json.dumps({"t_ms": int(vnow_ms()), "state": s, "rc": 0, "cumulative_us": c, "average_us": 0,
                          "maximum_us": 0, "minimum_us": 0, "dry": True}))
    return 0


def dry_uptime(a):
    card = a.get("card") or _dry_card()
    st = _dry_load(card)
    _dry_host_request(card, st, "uptime")
    m = int((vnow_ms() - st["boot_ms"]) / 60000)
    print(json.dumps({"t_ms": int(vnow_ms()), "rc": 0, "day": m // 1440, "hours": (m // 60) % 24, "mins": m % 60, "dry": True}))
    return 0


# ----------------------------------------------------------------------------------------------- self-test
def selftest():
    import tempfile
    ok = 0
    assert branch(58) == ("NAT-4", 62) and branch(60) == ("NAT-4", 62) and branch(61) == ("NAT-3", 63)
    assert branch(62) == ("NAT-2", 64) and branch(63) == ("NAT-1", 65) and branch(64) == ("NAT-1", 65)
    assert branch(65) == ("WARM", None) and branch(66) == ("LOOP", None) and branch(70) == ("LOOP", None)
    assert branch(None) == ("WARM", None)
    ok += 1
    for b in range(1, 9):
        r = t_block(b, "NAT-4", 128)
        assert abs(r.index("INT16@8") - r.index("PER16@8")) == 1
    firsts = ["INT" if t_block(b, "NAT-4", 128).index("INT16@8") < t_block(b, "NAT-4", 128).index("PER16@8") else "PER"
              for b in (1, 2, 3, 4)]
    assert firsts == ["INT", "PER", "PER", "INT"], firsts
    b4c_first = [t_block(b, "NAT-4", 128).index("B4C@32") < t_block(b, "NAT-4", 128).index("UNI32@4") for b in (1, 2, 3, 4)]
    assert b4c_first == [True, False, False, True], b4c_first
    assert t_block(1, "NAT-3", 192)[1] == "INT16@12" and t_block(5, "NAT-1", 128) == NAT1_ROW
    for name in ("INT16@8", "PER16@8", "INT16@12", "PER16@12", "B4C@32", "UNI32@4", "UNI32@16", "INT16@32",
                 "PER16@32", "ADD1", "ALL24", "UNI32@20"):
        run_def(name)
    assert run_def("INT16@12")[2] == 192 and run_def("PER16@12")[2] == 192 and run_def("ADD1") == ("0x00000001", 1, 1)
    assert run_def("UNI32@20")[2] == 640 and run_def("B4C@32") == ("0x00606000", 32, 128)
    ok += 1
    for pl in ("INT16@32", "PER16@32", "UNI32@16"):
        assert sum(1 for r in C1M_ROWS if r[0] == pl or r[-1] == pl) >= 2
    ip = ["INT" if r.index("INT16@32") < r.index("PER16@32") else "PER" for r in C1M_ROWS]
    assert ip == ["INT", "PER", "PER", "INT"], ip
    ok += 1
    d = tempfile.mkdtemp()
    p = os.path.join(d, "tel.jsonl")

    def w(rows):
        with open(p, "w") as f:
            for t, mhz, sr in rows:
                f.write(json.dumps({"t_ms": t, "since_reset_ms": sr, "temp_c": {"minshire": [66, 60, 70]},
                                    "mhz": {"minion": mhz}}) + "\n")
    te = 100000
    w([(te - 500, 800, 100)] + [(te + 100 * k, 700 if k < 5 else 600, 200 + k) for k in range(1, 101)])
    assert postcheck(p, te)[0] == 0
    w([(te + 100 * k, 800, 1) for k in range(1, 101)])
    assert postcheck(p, te)[0] == 1
    w([(te + 100 * k, 800 if k < 40 else 600, 1) for k in range(1, 101)])
    assert postcheck(p, te)[0] == 1
    w([(te + 100 * k, 600 if k < 50 or k > 60 else 800, 1) for k in range(1, 101)])
    assert postcheck(p, te)[0] == 0 and "re-climb" in postcheck(p, te)[1]      # 1.1 s excursion: transient
    w([(te + 100 * k, 600 if k < 50 or k > 75 else 800, 1) for k in range(1, 101)])
    assert postcheck(p, te)[0] == 1                                            # 2.6 s off 600
    w([(te + 100 * k, 600 if k < 90 else 800, 1) for k in range(1, 101)])
    assert postcheck(p, te)[0] == 1                                            # off 600 at the tail's end
    w([(te - 5000, 600, 1)])
    assert postcheck(p, te)[0] == 2
    w([(te - 3000 + 100 * k, 600, -1 if k < 5 else (k - 5) * 100) for k in range(0, 60)])
    assert reset_check(p, te)[0] is True
    w([(te - 3000 + 100 * k, 600, -1 if k < 5 else ((k - 5) % 10) * 100) for k in range(0, 60)])
    assert reset_check(p, te)[0] is False
    w([(te - 3000 + 100 * k, 600, -1) for k in range(0, 60)])
    assert reset_check(p, te)[0] is False
    w([(te - 3000 + 100 * k, 600, -1 if k < 35 else (k - 35) * 100) for k in range(0, 60)])
    assert reset_check(p, te)[0] is False
    ok += 1
    from sptrace_events import build_ring
    old = [(1000, "Thermal throttle down event, current temperature: 66, threshold: 65\n"),
           (1001, "thermal pwr mgmt svc error: -5 failed to get soc power\r\n")]
    a_, b_, c_ = (os.path.join(d, x) for x in ("a.bin", "b.bin", "c.bin"))
    open(a_, "wb").write(build_ring(old))
    open(b_, "wb").write(build_ring(old + [(2000, "new OP: Freq 600 MNN voltage 525 SRM voltage 750 \n")]))
    open(c_, "wb").write(build_ring(old + [(3000, "thermal pwr mgmt svc error: -1 failed to set operating point\r\n")]))
    assert dumpcheck(b_, a_)[0] == []
    assert len(dumpcheck(c_, b_)[0]) == 1
    assert len(dumpcheck(a_)[0]) == 1
    ok += 1
    rj = os.path.join(d, "runs.jsonl")
    with open(rj, "w") as f:
        for q in (True, True, False, False):
            f.write(json.dumps({"kind": "T", "block": 1, "cand": 0, "qualifies": q, "trip_s": 3.0 if q else None}) + "\n")
    assert dev1(d)["N"] == 192 and dev1(d)["KS"] == 4
    with open(rj, "w") as f:
        for q in (True, True, False, False):
            f.write(json.dumps({"kind": "T", "block": 1, "cand": 0, "qualifies": q, "trip_s": 3.0 if q else 0.8}) + "\n")
    r = dev1(d)
    assert r["N"] == 128 and r["flagged"]
    with open(rj, "w") as f:
        for b in (1, 2):
            for q in (True, True, True, b == 1):
                f.write(json.dumps({"kind": "T", "block": b, "cand": 0, "qualifies": q, "trip_s": 3.0}) + "\n")
    assert dev1(d)["cand"] == 0
    ok += 1
    print("dv2lib selftest: %d groups passed" % ok)
    return 0


# ----------------------------------------------------------------------------------------------- main
def _kv(argv):
    a, rest = {}, []
    i = 0
    while i < len(argv):
        x = argv[i]
        if x == "--":
            a["argv"] = argv[i + 1:]
            break
        if x.startswith("--"):
            k = x[2:].replace("-", "_")
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                a[k] = argv[i + 1]
                i += 2
                continue
            a[k] = "1"
        else:
            rest.append(x)
        i += 1
    a["_rest"] = rest
    return a


def _sh(v):
    s = str(v)
    return "'" + s.replace("'", "'\\''") + "'"


def _int_or_none(v):
    return int(v) if v is not None and str(v).lstrip("-").isdigit() else None


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, a = argv[0], _kv(argv[1:])
    if cmd == "selftest":
        return selftest()
    if cmd == "params":
        NF = night() if not any_time() else {}
        for k, v in DEFAULTS.items():
            if k == "launch_s" and NF.get("dev2_launch_s"):
                v = NF["dev2_launch_s"]          # DEVIATION-N5: the continuation session starts at DEV-2's value
            print("SET P_%s=%s" % (k, _sh(v)))
        return 0
    if cmd == "branch":
        br, S = branch(_int_or_none(a.get("r0")))
        NB = night() if not any_time() else {}
        if br == "NAT-1" and NB.get("nat1_off"):
            br, S = "WARM", None          # DEVIATION-N4: NAT-1 cannot climb at S = 65 (p6035)
        if NB.get("nat_branches") and br.startswith("NAT-") and br not in NB["nat_branches"]:
            br, S = "WARM", None          # validation: only the branch development used (PREREG-VAL; DEV-11)
        print(br, S if S is not None else "-", DEFAULTS["K"])
        return 0
    if cmd == "plan-c1m":
        for b, row in enumerate(C1M_ROWS, 1):
            for s, name in enumerate(row, 1):
                print("RUN", b, s, name)
        return 0
    if cmd == "plan-t":
        for s, name in enumerate(t_block(int(a["block"]), a["branch"], int(a["n"])), 1):
            print("RUN", s, name)
        return 0
    if cmd == "rundef":
        print(*run_def(a["_rest"][0]))
        return 0
    if cmd == "watch":
        return watch(a)
    if cmd == "postcheck":
        rc, why = postcheck(a["tel"], float(a["t_end"]), float(a.get("within_s", DEFAULTS["post_within_s"])),
                            float(a.get("tail_s", DEFAULTS["tail_s"])))
        print(why)
        return rc
    if cmd == "resets":
        good, why = reset_check(a["tel"], float(a["t0"]))
        print(("ONE " if good else "BAD ") + why)
        return 0 if good else 1
    if cmd == "dumpcheck":
        bad, note = dumpcheck(a["dump"], a.get("prev"))
        if bad is None:
            print("UNREADABLE", note)
            return 2
        if bad:
            print("FAIL-LINES %d (%s): %s" % (len(bad), note, " | ".join(e["text"][:80] for e in bad)))
            return 1
        print("clean (%s)" % note)
        return 0
    if cmd == "z1sum":
        z = z1sum(a["dir"], int(a["pass"]))
        print("READING", z.get("reading_c") if z.get("reading_c") is not None else "null",
              "THR", z.get("threshold_c") if z.get("threshold_c") is not None else "null",
              "COOL" if z.get("cool") else "-")
        return 0
    if cmd == "natok":
        good, why = natok(a["data"], float(a["now"]))
        print(("OK " if good else "NO ") + why)
        return 0 if good else 1
    if cmd == "c1mok":
        good, why = c1mok(a["data"], float(a["now"]), _int_or_none(a.get("r0")))
        print(("OK " if good else "NO ") + why)
        return 0 if good else 1
    if cmd == "dev1":
        d = dev1(a["data"])
        print("DEV1_CAND=%d DEV1_N=%d DEV1_KS=%d DEV1_JSON=%s" % (d["cand"], d["N"], d["KS"], _sh(json.dumps(d))))
        return 0
    if cmd == "slot":
        # the wall-clock slot of a pass (0: none): Z1 1k -> z1_first + (k - 1) x z1_period_s; the smoke smoke_at
        N = night()
        p = int(a["pass"])
        if any_time() or not N.get("day"):
            print(0)
        elif 1101 <= p <= 1999 and N.get("z1b_first"):
            # the dense watch (orchestrator DEVIATION-N2, 28 Sep 01:35): Z1 11xx -> z1b_first + (p - 1101) x z1b_period_s
            print(local_ms(N["day"], N["z1b_first"]) + (p - 1101) * int(N.get("z1b_period_s", 120)) * 1000)
        elif 1001 <= p <= 1999:
            print(local_ms(N["day"], N.get("z1_first", "00:40")) + (p - 1001) * int(N.get("z1_period_s", 600)) * 1000)
        elif 4001 <= p <= 4099:
            print(local_ms(N["day"], N.get("smoke_at", "02:30")))
        else:
            print(0)
        return 0
    if cmd == "endby":
        N = night()
        print(0 if any_time() or not N.get("day") else local_ms(N["day"], N.get("end_by", "08:00")))
        return 0
    if cmd == "kend":
        hl = heater_lines(a["heater"])
        print(max((h["t_end_ms"] for h in hl), default=int(float(a.get("fallback", 0)))))
        return 0
    if cmd == "runobs":
        import dv2obs
        o = dv2obs.runobs(a["tel"], a["heater"], K=int(a.get("K", 66)), target=int(a["target"]) if a.get("target") else None,
                          stop_ms=float(a["stop_ms"]) if a.get("stop_ms", "-") not in ("-", "") else None)
        print(json.dumps(o))
        return 0
    if cmd == "nightkey":
        N = night()
        k = a["_rest"][0]
        print(0 if any_time() or not N.get("day") or not N.get(k) else local_ms(N["day"], N[k]))
        return 0
    if cmd == "nightval":
        N = night()
        print(local_ms(N["day"], a["_rest"][0]) if N.get("day") else 0)
        return 0
    if cmd == "level-begin":
        act, orig, why = level_begin(a["state"], a["found"], a.get("block"))
        print("LV_ACTION=%s LV_ORIG=%s LV_WHY=%s" % (_sh(act), _sh(orig or ""), _sh(why)))
        return 0
    if cmd == "level-mark":
        level_mark(a["state"], a.get("block"), a.get("pending"), a.get("checked"))
        return 0
    if cmd == "level-show":
        st = level_state(a["state"])
        print("LV_PENDING=%s LV_ORIG=%s" % (_sh("1" if st.get("pending") else ""), _sh(st.get("original") or "")))
        return 0
    if cmd == "envcheck":
        good, bad = envcheck()
        print(" ".join(bad) if bad else "-")
        if not good:
            print("dry-only variables set without V3_DRY: %s" % " ".join(bad), file=sys.stderr)
            return 1
        return 0
    if cmd == "binhash":
        print(json.dumps(binhash(a["_rest"])))
        return 0
    if cmd == "vnow":
        print(int(vnow_ms()))
        return 0
    if cmd.startswith("dry-"):
        if not dry():
            print("%s: only under V3_DRY=1" % cmd, file=sys.stderr)
            return 2
        table = {"dry-sampler": dry_sampler, "dry-die": dry_die, "dry-heater": dry_heater, "dry-sptrace": dry_sptrace,
                 "dry-config": dry_config, "dry-loglevel": dry_loglevel, "dry-uptime": dry_uptime}
        if cmd == "dry-residency":
            a["states"] = [int(x) for x in a["_rest"]]
            return dry_residency(a)
        if cmd in table:
            return table[cmd](a)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
