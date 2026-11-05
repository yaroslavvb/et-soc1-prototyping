#!/usr/bin/env python3
"""Q142(v2) fix pass, Thu 5 Nov 2026: the self-test of score_p8_600_v3.py (dated note 2 beside E171.md and E172.md). Desk only: it reads
committed files and writes only into a temporary directory (removed at the end) and its --out and --txt files. No device, no ssh.

Its sessions are the committed builders': selftest_score_p8_600.synth (a518aa11) for the raw copy, the check of C and the reduction, then
selftest_score_p8_600_v2.session's steps (86d10a75; copied below with the pass list and the run as arguments, as the v2 verifier's
adversarial script did): the six anchors in s at known ratios, E78's items in every pass's runs and C logs, scored by the committed
scorer's command line as the collectors call it.

  W0  the inputs: v2's sha256 equals its SHA256SUMS-v2 line and the scorer's its SHA256SUMS line; v3 refuses (9) when v2's line names
      another hash; the committed scorer still writes the NOT SCORED mark v3 reads (its source line); the predictor's lists pass.
  W1  the genuine pair (E171 and E172, three kept passes each): v3 reads what v2 and the committed ka_pooled read (verdict, n, rows).
  W2  the verifier's fault 1: a session that kept one pass. The committed scorer writes its NOT SCORED mark and no rows; v2 refuses the pair
      (6), as the verifier found; v3 reads NOT SCORED as registered (E171 with one pass: n 2; E172 with one pass: n 2; both: n 0), equal to
      the committed ka_pooled, and with --scale-c (v2's scale-c on the one-pass session) the arm beside reads NOT SCORED too.
  W3  NOT SCORED marks the committed scorer never writes, each refused (6, nothing written): no rows and no mark; a mark beside two kept
      passes; a mark whose count is not the kept passes'; a mark beside rows; a mark beside a verdict other than NOT SCORED; a mark beside a
      P8-KA block.
  W4  the verifier's fault 2: E171's measurements laid out as E172's raw copy and scored --run E172. v2 reads the pair PASS, n 4, as the
      verifier found; v3 refuses it (6): the same measured D on every shared tile.
  W5  v2's refusals, carried by v3 (6, nothing written): E171 twice; E172 twice; the pair swapped; E171's file relabelled as E172's; a
      predictions_sha256 that is not the freeze's; a scorer_sha256 that is not the committed scorer's; a file with no c_sessions; a missing
      file; --scale-c with its two files swapped; and the positive control, --scale-c in order (0).
  W6  check (7) on real data: E163's and E164's committed primary reductions (pool 7 on aifoundry3 and on card 1): the tiles both measured
      with a non-zero D, and how many carry the same D to the bit (0: not refused); E163 against itself (refused).

Its output is the same on any machine and in any temporary directory: every line is masked (the repo and the temporary directory) before
any cut, and every sha256 of a file it writes is reported as the sha256 of that file's masked bytes (the v2 verifier's fault 6).

    /usr/bin/python3 -B tools/claims-v3/p8-600/selftest_score_p8_600_v3.py [--out <file.json>] [--txt <file.txt>]

Exit 0 when every part passes. Standard library and numpy (through the predictor). SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_p8_600 as SC  # noqa: E402  (committed, a518aa11)
import score_p8_600_v2 as V2  # noqa: E402  (committed, 86d10a75)
import score_p8_600_v3 as V3  # noqa: E402
import selftest_score_p8_600 as ST  # noqa: E402  (committed: its synthetic-session builder; importing runs nothing)
import selftest_score_p8_600_v2 as T2  # noqa: E402  (committed: RATIOS; importing runs nothing)
import ccsessions_p8 as CSN  # noqa: E402

DD = os.path.join(TOP, "docs", "reports", "data")
load = lambda p: json.load(gzip.open(p, "rt") if p.endswith(".gz") else open(p))  # noqa: E731
LINES = []
TMP = {"real": None, "given": None}
REG = []          # (sha256 of a file this test wrote, sha256 of its masked bytes), in the order written


# ------------------------------------------------------------------------------------------------- masks (fault 6: mask, then cut)
def mask(t):
    t = t.replace(TOP + os.sep, "").replace(TOP, "<repo>")
    for k in ("real", "given"):
        if TMP[k]:
            t = t.replace(TMP[k], "<tmp>")
    for real, can in REG:
        t = t.replace(real, can).replace(real[:12], can[:12])
    return t


def reg(path):
    """the file's sha256 and the sha256 of its masked bytes; every later output names the second"""
    real = SC.sha(path)
    can = hashlib.sha256(mask(open(path, "rb").read().decode("utf-8", "replace")).encode()).hexdigest()
    REG.append((real, can))
    return can


def say(s, n=None):
    s = mask(str(s))
    s = s[:n] if n else s
    LINES.append(s)
    print(s, flush=True)


# ------------------------------------------------------------------------------------------------- the sessions
def session(card, label, passes=(0, 1, 2), run=None, fail=()):
    """selftest_score_p8_600_v2.session (86d10a75), copied, with the pass list and the run as arguments: the committed builder's session,
    the six anchors in s at known ratios, E78's items in every pass's runs.jsonl and C log and in the check of C; scored by the committed
    scorer's command line. Returns the paths and the predictions."""
    run = run or T2.RUN_OF[card]
    raw, cc, red, pred, _ = ST.synth(card, TMP["real"], label, passes=passes, run=run)
    S = pred["sets"]
    rate = {t: pred["rates"][t]["stated_per_s"] for t in SC.FORMATS}
    res = load(red)
    want = dict(T2.RATIOS)
    for i, n in enumerate(sorted(S["scale_anchors_pool8"])):
        want[n] = 1.004 + 0.002 * i
    for n, q in want.items():
        t = n.split(".")[0]
        k1 = pred["m10_anchors"][n]["k1_J_per_op"] if n in pred["m10_anchors"] else pred["tiles"][n]["M10"]["k1_J_per_op"]
        d = q * rate[t] * k1
        res["items"][n]["D"]["mean"] = d
        for pp in res["per_pass"].values():
            if n in pp:
                pp[n]["D"] = d
    json.dump(res, open(red, "w"))
    c = load(cc)
    R = CSN.RUNS[run]
    k = 0
    item_of = {}
    for q in res["passes"]:
        d = os.path.join(raw, R["dir"], f"p{q}")
        names = ["anchor_pi"] + [n for _ in range(3) for n in V2.E78_ITEMS if n != "anchor_pi"] + ["anchor_pi"]
        with open(os.path.join(d, "runs.jsonl"), "a") as rf, open(os.path.join(d, "c-log.jsonl"), "a") as cf:
            for n in names:
                t0 = 2 * 10 ** 12 + k * 10
                k += 1
                rf.write(json.dumps({"item": n, "launch": 0, "t_start_ms": t0, "t_end_ms": t0 + 5}) + "\n")
                cf.write(json.dumps({"ccheck": 1, "kind": "c", "type": n.split(".")[0] if "." in n else "fp32", "launch": 0, "iters": 1,
                                     "t_start_ms": t0, "t_end_ms": t0 + 5, "ok": True, "groups": []}) + "\n")
                c["launches"].append({"log": f"c-log-p{q}.jsonl", "t_start_ms": t0, "t_end_ms": t0 + 5, "verdict": "PASS", "type": "fp32"})
        for line in open(os.path.join(d, "runs.jsonl")):
            r = json.loads(line)
            item_of[(r["t_start_ms"], r["t_end_ms"])] = r["item"]
    for v in c["launches"]:
        if item_of.get((v["t_start_ms"], v["t_end_ms"])) in set(fail):
            v["verdict"] = "FAIL"
    c["summary"].update(launches=len(c["launches"]), PASS=sum(v["verdict"] == "PASS" for v in c["launches"]),
                        FAIL=sum(v["verdict"] == "FAIL" for v in c["launches"]))
    c["summary"]["all_pass"] = c["summary"]["FAIL"] == 0
    json.dump(c, open(cc, "w"))
    reg(red)
    reg(cc)
    base = os.path.dirname(red)
    js, md = os.path.join(base, "scored.json"), os.path.join(base, "results.md")
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "score_p8_600.py"), "score", "--run", run, "--reduction", red, "--raw", raw,
                        "--ccheck", cc, "--json", js, "--md", md], capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not os.path.exists(js):
        raise RuntimeError(f"the committed scorer exited {r.returncode} on {label}: {mask(r.stdout[-300:])} {mask(r.stderr[-300:])}")
    reg(js)
    return {"run": run, "card": SC.RUN_CARD[run], "raw": raw, "cc": cc, "red": red, "scored": js, "pred": pred, "base": base}


def cli(script, args, timeout=900):
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, script)] + args, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def kap(script, a, b, tag, extra=()):
    """one ka-pooled call of v2 or v3: its exit, whether it wrote, its first line and its reading"""
    js = os.path.join(TMP["real"], f"kap-{tag}.json")
    if os.path.exists(js):
        os.remove(js)
    rc, so, se = cli(script, ["ka-pooled", a, b, *extra, "--json", js])
    rec = {"rc": rc, "wrote": os.path.exists(js), "line": mask((so.splitlines() or [""])[0])[:400]}
    if os.path.exists(js):
        o = load(js)
        b_ = (o.get("beside") or {}).get("c_clean_scale") or {}
        rec.update(verdict=o.get("verdict"), n=o.get("n"), why=o.get("why"), beside=b_.get("verdict"), beside_n=b_.get("n"),
                   measured_D=((o.get("identity") or {}).get("measured_D")), rows=o.get("rows"))
    if se:
        rec["stderr"] = mask(se[-300:])
    return rec


def scale_c(s, tag):
    """v2's scale-c (unchanged: the card day's) on a session; its scale-c.json registered"""
    js, md, work = (os.path.join(s["base"], f"scale-c-{tag}.json"), os.path.join(s["base"], f"scale-c-{tag}.md"),
                    os.path.join(s["base"], f"work-{tag}"))
    rc, so, se = cli("score_p8_600_v2.py", ["scale-c", "--run", s["run"], "--scored", s["scored"], "--reduction", s["red"], "--raw", s["raw"],
                                            "--ccheck", s["cc"], "--json", js, "--md", md, "--work", work])
    if os.path.exists(js):
        reg(js)
    return rc, mask(so)[:300], js


def variant(src, tag, fn):
    o = load(src)
    fn(o)
    p = os.path.join(TMP["real"], f"variant-{tag}.json")
    json.dump(o, open(p, "w"), indent=1, sort_keys=True)
    reg(p)
    return p


def brief(r):
    return {k: r.get(k) for k in ("rc", "wrote", "verdict", "n", "why", "beside", "beside_n", "line") if k in r}


# ------------------------------------------------------------------------------------------------- W0
def w0():
    bad = []
    sums = {}
    for f in ("SHA256SUMS", "SHA256SUMS-v2"):
        for line in open(os.path.join(HERE, f)):
            h, p = line.split(None, 1)
            sums[p.strip()] = h
    have_sc = SC.sha(os.path.join(HERE, "score_p8_600.py"))
    have_v2 = SC.sha(os.path.join(HERE, "score_p8_600_v2.py"))
    if have_sc != sums.get(V2.SCORER_REL):
        bad.append("the committed scorer is not its SHA256SUMS line")
    if have_v2 != sums.get(V3.V2_REL):
        bad.append("v2 is not its SHA256SUMS-v2 line")
    try:
        V3.committed_v2_sha()
        ok_real = True
    except SC.Refuse:
        ok_real = False
        bad.append("committed_v2_sha refused the committed list")
    wrong = os.path.join(TMP["real"], "SHA256SUMS-v2-wrong")
    open(wrong, "w").write("0" * 64 + "  " + V3.V2_REL + "\n")
    try:
        V3.committed_v2_sha(wrong)
        code = 0
    except SC.Refuse as e:
        code = e.code
    if code != 9:
        bad.append(f"a wrong v2 line gave {code}, not 9")
    src = open(os.path.join(HERE, "score_p8_600.py")).read()
    mark_line = "out[\"NOT SCORED\"] = f\"{len(res.get('passes', []))} kept passes, fewer than 2\""
    if mark_line not in src or V3.MARK_TAIL != " kept passes, fewer than 2":
        bad.append("the committed scorer's NOT SCORED mark is not the form v3 reads")
    lists = SC.A2().check_lists()
    out = {"scorer_sha256_ok": have_sc == sums.get(V2.SCORER_REL), "v2_sha256_ok": have_v2 == sums.get(V3.V2_REL),
           "committed_v2_sha_real_list": ok_real, "wrong_v2_line_exit": code, "mark_line_in_scorer": mark_line in src,
           "predictor_lists": lists, "pass": not bad, "differences": bad}
    say(f"W0 the scorer {have_sc[:12]} and v2 {have_v2[:12]} as listed; a wrong v2 line exits {code}; the scorer's NOT SCORED mark is "
        f"v3's form: {mark_line in src}; predictor lists {lists}: {'PASS' if not bad else 'FAIL'} {bad}")
    return out


# ------------------------------------------------------------------------------------------------- W1, W2, W3
def w1(A, C):
    r3, r2 = kap("score_p8_600_v3.py", A["scored"], C["scored"], "w1-v3"), kap("score_p8_600_v2.py", A["scored"], C["scored"], "w1-v2")
    theirs = SC.ka_pooled([A["scored"], C["scored"]])
    same = r3["rc"] == 0 and all(r3.get(k) == theirs.get(k) for k in ("verdict", "n", "rows")) and all(r3.get(k) == r2.get(k) for k in ("verdict", "n", "rows"))
    ok = same and r3.get("verdict") == "PASS" and r3.get("n") == 4
    say(f"W1 the genuine pair: v3 rc {r3['rc']} {r3.get('verdict')} n {r3.get('n')}; v2 {r2.get('verdict')} n {r2.get('n')}; the committed "
        f"ka_pooled {theirs.get('verdict')} n {theirs.get('n')}; rows equal {same}; measured D: {json.dumps(r3.get('measured_D'), sort_keys=True)}: "
        f"{'PASS' if ok else 'FAIL'}", 400)
    return {"v3": brief(r3), "v2": brief(r2), "committed": {k: theirs.get(k) for k in ("verdict", "n", "why")}, "measured_D": r3.get("measured_D"),
            "same_as_v2_and_committed": same, "pass": ok}


def w2(A, C):
    bad, out = [], {}
    A1 = session("aifoundry3", "A1", passes=(0,))
    C1 = session("aifoundry1c1", "C1", passes=(0,))
    sj = load(A1["scored"])
    pr = sj.get("primary") or {}
    out["E171 one pass, as the committed scorer writes it"] = {"primary_keys": sorted(pr), "rows": len(pr.get("rows") or {}),
                                                               "mark": pr.get("NOT SCORED"), "kept_passes": pr.get("kept_passes"),
                                                               "rules": sorted(pr.get("rules") or {}),
                                                               "verdicts": sorted(set((sj.get("verdicts") or {}).values()))}
    if pr.get("rows") or pr.get("NOT SCORED") != "1 kept passes, fewer than 2":
        bad.append(f"the one-pass session is not the form expected: {out['E171 one pass, as the committed scorer writes it']}")
    r = kap("score_p8_600_v2.py", A1["scored"], C["scored"], "w2-v2")
    out["v2 on (E171 one pass, E172)"] = brief(r)
    if r["rc"] != 6 or r["wrote"]:
        bad.append(f"v2 on the one-pass pair: rc {r['rc']} (the verifier's fault 1 reads 6)")
    for tag, a, b, n in (("v3 on (E171 one pass, E172)", A1, C, 2), ("v3 on (E171, E172 one pass)", A, C1, 2),
                         ("v3 on (both one pass)", A1, C1, 0)):
        r = kap("score_p8_600_v3.py", a["scored"], b["scored"], "w2-" + tag.split("(")[1][:6].replace(" ", "").replace(",", ""))
        theirs = SC.ka_pooled([a["scored"], b["scored"]])
        out[tag] = dict(brief(r), committed={k: theirs.get(k) for k in ("verdict", "n", "why")})
        if r["rc"] != 0 or not r["wrote"] or r.get("verdict") != "NOT SCORED" or r.get("n") != n or theirs.get("verdict") != "NOT SCORED" \
                or theirs.get("n") != n or r.get("why") != theirs.get("why"):
            bad.append(f"{tag}: rc {r['rc']} {r.get('verdict')} n {r.get('n')}, the committed {theirs.get('verdict')} n {theirs.get('n')}")
    rc1, l1, s1 = scale_c(A1, "w2")
    rc2, l2, s2 = scale_c(C, "w2")
    r = kap("score_p8_600_v3.py", A1["scored"], C["scored"], "w2-scalec", ("--scale-c", s1, s2))
    out["v3 --scale-c on (E171 one pass, E172)"] = dict(brief(r), scale_c_rc=[rc1, rc2], scale_c_lines=[l1, l2])
    if rc1 != 0 or rc2 != 0 or r["rc"] != 0 or r.get("verdict") != "NOT SCORED" or r.get("beside") != "NOT SCORED" or r.get("beside_n") != 2:
        bad.append(f"--scale-c on the one-pass pair: scale-c {rc1}/{rc2}, v3 rc {r['rc']} {r.get('verdict')}, beside {r.get('beside')} n "
                   f"{r.get('beside_n')}")
    out["pass"] = not bad
    out["differences"] = bad
    for k, v in out.items():
        if isinstance(v, dict):
            say(f"W2 {k}: {json.dumps(v, sort_keys=True)}", 420)
    say(f"W2 {'PASS' if not bad else 'FAIL'} {bad}")
    return out, A1


def w3(A, A1, C):
    bad, out = [], {}
    rowsA = load(A["scored"])["primary"]["rows"]
    kaA = load(A["scored"])["primary"]["rules"]["P8-KA"]
    cases = [("no rows and no mark", A["scored"], lambda o: o["primary"].pop("rows")),
             ("a mark beside two kept passes", A1["scored"], lambda o: o["primary"].update(kept_passes=[17110, 17111])),
             ("a mark whose count is not the kept passes'", A1["scored"], lambda o: o["primary"].update({"NOT SCORED": "0 kept passes, fewer than 2"})),
             ("a mark beside rows", A1["scored"], lambda o: o["primary"].update(rows=rowsA)),
             ("a mark beside a P8-KA verdict PASS", A1["scored"], lambda o: o["verdicts"].update({"P8-KA": "PASS"})),
             ("a mark beside a P8-KA block", A1["scored"], lambda o: o["primary"]["rules"].update({"P8-KA": kaA}))]
    for i, (tag, src, fn) in enumerate(cases):
        p = variant(src, f"w3-{i}", fn)
        r = kap("score_p8_600_v3.py", p, C["scored"], f"w3-{i}")
        out[tag] = brief(r)
        if r["rc"] != 6 or r["wrote"]:
            bad.append(f"{tag}: rc {r['rc']}, wrote {r['wrote']}")
    out["pass"] = not bad
    out["differences"] = bad
    for k, v in out.items():
        if isinstance(v, dict):
            say(f"W3 {k}: rc {v['rc']}, wrote {v['wrote']} | {v['line']}", 300)
    say(f"W3 {'PASS' if not bad else 'FAIL'} {bad}")
    return out


# ------------------------------------------------------------------------------------------------- W4, W5, W6
def w4(A, C):
    bad = []
    Ap = session("aifoundry3", "Aprime", run="E172")   # E171's designed measurements (aifoundry3's predictions) laid out as E172's raw copy
    ra, rp = load(A["red"]), load(Ap["red"])
    same_items = all(ra["items"][t]["D"]["mean"] == rp["items"][t]["D"]["mean"] for t in ra["items"] if t in rp["items"])
    r2 = kap("score_p8_600_v2.py", A["scored"], Ap["scored"], "w4-v2")
    r3 = kap("score_p8_600_v3.py", A["scored"], Ap["scored"], "w4-v3")
    sh, sm = V3.same_d([load(A["scored"]), load(Ap["scored"])])
    g_sh, g_sm = V3.same_d([load(A["scored"]), load(C["scored"])])
    out = {"reductions_D_identical": same_items, "v2": brief(r2), "v3": brief(r3), "shared_nonzero_D": len(sh), "bit_identical_D": len(sm),
           "genuine_pair_shared_nonzero_D": len(g_sh), "genuine_pair_bit_identical_D": len(g_sm)}
    if r2["rc"] != 0 or r2.get("verdict") != "PASS":
        bad.append(f"v2 on the relaid copy: rc {r2['rc']} {r2.get('verdict')} (the verifier's fault 2 reads 0, PASS)")
    if r3["rc"] != 6 or r3["wrote"] or "the same measured D" not in r3["line"]:
        bad.append(f"v3 on the relaid copy: rc {r3['rc']}, wrote {r3['wrote']}")
    if not sm or len(sm) != len(sh) or V3.one_session_twice(g_sh, g_sm):
        bad.append(f"the D counts: relaid {len(sm)} of {len(sh)}, genuine {len(g_sm)} of {len(g_sh)}")
    out["pass"] = not bad
    out["differences"] = bad
    say(f"W4 E171's measurements re-laid as E172 and scored --run E172: the reductions' D identical {same_items}; v2 rc {r2['rc']} "
        f"{r2.get('verdict')} n {r2.get('n')}; v3 rc {r3['rc']}, wrote {r3['wrote']} | {r3['line']}", 420)
    say(f"W4 bit-identical non-zero D: the relaid copy {len(sm)} of {len(sh)}; the genuine pair {len(g_sm)} of {len(g_sh)}: "
        f"{'PASS' if not bad else 'FAIL'} {bad}")
    return out


def w5(A, C):
    bad, out = [], {}
    relab = variant(A["scored"], "relabelled", lambda o: o.update(
        run="E172", card="aifoundry1c1", predictions="tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json",
        predictions_sha256=SC.freeze_sums()["tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json"]))
    predbad = variant(C["scored"], "predsha", lambda o: o.update(predictions_sha256="0" * 64))
    scbad = variant(C["scored"], "scorersha", lambda o: o.update(scorer_sha256="0" * 64))
    nocs = variant(C["scored"], "nocsessions", lambda o: o.pop("c_sessions"))
    cp = os.path.join(TMP["real"], "copy-of-A", "scored.json")
    os.makedirs(os.path.dirname(cp), exist_ok=True)
    shutil.copy2(A["scored"], cp)
    cases = [("E171 twice", A["scored"], A["scored"]), ("E171 and a byte copy of it", A["scored"], cp), ("E172 twice", C["scored"], C["scored"]),
             ("the pair swapped", C["scored"], A["scored"]), ("E171's file relabelled as E172's", A["scored"], relab),
             ("a predictions_sha256 not the freeze's", A["scored"], predbad), ("a scorer_sha256 not the committed one", A["scored"], scbad),
             ("a file with no c_sessions", A["scored"], nocs), ("a missing file", A["scored"], os.path.join(TMP["real"], "no-such.json"))]
    for i, (tag, a, b) in enumerate(cases):
        r = kap("score_p8_600_v3.py", a, b, f"w5-{i}")
        out[tag] = brief(r)
        if r["rc"] != 6 or r["wrote"]:
            bad.append(f"{tag}: rc {r['rc']}, wrote {r['wrote']}")
    _, _, sa = scale_c(A, "w5")
    _, _, sc_ = scale_c(C, "w5")
    r = kap("score_p8_600_v3.py", A["scored"], C["scored"], "w5-swapped", ("--scale-c", sc_, sa))
    out["--scale-c swapped"] = brief(r)
    if r["rc"] != 6 or r["wrote"]:
        bad.append(f"--scale-c swapped: rc {r['rc']}")
    r = kap("score_p8_600_v3.py", A["scored"], C["scored"], "w5-inorder", ("--scale-c", sa, sc_))
    out["--scale-c in order (positive control)"] = brief(r)
    if r["rc"] != 0 or r.get("verdict") != "PASS" or r.get("beside") != "PASS" or r.get("beside_n") != 4:
        bad.append(f"--scale-c in order: rc {r['rc']} {r.get('verdict')}, beside {r.get('beside')} n {r.get('beside_n')}")
    out["pass"] = not bad
    out["differences"] = bad
    for k, v in out.items():
        if isinstance(v, dict):
            say(f"W5 {k}: rc {v['rc']}, wrote {v['wrote']} | {v['line']}", 300)
    say(f"W5 {'PASS' if not bad else 'FAIL'} {bad}")
    return out


def w6():
    bad = []

    def rows_of(path):
        res = load(path)
        vals = {}
        for p in res.get("passes", []):
            for t, r in (res.get("per_pass", {}).get(str(p)) or {}).items():
                v = r.get("D") if isinstance(r, dict) else None
                if isinstance(v, (int, float)):
                    vals.setdefault(t, []).append(float(v))
        return {"primary": {"rows": {t: {"D_w": sum(v) / len(v)} for t, v in vals.items() if len(v) >= 2}}}
    a = rows_of(os.path.join(DD, "2026-11-04-e163-blind7-aifoundry3", "e163.json"))
    b = rows_of(os.path.join(DD, "2026-11-04-e164-blind7-card1", "e164.json"))
    sh, sm = V3.same_d([a, b])
    sh2, sm2 = V3.same_d([a, a])
    zeros = sorted(t for t in set(a["primary"]["rows"]) & set(b["primary"]["rows"])
                   if a["primary"]["rows"][t]["D_w"] == 0.0 and b["primary"]["rows"][t]["D_w"] == 0.0)
    out = {"E163_E164_shared_nonzero_D": len(sh), "E163_E164_bit_identical_D": len(sm), "refused": V3.one_session_twice(sh, sm),
           "both_exactly_zero": zeros, "E163_itself_shared": len(sh2), "E163_itself_identical": len(sm2),
           "E163_itself_refused": V3.one_session_twice(sh2, sm2)}
    if out["refused"] or sm or not out["E163_itself_refused"]:
        bad.append(f"check (7) on real data: {out}")
    out["pass"] = not bad
    say(f"W6 E163 and E164 (committed): {len(sh)} tiles with a non-zero D in both, {len(sm)} bit-identical (refused {out['refused']}; "
        f"exactly 0 W in both: {', '.join(zeros)}); E163 against itself: {len(sm2)} of {len(sh2)} (refused {out['E163_itself_refused']}): "
        f"{'PASS' if not bad else 'FAIL'}")
    return out


def main():
    outp = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    txtp = sys.argv[sys.argv.index("--txt") + 1] if "--txt" in sys.argv else None
    given = tempfile.mkdtemp(prefix="p8-600-v3-selftest-")
    TMP["given"], TMP["real"] = given, os.path.realpath(given)
    res = {}
    try:
        res["W0"] = w0()
        A = session("aifoundry3", "A")
        C = session("aifoundry1c1", "C")
        res["W1"] = w1(A, C)
        res["W2"], A1 = w2(A, C)
        for k, f in (("W3", lambda: w3(A, A1, C)), ("W4", lambda: w4(A, C)), ("W5", lambda: w5(A, C)), ("W6", w6)):
            try:
                res[k] = f()
            except Exception as e:  # noqa: BLE001
                res[k] = {"pass": False, "error": mask(f"{type(e).__name__}: {e}")[:600]}
                say(f"{k} ERROR {type(e).__name__}: {e}", 600)
    except Exception as e:  # noqa: BLE001
        res["ERROR"] = {"pass": False, "error": mask(f"{type(e).__name__}: {e}")[:600]}
        say(f"ERROR {type(e).__name__}: {e}", 600)
    finally:
        shutil.rmtree(given, ignore_errors=True)
    res["PASS"] = all(v.get("pass") for k, v in res.items() if isinstance(v, dict)) and all(f"W{i}" in res for i in range(7))
    say("SELFTEST-SCORE-P8-600-V3 " + ("PASS" if res["PASS"] else "FAIL") + " " +
        json.dumps({k: v.get("pass") for k, v in res.items() if isinstance(v, dict)}, sort_keys=True))
    if outp:
        open(outp, "w").write(mask(json.dumps(res, indent=1, sort_keys=True, default=str)) + "\n")
    if txtp:
        open(txtp, "w").write("\n".join(LINES) + "\n")
    return 0 if res["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
