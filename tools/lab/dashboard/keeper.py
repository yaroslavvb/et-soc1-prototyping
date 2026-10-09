#!/usr/bin/env python3
"""keeper.py: the box-side keeper of the lab dashboard's collector (README.md "The keeper", DESIGN.md §3).

It runs on the lab machines and needs no Mac: once a minute it reports the collector's health to the spacesheep
stream aifoundry-dash/<host> (one JSON line, the same shape the agents feed uses) and repairs what is safe to
repair. Written 8 October 2026, after the page froze from Wednesday 17:50 to Thursday 15:32: the collector, its
cron line and its deploy all live on one machine, and nothing noticed that it had stopped.

  keeper.py status [--json]   a read-only snapshot (apart from its page cache): cron, the last run, the last
                              deploy, the published page's age, HALT/EXPOSED, warnings and the fix for each
  keeper.py tick [--json]     the snapshot, then the safe repairs, then the snapshot as one JSON line: what
                              `spacesheep stream aifoundry-dash/<host> --every 60s -- keeper.py tick --json` pushes
  keeper.py repair [--force]  the safe repairs with their rate limits ignored, then `update.sh now` in the
                              foreground if the page is still stale; prints a human summary; 0 if the page is
                              fresh afterwards, 1 if not. This is what a person, or a watchdog elsewhere, runs over ssh
  keeper.py install [--dry-run] / uninstall    the systemd --user unit that keeps the stream alive

What it never does: deploy by itself (only by running update.sh, whose own rules decide whether to deploy),
clear HALT or EXPOSED (a person's step: update.sh resume), touch a /dev/et* node or a card tool, or kill
anything. It starts `update.sh run` detached and never waits for it, and a tick works to one deadline
(TICK_BUDGET_S), skipping what it has no time left for, so it fits in the minute the stream gives it.

Everything in the JSON reaches a public stream, so every piece of free text goes through scrub(): no login
names, paths, addresses, e-mail addresses, URLs or tailnet names. tests/test_keeper.py pins that collect.py's
own privacy check accepts what the keeper writes.

Files, all beside the collector's own (~/.cache/lab-dashboard, mode 0700): keeper.log (the repairs, rotated at
256 KB), keeper-state.json (the rate limits and the last repair), keeper-page.json (the cached signed-out read of
the page), keeper-stream.log (the unit's output). Nothing is written inside the checkout.

Test hooks, the same ones update.sh reads, so a test needs no box: LAB_DASH_CACHE, LAB_DASH_CONFIG (other
directories), LAB_DASH_UPDATE (the update.sh to call), LAB_DASH_CRONTAB (the crontab command), LAB_DASH_FETCH (a
command that prints the HTTP status, then the body, of an anonymous GET of its URL argument), LAB_DASH_HOST (this
machine's short name), LAB_DASH_STANDBY_AFTER_MIN (the standby's takeover age, which wins over config.json).
Python 3 standard library only (3.12 on the boxes).
"""
import argparse
import datetime as dt
import json
import os
import re
import shlex
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

SCHEMA = 1
UNIT = "lab-dashboard-keeper.service"
STREAM_PREFIX = "aifoundry-dash"
TAG = "# lab-dashboard"          # update.sh's crontab tag; the keeper only looks for it

PAGE_REFRESH_S = 600             # the signed-out read of the page, at most every 10 minutes
PAGE_TIMEOUT_S = 10
PAGE_MAX_BYTES = 400000
RUN_OVERDUE_MIN = 25             # cron runs update.sh every 10 minutes (update.sh's CRON_LINE: 2-59/10)
PAGE_STALE_MIN = 90              # the page itself reads STALE at 80 (collect.py RULES); 90 leaves a heartbeat of slack
PAGE_FRESH_MIN = 80              # `repair` succeeds only below this
STANDBY_MIN_FLOOR = 90           # update.sh's floor for standby_after_min (its main(), 8 Oct 2026), mirrored here
HL_MAX = 120                     # the headline ("hl"), kept short so it survives the stream list's cut
INSTALL_CRON_EVERY_S = 3600      # R1 at most once an hour
START_RUN_EVERY_S = 1200         # R2 and R3 share one 20-minute limit: both start the same `update.sh run`
INSTALL_CRON_TIMEOUT_S = 15      # a crontab edit takes a moment; this only bounds a stuck one
CRONTAB_TIMEOUT_S = 5
VERSION_TIMEOUT_S = 5
NOW_TIMEOUT_S = 300              # `repair`'s foreground `update.sh now` (a run can take ~8 minutes at worst, but
                                 # whoever runs `repair` waits on it, so it is cut at five)
NOW_EVERY_S = 600                # `repair`'s `now` deploys every time (update.sh applies the fingerprint and the
                                 # 10-minute gap only to a cron run, update.sh:490 and :493), and the account's
                                 # deploys are capped per day, so two `repair`s in a row need --force
# One tick's whole deadline. The stream asks for a line every 60 s, and the sum of the per-leg caps is more than
# that, so each leg gets what is left of this and a leg with nothing left is skipped and said so (8 October 2026: a
# tick with a wedged fetch and a wedged crontab measured 60.1 s, and the stream lost that minute's line).
TICK_BUDGET_S = 25
LEG_MIN_S = 3                    # too little left to be worth starting a leg: it would only fail and be cached
LOG_MAX = 256 * 1024
LOG_TAIL_BYTES = 200000          # enough of update.log for runs_since_deploy after a long gap
VERDICT_MAX = 140
# The verdict only the update.sh of before 8 October 2026 writes: its guard read `spacesheep list`, which returns
# the 50 most recently updated spaces, and treated a space that is not among them as a reason not to deploy.
DEADLOCK = "skipped(visibility unverified: list missing)"

# ---------------------------------------------------------------------------------------------- privacy
# The union of collect.py's §6 patterns and page/render.py's final check, because the two differ in both
# directions: render.py's address and IPv4 patterns are the looser ones (a program named 01.1.1.1 passed the
# collector on 30 September 2026 and stopped every render for a day), and collect.py's URL, IPv6, MAC and
# tailnet patterns are the wider ones. Substituting with both costs nothing and leaves nothing for either to
# refuse. tests/test_keeper.py pins it against collect.py.
PRIV_PATTERNS = [
    ("url", re.compile(r"\b(?:https?|ftp|ssh|wss?)://[^\s\"'<>]+", re.I)),
    ("url", re.compile(r"\b(?:https?|ftp|ssh|wss?)://", re.I)),   # a scheme with nothing after it: render.py refuses it
    ("tailscale-login", re.compile(r"login\.tailscale\.com", re.I)),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?!(?:service|socket|timer|mount|"
                         r"scope|slice|target|path|device|swap|automount)\b)[A-Za-z]{2,}")),
    ("tailnet-name", re.compile(r"\b[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.ts\.net\b", re.I)),
    ("ipv4", re.compile(r"(?<![\w.])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\w.])")),
    ("ipv6", re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}(?![\w:])"
                        r"|(?<![\w:])(?:[0-9A-Fa-f]{1,4}:)+:(?:[0-9A-Fa-f]{1,4}(?::[0-9A-Fa-f]{1,4})*)?(?![\w:])"
                        r"|(?<![\w:])::(?:[0-9A-Fa-f]{1,4}:)*[0-9A-Fa-f]{1,4}(?![\w:])")),
    ("mac", re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}(?![\w:])")),
]
# Every absolute path, not only other people's home trees: the keeper's own paths name the login too, and the
# lookbehind keeps hosts=3/3 and alerts=bad0/warn0/info0 intact.
PATH_RE = re.compile(r"(?<![\w/~.])~?/[A-Za-z0-9_.+-]+(?:/[A-Za-z0-9_.+-]*)*")
LOGIN_RE = re.compile(r"^[A-Za-z0-9._-]{3,32}$")


def scrub(s, limit=None, owner=None):
    """Free text made fit for a public stream: the patterns above, then every path, then the collector's own
    login, then the control characters (update.sh's `tr -cd '[:print:]'`), then the length."""
    if s is None:
        return None
    s = str(s)
    for name, rx in PRIV_PATTERNS:
        s = rx.sub("<%s>" % name, s)
    s = PATH_RE.sub("<path>", s)
    if owner and LOGIN_RE.match(owner):
        s = re.sub(r"\b%s\b" % re.escape(owner), "<user>", s)
    s = "".join(ch for ch in s if ch >= " " or ch == "\t").strip()
    if limit and len(s) > limit:
        s = s[: limit - 1] + "…"
    return s


# ---------------------------------------------------------------------------------------------- small helpers
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
# update.sh:537, the one line per run: '<stamp> run|now took=<s>s hosts=<r>/<n> alerts=bad<n>/warn<n>/info<n>
# fp=<fp> vis=<word> deploy=<verdict>', the stamp from log_line's `date '+%Y-%m-%dT%H:%M:%S%z'`. The log's other
# lines (a lock skip, a privacy refusal, a standby's line, the guard's reads) have no took=, so they are not runs.
# took=, hosts= and alerts= are allowed to be empty, because the keeper reads none of them and they come from `dj`,
# a python expression over data.json that prints nothing if it throws: one empty field must not hide the run.
RUN_RE = re.compile(r"^(?P<stamp>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d{4}) (?P<mode>run|now) took=\S* hosts=\S* "
                    r"alerts=\S* fp=(?P<fp>\S*) vis=(?P<vis>\S*) deploy=(?P<deploy>.*)$")
GEN_MS_RE = re.compile(r'"generated_ms"\s*:\s*(\d{10,16})')
COLLECTOR_RE = re.compile(r'"collector"\s*:\s*\{')
# collect.py writes the collector's short name (socket.gethostname().split(".")[0], collect.py:955); a short label
# is all the keeper accepts, so a page that ever carried an FQDN or an address could not relay it to the stream.
PAGE_HOST_RE = re.compile(r'"host"\s*:\s*"([A-Za-z0-9][A-Za-z0-9-]{0,31})"')


def now_ms(t=None):
    return int(round((time.time() if t is None else t) * 1000))


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_atomic(path, text, mode=0o600):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, 0o700, exist_ok=True)
    tmp = "%s.new.%d" % (path, os.getpid())    # per process: two keepers at once must not unlink each other's
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)          # a rename, so a reader never sees half a file


def stamp_ms(s):
    try:
        return now_ms(dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z").timestamp())
    except ValueError:
        return None


def local(ms_val, fmt="%F %T"):
    if not ms_val:
        return "-"
    return time.strftime(fmt, time.localtime(ms_val / 1000.0))


def age_min(ms_val, now):
    if not ms_val:
        return None
    return round((now - ms_val / 1000.0) / 60.0, 1)


def read_bounded(resp, cap):
    """The body under a deadline. urlopen's timeout bounds each recv, not the whole read, so a trickling origin can
    hold one resp.read() open far longer than it (36 s against a 20 s timeout, measured 8 October 2026). Chunks
    bound it instead: the worst case is one recv past the deadline, not an open-ended wait."""
    end = time.monotonic() + cap
    parts, got = [], 0
    while got < PAGE_MAX_BYTES and time.monotonic() < end:
        chunk = resp.read(min(65536, PAGE_MAX_BYTES - got))
        if not chunk:
            break
        parts.append(chunk)
        got += len(chunk)
    return b"".join(parts).decode("utf-8", "replace")


def tail_text(path, nbytes):
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            if size > nbytes:
                f.seek(size - nbytes)
                f.readline()       # drop the partial first line
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


class Keeper:
    def __init__(self, env=None, now=None):
        self.env = dict(os.environ if env is None else env)
        self.now = time.time() if now is None else now
        self.home = self.env.get("HOME") or os.path.expanduser("~")
        self.cache = self.env.get("LAB_DASH_CACHE") or os.path.join(self.home, ".cache", "lab-dashboard")
        self.conf = self.env.get("LAB_DASH_CONFIG") or os.path.join(self.home, ".config", "lab-dashboard")
        self.update = self.env.get("LAB_DASH_UPDATE") or os.path.join(HERE, "update.sh")
        self.crontab = shlex.split(self.env.get("LAB_DASH_CRONTAB") or "crontab")
        self.fetch = shlex.split(self.env.get("LAB_DASH_FETCH") or "")
        self.host = self.env.get("LAB_DASH_HOST") or socket.gethostname().split(".")[0]
        self.config = load_json(os.path.join(self.conf, "config.json"), {})
        if not isinstance(self.config, dict):
            self.config = {}
        self.owner = (self.config.get("owner") if isinstance(self.config.get("owner"), str) else None) \
            or self.env.get("USER") or self.env.get("LOGNAME") or ""
        self.state = load_json(os.path.join(self.cache, "keeper-state.json"), {})
        if not isinstance(self.state, dict):
            self.state = {}
        self._runs = None
        self._started = []       # the detached update.sh runs: kept only so nothing waits on them by accident
        self._late = []          # the legs a tick had no time left for
        self.standby_bad = None  # a standby_after_min setting update.sh refuses
        self.deadline = None     # monotonic: `tick` sets one, a person's `status` and `repair` have none

    # ------------------------------------------------------------------ paths and settings
    def p(self, *parts):
        return os.path.join(self.cache, *parts)

    def budget(self, cap):
        """How long a leg may take: its own cap, or whatever is left of the tick's deadline. 0 means the time is
        gone (under LEG_MIN_S), and the caller skips that leg — late() puts it in the warnings — rather than
        overrunning the minute or starting a read that can only time out and then be cached."""
        if self.deadline is None:
            return cap
        left = min(cap, self.deadline - time.monotonic())
        return left if left >= LEG_MIN_S else 0.0

    def late(self, leg):
        if leg not in self._late:
            self._late.append(leg)

    def space_uuid(self):
        """The uuid, read exactly as update.sh's space_uuid reads it. It is never put in the JSON: the page's
        address is the space's secret in the private mode, and a URL has no place on a public stream."""
        try:
            with open(os.path.join(self.conf, "space")) as f:
                u = "".join(f.read().split())
        except OSError:
            return None
        return u if UUID_RE.match(u) else None

    def standby_after_min(self):
        """On update.sh's own rule (its main()): a whole number of minutes, 90 or more, or nothing at all. A
        setting update.sh refuses is not a standby setting — it refuses every run with exit 2 and writes no run
        line — so the keeper treats such a box as not set up (role none) and says which value is wrong."""
        v = self.env.get("LAB_DASH_STANDBY_AFTER_MIN")          # as with LAB_DASH_VISIBILITY, the environment wins
        if v is None or (isinstance(v, str) and not v.strip()):  # empty is unset, the way update.sh reads it
            v = self.config.get("standby_after_min")
        if v is None or isinstance(v, bool) or (isinstance(v, str) and not v.strip()):
            return None
        s = str(int(v)) if isinstance(v, int) else str(v).strip()
        if re.match(r"^[0-9]{1,6}$", s) and int(s) >= STANDBY_MIN_FLOOR:
            return float(s)
        self.standby_bad = s[:20]
        return None

    def role(self):
        """standby: this box takes over when the page has been stale for standby_after_min. primary: it is the
        collector. none: the dashboard is not set up here, so the keeper reports and repairs nothing."""
        if self.standby_after_min() is not None:
            return "standby"
        if self.standby_bad:
            return "none"          # update.sh refuses every run here, so there is nothing to watch or restart
        return "primary" if self.space_uuid() else "none"

    def version(self):
        sha = ""
        t = self.budget(VERSION_TIMEOUT_S)
        try:
            if t:
                r = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                                   capture_output=True, text=True, timeout=t)
                sha = r.stdout.strip() if r.returncode == 0 else ""
        except (OSError, subprocess.SubprocessError):
            sha = ""
        # aifoundry1 and aifoundry3 hold an rsynced tree with no git, so "nogit" is the normal answer there
        return sha if re.match(r"^[0-9a-f]{6,40}$", sha) else "nogit"

    # ------------------------------------------------------------------ reading what the collector left
    def cron_installed(self):
        t = self.budget(CRONTAB_TIMEOUT_S)
        if not t:
            self.late("the crontab")
            return None
        try:
            r = subprocess.run(self.crontab + ["-l"], capture_output=True, text=True, timeout=t)
        except (OSError, subprocess.SubprocessError):
            return None            # the crontab command itself did not answer: not the same as "not installed"
        if r.returncode != 0 and "no crontab for" not in (r.stderr or ""):
            return None
        return TAG in (r.stdout or "")

    def read_runs(self):
        """(last run, last cron run, runs since the newest deploy=ok, the newest verdicts) from update.log. Read
        once per invocation: a tick parses the log, then the repairs ask about the same lines."""
        if self._runs is not None:
            return self._runs
        runs = []
        for line in tail_text(self.p("update.log"), LOG_TAIL_BYTES).splitlines():
            m = RUN_RE.match(line)
            if m:
                runs.append({"at_ms": stamp_ms(m.group("stamp")), "mode": m.group("mode"),
                             "deploy": m.group("deploy"), "vis": m.group("vis")})
        last = runs[-1] if runs else None
        last_cron = next((r for r in reversed(runs) if r["mode"] == "run"), None)
        since = 0
        for r in reversed(runs):
            if r["deploy"].startswith("ok"):
                break
            since += 1
        self._runs = (last, last_cron, since, [r["deploy"] for r in runs[-3:]])
        return self._runs

    def read_deploy_state(self):
        """deploy.state is '<epoch> <fingerprint>' (update.sh:500)."""
        try:
            with open(self.p("deploy.state")) as f:
                parts = f.read().split()
        except OSError:
            return None
        if not parts:
            return None
        try:
            at = float(parts[0])
        except ValueError:
            return None
        return {"at_ms": now_ms(at), "fp": scrub(parts[1], 24, self.owner) if len(parts) > 1 else None}

    # ------------------------------------------------------------------ the published page
    def fetch_page(self, uuid, timeout):
        """One signed-out read of the content origin, on update.sh's anon_fetch contract (the status on line 1,
        then the body). Returns (generated_ms, collector host, error)."""
        url = "https://%s.spacesheep.app/" % uuid
        if self.fetch:
            try:
                r = subprocess.run(self.fetch + [url], capture_output=True, text=True, timeout=timeout + 5,
                                   env=self.env)
            except (OSError, subprocess.SubprocessError):
                return None, None, "fetch failed"
            if r.returncode != 0:
                return None, None, "fetch exit %d" % r.returncode
            status, _, body = (r.stdout or "").partition("\n")
            status = status.strip()
        else:
            import urllib.error
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent":
                  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status, body = str(resp.status), read_bounded(resp, timeout)
            except urllib.error.HTTPError as e:
                return None, None, "HTTP %s" % e.code
            except Exception as e:                      # a name that cannot resolve, a timeout, a reset
                return None, None, type(e).__name__
        if status != "200":
            return None, None, "HTTP %s" % (status or "none")
        m = GEN_MS_RE.search(body)
        gen = int(m.group(1)) if m else None
        host = None
        c = COLLECTOR_RE.search(body)
        if c:
            hm = PAGE_HOST_RE.search(body, c.end(), c.end() + 400)
            host = hm.group(1) if hm else None
        return gen, host, None if gen else "no generated_ms in the page"

    def page(self, force=False):
        """The page's age, with the read cached in keeper-page.json: once every ten minutes is enough for a
        90-minute rule, and a tick a minute must not hammer the origin."""
        uuid = self.space_uuid()
        if not uuid:
            return {"age_min": None, "host": None, "checked_ms": None, "err": "no space configured"}
        cached = load_json(self.p("keeper-page.json"), {})
        if not isinstance(cached, dict):
            cached = {}
        checked = cached.get("checked_ms")
        if not force and checked and 0 <= self.now - checked / 1000.0 < PAGE_REFRESH_S:
            out = dict(cached)
        else:
            t = self.budget(PAGE_TIMEOUT_S)
            if not t:
                # the tick's deadline is gone: the line matters more than the read, and R3 waits a minute
                self.late("the published page")
                out = dict(cached) if cached else {"err": "not read: the tick ran out of time"}
            else:
                gen, host, err = self.fetch_page(uuid, t)
                out = {"generated_ms": gen, "host": host, "err": err, "checked_ms": now_ms(self.now)}
                write_atomic(self.p("keeper-page.json"), json.dumps(out))
        # the host comes off a page read over the public internet, and it goes straight onto a public stream
        return {"age_min": age_min(out.get("generated_ms"), self.now), "host": scrub(out.get("host"), 64, self.owner),
                "checked_ms": out.get("checked_ms"), "err": scrub(out.get("err"), 80, self.owner)}

    # ------------------------------------------------------------------ the snapshot
    def status(self, force_page=False):
        role = self.role()
        last, last_cron, since, recent = self.read_runs()
        page = self.page(force=force_page)
        cron = self.cron_installed()
        halt, exposed = os.path.exists(self.p("HALT")), os.path.exists(self.p("EXPOSED"))
        rep = self.state.get("repair") if isinstance(self.state.get("repair"), dict) else None
        snap = {
            "schema": SCHEMA, "host": scrub(self.host, 64, None),
            # One line a person or a watchdog can read even where the stream list cuts the value short (`spacesheep
            # streams` shows about the first 250 characters), so it sits near the front; filled in last.
            "hl": "",
            "t": now_ms(self.now), "keeper": self.version(), "role": role,
            "cron": {"installed": cron},
            "last_run": None if not last else {
                "at_ms": last["at_ms"], "mode": last["mode"],
                "deploy": scrub(last["deploy"], VERDICT_MAX, self.owner),
                "vis": scrub(last["vis"], 40, self.owner)},
            "runs_since_deploy": since,
            "last_deploy": self.read_deploy_state(),
            "page": page,
            "halt": halt, "exposed": exposed,
            "repair": None if not rep else {"at_ms": rep.get("at_ms"), "what": scrub(rep.get("what"), 120, self.owner)},
            "warn": [], "fix": [],
        }
        # What a reader (and whatever watches the stream) should know, newest trouble first. It says nothing
        # about a box where the dashboard is not set up — except that its standby setting is one update.sh refuses,
        # which is exactly why the box reads as not set up.
        if self.standby_bad:
            self.say(snap, "standby_after_min '%s' is not a whole number of minutes, %d or more, so update.sh "
                           "refuses every run" % (scrub(self.standby_bad, 20, self.owner), STANDBY_MIN_FLOOR),
                     "set standby_after_min to %d or more, or remove it" % STANDBY_MIN_FLOOR)
        if role == "none":
            snap["hl"] = self.headline(snap, role, page, None)
            return snap
        if cron is False:
            self.say(snap, "the lab-dashboard cron line is missing from this box's crontab",
                     "update.sh --install-cron (the keeper runs it once an hour)")
        elif cron is None:
            self.say(snap, "the crontab could not be read", "check the crontab command on this box")
        cron_age = age_min(last_cron["at_ms"] if last_cron else None, self.now)
        # Only the box that should be publishing is judged on its runs: update.sh's standby gate returns before it
        # writes the run line (update.sh:420 and :537), so a box standing by correctly has no run line at all.
        if self.active_collector(role, page):
            if cron_age is None:
                self.say(snap, "update.log holds no cron run",
                         "the keeper starts update.sh run; then update.sh status")
            elif cron_age > RUN_OVERDUE_MIN:
                self.say(snap, "no cron run for %d min (it runs every 10)" % cron_age,
                         "the keeper starts update.sh run; then check cron on this box")
        if page["age_min"] is None:
            self.say(snap, "the published page could not be read (%s)" % (page["err"] or "no answer"),
                     "check the network from this box, then update.sh status")
        elif page["age_min"] > PAGE_STALE_MIN:
            self.say(snap, "the published page is %d min old (it reads STALE at %d)"
                     % (page["age_min"], PAGE_FRESH_MIN),
                     "the keeper starts update.sh run; a person runs keeper.py repair if it stays stale"
                     if self.active_collector(role, page) else
                     "the collector on %s has stopped; a standby or that box takes over" % (page["host"] or "the other box"))
        if len(recent) >= 3 and all(v.startswith("FAILED") for v in recent[-3:]):
            self.say(snap, "the last 3 runs failed to deploy: %s" % scrub(recent[-1], 80, self.owner),
                     "update.sh status on this box")
        if last and last["deploy"] == DEADLOCK:
            # The deadlock of 8 October 2026: `spacesheep list` returns only the 50 most recently updated spaces,
            # and a space that has not been deployed to lately is not among them, so the guard skipped the deploy,
            # which kept it out of the list. Only a newer update.sh breaks the loop, so this is a checkout that
            # needs pulling — matched exactly, because the update.sh that fixed it writes a longer verdict for
            # the same list answer and that one is not the deadlock.
            self.say(snap, "the deploy is skipped because the space is not in `spacesheep list` (the top-50 deadlock)",
                     "update the checkout (git pull --ff-only)")
        if halt:
            self.say(snap, "HALT: deploys are stopped", "a person checks the space and runs update.sh resume")
        if exposed:
            self.say(snap, "EXPOSED: the space could not be set private",
                     "a person checks the space and runs update.sh resume")
        if self._late:
            self.say(snap, "this tick ran out of its %d s: %s not checked" % (TICK_BUDGET_S, ", ".join(self._late)),
                     "if it keeps happening, check this box's load and its route to the page")
        snap["hl"] = self.headline(snap, role, page, cron_age)
        return snap

    def headline(self, snap, role, page, cron_age):
        """snap["hl"]: the snapshot in one public-safe line of at most HL_MAX characters, the first warning when
        there is one ("WARN 2: the lab-dashboard cron line is missing …"), else what is well ("ok primary: ran 3 min
        ago, page 42 min old" or "ok standby: aifoundry2's page is 12 min old"). Built only from fields that are
        already scrubbed."""
        def mins(v):
            return "?" if v is None else "%d min" % v
        if snap["warn"]:
            line = "WARN %d: %s" % (len(snap["warn"]), snap["warn"][0])
        elif role == "none":
            line = "none: no dashboard collector is set up on this box"
        elif role == "standby" and not self.active_collector(role, page):
            line = "ok standby: %s's page is %s old" % (page.get("host") or "the primary", mins(page.get("age_min")))
        else:
            line = "ok %s: ran %s ago, page %s old" % (role, mins(cron_age), mins(page.get("age_min")))
        return scrub(line, HL_MAX, self.owner)

    @staticmethod
    def say(snap, warn, fix):
        snap["warn"].append(warn)
        if fix not in snap["fix"]:
            snap["fix"].append(fix)

    def active_collector(self, role, page):
        """Whose job it is to refresh the page now: the primary always, a standby once the page names it or has
        been stale longer than standby_after_min (so two boxes do not both deploy, DESIGN.md §3.2)."""
        if role == "primary":
            return True
        if role != "standby":
            return False
        if page.get("host") == self.host:
            return True
        after = self.standby_after_min()
        return page["age_min"] is not None and after is not None and page["age_min"] > after

    # ------------------------------------------------------------------ the repairs
    def log(self, line):
        path = self.p("keeper.log")
        try:
            if os.path.getsize(path) > LOG_MAX:
                os.replace(path, path + ".1")
        except OSError:
            pass
        os.makedirs(self.cache, 0o700, exist_ok=True)
        with open(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600), "w") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(self.now)), line))

    def save_state(self):
        write_atomic(self.p("keeper-state.json"), json.dumps(self.state, indent=1))

    def allowed(self, key, every_s, ignore_limits):
        if ignore_limits:
            return True
        last = self.state.get(key)
        return not isinstance(last, (int, float)) or self.now - last / 1000.0 >= every_s

    def did(self, key, what):
        self.state[key] = now_ms(self.now)
        self.state["repair"] = {"at_ms": now_ms(self.now), "what": scrub(what, 120, self.owner)}
        self.save_state()
        self.log(what)

    def start_update_run(self):
        """`update.sh run` detached: a new session, nothing inherited, never waited for. update.sh takes its own
        lock non-blockingly and returns at once if a run is in flight, so this is safe at any frequency; and
        Python closes every descriptor above 2 for the child, so none of ours can hold its lock. Returns None, or
        the error's name when update.sh could not be started at all (a moved or non-executable checkout): a tick
        reports that instead of dying on it, because a tick that dies pushes no line."""
        try:
            self._started.append(
                subprocess.Popen([self.update, "run"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True,
                                 cwd=self.home, env=self.env))
        except (OSError, ValueError) as e:
            return type(e).__name__
        return None

    def repairs(self, snap, ignore_limits=False, start_runs=True):
        """The safe repairs, in the order they matter. Only a box that is primary or standby repairs anything,
        and nothing here deploys: update.sh decides that. start_runs=False leaves R2 and R3 alone, for `repair`,
        whose own foreground `update.sh now` supersedes them (and would otherwise lose update.sh's lock to them)."""
        done = []
        if snap["role"] == "none":
            return done
        if snap["halt"] or snap["exposed"]:
            # R4: a person's step. Nothing is restarted while deploys are deliberately stopped.
            return done
        # R1: the cron line is gone (a reinstall, a hand-edited crontab, a new box)
        if snap["cron"]["installed"] is False and self.allowed("install_cron_ms", INSTALL_CRON_EVERY_S, ignore_limits):
            t = self.budget(INSTALL_CRON_TIMEOUT_S)
            if t:                              # out of time: the warning stands and the next tick runs it
                rc = self.run_update(["--install-cron"], t)[0]
                what = "ran update.sh --install-cron (the cron line was missing), exit %s" % rc
                self.did("install_cron_ms", what)
                done.append(what)
            else:
                self.late("the cron line")
        cron_age = None
        last_cron = self.read_runs()[1]
        if last_cron:
            cron_age = age_min(last_cron["at_ms"], self.now)
        mine = self.active_collector(snap["role"], snap["page"])
        # a standby writes no run line while it stands by (status() has the reason), so a missing run means
        # nothing until this box is the one that should be publishing
        overdue = mine and (cron_age is None or cron_age > RUN_OVERDUE_MIN)
        stale = snap["page"]["age_min"] is not None and snap["page"]["age_min"] > PAGE_STALE_MIN and mine
        # R2 and R3 start the same thing, so they share one limit: a stale page and a missing run are usually
        # the same fault seen twice.
        if start_runs and (overdue or stale) and self.allowed("update_run_ms", START_RUN_EVERY_S, ignore_limits):
            why = ("no cron run for %s min" % ("?" if cron_age is None else int(cron_age))) if overdue \
                else ("the page is %d min old" % snap["page"]["age_min"])
            err = self.start_update_run()
            what = "started update.sh run detached (%s)" % why if not err else \
                   "update.sh could not be started (%s): %s" % (why, err)
            self.did("update_run_ms", what)
            done.append(what)
            if err:
                self.say(snap, "update.sh could not be started on this box (%s)" % err,
                         "check that update.sh is in place and executable in this checkout")
        if stale:
            verdict = (snap["last_run"] or {}).get("deploy") or ""
            if verdict.startswith("skipped") or verdict.startswith("FAILED"):
                self.say(snap, "the page is stale and the newest run says deploy=%s" % verdict,
                         "update.sh status on this box")
        if done:
            snap["repair"] = {"at_ms": now_ms(self.now), "what": scrub(done[-1], 120, self.owner)}
        return done

    def run_update(self, args, timeout):
        """update.sh in the foreground, for the quick subcommands and for `repair`'s `now`. Returns
        (exit status or 'timeout', the output's tail)."""
        try:
            r = subprocess.run([self.update] + args, capture_output=True, text=True, timeout=timeout,
                               cwd=self.home, env=self.env)
        except subprocess.TimeoutExpired:
            return "timeout", "update.sh %s did not finish in %d s" % (" ".join(args), timeout)
        except OSError as e:
            return "error", type(e).__name__
        out = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
        return r.returncode, "\n".join(out[-8:])


# ---------------------------------------------------------------------------------------------- the systemd unit
def unit_dir(k):
    return os.path.join(k.home, ".config", "systemd", "user")


def find_node(k):
    """node and spacesheep.js as the boxes' other stream units name them: node is not on aifoundry1's or
    aifoundry3's login PATH, so the unit must spell it. The live monitor's unit is the one to copy."""
    path = os.path.join(unit_dir(k), "spacesheep-stream-aifoundry-%s.service" % k.host)
    try:
        with open(path) as f:
            m = re.search(r"^ExecStart=(.*)$", f.read(), re.M)
    except OSError:
        m = None
    if m:
        words = re.findall(r'"([^"]*)"', m.group(1)) or shlex.split(m.group(1))
        if len(words) >= 2 and os.path.exists(words[0]) and os.path.exists(words[1]):
            return words[0], words[1]
    node = os.path.join(k.home, ".local", "node", "bin", "node")
    js = os.path.join(k.home, ".local", "ss-stream", "node_modules", "spacesheep", "bin", "spacesheep.js")
    return node, js


def unit_text(k, node, js):
    me = os.path.abspath(__file__)
    argv = [node, js, "stream", "%s/%s" % (STREAM_PREFIX, k.host), "--every", "60s", "--",
            "/usr/bin/python3", me, "tick", "--json"]
    log = k.p("keeper-stream.log")
    return """[Unit]
Description=lab dashboard keeper (%s)
After=network-online.target
# never give up restarting (a slow network at boot), as robust.conf does for the live stream
StartLimitIntervalSec=0

[Service]
ExecStart=%s
Restart=always
RestartSec=5
Environment="PATH=%s"
Environment="HOME=%s"
StandardOutput=append:%s
StandardError=append:%s

[Install]
WantedBy=default.target
""" % (k.host, " ".join('"%s"' % a for a in argv),
       ":".join([os.path.dirname(node), os.path.join(k.home, ".local", "bin"), "/usr/local/bin", "/usr/bin", "/bin"]),
       k.home, log, log)


def cmd_install(k, dry):
    node, js = find_node(k)
    key = os.path.join(k.home, ".config", "spacesheep", "config.json")
    missing = [p for p in (node, js) if not os.path.exists(p)]
    if missing:
        print("keeper.py: not installed: %s is missing. Install the spacesheep CLI the way the live stream unit "
              "does (aifoundry-setup RESTORE.md), then run this again." % missing[0], file=sys.stderr)
        return 1
    if not os.path.exists(key):
        print("keeper.py: not installed: %s is missing, so the stream has no key. `spacesheep login` is a person's "
              "step." % key, file=sys.stderr)
        return 1
    text = unit_text(k, node, js)
    path = os.path.join(unit_dir(k), UNIT)
    cmds = [["systemctl", "--user", "daemon-reload"],
            ["systemctl", "--user", "enable", "--now", UNIT],
            ["loginctl", "show-user", k.env.get("USER") or k.owner or "self", "-p", "Linger"]]
    if dry:
        print("would write %s:\n" % path)
        print(text)
        print("would make %s (the unit's append: log lives there; systemd will not start without it)" % k.cache)
        print("would then run:")
        for c in cmds:
            print("  " + " ".join(c))
        return 0
    # systemd refuses a unit whose StandardOutput=append: directory is missing, and on a box where the dashboard
    # has never run nothing has made it yet
    os.makedirs(k.cache, 0o700, exist_ok=True)
    os.makedirs(unit_dir(k), 0o700, exist_ok=True)
    write_atomic(path, text, 0o644)       # by rename: a running daemon keeps reading its own copy
    print("wrote " + path)
    for c in cmds[:2]:
        r = subprocess.run(c, capture_output=True, text=True)
        print("  " + " ".join(c) + (" ok" if r.returncode == 0 else " FAILED: " + (r.stderr or "").strip()[:200]))
        if r.returncode != 0:
            return 1
    r = subprocess.run(cmds[2], capture_output=True, text=True)
    linger = (r.stdout or "").strip()
    print("  " + linger)
    if "yes" not in linger:
        print("  warning: linger is off, so the unit stops when the last login goes away "
              "(a person runs: loginctl enable-linger)")
    return 0


def cmd_uninstall(k):
    path = os.path.join(unit_dir(k), UNIT)
    for c in (["systemctl", "--user", "disable", "--now", UNIT], ):
        r = subprocess.run(c, capture_output=True, text=True)
        print("  " + " ".join(c) + (" ok" if r.returncode == 0 else " " + (r.stderr or "").strip()[:200]))
    try:
        os.remove(path)
        print("removed " + path)
    except OSError:
        print("no " + path)
    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True, text=True)
    return 0


# ---------------------------------------------------------------------------------------------- the subcommands
def print_human(snap):
    print("keeper %s on %s   role %s" % (snap["keeper"], snap["host"], snap["role"]))
    c = snap["cron"]["installed"]
    print("cron: %s" % ("installed" if c else "NOT INSTALLED" if c is False else "could not read the crontab"))
    r = snap["last_run"]
    print("last run: %s" % ("none" if not r else "%s %s vis=%s deploy=%s (%d run%s since a deploy)"
                            % (local(r["at_ms"]), r["mode"], r["vis"], r["deploy"],
                               snap["runs_since_deploy"], "" if snap["runs_since_deploy"] == 1 else "s")))
    d = snap["last_deploy"]
    print("last deploy: %s" % ("never" if not d else "%s fingerprint %s" % (local(d["at_ms"]), d["fp"])))
    p = snap["page"]
    print("page: %s (collector %s, read %s)" % ("%s min old" % p["age_min"] if p["age_min"] is not None
                                                else "not read: %s" % p["err"],
                                                p["host"] or "-", local(p["checked_ms"], "%T")))
    print("HALT: %s   EXPOSED: %s" % ("YES" if snap["halt"] else "no", "YES" if snap["exposed"] else "no"))
    if snap["repair"]:
        print("last repair: %s  %s" % (local(snap["repair"]["at_ms"]), snap["repair"]["what"]))
    for w in snap["warn"]:
        print("warn: " + w)
    for f in snap["fix"]:
        print("fix:  " + f)


def cmd_status(k, as_json):
    snap = k.status()
    if as_json:
        print(json.dumps(snap, separators=(",", ":")))
    else:
        print_human(snap)
    return 0


def cmd_tick(k):
    """One line a minute for the stream: the snapshot, the safe repairs, then the snapshot as JSON. The facts in
    it are the ones found before the repairs ran — a repair's effect shows on the next tick; only `repair`,
    `warn` and `fix` carry what this tick did. The line is printed whatever the repairs do: a tick that dies
    pushes nothing, which would take the keeper silent exactly when the collector's tree is broken."""
    k.deadline = time.monotonic() + TICK_BUDGET_S
    snap = k.status()
    try:
        k.repairs(snap)
    except Exception as e:
        Keeper.say(snap, scrub("the repairs raised %s" % type(e).__name__, VERDICT_MAX, k.owner),
                   "read keeper.log and update.log on this box")
    print(json.dumps(snap, separators=(",", ":")))
    return 0


def cmd_repair(k, force=False):
    """What a person, or a watchdog elsewhere, runs over ssh when the page stops: the repairs with their rate limits
    ignored, and then, if the page is still stale, one `update.sh now` in the foreground. R2 and R3 are left out
    (start_runs=False): the run they would start takes update.sh's lock without waiting, and the `now` below waits
    only 60 s for it (update.sh:412-416), so `repair` would report failure on the very freeze it was run for."""
    snap = k.status(force_page=True)
    print_human(snap)
    done = k.repairs(snap, ignore_limits=True, start_runs=False)
    print("\ndid: %s" % ("; ".join(done) if done else "nothing to repair before the run"))
    if snap["halt"] or snap["exposed"]:
        print("not running update.sh: deploys are halted, and only a person clears that (update.sh resume)")
        return 1
    if snap["role"] == "none":
        print("the dashboard is not set up on this box (no space, no standby_after_min): nothing to do")
        return 1
    page = snap["page"]
    if page["age_min"] is not None and page["age_min"] <= PAGE_FRESH_MIN:
        print("the page is %s min old: fresh" % page["age_min"])
        return 0
    if not force and not k.allowed("update_now_ms", NOW_EVERY_S, False):
        # every `now` deploys, and the account's deploys are capped per day: a second repair this soon means the
        # first did not work, which is a person's problem, not another deploy's
        print("update.sh now ran less than %d min ago and the page is still stale: not running it again "
              "(keeper.py repair --force overrides)" % (NOW_EVERY_S // 60))
        return 1
    rc, tail = k.run_update(["now"], NOW_TIMEOUT_S)
    k.now = time.time()                    # the run can take minutes; the page's age is read against now
    k.did("update_now_ms", "ran update.sh now (the page was %s min old), exit %s" % (page["age_min"], rc))
    print("ran update.sh now, exit %s:" % rc)
    for line in (tail or "").splitlines():
        # scrubbed like the JSON: a watchdog may relay this summary into a notification, and `update.sh now`
        # ends by printing the page's address
        print("  " + scrub(line, 160, k.owner))
    after = k.page(force=True)
    if after["age_min"] is None or after["age_min"] > PAGE_FRESH_MIN:
        time.sleep(15)             # the version can take a moment to be served; one more look, then give up
        k.now = time.time()
        after = k.page(force=True)
    print("page now: %s" % ("%s min old" % after["age_min"] if after["age_min"] is not None
                            else "not read: %s" % after["err"]))
    return 0 if after["age_min"] is not None and after["age_min"] <= PAGE_FRESH_MIN else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="keeper.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    for name in ("status", "tick"):
        s = sub.add_parser(name)
        s.add_argument("--json", action="store_true")
    s = sub.add_parser("repair")
    s.add_argument("--force", action="store_true", help="run update.sh now even if one ran in the last 10 minutes")
    s = sub.add_parser("install")
    s.add_argument("--dry-run", action="store_true")
    sub.add_parser("uninstall")
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 2
    k = Keeper()
    if args.cmd == "status":
        return cmd_status(k, args.json)
    if args.cmd == "tick":
        return cmd_tick(k)
    if args.cmd == "repair":
        return cmd_repair(k, args.force)
    if args.cmd == "install":
        return cmd_install(k, args.dry_run)
    return cmd_uninstall(k)


if __name__ == "__main__":
    sys.exit(main())
