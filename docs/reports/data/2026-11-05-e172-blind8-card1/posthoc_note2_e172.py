#!/usr/bin/env python3
"""E172's data README, dated note 2 (Thu 5 Nov 2026, post hoc, desk only): E172's C checked again from a fresh reference cache, compared
with the committed check, and P8-KC and the C-session gate re-read from the re-check.

The re-check is the registered checker as collect_e172.sh step 1 ran it (Q139(k)'s tools/claims-v3/ccheck/ccheck.py check, unchanged,
--jobs 2), over the C log of every listed session decompressed from this directory's committed c-log.jsonl.gz files as
c-log-<session>.jsonl, in ccsessions_p8.listed_sessions' order, with a new, empty --cache. This script judges nothing itself: it compares
the re-check's --out file with this directory's ccheck/ccheck-session.json.gz, then calls the committed code unchanged on the re-check:
score_p8_600.c_status and score_p8_600_v2.kc_of (P8-KC's block), ccsessions_p8.check (the C-session gate) and ccheck.load_clog (the
checker's own reader, for the counts). It reads this directory as committed and writes nothing; it prints repo-relative names only.

    /usr/bin/python3 -B docs/reports/data/2026-11-05-e172-blind8-card1/posthoc_note2_e172.py <the re-check's --out json>

Parts: 1 the inputs; 2 the whole file; 3 every C record, log by log; 4 the four passes (p17210-p17213) and the smoke; 5 what each count
counts (C records against the runs tables' launch records); 6 P8-KC re-read from the re-check; 7 the C-session gate on the re-check.
Exit 0 when the re-check equals the committed check record for record and P8-KC and the gate read as committed, else 1.
Python 3.9, standard library only. SPDX-License-Identifier: Apache-2.0
"""
import collections
import gzip
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
for _p in (os.path.join(TOP, "tools", "claims-v3", "p8-600"), os.path.join(TOP, "tools", "claims-v3", "ccheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import ccheck as CK  # noqa: E402  (Q139(k)'s checker; only its reader load_clog is called)
import ccsessions_p8 as CS  # noqa: E402  (the committed C-session gate)
import score_p8_600 as SC  # noqa: E402  (the committed P8 scorer, a518aa11; importing it runs nothing)
import score_p8_600_v2 as V2  # noqa: E402  (86d10a75; kc_of mirrors score_session's P8-KC block)

RUN, CARD = "E172", "aifoundry1c1"
COMMITTED = os.path.join(HERE, "ccheck", "ccheck-session.json.gz")
RAW = os.path.join(HERE, "aifoundry1-c1")
PASSES = ("p17210", "p17211", "p17212", "p17213")
SMOKE = "p17201"
CCHECK_PY_SHA = "2f806fe6080baeea33558ddd49fded16f2ebcb8c02f494217dfd32cc033c0a22"   # the sha256 E163's collection recorded
FAILS = []


def rel(p):
    a = os.path.abspath(p)
    return os.path.relpath(a, TOP) if a.startswith(TOP + os.sep) else os.path.basename(a)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def short(s):
    """a launch's values field as printed here: a file tile by its file name only (the C log records the box's path)"""
    return os.path.basename(s) if isinstance(s, str) and "/" in s else s


def say(s=""):
    print(s)


def need(ok, what):
    if not ok:
        FAILS.append(what)
    return ok


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    mine_path = argv[0]
    mine_bytes = open(mine_path, "rb").read()
    com_bytes = gzip.open(COMMITTED, "rb").read()
    mine, com = json.loads(mine_bytes), json.loads(com_bytes)

    say("== 1. the inputs")
    ck = os.path.join(TOP, "tools", "claims-v3", "ccheck", "ccheck.py")
    ck_sha = sha(open(ck, "rb").read())
    say(f"ccheck.py sha256 {ck_sha} ({'the file E163 recorded' if ck_sha == CCHECK_PY_SHA else 'NOT the file E163 recorded'})")
    need(ck_sha == CCHECK_PY_SHA, "ccheck.py is not the recorded file")
    eng = CK.ENGINE_SRC
    say(f"engine {rel(eng)} sha256 {sha(open(eng, 'rb').read())}; pinned {CK.ENGINE_SHA}")
    need(sha(open(eng, "rb").read()) == CK.ENGINE_SHA, "accum.c is not the pinned engine")
    say(f"the re-check's engine block {mine.get('engine')}; the committed check's {com.get('engine')}")
    need(mine.get("engine") == com.get("engine"), "engine blocks differ")
    say(f"the committed check: {rel(COMMITTED)} (gzip), {len(com_bytes):,} bytes decompressed, sha256 {sha(com_bytes)}")
    say(f"the re-check: {os.path.basename(mine_path)}, {len(mine_bytes):,} bytes, sha256 {sha(mine_bytes)}")

    say("\n== 2. the whole file")
    same_bytes = mine_bytes == com_bytes
    say(f"byte for byte: {'IDENTICAL' if same_bytes else 'different'}")
    say(f"summary: {'equal' if mine.get('summary') == com.get('summary') else 'DIFFERENT'}: {json.dumps(mine.get('summary'))}")
    need(mine.get("summary") == com.get("summary"), "the summaries differ")

    say("\n== 3. every C record, log by log (key: the log's name and line)")
    key = lambda v: (v.get("log"), v.get("line"))  # noqa: E731
    a = {key(v): v for v in mine["launches"]}
    b = {key(v): v for v in com["launches"]}
    say(f"records: re-check {len(mine['launches'])} ({len(a)} distinct keys), committed {len(com['launches'])} ({len(b)} distinct keys)")
    need(len(a) == len(mine["launches"]) and len(b) == len(com["launches"]), "a key repeats")
    only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    differ = collections.Counter()
    ndiff = 0
    for k in sorted(set(a) & set(b)):
        fs = sorted(f for f in set(a[k]) | set(b[k]) if a[k].get(f) != b[k].get(f))
        if fs:
            ndiff += 1
            differ.update(fs)
    say(f"only in the re-check {len(only_a)}; only in the committed {len(only_b)}; in both {len(set(a) & set(b))}, of which differing in "
        f"any field {ndiff} {dict(differ) if differ else ''}")
    need(not only_a and not only_b and ndiff == 0, "records differ")
    fields = sorted({f for v in com["launches"] for f in v})
    say(f"fields compared per record ({len(fields)}): {', '.join(fields)}")
    order_same = [key(v) for v in mine["launches"]] == [key(v) for v in com["launches"]]
    say(f"record order: {'the same' if order_same else 'DIFFERENT'}")
    per = collections.OrderedDict()
    for src, L in (("re-check", mine["launches"]), ("committed", com["launches"])):
        for v in L:
            r = per.setdefault(v.get("log"), {"re-check": collections.Counter(), "committed": collections.Counter()})
            r[src][v["verdict"]] += 1
            r[src][v["type"]] += 1
    say("| log | re-check: launches, verdicts | committed: launches, verdicts | fp32 / fp16 / int8 |")
    for lg, r in per.items():
        def fmt(c):
            n = sum(c[t] for t in CK.TYPES)
            return f"{n}, " + ", ".join(f"{k} {c[k]}" for k in CK.VERDICTS if c[k])
        say(f"| {lg} | {fmt(r['re-check'])} | {fmt(r['committed'])} | "
            f"{r['re-check']['fp32']} / {r['re-check']['fp16']} / {r['re-check']['int8']} |")

    say("\n== 4. the four passes (p17210-p17213) and the smoke")
    def block(names):
        lg = {f"c-log-{p}.jsonl" for p in names}
        m = [v for v in mine["launches"] if v.get("log") in lg]
        c = [v for v in com["launches"] if v.get("log") in lg]
        same = sum(1 for v in m if b.get(key(v)) == v)
        vm = collections.Counter(v["verdict"] for v in m)
        ty = collections.Counter(v["type"] for v in m)
        return len(m), len(c), same, dict(vm), dict(ty), len({v.get("tile_sha256") for v in m})
    for nm, names in (("the four passes", PASSES), ("the smoke", (SMOKE,))):
        n_m, n_c, same, vm, ty, ntile = block(names)
        say(f"{nm}: re-check {n_m} C records, committed {n_c}; identical in every field {same}; verdicts {vm}; by type {ty}; "
            f"{ntile} distinct tiles")
        need(n_m == n_c and same == n_m and vm.get("PASS") == n_m, f"{nm} differ")
    for p in PASSES + (SMOKE,):
        d = os.path.join(RAW, ("e172" if p != SMOKE else "e172-smoke"), p)
        clog = os.path.join(d, "c-log.jsonl.gz")
        tmp_n = sum(1 for v in mine["launches"] if v.get("log") == f"c-log-{p}.jsonl")
        say(f"  {p}: the committed c-log.jsonl.gz sha256 {sha(open(clog, 'rb').read())[:16]}…; launches the checker's reader finds "
            f"in it: {CS.n_launches_in_log(clog)}; judged in the re-check: {tmp_n}")

    say("\n== 5. what each count counts (C records against the runs tables' launch records, matched by t_start_ms and t_end_ms)")
    pred_path, pred = SC.load_pred(CARD)
    want = set(pred["tiles"])
    red = json.load(open(os.path.join(HERE, "e172.json")))
    kept = [f"p{p}" for p in red.get("passes", [])]
    say(f"pool 8's tiles in {rel(pred_path)}: {len(want)}; the registered primary's kept passes: {', '.join(kept)}; set aside: "
        f"{', '.join('p' + str(x.get('pass')) for x in red.get('passes_set_aside') or []) or 'none'}")
    by_t = {}
    for v in mine["launches"]:
        by_t[(v.get("t_start_ms"), v.get("t_end_ms"))] = v
    say("| session | C records | runs-table launch records | matched | C records with no runs-table record | of runs-table records: pool 8 / other items | of pool 8's: PASS |")
    tot = collections.Counter()
    for p in (SMOKE,) + PASSES:
        d = os.path.join(RAW, ("e172" if p != SMOKE else "e172-smoke"), p)
        recs = [json.loads(ln) for ln in open(os.path.join(d, "runs.jsonl")) if ln.startswith("{")]
        recs = [r for r in recs if "launch" in r and "item" in r]
        nC = sum(1 for v in mine["launches"] if v.get("log") == f"c-log-{p}.jsonl")
        keys = {(r.get("t_start_ms"), r.get("t_end_ms")) for r in recs}
        matched = sum(1 for r in recs if (r.get("t_start_ms"), r.get("t_end_ms")) in by_t)
        cl = {(v.get("t_start_ms"), v.get("t_end_ms")) for v in mine["launches"] if v.get("log") == f"c-log-{p}.jsonl"}
        unl = sorted(cl - keys)
        unl_vals = collections.Counter(short(by_t[k].get("values")) for k in unl)
        p8 = [r for r in recs if r.get("item") in want]
        p8pass = sum(1 for r in p8 if (by_t.get((r.get("t_start_ms"), r.get("t_end_ms"))) or {}).get("verdict") == "PASS")
        say(f"| {p} | {nC} | {len(recs)} | {matched} | {len(unl)} ({', '.join(f'{k} {n}' for k, n in unl_vals.items()) or '-'}) | "
            f"{len(p8)} / {len(recs) - len(p8)} | {p8pass} |")
        tot.update({"C": nC, "runs": len(recs), "matched": matched, "unlisted": len(unl), "p8": len(p8), "p8pass": p8pass,
                    "p8_kept": len(p8) if p in kept else 0, "p8pass_kept": p8pass if p in kept else 0})
        need(matched == len(recs), f"{p}: a runs-table launch record has no C record")
    say(f"totals: C records {tot['C']}; runs-table launch records {tot['runs']} (all matched: {tot['matched'] == tot['runs']}); "
        f"C records outside the runs tables {tot['unlisted']}; pool 8's launch records {tot['p8']} in all, {tot['p8_kept']} in the kept "
        f"passes ({tot['p8pass_kept']} PASS)")

    say("\n== 6. P8-KC re-read from the re-check (score_p8_600.c_status and score_p8_600_v2.kc_of, unchanged)")
    passes_dir = os.path.join(RAW, "e172")
    cstat = SC.c_status(list(pred["tiles"]), red, [mine_path], passes_dir)
    kc, _ = V2.kc_of(cstat, list(pred["tiles"]))
    scored = json.load(open(os.path.join(HERE, "scored.json")))
    kc_file = scored["primary"]["rules"]["P8-KC"]
    eq = all(kc.get(k) == kc_file.get(k) for k in ("verdict", "launches", "PASS", "c_excluded", "not_measured"))
    say(f"from the re-check: {json.dumps(kc, sort_keys=True)}")
    say(f"scored.json › primary.rules.P8-KC: {json.dumps(kc_file, sort_keys=True)}")
    say(f"equal: {eq}")
    need(eq, "P8-KC differs")
    allp = SC.c_status(list(pred["tiles"]), {"passes": [int(p[1:]) for p in PASSES]}, [mine_path], passes_dir)
    kc4, _ = V2.kc_of(allp, list(pred["tiles"]))
    say(f"reported beside, never a rule: the same over all four passes (the set-aside p17213 included): launches {kc4['launches']}, "
        f"PASS {kc4['PASS']}, c_excluded {kc4['c_excluded']}")
    e78 = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full")
    e78s = SC.c_status(list(e78), {"passes": [int(p[1:]) for p in PASSES]}, [mine_path], passes_dir)
    say("reported beside: E78's six items over the four passes: " + "; ".join(
        f"{t} {e78s.get(t, {}).get('PASS', 0)}/{e78s.get(t, {}).get('launches', 0)}" for t in e78))

    say("\n== 7. the C-session gate on the re-check (ccsessions_p8.check, unchanged, no --since)")
    g = CS.check(RUN, RAW, mine_path, None)
    g = json.loads(json.dumps(g).replace(TOP + os.sep, "").replace(os.path.dirname(os.path.abspath(mine_path)) + os.sep, ""))
    for ln in g.get("lines", []):
        say(f"  {ln}")
    at = {s.get("session"): s for s in scored["c_sessions"]["sessions"]}
    same = sum(1 for s in g.get("sessions", []) if all((at.get(s.get("session")) or {}).get(k) == s.get(k)
                                                     for k in ("status", "launches_in_log", "launches_judged", "log_name")))
    say(f"ok {g.get('ok')}; listed {g.get('listed')}; stop-path test {g.get('stoptest')}; sessions with the same record as scored.json's "
        f"c_sessions: {same} of {len(g.get('sessions', []))}")
    need(bool(g.get("ok")) and same == len(g.get("sessions", [])) == scored["c_sessions"]["listed"], "the C-session gate differs")

    say("\n== verdict")
    if FAILS:
        say("NOT AS COMMITTED: " + "; ".join(FAILS))
        return 1
    say(f"AS COMMITTED: every one of the {len(mine['launches'])} C records re-derived from a fresh cache equals the committed record in every "
        f"field ({'and the file is byte-identical' if same_bytes else 'the file bytes differ'}); P8-KC and the C-session gate read as committed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
