#!/usr/bin/env python3
"""E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): the self-test of
forecast_tol_e188.py, step 2 v3's forecast check with a stated tolerance (TOL_REL = 1e-12 of max(1, |value|)) on the last digits of the
forecast's floats. It shows how Python 3.9 and 3.12 differ on E188's forecast, and that the tolerance cannot pass a real change. It reads
the lab tree it sits in and writes nothing there (no file is written at all: every change below is made in memory or in a scratch copy
under the directory given).

    /usr/bin/python3 -B tools/claims-v3/e188/selftest_forecast_tol_e188.py <scratch dir outside the repository>

Cases (each prints its numbers; SELFTEST-FORECAST-TOL-E188 PASS or FAIL (<n> of <m>) last; exit 0 or 1):
  F1  this desk: forecast_tol_e188.py on the committed tree reads PASS; reported: the interpreter, numpy, the C library, whether the bytes
      are exact (they are on the Intel's 3.9.6, where forecast_e188.py check reads CHECK PASS) and every float that differs;
  F2  THE MECHANISM (on 3.12 or later): the forecast recomputed again with the built-in sum() replaced by plain left-to-right addition
      (what sum() does for floats before 3.12; 3.12 adds them with compensated summation): every float that still differs is a power
      value, 0.5 (1 + erf(.)) or a sum of two (math.erf, from the C library), by at most 16 units in the last place, and every other float
      of the file is then byte-identical, so the arguments erf receives are the committed ones; the rest of the native differences are
      sum()'s. The .txt is exact both ways;
  F3  THE COMPARATOR ALONE, on the committed file's own values: (a) every float moved by half its tolerance at once: none outside;
      (b) each float alone moved by twice its tolerance: that one float outside, every time; (c) each string alone changed by one
      character (every sha256 among them), each integer and boolean alone changed: an exact difference, every time; (d) each watt figure
      (a path component ending in _w) moved by 5e-6 W, half the last place the .txt prints: outside, by at least 1e5 times its tolerance;
  F4  REAL CHANGES OF THE INPUTS, recomputed through forecast_e188.forecast() with one input number changed in memory (the file's bytes,
      and so the sha256 strings, unchanged: only the recomputation can see these): the fp32 rate, or M12's gamma_B, x (1 + 1e-9): forecast()
      itself stops at its own exact check against E186's frozen kinds (an AssertionError, which the check reads as FAIL); a count of
      B05's F tile (its adder's net count, vpu.by_stage.adder_norm, in counts-e188.json; E188's own tile, which no E186 line holds)
      x (1 + r) for r from 1e-6 down to 1e-14: outside the
      tolerance at 1e-9 and above, the smallest r still seen reported (the comparator's resolution there); the registered train half-width
      (candidates_m12.HW_TRAIN, a code constant) x (1 + 1e-9) and E182's measured train se x (1 + 1e-9): each outside;
  F5  THE PINS, on scratch copies of the six files they read: the registration's list one line short; forecast-e188.json with one byte
      appended (its list line kept; "one byte changed" until fix-port188, verify-port188's nit 7: the case appends one); forecast-e188.json and its list line rewritten together (the count kept, every entry OK): each refused, naming
      the file or the list; the intact copies pass.
Needs numpy (forecast_e188.py's M10 chain). SPDX-License-Identifier: Apache-2.0
"""
import builtins
import hashlib
import json
import os
import platform
import shutil
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import forecast_tol_e188 as T  # noqa: E402  (the check under test)
import forecast_e188 as F  # noqa: E402  (unchanged; the registration's)

npass = ncase = 0


def ok(cond, what):
    global npass, ncase
    ncase += 1
    if cond:
        npass += 1
    print(f"-> {'PASS' if cond else 'FAIL'} ({what})", flush=True)


def floats_of(o, path=()):
    if isinstance(o, dict):
        for k in o:
            yield from floats_of(o[k], path + (k,))
    elif isinstance(o, list):
        for i, x in enumerate(o):
            yield from floats_of(x, path + (i,))
    elif type(o) is float:
        yield path


def others_of(o, path=()):
    if isinstance(o, dict):
        for k in o:
            yield from others_of(o[k], path + (k,))
    elif isinstance(o, list):
        for i, x in enumerate(o):
            yield from others_of(x, path + (i,))
    elif type(o) in (str, int, bool):
        yield path


def get(o, path):
    for k in path:
        o = o[k]
    return o


def put(o, path, v):
    for k in path[:-1]:
        o = o[k]
    o[path[-1]] = v


def canon(o):
    return json.loads(json.dumps(o, indent=1, sort_keys=True) + "\n")


def main():
    scratch = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else ""
    if not scratch or (scratch + os.sep).startswith(ROOT + os.sep):
        print("usage: selftest_forecast_tol_e188.py <scratch dir outside the repository>")
        return 2
    os.makedirs(scratch, exist_ok=True)
    import numpy
    print(f"interpreter {sys.executable} {sys.version.split()[0]}; numpy {numpy.__version__}; C library {' '.join(platform.libc_ver()) or 'unknown'}; "
          f"{platform.system()} {platform.machine()}")
    committed_text = open(os.path.join(HERE, "forecast-e188.json")).read()
    committed = json.loads(committed_text)
    txt_committed = open(os.path.join(HERE, "forecast-e188.txt")).read()
    kl = json.load(open(os.path.join(HERE, "kinds-e188.json")))

    print("\n== F1. this desk: the check on the committed tree")
    rc = T.main(["--root", ROOT])
    ok(rc == 0, "F1 forecast_tol_e188.py reads PASS on the committed tree here")
    o_native = canon(F.forecast(ROOT))
    ex_n, rows_n = T.compare(committed, o_native)
    native = {r[0] for r in rows_n}
    print(f"native: {len(rows_n)} float(s) differ, {len(ex_n)} exact value(s) differ; bytes exact: "
          f"{json.dumps(o_native, indent=1, sort_keys=True) + chr(10) == committed_text}")

    print("\n== F2. the mechanism: sum() as before 3.12 (plain left-to-right addition)")
    orig_sum = builtins.sum

    def sum_left_to_right(iterable, /, start=0):
        total = start
        for x in iterable:
            total = total + x
        return total
    builtins.sum = sum_left_to_right
    try:
        o_39 = canon(F.forecast(ROOT))
        txt_39 = F.txt(F.forecast(ROOT), kl)
    finally:
        builtins.sum = orig_sum
    ex_39, rows_39 = T.compare(committed, o_39)
    left = {r[0] for r in rows_39}
    for where, c, r, d, t, u, w in rows_39:
        print(f"  still differs: {where}: committed {c!r} recomputed {r!r} ulps {u}")
    powers = all(p.endswith(("power_excludes_0_if_M10", "power_excludes_0_if_M12")) for p in left)
    max_u = max([r[5] for r in rows_39], default=0)
    by_sum = sorted(native - left)
    print(f"  under the old summation: {len(rows_39)} float(s) differ (max {max_u} ulps), all of them power values: {powers}; "
          f"explained by sum() alone: {len(by_sum)}: {', '.join(by_sum)}")
    print(f"  in both readings (sum's change beside erf's): {', '.join(sorted(native & left)) or 'none'}")
    if sys.version_info >= (3, 12):
        ok(not ex_39 and powers and max_u <= 16 and left <= native and txt_39 == txt_committed,
           "F2 under the old summation only power values (math.erf) still differ, by at most 16 units in the last place, every other float "
           "byte-identical (so erf's arguments are the committed ones), the .txt exact")
    else:
        ok(rows_39 == rows_n, "F2 below 3.12 the old summation is the interpreter's own: the same reading as F1")

    print("\n== F3. the comparator alone, on the committed file's own values")
    fpaths = list(floats_of(committed))
    opaths = list(others_of(committed))
    print(f"  the committed file holds {len(fpaths)} floats and {len(opaths)} strings, integers and booleans")
    half = json.loads(committed_text)
    for p in fpaths:
        v = get(half, p)
        put(half, p, v + 0.5 * T.tol_of(v, v))
    ex, rows = T.compare(committed, half)
    moved = sum(1 for r in rows)
    ok(not ex and all(r[6] for r in rows) and moved >= 0.9 * len(fpaths),
       f"F3a every float moved by half its tolerance at once ({moved} of {len(fpaths)} move at all; the rest are too large to move by "
       f"that much): none outside")
    bad = 0
    for p in fpaths:
        m = json.loads(committed_text)
        v = get(m, p)
        put(m, p, v + 2.0 * T.tol_of(v, v))
        ex, rows = T.compare(committed, m)
        out = [r for r in rows if not r[6]]
        if ex or len(out) != 1 or out[0][0] != "/".join(map(str, p)):
            bad += 1
    ok(bad == 0, f"F3b each of the {len(fpaths)} floats alone moved by twice its tolerance: that float outside, every time ({bad} misses)")
    bad = 0
    for p in opaths:
        m = json.loads(committed_text)
        v = get(m, p)
        if type(v) is str:
            nv = (v[:-1] + ("0" if v[-1:] != "0" else "1")) if v else "x"
        elif type(v) is bool:
            nv = not v
        else:
            nv = v + 1
        put(m, p, nv)
        ex, rows = T.compare(committed, m)
        if len(ex) != 1:
            bad += 1
    ok(bad == 0, f"F3c each of the {len(opaths)} strings (every sha256 among them), integers and booleans alone changed: an exact "
                 f"difference, every time ({bad} misses)")
    wpaths = [p for p in fpaths if any(isinstance(k, str) and k.endswith("_w") for k in p)]
    worst = min(5e-6 / T.tol_of(get(committed, p), get(committed, p) + 5e-6) for p in wpaths)
    bad = 0
    for p in wpaths:
        m = json.loads(committed_text)
        put(m, p, get(m, p) + 5e-6)
        ex, rows = T.compare(committed, m)
        if ex or not rows or rows[0][6]:
            bad += 1
    print(f"  watt figures (a path component ending in _w): {len(wpaths)}, the largest magnitude "
          f"{max(abs(get(committed, p)) for p in wpaths):.4f} W")
    ok(bad == 0 and worst >= 1e5, f"F3d each of the {len(wpaths)} watt figures moved by 5e-6 W (half of the .txt's last printed place, "
                                  f"1e-5 W): outside every time ({bad} misses), by at least {worst:.3g} times its tolerance")

    print("\n== F4. real changes of the inputs, recomputed (one input number changed in memory; the files' bytes and sha256 unchanged)")
    orig_load = json.load

    def recompute_with(target, mutate):
        def load(fp, *a, **k):
            obj = orig_load(fp, *a, **k)
            if getattr(fp, "name", "").endswith(target):
                mutate(obj)
            return obj
        json.load = load
        try:
            return canon(F.forecast(ROOT))
        finally:
            json.load = orig_load

    def reading(o):
        ex, rows = T.compare(committed, o)
        out = [r for r in rows if not r[6]]
        return ex, rows, out
    def refused_by_forecast(target, mutate):
        try:
            recompute_with(target, mutate)
        except AssertionError as e:
            return str(e)[:120] or "AssertionError"
        return ""
    why = refused_by_forecast("m12/candidates-m12.json", lambda j: j["rates_per_s"].__setitem__("fp32", j["rates_per_s"]["fp32"] * (1 + 1e-9)))
    print(f"  the fp32 rate x (1 + 1e-9): forecast() itself refuses (its assertion that E186's kinds keep their lines to the last bit): {bool(why)}")
    ok(bool(why), "F4 the fp32 rate x (1 + 1e-9): the recomputation stops at forecast()'s own exact check against E186's frozen kinds (a FAIL)")

    def gamma_b(j):
        i = j["float"]["names"].index("gamma_B_w")
        j["float"]["b"][i] = j["float"]["b"][i] * (1 + 1e-9)
    why = refused_by_forecast("m12/m12.json", gamma_b)
    print(f"  M12's gamma_B x (1 + 1e-9): forecast() itself refuses (the same assertion, on M12's lines): {bool(why)}")
    ok(bool(why), "F4 M12's gamma_B x (1 + 1e-9): the recomputation stops at forecast()'s own exact check (a FAIL)")

    resolution = None
    for r_ in (1e-6, 1e-9, 1e-10, 1e-11, 1e-12, 1e-13, 1e-14):
        def adder(j, r_=r_):
            if "rows" in j and "fp32.e188_a1_b3f800020" in j["rows"]:
                st = j["rows"]["fp32.e188_a1_b3f800020"]["mean"]["vpu"]["by_stage"]
                st["adder_norm"] = st["adder_norm"] * (1 + r_)
        ex, rows, out = reading(recompute_with("e188/bench/counts-e188.json", adder))
        print(f"  B05's F tile (E188's own tile, no E186 line), its adder net count x (1 + {r_:g}): {len(rows)} float(s) differ, {len(out)} outside "
              f"the tolerance, the largest |diff|/tol {max([x[3] / x[4] for x in rows], default=0.0):.3g}; exact differences {len(ex)}")
        if out:
            resolution = r_
        if r_ >= 1e-9:
            ok(len(out) > 0 and not ex, f"F4 B05's F tile's adder net count x (1 + {r_:g}): outside the tolerance (no string changed: the float comparison alone)")
    print(f"  the comparator's resolution on that count: {resolution if resolution is None else format(resolution, 'g')} relative is the smallest change of these it still sees")
    ok(resolution is not None and resolution <= 1e-9, f"F4 the float comparison sees a change of that count down to {resolution} relative")

    CM = F.CM
    hw0 = CM.HW_TRAIN
    CM.HW_TRAIN = hw0 * (1 + 1e-9)
    try:
        ex, rows, out = reading(canon(F.forecast(ROOT)))
    finally:
        CM.HW_TRAIN = hw0
    print(f"  the registered train half-width (candidates_m12.HW_TRAIN, a code constant) x (1 + 1e-9): {len(rows)} float(s) differ, {len(out)} outside")
    ok(len(out) > 0 and not ex, "F4 the registered half-width x (1 + 1e-9): outside the tolerance")

    def se182(j):
        if "trains" in j:
            for t in ("T5", "T6"):
                if t in j["trains"]:
                    j["trains"][t]["estimate"]["se"] = j["trains"][t]["estimate"]["se"] * (1 + 1e-9)
    ex, rows, out = reading(recompute_with("trains-e182.json", se182))
    print(f"  E182's measured train se x (1 + 1e-9): {len(rows)} float(s) differ, {len(out)} outside")
    ok(len(out) > 0 and not ex, "F4 E182's measured train se x (1 + 1e-9): outside the tolerance")

    print("\n== F5. the pins, on scratch copies of the six files they read")
    S = os.path.join(scratch, "pins")
    if os.path.isdir(S):
        shutil.rmtree(S)

    def stage_copy():
        if os.path.isdir(S):
            shutil.rmtree(S)
        for p in (T.REG_LIST,) + T.RESTS_ON:
            d = os.path.join(S, os.path.dirname(p))
            os.makedirs(d, exist_ok=True)
            shutil.copyfile(os.path.join(ROOT, p), os.path.join(S, p))
    stage_copy()
    p0 = T.check_pins(S)
    print(f"  intact copies: {p0 or 'OK'}")
    lp = os.path.join(S, T.REG_LIST)
    lines = open(lp).read().splitlines(True)
    open(lp, "w").write("".join(lines[:-1]))
    p1 = T.check_pins(S)
    print(f"  the list one line short: {p1}")
    stage_copy()
    fj = os.path.join(S, T.E, "forecast-e188.json")
    open(fj, "a").write(" ")
    p2 = T.check_pins(S)
    print(f"  forecast-e188.json one byte added: {p2}")
    h = hashlib.sha256(open(fj, "rb").read()).hexdigest()
    t = open(lp).read().replace(next(ln for ln in open(lp).read().splitlines() if ln.endswith("/forecast-e188.json")),
                                f"{h}  {T.E}/forecast-e188.json")
    open(lp, "w").write(t)
    p3 = T.check_pins(S)
    print(f"  forecast-e188.json and its list line rewritten together: {p3}")
    ok(not p0 and any("SHA256SUMS-e188-registration" in x for x in p1) and any("forecast-e188.json" in x for x in p2)
       and any("SHA256SUMS-e188-registration" in x for x in p3) and not any("forecast-e188.json" in x for x in p3),
       "F5 the pins refuse a short list, a changed forecast, and a forecast rewritten with its list line (the list's own bytes); the "
       "intact copies pass")
    shutil.rmtree(S)

    print(f"\nSELFTEST-FORECAST-TOL-E188 {'PASS' if npass == ncase else 'FAIL'} ({npass} of {ncase})")
    return 0 if npass == ncase else 1


if __name__ == "__main__":
    sys.exit(main())
