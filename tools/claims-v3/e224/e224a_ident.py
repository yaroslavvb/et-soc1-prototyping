#!/usr/bin/env python3
"""E224's kit, ARM A (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): THE CARD'S IDENTITY and THE SAMPLER'S FRESHNESS for E224's
arm A, aifoundry1 card 1: E218's identity module (tools/claims-v3/e218/e218_ident.py, landed in 5582edfc; E215 arm A's, E206's module line for
line) with E215 ARM B's card (tools/claims-v3/e215/e215_ident.py's arm B: card 1's nodes /dev/et1_*, physical device ID 1, minion_mv below 510,
the lock etsoc-shire1.lock; E215 arm B ran FULL on this card with it, data 4f648f24). Every function below is E206's, line for line, but this
docstring, the arm table (arm A only: aifoundry1's card 1) and the self-check (card 1's cases). Python's own modules only (the box's system
python3; at the desk /usr/bin/python3 -I -B, 3.12.3).
  - THE CARD'S IDENTITY, read three ways before any launch and watched at every launch:
      * the start config read's stderr (the device layer's identity block): every 'PCIe target' line names /dev/et1_mgmt and every 'Physical
        device ID' line names 1, and the config's minion_mv is below 510 (card 1 read 499 or 500 in every committed read; aifoundry1's card 0
        and aifoundry2's card read 519; aifoundry3's 523);
      * with the sampler running and before the smoke: et-who (counts by card, never a name) shows at least one line of ours on /dev/et1_mgmt,
        none of ours off card 1, and no other login's line on card 1 (aifoundry1 has two cards: another login's line on card 0 is the
        runner's start rule, never this read's); and the sampler's own open files (/proc/<pid>/fd) hold /dev/et1_mgmt and no other card's node;
      * at every host process (the watch): its stderr's identity block and the nodes its process tree holds open name card 1 and no other card,
        else the run's stop file is touched at once (the host ends at its next launch boundary) and the session stops. In the smoke each process
        must also have shown card 1, and the board must rise over the rest by at least RISE_MIN_W during its launches;
  - THE SAMPLER'S FRESHNESS: a live sample less than SAMPLE_FRESH_S old before every process, else the session ends;
  - the self-check (python3 -I -B tools/claims-v3/e224/e224a_ident.py: E224A-IDENT SELF-CHECK PASS).
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import statistics
import threading
import time

DEV_DIR = "/dev"                 # where the cards' nodes are; a desk test points it at its own stand-in directory
IDENT = {
    "A": {"card": "1", "mgmt": "/dev/et1_mgmt", "ops": "/dev/et1_ops", "phys_id": 1, "mv_below": 510, "lock": "etsoc-shire1.lock",
          "one_card": False},
}
SAMPLE_FRESH_S = 2.0             # the verifier's finding 4: a live sample less than 2 s old before every process
RISE_MIN_W = 2.0                 # the smoke: the median board W inside a process's launches at least 2 W over the rest's median
RISE_MIN_SAMPLES = 3             # ... over at least 3 samples
WATCH_EVERY_S = 0.1              # the host watch's period

RE_TARGET = re.compile(r"^PCIe target:\s+/dev/et(\d+)_(ops|mgmt)\b")
RE_PHYS = re.compile(r"^Physical device ID:\s+(\d+)\b")
RE_LOCK = re.compile(r"^lock:etsoc-shire(\d+)\.lock$")
RE_NODE = re.compile(r"^/dev/et(\d+)_(ops|mgmt)$")


def parse_ident(text):
    """The device layer's identity block on a stderr: ([(card, node kind)], [physical device IDs]), every occurrence."""
    targets, ids = [], []
    for ln in (text or "").splitlines():
        s = ln.strip()
        m = RE_TARGET.match(s)
        if m:
            targets.append((m.group(1), m.group(2)))
        m = RE_PHYS.match(s)
        if m:
            ids.append(int(m.group(1)))
    return targets, ids


def config_identity(arm, j, err_text):
    """'' when the config read names the arm's card (every PCIe target line the arm's mgmt node, every physical device ID the arm's; an arm
    with a voltage bound also minion_mv below it: E224's arm has none); else why. A read with no such line fails: the card cannot be told."""
    I = IDENT[arm]
    targets, ids = parse_ident(err_text)
    why = []
    if not targets:
        why.append("no 'PCIe target' line on the config read's stderr")
    elif any(t != (I["card"], "mgmt") for t in targets):
        why.append("PCIe target " + ", ".join(sorted({f"/dev/et{c}_{k}" for c, k in targets})) + f", not {I['mgmt']}")
    if not ids:
        why.append("no 'Physical device ID' line on the config read's stderr")
    elif any(i != I["phys_id"] for i in ids):
        why.append(f"Physical device ID {sorted(set(ids))}, not {I['phys_id']}")
    if I["mv_below"] is not None:
        mv = (j or {}).get("minion_mv")
        if not isinstance(mv, (int, float)) or isinstance(mv, bool) or mv >= I["mv_below"]:
            why.append(f"minion_mv {mv}, not below {I['mv_below']} (card 1 read 499 or 500 in every committed read; card 0 519; aifoundry3 523)")
    return "; ".join(why)


def holder_card(field):
    """The card a holder line's first field names (/dev/etN_..., lock:etsoc-shireN.lock), or '?'."""
    m = re.match(r"^/dev/et(\d+)_", field)
    if m:
        return m.group(1)
    m = RE_LOCK.match(field)
    return m.group(1) if m else "?"


def etwho_identity(arm, lines, me):
    """The holder read made with the sampler running, before the smoke: ('' or why, counts). Every holder line of ours is on the arm's card
    (a node or its lock); at least one is on the arm's mgmt node (the sampler's); no other login holds the arm's card (on a one-card box
    anything; aifoundry1 has two: another login's line on card 0 is the runner's start rule). Counts only: no login is ever written."""
    I = IDENT[arm]
    c = I["card"]
    hold = [ln.split() for ln in lines if (ln.startswith("/dev/et") or ln.startswith("lock:")) and len(ln.split()) > 1]
    ours = [f for f in hold if f[1] == me]
    other = [f for f in hold if f[1] != me]
    counts = {"ours_on_mgmt": sum(1 for f in ours if f[0] == I["mgmt"]),
              "ours_on_card": sum(1 for f in ours if holder_card(f[0]) == c),
              "ours_off_card": sum(1 for f in ours if holder_card(f[0]) != c),
              "other_on_card": sum(1 for f in other if holder_card(f[0]) == c),
              "other_off_card": sum(1 for f in other if holder_card(f[0]) != c)}
    why = []
    if counts["ours_on_mgmt"] < 1:
        why.append(f"no holder line of ours on {I['mgmt']} (the sampler's) with the sampler running")
    if counts["ours_off_card"]:
        why.append(f"{counts['ours_off_card']} holder line(s) of ours off card {c}")
    one = I.get("one_card", True)
    if counts["other_on_card"] or (one and counts["other_off_card"]):
        why.append(f"{counts['other_on_card'] + (counts['other_off_card'] if one else 0)} holder line(s) of another login on the card")
    return "; ".join(why), counts


def node_of(path, dev_dir=None):
    """(card, kind) when path is a card node under dev_dir (/dev/etN_ops or /dev/etN_mgmt there), else None."""
    d = os.path.realpath(dev_dir or DEV_DIR) if (dev_dir or DEV_DIR) != "/dev" else "/dev"
    if not path or not path.startswith(d + "/"):
        return None
    m = re.match(r"^et(\d+)_(ops|mgmt)$", path[len(d) + 1:])
    return (m.group(1), m.group(2)) if m else None


def descendants(pid):
    """pid and its descendants, through /proc/<pid>/task/<tid>/children (else a scan of /proc/*/stat)."""
    out, todo = [], [pid]
    while todo:
        p = todo.pop()
        if p in out:
            continue
        out.append(p)
        kids = []
        try:
            for tid in os.listdir(f"/proc/{p}/task"):
                with open(f"/proc/{p}/task/{tid}/children") as f:
                    kids += [int(x) for x in f.read().split()]
        except OSError:
            try:
                for d in os.listdir("/proc"):
                    if d.isdigit():
                        try:
                            with open(f"/proc/{d}/stat") as f:
                                st = f.read()
                            if int(st[st.rindex(")") + 2:].split()[1]) == p:
                                kids.append(int(d))
                        except (OSError, ValueError, IndexError):
                            pass
            except OSError:
                pass
        todo += kids
    return out


def proc_nodes(pid, dev_dir=None):
    """The card nodes one process holds open (/proc/<pid>/fd) or mapped (/proc/<pid>/maps): {(card, kind)}."""
    seen = set()
    try:
        for fd in os.listdir(f"/proc/{pid}/fd"):
            try:
                n = node_of(os.readlink(f"/proc/{pid}/fd/{fd}"), dev_dir)
            except OSError:
                continue
            if n:
                seen.add(n)
    except OSError:
        pass
    try:
        with open(f"/proc/{pid}/maps") as f:
            for ln in f:
                parts = ln.split(None, 5)
                if len(parts) == 6:
                    n = node_of(parts[5].strip(), dev_dir)
                    if n:
                        seen.add(n)
    except OSError:
        pass
    return seen


def host_identity(arm, targets, ids, nodes):
    """(wrong, right) for one host process: wrong lists everything that names or holds another card; right is True when the arm's own card
    was named (a PCIe target or physical device ID on the host's stderr) or held (a node in its process tree)."""
    c = IDENT[arm]["card"]
    wrong = sorted({f"stderr PCIe target /dev/et{x}_{k}" for x, k in targets if x != c} |
                   {f"stderr Physical device ID {i}" for i in ids if str(i) != c} |
                   {f"holds /dev/et{x}_{k}" for x, k in nodes if x != c})
    right = any(x == c for x, k in targets) or any(str(i) == c for i in ids) or any(x == c for x, k in nodes)
    return wrong, right


class HostWatch(threading.Thread):
    """Watches one host process while it runs (every WATCH_EVERY_S): the new text of its stderr file for the device layer's identity block,
    and the card nodes its process tree (the `timeout` process and its children) holds open or mapped. The first sight of another card
    calls on_wrong(why) once, at once (the runner touches the hosts' stop file there)."""

    def __init__(self, arm, pid, err_path, dev_dir=None, on_wrong=None):
        super().__init__(daemon=True)
        self.arm, self.pid, self.err_path, self.dev_dir, self.on_wrong = arm, pid, err_path, dev_dir, on_wrong
        self.text = ""
        self.pos = 0
        self.nodes = set()
        self.polls = 0
        self.tripped = None
        self.done = threading.Event()

    def poll(self):
        self.polls += 1
        try:
            with open(self.err_path, "r", errors="replace") as f:
                f.seek(self.pos)
                new = f.read()
                self.pos = f.tell()
            self.text += new
        except OSError:
            pass
        for p in descendants(self.pid):
            self.nodes |= proc_nodes(p, self.dev_dir)
        targets, ids = parse_ident(self.text)
        wrong, _ = host_identity(self.arm, targets, ids, self.nodes)
        if wrong and not self.tripped:
            self.tripped = "; ".join(wrong)
            if self.on_wrong:
                self.on_wrong(f"the host named or held another card ({self.tripped})")

    def run(self):
        while not self.done.is_set():
            self.poll()
            self.done.wait(WATCH_EVERY_S)

    def finish(self):
        self.done.set()
        self.join(timeout=5)
        self.poll()          # the last of its stderr

    def result(self):
        targets, ids = parse_ident(self.text)
        wrong, right = host_identity(self.arm, targets, ids, self.nodes)
        return {"stderr_targets": sorted({f"/dev/et{c}_{k}" for c, k in targets}), "stderr_ids": sorted(set(ids)),
                "nodes_held": sorted(f"/dev/et{c}_{k}" for c, k in self.nodes), "wrong": wrong, "right": right, "polls": self.polls,
                "tripped": self.tripped}


def board_rise(samples, window_ms, rest_w):
    """(ok, rise W or None, n): the median board W of the samples inside window_ms [first launch's start, last launch's end] less the rest's
    median; ok when n >= RISE_MIN_SAMPLES and the rise is at least RISE_MIN_W."""
    if not window_ms or rest_w is None:
        return False, None, 0
    lo, hi = window_ms
    bw = [s.get("board_w") for s in samples if s.get("board_w") is not None and lo <= (s.get("t_ms") or 0) <= hi]
    if len(bw) < RISE_MIN_SAMPLES:
        return False, None, len(bw)
    rise = statistics.median(bw) - rest_w
    return rise >= RISE_MIN_W, round(rise, 3), len(bw)


def fresh(alive, last_rx, now=None):
    """The sampler is live: its process alive and a sample received less than SAMPLE_FRESH_S ago."""
    now = time.time() if now is None else now
    return bool(alive) and last_rx is not None and (now - last_rx) < SAMPLE_FRESH_S


# ------------------------------------------------------------------ the self-check
BLOCK = ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:1]: \nPCIe target:                                               /dev/et{c}_{k}       \n"
         "PCIBUS device name:                                        0000:02:00.0        \n"
         "Physical device ID:                                        {c}                    (0x{c})\nTDP (W):                                                   65\n")


def selfcheck():
    bad = []
    c1, c0 = BLOCK.format(c=1, k="mgmt"), BLOCK.format(c=0, k="mgmt")
    if parse_ident(c0) != ([("0", "mgmt")], [0]) or parse_ident(c1) != ([("1", "mgmt")], [1]) or parse_ident("") != ([], []):
        bad.append("parse_ident on card 0's and card 1's blocks")
    # aifoundry1's card 1: its config reads 499-500 mV (card 0 519), its block as the reader prints it there (E215 arm B's cases)
    ok_a = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 499}
    if config_identity("A", ok_a, c1) or config_identity("A", dict(ok_a, minion_mv=500), c1):
        bad.append("arm A's config identity: card 1's block at 499 / 500 mV must pass")
    if not config_identity("A", dict(ok_a, minion_mv=519), c0) or not config_identity("A", ok_a, c0) or \
            not config_identity("A", dict(ok_a, minion_mv=519), c1) or not config_identity("A", ok_a, "") or \
            not config_identity("A", dict(ok_a, minion_mv=None), c1) or not config_identity("A", ok_a, c1 + c0) or \
            not config_identity("A", dict(ok_a, minion_mv=523), c1) or not config_identity("A", ok_a, c1.replace("et1_mgmt", "et1_ops")):
        bad.append("arm A's config identity (card 0's block, 519 or 523 mV, none, both, no minion_mv, or the ops node must fail)")
    me = "us"
    sa = "/dev/et1_mgmt  us 100 00:05 the-sampler"
    lk1 = "lock:etsoc-shire1.lock us 99 00:06 python3 run_e224a.py"
    if etwho_identity("A", [sa, lk1], me)[0] or not etwho_identity("A", [lk1], me)[0] or \
            not etwho_identity("A", [sa.replace("et1", "et0"), lk1], me)[0] or not etwho_identity("A", [sa, lk1, "/dev/et0_ops us 7 0 x"], me)[0]:
        bad.append("arm A's holder read (ours on /dev/et1_mgmt; none of ours off card 1)")
    if not etwho_identity("A", [sa, lk1, "/dev/et1_ops other 8 0 y"], me)[0] or etwho_identity("A", [sa, lk1, "/dev/et0_ops other 8 0 y"], me)[0]:
        bad.append("arm A's other-login rule (another login on card 1 blocks; on card 0 it is the runner's start rule, not this read's)")
    w, c = etwho_identity("A", [sa, lk1], me)
    if c != {"ours_on_mgmt": 1, "ours_on_card": 2, "ours_off_card": 0, "other_on_card": 0, "other_off_card": 0}:
        bad.append(f"etwho_identity's counts {c}")
    if holder_card("/dev/et1_ops") != "1" or holder_card("lock:etsoc-shire1.lock") != "1" or holder_card("lock:x") != "?":
        bad.append("holder_card")
    if node_of("/dev/et1_ops") != ("1", "ops") or node_of("/dev/et10_mgmt") != ("10", "mgmt") or node_of("/dev/null") or node_of("/tmp/et1_ops"):
        bad.append("node_of")
    w, r = host_identity("A", [("1", "ops")], [1], {("1", "ops")})
    w0, r0 = host_identity("A", [("0", "ops")], [0], set())
    wn, rn = host_identity("A", [], [], set())
    wh, rh = host_identity("A", [("1", "ops")], [1], {("0", "ops")})
    if w or not r or not w0 or r0 or wn or rn or not wh:
        bad.append("host_identity")
    s = [{"t_ms": t, "board_w": 33.0 + (14.0 if 1000 <= t <= 3000 else 0.0)} for t in range(0, 4000, 100)]
    ok, rise, n = board_rise(s, (1000, 3000), 33.0)
    if not ok or abs(rise - 14.0) > 1e-9 or n != 21 or board_rise(s, (3500, 3900), 33.0)[0] or board_rise(s, (1000, 1150), 33.0)[0] or \
            board_rise(s, (1000, 3000), None)[0] or board_rise(s, None, 33.0)[0]:
        bad.append("board_rise")
    if not fresh(True, 100.0, 101.9) or fresh(True, 100.0, 102.0) or fresh(False, 100.0, 100.5) or fresh(True, None, 1.0):
        bad.append("fresh")
    if set(IDENT) != {"A"}:
        bad.append("an arm other than A")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E224A-IDENT SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
