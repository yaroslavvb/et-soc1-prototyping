#!/usr/bin/env python3
"""The self-test of arm_m1_e180.py (E180's dated note M2, E180.md.dated-note-M2.md section 1), on synthetic sessions scored by E180's own
scorer v3 (score_e180_v3.py, imported unchanged), so the reader reads the very record the card day's step 22 v3 writes. No E180 data
exists; nothing here is a forecast or a verdict.

    python3 -B tools/claims-v3/e180/selftest_arm_m1_e180.py > tools/claims-v3/e180/logs/selftest-arm-m1-e180.txt   # exit 0 if all pass

It reads only committed files and writes only in a temporary directory of its own (tempfile; TMPDIR decides where), removed at the end.
Every synthetic session has six passes; each kind's D is 26.0 W plus its truth, with a fixed pattern of a few hundredths of a watt on
4s, 5s or the zeros, so every interval is known in advance and far from the values it is read against (M5 excepted, by design).
  M0   check: the pinned inputs at their sha256 and M1's values: CHECK PASS
  M1   P's truth (every kind at P's frozen watts): the scorer's E180-H POSITIVE with P inside; the arm FAIL LOW on the board, on the
       rail (R = 0.7741 of each kind's D above 26 W) and for both kinds; the reader's intervals equal the test's own
  M2   the model's truth (4s and 5s at M1's +0.0298 and +0.0340 W above the zeros): PASS on all four. D(4s) alone averages about 26.03 W,
       so only the D - D(zeros) footing reads PASS (a reading of D(4s) itself against +0.0298 W would read FAIL LOW)
  M3   no difference (4s, 5s and the zeros equal but for +-0.05 W patterns): the arm PASS and 0 inside: "read alike"
  M4   the card reads less than the model (5s - 4s -0.05 W; 4s -0.02 and 5s -0.07 W above the zeros): FAIL HIGH on all four
  M5   E180-H's lower end inside the 00:00:55 frozen sentence's bracket, above M1's value: FAIL LOW at M1's value and the bracket's low
       end, PASS at its high end, the difference named
  M6   an end of E180-H's interval between 0 and the arm: the arm PASS, 0 W FAIL LOW, "read differently"; the bracket inside the
       interval reads PASS at both ends
  M7   one kept pass: the scorer NOT SCORED; the reader NOT READ, exit 0, and its NOT READ record written
  M8   the reduction is not the one scored (one pass's D(5s) moved by 0.1 W after scoring): exit 3, nothing written
  M9   the kept passes differ (a pass removed from the reduction after scoring): exit 3
  M10  no rail in the reduction: RA2 not read, the board's three readings as in M1
  M11  --write twice: the second run exits 4 and leaves both files byte for byte
  M12  a pinned input differs (one byte of M1's JSON, in a copy of the reader's directory): check and read exit 9, nothing written
  M13  a card other than aifoundry3 in the scorer's record: exit 2
  M14  no output names a directory of the test (its temporary directory, the home directory or the system's temporary directory), and
       each written file says REPORTED and never a verdict
SPDX-License-Identifier: Apache-2.0
"""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import power_e180 as pw  # noqa: E402  (the registered statistics, unchanged)
import score_e180_v3 as s3  # noqa: E402  (E180's scorer v3, unchanged)

READER = os.path.join(HERE, "arm_m1_e180.py")
PY = sys.executable
PASSES = [str(p) for p in (18010, 18011, 18012, 18013, 18014, 18015)]
K4, K5, KZ = "fadd.ps/f_4", "fadd.ps/f_5", "fadd.ps/zeros"
E4 = [+0.01, -0.01, +0.01, -0.01, +0.01, -0.01]
E5 = [-0.01, +0.01, +0.01, -0.01, -0.01, +0.01]
RAIL = 0.7741


def load(n):
    return json.load(open(os.path.join(HERE, n)))


FC, FOOT, OFF, NOISE = load("forecast-e180.json"), load("footing-e180-a1.json"), load("offset-e180-a1.json"), load("noise/noise-e180.json")
M1 = load("m1-october-forecast-model-e180.json")
KINDS = FC["kinds"]
PW = {nm: KINDS[nm]["W"]["aifoundry3"]["P"] for nm in KINDS}
ARM = M1["arm"]["model_W_above_zeros"]


def session(truth, e4=E4, e5=E5, ez=None, passes=PASSES, rail=RAIL):
    """a reduced session in reduce_e180_v3.py's form: D(kind) = 26.0 + truth(kind) (+ the patterns), R = rail x (D - 26.0)"""
    red = {"card": "aifoundry3", "passes": {}, "set_aside": {},
           "v3": {"what": "a synthetic session (selftest_arm_m1_e180.py)", "unreadable_passes": {}}}
    for i, p in enumerate(passes):
        D = {}
        for nm in KINDS:
            v = 26.0 + truth(nm)
            v += e4[i] if nm == K4 else e5[i] if nm == K5 else (ez[i] if (nm == KZ and ez) else 0.0)
            D[nm] = v
        rec = {"D": D, "runs": {nm: [{"w": v, "ops_per_s": 4.58e11}] for nm, v in D.items()}}
        if rail is not None:
            rec["R"] = {nm: rail * (v - 26.0) for nm, v in D.items()}
        red["passes"][p] = rec
    return red


def write_session(d, red):
    os.makedirs(d)
    scored = s3.score(copy.deepcopy(red), FC, "aifoundry3", FOOT, OFF, None, None, NOISE)
    with open(os.path.join(d, "reduced-e180-v3.json"), "w") as f:
        json.dump(red, f, indent=1)
    with open(os.path.join(d, "scored-e180.json"), "w") as f:
        json.dump(scored, f, indent=1, sort_keys=True)
    return scored


def run(args, reader=READER):
    p = subprocess.run([PY, "-B", reader] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return p.returncode, p.stdout


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    res, outputs = [], []
    tmp = tempfile.mkdtemp(prefix="selftest-arm-m1-e180-")

    def case(name, cond, detail):
        res.append(bool(cond))
        print(f"{name}: {'PASS' if cond else 'FAIL'} - {' | '.join(detail.splitlines())}")

    def read_case(tag, red, rail_note=""):
        d, w = os.path.join(tmp, tag), os.path.join(tmp, tag + "-out")
        scored = write_session(d, red)
        os.makedirs(w)
        rc, out = run(["read", "--session", d, "--write", w])
        outputs.append(out)
        rec = None
        if os.path.exists(os.path.join(w, "arm-m1-e180.json")):
            rec = json.load(open(os.path.join(w, "arm-m1-e180.json")))
            outputs.append(open(os.path.join(w, "arm-m1-e180.json")).read())
            outputs.append(open(os.path.join(w, "arm-m1-e180.md")).read())
        return rc, out, rec, scored, d, w

    def words(rec):
        r = (rec or {}).get("readings")
        if not r:
            return None
        return [r[k].get("words", r[k].get("status")) for k in ("H_board", "RA2_rail", "4s_above_zeros", "5s_above_zeros")]

    def hb(rec):
        return (rec or {}).get("readings", {}).get("H_board", {})

    try:
        rc, out = run(["check"])
        outputs.append(out)
        case("M0 check: the pinned inputs and M1's values", rc == 0 and out.startswith("CHECK PASS"), out.strip()[:200])

        # M1: P's truth
        rc, out, rec, sc, d, w = read_case("m1", session(lambda nm: PW[nm]))
        H = sc["rules"]["E180-H"]
        xs = [(PW[K5] + E5[i]) - (PW[K4] + E4[i]) for i in range(6)]
        m, lo, hi = pw.interval(xs)
        h = hb(rec)
        ok = (rc == 0 and H["sign"] == "POSITIVE" and H["size"]["P"] == "PASS" and words(rec) == ["FAIL LOW"] * 4
              and abs(h["lo"] - lo) < 1e-12 and abs(h["hi"] - hi) < 1e-12 and h["zero"] == "POSITIVE")
        case("M1 P's truth: the arm FAIL LOW on all four", ok,
             f"scorer E180-H {H['verdict']}; reader {words(rec) if rec else rc}; H {h.get('mean', 0):+.4f} "
             f"[{h.get('lo', 0):+.4f}, {h.get('hi', 0):+.4f}] (the test's own [{lo:+.4f}, {hi:+.4f}]) against {ARM['5s_minus_4s']:+.4f} W")

        # M2: the model's truth, and the footing
        tr = lambda nm: ARM["4s"] if nm == K4 else ARM["5s"] if nm == K5 else 0.0 if nm == KZ else PW[nm]
        rc, out, rec, sc, d, w = read_case("m2", session(tr))
        r = (rec or {}).get("readings", {})
        alone = [26.0 + ARM["4s"] + E4[i] for i in range(6)]
        m_a, lo_a, hi_a = pw.interval(alone)
        naive = pw.size(lo_a, hi_a, ARM["4s"])
        ok = (rc == 0 and words(rec) == ["PASS"] * 4 and naive == "FAIL LOW"
              and abs(r["4s_above_zeros"]["d_kind_alone_mean"] - m_a) < 1e-9)
        case("M2 the model's truth: PASS on all four, on the D - D(zeros) footing", ok,
             f"reader {words(rec) if rec else rc}; 4s above zeros {r.get('4s_above_zeros', {}).get('mean', 0):+.4f} against "
             f"{ARM['4s']:+.4f} W; D(4s) alone {m_a:.4f} W [{lo_a:.4f}, {hi_a:.4f}] would read {naive}")

        # M3: no difference
        tr = lambda nm: 0.0 if nm in (K4, K5, KZ) else PW[nm]
        big4, big5 = [5 * e for e in E4], [5 * e for e in E5]
        rc, out, rec, sc, d, w = read_case("m3", session(tr, e4=big4, e5=big5))
        h = hb(rec)
        ok = (rc == 0 and words(rec) == ["PASS"] * 4 and h["zero"] == "NOT RESOLVED" and h["arm_and_no_difference"] == "read alike")
        case("M3 no difference: the arm PASS, 0 inside, read alike", ok,
             f"reader {words(rec) if rec else rc}; H [{h.get('lo', 0):+.4f}, {h.get('hi', 0):+.4f}]; zero {h.get('zero')}; "
             f"{h.get('arm_and_no_difference')}")

        # M4: the card reads less than the model
        tr = lambda nm: -0.02 if nm == K4 else -0.07 if nm == K5 else 0.0 if nm == KZ else PW[nm]
        small4, small5 = [0.2 * e for e in E4], [0.2 * e for e in E5]
        rc, out, rec, sc, d, w = read_case("m4", session(tr, e4=small4, e5=small5))
        case("M4 the card below the model: FAIL HIGH on all four", rc == 0 and words(rec) == ["FAIL HIGH"] * 4,
             f"reader {words(rec) if rec else rc}")

        # M5: E180-H's lower end inside the bracket
        tiny4, tiny5 = [0.1 * e for e in E4], [0.1 * e for e in E5]
        dx = [tiny5[i] - tiny4[i] for i in range(6)]
        _, lo0, hi0 = pw.interval(dx)
        hw = (hi0 - lo0) / 2
        target_lo = 0.00445
        c = target_lo + hw
        tr = lambda nm: PW[K4] if nm == K4 else PW[K4] + c if nm == K5 else PW[nm]
        rc, out, rec, sc, d, w = read_case("m5", session(tr, e4=tiny4, e5=tiny5))
        h = hb(rec)
        br = h.get("bracket_00_00_55", {})
        ok = (rc == 0 and words(rec) is not None and ARM["5s_minus_4s"] < h["lo"] < br["W"][1] and h["words"] == "FAIL LOW"
              and br["words_at_ends"] == ["FAIL LOW", "PASS"] and br["same_words_across"] is False
              and "the words differ across" in out)
        case("M5 an end of E180-H's interval inside the 00:00:55 bracket: named", ok,
             f"H [{h.get('lo', 0):+.5f}, {h.get('hi', 0):+.5f}]; M1's {ARM['5s_minus_4s']:+.5f}: {h.get('words')}; bracket "
             f"{br.get('W', [0, 0])[0]:+.5f} to {br.get('W', [0, 0])[1]:+.5f}: {br.get('words_at_ends')}")

        # M6: an end of E180-H's interval between 0 and the arm
        c6 = 0.002 + hw
        tr = lambda nm: PW[K4] if nm == K4 else PW[K4] + c6 if nm == K5 else PW[nm]
        rc, out, rec, sc, d, w = read_case("m5b", session(tr, e4=tiny4, e5=tiny5))
        h = hb(rec)
        br = h.get("bracket_00_00_55", {})
        ok = (rc == 0 and words(rec) is not None and 0 < h["lo"] < ARM["5s_minus_4s"] and h["words"] == "PASS"
              and h["zero_words"] == "FAIL LOW" and h["arm_and_no_difference"] == "read differently"
              and br["words_at_ends"] == ["PASS", "PASS"] and br["same_words_across"] is True)
        case("M6 an end of E180-H's interval between 0 and the arm: read differently", ok,
             f"H [{h.get('lo', 0):+.5f}, {h.get('hi', 0):+.5f}]; the arm {h.get('words')}, 0 W {h.get('zero_words')}: "
             f"{h.get('arm_and_no_difference')}; bracket ends {br.get('words_at_ends')}")

        # M7: one kept pass
        rc, out, rec, sc, d, w = read_case("m6", session(lambda nm: PW[nm], passes=PASSES[:1]))
        ok = (rc == 0 and sc["rules"]["E180-H"]["verdict"] == "NOT SCORED" and rec is not None and rec["status"] == "NOT READ"
              and "NOT READ" in out)
        case("M7 one kept pass: NOT READ, exit 0", ok, f"scorer {sc['rules']['E180-H']['verdict']}; reader rc {rc}: {out.strip()[:200]}")

        # M8: the reduction is not the one scored
        d, w = os.path.join(tmp, "m7"), os.path.join(tmp, "m7-out")
        red = session(lambda nm: PW[nm])
        write_session(d, red)
        red["passes"]["18011"]["D"][K5] += 0.1
        with open(os.path.join(d, "reduced-e180-v3.json"), "w") as f:
            json.dump(red, f, indent=1)
        os.makedirs(w)
        rc, out = run(["read", "--session", d, "--write", w])
        outputs.append(out)
        case("M8 a reduction that is not the one scored: exit 3, nothing written", rc == 3 and os.listdir(w) == [], out.strip()[:200])

        # M9: the kept passes differ
        d, w = os.path.join(tmp, "m8"), os.path.join(tmp, "m8-out")
        red = session(lambda nm: PW[nm])
        write_session(d, red)
        red["passes"].pop("18015")
        with open(os.path.join(d, "reduced-e180-v3.json"), "w") as f:
            json.dump(red, f, indent=1)
        os.makedirs(w)
        rc, out = run(["read", "--session", d, "--write", w])
        outputs.append(out)
        case("M9 the kept passes differ: exit 3, nothing written", rc == 3 and os.listdir(w) == [], out.strip()[:200])

        # M10: no rail
        rc, out, rec, sc, d, w = read_case("m9", session(lambda nm: PW[nm], rail=None))
        ok = rc == 0 and words(rec) == ["FAIL LOW", "not read", "FAIL LOW", "FAIL LOW"]
        case("M10 no rail: RA2 not read, the board's three readings stand", ok,
             f"reader {words(rec) if rec else rc}; RA2: {rec['readings']['RA2_rail'].get('why') if rec else ''}")

        # M11: --write twice
        d, w = os.path.join(tmp, "m1"), os.path.join(tmp, "m1-out")
        before = {n: sha(os.path.join(w, n)) for n in ("arm-m1-e180.json", "arm-m1-e180.md")}
        rc, out = run(["read", "--session", d, "--write", w])
        outputs.append(out)
        after = {n: sha(os.path.join(w, n)) for n in before}
        case("M11 --write twice: exit 4, both files byte for byte", rc == 4 and before == after and sorted(os.listdir(w)) == sorted(before),
             out.strip()[:160])

        # M12: a pinned input differs
        alt = os.path.join(tmp, "alt")
        os.makedirs(alt)
        for n in ("arm_m1_e180.py", "power_e180.py", "m1-october-forecast-model-e180.json"):
            shutil.copy2(os.path.join(HERE, n), os.path.join(alt, n))
        p = os.path.join(alt, "m1-october-forecast-model-e180.json")
        b = open(p, "rb").read()
        with open(p, "wb") as f:
            f.write(b.replace(b"0.004166469466", b"0.004166469467", 1))
        rc1, out1 = run(["check"], reader=os.path.join(alt, "arm_m1_e180.py"))
        w = os.path.join(tmp, "m11-out")
        os.makedirs(w)
        rc2, out2 = run(["read", "--session", os.path.join(tmp, "m1"), "--write", w], reader=os.path.join(alt, "arm_m1_e180.py"))
        outputs += [out1, out2]
        case("M12 a pinned input differs: check and read exit 9, nothing written", rc1 == 9 and rc2 == 9 and os.listdir(w) == [],
             f"check rc {rc1}, read rc {rc2}: {out2.strip()[:140]}")

        # M13: another card
        d, w = os.path.join(tmp, "m12"), os.path.join(tmp, "m12-out")
        write_session(d, session(lambda nm: PW[nm]))
        q = os.path.join(d, "scored-e180.json")
        s = json.load(open(q))
        s["card"] = "aifoundry1-c1"
        with open(q, "w") as f:
            json.dump(s, f, indent=1, sort_keys=True)
        os.makedirs(w)
        rc, out = run(["read", "--session", d, "--write", w])
        outputs.append(out)
        case("M13 a card other than aifoundry3: exit 2, nothing written", rc == 2 and os.listdir(w) == [], out.strip()[:160])

        # M14: the outputs' hygiene
        dirs = (tmp, os.path.realpath(tmp), tempfile.gettempdir(), os.path.expanduser("~"), os.sep + "var" + os.sep + "folders",
                os.sep + "tmp" + os.sep)
        bad = [t for t in dirs if any(t in o for o in outputs)]
        tags = ("m1", "m2", "m3", "m4", "m5", "m5b", "m6", "m9")
        mds = [os.path.join(tmp, t + "-out", "arm-m1-e180.md") for t in tags]
        js = [os.path.join(tmp, t + "-out", "arm-m1-e180.json") for t in tags]
        said = all(("REPORTED" in open(f).read() and "never" in open(f).read()) for f in mds + js)
        case("M14 no output names a directory of the test; every written file says REPORTED, never a verdict", not bad and said,
             f"{len(outputs)} outputs scanned for {len(dirs)} directories: {len(bad)} found; {len(mds) + len(js)} written files")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n = len(res)
    print(f"SELFTEST-ARM-M1-E180 {'PASS' if all(res) else 'FAIL'} {sum(res)} of {n}")
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
