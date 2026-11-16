#!/usr/bin/env python3
"""E199's kit (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE IDENTITY GATE on aifoundry1 card 1 (E199.md section 3:
E191's dated note 1, 8c8f825f, section 1 item 3, unchanged), read by E191's own module tools/claims-v3/e191/e191_ident.py, UNCHANGED and
imported from beside this file at its pin in SHA256SUMS-e191-kit (3fabb603...; session_e199.sh checks it before anything). This file adds
only what E199's wrapper and gate need around it:
  - config_json: the config read's JSON object from `ettelem config`'s stdout once aifoundry1's runtime lines ("Opening device <n>" with
    its newline, wherever it fell: E191's kit note 2, 2d0fe517, its RUNTIME_LINE and drop_runtime, re-written here because
    e191_common_v2.py imports E191's whole plan) are dropped: the LAST remaining line that begins with "{" and parses as an object;
  - config_gate (the gate (a)): every runtime line dropped names device 1 ("Opening device 1"; since fix-e199, verify-e199 F5: a line
    naming another device is refused, as E170's real card-0 read prints "Opening device 0"); the JSON reads TDP 65 W, threshold 65 C and
    600 MHz (E191's CONFIG_LINE) and e191_ident.config_identity
    passes (every 'PCIe target' line on the read's stderr names /dev/et1_mgmt, every 'Physical device ID' line reads 1, minion_mv in
    (450, 510)); power_state_name is never compared;
  - etwho_b (the gate (b)): with the sampler running and before the smoke's first launch, et-who (its plain form, rc 0, read only when it
    answers: e191_ident.etwho_unreadable) gives every holder line of ours on card 1, at least one on /dev/et1_mgmt, none on card 0 and
    none of another login (e191_ident.etwho_identity, counts by card, never a name), and the sampler's own open files hold /dev/et1_mgmt and
    nothing of card 0 (e191_ident.sampler_identity on e191_ident.proc_nodes).
    python3 -I -B ident_e199.py config <stdout file> <stderr file>      IDENT-A OK ... (exit 0) | IDENT-A FAIL: why (exit 1)
    python3 -I -B ident_e199.py etwho-b <et-who output file> <rc> <sampler pid or ->   IDENT-B OK ... | IDENT-B FAIL: why
    python3 -I -B ident_e199.py selfcheck                            IDENT-E199 SELF-CHECK PASS: card 1's forms pass; card 0's, a missing
                                                                     selection (card 0's block), a second card's holder refused
Python's own modules only (aifoundry1's python3; the desk's /usr/bin/python3 -I -B). Nothing here opens a device or sends a command.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import pwd
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e191"))
import e191_ident as I  # noqa: E402   E191's, unchanged

RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")       # E191 kit note 2's (1a4bc1e3's smoke stdout.txt)
CONFIG_LINE = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}   # E191's (e191_common.CONFIG_LINE), card 1 as found


def drop_runtime(text):
    """(text without every runtime line, [the dropped lines in order])."""
    dropped = [m.group(0).rstrip("\n") for m in RUNTIME_LINE.finditer(text or "")]
    return RUNTIME_LINE.sub("", text or ""), dropped


def config_json(text):
    """The config read's JSON object, or {} when none parses."""
    rest, _ = drop_runtime(text)
    for ln in reversed(rest.splitlines()):
        s = ln.strip()
        if s.startswith("{"):
            try:
                j = json.loads(s)
            except ValueError:
                return {}
            return j if isinstance(j, dict) else {}
    return {}


def config_gate(out_text, err_text):
    """('' or why, facts) for the gate (a)."""
    j = config_json(out_text)
    why = []
    if not j:
        why.append("no config JSON on the read's stdout")
    else:
        off = {k: j.get(k) for k, v in CONFIG_LINE.items() if j.get(k) != v}
        if off:
            why.append("config %s, not %s" % (off, CONFIG_LINE))
    w = I.config_identity(j, err_text)
    if w:
        why.append(w)
    targets, ids = I.parse_ident(err_text)
    rl = drop_runtime(out_text)[1]
    other = sorted({x for x in rl if x != "Opening device 1"})
    if other:
        why.append("a runtime line names another device: %s (card 1 prints 'Opening device 1')" % ", ".join(other))
    facts = {"json": j, "targets": sorted({"/dev/et%s_%s" % t for t in targets}), "ids": sorted(set(ids)),
             "runtime_lines": rl}
    return "; ".join(why), facts


def etwho_b(lines, rc, sampler_pid, me=None, dev_dir=None):
    """('' or why, counts, sampler nodes) for the gate (b)."""
    me = me or pwd.getpwuid(os.getuid()).pw_name
    u = I.etwho_unreadable(rc, lines)
    if u:
        return u, {}, []
    why, counts = I.etwho_identity(lines, me)
    nodes = I.proc_nodes(sampler_pid, dev_dir) if sampler_pid else set()
    w2 = I.sampler_identity(nodes) if sampler_pid else "no sampler process found"
    why = "; ".join(x for x in (why, w2) if x)
    return why, counts, sorted("/dev/et%s_%s" % n for n in nodes)


def _read(p):
    with open(p, errors="replace") as f:
        return f.read()


def selfcheck():
    bad = []
    blk = I.BLOCK
    c1, c0 = blk.format(c=1, k="mgmt"), blk.format(c=0, k="mgmt")
    good = 'Opening device 1\n{"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": 499}\n'
    w, f = config_gate(good, c1)
    if w or f["runtime_lines"] != ["Opening device 1"]:
        bad.append("card 1's config read (runtime line first) refused: %s" % w)
    split = good.replace('"minion_mhz"', 'Opening device 1\n"minion_mhz"', 1)       # the runtime line inside the JSON line
    if config_gate(split, c1)[0]:
        bad.append("card 1's config read with the runtime line inside the line refused")
    if not config_gate(good.replace("499", "519"), c1)[0]:
        bad.append("card 0's minion_mv 519 passed")
    if not config_gate(good, c0)[0]:
        bad.append("card 0's identity block (/dev/et0_mgmt, ID 0: the read a missing ET_DEVICES gives on two cards) passed")
    if not config_gate(good, "")[0]:
        bad.append("a read with no identity block passed")
    if not config_gate(good.replace('"tdp_w": 65', '"tdp_w": 0'), c1)[0]:
        bad.append("TDP 0 W (not card 1's 65) passed")
    if not config_gate("Opening device 1\n", c1)[0]:
        bad.append("no JSON passed")
    if not config_gate(good.replace("Opening device 1", "Opening device 0"), c1)[0]:
        bad.append("a runtime line naming device 0 passed (card 1's JSON and identity block otherwise)")
    me = "me"
    ok_lines = ["/dev/et1_mgmt me 100 ettelem"]
    if etwho_b(ok_lines, 0, None, me)[0] != "no sampler process found":
        bad.append("etwho_b without a sampler pid")
    if I.etwho_identity(ok_lines, me)[0]:
        bad.append("card 1's holder line refused")
    for lines, what in ((["/dev/et1_mgmt me 100 ettelem", "/dev/et0_mgmt me 101 ettelem"], "a holder of ours on card 0"),
                        (["/dev/et1_mgmt me 100 ettelem", "/dev/et0_ops other 7 x_host"], "another login's holder on card 0 (a second card)"),
                        (["/dev/et1_mgmt me 100 ettelem", "/dev/et1_ops other 7 x_host"], "another login's holder on card 1"),
                        (["lock:etsoc-shire0.lock me 100 bash"], "card 0's lock held by us"),
                        ([], "no holder line at all (the sampler not seen)")):
        if not I.etwho_identity(lines, me)[0]:
            bad.append(what + " passed")
    if not etwho_b(["No process holds an ET-SoC-1 device node or card lock."], 2, None, me)[0].startswith("et-who unreadable"):
        bad.append("et-who rc 2 read")
    return bad


def main(argv):
    if len(argv) >= 1 and argv[0] == "selfcheck":
        bad = selfcheck()
        print("IDENT-E199 SELF-CHECK " + ("PASS: card 1's forms pass; card 0's block, card 0's minion_mv, no block, TDP 0, no JSON, a runtime line naming device 0, a "
                                          "holder of ours or another login's on either card, card 0's lock, no holder line and an "
                                          "unreadable et-who refused" if not bad else "FAIL: " + "; ".join(bad)))
        return 0 if not bad else 1
    if len(argv) == 3 and argv[0] == "config":
        why, f = config_gate(_read(argv[1]), _read(argv[2]))
        if why:
            print("IDENT-A FAIL: " + why)
            return 1
        print("IDENT-A OK: %s, physical device ID %s, minion_mv %s, TDP %s W / %s C / %s MHz; runtime lines dropped %d" % (
            ",".join(f["targets"]), ",".join(map(str, f["ids"])), f["json"].get("minion_mv"), f["json"].get("tdp_w"),
            f["json"].get("temp_threshold_c"), f["json"].get("minion_mhz"), len(f["runtime_lines"])))
        return 0
    if len(argv) == 4 and argv[0] == "etwho-b":
        pid = None if argv[3] == "-" else int(argv[3])
        why, counts, nodes = etwho_b(_read(argv[1]).splitlines(), int(argv[2]), pid)
        if why:
            print("IDENT-B FAIL: %s; counts %s" % (why, json.dumps(counts, sort_keys=True)))
            return 1
        print("IDENT-B OK: counts %s; the sampler holds %s" % (json.dumps(counts, sort_keys=True), nodes))
        return 0
    print(__doc__.split("\n    python3")[0][:200])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
