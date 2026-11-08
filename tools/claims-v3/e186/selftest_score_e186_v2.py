#!/usr/bin/env python3
"""E186 kit note 1 (Q158, fix-e186): the self-test of the pairing check (pairing_e186.py) and the scorer v2 (score_e186_v2.py). No card;
it writes only under <work dir>.

ON COMMITTED DATA (E182, 8 Nov 2026, docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3/; post hoc checks of code, deciding nothing):
  P1  the pairing check on E182's six committed train blocks (T1-T6, with their C logs from the data's ccheck/): every launch record of
      every process paired, against E182's plan and registered tiles; so the desk's FNV-1a 64 of the registered tile bytes equals the
      fnv the box's C-logging host wrote in every C record;
  P2  pairing_e186.fnv64 equals ccheck.py's fnv64 on the 15 kinds' registered tiles;
  P3  E182's T4 block copied, each of four faults made in the copy of its committed record or C log (one launch's train_kind off the
      schedule; its train_values the other kind's tile; its C record's fnv the other kind's; its C record removed), and the block's C log
      removed: each caught, by the check named.
ON SYNTHETIC SESSIONS (fake_card_e186_v2.py: fake_card_e186.py's session unchanged, with every train block's C log; reduce_e186.py trains
and anchors; score_e186.py AND score_e186_v2.py on the same session; note M1's reader on v2's file):
  Q1  M12's world (v1's B1 seed): v2's file equals v1's in every rule, verdict, train and reading, plus E186-PAIR PASS over the ten trains;
      note M1's reader reads v2's file as v1's (14 not covered, 8 not run);
  Q2  M10's world (v1's B2 seed): the same equality, E186-PAIR PASS;
  Q3  FAIL CLOSED, no anchors (v1's B7 seed): the same equality; the four ladder trains' SIZE and WHICH NOT SCORED, GB and GA NOT SCORED,
      E186-M over the five trains whose lines need no s (E186.md.dated-amendment-A1.md section A1-1);
  Q4  S23 (an equal-C swap), one launch with the other kind's tiles and its records consistent (--pair-kind): E186-C PASS (the check of
      C cannot see it), E186-PAIR FAIL [S23], S23 NOT SCORED by the pairing check, S23R NOT SCORED, E186-M over the other eight, TR-N
      re-read without S23; every other train's words equal v1's;
  Q5  Q63-swap (an equal-C int8 swap), one launch's train_values the other kind's tile (--pair-values): Q63-swap NOT SCORED, SPLIT63 NOT
      SCORED, SPLIT3 equal to v1's;
  Q6  B23-B15 (a ladder), one C record with the other kind's fnv (--pair-fnv): B23-B15 NOT SCORED, E186-GB read over B15-B7's 8 bits
      alone, E186-M without it;
  Q7  Q3-sign, one C record missing (--pair-noc): Q3-sign NOT SCORED, SPLIT3 NOT SCORED;
  Q8  H16 with no C log at all (--no-clog): H16 NOT SCORED (no C log for the block), E186-M unchanged (H16 is never in it);
  Q9  the pairing check's own text on Q4's raw copy: PAIRING FAILED naming S23, every other train PAIRED.
    /usr/bin/python3 -B selftest_score_e186_v2.py <work dir>
SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
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
import pairing_e186 as PR  # noqa: E402
E182D = os.path.join(TOP, "docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3")
PY = "/usr/bin/python3"
KF = "0.20563713796102187"
FAILS, N = [], [0]
LAD = ("B15-B7", "B23-B15", "A15-A7", "A23-A15")


def say(ok, what):
    N[0] += 1
    print(("PASS " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what[:80])


def run(*args, **kw):
    return subprocess.run([PY, "-B", *args], capture_output=True, text=True, cwd=TOP, **kw)


def rule_of(tid):
    return "E186-" + tid.replace("-", "").upper()


# ------------------------------------------------------------------------------------------------------------------- committed data
def committed(work):
    sys.path.insert(0, os.path.join(TOP, "tools/claims-v3/e182"))
    import e182_common as E2  # noqa: E402
    items2 = {it["name"]: it for it in E2.load_items()}
    res, nrec = [], 0
    for b in sorted(E2.TRAINS):
        t = E2.TRAINS[b]
        d = os.path.join(E182D, "aifoundry3", "e182", f"p{b}")
        r = PR.check_block(d, t, PR.tiles_of(t, items2), PR.clog_paths(d, b, os.path.join(E182D, "ccheck")), E2.LAUNCHES)
        res.append((t["train"], r["launch_records"], r["launches_paired"], r["ok"]))
        nrec += r["launch_records"]
    say(all(x[3] and x[1] == x[2] for x in res) and len(res) == 6,
        f"P1 E182's six committed trains: {res}; {nrec} launch records, every one paired with its C record's fnv the scheduled kind's tile's")
    sys.path.insert(0, os.path.join(TOP, "tools/claims-v3/ccheck"))
    import ccheck as CC  # noqa: E402  (fnv64 only)
    items = {it["name"]: it for it in E.load_items()}
    eq = [k for k in E.E186_NAMES if PR.fnv64(open(os.path.join(TOP, items[k]["tile"]), "rb").read()) ==
          CC.fnv64(open(os.path.join(TOP, items[k]["tile"]), "rb").read())]
    say(len(eq) == 15, f"P2 pairing_e186.fnv64 equals ccheck.fnv64 on {len(eq)} of E186's 15 kinds' tiles")
    # P3: E182's T4 block, copied, each fault made in the copy
    t = E2.TRAINS[18210]
    tl = PR.tiles_of(t, items2)
    src = os.path.join(E182D, "aifoundry3", "e182", "p18210")
    got = []
    for fault in ("train_kind", "train_values", "c_fnv", "no_c_record", "no_c_log"):
        d = os.path.join(work, "p3-" + fault)
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
        recs = [json.loads(x) for x in open(os.path.join(src, "train.jsonl")) if x.strip()]
        cl = []
        with gzip.open(os.path.join(E182D, "ccheck", "c-log-p18210.jsonl.gz"), "rt") as f:
            cl = [x for x in f]
        hit = next(r for r in recs if r["process"] == 2 and r["launch"] == 5)
        key = (hit["t_start_ms"], hit["t_end_ms"])
        other = "F" if hit["train_kind"] == "S" else "S"
        if fault == "train_kind":
            hit["train_kind"] = other
        if fault == "train_values":
            hit["train_values"] = "file:/x/" + tl[other]["tile"]
        out_cl = []
        for line in cl:
            try:
                r = json.loads(line) if line.strip().startswith("{") else None
            except ValueError:
                r = None
            if isinstance(r, dict) and r.get("kind") == "c" and (r.get("t_start_ms"), r.get("t_end_ms")) == key:
                if fault == "no_c_record":
                    continue
                if fault == "c_fnv":
                    r["fnv"] = tl[other]["fnv"]
                    line = json.dumps(r) + "\n"
            out_cl.append(line)
        with open(os.path.join(d, "train.jsonl"), "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        if fault != "no_c_log":
            with open(os.path.join(d, "c-log.jsonl"), "w") as f:
                f.writelines(out_cl)
        r = PR.check_block(d, t, tl, PR.clog_paths(d, 18210), E2.LAUNCHES)
        got.append((fault, r["ok"], r["failures_by_check"], r["why"]))
    want = {"train_kind": "train_kind", "train_values": "train_values", "c_fnv": "c_fnv", "no_c_record": "no_c_record"}
    ok = all((not g[1]) and (g[0] == "no_c_log" or g[2] == {want[g[0]]: 1}) for g in got) and got[-1][3] == "no C log for the block"
    say(ok, f"P3 E182's T4 block, a fault made in a copy: {got}")


# ------------------------------------------------------------------------------------------------------------------- synthetic sessions
def session(work, name, *args, anchors=True):
    d = os.path.join(work, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    r = run(os.path.join(HERE, "fake_card_e186_v2.py"), d, *args)
    if r.returncode != 0:
        print(r.stdout[-500:], r.stderr[-1500:])
        return None, None, None
    blocks = sorted(os.path.join(d, "raw", "e186", b) for b in os.listdir(os.path.join(d, "raw", "e186")) if b.startswith("p1861"))
    r = run(os.path.join(HERE, "reduce_e186.py"), "trains", *blocks, "--out", os.path.join(d, "trains-e186.json"))
    if r.returncode != 0:
        print(r.stderr[-1500:])
        return None, None, None
    common = ["--raw", os.path.join(d, "raw"), "--ccheck", os.path.join(d, "ccheck-all.json"), "--skip-c-gate",
              "--trains", os.path.join(d, "trains-e186.json")]
    if anchors:
        fl = [b for b in blocks if E.train_of_block(int(os.path.basename(b)[1:]))["type"] != "int8"]
        r = run(os.path.join(HERE, "reduce_e186.py"), "anchors", *fl, "--work", os.path.join(d, "aw"), "--leak", KF, "--no-refit",
                "--drop-dips", "--out", os.path.join(d, "e186-anchors.json"), "--txt", os.path.join(d, "anchors.txt"))
        if r.returncode != 0:
            print(r.stderr[-1500:])
            return None, None, None
        common += ["--anchors", os.path.join(d, "e186-anchors.json")]
    out = {}
    for v, f in (("v1", "score_e186.py"), ("v2", "score_e186_v2.py")):
        os.makedirs(os.path.join(d, v), exist_ok=True)
        r = run(os.path.join(HERE, f), "score", *common, "--json", os.path.join(d, v, "scored-e186.json"), "--md",
                os.path.join(d, v, "results-e186.md"))
        if r.returncode != 0:
            print(v, r.stderr[-2000:])
            return None, None, None
        out[v] = json.load(open(os.path.join(d, v, "scored-e186.json")))
    m = run(os.path.join(HERE, "arm_m1_read_e186.py"), "--scored", os.path.join(d, "v2", "scored-e186.json"), "--out",
            os.path.join(d, "v2", "arm-m1-e186"))
    arm = json.load(open(os.path.join(d, "v2", "arm-m1-e186.json"))) if m.returncode == 0 else None
    return out["v1"], out["v2"], arm


def strip(v2):
    s = copy.deepcopy(v2)
    for k in ("pairing", "scorer_v2"):
        s.pop(k, None)
    s["rules"].pop("E186-PAIR", None)
    s["verdicts"].pop("E186-PAIR", None)
    return s


def same(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def others_equal(v1, v2, tids, skip):
    """every train rule but the skipped ones reads the same words in v1 and v2"""
    bad = [t for t in tids if t not in skip and not same(v1["rules"][rule_of(t)], v2["rules"][rule_of(t)])]
    return not bad, bad


def synthetic(work):
    tids = json.load(open(os.path.join(HERE, "plan-e186.json")))["session_trains"]
    for nm, seed, extra, anchors in (("q1", "18691", ["--world", "M12"], True), ("q2", "18692", ["--world", "M10"], True),
                                     ("q3", "18697", ["--world", "M12", "--no-anchors"], False)):
        v1, v2, arm = session(work, nm, *extra, "--seed", seed, anchors=anchors)
        if v1 is None:
            say(False, f"{nm.upper()} the session did not run")
            continue
        eq = same(strip(v2), v1)
        pr = v2["rules"]["E186-PAIR"]
        line = f"{nm.upper()} {' '.join(extra)}: v2's file equals v1's but for the pairing ({eq}); E186-PAIR {pr['verdict']} over {len(pr['trains_read'])}"
        ok = eq and pr["verdict"] == "PASS" and len(pr["trains_read"]) == 10
        if nm == "q1":
            ok = ok and arm is not None and arm["counts"]["trains"] == {"not covered": 14, "not run": 8}
            line += f"; note M1's reader on v2's file {arm and arm['counts']}"
        if nm == "q3":
            R = v2["rules"]
            ok = ok and (not v2["scale"]["read"] and all(R[rule_of(t)]["size_M12"] == "NOT SCORED" and R[rule_of(t)]["which"] == "NOT SCORED"
                                                         for t in LAD) and v2["verdicts"]["E186-GB"] == "NOT SCORED" and
                         v2["verdicts"]["E186-GA"] == "NOT SCORED" and
                         sorted(R["E186-M"]["trains"]) == sorted(["S23", "Q63-sign", "Q63-swap", "Q3-sign", "Q3-swap"]))
            line += f"; s read {v2['scale']['read']}; E186-M over {R['E186-M']['trains']} ({R['E186-M']['verdict']})"
        say(ok, line)
    cases = (("q4", "--pair-kind", "S23", ("S23R",), "train_kind"), ("q5", "--pair-values", "Q63-swap", ("SPLIT63",), "train_values"),
             ("q6", "--pair-fnv", "B23-B15", (), "c_fnv"), ("q7", "--pair-noc", "Q3-sign", ("SPLIT3",), "no_c_record"),
             ("q8", "--no-clog", "H16", (), None))
    for nm, opt, tr, ns, chk in cases:
        v1, v2, _ = session(work, nm, "--world", "M12", "--seed", "18691", opt, tr)
        if v1 is None:
            say(False, f"{nm.upper()} the session did not run")
            continue
        R1, R2, V2 = v1["rules"], v2["rules"], v2["verdicts"]
        r = R2[rule_of(tr)]
        pr = R2["E186-PAIR"]
        p = v2["pairing"]["trains"][tr]
        ok = (V2["E186-C"] == "PASS" and v1["verdicts"]["E186-C"] == "PASS" and pr["verdict"] == "FAIL" and pr["trains_not_paired"] == [tr]
              and r["verdict"] == "NOT SCORED" and "the pairing check" in str(r.get("why")) and v2["trains"][tr]["lo"] is None
              and (chk is None or p["failures_by_check"] == {chk: 1}) and all(V2[f"E186-{x}"] == "NOT SCORED" for x in ns))
        eqo, bad = others_equal(v1, v2, tids, {tr})
        ok = ok and eqo
        m = R2["E186-M"]
        if tr != "H16":
            ok = ok and tr not in m["trains"] and len(m["trains"]) == len(R1["E186-M"]["trains"]) - 1
        else:
            ok = ok and same(R1["E186-M"], m)
        if tr != "H16":
            ok = ok and R2["E186-TR-N"].get("trains_left_out_by_the_pairing_check") == [tr]
        extra = ""
        if tr == "B23-B15":
            g1, g2 = R1["E186-GB"], R2["E186-GB"]
            ok = ok and g2["verdict"] != "NOT SCORED" and g2["gamma"]["mean"] != g1["gamma"]["mean"]
            extra = f"; GB v1 {g1['gamma']['mean']:+.5f} (two ladder trains), v2 {g2['gamma']['mean']:+.5f} (B15-B7's 8 bits alone)"
        if tr == "Q63-swap":
            ok = ok and same(R1["E186-SPLIT3"], R2["E186-SPLIT3"])
        dep = ", ".join("E186-" + x + " " + V2["E186-" + x] for x in ns) or "no derived rule named"
        say(ok, f"{nm.upper()} {opt} {tr}: C {V2['E186-C']}; PAIR {pr['verdict']} {pr['trains_not_paired']} ({p['failures_by_check']}, "
                f"{p['why']}); {tr} {r['verdict']}; {dep}; "
                f"E186-M over {len(m['trains'])} ({m['verdict']}); TR-N {V2['E186-TR-N']}; other trains equal to v1: {eqo} {bad}{extra}")
    r = run(os.path.join(HERE, "pairing_e186.py"), "check", "--raw", os.path.join(work, "q4", "raw"))
    lines = r.stdout.strip().splitlines()
    ok = (r.returncode == 0 and lines[-1].startswith("PAIRING FAILED") and sum(1 for x in lines if x.strip().startswith("S23 ") and "NOT PAIRED" in x) == 1
          and sum(1 for x in lines if " PAIRED" in x and "NOT PAIRED" not in x) == 9)
    say(ok, f"Q9 the pairing check's own text on Q4's raw copy: rc {r.returncode}, '{lines[-1] if lines else ''}'")


def main():
    work = os.path.abspath(sys.argv[1])
    if (work + os.sep).startswith(TOP + os.sep):
        print("the work dir must be outside the lab repository")
        return 2
    os.makedirs(work, exist_ok=True)
    committed(work)
    synthetic(work)
    print(f"SELFTEST-SCORE-E186-V2 {N[0] - len(FAILS)} of {N[0]} {'PASS' if not FAILS else 'FAIL'}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
