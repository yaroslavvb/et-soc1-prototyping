#!/usr/bin/env python3
"""live-collector.py: one JSON line per second describing this lab machine, for `spacesheep stream --run`.

Read-only: /proc, /sys, /proc/locks and et-usaged's /run/et-usage/now.json. It never reads another user's command line
(only the 15-character process name the kernel shows to all). The one exception to "never touch a card", which the owner
asked for on 2 Oct 2026: every LIVE_CARD_EVERY seconds (1) it reads each card's temperature with `ettelem temp --if-free`
(about 4 ms of every second holding the management node, which admits one opener), only while nobody holds any card node
or lock on this machine and the card's link is up. The reader also probes the card's lock just before it opens the node
and stops if someone holds it; the probe is released at once, so it never refuses anyone's `flock -n` (holding the lock
through the reading would: most lab programs open only the ops node, which this reader never collides with).
Who holds what comes from et-usaged's /run/et-usage/now.json, which needs no privilege; only when that is missing,
stale, from another boot or blind does it ask `et-who --check` (sudo), at most every LIVE_WHO_EVERY seconds (15) or
when a card lock changes hands, and then it reads a card only on the ticks it asked. Until 4 Oct 2026 it ran et-who
every second, which wrote two sudo lines a second into the journal (Requests for Roman H35).
Each line: {"host", "t" (ms), "up_s", "cpu": [per-core %], "cpu_all", "load": [1, 5, 15], "mem": {...},
"top": [[user, comm, pid, cpu%, rss_mb], ...], "nproc", "cards": [{"n", "pci", "link", "ok", "held", "holders": [[login, program], ...],
"temp": {"die_c", "die_max_c", "pmic_c", "board_w", "at"}}] ("held" and "holders" every second, from the lock table and
now.json; a program is its kernel name, the 15 characters ps shows (argv[0]'s base name from the et-who fallback), never
its arguments; die_max_c is the firmware's peak since the card started or its stats were last reset, not a current
hottest sensor: Requests for Roman C30),
"disk": [{"mount", "used_gb", "free_gb"}] for / and /home,
"temps": {"cpu", "nvme", "nic"}.
Every LIVE_HIST_EVERY seconds (5) it also appends a compact record to ~/live/history/<UTC date>.jsonl on this machine's
disk, for the history page (tools/lab/history/build.py); files older than LIVE_HIST_DAYS (9) are deleted.
Record: {"t", "cpu", "mem", "load", "temps": {...}, "cards": [{"n", "ok", "held", "die", "max", "w"}]} (die/max/w only
from a reading under 5 s old) (°C from hwmon; the ET card's own temperature is not visible to Linux)}.
"""
import json
import os
import pwd
import re
import socket
import subprocess
import sys
import time

HOST = socket.gethostname().split(".")[0]
TOP_N = int(os.environ.get("LIVE_TOP", "12"))
EVERY = float(os.environ.get("LIVE_EVERY", "1"))
HIST_EVERY = float(os.environ.get("LIVE_HIST_EVERY", "5"))
HIST_DAYS = int(os.environ.get("LIVE_HIST_DAYS", "9"))
HIST_DIR = os.path.expanduser(os.environ.get("LIVE_HIST_DIR", "~/live/history"))
CARD_EVERY = float(os.environ.get("LIVE_CARD_EVERY", "1"))
WHO_EVERY = float(os.environ.get("LIVE_WHO_EVERY", "15"))
NOW_JSON = "/run/et-usage/now.json"
# the temperature reader: a copy of ettelem named lab-monitor, so that the open tracer (tools/lab/et-usage/et-opens)
# and et-usage show the lab's monitor by name; the build's own ettelem if the copy is missing
ETTELEM = os.path.expanduser(os.environ.get("LIVE_ETTELEM", "~/live/lab-monitor"))
if not os.access(ETTELEM, os.X_OK):
    ETTELEM = os.path.expanduser("~/live/ettelem-build/ettelem")
TICK = os.sysconf("SC_CLK_TCK")
PAGE_MB = os.sysconf("SC_PAGE_SIZE") / 1048576.0
users = {}
ME = os.getuid()


def user(uid):
    """the login name for a uid (the owner chose to show every user's name on the public dashboard, 2 Oct 2026)"""
    if uid not in users:
        try:
            users[uid] = pwd.getpwuid(uid).pw_name
        except KeyError:
            users[uid] = str(uid)
    return users[uid]


def cpu_times():
    out = []
    with open("/proc/stat") as f:
        for line in f:
            if line.startswith("cpu") and line[3].isdigit():
                v = [int(x) for x in line.split()[1:9]]
                idle = v[3] + v[4]
                out.append((sum(v), idle))
    return out


def procs():
    """pid -> (uid, comm, cpu ticks, rss pages)"""
    out = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/stat") as f:
                s = f.read()
            r = s.rindex(")")
            comm = s[s.index("(") + 1:r]
            rest = s[r + 2:].split()
            ticks = int(rest[11]) + int(rest[12])
            rss = int(rest[21])
            uid = os.stat(f"/proc/{d}").st_uid
            out[int(d)] = (uid, comm, ticks, rss)
        except (OSError, ValueError, IndexError):
            continue
    return out


def mem():
    m = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, v = line.split(":", 1)
            m[k] = int(v.split()[0])
    tot, avail = m["MemTotal"] / 1024, m["MemAvailable"] / 1024
    return {"total_mb": round(tot), "used_mb": round(tot - avail), "avail_mb": round(avail),
            "swap_used_mb": round((m.get("SwapTotal", 0) - m.get("SwapFree", 0)) / 1024)}


def disk():
    """/ and, when it is a separate filesystem, /home. On ZFS (aifoundry1) the free space is the pool's, shared."""
    out, devs = [], set()
    for m in ("/", "/home"):
        try:
            st, dev = os.statvfs(m), os.stat(m).st_dev
        except OSError:
            continue
        if dev in devs:
            continue
        devs.add(dev)
        out.append({"mount": m, "used_gb": round((st.f_blocks - st.f_bfree) * st.f_frsize / 1e9, 1),
                    "free_gb": round(st.f_bavail * st.f_frsize / 1e9, 1)})
    return out


def lock_inodes():
    """inodes of files that hold a POSIX or flock lock right now"""
    held = set()
    try:
        with open("/proc/locks") as f:
            lines = f.readlines()
    except OSError:
        return held
    for line in lines:
        p = line.split()
        # 1: FLOCK  ADVISORY  WRITE 1234 08:02:1311 0 EOF   (with "->" lines for waiters)
        if "->" in p:
            continue
        try:
            dev_ino = p[5] if p[0].endswith(":") else p[4]
            held.add(int(dev_ino.split(":")[-1]))
        except (ValueError, IndexError):
            continue  # one odd line does not hide the others
    return held


# hwmon sensors worth a graph: (key, hwmon name, label). acpitz is left out: on all three boards it reads constants
# (16.8 and 27.8 °C).
SENSORS = [("cpu", "coretemp", "Package id 0"), ("nvme", "nvme", "Composite"), ("nic", "enp7s0", "MAC Temperature")]


def find_sensors():
    """key -> path of its temp*_input, found once"""
    out = {}
    base = "/sys/class/hwmon"
    try:
        mons = sorted(os.listdir(base))
    except OSError:
        return out
    for m in mons:
        d = f"{base}/{m}"
        try:
            name = open(f"{d}/name").read().strip()
            files = sorted(f for f in os.listdir(d) if f.startswith("temp") and f.endswith("_input"))
        except OSError:
            continue
        for key, want_name, want in SENSORS:
            if key in out or name != want_name:
                continue
            for f in files:
                try:
                    label = open(f"{d}/{f[:-6]}_label").read().strip()
                except OSError:
                    label = ""
                if want in (label, f):
                    out[key] = f"{d}/{f}"
                    break
    return out


def temps(paths):
    out = {}
    for k, p in paths.items():
        try:
            out[k] = round(int(open(p).read()) / 1000.0, 1)
        except (OSError, ValueError):
            pass
    return out


def cards():
    out = []
    base = "/sys/bus/pci/drivers/ET"
    try:
        devs = sorted(x for x in os.listdir(base) if x.startswith("0000:"))
    except OSError:
        return out
    held = lock_inodes()
    for d in devs:
        p = f"{base}/{d}"
        try:
            n = int(open(f"{p}/devnum").read().strip())
        except (OSError, ValueError):
            n = None
        try:
            with open(f"{p}/config", "rb") as f:
                ok = f.read(4) != b"\xff\xff\xff\xff"
            sp = open(f"{p}/current_link_speed").read().strip().replace(" PCIe", "")
            wd = open(f"{p}/current_link_width").read().strip()
            link = f"{sp} x{wd}" if ok else "DOWN"
        except OSError:
            ok, link = False, "?"
        lk = f"/run/lock/etsoc-shire{n}.lock"
        try:
            is_held = os.stat(lk).st_ino in held
        except OSError:
            is_held = None
        out.append({"n": n, "pci": d, "link": link, "ok": ok, "held": is_held})
    return out


HOLDER = re.compile(r"^(?:/dev/et(\d+)_\w+|lock:etsoc-shire(\d+)\.lock)\s+(\S+)\s+(\d+)\s+\S+\s+(\S+)")
WRAPPERS = {"flock", "timeout", "bash", "sh", "env", "nice", "setsid", "nohup"}


CI_COMMS = {"Runner.Worker", "Runner.Listener", "runsvc.sh"}


def root_kind(pid):
    """a card holder running as root: 'CI runner' when one of its ancestors is the CI runner, else 'root (shared login)'
    (people get the shared root login to create their own account); /proc/<pid>/stat's names and parents only"""
    p = pid
    for _ in range(20):
        try:
            st = open(f"/proc/{p}/stat").read()
        except OSError:
            break
        comm = st[st.index("(") + 1:st.rindex(")")]
        if comm in CI_COMMS:
            return "CI runner"
        p = int(st[st.rindex(")") + 2:].split()[1])
        if p <= 1:
            break
    return "root (shared login)"


def pick_holders(seen):
    """card n -> [(who, program, holds a node)] to card n -> [[login, program], ...]: a card's programs are those
    holding its device nodes when there are any, else its lock's holders (flock, timeout ...)"""
    out = {}
    for n, hs in seen.items():
        pick = ([h for h in hs if h[2] and h[1] not in WRAPPERS] + [h for h in hs if not h[2] and h[1] not in WRAPPERS]) or hs
        uniq = []
        for u, prog, _ in pick:
            if [u, prog] not in uniq:
                uniq.append([u, prog])
        out[n] = uniq[:3]
    return out


try:
    BOOT_ID = open("/proc/sys/kernel/random/boot_id").read().strip()
except OSError:
    BOOT_ID = None
NOW_MAX_AGE = 150  # s: et-usaged rewrites now.json on every change and at least once a minute


def holders_now():
    """(0 free / 1 held, card n -> holders) from et-usaged's now.json, or None when it cannot be trusted: missing,
    malformed, older than NOW_MAX_AGE, from another boot, its daemon gone, or the daemon unable to see every process.
    The daemon rewrites it within ~20 ms of any open or close of a card node (lock-only changes at most once a second,
    which the lock table covers in the meantime)."""
    try:
        with open(NOW_JSON) as f:
            d = json.load(f)
        if (not isinstance(d, dict) or d.get("v") != 1 or BOOT_ID is None or d.get("boot") != BOOT_ID
                or not d.get("sees_all") or not (time.time() - float(d["at"]) < NOW_MAX_AGE)
                or not os.path.exists(f"/proc/{int(d['pid'])}")):
            return None
        seen = {}
        for h in d.get("holds") or []:
            pid = int(h["pid"])
            comm = str(h.get("comm") or "?")[:32]
            who = root_kind(pid) if h.get("user") == "root" else str(h.get("user") or h.get("uid"))
            seen.setdefault(int(h["card"]), []).append((who, comm, bool(h.get("nodes"))))
    except Exception:  # whatever is in the file, the stream goes on: fall back to et-who
        return None
    return (1 if seen else 0), pick_holders(seen)


def holders_etwho():
    """(et-who --check's exit status: 0 free, 1 held, 2 failed; card n -> [[login, program], ...]). It runs sudo, which
    logs every call: the fallback only."""
    try:
        r = subprocess.run(["et-who", "--check"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return 2, {}
    seen = {}
    for line in r.stdout.splitlines():
        m = HOLDER.match(line)
        if not m:
            continue
        n = int(m.group(1) or m.group(2))
        prog = os.path.basename(m.group(5))[:32]
        who = root_kind(int(m.group(4))) if m.group(3) == "root" else m.group(3)
        seen.setdefault(n, []).append((who, prog, m.group(1) is not None))
    return r.returncode, pick_holders(seen)


class Holders:
    """who holds each card, every second: now.json when it can be trusted, else et-who, asked again only after
    WHO_EVERY seconds or when a card's lock changes hands. get() -> (rc, holders, fresh): fresh is False on a tick that
    reuses an older et-who answer, so that no card is read on it."""

    def __init__(self):
        self.cached, self.at, self.locks = None, -1e9, None

    def get(self, card_locks):
        r = holders_now()
        if r is not None:
            return r[0], r[1], True
        now = time.monotonic()
        if self.cached is None or now - self.at >= WHO_EVERY or card_locks != self.locks:
            self.cached, self.at, self.locks = holders_etwho(), now, card_locks
            return self.cached[0], self.cached[1], True
        return self.cached[0], self.cached[1], False


class CardTemps:
    """card n -> its last reading. `ettelem temp` is never killed (a sampler killed mid-request poisons the management
    queue): a run that has not finished after half a second is collected on a later tick, and nothing new starts
    until it has."""

    def __init__(self):
        self.last, self.proc, self.busy = {}, None, False

    def collect(self, wait):
        n, p = self.proc
        try:
            p.wait(timeout=wait)
        except subprocess.TimeoutExpired:
            return False
        self.proc = None
        try:
            v = json.loads(p.stdout.read().strip().splitlines()[-1])
            if p.returncode == 0 and "die_c" in v:
                self.last[n] = {k: v.get(k) for k in ("die_c", "die_max_c", "pmic_c", "board_w")}
                self.last[n]["at"] = v["t_ms"]
        except (ValueError, IndexError, KeyError, OSError):
            pass
        p.stdout.close()
        self.busy = p.returncode == 3  # the reader found the card's lock taken and opened nothing
        return True

    def tick(self, cards_now, free):
        """free: nobody holds any card node or lock on this machine this tick, by now.json (or a fresh et-who) and the
        lock table; the reader also probes the card's lock and opens nothing if someone holds it, and then this tick
        reads no other card either"""
        if self.proc and not self.collect(0):
            return
        due = [c["n"] for c in cards_now if c["ok"] and c["n"] is not None and
               time.time() * 1000 - (self.last.get(c["n"]) or {}).get("at", 0) >= CARD_EVERY * 1000 - 300]
        if not due or not os.access(ETTELEM, os.X_OK) or not free:
            return  # someone holds a card node or lock on this machine: no reading this time
        for n in due:
            env = dict(os.environ, ET_DEVICES=str(n), LD_LIBRARY_PATH="/opt/et/lib")
            try:
                self.proc = (n, subprocess.Popen([ETTELEM, "temp", "--if-free"], stdout=subprocess.PIPE,
                                                 stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, env=env, text=True))
            except OSError:
                return
            if not self.collect(0.5) or self.busy:
                return


def record(line):
    """append one compact history record; never let a disk problem stop the stream"""
    now_ms = line["t"]
    cs = []
    for c in line["cards"]:
        r = {"n": c["n"], "ok": c["ok"], "held": c["held"]}
        t = c.get("temp")
        if t and now_ms - t.get("at", 0) < 5000:
            r.update(die=t.get("die_c"), max=t.get("die_max_c"), w=t.get("board_w"))
        cs.append(r)
    m = line["mem"]
    rec = {"t": now_ms, "cpu": line["cpu_all"], "mem": round(100.0 * m["used_mb"] / max(m["total_mb"], 1), 1),
           "load": line["load"][0], "temps": line.get("temps", {}), "cards": cs}
    try:
        os.makedirs(HIST_DIR, exist_ok=True)
        day = time.strftime("%Y-%m-%d", time.gmtime(now_ms / 1000))
        with open(f"{HIST_DIR}/{day}.jsonl", "a") as f:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
        if time.gmtime(now_ms / 1000).tm_min == 0:  # once an hour or so: drop old days
            cut = time.strftime("%Y-%m-%d", time.gmtime(now_ms / 1000 - HIST_DAYS * 86400))
            for fn in os.listdir(HIST_DIR):
                if fn.endswith(".jsonl") and fn[:10] < cut:
                    os.remove(f"{HIST_DIR}/{fn}")
    except OSError:
        pass


def main():
    prev_cpu, prev_p, prev_t = cpu_times(), procs(), time.monotonic()
    card_state, card_at = cards(), 0.0
    disk_state = disk()
    ctemp = CardTemps()
    who = Holders()
    sensors = find_sensors()
    due = time.monotonic()
    hist_at = 0.0
    while True:
        due += EVERY  # a fixed cadence: the tick's own work does not stretch it
        time.sleep(max(0.0, due - time.monotonic()))
        now = time.monotonic()
        cur_cpu, cur_p = cpu_times(), procs()
        dt = max(now - prev_t, 1e-3)
        per = []
        for (t1, i1), (t0, i0) in zip(cur_cpu, prev_cpu):
            dtot = t1 - t0
            per.append(round(100.0 * (1 - (i1 - i0) / dtot), 1) if dtot > 0 else 0.0)
        top = []
        for pid, (uid, comm, ticks, rss) in cur_p.items():
            old = prev_p.get(pid)
            if old is None or old[1] != comm:
                continue
            pct = 100.0 * (ticks - old[2]) / TICK / dt
            if pct > 0.05 or rss * PAGE_MB > 2048:
                top.append([user(uid), comm, pid, round(pct, 1), round(rss * PAGE_MB)])
        top.sort(key=lambda r: (-r[3], -r[4]))
        if now - card_at >= 5:
            card_state, card_at, disk_state = cards(), now, disk()
        # who holds each card, every second: the lock table and et-usaged's now.json (node holders too), both without
        # privilege; only while some card answers, and before any temperature read, which they gate
        locked = lock_inodes()
        lks = {}
        for c in card_state:
            try:
                lks[c["n"]] = os.stat(f"/run/lock/etsoc-shire{c['n']}.lock").st_ino in locked
            except OSError:
                lks[c["n"]] = None
        rc, hold, fresh = (who.get(frozenset(n for n, v in lks.items() if v)) if any(c["ok"] for c in card_state)
                           else (None, {}, False))
        for c in card_state:
            lk, hs = lks.get(c["n"]), hold.get(c["n"], [])
            c["held"] = bool(lk or hs) if (lk is not None or rc in (0, 1)) else None
            c["holders"] = hs if rc in (0, 1) else None
        ctemp.tick(card_state, rc == 0 and fresh and not any(lks.values()))
        for c in card_state:
            c["temp"] = ctemp.last.get(c["n"])
        line = {
            "host": HOST, "t": int(time.time() * 1000),
            "up_s": int(float(open("/proc/uptime").read().split()[0])),
            "cpu": per, "cpu_all": round(sum(per) / max(len(per), 1), 1),
            "load": [round(x, 2) for x in os.getloadavg()], "mem": mem(),
            "top": top[:TOP_N], "nproc": len(cur_p), "cards": card_state,
            "disk": disk_state, "temps": temps(sensors),
        }
        sys.stdout.write(json.dumps(line, separators=(",", ":")) + "\n")
        sys.stdout.flush()
        if now - hist_at >= HIST_EVERY - 0.2:
            hist_at = now
            record(line)
        prev_cpu, prev_p, prev_t = cur_cpu, cur_p, now


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, BrokenPipeError):
        pass
