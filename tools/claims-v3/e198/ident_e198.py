#!/usr/bin/env python3
"""E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): THE IDENTITY GATE of E198.md section 3 (E191's dated note 1,
item 3, as E191's kit carries it), read through E191's own code, tools/claims-v3/e191/e191_ident.py, imported UNCHANGED by its path (at its
sha256 3fabb603... in harness-e198.json). Standard library only.

    python3 -I -B ident_e198.py config CONFIG_JSON CONFIG_ERR
        (a): the start config read made through E191's guard with ET_DEVICES=1, its stderr kept: every 'PCIe target' line names
        /dev/et1_mgmt and every 'Physical device ID' line reads 1 (e191_ident.config_identity), minion_mv above 450 and below 510, and the
        JSON reads TDP 65 W, threshold 65 C, minion 600 MHz (card 1 as found; E198.md 3); power_state_name never compared.
        IDENT-A OK ... / IDENT-A FAIL: ... (exit 0 / 3)
    python3 -I -B ident_e198.py nodes PID
        the card nodes process PID holds open or mapped, as JSON (e191_ident.proc_nodes), read while it runs
    python3 -I -B ident_e198.py etwho ETWHO_OUT --rc N --me LOGIN --pid PID --nodes NODES_JSON --client CLIENT_OUT --client-rc N
        (b): the box's et-who, read outside the private /dev with the identity sampler running inside it: readable
        (e191_ident.etwho_unreadable); every holder line of our login on card 1, at least one on /dev/et1_mgmt, none on card 0, no other
        login's line on either card (e191_ident.etwho_identity); the sampler's own nodes /dev/et1_mgmt and nothing of card 0
        (e191_ident.sampler_identity); and THE HOLDER CHECK FROM INSIDE: the answer holdercheck_e198.sh got inside the private /dev (through
        the warden) exits 1 and lists the sampler's line, /dev/et1_mgmt with the sampler's process ID, as the runner's exemption needs.
        Counts only are printed, never a login. IDENT-B OK ... / IDENT-B FAIL: ... (exit 0 / 3)
    python3 -I -B ident_e198.py selfcheck [--real ERR_FILE]
        both ways, every verdict stated first: card 1's forms pass; card 0's forms, a failed voltage read, a config that is not card 1's
        as found, an unreadable et-who, a card-0 holder line (ours or another login's), another login's card-1 line, a sampler on card 0,
        and an inside answer without the sampler's line are refused. --real reads a committed aifoundry1 card-1 stderr (E191's 7156ac15
        config-start.err) as card 1's form and the same bytes with card 1's name and ID made card 0's as card 0's.
SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IDENT_PATH = os.path.normpath(os.path.join(HERE, "..", "e191", "e191_ident.py"))
CFG_WANT = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}


def load_ident():
    spec = importlib.util.spec_from_file_location("e191_ident_for_e198", IDENT_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


I = load_ident()


def read(path):
    try:
        with open(path, errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def gate_a(cfg_text, err_text):
    """'' or why, for the start config read (a)."""
    try:
        j = json.loads(cfg_text.strip().splitlines()[-1]) if cfg_text.strip() else None
    except ValueError:
        j = None
    if not isinstance(j, dict):
        return "no config JSON came back"
    why = [f"{k} {j.get(k)!r}, not {v}" for k, v in CFG_WANT.items() if j.get(k) != v]
    w = I.config_identity(j, err_text)
    if w:
        why.append(w)
    return "; ".join(why)


def gate_b(etwho_text, rc, me, pid, nodes, client_text, client_rc):
    """('' or why, counts) for the identity read (b) and the holder check from inside."""
    lines = etwho_text.splitlines()
    why = []
    u = I.etwho_unreadable(rc, lines) if rc == 0 else ("" if rc == 1 else f"et-who unreadable (rc {rc})")
    # et-who --check exits 1 when a holder is listed (the sampler must be): rc 1 with holder lines is its readable answer
    if rc == 1 and not I.holder_rows(lines):
        u = "et-who --check exit 1 with no holder line"
    if u:
        why.append(u)
    w, counts = I.etwho_identity(lines, me)
    if w:
        why.append(w)
    s = I.sampler_identity({(c, k) for c, k in nodes})
    if s:
        why.append(s)
    crow = I.holder_rows(client_text.splitlines())
    mine = [f for f in crow if f[0] == I.MGMT and len(f) >= 3 and f[2] == str(pid)]
    if client_rc != 1 or not mine:
        why.append(f"the holder check from inside the private /dev (exit {client_rc}, {len(crow)} holder line(s)) does not list the "
                   f"sampler's /dev/et1_mgmt line with its process ID")
    direct = sorted(" ".join(f[:3]) for f in I.holder_rows(lines))
    inside = sorted(" ".join(f[:3]) for f in crow)
    counts["inside_lines"] = len(crow)
    counts["inside_same_as_outside"] = direct == inside
    return "; ".join(why), counts


def selfcheck(real_err):
    me = "labuser"
    base = real_err or ("PCIe target:            /dev/et1_mgmt\nPhysical device ID:     1                    (0x1)\n")
    card0 = base.replace("/dev/et1_mgmt", "/dev/et0_mgmt").replace("Physical device ID:" + base.split("Physical device ID:")[1].split("\n")[0],
                                                                 "Physical device ID:                                        0                    (0x0)")
    c1 = json.dumps({"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600,
                     "minion_mv": 499})
    cases = [
        ("A1 card 1's config and stderr", gate_a(c1, base), True),
        ("A2 card 0's stderr (PCIe target /dev/et0_mgmt, ID 0)", gate_a(c1, card0), False),
        ("A3 card 0's minion_mv 519", gate_a(c1.replace('"minion_mv": 499', '"minion_mv": 519'), base), False),
        ("A4 a failed voltage read (0)", gate_a(c1.replace('"minion_mv": 499', '"minion_mv": 0'), base), False),
        ("A5 no stderr identity at all (ET_DEVICES missing: the guard refused, nothing came back)", gate_a("", ""), False),
        ("A6 TDP 0 W (aifoundry3's form, not card 1 as found)", gate_a(c1.replace('"tdp_w": 65', '"tdp_w": 0'), base), False),
        ("A7 a second PCIe target line naming card 0 beside card 1's", gate_a(c1, base + "PCIe target: /dev/et0_mgmt\n"), False),
    ]
    s_line = f"/dev/et1_mgmt  {me}  4242  00:03 ettelem sample --seconds 10 --every-ms 100"
    good_nodes = [("1", "mgmt")]

    def b(etw, rc=1, nodes=good_nodes, client=None, crc=1):
        return gate_b(etw, rc, me, 4242, nodes, s_line if client is None else client, crc)[0]
    cases += [
        ("B1 the sampler's line only, inside the same", b(s_line), True),
        ("B2 our line on card 0's node", b(s_line + f"\n/dev/et0_mgmt  {me}  4243  00:01 ettelem"), False),
        ("B3 another login's line on card 0 (a second card's holder)", b(s_line + "\n/dev/et0_ops  otheruser  777  01:00 x_host"), False),
        ("B4 another login's line on card 1", b(s_line + "\n/dev/et1_ops  otheruser  778  01:00 x_host"), False),
        ("B5 card 0's lock held by us", b(s_line + f"\nlock:etsoc-shire0.lock {me} 4244 00:01 flock"), False),
        ("B6 et-who unreadable (exit 2, sudo refused)", b("", rc=2), False),
        ("B7 no line on /dev/et1_mgmt (the sampler not seen)", b("", rc=0), False),
        ("B8 the sampler holds card 0's node", b(s_line, nodes=[("0", "mgmt")]), False),
        ("B9 the inside answer lacks the sampler's line", b(s_line, client="", crc=0), False),
        ("B10 the inside answer failed (exit 2: no warden)", b(s_line, client="", crc=2), False),
    ]
    bad = 0
    for name, why, want_pass in cases:
        got = (why == "")
        ok = got == want_pass
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {'pass' if got else 'refused'} (want {'pass' if want_pass else 'refused'})"
              + ("" if got else f" - {why[:150]}"))
    print(f"E198-IDENT SELF-CHECK {'PASS' if not bad else 'FAIL'}: {len(cases) - bad} of {len(cases)} as stated"
          + (" (card 1's stderr: the committed aifoundry1 bytes)" if real_err else ""))
    return 0 if not bad else 3


def main(argv):
    if len(argv) == 3 and argv[0] == "config":
        why = gate_a(read(argv[1]), read(argv[2]))
        if why:
            print("IDENT-A FAIL: " + why)
            return 3
        print("IDENT-A OK: TDP 65 W, 65 C, minion 600 MHz as found; PCIe target /dev/et1_mgmt and physical device ID 1 on its stderr; "
              "minion_mv within (450, 510)")
        return 0
    if len(argv) == 2 and argv[0] == "nodes":
        print(json.dumps(sorted(I.proc_nodes(int(argv[1])))))
        return 0
    if argv and argv[0] == "etwho" and len(argv) >= 2:
        a = argv[2:]

        def opt(k, default=""):
            return a[a.index(k) + 1] if k in a else default
        try:
            nodes = [tuple(x) for x in json.loads(read(opt("--nodes")) or "[]")]
        except ValueError:
            nodes = []
        why, counts = gate_b(read(argv[1]), int(opt("--rc", "2")), opt("--me"), int(opt("--pid", "0") or 0), nodes,
                             read(opt("--client")), int(opt("--client-rc", "2") or 2))
        if why:
            print("IDENT-B FAIL: " + why + " " + json.dumps(counts, sort_keys=True))
            return 3
        print("IDENT-B OK: " + json.dumps(counts, sort_keys=True) + "; the sampler holds /dev/et1_mgmt and no card-0 node; the holder "
              "check from inside the private /dev lists the sampler's line by its process ID")
        return 0
    if argv and argv[0] == "selfcheck":
        return selfcheck(read(argv[argv.index("--real") + 1]) if "--real" in argv else "")
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
