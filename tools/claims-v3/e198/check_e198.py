#!/usr/bin/env python3
"""E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): the dry listing on aifoundry1 card 1 against E193's registered
listings (tools/claims-v3/e193/desk/dry-e193-*.txt, unchanged), E198.md 2: "the kit's dry listing on aifoundry1 differs from them only in
--device 1's prefix and the host's built path". The runner's own --dry lines name, besides the host's path, the things --device 1 sets
(the device prefix, the card and its lock in the first line, the one ops node) and the holder check the kit passes; each is mapped back to
E193's text by an exact rule below, counted, and then the two listings must be equal byte for byte. Any other difference is a DIFFERS.
The smoke gate, the stop reason, the summary and the nine checks are E193's own checker (check_e193.py), used unchanged.

    python3 -I -B check_e198.py drycmp LISTING REGISTERED --host PATH --holder-check PATH
        LISTING SAME / LISTING DIFFERS (exit 0 / 3)
The rules (each applied to a line only where its whole pattern stands; a line no rule touches is compared as it is):
  1. the host:          PATH (the session's --host, the kit's host wrapper) -> build/x04clock/host/x04clock_host (E193's REG_HOST)
  2. the device prefix: a line beginning 'DRY ET_DEVICES=1 ' -> 'DRY ET_DEVICES=0 '
  3. the holder check:  'DRY <holder-check PATH> --check; flock -n /run/lock/etsoc-shire1.lock (' -> 'DRY et-who --check; flock -n
                        /run/lock/etsoc-shire0.lock ('
  4. the ops node:      the line 'DRY count /dev/et*_ops: need exactly /dev/et1_ops' -> '... /dev/et0_ops'
  5. the first line:    ', card 1, lock /run/lock/etsoc-shire1.lock' at its end -> ', card 0, lock /run/lock/etsoc-shire0.lock'
Standard library only. Exit 0, 3, 2 (usage). SPDX-License-Identifier: Apache-2.0
"""
import collections
import os
import sys

REG_HOST = "build/x04clock/host/x04clock_host"


def lines(path):
    try:
        with open(path, errors="replace") as f:
            return f.read().splitlines()
    except OSError:
        return []


def mapped(listing, host, holder):
    n = collections.Counter()
    out = []
    pre3 = f"DRY {holder} --check; flock -n /run/lock/etsoc-shire1.lock ("
    for x in lines(listing):
        if x.startswith("DRY ET_DEVICES=1 "):
            x = "DRY ET_DEVICES=0 " + x[len("DRY ET_DEVICES=1 "):]
            n["device prefix"] += 1
        if host in x:
            x = x.replace(host, REG_HOST)
            n["host"] += 1
        if x.startswith(pre3):
            x = "DRY et-who --check; flock -n /run/lock/etsoc-shire0.lock (" + x[len(pre3):]
            n["holder check and lock"] += 1
        if x == "DRY count /dev/et*_ops: need exactly /dev/et1_ops":
            x = "DRY count /dev/et*_ops: need exactly /dev/et0_ops"
            n["ops node"] += 1
        if x.endswith(", card 1, lock /run/lock/etsoc-shire1.lock"):
            x = x[: -len(", card 1, lock /run/lock/etsoc-shire1.lock")] + ", card 0, lock /run/lock/etsoc-shire0.lock"
            n["card and lock line"] += 1
        out.append(x)
    return out, n


def drycmp(listing, registered, host, holder):
    a, n = mapped(listing, host, holder)
    b = lines(registered)
    nd = sum(1 for x in a if x.startswith("DRY ET_DEVICES="))
    left = [x for x in lines(listing) if "ET_DEVICES=1" in x and not x.startswith("DRY ET_DEVICES=1 ")]
    how = ", ".join(f"{k} {v}" for k, v in sorted(n.items()))
    if a == b and not left:
        print(f"LISTING SAME: {os.path.basename(registered)}, {nd} device calls, {len(a)} lines (mapped: {how})")
        return 0
    k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    print(f"LISTING DIFFERS from {os.path.basename(registered)} at line {k + 1} ({len(a)} lines against {len(b)}; {nd} device calls; "
          f"mapped: {how}): {(a[k] if k < len(a) else '<end>')[:160]!r} against {(b[k] if k < len(b) else '<end>')[:160]!r}")
    return 3


def main(argv):
    if len(argv) == 7 and argv[0] == "drycmp" and argv[3] == "--host" and argv[5] == "--holder-check":
        return drycmp(argv[1], argv[2], argv[4], argv[6])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
