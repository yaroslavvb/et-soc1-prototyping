#!/usr/bin/env python3
"""1117-mmsweep2: the card's identity, read before any launch and watched at every launch (Python's own modules only). The
form is E190's kit note 1 (tools/claims-v3/e190/e190_note1.py in the public lab repo), for three cards:
  * the start config read keeps its stderr, where the device layer names its PCIe target and physical device ID: the card's
    mgmt node and ID; on aifoundry1 also minion_mv (card 1 reads 499-500 mV, card 0 519 mV: below 510 on card 1, at or above
    on card 0);
  * with the sampler running and before the smoke: et-who (counts by card, never a login) shows a line of ours on the card's
    mgmt node, none of ours off the card, no other login on the card (aifoundry2: on any card); and the sampler's own open
    files hold the card's mgmt node and no other card's;
  * every host process is watched while it runs (HostWatch, every 0.1 s): its stderr's identity block and the card nodes its
    process tree holds open or mapped. Another card named or held: on_wrong() at once (the runner touches the hosts' stop
    file there and the session stops);
  * the sampler's freshness: alive with a sample less than SAMPLE_FRESH_S old.
    python3 -I -B src/mms_ident.py        the self-check (MMS-IDENT SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import statistics
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mms_common as C  # noqa: E402

DEV_DIR = "/dev"
WATCH_EVERY_S = 0.1
RISE_MIN_SAMPLES = 3
RE_TARGET = re.compile(r"^PCIe target:\s+/dev/et(\d+)_(ops|mgmt)\b")
RE_PHYS = re.compile(r"^Physical device ID:\s+(\d+)\b")
RE_LOCK = re.compile(r"^lock:etsoc-shire(\d+)\.lock$")


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


def config_identity(card, j, err_text):
    """'' when the config read names the card (every PCIe target its mgmt node, every physical device ID its own, and the
    minion_mv rule on aifoundry1), else why. A read with no such line fails: the card cannot be told."""
    c = C.CARDS[card]["card"]
    targets, ids = parse_ident(err_text)
    why = []
    if not targets:
        why.append("no 'PCIe target' line on the config read's stderr")
    elif any(t != (c, "mgmt") for t in targets):
        why.append("PCIe target " + ", ".join(sorted({f"/dev/et{x}_{k}" for x, k in targets})) + f", not {C.node(card, 'mgmt')}")
    if not ids:
        why.append("no 'Physical device ID' line on the config read's stderr")
    elif any(str(i) != c for i in ids):
        why.append(f"Physical device ID {sorted(set(ids))}, not {c}")
    mv = C.CARDS[card]["mv_rule"]
    if mv is not None and not C.rule_ok(mv, (j or {}).get("minion_mv")):
        why.append(f"minion_mv {(j or {}).get('minion_mv')}, not {mv[0]} {mv[1]} (aifoundry1: card 1 reads 499-500, card 0 519)")
    return "; ".join(why)


def holder_card(field):
    m = re.match(r"^/dev/et(\d+)_", field)
    if m:
        return m.group(1)
    m = RE_LOCK.match(field)
    return m.group(1) if m else "?"


def holder_lines(lines):
    return [ln.split() for ln in lines if (ln.startswith("/dev/et") or ln.startswith("lock:")) and len(ln.split()) > 1]


def etwho_block(card, lines, me):
    """Before the first card command, the session holding the card's lock: '' when nothing blocks, else why (counts only).
    Another login on the card (aifoundry2: on any card) blocks; any node line of ours blocks (no device of ours may be open
    before the session opens one); a lock line of ours on another card blocks (never two of our sessions on aifoundry1); our
    own lock line on this card is the session's; another login on the other card of aifoundry1 does not block."""
    c = C.CARDS[card]["card"]
    hold = holder_lines(lines)
    one_card_box = C.OTHER_CARD_ON_BOX[card] is None
    n_other = sum(1 for f in hold if f[1] != me and (one_card_box or holder_card(f[0]) == c))
    n_ours_node = sum(1 for f in hold if f[1] == me and f[0].startswith("/dev/"))
    n_ours_lock = sum(1 for f in hold if f[1] == me and f[0].startswith("lock:") and holder_card(f[0]) != c)
    why = []
    if n_other:
        why.append(f"{n_other} holder line(s) of another login on the card")
    if n_ours_node:
        why.append(f"{n_ours_node} node line(s) of ours (a device of ours is open already)")
    if n_ours_lock:
        why.append(f"{n_ours_lock} lock line(s) of ours on another card (never two of our sessions on one box)")
    return "; ".join(why)


def etwho_identity(card, lines, me):
    """With the sampler running, before the smoke: ('' or why, counts). A line of ours on the card's mgmt node (the sampler's),
    none of ours off the card, no other login on the card (aifoundry2: on any card)."""
    c = C.CARDS[card]["card"]
    mgmt = C.node(card, "mgmt")
    hold = holder_lines(lines)
    ours = [f for f in hold if f[1] == me]
    other = [f for f in hold if f[1] != me]
    counts = {"ours_on_mgmt": sum(1 for f in ours if f[0] == mgmt), "ours_on_card": sum(1 for f in ours if holder_card(f[0]) == c),
              "ours_off_card": sum(1 for f in ours if holder_card(f[0]) != c),
              "other_on_card": sum(1 for f in other if holder_card(f[0]) == c),
              "other_off_card": sum(1 for f in other if holder_card(f[0]) != c)}
    why = []
    if counts["ours_on_mgmt"] < 1:
        why.append(f"no holder line of ours on {mgmt} (the sampler's) with the sampler running")
    if counts["ours_off_card"]:
        why.append(f"{counts['ours_off_card']} holder line(s) of ours off card {c}")
    one_card_box = C.OTHER_CARD_ON_BOX[card] is None
    n = counts["other_on_card"] + (counts["other_off_card"] if one_card_box else 0)
    if n:
        why.append(f"{n} holder line(s) of another login on the card")
    return "; ".join(why), counts


def node_of(path, dev_dir=None):
    d = dev_dir or DEV_DIR
    d = "/dev" if d == "/dev" else os.path.realpath(d)
    if not path or not path.startswith(d + "/"):
        return None
    m = re.match(r"^et(\d+)_(ops|mgmt)$", path[len(d) + 1:])
    return (m.group(1), m.group(2)) if m else None


def descendants(pid):
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
        except (OSError, ValueError):
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


def host_identity(card, targets, ids, nodes):
    """(wrong, right): wrong lists everything that names or holds another card; right: the card itself was named or held."""
    c = C.CARDS[card]["card"]
    wrong = sorted({f"stderr PCIe target /dev/et{x}_{k}" for x, k in targets if x != c}
                   | {f"stderr Physical device ID {i}" for i in ids if str(i) != c}
                   | {f"holds /dev/et{x}_{k}" for x, k in nodes if x != c})
    right = any(x == c for x, k in targets) or any(str(i) == c for i in ids) or any(x == c for x, k in nodes)
    return wrong, right


class HostWatch(threading.Thread):
    """Watches one host process while it runs (every WATCH_EVERY_S): the new text of its stderr file and the card nodes its
    process tree holds. The first sight of another card calls on_wrong(why) once, at once."""

    def __init__(self, card, pid, err_path, dev_dir=None, on_wrong=None):
        super().__init__(daemon=True)
        self.card, self.pid, self.err_path, self.dev_dir, self.on_wrong = card, pid, err_path, dev_dir, on_wrong
        self.text, self.pos, self.nodes, self.polls, self.tripped = "", 0, set(), 0, None
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
        wrong, _ = host_identity(self.card, targets, ids, self.nodes)
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
        self.poll()

    def result(self):
        targets, ids = parse_ident(self.text)
        wrong, right = host_identity(self.card, targets, ids, self.nodes)
        return {"stderr_targets": sorted({f"/dev/et{x}_{k}" for x, k in targets}), "stderr_ids": sorted(set(ids)),
                "nodes_held": sorted(f"/dev/et{x}_{k}" for x, k in self.nodes), "wrong": wrong, "right": right,
                "polls": self.polls, "tripped": self.tripped}


def board_rise(samples, window_ms, rest_w):
    """(ok, rise W or None, n): the median board W of the samples inside window_ms less rest_w; ok when n >= 3 and the rise is
    at least C.RISE_MIN_W."""
    if not window_ms or rest_w is None:
        return False, None, 0
    lo, hi = window_ms
    bw = [s.get("board_w") for s in samples if s.get("board_w") is not None and lo <= (s.get("t_ms") or 0) <= hi]
    if len(bw) < RISE_MIN_SAMPLES:
        return False, None, len(bw)
    rise = statistics.median(bw) - rest_w
    return rise >= C.RISE_MIN_W, round(rise, 3), len(bw)


def fresh(alive, last_rx, now=None):
    now = time.time() if now is None else now
    return bool(alive) and last_rx is not None and (now - last_rx) < C.SAMPLE_FRESH_S


BLOCK = ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:1]: \nPCIe target:                         /dev/et{c}_{k}       \n"
         "PCIBUS device name:                  0000:02:00.0        \n"
         "Physical device ID:                  {c}                    (0x{c})\nTDP (W):                             65\n")


def selfcheck():
    bad = []
    c1, c0 = BLOCK.format(c=1, k="mgmt"), BLOCK.format(c=0, k="mgmt")
    if parse_ident(c1) != ([("1", "mgmt")], [1]):
        bad.append("parse_ident")
    j1 = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 499}
    j0 = dict(j1, minion_mv=519)
    if config_identity("a1c1", j1, c1) or not config_identity("a1c1", j0, c1) or not config_identity("a1c1", j1, c0) \
            or not config_identity("a1c1", j1, "") or not config_identity("a1c1", j1, c1 + c0):
        bad.append("card 1's config identity")
    if config_identity("a1c0", j0, c0) or not config_identity("a1c0", j1, c0) or not config_identity("a1c0", j0, c1):
        bad.append("card 0's config identity (aifoundry1)")
    if config_identity("a2c0", j0, c0) or config_identity("a2c0", j1, c0) or not config_identity("a2c0", j0, c1):
        bad.append("aifoundry2's config identity")
    me = "us"
    s1 = "/dev/et1_mgmt us 100 00:05 sampler"
    if etwho_identity("a1c1", [s1], me)[0] or not etwho_identity("a1c1", [], me)[0] \
            or not etwho_identity("a1c1", [s1, "/dev/et0_ops us 7 0 x"], me)[0] \
            or etwho_identity("a1c1", [s1, "/dev/et0_ops other 8 0 y"], me)[0] \
            or not etwho_identity("a1c1", [s1, "/dev/et1_ops other 8 0 y"], me)[0]:
        bad.append("card 1's holder read")
    s0 = "/dev/et0_mgmt us 100 00:05 sampler"
    if etwho_identity("a1c0", [s0], me)[0] or not etwho_identity("a1c0", [s0, "lock:etsoc-shire1.lock us 9 0 z"], me)[0] \
            or etwho_identity("a1c0", [s0, "/dev/et1_ops other 8 0 y"], me)[0]:
        bad.append("card 0's holder read (aifoundry1)")
    if etwho_identity("a2c0", [s0], me)[0] or not etwho_identity("a2c0", [s0, "/dev/et0_ops other 8 0 y"], me)[0]:
        bad.append("aifoundry2's holder read")
    own_lock1 = "lock:etsoc-shire1.lock us 99 00:01 python3"
    if etwho_block("a1c1", ["/dev/et0_ops other 8 0 y", own_lock1], me) or not etwho_block("a1c1", ["/dev/et1_ops other 8 0 y"], me) \
            or not etwho_block("a1c1", ["/dev/et0_ops us 8 0 y", own_lock1], me) \
            or not etwho_block("a1c1", [own_lock1, "lock:etsoc-shire0.lock us 98 00:01 python3"], me) \
            or not etwho_block("a2c0", ["/dev/et0_ops other 8 0 y"], me) or etwho_block("a2c0", ["lock:etsoc-shire0.lock us 9 0 p"], me) \
            or etwho_block("a2c0", [], me) or not etwho_block("a1c0", ["/dev/et1_mgmt us 5 0 s"], me):
        bad.append("the holder block before the first card command")
    if node_of("/dev/et1_ops") != ("1", "ops") or node_of("/dev/et10_mgmt") != ("10", "mgmt") or node_of("/dev/null") \
            or node_of("/tmp/et1_ops"):
        bad.append("node_of")
    w, r = host_identity("a1c1", [("1", "ops")], [1], {("1", "ops")})
    w0, r0 = host_identity("a1c1", [("0", "ops")], [0], set())
    wn, rn = host_identity("a1c1", [], [], set())
    wh, rh = host_identity("a1c0", [("0", "ops")], [0], {("1", "ops")})
    if w or not r or not w0 or r0 or wn or rn or not wh:
        bad.append("host_identity")
    s = [{"t_ms": t, "board_w": 33.0 + (14.0 if 1000 <= t <= 3000 else 0.0)} for t in range(0, 4000, 100)]
    ok, rise, n = board_rise(s, (1000, 3000), 33.0)
    if not ok or abs(rise - 14.0) > 1e-9 or n != 21 or board_rise(s, (3500, 3900), 33.0)[0] or board_rise(s, (1000, 1150), 33.0)[0]:
        bad.append("board_rise")
    if not fresh(True, 100.0, 101.9) or fresh(True, 100.0, 102.0) or fresh(False, 100.0, 100.5) or fresh(True, None, 1.0):
        bad.append("fresh")
    return bad


if __name__ == "__main__":
    b = selfcheck()
    print("MMS-IDENT SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
