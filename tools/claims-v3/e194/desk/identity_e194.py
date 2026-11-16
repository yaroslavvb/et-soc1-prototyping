#!/usr/bin/env python3
"""E194's identity-gate test (Q183, the kit, Sun 15 Nov 2026, after E194's registration and before any E194 datum): THE IDENTITY GATE
(e194_ident.py) both ways on the COMMITTED forms the cards printed: this card's forms pass; a second card's and a missing node's are refused.
Desk only, standard library only; it reads committed files and runs no host, no reader and no device.

    /usr/bin/python3 -I -B tools/claims-v3/e194/desk/identity_e194.py        (prints IDENTITY-E194 n of m PASS)

  I1  (a) THIS CARD's committed config reads (E190 arm A on aifoundry2 card 0, 13 Nov 2026: config-start and config-end, their stderr and
      JSON): the gate passes both (/dev/et0_mgmt, device ID 0, 519 mV);
  I2  (a) A SECOND CARD's committed reads (E190 arm B and E191's stop record, aifoundry1 card 1: /dev/et1_mgmt, ID 1, 499 mV): refused, each
      naming the card;
  I3  (a) A MISSING NODE's forms: an empty stderr (no block), the guard's own refusal on its stderr, a reader that could not open the node:
      each refused ("the card cannot be told"); and this card's block with minion_mv 0 (a failed read) or 619 (the 800 MHz point): refused;
  I4  another box's card 0 (E189's committed aifoundry3 host block; E189's kit kept no config stderr): it passes the card test (card 0,
      ID 0) - the gate tells cards apart, the runner's box check (hostname aifoundry2, the reader's pin, today's builds there) tells boxes
      apart: stated, reported;
  I5  (c) the hosts' committed stderr blocks: this card's (E190 arm A's smoke and runs, /dev/et0_ops, ID 0) read right with nothing wrong;
      a second card's (E190 arm B's, /dev/et1_ops, ID 1) read wrong, every one;
  I6  (b) et-who with the sampler running, in et-who's own line form: the sampler of ours on /dev/et0_mgmt and our lock on
      etsoc-shire0 pass; a line of ours on a second card's node or lock, another login's line on either, and no sampler line (a missing
      node) are refused; the sampler's own held nodes: card 0's management node passes, a second card's or none refused;
  I7  the holder rule before a launch (foreign_lines): a stray reader of ours on /dev/et0_mgmt before the sampler starts is the one reason
      read as transient (the runner re-reads it with the lock held); a host of ours on /dev/et0_ops, a line of ours on a second card and
      another login's line are not.
A desk check of code on committed records; nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
sys.path.insert(0, E)
import e194_ident as I  # noqa: E402

DD = os.path.join(REPO, "docs/reports/data")
A2 = os.path.join(DD, "2026-11-13-e190-large-gemm/aifoundry2")
A1 = os.path.join(DD, "2026-11-13-e190-large-gemm/aifoundry1-c1")
S191 = os.path.join(DD, "2026-11-15-e191-blind-day-aifoundry1-c1/session")
S189 = os.path.join(DD, "2026-11-14-e189-blind-day-aifoundry3/session")
RES = []


def ok(cond, what):
    RES.append(bool(cond))
    print(f"-> {'PASS' if cond else 'FAIL'} ({what})", flush=True)


def rd(d, name):
    return json.load(open(os.path.join(d, f"config-{name}.json"))), open(os.path.join(d, f"config-{name}.err")).read()


def main():
    print(f"identity_e194 ({sys.executable} {sys.version.split()[0]})")
    w = {}
    for nm in ("start", "end"):
        j, e = rd(A2, nm)
        w[nm] = (I.config_identity(j, e), I.parse_ident(e), j.get("minion_mv"))
        print(f"   I1 E190 arm A config-{nm}: targets/ids {w[nm][1]}, minion_mv {w[nm][2]} -> {w[nm][0] or 'passes'}")
    ok(not w["start"][0] and not w["end"][0] and w["start"][1] == ([("0", "mgmt")], [0]),
       "I1 this card's committed config reads (E190 arm A, both ends) pass the gate")
    got = []
    for d in (A1, S191):
        for nm in ("start", "end"):
            if not os.path.exists(os.path.join(d, f"config-{nm}.err")):
                continue
            j, e = rd(d, nm)
            why = I.config_identity(j, e)
            got.append(why)
            print(f"   I2 {os.path.relpath(d, DD)} config-{nm}: {why[:160]}")
    ok(len(got) == 4 and all("/dev/et1_mgmt" in x and "Physical device ID [1]" in x for x in got),
       "I2 a second card's committed reads (aifoundry1 card 1, E190 arm B and E191, both ends) refused, each naming the card (its 499 mV "
       "lies inside this one-card box's sanity band: the node and the ID refuse it)")
    j0, _ = rd(A2, "start")
    guard_refusal = "ettelem_guard_e194: refused (ET_DEVICES is set ('0'): aifoundry2's one card is opened with ET_DEVICES unset): not in E194's classified command list\n"
    open_fail = "LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:1]: \nError opening /dev/et0_mgmt: No such file or directory\n"
    miss = [I.config_identity(j0, ""), I.config_identity(j0, guard_refusal), I.config_identity(j0, open_fail)]
    _, e0 = rd(A2, "start")
    mv = [I.config_identity(dict(j0, minion_mv=0), e0), I.config_identity(dict(j0, minion_mv=619), e0)]
    print(f"   I3 missing node: {[x[:70] for x in miss]}; minion_mv 0 / 619: {[x[:70] for x in mv]}")
    ok(all("no 'PCIe target' line" in x for x in miss) and all("minion_mv" in x for x in mv),
       "I3 a missing node's forms (no block, the guard's refusal, a failed open) refused; minion_mv 0 and 619 refused")
    e3 = open(os.path.join(S189, "smoke", "copy-64m-random", "host.err")).read()
    w3 = I.host_identity(*I.parse_ident(e3), set())
    print(f"   I4 E189's committed aifoundry3 card 0 host block: targets/ids {I.parse_ident(e3)} -> wrong {w3[0]}, right {w3[1]}")
    ok(w3[1] and not w3[0], "I4 another box's card 0 (E189's aifoundry3 host block) passes the card test: stated (the runner's box check "
       "tells boxes apart, by hostname, the reader's pin and the builds made there today)")
    errs_a = sorted(glob.glob(os.path.join(A2, "smoke", "*", "proc.err")) + glob.glob(os.path.join(A2, "runs", "*", "proc-*.err")))
    errs_b = sorted(glob.glob(os.path.join(A1, "smoke", "*", "proc.err")) + glob.glob(os.path.join(A1, "runs", "*", "proc-*.err")))
    ra = [I.host_identity(*I.parse_ident(open(f).read()), set()) for f in errs_a]
    rb = [I.host_identity(*I.parse_ident(open(f).read()), set()) for f in errs_b]
    print(f"   I5 this card's host stderr files {len(ra)}: right {sum(1 for w_, r in ra if r and not w_)}; a second card's {len(rb)}: wrong "
          f"{sum(1 for w_, r in rb if w_)}")
    ok(len(ra) == 87 and all(r and not w_ for w_, r in ra) and len(rb) == 87 and all(w_ for w_, r in rb),
       "I5 the hosts' committed stderr blocks: this card's 87 read right, nothing wrong; a second card's 87 read wrong, every one")
    me = "us"
    sam, lk = "/dev/et0_mgmt  us 100 00:05 ettelem", "lock:etsoc-shire0.lock us 99 00:06 python3"
    good = I.etwho_identity([sam, lk], me)[0]
    bads = [I.etwho_identity(x, me)[0] for x in ([sam, lk, "/dev/et1_ops us 7 0 h"], [sam, lk, "lock:etsoc-shire1.lock us 7 0 x"],
                                                  [sam, lk, "/dev/et0_ops other 8 0 y"], [sam, lk, "/dev/et1_mgmt other 8 0 y"], [lk])]
    nodes = [I.sampler_identity({("0", "mgmt")}), I.sampler_identity({("1", "mgmt")}), I.sampler_identity(set())]
    ok(not good and all(bads) and not nodes[0] and nodes[1] and nodes[2],
       "I6 et-who with the sampler: card 0's lines pass; a second card's, another login's and a missing sampler line refused; the held nodes the same")
    f_reader = I.foreign_lines([lk, "/dev/et0_mgmt us 7 0 ettelem"], me)
    f_host = I.foreign_lines([lk, "/dev/et0_ops us 5 0 ledger_host"], me)
    f_card1 = I.foreign_lines([lk, "/dev/et1_mgmt us 6 0 e"], me)
    f_other = I.foreign_lines(["/dev/et0_mgmt other 9 0 z"], me)
    print(f"   I7 stray reader {f_reader}; host {f_host}; second card {f_card1}; another login {f_other}")
    ok(f_reader[0] and f_reader[2] and f_host[0] and not f_host[2] and f_card1[0] and not f_card1[2] and f_other[0] and not f_other[2],
       "I7 only a stray reader of ours on /dev/et0_mgmt reads transient (re-read with the lock held); a host, a second card, another login refuse")
    print(f"IDENTITY-E194 {sum(RES)} of {len(RES)} {'PASS' if all(RES) else 'FAIL'}")
    return 0 if all(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
