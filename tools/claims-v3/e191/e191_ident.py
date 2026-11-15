#!/usr/bin/env python3
"""E191's kit (Q178, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): THE IDENTITY GATE of E191's dated
note 1 (8c8f825f), section 1, item 3, and the watch at every launch, in E190's kit note 1's form (tools/claims-v3/e190/e190_note1.py,
bff31df2, arm B's half, unchanged beside it). Python's own modules only (aifoundry1's system python3; the desk's /usr/bin/python3 -I -B).
Every number is note 1's, or the kit's reading stated before any E191 datum; none touches a scored number.

  (a) the start config read keeps its stderr: every 'PCIe target' line names /dev/et1_mgmt and every 'Physical device ID' line reads 1
      (a read with no such line fails: the card cannot be told), and its JSON reads minion_mv below 510 (card 1 read 499 or 500 in every
      committed read, card 0 519) and, a gate made stricter for safety after the verifier's nit 11 (fix-e191k), above 450 (a failed
      voltage read of 0 no longer passes "below 510"); TDP, threshold and clock are e191_common.config_ok's; power_state_name is never
      compared;
  (b) with the sampler running and before the smoke's first launch, et-who (counts by card, never a name): every holder line of our own
      login is on a /dev/et1_ node or lock:etsoc-shire1.lock, at least one of them on /dev/et1_mgmt (the sampler's), none on a /dev/et0_
      node or lock:etsoc-shire0.lock (this also shows no other session of ours holds card 0); and, E190's addition, the sampler's own open
      files (/proc/<pid>/fd, what et-who's fuser reads) hold /dev/et1_mgmt and no card 0 node;
  (c) every host process is watched while it runs (HostWatch, every 0.1 s): its stderr's device-layer block (both hosts print it when they
      open their ops node: 'PCIe target: /dev/et0_ops' and 'Physical device ID: 0' in every pass of E189's committed data on aifoundry3
      card 0) and the card nodes its process tree holds open or mapped. Another card named or held: the session stops after that process
      (the hosts have no stop file and a device process is never killed: it ends by its own budget, at most `timeout 10`); in the smoke
      each device-opening process must also have shown card 1;
  foreign_lines: the holder lines that stop a session before a launch: another login's on either card (E189's foreign(), kept: the runners
      count openers across both cards), ours on card 0 (never two sessions of ours on aifoundry1; nothing on card 0), ours on card 1's ops
      node while no host of ours runs (a stray host);
  etwho_unreadable (fix-e191k, the verifier's finding 3): et-who is read only when it exits 0 and answers with a holder line or its
      no-holder sentence ("No process holds an ET-SoC-1 device node or card lock."); anything else (its privileged helper refused: rc 1
      and nothing on stdout; an answer with neither) is UNREADABLE, which refuses before the first card command and stops before a
      pass: an unread holder rule is never read as "no holder".
    python3 -I -B tools/claims-v3/e191/e191_ident.py      the self-check, card 1's forms passing and card 0's refused (E191-IDENT SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import threading

DEV_DIR = "/dev"                 # where the cards' nodes are; the dry pass and the desk tests point it at a stand-in directory
CARD = "1"
MGMT, OPS = "/dev/et1_mgmt", "/dev/et1_ops"
PHYS_ID = 1
MV_BELOW = 510
MV_ABOVE = 450                   # fix-e191k (nit 11): a gate made stricter for safety; card 1 read 499-500, a failed read reads 0
LOCK_NAME = "etsoc-shire1.lock"
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
    """'' when the start config read names card 1 (note 1, item 3(a)); else why."""
    targets, ids = parse_ident(err_text)
    why = []
    if not targets:
        why.append("no 'PCIe target' line on the config read's stderr")
    elif any(t != (CARD, "mgmt") for t in targets):
        why.append("PCIe target " + ", ".join(sorted({f"/dev/et{c}_{k}" for c, k in targets})) + f", not {MGMT}")
    if not ids:
        why.append("no 'Physical device ID' line on the config read's stderr")
    elif any(i != PHYS_ID for i in ids):
        why.append(f"Physical device ID {sorted(set(ids))}, not {PHYS_ID}")
    mv = (j or {}).get("minion_mv")
    if not isinstance(mv, (int, float)) or isinstance(mv, bool) or mv >= MV_BELOW:
        why.append(f"minion_mv {mv}, not below {MV_BELOW} (card 1 read 499 or 500 in every committed read; card 0 519)")
    elif mv <= MV_ABOVE:
        why.append(f"minion_mv {mv}, not above {MV_ABOVE} (a failed voltage read; card 1 read 499 or 500 in every committed read)")
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
    """'' when et-who's answer can be read (rc 0, and a holder line or its no-holder sentence); else why (fix-e191k, finding 3)."""
    if rc != 0:
        return f"et-who unreadable (rc {rc}{', nothing on its stdout' if not [x for x in lines if x.strip()] else ''})"
    if not holder_rows(lines) and NO_HOLDER not in [x.strip() for x in lines]:
        return "et-who unreadable (rc 0, but neither a holder line nor its no-holder sentence)"
    return ""


def etwho_identity(lines, me):
    """Note 1, item 3(b): ('' or why, counts). Counts only: no login is ever written."""
    hold = holder_rows(lines)
    ours = [f for f in hold if f[1] == me]
    other = [f for f in hold if f[1] != me]
    counts = {"ours_on_mgmt": sum(1 for f in ours if f[0] == MGMT),
              "ours_on_card1": sum(1 for f in ours if holder_card(f[0]) == CARD),
              "ours_on_card0": sum(1 for f in ours if holder_card(f[0]) == "0"),
              "ours_elsewhere": sum(1 for f in ours if holder_card(f[0]) not in (CARD, "0")),
              "other_on_card1": sum(1 for f in other if holder_card(f[0]) == CARD),
              "other_on_card0": sum(1 for f in other if holder_card(f[0]) == "0")}
    why = []
    if counts["ours_on_mgmt"] < 1:
        why.append(f"no holder line of ours on {MGMT} (the sampler's) with the sampler running")
    if counts["ours_on_card0"]:
        why.append(f"{counts['ours_on_card0']} holder line(s) of ours on card 0 (a /dev/et0_ node or lock:etsoc-shire0.lock)")
    if counts["ours_elsewhere"]:
        why.append(f"{counts['ours_elsewhere']} holder line(s) of ours off card 1")
    if counts["other_on_card1"] or counts["other_on_card0"]:
        why.append(f"{counts['other_on_card1'] + counts['other_on_card0']} holder line(s) of another login (either card)")
    return "; ".join(why), counts


def foreign_lines(lines, me, host_running=False):
    """The holder lines that stop a session before a launch (the module docstring): ('' or why, counts)."""
    hold = holder_rows(lines)
    other = [f for f in hold if f[1] != me]
    ours0 = [f for f in hold if f[1] == me and holder_card(f[0]) != CARD]
    ops = [f for f in hold if f[1] == me and f[0] == OPS]
    why = []
    if other:
        why.append(f"{len(other)} holder line(s) of another login")
    if ours0:
        why.append(f"{len(ours0)} holder line(s) of ours off card 1 (card 0's nodes or lock)")
    if ops and not host_running:
        why.append(f"{len(ops)} holder line(s) of ours on {OPS} while no host of ours runs")
    return "; ".join(why), {"other": len(other), "ours_off_card1": len(ours0), "ours_on_ops": len(ops)}


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
    """E190's addition to (b): '' when the sampler's own open nodes hold /dev/et1_mgmt and nothing of another card; else why."""
    names = sorted(f"/dev/et{c}_{k}" for c, k in nodes)
    why = []
    if (CARD, "mgmt") not in nodes:
        why.append(f"the sampler does not hold {MGMT} (it holds {names or 'no card node'})")
    off = [n for n in names if not n.startswith(f"/dev/et{CARD}_")]
    if off:
        why.append(f"the sampler holds another card's node(s) {off}")
    return "; ".join(why)


def host_identity(targets, ids, nodes):
    """(wrong, right) for one host process: wrong lists everything that names or holds another card; right is True when card 1 was named
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
    c1, c0 = BLOCK.format(c=1, k="mgmt"), BLOCK.format(c=0, k="mgmt")
    if parse_ident(c1) != ([("1", "mgmt")], [1]):
        bad.append("parse_ident on card 1's block")
    ok = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 499, "power_state_name": "low_power"}
    if config_identity(ok, c1) or config_identity(dict(ok, minion_mv=500, power_state_name="managed_power"), c1):
        bad.append("card 1's read (499 and 500 mV, either power state) refused")
    for name, j, e in (("card 0's block and 519 mV", dict(ok, minion_mv=519), c0), ("card 0's block", ok, c0),
                       ("519 mV on card 1's block", dict(ok, minion_mv=519), c1), ("no block", ok, ""),
                       ("no minion_mv", dict(ok, minion_mv=None), c1), ("both cards named", ok, c1 + c0),
                       ("510 mV", dict(ok, minion_mv=510), c1), ("an ops target", ok, BLOCK.format(c=1, k="ops")),
                       ("0 mV (a failed voltage read)", dict(ok, minion_mv=0), c1), ("450 mV", dict(ok, minion_mv=450), c1)):
        if not config_identity(j, e):
            bad.append(f"the config identity passed {name}")
    if config_identity(dict(ok, minion_mv=451), c1):
        bad.append("451 mV on card 1's block refused")
    # et-who's readability (fix-e191k, finding 3): rc 0 with a holder line or the no-holder sentence reads; nothing else does
    for name, rc, lines, want in (("the no-holder sentence", 0, [NO_HOLDER], ""), ("a holder line", 0, ["/dev/et1_mgmt  us 1 0 ettelem"], ""),
                                  ("a refusal (rc 1, no stdout)", 1, [], "x"), ("rc 2 with a holder line", 2, ["/dev/et1_mgmt us 1 0 e"], "x"),
                                  ("rc 0 and nothing", 0, [], "x"), ("rc 0 and other words", 0, ["et-who: its helper refused (double)"], "x"),
                                  ("rc 0 and a device name with no holder fields", 0, ["/dev/et1_mgmt"], "x")):
        if bool(etwho_unreadable(rc, lines)) != bool(want):
            bad.append(f"etwho_unreadable on {name}")
    me = "us"
    sam = "/dev/et1_mgmt  us 100 00:05 ettelem"
    lk1 = "lock:etsoc-shire1.lock us 99 00:06 python3"
    if etwho_identity([sam, lk1], me)[0]:
        bad.append("card 1's holder read refused")
    for name, lines in (("no sampler line", [lk1]), ("the sampler on card 0", [sam.replace("et1", "et0"), lk1]),
                        ("ours on card 0's ops", [sam, lk1, "/dev/et0_ops us 7 0 x"]),
                        ("ours on card 0's lock", [sam, lk1, "lock:etsoc-shire0.lock us 7 0 x"]),
                        ("another login on card 1", [sam, lk1, "/dev/et1_ops other 8 0 y"]),
                        ("another login on card 0", [sam, lk1, "/dev/et0_ops other 8 0 y"])):
        if not etwho_identity(lines, me)[0]:
            bad.append(f"the holder read passed {name}")
    if foreign_lines([sam, lk1], me)[0] or not foreign_lines([sam, lk1, "/dev/et1_ops us 5 0 h"], me)[0] or \
            foreign_lines([sam, lk1, "/dev/et1_ops us 5 0 h"], me, host_running=True)[0] or \
            not foreign_lines([sam, "/dev/et0_mgmt us 6 0 e"], me)[0] or not foreign_lines(["/dev/et0_ops other 9 0 z"], me)[0] or \
            foreign_lines(["No process holds an ET-SoC-1 device node or card lock."], me)[0]:
        bad.append("foreign_lines")
    if node_of("/dev/et1_ops") != ("1", "ops") or node_of("/dev/et10_mgmt") != ("10", "mgmt") or node_of("/dev/null") or node_of("/tmp/et1_ops"):
        bad.append("node_of")
    if sampler_identity({("1", "mgmt")}) or not sampler_identity({("0", "mgmt")}) or not sampler_identity(set()) or \
            not sampler_identity({("1", "mgmt"), ("0", "mgmt")}):
        bad.append("sampler_identity")
    w, r = host_identity([("1", "ops")], [1], {("1", "ops")})
    w0, r0 = host_identity([("0", "ops")], [0], set())
    wn, rn = host_identity([], [], set())
    wh, rh = host_identity([("1", "ops")], [1], {("0", "ops")})
    if w or not r or not w0 or r0 or wn or rn or not wh:
        bad.append("host_identity")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E191-IDENT SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
