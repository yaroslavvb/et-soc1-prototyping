#!/usr/bin/env python3
"""E163 (Q141(a)'s fix pass, Wed 4 Nov 2026): the desk checks behind E163.md.dated-note.md (amendment A1) and README.md.dated-note.md,
run before any E163 data and before the claim. Desk only: nothing here opens a device, runs ssh or measures anything. The E151 blocks it
reduces are E151's own committed raw blocks of 3 Nov, copied into a scratch directory and renumbered as E163's 16350-16359.

  1. KE-C's scope (A1-1): E151's ten committed B blocks reduced by reduce_e163.py --e151 --drop-dips --rail-filter (the collector's
     call, unchanged) and scored by score_e163.score_e151_block, first with no C check, then with stub C records, to show which blocks
     KE-C reads and which KE-D reads.
  2. FULL's passes (A1-2): the queue's FULL sequence, the scoring floor, and one simulated session on 2 and on 1 kept passes.
  3. What KE-D and KE-W can detect (A1-3), from E151's committed per-block steps (predictions-e163.json > spec > e151_block > ref).
  4. SHORT's drops (A1-4a), the predictions' copy (A1-4b), the byte twin's figures (A1-4c).
  5. Q141(t)'s committed 27-point arm (A1-5): file, sha256, commit, form, and the scorer reading it on a simulated session.
  6. The hash lists the round requires, the kit's own checks, and this file's device-command audit.

    /usr/bin/python3 -B tools/claims-v3/e163/selftest_notes_e163.py --work <scratch dir> > tools/claims-v3/e163/logs/selftest-notes.txt
    /usr/bin/python3 -B tools/claims-v3/e163/selftest_notes_e163.py --only-hashes          # part 6 alone

Needs numpy (the reducer's E78 code and E151's scorer chain); the simulated sessions are the self-test's (selftest_e163.fake) with the
bootstrap cut to 2,000 draws, as selftest.txt does. Nothing here is a measurement, and nothing here changes a frozen file.
SPDX-License-Identifier: Apache-2.0
"""
import ast
import copy
import hashlib
import json
import math
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e163 as S  # noqa: E402  (frozen in 442474d5)
import selftest_e163 as T  # noqa: E402  (frozen in 442474d5)
import e163_common as C  # noqa: E402  (frozen in 1c47ce62)
import check_e163 as K  # noqa: E402  (frozen in 1c47ce62)

E151_RAW = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-e151-int8-b-aifoundry3", "aifoundry3", "e151")
ARM27 = "docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry3.json"
SIX = ("int8.b1_0", "int8.b1_1", "int8.b1_2", "int8.b1_3", "int8.b1_4", "int8.b1_5")
ENV = dict(os.environ, OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", VECLIB_MAXIMUM_THREADS="2", MKL_NUM_THREADS="2")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else "missing"


def head(t):
    print(f"\n== {t}")


def aside_ids(x):
    return [a.get("pass") if isinstance(a, dict) else a for a in (x or [])]


# ------------------------------------------------------------------------------------------------- 1. KE-C's scope
def renumber(work):
    """E151's B blocks 15110-15119 copied to <work>/raw/p16350-p16359; the block number rewritten in runs.jsonl, marks.jsonl and
    block.json (the directory name is the rest). Every other byte is E151's."""
    raw = tempfile.mkdtemp(prefix="raw-", dir=work)
    dirs = []
    for i, old in enumerate(range(15110, 15120)):
        new = 16350 + i
        d = os.path.join(raw, f"p{new}")
        shutil.copytree(os.path.join(E151_RAW, f"p{old}"), d)
        for jf in ("runs.jsonl", "marks.jsonl"):
            p = os.path.join(d, jf)
            lines = []
            for line in open(p):
                if line.startswith("{"):
                    r = json.loads(line)
                    for k in ("block", "pass"):
                        if r.get(k) == old:
                            r[k] = new
                    line = json.dumps(r) + "\n"
                lines.append(line)
            open(p, "w").write("".join(lines))
        bj = os.path.join(d, "block.json")
        b = json.load(open(bj))
        if b.get("pass") == old:
            b["pass"] = new
        json.dump(b, open(bj, "w"))
        dirs.append(d)
    return raw, dirs


def stub_ccheck(work, launches, mutate=None):
    """A ccheck directory whose one file gives every launch PASS, after `mutate` (which may change a verdict or drop a record)."""
    L = copy.deepcopy(launches)
    if mutate:
        mutate(L)
    d = tempfile.mkdtemp(prefix="cc-", dir=work)
    json.dump({"launches": [{"t_start_ms": x["t_start_ms"], "t_end_ms": x["t_end_ms"], "verdict": x["verdict"]} for x in L
                            if not x.get("_drop")]}, open(os.path.join(d, "ccheck-all.json"), "w"))
    return d


def part1(reg, work):
    head("1. KE-C's scope (A1-1): E151's ten committed B blocks as E163's 16350-16359, the collector's E151 reduction, the frozen scorer")
    eb = reg["spec"]["e151_block"]
    raw, dirs = renumber(work)
    out = tempfile.mkdtemp(prefix="red-", dir=work)
    red_json, runs_csv = os.path.join(out, "e163-e151.json"), os.path.join(out, "runs-e151.csv")
    cmd = [sys.executable, "-B", os.path.join(HERE, "reduce_e163.py")] + dirs + \
          ["--e151", "--drop-dips", "--rail-filter", "--out", red_json, "--csv", runs_csv, "--txt", os.path.join(out, "reduce-e151.txt")]
    r = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True)
    print(f"reduce_e163.py --e151 --drop-dips --rail-filter over p16350-p16359: rc {r.returncode}")
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        return False
    red = json.load(open(red_json))
    print(f"the reduction keeps (its 'passes', KE-C's blocks): {red['passes']}; E78's gates set aside: {aside_ids(red.get('passes_set_aside'))}")
    e0 = S.score_e151_block(reg, runs_csv, red_json)
    print(f"E151's Book keeps (KE-D's and KE-W's blocks): {e0['blocks_kept']}; its train gate sets aside: {aside_ids(e0['set_aside'])}")
    worst = 0.0
    for t in SIX:
        x = e0["tiles"][t]
        worst = max(worst, abs(x["diff_w"]))
        print(f"  {t}: E163 path {x['E163']['mean']:.6f} W over {x['E163']['n']} blocks, E151 {x['E151']['mean']:.6f} W, diff {x['diff_w']:+.1e}")
    print(f"largest |difference| {worst:.1e} W; KE-D {e0[eb['id'] + '-D']['verdict']}, KE-W {e0[eb['id'] + '-W']['verdict']}, "
          f"KE-C {e0[eb['id'] + '-C']['verdict']} (no C check given), KE {e0[eb['id']]['verdict']}")
    launches = []
    for p in red["passes"]:
        for line in open(os.path.join(raw, f"p{p}", "runs.jsonl")):
            if line.startswith("{"):
                q = json.loads(line)
                launches.append({"t_start_ms": q["t_start_ms"], "t_end_ms": q["t_end_ms"], "verdict": "PASS", "_item": q["item"], "_p": p})
    kept = [int(b) for b in e0["blocks_kept"]]
    aside = [int(b) for b in aside_ids(e0["set_aside"])]
    n6 = {t: sum(1 for x in launches if x["_item"] == t) for t in SIX}
    n6_kept = {t: sum(1 for x in launches if x["_item"] == t and x["_p"] in kept) for t in SIX}
    print(f"launches of the six in the reduction's blocks: {sum(n6.values())} ({n6['int8.b1_0']} each); in the Book's kept blocks only: "
          f"{sum(n6_kept.values())}")

    def first(L, item, block):
        return next(x for x in L if x["_item"] == item and x["_p"] == block)

    def rounding(item, block):
        def m(L):
            first(L, item, block)["verdict"] = "ROUNDING"
        return m

    def drop(item, block):
        def m(L):
            first(L, item, block)["_drop"] = True
        return m

    k1 = kept[0]
    cases = [("every launch PASS", None),
             (f"one ROUNDING, int8.b1_3, in {k1} (a block the Book keeps)", rounding("int8.b1_3", k1)),
             (f"one ROUNDING, int8.b1_3, in {aside[0]} (a block the Book sets aside)", rounding("int8.b1_3", aside[0])),
             (f"one launch of int8.b1_0 with no C record, in {aside[-1]} (set aside)", drop("int8.b1_0", aside[-1])),
             (f"one ROUNDING, int8.hb1 (not one of the six), in {k1}", rounding("int8.hb1", k1))]
    print("stub C records (every launch of the reduction's blocks given a record; nothing here is a measurement):")
    for name, mut in cases:
        cc = stub_ccheck(work, launches, mut)
        e = S.score_e151_block(reg, runs_csv, red_json, ccheck_dir=cc, passes_dir=raw)
        print(f"  {name:66s} KE-C {e[eb['id'] + '-C']['verdict']:10s} KE-D {e[eb['id'] + '-D']['verdict']:5s} "
              f"KE {e[eb['id']]['verdict']:5s} KE' {e[eb['prime']]['verdict']}")
    return True


# ------------------------------------------------------------------------------------------------- 2. FULL's passes
def part2(reg):
    head("2. FULL's passes (A1-2): what the queue runs, what the scorer needs, and what decides a set-aside")
    q = open(os.path.join(HERE, "queue_e163.sh")).read()
    m = re.search(r'FULL\)\s+SEQ="([^"]+)"; BUDGET_S=(\d+)', q)
    print(f"queue_e163.sh FULL: SEQ '{m.group(1)}', BUDGET_S {m.group(2)} (60 s of it reserved); predictions-e163.json > plan > plans > "
          f"FULL > sequence {reg['plan']['plans']['FULL']['sequence']}")
    code = [ln for ln in q.splitlines() if not ln.lstrip().startswith("#")]
    pat = re.compile(r"reduce|set_aside|passes_set|e163\.json")
    nred = sum(1 for ln in code if pat.search(ln))
    print(f"queue_e163.sh lines (not comments) naming a reduction or a gate verdict: {nred}")
    print(f"scoring floor: predictions-e163.json > plan > min_kept_passes_scored {reg['plan']['min_kept_passes_scored']}, > spec > "
          f"min_kept_passes_scored {reg['spec']['min_kept_passes_scored']}, > plan > min_tile_passes {reg['plan']['min_tile_passes']}")
    r2 = copy.deepcopy(reg)
    r2["spec"]["bootstrap"]["draws"] = 2000
    print("  simulated sessions (selftest_e163.fake, M9 as good as its nested score; no C check is given, so K14 reads NOT SCORED):")
    for passes in ((16310, 16311, 16312), (16310, 16311), (16310,)):
        made = passes if len(passes) > 1 else (16310, 16311)      # fake() needs two passes; the one-pass case keeps only 16310
        res = T.fake(r2, random.Random("E163|notes|" + ",".join(map(str, made))), 1.0, 0.0, passes=made)
        if len(passes) == 1:
            res = dict(res, passes=[16310])
        s = S.score(res, r2)
        if "NOT SCORED" in s:
            print(f"  kept passes {list(passes)}: NOT SCORED ({s['NOT SCORED']})")
        else:
            v = S.verdicts(s, r2["spec"])
            print(f"  kept passes {list(passes)}: scored, {len(v)} verdicts (RANK1 {v.get('E163-RANK1')}, P1 {v.get('E163-P1')}, "
                  f"C1 {v.get('E163-C1')}, M1 {v.get('E163-M1')}, K14 {v.get('E163-K14')})")
    for f, what in (("docs/reports/data/2026-11-03-q139u-footing/reduced/e141-footing.json", "E141 on Q139(u)'s footing, dips removed"),
                    ("docs/reports/data/2026-11-03-e153-blind6-aifoundry3/e153.json", "E153's registered primary (the footing)"),
                    ("docs/reports/data/2026-11-02-e141-blind5-aifoundry3/e141.json", "E141's session-own reduction, dips kept")):
        d = json.load(open(os.path.join(ROOT, f)))
        print(f"  this card, {what}: kept {d.get('passes')}, set aside {aside_ids(d.get('passes_set_aside'))} ({f})")


# ------------------------------------------------------------------------------------------------- 3. KE-D's and KE-W's power
def part3(reg):
    head("3. What KE-D and KE-W can detect (A1-3): a lost step reads 0 and a doubled one 2s, so either departs from E151's by s itself")
    eb = reg["spec"]["e151_block"]
    flat = eb["flat_w"]
    print(f"KE-D's line: |D_E163 - D_E151| <= {flat} W on each tile. KE-W: Welch's 95% interval (pick6.welch). The expected half-widths below "
          "assume E163's kept blocks scatter as E151's eight kept blocks did (their per-block sd); planned, not measured.")
    print(f"  {'tile':10s} {'step s, W':>9s} {'se':>7s} {'per-block sd':>12s}  {'KE-D sees s lost/doubled':>24s}  "
          f"{'KE-W half-width, 3 / 2 blocks':>29s}  {'KE-W sees it (3 / 2)':>20s}")
    for t in SIX:
        x = eb["ref"][t]
        sd = statistics.stdev(list(x["per_block"].values()))
        hw = []
        for n in (3, 2):
            w = S.pick6.welch(x["mean"], x["se"], x["n"], x["mean"], sd / math.sqrt(n), n)
            hw.append(w["half_width_W"])
        seen = "yes" if x["mean"] > flat else "no"
        print(f"  {t[5:]:10s} {x['mean']:9.4f} {x['se']:7.4f} {sd:12.4f}  {seen:>24s}  {hw[0]:14.4f} / {hw[1]:.4f}      "
              f"{('yes' if x['mean'] > hw[0] else 'no'):>9s} / {('yes' if x['mean'] > hw[1] else 'no')}")


# ------------------------------------------------------------------------------------------------- 4. words
def part4(reg):
    head("4a. SHORT's drops (A1-4a): one SHORT pass against one FULL kinds pass, by e163_common.pass_order (the registered order code)")
    names = set(C.E163_NAMES) | set(C.ec.ANCHORS) | {C.ec.TIE}
    items = [{"name": n} for n in sorted(names)]
    frame = set(C.ec.ANCHORS) | {C.ec.TIE}
    full = {x["item"] for x in C.pass_order(items, "aifoundry3", 16310)} - frame
    short = {x["item"] for x in C.pass_order(items, "aifoundry3", 16320)} - frame
    gone = full - short
    print(f"tiles in 16310: {len(full)}; in 16320: {len(short)}; left out of 16320: {len(gone)} = the four priority-2 tests "
          f"({len(gone & set(C.P2_DROP_ORDER))} of {len(C.P2_DROP_ORDER)}) and the 16 re-runs ({len(gone & set(C.RERUN_NAMES))} of "
          f"{len(C.RERUN_NAMES)}), together; other: {sorted(gone - set(C.P2_DROP_ORDER) - set(C.RERUN_NAMES))}")
    print(f"e163_common.SHORT_NAMES: {len(C.SHORT_NAMES)} (pool 7's 61 less the four); any SHORT plan that keeps one set and drops the "
          f"other: {'none' if set(reg['plan']['plans']) == {'FULL', 'TWO', 'SHORT'} else sorted(reg['plan']['plans'])}")

    head("4b. The predictions' copy (A1-4b): predictions-blind7-aifoundry3.json (75802201) against predictions-e163.json > tiles")
    a = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry3.json")))["tiles"]
    b = reg["tiles"]
    nonnull = equal = 0
    absent = {}
    for t in sorted(a):
        for m in ("M6", "M7", "M8", "M9"):
            for k, v in a[t][m].items():
                if v is None:
                    if k not in b[t][m]:
                        absent.setdefault(f"{m}.{k}", 0)
                        absent[f"{m}.{k}"] += 1
                    continue
                nonnull += 1
                equal += b[t][m].get(k) == v
    extra = sum(1 for t in b for m in ("M6", "M7", "M8", "M9") for k in b[t][m] if k not in a[t][m])
    print(f"{len(a)} tiles x M6-M9: {equal} of {nonnull} non-null fields equal; left out of predictions-e163.json: "
          f"{absent} (null in the frozen file on every tile listed); fields added: {extra}")
    used = [f for f in os.listdir(HERE) if f.endswith(".py") and f != os.path.basename(__file__)
            and "D600_a3_95" in open(os.path.join(HERE, f)).read()]
    print(f"E163 code reading D600_a3_95: {used or 'none'}")

    head("4c. The byte twin's figures (as E163.md states them; for the records' wording)")
    bt = reg["spec"]["byte_twin"]
    line = next(ln for ln in open(os.path.join(ROOT, "docs/reports/data/2026-11-04-q140m-m9/recount-rule/recount-rule.txt"))
                if re.match(r"fp32\.cal_pi_b20\s+27\s", ln))
    print(f"recount-rule.txt: {line.strip()}  (columns: tile N mean_W 3pt-N_W se_samp se_intl e(N) met)")
    print(f"spec > byte_twin: tile {bt['tile']}, expected error (measured - M9) {bt['expected_error_w']:+.3f} +- {bt['expected_error_se_w']} W")


# ------------------------------------------------------------------------------------------------- 5. Q141(t)'s arm
def part5(reg):
    head("5. Q141(t)'s 27-point arm (A1-5), as committed")
    p = os.path.join(ROOT, ARM27)
    g = subprocess.run(["git", "log", "-1", "--format=%h %ad", "--date=format:%Y-%m-%d %H:%M:%S %z", "--", ARM27], cwd=ROOT,
                       capture_output=True, text=True).stdout.strip()
    arm = json.load(open(p))
    form = isinstance(arm, dict) and all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in arm.items())
    cls = {t: c for c, ts in reg["spec"]["classes"].items() for t in ts}
    print(f"{ARM27}: sha256 {sha(p)}; first commit {g}; form {{tile: D_w}}: {form}; {len(arm)} tiles")
    for t in sorted(arm):
        T_ = reg["tiles"].get(t, {})
        print(f"  {t}: arm {arm[t]} W, M9 {T_.get('M9', {}).get('D_w')} W, class {cls.get(t, T_.get('aim'))}, priority {T_.get('priority')}")
    r2 = copy.deepcopy(reg)
    r2["spec"]["bootstrap"]["draws"] = 2000
    res = S.run(r2, T.fake(r2, random.Random("E163|notes|arm27"), 1.0, 0.0), arm27=arm)
    a = res["primary"]["primary"].get("reported_arm27") or {}
    print(f"score_e163.run on one simulated session with the arm: reported_arm27 rows {a.get('n')}; the arm sets no verdict "
          f"(verdict keys with 'arm': {[k for k in res['verdicts'] if 'arm' in k.lower()]})")


# ------------------------------------------------------------------------------------------------- 6. hash lists and checks
def part6():
    head("6. The round's hash lists, the kit's own checks, and this file's device-command audit (read-only)")
    d7 = os.path.join(ROOT, "tools/claims-v3/kinds/blind7")
    ok = n = 0
    for line in open(os.path.join(d7, "SHA256SUMS")):
        mm = re.match(r"([0-9a-f]{64})\s+\*?(\S+)", line.strip())
        if mm:
            n += 1
            ok += sha(os.path.join(d7, mm.group(2))) == mm.group(1)
    print(f"tools/claims-v3/kinds/blind7/SHA256SUMS: {ok} of {n} OK")
    D = "docs/reports/data/2026-11-04-q140q-gemm-g4-stride"
    j = json.load(open(os.path.join(ROOT, D, "frozen-sha256-e168.json")))
    items = j.get("files", j) if isinstance(j, dict) else j
    pairs = items.items() if isinstance(items, dict) else [(x["path"], x["sha256"]) for x in items]
    pairs = [(k, v) for k, v in pairs if isinstance(v, str) and len(v) == 64]
    good = sum(1 for k, v in pairs if v in (sha(os.path.join(ROOT, k)), sha(os.path.join(ROOT, D, k))))
    print(f"{D}/frozen-sha256-e168.json: {good} of {len(pairs)} OK")
    n = good = 0
    for line in open(os.path.join(ROOT, D, "frozen-sha256-e168-scorer.txt")):
        mm = re.match(r"([0-9a-f]{64})\s+\*?(\S+)", line.strip())
        if mm:
            n += 1
            good += mm.group(1) in (sha(os.path.join(ROOT, mm.group(2))), sha(os.path.join(ROOT, D, mm.group(2))))
    print(f"{D}/frozen-sha256-e168-scorer.txt: {good} of {n} OK")
    P = "docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py"
    tree = ast.parse(open(os.path.join(ROOT, P)).read())
    fz = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == "FROZEN" for t in n.targets))
    print(f"{P} FROZEN (its input hashes, read by ast, not imported): "
          f"{sum(1 for k, h in fz.items() if sha(os.path.join(ROOT, k)) == h)} of {len(fz)} OK")
    bad, nk = K.check(ROOT, box=False)
    print(f"check_e163.check (desk: the box binaries not checked): {nk - len(bad)} of {nk} OK" + (f"; differs: {bad}" if bad else ""))
    v = subprocess.run([sys.executable, "-B", os.path.join(HERE, "e163_common.py"), "--verify"], cwd=ROOT, capture_output=True, text=True)
    print(f"e163_common.py --verify: rc {v.returncode}, problems {json.loads(v.stdout.strip().splitlines()[-1]).get('problems')}")
    a = subprocess.run([sys.executable, "-B", os.path.join(ROOT, "tools/claims-v3/dmcmd_audit.py"), os.path.relpath(__file__, ROOT)],
                       cwd=ROOT, capture_output=True, text=True)
    verdict = [ln for ln in (a.stdout + "\n" + a.stderr).splitlines() if ln.startswith("dmcmd_audit:")]
    print(f"dmcmd_audit.py on this file: rc {a.returncode}; {verdict[0] if verdict else (a.stdout + a.stderr).strip()[:200]}")


def main():
    if "--only-hashes" in sys.argv:
        part6()
        return 0
    reg = json.load(open(os.path.join(HERE, "predictions-e163.json")))
    work = sys.argv[sys.argv.index("--work") + 1] if "--work" in sys.argv else None
    tmp = None
    if work is None:
        tmp = tempfile.TemporaryDirectory()
        work = tmp.name
    os.makedirs(work, exist_ok=True)
    print("E163 notes self-test (Q141(a)'s fix pass): desk only, no device, no ssh; nothing here is a measurement. Inputs: the committed "
          "files named in each part; E151's raw blocks are copied into a scratch directory, never written in place.")
    ok = part1(reg, work)
    part2(reg)
    part3(reg)
    part4(reg)
    part5(reg)
    part6()
    print(f"\nSELFTEST-NOTES {'DONE' if ok else 'FAILED (part 1)'}")
    if tmp:
        tmp.cleanup()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
