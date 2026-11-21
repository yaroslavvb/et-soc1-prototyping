#!/usr/bin/env python3
"""E222's kit, STEP 2 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum): THE FROZEN SCORER'S TWO SELF-TESTS RUN WITHOUT WRITING IN THE
LAB (E213's lesson, verify-e215's finding 1, fix-e215's form; E220's rb/scorer_check_e220.py, kit 2f0ab9cd, line for line for E222). E222's scorer
(score_e222.py, frozen by the registration) writes its self-tests into its own folder (`--selftest-standins` -> selftest-standins.json,
`--selftest-real` -> selftest-real.json: registered files), so step 2 never runs those modes. This helper imports the frozen scorer by its path,
unchanged (no bytecode written), calls the same two functions with output paths in OUT (the card lane's RB_OUT), and compares each made file with
the committed one byte for byte:

    /usr/bin/python3 -I -B tools/claims-v3/e222/rb/scorer_check_e222.py <OUT dir>
        SCORER-CHECK-E222: stand-ins PASS (byte-identical to selftest-standins.json); real bytes OK (byte-identical to selftest-real.json)  exit 0
        anything else: SCORER-CHECK-E222 FAILED: <why>                                                                                   exit 1
It writes only <OUT>/selftest-standins-e222-check.json and <OUT>/selftest-real-e222-check.json, and refuses (exit 2) an OUT inside the lab clone.
Standard library only (the scorer's own imports; it loads E220's frozen scorer at its pin, whose readers it uses).
SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
E222 = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E222, "..", "..", ".."))


def main(argv):
    if len(argv) != 1:
        print("usage: scorer_check_e222.py <OUT dir outside the lab clone>")
        return 2
    out = os.path.realpath(argv[0])
    if out == os.path.realpath(REPO) or out.startswith(os.path.realpath(REPO) + os.sep):
        print("SCORER-CHECK-E222 REFUSED: OUT is inside the lab clone")
        return 2
    os.makedirs(out, exist_ok=True)
    spec = importlib.util.spec_from_file_location("score_e222_frozen", os.path.join(E222, "score_e222.py"))
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    why = []
    for name, fn, committed in (("stand-ins", S.selftest_standins, "selftest-standins.json"), ("real bytes", S.selftest_real, "selftest-real.json")):
        p = os.path.join(out, committed.replace(".json", "-e222-check.json"))
        try:
            ok = fn(p)
        except SystemExit as e:                   # the scorer refuses (exit 4) when a frozen file changed
            ok = False
            why.append(f"{name}: the scorer exited {e.code}")
        if not ok:
            why.append(f"{name}: the self-test did not pass")
        try:
            same = open(p, "rb").read() == open(os.path.join(E222, committed), "rb").read()
        except OSError as e:
            same = False
            why.append(f"{name}: {type(e).__name__}")
        if not same:
            why.append(f"{name}: {os.path.basename(p)} differs from the committed {committed}")
    if why:
        print("SCORER-CHECK-E222 FAILED: " + "; ".join(why))
        return 1
    print("SCORER-CHECK-E222: stand-ins PASS (byte-identical to selftest-standins.json); real bytes OK (byte-identical to selftest-real.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
