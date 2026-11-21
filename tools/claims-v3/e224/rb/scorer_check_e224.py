#!/usr/bin/env python3
"""E224's kit, BOTH ARMS' STEP 2 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): THE FROZEN SCORER'S TWO SELF-TESTS RUN WITHOUT
WRITING IN THE LAB (E213's lesson, verify-e215's finding 1, fix-e215's form, E220's rb/scorer_check_e220.py). E224's scorer (score_e224.py,
frozen by the registration) writes its self-tests into its own folder (`--selftest-standins` -> selftest-standins.json, `--selftest-real` ->
selftest-real.json: registered files), so step 2 never runs those modes. This helper imports the frozen scorer by its path, unchanged (no
bytecode written), calls the same two functions with output paths in OUT (the card lane's RB_OUT), and compares each made file with the
committed one:

  - the stand-in self-test: BYTE FOR BYTE (its record names no lab state: stand-in labs only);
  - the real-bytes self-test: its record names the lab's HEAD and THE PICK the lab holds there ('pick_reader_on_the_lab': lab_head, verdict,
    why), both of which move after the registration (any later commit; E222's scores once committed, when the reader reads PICKED). So it is
    compared FIELD BY FIELD with the committed record, every field equal but those three, which are REPORTED; the made record's own verdict
    must read OK and its pick reader ok (NO PICK, or PICKED with one of the eight compositions: the registered reading). A kit reading stated
    before any datum (KIT.md section 2), no rule of E224's changed.

    /usr/bin/python3 -I -B tools/claims-v3/e224/rb/scorer_check_e224.py <OUT dir>
        SCORER-CHECK-E224: stand-ins PASS (byte-identical to selftest-standins.json); real bytes OK (equal to selftest-real.json but the lab's
        HEAD and its pick: REPORTED <head12> <verdict>)                                                                              exit 0
        anything else: SCORER-CHECK-E224 FAILED: <why>                                                                                exit 1
It writes only <OUT>/selftest-standins-e224-check.json and <OUT>/selftest-real-e224-check.json, and refuses (exit 2) an OUT inside the lab clone.
Standard library only (the scorer's own imports).
SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
E224 = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E224, "..", "..", ".."))
MOVING = ("lab_head", "verdict", "why")       # pick_reader_on_the_lab's fields that follow the lab's HEAD (REPORTED, never compared)


def real_same(made, committed):
    """(same, words): every field of the real-bytes record equal but pick_reader_on_the_lab's MOVING fields; the made record OK"""
    a, b = json.loads(json.dumps(made)), json.loads(json.dumps(committed))
    pa, pb = a.get("pick_reader_on_the_lab") or {}, b.get("pick_reader_on_the_lab") or {}
    moved = {k: pa.get(k) for k in MOVING}
    for k in MOVING:
        pa.pop(k, None)
        pb.pop(k, None)
    if a != b:
        diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        return False, f"the real-bytes record differs from the committed one beyond the pick reader's moving fields: {diff}"
    if made.get("verdict") != "OK" or not (made.get("pick_reader_on_the_lab") or {}).get("ok"):
        return False, f"the made real-bytes record reads {made.get('verdict')} (pick reader ok {(made.get('pick_reader_on_the_lab') or {}).get('ok')})"
    return True, f"REPORTED {str(moved.get('lab_head'))[:12]} {moved.get('verdict')}"


def main(argv):
    if len(argv) != 1:
        print("usage: scorer_check_e224.py <OUT dir outside the lab clone>")
        return 2
    out = os.path.realpath(argv[0])
    if out == os.path.realpath(REPO) or out.startswith(os.path.realpath(REPO) + os.sep):
        print("SCORER-CHECK-E224 REFUSED: OUT is inside the lab clone")
        return 2
    os.makedirs(out, exist_ok=True)
    spec = importlib.util.spec_from_file_location("score_e224_frozen", os.path.join(E224, "score_e224.py"))
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    why, words = [], ""
    for name, fn, committed in (("stand-ins", S.selftest_standins, "selftest-standins.json"), ("real bytes", S.selftest_real, "selftest-real.json")):
        p = os.path.join(out, committed.replace(".json", "-e224-check.json"))
        try:
            ok = fn(p)
        except SystemExit as e:                   # the scorer refuses (exit 4) when a frozen file changed
            ok = False
            why.append(f"{name}: the scorer exited {e.code}")
        if not ok:
            why.append(f"{name}: the self-test did not pass")
        try:
            if name == "stand-ins":
                same = open(p, "rb").read() == open(os.path.join(E224, committed), "rb").read()
                if not same:
                    why.append(f"{name}: {os.path.basename(p)} differs from the committed {committed}")
            else:
                same, words = real_same(json.load(open(p)), json.load(open(os.path.join(E224, committed))))
                if not same:
                    why.append(f"{name}: {words}")
        except (OSError, ValueError) as e:
            why.append(f"{name}: {type(e).__name__}")
    if why:
        print("SCORER-CHECK-E224 FAILED: " + "; ".join(why))
        return 1
    print("SCORER-CHECK-E224: stand-ins PASS (byte-identical to selftest-standins.json); real bytes OK (equal to selftest-real.json but the "
          f"lab's HEAD and its pick: {words})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
