#!/usr/bin/env python3
"""live-collector.py: one JSON line per second describing this lab machine, for `spacesheep stream --run`.

Read-only and unprivileged: /proc, /sys and /proc/locks only. It never opens an ET-SoC-1 device node, never takes a
card lock, and never reads another user's command line (only the 15-character process name the kernel shows to all),
Each line: {"host", "t" (ms), "up_s", "cpu": [per-core %], "cpu_all", "load": [1, 5, 15], "mem": {...},
"top": [[user, comm, pid, cpu%, rss_mb], ...], "nproc", "cards": [{"n", "pci", "link", "ok", "held"}],
"disk": [{"mount", "used_gb", "free_gb"}] for / and /home,
"temps": {"cpu", "nvme", "nic"} (°C from hwmon; the ET card's own temperature is not visible to Linux)}.
"""
import json
import os
import pwd
import socket
import sys
import time

HOST = socket.gethostname().split(".")[0]
TOP_N = int(os.environ.get("LIVE_TOP", "12"))
EVERY = float(os.environ.get("LIVE_EVERY", "1"))
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
            for line in f:
                p = line.split()
                # 1: FLOCK  ADVISORY  WRITE 1234 08:02:1311 0 EOF   (with "->" lines for waiters)
                if "->" in p:
                    continue
                dev_ino = p[5] if p[0].endswith(":") else p[4]
                held.add(int(dev_ino.split(":")[-1]))
    except (OSError, ValueError, IndexError):
        pass
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


def main():
    prev_cpu, prev_p, prev_t = cpu_times(), procs(), time.monotonic()
    card_state, card_at = cards(), 0.0
    disk_state = disk()
    sensors = find_sensors()
    while True:
        time.sleep(EVERY)
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
        prev_cpu, prev_p, prev_t = cur_cpu, cur_p, now


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, BrokenPipeError):
        pass
