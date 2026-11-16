#!/usr/bin/env python3
"""E194's kit (Q183, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): THE IDENTITY GATE and the watch at
every launch, for aifoundry2's card 0. E191's identity module (tools/claims-v3/e191/e191_ident.py, eb1ac923, unchanged beside it; E190's
kit note 1's form) ported back to the box's own card: on aifoundry2 there is ONE card, so the gate's work is to show that every process
reached card 0 through its own nodes and that nothing names or holds a node of any other card (a second card's forms, as aifoundry1's
card 1 prints them, are refused), or that the card cannot be told (a missing node's forms: no identity block, no node held). Python's own
modules only (/usr/bin/python3 -I -B). Every number is the kit's reading stated before any E194 datum; none touches a scored number.

  (a) the start config read keeps its stderr: every 'PCIe target' line names /dev/et0_mgmt and every 'Physical device ID' line reads 0
      (a read with no such line fails: the card cannot be told; E190 arm A's committed read on this card printed /dev/et0_mgmt, ID 0),
      and its JSON reads minion_mv a number strictly between 450 and 600 (this card read 519 at rest in E190 arm A, at both ends; a
      failed voltage read of 0 and a voltage at the 800 MHz point at "rest" are refused; on a one-card box minion_mv tells no card from
      another, so it is a sanity bound, not an identity); TDP, threshold and clock are e194_common.config_ok's; power_state_name is never
      compared;
  (b) with the sampler running and before the smoke's first launch, et-who (counts by card, never a name): every holder line of our own
      login is on a /dev/et0_ node or lock:etsoc-shire0.lock, at least one of them on /dev/et0_mgmt (the sampler's), none elsewhere (a
      line of ours on any other card's node or lock refuses: a second card's form); no line of another login anywhere; and the sampler's
      own open files (/proc/<pid>/fd, what et-who's fuser reads) hold /dev/et0_mgmt and no other card's node;
  (c) every host process is watched while it runs (HostWatch, every 0.1 s): its stderr's device-layer block and the card nodes its process
      tree holds open or mapped. Another card named or held: the session stops after that process; in the smoke each device-opening
      process must also have shown card 0 (its own ops node, by name or held);
  foreign_lines: the holder lines that stop a session before a launch: another login's anywhere; ours off card 0; ours on /dev/et0_ops
      while no host of ours runs (a stray host); ours on /dev/et0_mgmt while no sampler of ours runs (a stray reader: on this box our own
      live collector's `ettelem temp`, which the runner re-reads with the lock held before its first card command, KIT.md section 4);
  etwho_unreadable (E191's fix-e191k): et-who is read only when it exits 0 and answers with a holder line or its no-holder sentence;
      anything else is UNREADABLE, which refuses before the first card command and stops before a pass.
    python3 -I -B tools/claims-v3/e194/e194_ident.py      the self-check, card 0's forms passing, a second card's and a missing node's refused
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import threading

DEV_DIR = "/dev"                 # where the card's nodes are; the dry pass and the desk tests point it at a stand-in directory
CARD = "0"
MGMT, OPS = "/dev/et0_mgmt", "/dev/et0_ops"
PHYS_ID = 0
MV_ABOVE, MV_BELOW = 450, 600    # e194_common's; this card read 519 at rest (E190 arm A, both ends)
LOCK_NAME = "etsoc-shire0.lock"
WATCH_EVERY_S = 0.1
NO_HOLDER = "No process holds an ET-SoC-1 device node or card lock."     # et-who's (et-holders') own sentence when nothing is held

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


def config_identity(j, err_text):
    """'' when the start config read names card 0 alone ((a) above); else why."""
    targets, ids = parse_ident(err_text)
    why = []
    if not targets:
        why.append("no 'PCIe target' line on the config read's stderr (the card cannot be told)")
    elif any(t != (CARD, "mgmt") for t in targets):
        why.append("PCIe target " + ", ".join(sorted({f"/dev/et{c}_{k}" for c, k in targets})) + f", not {MGMT} alone")
    if not ids:
        why.append("no 'Physical device ID' line on the config read's stderr")
    elif any(i != PHYS_ID for i in ids):
        why.append(f"Physical device ID {sorted(set(ids))}, not {PHYS_ID} alone")
    mv = (j or {}).get("minion_mv")
    if not isinstance(mv, (int, float)) or isinstance(mv, bool) or not MV_ABOVE < mv < MV_BELOW:
        why.append(f"minion_mv {mv}, not between {MV_ABOVE} and {MV_BELOW} (this card read 519 at rest; a failed read reads 0)")
    return "; ".join(why)


def holder_card(field):
    """The card a holder line's first field names (/dev/etN_..., lock:etsoc-shireN.lock), or '?'."""
    m = re.match(r"^/dev/et(\d+)_", field)
    if m:
        return m.group(1)
    m = RE_LOCK.match(field)
    return m.group(1) if m else "?"


def holder_rows(lines):
    return [ln.split() for ln in lines if (ln.startswith("/dev/et") or ln.startswith("lock:")) and len(ln.split()) > 1]


def etwho_unreadable(rc, lines):
    """'' when et-who's answer can be read (rc 0, and a holder line or its no-holder sentence); else why (E191's fix-e191k)."""
    if rc != 0:
        return f"et-who unreadable (rc {rc}{', nothing on its stdout' if not [x for x in lines if x.strip()] else ''})"
    if not holder_rows(lines) and NO_HOLDER not in [x.strip() for x in lines]:
        return "et-who unreadable (rc 0, but neither a holder line nor its no-holder sentence)"
    return ""


def etwho_identity(lines, me):
    """(b) above: ('' or why, counts). Counts only: no login is ever written."""
    hold = holder_rows(lines)
    ours = [f for f in hold if f[1] == me]
    other = [f for f in hold if f[1] != me]
    counts = {"ours_on_mgmt": sum(1 for f in ours if f[0] == MGMT),
              "ours_on_card0": sum(1 for f in ours if holder_card(f[0]) == CARD),
              "ours_off_card0": sum(1 for f in ours if holder_card(f[0]) != CARD),
              "other_on_card0": sum(1 for f in other if holder_card(f[0]) == CARD),
              "other_off_card0": sum(1 for f in other if holder_card(f[0]) != CARD)}
    why = []
    if counts["ours_on_mgmt"] < 1:
        why.append(f"no holder line of ours on {MGMT} (the sampler's) with the sampler running")
    if counts["ours_off_card0"]:
        why.append(f"{counts['ours_off_card0']} holder line(s) of ours off card 0 (another card's node or lock)")
    if counts["other_on_card0"] or counts["other_off_card0"]:
        why.append(f"{counts['other_on_card0'] + counts['other_off_card0']} holder line(s) of another login")
    return "; ".join(why), counts


def foreign_lines(lines, me, host_running=False, sampler_running=False):
    """The holder lines that stop a session before a launch (the module docstring): ('' or why, counts, transient). transient is True
    when every reason is a line of ours on /dev/et0_mgmt while no sampler of ours runs (a stray reader: our live collector's read in
    flight), which the runner may re-read with the card's lock held before its first card command."""
    hold = holder_rows(lines)
    other = [f for f in hold if f[1] != me]
    off = [f for f in hold if f[1] == me and holder_card(f[0]) != CARD]
    ops = [f for f in hold if f[1] == me and f[0] == OPS]
    mgmt = [f for f in hold if f[1] == me and f[0] == MGMT]
    why, hard = [], False
    if other:
        why.append(f"{len(other)} holder line(s) of another login")
        hard = True
    if off:
        why.append(f"{len(off)} holder line(s) of ours off card 0 (another card's node or lock)")
        hard = True
    if ops and not host_running:
        why.append(f"{len(ops)} holder line(s) of ours on {OPS} while no host of ours runs")
        hard = True
    if mgmt and not sampler_running:
        why.append(f"{len(mgmt)} holder line(s) of ours on {MGMT} while no sampler of ours runs")
    counts = {"other": len(other), "ours_off_card0": len(off), "ours_on_ops": len(ops), "ours_on_mgmt": len(mgmt)}
    return "; ".join(why), counts, bool(why) and not hard


def node_of(path, dev_dir=None):
    """(card, kind) when path is a card node under dev_dir (/dev/etN_ops or /dev/etN_mgmt there), else None."""
    d = dev_dir or DEV_DIR
    d = os.path.realpath(d) if d != "/dev" else "/dev"
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


def sampler_identity(nodes):
    """'' when the sampler's own open nodes hold /dev/et0_mgmt and nothing of another card; else why."""
    names = sorted(f"/dev/et{c}_{k}" for c, k in nodes)
    why = []
    if (CARD, "mgmt") not in nodes:
        why.append(f"the sampler does not hold {MGMT} (it holds {names or 'no card node'})")
    off = [n for n in names if not n.startswith(f"/dev/et{CARD}_")]
    if off:
        why.append(f"the sampler holds another card's node(s) {off}")
    return "; ".join(why)


def host_identity(targets, ids, nodes):
    """(wrong, right) for one host process: wrong lists everything that names or holds another card; right is True when card 0 was named
    (a PCIe target or physical device ID on its stderr) or held (a node in its process tree)."""
    wrong = sorted({f"stderr PCIe target /dev/et{x}_{k}" for x, k in targets if x != CARD} |
                   {f"stderr Physical device ID {i}" for i in ids if str(i) != CARD} |
                   {f"holds /dev/et{x}_{k}" for x, k in nodes if x != CARD})
    right = any(x == CARD for x, k in targets) or any(str(i) == CARD for i in ids) or any(x == CARD for x, k in nodes)
    return wrong, right


class HostWatch(threading.Thread):
    """Watches one host process while it runs (every WATCH_EVERY_S): the new text of its stderr file for the device layer's block, and
    the card nodes its process tree (the `timeout` process and its children) holds open or mapped. The first sight of another card calls
    on_wrong(why) once, at once (the runner then lets nothing further start)."""

    def __init__(self, pid, err_path, dev_dir=None, on_wrong=None):
        super().__init__(daemon=True)
        self.pid, self.err_path, self.dev_dir, self.on_wrong = pid, err_path, dev_dir, on_wrong
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
        wrong, _ = host_identity(targets, ids, self.nodes)
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
        wrong, right = host_identity(targets, ids, self.nodes)
        return {"stderr_targets": sorted({f"/dev/et{c}_{k}" for c, k in targets}), "stderr_ids": sorted(set(ids)),
                "nodes_held": sorted(f"/dev/et{c}_{k}" for c, k in self.nodes), "wrong": wrong, "right": right, "polls": self.polls,
                "tripped": self.tripped}


BLOCK = ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:1]: \nPCIe target:                                               /dev/et{c}_{k}       \n"
         "PCIBUS device name:                                        0000:02:00.0        \n"
         "Physical device ID:                                        {c}                    (0x{c})\nTDP (W):                                                   65\n")


def selfcheck():
    bad = []
    c0, c1 = BLOCK.format(c=0, k="mgmt"), BLOCK.format(c=1, k="mgmt")
    if parse_ident(c0) != ([("0", "mgmt")], [0]):
        bad.append("parse_ident on card 0's block")
    ok = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 519, "power_state_name": "low_power"}
    for name, j in (("519 mV", ok), ("518 mV, managed_power", dict(ok, minion_mv=518, power_state_name="managed_power")),
                    ("523 mV", dict(ok, minion_mv=523)), ("451 mV", dict(ok, minion_mv=451)), ("599 mV", dict(ok, minion_mv=599))):
        if config_identity(j, c0):
            bad.append(f"card 0's read refused ({name})")
    for name, j, e in (("a second card's block (card 1, 499 mV)", dict(ok, minion_mv=499), c1), ("a second card's block", ok, c1),
                       ("no block (a missing node)", ok, ""), ("both cards named", ok, c0 + c1), ("an ops target", ok, BLOCK.format(c=0, k="ops")),
                       ("no minion_mv", dict(ok, minion_mv=None), c0), ("0 mV (a failed voltage read)", dict(ok, minion_mv=0), c0),
                       ("450 mV", dict(ok, minion_mv=450), c0), ("600 mV", dict(ok, minion_mv=600), c0),
                       ("619 mV (the 800 MHz point)", dict(ok, minion_mv=619), c0), ("a bool for minion_mv", dict(ok, minion_mv=True), c0),
                       ("card 10's block", ok, BLOCK.format(c=10, k="mgmt"))):
        if not config_identity(j, e):
            bad.append(f"the config identity passed {name}")
    for name, rc, lines, want in (("the no-holder sentence", 0, [NO_HOLDER], ""), ("a holder line", 0, ["/dev/et0_mgmt  us 1 0 ettelem"], ""),
                                  ("a refusal (rc 1, no stdout)", 1, [], "x"), ("rc 2 with a holder line", 2, ["/dev/et0_mgmt us 1 0 e"], "x"),
                                  ("rc 0 and nothing", 0, [], "x"), ("rc 0 and other words", 0, ["et-who: its helper refused (double)"], "x"),
                                  ("rc 0 and a device name with no holder fields", 0, ["/dev/et0_mgmt"], "x")):
        if bool(etwho_unreadable(rc, lines)) != bool(want):
            bad.append(f"etwho_unreadable on {name}")
    me = "us"
    sam = "/dev/et0_mgmt  us 100 00:05 ettelem"
    lk0 = "lock:etsoc-shire0.lock us 99 00:06 python3"
    if etwho_identity([sam, lk0], me)[0]:
        bad.append("card 0's holder read refused")
    for name, lines in (("no sampler line", [lk0]), ("the sampler on a second card", [sam.replace("et0", "et1"), lk0]),
                        ("ours on a second card's ops", [sam, lk0, "/dev/et1_ops us 7 0 x"]),
                        ("ours on a second card's lock", [sam, lk0, "lock:etsoc-shire1.lock us 7 0 x"]),
                        ("another login on card 0", [sam, lk0, "/dev/et0_ops other 8 0 y"]),
                        ("another login on a second card", [sam, lk0, "/dev/et1_ops other 8 0 y"])):
        if not etwho_identity(lines, me)[0]:
            bad.append(f"the holder read passed {name}")
    f0 = foreign_lines([lk0], me)
    f1 = foreign_lines([lk0, "/dev/et0_ops us 5 0 h"], me)
    f2 = foreign_lines([lk0, "/dev/et0_ops us 5 0 h"], me, host_running=True)
    f3 = foreign_lines([lk0, "/dev/et1_mgmt us 6 0 e"], me)
    f4 = foreign_lines(["/dev/et0_ops other 9 0 z"], me)
    f5 = foreign_lines([NO_HOLDER], me)
    f6 = foreign_lines([lk0, "/dev/et0_mgmt us 7 0 ettelem"], me)
    f7 = foreign_lines([lk0, sam], me, sampler_running=True)
    f8 = foreign_lines([lk0, "/dev/et0_mgmt us 7 0 ettelem", "/dev/et0_ops other 9 0 z"], me)
    if f0[0] or not f1[0] or f1[2] or f2[0] or not f3[0] or f3[2] or not f4[0] or f4[2] or f5[0] or not f6[0] or not f6[2] or f7[0] \
            or not f8[0] or f8[2]:
        bad.append(f"foreign_lines {[f0, f1, f2, f3, f4, f5, f6, f7, f8]}")
    if node_of("/dev/et0_ops") != ("0", "ops") or node_of("/dev/et10_mgmt") != ("10", "mgmt") or node_of("/dev/null") or node_of("/tmp/et0_ops"):
        bad.append("node_of")
    if sampler_identity({("0", "mgmt")}) or not sampler_identity({("1", "mgmt")}) or not sampler_identity(set()) or \
            not sampler_identity({("0", "mgmt"), ("1", "mgmt")}):
        bad.append("sampler_identity")
    w, r = host_identity([("0", "ops")], [0], {("0", "ops")})
    w1, r1 = host_identity([("1", "ops")], [1], set())
    wn, rn = host_identity([], [], set())
    wh, rh = host_identity([("0", "ops")], [0], {("1", "ops")})
    if w or not r or not w1 or r1 or wn or rn or not wh:
        bad.append("host_identity")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E194-IDENT SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
