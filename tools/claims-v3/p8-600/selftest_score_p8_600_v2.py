#!/usr/bin/env python3
"""Q142(k6) fix pass: the self-test of score_p8_600_v2.py (dated note 1 beside E171.md and E172.md, N1 and N2). Desk only: it reads
committed files and writes only into a temporary directory (removed at the end) and its --out and --txt files. No device, no ssh.

  V0  the inputs: the committed scorer's sha256 equals its SHA256SUMS line (a518aa11); v2's E78 list equals e78_common's ANCHORS and TIE;
      the predictor's lists pass.
  V1  N1, ka-pooled, on a synthetic session per card (the committed self-test's builder, with E78's items added to every pass's runs
      and C logs), scored by the committed scorer's command line as the collectors call it: the right pair reads as the committed
      ka_pooled reads it (verdict, n and rows). Refused with exit 6 and nothing written: E171 twice; E172 twice; the pair swapped; a copy
      of E171's file relabelled as E172's (run, card, predictions path and sha256: its rows stay aifoundry3's); a predictions_sha256 that
      is not the freeze's; a scorer_sha256 that is not the committed scorer's; a file with no c_sessions; a missing file; --scale-c with
      its two files swapped.
  V2  N2, scale-c: (a) every anchor C all PASS on both cards: six anchors in s, each all PASS, the arm is the primary; (b) one of pool 8's
      scale anchors judged FAIL on every launch: P8-KC FAIL in the scored file, as registered, the anchor named, the arm's s equal to the
      median of the other anchors' ratios (computed here) and not the primary's, its verdicts recorded with the rules that differ; on
      both cards; (c) E78's fp32.randn judged FAIL: P8-KC PASS in the scored file (it covers pool 8's tiles only), the anchor named, the
      arm without it; (d) every anchor in s judged FAIL: the arm's s is 1 and its KA NOT SCORED; (e) E78's fp32.zeros judged FAIL: named
      as a footing item, no arm; (f) refusals with exit 6 and nothing written: the other card's scored file, a reduction other than the
      one scored (one tile's D moved by 1 mW), another session's check of C, a scored file without c_sessions, the other run named;
      exit 9 for predictions that are not the freeze's; the
      predictor's own stop (SystemExit) propagates and leaves nothing; (g) ka-pooled --scale-c with (b)'s arm on E171: the beside
      reading comes from the arm's KA rows, and the registered reading is unchanged.
  V3  real data: the same C-status reading on E163's and E164's committed sessions (their committed reductions, raw passes and checks of
      C): every anchor of M10's list that ran (E78's fp32.randn and fp16.randn, pool 7's four random anchors) and E78's footing items
      read C all PASS, with their launch counts.

    /usr/bin/python3 -B tools/claims-v3/p8-600/selftest_score_p8_600_v2.py [--out <file.json>] [--txt <file.txt>]

Exit 0 when every part passes. Standard library and numpy (through the predictor). SPDX-License-Identifier: Apache-2.0
"""
import contextlib
import gzip
import hashlib
import io
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_p8_600 as SC  # noqa: E402  (committed, a518aa11)
import score_p8_600_v2 as V2  # noqa: E402
import selftest_score_p8_600 as ST  # noqa: E402  (committed: its synthetic-session builder; importing runs nothing)
import ccsessions_p8 as CSN  # noqa: E402

DD = os.path.join(TOP, "docs", "reports", "data")
E163D = os.path.join(DD, "2026-11-04-e163-blind7-aifoundry3")
E164D = os.path.join(DD, "2026-11-04-e164-blind7-card1")
load = lambda p: json.load(gzip.open(p, "rt") if p.endswith(".gz") else open(p))  # noqa: E731
RUN_OF = {"aifoundry3": "E171", "aifoundry1c1": "E172"}
LINES = []


def say(s):
    LINES.append(s)
    print(s, flush=True)


# ------------------------------------------------------------------------------------------------- the sessions
RATIOS = {"fp32.randn": 1.000, "fp16.randn": 1.002}   # pool 8's four scale anchors: 1.004, 1.006, 1.008, 1.010 in sorted name order


def session(card, tmp, label, fail=(), ratios=True):
    """the committed builder's session, then: the six anchors in s at known ratios (so removing one moves the median), E78's items in
    every pass's runs.jsonl and C log and in the check of C, and the launches of `fail` judged FAIL. Scored by the committed scorer's
    command line. Returns a dict of paths and the predictions."""
    run = RUN_OF[card]
    raw, cc, red, pred, _ = ST.synth(card, tmp, label)
    S = pred["sets"]
    rate = {t: pred["rates"][t]["stated_per_s"] for t in SC.FORMATS}
    res = load(red)
    if ratios:
        want = dict(RATIOS)
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
    base = os.path.dirname(red)
    js, md = os.path.join(base, "scored.json"), os.path.join(base, "results.md")
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "score_p8_600.py"), "score", "--run", run, "--reduction", red, "--raw", raw,
                        "--ccheck", cc, "--json", js, "--md", md], capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not os.path.exists(js):
        raise RuntimeError(f"the committed scorer exited {r.returncode} on {label}: {r.stdout[-300:]} {r.stderr[-300:]}")
    return {"run": run, "card": card, "raw": raw, "cc": cc, "red": red, "scored": js, "pred": pred, "base": base}


def v2(args, timeout=600):
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "score_p8_600_v2.py")] + args, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def scale_c(s, tag, scored=None, red=None, cc=None, run=None):
    js, md = os.path.join(s["base"], f"scale-c-{tag}.json"), os.path.join(s["base"], f"scale-c-{tag}.md")
    work = os.path.join(s["base"], f"work-{tag}")
    rc, out, err = v2(["scale-c", "--run", run or s["run"], "--scored", scored or s["scored"], "--reduction", red or s["red"], "--raw",
                       s["raw"], "--ccheck", cc or s["cc"], "--json", js, "--md", md, "--work", work])
    wrote = os.path.exists(js) or os.path.exists(md) or (os.path.isdir(work) and bool(os.listdir(work)))
    return rc, out, err, (load(js) if os.path.exists(js) else None), wrote, js


# ------------------------------------------------------------------------------------------------- V0
def v0():
    sums = {}
    for line in open(os.path.join(HERE, "SHA256SUMS")):
        h, p = line.split(None, 1)
        sums[p.strip()] = h
    have = hashlib.sha256(open(os.path.join(HERE, "score_p8_600.py"), "rb").read()).hexdigest()
    sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "kinds"))
    try:
        import e78_common as ec  # noqa: E402
        e78 = tuple(ec.ANCHORS) + (ec.TIE,)
    finally:
        sys.path.pop(0)
    out = {"scorer_sha256": have, "scorer_listed": sums.get(V2.SCORER_REL), "e78_items": list(V2.E78_ITEMS), "e78_common": list(e78),
           "predictor_lists": SC.A2().check_lists(), "pool8_inputs": SC.P().check_inputs()}
    out["pass"] = have == sums.get(V2.SCORER_REL) and sorted(V2.E78_ITEMS) == sorted(e78) and len(V2.E78_ITEMS) == len(e78)
    say(f"V0 scorer {have[:12]} listed {str(sums.get(V2.SCORER_REL))[:12]}; E78 items {list(V2.E78_ITEMS) == list(e78)}: "
        f"{'PASS' if out['pass'] else 'FAIL'}")
    return out


# ------------------------------------------------------------------------------------------------- V1
def v1(tmp, A, C):
    out, bad = {}, []
    jsn = os.path.join(tmp, "kap.json")

    def kap(a, b, tag, extra=()):
        if os.path.exists(jsn):
            os.remove(jsn)
        rc, so, se = v2(["ka-pooled", a, b, *extra, "--json", jsn])
        rec = {"rc": rc, "wrote": os.path.exists(jsn), "line": (so.splitlines() or [""])[0][:300]}
        out[tag] = rec
        return rec
    ok = kap(A["scored"], C["scored"], "the right pair")
    mine = load(jsn) if os.path.exists(jsn) else {}
    theirs = SC.ka_pooled([A["scored"], C["scored"]])
    same = ok["rc"] == 0 and all(mine.get(k) == theirs.get(k) for k in ("verdict", "n", "rows"))
    out["the right pair"]["same_as_committed"] = same
    out["the right pair"]["verdict"] = mine.get("verdict")
    out["the right pair"]["n"] = mine.get("n")
    if not same or mine.get("verdict") != "PASS" or mine.get("n") != 4:
        bad.append(f"the right pair: rc {ok['rc']}, {mine.get('verdict')} n {mine.get('n')}, same as committed {same}")
    # the files a hand call could give
    def variant(src, tag, fn):
        o = load(src)
        fn(o)
        p = os.path.join(tmp, f"variant-{tag}.json")
        json.dump(o, open(p, "w"), indent=1, sort_keys=True)
        return p
    relab = variant(A["scored"], "relabelled", lambda o: o.update(
        run="E172", card="aifoundry1c1", predictions="tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json",
        predictions_sha256=SC.freeze_sums()["tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json"]))
    predbad = variant(C["scored"], "predsha", lambda o: o.update(predictions_sha256="0" * 64))
    scbad = variant(C["scored"], "scorersha", lambda o: o.update(scorer_sha256="0" * 64))
    nocs = variant(C["scored"], "nocsessions", lambda o: o.pop("c_sessions"))
    cases = [("E171 twice", A["scored"], A["scored"]), ("E172 twice", C["scored"], C["scored"]), ("the pair swapped", C["scored"], A["scored"]),
             ("E171's file relabelled as E172's", A["scored"], relab), ("a predictions_sha256 not the freeze's", A["scored"], predbad),
             ("a scorer_sha256 not the committed one", A["scored"], scbad), ("a file with no c_sessions", A["scored"], nocs),
             ("a missing file", A["scored"], os.path.join(tmp, "no-such.json"))]
    for tag, a, b in cases:
        r = kap(a, b, tag)
        if r["rc"] != 6 or r["wrote"]:
            bad.append(f"{tag}: rc {r['rc']}, wrote {r['wrote']}")
    # --scale-c with its two files swapped (each scale-c.json names its own scored file)
    sa = scale_c(A, "v1")[5]
    sc_ = scale_c(C, "v1")[5]
    r = kap(A["scored"], C["scored"], "--scale-c swapped", ("--scale-c", sc_, sa))
    if r["rc"] != 6 or r["wrote"]:
        bad.append(f"--scale-c swapped: rc {r['rc']}")
    r = kap(A["scored"], C["scored"], "--scale-c in order (positive control)", ("--scale-c", sa, sc_))
    m2 = load(jsn) if os.path.exists(jsn) else {}
    b = (m2.get("beside") or {}).get("c_clean_scale") or {}
    out["--scale-c in order (positive control)"].update(verdict=m2.get("verdict"), beside=b.get("verdict"), beside_n=b.get("n"))
    if r["rc"] != 0 or m2.get("verdict") != mine.get("verdict") or b.get("verdict") != mine.get("verdict") or b.get("n") != 4:
        bad.append(f"--scale-c in order: rc {r['rc']}, {m2.get('verdict')}, beside {b.get('verdict')} n {b.get('n')}")
    out["differences"] = bad
    out["pass"] = not bad
    for k, v in out.items():
        if isinstance(v, dict):
            say(f"V1 {k}: rc {v['rc']}, wrote {v['wrote']} | {v['line'][:150]}")
    say(f"V1 {'PASS' if not bad else 'FAIL'} {bad}")
    return out


# ------------------------------------------------------------------------------------------------- V2
def v2_cases(tmp, A, C):
    out, bad = {}, []
    # (a) every anchor C all PASS, both cards
    for s in (A, C):
        rc, so, se, c, wrote, _ = scale_c(s, "a")
        rec = {"rc": rc, "line": so[:300]}
        if c:
            rec.update(in_s=len(c["primary"]["anchors_used"]), all_pass=all(c["scale_anchors"][n]["all_pass"] for n in c["primary"]["anchors_used"]),
                       arm=c["arm"], launches={n: c["scale_anchors"][n]["launches"] for n in c["primary"]["anchors_used"]},
                       footing={n: [r["launches"], r["all_pass"]] for n, r in c["footing_items"].items()})
        out[f"(a) {s['card']}: every anchor C all PASS"] = rec
        if rc != 0 or not c or c["arm"] is not None or rec["in_s"] != 6 or not rec["all_pass"] or not all(v[1] for v in rec["footing"].values()):
            bad.append(f"(a) {s['card']}: rc {rc} {so[:200]} {se[-300:]}")
    # (b) one of pool 8's scale anchors judged FAIL on every launch, both cards
    for card in ("aifoundry3", "aifoundry1c1"):
        pred = A["pred"] if card == "aifoundry3" else C["pred"]
        fa = sorted(pred["sets"]["scale_anchors_pool8"])[0]
        s = session(card, tmp, f"b-{card}", fail=(fa,))
        sj = load(s["scored"])
        rc, so, se, c, wrote, _ = scale_c(s, "b")
        rec = {"rc": rc, "line": so[:300], "anchor": fa, "KC_in_scored": sj["verdicts"]["P8-KC"],
               "excluded_in_scored": fa in sj["primary"]["rules"]["P8-KC"]["c_excluded"]}
        if c and c["arm"]:
            ratios = sj["primary"]["scale"]["ratios"]
            expect = statistics.median([v for n, v in ratios.items() if n != fa])
            rec.update(named=c["in_s_not_all_pass"], s_primary=c["primary"]["s_float"], s_arm=c["arm"]["s_float"], s_expected=expect,
                       differs=c["arm"]["differs_from_primary"], arm_verdicts=c["arm"]["verdicts"])
            if not (abs(c["arm"]["s_float"] - expect) < 1e-12 and abs(c["arm"]["s_float"] - c["primary"]["s_float"]) > 1e-6
                    and c["in_s_not_all_pass"] == [fa] and c["primary"]["verdicts"] == sj["verdicts"]):
                bad.append(f"(b) {card}: s arm {c['arm']['s_float']} expected {expect}, primary {c['primary']['s_float']}")
        else:
            bad.append(f"(b) {card}: no arm (rc {rc}, {so[:200]}, {se[-300:]})")
        if rec["KC_in_scored"] != "FAIL" or not rec["excluded_in_scored"]:
            bad.append(f"(b) {card}: the scored file's KC {rec['KC_in_scored']}")
        out[f"(b) {card}: pool 8's scale anchor {fa} FAILs"] = rec
        if card == "aifoundry3":
            B3 = (s, c)
    # (c) E78's fp32.randn judged FAIL (aifoundry3)
    s = session("aifoundry3", tmp, "c", fail=("fp32.randn",))
    sj = load(s["scored"])
    rc, so, se, c, wrote, _ = scale_c(s, "c")
    expect = statistics.median([v for n, v in sj["primary"]["scale"]["ratios"].items() if n != "fp32.randn"])
    rec = {"rc": rc, "line": so[:300], "KC_in_scored": sj["verdicts"]["P8-KC"], "named": c and c["in_s_not_all_pass"],
           "s_arm": c and c["arm"] and c["arm"]["s_float"], "s_expected": expect}
    out["(c) E78's fp32.randn FAILs"] = rec
    if rc != 0 or sj["verdicts"]["P8-KC"] != "PASS" or not c or not c["arm"] or c["in_s_not_all_pass"] != ["fp32.randn"] or \
            abs(c["arm"]["s_float"] - expect) > 1e-12:
        bad.append(f"(c): rc {rc}, KC {sj['verdicts']['P8-KC']}, {rec}")
    # (d) every anchor in s judged FAIL
    alln = ["fp32.randn", "fp16.randn"] + list(A["pred"]["sets"]["scale_anchors_pool8"])
    s = session("aifoundry3", tmp, "d", fail=alln)
    rc, so, se, c, wrote, _ = scale_c(s, "d")
    rec = {"rc": rc, "line": so[:300], "s_arm": c and c["arm"] and c["arm"]["s_float"],
           "KA_arm": c and c["arm"] and c["arm"]["verdicts"].get("P8-KA")}
    out["(d) every anchor in s FAILs"] = rec
    if rc != 0 or not c or not c["arm"] or c["arm"]["s_float"] != 1.0 or c["arm"]["verdicts"].get("P8-KA") != "NOT SCORED":
        bad.append(f"(d): {rec}")
    # (e) E78's fp32.zeros judged FAIL: a footing item, no arm
    s = session("aifoundry3", tmp, "e", fail=("fp32.zeros",))
    rc, so, se, c, wrote, _ = scale_c(s, "e")
    rec = {"rc": rc, "line": so[:300], "footing_not_all_pass": c and c["footing_not_all_pass"], "arm": c and c["arm"]}
    out["(e) E78's fp32.zeros FAILs"] = rec
    if rc != 0 or not c or c["footing_not_all_pass"] != ["fp32.zeros"] or c["arm"] is not None:
        bad.append(f"(e): {rec}")
    # (f) refusals
    Bs, Bc = B3
    nocs = os.path.join(tmp, "nocs-scored.json")
    o = load(A["scored"])
    o.pop("c_sessions")
    json.dump(o, open(nocs, "w"))
    # another session's reduction: the builder is deterministic, so (b)'s reduction is byte-identical to A's (only its check of C
    # differs); a different reduction is A's with one N1 tile's measured D moved by 1 mW in every pass
    other = load(A["red"])
    t1 = sorted(A["pred"]["sets"]["N1"])[0]
    for pp in other["per_pass"].values():
        if t1 in pp:
            pp[t1]["D"] += 0.001
    other["items"][t1]["D"]["mean"] += 0.001
    other_red = os.path.join(tmp, "other-reduction.json")
    json.dump(other, open(other_red, "w"))
    ref = {}
    for tag, kw in (("the other card's scored file", {"scored": C["scored"]}), ("another session's reduction", {"red": other_red}),
                    ("another session's check of C", {"cc": Bs["cc"]}), ("a scored file without c_sessions", {"scored": nocs}),
                    ("the other run named", {"run": "E172"})):
        rc, so, se, c, wrote, _ = scale_c(A, "f" + str(len(ref)), **kw)
        ref[tag] = {"rc": rc, "wrote": wrote, "line": so[:240]}
        if rc != 6 or wrote:
            bad.append(f"(f) {tag}: rc {rc}, wrote {wrote}, {so[:200]} {se[-200:]}")
    # exit 9: predictions that are not the freeze's (in process, the freeze's list replaced for this call only)
    keep = SC.freeze_sums
    js = os.path.join(A["base"], "scale-c-f9.json")
    try:
        SC.freeze_sums = lambda: {k: ("0" * 64 if "predictions-pool8" in k else v) for k, v in keep().items()}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = V2.main(["scale-c", "--run", "E171", "--scored", A["scored"], "--reduction", A["red"], "--raw", A["raw"], "--ccheck", A["cc"],
                          "--json", js])
    finally:
        SC.freeze_sums = keep
    ref["predictions not the freeze's"] = {"rc": rc, "wrote": os.path.exists(js), "line": buf.getvalue().strip()[:200]}
    if rc != 9 or os.path.exists(js):
        bad.append(f"(f) predictions: rc {rc}")
    # the predictor's own stop: it propagates as SystemExit (exit 1 on the command line), and nothing is written
    keep2 = SC.P().check_inputs
    js = os.path.join(Bs["base"], "scale-c-fstop.json")
    work = os.path.join(Bs["base"], "work-fstop")
    stopped = None
    try:
        def boom():
            raise SystemExit("POOL8 STOPPED: a test stand-in for a changed input")
        SC.P().check_inputs = boom
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                V2.main(["scale-c", "--run", "E171", "--scored", Bs["scored"], "--reduction", Bs["red"], "--raw", Bs["raw"], "--ccheck", Bs["cc"],
                         "--json", js, "--work", work])
        except SystemExit as e:
            stopped = str(e)
    finally:
        SC.P().check_inputs = keep2
    wrote = os.path.exists(js) or (os.path.isdir(work) and bool(os.listdir(work)))
    ref["the predictor's stop"] = {"stopped": stopped, "wrote": wrote}
    if not stopped or not stopped.startswith("POOL8 STOPPED") or wrote:
        bad.append(f"(f) the predictor's stop: {stopped}, wrote {wrote}")
    out["(f) refusals"] = ref
    # (g) ka-pooled --scale-c with (b)'s arm on E171, against E172's all-PASS session
    sa = scale_c(Bs, "g")[5]
    scc = scale_c(C, "g")[5]
    jsn = os.path.join(tmp, "kap-g.json")
    rc, so, se = v2(["ka-pooled", Bs["scored"], C["scored"], "--scale-c", sa, scc, "--json", jsn])
    m = load(jsn) if os.path.exists(jsn) else {}
    b = (m.get("beside") or {}).get("c_clean_scale") or {}
    arm_ka = (load(sa)["arm"] or {}).get("P8-KA") or {}
    arm_rows = sorted((t, r["e_primary"]) for t, r in (arm_ka.get("tiles") or {}).items())
    beside_rows = sorted((r["tile"], r["e_primary"]) for r in b.get("rows", []) if r.get("run") == "E171")
    committed = SC.ka_pooled([Bs["scored"], C["scored"]])
    rec = {"rc": rc, "verdict": m.get("verdict"), "n": m.get("n"), "committed": [committed.get("verdict"), committed.get("n")],
           "beside": [b.get("verdict"), b.get("n")], "beside_rows_are_the_arm's": arm_rows == beside_rows and bool(arm_rows),
           "sessions": b.get("sessions")}
    out["(g) ka-pooled --scale-c with an arm"] = rec
    if rc != 0 or [m.get("verdict"), m.get("n")] != rec["committed"] or not rec["beside_rows_are_the_arm's"]:
        bad.append(f"(g): {rec}")
    out["differences"] = bad
    out["pass"] = not bad
    for k, v in out.items():
        if isinstance(v, dict) and k != "(f) refusals":
            say(f"V2 {k}: " + json.dumps({x: v.get(x) for x in v if x not in ("arm_verdicts", "footing", "launches", "differs", "sessions")},
                                          default=str)[:330])
    for k, v in ref.items():
        say(f"V2 (f) {k}: {json.dumps(v, default=str)[:300]}")
    say(f"V2 {'PASS' if not bad else 'FAIL'} {bad}")
    return out


# ------------------------------------------------------------------------------------------------- V3
def v3():
    out, bad = {}, []
    p = SC.P()
    names = list(dict.fromkeys(p.m10_anchor_names() + list(V2.E78_ITEMS)))
    e164raw = os.path.join(E164D, "aifoundry1-c1", "e164")
    for lab, red, ccf, pdir in (("E163", os.path.join(E163D, "e163.json"), os.path.join(E163D, "ccheck", "ccheck-all.json"),
                                 os.path.join(E163D, "aifoundry3", "e163")),
                                ("E164", os.path.join(E164D, "e164.json"), os.path.join(E164D, "ccheck", "ccheck-session.json.gz"), e164raw)):
        res = load(red)
        cs = SC.c_status(names, res, [ccf], pdir)
        ran = {n: {"launches": cs[n]["launches"], "all_pass": cs[n]["all_pass"]} for n in names if n in cs and cs[n]["launches"]}
        notran = [n for n in names if n not in ran]
        need = {"fp32.randn", "fp16.randn", "fp32.anchor7_randn_a", "fp32.anchor7_randn_b", "fp16.anchor7_randn_a", "fp16.anchor7_randn_b"}
        ok = all(v["all_pass"] for v in ran.values()) and need <= set(ran) and set(V2.E78_ITEMS) - {"anchor_pi"} <= set(ran)
        out[lab] = {"kept_passes": res.get("passes"), "ran": ran, "not_ran": notran, "pass": ok}
        if not ok:
            bad.append(f"{lab}: {ran} not ran {notran}")
        say(f"V3 {lab}: kept passes {res.get('passes')}; " + ", ".join(f"{n} {v['launches']}{'' if v['all_pass'] else ' NOT ALL PASS'}"
                                                                     for n, v in ran.items()) + f"; not run: {notran}")
    out["pass"] = not bad
    say(f"V3 {'PASS' if not bad else 'FAIL'} {bad}")
    return out


def main():
    outp = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    txtp = sys.argv[sys.argv.index("--txt") + 1] if "--txt" in sys.argv else None
    tmp = tempfile.mkdtemp(prefix="p8-600-v2-selftest-")
    res = {}
    try:
        res["V0"] = v0()
        A = session("aifoundry3", tmp, "base-a3")
        C = session("aifoundry1c1", tmp, "base-c1")
        for k, f in (("V1", lambda: v1(tmp, A, C)), ("V2", lambda: v2_cases(tmp, A, C)), ("V3", v3)):
            try:
                res[k] = f()
            except Exception as e:  # noqa: BLE001
                import traceback
                res[k] = {"pass": False, "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-1500:]}
                say(f"{k} ERROR {type(e).__name__}: {e}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    res["PASS"] = all(v.get("pass") for k, v in res.items() if k.startswith("V"))
    say("SELFTEST-SCORE-P8-600-V2 " + ("PASS" if res["PASS"] else "FAIL") + " " +
        json.dumps({k: v.get("pass") for k, v in res.items() if k.startswith("V")}, sort_keys=True))
    clean = lambda t: t.replace(TOP + os.sep, "").replace(TOP, "<repo>").replace(tmp, "<tmp>")  # noqa: E731
    if outp:
        open(outp, "w").write(clean(json.dumps(res, indent=1, sort_keys=True, default=str)) + "\n")
    if txtp:
        open(txtp, "w").write(clean("\n".join(LINES)) + "\n")
    return 0 if res["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
