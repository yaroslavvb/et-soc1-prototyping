#!/usr/bin/env python3
"""collect.py: the lab dashboard's collector (tools/lab/dashboard/DESIGN.md §1, §2, §5, §6).

Runs remote.sh on the three lab hosts in parallel (over ssh, or locally on this host), plus `claudes status` and
`spacesheep sessions list`, parses everything, applies the privacy filter, derives people, alerts, levels, the 48 h
history and the fingerprint, and writes ~/.cache/lab-dashboard/data.json (the page's data), history.jsonl,
state.json and raw/<host>.txt. Python 3 standard library only. Read-only everywhere; the optional card telemetry
sample (--card-sample, DESIGN.md §2.6) is off by default and passes every gate of the lab's card etiquette.

  collect.py [--out DIR] [--hosts a1,a2,a3] [--card-sample] [--sample-dry] [--from-raw DIR] [--no-sessions]
             [--no-backoff] [--health] [--quiet] [--now S --owner LOGIN (tests)]

  --out DIR       where data.json, history.jsonl, state.json and raw/ go (default ~/.cache/lab-dashboard)
  --hosts LIST    probe only these hosts (the others keep their last data, marked stale)
  --card-sample   take the telemetry sample this run (also: "card_sample": true in config.json)
  --sample-dry    run the sample's gates on each host and print the command it would run; runs nothing
  --from-raw DIR  parse saved probe outputs (DIR/raw-<host>.txt, DIR/claudes.txt, DIR/sessions.json), no ssh
  --no-sessions   skip `claudes status` and `spacesheep sessions list`
  --no-backoff    try every host now, even one waiting out its hourly retry after "approval needed"
  --health        run et-lab-health on every host this run (by default each host's check runs hourly)

Exit status: 0 data.json written (even with hosts missing); 3 the privacy check refused it; 2 a usage error;
4 another collector held the output directory's lock for 60 s.
Settings: ~/.config/lab-dashboard/config.json (optional): {"owner": "<login>", "card_sample": false,
"card_sample_every_min": 30, "sample_boot": {"aifoundry1": "<boot id a person confirmed>"},
"ssh": {"aifoundry1": "<ssh target>"}}; acknowledgements: ack.json (update.sh ack).
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import shlex
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
ETLH_PATH = os.path.join(REPO, "tools", "lab", "et-lab-health")
REMOTE_PATH = os.path.join(HERE, "remote.sh")
LAB_PATH = os.path.join(HERE, "lab.json")
HOME = os.path.expanduser("~")
CACHE = os.environ.get("LAB_DASH_CACHE") or os.path.join(HOME, ".cache", "lab-dashboard")
CONFIG = os.environ.get("LAB_DASH_CONFIG") or os.path.join(HOME, ".config", "lab-dashboard")

SLOT_S = 600          # history slot: ten minutes
SLOTS = 288           # 48 hours
HISTORY_KEEP_S = 7 * 86400
PROBE_TIMEOUT_S = 30
NOT_PROBED = "not probed this run"
PROBE_SAMPLE_TIMEOUT_S = 45   # a probe that may take the card sample: it starts only in the probe's first 10 s
HEALTH_EVERY_S = 3600         # et-lab-health runs hourly on each host (it runs sudo et-holders again, and ~300 processes)
UNIT_RE = re.compile(r"^[A-Za-z0-9@._:\\-]{1,120}$")
LOGIN_RE = re.compile(r"^[A-Za-z0-9._-]{1,32}$")
LEVELS = {"ok": 0, "info": 1, "warn": 2, "bad": 3}

# The health rules' thresholds (DESIGN.md §5), in one place.
RULES = {
    "disk_warn_pct": 85, "disk_bad_pct": 97,
    "mem_warn_pct": 10,
    "load_warn_per_thread": 1.5,
    "nodewatch_warn_min": 5, "nodewatch_bad_min": 30,
    "die_warn_c": 90, "die_bad_c": 100,
    "hold_long_s": 2 * 3600,
    "lapse_warn_days": 7,
    "watchdog_warn_min": 5,
    "active_min": 30, "away_min": 24 * 60,
    "approval_retry_min": 60,
    "sample_every_min": 30, "sample_min_every_min": 10, "sample_no_output_wait_min": 60,
    # a deploy on any state change, else every heartbeat_min; STALE after one missed heartbeat run and some slack
    "interval_min": 10, "cron_minute": 2, "heartbeat_min": 60, "stale_after_min": 80,
}

# ------------------------------------------------------------------------------------------------ privacy (§6)
PRIV_PATTERNS = [
    ("url", re.compile(r"\b(?:https?|ftp|ssh|wss?)://[^\s\"'<>]+", re.I)),
    ("tailscale-login", re.compile(r"login\.tailscale\.com", re.I)),
    # an address, but not a systemd template unit (getty@tty1.service, wg-quick@wg0.service): render.py's lookahead
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z][A-Za-z0-9-]*(?:\.[A-Za-z0-9-]+)*\.(?!(?:service|socket|timer|mount|"
                         r"scope|slice|target|path|device|swap|automount)\b)[A-Za-z]{2,}")),
    ("tailnet-name", re.compile(r"\b[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.ts\.net\b", re.I)),
    ("ipv4", re.compile(r"(?<![\w.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?!\w|\.\d)")),
    ("ipv6", re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}(?![\w:])"
                        r"|(?<![\w:])(?:[0-9A-Fa-f]{1,4}:)+:(?:[0-9A-Fa-f]{1,4}(?::[0-9A-Fa-f]{1,4})*)?(?![\w:])"
                        r"|(?<![\w:])::(?:[0-9A-Fa-f]{1,4}:)*[0-9A-Fa-f]{1,4}(?![\w:])")),
    ("mac", re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}(?![\w:])")),
]


class Privacy:
    """The scrubber (free text) and the final check (every string of data.json)."""

    def __init__(self, owner):
        self.owner = owner
        self.home_re = re.compile(r"/home/(?!%s(?:/|\b))[A-Za-z0-9._-]+" % re.escape(owner))

    def scrub(self, s, limit=None):
        if s is None:
            return None
        s = str(s)
        for name, rx in PRIV_PATTERNS:
            s = rx.sub("<%s>" % name, s)
        s = self.home_re.sub("/home/<user>", s)
        s = "".join(ch for ch in s if ch >= " " or ch == "\t")
        if limit and len(s) > limit:
            s = s[: limit - 1] + "…"
        return s

    def check(self, obj, path="$"):
        """[(json path, pattern name)] for every string that still matches a pattern."""
        found = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                found += self.check(str(k), path + ".<key>")
                found += self.check(v, "%s.%s" % (path, k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                found += self.check(v, "%s[%d]" % (path, i))
        elif isinstance(obj, str):
            for name, rx in PRIV_PATTERNS:
                if rx.search(obj):
                    found.append((path, name))
            if self.home_re.search(obj):
                found.append((path, "home-path"))
        return found


# ------------------------------------------------------------------------------------------------ small helpers
def iso(ts):
    if ts is None:
        return None
    return dt.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def ms(ts):
    return None if ts is None else int(round(ts * 1000))


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_atomic(path, text, mode=0o600):
    tmp = path + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def num(s, cast=float):
    try:
        return cast(s)
    except (TypeError, ValueError):
        return None


def etime_s(s):
    """ps etime ([[dd-]hh:]mm:ss) in seconds."""
    if not s:
        return None
    days = 0
    if "-" in s:
        d, s = s.split("-", 1)
        days = num(d, int) or 0
    parts = [num(p, int) for p in s.split(":")]
    if None in parts:
        return None
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, sec = parts
    return days * 86400 + h * 3600 + m * 60 + sec


def fmt_hm(ts):
    return dt.datetime.fromtimestamp(ts).strftime("%H:%M") if ts else "—"


def fmt_when(ts, now=None):
    """HH:MM today, "Tue HH:MM" within a week, else "25 Sep HH:MM" (for alert titles that stay true)."""
    if not ts:
        return "?"
    t, n = dt.datetime.fromtimestamp(ts), dt.datetime.fromtimestamp(now or time.time())
    if t.date() == n.date():
        return t.strftime("%H:%M")
    return t.strftime("%a %H:%M" if abs((n - t).days) < 6 else "%-d %b %H:%M")


def git_code():
    try:
        sha = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h", "--", "tools/lab/dashboard"],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        dirty = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", "tools/lab/dashboard"],
                               capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        sha, dirty = "", ""
    h = hashlib.sha256()
    for p in (os.path.join(HERE, "collect.py"), REMOTE_PATH):
        try:
            h.update(open(p, "rb").read())
        except OSError:
            pass
    return (sha or "uncommitted") + ("+" + h.hexdigest()[:6] if dirty or not sha else "")


# ------------------------------------------------------------------------------------------------ running probes
APPROVAL_RE = re.compile(r"login\.tailscale\.com|Tailscale SSH requires|additional check", re.I)


def classify_ssh_error(stderr, rc):
    e = stderr or ""
    if APPROVAL_RE.search(e):
        return "approval needed"
    if re.search(r"Could not resolve hostname|Name or service not known|nodename nor servname", e):
        return "unknown host"
    if re.search(r"Connection timed out|Operation timed out|timed out", e, re.I):
        return "timeout"
    if re.search(r"Connection refused|Permission denied|Host key verification failed", e):
        return "refused"
    if re.search(r"No route to host|Network is unreachable", e):
        return "unreachable"
    return "ssh failed (exit %s)" % rc


def run_probe(name, target, local, script, timeout_s=PROBE_TIMEOUT_S):
    """Run the composed probe; returns (stdout, error word or None, took_ms). Kills its own ssh client as soon as
    Tailscale's check prompt appears (the URL is never kept)."""
    inner = "nice -n 10 ionice -c3 bash -s"
    if local:
        cmd = ["bash", "-c", inner]
    else:
        cmd = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "-o", "ServerAliveInterval=5",
               "-o", "ServerAliveCountMax=2", target, inner]
    t0 = time.time()
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=HOME, start_new_session=True)
    except OSError as e:
        return "", "ssh failed (%s)" % type(e).__name__, 0
    out_chunks, err_chunks, approval = [], [], threading.Event()

    def feed():
        try:
            p.stdin.write(script.encode())
            p.stdin.close()
        except (OSError, ValueError):
            pass

    def read_out():
        for chunk in iter(lambda: p.stdout.read(65536), b""):
            out_chunks.append(chunk)

    def read_err():
        for line in iter(p.stderr.readline, b""):
            err_chunks.append(line)
            if APPROVAL_RE.search(line.decode(errors="replace")):
                approval.set()

    threads = [threading.Thread(target=f, daemon=True) for f in (feed, read_out, read_err)]
    for th in threads:
        th.start()
    deadline = t0 + timeout_s
    while p.poll() is None and time.time() < deadline and not approval.is_set():
        time.sleep(0.05)
    timed_out = p.poll() is None
    if timed_out:
        p.terminate()  # our own ssh client or bash, never a card tool
        try:
            p.wait(3)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
    for th in threads[1:]:
        th.join(2)
    took = int((time.time() - t0) * 1000)
    out = b"".join(out_chunks).decode(errors="replace")
    err = b"".join(err_chunks).decode(errors="replace")
    if approval.is_set():
        return out, "approval needed", took
    if "@@end" in out:
        return out, None, took
    if timed_out:
        return out, "timeout", took
    if local:
        return out, "probe failed (exit %s)" % p.returncode, took
    if p.returncode == 255 or not out:
        return out, classify_ssh_error(err, p.returncode), took
    return out, "probe incomplete (exit %s)" % p.returncode, took


def run_cmd(cmd, timeout_s):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, stdin=subprocess.DEVNULL, cwd=HOME)
        return r.stdout, r.returncode
    except (OSError, subprocess.SubprocessError) as e:
        return None, type(e).__name__


def compose_script(params, etlh_text, remote_text):
    marker = "__ETLH_EOF_lab_dashboard__"
    if marker in etlh_text:
        raise ValueError("et-lab-health contains the heredoc marker")
    lines = ["#!/bin/bash"]
    for k, v in params.items():
        lines.append("%s=%s" % (k, shlex.quote(str(v))))
    lines.append("ETLH=$(cat <<'%s'\n%s\n%s\n)" % (marker, etlh_text.rstrip("\n"), marker))
    return "\n".join(lines) + "\n" + remote_text


# ------------------------------------------------------------------------------------------------ parsing
def sections(text):
    secs, cur = {}, None
    for line in text.splitlines():
        if line.startswith("@@"):
            name, _, arg = line[2:].partition(" ")
            if name == "health-exit":
                secs["health_exit"] = [arg.strip()]
                continue
            cur = name
            secs.setdefault(cur, [])
            continue
        if cur is not None:
            secs[cur].append(line)
    return secs


def kv_lines(lines):
    d = {}
    for ln in lines:
        k, _, v = ln.partition(" ")
        d[k] = v.strip()
    return d


def p_meta(lines):
    d = kv_lines(lines)
    now, off = (d.get("now", "") + " ").split(" ")[:2]
    ld = d.get("loadavg", "").split()
    nproc = num(d.get("nproc"), int)
    load = None
    if len(ld) >= 3:
        l1, l5, l15 = (num(x) for x in ld[:3])
        load = {"1": l1, "5": l5, "15": l15, "threads": nproc,
                "per_thread": round(l1 / nproc, 3) if (l1 is not None and nproc) else None}
    me = d.get("me", "").split()
    return {"hostname": d.get("host"), "now": num(now, int), "tz": off or None,
            "uptime_s": num(d.get("uptime")), "load": load, "nproc": nproc,
            "boot": d.get("boot") or None, "kernel": d.get("kernel") or None,
            "me": me[0] if me else None, "my_uid": num(me[1], int) if len(me) > 1 else None,
            "probe_session": None if d.get("probe_session") in (None, "", "-") else d.get("probe_session"),
            "tree": d.get("tree") == "yes"}


def p_mem(lines):
    d = {k.rstrip(":"): num(v, int) for k, v in (ln.split()[:2] for ln in lines if len(ln.split()) >= 2)}
    tot, av = d.get("MemTotal"), d.get("MemAvailable")
    if not tot or av is None:
        return None
    return {"total_gib": round(tot / 1048576, 1), "avail_gib": round(av / 1048576, 1), "avail_pct": round(100 * av / tot)}


def p_disk(lines):
    out, seen = [], set()
    for ln in lines:
        f = ln.split()
        if len(f) < 4 or f[0] in seen:
            continue
        seen.add(f[0])
        size, used, avail = (num(x, int) for x in f[1:4])
        if not size:
            continue
        # df's Use%: used / (used + available), rounded up
        pct = -(-100 * used // (used + avail)) if (used is not None and avail is not None and used + avail) else None
        out.append({"mount": f[0], "used_pct": pct, "free_gib": round(avail / 2**30) if avail is not None else None,
                    "size_gib": round(size / 2**30)})
    return out


def p_kernel(lines, running):
    k = {"running": running, "reboot_pending": False, "pending_since": None, "pending_since_ms": None, "pending": []}
    for ln in lines:
        f = ln.split()
        if f[:1] == ["reboot_required"] and len(f) > 1:
            ts = num(f[1], int)
            k.update(reboot_pending=True, pending_since=iso(ts), pending_since_ms=ms(ts))
        elif f[:1] == ["pkg"] and len(f) > 1:
            k["pending"].append(f[1])
    return k


def p_systemd(lines):
    s = {"state": None, "failed": []}
    for ln in lines:
        k, _, v = ln.partition(" ")
        if k == "state":
            s["state"] = v.strip() or None
        elif k == "failed" and v.strip():
            u = v.strip()
            s["failed"].append(u if UNIT_RE.match(u) else re.sub(r"[^A-Za-z0-9@._:-]", "?", u)[:120])
    return s


def p_temps(lines):
    t = {"cpu_c": None, "nvme_c": None}
    for ln in lines:
        f = ln.split()
        if len(f) < 3:
            continue
        v = num(f[2])
        if v is None:
            continue
        c = round(v / 1000, 1)
        if f[0] == "coretemp" and f[1].startswith("Package") and t["cpu_c"] is None:
            t["cpu_c"] = c
        elif f[0] == "k10temp" and f[1] in ("Tctl", "Tdie") and t["cpu_c"] is None:
            t["cpu_c"] = c
        elif f[0] == "nvme" and f[1] == "Composite" and t["nvme_c"] is None:
            t["nvme_c"] = c
    return t


def p_people(secs, meta, now):
    """Per login on this host: sessions (not closing), closing, ttys, idle_min, procs, device_procs. uid >= 1000
    only; the probe's own session is left out. Returns (people dict, sessions count, raw session list)."""
    probe = meta.get("probe_session")
    sess = []
    raw = "".join(secs.get("sessions", [])).strip()
    if raw:
        for s in json.loads(raw):
            if str(s.get("session")) == str(probe):
                continue
            sess.append(s)
    people = {}

    def ent(login):
        return people.setdefault(login, {"sessions": 0, "closing": 0, "ttys": 0, "idle_min": None, "procs": 0,
                                          "device_procs": 0, "notty_sessions": 0})
    uid_of = {}
    for s in sess:
        uid, user = s.get("uid"), str(s.get("user") or "")
        if not isinstance(uid, int) or uid < 1000 or uid == 65534 or not LOGIN_RE.match(user):
            continue
        uid_of[user] = uid
        e = ent(user)
        if s.get("state") == "closing":
            e["closing"] += 1
        else:
            e["sessions"] += 1
            if not s.get("tty"):
                e["notty_sessions"] += 1
    newest = {}
    for ln in secs.get("pts", []):
        f = ln.split()
        if len(f) < 3:
            continue
        uid, user, at = num(f[0], int), f[1], num(f[2], int)
        if uid is None or uid < 1000 or uid == 65534 or not LOGIN_RE.match(user):
            continue
        e = ent(user)
        e["ttys"] += 1
        if at:
            newest[user] = max(newest.get(user, 0), at)
    host_now = meta.get("now") or int(now)
    for user, at in newest.items():
        people[user]["idle_min"] = max(0, round((host_now - at) / 60))
    ci_jobs = 0
    for ln in secs.get("procs", []):
        f = ln.split()
        if f[:1] == ["ci_jobs"] and len(f) > 1:
            ci_jobs = num(f[1], int) or 0
            continue
        if f[:1] != ["procs"] or len(f) < 5:
            continue
        uid, user, n, dv = num(f[1], int), f[2], num(f[3], int), num(f[4], int)
        if uid is None or uid < 1000 or uid == 65534 or not LOGIN_RE.match(user):
            continue
        e = ent(user)
        e["procs"] = n or 0
        e["device_procs"] = dv or 0
    nsess = sum(e["sessions"] + e["closing"] for e in people.values())
    return people, nsess, ci_jobs


def p_etwho(lines):
    d = {"exit": None, "held": [], "idle": False}
    for ln in lines:
        f = ln.split()
        if f[:1] == ["exit"] and len(f) > 1:
            d["exit"] = num(f[1], int)
        elif f[:1] == ["held"] and len(f) >= 3:
            login = f[2] if LOGIN_RE.match(f[2]) else "?"
            d["held"].append({"node": f[1], "login": login, "etime_s": etime_s(f[3]) if len(f) > 3 else None})
        elif f[:1] == ["idle"]:
            d["idle"] = True
    d["ok"] = d["exit"] == 0 and (d["idle"] or bool(d["held"]))
    return d


def p_cards(lines):
    devs, nodes, locks = {}, [], {}
    for ln in lines:
        f = ln.split()
        if not f:
            continue
        if f[0] == "card" and len(f) >= 3:
            devs[f[1]] = {"excluded": f[2] == "excluded=1", "attrs": {}, "ce": {}, "uce": {}}
        elif f[0] == "node" and len(f) > 1:
            nodes.append(f[1])
        elif f[0] == "lockfile" and len(f) > 2:
            locks[f[1]] = f[2]
        elif f[0] in devs and len(f) >= 2:
            d = devs[f[0]]
            if f[1] in ("ce", "uce") and len(f) >= 4:
                d[f[1]][f[2]] = num(f[3], int) or 0
            elif f[1] == "aer_port" and len(f) >= 3:
                d["aer_port"] = num(f[2], int)
                d["root_port"] = f[3] if len(f) > 3 else None
            else:
                d["attrs"][f[1]] = " ".join(f[2:])
    return devs, nodes, locks


def p_guard(lines):
    for ln in lines:
        f = ln.split()
        if f[:1] == ["marker"]:
            if len(f) > 1 and f[1] == "unreadable":
                return {"present": True, "this_boot": None, "readable": False}
            return {"present": True, "this_boot": len(f) > 1 and f[1] == "this_boot",
                    "minion_mhz": num(f[2], int) if len(f) > 2 else None,
                    "noc_mhz": num(f[3], int) if len(f) > 3 else None,
                    "tdp_w": num(f[4], int) if len(f) > 4 else None}
    return None


def p_nodewatch(lines, host_now):
    nw = {"present": False, "buckets": [], "events": [], "logins": None, "last": None}
    for ln in lines:
        f = ln.split()
        if not f:
            continue
        if f[0] == "present":
            nw["present"] = True
        elif f[0] == "b" and len(f) >= 10:
            try:
                t = dt.datetime.strptime(f[1] + "0:00" + f[2], "%Y-%m-%dT%H:%M:%S%z").timestamp()
            except ValueError:
                continue
            vals = [None if x == "-" else num(x) for x in f[3:10]]
            nw["buckets"].append({"t": t, "n": vals[0], "load": vals[1], "mem": vals[2], "so": vals[3],
                                  "sa": vals[4], "tmux": vals[5], "claude": vals[6]})
        elif f[0] == "ev" and len(f) >= 4:
            try:
                t = dt.datetime.strptime(f[1], "%Y-%m-%dT%H:%M:%S%z").timestamp()
            except ValueError:
                continue
            nw["events"].append({"t": iso(t), "t_ms": ms(t), "type": re.sub(r"[^A-Z-]", "", f[2])[:14],
                                 "what": re.sub(r"[^A-Za-z0-9-]", "", f[3])[:14]})
        elif f[0] == "logins" and len(f) >= 3:
            nw["logins"] = {"in": num(f[1], int), "out": num(f[2], int)}
        elif f[0] == "last" and len(f) >= 2:
            last = {}
            try:
                last["t"] = dt.datetime.strptime(f[1], "%Y-%m-%dT%H:%M:%S%z").timestamp()
            except ValueError:
                last["t"] = None
            for kv in f[2:]:
                k, _, v = kv.partition("=")
                last[k] = v
            nw["last"] = last
    if not nw["present"]:
        return {"present": False}
    last = nw["last"] or {}
    out = {"present": True, "beat_at": iso(last.get("t")), "beat_at_ms": ms(last.get("t")),
           "beat_age_min": round((host_now - last["t"]) / 60, 1) if last.get("t") and host_now else None,
           "user_manager": last.get("user@"), "linger": {"yes": True, "no": False}.get(last.get("linger")),
           "tmux": {"1": True, "0": False}.get(last.get("tmux")), "claude": num(last.get("claude"), int),
           "load": num(last.get("load")), "sessions": last.get("sessions"),
           "events_48h": nw["events"][-50:], "logins_48h": nw["logins"]}
    return out, nw["buckets"]


def p_experiments(lines):
    e = {"running": [], "last_log": None, "our_device_procs": 0}
    for ln in lines:
        f = ln.split()
        if not f:
            continue
        if f[0].isdigit() and len(f) >= 3 and f[1] == "running":
            e["running"].append({"kind": f[2], "what": f[3] if len(f) > 3 else None, "count": int(f[0])})
        elif f[0] == "our_device_procs" and len(f) > 1:
            e["our_device_procs"] = num(f[1], int) or 0
        elif f[0] == "last_log" and len(f) >= 3:
            ts = num(f[2], int)
            e["last_log"] = {"file": f[1], "at": iso(ts), "at_ms": ms(ts), "line": None}
        elif f[0] == "last_line" and e["last_log"] is not None:
            e["last_log"]["line"] = ln[len("last_line "):]
    return e


def parse_tel_line(kind, line):
    """One experiment or live telemetry line -> the card's telemetry fields."""
    try:
        o = json.loads(line)
    except ValueError:
        return None
    if not isinstance(o, dict):
        return None
    t = {"die_c": None, "die_max_c": None, "pmic_c": None, "board_w": None, "minion_mhz": None, "noc_mhz": None,
         "ddr_mhz": None}
    at = o.get("t_ms")
    if kind in ("ettelem", "live"):
        tc = o.get("temp_c") or {}
        ms_ = tc.get("minshire") or []
        t["die_c"] = ms_[0] if len(ms_) > 0 else None
        t["die_max_c"] = ms_[2] if len(ms_) > 2 else None
        t["pmic_c"] = tc.get("pmic")
        t["board_w"] = o.get("board_w")
        mhz = o.get("mhz") or {}
        t["minion_mhz"], t["noc_mhz"], t["ddr_mhz"] = mhz.get("minion"), mhz.get("noc"), mhz.get("ddr")
    elif kind == "tel":
        f = str(o.get("summary") or "").split()
        t["die_c"] = num(f[0]) if f else None
        t["minion_mhz"] = num(f[1], int) if len(f) > 1 else None
    elif kind == "marks":
        t["die_c"], t["minion_mhz"] = o.get("die_c"), o.get("mhz")
    else:  # energy.json and anything else: the common keys if present
        t["die_c"], t["board_w"] = o.get("die_c"), o.get("board_w")
    for k in list(t):
        if t[k] is not None and not isinstance(t[k], (int, float)):
            t[k] = num(t[k])
    t["at_s"] = at / 1000 if isinstance(at, (int, float)) else None
    return t


def p_telemetry(lines):
    out, cur = {}, None
    for ln in lines:
        if ln.startswith("file "):
            f = ln.split()
            if len(f) >= 5:
                cur = {"card": f[1], "kind": f[2], "mtime": num(f[3], int), "from": f[4], "line": None}
                out.setdefault(f[1], []).append(cur)
        elif ln.startswith("line ") and cur is not None:
            cur["line"] = ln[5:]
    return out


def p_manifest(lines):
    m = {"cpu": None, "et_soc1": None, "srcversion": None, "libetrt": None, "libdevicelayer": None,
         "dev_mngt_service": None, "power": None}
    for ln in lines:
        f = ln.split(None, 1)
        if len(f) < 2:
            continue
        k, v = f[0], f[1].strip()
        if k == "cpu":
            m["cpu"] = v
        elif k == "et_soc1":
            mm = re.search(r"version=(\S*)", v)
            ss = re.search(r"srcversion=(\S*)", v)
            m["et_soc1"] = mm.group(1) if mm and mm.group(1) else None
            m["srcversion"] = ss.group(1) if ss and ss.group(1) else None
        elif k == "sha256":
            g = v.split()
            if len(g) == 2:
                key = {"libetrt.so": "libetrt", "libdeviceLayer.a": "libdevicelayer",
                       "dev_mngt_service": "dev_mngt_service"}.get(os.path.basename(g[1]))
                if key:
                    m[key] = g[0][:16]
        elif k == "power":
            m["power"] = v
    return m


HEALTH_TWO_WORD = ("card ", "kernel ", "disk ", "zfs ", "net ", "clock ", "ci ")


def p_health(lines):
    out = []
    for ln in lines:
        lvl = ln[:6].strip()
        if lvl not in ("OK", "WARN", "INFO"):
            continue
        rest = ln[6:].strip()
        words = rest.split()
        n = 2 if any(rest.startswith(p) for p in HEALTH_TWO_WORD) and len(words) >= 2 else 1
        check = " ".join(words[:n])
        text = rest[len(check):].strip() if rest.startswith(check) else " ".join(words[n:])
        out.append({"level": lvl, "check": check, "text": text})
    return out


def p_sample(lines):
    s = {"gates": [], "would_run": None, "started": False, "ran": None, "tel": []}
    for ln in lines:
        f = ln.split()
        if not f:
            continue
        if f[0] == "gate" and len(f) >= 3:
            s["gates"].append({"gate": f[1], "ok": f[2] == "ok", "detail": " ".join(f[3:])})
        elif f[0] == "would_run":
            s["would_run"] = ln[len("would_run "):]
        elif f[0] == "start":
            s["started"] = True
        elif f[0] == "ran":
            d = dict(x.split("=", 1) for x in f[1:] if "=" in x)
            s["ran"] = {"rc": num(d.get("rc"), int), "before": num(d.get("msgs_before"), int),
                        "after": num(d.get("msgs_after"), int)}
        elif f[0] == "tel":
            s["tel"].append(ln[4:])
    return s


# ------------------------------------------------------------------------------------------------ the collector
class Collector:
    def __init__(self, args):
        self.args = args
        self.t_wall = time.time()
        self.now = args.now if (args.now and args.from_raw) else self.t_wall
        self.lab = load_json(LAB_PATH, None)
        if not self.lab:
            raise SystemExit("collect.py: cannot read %s" % LAB_PATH)
        self.out = args.out
        self.config = load_json(os.path.join(CONFIG, "config.json"), {})
        self.acks = load_json(os.path.join(CONFIG, "ack.json"), {})
        self.state = load_json(os.path.join(self.out, "state.json"), {})
        self.state.setdefault("hosts", {})
        self.state.setdefault("cards", {})
        self.state.setdefault("alerts_since", {})
        self.state.setdefault("owner", {})
        self.owner = (args.owner or self.config.get("owner") or os.environ.get("USER") or os.environ.get("LOGNAME")
                      or "owner")
        if not LOGIN_RE.match(self.owner):
            raise SystemExit("collect.py: owner login %r is not a login" % self.owner)
        self.priv = Privacy(self.owner)
        self.errors = []
        self.this_host = socket.gethostname().split(".")[0]
        self.sample_enabled = bool(args.card_sample or args.sample_dry or self.config.get("card_sample"))
        every = self.config.get("card_sample_every_min", RULES["sample_every_min"])
        self.sample_every_min = max(RULES["sample_min_every_min"], num(every, int) or RULES["sample_every_min"])
        self.known = {k["id"]: k.get("note") for k in self.lab.get("known", [])}

    # -------------------------------------------------------------- the run
    def run(self):
        lab_hosts = self.lab["hosts"]
        wanted = list(lab_hosts)
        if self.args.hosts:
            wanted = [h.strip() for h in self.args.hosts.split(",") if h.strip()]
            bad = [h for h in wanted if h not in lab_hosts]
            if bad:
                print("collect.py: unknown host(s): %s" % ", ".join(bad), file=sys.stderr)
                return 2
        etlh = open(ETLH_PATH).read()
        remote = open(REMOTE_PATH).read()
        raw, results, jobs, todo = {}, {}, {}, {}
        self.sample_plan = {}
        self.health_ran = {}
        if not self.args.from_raw:
            self.recover_inflight()
        t_start = time.time()
        for h in lab_hosts:
            if h not in wanted:
                continue
            hs = self.state["hosts"].get(h, {})
            if (not self.args.no_backoff and not self.args.from_raw and hs.get("next_try_ms")
                    and hs["next_try_ms"] > ms(self.now)):
                results[h] = ("", "approval needed", 0, True)
                continue
            if self.args.from_raw:
                plan = self.plan_sample(h)  # so that a saved @@sample section is parsed as that card's
                if plan:
                    self.sample_plan[h] = plan
                p = os.path.join(self.args.from_raw, "raw-%s.txt" % h)
                try:
                    text = open(p).read()
                    if text.startswith("@@error "):  # a test file standing for a failed probe
                        results[h] = ("", text.split("\n", 1)[0][8:].strip(), 0, False)
                    else:
                        results[h] = (text, None if "@@end" in text else "probe incomplete", 0, False)
                except OSError:
                    results[h] = ("", "ssh failed (no raw file)", 0, False)
                continue
            todo[h] = self.probe_params(h)
        # The in-flight marker, written before any probe that may take a sample: a sample lost together with its
        # probe (apply_sample_lost) or with this collector (recover_inflight, next run) is never forgotten.
        live = [h for h in todo if h in self.sample_plan and not self.args.sample_dry]
        for h in live:
            self.state["cards"].setdefault(self.sample_plan[h], {}).setdefault("sample", {})["inflight_ms"] = ms(self.now)
        if live:
            self.save_state()
        with cf.ThreadPoolExecutor(max_workers=5) as ex:
            for h, params in todo.items():
                script = compose_script(params, etlh, remote)
                target = (self.config.get("ssh") or {}).get(h) or lab_hosts[h].get("ssh") or h
                local = (h == self.this_host)
                tmo = PROBE_SAMPLE_TIMEOUT_S if h in live else PROBE_TIMEOUT_S
                jobs[h] = ex.submit(run_probe, h, target, local, script, tmo)
            if not self.args.no_sessions and not self.args.from_raw:
                jobs["@claudes"] = ex.submit(run_cmd, ["timeout", "60", "claudes", "status"], 65)
                jobs["@sessions"] = ex.submit(run_cmd, ["timeout", "20", "spacesheep", "sessions", "list",
                                                        "--limit", "50"], 25)
            for k, fut in jobs.items():
                if k.startswith("@"):
                    raw[k] = fut.result()
                else:
                    out, err, took = fut.result()
                    results[k] = (out, err, took, False)
        if self.args.from_raw and not self.args.no_sessions:
            for k, fn in (("@claudes", "claudes.txt"), ("@sessions", "sessions.json")):
                try:
                    raw[k] = (open(os.path.join(self.args.from_raw, fn)).read(), 0)
                except OSError:
                    pass
        self.probe_wall_s = round(time.time() - t_start, 1)
        self.raw_results = results
        return self.build(results, raw)

    def recover_inflight(self):
        """A marker left by an earlier run means that collector stopped while a probe that could take a sample was
        out: whether the sample ran is unknown, so the card's sample is disabled until a person looks."""
        for cid, cs in self.state["cards"].items():
            ss = cs.get("sample") or {}
            if ss.get("inflight_ms"):
                ss["disabled"] = True
                ss["result"] = "failed: interrupted (the collector stopped during a sample attempt)"
                ss["last_try_ms"] = ss.pop("inflight_ms")
                self.errors.append("%s: the last run stopped during a sample attempt; sampling is off until "
                                   "update.sh sample-reset %s" % (cid, cid))

    def probe_params(self, h):
        hc = self.lab["hosts"][h]
        excl = [c["pci"] for cid, c in self.lab["cards"].items() if c.get("host") == h and c.get("excluded")]
        hs = self.state["hosts"].get(h, {})
        health = bool(self.args.health or not hs.get("health_ms")
                      or ms(self.now) - hs["health_ms"] >= (HEALTH_EVERY_S - 120) * 1000)
        self.health_ran[h] = health
        p = {"DASH_TREE": hc.get("tree", "nekko"), "DASH_EXCLUDE_PCI": " ".join(excl), "DASH_HEALTH": int(health)}
        plan = self.plan_sample(h)
        if plan:
            c = self.lab["cards"][plan]
            cs = self.state["cards"].get(plan, {})
            boot = str((self.config.get("sample_boot") or {}).get(h) or "")
            p.update({"DASH_SAMPLE_CARD": plan, "DASH_SAMPLE_PCI": c["pci"], "DASH_SAMPLE_DEVNUM": c["devnum"],
                      "DASH_SAMPLE_ETDEV": c["devnum"] if len(hc["cards"]) > 1 else "",
                      "DASH_SAMPLE_LOCK": "/run/lock/etsoc-shire%d.lock" % c["devnum"],
                      "DASH_SAMPLE_BIN": hc.get("ettelem", ""), "DASH_SAMPLE_EVERY_MIN": self.sample_every_min,
                      "DASH_SAMPLE_BOOT": boot if re.match(r"^[0-9a-f-]{36}$", boot) else "",
                      "DASH_SAMPLE_SQ_PREV": cs["sq"] if isinstance(cs.get("sq"), int) else "",
                      "DASH_SAMPLE_SQ_BOOT": cs.get("boot") or "",
                      "DASH_SAMPLE_DRY": 1 if self.args.sample_dry else 0})
            self.sample_plan[h] = plan
        for k, v in p.items():
            if not re.match(r"^[A-Za-z0-9 ._/:-]*$", str(v)):
                raise SystemExit("collect.py: refusing probe parameter %s=%r" % (k, v))
        return p

    def plan_sample(self, h):
        """The card to sample on host h this run, or None (DESIGN.md §2.6): never an excluded card, never
        aifoundry1 card 0, at most one card per host, not more often than every sample_every_min (>= 10)."""
        if not self.sample_enabled:
            return None
        best = None
        for cid, dn in self.lab["hosts"][h]["cards"].items():
            c = self.lab["cards"].get(cid, {})
            if c.get("excluded") or (h == "aifoundry1" and dn == 0):
                continue
            ss = self.state["cards"].get(cid, {}).get("sample", {})
            if ss.get("disabled"):
                continue
            if not self.args.sample_dry:
                if ss.get("last_try_ms") and ms(self.now) - ss["last_try_ms"] < self.sample_every_min * 60000:
                    continue
                if ss.get("next_after_ms") and ms(self.now) < ss["next_after_ms"]:
                    continue
            key = ss.get("last_try_ms") or 0
            if best is None or key < best[0]:
                best = (key, cid)
        return best[1] if best else None

    # -------------------------------------------------------------- building data.json
    def build(self, results, raw):
        now = self.now
        self.alerts = {}
        hosts, cards, host_people, hist_h, hist_c = {}, {}, {}, {}, {}
        self.nodewatch_buckets = {}
        os.makedirs(os.path.join(self.out, "raw"), mode=0o700, exist_ok=True)
        for h, hc in self.lab["hosts"].items():
            hs = self.state["hosts"].setdefault(h, {})
            res = results.get(h)
            fresh = None
            if res is not None:
                text, err, took, skipped = res
                if text and not skipped and not self.args.from_raw:
                    write_atomic(os.path.join(self.out, "raw", "%s.txt" % h), text)
                if err is None:
                    try:
                        fresh = self.parse_host(h, text, took)
                    except Exception as e:  # a whole-host parse failure keeps the last good data
                        self.errors.append("%s: could not parse the probe (%s)" % (h, type(e).__name__))
                        err = "probe unparsable"
                if err is not None and not skipped and h in self.sample_plan:
                    self.apply_sample_lost(h, text, err)
                if fresh is not None:
                    hs.update(last_ok_ms=ms(now), fails_in_row=0, error=None, next_try_ms=None,
                              block=fresh["host"], cards_block=fresh["cards"], people=fresh["people"],
                              buckets=fresh["buckets"])
                else:
                    if not skipped:
                        hs["fails_in_row"] = hs.get("fails_in_row", 0) + (0 if err == "approval needed" else 1)
                        if err == "approval needed":
                            hs["next_try_ms"] = ms(now + RULES["approval_retry_min"] * 60)
                    hs["error"] = err
                    hs["last_fail_ms"] = ms(now)
                    hs["took_ms"] = took
            else:
                hs["error"] = NOT_PROBED  # --hosts left it out: its last data stays, with no alert and no history
            hosts[h], hcards = self.host_view(h, hs, fresh is not None)
            cards.update(hcards)
            host_people[h] = hs.get("people") or {}
            self.nodewatch_buckets[h] = hs.get("buckets") or []
        people = self.people_view(host_people, hosts, cards)
        owner = self.owner_view(raw, hosts)
        self.derive_alerts(hosts, cards, people, owner)
        alerts = self.rank_alerts()
        self.apply_levels(hosts, cards, alerts)
        status = self.status_view(alerts)
        hist_line = self.history_line(hosts, cards)
        history = self.history_view(hist_line)
        for h, hb in hosts.items():
            if (hb.get("nodewatch") or {}).get("present"):
                hb["nodewatch"]["gaps_48h"] = history["hosts"][h]["gaps"]
        data = {
            "schema": 1,
            "generated_at": iso(now), "generated_ms": ms(now),
            "collector": {"host": self.this_host, "code": git_code(), "took_s": round(time.time() - self.t_wall, 1),
                          "probe_wall_s": getattr(self, "probe_wall_s", None),
                          "interval_min": RULES["interval_min"], "cron_minute": RULES["cron_minute"],
                          "heartbeat_min": RULES["heartbeat_min"], "stale_after_min": RULES["stale_after_min"],
                          "card_sample": ("dry" if self.args.sample_dry else
                                          "on (every %d min)" % self.sample_every_min if self.sample_enabled else "off"),
                          "halted": self.halt_reason(), "last_deploy": self.last_deploy(),
                          "errors": [self.priv.scrub(e, 200) for e in self.errors]},
            "status": status,
            "fingerprint": None,
            "alerts": alerts,
            "hosts": hosts,
            "cards": cards,
            "people": people,
            "owner": owner,
            "history": history,
        }
        data["fingerprint"] = self.fingerprint(data)
        found = self.priv.check(data)
        if found:
            msg = "; ".join("%s at %s" % (name, path) for path, name in found[:10])
            print("collect.py: PRIVACY CHECK REFUSED data.json: %s" % msg, file=sys.stderr)
            self.log_refusal(msg)
            self.save_state()  # the card samples' results and the counters stay recorded (state.json never leaves)
            return 3
        text = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        write_atomic(os.path.join(self.out, "data.json"), text)
        self.append_history(hist_line)
        self.save_state()
        self.data = data
        if not self.args.quiet:
            self.print_summary(data)
        return 0

    def halt_reason(self):
        try:
            return open(os.path.join(self.out, "HALT")).read().strip()[:200] or "halted"
        except OSError:
            return None

    def last_deploy(self):
        try:
            f = open(os.path.join(self.out, "deploy.state")).read().split()
            return {"at": iso(int(f[0])), "at_ms": int(f[0]) * 1000, "fingerprint": f[1] if len(f) > 1 else None}
        except (OSError, ValueError, IndexError):
            return None

    def log_refusal(self, msg):
        try:
            with open(os.path.join(self.out, "privacy-refusal.txt"), "w") as f:
                f.write("%s %s\n" % (iso(self.now), msg))
        except OSError:
            pass

    # -------------------------------------------------------------- one host
    def parse_host(self, h, text, took):
        secs = sections(text)
        err = self.errors

        def safe(name, fn, *a):
            try:
                return fn(*a)
            except Exception as e:
                err.append("%s: could not parse @@%s (%s)" % (h, name, type(e).__name__))
                return None
        meta = safe("meta", p_meta, secs.get("meta", [])) or {}
        if meta.get("hostname") and meta["hostname"] != h:
            err.append("%s: the probe answered as %s" % (h, self.priv.scrub(meta["hostname"], 40)))
        host_now = meta.get("now") or int(self.now)
        mem = safe("mem", p_mem, secs.get("mem", []))
        disks = safe("disk", p_disk, secs.get("disk", [])) or []
        kernel = safe("kernel", p_kernel, secs.get("kernel", []), meta.get("kernel"))
        systemd = safe("systemd", p_systemd, secs.get("systemd", []))
        temps = safe("temps", p_temps, secs.get("temps", []))
        pp = safe("sessions", p_people, secs, meta, self.now)
        people, nsess, ci_jobs = pp if pp else ({}, None, None)
        etwho = safe("etwho", p_etwho, secs.get("etwho", [])) or {"ok": False, "held": []}
        cp = safe("cards", p_cards, secs.get("cards", []))
        devs, nodes, lockfiles = cp if cp else ({}, [], {})
        guard = safe("guard", p_guard, secs.get("guard", []))
        nwp = safe("nodewatch", p_nodewatch, secs.get("nodewatch", []), host_now)
        if isinstance(nwp, tuple):
            nodewatch, buckets = nwp
        else:
            nodewatch, buckets = (nwp or {"present": False}), []
        exps = safe("experiments", p_experiments, secs.get("experiments", [])) or {"running": [], "last_log": None}
        tel = safe("telemetry", p_telemetry, secs.get("telemetry", [])) or {}
        manifest = safe("manifest", p_manifest, secs.get("manifest", []))
        health_exit = (secs.get("health_exit") or [None])[0]
        hs = self.state["hosts"].setdefault(h, {})
        health_at = self.now
        if health_exit == "skipped" and hs.get("health_raw") is not None:
            # et-lab-health runs hourly: this run keeps the last run's lines, with their time
            health_raw, health_exit = hs["health_raw"], hs.get("health_exit")
            health_at = (hs.get("health_ms") or ms(self.now)) / 1000
        else:
            health_raw = secs.get("health", [])
            if health_exit not in (None, "none", "skipped"):
                hs["health_raw"], hs["health_exit"], hs["health_ms"] = health_raw, health_exit, ms(self.now)
        health_lines = safe("health", p_health, health_raw) or []
        sample = safe("sample", p_sample, secs.get("sample", [])) if "sample" in secs else None
        self.apply_sample_results(h, sample)

        # health lines: the fields the collector keeps, the lines for the page (§2.3)
        zpools, zfs_notes, ci, power_profile, chrony, keep, klog = [], {}, None, None, None, [], {}
        klog_window = None
        for ln in health_lines:
            c, t = ln["check"], ln["text"]
            if c in ("host", "logins", "holders"):
                continue
            if c == "ci runner":
                m = re.search(r" (\w+)/(\w+), jobs running: (\d+)", t)
                ci = ci or {"units": 0, "active": 0, "jobs": 0}
                ci["units"] += 1
                if m and m.group(1) == "active":
                    ci["active"] += 1
                if m:
                    ci["jobs"] = max(ci["jobs"], int(m.group(3)))
                continue
            if c.startswith("zfs "):
                pool = c[4:]
                m = re.match(r"(\S+), (\d+)% full", t)
                if m:
                    zpools.append({"pool": pool, "state": m.group(1), "used_pct": int(m.group(2)), "note": None})
                else:
                    m2 = re.search(r"with (\d+) errors on (.+?)(?:;|\))", t)
                    zfs_notes[pool] = ("%s errors at the last scrub (%s)" % (m2.group(1), m2.group(2)) if m2
                                       else self.priv.scrub(t, 160))
            elif c == "power":
                m = re.match(r"profile (\S+)", t)
                power_profile = m.group(1) if m else None
            elif c == "kernel log":
                w = re.search(r"cover only its last ([\d.]+) h", t)
                klog_window = float(w.group(1)) if w else None
            elif c == "time":
                chrony = {"synced": ln["level"] == "OK", "offset_ms": None, "text": self.priv.scrub(t, 80)}
            elif c.startswith("card "):
                bdf = c[5:]
                m = re.search(r"kernel log: (\d+) (card error events|refused second opens)", t)
                m2 = re.search(r"kernel log: enabled (\d+) times", t)
                w = re.search(r"in the last ([\d.]+) h", t)
                d = klog.setdefault(bdf, {"error_events": 0, "refused_opens": 0, "enables": None, "window_h": None})
                if m:
                    d["error_events" if m.group(2).startswith("card") else "refused_opens"] = int(m.group(1))
                if m2:
                    d["enables"] = int(m2.group(1))
                if w:
                    d["window_h"] = float(w.group(1))
            keep.append({"level": ln["level"], "check": self.priv.scrub(c, 40), "text": self.priv.scrub(t, 240)})
        for z in zpools:
            z["note"] = zfs_notes.get(z["pool"])
        zfs = None
        if zpools:
            worst = max(zpools, key=lambda z: (z["state"] != "ONLINE", z["used_pct"]))
            zfs = dict(worst, pools=zpools)
        if manifest and manifest.get("power") and not power_profile:
            m = re.search(r"profile=(\S+)", manifest["power"])
            power_profile = m.group(1) if m and m.group(1) else None
        up_h = round(meta["uptime_s"] / 3600, 1) if meta.get("uptime_s") else None
        for d in klog.values():
            if d["window_h"] is None:
                d["window_h"] = klog_window or up_h
            if d["enables"] is None:
                d["enables"] = 1
        host = {
            "reachable": True, "via": "local" if h == self.this_host else "ssh", "error": None,
            "answered_at": iso(self.now), "answered_ms": ms(self.now), "took_ms": took,
            "uptime_h": up_h, "boot_id8": (meta.get("boot") or "")[:8] or None,
            "load": meta.get("load"), "mem": mem, "disks": disks, "zfs": zfs, "kernel": kernel,
            "systemd": systemd, "temps": temps, "power_profile": power_profile, "chrony": chrony,
            "health": {"rev": 3, "exit": num(health_exit, int), "warn": sum(1 for x in keep if x["level"] == "WARN"),
                       "info": sum(1 for x in keep if x["level"] == "INFO"), "lines": keep,
                       "at": iso(health_at), "at_ms": ms(health_at)},
            "manifest": {k: manifest.get(k) for k in ("cpu", "et_soc1", "srcversion", "libetrt", "libdevicelayer")}
            if manifest else None,
            "ci_runner": dict(ci, jobs_now=ci_jobs) if ci else None,
            "logins": {"sessions": nsess, "people": len([p for p in people.values()
                                                          if p["sessions"] + p["closing"] > 0])},
            "nodewatch": {k: v for k, v in nodewatch.items()},
            "experiments": {"running": exps.get("running", []),
                            "last_log": self.scrub_log(exps.get("last_log")),
                            "our_device_procs": exps.get("our_device_procs", 0),
                            "others_device_procs": sum(p["device_procs"] for u, p in people.items() if u != self.owner),
                            "ci_jobs": ci_jobs},
            "etwho_ok": etwho.get("ok"),
            "host_now": host_now, "tz": meta.get("tz"),
        }
        for bdf in devs:
            klog.setdefault(bdf, {"error_events": 0, "refused_opens": 0, "enables": 1,
                                  "window_h": klog_window or up_h})
        cards_out = self.parse_cards(h, meta, devs, nodes, lockfiles, etwho, guard, klog, tel, sample)
        return {"host": host, "cards": cards_out, "people": people, "buckets": buckets}

    def scrub_log(self, ll):
        if not ll:
            return None
        return dict(ll, file=self.priv.scrub(ll.get("file"), 80), line=self.priv.scrub(ll.get("line"), 200))

    def parse_cards(self, h, meta, devs, nodes, lockfiles, etwho, guard, klog, tel, sample):
        out = {}
        hc = self.lab["hosts"][h]
        by_devnum = {}
        for b, d in devs.items():
            dn = num(d["attrs"].get("devnum"), int)
            if dn is not None:
                by_devnum[dn] = b
        # holders from et-who: /dev/etN_mgmt, /dev/etN_ops, lock:etsoc-shireN.lock -> N
        holds = {}
        for x in etwho.get("held", []):
            m = re.match(r"/dev/et(\d+)_|lock:etsoc-shire(\d+)\.lock", x["node"])
            if m:
                n = int(m.group(1) or m.group(2))
                holds.setdefault(n, []).append(x)
        for cid, dn in hc["cards"].items():
            lc = self.lab["cards"].get(cid, {})
            cs = self.state["cards"].setdefault(cid, {})
            bdf = lc.get("pci")
            numbering = None
            if not lc.get("excluded"):
                if bdf in devs and num(devs[bdf]["attrs"].get("devnum"), int) not in (None, dn):
                    numbering = "devnum at %s is %s, expected %s" % (bdf, devs[bdf]["attrs"].get("devnum"), dn)
                if bdf not in devs and dn in by_devnum:
                    bdf = by_devnum[dn]
            d = devs.get(bdf)
            present = d is not None
            a = d["attrs"] if d else {}
            link = None
            if d:
                sp, wd = a.get("current_link_speed"), num(a.get("current_link_width"), int)
                msp, mwd = a.get("max_link_speed"), num(a.get("max_link_width"), int)
                speed = sp.replace(" PCIe", "") if sp else None
                mspeed = msp.replace(" PCIe", "") if msp else None
                down = not wd or not speed or speed.lower().startswith("unknown")
                full = (speed == "16.0 GT/s" and wd == 8) if not mspeed else (speed == mspeed and wd == mwd)
                link = {"speed": speed, "width": wd, "max_speed": mspeed, "max_width": mwd, "ok": (not down) and full,
                        "down": down}
            errors = None
            if d:
                ce = {k: v for k, v in d["ce"].items() if v}
                uce = {k: v for k, v in d["uce"].items() if v}
                prev_ce, prev_uce = cs.get("ce"), cs.get("uce")
                same_boot = cs.get("boot") == meta.get("boot")
                ce_new = uce_new = None
                if prev_ce is not None and same_boot:
                    ce_new = {k: v - prev_ce.get(k, 0) for k, v in d["ce"].items() if v - prev_ce.get(k, 0) > 0}
                    uce_new = {k: v - prev_uce.get(k, 0) for k, v in d["uce"].items()
                               if prev_uce is not None and v - prev_uce.get(k, 0) > 0}
                errors = {"ce": ce, "uce": uce, "ce_new": ce_new, "uce_new": uce_new}
                cs["ce"], cs["uce"] = d["ce"], d["uce"]
            aer = None
            if d:
                port = d.get("aer_port")
                rate = None
                if port is not None and cs.get("aer_port") is not None and cs.get("boot") == meta.get("boot") \
                        and cs.get("aer_port_ms") and port >= cs["aer_port"]:
                    dh = (ms(self.now) - cs["aer_port_ms"]) / 3.6e6
                    rate = round((port - cs["aer_port"]) / dh) if dh > 0.05 else None
                if rate is None and port is not None and meta.get("uptime_s"):
                    rate = round(port / (meta["uptime_s"] / 3600 + 0.001))
                aer = {"card_total": num(a.get("aer_card"), int), "port_total": port, "port_per_h": rate,
                       "root_port": d.get("root_port")}
                if port is not None:
                    cs["aer_port"], cs["aer_port_ms"] = port, ms(self.now)
            # activity: the submission-queue counters moved since the last run, net of our own sample
            activity = None
            if d and not d["excluded"]:
                sq = (num(a.get("mgmt_sq"), int) or 0) + (num(a.get("ops_sq"), int) or 0)
                own = 0
                if sample and sample.get("ran") and self.sample_plan.get(h) == cid:
                    r = sample["ran"]
                    if r.get("before") is not None and r.get("after") is not None:
                        own = max(0, r["after"] - r["before"])
                used = None
                if cs.get("sq") is not None and cs.get("boot") == meta.get("boot") and sq >= cs["sq"]:
                    used = (sq - cs["sq"] - own) > 0
                holders_now = [x["login"] for x in holds.get(dn, [])]
                if used:
                    cs["last_used_ms"] = ms(self.now)
                    cs["last_used_by"] = (holders_now[0] if holders_now else None)
                activity = {"mgmt": num(a.get("mgmt_sq"), int), "ops": num(a.get("ops_sq"), int), "used": used,
                            "last_used_at": iso(cs["last_used_ms"] / 1000) if cs.get("last_used_ms") else None,
                            "last_used_ms": cs.get("last_used_ms"), "last_used_by": cs.get("last_used_by")}
                cs["sq"] = sq
            if d:
                cs["boot"] = meta.get("boot")
            holder = None
            if etwho.get("ok"):
                who = [{"node": x["node"], "login": x["login"], "etime_s": x["etime_s"],
                        "ours": x["login"] == self.owner, "system": x["login"] == "root"} for x in holds.get(dn, [])]
                holder = {"held": bool(who), "who": who}
            telemetry = ({"source": "none"} if lc.get("excluded") else
                         self.card_telemetry(cid, tel.get(cid, []), sample if self.sample_plan.get(h) == cid else None))
            out[cid] = {
                "host": h, "devnum": dn, "pci": bdf, "lock": "etsoc-shire%d.lock" % dn,
                "lock_owner": lockfiles.get("etsoc-shire%d.lock" % dn),
                "label": lc.get("label", cid), "excluded": bool(lc.get("excluded")), "note": lc.get("note"),
                "present": present, "numbering": numbering,
                "static": {k: lc.get(k) for k in ("firmware", "bl", "pmic", "minion", "tdp_w", "clock", "policy",
                                                  "idle_c", "idle_w")},
                "link": link,
                "power_state": a.get("power_state") if d and not d["excluded"] else None,
                "enabled": (a.get("enable") == "1") if d and not d["excluded"] and a.get("enable") else None,
                "errors": errors, "aer": aer,
                "kernel_log": klog.get(bdf),
                "activity": activity, "holder": holder,
                "telemetry": telemetry,
                "sample": self.card_sample_view(cid),
                "guard": guard if guard else None,
                "level": None, "reasons": [],
            }
        return out

    def card_telemetry(self, cid, files, sample):
        """The newest reading: a live sample (this run or an earlier one) or an experiment file on the card's own
        host; with its source and age."""
        cs = self.state["cards"].setdefault(cid, {})
        best = None
        for f in files:
            if not f.get("line"):
                continue
            t = parse_tel_line(f["kind"], f["line"])
            if not t or (t.get("die_c") is None and t.get("board_w") is None):
                continue
            t["at_s"] = t["at_s"] or f.get("mtime")
            t["from"] = self.priv.scrub(f.get("from"), 120)
            t["source"] = "experiment"
            if best is None or (t["at_s"] or 0) > (best["at_s"] or 0):
                best = t
        if sample and sample.get("tel"):
            t = parse_tel_line("live", sample["tel"][-1])
            if t:
                t["source"], t["from"] = "live", "ettelem sample"
                t["at_s"] = t["at_s"] or self.now
                cs["live"] = t
        live = cs.get("live")
        if live and (best is None or (live.get("at_s") or 0) >= (best.get("at_s") or 0)):
            best = dict(live)
        if best and best.get("source") == "experiment":
            # a marks line carries only die and clock: fill watts and the like from an ettelem line of the same
            # card within 15 minutes of it
            for f in files:
                if f.get("kind") != "ettelem" or not f.get("line"):
                    continue
                t = parse_tel_line("ettelem", f["line"])
                ta = (t or {}).get("at_s") or f.get("mtime")
                if t and ta and best.get("at_s") and abs(ta - best["at_s"]) <= 900:
                    for k in ("die_max_c", "pmic_c", "board_w", "noc_mhz", "ddr_mhz"):
                        if best.get(k) is None and t.get(k) is not None:
                            best[k] = t[k]
        if not best:
            return {"source": "none"}
        at = best.pop("at_s", None)
        best["at"], best["at_ms"] = iso(at), ms(at)
        best["age_min"] = round((self.now - at) / 60) if at else None
        return best

    def card_sample_view(self, cid):
        ss = self.state["cards"].get(cid, {}).get("sample", {})
        return {"enabled": self.sample_enabled and not ss.get("disabled"),
                "disabled": bool(ss.get("disabled")),
                "last_try": iso(ss["last_try_ms"] / 1000) if ss.get("last_try_ms") else None,
                "result": ss.get("result") or ("disabled" if not self.sample_enabled else None),
                "next_after": iso(ss["next_after_ms"] / 1000) if ss.get("next_after_ms") else None}

    SAMPLE_SKIP = {"etwho": "held", "experiment": "our experiment", "others": "a device process or CI job",
                   "people": "someone active", "stamp": "too soon", "quiet": "card used since the last run",
                   "boot": "boot not confirmed", "lock": "lock file", "binary": "binary", "card": "card",
                   "time": "probe too slow"}

    def apply_sample_results(self, h, sample):
        """Record this run's sample (or dry run) in the card's state (DESIGN.md §2.6)."""
        cid = self.sample_plan.get(h)
        if not cid:
            return
        ss = self.state["cards"].setdefault(cid, {}).setdefault("sample", {})
        rc = None
        if not sample:
            result = "failed: no sample section"
        else:
            failed = next((g for g in sample["gates"] if not g["ok"]), None)
            if failed:
                result = "skipped: %s" % self.SAMPLE_SKIP.get(failed["gate"], failed["gate"])
            elif sample.get("would_run"):
                result = "dry: would run"
            elif sample.get("ran"):
                rc = sample["ran"]["rc"]
                if rc == 97:
                    result = "skipped: lock held"
                elif rc == 98:
                    result = "skipped: lock file would not open"
                elif rc == 124:
                    result = "failed: timeout (stopped by SIGTERM)"
                elif rc == 137:
                    result = "failed: killed after the timeout (queue likely poisoned)"
                elif sample["tel"]:
                    result = "ok"
                else:
                    result = "failed: no output (exit %s)" % rc
            elif sample.get("started"):
                result = "failed: started, no result"
            else:
                result = "failed: no result"
        self.sample_results = getattr(self, "sample_results", {})
        self.sample_results[cid] = {"result": result, "gates": sample["gates"] if sample else [],
                                    "would_run": sample.get("would_run") if sample else None}
        if self.args.sample_dry:
            return
        ss.pop("inflight_ms", None)
        ss["last_try_ms"] = ms(self.now)
        ss["result"] = result
        ss["rc"] = rc
        if result.startswith("failed: no output"):
            ss["no_output_in_row"] = ss.get("no_output_in_row", 0) + 1
            if ss["no_output_in_row"] >= 2:
                ss["next_after_ms"] = ms(self.now + RULES["sample_no_output_wait_min"] * 60)
        elif result == "ok":
            ss["no_output_in_row"] = 0
            ss["next_after_ms"] = None
        if rc in (124, 137) or result.startswith("failed: started"):
            ss["disabled"] = True

    def apply_sample_lost(self, h, text, err):
        """The probe of a host with a planned sample failed. If its output shows the sample started (the "start"
        line, or every gate passed) with no "ran" line, the sample may have been cut off mid-request: disable it."""
        cid = self.sample_plan.get(h)
        if not cid:
            return
        ss = self.state["cards"].setdefault(cid, {}).setdefault("sample", {})
        self.sample_results = getattr(self, "sample_results", {})
        if cid in self.sample_results:
            return  # recorded by apply_sample_results before the parse failed
        secs = sections(text or "")
        smp = p_sample(secs.get("sample", [])) if "sample" in secs else None
        started = bool(smp) and not smp.get("ran") and not smp.get("would_run") and (
            smp["started"] or (smp["gates"] and all(g["ok"] for g in smp["gates"])
                               and any(g["gate"] == "time" for g in smp["gates"])))
        if self.args.sample_dry:
            self.sample_results[cid] = {"result": "dry: the probe failed (%s)" % err,
                                        "gates": smp["gates"] if smp else [], "would_run": None}
            return
        if started:
            result = "failed: lost with the probe (%s) after it started" % err
            ss["disabled"] = True
        else:
            result = "skipped: the probe failed (%s) before the sample" % err
        ss.pop("inflight_ms", None)
        ss["last_try_ms"] = ms(self.now)
        ss["result"] = result
        self.sample_results[cid] = {"result": result, "gates": smp["gates"] if smp else [], "would_run": None}

    def host_view(self, h, hs, fresh):
        """The host block and its cards, fresh or from the last good run (stale)."""
        block = hs.get("block")
        cblock = hs.get("cards_block") or {}
        if block is None:
            block = {"reachable": False, "via": None, "answered_at": None, "uptime_h": None, "load": None,
                     "mem": None, "disks": [], "zfs": None, "kernel": None, "systemd": None, "temps": None,
                     "power_profile": None, "chrony": None, "health": None, "manifest": None, "ci_runner": None,
                     "logins": None, "nodewatch": {"present": False}, "experiments": None}
        block = json.loads(json.dumps(block))
        block["reachable"] = bool(fresh)
        block["error"] = None if fresh else hs.get("error")
        block["last_ok_at"] = iso(hs["last_ok_ms"] / 1000) if hs.get("last_ok_ms") else None
        block["last_ok_ms"] = hs.get("last_ok_ms")
        block["fails_in_row"] = hs.get("fails_in_row", 0)
        block["next_try_at"] = iso(hs["next_try_ms"] / 1000) if hs.get("next_try_ms") else None
        block["next_try_ms"] = hs.get("next_try_ms")
        if not fresh:
            block["stale"] = True
            block["as_of"] = block["last_ok_at"]
            if "took_ms" in hs:
                block["took_ms"] = hs["took_ms"]
        block.pop("host_now", None)
        cards = {}
        for cid in self.lab["hosts"][h]["cards"]:
            c = json.loads(json.dumps(cblock.get(cid))) if cblock.get(cid) else None
            if c is None:
                lc = self.lab["cards"].get(cid, {})
                c = {"host": h, "devnum": self.lab["hosts"][h]["cards"][cid], "pci": lc.get("pci"),
                     "label": lc.get("label", cid), "excluded": bool(lc.get("excluded")), "note": lc.get("note"),
                     "present": None, "static": {k: lc.get(k) for k in ("firmware", "bl", "pmic", "minion", "tdp_w",
                                                                         "clock", "policy", "idle_c", "idle_w")},
                     "link": None, "errors": None, "aer": None, "kernel_log": None, "activity": None,
                     "holder": None, "telemetry": {"source": "none"}, "guard": None}
            tl = c.get("telemetry") or {}
            if tl.get("at_ms"):
                tl["age_min"] = round((ms(self.now) - tl["at_ms"]) / 60000)
            if not fresh:
                c["stale"] = True
                c["as_of"] = block["last_ok_at"]
                if c.get("errors"):
                    c["errors"]["ce_new"] = None
                    c["errors"]["uce_new"] = None
                if c.get("activity"):
                    c["activity"]["used"] = None
            c["sample"] = self.card_sample_view(cid)
            cards[cid] = c
        return block, cards

    # -------------------------------------------------------------- people and owner
    def people_view(self, host_people, hosts, cards):
        rank = {"active": 0, "idle": 1, "away": 2, "processes only": 3}
        merged = {}
        for h, pl in host_people.items():
            for login, e in pl.items():
                m = merged.setdefault(login, {"login": login, "owner": login == self.owner, "status": None,
                                              "hosts": {}, "card_holds": [], "device_procs": 0, "stale_hosts": []})
                m["hosts"][h] = {k: e.get(k) for k in ("sessions", "closing", "ttys", "idle_min", "procs")}
                m["device_procs"] += e.get("device_procs", 0)
                if not hosts[h]["reachable"]:
                    m["stale_hosts"].append(h)
                    m["hosts"][h]["stale"] = True
                st = self.person_status(e)
                m["hosts"][h]["status"] = st  # on this machine; "status" below is the person's best
                if st and (m["status"] is None or rank[st] < rank[m["status"]]):
                    m["status"] = st
        for cid, c in cards.items():
            for w in ((c.get("holder") or {}).get("who") or []):
                if w["login"] in merged:
                    ch = merged[w["login"]]["card_holds"]
                    same = next((x for x in ch if x["card"] == cid), None)
                    if same:  # the lock and the nodes of one card are one hold
                        same["etime_s"] = max(same["etime_s"] or 0, w.get("etime_s") or 0)
                        continue
                    ch.append({"card": cid, "etime_s": w.get("etime_s")})
                elif w["login"] not in ("root", "?"):
                    merged[w["login"]] = {"login": w["login"], "owner": w["login"] == self.owner,
                                          "status": "processes only", "hosts": {}, "device_procs": 0,
                                          "stale_hosts": [],
                                          "card_holds": [{"card": cid, "etime_s": w.get("etime_s")}]}
        for m in merged.values():
            m["status"] = m["status"] or "processes only"
            idles = [x["idle_min"] for x in m["hosts"].values() if x.get("idle_min") is not None]
            m["idle_min"] = min(idles) if idles else None
        return sorted(merged.values(), key=lambda m: (not m["owner"], rank[m["status"]], m["login"]))

    def person_status(self, e):
        if e.get("sessions", 0) == 0:
            return "processes only" if (e.get("closing") or e.get("procs")) else None
        if e.get("notty_sessions"):
            return "active"
        idle = e.get("idle_min")
        if idle is None:
            return "active"
        if idle < RULES["active_min"]:
            return "active"
        if idle < RULES["away_min"]:
            return "idle"
        return "away"

    def owner_view(self, raw, hosts):
        so = self.state["owner"]
        claudes = None
        if "@claudes" in raw and raw["@claudes"][0]:
            try:
                claudes = self.parse_claudes(raw["@claudes"][0])
                so["claudes"] = claudes
            except Exception as e:
                self.errors.append("claudes status: could not parse (%s)" % type(e).__name__)
        elif "@claudes" in raw:
            self.errors.append("claudes status failed (%s)" % raw["@claudes"][1])
        if claudes is None and so.get("claudes"):
            claudes = dict(so["claudes"], stale=True)
        sessions = None
        if "@sessions" in raw and raw["@sessions"][0]:
            try:
                sessions = self.parse_sessions(raw["@sessions"][0])
                so["sessions"] = sessions
            except Exception as e:
                self.errors.append("spacesheep sessions list: could not parse (%s)" % type(e).__name__)
        elif "@sessions" in raw:
            self.errors.append("spacesheep sessions list failed (%s)" % raw["@sessions"][1])
        if sessions is None and so.get("sessions"):
            sessions = dict(so["sessions"], stale=True)
        nw = {}
        for h, hb in hosts.items():
            n = hb.get("nodewatch") or {}
            if n.get("present"):
                nw[h] = {"tmux": n.get("tmux"), "claude": n.get("claude"), "linger": n.get("linger"),
                         "user_manager": n.get("user_manager"), "beat_age_min": n.get("beat_age_min"),
                         "stale": not hb["reachable"]}
        return {"login": self.owner, "host": self.lab.get("owner_host"), "claudes": claudes, "sessions": sessions,
                "nodewatch": nw}

    def parse_claudes(self, text):
        now = dt.datetime.fromtimestamp(self.now).astimezone()
        accounts, pins, tmux, watchdog = {}, [], [], None
        procs = {}
        in_table = False
        for ln in text.splitlines():
            m = re.match(r"^account (\d+)\s+(.*?)\s+home \S+\s+tmux (\S+)\s+login (.*)$", ln)
            if m:
                n, who, sess, lapse = int(m.group(1)), m.group(2).strip(), m.group(3), m.group(4)
                logged_in = not who.startswith("NOT LOGGED IN")
                lapses, days = None, None
                ml = re.search(r"lapses \w{3} (\d{1,2}) (\w{3})", lapse)
                if ml:
                    for y in (now.year - 1, now.year, now.year + 1):
                        try:
                            d = dt.datetime.strptime("%s %s %d" % (ml.group(1), ml.group(2), y), "%d %b %Y").date()
                        except ValueError:
                            continue
                        dd = (d - now.date()).days
                        if -40 <= dd <= 330:
                            lapses, days = d.isoformat(), dd
                            break
                accounts[n] = {"n": n, "logged_in": logged_in, "wrong_account": "EXPECTED" in who,
                               "lapses": lapses, "lapse_days": days, "tmux": re.sub(r"[^\w.-]", "", sess)[:20],
                               "server": False, "phones": 0, "sessions": 0,
                               "credentials_note": None if ml or not logged_in else self.priv.scrub(lapse, 60)}
                continue
            m = re.match(r"^pin (\w{8})\s+account (\d+)\s+\S+?:(\S+)\s+(running|DOWN)", ln)
            if m:
                pins.append({"id8": m.group(1), "account": int(m.group(2)), "window": m.group(3)[:20],
                             "running": m.group(4) == "running"})
                continue
            if ln.startswith("watchdog:"):
                if "OFF" in ln:
                    watchdog = {"on": False, "last_run": None, "age_min": None}
                else:
                    mw = re.search(r"last at (\w{3}) (\d\d):(\d\d):(\d\d)", ln)
                    last = None
                    if mw:
                        for back in range(0, 8):
                            d = now - dt.timedelta(days=back)
                            cand = d.replace(hour=int(mw.group(2)), minute=int(mw.group(3)),
                                             second=int(mw.group(4)), microsecond=0)
                            if cand.strftime("%a") == mw.group(1) and cand <= now + dt.timedelta(seconds=60):
                                last = cand
                                break
                    watchdog = {"on": True, "last_run": last.isoformat(timespec="seconds") if last else None,
                                "age_min": round((now - last).total_seconds() / 60, 1) if last else None}
                continue
            m = re.match(r"^([\w.-]+): (\d+) windows \(created [^)]*\)( \(attached\))?", ln)
            if m:
                tmux.append({"name": m.group(1)[:20], "windows": int(m.group(2)), "attached": bool(m.group(3))})
                continue
            if re.match(r"^\s*PID\s+ACCT\s+KIND", ln):
                in_table = True
                continue
            if in_table:
                m = re.match(r"^\s*(\d+)\s+(\S+)\s+(\S+)\s+\S+", ln)
                if m:
                    procs.setdefault(m.group(2), []).append(m.group(3))
        for a, kinds in procs.items():
            n = num(a, int)
            if n in accounts:
                accounts[n]["server"] = "server" in kinds
                accounts[n]["phones"] = kinds.count("phone")
                accounts[n]["sessions"] = kinds.count("session")
        return {"as_of": iso(self.now), "accounts": [accounts[k] for k in sorted(accounts)], "pins": pins,
                "watchdog": watchdog, "tmux": tmux}

    def parse_sessions(self, text):
        d = json.loads(text)
        items = d.get("sessions") if isinstance(d, dict) else d
        by_machine, lab = {}, []
        lab_hosts = set(self.lab["hosts"])
        for s in items or []:
            if not isinstance(s, dict):
                continue
            mach = re.sub(r"[^\w.-]", "", str(s.get("machine") or "unknown"))[:32] or "unknown"
            if mach not in lab_hosts:
                mach = "other"  # the owner's machines outside the lab: one total, never their names
            state = re.sub(r"[^\w-]", "", str(s.get("state") or "unknown"))[:16]
            bm = by_machine.setdefault(mach, {"last_at": None, "last_ms": None})
            bm[state] = bm.get(state, 0) + 1
            la = s.get("last_at")
            if isinstance(la, (int, float)) and (bm["last_ms"] is None or la > bm["last_ms"]):
                bm["last_ms"], bm["last_at"] = int(la), iso(la / 1000)
            if mach != "other":
                lab.append({"machine": mach, "title": self.priv.scrub(s.get("title") or "", 60), "state": state,
                            "model": re.sub(r"[^\w.-]", "", str(s.get("model") or ""))[:40] or None,
                            "turns": s.get("turns") if isinstance(s.get("turns"), int) else None,
                            "started_at": iso(s["started_at"] / 1000) if isinstance(s.get("started_at"), (int, float)) else None,
                            "last_at": iso(la / 1000) if isinstance(la, (int, float)) else None,
                            "last_ms": int(la) if isinstance(la, (int, float)) else None,
                            "source": re.sub(r"[^\w.-]", "", str(s.get("source") or ""))[:20] or None})
        lab.sort(key=lambda x: -(x["last_ms"] or 0))
        working = sum(v.get("working", 0) for v in by_machine.values())
        return {"as_of": iso(self.now), "by_machine": by_machine, "lab": lab[:20], "working": working,
                "needs_you": sum(v.get("needs_you", 0) for v in by_machine.values())}

    # -------------------------------------------------------------- alerts (§5)
    def add(self, aid, level, scope, title, detail=None, host=None, card=None, source=None, stale=False):
        a = self.alerts.get(aid)
        if a and LEVELS[a["level"]] >= LEVELS[level]:
            return
        self.alerts[aid] = {"id": aid, "level": level, "scope": scope, "host": host, "card": card,
                            "title": self.priv.scrub(title, 120), "detail": self.priv.scrub(detail, 300),
                            "source": source, "since": None, "known": None, "ack": None, "stale": stale}

    def derive_alerts(self, hosts, cards, people, owner):
        R = RULES
        halt = self.halt_reason()
        if halt:
            self.add("collector:halt", "bad", "collector", "deploys halted: " + halt,
                     "update.sh stopped deploying after a visibility check failed; run update.sh status, then resume",
                     source="update.sh")
        for e in self.errors:
            self.add("collector:parse:%s" % hashlib.sha256(e.encode()).hexdigest()[:8], "warn", "collector", e,
                     source="collect.py")
        if self.sample_enabled:
            self.add("collector:card-sample", "info", "collector",
                     "card telemetry sampling is %s" % ("in dry mode" if self.args.sample_dry else "on"),
                     "at most one card per host per run, every %d min at most, behind every etiquette gate"
                     % self.sample_every_min, source="collect.py")
        for h, hb in hosts.items():
            st = not hb["reachable"]
            if st and hb.get("error") != NOT_PROBED:
                err = hb.get("error") or "no answer"
                last = hb.get("last_ok_at")
                det = "last data %s" % (fmt_hm(hb["last_ok_ms"] / 1000) if hb.get("last_ok_ms") else "never")
                if err == "approval needed":
                    det += "; Tailscale check approval needed (run `ssh %s true` on %s and approve)" % (
                        h, self.lab.get("owner_host"))
                    if hb.get("next_try_at"):
                        det += "; next try %s" % hb["next_try_at"][11:16]
                    self.add("host:%s:reach" % h, "warn", "host-down", "%s: approval needed" % h, det, host=h,
                             source="ssh")
                else:
                    lvl = "bad" if hb.get("fails_in_row", 0) >= 2 else "warn"
                    self.add("host:%s:reach" % h, lvl, "host-down", "%s unreachable: %s" % (h, err), det, host=h,
                             source="ssh")
                if hb.get("health") is None:
                    continue
            # from et-lab-health's WARN lines (card lines map to the card, the rest to the host)
            for ln in (hb.get("health") or {}).get("lines", []):
                if ln["level"] != "WARN":
                    if ln["level"] == "INFO" and ln["check"] == "reboot":
                        self.add("host:%s:reboot" % h, "info", "host", "reboot pending", ln["text"], host=h,
                                 source="et-lab-health", stale=st)
                    continue
                c, t = ln["check"], ln["text"]
                if c.startswith("card "):
                    cid = self.card_by_pci(h, c[5:], cards)
                    if "power or thermal" in t:
                        kind, title = "ce", "power or thermal events since the driver loaded"
                    elif "uncorrectable" in t:
                        kind, title = "uce", "uncorrectable events since the driver loaded"
                    elif "root port" in t:
                        kind, title = "aer-port", "root port corrected PCIe errors"
                    elif "link" in t:
                        kind, title = "link", "PCIe link below 16 GT/s x8"
                    else:
                        kind, title = "health", "et-lab-health warning"
                    if cid:
                        self.add("card:%s:%s" % (cid, kind), "warn", "card", title, t, host=h, card=cid,
                                 source="et-lab-health", stale=st)
                    else:
                        self.add("host:%s:%s" % (h, re.sub(r"\W+", "-", c)), "warn", "host", c + ": " + t, t, host=h,
                                 source="et-lab-health", stale=st)
                    continue
                if c.startswith("disk ") or c.startswith("zfs "):
                    continue  # from the collector's own numbers below
                slug = re.sub(r"[^\w/.-]+", "-", c).strip("-")
                self.add("host:%s:%s" % (h, slug), "warn", "host", "%s: %s" % (c, t.split(" (")[0]), t, host=h,
                         source="et-lab-health", stale=st)
            for d in hb.get("disks") or []:
                p = d.get("used_pct")
                if p is None:
                    continue
                lvl = "bad" if p >= R["disk_bad_pct"] else "warn" if p >= R["disk_warn_pct"] else None
                if lvl:
                    self.add("host:%s:disk:%s" % (h, d["mount"]), lvl, "host", "%s %d%% used" % (d["mount"], p),
                             "%s GiB free" % d.get("free_gib"), host=h, source="df", stale=st)
            for z in ((hb.get("zfs") or {}).get("pools") or []):
                p = z.get("used_pct") or 0
                lvl = "bad" if p >= R["disk_bad_pct"] else "warn" if (p >= R["disk_warn_pct"] or z["state"] != "ONLINE") else None
                if lvl:
                    self.add("host:%s:zfs:%s" % (h, z["pool"]), lvl, "host", "pool %s %d%% full (%s)" % (
                        z["pool"], p, z["state"]), z.get("note"), host=h, source="et-lab-health", stale=st)
                if z.get("note"):
                    self.add("host:%s:zfs-scrub:%s" % (h, z["pool"]), "info", "host", "pool %s: %s" % (z["pool"], z["note"]),
                             None, host=h, source="et-lab-health", stale=st)
            m = hb.get("mem") or {}
            if m.get("avail_pct") is not None and m["avail_pct"] < R["mem_warn_pct"]:
                self.add("host:%s:memory" % h, "warn", "host", "memory %d%% available" % m["avail_pct"], None, host=h,
                         source="meminfo", stale=st)
            ld = hb.get("load") or {}
            if not st and ld.get("per_thread") is not None and ld["per_thread"] > R["load_warn_per_thread"]:
                self.add("host:%s:load" % h, "warn", "host", "load %.1f per thread" % ld["per_thread"], None, host=h,
                         source="loadavg")
            sd = hb.get("systemd") or {}
            if sd.get("failed"):
                self.add("host:%s:systemd" % h, "warn", "host", "%d failed unit(s)" % len(sd["failed"]),
                         ", ".join(sd["failed"][:3]), host=h, source="systemctl", stale=st)
            ci = hb.get("ci_runner") or {}
            if ci.get("jobs"):
                self.add("host:%s:ci" % h, "info", "host", "CI runner job running", None, host=h, source="et-lab-health",
                         stale=st)
            nw = hb.get("nodewatch") or {}
            if not st and nw.get("present") and nw.get("beat_age_min") is not None:
                age = nw["beat_age_min"]
                last = fmt_when(nw["beat_at_ms"] / 1000, self.now) if nw.get("beat_at_ms") else "?"
                if age > R["nodewatch_bad_min"]:
                    self.add("host:%s:nodewatch" % h, "bad", "host", "nodewatch's last heartbeat at %s" % last,
                             "%d min before this check: its per-minute cron job may have stopped" % age, host=h,
                             source="nodewatch")
                elif age > R["nodewatch_warn_min"]:
                    self.add("host:%s:nodewatch" % h, "warn", "host", "nodewatch's last heartbeat at %s" % last,
                             "%d min before this check" % age, host=h, source="nodewatch")
            ex = hb.get("experiments") or {}
            if not st and ex.get("running"):
                self.add("host:%s:experiment" % h, "info", "host", "our experiment running: %s" % ", ".join(
                    r["kind"] for r in ex["running"]), None, host=h, source="pgrep")
        # cards
        for cid, c in cards.items():
            h = c["host"]
            st = bool(c.get("stale"))
            if c.get("present") is False:
                self.add("card:%s:missing" % cid, "bad", "card", "missing from the PCI bus",
                         "lab.json expects it at %s; no device is bound to the ET driver there" % c.get("pci"),
                         host=h, card=cid, source="sysfs", stale=st)
                continue
            if c.get("numbering"):
                self.add("card:%s:numbering" % cid, "warn", "card", "card numbering changed", c["numbering"],
                         host=h, card=cid, source="sysfs", stale=st)
            lk = c.get("link") or {}
            if lk.get("down"):
                self.add("card:%s:link" % cid, "bad", "card", "PCIe link down", None, host=h, card=cid,
                         source="sysfs", stale=st)
            elif lk and lk.get("ok") is False:
                self.add("card:%s:link" % cid, "warn", "card", "PCIe link %s x%s of %s x%s" % (
                    lk.get("speed"), lk.get("width"), lk.get("max_speed"), lk.get("max_width")), None, host=h,
                    card=cid, source="sysfs", stale=st)
            # "new since the last check" and "hot" need this run's data: never from a machine that did not answer
            er = c.get("errors") or {}
            if not st and er.get("uce_new"):
                self.add("card:%s:uce-new" % cid, "bad", "card", "new uncorrectable events", json.dumps(er["uce_new"]),
                         host=h, card=cid, source="err_stats", stale=st)
            if not st and er.get("ce_new"):
                self.add("card:%s:ce-new" % cid, "warn", "card", "new corrected events since the last check",
                         ", ".join("%s +%d" % kv for kv in er["ce_new"].items()), host=h, card=cid, source="err_stats",
                         stale=st)
            tl = c.get("telemetry") or {}
            if not st and tl.get("source") == "live" and tl.get("die_c") is not None and tl.get("at_ms") \
                    and ms(self.now) - tl["at_ms"] <= 30 * 60000:
                lvl = "bad" if tl["die_c"] >= R["die_bad_c"] else "warn" if tl["die_c"] >= R["die_warn_c"] else None
                if lvl:
                    self.add("card:%s:hot" % cid, lvl, "card", "die %d °C at %s" % (tl["die_c"], fmt_when(tl["at_ms"] / 1000, self.now)),
                             None, host=h, card=cid, source="ettelem", stale=st)
            sm = self.state["cards"].get(cid, {}).get("sample", {})
            if sm.get("disabled"):
                # the collector's own state, current even when the machine did not answer this run
                res = sm.get("result") or "failed"
                if sm.get("rc") == 137 or "killed" in res:
                    title = "telemetry sample killed after its timeout"
                    det = ("ettelem was still in a request 3 s after SIGTERM, so SIGKILL landed mid-request: the card's "
                           "management queue is likely poisoned and the next program to open the card may crash. Tell "
                           "the lab admin (a drain or reset is theirs); after that, update.sh sample-reset %s" % cid)
                elif sm.get("rc") == 124 or "timeout" in res:
                    title = "telemetry sample stopped by its timeout"
                    det = ("ettelem did not end its 2 s sample within 10 s and stopped on SIGTERM; a request may still "
                           "have been in flight. A person should check the card (a short kernel under its lock) before "
                           "anyone uses it; then update.sh sample-reset %s" % cid)
                else:
                    title = "telemetry sample cut off"
                    det = ("%s. Whether ettelem finished is unknown: a person should check the card before anyone "
                           "uses it; then update.sh sample-reset %s" % (res, cid))
                self.add("card:%s:sample-failed" % cid, "bad", "card", title, det, host=h, card=cid, source="collect.py")
            if not st:
                for w in ((c.get("holder") or {}).get("who") or []):
                    who = "system or CI" if w.get("system") else w["login"]
                    since = fmt_when(self.now - w["etime_s"], self.now) if w.get("etime_s") is not None else None
                    self.add("card:%s:held" % cid, "info", "card", "held by %s%s" % (
                        who, " since %s" % since if since else ""), w["node"], host=h, card=cid, source="et-who")
                    if w.get("etime_s") and w["etime_s"] > R["hold_long_s"]:
                        self.add("card:%s:held-long" % cid, "warn", "card", "held by the same process since %s" % since,
                                 "%s by %s, %d h at this check" % (w["node"], who, w["etime_s"] // 3600), host=h,
                                 card=cid, source="et-who")
                act = c.get("activity") or {}
                if act.get("used"):
                    self.add("card:%s:used" % cid, "info", "card", "used since the last check", None, host=h,
                             card=cid, source="vq counters")
        # owner (§5): on the owner's host
        oh = self.lab.get("owner_host")
        nwo = (owner.get("nodewatch") or {}).get(oh)
        if nwo and not nwo.get("stale"):
            if nwo.get("tmux") is False:
                self.add("owner:tmux", "bad", "owner", "tmux gone on %s" % oh, "nodewatch sees no tmux server",
                         host=oh, source="nodewatch")
            if nwo.get("claude") == 0:
                self.add("owner:claude", "bad", "owner", "no Claude process on %s" % oh, None, host=oh,
                         source="nodewatch")
            if nwo.get("linger") is False:
                self.add("owner:linger", "warn", "owner", "linger off on %s" % oh,
                         "systemd stops the user manager (and a snap tmux) 10 s after the last login", host=oh,
                         source="nodewatch")
        cl = owner.get("claudes") or {}
        if cl and not cl.get("stale"):
            for a in cl.get("accounts", []):
                if not a["logged_in"]:
                    self.add("owner:account:%d:login" % a["n"], "bad", "owner", "claudes account %d logged out" % a["n"],
                             "claudes login %d" % a["n"], source="claudes")
                elif a.get("wrong_account"):
                    self.add("owner:account:%d:login" % a["n"], "bad", "owner",
                             "claudes account %d signed in to the wrong account" % a["n"], None, source="claudes")
                elif a.get("lapse_days") is not None and a["lapse_days"] <= R["lapse_warn_days"]:
                    self.add("owner:account:%d:lapse" % a["n"], "warn", "owner", "account %d login lapses in %d days"
                             % (a["n"], a["lapse_days"]), a.get("lapses"), source="claudes")
            for p in cl.get("pins", []):
                if not p["running"]:
                    self.add("owner:pin:%s" % p["id8"], "warn", "owner", "pinned session %s down" % p["id8"],
                             "claudes up (or the watchdog) restarts it", source="claudes")
            wd = cl.get("watchdog") or {}
            if wd.get("on") is False:
                self.add("owner:watchdog", "warn", "owner", "claudes watchdog off", "claudes watch on", source="claudes")
            elif wd.get("age_min") is not None and wd["age_min"] > R["watchdog_warn_min"]:
                lr = (wd.get("last_run") or "")[11:16] or "?"
                self.add("owner:watchdog", "warn", "owner", "claudes watchdog last ran at %s" % lr,
                         "%d min before this check" % wd["age_min"], source="claudes")
            phones = sum(a.get("phones", 0) for a in cl.get("accounts", []))
            if phones:
                self.add("owner:phones", "info", "owner", "%d phone connection(s)" % phones, None, source="claudes")
        ss = owner.get("sessions") or {}
        if ss and ss.get("working"):
            self.add("owner:sessions", "info", "owner", "%d session(s) working" % ss["working"], None,
                     source="spacesheep")
        # people
        running = {h for h, hb in hosts.items() if hb["reachable"] and (hb.get("experiments") or {}).get("running")}
        for p in people:
            if p["owner"]:
                continue
            for hold in p["card_holds"]:
                self.add("people:%s:hold:%s" % (p["login"], hold["card"]), "info", "people", "%s holds %s" % (
                    p["login"], self.lab["cards"].get(hold["card"], {}).get("label", hold["card"])), None,
                    card=hold["card"], source="et-who")
            if p["status"] == "active":
                for h in p["hosts"]:
                    if h in running:
                        self.add("people:%s:active:%s" % (p["login"], h), "info", "people",
                                 "%s is active on %s while our experiment runs" % (p["login"], h), None, host=h,
                                 source="loginctl")

    def card_by_pci(self, h, bdf, cards):
        for cid, c in cards.items():
            if c["host"] == h and c.get("pci") == bdf:
                return cid
        return None

    def rank_alerts(self):
        since = self.state["alerts_since"]
        now_ms = ms(self.now)
        keep = {}
        acks = self.acks if isinstance(self.acks, dict) else {}
        out = []
        scope_rank = {"collector": 0, "host-down": 1, "card": 2, "host": 3, "owner": 4, "people": 5}
        for aid, a in self.alerts.items():
            keep[aid] = since.get(aid) or now_ms
            a["since_ms"] = keep[aid]
            a["since"] = iso(keep[aid] / 1000)
            a["raw_level"] = a["level"]
            if aid in self.known and a["level"] != "bad":
                a["known"] = self.known[aid]
                a["level"] = "info"
            ack = acks.get(aid)
            if ack and (ack.get("until_ms") or 0) > now_ms and a["level"] != "info":
                a["ack"] = {"until": ack.get("until"), "note": self.priv.scrub(ack.get("note"), 120)}
                a["level"] = "info"
            out.append(a)
        self.state["alerts_since"] = keep
        out.sort(key=lambda a: (-LEVELS[a["level"]], scope_rank.get(a["scope"], 9), -(a["since_ms"] or 0), a["id"]))
        return out

    def apply_levels(self, hosts, cards, alerts):
        worst_card, worst_host = {}, {}
        reasons = {}
        for a in alerts:
            if a["level"] == "info" and (a["known"] or a["ack"]):
                continue
            if a["card"]:
                worst_card[a["card"]] = max(worst_card.get(a["card"], 0), LEVELS[a["level"]])
                if a["level"] in ("warn", "bad"):
                    reasons.setdefault(a["card"], []).append(a["title"])
            if a["host"]:
                worst_host[a["host"]] = max(worst_host.get(a["host"], 0), LEVELS[a["level"]])
        inv = {v: k for k, v in LEVELS.items()}
        for cid, c in cards.items():
            if c.get("excluded"):
                c["level"] = "excluded"
            elif c.get("stale"):
                c["level"] = "unknown"
            else:
                lv = worst_card.get(cid, 0)
                c["level"] = "ok" if lv <= 1 else inv[lv]
            c["reasons"] = reasons.get(cid, [])[:4]
            if not c.get("excluded"):
                worst_host[c["host"]] = max(worst_host.get(c["host"], 0), worst_card.get(cid, 0))
        for h, hb in hosts.items():
            lv = worst_host.get(h, 0)
            hb["level"] = "ok" if lv <= 1 else inv[lv]
            if not hb["reachable"] and hb["level"] == "ok":
                hb["level"] = "warn"

    def status_view(self, alerts):
        counts = {"bad": 0, "warn": 0, "info": 0, "known": 0}
        for a in alerts:
            if a["known"] or a["ack"]:
                counts["known"] += 1
            else:
                counts[a["level"]] += 1
        live = [a for a in alerts if not (a["known"] or a["ack"])]
        level = "bad" if counts["bad"] else "warn" if counts["warn"] else "ok"

        def label(a):
            who = a["card"] and self.lab["cards"].get(a["card"], {}).get("label") or a["host"] or ""
            t = a["title"]
            return t if (not who or t.startswith(who)) else "%s %s" % (who, t)
        if level == "ok":
            head = "All clear" + (" (%d known condition%s)" % (counts["known"], "" if counts["known"] == 1 else "s")
                                  if counts["known"] else "")
        else:
            top = [a for a in live if a["level"] == level]
            n = len(top)
            word = ("problem" if level == "bad" else "warning") + ("" if n == 1 else "s")
            head = "%d %s: %s" % (n, word, ", ".join(label(a) for a in top[:3])) + (", …" if n > 3 else "")
            if level == "bad" and counts["warn"]:
                head += "; %d warning%s" % (counts["warn"], "" if counts["warn"] == 1 else "s")
        return {"level": level, "counts": counts, "headline": self.priv.scrub(head, 240)}

    # -------------------------------------------------------------- history (§1.7)
    def history_line(self, hosts, cards):
        line = {"t": int(self.now), "h": {}, "c": {}}
        for h, hb in hosts.items():
            if hb.get("error") == NOT_PROBED:
                continue
            # up: 1 answered, 2 waiting for a Tailscale check approval, 0 no answer
            line["h"][h] = {"up": 1 if hb["reachable"] else 2 if hb.get("error") == "approval needed" else 0,
                            "warn": sum(1 for a in self.alerts.values() if a["host"] == h and a["level"] in ("warn", "bad")
                                        and not a.get("known") and not a.get("ack"))}
        for cid, c in cards.items():
            if c.get("stale"):
                continue
            hold = None
            if c.get("holder") is not None:
                who = c["holder"].get("who") or []
                hold = ("system" if who[0].get("system") else who[0]["login"]) if who else ""
            act = c.get("activity") or {}
            tl = c.get("telemetry") or {}
            ce_new = (c.get("errors") or {}).get("ce_new") or {}
            e = {"hold": hold, "used": None if act.get("used") is None else int(bool(act.get("used"))),
                 "ce": sum(ce_new.values())}
            if tl.get("at_ms") and tl.get("source") in ("live", "experiment"):
                e["die"], e["w"], e["dt"], e["src"] = tl.get("die_c"), tl.get("board_w"), tl["at_ms"] // 1000, tl["source"]
            line["c"][cid] = e
        return line

    def history_view(self, current):
        end = int(self.now // SLOT_S) * SLOT_S
        t0 = end - (SLOTS - 1) * SLOT_S

        def idx(t):
            i = int((t - t0) // SLOT_S)
            return i if 0 <= i < SLOTS else None
        lines = []
        try:
            with open(os.path.join(self.out, "history.jsonl")) as f:
                for ln in f:
                    try:
                        lines.append(json.loads(ln))
                    except ValueError:
                        pass
        except OSError:
            pass
        lines.append(current)
        H = {}
        for h in self.lab["hosts"]:
            H[h] = {k: [None] * SLOTS for k in ("up", "warn", "load", "mem_avail_gib", "sessions_all",
                                                 "sessions_owner", "tmux", "claude", "beats")}
            for b in self.nodewatch_buckets.get(h) or []:
                i = idx(b["t"])
                if i is None:
                    continue
                H[h]["load"][i] = b["load"]
                H[h]["mem_avail_gib"][i] = b["mem"]
                H[h]["sessions_all"][i] = b["sa"]
                H[h]["sessions_owner"][i] = b["so"]
                H[h]["tmux"][i] = None if b["tmux"] is None else int(b["tmux"])
                H[h]["claude"][i] = None if b["claude"] is None else int(b["claude"])
                H[h]["beats"][i] = None if b["n"] is None else int(b["n"])
        C = {cid: {k: [None] * SLOTS for k in ("hold", "used", "die_c", "board_w", "ce_new")}
             for c in self.lab["hosts"].values() for cid in c["cards"]}
        for ln in lines:
            i = idx(ln.get("t", 0))
            if i is not None:
                for h, v in (ln.get("h") or {}).items():
                    if h in H:
                        u, prev = v.get("up"), H[h]["up"][i]
                        H[h]["up"][i] = u if prev is None or u == 1 or (u == 2 and prev == 0) else prev
                        H[h]["warn"][i] = v.get("warn")
            for cid, v in (ln.get("c") or {}).items():
                if cid not in C:
                    continue
                if i is not None:
                    if v.get("hold") is not None:
                        prev = C[cid]["hold"][i]
                        C[cid]["hold"][i] = v["hold"] if not prev else prev
                    if v.get("used") is not None:
                        C[cid]["used"][i] = max(C[cid]["used"][i] or 0, v["used"])
                    C[cid]["ce_new"][i] = (C[cid]["ce_new"][i] or 0) + (v.get("ce") or 0)
                if v.get("dt"):
                    j = idx(v["dt"])
                    if j is not None:
                        if v.get("die") is not None:
                            C[cid]["die_c"][j] = v["die"]
                        if v.get("w") is not None:
                            C[cid]["board_w"][j] = v["w"]
        for h in H:
            beats = H[h]["beats"]
            first = next((i for i, b in enumerate(beats) if b), None)
            gaps, run = [], None
            if first is not None:
                for i in range(first, SLOTS - 1):
                    if not beats[i]:
                        run = run if run is not None else i
                    elif run is not None:
                        gaps.append((run, i))
                        run = None
                if run is not None:
                    gaps.append((run, SLOTS - 1))
            H[h]["gaps"] = [{"from": iso(t0 + a * SLOT_S), "to": iso(t0 + b * SLOT_S), "min": (b - a) * 10}
                            for a, b in gaps][-20:]
        return {"t0_ms": t0 * 1000, "step_min": SLOT_S // 60, "n": SLOTS, "hosts": H, "cards": C}

    def append_history(self, line):
        p = os.path.join(self.out, "history.jsonl")
        keep_after = self.now - HISTORY_KEEP_S
        lines = []
        try:
            with open(p) as f:
                for ln in f:
                    try:
                        if json.loads(ln).get("t", 0) >= keep_after:
                            lines.append(ln.rstrip("\n"))
                    except ValueError:
                        pass
        except OSError:
            pass
        lines.append(json.dumps(line, separators=(",", ":")))
        write_atomic(p, "\n".join(lines) + "\n")

    # -------------------------------------------------------------- fingerprint (§1.7)
    # Alerts that come and go with ordinary use: their state is in the fingerprint another way, or not worth a version.
    FP_VOLATILE = re.compile(r"^card:[^:]+:used$|^owner:sessions$|^owner:phones$")

    def fingerprint(self, data):
        """A hash of the state worth a new version: what the page says, not how its numbers drift. Left out: load,
        memory, ages, message counters and the used flag, telemetry times, the count of working Claude sessions,
        the owner's own login sessions (every ssh of an agent is one), and error counts (their kinds stay)."""
        m = {"hosts": {}, "cards": {}, "people": [], "owner": {}, "alerts": []}
        for h, hb in data["hosts"].items():
            m["hosts"][h] = {"reachable": hb["reachable"], "error": hb.get("error"),
                             "warn": sorted(x["check"] for x in ((hb.get("health") or {}).get("lines") or [])
                                            if x["level"] == "WARN"),
                             "failed": (hb.get("systemd") or {}).get("failed"),
                             "reboot": (hb.get("kernel") or {}).get("reboot_pending"),
                             "tmux": (hb.get("nodewatch") or {}).get("tmux"),
                             "claude": bool((hb.get("nodewatch") or {}).get("claude")),
                             "running": sorted({r["kind"] + ":" + str(r.get("what")) for r in
                                                ((hb.get("experiments") or {}).get("running") or [])})}
        for cid, c in data["cards"].items():
            er = c.get("errors") or {}
            sm = c.get("sample") or {}
            m["cards"][cid] = {"present": c.get("present"), "link": (c.get("link") or {}).get("ok"),
                               "errors": {k: sorted((er.get(k) or {}).keys()) for k in ("ce", "uce")},
                               "holders": sorted(w["login"] for w in ((c.get("holder") or {}).get("who") or [])),
                               "sample": [bool(sm.get("disabled")), str(sm.get("result") or "").startswith("failed")]}
        for p in data["people"]:
            m["people"].append([p["login"], p["status"], [] if p["owner"] else
                                sorted((h, x.get("sessions"), x.get("closing")) for h, x in p["hosts"].items())])
        cl = data["owner"].get("claudes") or {}
        m["owner"] = {"accounts": [(a["n"], a["logged_in"], a.get("lapses")) for a in cl.get("accounts", [])],
                      "pins": [(p["id8"], p["running"]) for p in cl.get("pins", [])]}
        m["alerts"] = sorted((a["id"], a["level"]) for a in data["alerts"] if not self.FP_VOLATILE.match(a["id"]))
        m["halted"] = data["collector"].get("halted")
        return hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()[:12]

    # -------------------------------------------------------------- state and output
    def save_state(self):
        self.state["saved_ms"] = ms(self.now)
        write_atomic(os.path.join(self.out, "state.json"), json.dumps(self.state, indent=1))

    def print_summary(self, data):
        print("%s  %s" % (data["status"]["level"].upper(), data["status"]["headline"]))
        for h, hb in data["hosts"].items():
            if hb["reachable"]:
                print("  %-11s ok      %5d ms  level %s" % (h, hb.get("took_ms") or 0, hb.get("level")))
            else:
                print("  %-11s %-7s %5s     %s (last data %s)" % (h, "STALE", "", hb.get("error"),
                                                               (hb.get("last_ok_at") or "never")[:16]))
        for a in data["alerts"]:
            if a["level"] in ("bad", "warn"):
                who = a["card"] or a["host"] or a["scope"]
                print("  [%s] %s" % (a["level"], a["title"] if a["title"].startswith(who) else "%s: %s" % (who, a["title"])))
        for cid, r in (getattr(self, "sample_results", {}) or {}).items():
            print("  sample %s: %s" % (cid, r["result"]))
            for g in r["gates"]:
                print("    gate %-10s %s %s" % (g["gate"], "ok" if g["ok"] else "FAIL", g["detail"]))
            if r.get("would_run"):
                print("    would run: %s" % r["would_run"])
        if data["collector"]["errors"]:
            print("  collector errors: %s" % "; ".join(data["collector"]["errors"]))
        print("  fingerprint %s, took %.1f s" % (data["fingerprint"], data["collector"]["took_s"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=CACHE)
    ap.add_argument("--hosts")
    ap.add_argument("--card-sample", action="store_true")
    ap.add_argument("--sample-dry", action="store_true")
    ap.add_argument("--from-raw")
    ap.add_argument("--no-sessions", action="store_true")
    ap.add_argument("--no-backoff", action="store_true")
    ap.add_argument("--health", action="store_true", help="run et-lab-health on every host this run (else hourly)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--now", type=float, help="with --from-raw: the collector's clock (epoch seconds), for tests")
    ap.add_argument("--owner", help="the owner's login (tests; else config.json's owner, else $USER)")
    args = ap.parse_args()
    os.umask(0o077)
    if not os.path.isdir(args.out):
        os.makedirs(args.out, mode=0o700)
    elif os.path.realpath(args.out) == os.path.realpath(CACHE):
        try:
            os.chmod(args.out, 0o700)  # the default directory only: another --out keeps its mode
        except OSError:
            pass
    # One collector at a time per output directory (a hand run racing cron would lose state.json updates). Its
    # own file: update.sh holds "lock" around the whole run and never passes that descriptor on.
    lockf = open(os.path.join(args.out, "collect.lock"), "a")
    deadline = time.time() + 60
    while True:
        try:
            fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError:
            if time.time() > deadline:
                print("collect.py: another collector holds %s/collect.lock" % args.out, file=sys.stderr)
                return 4
            time.sleep(1)
    col = Collector(args)
    rc = col.run()
    return rc


if __name__ == "__main__":
    sys.exit(main())
