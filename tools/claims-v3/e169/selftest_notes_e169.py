#!/usr/bin/env python3
"""E169 (Q141(s), the fix pass after its verifier, Wed 4 Nov 2026): the self-test of the two dated notes, REGISTRATION-A2.md.dated-note-2.md
and README.md.dated-note.md. Desk only: no card, no device command, no lab box, and no E169 data (none exists). It changes nothing frozen. It
imports unchanged the frozen scorer (score_e169.py), the reduction (reduce_e169.py), the queue (queue_e169.py, whose smoke check it calls on
files) and the committed self-test's made-up reductions (selftest_e169.py). It runs E169's runner only with --dry, on run_hpl.py's toy card,
and it refuses to run on a host with an ET-SoC-1 device node.

    nice -n 10 python3 -B tools/claims-v3/e169/selftest_notes_e169.py --work <an empty scratch dir outside the tree> > tools/claims-v3/e169/selftest-notes.txt

1. A negative step (note-2, item 1). Made-up passes through score_e169.score(): a decisive pair whose whole 95% interval lies below -3.0
   points reads "NONE OF THE THREE: below every zone", its presence UNRESOLVED and its size NOT SM, and the verdict UNRESOLVED; the same
   with the other decisive pair PRESENT (SM or NOT SM) or ABSENT; one on the -3.0 edge; one on the reported pair P2/N2. Then a sweep of
   each decisive pair's step from -10% to +45% in 0.5-point steps: a presence is UNRESOLVED exactly when its interval holds -3.0 or +3.0
   points (an edge) or lies wholly below -3.0 points (a negative step), never both; the verdict is UNRESOLVED exactly when a decisive
   presence is.
2. A pass split across two sessions (note-2, item 2; README note, step 7). E158's committed session is cut in two inside its pass 2
   (block C), as a resume would leave it: each run in one session only, the second session's SP start dump the first's last dump.
   reduce_e169 on the two must give E158's committed per-pass and per-shape T800s, launch counts and checks of C exactly, and the step
   machinery the same readings on E158's four committed collapses, some of them split across the two sessions.
3. A dry pass in the real run directory (README note, step 4). The runner refuses a directory that holds a session (exit 2), and the
   queue's smoke check, reading the dry records left there, fails a real queue on their cycles, so the queue would halt with no session.
4. The zero tiles (README note, step 2). Every tile the six protocols name is in frozen-sha256-e169-tiles.txt, 2,048 bytes, every byte
   zero, with the listed sha256.
5. B7's point (note-2, item 3). score_e169.b7 reads the point as |measured / SM - 1| <= 3%, E158's convention: +3.05% fails and
   -2.95% passes, where |SM / measured - 1| <= 3% would read the two the other way.
6. The count (README note). selftest_e169.py's part 3 makes 22 checks on 17 made-up reductions (calls of score()).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import contextlib
import glob
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e158"))
import reduce_e169 as RE  # noqa: E402
import score_e169 as SC  # noqa: E402
import selftest_e169 as ST  # noqa: E402

E158D = os.path.join(LAB, "docs/reports/data/2026-11-03-e158-l3-retention")
FAILS = []


def say(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def rt(x):
    return json.loads(json.dumps(x, default=lambda o: None))


# ------------------------------------------------------------------ 1. a negative step
def part1(rule, pred, kit):
    hyp = rule["hypotheses"]
    band = rule["rule"]["band_points"] / 100.0
    iso = ST.model_T(pred, "ISO")
    ties = rule["ties_e158"]["T800"]
    sm = {k: hyp[k]["fp32"]["steps"]["SM"] for k in ("P1/N1", "P2/N2", "P3/N3")}

    def at(steps):
        """the six shapes at ISO's frozen T800, each named pair's P at its N times (1 + step)"""
        T = dict(iso)
        for P, N in SC.PAIRS:
            if f"{P}/{N}" in steps:
                T[P] = iso[N] * (1 + steps[f"{P}/{N}"])
        return SC.score(ST.fake(T, ties=ties), rule, pred, kit)

    def negative(x):
        """the notes' 'a negative step': a pair with a reading whose whole 95% interval lies below -3.0 points"""
        return x["reading"] != "NO READING" and x["hi"] < -band

    def edge(x):
        """an interval that holds -3.0 or +3.0 points (the no-step zone's edges on P1/N1 and P3/N3)"""
        return x["reading"] != "NO READING" and (x["lo"] <= -band <= x["hi"] or x["lo"] <= band <= x["hi"])

    def line(v, k):
        x = v["steps"][k]
        return f"{k} {100 * x['step']:+.2f}% [{100 * x['lo']:+.2f}, {100 * x['hi']:+.2f}] '{x['reading']}', presence {x['presence']}, size {x['size']}"

    v = at({"P1/N1": -0.06, "P3/N3": -0.06})
    a, b = v["steps"]["P1/N1"], v["steps"]["P3/N3"]
    say(all(negative(x) and x["reading"].startswith("NONE OF THE THREE: below every zone") and x["presence"] == "UNRESOLVED" and x["size"] == "NOT SM"
            for x in (a, b)) and v["verdict"] == "UNRESOLVED",
        f"both decisive pairs at -6%: {line(v, 'P1/N1')}; {line(v, 'P3/N3')} -> VERDICT {v['verdict']}")
    for name, steps, want in (("P1/N1 at +30% (a step, not SM's size), P3/N3 at -6%", {"P1/N1": 0.30, "P3/N3": -0.06}, "PRESENT"),
                              ("P1/N1 at SM's step, P3/N3 at -6%", {"P1/N1": sm["P1/N1"], "P3/N3": -0.06}, "PRESENT"),
                              ("P1/N1 at 0 (no step), P3/N3 at -6%", {"P1/N1": 0.0, "P3/N3": -0.06}, "ABSENT")):
        v = at(steps)
        b = v["steps"]["P3/N3"]
        say(v["steps"]["P1/N1"]["presence"] == want and negative(b) and b["presence"] == "UNRESOLVED" and v["verdict"] == "UNRESOLVED",
            f"{name}: P1/N1 presence {v['steps']['P1/N1']['presence']}, size {v['steps']['P1/N1']['size']}; {line(v, 'P3/N3')} -> VERDICT {v['verdict']}")
    v = at({"P1/N1": -0.030, "P3/N3": 0.0})
    a = v["steps"]["P1/N1"]
    say(edge(a) and not negative(a) and a["reading"].startswith("UNRESOLVED: crosses the edge") and a["presence"] == "UNRESOLVED" and v["verdict"] == "UNRESOLVED",
        f"P1/N1 on the -3.0 edge, P3/N3 at 0: {line(v, 'P1/N1')} -> VERDICT {v['verdict']} (the table's 'a presence crosses its edge')")
    v = at({"P1/N1": sm["P1/N1"], "P2/N2": -0.06, "P3/N3": sm["P3/N3"]})
    c = v["steps"]["P2/N2"]
    say(v["verdict"] == "INDEX STEP AS SM" and c["reading"].startswith("NONE OF THE THREE: below every zone") and c["decisive"] is False,
        f"P2/N2 (reported, not counted) at -6%, both decisive pairs at SM's steps: P2/N2 '{c['reading']}' -> VERDICT {v['verdict']} (unchanged by it)")
    n = n_neg = n_edge = 0
    bad = []
    for k in ("P1/N1", "P3/N3"):
        other = "P3/N3" if k == "P1/N1" else "P1/N1"
        for i in range(-200, 901, 10):
            s = i / 2000.0
            v = at({k: s, other: sm[other]})
            x = v["steps"][k]
            ng, ed = negative(x), edge(x)
            n += 1
            n_neg += ng
            n_edge += ed
            ok = ((x["presence"] == "UNRESOLVED") == (ng or ed)) and not (ng and ed)
            ok = ok and (ng == x["reading"].startswith("NONE OF THE THREE: below every zone"))
            ok = ok and (not ng or x["size"] == "NOT SM")
            ok = ok and ((v["verdict"] == "UNRESOLVED") == (x["presence"] == "UNRESOLVED"))
            if not ok:
                bad.append(f"{k} {100 * s:+.1f}%")
    say(not bad, f"sweep, {n} made-up sessions (each decisive pair's step -10% to +45% by 0.5 points, the other at SM's): presence UNRESOLVED exactly when "
                 f"the interval holds -3.0 or +3.0 points ({n_edge}) or lies wholly below -3.0 points ({n_neg}), never both; every negative step reads "
                 f"'NONE OF THE THREE: below every zone' with size NOT SM; the verdict UNRESOLVED exactly then" + (f"; wrong at {bad}" if bad else ""))


# ------------------------------------------------------------------ 2. a pass split across two sessions
def split_session(src, dst1, dst2, k):
    """E158's session src cut after its k-th run: each run, its launches, its sampler file and its SP dump in one of two sessions; every
    session-level file in both; the second session's SP start dump the first's last run's dump (the trace a resumed session reads first)"""
    runs = [json.loads(x) for x in open(os.path.join(src, "runs.jsonl"))]
    parts = ((dst1, runs[:k]), (dst2, runs[k:]))
    lp = os.path.join(src, "launches.jsonl.gz")
    launches = [json.loads(x) for x in gzip.open(lp, "rt")]
    for d, rr in parts:
        os.makedirs(os.path.join(d, "tel"))
        os.makedirs(os.path.join(d, "sp"))
        os.makedirs(os.path.join(d, "logs"))
        for f in os.listdir(src):
            p = os.path.join(src, f)
            if os.path.isfile(p) and f not in ("runs.jsonl", "launches.jsonl.gz"):
                shutil.copy2(p, os.path.join(d, f))
        names = {r["run"] for r in rr}
        with open(os.path.join(d, "runs.jsonl"), "w") as f:
            for r in rr:
                f.write(json.dumps(r) + "\n")
        with gzip.open(os.path.join(d, "launches.jsonl.gz"), "wt") as f:
            for L in launches:
                if L.get("run") in names:
                    f.write(json.dumps(L) + "\n")
        for r in rr:
            tel = os.path.join(src, r["tel"]) if r.get("tel") else None
            for t in ([tel, tel + ".gz"] if tel else []):
                if os.path.exists(t):
                    shutil.copy2(t, os.path.join(d, "tel", os.path.basename(t)))
            sp = os.path.join(src, "sp", f"{r['run']}.bin")
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(d, "sp", os.path.basename(sp)))
    start = os.path.join(src, "sp", "start.bin")
    if os.path.exists(start):
        shutil.copy2(start, os.path.join(dst1, "sp", "start.bin"))
    shutil.copy2(os.path.join(src, "sp", f"{runs[k - 1]['run']}.bin"), os.path.join(dst2, "sp", "start.bin"))
    return runs


def part2(rule, work):
    src = os.path.join(E158D, "aifoundry2/s1")
    P158 = json.load(open(os.path.join(LAB, "tools/claims-v3/e158/predictions-e158.json")))
    R158 = json.load(open(os.path.join(E158D, "results.json")))
    runs = [json.loads(x) for x in open(os.path.join(src, "runs.jsonl"))]
    ic = [i for i, r in enumerate(runs) if r["block"] == "C"]
    k = ic[len(ic) // 2]
    base = os.path.join(work, "e158-split")
    s1, s2 = os.path.join(base, "s1"), os.path.join(base, "s2")
    split_session(src, s1, s2, k)
    where = {r["label"].split("-")[0]: ("s1" if i < k else "s2") for i, r in enumerate(runs) if r["block"] == "C"}
    print(f"     E158's 98 runs cut after run {k} (block C, its pass 2): {sum(1 for i in ic if i < k)} of block C's {len(ic)} runs in s1, "
          f"{sum(1 for i in ic if i >= k)} in s2")
    red = RE.reduce([s1, s2], P158, RE.PASS_OF_BLOCK_E158)
    for key in ("t800_by_pass", "launches_800_by_pass", "cycles_per_op_800_by_pass", "per_shape", "checks"):
        say(rt(red[key]) == R158[key], f"two sessions: reduce_e169 on s1 + s2 reproduces E158's results.json {key} exactly")
    say(red["n_runs"] == 98 and red["sessions"] == ["s1", "s2"], f"two sessions: {red['n_runs']} runs over {red['sessions']}, each run once")
    say(rt(red["cells"]) == R158["cells"] and rt(red["skipped"]) == R158["skipped"] and rt(red["config_after"]) == R158["config_after"],
        "two sessions: cells, skipped and config_after equal to E158's results.json")

    def unprefixed(pk):
        return {k: (v.split("/", 1)[1] if k.endswith("_run") and isinstance(v, str) else v) for k, v in pk.items()}
    moved = sorted(k for k in R158["peaks"] if rt(red["peaks"]).get(k) != R158["peaks"].get(k))
    say(unprefixed(rt(red["peaks"])) == unprefixed(R158["peaks"]),
        f"two sessions: peaks the same values in the same runs; only the session in a run's name changes where that run now sits in s2 ({', '.join(moved) or 'none'})")
    import model_e158 as M          # E158's frozen model, imported unchanged
    import reduce_e158 as R8        # E158's registered reduction and score(), imported unchanged
    desk = M.load_desk()
    ab, c1 = M.load_prices()
    e146 = json.load(open(R8.E146_RES))
    checks_ok = bool(red["checks"]) and all(x in ("exact", "approx") for x in red["checks"])
    V, ERR = R8.score(red["per_shape"], red["t800_by_pass_raw"], P158, desk, ab, c1, checks_ok, red["cells"], e146, R8.power_fn())
    say(rt(V) == R158["rules"] and rt(ERR) == R158["errors"],
        f"two sessions: E158's registered score() on s1 + s2 reproduces results.json rules and errors exactly (R1 {V['R1']['consistent']}, "
        f"R2 {V['R2']['verdict']}, R3 {V['R3']['verdict']}, R4 {V['R4']['verdict']}, R5 {V['R5']['pass']} of {V['R5']['n']})")
    st = rule["committed_collapses_C3_post_hoc"]
    for a, b in (("D4", "D2"), ("K4n8", "K4n7"), ("K6n4", "K6n3"), ("K6n4", "K6n5")):
        ref = st[f"E158:{a}/{b}"]
        v = SC.pair_reading(red["t800_by_pass_raw"], red["launches_800_by_pass"], a, b, "fp32", ref["models"], rule)
        iv = ref["rule_interval_3_passes"]
        same = (v["n"] == 3 and abs(v["step"] - iv["step"]) < 2e-5 and abs(v["lo"] - iv["lo"]) < 2e-5 and abs(v["hi"] - iv["hi"]) < 2e-5
                and v["reading"].split(":")[0] == ref["reading_post_hoc"])
        sp = f"pass 2's {a} in {where.get(a)}, {b} in {where.get(b)}" + (": split" if where.get(a) != where.get(b) else "")
        say(same, f"two sessions, E158 {a}/{b} ({sp}): {100 * v['step']:+.2f}% [{100 * v['lo']:+.2f}, {100 * v['hi']:+.2f}] over {v['n']} passes -> "
                  f"{v['reading'].split(':')[0]}, as on one session")
    nsplit = sum(1 for a, b in (("D4", "D2"), ("K4n8", "K4n7"), ("K6n4", "K6n3"), ("K6n4", "K6n5")) if where.get(a) != where.get(b))
    say(nsplit >= 1, f"two sessions: {nsplit} of the four committed collapses have pass 2's two bursts in two sessions, and every one counts")
    rr = SC.r0(red)
    say(rr["verdict"] == "PASS" and rr["runs"] == 98, f"two sessions: E169's R0 over both reads {rr['verdict']} on {rr['runs']} runs")


# ------------------------------------------------------------------ 3. a dry pass in the real run directory
def part3(work):
    import queue_e169 as QE
    proto_dry = os.path.join(HERE, "protocol-dry.json")
    rd = os.path.join(work, "runs-reused", "smoke")
    cmd = [sys.executable, "-B", os.path.join(HERE, "run_e169.py"), "--protocol", proto_dry, "--out", rd, "--only", "SMOKE", "--max-card-min", "3.00", "--dry"]
    r1 = subprocess.run(cmd, cwd=LAB, stdin=subprocess.DEVNULL, capture_output=True, timeout=300)
    end1 = open(os.path.join(rd, "end.json"), "rb").read() if os.path.exists(os.path.join(rd, "end.json")) else b""
    say(r1.returncode == 0 and json.loads(end1 or b"{}").get("exit") == 0, f"the dry smoke on the toy card: exit {r1.returncode}, end.json exit {json.loads(end1 or b'{}').get('exit')}")
    r2 = subprocess.run(cmd, cwd=LAB, stdin=subprocess.DEVNULL, capture_output=True, timeout=300)
    end2 = open(os.path.join(rd, "end.json"), "rb").read()
    err = r2.stderr.decode(errors="replace")
    say(r2.returncode == 2 and "already holds a session" in err and end2 == end1,
        f"a second session into the same directory: exit {r2.returncode} ('{'already holds a session' if 'already holds a session' in err else err.strip()[-80:]}'), "
        f"end.json left as the dry pass wrote it")
    slot = os.path.join(work, "slot-check.txt")
    open(slot, "w").write("SLOT E169: start 1 (smoke check only) end 2 (smoke check only) \n")
    ns = argparse.Namespace(root=LAB, runs=os.path.join(work, "runs-reused"), slots=slot, protocol=os.path.join(HERE, "protocol.json"),
                            stoptest={"board": os.path.join(HERE, "protocol-stoptest-board.json"), "die": os.path.join(HERE, "protocol-stoptest-die.json")},
                            cap=20.0, give_up_min=25.0, cap_margin_s=180.0, dry=False)
    q = QE.Queue(ns)
    bad = q.check_smoke()
    want = json.load(open(os.path.join(HERE, "protocol.json")))["smoke_cycles"]
    say(bad is not None and "cycles per op" in bad and "546" in bad,
        f"the real queue's smoke check on the dry records left there: '{bad}' -> QUEUE-HALT, no session (the frozen smoke cycles "
        f"{min(want.values()):g}-{max(want.values()):g}, 50-250% allowed; the toy card's 546)")
    ns.dry = True
    say(QE.Queue(ns).check_smoke() is None, "the same records pass the dry queue's own smoke check (it skips the config and cycles checks), so the box's dry pass "
                                           "itself looks sound")


# ------------------------------------------------------------------ 4. the zero tiles
def part4():
    lst = os.path.join(HERE, "frozen-sha256-e169-tiles.txt")
    rows = [ln.split(None, 1) for ln in open(lst) if ln.strip()]
    listed = {os.path.normpath(os.path.join(HERE, f.strip())): h for h, f in rows}
    named = set()
    for p in sorted(glob.glob(os.path.join(HERE, "protocol*.json"))):
        s = open(p).read()
        for part in s.split('"'):
            if ":tiles:" in part:
                named.add(os.path.normpath(os.path.join(LAB, part.split(":tiles:", 1)[1])))
    say(named == set(listed), f"the six protocols name {len(named)} tile file(s); frozen-sha256-e169-tiles.txt lists {len(listed)}, the same set")
    z = hashlib.sha256(bytes(2048)).hexdigest()
    for p, h in sorted(listed.items()):
        b = open(p, "rb").read() if os.path.isfile(p) else None
        rel = os.path.relpath(p, LAB)
        say(b is not None and len(b) == 2048 and not any(b) and hashlib.sha256(b).hexdigest() == h == z,
            f"{rel}: {None if b is None else len(b)} bytes, {'every byte zero' if b is not None and not any(b) else 'NOT all zero'}, sha256 {h[:16]}... "
            f"(2,048 zero bytes hash to {z[:16]}...)")


# ------------------------------------------------------------------ 5. B7's point
def part5(rule, pred, kit):
    S = pred["shapes"]
    smT = {s: S[s]["fp32"]["SM"]["T800"] for s in SC.SHAPES}
    for f, want in ((1.0305, False), (0.9705, True)):
        T = dict(smT)
        T["P1"] = smT["P1"] * f
        v = SC.score(ST.fake(T, ties=rule["ties_e158"]["T800"]), rule, pred, kit)
        p = v["B7"]["fp32"]["point"]["P1"]
        other = abs(smT["P1"] / p["T800"] - 1) <= rule["b7_as_registered"]["point_rel"]
        say(p["ok"] is want and other is not want and v["B7"]["fp32"]["point_verdict"] == ("PASS" if want else "FAIL (1 of 6 outside 3%)"),
            f"P1 at {f:.4f} x SM's T800: measured / SM - 1 = {100 * p['rel']:+.2f}% -> {'inside' if p['ok'] else 'outside'} 3%, B7 point "
            f"{v['B7']['fp32']['point_verdict']}; |SM / measured - 1| = {100 * abs(smT['P1'] / p['T800'] - 1):.2f}% would read it "
            f"{'inside' if other else 'outside'}")


# ------------------------------------------------------------------ 6. the count
def part6(rule, pred, kit):
    calls = {"score": 0, "say": 0, "fail": 0}
    real_score, real_say = SC.score, ST.say

    def score(*a, **k):
        calls["score"] += 1
        return real_score(*a, **k)

    def count_say(ok, what):
        calls["say"] += 1
        calls["fail"] += 0 if ok else 1
    SC.score, ST.say = score, count_say
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            ST.part3(rule, pred, kit)
    finally:
        SC.score, ST.say = real_score, real_say
    say(calls["say"] == 22 and calls["fail"] == 0 and calls["score"] == 17,
        f"selftest_e169.py part 3: {calls['say']} checks, {calls['fail']} failed, on {calls['score']} made-up reductions (calls of score(): "
        f"SM's truth carries 4 checks, ISO's 3 with the floor's, every other one 1); with parts 1-2's 20, 42 checks in all")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="an empty scratch directory outside the lab tree")
    a = ap.parse_args()
    if glob.glob("/dev/et*"):
        raise SystemExit("refused: an ET-SoC-1 device node is present; this is a desk test")
    work = os.path.abspath(a.work)
    if work == LAB or work.startswith(LAB + os.sep):
        raise SystemExit("refused: --work must be outside the lab tree")
    os.makedirs(work, exist_ok=True)
    work = tempfile.mkdtemp(prefix="e169-notes-", dir=work)
    say(SC.check_frozen() is None, f"the scorer's frozen inputs match their committed bytes ({len(SC.FROZEN)} files)")
    rule, pred, kit = SC.load()
    print("\n1. A negative step (REGISTRATION-A2.md.dated-note-2.md, item 1)")
    part1(rule, pred, kit)
    print("\n2. A pass split across two sessions (note-2, item 2; README.md.dated-note.md, step 7)")
    part2(rule, work)
    print("\n3. A dry pass in the real run directory (README.md.dated-note.md, step 4)")
    part3(work)
    print("\n4. The zero tiles (README.md.dated-note.md, step 2)")
    part4()
    print("\n5. B7's point, measured / SM - 1 (note-2, item 3)")
    part5(rule, pred, kit)
    print("\n6. The count of selftest_e169.py's made-up truths (README.md.dated-note.md)")
    part6(rule, pred, kit)
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
