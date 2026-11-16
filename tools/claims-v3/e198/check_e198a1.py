#!/usr/bin/env python3
"""E198's kit after dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): the dry listing of THE LAB'S RUNNER
COPY (run_x04_e198a1.py) on aifoundry1 card 1 against E193's registered listings (tools/claims-v3/e193/desk/dry-e193-*.txt, unchanged).
It is check_e198.py (kit-e198, Q191; unchanged beside it, imported by its path) with ONE MORE EXACT RULE, A1's only change to a listed line:

  6. the timeout:       in a device call (a line beginning 'DRY ET_DEVICES=0 ' once rule 2 has run), 'DRY ET_DEVICES=0 timeout 10 ' ->
                        'DRY ET_DEVICES=0 timeout -k 1 10 ' (E193's runner wraps each device process in `timeout -k 1 10`; the lab's copy
                        in a plain `timeout 10`: E198.md.dated-amendment-A1.md)

counted, and then the two listings must be equal byte for byte, as check_e198.py's drycmp requires. Stricter than check_e198.py: the
listing itself must name no 'timeout -k' anywhere, and every one of its device calls must have taken rule 6 (a device call under any other
wrapper is a DIFFERS).

    python3 -I -B check_e198a1.py drycmp LISTING REGISTERED --host PATH --holder-check PATH
        LISTING SAME / LISTING DIFFERS (exit 0 / 3)
Standard library only. Exit 0, 3, 2 (usage). SPDX-License-Identifier: Apache-2.0
"""
import collections
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("check_e198_for_a1", os.path.join(HERE, "check_e198.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

A1_FROM = "DRY ET_DEVICES=0 timeout 10 "
A1_TO = "DRY ET_DEVICES=0 timeout -k 1 10 "


def drycmp(listing, registered, host, holder):
    a, n = C.mapped(listing, host, holder)
    n = collections.Counter(n)
    out = []
    for x in a:
        if x.startswith(A1_FROM):
            x = A1_TO + x[len(A1_FROM):]
            n["timeout (A1)"] += 1
        out.append(x)
    b = C.lines(registered)
    raw = C.lines(listing)
    nd = sum(1 for x in out if x.startswith("DRY ET_DEVICES="))
    left = [x for x in raw if "ET_DEVICES=1" in x and not x.startswith("DRY ET_DEVICES=1 ")]
    k_in = [x for x in raw if "timeout -k" in x or "--kill-after" in x]
    how = ", ".join(f"{k} {v}" for k, v in sorted(n.items()))
    if out == b and not left and not k_in and n["timeout (A1)"] == nd:
        print(f"LISTING SAME: {os.path.basename(registered)}, {nd} device calls, {len(out)} lines (mapped: {how}); the listing names "
              f"no 'timeout -k'; every device call under a plain 'timeout 10' (E198 A1)")
        return 0
    if k_in:
        print(f"LISTING DIFFERS from {os.path.basename(registered)}: the listing names 'timeout -k' or '--kill-after' "
              f"({len(k_in)} line(s)): {k_in[0][:160]!r}")
        return 3
    if n["timeout (A1)"] != nd:
        print(f"LISTING DIFFERS from {os.path.basename(registered)}: {nd} device calls but {n['timeout (A1)']} under a plain 'timeout 10'")
        return 3
    k = next((i for i, (x, y) in enumerate(zip(out, b)) if x != y), min(len(out), len(b)))
    print(f"LISTING DIFFERS from {os.path.basename(registered)} at line {k + 1} ({len(out)} lines against {len(b)}; {nd} device calls; "
          f"mapped: {how}): {(out[k] if k < len(out) else '<end>')[:160]!r} against {(b[k] if k < len(b) else '<end>')[:160]!r}")
    return 3


def main(argv):
    if len(argv) == 7 and argv[0] == "drycmp" and argv[3] == "--host" and argv[5] == "--holder-check":
        return drycmp(argv[1], argv[2], argv[4], argv[6])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
