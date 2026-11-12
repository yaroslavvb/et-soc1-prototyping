#!/usr/bin/env python3
"""E188 (Q165, the kit): the scorer's, the reductions', the pairing check's and the exact copy-back's self-test. No card; it writes only
under <work dir>. A port of tools/claims-v3/e186/selftest_score_e186.py (E186's kit) to E188's rules.

ON COMMITTED DATA (E186, 9 Nov 2026, docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/; post hoc checks of code, deciding
nothing):
  A1  THE SCALE ROUTE (E188.md section 4.2), by the kit's own code: reduce_e188.py's anchor passes from two of E186's committed fp32 train
      blocks (S23 p18611, B15-B7 p18614), E78's reduction on E182's registered footing, then score_e188.read_scale: both passes kept, the
      scale read from fp32.randn; and read_scale on E186's committed e186-anchors.json equals E186's scored s (1.00873) to the last bit;
  A2  E182's reduce_train, as reduce_e188.py imports it (unchanged), on the same two committed blocks: each estimate equals
      trains-e186.json's to the last bit;
  A3  the trains' measured rate from their own launch records (reduce_e188.train_rate) on E186's six committed fp32 trains, against
      forecast-e188.json's rate_fp32_per_s, reported, each within 2%;
  A4  e188_stats.py's own self-check passes;
  A5  the words E188's scorer reads with E186's functions (size_band, which), re-made from E186's committed intervals and scored lines for
      E186's twelve sized rules: every word equals scored-e186.json's;
  A6  the pairing check (pairing_e188.check_block) on E186's committed fp32 train blocks S23 and B15-B7 with their registered tiles: every
      launch record paired, as E186-PAIR read them.
ON SYNTHETIC SESSIONS (fake_card_e188.py, the box's layout; reduce_e188.py trains and anchors, score_e188.py score, as the collector runs
them; noise at half the registered for the wiring cases B1-B3, so each word read is the world's, not chance's; B4 at 3 times):
  B1  M12's world, FULL (seven trains and two kinds passes): every train within 4 se of M12's scored line; E188-M's Q under 40 for M12
      and over 100 for M10, and its word M12 at this seed; GB1 POSITIVE, SIZE
      M12 PASS, REPEAT AGREES; BPOS FLAT; GA23 POSITIVE, SIZE M12 PASS, REPEAT DIFFERS LOW (as registered for M12's world); TR-N AS
      FORECAST; C PASS; SCHED PASS over seven trains; s read from the anchors; LV NOT SCORED (FULL); the kinds-pass contrasts reported
      over six segments for the seven kinds against fp32.ones, and the tie's;
  B2  M10's world: every train within 4 se of M10's scored line; E188-M's Q under 40 for M10 and over 100 for M12 (its word is chance's
      at the 5% level and is reported: at this seed M10's Q reads 18.2, above 14.07, so the word reads NEITHER); GB1 and GA23 SIZE M12
      FAIL HIGH;
  B3  M12 with the one-bit B price moved with the bit's place (POS-6): BPOS VARIES;
  B4  noise at 3 times the forecast: TR-N FAILS;
  B5  B19 cut to 10 processes (5 units): B19 NOT SCORED, GB1 over the other four, E188-M over six;
  B6  one B10 launch FAILs the check of C: E188-C FAIL, B10 NOT SCORED, GB1 over four;
  B7  no anchors: s read from FULL's kinds passes; no anchors and no kinds pass: s unread (1 used), every train rule still scored and
      carrying "s unread (1 used)";
  B8  the fallback (five kinds passes, no train): E188-LV M12 BETTER, every train rule NOT SCORED, SCHED PASS over no train block, s read
      from the kinds passes;
  B9  ccsessions_e188's list on a synthetic raw tree: the smoke, every train block (by train.jsonl or its anchors) and every kinds pass of
      either family with a launch record, and no .attempt copy;
  B10 smoke_gate_e188.py --part train on a synthetic smoke (B05's two processes, the C log's host, tiles and C records, the dumps): PASS;
      with one launch's kind off the schedule: FAIL;
  B11 THE EXACT COPY-BACK (copyback_e188.py) on a synthetic session directory and its blocks: EXACT; one byte changed: DIFFERS; an extra
      file: EXTRA; no manifest: NO-MANIFEST; a block directory the manifest does not name: DIFFERS;
  B12 THE IMAGES of E188's fifteen kinds (e188_common.image_problems): all hold their A and B words (lq_h0's eight B words); one 32-bit word
      changed in a copy of each kind's image is caught; a 2,047-byte image is caught;
  B13 THE PAIRING CHECK (E188-SCHED): one PAIR C record carrying the other kind's tile bytes: PAIR NOT SCORED, SCHED FAIL naming PAIR,
      E188-C PASS, the other six scored; one B04 launch off the schedule with its record consistent: B04 NOT SCORED;
  B14 the C-session gate: the scorer without --skip-c-gate on a session whose listed C logs have no finished check refuses (4) and writes
      nothing.
    /usr/bin/python3 -B selftest_score_e188.py <work dir>
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
import e188_common as E  # noqa: E402
E186D = os.path.join(TOP, "docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3")
PY = "/usr/bin/python3"
KF = "0.20563713796102187"
FAILS, N = [], [0]
TIDS = ("B05", "PAIR", "B19", "AALL", "B10", "B22", "B04")


def say(ok, what):
    N[0] += 1
    print(("PASS " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


def run(*args, **kw):
    return subprocess.run([PY, "-B", *args], capture_output=True, text=True, cwd=TOP, **kw)


def committed(work):
    import score_e188 as SC  # noqa: E402
    # A1 the scale route on two of E186's committed fp32 trains, and on E186's committed anchors' reduction
    d = os.path.join(work, "a1")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "aw"))
    code = ("import sys, json, os\nsys.path.insert(0, sys.argv[1])\nimport reduce_e188 as RD\n"
            "e188 = RD.refuse_unless_frozen()\nw = sys.argv[2]\n"
            "dirs = [RD.assemble_anchor_pass(b, os.path.join(w, 'aw')) for b in sys.argv[3:5]]\n"
            "removed = {}\nflags = {'--drop-dips': True, '--gates-off': False}\n"
            "RD._e78_main(dirs + ['--leak', '" + KF + "', '--no-refit', '--out', os.path.join(w, 'a.json'), '--txt', os.path.join(w, 'a.txt')], flags, 'anchors', removed)\n")
    py = os.path.join(d, "a1.py")
    open(py, "w").write(code)
    r = run(py, HERE, d, os.path.join(E186D, "aifoundry3/e186/p18611"), os.path.join(E186D, "aifoundry3/e186/p18614"))
    res = json.load(open(os.path.join(d, "a.json"))) if os.path.exists(os.path.join(d, "a.json")) else {}
    s, note = SC.read_scale(os.path.join(d, "a.json")) if res else (None, r.stderr[-300:])
    s186 = json.load(open(os.path.join(E186D, "scored-e186.json")))["scale"]["s_float"]
    s2, note2 = SC.read_scale(os.path.join(E186D, "e186-anchors.json"))
    say(r.returncode == 0 and res.get("passes") == [18611, 18614] and not res.get("passes_set_aside") and s is not None and
        isinstance(note, dict) and note.get("anchors_used") == ["fp32.randn"] and abs(s / s186 - 1) < 0.02 and s2 == s186,
        f"A1 the scale route: from two of E186's committed fp32 trains' anchors, passes kept {res.get('passes')}, s {s} from "
        f"{note.get('anchors_used') if isinstance(note, dict) else note}; from E186's committed anchors' reduction {s2} (E186's scored {s186})")
    # A2 E182's reduce_train through E188's import, on the same two blocks
    sys.path.insert(0, os.path.join(TOP, "tools/claims-v3/e182"))
    import reduce_e182 as R182  # noqa: E402
    import e188_stats as E8  # noqa: E402
    pl = json.load(open(os.path.join(TOP, "tools/claims-v3/e186/plan-e186.json")))
    tc = json.load(open(os.path.join(E186D, "trains-e186.json")))["trains"]
    ok, msg = True, []
    for b in (18611, 18614):
        t = next(x for x in pl["trains"] if x["block"] == b)
        v = R182.reduce_train(os.path.join(E186D, "aifoundry3/e186", f"p{b}"), E8.S, t)
        same = all(v["estimate"][k] == tc[t["train"]]["estimate"][k] for k in ("n", "mean", "lo", "hi", "se"))
        ok = ok and same
        msg.append(f"{t['train']} {v['estimate']['mean']:+.6f} [{v['estimate']['lo']:+.6f}, {v['estimate']['hi']:+.6f}] equal {same}")
    say(ok, "A2 E182's reduce_train via E188's import, on E186's committed blocks: " + "; ".join(msg))
    # A3 the measured rate from the trains' own launch records
    import reduce_e188 as RD  # noqa: E402
    rate = json.load(open(os.path.join(HERE, "forecast-e188.json")))["rate_fp32_per_s"]
    ok, msg = True, []
    for t in pl["trains"]:
        if t["type"] != "fp32":
            continue
        rt, n = RD.train_rate(os.path.join(E186D, "aifoundry3/e186", f"p{t['block']}"), t)
        q = rt / rate if rt else None
        ok = ok and q is not None and abs(q - 1) < 0.02
        msg.append(f"{t['train']} {q:.4f} ({n})" if q else f"{t['train']} none")
    say(ok, "A3 the trains' measured rate over forecast-e188.json's fp32 rate, on E186's committed fp32 trains (reported): " + ", ".join(msg))
    r = run(os.path.join(HERE, "e188_stats.py"))
    say(r.returncode == 0 and "self-check PASS" in r.stdout, f"A4 e188_stats.py's self-check: {r.stdout.strip()[-60:]}")
    # A5 E186's committed SIZE and WHICH words re-made by the functions E188's scorer calls
    sc = json.load(open(os.path.join(E186D, "scored-e186.json")))
    R = E8.R
    n, bad = 0, []
    for rn, v in sc["rules"].items():
        if "size_M12" not in v or "lines_w" not in v or "estimate" not in v:
            continue
        iv, ln = v["estimate"], v["lines_w"]
        w12, w10 = R.size_band(iv, ln["M12"], ln["M12_se"]), R.size_band(iv, ln["M10"], 0.0)
        n += 1
        if (w12, w10, R.which(w12, w10)) != (v["size_M12"], v["size_M10"], v["which"]):
            bad.append(rn)
    say(n >= 10 and not bad, f"A5 E186's committed SIZE and WHICH words re-made by e186_stats' size_band and which (E188's calls): {n} rules, "
                             f"{len(bad)} differ {bad}")
    # A6 the pairing check on E186's committed fp32 train blocks
    import pairing_e188 as PR  # noqa: E402
    items186 = {k["key"]: k for k in json.load(open(os.path.join(TOP, "tools/claims-v3/m12/kinds-m12-e186.json")))["kinds"]}
    ok, msg = True, []
    for b in (18611, 18614):
        t = dict(next(x for x in pl["trains"] if x["block"] == b))
        tiles = {}
        for kk, nm in (("F", t["first"]), ("S", t["second"])):
            raw = open(os.path.join(TOP, items186[nm]["tile"]), "rb").read()
            tiles[kk] = {"name": nm, "tile": items186[nm]["tile"], "fnv": PR.fnv64(raw), "sha256": items186[nm]["sha256"]}
        d = os.path.join(E186D, "aifoundry3/e186", f"p{b}")
        res = PR.check_block(d, t, tiles, PR.clog_paths(d, b, os.path.join(E186D, "ccheck")), 13)
        ok = ok and res["ok"] and res["launches_paired"] == res["launch_records"] == 76 * 14
        msg.append(f"{t['train']} {res['launches_paired']} of {res['launch_records']} paired ({res['c_log']})")
    say(ok, "A6 the pairing check on E186's committed fp32 train blocks: " + "; ".join(msg))


def session(work, name, *args, anchors=True, fallback=False, trains=True, skip_c=True):
    d = os.path.join(work, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    r = run(os.path.join(HERE, "fake_card_e188.py"), d, *args)
    if r.returncode != 0:
        print(r.stdout[-500:], r.stderr[-1500:])
        return None
    cmd = [os.path.join(HERE, "score_e188.py"), "score", "--raw", os.path.join(d, "raw"), "--ccheck", os.path.join(d, "ccheck-all.json"),
           "--json", os.path.join(d, "scored-e188.json"), "--md", os.path.join(d, "results-e188.md")]
    if skip_c:
        cmd.append("--skip-c-gate")
    if os.path.exists(os.path.join(d, "e188.json")):
        cmd += ["--reduction", os.path.join(d, "e188.json"), "--runs-csv", os.path.join(d, "runs.csv")]
    if trains and not fallback:
        blocks = sorted(os.path.join(d, "raw", "e188", b) for b in os.listdir(os.path.join(d, "raw", "e188")) if b.startswith("p1881"))
        r = run(os.path.join(HERE, "reduce_e188.py"), "trains", *blocks, "--out", os.path.join(d, "trains-e188.json"))
        if r.returncode != 0:
            print(r.stderr[-1500:])
            return None
        cmd += ["--trains", os.path.join(d, "trains-e188.json")]
        if anchors:
            r = run(os.path.join(HERE, "reduce_e188.py"), "anchors", *blocks, "--work", os.path.join(d, "aw"), "--leak", KF, "--no-refit",
                    "--drop-dips", "--out", os.path.join(d, "e188-anchors.json"), "--txt", os.path.join(d, "anchors.txt"))
            if r.returncode != 0:
                print(r.stderr[-1500:])
                return None
            cmd += ["--anchors", os.path.join(d, "e188-anchors.json")]
    r = run(*cmd)
    if r.returncode != 0:
        return {"_rc": r.returncode, "_stderr": r.stderr[-600:], "_written": os.path.exists(os.path.join(d, "scored-e188.json"))}
    return json.load(open(os.path.join(d, "scored-e188.json")))


def zs(s, tids):
    import e188_stats as E8  # noqa: E402
    z12, z10 = {}, {}
    for t in tids:
        iv, ln = s["trains"][t], s["trains"][t].get("lines")
        z12[t] = E8.R.zscore(iv, ln["M12_w"], ln["M12_se_w"]) if ln and iv.get("se") else float("nan")
        z10[t] = E8.R.zscore(iv, ln["M10_w"], 0.0) if ln and iv.get("se") else float("nan")
    return z12, z10


def fmt(z):
    return "{" + ", ".join(f"{k} {v:+.1f}" for k, v in z.items()) + "}"


def synthetic(work):
    s = session(work, "b1", "--world", "M12", "--seed", "18891", "--noise-scale", "0.5")
    v, R = s["verdicts"], s["rules"]
    z12, z10 = zs(s, TIDS)
    kvo = s["reported"].get("kinds_vs_ones", {})
    ok = (all(abs(z12[t]) < 4 for t in TIDS) and R["E188-M"]["M12"]["Q"] < 40 and R["E188-M"]["M10"]["Q"] > 100 and
          v["E188-M"] == "M12" and v["E188-GB1"] == "POSITIVE" and R["E188-GB1"]["size_M12"] == "PASS"
          and R["E188-GB1"]["repeat_E186_GB"] == "AGREES" and v["E188-BPOS"] == "FLAT" and v["E188-GA23"] == "POSITIVE" and
          R["E188-GA23"]["size_M12"] == "PASS" and R["E188-GA23"]["repeat_E186_GA"] == "DIFFERS LOW" and v["E188-TR-N"] == "AS FORECAST" and
          v["E188-C"] == "PASS" and v["E188-SCHED"] == "PASS" and len(R["E188-SCHED"]["trains_checked"]) == 7 and s["scale"]["read"] and
          s["scale"]["tries"][0]["from"].startswith("the trains' anchors") and v["E188-LV"] == "NOT SCORED" and s["plan"] == "FULL" and
          len(kvo) == 7 and all(x.get("segments") == 6 for x in kvo.values()) and s["reported"]["tie"]["passes"] == 2)
    say(ok, f"B1 M12's world, FULL: {v}; GB1 {R['E188-GB1'].get('size_M12')}/{R['E188-GB1'].get('repeat_E186_GB')}, GA23 "
            f"{R['E188-GA23'].get('size_M12')}/{R['E188-GA23'].get('repeat_E186_GA')}; s {s['scale']['s_float']}; z against M12 {fmt(z12)}; "
            f"kinds-pass contrasts {len(kvo)} kinds, segments {sorted({x.get('segments') for x in kvo.values()})}")
    s = session(work, "b2", "--world", "M10", "--seed", "18892", "--noise-scale", "0.5")
    v, R = s["verdicts"], s["rules"]
    z12, z10 = zs(s, TIDS)
    say(R["E188-M"]["M10"]["Q"] < 40 and R["E188-M"]["M12"]["Q"] > 100 and R["E188-GB1"]["size_M12"] == "FAIL HIGH" and
        R["E188-GA23"]["size_M12"] == "FAIL HIGH" and all(abs(z10[t]) < 4 for t in TIDS),
        f"B2 M10's world: {v}; z against M10 {fmt(z10)}; E188-M's Q, M12 {R['E188-M']['M12']['Q']:.1f}, M10 {R['E188-M']['M10']['Q']:.1f} "
        f"(word {v['E188-M']}, reported)")
    s = session(work, "b3", "--world", "POS-6", "--seed", "18893", "--noise-scale", "0.5")
    say(s["verdicts"]["E188-BPOS"] == "VARIES", f"B3 the one-bit B price moved with the place (POS-6): BPOS {s['verdicts']['E188-BPOS']} "
                                                f"(Q {s['rules']['E188-BPOS'].get('flat_q', {}).get('Q')})")
    s = session(work, "b4", "--world", "M12", "--seed", "18894", "--noise-scale", "3.0")
    say(s["verdicts"]["E188-TR-N"] == "FAILS", f"B4 noise at 3 times: TR-N {s['verdicts']['E188-TR-N']} (ratio {s['rules']['E188-TR-N'].get('ratio')})")
    s = session(work, "b5", "--world", "M12", "--seed", "18895", "--noise-scale", "0.5", "--short", "B19:10")
    v, R = s["verdicts"], s["rules"]
    say(v["E188-B19"] == "NOT SCORED" and R["E188-GB1"].get("trains") == ["B04", "B05", "B10", "B22"] and len(R["E188-M"]["trains"]) == 6,
        f"B5 B19 cut to 10 processes: B19 {v['E188-B19']} ({R['E188-B19'].get('why')}), GB1 over {R['E188-GB1'].get('trains')}, "
        f"E188-M over {len(R['E188-M']['trains'])}")
    s = session(work, "b6", "--world", "M12", "--seed", "18896", "--noise-scale", "0.5", "--cfail", "B10")
    v, R = s["verdicts"], s["rules"]
    say(v["E188-C"] == "FAIL" and v["E188-B10"] == "NOT SCORED" and R["E188-GB1"].get("trains") == ["B04", "B05", "B19", "B22"],
        f"B6 a C FAIL in B10: C {v['E188-C']}, B10 {v['E188-B10']}, GB1 over {R['E188-GB1'].get('trains')}")
    s = session(work, "b7", "--world", "M12", "--seed", "18897", "--noise-scale", "0.5", "--no-anchors", anchors=False)
    s2 = session(work, "b7b", "--world", "M12", "--seed", "18897", "--noise-scale", "0.5", "--no-anchors", "--full-passes", "0", anchors=False)
    ok = (s["scale"]["read"] and s["scale"]["tries"][-1]["from"].startswith("the session's kinds passes") and
          not s2["scale"]["read"] and s2["scale"]["word"] == "s unread (1 used)" and s2["scale"]["s_used"] == 1.0 and
          all(s2["verdicts"][f"E188-{t}"] != "NOT SCORED" and s2["rules"][f"E188-{t}"].get("s_word") == "s unread (1 used)" for t in TIDS)
          and s2["verdicts"]["E188-GB1"] != "NOT SCORED")
    say(ok, f"B7 no anchors: s {s['scale']['s_float']} from {s['scale']['tries'][-1]['from']}; no anchors and no kinds pass: s read "
            f"{s2['scale']['read']}, used {s2['scale']['s_used']}, {s2['scale']['word']}; the train words {[s2['verdicts'][f'E188-{t}'] for t in TIDS]}")
    s = session(work, "b8", "--world", "M12", "--seed", "18898", "--passes", "5", fallback=True)
    v, R = s["verdicts"], s["rules"]
    say(v["E188-LV"] == "M12 BETTER" and all(v[f"E188-{t}"] == "NOT SCORED" for t in TIDS) and v["E188-SCHED"] == "PASS" and
        not R["E188-SCHED"]["trains_checked"] and s["scale"]["read"] and s["plan"] == "PASSES",
        f"B8 the fallback: LV {v['E188-LV']} ({R['E188-LV'].get('boot', {}).get('diff')}), trains NOT SCORED, SCHED {v['E188-SCHED']} "
        f"({R['E188-SCHED'].get('why')}), s {s['scale']['s_float']}")
    # B9 the C-session list
    import ccsessions_e188 as CS  # noqa: E402
    raw = os.path.join(work, "b9raw")
    if os.path.isdir(raw):
        shutil.rmtree(raw)
    for sub in ("e188-smoke/p18801", "e188-stoptest/p18802", "e188/p18810", "e188/p18816", "e188/p18820", "e188/p18821",
                "e188/p18820.attempt-1", "e188/p18830", "e188/p18831"):
        os.makedirs(os.path.join(raw, sub))
    open(os.path.join(raw, "e188/p18810/train.jsonl"), "w").write(json.dumps({"process": 0, "launch": 0}) + "\n")
    os.makedirs(os.path.join(raw, "e188/p18816/a0"))
    open(os.path.join(raw, "e188/p18816/a0/runs.jsonl"), "w").write(json.dumps({"item": "fp32.zeros", "launch": 0}) + "\n")
    for p in ("p18820", "p18820.attempt-1", "p18830"):
        open(os.path.join(raw, "e188", p, "runs.jsonl"), "w").write(json.dumps({"item": "fp32.ones", "launch": 0}) + "\n")
    got = [os.path.relpath(x, raw) for x in CS.listed_sessions("E188", raw)]
    say(got == ["e188-smoke/p18801", "e188/p18810", "e188/p18816", "e188/p18820", "e188/p18830"], f"B9 the C-session list: {got}")
    # B10 the smoke gate's train part on a synthetic B05 smoke, then with one launch off the schedule
    res = []
    for nm, extra in (("b10", []), ("b10bad", ["--break-schedule"])):
        d = os.path.join(work, nm)
        if os.path.isdir(d):
            shutil.rmtree(d)
        run(os.path.join(HERE, "fake_card_e188.py"), d, "--smoke", *extra)
        r = run(os.path.join(HERE, "smoke_gate_e188.py"), os.path.join(d, "p18801"), os.path.join(d, "none"), "--part", "train")
        res.append((r.returncode, r.stdout.strip().splitlines()[-1][:160] if r.stdout.strip() else r.stderr[-200:]))
    say(res[0][0] == 0 and res[1][0] == 1, f"B10 the smoke gate's train part (B05): a good smoke {res[0]}; one launch off the schedule {res[1]}")
    # B13 the pairing check's two faults
    s = session(work, "b13", "--world", "M12", "--seed", "18899", "--noise-scale", "0.5", "--swap-fnv", "PAIR")
    v, R = s["verdicts"], s["rules"]
    s2 = session(work, "b13b", "--world", "M12", "--seed", "18899", "--noise-scale", "0.5", "--off-schedule", "B04")
    v2, R2 = s2["verdicts"], s2["rules"]
    say(v["E188-PAIR"] == "NOT SCORED" and v["E188-SCHED"] == "FAIL" and R["E188-SCHED"]["trains_not_paired"] == ["PAIR"] and
        v["E188-C"] == "PASS" and all(v[f"E188-{t}"] != "NOT SCORED" for t in TIDS if t != "PAIR") and
        v2["E188-B04"] == "NOT SCORED" and R2["E188-SCHED"]["trains_not_paired"] == ["B04"] and v2["E188-C"] == "PASS",
        f"B13 the pairing check: a PAIR C record of the other tiles: PAIR {v['E188-PAIR']}, SCHED {v['E188-SCHED']} "
        f"{R['E188-SCHED'].get('trains_not_paired')}, C {v['E188-C']}; a B04 launch off the schedule: B04 {v2['E188-B04']}, "
        f"SCHED {R2['E188-SCHED'].get('trains_not_paired')}")
    # B14 the C-session gate
    s = session(work, "b14", "--world", "M12", "--seed", "18900", "--noise-scale", "0.5", skip_c=False)
    say(isinstance(s, dict) and s.get("_rc") == 4 and not s.get("_written"),
        f"B14 the C-session gate without a finished check of C: rc {s.get('_rc')}, scored file written {s.get('_written')}")


def copyback(work):
    """B11: a synthetic session directory and two blocks, its manifest written as session_e188.sh writes it, then copied as step 11 does"""
    d = os.path.join(work, "b11")
    if os.path.isdir(d):
        shutil.rmtree(d)
    box = os.path.join(d, "box")
    t0 = "1800000000"
    files = {f"build/e188/T{t0}/session.log": "session start\nsession end\n", f"build/e188/T{t0}/queue.out": "done\n",
             f"build/e188/T{t0}/blocks.txt": "build/claims-v3/aifoundry3/e188-stoptest/p18802\nbuild/claims-v3/aifoundry3/e188/p18810\n",
             "build/claims-v3/aifoundry3/e188-stoptest/p18802/block.json": "{}\n", "build/claims-v3/aifoundry3/e188/p18810/train.jsonl": "{}\n",
             "build/claims-v3/aifoundry3/e188/p18810/a0/runs.jsonl": "{}\n"}
    for p, c in files.items():
        os.makedirs(os.path.dirname(os.path.join(box, p)), exist_ok=True)
        open(os.path.join(box, p), "w").write(c)
    man = "".join(f"{hashlib.sha256(c.encode()).hexdigest()}  {p}\n" for p, c in sorted(files.items()))
    open(os.path.join(box, f"build/e188/T{t0}/MANIFEST.sha256"), "w").write(man)

    def copy(raw):
        if os.path.isdir(raw):
            shutil.rmtree(raw)
        shutil.copytree(os.path.join(box, f"build/e188/T{t0}"), os.path.join(raw, "logs"))
        for b in ("e188-stoptest/p18802", "e188/p18810"):
            shutil.copytree(os.path.join(box, "build/claims-v3/aifoundry3", b), os.path.join(raw, b))
        os.makedirs(os.path.join(raw, "logs", "step6"), exist_ok=True)
        open(os.path.join(raw, "logs", "step6", "e188-build-attempts.txt"), "w").write("a step-6 line\n")
        open(os.path.join(raw, "logs", "absent-on-box.txt"), "w").write("none\n")
    out = []
    raw = os.path.join(d, "raw")
    copy(raw)
    out.append(("exact", run(os.path.join(HERE, "copyback_e188.py"), raw, t0)))
    open(os.path.join(raw, "e188/p18810/train.jsonl"), "w").write("{} \n")
    out.append(("one byte", run(os.path.join(HERE, "copyback_e188.py"), raw, t0)))
    copy(raw)
    open(os.path.join(raw, "e188/p18810/extra.txt"), "w").write("x\n")
    out.append(("extra", run(os.path.join(HERE, "copyback_e188.py"), raw, t0)))
    copy(raw)
    os.remove(os.path.join(raw, "logs", "MANIFEST.sha256"))
    out.append(("no manifest", run(os.path.join(HERE, "copyback_e188.py"), raw, t0)))
    copy(raw)
    os.makedirs(os.path.join(raw, "e188/p18811"))
    open(os.path.join(raw, "e188/p18811/block.json"), "w").write("{}\n")
    out.append(("unnamed block", run(os.path.join(HERE, "copyback_e188.py"), raw, t0)))
    want = [(0, "COPY-BACK EXACT 6 files"), (4, "COPY-BACK DIFFERS"), (4, "COPY-BACK EXTRA"), (4, "COPY-BACK NO-MANIFEST"), (4, "COPY-BACK DIFFERS")]
    got = [(r.returncode, r.stdout.strip()) for _, r in out]
    say(all(g[0] == w[0] and g[1].startswith(w[1]) for g, w in zip(got, want)),
        "B11 the exact copy-back: " + "; ".join(f"{nm} rc {g[0]} '{g[1][:70]}'" for (nm, _), g in zip(out, got)))


def images(work):
    bad0 = []
    for k in E.E188_NAMES:
        bad0 += E.image_problems(k, open(os.path.join(TOP, E.tile_path(k)), "rb").read())
    caught = []
    for k in E.E188_NAMES:
        raw = bytearray(open(os.path.join(TOP, E.tile_path(k)), "rb").read())
        raw[1024 + 4 * 77] ^= 0x01                                       # one bit of one B word
        caught.append(bool(E.image_problems(k, bytes(raw))))
    short = E.image_problems(E.E188_NAMES[0], open(os.path.join(TOP, E.tile_path(E.E188_NAMES[0])), "rb").read()[:2047])
    lq = len(E.words_of("fp32.lq_h0")[1])
    say(not bad0 and all(caught) and bool(short) and lq == 8,
        f"B12 the images: all {len(E.E188_NAMES)} hold their words ({bad0 or 'no problem'}; lq_h0's B words {lq}); a changed B word caught "
        f"in {sum(caught)} of {len(caught)}; a 2,047-byte image caught")


def main():
    work = os.path.abspath(sys.argv[1])
    os.makedirs(work, exist_ok=True)
    committed(work)
    synthetic(work)
    copyback(work)
    images(work)
    print(f"SELFTEST-SCORE-E188 {N[0] - len(FAILS)} of {N[0]} PASS" + ("" if not FAILS else ": " + "; ".join(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
