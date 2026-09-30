#!/usr/bin/env python3
"""Write fixture.json: a complete, made-up data.json for the lab dashboard page (DESIGN.md §1).

    python3 tools/lab/dashboard/page/make_fixture.py [out.json]     (default: fixture.json beside this file)

Everything about people here is invented: the logins are user-a (the owner) to user-e, the session titles and the
schedule names are made up, and no address, e-mail or URL appears. Host names, card facts and firmware versions are
the lab's public facts (AGENT.md §4). The scenario, at 13:12 PDT on 30 September 2026:

- aifoundry3 does not answer (Tailscale check approval needed) since 11:50, so its block is the 11:40 one, stale;
- aifoundry1: its ZFS pool 95% full and /home 88% (et-lab-health WARNs), a pending reboot, card 1 held by user-c,
  card 0 excluded with its known events;
- aifoundry2: one failed unit, our queue running on its card, the owner's tmux and Claude alive;
- the owner's second claudes login lapses in 5 days.

render.py --fixture moves every time in it so that the data is 4 minutes old when the page is built."""
import json
import math
import os
import random
import sys
from datetime import datetime, timedelta, timezone

PDT = timezone(timedelta(hours=-7))
NOW = datetime(2026, 9, 30, 13, 12, 4, tzinfo=PDT)
STEP = 10  # minutes per history slot
N = 288
rnd = random.Random(20260930)


def iso(d):
    return d.isoformat(timespec="seconds")


def ms(d):
    return int(d.timestamp() * 1000)


def at(d, key="at"):
    """{key: iso, <key without _at>_ms: epoch ms}"""
    base = key[:-3] if key.endswith("_at") else key
    return {key: iso(d), base + "_ms": ms(d)}


def ago(**kw):
    return NOW - timedelta(**kw)


def t(day, hh, mm):
    return datetime(2026, 9, day, hh, mm, tzinfo=PDT)


# ---- the history grid ----
cur_slot = NOW.replace(minute=NOW.minute - NOW.minute % STEP, second=0, microsecond=0)
T0 = cur_slot - timedelta(minutes=STEP * (N - 1))
slot_t = [T0 + timedelta(minutes=STEP * i) for i in range(N)]


def idx(d):
    return int((d - T0).total_seconds() // (STEP * 60))


def span(a, b):
    """slot indices from datetime a up to (not including) b, clipped to the grid"""
    return range(max(0, idx(a)), min(N, idx(b)))


def noise(base, amp, i, period=37.0):
    return base + amp * math.sin(i / period * 2 * math.pi) + rnd.uniform(-amp / 3, amp / 3)


# approval lapses (the host answered nothing to us) and the collector's own gap
lapse = {
    "aifoundry1": [(t(30, 1, 10), t(30, 7, 30))],
    "aifoundry3": [(t(30, 0, 50), t(30, 7, 10)), (t(30, 11, 50), NOW + timedelta(minutes=10))],
    "aifoundry2": [],
}
collector_gap = (t(29, 3, 20), t(29, 3, 50))  # three collector runs missing (a made-up gap)
last_ok = {"aifoundry1": ago(minutes=2), "aifoundry2": ago(minutes=0), "aifoundry3": t(30, 11, 40)}

hist_hosts = {}
threads = {"aifoundry1": 16, "aifoundry2": 12, "aifoundry3": 32}
mem_total = {"aifoundry1": 31, "aifoundry2": 63, "aifoundry3": 125}
for h in ("aifoundry1", "aifoundry2", "aifoundry3"):
    up, load, mem, s_all, s_own, tmux, claude, warn = ([None] * N for _ in range(8))
    for i in range(N):
        down = any(i in span(a, b) for a, b in lapse[h])
        if i in span(*collector_gap):
            up[i] = None
        else:
            up[i] = "approval" if down else 1
        # nodewatch's heartbeat keeps its own record while we cannot reach the host; it is fetched when we can,
        # so the series stop at the last successful probe
        if slot_t[i] > last_ok[h]:
            continue
        busy = 0.0
        if h == "aifoundry2":
            busy = 5.5 if 150 <= i % 144 <= 156 else 0.0  # a build now and then
            load[i] = round(max(0.05, noise(1.4, 0.6, i) + busy), 2)
            mem[i] = round(noise(57.5, 1.5, i, 53), 1)
            s_own[i] = 5 if i > 60 else 4
            s_all[i] = s_own[i] + (1 if 100 <= i <= 200 else 0)
            tmux[i] = 1
            claude[i] = 6 if i > 200 else 5
        elif h == "aifoundry1":
            busy = 9.0 if 40 <= i <= 46 or 170 <= i <= 175 else 0.0  # CI jobs
            load[i] = round(max(0.02, noise(0.5, 0.3, i) + busy), 2)
            mem[i] = round(noise(26.0, 1.2, i, 41) - (5 if busy else 0), 1)
            s_own[i] = 1 if 80 <= i <= 110 or i >= 280 else 0
            s_all[i] = s_own[i] + (2 if 20 <= i <= 140 else 1) + (1 if i >= 276 else 0)
        else:
            load[i] = round(max(0.02, noise(0.7, 0.25, i)), 2)
            mem[i] = round(noise(119.0, 1.0, i, 61), 1)
            s_own[i] = 1 if 40 <= i <= 60 else 0
            s_all[i] = s_own[i] + 1
        warn[i] = {"aifoundry1": 3, "aifoundry2": 1 if i >= idx(t(30, 9, 0)) else 0, "aifoundry3": 0}[h]
    hist_hosts[h] = {"up": up, "load": load, "mem_avail_gib": mem, "sessions_all": s_all, "sessions_owner": s_own,
                     "tmux": tmux, "claude": claude, "warn": warn}

# card series: holds, use, telemetry readings where an experiment file or a sample exists
hist_cards = {}
holds = {
    "aifoundry2": [(t(28, 20, 45) + timedelta(minutes=40 * k), t(28, 20, 45) + timedelta(minutes=40 * k + 28), "user-a")
                   for k in range(30)] + [(t(29, 16, 59), t(29, 17, 38), "user-a"), (t(30, 12, 40), NOW + timedelta(minutes=10), "user-a")],
    "aifoundry1-c1": [(t(29, 9, 0), t(29, 9, 40), "user-a"), (t(29, 10, 10), t(29, 11, 30), "user-a"),
                      (t(29, 12, 0), t(29, 13, 0), "user-a"), (t(29, 15, 20), t(29, 15, 50), "user-b"),
                      (t(30, 13, 0), NOW + timedelta(minutes=10), "user-c")],
    "aifoundry3": [(t(29, 3, 0), t(29, 6, 0), "user-a"), (t(29, 18, 0), t(29, 18, 40), "user-e")],
    "aifoundry1-c0": [],
}
for c, hs in holds.items():
    host = c.split("-")[0]
    hold, used, die, watts, ce = ([None] * N for _ in range(5))
    for i in range(N):
        if hist_hosts[host]["up"][i] != 1:
            continue  # no run, or the host did not answer: unknown
        who = next((w for a, b, w in hs if i in span(a, b)), "")
        hold[i] = who
        used[i] = 1 if who else 0
        ce[i] = 0
        if c == "aifoundry1-c0":
            ce[i] = 2 if i % 9 == 0 else 0
            continue
        if who == "user-a":
            base = {"aifoundry2": 77, "aifoundry3": 70, "aifoundry1-c1": 66}[c]
            k = i - next(a_ for a_ in range(i, -1, -1) if hold[a_ - 1] != who or a_ == 0)  # slots into this hold
            die[i] = round(base + min(k, 4) * 1.5 + 1.5 * math.sin(i / 5.0))  # warms up, then wanders
            watts[i] = round(base / 2.0 + min(k, 3) * 1.2 + 0.8 * math.sin(i / 4.0), 1)
        elif who == "" and c == "aifoundry2" and hold[i - 1] == "user-a":
            die[i] = 71  # the idle reading taken after a block
            watts[i] = 33.1
    hist_cards[c] = {"hold": hold, "used": used, "die_c": die, "board_w": watts, "ce_new": ce}

# ---- hosts ----
def health(lines):
    ws = sum(1 for lv, _, _ in lines if lv == "WARN")
    return {"rev": 3, "exit": 1 if ws else 0, "warn": ws, "info": sum(1 for lv, _, _ in lines if lv == "INFO"),
            "lines": [{"level": lv, "check": ck, "text": tx} for lv, ck, tx in lines]}


hosts = {
    "aifoundry1": {
        "reachable": True, "via": "ssh", "error": None, **at(ago(minutes=0, seconds=6), "answered_at"),
        **at(ago(seconds=6), "last_ok_at"), "fails_in_row": 0, "took_ms": 1240, "stale": False, "as_of": None,
        "uptime_h": 245.3, "boot_id8": "3c9e71aa",
        "load": {"1": 0.41, "5": 0.52, "15": 0.6, "threads": 16, "per_thread": 0.03},
        "mem": {"total_gib": 31, "avail_gib": 26.4, "avail_pct": 85},
        "disks": [{"mount": "/", "used_pct": 95, "free_gib": 21}, {"mount": "/home", "used_pct": 88, "free_gib": 54}],
        "zfs": {"pool": "rpool", "state": "ONLINE", "used_pct": 95, "note": "42 errors at the last scrub"},
        "kernel": {"running": "7.0.0-31-generic", "reboot_pending": True, "pending_since": "25 Sep 16:38",
                   "pending": ["linux-image-7.0.0-34-generic", "linux-modules-7.0.0-34-generic"]},
        "systemd": {"state": "running", "failed": []},
        "temps": {"cpu_c": 48, "nvme_c": 39},
        "power_profile": "balanced", "chrony": {"synced": True, "offset_ms": 0.4},
        "health": health([
            ("OK", "driver", "et_soc1 0.20.0; built for 7.0.0-31-generic and 7.0.0-34-generic"),
            ("WARN", "card 0", "16.0 GT/s x8; err_stats: 4 PmicCeEvent, 212 ThermThrottleCeEvent"),
            ("INFO", "card 0 kernel", "11 card error events / 9 refused second opens / enabled 2 times in the last 10.1 h"),
            ("INFO", "card 0 port", "3980 corrected PCIe errors per hour at the root port"),
            ("OK", "card 1", "16.0 GT/s x8; no error events"),
            ("OK", "device nodes", "4 nodes, mode 0666"),
            ("OK", "lock files", "etsoc-shire0.lock, etsoc-shire1.lock owned by root"),
            ("OK", "memory", "26 GiB of 31 available"),
            ("WARN", "disk", "/home 88% used"),
            ("WARN", "zfs", "rpool ONLINE, 95% used; 42 errors at the last scrub"),
            ("OK", "dpkg", "audit clean"),
            ("INFO", "reboot", "pending since 25 Sep 16:38 (2 packages)"),
            ("OK", "systemd", "running"),
            ("OK", "chrony", "synced, offset 0.4 ms"),
            ("INFO", "power profile", "balanced"),
            ("INFO", "ci runner", "1 unit active, no job"),
        ]),
        "manifest": {"cpu": "16 threads", "et_soc1": "0.20.0", "srcversion": "5A0C1E2F9B7D", "libetrt": "ab12cd34"},
        "ci_runner": {"units": 1, "active": 1, "jobs": 0},
        "logins": {"sessions": 4, "people": 3},
        "nodewatch": {"present": True, **at(ago(seconds=40), "beat_at"), "beat_age_min": 0.7, "user_manager": "active",
                      "linger": True, "tmux": False, "claude": 0, "gaps_48h": [], "events_48h": [
                          {**at(t(30, 13, 0)), "type": "LOGIN", "what": "up"}]},
        "experiments": {"running": [], "last_log": {"file": "queue-tau-aifoundry1.log", **at(t(29, 13, 2)),
                                                    "line": "13:02:41 queue ends: 6 blocks ok, 0 failed"},
                        "others_device_procs": 1, "ci_jobs": 0},
    },
    "aifoundry2": {
        "reachable": True, "via": "local", "error": None, **at(ago(seconds=4), "answered_at"),
        **at(ago(seconds=4), "last_ok_at"), "fails_in_row": 0, "took_ms": 820, "stale": False, "as_of": None,
        "uptime_h": 285.5, "boot_id8": "0a1b2c3d",
        "load": {"1": 0.97, "5": 1.1, "15": 1.2, "threads": 12, "per_thread": 0.08},
        "mem": {"total_gib": 63, "avail_gib": 59, "avail_pct": 93},
        "disks": [{"mount": "/", "used_pct": 79, "free_gib": 190}],
        "zfs": None,
        "kernel": {"running": "7.0.0-31-generic", "reboot_pending": False, "pending_since": None, "pending": []},
        "systemd": {"state": "degraded", "failed": ["apport-coredump-hook@3-2211-1000.service"]},
        "temps": {"cpu_c": 61, "nvme_c": 43},
        "power_profile": "performance", "chrony": {"synced": True, "offset_ms": 0.2},
        "health": health([
            ("OK", "driver", "et_soc1 0.20.0; built for 7.0.0-31-generic"),
            ("OK", "card 0", "16.0 GT/s x8; err_stats: 18 PmicCeEvent, 10 ThermThrottleCeEvent (no power or thermal event since boot)"),
            ("INFO", "card 0 kernel", "0 card error events / 3 refused second opens / enabled 2 times in the last 52.1 h"),
            ("OK", "device nodes", "2 nodes, mode 0666"),
            ("OK", "lock files", "etsoc-shire0.lock owned by root"),
            ("OK", "memory", "59 GiB of 63 available"),
            ("OK", "disk", "/ 79% used"),
            ("OK", "dpkg", "audit clean"),
            ("OK", "reboot", "none pending"),
            ("WARN", "systemd", "degraded, 1 failed unit(s): apport-coredump-hook@3-2211-1000.service"),
            ("OK", "chrony", "synced, offset 0.2 ms"),
            ("OK", "power profile", "performance"),
            ("INFO", "ci runner", "1 unit active, no job"),
            ("INFO", "journal", "2.1 GiB, 38 boots since 14 Aug"),
        ]),
        "manifest": {"cpu": "12 threads", "et_soc1": "0.20.0", "srcversion": "5A0C1E2F9B7D", "libetrt": "9f3e1c20"},
        "ci_runner": {"units": 1, "active": 1, "jobs": 0},
        "logins": {"sessions": 6, "people": 2},
        "nodewatch": {"present": True, **at(ago(seconds=25), "beat_at"), "beat_age_min": 0.4, "user_manager": "active",
                      "linger": True, "tmux": True, "claude": 6,
                      "gaps_48h": [{**at(t(29, 3, 21), "from"), **at(t(29, 3, 35), "to"), "min": 14}],
                      "events_48h": [{**at(t(30, 12, 23)), "type": "CLAUDE", "what": "up"},
                                     {**at(t(30, 12, 34)), "type": "CLAUDE", "what": "up"},
                                     {**at(t(29, 3, 35)), "type": "WARN", "what": "gone"}]},
        "experiments": {"running": [{"kind": "queue.sh", "what": "schedule-nocr-aifoundry2.txt"}],
                        "last_log": {"file": "queue-nocr-aifoundry2.log", **at(ago(minutes=4)),
                                     "line": "13:08:14 block nocr p4 begins"},
                        "others_device_procs": 0, "ci_jobs": 0},
    },
    "aifoundry3": {
        "reachable": False, "via": "ssh", "error": "approval needed", **at(ago(seconds=30), "answered_at"),
        **at(t(30, 11, 40), "last_ok_at"), "fails_in_row": 9, "took_ms": 8000, "stale": True,
        **at(t(30, 11, 40), "as_of"), "next_try_ms": ms(t(30, 13, 52)),
        "uptime_h": 101.9, "boot_id8": "8d1f00c4",
        "load": {"1": 0.62, "5": 0.7, "15": 0.71, "threads": 32, "per_thread": 0.02},
        "mem": {"total_gib": 125, "avail_gib": 119, "avail_pct": 95},
        "disks": [{"mount": "/", "used_pct": 41, "free_gib": 530}, {"mount": "/home", "used_pct": 12, "free_gib": 1610}],
        "zfs": None,
        "kernel": {"running": "7.0.0-31-generic", "reboot_pending": False, "pending_since": None, "pending": []},
        "systemd": {"state": "running", "failed": []},
        "temps": {"cpu_c": 44, "nvme_c": None},
        "power_profile": "performance", "chrony": {"synced": True, "offset_ms": 1.1},
        "health": health([
            ("OK", "driver", "et_soc1 0.20.0; built for 7.0.0-31-generic"),
            ("OK", "card 0", "16.0 GT/s x8; no error events"),
            ("OK", "clock guard", "marker for this boot: 600 MHz minion, 400 MHz NoC, TDP 0 W"),
            ("OK", "device nodes", "2 nodes, mode 0666"),
            ("OK", "lock files", "etsoc-shire0.lock owned by root"),
            ("OK", "memory", "119 GiB of 125 available"),
            ("OK", "disk", "/ 41% used, /home 12% used"),
            ("OK", "systemd", "running"),
            ("INFO", "demo", "1 demo service active"),
        ]),
        "manifest": {"cpu": "32 threads", "et_soc1": "0.20.0", "srcversion": "5A0C1E2F9B7D", "libetrt": "77c0de11"},
        "ci_runner": None,
        "logins": {"sessions": 2, "people": 1},
        "nodewatch": {"present": True, **at(t(30, 11, 39), "beat_at"), "beat_age_min": 0.8, "user_manager": "active",
                      "linger": True, "tmux": False, "claude": 0, "gaps_48h": [], "events_48h": []},
        "experiments": {"running": [], "last_log": {"file": "queue-sp-aifoundry3.log", **at(t(29, 6, 1)),
                                                    "line": "06:01:12 queue ends: 4 blocks ok, 0 failed"},
                        "others_device_procs": 0, "ci_jobs": 0},
    },
}

# ---- cards ----
def card_base(host, devnum, pci, lock):
    return {"host": host, "devnum": devnum, "pci": pci, "lock": lock, "excluded": False, "note": None, "present": True}


LINK_OK = {"speed": "16.0 GT/s", "width": 8, "max_speed": "16.0 GT/s", "max_width": 8, "ok": True}
cards = {
    "aifoundry2": {
        **card_base("aifoundry2", 0, "0000:01:00.0", "etsoc-shire0.lock"),
        "static": {"firmware": "1.3.1", "bl": "0.20.0", "pmic": "1.5.0", "minion": "0.20.0", "tdp_w": 65,
                   "clock": "DVFS 600–800 MHz, in practice 600 (die above 65 °C)", "policy": "dvfs",
                   "idle_c": [60, 80], "idle_w": [26, 36]},
        "link": dict(LINK_OK), "power_state": "D0", "enabled": True,
        "errors": {"ce": {"PmicCeEvent": 18, "ThermThrottleCeEvent": 10}, "uce": {}, "ce_new": {}},
        "aer": {"card_total": 0, "port_total": 12, "port_per_h": 0},
        "kernel_log": {"error_events": 0, "refused_opens": 3, "enables": 2, "window_h": 52.1},
        "activity": {"mgmt": 261442, "ops": 3377811, "used": True, **at(ago(minutes=1), "last_used_at"),
                     "last_used_by": "queue"},
        "holder": {"held": True, "who": [{"node": "lock:etsoc-shire0.lock", "login": "user-a", "etime_s": 272, "ours": True}]},
        "telemetry": {"source": "experiment", **at(ago(minutes=3)), "age_min": 3, "die_c": 79, "die_max_c": 84,
                      "pmic_c": 63, "board_w": 41.2, "minion_mhz": 600, "noc_mhz": 400, "ddr_mhz": 933,
                      "from": "claims-v3/aifoundry2/nocr/p4/marks.jsonl"},
        "sample": {"enabled": False, "last_try": None, "result": "disabled", "next_after": None},
        "guard": None, "level": "ok", "reasons": ["our experiment running"],
    },
    "aifoundry3": {
        **card_base("aifoundry3", 0, "0000:41:00.0", "etsoc-shire0.lock"),
        "stale": True, **at(t(30, 11, 40), "as_of"),
        "static": {"firmware": "1.3.1", "bl": "0.20.0", "pmic": "1.5.0", "minion": "0.20.0", "tdp_w": 0,
                   "clock": "pinned at 600 MHz: a boot service sets a 0 W TDP, which latches the governor",
                   "policy": "pinned", "idle_c": [52, 62], "idle_w": [24, 29]},
        "link": dict(LINK_OK), "power_state": "D0", "enabled": True,
        "errors": {"ce": {"PmicCeEvent": 2}, "uce": {}, "ce_new": {}},
        "aer": {"card_total": 0, "port_total": 0, "port_per_h": 0},
        "kernel_log": {"error_events": 0, "refused_opens": 0, "enables": 1, "window_h": 101.9},
        "activity": {"mgmt": 88410, "ops": 1204551, "used": False, **at(t(29, 18, 40), "last_used_at"),
                     "last_used_by": "user-e"},
        "holder": {"held": False, "who": []},
        "telemetry": {"source": "experiment", **at(t(29, 6, 0)), "age_min": 1752, "die_c": 58, "die_max_c": 61,
                      "pmic_c": 49, "board_w": 27.4, "minion_mhz": 600, "noc_mhz": 400, "ddr_mhz": 933,
                      "from": "claims-v3/aifoundry3/sp/p2/tel.jsonl"},
        "sample": {"enabled": False, "last_try": None, "result": "disabled", "next_after": None},
        "guard": {"present": True, "this_boot": True, "minion_mhz": 600, "noc_mhz": 400, "tdp_w": 0},
        "level": "unknown", "reasons": ["aifoundry3 did not answer: approval needed"],
    },
    "aifoundry1-c1": {
        **card_base("aifoundry1", 1, "0000:02:00.0", "etsoc-shire1.lock"),
        "static": {"firmware": "1.2.0", "bl": "0.18.2", "pmic": "1.4.0", "minion": "0.18.2", "tdp_w": 65,
                   "clock": "600 MHz in every sample since 25 Sep: its governor never raises the clock",
                   "policy": "fixed", "idle_c": [55, 68], "idle_w": [25, 31]},
        "link": dict(LINK_OK), "power_state": "D0", "enabled": True,
        "errors": {"ce": {}, "uce": {}, "ce_new": {}},
        "aer": {"card_total": 0, "port_total": 3, "port_per_h": 0},
        "kernel_log": {"error_events": 0, "refused_opens": 1, "enables": 1, "window_h": 10.1},
        "activity": {"mgmt": 140221, "ops": 2210934, "used": True, **at(ago(minutes=2), "last_used_at"),
                     "last_used_by": "user-c"},
        "holder": {"held": True, "who": [{"node": "/dev/et1_ops", "login": "user-c", "etime_s": 723, "ours": False}]},
        "telemetry": {"source": "experiment", **at(t(29, 13, 0)), "age_min": 1452, "die_c": 64, "die_max_c": 69,
                      "pmic_c": 52, "board_w": 29.8, "minion_mhz": 600, "noc_mhz": 400, "ddr_mhz": 933,
                      "from": "claims-v3/aifoundry1-c1/tau/p6/tel-3.jsonl"},
        "sample": {"enabled": False, "last_try": None, "result": "disabled", "next_after": None},
        "guard": None, "level": "ok", "reasons": ["held by user-c since 12:48"],
    },
    "aifoundry1-c0": {
        **card_base("aifoundry1", 0, "0000:01:00.0", "etsoc-shire0.lock"),
        "excluded": True, "note": "overheats; excluded from all work and never touched",
        "static": {"firmware": "1.4.1", "bl": "0.21.0", "pmic": "1.6.0", "minion": "0.21.0", "tdp_w": 65,
                   "clock": "DVFS; idles at 300 MHz, and its governor acts only while a kernel runs",
                   "policy": "dvfs", "idle_c": [95, 117], "idle_w": None},
        "link": dict(LINK_OK), "power_state": None, "enabled": None,
        "errors": {"ce": {"PmicCeEvent": 4, "ThermThrottleCeEvent": 212}, "uce": {}, "ce_new": {"ThermThrottleCeEvent": 2}},
        "aer": {"card_total": None, "port_total": 1140744, "port_per_h": 3980},
        "kernel_log": {"error_events": 11, "refused_opens": 9, "enables": 2, "window_h": 10.1},
        "activity": None,
        "holder": {"held": False, "who": []},
        "telemetry": {"source": "none"},
        "sample": {"enabled": False, "last_try": None, "result": "disabled", "next_after": None},
        "guard": None, "level": "excluded", "reasons": ["excluded (overheats)"],
    },
}

# ---- people and the owner ----
people = [
    {"login": "user-a", "owner": True, "status": "active",
     "hosts": {"aifoundry2": {"sessions": 5, "closing": 1, "ttys": 12, "idle_min": 3, "procs": 214, "status": "active"},
               "aifoundry1": {"sessions": 1, "closing": 0, "ttys": 1, "idle_min": 40, "procs": 9, "status": "idle"}},
     "card_holds": [{"card": "aifoundry2", "etime_s": 272}], "device_procs": 0},
    {"login": "user-c", "owner": False, "status": "active",
     "hosts": {"aifoundry1": {"sessions": 1, "closing": 0, "ttys": 2, "idle_min": 1, "procs": 18, "status": "active"}},
     "card_holds": [{"card": "aifoundry1-c1", "etime_s": 723}], "device_procs": 1},
    {"login": "user-b", "owner": False, "status": "idle",
     "hosts": {"aifoundry1": {"sessions": 2, "closing": 0, "ttys": 3, "idle_min": 187, "procs": 41, "status": "idle"}},
     "card_holds": [], "device_procs": 0},
    {"login": "user-d", "owner": False, "status": "processes only",
     "hosts": {"aifoundry2": {"sessions": 1, "closing": 1, "ttys": 0, "idle_min": None, "procs": 7, "status": "processes only"}},
     "card_holds": [], "device_procs": 0},
    {"login": "user-e", "owner": False, "status": "away", "stale": True,
     "hosts": {"aifoundry3": {"sessions": 1, "closing": 0, "ttys": 1, "idle_min": 2890, "procs": 12, "stale": True, "status": "away"}},
     "card_holds": [], "device_procs": 0},
]

owner = {
    "login": "user-a",
    "claudes": {**at(ago(minutes=1), "as_of"), "accounts": [
        {"n": 1, "logged_in": True, "lapses": "2026-10-28", "lapse_days": 28, "tmux": "claude", "server": True,
         "phones": 1, "sessions": 3},
        {"n": 2, "logged_in": True, "lapses": "2026-10-05", "lapse_days": 5, "tmux": "claude2", "server": True,
         "phones": 0, "sessions": 1}],
        "pins": [{"id8": "0a1b2c3d", "account": 1, "window": "main", "running": True},
                 {"id8": "5e6f7a8b", "account": 2, "window": "review", "running": True}],
        "watchdog": {"on": True, **at(ago(seconds=20), "last_run"), "age_min": 0.3}},
    "sessions": {**at(ago(minutes=1), "as_of"),
                 "by_machine": {"aifoundry2": {"working": 2, "idle": 3, "done": 1, **at(ago(minutes=1), "last_at")},
                                "other": {"working": 1, "idle": 12, "done": 4, **at(ago(minutes=26), "last_at")}},
                 "lab": [
                     {"title": "Lab dashboard", "state": "working", "model": "claude-opus-5-5", "turns": 301,
                      **at(t(30, 12, 34), "started_at"), **at(ago(minutes=1), "last_at"), "source": "claude-code"},
                     {"title": "Queue watch for the third card", "state": "working", "model": "claude-opus-5-5",
                      "turns": 88, **at(t(30, 9, 5), "started_at"), **at(ago(minutes=6), "last_at"),
                      "source": "claude-code"},
                     {"title": "Heat placement page review", "state": "idle", "model": "claude-opus-5-5",
                      "turns": 142, **at(t(29, 19, 40), "started_at"), **at(t(30, 8, 12), "last_at"),
                      "source": "claude-code"},
                     {"title": "DV2 reduction", "state": "done", "model": "claude-opus-5-5", "turns": 57,
                      **at(t(29, 17, 2), "started_at"), **at(t(29, 21, 30), "last_at"), "source": "claude-code"}]},
    "nodewatch": {"aifoundry2": {"tmux": True, "claude": 6, "linger": True, "user_manager": "active", "beat_age_min": 0.4}},
}

# ---- alerts ----
def alert(aid, level, scope, title, detail, since, source, host=None, card=None, known=False, ack=None):
    return {"id": aid, "level": level, "scope": scope, "host": host, "card": card, "title": title, "detail": detail,
            **at(since, "since"), "source": source, "known": known, "ack": ack}


alerts = [
    alert("host:aifoundry3:reach", "warn", "host", "Does not answer: Tailscale check approval needed",
          "Its panel shows the last good data, greyed. Approve a check on aifoundry2 (ssh aifoundry3 true, then open "
          "the address it prints), then run update.sh now. Until then the collector tries this host once an hour.",
          t(30, 11, 50), "collector", host="aifoundry3"),
    alert("host:aifoundry1:zfs:rpool", "warn", "host", "ZFS pool rpool 95% full",
          "rpool ONLINE, 95% used; 42 errors at the last scrub. / is 95% used, /home 88%.", t(28, 7, 54),
          "et-lab-health", host="aifoundry1"),
    alert("host:aifoundry1:disk:/home", "warn", "host", "/home 88% used", "et-lab-health warns at 85%.",
          t(28, 7, 54), "et-lab-health", host="aifoundry1"),
    alert("host:aifoundry2:systemd", "warn", "host", "1 failed unit",
          "degraded: apport-coredump-hook@3-2211-1000.service (a crash report hook; clears at the next boot or with a "
          "reset-failed by an admin)", t(30, 9, 2), "et-lab-health", host="aifoundry2"),
    alert("owner:claudes:2:lapse", "warn", "owner", "claudes account 2: login lapses in 5 days",
          "Lapses on 5 Oct. Log in again with claudes before then.", t(30, 0, 2), "claudes status"),
    alert("card:aifoundry1-c1:held", "info", "card", "Held by user-c since 12:48", "/dev/et1_ops, 723 s",
          t(30, 13, 0), "et-who", host="aifoundry1", card="aifoundry1-c1"),
    alert("card:aifoundry2:experiment", "info", "card", "Our experiment running: queue.sh schedule-nocr-aifoundry2.txt",
          "13:08:14 block nocr p4 begins", t(30, 12, 40), "pgrep", host="aifoundry2", card="aifoundry2"),
    alert("host:aifoundry1:reboot", "info", "host", "Reboot pending since 25 Sep 16:38",
          "linux-image-7.0.0-34-generic, linux-modules-7.0.0-34-generic", t(28, 7, 54), "et-lab-health",
          host="aifoundry1"),
    alert("host:aifoundry1:zfs-scrub", "info", "host", "ZFS: 42 errors at the last scrub", "rpool", t(28, 7, 54),
          "et-lab-health", host="aifoundry1"),
    alert("owner:sessions:working", "info", "owner", "3 Claude sessions working", "2 on aifoundry2, 1 on another machine",
          t(30, 12, 34), "spacesheep sessions"),
    alert("card:aifoundry1-c0:ce", "info", "card", "New corrected events: 2 ThermThrottleCeEvent",
          "212 ThermThrottleCeEvent and 4 PmicCeEvent since boot", t(28, 7, 54), "sysfs err_stats",
          host="aifoundry1", card="aifoundry1-c0", known="card 0 overheats; excluded (AGENT.md §4)"),
    alert("card:aifoundry1-c0:aer-port", "info", "card", "Root port: 3,980 corrected PCIe errors an hour",
          "1,140,744 since boot", t(28, 7, 54), "sysfs aer_dev_correctable", host="aifoundry1", card="aifoundry1-c0",
          known="its root port logs about 4,000 corrected errors an hour"),
    alert("host:aifoundry1:power-profile", "info", "host", "CPU power profile balanced", "et-lab-health INFO",
          t(28, 7, 54), "et-lab-health", host="aifoundry1",
          ack={"note": "the lab's choice", **at(t(30, 9, 0), "at"), **at(t(30, 9, 0) + timedelta(days=7), "until")}),
]

data = {
    "schema": 1,
    **at(NOW, "generated_at"),
    "collector": {"host": "aifoundry2", "code": "a1b46e9", "took_s": 7.9, "interval_min": 10, "cron_minute": 2,
                  "heartbeat_min": 60, "stale_after_min": 80, "card_sample": "off", "errors": [],
                  "fixture": True},
    "status": {"level": "warn", "counts": {"bad": 0, "warn": 5, "info": 5, "known": 3},
               "headline": "5 warnings: aifoundry3 needs a Tailscale approval, aifoundry1's pool is 95% full and "
                           "/home 88%, aifoundry2 has 1 failed unit, a claudes login lapses in 5 days"},
    "fingerprint": "3fa2c1d09e4b",
    "alerts": alerts,
    "hosts": hosts,
    "cards": cards,
    "people": people,
    "owner": owner,
    "history": {"t0_ms": ms(T0), "step_min": STEP, "n": N, "hosts": hist_hosts, "cards": hist_cards},
}

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture.json")
with open(out, "w") as f:
    json.dump(data, f, indent=None, separators=(",", ":"), ensure_ascii=False)
    f.write("\n")
print("wrote", out, os.path.getsize(out), "bytes")
