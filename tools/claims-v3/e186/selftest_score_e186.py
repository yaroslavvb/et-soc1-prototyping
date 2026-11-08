#!/usr/bin/env python3
"""E186 (Q158, the kit): the scorer's, the reductions' and the exact copy-back's self-test. No card; it writes only under <work dir>.

ON COMMITTED DATA (E182, 8 Nov 2026, docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3/; post hoc checks of code, deciding nothing):
  A1  THE SCALE FROM THE FLOAT TRAINS' ANCHORS (E186.md section 4.2), by the kit's own route: reduce_e186.py's anchor passes from E182's
      two fp32 train blocks (T5 p18211, T6 p18213), E78's reduction on E182's registered footing, then score_e178.session_scale: both
      passes kept, the scale read from fp32.randn; its value set beside E182's own, read from E182's kinds passes (scored.json > scale);
  A2  E182's reduce_train, as reduce_e186.py imports it (unchanged), on E182's committed T1 and T5 blocks: each estimate equals
      trains-e182.json's to the last bit;
  A3  the trains' measured rate from their own launch records (reduce_e186.train_rate) on E182's six committed trains, against the
      candidates' rates (forecast-e186.json > rates_per_s), reported, each within 2%;
  A4  e186_stats.py's own self-check (the chi-square points, size_band's two forms, split_from) passes.
ON SYNTHETIC SESSIONS (fake_card_e186.py, the box's layout; reduce_e186.py trains and anchors, score_e186.py score, and note M1's reader,
as the collector and step 11 run them):
  B1  M12's world: every train's estimate within 4 se of M12's scored line, and more than 4 from M10's on the seven trains the two
      separate by 9 se or more (the lines' wiring; a SIZE word alone holds with chance 0.95); E186-H16 F16-SAME; SPLIT3 and SPLIT63 A+B; GB and GA POSITIVE with
      SIZE M12 PASS; S23R AGREES; E186-M M12; TR-N AS FORECAST; C PASS; s read from the anchors; note M1's reader reads 14 trains not
      covered and 8 not run, as planned;
  B2  M10's world: E186-H16 M10; every train within 4 se of M10's scored line, and more than 4 from M12's on the seven; E186-M's Q under
      40 for M10 and over 100 for M12;
  B3  M12 with H16 at the fp16-scaled arm: E186-H16 SCALED;
  B4  noise at 2.5 times the forecast: TR-N FAILS;
  B5  Q3-sign cut to 6 processes (3 units): Q3-sign NOT SCORED, SPLIT3 NOT SCORED, E186-M read over the other eight;
  B6  one S23 launch FAILs the check of C: E186-C FAIL, S23 and S23R NOT SCORED;
  B7  FAIL CLOSED: the trains' anchors left out, so s cannot be read: the four ladder trains' SIZE and WHICH NOT SCORED with their SIGN
      read, GB and GA NOT SCORED, E186-M over the five trains whose lines need no s;
  B8  the fallback (five kinds passes, no train): E186-LV scored, every train rule NOT SCORED; s read from the kinds passes; note M1's
      reader reads fp32.ones (K09) against v4's band;
  B9  ccsessions_e186's list on a synthetic raw tree: the smoke, every train block (by train.jsonl or its anchors) and every kinds pass with
      a launch record, and no .attempt copy;
  B10 smoke_gate_e186.py --part train on a synthetic smoke (H16's two fp16 processes, the C log's host, tiles and C records, the dumps):
      PASS; with one launch's kind off the schedule: FAIL;
  B11 THE EXACT COPY-BACK (copyback_e186.py) on a synthetic session directory and its blocks: EXACT; one byte changed: DIFFERS; an extra
      file: EXTRA; no manifest: NO-MANIFEST; a block directory the manifest does not name: DIFFERS;
  B12 THE IMAGES of E186's kinds (e186_common.image_problems): all 15 hold their A and B words whole (the fp16 pair's two halves a
      word); one 32-bit word changed in a copy of each session kind's image is caught; a 2,047-byte image is caught.
    /usr/bin/python3 -B selftest_score_e186.py <work dir>
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e186_common as E  # noqa: E402
E182D = os.path.join(TOP, "docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3")
PY = "/usr/bin/python3"
KF = "0.20563713796102187"
FAILS, N = [], [0]


def say(ok, what):
    N[0] += 1
    print(("PASS " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


def run(*args, **kw):
    return subprocess.run([PY, "-B", *args], capture_output=True, text=True, cwd=TOP, **kw)


def committed(work):
    # A1 the scale from the float trains' anchors, on E182's committed fp32 trains
    d = os.path.join(work, "a1")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    code = ("import sys, json, os\nsys.path.insert(0, sys.argv[1])\nimport reduce_e186 as RD\n"
            "e186 = RD.refuse_unless_frozen()\nw = sys.argv[2]\n"
            "dirs = [RD.assemble_anchor_pass(b, os.path.join(w, 'aw')) for b in sys.argv[3:5]]\n"
            "removed = {}\nflags = {'--drop-dips': True, '--gates-off': False}\n"
            "RD._e78_main(dirs + ['--leak', '" + KF + "', '--no-refit', '--out', os.path.join(w, 'a.json'), '--txt', os.path.join(w, 'a.txt')], flags, 'anchors', removed)\n")
    py = os.path.join(d, "a1.py")
    open(py, "w").write(code)
    os.makedirs(os.path.join(d, "aw"))
    r = run(py, HERE, d, os.path.join(E182D, "aifoundry3/e182/p18211"), os.path.join(E182D, "aifoundry3/e182/p18213"))
    res = json.load(open(os.path.join(d, "a.json"))) if os.path.exists(os.path.join(d, "a.json")) else {}
    import score_e186 as SC  # noqa: E402
    s, note = SC.read_scale(os.path.join(d, "a.json")) if res else (None, r.stderr[-300:])
    s182 = json.load(open(os.path.join(E182D, "scored.json")))["scale"]["s_float"]
    say(r.returncode == 0 and res.get("passes") == [18211, 18213] and not res.get("passes_set_aside") and s is not None and
        note.get("anchors_used") == ["fp32.randn"] and abs(s / s182 - 1) < 0.02,
        f"A1 the scale from E182's two fp32 trains' anchors: passes kept {res.get('passes')}, set aside {res.get('passes_set_aside')}, "
        f"s {s} from {note.get('anchors_used') if isinstance(note, dict) else note}; E182's own, from its kinds passes, {s182:.5f} (reported)")
    # A2 E182's reduce_train through E186's import, on E182's committed T1 and T5
    sys.path.insert(0, os.path.join(TOP, "tools/claims-v3/e182"))
    import reduce_e182 as R182  # noqa: E402
    import e186_stats as RS  # noqa: E402
    pl = json.load(open(os.path.join(TOP, "tools/claims-v3/e182/plan-e182.json")))
    tc = json.load(open(os.path.join(E182D, "trains-e182.json")))["trains"]
    ok, msg = True, []
    for b, tid in ((18215, "T1"), (18211, "T5")):
        t = next(x for x in pl["trains"] if x["block"] == b)
        v = R182.reduce_train(os.path.join(E182D, "aifoundry3/e182", f"p{b}"), RS.S, t)
        same = all(v["estimate"][k] == tc[tid]["estimate"][k] for k in ("n", "mean", "lo", "hi", "se"))
        ok = ok and same
        msg.append(f"{tid} {v['estimate']['mean']:+.6f} [{v['estimate']['lo']:+.6f}, {v['estimate']['hi']:+.6f}] equal {same}")
    say(ok, "A2 E182's reduce_train via E186's import, on E182's committed blocks: " + "; ".join(msg))
    # A3 the measured rate from the trains' own launch records
    import reduce_e186 as RD  # noqa: E402
    rates = json.load(open(os.path.join(HERE, "forecast-e186.json")))["rates_per_s"]
    ok, msg = True, []
    for t in pl["trains"]:
        rt, n = RD.train_rate(os.path.join(E182D, "aifoundry3/e182", f"p{t['block']}"), t)
        q = rt / rates[t["type"]] if rt else None
        ok = ok and q is not None and abs(q - 1) < 0.02
        msg.append(f"{t['train']} {q:.4f} ({n})" if q else f"{t['train']} none")
    say(ok, "A3 the trains' measured rate over the candidates' rate, on E182's six committed trains (reported): " + ", ".join(msg))
    r = run(os.path.join(HERE, "e186_stats.py"))
    say(r.returncode == 0 and "self-check PASS" in r.stdout, f"A4 e186_stats.py's self-check: {r.stdout.strip()[-60:]}")


def session(work, name, *args, anchors=True, fallback=False):
    d = os.path.join(work, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    r = run(os.path.join(HERE, "fake_card_e186.py"), d, *args)
    if r.returncode != 0:
        print(r.stdout[-500:], r.stderr[-1500:])
        return None, None
    cmd = [os.path.join(HERE, "score_e186.py"), "score", "--raw", os.path.join(d, "raw"), "--ccheck", os.path.join(d, "ccheck-all.json"),
           "--skip-c-gate", "--json", os.path.join(d, "scored-e186.json"), "--md", os.path.join(d, "results-e186.md")]
    if fallback:
        cmd += ["--reduction", os.path.join(d, "e186.json"), "--runs-csv", os.path.join(d, "runs.csv")]
    else:
        blocks = sorted(os.path.join(d, "raw", "e186", b) for b in os.listdir(os.path.join(d, "raw", "e186")) if b.startswith("p1861"))
        r = run(os.path.join(HERE, "reduce_e186.py"), "trains", *blocks, "--out", os.path.join(d, "trains-e186.json"))
        if r.returncode != 0:
            print(r.stderr[-1500:])
            return None, None
        cmd += ["--trains", os.path.join(d, "trains-e186.json")]
        if anchors:
            fl = [b for b in blocks if E.train_of_block(int(os.path.basename(b)[1:]))["type"] != "int8"]
            r = run(os.path.join(HERE, "reduce_e186.py"), "anchors", *fl, "--work", os.path.join(d, "aw"), "--leak", KF, "--no-refit",
                    "--drop-dips", "--out", os.path.join(d, "e186-anchors.json"), "--txt", os.path.join(d, "anchors.txt"))
            if r.returncode != 0:
                print(r.stderr[-1500:])
                return None, None
            cmd += ["--anchors", os.path.join(d, "e186-anchors.json")]
    r = run(*cmd)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        return None, None
    m = run(os.path.join(HERE, "arm_m1_read_e186.py"), "--scored", os.path.join(d, "scored-e186.json"), "--out", os.path.join(d, "arm-m1-e186"))
    arm = json.load(open(os.path.join(d, "arm-m1-e186.json"))) if m.returncode == 0 else None
    return json.load(open(os.path.join(d, "scored-e186.json"))), arm


SEP9 = ("H16", "S23", "Q63-sign", "Q63-swap", "B15-B7", "B23-B15", "Q3-sign")     # M12 and M10 9 se apart or more (E186.md section 0)


def zs(s, tids):
    """each train's z against M12's and M10's scored lines (the wiring check: |z| < 4 against the true world, > 4 against the other)"""
    import e186_stats as RS  # noqa: E402
    z12, z10 = {}, {}
    for t in tids:
        iv, ln = s["trains"][t], s["trains"][t].get("lines")
        z12[t] = RS.zscore(iv, ln["M12"][0], ln["M12"][1]) if ln and iv.get("se") else float("nan")
        z10[t] = RS.zscore(iv, ln["M10"][0], 0.0) if ln and iv.get("se") else float("nan")
    return z12, z10


def fmt(z):
    return "{" + ", ".join(f"{k} {v:+.1f}" for k, v in z.items()) + "}"


def synthetic(work):
    s, arm = session(work, "b1", "--world", "M12", "--seed", "18691")
    v, R = s["verdicts"], s["rules"]
    tids = json.load(open(os.path.join(HERE, "plan-e186.json")))["session_trains"]
    import score_e186 as SC  # noqa: E402
    z12, z10 = zs(s, tids)
    trains_ok = all(abs(z12[t]) < 4 for t in tids) and all(abs(z10[t]) > 4 for t in SEP9)
    ok = (trains_ok and v["E186-H16"] == "F16-SAME" and v["E186-SPLIT3"] == "A+B" and v["E186-SPLIT63"] == "A+B" and
          v["E186-GB"] == "POSITIVE" and R["E186-GB"]["size_M12"] == "PASS" and v["E186-GA"] == "POSITIVE" and R["E186-GA"]["size_M12"] == "PASS"
          and v["E186-S23R"] == "AGREES" and v["E186-M"] == "M12" and v["E186-TR-N"] == "AS FORECAST" and v["E186-C"] == "PASS" and
          s["scale"]["read"] and arm is not None and arm["counts"]["trains"] == {"not covered": 14, "not run": 8})
    say(ok, f"B1 M12's world: {v}; s {s['scale']['s_float']}; z against M12 {fmt(z12)}; note M1's reader {arm and arm['counts']}")
    s, _ = session(work, "b2", "--world", "M10", "--seed", "18692")
    v, R = s["verdicts"], s["rules"]
    z12, z10 = zs(s, tids)
    say(v["E186-H16"] == "M10" and all(abs(z10[t]) < 4 for t in tids) and all(abs(z12[t]) > 4 for t in SEP9) and
        R["E186-M"]["M10"]["Q"] < 40 and R["E186-M"]["M12"]["Q"] > 100,
        f"B2 M10's world: {v}; z against M10 {fmt(z10)}; E186-M's Q, M12 {R['E186-M']['M12']['Q']:.1f}, M10 {R['E186-M']['M10']['Q']:.1f}")
    s, _ = session(work, "b3", "--world", "M12-H16S", "--seed", "18693")
    say(s["verdicts"]["E186-H16"] == "SCALED", f"B3 H16 at the scaled arm: E186-H16 {s['verdicts']['E186-H16']}")
    s, _ = session(work, "b4", "--world", "M12", "--seed", "18694", "--noise-scale", "2.5")
    say(s["verdicts"]["E186-TR-N"] == "FAILS", f"B4 noise at 2.5 times: TR-N {s['verdicts']['E186-TR-N']} "
                                               f"(ratio {s['rules']['E186-TR-N'].get('largest_ratio')})")
    s, _ = session(work, "b5", "--world", "M12", "--seed", "18695", "--short", "Q3-sign:6")
    v, R = s["verdicts"], s["rules"]
    say(v["E186-Q3SIGN"] == "NOT SCORED" and v["E186-SPLIT3"] == "NOT SCORED" and v["E186-SPLIT63"] != "NOT SCORED" and
        len(R["E186-M"]["trains"]) == 8, f"B5 Q3-sign cut to 6 processes: Q3SIGN {v['E186-Q3SIGN']}, SPLIT3 {v['E186-SPLIT3']}, "
                                         f"E186-M over {len(R['E186-M']['trains'])}")
    s, _ = session(work, "b6", "--world", "M12", "--seed", "18696", "--cfail", "S23")
    v = s["verdicts"]
    say(v["E186-C"] == "FAIL" and v["E186-S23"] == "NOT SCORED" and v["E186-S23R"] == "NOT SCORED" and v["E186-H16"] == "F16-SAME",
        f"B6 a C FAIL in S23: C {v['E186-C']}, S23 {v['E186-S23']}, S23R {v['E186-S23R']}")
    s, _ = session(work, "b7", "--world", "M12", "--seed", "18697", "--no-anchors", anchors=False)
    v, R = s["verdicts"], s["rules"]
    lad = ("B15-B7", "B23-B15", "A15-A7", "A23-A15")
    ok = (not s["scale"]["read"] and all(R[SC.rule_of(t)]["size_M12"] == "NOT SCORED" and R[SC.rule_of(t)]["which"] == "NOT SCORED" and
                                         R[SC.rule_of(t)]["sign"] == "POSITIVE" for t in lad) and
          v["E186-GB"] == "NOT SCORED" and v["E186-GA"] == "NOT SCORED" and sorted(R["E186-M"]["trains"]) ==
          sorted(["S23", "Q63-sign", "Q63-swap", "Q3-sign", "Q3-swap"]) and v["E186-S23"] == "M12")
    say(ok, f"B7 fail closed, no anchors: s read {s['scale']['read']} ({str(s['scale']['note'])[:80]}); the ladders "
            f"{[(R[SC.rule_of(t)]['sign'], R[SC.rule_of(t)]['size_M12']) for t in lad]}; GB {v['E186-GB']}, GA {v['E186-GA']}; "
            f"E186-M over {R['E186-M']['trains']}")
    s, arm = session(work, "b8", "--world", "M12", "--seed", "18698", "--passes", "5", fallback=True)
    v, R = s["verdicts"], s["rules"]
    k09 = (arm or {}).get("kinds", {}).get("K09", {})
    say(v["E186-LV"] in ("M12 BETTER", "NOT RESOLVED") and "boot" in R["E186-LV"] and all(v[SC.rule_of(t)] == "NOT SCORED" for t in tids) and
        s["scale"]["read"] and k09.get("reading") == "read",
        f"B8 the fallback: LV {v['E186-LV']} ({R['E186-LV'].get('boot', {}).get('diff')}), trains NOT SCORED, s {s['scale']['s_float']}; "
        f"note M1's reader K09 {k09.get('reading')} {k09.get('measured_in_model_band')}")
    # B9 the C-session list
    import ccsessions_e186 as CS  # noqa: E402
    raw = os.path.join(work, "b9raw")
    if os.path.isdir(raw):
        shutil.rmtree(raw)
    for sub in ("e186-smoke/p18601", "e186-stoptest/p18602", "e186/p18610", "e186/p18619", "e186/p18620", "e186/p18621",
                "e186/p18620.attempt-1", "e186/p18622"):
        os.makedirs(os.path.join(raw, sub))
    open(os.path.join(raw, "e186/p18610/train.jsonl"), "w").write(json.dumps({"process": 0, "launch": 0}) + "\n")
    os.makedirs(os.path.join(raw, "e186/p18619/a0"))
    open(os.path.join(raw, "e186/p18619/a0/runs.jsonl"), "w").write(json.dumps({"item": "fp32.zeros", "launch": 0}) + "\n")
    for p in ("p18620", "p18620.attempt-1"):
        open(os.path.join(raw, "e186", p, "runs.jsonl"), "w").write(json.dumps({"item": "fp32.ones", "launch": 0}) + "\n")
    got = [os.path.relpath(x, raw) for x in CS.listed_sessions("E186", raw)]
    say(got == ["e186-smoke/p18601", "e186/p18610", "e186/p18619", "e186/p18620"], f"B9 the C-session list: {got}")
    # B10 the smoke gate's train part on a synthetic H16 smoke, then with one launch off the schedule
    res = []
    for nm, extra in (("b10", []), ("b10bad", ["--break-schedule"])):
        d = os.path.join(work, nm)
        if os.path.isdir(d):
            shutil.rmtree(d)
        run(os.path.join(HERE, "fake_card_e186.py"), d, "--smoke", *extra)
        r = run(os.path.join(HERE, "smoke_gate_e186.py"), os.path.join(d, "p18601"), os.path.join(d, "none"), "--part", "train")
        res.append((r.returncode, r.stdout.strip().splitlines()[-1][:160] if r.stdout.strip() else r.stderr[-200:]))
    say(res[0][0] == 0 and res[1][0] == 1, f"B10 the smoke gate's train part (H16, fp16): a good smoke {res[0]}; one launch off the schedule {res[1]}")


def copyback(work):
    """B11: a synthetic session directory and two blocks, its manifest written as session_e186.sh writes it, then copied as step 11 does"""
    d = os.path.join(work, "b11")
    if os.path.isdir(d):
        shutil.rmtree(d)
    box = os.path.join(d, "box")
    t0 = "1800000000"
    files = {f"build/e186/T{t0}/session.log": "session start\nsession end\n", f"build/e186/T{t0}/queue.out": "done\n",
             f"build/e186/T{t0}/blocks.txt": "build/claims-v3/aifoundry3/e186-stoptest/p18602\nbuild/claims-v3/aifoundry3/e186/p18610\n",
             "build/claims-v3/aifoundry3/e186-stoptest/p18602/block.json": "{}\n", "build/claims-v3/aifoundry3/e186/p18610/train.jsonl": "{}\n",
             "build/claims-v3/aifoundry3/e186/p18610/a0/runs.jsonl": "{}\n"}
    for p, c in files.items():
        os.makedirs(os.path.dirname(os.path.join(box, p)), exist_ok=True)
        open(os.path.join(box, p), "w").write(c)
    man = "".join(f"{hashlib.sha256(c.encode()).hexdigest()}  {p}\n" for p, c in sorted(files.items()))
    open(os.path.join(box, f"build/e186/T{t0}/MANIFEST.sha256"), "w").write(man)

    def copy(raw):
        if os.path.isdir(raw):
            shutil.rmtree(raw)
        shutil.copytree(os.path.join(box, f"build/e186/T{t0}"), os.path.join(raw, "logs"))
        for b in ("e186-stoptest/p18602", "e186/p18610"):
            shutil.copytree(os.path.join(box, "build/claims-v3/aifoundry3", b), os.path.join(raw, b))
        os.makedirs(os.path.join(raw, "logs", "step6"), exist_ok=True)
        open(os.path.join(raw, "logs", "step6", "e186-build-attempts.txt"), "w").write("a step-6 line\n")
        open(os.path.join(raw, "logs", "absent-on-box.txt"), "w").write("none\n")
    out = []
    raw = os.path.join(d, "raw")
    copy(raw)
    out.append(("exact", run(os.path.join(HERE, "copyback_e186.py"), raw, t0)))
    open(os.path.join(raw, "e186/p18610/train.jsonl"), "w").write("{} \n")
    out.append(("one byte", run(os.path.join(HERE, "copyback_e186.py"), raw, t0)))
    copy(raw)
    open(os.path.join(raw, "e186/p18610/extra.txt"), "w").write("x\n")
    out.append(("extra", run(os.path.join(HERE, "copyback_e186.py"), raw, t0)))
    copy(raw)
    os.remove(os.path.join(raw, "logs", "MANIFEST.sha256"))
    out.append(("no manifest", run(os.path.join(HERE, "copyback_e186.py"), raw, t0)))
    copy(raw)
    os.makedirs(os.path.join(raw, "e186/p18611"))
    open(os.path.join(raw, "e186/p18611/block.json"), "w").write("{}\n")
    out.append(("unnamed block", run(os.path.join(HERE, "copyback_e186.py"), raw, t0)))
    want = [(0, "COPY-BACK EXACT 6 files"), (4, "COPY-BACK DIFFERS"), (4, "COPY-BACK EXTRA"), (4, "COPY-BACK NO-MANIFEST"), (4, "COPY-BACK DIFFERS")]
    got = [(r.returncode, r.stdout.strip()) for _, r in out]
    say(all(g[0] == w[0] and g[1].startswith(w[1]) for g, w in zip(got, want)),
        "B11 the exact copy-back: " + "; ".join(f"{nm} rc {g[0]} '{g[1][:70]}'" for (nm, _), g in zip(out, got)))


def images(work):
    bad0 = []
    for k in E.E186_NAMES:
        bad0 += E.image_problems(k, open(os.path.join(TOP, E.tile_path(k)), "rb").read())
    caught = []
    for k in E.SESSION_KINDS:
        raw = bytearray(open(os.path.join(TOP, E.tile_path(k)), "rb").read())
        raw[1024 + 4 * 77] ^= 0x01                                       # one bit of one B word
        caught.append(bool(E.image_problems(k, bytes(raw))))
    short = E.image_problems(E.SESSION_KINDS[0], open(os.path.join(TOP, E.tile_path(E.SESSION_KINDS[0])), "rb").read()[:2047])
    fp16 = [E._MK[k]["a_word"] + "/" + E._MK[k]["b_word"] for k in E.E186_NAMES if k.startswith("fp16.")]
    say(not bad0 and all(caught) and bool(short), f"B12 the images: all {len(E.E186_NAMES)} hold their words ({bad0 or 'no problem'}); a changed B "
                                                  f"word caught in {sum(caught)} of {len(caught)} session kinds; a 2,047-byte image caught; "
                                                  f"the fp16 pair {fp16}")


def main():
    work = os.path.abspath(sys.argv[1])
    os.makedirs(work, exist_ok=True)
    committed(work)
    synthetic(work)
    copyback(work)
    images(work)
    print(f"SELFTEST-SCORE-E186 {N[0] - len(FAILS)} of {N[0]} PASS" + ("" if not FAILS else ": " + "; ".join(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
