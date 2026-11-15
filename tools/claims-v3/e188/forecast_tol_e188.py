#!/usr/bin/env python3
"""E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): the registration's forecast check
on any desk interpreter, with a stated tolerance on the last digits of the forecast's floats. It replaces step 2's `forecast_e188.py
check` (which compares bytes, and reads CHECK FAIL under Python 3.12) in step 2 v3 (rb/s03_desk_e188_v3.sh). It writes nothing and never
re-freezes: the committed forecast-e188.json, forecast-e188.txt and kinds-e188.json stay the pinned truth, read at the registration's
sha256, and nothing reads the recomputed numbers but this comparison.

    /usr/bin/python3 -B tools/claims-v3/e188/forecast_tol_e188.py --root .     # FORECAST-TOL-E188 PASS or FAIL; exit 0, 1 (or 2: usage)

What it reads, in order (any failure is a FAIL, never skipped):
  1. THE PINS: the registration's list SHA256SUMS-e188-registration at its count (20) and its own sha256 (b098561b..., as step 2 pins it),
     and in it, at their listed sha256, the files this check rests on: forecast_e188.py, forecast-e188.json, forecast-e188.txt,
     kinds-e188.json and bench/counts-e188.json;
  2. THE RECOMPUTATION: forecast_e188.py imported unchanged, stage(root, False) and forecast(root) run in memory, as its own `check` runs
     them (forecast() asserts its own checks: the bench's reference rows, E186's kinds to the last bit, AALL as E186's R4);
  3. EXACT, as forecast_e188.py's check: kinds-e188.json's bytes, every new tile's bytes, and forecast-e188.txt's bytes (every figure the
     registration prints, to its printed digits); and in forecast-e188.json every key, every list's length, every string (each input's
     sha256 in inputs_sha256 and m12's among them), integer, boolean and null;
  4. WITHIN THE TOLERANCE, every float of forecast-e188.json: |committed - recomputed| <= TOL_REL x max(1, |committed|, |recomputed|),
     TOL_REL = 1e-12 (a watt line near 8 W may move by 8e-12 W, a value at or below 1 by 1e-12). A NaN equals only a NaN.
It prints whether the forecast's bytes are exact (as `forecast_e188.py check` reads them: exact on the Intel's 3.9.6), and each float that
differs: both values, the difference, the tolerance and the distance in units in the last place.

WHY A TOLERANCE, AND WHY IT CANNOT PASS A REAL CHANGE (KIT.md.dated-note-2.md section 2; selftest_forecast_tol_e188.py shows each claim):
  - under /usr/bin/python3 3.12.3 (aifoundry2) the recomputation differs from the committed file in 16 floats, by at most 8.1e-14 (a power
    near 0.07) and 1.8e-15 W (a line), and in no byte of the .txt: 3.12's built-in sum() adds floats with compensated summation (7 of
    them, and two more in part), and math.erf comes from a different C library (the other 9: with sum() as before 3.12 each is at most
    8 units in the last place; natively PAIR's two powers from the registered noise, which carry both sources, differ by 5,804 units);
  - a change of the committed forecast fails the pins (1); of any input file, the exact sha256 strings (3); of any printed figure, the
    .txt's bytes (3); the float comparison sees B05's F tile's adder count changed by 1e-10 relative (the self-test's F4; at 1e-11 the
    largest difference is 0.271 of the tolerance), about 1e4 below the 1e-5 W the registration prints on an 8 W line. (Fixed by
    fix-port188 before the land, verify-port188's nits 3 and 7: this paragraph said "about 1e-11 relative, a million times below".)
Standard library only, beside what forecast_e188.py imports (numpy, for M10's chain). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import struct
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
E = "tools/claims-v3/e188"
REG_LIST = f"{E}/SHA256SUMS-e188-registration"
REG_COUNT = 20
REG_SHA256 = "b098561b055e9d85b87ea7e501105fda2f84234699a2b50b7ee8724fa0b9970e"
RESTS_ON = (f"{E}/forecast_e188.py", f"{E}/forecast-e188.json", f"{E}/forecast-e188.txt", f"{E}/kinds-e188.json",
            f"{E}/bench/counts-e188.json")
TOL_REL = 1e-12


def tol_of(a, b):
    return TOL_REL * max(1.0, abs(a), abs(b))


def ulps(a, b):
    """the distance between two finite doubles in units in the last place (the count of doubles between them)"""
    def key(x):
        i = struct.unpack("<q", struct.pack("<d", x))[0]
        return i if i >= 0 else -(i & 0x7FFFFFFFFFFFFFFF)
    return abs(key(a) - key(b))


def compare(committed, recomputed, path=()):
    """walk two JSON values side by side; returns (exact_problems, float_rows): exact_problems lists every key, length, type, string,
    integer, boolean or null that differs; float_rows lists (path, committed, recomputed, |diff|, tol, ulps, within) for every float
    that differs at all"""
    exact, rows = [], []
    where = "/".join(map(str, path)) or "<top>"
    if isinstance(committed, dict) or isinstance(recomputed, dict):
        if not (isinstance(committed, dict) and isinstance(recomputed, dict)):
            return [f"{where}: a dict on one side only"], rows
        if sorted(committed) != sorted(recomputed):
            only_c = sorted(set(committed) - set(recomputed))
            only_r = sorted(set(recomputed) - set(committed))
            exact.append(f"{where}: keys differ (committed only {only_c[:5]}, recomputed only {only_r[:5]})")
        for k in sorted(set(committed) & set(recomputed)):
            e, r = compare(committed[k], recomputed[k], path + (k,))
            exact += e
            rows += r
        return exact, rows
    if isinstance(committed, list) or isinstance(recomputed, list):
        if not (isinstance(committed, list) and isinstance(recomputed, list)):
            return [f"{where}: a list on one side only"], rows
        if len(committed) != len(recomputed):
            exact.append(f"{where}: list lengths {len(committed)} and {len(recomputed)}")
        for i, (x, y) in enumerate(zip(committed, recomputed)):
            e, r = compare(x, y, path + (i,))
            exact += e
            rows += r
        return exact, rows
    tc, tr = type(committed), type(recomputed)
    if tc is float and tr is float:
        if committed == recomputed or (math.isnan(committed) and math.isnan(recomputed)):
            return exact, rows
        if not (math.isfinite(committed) and math.isfinite(recomputed)):
            return [f"{where}: {committed!r} against {recomputed!r} (a non-finite float on one side)"], rows
        d = abs(committed - recomputed)
        t = tol_of(committed, recomputed)
        rows.append((where, committed, recomputed, d, t, ulps(committed, recomputed), d <= t))
        return exact, rows
    if tc is not tr or committed != recomputed:      # strings (every sha256), integers, booleans, null: exact, and of the same type
        exact.append(f"{where}: {committed!r} ({tc.__name__}) against {recomputed!r} ({tr.__name__})")
    return exact, rows


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_pins(root):
    """the registration's list at its count and its own bytes; the files this check rests on at their listed sha256"""
    bad = []
    lp = os.path.join(root, REG_LIST)
    if not os.path.isfile(lp):
        return [f"{REG_LIST}: missing"]
    lines = [ln for ln in open(lp).read().splitlines() if ln.strip()]
    own = sha(lp)
    if len(lines) != REG_COUNT or own != REG_SHA256:
        bad.append(f"{REG_LIST}: {len(lines)} entries, own sha256 {own[:12]}... (pinned {REG_COUNT}, {REG_SHA256[:12]}...)")
    listed = {}
    for ln in lines:
        h, _, p = ln.partition("  ")
        listed[p.strip()] = h.strip()
    for p in RESTS_ON:
        fp = os.path.join(root, p)
        if p not in listed:
            bad.append(f"{p}: not in the registration's list")
        elif not os.path.isfile(fp):
            bad.append(f"{p}: missing")
        elif sha(fp) != listed[p]:
            bad.append(f"{p}: its sha256 {sha(fp)[:12]}... is not the registration's {listed[p][:12]}...")
    return bad


def recompute(root):
    """forecast_e188.py, imported unchanged from this file's directory: stage() and forecast() in memory (nothing written)"""
    sys.path.insert(0, HERE)
    import forecast_e188 as F  # noqa: E402  (unchanged; pinned by the registration's list)
    out, blobs = F.stage(root, False)
    o = F.forecast(root)
    kl = json.load(open(os.path.join(HERE, "kinds-e188.json")))
    return F, out, blobs, o, F.txt(o, kl)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", required=True, help="the lab tree's top")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if os.path.realpath(os.path.join(root, E)) != os.path.realpath(HERE):
        print(f"forecast_tol_e188: --root {a.root} is not this file's tree")
        return 2
    print(f"forecast_tol_e188: {sys.executable} {sys.version.split()[0]}; tolerance on each float |committed - recomputed| <= "
          f"{TOL_REL:g} x max(1, |committed|, |recomputed|); every other value, the .txt and kinds-e188.json exact")
    pins = check_pins(root)
    print(f"pins: the registration's list at {REG_COUNT} entries and {REG_SHA256[:12]}..., and its lines for {len(RESTS_ON)} files: "
          + ("OK" if not pins else "FAIL: " + "; ".join(pins)))
    try:
        F, out, blobs, o, txt_new = recompute(root)
    except Exception as ex:  # forecast()'s own assertions, an input missing, an import that fails: a FAIL, never a pass
        print(f"recomputation failed: {type(ex).__name__}: {str(ex)[:300]}")
        print("FORECAST-TOL-E188 FAIL: the forecast could not be recomputed")
        return 1
    kinds_ok = open(os.path.join(HERE, "kinds-e188.json")).read() == json.dumps(out, indent=1, sort_keys=True) + "\n"
    tiles_ok = all(open(os.path.join(root, p), "rb").read() == raw for p, raw in blobs.items())
    txt_ok = open(os.path.join(HERE, "forecast-e188.txt")).read() == txt_new
    committed_text = open(os.path.join(HERE, "forecast-e188.json")).read()
    new_text = json.dumps(o, indent=1, sort_keys=True) + "\n"
    bytes_exact = committed_text == new_text
    nl = sum(1 for x, y in zip(committed_text.splitlines(), new_text.splitlines()) if x != y)
    exact, rows = compare(json.loads(committed_text), json.loads(new_text))
    outside = [r for r in rows if not r[6]]
    print(f"kinds-e188.json bytes {'exact' if kinds_ok else 'DIFFER'}; the {len(blobs)} new tiles' bytes {'exact' if tiles_ok else 'DIFFER'}; "
          f"forecast-e188.txt bytes {'exact' if txt_ok else 'DIFFER'}")
    print(f"forecast-e188.json bytes: {'EXACT (forecast_e188.py check would read CHECK PASS)' if bytes_exact else f'differ in {nl} lines (forecast_e188.py check reads CHECK FAIL)'}")
    print(f"forecast-e188.json values: {len(exact)} exact value(s) differ; {len(rows)} float(s) differ, {len(outside)} outside the tolerance")
    for p in exact[:20]:
        print(f"  EXACT DIFFERS {p}")
    for where, c, r, d, t, u, w in rows:
        print(f"  {'within ' if w else 'OUTSIDE'} {where}: committed {c!r} recomputed {r!r} |diff| {d:.3e} tol {t:.3e} ulps {u}")
    if rows:
        worst = max(rows, key=lambda x: x[3] / x[4])
        print(f"  largest |diff|/tol: {worst[3] / worst[4]:.4f} at {worst[0]}")
    ok = not pins and kinds_ok and tiles_ok and txt_ok and not exact and not outside
    why = [w for w, bad in (("pins", pins), ("kinds-e188.json", not kinds_ok), ("tiles", not tiles_ok), ("forecast-e188.txt", not txt_ok),
                            ("exact values", exact), ("floats outside the tolerance", outside)) if bad]
    print(f"FORECAST-TOL-E188 {'PASS' if ok else 'FAIL'}: "
          + (f"the committed forecast re-made within the tolerance ({len(rows)} float(s) differ in their last digits, the largest "
             f"|diff|/tol {max([x[3] / x[4] for x in rows], default=0.0):.4f}; bytes {'exact' if bytes_exact else 'not exact'}); every other value, "
             f"the .txt and the kinds exact; the registration's pins OK" if ok else "; ".join(why)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
